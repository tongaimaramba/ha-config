import adbase as ad
import re
import copy
from datetime import datetime, timedelta, timezone, time
import traceback
import requests

class ZonesApp(ad.ADBase):
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
        
        self.adbase.log("\n\n************\n*\n* Welcome to Device Zones App\n*\n************\n") #Launch message

        self.tongai = "sensor.pixel_3_geocoded_location"
        self.mojgan = "sensor.iphone_geocoded_location"
        devices = ["self.tongai","self.mojgan"]
 #       self.adbase.log(f"upstairs main bedroom internal sensors: {self.internal_sensors['upstairs']['main']}")
        
        for ent in devices:
            self.adbase.listen_state(self.get_loc,ent,attribute="all")
#        self.adbase.listen_state(self.get_loc,self.mojgan,attribute="all")
        
    def get_loc(self, entity, attribute, old, new, kwargs):
        
        self.adbase.log(f"Line {self.au.lnn()}::New Geo state: {new}\n")