import adbase as ad
import re
import copy
from datetime import timedelta, timezone, time
import datetime
from time import sleep
import traceback
import requests 


class TriggerApp(ad.ADBase):
#
#####
#
    def initialize(self):
        """Initialize AppDaemon App."""
        self.adbase = self.get_ad_api()
        self.hass = self.get_plugin_api("HASS")
        self.mqtt = self.get_plugin_api("MQTT")
        self.au = self.adbase.get_app("auto_unlock")
        
        self.adbase.log("\n\n************\n*\n* Welcome to Test App\n*\n************\n") #Launch message
 
 ## Get Setup Config       
        self.cameras = {"4b42f81fb3bb5debbe7ca2a9eb6a0597":"Garden","f4abd2fe653ecaff0c1a4676092c52d4":"Front"}
        self.pairs ={}
        self.trigger_pairs = self.tidy_conf(self.args.get("trigger_pairs"),"pairs")     # each pair has a device and a trigger sensor e.g. light and contact sensor
        for t in self.trigger_pairs: 
            self.trigger_pairs[t] = self.tidy_conf(self.trigger_pairs[t],"times")  #parse any on/off times into a dict
#        self.adbase.log(f"Line {self.au.lnn()}:: trig pairs: {self.trigger_pairs}", level="DEBUG")
#
## Start the Listeners
        for t in self.trigger_pairs:
            if t == "entity_state":
                for p in self.trigger_pairs[t]:
                    ent = p["sensor"]
                    dev = p["device"]
                    self.adbase.listen_state(self.state_trig,ent,attribute="all",device=dev)      #listen for the sensor to change state, pass it the device to turn on/off
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
                if presence == "off" and camera == "Front":
                    msg = "Person detected by " + camera + " camera, while someone is out. Ran monitor scan"
                    self.mqtt.mqtt_publish("monitor/run_scan/arrive")
                 #   self.au.shout("mqtt-status","amber")
                #    self.au.shout("loud",msg,heading="Unlock Nest Prescan")
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
            
        self.adbase.log(f"Line {self.au.lnn()}:: {sensor.title()} triggered to make {device.title()} {act.upper()}\n")
#        
    def time_trig(self, kwargs):
        if kwargs["act"] == "on":
            self.hass.turn_on(kwargs["ent"])
        elif kwargs["act"] == "off":
            self.hass.turn_off(kwargs["ent"])
        self.adbase.log(f" {self.au.lnn()}:: Time trigger turned {kwargs['act']} {kwargs['ent']}.")
#
    def tidy_conf(self,confDict,typ):
        if typ == "pairs": # function to remove any event types that are not in use in the config
            record = confDict.copy()
            for event in confDict:
                if confDict[event] == None:
                    record.pop(event)
                    self.adbase.log(f"Line {self.au.lnn()}:: Removed {event}\n",level="DEBUG")
                else:
                    continue
                
        if typ == "times":    # function to identify and parse out the time window for easier use
            record = []
            if not (confDict): return 
            for i in range(len(confDict)):
                pair = confDict[i].split() #convert one config row under an event type into a list
                if len(pair) <  2 or len(pair) > 6:
                    confRec = ''
                    self.adbase.log(f"Line {self.au.lnn()}:: Invalid config record, ignoring -> {pair}")
                elif len(pair) > 1:
                    device = pair[0]
                    sensor = pair[1] if pair[1].lower() != "on" else "scheduler"
                    if len(pair) > 2:
                        for y in range(len(pair)):
                            if pair[y].lower() == "on":
                                win = {pair[y].lower():pair[y+1],pair[y+2].lower():pair[y+3]}           # a time window has been included
                                break
                        confRec = {"device":device,"sensor":sensor,"win":win}
                    else:
                        confRec = {"device":device,"sensor":sensor}
                if confRec: record.append(confRec)
#       self.adbase.log(f"Line {self.au.lnn()}:: end of loop. {record}", level="DEBUG")
        return record





