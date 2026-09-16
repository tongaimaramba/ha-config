import adbase as ad
from datetime import datetime, timedelta, timezone, time
from time import sleep
import traceback

class RebeginApp(ad.ADBase):
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
        
        self.adbase.log("\n\n************\n*\n* Welcome to App Relauncher\n*\n************\n") #Launch message
        
        self.hass.listen_state(self.whichapp,"input_boolean.relaunch",attribute="all")
        
    def whichapp(self, entity, attribute, old, new, kwargs):
#        self.adbase.log(f"Line {self.au.lnn()}:{new}", level="DEBUG")
        if old['state'] == new['state']:
            return
        self.app = self.hass.get_state('input_text.app_reload')
        self.adbase.log(f"Line {self.au.lnn()}: Got to update {self.app}. Toggle was {old['state']} now {new['state']}", level="DEBUG")
        self.adbase.call_service("app/restart", app=self.app, namespace="appdaemon")
        self.adbase.log(f"Line {self.au.lnn()}: Done", level="DEBUG")