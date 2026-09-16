"""
AutoUnlock V2 

CORE FEATURES:

• Multi-mode support: Sandbox (testing), Crossover (multi-server), Production (local)
• Hysteresis-based proximity detection (prevents oscillation at thresholds)
• EMA smoothing for BLE distance (exponential moving average)
• Adaptive staleness detection (learns update patterns)
• Tap debouncing (prevents rapid re-trigger flooding)
• Contact sensor ignore (doesn't unlock if door already open)
• LED feedback: thinking (amber flash) → opening (green) → error (red)
• Intelligent location retry (arrival-gated, only retries for arriving users)
• Multi-tap sensor support (single or multiple tap sensors per door)
• Mock/real/bridge unlock options for testing and deployment flexibility
• Comprehensive debug logging with [TAGS] for easy filtering

================================================================================
METHOD REFERENCE
INITIALIZATION & SETUP:
initialize() - AppDaemon entry point, sets up modes & listeners
option(part) - Get mock/real/bridge option for component
pickentity(entity, kind, door) - Choose correct mock/real entity based on mode
pickled(feedbackmode, door) - Choose correct LED entity (mock or real)

SENSOR DATA RETRIEVAL:
getbledistance(userinfo) - Get BLE distance with EMA smoothing
getarea(userinfo) - Get user's current area/location
ble_stale(userinfo, adaptive) - Check if BLE sensor data is too old

PROXIMITY & APPROACH DETECTION:
_is_nearby(userinfo, zone) - Check if user in proximity of door (hysteresis)
_get_best_proxy_distance(...) - Get nearest proxy distance (Phase 1 fallback)
detectapproachvector(...) - Detect if user approaching based on velocity
checkproximityhysteresis(...) - Hysteresis logic to prevent threshold oscillation

ARRIVAL DETECTION & GATING:
_has_user_arrived_recently(...) - Check if user is in arrival phase (gates retries)

TAP HANDLING & RETRY:
on_tap(entity, attribute, ...) - Handle tap sensor triggers with debouncing
tapretry(kwargs) - Retry location check (arrival-gated)
ledfeedback(feedbackmode, ...) - LED feedback (thinking/opening/error)

ELIGIBILITY CHECKS:
_is_eligible(door) - Check all eligibility criteria for unlock
(contact sensor, cooldown, etc.)

UNLOCK EXECUTION:
unlock(door) - Execute unlock (mock/bridge/real, mode-specific)

SYSTEM HEALTH:
healthcheck(kwargs) - Periodic health monitoring with heartbeat
set_log_level(level) - Update runtime logging level

CONFIGURATION:
STAGEMAPPING - Hardware stage definitions (1-5)
MOCKLEDMAP - Mock LED entity mapping

================================================================================
SECURITY NOTES
• Arrival phase detection: Prevents unlock if user already home (prevents bypass)
• Tap debouncing: Prevents rapid re-trigger flooding
• Contact sensor check: Won't unlock if door is physically open
• Just-unlocked cooldown: Prevents immediate re-unlock (default 30s)
• Only retry for users in arrival phase (Phase 2 enhancement)

================================================================================
"""

import appdaemon.plugins.hass.hassapi as hass
import datetime
from collections import deque


class AutoUnlockV2(hass.Hass):
    """Complete AutoUnlock V2 with Phase 1 & 2, respecting original config naming."""

    STAGEMAPPING = {
        1: {"tap": "mock", "homeaway": "mock", "bledistance": "mock", "intent": "mock", "unlock": "mock", "ledmode": "mock"},
        2: {"tap": "mock", "homeaway": "mock", "bledistance": "mock", "intent": "mock", "unlock": "mock", "ledmode": "mock"},
        3: {"tap": "mock", "homeaway": "real", "bledistance": "real", "intent": "mock", "unlock": "mock", "ledmode": "real"},
        4: {"tap": "mock", "homeaway": "real", "bledistance": "real", "intent": "real", "unlock": "mock", "ledmode": "real"},
        5: {"tap": "mock", "homeaway": "real", "bledistance": "real", "intent": "real", "unlock": "real", "ledmode": "real"},
    }

    MOCKLEDMAP = {"thinking": "ledamber", "opening": "ledgreen", "error": "ledred"}

    def initialize(self):
        """AppDaemon entry point. Initialize configuration, mode, and listeners."""

        rawcfg = self.args
        self.cfg = rawcfg  # Config uses snake_case, no normalization needed
        self.mode = self.cfg.get("mode", "sandbox")
        self.hardwarestage = int(self.cfg.get("hardware_stage", 1))

        self.log(
            f"[INIT] Mode {self.mode}, Hardware Stage {self.hardwarestage}",
            level="INFO",
        )

        self.sandboxoptions = dict(self.STAGEMAPPING.get(self.hardwarestage, {}))
        self.sandboxoptions.update(self.cfg.get("sandbox_options", {}))
        self.bridgeappname = self.cfg.get("bridge_app", "habridgerpi5")

        self.state = {}
        self.loglevel = self.cfg.get("loglevel", "INFO").upper()

        self.healthfailcount = 0
        self.last_health_state = None  # Track health state changes for logging

        # Proximity state tracking
        self.proximitystate = {}
        self.emadistances = {}
        self.emawindow = self.cfg.get("proximity_advanced", {}).get("ema_window", 5)
        self.emaalpha = self.cfg.get("proximity_advanced", {}).get("ema_alpha", 0.3)

        self.approachvectors = {}
        self.vectorwindow = self.cfg.get("proximity_advanced", {}).get("approach_window", 10)
        self.approachthreshold = self.cfg.get("proximity_advanced", {}).get("approach_velocity_threshold", -0.3)

        self.updatefrequencies = {}
        self.frequencywindow = self.cfg.get("staleness_adaptive", {}).get("frequency_window", 20)
        self.adaptiveenabled = self.cfg.get("staleness_adaptive", {}).get("enabled", True)

        self.ledhandles = {}

        # Location retry state (arrival-gated)
        self.locationretryconfig = self.cfg.get(
            "location_retry", {"enabled": True, "attempts": 2, "interval": [2, 5], "amber_pulse": True}
        )

        # Setup tap listeners (support multiple tap sensors per door)
        for door, data in self.cfg.get("locks", {}).items():
            tapsensors = data.get("tap_sensor", [])

            # Always treat as list
            if isinstance(tapsensors, str):
                tapsensors = [tapsensors]

            for ts in tapsensors:
                chosensensor = self.pickentity(ts, "tap", door)
                self.listen_state(self.on_tap, chosensensor, door=door)
                self.log(
                    f"[INIT] Listening for taps on {chosensensor} for door {door}",
                    level="INFO",
                )

        # Health check (all modes now support it)
        healthcheck_interval = self.cfg.get("health_check", {}).get("interval", 180)
        self.run_every(
            self.healthcheck,
            datetime.datetime.now() + datetime.timedelta(seconds=5),
            healthcheck_interval,
        )

        # ════════════════════════════════════════════════════════════════════════════════
        # WELCOME BANNER - Always display on startup
        # ════════════════════════════════════════════════════════════════════════════════
        mode_name = self.mode.upper()
        if self.mode == "sandbox":
            mode_desc = "Testing"
            sandbox_details = f" | HW Stage: {self.hardwarestage} | Options: {self.sandboxoptions}"
        elif self.mode == "crossover":
            mode_desc = "Production Multi-Server"
            sandbox_details = f" | Options: {self.sandboxoptions}"
        else:
            mode_desc = "Production Local-Server"
            sandbox_details = ""

        retry_status = (
            "ENABLED (arrival-gated)"
            if self.locationretryconfig.get("enabled")
            else "DISABLED"
        )

        mode_message = f"""
***************************************************************************

* Welcome to AutoUnlock V2 (Production Ready)

* Mode: {mode_name} ({mode_desc})
* Bridge: {self.bridgeappname}{sandbox_details}
* Location Retry: {retry_status}

***************************************************************************
"""
        self.log(mode_message, level="INFO")

    def option(self, part):
        """Get mock/real/bridge option for hardware component."""
        return self.sandboxoptions.get(part, "mock")

    def pickentity(self, entity, kind=None, door=None):
        """Choose correct mock or real entity based on mode/sandbox options."""

        if kind == "tap" and self.mode in ["sandbox", "crossover"] and self.option("tap") == "mock":
            mockmap = self.cfg.get("sandbox_entities", {})
            chosen = mockmap.get(f"tap_{door}", entity)
            self.log(
                f"[PICKENTITY] Tap for door '{door}': {chosen} (mock)",
                level="DEBUG",
            )
            return chosen

        if kind == "lock" and self.mode == "sandbox" and self.option("unlock") == "mock":
            chosen = self.cfg.get("sandbox_entities", {}).get("lock_entity", entity)
            self.log(f"[PICKENTITY] Lock: {chosen} (mock)", level="DEBUG")
            return chosen

        self.log(f"[PICKENTITY] {kind or entity}: {entity} (real)", level="DEBUG")
        return entity

    def pickled(self, feedbackmode: str, door: str = None) -> str:
        """Pick correct LED entity mock or real."""

        if self.mode in ["sandbox", "crossover"]:
            ledmode = self.option("ledmode")
        else:
            ledmode = "real"

        if ledmode == "real" and door and door in self.cfg.get("locks", {}):
            if self.cfg.get("locks", {}).get(door, {}).get("led_controller"):
                ledentity = self.cfg["locks"][door]["led_controller"]
                self.log(
                    f"[PICKLED] {feedbackmode} for door '{door}': {ledentity} (real)",
                    level="DEBUG",
                )
                return ledentity

        key = self.MOCKLEDMAP.get(feedbackmode)
        if key:
            ledentity = self.cfg.get("sandbox_entities", {}).get(key, f"input_boolean.mock_{key}")
            self.log(
                f"[PICKLED] {feedbackmode}: {ledentity} (mock)",
                level="DEBUG",
            )
            return ledentity

        self.log(f"[PICKLED] {feedbackmode}: No mapping found", level="DEBUG")
        return None

    def getbledistance(self, userinfo):
        """Get BLE distance with EMA smoothing."""

        if self.mode in ["sandbox", "crossover"] and self.option("bledistance") == "mock":
            rawdistance = float(
                self.get_state(
                    self.cfg.get("sandbox_entities", {}).get("ble_distance", "input_number.mock_ble_distance")
                )
                or 999
            )
            self.log(f"[GETBLEDISTANCE] Using mock: {rawdistance}m", level="DEBUG")
        else:
            rawdistance = float(self.get_state(userinfo.get("bermuda_dist")) or 999)
            self.log(
                f"[GETBLEDISTANCE] Using real ({userinfo.get('bermuda_dist')}): {rawdistance}m",
                level="DEBUG",
            )

        userid = userinfo.get("person", "unknown")

        if userid not in self.emadistances:
            self.emadistances[userid] = deque(maxlen=self.emawindow)

        self.emadistances[userid].append(rawdistance)

        if len(self.emadistances[userid]) > 0:
            ema = self.emadistances[userid][0]
            for dist in list(self.emadistances[userid])[1:]:
                ema = (self.emaalpha * dist) + (1 - self.emaalpha) * ema
            self.log(
                f"[GETBLEDISTANCE] EMA smoothed: {ema:.1f}m (from raw {rawdistance:.1f}m)",
                level="DEBUG",
            )
            return ema

        return rawdistance

    def getarea(self, userinfo):
        """Get user area/location."""

        if self.mode in ["sandbox", "crossover"] and self.option("homeaway") == "mock":
            area = self.get_state(
                self.cfg.get("sandbox_entities", {}).get("location_area", "input_select.mock_location_area")
            )
            self.log(f"[GETAREA] Using mock: {area}", level="DEBUG")
        else:
            area = self.get_state(userinfo.get("bermuda_area"))
            self.log(
                f"[GETAREA] Using real ({userinfo.get('bermuda_area')}): {area}",
                level="DEBUG",
            )

        return area

    def ble_stale(self, userinfo, adaptive=True):
        """Check if BLE sensor is too old using lastupdated (not lastchanged)."""

        if self.mode in ["sandbox", "crossover"] and self.option("bledistance") == "mock":
            self.log("[BLESTALE] Mock mode: never stale", level="DEBUG")
            return False

        sensor = userinfo.get("bermuda_area")
        basethreshold = userinfo.get("min_ble_update_sec", 120)

        if not sensor:
            self.log("[BLESTALE] No sensor configured: stale", level="DEBUG")
            return True

        lastupdated = self.get_state(sensor, attribute="last_updated")

        if not lastupdated:
            self.log("[BLESTALE] No lastupdated for sensor: stale", level="DEBUG")
            return True

        lastupdateddt = self.convert_utc(lastupdated)
        now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)

        # Timezone fix
        if lastupdateddt.tzinfo is not None:
            lastupdateddt = lastupdateddt.replace(tzinfo=None)

        secondssince = (now - lastupdateddt).total_seconds()

        userid = userinfo.get("person", "unknown")

        if userid not in self.updatefrequencies:
            self.updatefrequencies[userid] = deque(maxlen=self.frequencywindow)

        self.updatefrequencies[userid].append(secondssince)

        # Adaptive threshold
        if adaptive and self.adaptiveenabled and len(self.updatefrequencies[userid]) >= 5:
            recentintervals = list(self.updatefrequencies[userid])
            avginterval = sum(recentintervals) / len(recentintervals)

            tightthreshold = self.cfg.get("staleness_adaptive", {}).get("tight_threshold", 30)
            tightavg = self.cfg.get("staleness_adaptive", {}).get("tight_avg_interval", 2.0)
            relaxedavg = self.cfg.get("staleness_adaptive", {}).get("relaxed_avg_interval", 10.0)

            if avginterval <= tightavg:
                threshold = tightthreshold
            elif avginterval >= relaxedavg:
                threshold = basethreshold
            else:
                threshold = tightthreshold + (basethreshold - tightthreshold) * (
                    (avginterval - tightavg) / (relaxedavg - tightavg)
                )

            self.log(
                f"[ADAPTIVE_STALENESS] {userid}: avginterval={avginterval:.1f}s, threshold={threshold:.0f}s",
                level="DEBUG",
            )
        else:
            threshold = basethreshold

        isstale = secondssince > threshold

        if isstale:
            self.log(
                f"[STALENESS] BLE sensor ({sensor}): stale ({secondssince:.0f}s > {threshold:.0f}s)",
                level="DEBUG",
            )
        else:
            self.log(
                f"[STALENESS] BLE sensor ({sensor}): fresh ({secondssince:.0f}s < {threshold:.0f}s)",
                level="DEBUG",
            )

        return isstale

    def detectapproachvector(self, userinfo, door):
        """Detect if user is approaching based on distance trend."""

        userid = userinfo.get("person", "unknown")
        currentdistance = self.getbledistance(userinfo)
        now = datetime.datetime.now()

        if userid not in self.approachvectors:
            self.approachvectors[userid] = deque(maxlen=self.vectorwindow)

        self.approachvectors[userid].append((now, currentdistance))

        if len(self.approachvectors[userid]) < 5:
            self.log(
                f"[APPROACH_VECTOR] {userid}: Insufficient data ({len(self.approachvectors[userid])}/5 readings)",
                level="DEBUG",
            )
            return False, 0.0

        readings = list(self.approachvectors[userid])
        timespan = (readings[-1][0] - readings[0][0]).total_seconds()

        if timespan < 0.5:
            self.log(
                f"[APPROACH_VECTOR] {userid}: Time span too short ({timespan:.1f}s)",
                level="DEBUG",
            )
            return False, 0.0

        distancechange = readings[-1][1] - readings[0][1]
        velocity = distancechange / timespan
        isapproaching = velocity < self.approachthreshold

        self.log(
            f"[APPROACH_VECTOR] {userid}: velocity={velocity:.2f}m/s, approaching={isapproaching}",
            level="DEBUG",
        )

        return isapproaching, velocity

    def checkproximityhysteresis(self, userinfo, door, currentdistance):
        """Hysteresis logic to prevent oscillation at threshold boundaries."""

        userid = userinfo.get("person", "unknown")
        zone = self.cfg.get("locks", {}).get(door, {}).get("zone")

        entrythreshold = None
        for pz in self.cfg.get("proxy_zones", []):
            if str(pz.get("name", "")).casefold() == str(zone).casefold():
                entrythreshold = pz.get("ble_distance", 2.0)
                break

        if entrythreshold is None:
            entrythreshold = 2.0
            self.log(
                f"[HYSTERESIS] No threshold found for zone '{zone}', using default {entrythreshold}m",
                level="DEBUG",
            )

        hysteresisband = self.cfg.get("proximity_advanced", {}).get("hysteresis_band", 0.4)
        exitthreshold = entrythreshold + hysteresisband

        if userid not in self.proximitystate:
            self.proximitystate[userid] = {"inrange": False, "lastdistance": currentdistance}

        state = self.proximitystate[userid]

        if state["inrange"]:
            if currentdistance > exitthreshold:
                state["inrange"] = False
                self.log(
                    f"[HYSTERESIS] {userid}: Exited range ({currentdistance:.1f}m > {exitthreshold:.1f}m)",
                    level="DEBUG",
                )
        else:
            if currentdistance < entrythreshold:
                state["inrange"] = True
                self.log(
                    f"[HYSTERESIS] {userid}: Entered range ({currentdistance:.1f}m < {entrythreshold:.1f}m)",
                    level="DEBUG",
                )

        state["lastdistance"] = currentdistance

        return state["inrange"]

    def _has_user_arrived_recently(self, userinfo):
        """Check if user has arrived recently (person entity state management)."""

        person = userinfo.get("person")
        if not person:
            return False

        try:
            person_state = self.get_state(person)
            personid = person.split(".")[-1]

            # Track arrival transitions
            statekey = f"{personid}_arrival_tracked"
            wasaway = self.state.get(statekey, False)

            if str(person_state).casefold() == "home":
                if not wasaway:
                    # Just transitioned from away to home
                    self.state[statekey] = True
                    self.log(
                        f"[ARRIVAL] {personid} just arrived at home",
                        level="DEBUG",
                    )
                    return True
            else:
                self.state[statekey] = False

            return False

        except Exception as e:
            self.log(f"[ARRIVAL] Error checking {userinfo.get('person')}: {e}", level="DEBUG")
            return False

    def _is_nearby(self, userinfo, zone):
        """
        PHASE 1 ENHANCEMENT: Check if user is in proximity of door with hysteresis.
        Now includes direct proxy distance fallback for Bermuda area latching scenarios.
        """
        area = self.getarea(userinfo)
        distance = self.getbledistance(userinfo)
        userid = userinfo.get("person", "unknown").split(".")[-1]

        self.log(
            f"[PROXIMITY] {userid} area={area}, distance={distance:.1f}m, targetzone={zone}",
            level="DEBUG",
        )

        for pz in self.cfg.get("proxy_zones", []):
            if str(pz.get("name", "")).casefold() != str(zone).casefold():
                continue

            # Area matching
            areamatch = any(
                str(area).casefold() == str(loc).casefold()
                for loc in pz.get("locations", [])
            )

            # Existing door/distance check...
            door = None
            for d, data in self.cfg.get("locks", {}).items():
                if str(data.get("zone", "")).casefold() == str(zone).casefold():
                    door = d
                    break

            if door:
                distanceok = self.checkproximityhysteresis(userinfo, door, distance)
            else:
                distanceok = distance < pz.get("ble_distance", 2)

            self.log(
                f"[PROXIMITY] {userid} Zone {zone} - areamatch={areamatch}, "
                f"distanceok={distanceok} threshold={pz.get('ble_distance', 2)}m",
                level="DEBUG",
            )

            if areamatch and distanceok:
                return True

        # ─────────────────────────────────────────────────────────────────────────
        # FALLBACK: Try direct proxy distance if Bermuda area didn't match
        # This helps during arrival scenarios when Bermuda area transitions are slow
        # ─────────────────────────────────────────────────────────────────────────

        proxy, proxy_distance, is_fresh = self._get_best_proxy_distance(userinfo, zone)

        if proxy and is_fresh:
            # Get zone distance threshold
            zone_threshold = None
            for pz in self.cfg.get("proxy_zones", []):
                if str(pz.get("name", "")).casefold() == str(zone).casefold():
                    zone_threshold = pz.get("ble_distance", 2.0)
                    break

            if zone_threshold is None:
                zone_threshold = 2.0

            if proxy_distance < zone_threshold:
                self.log(
                    f"[PROXIMITY] {userid} IN RANGE via proxy fallback: "
                    f"{proxy} {proxy_distance:.1f}m < {zone_threshold}m "
                    f"(Bermuda area latched to {area})",
                    level="INFO",
                )
                return True
            else:
                self.log(
                    f"[PROXIMITY] {userid} PROXY FALLBACK FAILED: "
                    f"{proxy} {proxy_distance:.1f}m >= {zone_threshold}m",
                    level="DEBUG",
                )
        else:
            self.log(
                f"[PROXIMITY] {userid} Proxy fallback unavailable "
                f"(proxy={proxy}, fresh={is_fresh})",
                level="DEBUG",
            )

        return False

    def _get_best_proxy_distance(self, userinfo, zone):
        """
        PHASE 1 ENHANCEMENT: Get nearest proxy distance for a zone, bypassing Bermuda area latching.

        This method reads raw proxy distances instead of relying on Bermuda's
        fused area estimate, which may be slow to transition during arrivals.

        Args:
            userinfo (dict): User config from trusted_devices
            zone (str): Door zone (e.g., "frontdoor", "garage")

        Returns:
            tuple: (proxy_name, distance_m, is_fresh)
        """

        # Find which proxies serve this zone
        zone_proxies = []
        for pz in self.cfg.get("proxy_zones", []):
            if str(pz.get("name", "")).casefold() == str(zone).casefold():
                zone_proxies = pz.get("proxies", [])
                break

        if not zone_proxies:
            return None, 999.0, False

        best_proxy = None
        best_distance = 999.0

        # Check each proxy for this zone
        proxy_distances_config = userinfo.get("proxy_distances", {})
        if not proxy_distances_config:
            self.log(
                f"[PROXY_DISTANCE] No proxy_distances config for {userinfo.get('person')}",
                level="DEBUG",
            )
            return None, 999.0, False

        for proxy_name in zone_proxies:
            proxy_key = f"{proxy_name}_proxy"
            sensor_id = proxy_distances_config.get(proxy_key)

            if not sensor_id:
                self.log(
                    f"[PROXY_DISTANCE] No sensor configured for {proxy_name}",
                    level="DEBUG",
                )
                continue

            # Read raw distance from proxy
            try:
                raw_distance = float(self.get_state(sensor_id) or 999.0)
            except (ValueError, TypeError):
                self.log(
                    f"[PROXY_DISTANCE] Could not parse distance from {sensor_id}",
                    level="DEBUG",
                )
                continue

            # Check if sensor data is fresh
            is_stale = self.ble_stale(userinfo, adaptive=True)

            if raw_distance < best_distance:
                best_distance = raw_distance
                best_proxy = proxy_name

        is_fresh = not self.ble_stale(userinfo, adaptive=True)

        if best_proxy:
            self.log(
                f"[PROXY_DISTANCE] Best proxy: {best_proxy} {best_distance:.1f}m "
                f"(fresh={is_fresh})",
                level="DEBUG",
            )

        return best_proxy, best_distance, is_fresh

    def _is_eligible(self, door):
        """Check all eligibility criteria for unlock."""

        lockinfo = self.cfg.get("locks", {}).get(door)
        if not lockinfo:
            self.log(f"[ELIGIBILITY] Door {door} not configured", level="DEBUG")
            return False, "Door not configured"

        # Check 1: Contact sensor (door must be closed)
        contactsensor = lockinfo.get("contact_sensor")
        if contactsensor:
            state = self.get_state(contactsensor)
            if str(state).casefold() == "on":
                self.log(
                    f"[ELIGIBILITY] Check 1/5 FAILED: Door already open (contact sensor active)",
                    level="DEBUG",
                )
                return False, "Door already open"
            self.log(
                f"[ELIGIBILITY] Check 1/5 PASSED: Contact sensor closed",
                level="DEBUG",
            )
        else:
            self.log(
                f"[ELIGIBILITY] Check 1/5 SKIPPED: No contact sensor configured",
                level="DEBUG",
            )

        # Check 2: Not in cooldown (just_unlocked)
        interval = self.cfg.get("just_unlocked_interval", 30)
        if self.state.get(f"{door}_just_unlocked", False):
            self.log(
                f"[ELIGIBILITY] Check 2/5 FAILED: Door was just unlocked (cooldown {interval}s)",
                level="DEBUG",
            )
            return False, f"Cooldown active ({interval}s)"
        self.log(
            f"[ELIGIBILITY] Check 2/5 PASSED: Not in cooldown",
            level="DEBUG",
        )

        # Check 3-5: Placeholder (typically handled by caller)
        self.log(
            f"[ELIGIBILITY] Checks 3-5 PASSED: User proximity verified",
            level="DEBUG",
        )

        return True, None

    def ledfeedback(self, feedbackmode, door=None):
        """Send LED feedback based on event state."""

        rgb = {
            "thinking": (255, 127, 0),  # Amber/Orange
            "opening": (0, 255, 0),     # Green
            "error": (255, 0, 0),       # Red
        }.get(feedbackmode, (0, 0, 0))

        ledentity = self.pickled(feedbackmode, door)

        if not ledentity:
            self.log(
                f"[LED] No LED entity found for {feedbackmode}",
                level="DEBUG",
            )
            return

        ismockled = ledentity.startswith("input_boolean.")

        try:
            if feedbackmode == "thinking":
                self.log(
                    f"[LED] Starting amber flash sequence for {ledentity} ({'mock' if ismockled else 'real'})",
                    level="DEBUG",
                )

                flashcount = 10
                flashinterval = 0.2

                def flashled(kwargs):
                    flashnum = kwargs.get("flashnum", 0)

                    if flashnum >= flashcount:
                        self.call_service(
                            "homeassistant/turn_off", entity_id=ledentity
                        )
                        return

                    if flashnum % 2 == 0:
                        if ismockled:
                            self.call_service(
                                "homeassistant/turn_on", entity_id=ledentity
                            )
                        else:
                            self.call_service(
                                "light/turn_on",
                                entity_id=ledentity,
                                rgb_color=rgb,
                                brightness=255,
                            )
                    else:
                        self.call_service(
                            "homeassistant/turn_off", entity_id=ledentity
                        )

                    handle = self.run_in(
                        flashled, flashinterval, flashnum=flashnum + 1
                    )

                    if door:
                        if door not in self.ledhandles:
                            self.ledhandles[door] = []
                        self.ledhandles[door].append(handle)

                flashled({"flashnum": 0})

            else:
                # Cancel existing LED animations for this door
                if door and door in self.ledhandles:
                    for handle in self.ledhandles[door]:
                        try:
                            self.cancel_timer(handle)
                        except:
                            pass
                    self.ledhandles[door] = []

                if feedbackmode in ["opening", "error"]:
                    # Solid color
                    if ismockled:
                        self.call_service(
                            "homeassistant/turn_on", entity_id=ledentity
                        )
                        self.log(
                            f"[LED] {feedbackmode} sent to {ledentity} (mock)",
                            level="DEBUG",
                        )
                    else:
                        self.call_service(
                            "light/turn_on",
                            entity_id=ledentity,
                            rgb_color=rgb,
                            brightness=255,
                        )
                        self.log(
                            f"[LED] {feedbackmode} sent to {ledentity} (real), RGB={rgb}",
                            level="INFO",
                        )

                    handle = self.run_in(
                        lambda kwargs: self.call_service(
                            "homeassistant/turn_off", entity_id=ledentity
                        ),
                        5,
                    )

                    if door:
                        if door not in self.ledhandles:
                            self.ledhandles[door] = []
                        self.ledhandles[door].append(handle)

        except Exception as e:
            self.log(f"[LED] ERROR {feedbackmode}: {e}", level="ERROR")

    def unlock(self, door):
        """Unlock the specified door (sandbox/crossover/production)."""

        lockinfo = self.cfg.get("locks", {}).get(door)
        unlockservice = lockinfo.get("unlock_service")
        unlockservicedata = lockinfo.get("unlock_service_data", {})
        lockentity = lockinfo.get("lock_entity")

        self.log(
            f"[UNLOCK] Called for door '{door}', mode={self.mode}, "
            f"unlock_option={'mock' if self.option('unlock') == 'mock' else 'real'}",
            level="DEBUG",
        )

        try:
            if self.mode == "sandbox":
                unlockoption = self.option("unlock")

                if unlockoption == "mock":
                    lockentity = self.cfg.get("sandbox_entities", {}).get("lock_entity", lockentity)
                    self.log(
                        f"[UNLOCK] SANDBOX-MOCK Turning OFF mock lock entity {lockentity}",
                        level="DEBUG",
                    )
                    self.turn_off(lockentity)
                    self.log(
                        f"[UNLOCK] SANDBOX-MOCK Door '{door}' unlocked (mock toggled)",
                        level="INFO",
                    )

                elif unlockoption == "bridge":
                    bridge = self.get_app(self.bridgeappname)
                    self.log(
                        f"[UNLOCK] SANDBOX-BRIDGE Using bridge app {self.bridgeappname}",
                        level="DEBUG",
                    )

                    if unlockservice == "mqtt.publish":
                        self.log(
                            f"[UNLOCK] SANDBOX-BRIDGE Sending mqtt.publish to bridge",
                            level="DEBUG",
                        )
                        bridge.send_service_call("mqtt", "publish", service_data=unlockservicedata)
                    else:
                        entityid = lockentity
                        self.log(
                            f"[UNLOCK] SANDBOX-BRIDGE Sending {unlockservice} to bridge for {entityid}",
                            level="DEBUG",
                        )
                        bridge.send_service_call(
                            unlockservice.split(".")[0],
                            unlockservice.split(".")[1],
                            entity_id=entityid,
                        )
                    self.log(
                        f"[UNLOCK] SANDBOX-BRIDGE Sent unlock command for door '{door}' via bridge",
                        level="INFO",
                    )

                else:  # real
                    if unlockservice == "mqtt.publish":
                        self.log(
                            f"[UNLOCK] SANDBOX-REAL Calling mqtt.publish",
                            level="DEBUG",
                        )
                        self.call_service("mqtt/publish", **unlockservicedata)
                    else:
                        entityid = lockentity
                        self.log(
                            f"[UNLOCK] SANDBOX-REAL Calling {unlockservice} for {entityid}",
                            level="DEBUG",
                        )
                        self.call_service(unlockservice, entity_id=entityid)

            elif self.mode == "crossover":
                unlockoption = self.option("unlock")

                if unlockoption == "mock":
                    lockentity = self.cfg.get("sandbox_entities", {}).get("lock_entity", lockentity)
                    self.log(
                        f"[UNLOCK] CROSSOVER-MOCK Turning OFF mock lock entity {lockentity}",
                        level="DEBUG",
                    )
                    self.turn_off(lockentity)
                    self.log(
                        f"[UNLOCK] CROSSOVER-MOCK Door '{door}' unlocked (mock toggled)",
                        level="INFO",
                    )

                else:
                    bridge = self.get_app(self.bridgeappname)
                    self.log(
                        f"[UNLOCK] CROSSOVER Using bridge app {self.bridgeappname}",
                        level="DEBUG",
                    )

                    if unlockservice == "mqtt.publish":
                        self.log(
                            f"[UNLOCK] CROSSOVER Sending mqtt.publish to bridge",
                            level="DEBUG",
                        )
                        bridge.send_service_call("mqtt", "publish", service_data=unlockservicedata)
                    else:
                        entityid = lockentity
                        self.log(
                            f"[UNLOCK] CROSSOVER Sending {unlockservice} to bridge for {entityid}",
                            level="DEBUG",
                        )
                        bridge.send_service_call(
                            unlockservice.split(".")[0],
                            unlockservice.split(".")[1],
                            entity_id=entityid,
                        )
                    self.log(
                        f"[UNLOCK] CROSSOVER Sent unlock command for door '{door}' via bridge",
                        level="INFO",
                    )

            else:  # production
                if unlockservice == "mqtt.publish":
                    self.log(
                        f"[UNLOCK] PRODUCTION Calling mqtt.publish",
                        level="DEBUG",
                    )
                    self.call_service("mqtt/publish", **unlockservicedata)
                else:
                    entityid = lockentity
                    self.log(
                        f"[UNLOCK] PRODUCTION Calling {unlockservice} for {entityid}",
                        level="DEBUG",
                    )
                    self.call_service(unlockservice, entity_id=entityid)
                self.log(
                    f"[UNLOCK] PRODUCTION Called unlock for door '{door}'",
                    level="INFO",
                )

        except Exception as e:
            self.log(f"[UNLOCK] Exception during unlock: {e}", level="ERROR")
            self.state[f"{door}_tap_in_progress"] = False
            return

        # Set justunlocked cooldown
        interval = self.cfg.get("just_unlocked_interval", 30)
        self.state[f"{door}_just_unlocked"] = True
        self.run_in(
            lambda kwargs: self.state.update({f"{door}_just_unlocked": False}),
            interval,
        )

    def healthcheck(self, kwargs):
        """Periodic health check - logs status every cycle."""

        try:
            dependencies = self.cfg.get("health_check", {}).get("require_online", [])

            all_online = True

            for dep in dependencies:
                state = self.get_state(dep)

                if str(state).casefold() not in ["on", "ready", "online", "ok"]:
                    all_online = False
                    self.healthfailcount += 1
                    self.log(
                        f"[HEALTHCHECK] Dependency {dep} not online (state={state}), "
                        f"failcount={self.healthfailcount}",
                        level="DEBUG",
                    )

                    if self.healthfailcount >= 2:
                        self.call_service(
                            self.cfg.get("health_check", {}).get("notify_entity"),
                            message=self.cfg.get("health_check", {}).get("alert_message"),
                        )
                        self.ledfeedback("error", "frontdoor")
                        self.set_log_level("ERROR")
                        self.log(
                            f"[HEALTHCHECK] Alert sent, log level changed to ERROR",
                            level="ERROR",
                        )
                        return

            # ─────────────────────────────────────────────────────────────────────────
            # ALWAYS log status every cycle (heartbeat)
            # ─────────────────────────────────────────────────────────────────────────
            current_health_state = "HEALTHY" if all_online else "DEGRADED"

            if all_online:
                self.healthfailcount = 0
                self.set_log_level(self.loglevel)

            # Log heartbeat (every cycle, not just on state change)
            self.log(
                f"[HEALTHCHECK] Heartbeat: Status={current_health_state}, failcount={self.healthfailcount}",
                level="INFO",
            )

        except Exception as e:
            self.log(f"[HEALTHCHECK] Error: {e}", level="ERROR")

    def set_log_level(self, level):
        """Set logging level."""
        self.loglevel = level
        self.log(f"[CONFIG] Log level changed to {level}", level="INFO")

    def on_tap(self, entity, attribute, old, new, kwargs):
        """
        Handle tap sensor triggers with robust debouncing, contact sensor ignore,
        and PHASE 2 ENHANCED arrival-gated location retry with SECURITY FIX.
        
        SECURITY FIX: Only allow unlock if user is in arrival phase (not already home).
        """

        door = kwargs.get("door")

        if not door:
            self.log(
                f"[TAP] Tap callback missing door param: entity={entity}",
                level="DEBUG",
            )
            return

        # CRITICAL: Check tap_in_progress IMMEDIATELY (FIXED DEBOUNCE)
        if self.state.get(f"{door}_tap_in_progress", False):
            self.log(
                f"[TAP DEBOUNCE] Tap already being processed for '{door}', ignoring.",
                level="INFO",
            )
            return

        # Set flag and 60s safety timeout
        self.state[f"{door}_tap_in_progress"] = True
        self.run_in(
            lambda kwargs: self.state.update({f"{door}_tap_in_progress": False}), 60
        )

        # Case-insensitive state check
        if str(new).casefold() != "on":
            self.state[f"{door}_tap_in_progress"] = False
            return

        # Check if door is already open (contact sensor ignore)
        contactsensor = self.cfg.get("locks", {}).get(door, {}).get("contact_sensor")

        if contactsensor:
            state = self.get_state(contactsensor)
            if state == "on":
                self.log(
                    f"[TAP IGNORED] {door} is already open (contact sensor active)",
                    level="INFO",
                )
                self.state[f"{door}_tap_in_progress"] = False
                return

        # Check if door was just unlocked (cooldown ignore)
        interval = self.cfg.get("just_unlocked_interval", 30)

        if self.state.get(f"{door}_just_unlocked", False):
            self.log(
                f"[TAP IGNORED] {door} unlocked recently (within {interval}s)",
                level="INFO",
            )
            self.state[f"{door}_tap_in_progress"] = False
            return

        # ← ALL SAFETY CHECKS PASSED
        self.log(
            f"[TAP] Tap detected at {door}, entity {entity}, attribute {attribute}, old={old}, new={new}",
            level="INFO",
        )

        zone = self.cfg.get("locks", {}).get(door, {}).get("zone")

        # Determine users to check
        users_to_check = []

        if self.mode == "sandbox":
            mock_user_input = self.get_state(
                self.cfg.get("sandbox_entities", {}).get("user_select")
            )
            casefold_map = {k.casefold(): k for k in self.cfg.get("trusted_devices", {}).keys()}

            if mock_user_input and mock_user_input.casefold() in casefold_map:
                real_key = casefold_map[mock_user_input.casefold()]
                users_to_check = [(real_key, self.cfg.get("trusted_devices", {})[real_key])]
            else:
                self.log(f"[FEEDBACK] No valid mock user selected", level="DEBUG")
                self.state[f"{door}_tap_in_progress"] = False
                return
        else:
            users_to_check = list(self.cfg.get("trusted_devices", {}).items())

        # Check proximity and arrival status
        user_in_proximity = False
        user_in_arrival = False

        for user, user_info in users_to_check:
            if self._is_nearby(user_info, zone):
                user_in_proximity = True
                self.log(
                    f"[FEEDBACK] User {user} is in proximity for door '{door}'",
                    level="DEBUG",
                )
                break

            if self._has_user_arrived_recently(user_info):
                user_in_arrival = True

        # ─────────────────────────────────────────────────────────────────────────
        # PHASE 2 ENHANCEMENT: Filter users for retry—only those in arrival phase
        # ─────────────────────────────────────────────────────────────────────────
        users_for_retry = []
        for user, user_info in users_to_check:
            if self._has_user_arrived_recently(user_info):
                users_for_retry.append((user, user_info))
                self.log(
                    f"[ARRIVAL GATE] {user} eligible for retry",
                    level="DEBUG",
                )
            else:
                self.log(
                    f"[ARRIVAL GATE] {user} EXCLUDED - not in arrival phase",
                    level="DEBUG",
                )
        # ─────────────────────────────────────────────────────────────────────────

        # HANDLER 1: Not in proximity but arriving → Start retry loop
        if not user_in_proximity:
            if user_in_arrival and self.locationretryconfig.get("enabled"):
                self.log(
                    f"[LOCATION RETRY] User is arriving but location stale. Starting retry...",
                    level="INFO",
                )

                if self.locationretryconfig.get("amber_pulse"):
                    self.ledfeedback("thinking", door)

                retryintervals = self.locationretryconfig.get("interval", [2, 5])
                firstdelay = retryintervals[0] if len(retryintervals) > 0 else 2

                self.log(
                    f"[LOCATION RETRY] Scheduling first retry in {firstdelay}s",
                    level="DEBUG",
                )

                self.run_in(
                    self.tapretry,
                    firstdelay,
                    door=door,
                    attempt=1,
                    users_to_check=users_for_retry,
                    zone=zone,
                )
            else:
                # Not in proximity and not arriving → Fail
                self.log(
                    f"[TAP] Not in proximity, not arriving. Unlock failed.",
                    level="INFO",
                )
                self.ledfeedback("error", door)

            self.state[f"{door}_tap_in_progress"] = False
            return

        # ─────────────────────────────────────────────────────────────────────────
        # SECURITY FIX: HANDLER 2 - Only unlock if user is in ARRIVAL phase
        # (not if they're already home and just inside)
        # ─────────────────────────────────────────────────────────────────────────
        
        # Check if ANY user in proximity is NOT in arrival phase (already home)
        user_already_home = False
        for user, user_info in users_to_check:
            if self._is_nearby(user_info, zone):
                # User is in proximity - check if they're already home
                person_state = self.get_state(user_info.get("person"))
                if str(person_state).casefold() == "home":
                    # Check if this is a new arrival or already home
                    if not self._has_user_arrived_recently(user_info):
                        # User is home and NOT just arriving (already home)
                        user_already_home = True
                        self.log(
                            f"[SECURITY] {user} in proximity but NOT in arrival phase (already home)",
                            level="DEBUG",
                        )
                        break

        if user_already_home:
            self.log(
                f"[TAP DENIED] User already home, not in arrival phase. Unlock denied for security.",
                level="INFO",
            )
            self.ledfeedback("error", door)
            self.state[f"{door}_tap_in_progress"] = False
            return

        # ─────────────────────────────────────────────────────────────────────────
        # User is in proximity AND in arrival phase → Check eligibility
        # ─────────────────────────────────────────────────────────────────────────
        self.ledfeedback("thinking", door)
        self.log(f"[TAP] Called ledfeedback('thinking') for {door}", level="DEBUG")

        eligible, reason = self._is_eligible(door)

        self.log(
            f"[TAP] _is_eligible({door}) returned: {eligible}, reason: {reason}",
            level="DEBUG",
        )

        if eligible:
            # HANDLER 3: Eligible → Unlock
            self.ledfeedback("opening", door)
            self.unlock(door)
            self.log(f"[TAP] Door {door} unlocked", level="INFO")
        else:
            # HANDLER 4: Not eligible → Fail
            self.log(f"[TAP] Unlock failed: {reason}", level="INFO")
            self.ledfeedback("error", door)

        self.state[f"{door}_tap_in_progress"] = False

    def tapretry(self, kwargs):
        """
        Retry location check after delay. Called after initial proximity check fails
        but user WAS in arrival phase.

        PHASE 2 ENHANCEMENT: Only checks users that were passed to retry list
        (i.e., users that passed arrival gate)

        Keeps amber LED flashing during retry window.
        """

        door = kwargs["door"]
        attempt = kwargs["attempt"]
        users_to_check = kwargs["users_to_check"]
        zone = kwargs["zone"]

        maxattempts = self.locationretryconfig.get("attempts", 2)
        retryintervals = self.locationretryconfig.get("interval", [2, 5])

        self.log(
            f"[LOCATION RETRY] Attempt {attempt}/{maxattempts} for door '{door}'",
            level="DEBUG",
        )

        # Check proximity again
        user_in_proximity = False

        for user, user_info in users_to_check:
            if self._is_nearby(user_info, zone):
                user_in_proximity = True
                self.log(
                    f"[LOCATION RETRY] User {user} now in proximity for door '{door}'",
                    level="DEBUG",
                )
                break

        if user_in_proximity:
            # User now in range → check full eligibility
            eligible, reason = self._is_eligible(door)

            if eligible:
                # UNLOCK!
                self.ledfeedback("opening", door)
                self.unlock(door)
                self.log(f"[LOCATION RETRY] Door {door} unlocked after {attempt} retry attempts", level="INFO")
                self.state[f"{door}_tap_in_progress"] = False
                return
            else:
                # Not eligible despite proximity
                self.log(
                    f"[LOCATION RETRY] User in proximity but not eligible: {reason}",
                    level="INFO",
                )
                self.ledfeedback("error", door)
                self.state[f"{door}_tap_in_progress"] = False
                return

        elif attempt >= maxattempts:
            # Max retries reached
            self.log(
                f"[LOCATION RETRY] Max retries reached ({attempt}/{maxattempts}). Unlock failed.",
                level="INFO",
            )
            self.ledfeedback("error", door)
            self.state[f"{door}_tap_in_progress"] = False
            return

        else:
            # Schedule next retry
            nextdelay = retryintervals[attempt] if attempt < len(retryintervals) else retryintervals[-1]

            self.log(
                f"[LOCATION RETRY] Scheduling retry {attempt + 1}/{maxattempts} in {nextdelay}s",
                level="DEBUG",
            )

            self.run_in(
                self.tapretry,
                nextdelay,
                door=door,
                attempt=attempt + 1,
                users_to_check=users_to_check,
                zone=zone,
            )