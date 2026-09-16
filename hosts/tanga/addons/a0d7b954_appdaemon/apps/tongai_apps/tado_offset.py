# 1. every 5 mins check temp of tado and external sensor (nest) and check time period flag
# 2. if time period (flag) has expired 
# 3. if ext sensor is less than tado, round difference, and print it 
# 4. increase tado target temp by the difference for 10 mins using tado.set_climate_timer giving entity id; time_period: 00:10:00; and temperature. set time period flag (use run_in?)
# 5. 

import adbase as ad
import re
import copy
from datetime import datetime, timedelta, timezone, time
import traceback

class TadoOffsetApp(ad.ADBase):
#
#####
#
    def initialize(self):
        """Initialize AppDaemon App."""
        self.adbase = self.get_ad_api()
        self.hass = self.get_plugin_api("HASS")
        self.au = self.adbase.get_app("auto_unlock")
        
        self.adbase.log("\n\n************\n*\n* Welcome to the Tado Offset App\n*\n************\n") #Launch message

        #initialise key variables
        self.trv = self.args.get("tado_trv")
        self.ext = self.args.get("external_sensor")
        self.freq = self.args.get("temp_check_frequency",5) if self.args.get("temp_check_frequency",5) >= 5 else 5
        self.heat_duration = self.freq+5
        self.boost_timer = self.adbase.datetime() - timedelta(minutes=1)
        self.target_temp = ""
        
        self.adbase.log(f"Line {self.au.lnn()}:: Configured parameters: tado sensor {self.trv}; external sensor {self.ext}; run frequency {self.freq} minutes.", level="DEBUG")
        
        try:
            self.adbase.log(f"Line {self.au.lnn()}::flow check", level="DEBUG")
            self.adbase.run_every(self.fix_temp,"now",self.freq*60)   #scheduled runs every "freq"
            
        except Exception as e:
            self.adbase.log(f"Line {self.au.lnn()}::{e}")

    def fix_temp(self, kwargs):
        
        ext_temp = self.hass.get_state(self.ext,attribute="all")['attributes']['current_temperature']
        
        if self.boost_timer <= self.adbase.datetime():
            self.target_temp = self.hass.get_state(self.trv,attribute="all")['attributes']['temperature']
            if ext_temp < self.target_temp:
                
                #get the boost temperature
                diff = round(self.target_temp - ext_temp)
                boost_temp = self.target_temp + diff
                if boost_temp > 25: boost_temp = 25   #cap temp at 25 degrees
                
                #get the boost duration
                self.boost_timer = self.adbase.datetime() + timedelta(minutes=self.heat_duration,seconds=30)
                tado_timer = "00:"+ str(self.heat_duration) + ":00"
                
                #boost!
                self.adbase.call_service("tado/set_climate_timer",entity_id=self.trv, time_period = tado_timer,temperature=boost_temp) 
                self.adbase.log(f"Line {self.au.lnn()}:: Started boosting TRV {self.trv} by {diff} degrees to reach target temp of {self.target_temp}. Currently at {ext_temp} according to {self.ext}",level="INFO")
            else:
               self.adbase.log(f"Line {self.au.lnn()}:: Temperature {ext_temp} spot on, no need for boost (target temp is {self.target_temp}",level="DEBUG") 
        else:
            self.adbase.log(f"Line {self.au.lnn()}:: Already boosting. Currently at {ext_temp} and aiming for {self.target_temp}",level="DEBUG")
            return