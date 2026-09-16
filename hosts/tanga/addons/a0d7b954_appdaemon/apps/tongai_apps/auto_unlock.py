#
# def create_lists(self): load config, create lists of entities to monitor
# def update_guests(self): remove redundant ents and create new ones
# def update_entities(self,action,devices): function to delete or create an ent
# def authenticate(self, entity, attribute, old, new, kwargs): unlock if criteria are met
# def hass_ts(self,hass): convert Hass time stamps from UTC to local time
# def authenticate_guests(self,entity): check if guests are accessing an authorised door at an authorised time
# def open_up(self,lock,key,user_ent): unlock the door
# def shout(self,loudness, msg,**kwargs): phone notifications
# def tidy_up(self,scope): re-initialise variables after each unlock attempt
# def lnn(self): return current line number in code
# def door_status_chk(self, door, **kwargs): function to test if a door has been open in the last X seconds
# def retry_open (self,trigger): creates a window of time in which a door will open on trigger if it was recently authenticated
# [WIP] def trigger_classifier(self): function to classify triggers as real or noise

import adbase as ad
import re
import copy
from datetime import datetime, timedelta
from time import sleep, time
import traceback
import inspect
import sys

class AutoUnlockApp(ad.ADBase):
#
#####
#
    def initialize(self):
        """Initialize AppDaemon App."""
        self.adbase = self.get_ad_api()
        self.hass = self.get_plugin_api("HASS")
        self.mqtt = self.get_plugin_api("MQTT")
        self.access = self.adbase.get_app("guest_access")
        
        self.production_mode = self.args.get("production_mode")     #set to false to disable lock operation
        self.logging = self.args.get("log_level","INFO")
        
        self.adbase.log(f"\n\n************\n*\n* Welcome to Auto_Unlock\n*\n************\nProduction Mode is {self.production_mode}\nLog Level is {self.logging}\n") #Launch message

#Load configuration
        self.configured_residents = self.args.get("residents_list")
        self.timeout = self.args.get("trigger_timeout")
        self.led_delay = self.args.get("led_delay")    #time in seconds to wait between when door starts to unlock, and when we give green light to push open
        self.prescan_delay = self.args.get("prescan_delay")    #time in seconds to wait before running mqtt pre-scan
        self.notif_level = self.args.get("notif_level","admin")         #which devices to send notifications - default is admin
        self.admin_device = self.args.get("admin_device", "all_android") #which device is the admin, default is all android
        self.lock_list = self.args.get("locks")
        self.door_list = self.args.get("door_contact")
        self.dot = self.args.get("door_open_timeout")
        self.noise_list = self.args.get("noise_list")
        self.alarm_mode = self.adbase.get_entity('sensor.alarm_mode')

#Set-up lists from config
        self.create_lists()  #Get list of entities to monitor
        self.update_guests() 
        
# Initialise variables
        self.trigger = []
        self.resident = []
        self.guest = []
        self.start_ts = ""
        self.time_window = ""
        self.last_unlock = []
        self.on_states = ["on","tojgan","home","78:d2:94:b6:07:31","7e:d2:94:b6:07:2f","78:d2:94:ba:14:cd"," 7e:d2:94:ba:14:cb","98:9b:cb:16:17:c7","98:9b:cb:16:17:c4"]

        self.shout("normal","Auto_Unlock Just Started.",heading="*** HASS Admin ***")
        
        #Listen
        try:
            for ent in self.listen_list:
                self.hass.listen_state(self.authenticate,ent)#,attribute="all")
                
        except Exception as e:
            self.adbase.log(f"Line {self.lnn()}: Listen Error: {e}",level="INFO") 
######
#
    def create_lists(self):
        
        self.live_devices=[]
        self.resident_list=[]
        self.guest_list=[]
        self.guest_mac={}
        self.guest_door={}
        self.user_dict = {}
        self.device_list=[]
        self.listen_list=[]
        self.trig_list = []
        self.pre_scan_triggers = []
        
        #get live devices
        for ent in self.hass.get_state("binary_sensor"): # List of live devices
            if "monitor_" in ent:
                self.live_devices.append(ent)
                
        #handle residents entities
        if not self.configured_residents: 
            self.adbase.log(f"Line {self.lnn()}:Config Error:: No resident devices included in config.",level="DEBUG")    # handle config errors
        else:
            for user in self.configured_residents:
                sensor = f"binary_sensor.monitor_{user}"
                door = self.configured_residents[user]
                self.resident_list.append(sensor)
                self.user_dict[sensor] = door
                self.adbase.log(f"Line {self.lnn()}: Configured resident sensor: {sensor} for {self.user_dict[sensor]} door.", level="DEBUG")

        #handle guest entities
            if not self.args.get("guests_list"):
               self.adbase.log(f"Line {self.lnn()}:Config Warning:: No guest devices included in config.",level="WARNING")    # handle config errors
            else:
                for ent in (rec.split() for rec in self.args.get("guests_list")):
                    if len(ent) != 3:
                        self.adbase.log(f"Line {self.lnn()}: Config Error:: In complete guest record for. Found: {ent}",level="DEBUG")                    # handle config errors - incomplete entries
                        continue
                    else:
                        ent[0] = user
                        sensor = f"binary_sensor.monitor_{user}"
                        ent[1] = mac
                        ent [2] = door

                        self.guest_list.append(sensor)                                  #handle guest entities
                        self.guest_mac[user] = mac                                      #handle guest mac addresses
                        self.guest_door[user] = door                                    #handle guest access door
                        self.user_dict[sensor] = door
                        self.adbase.log(f"Line {self.lnn()}: Configured guest sensor: {sensor} with mac address {mac} for {door} door.", level="DEBUG")

        #create trigger list
        if self.args.get("require_trigger"):
            self.triggers = self.args.get("trigger_sensor",{})
            self.trig_list = list(self.triggers.keys())
        self.adbase.log(f"Line {self.lnn()}:Config check - require_trigger is: {self.args.get('require_trigger')} so triggers are: {self.trig_list}",level="DEBUG")   
        
        #create pre_scan_triggers for early detection of new arrivals
        self.pre_scan_triggers = self.args.get("prescan_sensors",{})
        self.adbase.log(f"Line {self.lnn()}:Config check - the prescan sensors are {self.pre_scan_triggers}",level="DEBUG")
        
        # handle door contacts
        self.door_contacts = self.args.get("door_contact")
        
        #create lists of new and redundant entities
        self.create_ent=list(set(self.guest_list)-set(self.live_devices))
        self.remove_ent=list(set(self.live_devices)-set(self.resident_list)-set(self.guest_list))
        
        #create full listen list
        self.listen_list=self.resident_list+self.guest_list+self.trig_list+self.pre_scan_triggers
        self.adbase.log("Line {}: All entities: {}".format(self.lnn(),self.listen_list),level="DEBUG")   #Enable for Debugging
#
    def update_guests(self):
    # tidy up the live entities based on latest config
    
        self.update_entities("create",self.create_ent) #create the missing entities
        self.update_entities("remove",self.remove_ent) #remove the redundant entities
#
    def update_entities(self,action,devices):
        
    # Trigger Guest Access App to create/delete guest entities   

#        self.adbase.log("Line {}:Number of devices: {} to {}".format(self.lnn(),len(devices),action))#,level="DEBUG")   #Enable for Debugging            

        for ent in devices:                    
            dev = ent[22:]
            self.hass.set_state("input_text.guest_name",state=dev)  
            self.hass.set_state("input_select.relationship",state="Guest")
            
#            self.adbase.log(f"Line {self.lnn()}:Current device to handle: {dev}"#,level="DEBUG")   #Enable for Debugging            

            if action == "create":
                self.hass.set_state("input_number.monitor_action",state="2.0")
                self.hass.set_state("input_text.mac_addr",state=self.guest_mac[dev])
                self.access.manage_guest("run_guest_access")
                return
            elif action == "remove":
                dev_conf = "sensor.monitor_" + dev + "_frontdoor_conf"
                try:
                    dev_mac = self.hass.get_state(dev_conf,attribute="all")["attributes"]["id"]
                    self.hass.set_state("input_number.monitor_action",state="1.0")
                    self.hass.set_state("input_text.mac_addr",state=dev_mac)
                    self.access.manage_guest("run_guest_access")
                except Exception as e:
                    self.adbase.log(f"Line {self.lnn()}:Entity update error: Remove_Enitity failed. {e}",level="WARNING")
                return
            else:
                self.hass.set_state("input_number.monitor_action",state="0.0")
                self.adbase.log(f"Line {self.lnn()}: Entity update error: No action requested. Nothing done.",level="WARNING")    # handle config errors
                return
#
    def authenticate(self, entity, attribute, old, new, kwargs):
        
        active_ent = self.adbase.get_state(entity,attribute="all")
        ts = self.hass_ts(active_ent["last_changed"])[0]
        
        self.adbase.log(f"Line {self.lnn()}: State change to {active_ent['state']}, triggered by {active_ent['attributes']['friendly_name']}",level="DEBUG")

        if active_ent['state'] not in self.on_states:
            return

        self.adbase.log("Line {}: Entity {} changed state to {} at {}".format(self.lnn(),active_ent["attributes"]["friendly_name"],active_ent["state"],active_ent["last_changed"]),level="DEBUG")   #Enable for Debugging        

        if not self.start_ts: 
            self.start_ts = self.adbase.datetime()
            self.adbase.log(f"Line {self.lnn()}: Unlock cycle begins here {self.start_ts}, triggered by {active_ent['attributes']['friendly_name']}",level="DEBUG")
        elif int((ts - self.start_ts).total_seconds()) > self.timeout: 
            self.start_ts_old = self.start_ts
            self.start_ts = self.adbase.datetime()
            self.tidy_up("all")
            self.adbase.log(f"Line {self.lnn()}: Timeout: Resetting unlock cycle start time to now ({self.start_ts}) since this cycle started at {self.start_ts_old} (Exceeded timeout by {int((ts - self.start_ts_old).total_seconds())-self.timeout} seconds).",level="DEBUG")
        
        # populate entity list
        
        friendly = active_ent["attributes"]["friendly_name"]
        state = active_ent["state"]
        ent_typ = ""
        
        if entity in self.pre_scan_triggers:
            if self.hass.get_state("binary_sensor.everyone_home") == "off":     #If someone is away
                if state in self.on_states:    #and is coming back,
                    self.shout("mqtt-hci","1")
                    self.adbase.run_in(self.scan_later,self.prescan_delay)           #then trigger monitor scan
                    self.adbase.log(f"Line {self.lnn()}: Someone approaching so pre-scan was triggered by {friendly}.",level="INFO")
                elif state == "off":                                            #if they are leaving, just ignore 
                    self.adbase.log(f"Line {self.lnn()}: Prescan sensor changed to Off state.  Ignoring as this is probably a departure",level="DEBUG")
            return
        
        # If justina has just arrived (everyone_home is off or on for less than n seconds AND justina off to on)
        # Changed timeout to x minutes until a door opens or its been z minutes
        # replace self.timeout with a local var and set timeout here
        #if self.hass.get_state("binary_sensor.everyone_home") == "off":
        #   
            
        if entity in self.triggers:
            self.shout("mqtt-status","amber")
            self.shout("mqtt-hci","1")
            if len(self.trigger) and int((ts - self.start_ts).total_seconds()) > self.timeout:  #if this trigger is happening a long time after another trigger, then reset the timer to now
                self.start_ts_old = self.start_ts
                self.adbase.log(f"Line {self.lnn()}: Timeout: Resetting unlock cycle start time to now ({self.start_ts}) since this cycle started at {self.start_ts_old} (Exceeded timeout by {int((ts - self.start_ts_old).total_seconds())-self.timeout} seconds).", level="DEBUG")
                self.start_ts = self.adbase.datetime()
            ent_type = "T" 
            lock = self.triggers[entity]
            self.trigger = [entity,friendly,ts,lock]
            self.adbase.log(f"Line {self.lnn()}: Processing trigger {self.trigger[1]} and {ent_type}.",level="DEBUG")
            
            retryOpen = self.retry_open(entity)             #if we just tried to open the door but failed, try again
            if retryOpen:                                   #if it works this time, tidy up and stop here
                self.tidy_up("all")
                return
            noise_flag = self.trigger_classifier(entity)
            if noise_flag:
                self.adbase.log(f"Line {self.lnn()}: This was caused by noise (sensor was: {noise_flag}). Doing nothing.",level="DEBUG")
                self.tidy_up("all")
                return
            
        elif entity in self.resident_list:
            ent_type = "R"
            self.resident = [entity,friendly,ts]
            self.adbase.log(f"Line {self.lnn()}: Now processing resident {self.resident[1]} and {ent_type}.",level="DEBUG")
        elif entity in self.guest_list:
            ent_type = "G"
            window_flag = self.authenticate_guests(entity)
            self.guest = [entity,friendly,ts,self.guest_lock,window_flag,self.time_window]
            self.adbase.log(f"Line {self.lnn()}: Processing guest {self.guest[1]} and {ent_type}.",level="DEBUG")        

        # check for timeouts between device and trigger
        # active ent is a trigger
        try:
            self.adbase.log(f"Line {self.lnn()}: Starting timeout checks active ent {entity} and ent type is {ent_type}",level="DEBUG")
            if ent_type == "T":
                if len(self.resident):
                    self.adbase.log(f"Line {self.lnn()}: This is a Trigger and Resident already arrived",level="DEBUG")
                    ts_gap = int((ts - self.resident[2]).total_seconds())
                    if ts_gap <= self.timeout:
                        #if its a resident, unlock then tidy up
                        self.adbase.log(f"Line {self.lnn()}:flow check",level="DEBUG")
                        if self.open_up(self.trigger[3],self.resident[1],self.resident[0]):
                            reaction_time = int((self.adbase.datetime()-self.trigger[2]).total_seconds())    #how long between a trigger and the unlock
                            self.adbase.log(f"Line {self.lnn()}: Unlocked {self.trigger[3]} for {self.resident[1]} in {ts_gap} seconds",level="DEBUG")
                            self.shout("normal",f"Unlocked {self.trigger[3]} for {self.resident[1]}  with reaction time of {reaction_time} seconds",heading="*** Resident Home ***")
                            self.tidy_up("all")
                            return
                        else:
                            self.adbase.log(f"Line {self.lnn()}: Failed to unlock {self.trigger[3]}", level="DEBUG")
                            self.tidy_up("all")
                            return
                    else:
                        # device timed out
                        self.adbase.log(f"Line {self.lnn()}: Timeout: Device {self.resident[1]} has already been home for too long ({ts_gap} seconds).", level="DEBUG")
                        self.shout("mqtt-status","red" )
                        self.tidy_up("all")
                        return
                elif len(self.guest):
                    self.adbase.log(f"Line {self.lnn()}: Debug: This is a Trigger and Guest already arrived",level="DEBUG")
                    ts_gap = int((ts - self.guest[2]).total_seconds())
                    if ts_gap <= self.timeout:
                        #if its a guest, check window and door, then unlock/alert and tidy up
                        if self.guest[4] and self.guest[3] == self.trigger[3]:
                            # unlock and tidy up
                            if self.open_up(self.trigger[3],self.guest[1],self.guest[0]):
                                reaction_time = int((self.adbase.datetime()-self.trigger[2]).total_seconds())    #how long between a trigger and the unlock
                                self.adbase.log(f"Line {self.lnn()}: Guest Unlocked {self.trigger[3]} for {self.guest[1]} in {ts_gap} seconds",level="INFO")
                                self.shout("loud",f"Guest Unlocking: {self.trigger[3]} for {self.guest[1]} ({reaction_time} seconds)",heading="*** Guest Access Alert ***")
                                self.tidy_up("all")
                                return
                            else:
                                self.adbase.log(f"Line {self.lnn()}: Failed to unlock {self.trigger[3]}", level="DEBUG")
                                self.tidy_up("all")
                                return
                        elif not self.guest[4]:
                            # out of window
                            self.adbase.log(f"Line {self.lnn()}: Access Alert: Guest device {self.guest[1]} just tried to access lock on {self.guest[3]} outside time window {self.guest[5]}",level="INFO")
                            self.shout("mqtt-status","red")
                            self.shout("loud",f"Guest device {self.guest[1]} just tried to access {self.guest[3]} outside time window {self.guest[5]}",heading="*** Guest Access Alert***")
                            self.tidy_up("all")
                            return
                        else:
                            # wrong lock
                            self.adbase.log(f"Line {self.lnn()}: Access Alert: Guest device {self.guest[1]} tried to access wrong lock: {self.trigger[3]} instead of {self.guest[3]}",level="INFO")
                            self.shout("mqtt-status","red")
                            self.shout("loud",f"Guest device {self.guest[1]} tried to access wrong lock: {self.trigger[3]} instead of {self.guest[3]}",heading="*** Guest Access Alert***")
                            self.tidy_up("all")
                            return
                    else:
                        # device timed out
                        self.adbase.log(f"Line {self.lnn()}: Timeout: Device {self.guest[1]} has already been home for too long ({ts_gap} seconds).", level="INFO")
                        self.shout("mqtt-status","red")
                        self.tidy_up("all")
                        return
                else:
                    # No device arrived yet
                    if self.hass.get_state("binary_sensor.everyone_home") == "off":
                        self.mqtt.mqtt_publish("monitor/run_scan/arrive")
                        self.adbase.log(f"Line {self.lnn()}: Interim: Got the trigger {self.trigger[1]} but no device has changed state to Home yet.",level="DEBUG")
                    else:
                        self.adbase.log(f"Line {self.lnn()}: Everyone home, ignoring trigger {self.trigger[1]}.",level="DEBUG")
                        self.shout("mqtt-status","red")
                        self.tidy_up("all")
                    return
            
            if not len(self.trigger):
                # No trigger yet
                self.adbase.log(f"Line {self.lnn()}: Interim: Device {friendly} just arrived, but no trigger seen yet.",level="DEBUG")
                return
            
            ts_gap = int((ts - self.trigger[2]).total_seconds())
            if ts_gap > self.timeout:
                # Trigger timeout
                self.adbase.log(f"Line {self.lnn()}: Timeout: Resetting Trigger - {self.trigger[1]} last triggered too long ago ({ts_gap} seconds). ",level="DEBUG")
                self.tidy_up("trig") 
                return
            
            # active ent is a resident
            if ent_type == "R": 
                #unlock and tidy up
                self.adbase.log(f"Line {self.lnn()}: This is a Resident and Trigger already happened",level="DEBUG")
                if self.open_up(self.trigger[3],self.resident[1],self.resident[0]):
                    self.adbase.log(f"Line {self.lnn()}:flow check",level="DEBUG")
                    reaction_time = int((self.adbase.datetime()-self.trigger[2]).total_seconds())    #how long between a trigger and the unlock
                    self.adbase.log(f"Line {self.lnn()}: Resident R Unlocked {self.trigger[3]} for {self.resident[1]} in {ts_gap} seconds",level="INFO")
                    self.shout("normal",f"Unlocked {self.trigger[3]} for {self.resident[1]} with reaction time of {reaction_time} seconds",heading="*** Resident Home ***")
                    self.tidy_up("all")
                    return
                else:
                    self.adbase.log(f"Line {self.lnn()}: Failed to unlock {self.trigger[3]}", level="DEBUG")
                    self.tidy_up("all")
                    return
            
            # active ent is a guest
            if ent_type == "G": 
                if self.guest[4] and self.guest[3] == self.trigger[3]:
                    # unlock and tidy up
                    self.adbase.log(f"Line {self.lnn()}: This is a Guest and Trigger already happened",level="DEBUG")
                    if self.open_up(self.trigger[3],self.guest[1],self.guest[0]):
                        reaction_time = int((self.adbase.datetime()-self.trigger[2]).total_seconds())    #how long between a trigger and the unlock
                        self.adbase.log(f"Line {self.lnn()}: Guest G Unlocked {self.trigger[3]} for {self.guest[1]} in {ts_gap} seconds",level="INFO")
                        self.shout("loud",f"Guest Unlocking: {self.trigger[3]} for {self.guest[1]} ({reaction_time} seconds)",heading="*** Guest Access Alert ***")
                        self.tidy_up("all")
                        return
                    else:
                        self.adbase.log(f"Line {self.lnn()}: Failed to unlock {self.trigger[3]}", level="DEBUG")
                        self.tidy_up("all")
                        return
                elif not self.guest[4]:
                    # out of window
                    self.adbase.log(f"Line {self.lnn()}: Access Alert: Guest device {self.guest[1]} just tried to access lock on {self.guest[3]} outside time window {self.guest[5]}",level="INFO")
                    self.shout("loud",f"Guest device {self.guest[1]} just tried to access {self.guest[3]} outside time window {self.guest[5]}",heading="*** Guest Access Alert***")
                    self.shout("mqtt-status","red")
                    self.tidy_up("all")
                    return
                else:
                    # wrong lock
                    self.adbase.log(f"Line {self.lnn()}: Access Alert: Guest device {self.guest[1]} tried to access wrong lock: {self.trigger[3]} instead of {self.guest[3]}",level="INFO")
                    self.shout("loud",f"Guest device {self.guest[1]} tried to access wrong lock: {self.trigger[3]} instead of {self.guest[3]}",heading="*** Guest Access Alert***")
                    self.shout("mqtt-status","red")
                    self.tidy_up("all")
                    return

        except Exception as e:
            self.adbase.log(f"Line {self.lnn()}: State change event: {e}")
            return
#
    def authenticate_guests(self,entity):
    #confirm this is the right time window for guest unlock, also approved door and trigger sensor
        # time window
        try: 
            self.time_window = self.args.get("time_window").split()
            starting = "0"+ self.time_window[0] + ":00"
            ending = "0"+ self.time_window[1] + ":00" 
            now = self.adbase.now_is_between(starting, ending)
        except Exception as e:
            now=False
            self.adbase.log(f"Line {self.lnn()}: Guest time_window error: \n{e}\nInvalid time window configured in auto_unlock.yaml so guest will not have access",level="INFO") 

#        self.adbase.log(f"Line {self.lnn()}: Guests have access: {now}")#,level="DEBUG")   #Enable for Debugging
        try:
            dev = entity [22:]       # match guest to approved lock  or none if outside time window
            self.guest_lock = self.guest_door[dev]
        except Exception as e:
            self.guest_lock = None
            self.adbase.log(f"Line {self.lnn()}: Guest lock allocation error: {e}")
            
        return now
#
    def hass_ts(self,hass):
        # convert a HASS time format to a python datetime format
        ts_list = (hass[:19]).split("T",1)
        ts_str=ts_list[0] + " " + ts_list[1]
        hass_ts = self.adbase.parse_datetime(ts_str)
        pyth_ts = hass_ts + timedelta(minutes=self.adbase.get_tz_offset())
        py_ts = [pyth_ts,hass_ts]
        return py_ts
#
    def open_up(self,lock,key,user_ent):
        if self.door_status_chk(lock,win="recently_opened"):
            self.adbase.log(f"Line {self.lnn()}: flow check - returned ok from door check", level="DEBUG")
            1
        else:
            return False

        if self.user_dict[user_ent] != lock and self.user_dict[user_ent] != "all":
            self.adbase.log(f"Line {self.lnn()}: Failed:: User trying to access unauthorised door.",level="DEBUG")
            return False
            
        self.adbase.log(f"Line {self.lnn()}: flow check - {key} is allowed to open {self.user_dict[user_ent]}. Continuing to open.", level="DEBUG")    
        
        mq_msg = []
        self.adbase.log(f"Line {self.lnn()}: Unlocking: {lock} for {key}.",level="INFO")
        ts_now = self.adbase.get_now()
        self.last_unlock = {"time": ts_now, "lock": lock, "key": key, "user_ent": user_ent }
        
        away = self.alarm_mode.is_state('away')
        
        if self.production_mode and not away:
            if lock == 'front_door':
                self.shout("mqtt-action","unlatch")
                self.adbase.run_in(self.shout_later,self.led_delay,loudness="mqtt-status",msg="green",heading="")
            else:
                self.adbase.call_service("lock/unlock",entity_id=self.lock_list[lock])
                self.adbase.run_in(self.shout_later,self.led_delay,loudness="mqtt-status",msg="green",heading="")
        else:
            self.adbase.log(f"Line {self.lnn()}:<TEST MODE> Unlock service call returned succesfully",level="DEBUG")
            self.shout("mqtt-status","green",heading="")
            self.shout("normal",f"<TEST MODE> Unlocked {lock} succesfully",heading="")
        return True

    def shout(self,loudness, msg,**kwargs):

        # Determine which devcies to notify in the service call
        notif_device = self.admin_device        # default is to notify Admin only
        if self.notif_level == "all": notif_device = "all_phones"
        notif_device = kwargs["notif_device"] if "notif_device" in kwargs else notif_device   # enables other functions to call shout() and choose which devices to notify
        surface = "notify/" + notif_device # default is Admin phone only
        
        # Capture other params from kwargs
        heading = kwargs["heading"] if kwargs.get("heading") else ""
        url_path = kwargs["url"] if kwargs.get("url") else ""
        
        # Define the options for persistence of notifications
        data_loud = {
        #    "clickAction":url_path,        #android url
        #    "url": url_path,               #ios url
            "visibility":"public",
            "channel":"Alarmz",
            "importance":"high",
            "persistent": "true",
            "tag":"persistent",
            "group": "Unlock Notifs"
            }
        data_normal = {
        #    "clickAction":url_path,        #android url
        #    "url": url_path,               #ios url
        #    "timeout": 60,        
            "visibility":"public",
            "channel":"General",
            "group": "Unlock Notifs"
            }
            
        data_level = data_normal                                                        # The default notif peristence level is "normal"
        
        #Start shouting...
        
        if loudness == "mqtt-status":
            self.mqtt.mqtt_publish("/Homeassistant/Auto_Unlock/Status",msg)             # LED colour
            return
        
        if loudness == "mqtt-action":
            self.mqtt.mqtt_publish("nuki/lock/action",msg)                              # Control front door lock
            return

        if loudness == "mqtt-nuki-reboot":
            self.mqtt.mqtt_publish("/rpi/gpio",msg)                              # Reboot front door lock
            return
        
        if loudness == "mqtt-hci":
            self.mqtt.mqtt_publish("hci_monitor/command",msg)                              # Restart front door pi BT
            return

        if loudness == "loud": data_level = data_loud                                   # Check which persistence option to use
        
        self.adbase.call_service(surface,message=msg,title=heading,data=data_level)     # Push out notification
#
    def shout_later(self,kwargs):
        self.adbase.log(f"Line {self.lnn()}:using wrapper for Shout function scheduler",level="DEBUG")
        self.shout(kwargs["loudness"],kwargs["msg"],heading = kwargs["heading"])
#
    def scan_later(self,kwargs):
        self.adbase.log(f"Line {self.lnn()}:using wrapper for Monitor Scan scheduling",level="DEBUG")
        self.mqtt.mqtt_publish("monitor/run_scan/arrive") 
#
    def tidy_up(self,scope):
        #scope = all; trig -> clear trigger
        if scope == "all":
            self.start_ts = ""
            self.resident.clear()
            self.guest.clear()
            self.trigger.clear()
            self.last_unlock.clear()
        if scope == "trig":
            self.trigger.clear()
        if scope == "retries":
            self.last_unlock.clear()
        return
#
    def mqtt_message(self, event_name, data, kwargs):
        """Process a message sent on the MQTT Topic."""
#        self.adbase.log("\n\n***\nfinally in the presence function\n***\n\n")
        mq_msg = []
        mq_msg = [data.get("topic"), data.get("payload")]
#        self.adbase.log(f"Line {self.lnn()}:Topic is: {mq_msg[0]} and payload is: {mq_msg[1]}", level="DEBUG")
        return mq_msg
#
    def lnn(self):
        #Returns the current line number in our program.
        return inspect.currentframe().f_back.f_lineno  
#
    def door_status_chk(self, door, **kwargs):                                                  #function to test of a door has been open in the last X seconds
        contact_sensor = self.door_list[door]                                                   #get the door's contact sensor
        t = kwargs["win"] if "win" in kwargs else "default"                                   #determine which time window from config to use based on call back.
        time_win = self.dot[t]                                                                #time window for door status check
        tm_chg = self.adbase.get_state(contact_sensor, attribute="all")['last_changed']         #get the last time contact sensor changed state (aka last time door opened)

        self.adbase.log(f"Line {self.lnn()}: flow check - about to calc diff", level="DEBUG")
        ts_now = self.adbase.get_now()
        tm_chg = self.adbase.convert_utc(tm_chg)
        diff_secs = datetime.timestamp(ts_now) - datetime.timestamp(tm_chg)                     #how many seconds has it been from now, since the door last opened?
        diff_hms_tidy = str(timedelta(seconds=diff_secs)).split('.')[0]                         #make the time difference human readable (aka in hms format)
        dot_hms_tidy = str(timedelta(seconds=time_win))                                         #make door_open_timeout human readable... not essential
        
        if diff_secs > time_win:                                                            
            self.adbase.log(f"Line {self.lnn()}: Returning **True**. According to {contact_sensor}, {door} last opened at {tm_chg} which is {diff_secs} seconds ago, and more than the window of {time_win} seconds.", level="DEBUG")
            return True
        else:
            self.adbase.log(f"Line {self.lnn()}: Returning **False**. According to {contact_sensor}, last opening was at {tm_chg} so the time diff is {diff_secs} which is within the {time_win} seconds limit.", level="DEBUG")
            return False
#            
    def retry_open (self,trigger):
        #self.trigger = [entity,friendly,ts,lock]
        self.adbase.log(f"Line {self.lnn()}: flow check - doing a retry", level="DEBUG")
        triggered_lock = self.trigger[3]
        trigger_time = self.trigger[2]
        status = False
        if self.last_unlock:                                                        #true, if door unlocked but wasn't opened
            self.adbase.log(f"Line {self.lnn()}: flow check: self.last_unlock isn't empty", level="DEBUG")
            person = self.last_unlock['key']
            user_ent = self.last_unlock['user_ent']
            opened_lock = self.last_unlock['lock']
            last_open_attempt = self.last_unlock['time']
            if triggered_lock == opened_lock:                                       #true, if the trigger is on the same door as we just tried to open
                self.adbase.log(f"Line {self.lnn()}: flow check: same lock triggered this time too", level="DEBUG")
                actual_gap = datetime.timestamp(trigger_time) - datetime.timestamp(last_open_attempt)                       #"gap" is the time between now and when we last tried to open the door
                self.dot["try_gap"] = actual_gap
                not_opened = self.door_status_chk(opened_lock,win="try_gap")        #check if the door has opened since we last tried
                not_expired = True if actual_gap < self.dot['retry'] else False     #check if this attempt is outside the timeout window
                if not_opened and not_expired:                                      #true if we tried and failed to open this door within the timeout
                    self.adbase.log(f"Line {self.lnn()}: Giving {person} one more chance to open {opened_lock}", level="DEBUG")
                    self.open_up(opened_lock,person,user_ent)
                    status = True
                else:
                    self.adbase.log(f"Line {self.lnn()}: Doing nothing. Either {opened_lock} has been opened ({not not_opened})\n Or window has expired ({not not_expired}):: Gap was: {actual_gap} and Window is {self.dot['retry']}", level="DEBUG")
                    status = False
                self.tidy_up("retries")
            else:
                self.adbase.log(f"Line {self.lnn()}: Doing nothing. Trigger is for {triggered_lock} but we last tried to open {opened_lock}.", level="DEBUG")
                status = False                                                   #if triiger is for a different door, do nothing
        else:
            self.adbase.log(f"Line {self.lnn()}: Doing nothing. {triggered_lock} opened fine last time we unlocked it.", level="DEBUG")
            status = False                                                       #if door unlocked AND opened, do nothing
        return status
#
    def trigger_classifier(self,trigger): 
            # get trigger details
            # test for indicators of noise
            # return classification
        #self.adbase.log(f"Line {self.lnn()}: Doing nothing.",level="DEBUG")
        triggered_sensor_ent = self.trigger[0]
        triggered_sensor_name = self.trigger[1]
        trigger_time = self.trigger[2]
        triggered_lock = self.trigger[3]
        it_is_noise = ""
        #self.adbase.log(f"Line {self.lnn()}: ***\n triggered_sensor_ent: {triggered_sensor_ent}\n triggered_sensor_name: {triggered_sensor_name}\n trigger_time: {trigger_time}\n triggered_lock: {triggered_lock}\n",level="DEBUG")
        
        # noise 1: check the other sensors for movement
        for entity in self.noise_list:
            
            if entity == "timeout":                     #"timeout" is how long to wait for a noise trigger. each sensor can have its own, or use the overall default timeout
                timeout = self.noise_list[entity]
                continue
            
            try: 
                ent = self.noise_list[entity].split()
                sensor_type = ent[0]
                timeout = int(ent[1])
            except:
                sensor_type = self.noise_list[entity]
                
            noise_ent = self.adbase.get_state(entity,attribute="all")
            if noise_ent == None:
                self.adbase.log(f"Line {self.lnn()}: Please double check that this entity exists: {entity}",level="DEBUG")
                continue
            
            noise_name = noise_ent['attributes']['friendly_name']
            ts = self.hass_ts(noise_ent["last_changed"])[0]
            gap = datetime.timestamp(trigger_time) - datetime.timestamp(ts)
            state = noise_ent['state']
            
            self.adbase.log(f"Line {self.lnn()}: {noise_name} last changed at {ts} to {state}. Gap is {gap}.",level="DEBUG")
            
            if gap < timeout:
                if sensor_type == 'contact':
                    self.adbase.log(f"Line {self.lnn()}: Timeout is {timeout}. {noise_name} of type {sensor_type}  changed state to {state} {gap} seconds ago",level="DEBUG")
                    it_is_noise = noise_name
            
                if sensor_type == 'motion':    
                    self.adbase.log(f"Line {self.lnn()}: Timeout is {timeout}. {noise_name} of type {sensor_type} changed state to {state} {gap} seconds ago",level="DEBUG")
                    it_is_noise = noise_name
                
                if sensor_type == 'other':    
                    self.adbase.log(f"Line {self.lnn()}: Timeout is {timeout}. {noise_name} of type {sensor_type} changed state to {state} {gap} seconds ago",level="DEBUG")
                    it_is_noise = noise_name
                
                if it_is_noise: break
            
        self.adbase.log(f"Line {self.lnn()}: returning {it_is_noise}.",level="DEBUG")
        return it_is_noise
        








