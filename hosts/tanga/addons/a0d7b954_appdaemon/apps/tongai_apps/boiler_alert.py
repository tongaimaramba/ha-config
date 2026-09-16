import adbase as ad
from datetime import datetime, timedelta, time

class BOILERApp(ad.ADBase):

    def initialize(self):
        """Initialize AppDaemon App."""
        self.adbase = self.get_ad_api()
        self.hass = self.get_plugin_api("HASS")
        self.au = self.adbase.get_app("auto_unlock")
        
        self.log_welcome_message()
        
        # Load configuration
        self.load_configuration()
        
        # Initialize attributes for heating period tracking
        self.heating_start_temp = None
        self.heating_start_time = None
        self.current_schedule = None
        self.check_handle = None
        self.anomaly_flag = False

        # Prepare heater schedule
        self.prepare_heater_schedule()

        # Schedule optimization and checks
        self.schedule_daily_tasks()

    def log_welcome_message(self):
        """Log a welcome message."""
        welcome_msg = "\n\n************\n*\n* Welcome to Boiler Alert App ************\n*\n************\n"
        self.adbase.log(welcome_msg)

    def load_configuration(self):
        """Load configuration from arguments."""
        self.notif_device = self.args.get('notif_device')
        self.heater_times_raw = self.args.get('heater_times')
        self.time_window = max(self.args.get('time_window', 1), 1)  # Ensure time window is at least 1 minute
        self.min_temp_rise = self.args.get('min_temp_rise')
        self.alert_ent = self.args.get('alert_ent')  # input_boolean.boiler_anomaly_alert
        self.temp_sensor = self.args.get('temp_sensor')
        self.peak_temp_min = self.args.get('peak_temp_min')
        self.peak_temp_max = self.args.get('peak_temp_max')
        
        # Set history days for optimization
        self.history_days = 7 #30  # Increased for better optimization

    def prepare_heater_schedule(self):
        """Prepare the heater schedule based on raw input times."""
        self.heater_schedule = []
        
        for s in self.heater_times_raw:
            try:
                r = [int(i) for i in self.heater_times_raw[s].split(',')]
                rec = [time(r[0], r[1]), time(r[2], r[3])]
                self.heater_schedule.append(rec)
                self.adbase.log(f"Line {self.au.lnn()}: Heater times: {r}.", level="DEBUG")
            except Exception as e:
                # Default schedule if parsing fails
                rec = [time(7, 0), time(16, 0)]
                self.heater_schedule.append(rec)
                self.adbase.log(f"Line {self.au.lnn()}: Error parsing heater times: {e}. Using default schedule.", level="ERROR")

    def schedule_daily_tasks(self):
        """Schedule daily optimization and heating checks."""
        for start, end in self.heater_schedule:
            self.adbase.run_daily(self.start_heating_check, start)
            self.adbase.run_daily(self.stop_heating_check, end)
            self.adbase.log(f"Line {self.au.lnn()}: Scheduled daily checks: Start at {start}, End at {end}.", level="DEBUG")
        self.adbase.run_daily(self.optimize_parameters, time(0,0))

    def start_heating_check(self, kwargs):
        """Start the heating check."""
        self.adbase.log(f"Line {self.au.lnn()}: Starting heating period check", level="DEBUG")
        current_time = self.adbase.time()
        
        # Find the current schedule
        self.current_schedule = next((s for s in self.heater_schedule if s[0] <= current_time < s[1]), None)
        
        if self.current_schedule is None:
            self.adbase.log(f"Line {self.au.lnn()}: No matching schedule found for the current time", level="DEBUG")
            return
    
        try:
            self.heating_start_temp = float(self.adbase.get_state("sensor.boiler_temp_temperature_measurement"))
            self.heating_start_time = self.adbase.datetime()
            
            # Schedule regular checks during the heating period
            self.check_handle = self.adbase.run_every(self.check_temperature, "now", self.time_window * 60)
            self.adbase.log(f"Line {self.au.lnn()}: Running temperature checker every {self.time_window * 60} seconds", level="DEBUG")
        except ValueError as e:
            self.adbase.log(f"Line {self.au.lnn()}: Error starting heating check: {e}", level="ERROR")

    def stop_heating_check(self, kwargs):
        """Stop the heating check and report results."""
        if hasattr(self, 'check_handle'):
            if self.check_handle:
                self.adbase.cancel_timer(self.check_handle)

            current_temp, total_rise, duration = self.get_delta()

            msg_status = "Anomaly found" if self.anomaly_flag else "No anomaly found"
            report_msg = (f"Completed heating session. Temp change: {round(total_rise, 1)} degrees in "
                          f"{round(duration, 0)} minutes. {msg_status}. Params: expected temp change: "
                          f"{round(self.min_temp_rise, 1)} degrees; peak temp target: "
                          f"{self.peak_temp_min} degrees in {round(self.time_window, 0)} minutes.")
            
            # Log session results
            self.adbase.log(report_msg, level="INFO")

            # Reset tracking variables for the next session
            self.reset_vars()

    def reset_vars(self):
      """Reset relevant variables after checking temperature."""
      # Reset tracking variables after completing the heating session.
      current_vars_to_reset= {
          "heating_start_temp": None,
          "heating_start_time": None,
          "current_schedule": None,
          "anomaly_flag": False,
      }
      for var_name in current_vars_to_reset.keys():
          setattr(self,var_name,current_vars_to_reset[var_name])

    def check_temperature(self, kwargs):
      """Check the temperature during the heating period."""
      if not (self.heating_start_temp and self.current_schedule):
          return

      current_temp, total_rise, duration = self.get_delta()
      
      msg_details = f"Temp Check - Total rise: {round(total_rise, 1)} degrees over {round(duration, 0)} minutes"
      self.adbase.log(f"Line {self.au.lnn()}: Check temp started. Start temp: {self.heating_start_temp}; schedule: {self.current_schedule}. Details: {msg_details}")
      
      # Log temperature check details.
      if (total_rise < self.min_temp_rise and duration >= (self.time_window)) and not (self.peak_temp_min <= current_temp <= (self.peak_temp_max)):
          msg_anomaly= "Anomaly detected."
          
          if not (self.peak_temp_min <= current_temp <= (self.peak_temp_max)):
              msg_anomaly+= f" Didn't reach expected peak temp. Current: {current_temp}; Min: {self.peak_temp_min}."
              
          msg_anomaly+= f" Insufficient temperature rise. Total rise: {round(total_rise, 1)} degrees over {round(duration, 0)} minutes."
          
          anomaly_log= f"Line {self.au.lnn()}: {msg_anomaly}"
          # Log anomaly message.
          msg_full= f"{anomaly_log} - Triggering alert."
          msg_full+= f" Current temp: {current_temp}, Total rise: {total_rise}, Duration: {duration}."
          
          # Log anomaly detection.
          self.adbase.log(msg_full,level="DEBUG")
          
          # Set anomaly flag and trigger alert entity.
          self.au.shout("normal",msg_anomaly)
          self.anomaly_flag = True
          self.hass.turn_on(self.alert_ent)
          
      else:
          self.adbase.log(f"Line {self.au.lnn()}: no issues all good",level="DEBUG")
          self.anomaly_flag = False
          self.hass.turn_off(self.alert_ent)

    def optimize_parameters(self, kwargs):
        """Optimize parameters based on historical data."""
        self.adbase.log(f"Line {self.au.lnn()}:opto!",level="DEBUG")
        history = self.get_history(entity_id="sensor.boiler_temp_temperature_measurement", days=self.history_days)
        
        time_deltas = []
        temp_rises = []
        peak_temps = []
        anomalies_detected = 0
        
        for start_time, end_time in self.heater_schedule:
            for day_data in history:
                period_data = []
                for entry in day_data:
                    last_changed = datetime.fromisoformat(entry['last_changed'].replace('Z', '+00:00'))
                    if start_time <= last_changed.time() <= end_time:
                        period_data.append({'state': float(entry['state']), 'last_changed': last_changed})
                
                if len(period_data) >= 2:  # Ensure we have at least start and end points
                    total_rise = period_data[-1]['state'] - period_data[0]['state']
                    duration = (period_data[-1]['last_changed'] - period_data[0]['last_changed']).total_seconds() / 60
                    peak_temp = max(entry['state'] for entry in period_data)
                    
                    # Check for anomaly over the entire heating period
                    if total_rise < self.min_temp_rise or peak_temp < self.peak_temp_min or peak_temp > self.peak_temp_max:
                        anomalies_detected += 1
                        self.adbase.log(f"Anomaly found: Start: {period_data[0]}, End: {period_data[-1]}, Rise: {total_rise}, Peak: {peak_temp}")
                    else:
                        # Normal conditions: calculate time deltas and rises
                        time_deltas.append(duration)
                        temp_rises.append(total_rise)
                        peak_temps.append(peak_temp)
    
        # Update parameters only if no anomalies were detected
        if anomalies_detected == 0:
            if time_deltas:
                self.time_window = max(int(sum(time_deltas) / len(time_deltas)), 1)  # Ensure at least 1 minute
            if temp_rises:
                self.min_temp_rise = max(sum(temp_rises) / len(temp_rises), 0.1)  # Ensure a minimum rise of 0.1
            if peak_temps:
                self.peak_temp_min = min(peak_temps)  # Set to the minimum of observed peaks
                self.peak_temp_max = max(peak_temps)  # Set to the maximum of observed peaks
            
            self.adbase.log(f"## Optimized time_window: {self.time_window}, min_temp_rise: {self.min_temp_rise}, "
                            f"peak_temp_min: {self.peak_temp_min}, peak_temp_max: {self.peak_temp_max}", level="INFO")
        else:
            self.adbase.log(f"## Optimization skipped due to {anomalies_detected} anomalies detected in the last {self.history_days} days.", level="INFO")
            
    def update_parameters(time_deltas,temp_rises):
       """Update parameters based on calculated averages."""
       if time_deltas:
           avg_time_delta=max(int(sum(time_deltas)/len(time_deltas)),1) 
           avg_time_delta
        
       if temp_rises:
           avg_min_rise=max(sum(temp_rises)/len(temp_rises),0.1)

       if peak_temps:
           min_peak=min(peak_temps) 
           max_peak=max(peak_temps)

       log_msg=f"## Optimized time_window: {avg_time_delta}, min_temp_rise: {avg_min_rise}, peak_temp_min: {min_peak}, peak_temp_max: {max_peak}"
       log_msg(level="INFO")

    def get_history(self, entity_id, days):
       """Use Home Assistant API to get historical data."""
       end_time=datetime.now()
       start_time=end_time-timedelta(days=days)
       
       history=self.hass.get_history(entity_id=entity_id,start_time=start_time,end_time=end_time)
       
       return history

    def get_delta(self):
       """Calculate temperature change since heating started."""
       current_temp=float(self.adbase.get_state("sensor.boiler_temp_temperature_measurement"))
       total_rise=current_temp-self.heating_start_temp

       duration=(datetime.now()-self.heating_start_time).total_seconds()/60

       return current_temp,total_rise,duration
