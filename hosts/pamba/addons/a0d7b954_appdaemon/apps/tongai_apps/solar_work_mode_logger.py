import appdaemon.plugins.hass.hassapi as hass
from datetime import time, datetime


class SolarWorkModeLogger(hass.Hass):
    def initialize(self):
        #self.hass = self.get_plugin_api("HASS")
        self.mqtt = self.get_plugin_api("MQTT")
        
        # Configurable parameters from apps.yaml
        self.entity_id = self.args.get("entity_id", "select.growatt_sph_work_mode_priority")
        self.topic_command = self.args.get("topic_command", "solar_assistant/inverter_1/work_mode_priority/set")
        self.topic_state = self.args.get("topic_state", "solar_assistant/inverter_1/device_mode/state")
        self.start_time = self.parse_time(self.args.get("start_time", "03:00:00"))
        self.end_time = self.parse_time(self.args.get("end_time", "04:00:00"))
        self.listen_to_mqtt = self.args.get("listen_to_mqtt", True)
        self.debug_log = self.args.get("debug_log", False)

        # Listen for state changes within the time window
        self.listen_state(self.state_change_handler, self.entity_id,attribute = "all")

        # Subscribe directly to MQTT topics (via MQTT plugin/namespace)
        self.mqtt.listen_event(self.mqtt_message_handler, "MQTT_MESSAGE", topic=self.topic_command)
        self.mqtt.listen_event(self.mqtt_message_handler, "MQTT_MESSAGE", topic=self.topic_state)

        self.log("\n\n************\n*\n* Welcome to Solar Work Mode Debugger   ************\n*\n************\n") #Launch message
        self.log(f"SolarWorkModeLogger initialized for {self.entity_id}; "
            f"command_topic={self.topic_command}, state_topic={self.topic_state}. "
            f"Logging from {self.start_time} to {self.end_time}.")

    def in_active_window(self):
        now = datetime.now().time()
        return self.start_time <= now <= self.end_time

    def state_change_handler(self, entity, attribute, old, new, kwargs):
        if self.in_active_window():
            msg = (f"[STATE CHANGE] {entity}: {old['state']} >>> {new['state']} at {datetime.now().isoformat()} | "
                   f"By {self.get_state(entity, attribute='last_changed')}")
            self.log(msg, level="INFO")
            if self.debug_log:
                # Log additional context for power users
                self.log(f"[STATE CHANGE FULL OLD]: {old}\n**\n [STATE CHANGE FULL NEW]: {new}", level="DEBUG")

    def mqtt_message_handler(self, event_name, data, kwargs):
       # self.log("***mqtt listener called!*****\n", level="INFO")
        topic = data.get("topic", "")
        payload = data.get("payload", "")
        now_str = datetime.now().isoformat()
        if topic == self.topic_command and self.in_active_window():
            msg = (
                f"[MQTT COMMAND SENT] topic: {topic} | payload: {payload} | at {now_str}\n"
            )
            self.log(msg, level="INFO")
        elif topic == self.topic_state and self.in_active_window():
            msg = (
                f"[MQTT STATE RECEIVED] topic: {topic} | payload: {payload} | at {now_str}\n"
            )
            self.log(msg, level="INFO")
       # elif self.debug_log and (topic == self.topic_command or topic == self.topic_state):
        #    self.log(
        #        f"[DEBUG-MQTT] Received message outside window on topic: {topic} (payload: {payload})",
        #        level="DEBUG",
        #    )