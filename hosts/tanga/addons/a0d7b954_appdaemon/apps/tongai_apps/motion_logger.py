import appdaemon.plugins.hass.hassapi as hass
import csv
import os
from datetime import datetime

CAR_PATH_CODES = {"CAR_L", "CAR_R", "LV_CAR"}

USER_PHONE_CONFIG = {
    "Tongai": {
        "bermuda_area": "sensor.bermuda_tongai_phone_area",
        "bermuda_dist": "sensor.bermuda_tongai_phone_distance",
        "bermuda_nearest_scanner": "sensor.bermuda_943325332614c25806d5320a803683b_100_40004_nearest_scanner",
        "bermuda_nearest_rssi": "sensor.bermuda_943325332614c25806d5320a803683b_100_40004_nearest_rssi",
        "bermuda_area_last_seen": "sensor.bermuda_943325332614c25806d5320a803683b_100_40004_area_last_seen",
        "bermuda_dist_bedroom": "sensor.bermuda_943325332614c25806d5320a803683b_100_40004_distance_to_bedroom_presence",
        "bermuda_dist_zane": "sensor.bermuda_943325332614c25806d5320a803683b_100_40004_distance_to_front_door",
        "bermuda_dist_kai": "sensor.bermuda_tongai_phone_distance_to_kai_proxy",
        "bermuda_dist_work": "sensor.bermuda_tongai_phone_distance_to_work_status",
        "bermuda_dist_nya": "sensor.bermuda_tongai_phone_distance_to_nya_proxy",
        "tracker": "device_tracker.bermuda_tongai_phone_bermuda_tracker",
        "person": "person.tongai",
        "wifi_bssid": "sensor.tongaism25_wi_fi_bssid",
        "wifi_rssi": "sensor.tongaism25_wi_fi_signal_strength"
    },
    "Mojgan": {
        "bermuda_area": "sensor.bermuda_mojgan_iphone11_area",
        "bermuda_dist": "sensor.bermuda_mojgan_iphone11_distance",
        "bermuda_nearest_scanner": "sensor.bermuda_mojgan_iphone11_nearest_scanner",
        "bermuda_nearest_rssi": "sensor.bermuda_mojgan_iphone11_nearest_rssi",
        "bermuda_area_last_seen": "sensor.bermuda_mojgan_iphone11_area_last_seen",
        "bermuda_dist_bedroom": "sensor.bermuda_mojgan_iphone11_distance_to_bedroom_presence",
        "bermuda_dist_zane": "sensor.bermuda_mojgan_iphone11_distance_to_front_door",
        "bermuda_dist_kai": "sensor.bermuda_mojgan_iphone11_distance_to_kai_proxy",
        "bermuda_dist_work": "sensor.bermuda_mojgan_iphone11_distance_to_work_status",
        "bermuda_dist_nya": "sensor.bermuda_mojgan_iphone11_distance_to_nya_proxy",
        "tracker": "device_tracker.bermuda_mojgan_iphone11_bermuda_tracker",
        "person": "person.mojgan",
        "wifi_bssid": "sensor.mojgan_iphone11_wi_fi_bssid",
        "wifi_rssi": "sensor.mojgan_iphone11_wi_fi_signal_strength"
    },
    "Hannah": {
        "bermuda_area": "sensor.bermuda_hannah_iphone13_area",
        "bermuda_dist": "sensor.bermuda_hannah_iphone13_distance",
        "bermuda_nearest_scanner": "sensor.bermuda_hannah_iphone13_nearest_scanner",
        "bermuda_nearest_rssi": "sensor.bermuda_hannah_iphone13_nearest_rssi",
        "bermuda_area_last_seen": "sensor.bermuda_hannah_iphone13_area_last_seen",
        "bermuda_dist_bedroom": "sensor.bermuda_hannah_iphone13_distance_to_bedroom_presence",
        "bermuda_dist_zane": "sensor.bermuda_hannah_iphone13_distance_to_front_door",
        "bermuda_dist_kai": "sensor.bermuda_hannah_iphone13_distance_to_kai_proxy",
        "bermuda_dist_work": "sensor.bermuda_hannah_iphone13_distance_to_work_status",
        "bermuda_dist_nya": "sensor.bermuda_hannah_iphone13_distance_to_nya_proxy",
        "tracker": "device_tracker.bermuda_hannah_iphone13_bermuda_tracker",
        "person": "person.hannah",
        "wifi_bssid": "sensor.hannah_iphone13_wi_fi_bssid",
        "wifi_rssi": "sensor.hannah_iphone13_wi_fi_signal_strength"
    },
}

CAR_TRACKER = "device_tracker.volvo_eva_location"

class MotionLogger(hass.Hass):
    def initialize(self):
        self.csv_dir = "/config/www/motion_logs"
        self.max_file_size_mb = 10
        self.log_filename = "motion_log.csv"
        self.poll_frequency = 0.1
        self.debug_level = self.args.get('debug_level', 'INFO')
        self.recording = False
        self.recording_task = None
        self.csv_writer = None
        self.csv_file_handle = None
        self.active_user = None

        os.makedirs(self.csv_dir, exist_ok=True)
        self.listen_state(self.toggle_pressed, "input_boolean.motion_logger_start_tongai")
        self.listen_state(self.toggle_pressed, "input_boolean.motion_logger_start_mojgan")
        self.listen_state(self.toggle_pressed, "input_boolean.motion_logger_start_hannah")
        self.listen_state(self.toggle_pressed, "input_boolean.motion_logger_stop")
        self.log("MotionLogger initialized", level="INFO")

    def should_log(self, level):
        levels = {"DEBUG": 1, "INFO": 2, "WARNING": 3, "ERROR": 4}
        return levels[level] >= levels[self.debug_level]

    def log(self, message, level="INFO"):
        if self.should_log(level):
            super().log(message, level=level)

    def toggle_pressed(self, entity, attribute, old, new, kwargs):
        if new != "on":
            return

        if entity == "input_boolean.motion_logger_stop":
            self.stop_recording()
            self.turn_off_all_buttons()
            return

        user_lookup = {
            "input_boolean.motion_logger_start_tongai": "Tongai",
            "input_boolean.motion_logger_start_mojgan": "Mojgan",
            "input_boolean.motion_logger_start_hannah": "Hannah"
        }
        desired_user = user_lookup.get(entity)
        self.turn_off_all_buttons()
        if not self.recording:
            self.active_user = desired_user
            self.start_recording()
        else:
            self.log("Already recording; stop before switching user.", level="WARNING")

    def turn_off_all_buttons(self):
        self.set_state("input_boolean.motion_logger_start_tongai", state="off")
        self.set_state("input_boolean.motion_logger_start_mojgan", state="off")
        self.set_state("input_boolean.motion_logger_start_hannah", state="off")
        self.set_state("input_boolean.motion_logger_stop", state="off")

    def start_recording(self):
        user = self.active_user
        if user not in USER_PHONE_CONFIG:
            self.log(f"No phone config for user '{user}'", level="ERROR")
            return

        travel_path = self.get_state("input_select.motion_travel_path") or "unknown"
        self.csv_file_handle, is_new = self.prepare_file()
        self.csv_writer = csv.writer(self.csv_file_handle)
        
        # Extended header with all Bermuda sensors
        header = [
            "timestamp_iso", "timestamp_ms", "user", "path_code",
            "wifi_bssid", "wifi_rssi",
            "bermuda_area", "bermuda_distance",
            "bermuda_nearest_scanner", "bermuda_nearest_rssi",
            "bermuda_area_last_seen",
            "bermuda_dist_bedroom", "bermuda_dist_zane", 
            "bermuda_dist_kai", "bermuda_dist_work", "bermuda_dist_nya",
            "tracker_state", "tracker_scanner",
            "person_state", "person_source", "person_user", 
            "person_lat", "person_lon"
        ]
        
        if self.get_travel_code(travel_path) in CAR_PATH_CODES:
            header += ["car_tracker_state", "car_lat", "car_lon"]

        if is_new:
            self.csv_writer.writerow(header)
            self.csv_file_handle.flush()
        self.header = header

        self.recording = True
        self.recording_task = self.run_every(self.poll_sensors, datetime.now(), self.poll_frequency)
        self.log(f"Recorder started for {user}", level="INFO")

    def stop_recording(self):
        self.log("Stopping recording", level="INFO")
        if not self.recording:
            return
        if self.recording_task:
            try:
                self.cancel_timer(self.recording_task)
            except Exception as e:
                self.log(f"Failed to cancel timer: {e}", level="WARNING")
            self.recording_task = None
        if self.csv_file_handle:
            try:
                self.csv_file_handle.close()
            except Exception as e:
                self.log(f"Failed to close file: {e}", level="WARNING")
            self.csv_file_handle = None
            self.csv_writer = None

        self.recording = False
        self.active_user = None

    def prepare_file(self):
        filepath = os.path.join(self.csv_dir, self.log_filename)
        is_new = False
        if os.path.exists(filepath):
            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            if size_mb > self.max_file_size_mb:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                archive_name = f"motion_log_{timestamp}.csv"
                archive_path = os.path.join(self.csv_dir, archive_name)
                os.rename(filepath, archive_path)
                is_new = True
        else:
            is_new = True

        handle = open(filepath, 'a', newline='')
        return handle, is_new

    def poll_sensors(self, kwargs):
        if not self.recording or not self.csv_writer or not self.active_user:
            return

        phone = USER_PHONE_CONFIG[self.active_user]
        now = datetime.now()
        timestamp_iso = now.isoformat()
        timestamp_ms = int(now.timestamp() * 1000)
        path_code = self.get_travel_code(self.get_state("input_select.motion_travel_path"))
        
        row = [timestamp_iso, timestamp_ms, self.active_user, path_code]
        
        # WiFi data (user-specific)
        wifi_bssid = self.get_state(phone["wifi_bssid"]) or ""
        wifi_rssi = self.get_state(phone["wifi_rssi"]) or ""
        row.extend([wifi_bssid, wifi_rssi])
        
        # Bermuda core sensors
        bermuda_area = self.get_state(phone["bermuda_area"]) or ""
        bermuda_distance = self.get_state(phone["bermuda_dist"]) or ""
        row.extend([bermuda_area, bermuda_distance])
        
        # Bermuda additional sensors
        nearest_scanner = self.get_state(phone["bermuda_nearest_scanner"]) or ""
        nearest_rssi = self.get_state(phone["bermuda_nearest_rssi"]) or ""
        area_last_seen = self.get_state(phone["bermuda_area_last_seen"]) or ""
        row.extend([nearest_scanner, nearest_rssi, area_last_seen])
        
        # Distance to each proxy
        dist_bedroom = self.get_state(phone["bermuda_dist_bedroom"]) or ""
        dist_zane = self.get_state(phone["bermuda_dist_zane"]) or ""
        dist_kai = self.get_state(phone["bermuda_dist_kai"]) or ""
        dist_work = self.get_state(phone["bermuda_dist_work"]) or ""
        dist_nya = self.get_state(phone["bermuda_dist_nya"]) or ""
        row.extend([dist_bedroom, dist_zane, dist_kai, dist_work, dist_nya])
        
        # Tracker data
        tracker_data = self.get_state(phone["tracker"], attribute="all")
        tracker_state = tracker_data["state"] if tracker_data else ''
        tracker_scanner = tracker_data["attributes"].get("scanner", '') if tracker_data else ''
        row.extend([tracker_state, tracker_scanner])
        
        # Person data
        person_data = self.get_state(phone["person"], attribute="all")
        person_state = person_data["state"] if person_data else ''
        person_source = person_data["attributes"].get('source', '') if person_data else ''
        person_user = person_data["attributes"].get('user_id', '') if person_data else ''
        lat = person_data["attributes"].get('latitude', '') if person_data else ''
        lon = person_data["attributes"].get('longitude', '') if person_data else ''
        row.extend([person_state, person_source, person_user, lat, lon])
        
        # Car data (only for car paths)
        if path_code in CAR_PATH_CODES:
            car_data = self.get_state(CAR_TRACKER, attribute="all")
            car_state = car_data["state"] if car_data else ''
            car_lat = car_data["attributes"].get('latitude', '') if car_data else ''
            car_lon = car_data["attributes"].get('longitude', '') if car_data else ''
            row += [car_state, car_lat, car_lon]
        
        try:
            self.csv_writer.writerow(row)
            self.csv_file_handle.flush()
        except Exception as e:
            self.log(f"Failed to write row: {e}", level="ERROR")

    def get_travel_code(self, travel_path):
        codes = {
            "Arriving from left pavement": "PAVE_L",
            "Arriving from right pavement": "PAVE_R",
            "Arriving by car into driveway": "CAR_L",
            "Leaving to left pavement": "LV_PAVE_L",
            "Leaving to right pavement": "LV_PAVE_R",
            "Leaving by car from driveway": "LV_CAR",
        }
        return codes.get(travel_path, "UNK")

    def terminate(self):
        self.log("Terminating MotionLogger", level="INFO")
        if self.recording:
            self.stop_recording()
