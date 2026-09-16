"""
Alarm App v2 for AppDaemon + Home Assistant.

A home security / automation controller that manages:
  • Mode lifecycle       (home → out → away, with auto-escalation)
  • Perimeter monitoring (building contacts/vibration, car doors/windows)
  • Camera threat sensing (Google Nest person detection)
  • Occupancy lighting   (data-driven schedules with randomisation)
  • Climate control      (Tado + Nest thermostat + hot water)
  • Notifications        (tiered: whisper → shout → scream, with cooldowns)

Architecture
────────────
All behaviour is driven by two pieces of state:
  1. **mode**     – home | out | away   (derived from presence + holiday sensors)
  2. **schedule** – season-aware time slots (sunrise, wakeup, sunset … nighttime)

When either changes, `_activate_mode()` tears down all prior listeners/timers
and rebuilds them from scratch.  Individual subsystems (perimeter, lighting,
climate, cameras) are pure functions of (mode, schedule) with no hidden state.

Key improvements over v1
────────────────────────
• Data-driven lighting: schedules live in YAML, not hard-coded if/elif blocks.
• Alert cooldowns: prevents notification floods from flapping sensors.
• Camera integration: Nest person-detection treated as a threat sensor.
• Snapshot capture: grabs a camera still on high-severity alerts.
• Typed schedule dict via dataclass for IDE support.
• Proper listener cleanup (no bare except).
• Consistent logging with structured context.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, time as dt_time
from typing import Any

import adbase as ad


# ─── Data Structures ────────────────────────────────────────────────────────

@dataclass
class Schedule:
    """Immutable snapshot of the current mode + season parameters."""
    mode: str
    season: str
    sunrise: str
    wakeup: str
    sunset: str
    evening: str
    bedtime: str
    nighttime: str

    def as_dict(self) -> dict[str, str]:
        return asdict(self)

    @property
    def title_mode(self) -> str:
        return self.mode.title()

    @property
    def title_season(self) -> str:
        return self.season.title()


# Alert severity tiers (lowest → highest)
SEVERITY_WHISPER = "whisper"
SEVERITY_SHOUT   = "shout"
SEVERITY_SCREAM  = "scream"


# ─── Main Application ───────────────────────────────────────────────────────

class AlarmApp(ad.ADBase):
    """AppDaemon app: whole-house security and automation controller."""

    # ── Initialisation ──────────────────────────────────────────────────────

    def initialize(self) -> None:
        """Bootstrap the app: load config, wire listeners, activate mode."""
        self.adbase = self.get_ad_api()
        self.hass   = self.get_plugin_api("HASS")
        self.mqtt   = self.get_plugin_api("MQTT")

        # Companion apps (optional — graceful if missing)
        self._access = self._get_companion("guest_access")
        self._au     = self._get_companion("auto_unlock")

        self._log_banner("Alarm App v2 starting")

        # ── Load configuration sections ──
        self._cfg_notif   = self.args["notification"]
        self._cfg_presence = self.args["presence"]
        self._cfg_car     = self.args.get("car", {})
        self._cfg_cameras = self.args.get("cameras", {})
        self._cfg_climate = self.args.get("climate", {})
        self._cfg_lights  = self.args.get("lights", {})
        self._cfg_autos   = self.args.get("managed_automations", {})

        self._summer_months: list[int] = self.args.get("summer_months", [5, 6, 7, 8, 9])
        self._schedules_cfg: dict      = self.args["schedules"]

        self._out_to_away_secs: int = int(self._cfg_presence.get("out_to_away_hours", 24)) * 3600

        # ── Wrap HA entities ──
        self._e = {}  # entity cache
        for key in ("all_home", "a_parent_home", "disable_auto_modes",
                     "holiday", "force_home", "nearly_home", "mute_alarm"):
            eid = self._cfg_presence.get(key)
            if eid:
                self._e[key] = self.adbase.get_entity(eid)

        if self._cfg_car:
            self._e["car_location"] = self.adbase.get_entity(self._cfg_car["location"])
            self._e["car_alarm_off"] = self.adbase.get_entity(self._cfg_car["alarm_off"])

        # ── Runtime state ──
        self._out_flag: bool = False
        self._out_timer_handle: Any = None
        self._house_listeners: list = []
        self._car_listeners: list   = []
        self._camera_listeners: list = []
        self._light_timers: dict[str, Any] = {}
        self._alert_cooldowns: dict[str, datetime] = {}  # sensor_id → last alert time

        # ── Bootstrap ──
        self._e["holiday"].turn_off()  # safe default on restart
        self._activate_mode()

        # ── Global listeners ──
        presence_id = self._cfg_presence["a_parent_home"]
        holiday_id  = self._cfg_presence["holiday"]
        force_id    = self._cfg_presence["force_home"]

        self.adbase.listen_state(self._on_presence_change, [presence_id, holiday_id])
        self.adbase.listen_state(self._on_force_home_change, force_id, attribute="all")

        self._log("Initialisation complete", level="INFO")

    # ── Companion helpers ───────────────────────────────────────────────────

    def _get_companion(self, name: str):
        """Safely fetch a companion app; return None if unavailable."""
        try:
            return self.adbase.get_app(name)
        except Exception:
            self._log(f"Companion app '{name}' not available — skipping", level="WARNING")
            return None

    def lnn(self) -> int:
        """Return current line number for debug logging."""
        return sys._getframe(1).f_lineno

    # ── Logging helpers ─────────────────────────────────────────────────────

    def _log(self, msg: str, level: str = "DEBUG") -> None:
        self.adbase.log(msg, level=level)

    def _log_banner(self, text: str) -> None:
        self.adbase.log(f"\n{'='*50}\n  {text}\n{'='*50}", level="INFO")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #  MODE MANAGEMENT
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _determine_mode(self) -> str:
        """
        Derive the current operating mode from sensor state.

        Priority:
          1. force_home ON               → home
          2. everyone present             → home
          3. nobody present + holiday ON  → away
          4. nobody present + holiday OFF → out  (starts auto-escalation timer)
          5. holiday ON but someone home  → away  (cleaning scenario)
        """
        if self._e["force_home"].is_state("on"):
            return "home"

        nobody_home = (
            self._e["a_parent_home"].is_state("off")
            and self._e["disable_auto_modes"].is_state("off")
        )
        is_holiday = self._e["holiday"].is_state("on")

        if nobody_home:
            if is_holiday:
                self._cancel_out_timer()
                return "away"
            # Start escalation timer if not already running
            if not self._out_flag:
                self._out_timer_handle = self.adbase.run_in(
                    self._on_out_timer_expired, self._out_to_away_secs
                )
                self._out_flag = True
                self._log(f"Out-timer started ({self._out_to_away_secs}s)", level="INFO")
            return "out"

        # Someone IS home
        self._cancel_out_timer()
        return "away" if is_holiday else "home"

    def _cancel_out_timer(self) -> None:
        if self._out_flag and self._out_timer_handle:
            self.adbase.cancel_timer(self._out_timer_handle)
        self._out_flag = False
        self._out_timer_handle = None

    def _on_out_timer_expired(self, _cb_args: Any) -> None:
        """Auto-escalate out → away after timeout."""
        self._log("Out-timer expired — escalating to AWAY", level="INFO")
        self._e["holiday"].set_state(state="on")
        self._out_flag = False

    def _build_schedule(self, mode: str) -> Schedule:
        """Build a Schedule from config + current month."""
        month = datetime.now().month
        season = "summer" if month in self._summer_months else "winter"
        params = self._schedules_cfg[season]
        return Schedule(
            mode=mode,
            season=season,
            sunrise=params["sunrise"],
            wakeup=params["wakeup"],
            sunset=params["sunset"],
            evening=params["evening"],
            bedtime=params["bedtime"],
            nighttime=params["nighttime"],
        )

    def _activate_mode(self) -> None:
        """
        Central orchestrator.  Tears down prior state and rebuilds everything
        for the current mode.  Called on init and every presence/holiday change.
        """
        mode = self._determine_mode()
        schedule = self._build_schedule(mode)

        self._log_banner(f"Activating mode: {mode.upper()} ({schedule.season})")

        # Publish to HA for dashboards
        self.adbase.set_state(
            entity_id="sensor.alarm_mode",
            state=schedule.title_mode,
            attributes=schedule.as_dict(),
        )

        # ── Tear down ──
        self._teardown_listeners()
        self._teardown_light_timers()

        # ── Build up ──
        self._setup_perimeter(schedule)
        self._setup_cameras(schedule)
        self._setup_lighting(schedule)
        self._setup_climate(schedule)
        self._setup_managed_automations(schedule)

        # Reset nearly-home after it's been consumed
        if self._e.get("nearly_home") and self._e["nearly_home"].is_state("on"):
            self._e["nearly_home"].set_state(state="off")

        # Publish overview
        overview = self._build_overview(schedule)
        self._log(overview, level="INFO")

    def _teardown_listeners(self) -> None:
        for listener_list in (self._house_listeners, self._car_listeners, self._camera_listeners):
            for handle in listener_list:
                try:
                    self.adbase.cancel_listen_state(handle)
                except Exception as exc:
                    self._log(f"Listener cleanup error: {exc}", level="WARNING")
            listener_list.clear()

    def _teardown_light_timers(self) -> None:
        for key, handle in self._light_timers.items():
            try:
                self.adbase.cancel_timer(handle)
            except Exception as exc:
                self._log(f"Timer cleanup error ({key}): {exc}", level="WARNING")
        self._light_timers.clear()

    # ── Event handlers ──

    def _on_presence_change(self, entity, attribute, old, new, kwargs) -> None:
        self._activate_mode()

    def _on_force_home_change(self, entity, attribute, old, new, kwargs) -> None:
        if new.get("state") == "on":
            self._e["holiday"].turn_off()
            self._e["force_home"].turn_off()
            # Mode refresh happens via the holiday state change listener

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #  PERIMETER MONITORING
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _setup_perimeter(self, schedule: Schedule) -> None:
        """Register listeners for building + car perimeter sensors."""
        mode = schedule.mode

        # Building — contacts + vibration sensors
        building_sensors = (
            self.args.get("home_perimeter", {}).get("contacts", [])
            + self.args.get("home_perimeter", {}).get("vibration", [])
        )
        if building_sensors:
            handles = self.adbase.listen_state(
                self._on_perimeter_event,
                building_sensors,
                new="on",
                schedule=schedule,
                zone="building",
            )
            self._house_listeners = handles if isinstance(handles, list) else [handles]

        # Car
        car_sensors = self._cfg_car.get("perimeter", [])
        if car_sensors:
            handles = self.adbase.listen_state(
                self._on_perimeter_event,
                car_sensors,
                new="on",
                schedule=schedule,
                zone="car",
            )
            self._car_listeners = handles if isinstance(handles, list) else [handles]

        self._log(f"Perimeter armed: {len(building_sensors)} building, {len(car_sensors)} car sensors", level="INFO")

    def _on_perimeter_event(self, entity, attribute, old, new, kwargs) -> None:
        """Evaluate a perimeter sensor trigger against current mode/schedule."""
        schedule: Schedule = kwargs["schedule"]
        zone: str = kwargs["zone"]
        mode = schedule.mode

        should_alert = False

        if zone == "car":
            should_alert = self._evaluate_car_alert(schedule)
        elif zone == "building":
            should_alert = self._evaluate_building_alert(schedule)

        if should_alert and self._check_cooldown(entity):
            severity = SEVERITY_SCREAM if mode == "away" else SEVERITY_SHOUT
            self._send_alert(severity, entity, mode=mode)
            self._log(
                f"PERIMETER ALERT: zone={zone} mode={mode} sensor={entity} severity={severity}",
                level="INFO",
            )

    def _evaluate_car_alert(self, schedule: Schedule) -> bool:
        """Should we alert for a car perimeter event?"""
        if self._e.get("car_alarm_off") and self._e["car_alarm_off"].is_state("on"):
            return False

        mode = schedule.mode
        if mode == "home":
            in_drive = self._e.get("car_location") and self._e["car_location"].is_state("home")
            if in_drive:
                return self.adbase.now_is_between(schedule.evening, schedule.wakeup)
            return True  # car not on driveway — always alert
        return True  # out/away — always alert

    def _evaluate_building_alert(self, schedule: Schedule) -> bool:
        """Should we alert for a building perimeter event?"""
        mode = schedule.mode
        if mode == "away":
            return True  # always
        if mode in ("home", "out"):
            return self.adbase.now_is_between(schedule.bedtime, schedule.wakeup)
        return False

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #  CAMERA INTEGRATION (Nest SDM event entities)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _setup_cameras(self, schedule: Schedule) -> None:
        """
        Listen for events on Nest camera event entities.

        Nest SDM exposes a single event entity per camera (e.g. event.front_door_motion).
        Every detection — person, motion, sound — fires as a state change on that entity,
        with the `event_type` attribute distinguishing between them:
          • camera_person  → person detected (security alert)
          • camera_motion  → generic motion  (optional low-priority alert)
          • camera_sound   → sound detected  (logged only)

        We listen for ANY state change on the event entity, then filter by
        event_type in the callback.  Only `camera_person` triggers security
        alerts; `camera_motion` optionally triggers a whisper notification
        if `motion_alerts` is enabled in config.

        Sensitivity levels control WHEN person alerts fire:
          high   → any person detection in out/away (24/7)
          medium → person detection between sunset and sunrise
          low    → person detection only during bedtime→wakeup
        """
        cfg = self._cfg_cameras
        if not cfg.get("enabled"):
            self._log("Cameras disabled in config", level="INFO")
            return

        if schedule.mode == "home":
            self._log("Cameras: home mode — monitoring disabled", level="INFO")
            return

        devices = cfg.get("devices", {})
        for cam_name, cam_cfg in devices.items():
            event_entity = cam_cfg.get("event_entity")
            if not event_entity:
                self._log(f"Camera {cam_name}: no event_entity configured — skipping", level="WARNING")
                continue

            # Listen for ALL state changes on the event entity (not just new="on").
            # Event entities change state to a timestamp each time they fire,
            # so we watch for any change.
            handle = self.adbase.listen_state(
                self._on_camera_event,
                event_entity,
                schedule=schedule,
                cam_name=cam_name,
                cam_entity=cam_cfg.get("camera_entity"),
            )
            if isinstance(handle, list):
                self._camera_listeners.extend(handle)
            else:
                self._camera_listeners.append(handle)

        self._log(
            f"Cameras armed: {len(devices)} devices, "
            f"sensitivity={cfg.get('sensitivity', 'high')}, "
            f"motion_alerts={cfg.get('motion_alerts', False)}",
            level="INFO",
        )

    def _on_camera_event(self, entity, attribute, old, new, kwargs) -> None:
        """
        Handle any event from a Nest camera event entity.

        Reads the `event_type` attribute to determine what kind of detection
        occurred and routes accordingly:
          camera_person → security alert (severity based on mode)
          camera_motion → optional whisper alert if motion_alerts enabled
          camera_sound  → logged, no notification
        """
        schedule: Schedule = kwargs["schedule"]
        cam_name: str = kwargs["cam_name"]
        cam_entity: str = kwargs.get("cam_entity")

        # Read the event_type from the entity's attributes
        event_type = self.adbase.get_state(entity, attribute="event_type") or ""

        self._log(
            f"Camera {cam_name}: event fired — event_type={event_type}, entity={entity}",
            level="DEBUG",
        )

        if event_type == "camera_person":
            self._handle_person_detection(entity, schedule, cam_name, cam_entity)
        elif event_type == "camera_motion":
            self._handle_motion_detection(entity, schedule, cam_name, cam_entity)
        elif event_type == "camera_sound":
            self._log(f"Camera {cam_name}: sound detected — logged only", level="DEBUG")
        else:
            self._log(f"Camera {cam_name}: unknown event_type '{event_type}' — ignoring", level="DEBUG")

    def _handle_person_detection(
        self, entity: str, schedule: Schedule, cam_name: str, cam_entity: str | None
    ) -> None:
        """Process a person-detection event — this is the primary security trigger."""
        sensitivity = self._cfg_cameras.get("sensitivity", "high")

        should_alert = False
        if sensitivity == "high":
            should_alert = True
        elif sensitivity == "medium":
            should_alert = self.adbase.now_is_between(schedule.sunset, schedule.sunrise)
        elif sensitivity == "low":
            should_alert = self.adbase.now_is_between(schedule.bedtime, schedule.wakeup)

        if not should_alert:
            self._log(
                f"Camera {cam_name}: PERSON detected but outside {sensitivity} sensitivity window",
                level="DEBUG",
            )
            return

        if not self._check_cooldown(f"camera_person_{entity}"):
            return

        # Capture snapshot
        if self._cfg_cameras.get("snapshot_on_alert") and cam_entity:
            self._capture_snapshot(cam_entity, cam_name)

        severity = SEVERITY_SCREAM if schedule.mode == "away" else SEVERITY_SHOUT
        self._send_alert(
            severity,
            entity,
            mode=schedule.mode,
            heading=f"🚨 Person Detected: {cam_name.replace('_', ' ').title()}",
        )
        self._log(
            f"CAMERA ALERT: {cam_name} PERSON detected, mode={schedule.mode}, severity={severity}",
            level="INFO",
        )

    def _handle_motion_detection(
        self, entity: str, schedule: Schedule, cam_name: str, cam_entity: str | None
    ) -> None:
        """Process a generic motion event — optional low-priority alert."""
        if not self._cfg_cameras.get("motion_alerts", False):
            self._log(f"Camera {cam_name}: motion detected — motion_alerts disabled, ignoring", level="DEBUG")
            return

        if not self._check_cooldown(f"camera_motion_{entity}"):
            return

        self._send_alert(
            SEVERITY_WHISPER,
            entity,
            mode=schedule.mode,
            heading=f"Motion: {cam_name.replace('_', ' ').title()}",
            message=f"Motion detected on {cam_name.replace('_', ' ')} camera. Mode is {schedule.mode}.",
        )
        self._log(
            f"Camera {cam_name}: motion alert sent (whisper), mode={schedule.mode}",
            level="INFO",
        )

    def _capture_snapshot(self, cam_entity: str, cam_name: str) -> None:
        """Save a snapshot from the camera for review."""
        snap_path = self._cfg_cameras.get("snapshot_path", "/config/www/snapshots")
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{snap_path}/{cam_name}_{ts}.jpg"
        try:
            self.hass.call_service(
                "camera/snapshot",
                entity_id=cam_entity,
                filename=filename,
            )
            self._log(f"Snapshot saved: {filename}", level="INFO")
        except Exception as exc:
            self._log(f"Snapshot failed for {cam_entity}: {exc}", level="WARNING")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #  LIGHTING (data-driven)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _setup_lighting(self, schedule: Schedule) -> None:
        """
        Build daily light timers from YAML config.

        Each light in config can have schedules keyed by mode (or "all").
        Each entry specifies an action (dim/on/off), a time-slot name,
        optional randomisation, and optional season filter.
        """
        mode = schedule.mode
        self._log(f"Lighting setup for mode={mode}", level="INFO")

        for ent_id, light_cfg in self._cfg_lights.items():
            if not isinstance(light_cfg, dict):
                continue

            dim_pct = light_cfg.get("dim_pct", 0)
            mode_schedules = light_cfg.get("schedules", {})

            # Collect entries for current mode + "all"
            entries = mode_schedules.get("all", []) + mode_schedules.get(mode, [])

            for entry in entries:
                # Season filter
                entry_season = entry.get("season")
                if entry_season and entry_season != schedule.season:
                    continue

                action = entry["action"]
                time_key = entry["at"]
                time_str = getattr(schedule, time_key)

                # Randomisation
                rand_mins = entry.get("random_minutes", 0)
                rand_secs = rand_mins * 60
                rand_kwargs = {}
                if rand_secs > 0:
                    rand_kwargs = {"random_start": -rand_secs, "random_end": rand_secs}

                handle = self.adbase.run_daily(
                    self._on_light_timer,
                    time_str,
                    entity=ent_id,
                    action=action,
                    dim_pct=dim_pct,
                    **rand_kwargs,
                )
                key = f"{mode}_{ent_id}_{action}_{time_key}"
                self._light_timers[key] = handle
                self._log(f"  Light timer: {ent_id} → {action} at {time_key} ({time_str})", level="DEBUG")

    def _on_light_timer(self, kwargs) -> None:
        """Execute a scheduled light action."""
        ent = kwargs["entity"]
        action = kwargs["action"]
        dim_pct = kwargs.get("dim_pct", 0)

        if action == "on":
            self.hass.turn_on(ent)
        elif action == "off":
            self.hass.turn_off(ent)
        elif action == "dim":
            if dim_pct > 0:
                # Skip dimming the night light if everyone is home
                if ent == "light.lounge_lamp_2" and self._e.get("all_home"):
                    if self._e["all_home"].is_state("on"):
                        self._log(f"Skipping {ent} dim — all home", level="DEBUG")
                        return
                self.adbase.call_service(
                    "light/turn_on", entity_id=ent, brightness_pct=dim_pct
                )
            else:
                self._log(f"Skipping {ent} dim — dim_pct is 0", level="DEBUG")

        self._log(f"Light action: {ent} → {action} (dim_pct={dim_pct})", level="DEBUG")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #  CLIMATE CONTROL
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _setup_climate(self, schedule: Schedule) -> None:
        """Configure Tado + Nest heating based on mode and nearly-home flag."""
        cfg = self._cfg_climate
        if not cfg:
            return

        mode = schedule.mode
        nearly_home = self._e.get("nearly_home") and self._e["nearly_home"].is_state("on")
        all_tados = cfg["tado_group"]
        nest = cfg.get("nest_thermostat")
        hot_water = cfg.get("hot_water")

        self._log(f"Climate setup: mode={mode}, nearly_home={nearly_home}", level="INFO")

        # Resume auto schedules first
        self.adbase.call_service("climate/set_hvac_mode", entity_id=all_tados, hvac_mode="auto")
        if hot_water:
            self.adbase.call_service(
                "water_heater/set_operation_mode",
                entity_id=hot_water,
                operation_mode="auto",
            )

        if nearly_home:
            # Boost everything — we're coming home
            self.adbase.call_service("climate/set_preset_mode", entity_id=all_tados, preset_mode="home")
            if nest:
                self.adbase.call_service("climate/set_preset_mode", entity_id=nest, preset_mode="none")
            if hot_water:
                self.adbase.call_service(
                    "tado/set_water_heater_timer",
                    entity_id=hot_water,
                    time_period=cfg.get("boost_duration", "00:30:00"),
                )
            if schedule.season == "winter":
                self.adbase.call_service(
                    "tado/set_climate_timer",
                    entity_id=all_tados,
                    time_period=cfg.get("boost_duration", "00:30:00"),
                    temperature=cfg.get("boost_temp", 20),
                )
                boost_script = cfg.get("boost_script")
                if boost_script:
                    self.adbase.call_service("script/turn_on", entity_id=boost_script)
        else:
            tado_preset, nest_preset = ("away", "eco") if mode == "away" else ("home", "none")
            self.adbase.call_service("climate/set_preset_mode", entity_id=all_tados, preset_mode=tado_preset)
            if nest:
                self.adbase.call_service("climate/set_preset_mode", entity_id=nest, preset_mode=nest_preset)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #  MANAGED AUTOMATIONS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _setup_managed_automations(self, schedule: Schedule) -> None:
        """Enable/disable HA automations based on mode."""
        disable_list = self._cfg_autos.get("disable_when_away", [])
        if not disable_list:
            return

        service = "automation/turn_off" if schedule.mode == "away" else "automation/turn_on"
        for auto_id in disable_list:
            self.adbase.call_service(service, entity_id=auto_id)
            self._log(f"Automation {auto_id} → {service}", level="INFO")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #  NOTIFICATIONS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _check_cooldown(self, sensor_id: str) -> bool:
        """
        Return True if enough time has passed since the last alert for this sensor.
        Prevents notification floods from flapping sensors.
        """
        cooldown_secs = self._cfg_notif.get("cooldown", 300)
        now = datetime.now()
        last = self._alert_cooldowns.get(sensor_id)

        if last and (now - last).total_seconds() < cooldown_secs:
            self._log(f"Cooldown active for {sensor_id} — suppressing", level="DEBUG")
            return False

        self._alert_cooldowns[sensor_id] = now
        return True

    def _send_alert(self, severity: str, sensor_entity: str, **kwargs) -> None:
        """
        Send a notification at the given severity level.

        Severity tiers:
          whisper → low-priority push (general channel)
          shout   → normal push (general channel)
          scream  → persistent high-priority push + optional TTS
        """
        heading = kwargs.get("heading", "House Alarm")
        mode    = kwargs.get("mode", "")
        message = kwargs.get("message")
        url_path = kwargs.get("url", self._cfg_notif.get("admin_url", ""))

        device = self._cfg_notif["admin_device"]
        surface = f"notify/{device}"

        sensor_name = self.adbase.get_state(sensor_entity, attribute="friendly_name") or sensor_entity
        if not message:
            message = f"ALERT: {sensor_name} was triggered. Mode is {mode}."

        not_muted = self._e.get("mute_alarm") and self._e["mute_alarm"].is_state("off")

        if severity == SEVERITY_SCREAM:
            data = {
                "clickAction": url_path,
                "url": url_path,
                "visibility": "public",
                "channel": "Alarmz",
                "importance": "high",
                "persistent": "true",
                "tag": "persistent",
                "group": "Alarm Notifs",
            }
            self.adbase.call_service(surface, message=message, title=heading, data=data)
            if not_muted:
                tts_data = {"tts_text": "Alarm has been triggered. Please check Home Assistant."}
                self.adbase.call_service(surface, message="TTS", data=tts_data)

        elif severity == SEVERITY_SHOUT:
            data = {
                "clickAction": url_path,
                "url": url_path,
                "visibility": "public",
                "channel": "General",
                "group": "Alarm Notifs",
            }
            self.adbase.call_service(surface, message=message, title=heading, data=data)

        else:  # whisper
            data = {
                "clickAction": url_path,
                "url": url_path,
                "channel": "General",
                "group": "Alarm Notifs",
            }
            self.adbase.call_service(surface, message=message, title=heading, data=data)

        self._log(f"Notification sent: severity={severity} heading={heading}", level="INFO")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #  OVERVIEW / STATUS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _build_overview(self, schedule: Schedule) -> str:
        """Generate a human-readable status summary and publish to HA sensor."""
        mode = schedule.mode
        s = schedule
        lights_cfg = self._cfg_lights

        lines = [
            f"Mode: {mode.upper()}",
            f"Season: {s.season.upper()}",
            f"Sunrise: {s.sunrise}  Sunset: {s.sunset}",
            f"Wakeup: {s.wakeup}  Evening: {s.evening}  Bedtime: {s.bedtime}  Nighttime: {s.nighttime}",
            "",
        ]

        # Perimeter
        if mode == "away":
            lines.append("Building perimeter: ALWAYS armed")
            lines.append("Car security: ALWAYS armed")
        elif mode in ("home", "out"):
            lines.append(f"Building perimeter: armed {s.bedtime} → {s.wakeup}")
            if mode == "home":
                lines.append(f"Car security: armed {s.evening} → {s.wakeup} (if on driveway)")
            else:
                lines.append("Car security: ALWAYS armed")

        # Cameras
        cam_cfg = self._cfg_cameras
        if cam_cfg.get("enabled") and mode != "home":
            lines.append(f"Cameras: armed (sensitivity={cam_cfg.get('sensitivity', 'high')})")
        else:
            lines.append("Cameras: monitoring off (home mode)")

        # Climate
        nearly_home = self._e.get("nearly_home") and self._e["nearly_home"].is_state("on")
        if nearly_home:
            lines.append("Climate: BOOST mode (nearly home)")
        elif mode == "away":
            lines.append("Climate: away/eco preset")
        else:
            lines.append("Climate: normal schedule")

        # Lights summary
        lines.append("")
        lines.append("Light schedules:")
        for ent_id, lcfg in lights_cfg.items():
            if not isinstance(lcfg, dict):
                continue
            mode_scheds = lcfg.get("schedules", {})
            entries = mode_scheds.get("all", []) + mode_scheds.get(mode, [])
            for entry in entries:
                es = entry.get("season")
                if es and es != s.season:
                    continue
                lines.append(f"  {ent_id}: {entry['action']} at {entry['at']}")

        # Publish as HA sensor
        routine = {chr(ord("A") + i): line for i, line in enumerate(lines) if line}
        self.adbase.set_state(
            entity_id="sensor.alarm_schedule",
            state=f"{mode.title()} - {s.season.title()}",
            attributes=routine,
            replace="True",
        )

        separator = "\n  │ "
        return f"\n{'='*50}\n  OVERVIEW{separator}{separator.join(lines)}\n{'='*50}"

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #  TESTING
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def test_trigger(self) -> None:
        """Simulate sensor triggers for testing (call from HA service or CLI)."""
        test_sensors = [
            "binary_sensor.bathroom_window_contact",
            "event.front_door_motion",
            "event.garden_a_motion",
        ]
        import time as _time
        for sensor in test_sensors:
            self.adbase.set_state(sensor, state="on")
            _time.sleep(1)
            self.adbase.set_state(sensor, state="off")
            self._log(f"TEST: toggled {sensor}", level="WARNING")