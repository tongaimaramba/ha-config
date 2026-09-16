# App to automatically troubleshoot and resolve issues for Auto Unlock
#
import adbase as ad
from datetime import datetime, timedelta, timezone, time
import sys 
from string import ascii_lowercase as alc
import requests

class AUTApp(ad.ADBase):
#
#####
#
 fix indent here    def initialize(self):
        """Initialize AppDaemon App."""
        self.adbase = self.get_ad_api()
        self.hass = self.get_plugin_api("HASS")
        self.mqtt = self.get_plugin_api("MQTT")
        self.access = self.adbase.get_app("guest_access")
        self.au = self.adbase.get_app("auto_unlock")
        self.door_list = self.args.get("door_contact")
        
        self.adbase.log("\n\n************\n*\n* Welcome to Auto Unlock Troubleshoot App   ************\n*\n************\n") #Launch message

#***** for testing api calls
        self.test_flag = False
#***** end test flags
        
        # load configuration  

        self.monitor_devices = self.args.get('monitor_devices')
        self.presence_sensors = self.args.get('presence_sensors') # self.presence_sensor['<name>']['<locator|tracker|person|monitor']
        self.rpi_connections = self.args.get('rpi_connections')  #sensors with the status of the connection to each rpi
        self.esp_cmd = self.args.get('esp_commands')  # switches that trigger commands via rpi gpio ## esp_commands{'frontdoor':['rpi_cycle': switch.rpi_rebooter_reboot_switch,'wlan_cycle': switch.rpi_rebooter_wlan0_restart]
        self.win = self.args.get('window')*60     #converting window from minutes to seconds
        self.api_call = self.args.get('api_call')   #self.api_call[username|password|mqtt_url|nw_url]
        
        # Initialise variables
        self.waiting_for_run = False
        self.skip_this = False
        self.system_state = ['null','null']
        
        # Listen for mode qualifiers:
        self.adbase.log(f"Line {self.au.lnn()}: ****\nRunning Listeners ",level="DEBUG")
        self.adbase.listen_state(self.check,self.monitor_devices)  #,new="off")
         
    def check(self,entity, attribute, old, new, kwargs):
        #if self.skip_this: return
        self.adbase.log(f"Line {self.au.lnn()}: sensor check triggered by {entity}")
        
        if entity in self.monitor_devices:
            if not self.waiting_for_run:
                self.verify_sensors('first_try')
                if self.system_state[0] == "not ok":
                    self.adbase.log(f"Line {self.au.lnn()}: ** sensors disagree, checking again in {self.win/60} minutes", level="INFO")
                    self.waiting_for_run = True
                    self.adbase.run_in(self.verify_sensors,self.win,i='retry')
                else:
                    self.adbase.log(f"Line {self.au.lnn()}: ** sensors agree, no action needed.",level="DEBUG")
                    
        if entity == "manual_from_retry":
            if self.system_state[0] == "not ok":
                self.adbase.log(f"Line {self.au.lnn()}: ** sensors still disagree, checking pi and fixing issues.", level="INFO")
                self.handle_issues()
            else:
                    self.adbase.log(f"Line {self.au.lnn()}: ** sensors agree, no action needed.",level="DEBUG")
        
        # also add a nuki heartbeat
        
    def verify_sensors(self,cb_args):
        consensus = 0
        result = {}
        state = {}
        self.system_state.clear()
        try: 
            instance = cb_args['i']
        except:
            instance = cb_args 
        
        #self.adbase.log(f"Line {self.au.lnn()}: instance: {instance}")
        
        for n in self.presence_sensors:
            #self.adbase.log(f"n is {n}", level="DEBUG")
            state[n]={}
            state[n]['mon'] = self.adbase.get_state(self.presence_sensors[n]['monitor'])   #on/off ignore unavailable
            state[n]['loc'] = self.adbase.get_state(self.presence_sensors[n]['locator'])   #home/not-home ignore unavailable
            state[n]['trk'] = self.adbase.get_state(self.presence_sensors[n]['tracker'])   #home/not-home ignore unavailable
            state[n]['per'] = self.adbase.get_state(self.presence_sensors[n]['person'])    #home/not-home ignore unavailable    
            
            
            for s in state[n]:
                if state[n][s] in ('home','on'):     # home = -1
                    state[n][s] = -1
                elif state[n][s] == 'unavailable':
                    state[n][s] = 0
                else: 
                    state[n][s] = 1
                
            consensus = state[n]['loc']+state[n]['trk']+state[n]['per']    #majority consenus is home if total is lt 0; and away if gt 0
            
            if consensus < 0:
                consensus = -1   #home
            elif consensus == 0:
                consensus = 0     #unavailable
            elif consensus > 0:
                consensus = 1     #away
            
            if consensus != 0 and state[n]['mon'] != 0:
                result[n] = 1 if consensus == state[n]['mon'] else -1   #1=ok; -1=not ok
            else:
                result[n] = 0     # 0=unavilable
                
        if sum(result.values()) == len(result):
            self.system_state = ['ok','sensors all agree.'] 
        else:
            details = {}
            for n in self.presence_sensors:
                for s in state[n]:
                    if state[n][s] == -1:     
                        state[n][s] = "home"
                    elif state[n][s] == 0:
                        state[n][s] = "unavailable"
                    elif state[n][s] == 1:
                            state[n][s] = "away"
                    
                if result[n] != 1:
                    mon_s = self.presence_sensors[n]['monitor']
                    loc_s = self.presence_sensors[n]['locator']
                    trk_s = self.presence_sensors[n]['tracker']
                    per_s = self.presence_sensors[n]['person']
                    details[n] = "sensors disagree. *** " +mon_s+": "+str(state[n]['mon'])+" ## "+per_s+": "+str(state[n]['per'])+" ## "+trk_s+": "+str(state[n]['trk'])+" ## "+loc_s+": "+str(state[n]['loc']) 
                    
            self.system_state = ['not ok',details]
            
        self.adbase.log(f"Line {self.au.lnn()}: on the {instance}, sensor check result: {self.system_state[0]}", level="INFO")
        
        if instance == "retry":  
            self.waiting_for_run = False
            self.check("manual_from_retry","all","null","null","null")

    def handle_issues(self):
        self.adbase.log(f"Line {self.au.lnn()}: Handle_Issues now running") #, level="DEBUG")
        mqtterr_result = self.pi_api('mqtterr')                     #<< check mqtt messages to see if its a network issue
        if mqtterr_result: 
            nw_restart = self.pi_api('nw')
            self.adbase.log(f"Line {self.au.lnn()}: WLAN0 restart success is: {nw_restart}", level="INFO")
        else:
            au_processes_issue = self.pi_api('mon-proc')               #<< check that all processes are running on the pi
            if au_processes_issue:
                rpi_reboot = self.pi_api('rbtn')
                self.adbase.log(f"Line {self.au.lnn()}: RPI reboot success is: {rpi_reboot}", level="INFO")
            else:
                #check if monitor and auto-unlock are running on HASS
                HASS_proccess_issue = self.pi_api('hass_check')
                if HASS_proccess_issue:
                    hass_restart = self.pi_api('hass_start')
                    self.adbase.log(f"Line {self.au.lnn()}: Appdaemon process restart result is: {hass_restart}", level="INFO")
                    #restart appdaemon processes or send notif to admin
                else:
                    #no idea why the issue, reboot the rpi
                    rpi_reboot = self.pi_api('rbtn')
                    self.adbase.log(f"Line {self.au.lnn()}: Not sure what went wrong, rebooting RPI. Reboot success is: {rpi_reboot}", level="INFO")
                    
    def pi_api(self, api):
        self.adbase.log(f"Line {self.au.lnn()}: {api} API call") #, level="DEBUG")
        
        #-- Diagnosis API Actions --##
        if api == "mqtterr":
            self.adbase.log(f"Line {self.au.lnn()}: Checking for MQTT errors on RPI")
            #call mqtterr api
                #mqtt_status = requests.get(url = self.api_call[mqtt_url], auth = ("<redacted>","<redacted>")) #self.api_call[username|password|mqtt_url|nw_url]
                #timestamp = mqtt_status[7] # has to be YY-MM-DD-HH:MM:SS
                #event_in_window = self.check_timeout(timeout = 2*self.win, event_time=timestamp)
 ##<<<<< fix then when going into production
            event_in_window = False #self.check_timeout(timeout = 60000, event_time="11:00:00")  # the "50" is parsed from mqtterr output and converted to the right format> # get this *************<
            return event_in_window
        
        if api == "mon-proc":
            self.adbase.log(f"Line {self.au.lnn()}: Checking for missing processes on RPI")
            #confirm that mon-proc returns monitor and led2
            #return True if error else False
            
        if api == "hass_check":
            self.adbase.log(f"Line {self.au.lnn()}: Checking for missng processes on Hass")
            #return True if error else False
            
        #-- Resolution API Actions --##
        if api == "nw":
            self.adbase.log(f"Line {self.au.lnn()}: Restarting WLAN0")
            self.hass.turn_on(self.esp_cmd['frontdoor']['wlan_cycle']) #call nw 
            return True # find a way to return result of restart
            
        if api == "hci":
            self.adbase.log(f"Line {self.au.lnn()}: Running {api}")
            #return True if success else False
        
        if api == "rbtn":
            self.adbase.log(f"Line {self.au.lnn()}: Running {api}")
            self.hass.turn_on(self.esp_cmd['frontdoor']['rpi_cycle']) #call rbtn
            #return True if success else False
        
        if api == "hass_start":
            self.adbase.log(f"Line {self.au.lnn()}: Running {api}")
            #return True if success else False
    
    def nuki_heartbeat(self):
        self.adbase.log(f"Line {self.au.lnn()}: checking for Nuki heartbeat")
        #event_in_window = self.check_timeout(timeout = self.win, event_time=50) #use this function to see if the heartbeat happened recently
        
    def check_timeout(self, timeout, event_time):
        
        self.adbase.log(f"Line {self.au.lnn()}: flow check - about to calc diff", level="DEBUG")
        
        status = ""
        now = self.adbase.get_now()
        e_t = self.adbase.parse_datetime(event_time,aware=True)
        cut_off_time = now - timedelta(seconds=timeout)                     #how many seconds has it been from now, since the door last opened?
        
        self.adbase.log(f"Line {self.au.lnn()}: cut_off: {cut_off_time} event time: {e_t}",level="DEBUG")
        
        if e_t > cut_off_time:    #if true, last event was more recent than cut_off_time
             status=True
        else:
             status=False
             
        result = [e_t,cut_off_time, timeout, status]
        return status        
        
        
        
        
        
        
        
        
        
        
        