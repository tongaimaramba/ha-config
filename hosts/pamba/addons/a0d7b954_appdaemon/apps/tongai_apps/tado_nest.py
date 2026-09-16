import adbase as ad
import re
import copy
from datetime import datetime, timedelta, timezone, time
import traceback

class TadoNestApp(ad.ADBase):
#
#####
#
    def initialize(self):
        """Initialize AppDaemon App."""
        self.adbase = self.get_ad_api()
        self.hass = self.get_plugin_api("HASS")
        self.au = self.adbase.get_app("auto_unlock")
        
        self.adbase.log("\n\n************\n*\n* Welcome to the Tado Nest App\n*\n************\n") #Launch message

        #Initialise sensors and thermostat lists
        self.internal_sensors = {"upstairs":{"bathroom":"sensor.bathroom_temperature","main":{"dyson":"sensor.bedroom_temperature","nest":"sensor.bedroom_temperature_2","tado":"sensor.main_temperature"},"friends":{"tado":"sensor.friends_temperature","dyson":"sensor.upstairs_temperature"},"landing":"sensor.landing_temperature","study":"sensor.study_temperature"},"downstairs":{"hallway":"sensor.coats_temperature","dining":"sensor.downstairs_temperature","utility":"sensor.utility_motion_temperature","kitchen":"sensor.worktop_sensor_temperature"}}
        self.tado = {"upstairs":{"main":"climate.main","study":"climate.study","friends":"climate.friends"}}
        self.nest = {"upstairs":"climate.bedroom","downstairs":"climate.downstairs"}
        
        #Listen for changes in any of the thermostats
        self.adbase.listen_state(self.change_nest,"climate",attribute="all")
        
    def change_nest(self, entity, attribute, old, new, kwargs):
        
        trv_temps = {}
        old_target = old['attributes']['temperature']
        new_target = new['attributes']['temperature']
        
        if new_target == old_target:
            self.adbase.log(f"Line {self.au.lnn()}::No action, {entity} temperature didn't change.",level="DEBUG")
            return
        
        if entity in ("climate.downstairs","climate.bedroom"): 
            self.adbase.log(f"Line {self.au.lnn()}:: This is a Nest thermosat.  No action.",level="DEBUG")
            return
        else:
            #If it was a radiator thermostat that changed, then update nest
            for room in self.tado["upstairs"]:
                trv = self.tado["upstairs"][room]
                trv_temps[trv] = self.adbase.get_state(trv,attribute="all")['attributes']['temperature']    #get all the latest temp settings from Tado thermostats
#                self.adbase.log(f"TRV: {trv} {self.adbase.get_state(trv,attribute='all')}")
            hottest_trv = list(sorted(trv_temps.items(), key=lambda x: x[1], reverse=True))[0]  #reorder the thermostats with the one needing highest temp first.
            top_temp = hottest_trv[1] + self.args.get("offset")      #The Nest target temp needs to be equal to or greater than the Tado with highest temp.  Also included an offset option.
            self.adbase.call_service("climate/set_temperature",entity_id=self.nest['upstairs'], temperature=top_temp) #Update Nest.
            self.adbase.log(f"Line {self.au.lnn()}:: Setting {self.nest['upstairs']} to {top_temp} because of {hottest_trv[0]}")  
            
            
            
            
            
            