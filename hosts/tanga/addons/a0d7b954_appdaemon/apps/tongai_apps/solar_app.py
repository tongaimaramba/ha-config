#
# 1. tell me how free I can eb with consumption
# 2. tell me how much I'm spending (especially at peak price)
# 3. maximise export arbitrage to offset my costs
#

import adbase as ad
#import re
#import copy
from datetime import datetime, timedelta, timezone, time
#from time import sleep
#import traceback
#import requests
#import getpass 
import sys 
from string import ascii_lowercase as alc

class SolarApp(ad.ADBase):
#
#####
#
    def initialize(self):
        """Initialize AppDaemon App."""
        self.adbase = self.get_ad_api()
        self.hass = self.get_plugin_api("HASS")
        self.mqtt = self.get_plugin_api("MQTT")
        self.au = self.adbase.get_app("auto_unlock")
        
        self.adbase.log("\n\n************\n*\n* Welcome to Solar App   ************\n*\n************\n") #Launch message
        
##  load sensors from config        
        load_now = self.args.get('load_now')
        solar_now = self.args.get('solar_now')
        grid_now = self.args.get('grid_now')
        battery_now = self.args.get('battery_now')
        battery_soc = self.args.get('battery_soc')
        work_mode = self.args.get('work_mode')
        pv_wk = self.args.get('pv_wk')
        load_wk = self.args.get('load_wk')
        grid_in_wk = self.args.get('grid_in_wk')
        grid_out_wk = self.args.get('grid_out_wk')
        self.peak_grid_price = self.args.get('peak_grid_price')
        self.offpeak_grid_price = self.args.get('offpeak_grid_price')
        #--
        self.load_now = self.adbase.get_entity(load_now)
        self.solar_now = self.adbase.get_entity(solar_now)
        self.grid_now = self.adbase.get_entity(grid_now)
        self.battery_now = self.adbase.get_entity(battery_now)
        self.battery_soc = self.adbase.get_entity(battery_soc)
        self.work_mode = self.adbase.get_entity(work_mode)
        self.pv_wk = self.adbase.get_entity(pv_wk)
        self.load_wk = self.adbase.get_entity(load_wk)
        self.grid_in_wk = self.adbase.get_entity(grid_in_wk)
        self.grid_out_wk_this_week_sensor = self.adbase.get_entity(grid_out_wk)
        self.grid_in_today = self.adbase.get_entity("sensor.tojgan3_grid_import_today")
        self.grid_in_today.add(state=0.0, attributes={"friendly_name": "Grid Imported Today","cost (£)": 0,"state_class": "total_increasing","unit_of_measurement": "kWh","device_class": "energy"})
    
        self.adbase.listen_state(self.update_sensors, load_now, tracking_sensor=grid_in_wk)
    
    def update_sensors(self,entity, attribute, old, new, kwargs):

        #self.adbase.log(f"Line {self.au.lnn()}: {sys._getframe().f_code.co_name.upper()}",level="INFO")
        
    #-- How much expensive Grid have we used today    
        tracking_sensor=kwargs['tracking_sensor']
        peak_start_time = self.adbase.parse_datetime(self.args.get('peak_start')+":00",aware=True)   #YY-MM-DD-HH:MM:SS
        now = self.adbase.get_now()
        if now > peak_start_time:
            data = self.hass.get_history(entity_id=tracking_sensor, start_time = peak_start_time)
            start = data[0][0]['state']
            data = self.hass.get_history(entity_id=tracking_sensor, start_time = datetime.now())
            current = data[0][0]['state']
            state_change = round(float(current)-float(start),2)
            cost = round((state_change * self.peak_grid_price/100),2)
            self.grid_in_today.set_state(state = state_change, attributes= {"cost (£)": cost})
        #self.adbase.set_state(entity_id="sensor.tojgan_grid_import_today", state = state_change, attributes= {"cost (£)": cost})
        #self.adbase.log(f"Line {self.au.lnn()}: Grid import since {peak_start_time} is {state_change}, going from {start} to {current}\n",level="DEBUG")   #offpeak price: {self.offpeak_grid_price} ** Load Now ent: {self.load_now}",level="DEBUG")
        
##  create new sensors
        ### create the entities through UI and just laod them through config.
        #self.load_today = self.adbase.get_entity("sensor.tojgan-solr_load_today")
        #self.load_today.add(state=0, attributes={"friendly_name": "Load Today"}) 
"""
        #--
        self.pv_today = self.adbase.get_entity("sensor.solar_today")
        self.pv_today.adbase.add(state=0, attributes={"friendly_name": "Solar Today"})
        #--
        self.grid_in_today = self.adbase.get_entity("sensor.grid_import_today")
        self.grid_in_today.adbase.add(state=0, attributes={"friendly_name": "Grid Imported Today"})
        self.peak_grid_in_today = self.adbase.get_entity("sensor.peak_grid_import_today")
        self.peak_grid_in_today.adbase.add(state=0, attributes={"friendly_name": "Peak Grid Imported Today"})
        self.offpeak_grid_in_today = self.adbase.get_entity("sensor.offpeak_grid_import_today")
        self.offpeak_grid_in_today.adbase.add(state=0, attributes={"friendly_name": "Off-Peak Grid Imported Today"})
        #--
        self.grid_out_today = self.adbase.get_entity("sensor.grid_export_today")
        self.grid_out_today.adbase.add(state=0, attributes={"friendly_name": "Grid Exported Today"})
"""        
        

        # Listen for mode qualifiers:
       # self.adbase.log(f"Line {self.au.lnn()}: ****\nRunning Listeners ",level="DEBUG")
       # self.adbase.listen_state(self.modes,[presence_sensor,holiday_sensor])
      #  self.adbase.listen_state(self.force_home_mode, force_home_id, attribute='all')

"""         
    def perimeter(self,entity, attribute, old, new, kwargs): #mode should be a param passed in
        mode = kwargs['schedule']['mode']
        self.adbase.log(f"Line {self.au.lnn()}: Started function {sys._getframe().f_code.co_name.upper()} with mode: {mode}",level="DEBUG")
        
        result = False
        triggered_sensor = entity
        schedule = kwargs['schedule']
        zone = kwargs['zone']
        
        if zone == "car":
            if not self.car_alarm_off: # if car alarm is enabled then...
                if mode == "home":
                    in_drive = self.car_location_sensor.is_state('home')
                    if in_drive:
                        start = schedule['evening']
                        end = schedule['wakeup']
                        result = self.adbase.now_is_between(start,end)
                        self.adbase.log(f"Line {self.au.lnn()}: result: {result} start: {start}; end: {end}", level="DEBUG")
                    else:
                        result =True
                        self.adbase.log(f"Line {self.au.lnn()}: zone: {zone}; mode: {mode} but in_drive is {in_drive} so notifying.", level="DEBUG")
                else:
                    result = True
                    self.adbase.log(f"Line {self.au.lnn()}: zone: {zone}; mode: {mode} notifying.", level="DEBUG")
            else:  #if car alarm is disabled then... 
                result=False  
            
        if zone == "building":       
            if mode == "home":
                start = schedule['bedtime']
                end = schedule['wakeup']
                result = self.adbase.now_is_between(start,end)
                #self.adbase.log(f"Line {self.au.lnn()}: start: {start}; end: {end}", level="DEBUG")
                 
            if mode == "out":
                start = schedule['bedtime']
                end = schedule['wakeup']
                result = self.adbase.now_is_between(start,end)
                
            if mode == "away":
                result=True
        
        if result:
           notify = "scream" if mode == "away" else "shout"
           self.notif(notify,triggered_sensor, mode=mode) # call notif function, pass it notify and triggered_sensor, mode, heading
           self.adbase.log(f"Line {self.au.lnn()}: PERIMETER:: notification_level: {notify}; mode: {mode}; triggered sensor: {triggered_sensor}", level="INFO")
        else:
            #placeholder for other actions
            notify = "none"
            
        
        self.adbase.log(f"Line {self.au.lnn()}: It is {result} that the event happened in a critical window on {triggered_sensor}. So notify level is {notify}. Mode is {mode}.", level="DEBUG")
"""        