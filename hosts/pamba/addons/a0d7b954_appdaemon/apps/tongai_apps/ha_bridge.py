import appdaemon.plugins.hass.hassapi as hass
import appdaemon.plugins.mqtt.mqttapi as mqtt
import json
from datetime import datetime, timedelta
from collections import deque

class HABridge(hass.Hass, mqtt.Mqtt):
    def initialize(self):
        self.cfg = self.args
        self.mqtt_namespace = self.cfg.get('namespace', 'interha_bridge')
        self.hass_namespace = self.cfg.get('hass_namespace', 'default')
        self.server_id = self.cfg['server_id']
        self.remote_server = self.cfg['remote_server']
        self.kill_switch = self.cfg.get('kill_switch', False)
        self.mirrors = self.cfg.get('mirrors', {})
        
        # Statistics and monitoring
        self.stats = {
            'messages_sent': 0, 
            'messages_received': 0, 
            'errors': 0,
            'loop_prevention_blocks': 0,
            'last_error_time': None,
            'consecutive_errors': 0
        }
        
        # Loop prevention: track recently processed messages
        self.recent_messages = deque(maxlen=100)  # Track last 100 message signatures
        self.loop_detection_window = 5  # seconds
        self.max_duplicate_rate = 10  # max times same message in window before blocking
        
        # Health monitoring
        self.error_threshold = 10  # consecutive errors before alert
        self.last_health_check = datetime.now()
        self.health_check_interval = 300  # 5 minutes
        self.notification_entity = self.cfg.get('notification_entity', 'persistent_notification')
        
        # Connection state tracking
        self.mqtt_connected = False
        self.connection_recovery_attempted = False
        
        # Subscribe to all bridge messages from the remote server
        try:
            self.mqtt_subscribe(
                f"ha_bridge/{self.remote_server}/#", namespace=self.mqtt_namespace
            )
            self.listen_event(self._on_mqtt_message, "MQTT_MESSAGE", namespace=self.mqtt_namespace)
            self.log(f"[HABridge] Successfully subscribed to MQTT topic: ha_bridge/{self.remote_server}/#", level="INFO")
        except Exception as e:
            self.log(f"[HABridge] CRITICAL: Failed to subscribe to MQTT: {e}", level="ERROR")
            self._send_critical_alert(f"MQTT subscription failed: {e}")
            
        # Config-driven local->remote entity mirroring
        try:
            for local_entity, remote_entity in self.mirrors.items():
                self.listen_state(
                    self._mirror_on_change, 
                    local_entity, 
                    namespace=self.hass_namespace, 
                    remote_entity=remote_entity
                )
            self.log(f"[HABridge] Configured {len(self.mirrors)} entity mirrors", level="INFO")
        except Exception as e:
            self.log(f"[HABridge] Error setting up mirrors: {e}", level="ERROR")
            self._send_alert(f"Mirror configuration error: {e}")
        
        # Schedule periodic health checks
        self.run_every(self._health_check, "now+60", self.health_check_interval)
        
        self.log(
            f"[HABridge] {self.server_id} bridge initialized. MQTT ns: {self.mqtt_namespace}, "
            f"HASS ns: {self.hass_namespace}, kill_switch={self.kill_switch}", 
            level="INFO"
        )

    # ----------- Health Monitoring & Self-Healing -----------

    def _health_check(self, kwargs):
        """Periodic health check and stats reporting."""
        try:
            self.log(
                f"[HABridge Health] Sent: {self.stats['messages_sent']}, "
                f"Received: {self.stats['messages_received']}, "
                f"Errors: {self.stats['errors']}, "
                f"Loop blocks: {self.stats['loop_prevention_blocks']}, "
                f"MQTT connected: {self.mqtt_connected}",
                level="INFO"
            )
            
            # Check for persistent error conditions
            if self.stats['consecutive_errors'] >= self.error_threshold:
                self._send_critical_alert(
                    f"Bridge experiencing persistent errors: {self.stats['consecutive_errors']} consecutive failures"
                )
                
                # Attempt self-healing: try reconnecting MQTT
                if not self.connection_recovery_attempted:
                    self.log("[HABridge] Attempting MQTT reconnection...", level="WARNING")
                    self._attempt_mqtt_recovery()
                    
            # Reset consecutive errors if we've been stable
            if self.stats['last_error_time']:
                time_since_error = datetime.now() - self.stats['last_error_time']
                if time_since_error > timedelta(minutes=10):
                    self.stats['consecutive_errors'] = 0
                    self.connection_recovery_attempted = False
                    
        except Exception as e:
            self.log(f"[HABridge] Health check failed: {e}", level="ERROR")

    def _attempt_mqtt_recovery(self):
        """Attempt to recover MQTT connection."""
        try:
            # Re-subscribe to topics
            self.mqtt_subscribe(
                f"ha_bridge/{self.remote_server}/#", namespace=self.mqtt_namespace
            )
            self.connection_recovery_attempted = True
            self.log("[HABridge] MQTT recovery attempted", level="INFO")
            self._send_alert("Bridge attempted MQTT recovery")
        except Exception as e:
            self.log(f"[HABridge] MQTT recovery failed: {e}", level="ERROR")
            self._send_critical_alert(f"MQTT recovery failed: {e}")

    def _send_alert(self, message):
        """Send non-critical alert notification."""
        try:
            self.call_service(
                "persistent_notification/create",
                title="HA Bridge Alert",
                message=f"[{self.server_id}] {message}",
                notification_id=f"ha_bridge_{self.server_id}_alert"
            )
        except Exception as e:
            self.log(f"[HABridge] Failed to send alert: {e}", level="ERROR")

    def _send_critical_alert(self, message):
        """Send critical alert notification."""
        try:
            self.call_service(
                "persistent_notification/create",
                title=f"⚠️ HA Bridge CRITICAL [{self.server_id}]",
                message=message,
                notification_id=f"ha_bridge_{self.server_id}_critical"
            )
            self.log(f"[HABridge] CRITICAL ALERT: {message}", level="ERROR")
        except Exception as e:
            self.log(f"[HABridge] Failed to send critical alert: {e}", level="ERROR")

    def _record_error(self):
        """Track error for monitoring."""
        self.stats['errors'] += 1
        self.stats['consecutive_errors'] += 1
        self.stats['last_error_time'] = datetime.now()

    def _record_success(self):
        """Reset error counter on successful operation."""
        if self.stats['consecutive_errors'] > 0:
            self.stats['consecutive_errors'] = 0

    # ----------- Loop Prevention -----------

    def _get_message_signature(self, payload):
        """Create a signature for loop detection."""
        try:
            msg_type = payload.get('type', '')
            entity_id = payload.get('entity_id', '')
            state = payload.get('state', '')
            timestamp = payload.get('timestamp', '')
            source = payload.get('source_server', '')
            
            # Create signature without timestamp for duplicate detection
            return f"{msg_type}:{source}:{entity_id}:{state}"
        except Exception:
            return None

    def _is_loop_detected(self, signature):
        """Check if message is part of a publish loop."""
        if not signature:
            return False
            
        now = datetime.now()
        
        # Count recent occurrences of this signature
        recent_count = sum(
            1 for (sig, timestamp) in self.recent_messages
            if sig == signature and (now - timestamp).total_seconds() < self.loop_detection_window
        )
        
        if recent_count >= self.max_duplicate_rate:
            self.stats['loop_prevention_blocks'] += 1
            return True
            
        return False

    def _record_message(self, signature):
        """Record message signature for loop detection."""
        if signature:
            self.recent_messages.append((signature, datetime.now()))

    # ----------- Bridge API (for wrappers/other scripts) -----------

    def send_state(self, entity_id, remote_entity_id=None, state=None, attributes=None):
        """Send/replicate a state+attribute update to remote server."""
        if self.kill_switch:
            self.log("Kill switch active, not sending state", level="WARNING")
            return False
            
        try:
            actual_state = state if state is not None else self.get_state(entity_id, namespace=self.hass_namespace)
            
            if actual_state is None:
                self.log(f"[HABridge] Cannot send state for {entity_id}: entity not found", level="WARNING")
                return False
                
            actual_attrs = attributes if attributes is not None else self.get_state(
                entity_id, attribute="all", namespace=self.hass_namespace
            ).get("attributes", {})
            
            msg_entity = remote_entity_id or entity_id
            message = {
                "type": "state_update",
                "entity_id": msg_entity,
                "state": actual_state,
                "attributes": actual_attrs,
                "timestamp": datetime.now().isoformat(),
                "source_server": self.server_id
            }
            
            topic = f"ha_bridge/{self.server_id}/state/{msg_entity.replace('.', '/')}"
            self.mqtt_publish(topic, json.dumps(message), namespace=self.mqtt_namespace, retain=False)
            self.stats['messages_sent'] += 1
            self._record_success()
            self.log(f"(API) Sent {entity_id} as {msg_entity}: {actual_state}", level="DEBUG")
            return True
            
        except Exception as e:
            self.log(f"[HABridge] Error sending state for {entity_id}: {e}", level="ERROR")
            self._record_error()
            return False

    def send_service_call(self, domain, service, entity_id=None, service_data=None):
        """Send service call to remote Home Assistant."""
        if self.kill_switch:
            self.log("Kill switch active, not sending service call", level="WARNING")
            return False
            
        try:
            message = {
                "type": "service_call",
                "domain": domain,
                "service": service,
                "entity_id": entity_id,
                "service_data": service_data or {},
                "timestamp": datetime.now().isoformat(),
                "source_server": self.server_id
            }
            
            topic = f"ha_bridge/{self.server_id}/service/{domain}/{service}"
            self.mqtt_publish(topic, json.dumps(message), namespace=self.mqtt_namespace, retain=False)
            self.stats['messages_sent'] += 1
            self._record_success()
            self.log(f"(API) Sent remote service call: {domain}.{service} {entity_id or ''}", level="DEBUG")
            return True
            
        except Exception as e:
            self.log(f"[HABridge] Error sending service call {domain}.{service}: {e}", level="ERROR")
            self._record_error()
            return False

    def send_custom(self, custom_type, payload):
        """Send custom message to remote server."""
        if self.kill_switch:
            self.log("Kill switch active, not sending custom", level="WARNING")
            return False
            
        try:
            message = {
                "type": custom_type,
                "payload": payload,
                "timestamp": datetime.now().isoformat(),
                "source_server": self.server_id
            }
            
            topic = f"ha_bridge/{self.server_id}/custom/{custom_type}"
            self.mqtt_publish(topic, json.dumps(message), namespace=self.mqtt_namespace, retain=False)
            self.stats['messages_sent'] += 1
            self._record_success()
            self.log(f"(API) Sent custom message '{custom_type}'", level="DEBUG")
            return True
            
        except Exception as e:
            self.log(f"[HABridge] Error sending custom message: {e}", level="ERROR")
            self._record_error()
            return False

    # ----------- Mirroring Logic (config-driven) -----------

    def _mirror_on_change(self, entity, attribute, old, new, kwargs):
        """Handle state changes for mirrored entities."""
        try:
            remote_entity = kwargs.get('remote_entity')
            
            if not remote_entity:
                self.log(f"[HABridge] No remote_entity configured for {entity}", level="WARNING")
                return
                
            if old != new:
                success = self.send_state(entity, remote_entity_id=remote_entity)
                if success:
                    self.log(f"(Mirror) {entity} → {remote_entity}: {old} → {new}", level="INFO")
                else:
                    self.log(f"(Mirror) Failed to mirror {entity} → {remote_entity}", level="WARNING")
                    
        except Exception as e:
            self.log(f"[HABridge] Error in mirror handler for {entity}: {e}", level="ERROR")
            self._record_error()

    # ----------- Incoming MQTT message router -----------

    def _on_mqtt_message(self, event_name, data, kwargs):
        """Handle incoming MQTT messages with robust error handling."""
        try:
            if self.kill_switch:
                return
                
            # Extract message data with safety checks
            topic = data.get('topic')
            payload_raw = data.get('payload')
            state = data.get('state')
            
            # Handle MQTT connection status events (CRITICAL FIX #1)
            if state in ("Connected", "Disconnected"):
                self.mqtt_connected = (state == "Connected")
                self.log(f"[HABridge] MQTT {state}", level="INFO")
                if state == "Connected":
                    self._send_alert(f"Bridge MQTT reconnected")
                return
                
            # Ignore messages without topic (CRITICAL FIX #1)
            if not topic:
                self.log(f"[HABridge] Ignoring message with no topic (state={state})", level="DEBUG")
                return
                
            # Filter messages not from remote server
            if not topic.startswith(f"ha_bridge/{self.remote_server}/"):
                return
                
            # Ignore empty payloads
            if not payload_raw:
                self.log(f"[HABridge] Ignoring empty payload on topic {topic}", level="DEBUG")
                return
                
            # Parse JSON payload with error handling
            try:
                payload = json.loads(payload_raw)
            except (json.JSONDecodeError, TypeError, ValueError) as e:
                self.log(f"[HABridge] Failed to decode JSON on topic {topic}: {e}", level="WARNING")
                self._record_error()
                return
                
            # Validate payload structure
            if not isinstance(payload, dict):
                self.log(f"[HABridge] Invalid payload format on topic {topic}", level="WARNING")
                return
                
            # Extract message type
            mtype = payload.get("type")
            if not mtype:
                self.log(f"[HABridge] Message missing 'type' field on topic {topic}", level="WARNING")
                return
                
            # Loop detection (ENHANCEMENT #2)
            signature = self._get_message_signature(payload)
            if self._is_loop_detected(signature):
                self.log(
                    f"[HABridge] LOOP DETECTED: Blocking duplicate message {signature}",
                    level="WARNING"
                )
                # Send alert on first loop detection
                if self.stats['loop_prevention_blocks'] == 1 or self.stats['loop_prevention_blocks'] % 100 == 0:
                    self._send_alert(f"Message loop detected and blocked ({self.stats['loop_prevention_blocks']} total)")
                return
                
            # Record message for loop detection
            self._record_message(signature)
            
            # Route to appropriate handler
            if mtype == "state_update":
                self._handle_remote_state_update(payload)
            elif mtype == "service_call":
                self._handle_remote_service_call(payload)
            elif mtype.startswith("custom"):
                self._handle_remote_custom(payload)
            else:
                self.log(f"[HABridge] Unknown message type '{mtype}' on topic {topic}", level="WARNING")
                return
                
            self.stats["messages_received"] += 1
            self._record_success()
            
        except Exception as e:
            self.log(f"[HABridge] Unexpected error in message handler: {e}", level="ERROR")
            self._record_error()
            
            # Send alert on repeated failures
            if self.stats['consecutive_errors'] >= 3:
                self._send_alert(f"Bridge experiencing errors: {self.stats['consecutive_errors']} consecutive failures")

    def _handle_remote_state_update(self, payload):
        """Handle incoming state update from remote server."""
        try:
            entity_id = payload.get('entity_id')
            state = payload.get('state')
            attrs = payload.get('attributes', {})
            
            if not entity_id:
                self.log(f"[HABridge] State update missing entity_id", level="WARNING")
                return
                
            # Set state with error handling
            try:
                self.set_state(
                    entity_id, 
                    state=state, 
                    attributes=attrs, 
                    namespace=self.hass_namespace
                )
                self.log(f"(Inbound) Mirrored update: {entity_id} ← {state}", level="DEBUG")
            except Exception as e:
                self.log(f"(Inbound) Failed to set state for {entity_id}: {e}", level="ERROR")
                self._record_error()
                
        except Exception as e:
            self.log(f"[HABridge] Error handling state update: {e}", level="ERROR")
            self._record_error()

    def _handle_remote_service_call(self, payload):
        """Handle incoming service call from remote server."""
        try:
            domain = payload.get("domain")
            service = payload.get("service")
            entity_id = payload.get("entity_id")
            service_data = payload.get("service_data", {})
            
            if not domain or not service:
                self.log(f"[HABridge] Service call missing domain or service", level="WARNING")
                return
                
            # Execute service call with error handling
            try:
                if entity_id:
                    self.call_service(
                        f"{domain}/{service}", 
                        entity_id=entity_id, 
                        **service_data
                    )
                else:
                    self.call_service(f"{domain}/{service}", **service_data)
                    
                self.log(f"(Inbound) Executed service: {domain}.{service} {entity_id or ''}", level="INFO")
            except Exception as e:
                self.log(f"(Inbound) Failed to execute service {domain}.{service}: {e}", level="ERROR")
                self._record_error()
                self._send_alert(f"Failed to execute remote service: {domain}.{service}")
                
        except Exception as e:
            self.log(f"[HABridge] Error handling service call: {e}", level="ERROR")
            self._record_error()

    def _handle_remote_custom(self, payload):
        """Handle custom message from remote server."""
        try:
            self.log(f"(Inbound) Custom message received: {payload.get('type', 'unknown')}", level="INFO")
            # Extensibility point for future custom message handling
        except Exception as e:
            self.log(f"[HABridge] Error handling custom message: {e}", level="ERROR")
            self._record_error()

    # ----------- Utility Methods -----------

    def get_stats(self):
        """Return bridge statistics (callable from other apps)."""
        return self.stats.copy()

    def reset_stats(self):
        """Reset bridge statistics."""
        self.stats = {
            'messages_sent': 0, 
            'messages_received': 0, 
            'errors': 0,
            'loop_prevention_blocks': 0,
            'last_error_time': None,
            'consecutive_errors': 0
        }
        self.log("[HABridge] Statistics reset", level="INFO")
