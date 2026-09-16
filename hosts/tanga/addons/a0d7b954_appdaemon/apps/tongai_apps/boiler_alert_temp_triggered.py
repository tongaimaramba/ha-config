# App to alert when boiler doesn't work
#
import adbase as ad
from datetime import datetime, timedelta, timezone, time
import sys 
from string import ascii_lowercase as alc
import requests

class BOILERApp(ad.ADBase):
#
#####
#
    def initialize(self):
        """Initialize AppDaemon App."""
        self.adbase = self.get_ad_api()
        self.hass = self.get_plugin_api("HASS")
        self.mqtt = self.get_plugin_api("MQTT")
        self.au = self.adbase.get_app("auto_unlock")
       
        self.adbase.log("\n\n************\n*\n* Welcome to Bolier Alert App   ************\n*\n************\n") #Launch message

       # load configuration  

        self.heater_times_raw = self.args.get('heater_times')
        self.time_window = self.args.get('time_window')
        self.min_temp_rise = self.args.get('min_temp_rise') 
        self.alert_ent = self.args.get('alert_ent') #input_boolean.boiler_anomaly_alert
        self.temp_sensor = self.args.get('temp_sensor')
        self.heater_schedule = []
        self.heating_start_temp = None
        self.heating_start_time = None
        
        self.adbase.log(f"Line {self.au.lnn()}: heater times: {self.heater_times_raw}.",level="DEBUG")
        for s in self.heater_times_raw:
            r = [int(i) for i in self.heater_times_raw[s].split(',')]
            self.adbase.log(f"Line {self.au.lnn()}: heater times: {r}.",level="DEBUG")
            try:
                rec = [time(r[0],r[1]),time(r[2],r[3])]
            except:
                rec = [time(7,0),time(16,0)]
            self.heater_schedule.append(rec)
        
        # Schedule optimization every day at midnight
        self.adbase.run_daily(self.optimize_parameters, time(0, 0))
        
        # Get the initial temperature
        self.adbase.listen_state(self.check_temperature, self.temp_sensor)


    def optimize_parameters(self, kwargs):
        # Query historical data from Home Assistant
        history = self.get_history(entity_id=self.temp_sensor, days=7)

        time_deltas = []
        temp_rises = []

        for start_time, end_time in self.heater_schedule:
            # Filter data for each schedule period
            for day_data in history:
                period_data = [entry for entry in day_data if start_time <= entry['last_changed'].time() <= end_time]

                # Calculate time deltas and temperature rises
                for i in range(1, len(period_data)):
                    if float(period_data[i]['state']) > float(period_data[i-1]['state']):
                        time_deltas.append((period_data[i]['last_changed'] - period_data[i-1]['last_changed']).seconds / 60)
                        temp_rises.append(float(period_data[i]['state']) - float(period_data[i-1]['state']))

        # Update parameters
        if time_deltas:
            self.time_window = max(int(sum(time_deltas) / len(time_deltas)), 1)  # Ensure at least 1 minute
        if temp_rises:
            self.min_temp_rise = max(sum(temp_rises) / len(temp_rises), 0.1)  # Ensure a minimum rise of 0.1

        self.adbase.log(f"Line {self.au.lnn()}:Optimized time_window: {self.time_window}, min_temp_rise: {self.min_temp_rise}",level="INFO")

    def check_temperature(self, entity, attribute, old, new, kwargs):
        # Check if the current time is within any of the expected heating schedules
        self.adbase.log(f"Line {self.au.lnn()}: temp sensor changed to {new}.",level="DEBUG")
        current_time = datetime.now().time()
        for start_time, end_time in self.heater_schedule:
            self.adbase.log(f"Line {self.au.lnn()}: checking time window. now: {current_time}; start: {start_time}; end: {end_time}",level="DEBUG")
            
            if self.is_within_time_window(current_time, start_time, end_time):
                # Check if the temperature has risen sufficiently
                if self.heating_start_temp is None:
                    # Start of heating period
                    self.heating_start_temp = float(old)
                    self.heating_start_time = datetime.now()
                
                # Check if we're at the end of the heating period
                if current_time >= end_time:
                    total_rise = float(new) - self.heating_start_temp
                    duration = (datetime.now() - self.heating_start_time).total_seconds() / 60

                    if total_rise < self.min_temp_rise and duration >= self.time_window:
                        msg = f"Anomaly detected: Insufficient temperature rise. Total rise: {total_rise}°C over {duration} minutes"
                        self.adbase.log(msg,level="INFO")
                        self.au.shout("loud",msg)
                        self.hass.turn_on(self.alert_ent)
                    else:
                        self.adbase.log(f"Line {self.au.lnn()}: no issues all good",level="DEBUG")
                        self.hass.turn_off(self.alert_ent)
                        
                    # Reset for next heating period
                    self.heating_start_temp = None
                    self.heating_start_time = None
                break
            else:
                # Outside heating period, reset values
                self.heating_start_temp = None
                self.heating_start_time = None

    def is_within_time_window(self, current_time, start_time, end_time):
        # Calculate the start and end time with the time window
        start_window = (datetime.combine(datetime.today(), start_time) - timedelta(minutes=self.time_window)).time()
        end_window = (datetime.combine(datetime.today(), end_time) + timedelta(minutes=self.time_window)).time()
        return start_window <= current_time <= end_window    
        
    def get_history(self, entity_id, days):
        # Use Home Assistant API to get historical data
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        history = self.get_history(entity_id=entity_id, start_time=start_time, end_time=end_time)
        return history