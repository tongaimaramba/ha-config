import adbase as ad
import re
import copy
from datetime import timedelta, timezone, time
import datetime
from time import sleep
import traceback
import requests 


class PumpApp(ad.ADBase):
#
#####
#
    def initialize(self):
        """Initialize AppDaemon App."""
        self.adbase = self.get_ad_api()
        self.hass = self.get_plugin_api("HASS")
        self.mqtt = self.get_plugin_api("MQTT")
        self.au = self.adbase.get_app("auto_unlock")
        
        self.adbase.log("\n\n************\n*\n* Welcome to Pump App\n*\n************\n") #Launch message
        
        self.dev = "switch.sonoff_1000eced8f"
        self.wait_ent = "input_number.timer_length"
    #    self.wait_ent = "input_text.runtime"
        self.pump_toggle = "input_boolean.pump_timer"
        self.adbase.log(f"Line {self.au.lnn()}:: loaded config")
        
        self.adbase.listen_state(self.run_time,self.pump_toggle,new="on",device=self.dev)     

    def run_time(self, entity, attribute, old, new, kwargs):
        t = self.adbase.get_state(self.wait_ent)
        t = int(float(t))*60
     #   t = int(t)*60
        self.adbase.log(f"Line {self.au.lnn()}:: starting {self.dev} with run time of {t/60} mins")
        self.hass.turn_on(kwargs['device'])
        self.handle = self.adbase.run_in(self.run_in_c, t,ent=entity,device=self.dev, runtime=t)
        
    def run_in_c(self, kwargs):
        self.adbase.log(f"Line {self.au.lnn()}:: after {kwargs['runtime']/60} mins, turning off {kwargs['ent']} and {kwargs['device']}")
        self.adbase.set_state(kwargs['ent'], state="off")
        self.hass.turn_off(kwargs['device'])
        
        
        
"""
                    self.adbase.log(f"Line {self.au.lnn()}:: Listening for state changes in {t} by {ent} to trigger {dev}")
            elif t == "nest_event":
                self.adbase.listen_event(self.event_trig,t) #listen for nest events 
                self.adbase.log(f"Line {self.au.lnn()}:: Listening for {t}s.", level = "DEBUG")
            elif t == "scheduled_action":
                for i in range(len(self.trigger_pairs[t])):
                    ent = self.trigger_pairs[t][i]["device"]
                    on_time = self.trigger_pairs[t][i]["win"]["on"]
                    off_time = self.trigger_pairs[t][i]["win"]["off"]
            #        self.adbase.run_daily(self.time_trig,on_time,ent=ent,act="on")
            #        self.adbase.run_daily(self.time_trig,off_time,ent=ent,act="off")
                    self.adbase.log(f"Line {self.au.lnn()}:: Scheduled {ent} to come on daily at {on_time} and off at {off_time}\n") 
#
    def event_trig(self, event_name, data, kwargs):
        #Event example: {'device_id': 'f4abd2fe653ecaff0c1a4676092c52d4', 'type': 'camera_motion', 'timestamp': '2021-10-04T18:15:48.793000+00:00', 'metadata': {'origin': 'LOCAL', 'time_fired': '2021-10-04T18:15:57.481670+00:00', 'context': {'id': '3d87271317f2c30c09c888f3101367b8', 'parent_id': None, 'user_id': None}}}
        actions = [] 
        camera = self.cameras[data['device_id']]
        event_type = data['type']
        
   #     self.adbase.log(f"Line {self.au.lnn()}:: Nest event triggered by {event_type.title()} on {camera} camera.", level="DEBUG")
        
        pairs = self.trigger_pairs[event_name]
        for p in pairs:
            device = p["device"]
            trig_ev = p["sensor"]
            if "win" in p:
                win = p["win"]
                start = str(p["win"]["on"])+":00"
                end = str(p["win"]["off"])+":00"
                time_window = self.adbase.now_is_between(start,end)
            else:
                win = None
                start = 'None specified'
                end = 'None specified'
                time_window = True
#            self.adbase.log(f"Line {self.au.lnn()}:: Action Device {device.title()} Trigger {trig_ev.title()} Time Window: {'Now' if time_window else 'Not Now'} because start is {start} and end is {end}")
        
            #for this device: are we in the time window, was this an event_type we were watching
            #if event_type == trig_ev and time_window: do the action for that device
        
            if event_type == trig_ev and time_window: actions.append(device)
        
        notify = True    
        for a in actions:
            if a == "arrive":
                presence = self.adbase.get_state("binary_sensor.everyone_home")
                if presence == "off":
                    msg = "Person detected by " + camera + " camera, while someone is out. Ran monitor scan"
                    self.mqtt.mqtt_publish("monitor/run_scan/arrive")
                    self.au.shout("loud",msg,heading="Unlock Nest Prescan")
                    self.adbase.log(f"Line {self.au.lnn()}:: {msg}") 
                    notify = False
                else:
                    self.adbase.log(f"Line {self.au.lnn()}::Person detected by {camera} camera but everyone is home (Presence State: {presence}), so no action", level="DEBUG")
            elif a == "shout" and notify:
                msg =  "Investigate:: " + event_type.title() + " by " + camera + " camera."
                self.au.shout("loud",msg,heading="Camera Alert")
                self.adbase.log(f"Line {self.au.lnn()}:: {msg}",level="DEBUG")
                notify = False
            else:
                msg =  "FYI:: " + event_type.title() + " by " + camera + " camera. Triggered " + a.title() + " ."
                self.hass.toggle(a)
            #    self.hass.toggle(device)
                self.au.shout("quiet",msg,heading="Camera Notif") 
                self.adbase.log(f"Line {self.au.lnn()}:: {msg}", level="DEBUG")
                notify = False
   # can't concatenate "actions" - its a list     acts = "and " + event_type.title() + " triggered the following Actions: " + actions + "." if actions else "but no actions needed for " + event_type.title() + " at the moment."   
#        self.adbase.log(f"Line {self.au.lnn()}:: {event_name.title()} happened on {camera} at {data['timestamp']}, {acts}", level="DEBUG")
        
    def state_trig(self,entity, attribute, old, new, kwargs):
        device = kwargs['device']
        sensor = entity
        act = new['state']
        
        self.adbase.log(f"Line {self.au.lnn()}:: Entity state change for {sensor.title()} will turn {act.lower()} {device.title()}.", level="DEBUG")
        
        if act == "on":
            self.hass.turn_on(device)
        elif act == "off":
            self.hass.turn_off(device)
"""