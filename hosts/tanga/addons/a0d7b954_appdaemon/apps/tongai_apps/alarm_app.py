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

class AlarmApp(ad.ADBase):
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
        self.door_list = self.args.get("door_contact")
        
        self.adbase.log("\n\n************\n*\n* Welcome to Alarm App   ************\n*\n************\n") #Launch message
        
        # load configuration 
        self.admin_dev = self.args.get('admin_device')
        self.admin_url = self.args.get('admin_url')
        self.other_url = self.args.get('other_url')
        all_home_sensor = self.args.get('all_home')
        presence_sensor = self.args.get('presence')
        disable_out_mode = self.args.get('disable_presence_check') # when this is TRUE, the system becomes manual - will not automatically switch to Out or Away.
        holiday_sensor = self.args.get('holiday')
        mute_alarm = self.args.get('mute_alarm')
        car_location_sensor = self.args.get('car_location')
        car_alarm_off = self.args.get('car_alarm_off')
        self.out_to_away_timeout = int(self.args.get('out_to_away_timeout'))*3600 #the timeout is in config in hours, convert to seconds
        self.summer_months = [int(i) for i in self.args.get('summer_months').split()]
        self.mode_params = self.args.get('mode_params')
        self.lights = self.args.get('lights')
        self.light_routines = {}
        self.home_perimeter = self.args.get('home_perimeter')
        self.car_perimeter = self.args.get('car_security')
        self.all_home_sensor = self.adbase.get_entity(all_home_sensor)
        self.presence_sensor = self.adbase.get_entity(presence_sensor)
        self.disable_out_mode = self.adbase.get_entity(disable_out_mode)
        self.holiday_sensor = self.adbase.get_entity(holiday_sensor)
        self.mute_alarm = self.adbase.get_entity(mute_alarm)
        self.car_location_sensor = self.adbase.get_entity(car_location_sensor)
        self.car_alarm_off = self.adbase.get_entity(car_alarm_off)
        self.nearly_home_flag = self.adbase.get_entity('input_boolean.nearly_home')
        self.alr_st = self.adbase.get_entity('input_text.alarm_status')
        self.force_home = self.adbase.get_entity('input_boolean.force_home_mode')
        force_home_id = 'input_boolean.force_home_mode'
        self.out_flag = False
        self.house_listener = ""
        self.car_listener = ""
        self.plus_n_seconds = 43200
        
        #Initialise Alarm mode
        self.holiday_sensor.turn_off()  #when app restarts it should use Home mode by default
        self.modes(presence_sensor,"all","on","off","null") #call function to set schedule for the first time
   
        # Listen for mode qualifiers:
        self.adbase.log(f"Line {self.au.lnn()}: ****\nRunning Listeners ",level="DEBUG")
        self.adbase.listen_state(self.modes,[presence_sensor,holiday_sensor])
        self.adbase.listen_state(self.force_home_mode, force_home_id, attribute='all')
         
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
        
    def lighting(self,schedule): #mode should be a param passed in
        mode = schedule['mode']
        self.adbase.log(f"Line {self.au.lnn()}: *** Started function {sys._getframe().f_code.co_name.upper()} with mode: {mode}",level="INFO")   
        
        # reset all the running routines
        for h in self.light_routines:
            self.adbase.log(f"Line {self.au.lnn()}: New mode: {mode} so cancelling {h}",level="DEBUG")
            h_del = self.light_routines[h]
            self.adbase.cancel_timer(h_del)
        self.light_routines.clear()
        
        #downstairs lights off
        ent = "light.downstairs_lights" 
        handle = self.adbase.run_daily(self.switch_later,schedule['nighttime'],entity=ent,state="off",typ="light")
        hdl_key = mode+"_"+ent+"_off"
        self.light_routines[hdl_key]=handle
            
        if mode == "home":
            # Hall Night Light 
            ent = "light.lounge_lamp_2"
            State = "dim"
            handle = self.adbase.run_daily(self.switch_later,schedule['bedtime'],entity=ent,state=State,typ="light")
            hdl_key = mode+"_"+ent+"_"+State
            self.light_routines[hdl_key]=handle
            
        if mode == "out":
            # Lounge Lamps on low at sunset 
            ent = "light.wall_lamps"
            State="dim"
            handle = self.adbase.run_daily(self.switch_later,schedule['sunset'],entity=ent,state=State,typ="light")
            hdl_key = mode+"_"+ent+"_"+State
            self.light_routines[hdl_key]=handle
        
            # Hall Night Light 
            ent = "light.lounge_lamp_2"
            State="dim"
            handle = self.adbase.run_daily(self.switch_later,schedule['nighttime'],entity=ent,state=State,typ="light")
            hdl_key = mode+"_"+ent+"_"+State
            self.light_routines[hdl_key]=handle
            State="off"
            handle = self.adbase.run_daily(self.switch_later,schedule['wakeup'],entity=ent,state=State,typ="light")
            hdl_key = mode+"_"+ent+"_"+State
            self.light_routines[hdl_key]=handle
        
        if mode == "away":
            # Lounge Lamps on low at sunset 
            ent = "light.wall_lamps"
            State="dim"
            handle = self.adbase.run_daily(self.switch_later,schedule['sunset'],entity=ent,state=State,typ="light")
            hdl_key = mode+"_"+ent+"_"+State
            self.light_routines[hdl_key]=handle
            
            #Isla on sunset-bedtime -1hr random 
            ent = "light.hannah_lamp"
            State="dim"
            if schedule['season'] == "winter": #in the winter also come on early and off at sunrise
                handle = self.adbase.run_daily(self.switch_later,schedule['wakeup'],random_start=-900, random_end=900, entity=ent,state=State,typ="light")
                hdl_key = "WINTER_"+mode+"_"+ent+"_"+State
                self.light_routines[hdl_key]=handle
            handle = self.adbase.run_daily(self.switch_later,schedule['sunset'],random_start=-900, random_end=900, entity=ent,state=State,typ="light")
            hdl_key = mode+"_"+ent+"_"+State
            self.light_routines[hdl_key]=handle
            State="off"
            if schedule['season'] == "winter": #in the winter also come on early and off at sunrise
                handle = self.adbase.run_daily(self.switch_later,schedule['sunrise'],random_start=-900, random_end=1800, entity=ent,state=State,typ="light")
                hdl_key = "WINTER_"+mode+"_"+ent+"_"+State
                self.light_routines[hdl_key]=handle
            off_time = (self.adbase.parse_datetime(schedule['bedtime']) - timedelta(hours=1)).time()
            handle = self.adbase.run_daily(self.switch_later,off_time,random_start=-900, random_end=900,entity=ent,state="off",typ="light")
            hdl_key = mode+"_"+ent+"_"+State
            self.light_routines[hdl_key]=handle
            
            #M side on sunset-bedtime random
            ent = "light.ellie_window_lamp"
            State="dim"
            handle = self.adbase.run_daily(self.switch_later,schedule['sunset'],random_start=-900, random_end=900,entity=ent,state=State,typ="light")
            hdl_key = mode+"_"+ent+"_"+State
            self.light_routines[hdl_key]=handle
            State="off"
            off_time = (self.adbase.parse_datetime(schedule['bedtime']) - timedelta(hours=0)).time() # can be used to add an offset if needed. currently, offset is 0
            handle = self.adbase.run_daily(self.switch_later,off_time,random_start=-1800, random_end=1800,entity=ent,state=State,typ="light")
            hdl_key = mode+"_"+ent+"_"+State
            self.light_routines[hdl_key]=handle
            
            # Hall Night Light 
            ent = "light.lounge_lamp_2"
            State="dim"
            handle = self.adbase.run_daily(self.switch_later,schedule['nighttime'],entity=ent,state=State,typ="light")
            hdl_key = mode+"_"+ent+"_"+State
            self.light_routines[hdl_key]=handle
            State="off"
            handle = self.adbase.run_daily(self.switch_later,schedule['wakeup'],entity=ent,state=State,typ="light")
            hdl_key = mode+"_"+ent+"_"+State
            self.light_routines[hdl_key]=handle

    def climate_control(self,schedule): #mode should be a param passed in
        mode = schedule['mode']
        self.adbase.log(f"Line {self.au.lnn()}: *** Started function {sys._getframe().f_code.co_name.upper()} with mode: {mode}",level="INFO")
        
        any_tado_room = "climate.study"
        all_tados = "group.tado_rads"
        warm =20 #this is the boost temp in degrees
        nearly_home = self.nearly_home_flag.is_state("on")
        
        if nearly_home:
            tado = "home"
            nest = "none"
        else:
            tado,nest = ("away","eco") if mode == "away" else ("home","none")
        
        self.adbase.call_service("climate/set_hvac_mode",entity_id=all_tados,hvac_mode="auto")  #this is like "resume schedule" if geo loc is away, schedule is frost prevention 
        self.adbase.call_service("water_heater/set_operation_mode",entity_id="water_heater.hot_water",operation_mode="auto")  #this is like "resume schedule" if geo loc is away, schedule is off
        self.adbase.call_service("climate/set_preset_mode",entity_id=all_tados,preset_mode=tado)
        self.adbase.call_service("climate/set_preset_mode",entity_id="climate.downstairs",preset_mode=nest)
        
        if  nearly_home:
            self.adbase.call_service("tado/set_water_heater_timer",entity_id="water_heater.hot_water",time_period="00:30:00")
            if schedule['season'] == "winter":
                self.adbase.call_service("tado/set_climate_timer",entity_id=all_tados,time_period="00:30:00", temperature=warm)
                self.adbase.call_service("script/turn_on",entity_id="script.boost_downstairs")

    def cameras(self,schedule): #mode should be a param passed in
        mode = schedule['mode']
        self.adbase.log(f"Line {self.au.lnn()}: *** Started function {sys._getframe().f_code.co_name.upper()} with mode: {mode}",level="INFO")
        
    def robots(self,schedule): #mode should be a param passed in
        mode = schedule['mode']
        self.adbase.log(f"Line {self.au.lnn()}: *** Started function {sys._getframe().f_code.co_name.upper()} with mode: {mode}",level="INFO")
    
    def automations(self,schedule): #mode should be a param passed in
        mode = schedule['mode']
        self.adbase.log(f"Line {self.au.lnn()}: *** Started function {sys._getframe().f_code.co_name.upper()} with mode: {mode}",level="INFO")
        # call a service automation.turn_on/off
        # automation.timed_pump
        
    def modes(self,entity, attribute, old, new, kwargs):

        self.adbase.log(f"Line {self.au.lnn()}: {sys._getframe().f_code.co_name.upper()} - updating all functions for new mode",level="INFO")
        
        mode = self.set_mode()
        schedule = self.get_schedule(mode)
        self.adbase.set_state(entity_id="sensor.alarm_mode", state = schedule["mode"].title(), attributes=schedule) 
        
        #Clean up prior listeners
        try:
            for i in self.house_listener:
                self.adbase.cancel_listen_state(i)
            for j in self.car_listener:
                self.adbase.cancel_listen_state(j)
        except:
            pass # True on first run
        
        self.adbase.log(f"{self.mode_overview(schedule)}",level="INFO") # confirm the behaviour when in this mode
        
        # Activate the mode across all functions
        self.house_listener = self.adbase.listen_state(self.perimeter,self.home_perimeter,new="on",schedule=schedule,zone="building") 
        self.car_listener = self.adbase.listen_state(self.perimeter,self.car_perimeter,new="on",schedule=schedule, zone="car")
        self.adbase.log(f"Line {self.au.lnn()}: *** Started listeners for PERIMETER with mode: {mode}",level="INFO")
        self.lighting(schedule)
        self.climate_control(schedule)
        
        #-- WIP functions
        self.cameras(schedule)
        self.robots(schedule)
        self.automations(schedule)
        #--
        
        if self.nearly_home_flag.is_state("on"):
            self.nearly_home_flag.set_state(state="off") 
        
        # self.adbase.log(f"Line {self.au.lnn()}: **** All functions activated",level="DEBUG")

        #self.test_trig()  
        
    def force_home_mode(self, entity, attribute, old, new, kwargs):
        
        if new['state'] == 'on':
            self.holiday_sensor.turn_off() # if the force home button is pressed, disable "Away" mode
            self.force_home.turn_off() #then reset the force home button
            #--self.modes(None, None, None, None, None) # refresh modes
            # -- disabled this timer--#Start 24 hour timer
            #--self.force_home_timer = self.adbase.run_in(self.send_force_home_reminder, self.plus_n_seconds)
            
    def send_force_home_reminder(self, kwargs):
        self.notif("shout","input_boolean.force_home_mode",message="Force Home Mode is still on!", heading="Friendly Reminder", notif_type="other")
        self.force_home_timer = self.adbase.run_in(self.turn_off_force_home, self.plus_n_seconds)
    
    def turn_off_force_home(self, kwargs):
        self.force_home.turn_off()
        
    def set_mode(self): #function to decide what mode we're in
        
        force_home = self.adbase.get_entity('input_boolean.force_home_mode')
        if force_home.is_state("on"):
            return "home"
            
        is_away = self.holiday_sensor.is_state("on")
        is_out = self.presence_sensor.is_state("off") and self.disable_out_mode.is_state("off")
        
        if is_out:
            if is_away: 
                mode = "away"
            else:
                mode = "out"
                if not self.out_flag:
                    self.out_timer_handle = self.adbase.run_in(self.out_timer,self.out_to_away_timeout)  #if we're still out in 24hrs (86400 seconds), change mode to "away"
                    self.out_flag = True
        else:
            if self.out_flag:
                self.adbase.cancel_timer(self.out_timer_handle)   # reset out timer
                self.out_flag = False
            if is_away:
                mode = "away"
                #cleaning maman scenario
            else:
                mode = "home"
        self.adbase.log(f"\n\n************\n*\n*Currently in {mode.upper()} mode\n*\n************\n",level="DEBUG")        
        return mode
    
    def out_timer(self,cb_args):
        
        self.holiday_sensor.set_state(state="on")
        self.out_flag = False
        
    def get_schedule(self,mode): #mode should be a param passed in
     #   self.adbase.log(f"Line {self.au.lnn()}: Started function {sys._getframe().f_code.co_name.upper()}",level="DEBUG")
        
        # get the schedule 
        month = datetime.now().month
        season = "summer" if month in self.summer_months else "winter"
        sunset = self.mode_params[season]['sunset']
        sunrise = self.mode_params[season]['sunrise']
        evening = self.mode_params[season]['evening']
        bedtime = self.mode_params[season]['bedtime']
        nighttime = self.mode_params[season]['nighttime']
        wakeup = self.mode_params[season]['wakeup']
        
        schedule = {'mode':mode,'season':season,'dash_season':season.title(),'sunset':sunset,'sunrise':sunrise,'evening':evening,'bedtime':bedtime,'wakeup':wakeup, 'nighttime': nighttime}
      #  self.adbase.log(f"Line {self.au.lnn()}: In mode {schedule['mode']} and it is {schedule['season']} and wakeup is at {schedule['wakeup']}",level="DEBUG")
        return schedule 
    
    def switch_later(self,kwargs):
       #  self.adbase.log(f"Line {self.au.lnn()}: Started function {sys._getframe().f_code.co_name.upper()}",level="DEBUG")    
        # this is run at specific times with state being on, off, %brightness, Robert everywhere run 
        ent = kwargs['entity']
        new_state = kwargs['state']
        dev_type = kwargs['typ']
        if dev_type == 'light':
            if new_state == 'on':
                self.hass.turn_on(ent)
            elif new_state == 'dim':
                if self.lights[ent] > 0:
                    Brightness = self.lights[ent]
                    if self.all_home_sensor.is_state("on") and ent=="light.lounge_lamp_2":
                        pass
                    else:
                        self.adbase.call_service("light/turn_on",entity_id=ent,brightness_pct=Brightness)
                    # use a service call for light.turn_on
                    #self.hass.turn_on(ent,brightness=Brightness)
            elif new_state == 'off':
                self.hass.turn_off(ent)
        elif dev_type == 'robert':
            pass
                
        self.adbase.log(f"Line {self.au.lnn()}: Done switch later: entity {ent} going {new_state} for type {dev_type}", level="DEBUG")
    
    def notif(self,level, ent,**kwargs):
    #     self.adbase.log(f"Line {self.au.lnn()}: Started function {sys._getframe().f_code.co_name.upper()}",level="DEBUG")
    
        # Capture other params from kwargs
        heading = kwargs["heading"] if kwargs.get("heading") else "House Alarm"
        url_path = kwargs["url"] if kwargs.get("url") else self.admin_url
        notif_type = kwargs["notif_type"] if kwargs.get("notif_type") else "none"
        ent_name = self.adbase.get_state(ent,attribute="friendly_name")
        not_muted = self.mute_alarm.is_state("off")
        
        if level == "scream":
            notif_device = self.admin_dev   #"parents"
            data_txt = {
                "clickAction":url_path,        #android url
                "visibility":"public",
                "channel":"Alarmz",
                "importance":"high",
                "persistent": "true",
                "tag":"persistent",
                "group": "Alarm Notifs"
                }
            data_ios = {
                "url": url_path,               #ios url
                "visibility":"public",
                "channel":"Alarmz",
                "importance":"high",
                "persistent": "true",
                "tag":"persistent",
                "group": "Alarm Notifs"
                }

            data_tts = {
                "tts_text": "Alarm has been triggered. Please check home assistant."
                }
                
        elif level == "flag": 
            pass
        
        elif level == "shout":
            notif_device = self.admin_dev
            data_txt = {
                "clickAction":url_path,        #android url
        #        "timeout": 60,        
                "visibility":"public",
                "channel":"General",
                "group": "Alarm Notifs"
                }
                
        else:
            notif_device = self.admin_dev
            data_txt = {
                "clickAction":url_path,        #android url
        #        "timeout": 60,        
                "visibility":"public",
                "channel":"General",
                "group": "Alarm Notifs"
                }
                
        surface = "notify/" + notif_device # default is Admin phone only
        
        if notif_type == "other":
            msg = kwargs['message']
        else:
            msg = f"ALERT: {ent_name} was triggered. Mode is {kwargs['mode']}."
        
        #Send notification...
        
        self.adbase.call_service(surface,message=msg,title=heading,data=data_txt)     # Push out notification
        if level == "scream" and not_muted:
            self.adbase.call_service(surface,message="TTS",data=data_tts)     # voice notif

#
    def notif_later(self,kwargs):
    #     self.adbase.log(f"Line {self.au.lnn()}: Started function {sys._getframe().f_code.co_name.upper()}",level="DEBUG")    
        self.adbase.log(f"Line {self.lnn()}:using wrapper for Shout function scheduler",level="DEBUG")
        self.shout(kwargs["loudness"],kwargs["msg"],heading = kwargs["heading"])
    
    def mode_overview(self,schedule):
        self.adbase.log(f"Line {self.au.lnn()}: Started function {sys._getframe().f_code.co_name.upper()}",level="DEBUG")
        
        # summarise what the current mode will do
        mode=schedule['mode']
        nearly_home = self.nearly_home_flag.is_state("on")
        
        season=schedule['season']
        sunrise=schedule['sunrise']
        wakeup=schedule['wakeup']
        sunset=schedule['sunset']
        evening=schedule['evening']
        bedtime=schedule['bedtime']
        nighttime=schedule['nighttime']
        
    #     Always:
        dl = "Downstairs Lights"
        nl = "Night light (if someone is out)" # if self.all_home_sensor.is_state("off") and self.presence_sensor.is_state("on"):
    
    #     By mode:
        cs = "Car Security"
        bp = "Building Perimeter"
        au = "Auto-Unlock"              # (disable when "away")
        rb = "Robert"                   # (WIP: 2hrs after we are "away" clean everywhere then disable schedules)
        hw = "Hot Water"                # (off if away)
        ll = "Wall Lamps"             # (dimmed if not home)  Brightness = self.lights[group.lounge_lamps]
        el = "E Lamp"
          
    #     By mode and Season:
        hl = "H Lamp"                  # on morning (winter) and evening
        ha = "Heating and AC"          # (if nearly Home, boost heat in winter)
        
        overview = {}
        overview[dl]={}
        overview[nl]={}
        overview[cs]={}
        overview[bp]={}
        overview[au]={}
        overview[rb]={}
        overview[hw]={}
        overview[ll]={}
        overview[el]={}
        overview[hl]={}
        overview[ha]={}
        
        overview["schedule"]=schedule
        overview[dl]="off at "+nighttime 
        overview[nl]="on from "+bedtime +" to "+wakeup+" if someone is out"
            
        if mode == "home":
            overview[cs]="armed from "+evening+" to "+wakeup+" if on driveway else always armed" 
            overview[bp]="armed from "+bedtime+" to "+wakeup
            overview[ha]="on the usual schedule"
            overview[hw]="on the usual schedule"
            
        elif mode == "out":
            overview[cs]="always armed"
            overview[bp]="armed from "+bedtime+" to "+wakeup
            overview[ll]="on and dimmed to "+str(self.lights["light.wall_lamps"])+"% at "+sunset+" and off at "+nighttime
            overview[ha]="on the usual schedule"
            overview[hw]="on the usual schedule"
            
        elif mode == "away":
            overview[cs]="always armed"
            overview[bp]="always armed"
            overview[ll]="on and dimmed to "+str(self.lights["light.wall_lamps"])+"% at "+sunset+" and off at "+nighttime
            overview[ha]="always off"
            overview[hw]="always off"
            overview[el]="on and dimmed to "+str(self.lights["light.ellie_window_lamp"])+"% at "+sunset+" and off at "+bedtime
            overview[hl]["summer"]="on and dimmed to "+str(self.lights["light.hannah_lamp"])+"% at "+sunset+" and off at "+bedtime
            overview[au]="disabled"
            overview[rb]="wait 2hrs, then clean everywhere, then disable schedules"
            overview[hl]["winter"]="on and dimmed to "+str(self.lights["light.hannah_lamp"])+"% at "+wakeup+" and off at "+sunrise+"; then in the evening, is on and dimmed to "+str(self.lights["light.isla_wall"])+"% at "+sunset+" and off at "+bedtime
                
        if nearly_home:
            overview[hw]="doing a 30 minute heating boost"
            if season == "winter":
                overview[ha]="on for 30 minute boost"
            
        if self.car_alarm_off and mode in ('out','away'):
            overview[cs]="manually disarmed"
       
        ov = [0,1,2,3,4,5,6,7]
        rt = [0,1,2,3,4,5,6,7,8,9]
        ov[0]="Mode: "+mode.upper()
        ov[1]="Season: "+season.upper()
        ov[2]="Sunrise: "+sunrise
        ov[3]="Sunset: "+sunset
        ov[4]="Wake Up: "+wakeup
        ov[5]="Evening: "+evening
        ov[6]="Bedtime: "+bedtime
        ov[7]="Nighttime: "+nighttime
        
        rt[0]="Downstairs lights are "+overview[dl]
        rt[1]="Night light is "+overview[nl]
        rt[2]="Lounge lights are "+overview[ll] if mode != "home" else "Lounge Lights are not automated"
        rt[3]="Ellie's room light is "+overview[el] if mode == "away" else "Ellie's Room is not automated"
        rt[4]="Hannah's room light is "+overview[hl][season] if mode == "away" else "Hannah's Room is not automated" 
        rt[5]="Car security is "+overview[cs]
        rt[6]="Building perimeter is "+overview[bp]
        rt[7]="Climate control is "+overview[ha]
        rt[8]="Hot water is "+overview[hw]
        rt[9]="Others are wip"  #+overview[au]
        
        routine={}
        for i in range(len(rt)):
            k=chr(ord('a')+i).upper()+"."
            routine[k]=rt[i]

        sep = "\n*--   "
        status=f"\n\n*********\n*\n* Overview\n*\n*--   {ov[0]}   {ov[1]}\n*\n*--   {ov[2]};  {ov[3]};  {ov[4]};  {ov[5]};  {ov[6]};  {ov[7]}\n*\n***** Routine\n*\n*--   {sep.join(rt)}\n*\n********\n"
        #self.alr_st.set_state(state=f"{ov[0]} > {ov[1]}")
        self.adbase.set_state(entity_id="sensor.alarm_schedule", state = mode.title()+" - "+season.title(), attributes=routine, replace="True")
        
        return status
    
    def test_trig(self):
        self.adbase.set_state("binary_sensor.bathroom_window_contact", state="on")
        time.sleep(1)
        self.adbase.set_state("binary_sensor.bathroom_window_contact", state="off")
        # evie door
        self.adbase.set_state("binary_sensor.bathroom_window_contact", state="on")
        time.sleep(1)
        self.adbase.set_state("binary_sensor.bathroom_window_contact", state="off")
        # switch on a light
        self.adbase.set_state("binary_sensor.bathroom_window_contact", state="on")
        time.sleep(1)
        self.adbase.set_state("binary_sensor.bathroom_window_contact", state="off")