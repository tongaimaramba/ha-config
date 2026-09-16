import adbase as ad
from datetime import datetime, timedelta
import traceback
import inspect

class RebootMonitorApp(ad.ADBase):
#
#####
#
    def initialize(self):
        """Initialize AppDaemon App."""
        self.adbase = self.get_ad_api()
        self.hass = self.get_plugin_api("HASS")
        self.mqtt = self.get_plugin_api("MQTT")
        self.au = self.adbase.get_app("auto_unlock")
        
        self.adbase.log("\n\n************\n*\n* Welcome to Reboot_Monitor\n*\n************\n") #Launch message
        self.au.shout("normal","Reboot_Monitor Just Started.",heading="*** HASS Admin ***")

        self.hass.listen_state(self.reboot,"binary_sensor.everyone_home",new="off")
        
    def reboot(self, entity, attribute, old, new, kwargs):
        if self.hass.get_state("binary_sensor.me_presence") == "on":
           self.au.shout("loud","need to check monitor node", heading="Monitor Admin")
            
