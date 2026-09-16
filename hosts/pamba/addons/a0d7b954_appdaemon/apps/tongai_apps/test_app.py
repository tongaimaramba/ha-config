import adbase as ad
#import re
#import copy
from datetime import datetime, timedelta, timezone, time
#from time import sleep
#import traceback
#import requests
#import getpass
import sys
#import numpy as np



class TestApp(ad.ADBase):
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
        self.pi = self.adbase.get_app("aut")

        self.adbase.log("\n\n************\n*\n* Welcome to Test App\n*\n************\n") #Launch message
        
        #self.ts(60,"11:14:01")
        
    def ts(self, to, et):
        valid = "last event was more recent than cut_off_time - resolution needed"
        invalid = "last event happened too long ago"
        a = self.pi.check_timeout(timeout=to, event_time=et)
        #result = valid if a else invalid
        self.adbase.log(f"Line {self.au.lnn()}: event time: {a[0]}, cut-off: {a[1]}, timeout window: {a[2]}, status: {a[3]}")     
        #self.adbase.log(f"Line {self.au.lnn()}: {result}")  #, level="DEBUG")
""" 
# ----- Start range sensor app 
        self.detector = self.args.get("range_sensor")
        self.ranges = self.args.get("ranges")
        self.range_led = self.args.get("parking_light")
        self.hass.turn_off(self.range_led)
        self.led_timeout = self.args.get("led_timeout")
        self.snooze_time = self.args.get("snooze_time")
        self.rgb_to_name = {"[0, 128, 0]":"green","[255, 165, 0]":"orange","[255, 0, 0]":"red","[0, 0, 255]":"blue","[0, 0, 0]":"black"}
        self.colours_list = ("green","orange","red","blue","black")
        self.colour_in_use = dict.fromkeys(self.colours_list,False)
        self.timer_handles = dict.fromkeys(self.colours_list,0)
        self.array_size = 5 
        self.readings = [False]*self.array_size
        self.colours_all_off = False
        self.more_data = False
        self.br=50 #brightness level for testing is 10
        self.oor=10

        
        self.adbase.log(f"Initialised", level="DEBUG")
        
        self.adbase.listen_state(self.mode,self.detector,attribute="all")

    def mode(self,entity, attribute, old, new, kwargs):
        self.adbase.log(f"Line {self.au.lnn()}: {new['state']}m",level="INFO")
        self.position = float(new['state']) if new['state'] != 'unknown' else self.oor
        if new['state'] == "0.03" or new['state'] == "0.04":
            self.position = self.oor
            self.adbase.log(f"Line {self.au.lnn()}: Ignored signal {new['state']}m so set to range {self.position}m and ignoring.",level="DEBUG")
        
        delay = self.led_timeout
        rgb = str(self.adbase.get_state(self.range_led,attribute="all")["attributes"]["rgb_color"])
        try:
            current_colour = self.rgb_to_name[rgb]
        except:
            current_colour = "off"
        
        if self.position > self.ranges['parking_green'] and self.position <= self.oor:
            colour = "orange"                           #still too far out
        elif self.position > self.ranges['parking_red'] and self.position < self.ranges['parking_green']:
            colour = "green"                            #perfect parking zone
        elif self.position < self.ranges['front_door']:
            colour = "blue"                              #when someone is at the door, turn off the parking light
        elif self.position > self.ranges['front_door'] and self.position < self.ranges['parking_red']:
            colour = "red" #parked too close
        else:
            colour = "black"
                
        self.adbase.log(f"Line {self.au.lnn()}: Mode function called. Key params: range: {self.position}m; range status:{colour}; current colour: {current_colour} ({rgb}); delay: {delay}", level="DEBUG")
        
######### if colour is blue, ignore the parking/leaving thing.
        
        if colour == "blue":
            if not self.colour_in_use[colour]:                 #make sure we haven't already set to this colour
                self.adbase.log(f"Line {self.au.lnn()}: Status: {colour} ## Range {self.position}m ## Previous Status: {current_colour}",level="INFO")
                delay = self.led_timeout/15
                self.adbase.call_service("light/turn_on", entity_id =self.range_led, color_name = colour,brightness_pct=self.br)
        ###-->> self.hass.turn_on(self.range_led, color_name = colour,brightness_pct=self.br)
                self.colour_in_use[colour] = self.adbase.run_in(self.do_later,delay,entity=self.range_led,status=colour,type="light")

                for c in self.colour_in_use:
                    if c != colour:
                        self.adbase.log(f"Line {self.au.lnn()}: 1. Colour: {c} Handle: {self.colour_in_use[c]} and Status: {self.colour_in_use[c]}",level="DEBUG")
                        self.adbase.cancel_timer(self.colour_in_use[c], False)
                        self.colour_in_use[c] = False
                    self.adbase.log(f"Line {self.au.lnn()}: 2. Colour: {c} Handle: {self.colour_in_use[c]} and Status: {self.colour_in_use[c]}",level="DEBUG")

                self.adbase.log(f"Line {self.au.lnn()}: ### Current State is {self.colour_in_use}",level="DEBUG")

        else:
            dir = self.normalise(self.position)
            self.adbase.log(f"Line {self.au.lnn()}: Direction is: {dir}", level="DEBUG")
            if dir == "Parking":
                if not self.colours_all_off:
                    if not self.colour_in_use[colour]:                 #make sure we haven't already set to this colour
                        self.adbase.log(f"Line {self.au.lnn()}: {dir} - {colour} ## Range {self.position}m ## Previous Status: {current_colour}",level="INFO")
                        delay = self.led_timeout+30 if colour == "red" else self.led_timeout
                        self.adbase.call_service("light/turn_on", entity_id =self.range_led, color_name = colour,brightness_pct=self.br)
                ###-->> self.hass.turn_on(self.range_led, color_name = colour,brightness_pct=self.br)
                        self.colour_in_use[colour] = self.adbase.run_in(self.do_later,delay,entity=self.range_led,status=colour,type="light")

                        for c in self.colour_in_use:
                            if c != colour:
                                self.adbase.log(f"Line {self.au.lnn()}: >>>1. Colour: {c} Handle: {self.colour_in_use[c]} ",level="DEBUG")
                                self.adbase.cancel_timer(self.colour_in_use[c], False)
                                self.colour_in_use[c] = False
                            self.adbase.log(f"Line {self.au.lnn()}: ---2. Colour: {c} Handle: {self.colour_in_use[c]}",level="DEBUG")
                                
                    self.adbase.log(f"Line {self.au.lnn()}: ### Current State is {self.colour_in_use}",level="DEBUG")
                    
            elif dir == "Leaving": 
                self.adbase.call_service("light/turn_off", entity_id =self.range_led)
        ###-->> self.hass.turn_off(self.range_led)
                self.colour_in_use = dict.fromkeys(self.colours_list,False)
                self.adbase.log(f"Line {self.au.lnn()}: {dir}", level="INFO")
                self.adbase.log(f"Line {self.au.lnn()}: ### Current State is {self.colour_in_use}",level="DEBUG")
                
#        if direction is parking, shout once (every 5 min?) to extend door timeout to 5 mins  - use do_later, set time out to 10s and run twice for door, and 3 times for light
 
    def normalise(self,range,**kwargs):
        
        if range == self.oor:
            return "invalid"
        
        # get the datapoints
        i = 0
        
        #Future: add a flag to make the script run through fewer data points if this is an extended run (i.e. need more data)
        self.adbase.log(f"Line {self.au.lnn()}:  working loops: {self.array_size}", level="DEBUG")    
        
        while i < self.array_size:
            
            self.adbase.log(f"Line {self.au.lnn()}:  working loops, iteration number: {i}", level="DEBUG")
            
            if not self.readings[i]:
                self.readings[i] = range
                return "Working"
            else: 
                i += 1
        
        self.adbase.log(f"Line {self.au.lnn()}:  anomalies loops: {self.array_size} for data points: {self.readings}", level="DEBUG")  
        
        # look for anomalies 
        sz = self.array_size - 1
        res = [False]*sz
        
        i=0
        self.adbase.log(f"Line {self.au.lnn()}:  anomalies loops array size: {sz}",level="DEBUG")
        
        while i < (self.array_size-1):
            r = (self.readings[i] - self.readings[i+1])
            res[i] = np.sign(r)
            self.adbase.log(f"Line {self.au.lnn()}:  anomaly loop (full), iteration number: {i} and sign is {res[i]}", level="DEBUG")
            i += 1
        
        v = int(self.array_size*0.3)
        i = self.array_size - v - 1
        r = 0
        
        self.adbase.log(f"Line {self.au.lnn()}: \n**\n",level="DEBUG")
        
        while i < (self.array_size-1):
            r += res[i]
            self.adbase.log(f"Line {self.au.lnn()}: anomaly loop (last few), iteration number: {i} and sum is {r}", level="DEBUG")
            i += 1
        
        agg_dir = sum(res)
        self.adbase.log(f"Line {self.au.lnn()}: direction factors: agg_dir: {agg_dir}; latest dir: {r}; size of last few {v}", level="DEBUG")
        if np.sign(-r) == np.sign(agg_dir)  and r==v:
        #    self.more_data = True
            result = "Inconclusive"
        else:
            result = "Parking" if np.sign(agg_dir) >= 0 else "Leaving"
            self.more_data = False
        
        self.adbase.log(f"Line {self.au.lnn()}: direction: {result}; readings used: {self.readings}",level="DEBUG")
        self.readings = [False]*self.array_size #tidy up self.readings
        self.adbase.log(f"Line {self.au.lnn()}: readings dict after tidy-up: {self.readings}",level="DEBUG")
        
        return result
            
    def do_later(self,kwargs):
        
        check_colour = kwargs['status']
        
        if kwargs['type'] == "light":
            ent = kwargs['entity']
            ent_state = self.adbase.get_state(ent,attribute="all")
            rgb = str(ent_state["attributes"]["rgb_color"])
            
            try:
                current_colour = self.rgb_to_name[rgb]
            except:
                current_colour = "off"
            
            if check_colour == current_colour: 
                self.adbase.call_service("light/turn_off", entity_id =ent)
        ###-->> self.hass.turn_off(ent)
                if check_colour != "blue":      #for all the parking colours we should disable to range LED for a while, for blue no need
                    self.colours_all_off = True #-->set all the colours to False
                    self.adbase.run_in(self.do_later,self.snooze_time,status=check_colour,type="flag")
                    self.adbase.log(f"Line {self.au.lnn()}: Timeout for {check_colour} has expired and light is still {current_colour} so turning it off.",level="INFO")
                self.colour_in_use[check_colour] = False
            else:
                self.colour_in_use[check_colour] = False
                self.adbase.log(f"Line {self.au.lnn()}: >>> STRANGE! ***Timeout for {check_colour} has expired but light changed to {current_colour} so doing nothing. Flags status {self.colour_in_use}",level="DEBUG")
               
        
        elif kwargs['type'] == "flag":
            self.colours_all_off = False  #-->set all the colours to true
            self.colour_in_use = dict.fromkeys(self.colours_list,False)
            self.adbase.log(f"Line {self.au.lnn()}: Snooze timeout for {check_colour} has expired so light has been re-enabled. Flags status {self.colour_in_use}. ",level="DEBUG")
   
    def sign(self,number):
        if number > 0:
            return 1
        elif number < 0:
            return -1
        else:
            return 0
# ----- End range sensor app 
"""

"""        
        self.trackers_map=self.args.get("device_trackers")
        self.tracker_list=list(self.trackers_map.keys())
        for ent in self.tracker_list:
            continue
            #self.hass.listen_state(self.heartbeat,ent, new="not_home")#,attribute="all")
    
    def heartbeat(self, entity, attribute, old, new, kwargs):
        monitor_phone = self.trackers_map[entity]
        monitor_state = self.adbase.get_state(monitor_phone)
        if monitor_state != "off":
            #reboot monitor app
"""

    #    self.hass.listen_event(self.matches,event="person_detected")
"""
        for d in self.door_list:
            self.hass.listen_state(self.door_trig,self.door_list[d], door=d)
        
    def matches(self, event_name,data,kwargs):
        data["device_id"]
        
    def door_trig(self, entity, attribute, old, new, kwargs):
        d = kwargs['door']
        if self.door_status_chk('front_door'):
            self.adbase.log(f"All good!")
        else:
            self.adbase.log(f"No good!")

    def door_status_chk(self, door, **kwargs):
        self.dot = self.args.get("door_open_timeout")                                           #the door to be auto opened is passed via kwargs 
        contact_sensor = self.door_list[door]                                                   #get the door's contact sensor
        tm_chg = self.adbase.get_state(contact_sensor, attribute="all")['last_changed']         #get the last time contact sensor changed state (aka last time door opened)
        diff_secs = datetime.now().timestamp() - self.adbase.convert_utc(tm_chg).timestamp()    #how many seconds has it been from now, since the door last opened?
        diff_hms_tidy = str(timedelta(seconds=diff_secs)).split('.')[0]                         #make the time difference human readable (aka in hms format)
        dot_hms_tidy = str(timedelta(seconds=self.dot))                                         #make door_open_timeout human readable... not essential
        if diff_secs > self.dot:
            self.adbase.log(f"Opening {door} because according to {contact_sensor}, last opening was at {tm_chg} so {door} hasn't opened for the last {diff_hms_tidy} which is more than the {self.dot} seconds limit.", level="DEBUG")
            return True
        else:
            self.adbase.log(f"No action taken - too recently opened. According to {contact_sensor}, last opening was at {tm_chg} so the time diff is {diff_hms_tidy} which is within the {self.dot} seconds limit.", level="DEBUG")
            return False
"""        
"""

     #   kit = by_name("Kitchen",allow_network_scan=True)
        kit = SoCo('192.168.179.166')
    #    sea = kit.music_library.get_music_library_information('sonos_favorites')
        f = kit.music_library.get_sonos_favorites()
    #    tt = soco.data_structures.DidlFavorite.reference
    #    r = kit.get_uri('<DidlFavorite 'b'World Book Club'' at 0xb4da3178>')
    #    b = kit.music_library.browse(ml_item='sonos_playlists')
        
        #
        s = kit.music_library.get_favorite_radio_stations()
        p = kit.get_sonos_playlists()
        pl = kit.music_library.get_playlists()
        al = kit.music_library.get_albums()
        #
        
        m = MusicService.get_all_music_services_names()
        n = MusicService.get_data_for_name('BBC Sounds')
        bbc = MusicService('BBC Sounds')
        bc = bbc.available_search_categories
        bm = bbc.get_metadata()
        bd = MusicService.get_data_for_name('BBC Sounds')
    #    bu = MusicService.sonos_uri_from_id('325')
        
        v=f.__dict__
        e=v['_metadata']['item_list'][6]
        u=e.reference.get_uri 
        title = e.title 
        self.adbase.log(f"now playing {bm}")
      #  kit.play_uri(uri=u,title=e.title)
        
      #  kit.add_item_to_sonos_playlist(e,"New")
        
        for i in v['_metadata']['item_list']:
        #    rec = i.split()
        #    rec[]  
            e=i.reference
            j=e.__dict__
         #   self.adbase.log(f"ref: {e.item_id}")
        #    self.adbase.log(f"fave: {j['title']} and id is {j['item_id']}") #{(f[1].replace(",","\n"))}\n")
        self.adbase.log(f"count: {len(f)}")
        self.hass.listen_event(self.matches,event="tag_scanned") #Tag_iD="2a0f6d2b-ab0f-4c90-a803-3a63488753b5")

    def matches(self, event_name,data,kwargs):
        c = "no device"
        if data.get("device_id",0):
            c = data["device_id"] 
            tag = data["tag_id"]
        self.adbase.log(f"hello, tag scanned {tag} by: {c}\n") #*** full data: {data}\n")
   #     s= soco.music_library.get_favorite_radio_shows()
    #    t = soco.music_library.get_favorite_radio_stations()
    #    f = soco.music_library.get_sonos_favorites()
    #    self.adbase.log(f"radio_shows {s}\n radio_stations {t}\n faves {f}\n")
  #      match c:
   #         case "open":
  #              self.adbase.log("door opened")
    #        case "retry":
    #            self.adbase.log("recent retry")
    #        case "fail":
    #            self.adbase.log("lock failure")
     #       case _:
   #             self.adbase.log("no issues, continue!")
"""            
"""        
        self.dash = 0
        self.topic="/rpi/reboot/"
        self.lTopic = self.topic + "response/"
        
        self.mqtt.mqtt_subscribe(f"{self.topic}#")
        self.hass.listen_state(self.mqtt_io,"input_select.mqtt_messages")
        self.mqtt.listen_event(self.mqtt_message,"MQTT_MESSAGE",topic=self.lTopic)
       
    def mqtt_io(self, entity, attribute, old, new, kwargs):        
        self.mqtt.mqtt_publish(self.topic,new)
        self.dash = 1

    def mqtt_message(self, event_name, data, kwargs):
        if self.dash and data["payload"]:
            self.hass.set_textvalue("input_text.mqtt_payload", data["payload"])
        elif self.dash and data["payload"] == "unknown command":
            self.hass.set_textvalue("input_text.mqtt_payload", "unkown command")
        dash = "" if self.dash else "not "
        self.adbase.log(f"Line {self.au.lnn()}:Payload is >> {data['payload']} << *** This was {dash}entered via UI\n", level="DEBUG")
        self.dash=0
        return
"""
"""        

        self.hass.listen_state(self.states,"light.t_side", new="on")
        
    def states(self, entity, attribute, old, new, kwargs):
        self.adbase.log(f"hello, {entity} just came on\n")
        moj = self.adbase.get_state("device_tracker.iphone", attribute="all")
        just = self.adbase.get_state("binary_sensor.monitor_justina", attribute="all")
        ton = self.adbase.get_state("device_tracker.tojgan_21", attribute="all")
        self.adbase.log(f"\nMojgan {moj['state']} since {datetime.time(self.adbase.convert_utc(moj['last_changed'])).hour}:{datetime.time(self.adbase.convert_utc(moj['last_changed'])).minute}\nJustina {just['state']} since {datetime.time(self.adbase.convert_utc(just['last_changed'])).hour}:{datetime.time(self.adbase.convert_utc(just['last_changed'])).minute}\nTongai {ton['state']} since {datetime.time(self.adbase.convert_utc(ton['last_changed'])).hour}:{datetime.time(self.adbase.convert_utc(ton['last_changed'])).minute}\n*****")
"""
"""        
        self.adbase.listen_state(self.sched,"light.study_desk_lamp",new="on")
        
    def sched(self,entity, attribute, old, new, kwargs):
        self.adbase.run_in(self.shout_later,2,loudness="mqtt",msg="green later",heading="")
#        self.adbase.run_in(self.shout,2,"mqtt","green",heading="test heading")
        self.shout("mqtt","green",heading="test heading")
"""        
"""
    def shout_later(self,kwargs):
        self.adbase.log(f"using wrapper for scheduler")
        self.shout(kwargs["loudness"],kwargs["msg"],heading = kwargs["heading"])
                

    def shout(self,loudness,msg,**kwargs):
        heading = kwargs["heading"]
        self.adbase.log(f"shout says: loudness is:{loudness}, heading is {heading} and msg is {msg}")       
"""        
"""

        self.adbase.log(f"hello 27 {sys.path} \n username {getpass.getuser()}")
        
# remote control pi gpio
        
        factory = PiGPIOFactory(host='192.168.179.63')

        button = Button(12, pull_up=True,pin_factory=factory)
        meter = LED(14,pin_factory=factory)
        traffic = TrafficLights(21, 20, 16,pin_factory=factory)
        pixel = neopixel.NeoPixel(board.D18, 1)
#        pixel = PixelStrip(1, 18)
       
#        button.when_pressed = meter.toggle
#        button.when_released = meter.off 
      
        def bp():
            pixel[0] = (255, 0, 0)
            sleep (5)
            pixel[0] = (0,255,0)
            sleep (5)
            pixel[0] = (0,0,255)
            sleep (5)
            pixel[0] = (100,50,200)
            sleep (5)
            pixel[0] = (0,0,0)
            return
        
        def flash():
            traffic.red.on()
            sleep (0.5)
            traffic.amber.on()
            sleep (0.5)
            traffic.green.on()
            sleep (0.5)
            traffic.off()
            self.adbase.log(f"Hello Hannah blaa blaa blaa")
            return
        
        button.when_pressed = bp
        
 #       pause()
        
        self.adbase.log(f"Hello Hannah blaa blaa blaa")
   #     self.adbase.log(f"Hello Daddy")
        

 #       if self.adbase.now_is_between("17:30:00", "21:15:00"):
#        button1.when_pressed = button_pressed
        while self.adbase.now_is_between("14:35:00", "22:10:00"):
            button.when_pressed = meter.on 
            self.adbase.log(f"hello 38")
#       while True:
#            if button.is_pressed:
 #               self.adbase.log(f"Button is pressed")
 #           else:
 #               self.adbase.log("Button is not pressed")
  #      button.when_pressed=red.on 

"""
        
        

"""

#        self.internal_sensors = {"upstairs":{"bathroom":"sensor.bathroom_temperature","main":{"dyson":"sensor.bedroom_temperature","nest":"sensor.bedroom_temperature_2","tado":"sensor.main_temperature"},"friends":{"tado":"sensor.friends_temperature","dyson":"sensor.upstairs_temperature"},"landing":"sensor.landing_temperature","study":"sensor.study_temperature"},"downstairs":{"hallway":"sensor.coats_temperature","dining":"sensor.downstairs_temperature","utility":"sensor.utility_motion_temperature","kitchen":"sensor.worktop_sensor_temperature"}}
#        self.tado = {"upstairs":{"bathroom":"climate.bathroom","landing":"climate.landing","main":"climate.main","study":"climate.study","friends":"climate.friends"}}
#        self.nest = {"upstairs":"climate.bedroom","downstairs":"climate.downstairs"}
        
 #       self.adbase.log(f"upstairs main bedroom internal sensors: {self.internal_sensors['upstairs']['main']}")
 #       blaa = self.adbase.get_state("climate.downstairs",attribute="all")
 #       self.adbase.log(f"state: {blaa}")
 #       self.adbase.listen_state(self.change_nest,"climate",attribute="all")
"""
"""
    def change_nest(self, entity, attribute, old, new, kwargs):
        trv_temps = {}
        if new["state"]=="auto":
            self.adbase.log(f"Line {self.au.lnn()}::No action, {entity} temp didn't change ")
            return
        
        if entity in ("climate.downstairs","climate.bedroom"):
            new="its nest" 
            self.adbase.log(f"state: {new}")
           
        else:
            for room in self.tado["upstairs"]:
                trv = self.tado["upstairs"][room]
                thermo = self.adbase.get_state(trv,attribute="all")
                temp = thermo['attributes']['temperature']
                trv_temps[trv] = temp
            hottest_trv = list(sorted(trv_temps.items(), key=lambda x: x[1], reverse=True))[0]
            self.adbase.log(f"Highest thermo: {hottest_trv[0]} needs temp: {hottest_trv[1]}")  
            top_temp = hottest_trv[1] + 2
#            self.adbase.call_service("climate/set_temperature",entity_id=self.nest['upstairs'], temperature=top_temp)
            self.adbase.log(f"\nOld state {old}\nNew state {new}")  

   #     gurl="https://www.googleapis.com/oauth2/v4/token?client_id=9069484476-n30evkeontdruabgcsj8auemcvbv6sb8.apps.googleusercontent.com&client_secret=vDoBsU69ynzSf-YzYAAs501f&code=4/0AfDhmrixjzMDMG6_LKK8CHep3LECKsCyKVxYRacXTHkltgQW_Ru144qLppZXMQRM8MJhKg&grant_type=authorization_code&redirect_uri=https://www.google.com"
  #      g=requests.get(url=gurl)
        

  #      ts = self.adbase.get_state("binary_sensor.monitor_justina",attribute="all")
  #      self.adbase.log(f"entity: {ts}")
  #      self.adbase.log("entity: {} changed state to: {} at {}".format(ts["entity_id"],ts["state"],ts["last_changed"]))
    def get_octo_data(self):      
        gas_url = "https://api.octopus.energy/v1/gas-meter-points/608682103/meters/E6S15330572061/consumption/"
        elec_url = "https://api.octopus.energy/v1/electricity-meter-points/1900029019461/meters/20L3348755/consumption/"
        products = "https://api.octopus.energy/v1/products/"
        agile = "https://api.octopus.energy/v1/products/AGILE-18-02-21/electricity-tariffs/E-1R-AGILE-18-02-21-J/standard-unit-rates/"
        un = "<redacted>"
    #    PARAMS = {"group_by":"week"}
#       # prod_params = {"is_green":"true"}
        g = requests.get(url = gas_url, auth = (un,""))
        g_data = g.json()
        e = requests.get(url = elec_url, auth = (un,""))
        e_data = e.json()
#        p = requests.get(url = products, auth = (un,"",params = prod_params))
#        p_data = p.json()
#        a_data = a.json()
        a = requests.get(url = agile, auth = (un,""))
 #       ed = e_data['results']['consumption']
        
    #   self.adbase.log(f"\n\n Elec: Status: {e}\n{e_data}")#"\nProducts: Status: {p}\n{p_data}") #"\n\n******\n\n\n\nAgile: Status: {a}\n{a_data}")
# from 2020-11-13 11:11:49.002085 to 2017-05-05T05:37:27Z
# 
#       Determine the runtime based on config
   #     start_time = self.args.get("start_time")
  #     now = self.adbase.datetime()
  #      td = datetime.date(now)
#        rt = datetime.combine(td,nw)
#        self.adbase.log(f"Line {self.au.lnn()}:: Runtime: {rt}, now {nw}")
 #      nw = time(hour=(now.hour+1))
#        if start_time is not None:
#            start_time = self.adbase.parse_datetime("0"+ str(start_time) + ":00:00")
#            if start_time < now:
#                start_time = start_time + timedelta(days=1,minutes=1) 
#        else:
#            start_time = now
#        runtime = start_time
            
 #       runtime = self.parse_datetime(start_time) if start_time else self.adbase.datetime()
#        self.adbase.log(f"Line {self.au.lnn()}:: Runtime: {runtime}")



#        now = self.adbase.datetime()
#        u ="T"
#        now=u.join((f"{now}")[:19].split())+"Z"
   #     now_utc = now[0]+"T"+now[1]+"Z"
  #      nowd = self.adbase.parse_datetime(now_utc)
#        self.adbase.log(f"now: {now}")
#        other = self.adbase.parse_datetime("2020-10-30 10:22:48")
#        up = self.adbase.parse_datetime("sunrise")
#        trig = self.adbase.parse_datetime("2020-10-15 16:08:07")
#        door = self.adbase.parse_datetime("2020-10-15 10:35:21")
##        down = self.adbase.parse_datetime("sunset")
#        a=door
#        b=other
#        if a < b: 
            
#            self.adbase.log(f"trig type: {type(b)} happens, then door: {type(a)}") 
#        else:
#            self.adbase.log(f" we don't care") # - door: {a} happens, then trig:{b}")

#   self.adbase.log(f"now {now}; sunrise {up}; sunset {down} day length {int(((down-up).total_seconds())/3600)} hours")


#        mac = "00:26:B4:C9:11:BC"
#        dev = "light.study_desk_lamp"
#        dev = "binary_sensor.doorstep_acceleration"
#        dev = "binary_sensor.doorstep_contact"
#        self.hass.listen_state(self.test,dev,attribute="all")
#    def test(self, entity, attribute, old, new, kwargs):
#        self.adbase.log("State Attributes for {} \n Specifc: {} {}".format(entity,new["state"],new["attributes"]["friendly_name"]))
 #       self.adbase.log("State Attributes for {} \n All: {}".format(entity,new))
#        self.adbase.log("State Attributes for {} \n All: {}".format(entity,attribute))
        

    def remove_known_device(self, device):
        #Request all known devices in config to be deleted from monitors.

        self.adbase.log(f"2 Line 29 in the function and working on mac {device}")
      
        topic="monitor/setup/DELETE STATIC DEVICE"
        payload=device
        self.mqtt.mqtt_publish(topic,payload)
        
        self.adbase.log(f"3 Line 35: just sent this to monitor {topic} {device}")
         
        # now remove the device from AD
        self.adbase.log(f"4 Line 38: now remove the device from AD")
        entities = list(
            self.mqtt.get_state("monitor", copy=False, default={}).keys()
        )
        self.adbase.log("5 Line 42: live entities for monitor: {}".format(entities))
        device_name = None
        for entity in entities:
            if device == self.mqtt.get_state(entity, attribute="id", copy=False):
                location = self.mqtt.get_state(entity, attribute="location")
                self.adbase.log(f"6 Line 47: Entity location is {location}")
                if location is None:
                    continue

                node = location.replace(" ", "_").lower()
                self.mqtt.remove_entity(entity)
                self.adbase.log(f"7 Line 53: mqtt remove entity {entity} and device name is {device_name}")
                if device_name is None:
                    _, domain_device = self.mqtt.split_entity(entity)
                    device_name = domain_device.replace(f"_{node}", "")
                self.adbase.log(f"8 Line 57: device name is now {device_name} and domain device is {domain_device}")
        
        # now remove the conf sensor from HA
        self.adbase.log(f"9 Line 60: now remove the conf sensor from HA")            
        entities = list(self.hass.get_state("sensor", copy=False, default={}).keys())
        
        for entity in entities:
            if device == self.hass.get_state(entity, attribute="id", copy=False):
                # first cancel the handler if it exists
  #              handler = self.confidence_handlers.get(entity)
 #               if handler is not None:
 #                   self.hass.cancel_listen_state(handler)
                self.hass.call_service("state/remove_entity", entity_id=entity, namespace="default")                
            #    self.hass.remove_entity(entity)
                self.adbase.log(f"10 Line 70: sent remove entity for: {entity}")
         
        # now remove the binary sensor from HA
#        device_name = "gich"
        self.adbase.log(f"11 Line 73: now remove the binary sensor from HA")
        self.adbase.log(f"12 Line 74: device name is now {device_name}")
        if device_name is not None:
            device_entity_id = f"monitor_{device_name}"
            device_state_sensor = f"binary_sensor.{device_entity_id}"
            self.adbase.log(f"13 Line 78: device entity id is {device_entity_id} and device sensor is {device_state_sensor}")
            # now remove for HA
            self.call_service("state/remove_entity", entity_id=device_state_sensor, namespace="default")
       #     self.hass.remove_entity(device_state_sensor)
            self.adbase.log(f"14 Line 81: hass.remove_entity: {device_state_sensor}")
            # now remove for AD
            self.mqtt.remove_entity(device_state_sensor)
            self.adbase.log(f"15 Line 84: ad remove_entity: {device_state_sensor}")
"""
      
