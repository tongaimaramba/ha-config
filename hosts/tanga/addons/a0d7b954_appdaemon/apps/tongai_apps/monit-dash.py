# use monit API to display status in Hass    

import adbase as ad
import re
import copy
from datetime import datetime, timedelta, time
import traceback
import requests
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET

class MMonitApp(ad.ADBase): 
#
#####
#
    def initialize(self):
        """Initialize AppDaemon App."""
        self.adbase = self.get_ad_api()
        self.hass = self.get_plugin_api("HASS")
        self.mqtt = self.get_plugin_api("MQTT")
        self.au = self.adbase.get_app("auto_unlock") 
        
        self.adbase.log("\n\n************\n*\n* Welcome to Monit Dash App\n*\n************\n") #Launch message
        
        #Authentication
        self.un = "<redacted>"
        self.pw = "<redacted>"
        self.basic_url = 'http://192.168.179.33:2812/_status?format=xml'
        mins = 1440
        intvl = mins *60

#        s.auth = ('<redacted>','<redacted>')
#        s = requests.Session()
#        status = s.get(self.basic_url)  
#        root = ET.fromstring(status.text)
#        for child in root:
#            for element in child:
#                if element.tag in ("name","status","uptime","cpu"):
#                    val = str(int(int(element.text)/3600)) + " hrs" if element.tag == "uptime" else element.text
#                    if element.tag == "status" and int(element.text)==0:
#                        val = "OK"
#                        val = "NOK"
#                    if element.tag == "status" and int(element.text)!=0: 
#                    rec[element.tag] = val
#            self.adbase.log(f" >> {rec['name']} :: {rec['status']} :: {rec['uptime']}")

        try:
            self.adbase.log(f"Line {self.au.lnn()}::flow check", level="DEBUG")
            self.adbase.run_every(self.ping_monit,"now",intvl)   #scheduled runs every "intvl"
            
        except Exception as e:
            self.adbase.log(f"Line {self.au.lnn()}::{e}")
            
        
    def ping_monit(self,kwargs):
        self.adbase.log(f"Line {self.au.lnn()}:: Ping_Monit called", level="DEBUG")
        rec = {"name":"","status":"","uptime":""}
        check = {}
        s = requests.Session()
        s.auth = (self.un,self.pw)
        status = s.get(self.basic_url)  
        root = ET.fromstring(status.text)
        for child in root:
            for element in child:
                if element.tag in ("name","status","uptime","cpu"):
                    val = str(int(int(element.text)/3600)) + " hrs" if element.tag == "uptime" else element.text
                    if element.tag == "status" and int(element.text)==0:
                        val = "OK"
                    if element.tag == "status" and int(element.text)!=0: 
                        val = "NOK"
                    rec[element.tag] = val
    #        self.adbase.log(f" >> {rec['name']} :: {rec['status']} :: {rec['uptime']}",level="DEBUG")
            check[rec['name']] = {"status":rec['status'],"uptime":rec['uptime']}
        
        #update status sensor
        for nm in check:
        sta = "monit_" + check[nm]['name'] *
            self.update_sensors(sta,state=check[nm]['status'],attributes = {"uptime": check[nm]['uptime']})
            self.adbase.log(f"Line {self.au.lnn()}:: Service: {nm} Status: {check[nm]['status']} Uptime: {check[nm]['uptime']}", level="INFO")
            

    def update_sensors(self,sensor,**kwargs):
        # update sensor
        self.adbase.set_state(sensor,state=kwargs["state"],attributes=kwargs["attributes"])










