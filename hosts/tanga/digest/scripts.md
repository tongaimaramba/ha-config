# tanga — scripts.yaml (29 scripts)

| entity_id | alias | mode | actions | entities referenced |
|---|---|---|---|---|
| script.manage_guest_access | manage_guests | single | input_number.set_value, notify.all_android | input_number.monitor_action, input_number.set_value, input_select.guest_access, input_select.relationship, input_text.guest_name, input_text.mac_addr, notify.all_android |
| script.bathtime_on | Bathtime On | single | climate.set_temperature, climate.turn_on | climate.set_temperature, climate.turn_on, climate.upstairs, light.bathroom_heater, light.bathroom_sink, light.isla_wall, light.m_side |
| script.bathtime_off | Bathtime Off | single | climate.turn_off | climate.turn_off, climate.upstairs, light.bathroom_heater, light.bathroom_sink, light.isla_wall, light.m_side |
| script.study_boost | Study Boost | single | tado.set_climate_timer | input_select.room_heater |
| script.relaunch_apps | Relaunch Apps | single | input_boolean.toggle | input_boolean.relaunch, input_boolean.toggle |
| script.lock_nuki_momentary | Lock Nuki - momentary | single | switch.turn_off, switch.turn_on | switch.lock_nuki, switch.turn_off, switch.turn_on |
| script.unlock_nuki_momentary | Unlock Nuki - momentary | single | switch.turn_off, switch.turn_on | switch.turn_off, switch.turn_on, switch.unlock_nuki |
| script.open_nuki_momentary | Open Nuki - momentary | single | switch.turn_off, switch.turn_on | switch.open_nuki, switch.turn_off, switch.turn_on |
| script.movie_lights | Movie Lights | single | light.turn_off | light.dining_spotlights_3, light.lounge_lamp_1, light.movie_lamp, light.turn_off |
| script.home_fires | Home Fires | single | light.turn_off, light.turn_on | group.downstairs_lights, light.lounge_lamp_2, light.movie_lamp, light.turn_off, light.turn_on |
| script.nearly_home | Nearly Home | single | input_boolean.turn_off, input_boolean.turn_on | input_boolean.away_on_holiday, input_boolean.nearly_home, input_boolean.turn_off, input_boolean.turn_on |
| script.boost_downstairs | Boost Downstairs | single | climate.set_temperature | climate.downstairs, climate.set_temperature |
| script.grid | Grid | single | input_boolean.turn_off, input_boolean.turn_on | input_boolean.importing, input_boolean.turn_off, input_boolean.turn_on, sensor.growatt_sph_load_power, sensor.growatt_sph_pv_power |
| script.change_sound_output | change sound output | single | webostv.select_sound_output | input_boolean.audio_switch, media_player.projector |
| script.downstairs_lights_off | Downstairs Lights Off | single | light.turn_off, switch.turn_off | light.downstairs_lights, light.movie_lamp, light.study_desk_lamp, light.turn_off, switch.sonoff_lights, switch.turn_off |
| script.fp_delete_fingerprint | Delete Single Fingerprint | single | esphome.fp_delete_fingerprint, input_text.set_value | input_number.fp_enroll_id, input_text.fp_metadata, input_text.set_value |
| script.fp_delete_all_fingerprints | Delete All Fingerprints | single | esphome.fp_delete_all_fingerprints, input_text.set_value | input_text.fp_metadata, input_text.set_value |
| script.fp_enroll_fingerprint | fp_enroll_fingerprint | single | esphome.fp_enroll, input_text.set_value | input_number.fp_enroll_id, input_number.fp_enroll_scans, input_text.fp_enroll_finger, input_text.fp_enroll_name, input_text.fp_metadata, input_text.set_value |
| script.fp_reset | fp reset | single | esphome.fp_reset_lockout |  |
| script.auto_allocate_fingerprint_id | Auto-select Next Fingerprint ID | single | input_number.set_value, notify.mobile_app_tongai_s22 | input_number.fp_enroll_id, input_number.set_value, input_text.fp_metadata_store, notify.mobile_app_tongai_s22 |
| script.debug_fingerprint_id_parser | Enhanced Debug Fingerprint ID Parser | single | notify.mobile_app_tongai_s22 | notify.mobile_app_tongai_s22, sensor.fp_auth_fingerprint_metadata_part_1, sensor.fp_auth_fingerprint_metadata_part_2, sensor.fp_auth_fingerprint_metadata_part_3 |
| script.manage_fp_metadata | Manage FP Metadata | single | input_text.set_value | input_text.fp_metadata_store, input_text.set_value, script.manage_fp_metadata |
| script.ignore_ac_automation_for_1_hour | Ignore AC Automation for 1 Hour | single | input_boolean.turn_on, input_datetime.set_datetime, persistent_notification.create | input_boolean.ignore_ac_automation, input_boolean.turn_on, input_datetime.ignore_until, input_datetime.set_datetime |
| script.reset_all_ac_flags | Reset All AC Flags | single | input_boolean.turn_off, input_datetime.set_datetime, light.turn_off | input_boolean.ignore_ac_automation, input_boolean.turn_off, input_datetime.ignore_until, input_datetime.set_datetime, light.scenario_1_light, light.scenario_2_light, light.scenario_3_light, light.turn_off |
| script.set_growatt_sph_mode_with_retry | Set Growatt SPH Mode with Retry | single | mqtt.publish | sensor.growatt_sph_device_mode |
| script.set_growatt_mode_from_dropdown | Set Growatt Mode From Dropdown | single | script.set_growatt_sph_mode_with_retry | input_select.inverter_mode, script.set_growatt_sph_mode_with_retry |
| script.take_calibration_snapshot | Take Calibration Snapshot | single | notify.send_message | device_tracker.bermuda_tongai_phone_bermuda_tracker, input_select.calibration_location, notify.file, notify.send_message, sensor.bermuda_tongai_phone_area, sensor.bermuda_tongai_phone_distance, sensor.tongaism25_wi_fi_bssid, sensor.tongaism25_wi_fi_signal_strength |
| script.arrive_at_front_door | Arrive at Front Door | single | input_boolean.turn_on, input_number.set_value, input_select.select_option, input_text.set_value | input_boolean.mock_tap_front_door, input_boolean.turn_on, input_number.mock_ble_distance, input_number.set_value, input_select.mock_location_area, input_select.select_option, input_text.mock_user, input_text.set_value |
| script.leave_to_away | Leave to Away | single | input_boolean.turn_off, input_select.select_option | input_boolean.mock_tap_front_door, input_boolean.turn_off, input_select.mock_location_area, input_select.select_option |
