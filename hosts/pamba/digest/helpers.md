# pamba — UI-created helpers (.storage/input_*, counter, timer, zone)

## input_boolean (31)

| entity_id | name | settings |
|---|---|---|
| input_boolean.just_got_home | away on holiday | {} |
| input_boolean.just_knocked | Disable Alarm Auto Modes | {} |
| input_boolean.tap_to_open | Importing | {} |
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
| input_boolean.ac_toggle | AC Toggle | {"icon": "mdi:air-filter"} |
| input_boolean.dyson_toggle | Dyson Toggle | {"icon": "mdi:fan"} |
| input_boolean.blinds_toggle | Blinds Toggle | {"icon": "mdi:blinds"} |
| input_boolean.ignore_ac_automation | Ignore AC Automation | {"icon": "mdi:air-conditioner"} |
| input_boolean.ac_hi_lo_speed | AC Hi-Lo Speed | {"icon": "mdi:fan"} |
| input_boolean.blinds_are_closed | Blinds are closed | {} |
| input_boolean.test_bridge | test bridge rpi4 | {"icon": "mdi:bridge"} |
| input_boolean.bridge_sync | bridge sync | {"icon": "mdi:database-sync-outline"} |
| input_boolean.testing_bridge_update | Testing bridge update | {} |
| input_boolean.garden_d_cleared | Garden D Cleared | {"icon": "mdi:dog"} |
| input_boolean.oppy_schedule_enabled | Oppy Schedule Enabled | {"icon": "mdi:clock-outline"} |

## input_datetime (8)

| entity_id | name | settings |
|---|---|---|
| input_datetime.weekday_shower | weekday shower | {"icon": "mdi:shower-head", "has_time": true, "has_date": false} |
| input_datetime.return | Return | {"has_date": true, "has_time": true} |
| input_datetime.start_window | Start Window | {"has_date": false, "has_time": true} |
| input_datetime.end_window | End window | {"has_date": false, "has_time": true} |
| input_datetime.high_start | high start | {"has_date": true, "has_time": true, "icon": "mdi:currency-gbp"} |
| input_datetime.high_end | high end | {"has_date": false, "has_time": true, "icon": "mdi:currency-gbp"} |
| input_datetime.ignore_until | Ignore Until | {"has_date": true, "icon": "mdi:air-filter", "has_time": true} |
| input_datetime.oppy_mow_time | Oppy Mow Time | {"has_date": false, "icon": "mdi:timer-outline", "has_time": true} |

## input_number (10)

| entity_id | name | settings |
|---|---|---|
| input_number.timer_length | timer length | {"min": 0.0, "max": 600.0, "icon": "mdi:av-timer", "unit_of_measurement": " mins", "mode": "box", "step": 1.0} |
| input_number.daily_event_count | daily event count | {"min": 0.0, "max": 1.0, "step": 0.01, "mode": "slider"} |
| input_number.battery_max_charge | Battery Max Charge | {"min": 0.0, "max": 100.0, "mode": "slider", "step": 1.0, "unit_of_measurement": "%"} |
| input_number.off_peak_electric | Peak Grid Consumption Today | {"min": 0.0, "max": 1000.0, "mode": "box", "step": 1.0, "icon": "mdi:led-outline", "unit_of_measurement": "kWh"} |
| input_number.peak_electric_price | Peak Electric Price | {"min": 0.0, "max": 100.0, "icon": "mdi:led-on", "mode": "box", "step": 1.0} |
| input_number.blind_open_duration | blind_open_duration | {"min": 0.0, "max": 100.0, "icon": "mdi:timer", "mode": "slider", "step": 1.0} |
| input_number.blind_close_duration | blind_close_duration | {"min": 0.0, "max": 100.0, "icon": "mdi:timer", "mode": "slider", "step": 1.0} |
| input_number.ac_temp | AC Temp Heat | {"min": 20.0, "max": 26.0, "step": 0.5, "mode": "slider"} |
| input_number.dyson_speed | Dyson Speed | {"min": 2.0, "max": 10.0, "icon": "mdi:fan", "step": 1.0, "mode": "slider"} |
| input_number.ac_temp_cool | AC Temp Cool | {"min": 18.0, "max": 21.0, "icon": "mdi:air-conditioner", "step": 0.5, "mode": "slider"} |

## input_select (9)

| entity_id | name | settings |
|---|---|---|
| input_select.device_type | Relationship | {"options": ["Guest", "Resident"], "icon": "mdi:face"} |
| input_select.room_heater | Room Heater | {"icon": "mdi:fireplace", "options": ["climate.study", "climate.main", "climate.friends", "climate.bathroom_2", "climate.loft_suite_rad"]} |
| input_select.mqtt_messages | MQTT Messages | {"options": ["ping", "frontdoor", "swings", "patio", "test"]} |
| input_select.matcher | matcher | {"icon": "mdi:alarm-panel", "options": ["open", "retry", "fail", "ants"]} |
| input_select.work_status | Work Status | {"icon": "mdi:laptop", "options": ["Not working, yay!", "At work", "On a call", "Focus time"]} |
| input_select.ac_mode | AC Mode | {"icon": "mdi:air-conditioner", "options": ["Fan", "Heat", "Cool"]} |
| input_select.dyson_mode | Dyson Mode | {"icon": "mdi:fan", "options": ["Normal", "Night"]} |
| input_select.inverter_mode_change_retry | inverter_mode_change_retry | {"icon": "mdi:repeat", "options": ["Battery First", "Load First", "Grid First"]} |
| input_select.inverter_mode | Inverter Mode | {"icon": "mdi:server", "options": ["Load first", "Battery first", "Grid first"]} |

## input_text (6)

| entity_id | name | settings |
|---|---|---|
| input_text.app_reload | App Reload | {"icon": "mdi:power", "max": 100, "min": 0, "mode": "text"} |
| input_text.runtime | runtime | {"icon": "mdi:camera-timer", "max": 100, "mode": "text", "min": 0} |
| input_text.mqtt_payload | mqtt_payload | {"mode": "text", "min": 0, "max": 100} |
| input_text.mqtt_cmd | mqtt_cmd | {"icon": "mdi:remote-desktop", "mode": "text", "min": 0, "max": 100} |
| input_text.web | Web | {"max": 100, "mode": "text", "min": 0} |
| input_text.alarm_status | alarm_status | {"max": 500, "min": 0, "mode": "text"} |

## input_button (2)

| entity_id | name | settings |
|---|---|---|
| input_button.alx | alx | {} |
| input_button.speedtest | Speedtest | {"icon": "mdi:speedometer"} |

## counter (1)

| entity_id | name | settings |
|---|---|---|
| counter.event_counting | event counting | {"step": 1, "maximum": null, "restore": true, "initial": 0, "minimum": null} |

## timer (0)

_none_

## zone (3)

| entity_id | name | settings |
|---|---|---|
| zone.school | School | {"latitude": 51.39945666354604, "longitude": -0.3033095598220826, "icon": "mdi:school", "passive": false, "radius": 110.39644167948852} |
| zone.m_work | Maple Works | {"latitude": 51.394462979231, "longitude": -0.3082783520221711, "icon": "mdi:office-building", "passive": false, "radius": 7.305791288997416} |
| zone.t_work | Meta Office Kings Cross | {"latitude": 51.538114321228925, "longitude": -0.12655735015869143, "icon": "mdi:office-building", "passive": false, "radius": 184.0} |

## person (5)

| entity_id | name | settings |
|---|---|---|
| person.tongai | Tongai | {"device_trackers": ["device_tracker.garmin_device", "device_tracker.tongaism25"], "user_id": "654b5cdf36f8494cb948a9d13e1c17c7", "picture": null} |
| person.mojgan | Mojgan | {"device_trackers": ["device_tracker.mm_iphone", "device_tracker.iphone_32", "device_tracker.macbook_pro"], "user_id": "06495997aca44e59a54f1b3138ad088e", "pict |
| person.feasby | Feasby | {"device_trackers": [], "user_id": "c99ca07941bd4465a02d08ecb04551bc", "picture": null} |
| person.hannah | Hannah | {"device_trackers": ["device_tracker.hannahs_iphone", "device_tracker.hannah_iphone", "device_tracker.hannahs_iphone13"], "user_id": "f23d493823c54dfea81dad50a9 |
| person.ellie_maramba | Ellie Maramba | {"device_trackers": ["device_tracker.ellie_s_gym_bag", "device_tracker.ellie_s_hockey_bag", "device_tracker.ellie_iphone"], "user_id": "bdb073282fe44ad38e72a06f |

