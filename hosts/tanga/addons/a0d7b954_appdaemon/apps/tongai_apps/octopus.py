# make the usage code into function to aggregate over different time periods and use forecast where needed
# write to the correct sensor
# need a function to calculate where we are in the period and calculate time remaining
# need function to forecast rest of period based on time to date    

import adbase as ad
import re
import copy
from datetime import datetime, timedelta, time
import traceback
import requests
#from requests.auth import HTTPBasicAuth

class OctopusApp(ad.ADBase): 
#
#####
#
    def initialize(self):
        """Initialize AppDaemon App."""
        self.adbase = self.get_ad_api()
        self.hass = self.get_plugin_api("HASS")
        self.mqtt = self.get_plugin_api("MQTT")
        self.au = self.adbase.get_app("auto_unlock") 
        
        self.adbase.log("\n\n************\n*\n* Welcome to Octopus App\n*\n************\n") #Launch message
        
        #Octopus URLs
        self.gas_url = "https://api.octopus.energy/v1/gas-meter-points/608682103/meters/E6S15330572061/consumption/"
        self.elec_url = "https://api.octopus.energy/v1/electricity-meter-points/1900029019461/meters/20L3348755/consumption/"
        self.agile = "https://api.octopus.energy/v1/products/AGILE-18-02-21/electricity-tariffs/E-1R-AGILE-18-02-21-J/standard-unit-rates/"
        self.un = "<redacted>"
        self.g_px = self.args.get("gas_tariff") #get the gas tariff from config

#       define sensors
        elec_use= {"hour":"sensor.elec_usage_hourly","day":"sensor.elec_usage_daily","week":"sensor.elec_usage_weekly","month":"sensor.elec_usage_monthly"}
        gas_use = {"hour":"sensor.gas_usage_hourly","day":"sensor.gas_usage_daily","week":"sensor.gas_usage_weekly","month":"sensor.gas_usage_monthly"}
        energy_use = {"hour":"sensor.energy_usage_hourly","day":"sensor.energy_usage_daily","week":"sensor.energy_usage_weekly","month":"sensor.energy_usage_monthly"}
        elec_cost= {"hour":"sensor.elec_cost_hourly","day":"sensor.elec_cost_daily","week":"sensor.elec_cost_weekly","month":"sensor.elec_cost_monthly"}
        gas_cost = {"hour":"sensor.gas_cost_hourly","day":"sensor.gas_cost_daily","week":"sensor.gas_cost_weekly","month":"sensor.gas_cost_monthly"}
        energy_cost = {"hour":"sensor.energy_cost_hourly","day":"sensor.energy_cost_daily","week":"sensor.energy_cost_weekly","month":"sensor.energy_cost_monthly"}
        self.energy_sensors = {"elec_use":elec_use,"gas_use":gas_use,"energy_use":energy_use,"elec_cost":elec_cost,"gas_cost":gas_cost,"energy_cost":energy_cost}


#        bill_mtd = {elec_mtd,gas_mtd}
#        bill_fcast = {elec_fcast,gas_fcast}
 
        # run from the start of the next hour
        now = self.adbase.datetime()
        nw = time(hour=(now.hour+1))
        td = datetime.date(now)
        runtime = datetime.combine(td,nw)    
        self.adbase.log(f"Line {self.au.lnn()}:: Runtime: {runtime}",level="DEBUG")
        
        #Configure other behaviour
        freq_hrs = self.args.get("update_frequency")
        grouping = self.args.get("data_aggregation")     #Aggregate options:  ‘hour’ * ‘day’ * ‘week’ * ‘month’ * ‘quarter’
        nrg = self.args.get("energy_types","all")    # show data for Gas or Electric only, or both together. Options: elec, gas, all. Default is all

        self.octo_conf = {"energy":nrg,"sen":"sensor.test_elec_usage","aggr":grouping,"intvl":freq_hrs*3600}
        self.adbase.log(f"Line {self.au.lnn()}:: Configured parameters: Runtime: {runtime} Others: {self.octo_conf}")
        
        try:
            self.adbase.log(f"Line {self.au.lnn()}::flow check", level="DEBUG")
            self.ping_octo(self.octo_conf["intvl"])    # an initial run to get data now
            self.adbase.run_every(self.ping_octo,runtime,self.octo_conf["intvl"])   #scheduled runs every "intvl" starting at "runtime"
            
        except Exception as e:
            self.adbase.log(f"Line {self.au.lnn()}::{e}")
            
        
    def ping_octo(self,kwargs):
        self.adbase.log(f"Line {self.au.lnn()}::flow check\n energy test is {self.octo_conf['energy']}", level="DEBUG")
        
        now = self.adbase.datetime()
        nrg = "energy" if self.octo_conf["energy"] == "all" else self.octo_conf["energy"] 
        group = self.octo_conf["aggr"] if self.octo_conf["aggr"] else "" #default is hourly consumption intervals
        ts = self.get_usage_window(now,group)
        PARAMS = {"order_by":"-period","page_size":10000,"group_by":group,"period_from":ts[0],"period_to":ts[1]}
        self.adbase.log(f"Line {self.au.lnn()}::flow check. Params: {PARAMS}", level="DEBUG")
        
        g_cost = 0
        g_usage = 0
        e_cost = 0
        e_usage = 0
        e_px = 0
        en_sensor = {}
        ts_open = now
        ts_close = now
# Gas
        if nrg in ("energy","gas"):
            self.adbase.log(f"Line {self.au.lnn()}::flow check", level="DEBUG")
            #get latest gas usage
            try:
                g = requests.get(url = self.gas_url, auth = (self.un,""),params = PARAMS)
                g_data = g.json()
                self.adbase.log(f"Line {self.au.lnn()}:: Gas status {g} Gas result {g_data}", level = "DEBUG")
                if len(g_data["results"]):
                    latest_g = g_data["results"][0]
                    g_usage = round(latest_g["consumption"] * 1.02264 * 38.8 / 3.6,2) 
                else:
                    g_usage = 0
              #      self.adbase.log(f"Line {self.au.lnn()}::API Error: No data found",level="WARNING")
            except Exception as e:    
                self.adbase.log(f"Line {self.au.lnn()}::API Error: {e}")
                return
         
            #calculate gas bill
            g_cost = round(g_usage*self.g_px,2)
        
# Electricity
        if nrg in ("energy","elec"):
            self.adbase.log(f"Line {self.au.lnn()}::flow check", level="DEBUG")
            #get latest electricty usage
            try:
                e = requests.get(url = self.elec_url, auth = (self.un,""),params = PARAMS)
                e_data = e.json()
                self.adbase.log(f"Line {self.au.lnn()}:: Elec status {e} Elec result {e_data}", level = "DEBUG")  
                if len(e_data["results"]):
                    e_usage = e_data["results"][0]["consumption"]
                    ts_open = e_data["results"][0]["interval_start"]
                    ts_close = e_data["results"][0]["interval_end"]
                else:
                    e_usage = 0
                    self.adbase.log(f"Line {self.au.lnn()}::API Error: No data found",level="WARNING")
            except Exception as e:
                self.adbase.log(f"Line {self.au.lnn()}::API Error: {e}")
                return
            
            #get the right price window for Agile
            if len(e_data["results"]):
                px_params = {"group_by":group,"page_size":1500,"period_from":ts[0], "period_to":ts[1]}
            else:
                px_params = ""
            
            #get Agile price
            try:
                a = requests.get(url = self.agile, auth = (self.un,""), params = px_params)
                a_data = a.json()
                self.adbase.log(f"Line {self.au.lnn()}:: Price status {a} Price result {a_data}",level="DEBUG")
                if len(a_data["results"]):
                    e_px = self.avg_px(a_data["results"])      

                else:
                    e_px = 0
                    self.adbase.log(f"Line {self.au.lnn()}::API Error: No price data found",level="WARNING")
            except Exception as e:
                self.adbase.log(f"Line {self.au.lnn()}::API Error: {e}")
                return
                
            #calculate bill
            e_cost = round(e_usage*e_px,0)
        
        usage = g_usage + e_usage
        cost = g_cost + e_cost
        
        bill = {"energy_use": usage,"energy_cost":cost,"gas_use":g_usage,"gas_px":self.g_px,"gas_cost":g_cost,"elec_use":e_usage,"elec_px":e_px,"elec_cost":e_cost,"period_from":ts_open,"period_to":ts_close}
        
        # update the required sensors per config
        
        for bill_var in self.energy_sensors:
            consumption = bill[bill_var]
            sensor = self.energy_sensors[bill_var][group]
            
            self.adbase.log(f"Line {self.au.lnn()}:: Bill variable {bill_var} for sensor {sensor} with state {consumption}", level = "DEBUG")
            
            if nrg == "energy":
                en_sensor[sensor] = consumption
                self.adbase.log(f"Line {self.au.lnn()}:: Sensor: {sensor} with state {en_sensor[sensor]}", level = "DEBUG")
            if nrg == "gas" and bill_var in ("gas_use","gas_cost"):
                en_sensor[sensor] = consumption
                self.adbase.log(f"Line {self.au.lnn()}:: Sensor: {sensor} with state {en_sensor[sensor]}", level = "DEBUG")
            if nrg == "elec" and bill_var in ("elec_use","elec_cost"):
                en_sensor[sensor] = consumption
                self.adbase.log(f"Line {self.au.lnn()}:: Sensor: {sensor} with state {en_sensor[sensor]}", level = "DEBUG")
            
        for sensor in en_sensor:
            self.adbase.log(f"Line {self.au.lnn()}::Sensor data: sensor {sensor}; timestamp:{ts[1]}, state {en_sensor[sensor]}", level = "DEBUG")
            self.update_sensors(sensor,ts[1],state=en_sensor[sensor])    
            
 #       en_use = nrg + "_use"
 #       en_cost = nrg + "_cost"
#        en_sensor = [self.energy_sensors[en_use][group],self.energy_sensors[en_cost][group]]
        
#        self.update_sensors(en_sensor[0],ts[1],state=e_usage)
#        self.update_sensors(en_sensor[1],ts[1],state=e_cost)
        self.adbase.log(f"Line {self.au.lnn()}::Total cost: {bill['energy_cost']} pence as at {bill['period_to']} with elec usage: {bill['elec_use']} kWh and gas usage: {bill['gas_use']} kWh")
#        self.au.shout("normal",f"Total cost: {bill['total_cost']} pence as at {bill['period_to']} with elec usage: {bill['elec_use']} kWh and gas usage: {bill['gas_use']} kWh",heading="*** Octo Alert Yesterday's Bill ***")
        return bill
    
    def update_sensors(self,sensor,ts,**kwargs):
        # update sensor
        Attr = {"time":ts,"unit_of_measurement":" "} 
        self.adbase.set_state(sensor,state=kwargs["state"],attributes=Attr)

    def get_usage_window(self,now,group):
        #As of this time yesterday, get the beginning of the consumption period
        self.adbase.log(f"Line {self.au.lnn()}::flow check. \n group: {group} and timestamp: {now}", level="DEBUG")

        if group == "quarter":
            period_from = now - timedelta(days=91)
            period_to = now - timedelta(days=1)
        elif group == "month":
            period_from = now - timedelta(days=31)
            period_to = now - timedelta(days=1)
        elif group == "week":
            period_from = now - timedelta(days=8)
            period_to = now - timedelta(days=1)
        elif group == "day":
            period_from = now - timedelta(days=2)
            period_to = now - timedelta(days=1)
        else:
            period_from = now - timedelta(hours=25,minutes=1)
            period_to = now - timedelta(hours=24,minutes=1)
            
        window=[self.make_utc(period_from),self.make_utc(period_to)]    
        self.adbase.log(f"Line {self.au.lnn()}::flow check Returning: list of length {len(window)} containing: {window[0]}", level="DEBUG")

        return window
        
    def make_utc(self,ts):
        u ="T"
        ts=u.join((f"{ts}")[:19].split())+"Z"
        return ts
 
    def avg_px(self, data):
        self.adbase.log(f"Line {self.au.lnn()}::flow check", level="DEBUG")
        px = []
        for i in range(len(data)):
            px.append(data[i]["value_inc_vat"])
        avg = sum(px)/len(px)
        self.adbase.log(f"Line {self.au.lnn()}::Average price: {avg} from {len(px)} data points", level="DEBUG")
        return round(avg,2)
       









