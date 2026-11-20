# tanga — UI-created helpers (.storage/input_*, counter, timer, zone)

## input_boolean (27)

| entity_id | name | settings |
|---|---|---|
| input_boolean.just_got_home | away on holiday | {} |
| input_boolean.just_knocked | Disable Alarm Auto Modes | {} |
| input_boolean.iphone_wifi | iphone_wifi | {"icon": "mdi:wifi"} |
| input_boolean.relaunch | relaunch | {} |
| input_boolean.pump_timer | pump_timer | {"icon": "mdi:water-pump"} |
| input_boolean.morning_heater | morning heater | {"icon": "mdi:air-conditioner"} |
| input_boolean.device_presence | device_presence | {"icon": "mdi:devices"} |
| input_boolean.m | Mute Alarm | {"icon": "mdi:alarm-light-off"} |
| input_boolean.nearly_home | Nearly Home | {"icon": "mdi:road"} |
| input_boolean.parents_home | All Parents Home | {"icon": "mdi:family-tree"} |
| input_boolean.a_parent_home | A Parent Home | {"icon": "mdi:account-group"} |
| input_boolean.we_took_the_car | We Took the Car | {"icon": "mdi:car"} |
| input_boolean.force_home_mode | Mode Override | {"icon": "mdi:home"} |
| input_boolean.loft_blind_is_open | Loft blind is open | {"icon": "mdi:blinds-open"} |
| input_boolean.export_window | Export window | {} |
| input_boolean.battery_charging_window | Battery Charging Window | {"icon": "mdi:battery-charging"} |
| input_boolean.audio_switch | audio-switch | {"icon": "mdi:cast-audio"} |
| input_boolean.boiler_anomaly_alert | boiler_anomaly_alert | {"icon": "mdi:alert"} |
| input_boolean.dawn_lamp | Dawn lamp | {} |
| input_boolean.bedroom_presence_debug | Bedroom Presence Debug | {"icon": "mdi:bug-check"} |
| input_boolean.motion_recording_active | Motion Recording Active | {"icon": "mdi:record-rec"} |
| input_boolean.tongai | Tongai | {"icon": "mdi:track-light"} |
| input_boolean.mojgan | Mojgan | {"icon": "mdi:track-light"} |
| input_boolean.hannah | Hannah | {"icon": "mdi:track-light"} |
| input_boolean.stop_recording | Stop Recording | {"icon": "mdi:stop-circle"} |
| input_boolean.test_bridge_rpi5 | test bridge rpi5 | {"icon": "mdi:bridge"} |
| input_boolean.bridge_sync | bridge sync | {"icon": "mdi:database-sync-outline"} |

## input_datetime (6)

| entity_id | name | settings |
|---|---|---|
| input_datetime.weekday_shower | weekday shower | {"icon": "mdi:shower-head", "has_time": true, "has_date": false} |
| input_datetime.return | Return | {"has_date": true, "has_time": true} |
| input_datetime.start_window | Start Window | {"has_date": false, "has_time": true} |
| input_datetime.end_window | End window | {"has_date": false, "has_time": true} |
| input_datetime.high_start | high start | {"has_date": true, "has_time": true, "icon": "mdi:currency-gbp"} |
| input_datetime.high_end | high end | {"has_date": false, "has_time": true, "icon": "mdi:currency-gbp"} |

## input_number (11)

| entity_id | name | settings |
|---|---|---|
| input_number.timer_length | timer length | {"min": 0.0, "max": 600.0, "icon": "mdi:av-timer", "unit_of_measurement": " mins", "mode": "box", "step": 1.0} |
| input_number.daily_event_count | daily event count | {"min": 0.0, "max": 1.0, "step": 0.01, "mode": "slider"} |
| input_number.battery_max_charge | Battery Max Charge | {"min": 0.0, "max": 100.0, "mode": "slider", "step": 1.0, "unit_of_measurement": "%"} |
| input_number.blind_open_duration | blind_open_duration | {"min": 0.0, "max": 100.0, "icon": "mdi:timer", "mode": "slider", "step": 1.0} |
| input_number.blind_close_duration | blind_close_duration | {"min": 0.0, "max": 100.0, "icon": "mdi:timer", "mode": "slider", "step": 1.0} |
| input_number.fp_slot_id | Fingerprint ID (Auto-assigned) | {"min": 1.0, "max": 127.0, "mode": "box", "step": 1.0} |
| input_number.fp_enroll_scans | fp_enroll_scans | {"min": 0.0, "max": 5.0, "step": 1.0, "mode": "slider"} |
| input_number.authentication_time_window | fp_authentication_time_window | {"min": 0.0, "max": 30.0, "step": 1.0, "mode": "box"} |
| input_number.lockout_duration | Lockout Duration | {"min": 0.0, "max": 600.0, "mode": "box", "step": 30.0} |
| input_number.max_lockout_attempts | Max Lockout Attempts | {"min": 2.0, "max": 10.0, "step": 1.0, "mode": "box"} |
| input_number.fp_delete_id | Fingerprint ID to Delete | {"min": 1.0, "max": 127.0, "mode": "box", "step": 1.0} |

## input_select (8)

| entity_id | name | settings |
|---|---|---|
| input_select.device_type | Relationship | {"options": ["Guest", "Resident"], "icon": "mdi:face"} |
| input_select.room_heater | Room Heater | {"icon": "mdi:fireplace", "options": ["climate.study", "climate.main", "climate.friends", "climate.bathroom_2", "climate.loft_suite_rad"]} |
| input_select.mqtt_messages | MQTT Messages | {"options": ["ping", "frontdoor", "swings", "patio", "test"]} |
| input_select.matcher | matcher | {"icon": "mdi:alarm-panel", "options": ["open", "retry", "fail", "ants"]} |
| input_select.work_status | Work Status | {"icon": "mdi:laptop", "options": ["Not working, yay!", "At work", "On a call", "Focus time"]} |
| input_select.fp_enroll_finger | Finger Name | {"options": ["Left Thumb", "Right Thumb", "Left Index", "Right Index", "Left Middle", "Right Middle", "Left Ring", "Right Ring", "Left Little", "Right Little"], |
| input_select.calibration_location | Calibration Location | {"icon": "mdi:map-marker-radius", "options": ["test desk", "inside front door", "outside front door", "outside garage", "car door driver", "car door passenger", |
| input_select.motion_travel_path | Motion Travel Path | {"options": ["Arriving from left pavement", "Arriving from right pavement", "Arriving by car into driveway", "Leaving to left pavement", "Leaving to right pavem |

## input_text (15)

| entity_id | name | settings |
|---|---|---|
| input_text.app_reload | App Reload | {"icon": "mdi:power", "max": 100, "min": 0, "mode": "text"} |
| input_text.runtime | runtime | {"icon": "mdi:camera-timer", "max": 100, "mode": "text", "min": 0} |
| input_text.mqtt_payload | mqtt_payload | {"mode": "text", "min": 0, "max": 100} |
| input_text.mqtt_cmd | mqtt_cmd | {"icon": "mdi:remote-desktop", "mode": "text", "min": 0, "max": 100} |
| input_text.web | Web | {"max": 100, "mode": "text", "min": 0} |
| input_text.alarm_status | alarm_status | {"max": 500, "min": 0, "mode": "text"} |
| input_text.fp_slot_1 | fp_slot_1 | {"mode": "text", "min": 0, "max": 100} |
| input_text.fp_slot_2 | fp_slot_2 | {"mode": "text", "min": 0, "max": 100} |
| input_text.fp_slot_3 | fp_slot_3 | {"mode": "text", "min": 0, "max": 100} |
| input_text.button_sequence | button sequence | {"min": 0, "mode": "text", "max": 100} |
| input_text.valid_button_sequence | fp_valid_button_sequence | {"min": 0, "mode": "text", "max": 100} |
| input_text.fp_enroll_name | fp_enroll_name | {"min": 0, "mode": "text", "max": 100} |
| input_text.fp_metadata_store | fp_metadata_store | {"max": 255, "mode": "text", "min": 0, "icon": "mdi:fingerprint"} |
| input_text.n8n | n8n | {"max": 100, "min": 0, "mode": "text"} |
| input_text.ellie_todat | Ellie Today | {"min": 0, "mode": "text", "max": 100} |

## input_button (6)

| entity_id | name | settings |
|---|---|---|
| input_button.alx | alx | {} |
| input_button.speedtest | Speedtest | {"icon": "mdi:speedometer"} |
| input_button.fp_lockout_reset | Reset FP Lockout | {"icon": "mdi:lock-reset"} |
| input_button.enroll_fingerprint | Enroll Fingerprint | {} |
| input_button.delete_fingerprint | Delete Fingerprint | {"icon": "mdi:delete"} |
| input_button.delete_all_fingerprints | Delete All Fingerprints | {"icon": "mdi:delete-alert-outline"} |

## counter (1)

| entity_id | name | settings |
|---|---|---|
| counter.event_counting | event counting | {"step": 1, "maximum": null, "restore": true, "initial": 0, "minimum": null} |

## timer (0)

_none_

## zone (7)

| entity_id | name | settings |
|---|---|---|
| zone.school | School | {"latitude": 51.39920272162223, "longitude": -0.30331449839823676, "icon": "mdi:school", "passive": false, "radius": 106.0} |
| zone.hinchley_wood | Hinchley Wood | {"latitude": 51.36834780591349, "longitude": -0.3451325611249274, "icon": "mdi:shoe-sneaker", "passive": false, "radius": 169.0} |
| zone.church | Church | {"latitude": 51.41775403919203, "longitude": -0.2855732686637964, "icon": "mdi:church-outline", "passive": false, "radius": 35.0} |
| zone.npl | NPL | {"latitude": 51.42454267593948, "longitude": -0.34200773561366304, "icon": "mdi:scale", "passive": false, "radius": 236.0} |
| zone.shc | SHC | {"latitude": 51.38197313549108, "longitude": -0.3246875433117964, "icon": "mdi:hockey-sticks", "passive": false, "radius": 114.0} |
| zone.tgc | TGC | {"latitude": 51.37551580372187, "longitude": -0.2939921703888615, "icon": "mdi:gymnastics", "passive": false, "radius": 72.0} |
| zone.jpmc | JPMC | {"latitude": 51.504364308038674, "longitude": -0.020008451913582803, "icon": "mdi:bank-circle", "passive": false, "radius": 345.0} |

## person (4)

| entity_id | name | settings |
|---|---|---|
| person.tongai | Tongai | {"device_trackers": ["device_tracker.garmin_device", "device_tracker.bermuda_tongai_phone_bermuda_tracker", "device_tracker.tongai_samsung25"], "user_id": "654b |
| person.mojgan | Mojgan | {"device_trackers": ["device_tracker.mm_iphone", "device_tracker.iphone_32"], "user_id": "06495997aca44e59a54f1b3138ad088e", "picture": null} |
| person.hannah | Hannah | {"device_trackers": ["device_tracker.hannahs_iphone", "device_tracker.hannah_hockey_bag", "device_tracker.hannah_keys", "device_tracker.hannah_iphone", "device_ |
| person.ellie | Ellie | {"device_trackers": ["device_tracker.ellie_s_gym_bag", "device_tracker.ellie_s_phone", "device_tracker.ellie_bag", "device_tracker.ellie_s_hockey_bag", "device_ |

