import adbase as ad
 
class REMQApp(ad.ADBase):
#
#####
#
    def initialize(self):
        """Initialize AppDaemon App."""
        self.adbase = self.get_ad_api()
        self.hass = self.get_plugin_api("HASS")
        self.mqtt = self.get_plugin_api("MQTT")
        self.access = self.adbase.get_app("guest_access")
        self.au = self.adbase.get_app("auto_unlock")
        
        self.adbase.log("\n\n************\n*\n* Welcome to Reboot by MQTT App\n*\n************\n") #Launch message
        
        self.dash = 0
        self.cmd = ""
        self.topic="/rpi/reboot/"
        self.lTopic = self.topic + "response/"
        self.adbase.log(f"Line {self.au.lnn()}:Dash Flag initiliased to {self.dash}\nCommand initialised to {self.cmd}\nPublish Topic is {self.topic}\nListen Topic is {self.lTopic}\n", level="DEBUG")
        self.mqtt.mqtt_subscribe(f"{self.topic}#")
        self.hass.listen_state(self.mqtt_io,"input_select.mqtt_messages")
        self.mqtt.listen_event(self.mqtt_message,"MQTT_MESSAGE",topic=self.lTopic)
        
    def mqtt_io(self, entity, attribute, old, new, kwargs):        
        self.mqtt.mqtt_publish(self.topic,new)
        self.dash = 1
        self.cmd = new
        self.adbase.log(f"Line {self.au.lnn()}:Published to topic: {self.topic}\nPayload is: {new}\nDash Flag set to {self.dash}\n", level="DEBUG")

    def mqtt_message(self, event_name, data, kwargs):
        if self.dash and data["payload"]:
            self.hass.set_textvalue("input_text.mqtt_payload", data["payload"])
            self.adbase.log(f"Line {self.au.lnn()}:Updating Input Text field with: {data['payload']}\n", level="DEBUG")
        elif self.dash and data["payload"] == "unknown command":
            self.hass.set_textvalue("input_text.mqtt_payload", "unkown command")
            self.adbase.log(f"Line {self.au.lnn()}:Unknown command sent - no action\n", level="DEBUG")
        if self.dash:
            self.adbase.log(f"Line {self.au.lnn()}:Command sent >> {self.cmd} <<*** and payload received was >> {data['payload']} << *** This was entered via UI", level="INFO")
            self.dash=0
        else: 
            self.adbase.log(f"Line {self.au.lnn()}:Payload received was >> {data['payload']} << *** but this not was entered via UI so the command is not known", level="INFO")
#        self.cmd=""
        return