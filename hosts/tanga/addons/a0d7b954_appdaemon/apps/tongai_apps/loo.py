import adbase as ad
import re
import copy
from datetime import timedelta, timezone, time
import datetime
from time import sleep
import traceback
import requests 


class LooApp(ad.ADBase):
#
#####
#
    def initialize(self):
        """Initialize AppDaemon App."""
        self.adbase = self.get_ad_api()
        self.hass = self.get_plugin_api("HASS")
        self.au = self.adbase.get_app("auto_unlock")
        
        self.adbase.log("\n\n************\n*\n* Welcome to loo App\n*\n************\n") #Launch message
        
        self.adbase.listen_state(self.restart,"binary_sensor.loo_light_acceleration", attribute="all")
        self.adbase.listen_state(self.restart,"binary_sensor.loo_light_contact", attribute="all")
        self.adbase.listen_state(self.restart,"light.hue_white_spot_1", attribute="all")
#        self.adbase.listen_state(self.restart,"light.t_bedside", attribute="all")
        
        
    
    def restart(self,entity, attribute, old, new, kwargs):
        old_ts = self.adbase.convert_utc(old['last_changed'])
        old_time = old_ts.time()
        old_day = old_ts.date()
        new_ts = self.adbase.convert_utc(new['last_changed'])
        new_time = new_ts.time()
        new_day = new_ts.date()
        self.adbase.log(f"{old['attributes']['friendly_name']},{entity},{old['state']},{new['state']},{old_day},{old_time},{new_day},{new_time}")
  #      if old == "unavailable" and new == "off":
  #          self.adbase.log(f"Line {self.au.lnn()}:: {entity} is now {new}\n")
  #          self.hass.turn_on(entity)
        



