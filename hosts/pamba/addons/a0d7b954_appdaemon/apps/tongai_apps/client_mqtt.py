import adbase as ad
from datetime import datetime, timedelta, timezone, time
from time import sleep
import traceback
import requests


class MQTTClientApp(ad.ADBase):
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
        
        self.adbase.log("\n\n************\n*\n* Welcome to Test App\n*\n************\n") #Launch message
        
        colours = {"red":{"r":255,"g":0,"b":0},"amber":{"r":255,"g":30,"b":0},"green":{"r":0,"g":255,"b":0}}
        rgb = list(colours["red"].values())
        rb = (", ".join(rgb))
        self.adbase.log(f"colours: ({rb})")
        
        self.post = "Homeassistant/Auto_Unlock/Status"
        self.result = "Homeassistant/Auto_Unlock/Result"
        payload = "hello cheese - starting up"
        #self.mqtt.mqtt_subscribe(self.post)
        #self.mqtt.mqtt_subscribe(self.result)
        #self.mqtt.mqtt_publish(self.post,payload)
         
        #self.mqtt.listen_event(self.update_led, "MQTT_MESSAGE",topic=self.post)
         
    def update_led(self, event_name, data, kwargs):
        msg = data["payload"]
        self.adbase.log(f"hello, just saw message {msg}\nNow change status of LED")
        payload = "LED update"
        self.mqtt.mqtt_publish(self.result,payload)
    
    def led_result(self, event_name, data, kwargs):
        self.adbase.log(f"hello, just saw message {data}\n LED has been updated")
        