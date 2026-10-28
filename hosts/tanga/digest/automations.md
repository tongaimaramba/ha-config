# tanga — automations.yaml (42 automations)

| id | alias | mode | triggers | entities referenced |
|---|---|---|---|---|
| 1606917291219 | Mojgan Iphone WiFi | single | state:sensor.iphone_ssid | input_boolean.iphone_wifi, input_boolean.turn_off, input_boolean.turn_on, sensor.iphone_ssid |
| 1641497968693 | patio and lamps | single | event:hue_event | sensor.lounge_lamp_dimmer, switch.sonoff_100125dac5, switch.turn_off, switch.turn_on |
| 1642517830283 | patio and worktop | single | event:hue_event | sensor.kitchen_worktop, switch.sonoff_100125dac5, switch.turn_off, switch.turn_on |
| 1642112099034 | Morning  | single | time:input_datetime.weekday_shower | input_boolean.morning_heater, input_datetime.weekday_shower, light.hue_smart_plug_1, sensor.bathroom_temperature_2 |
| 1645567096937 | lights for Robert | single | device:vacuum.robert | light.kitchen_worktop, light.turn_on, vacuum.robert |
| 1646081816959 | Garage light timer | single | state:['switch.sonoff_100140291c'] | switch.sonoff_100140291c, switch.turn_off |
| 1656705377102 | Audio | single | device | media_player.projector |
| 1659019447358 | Tag Downstairs Lights Off is scanned | single | tag, event:tag_scanned | group.downstairs_lights, light.turn_off |
| 1659303236672 | favetune | single | tag | media_player.kitchen, media_player.play_media, media_player.volume_set |
| 1659304799679 | Tag T-light is scanned | single | tag | light.t_side, light.toggle |
| 1668696568745 | timed pump | single | state:['input_boolean.pump_timer'] | input_boolean.pump_timer, input_boolean.toggle, input_number.timer_length, switch.sonoff_1000eced8f, switch.turn_off, switch.turn_on |
| 1669495424339 | Downstairs off tag | single | tag | group.downstairs_lights |
| 1669496534955 | Study lamp | single | time:21:00:00, time:06:30:00 | light.study_desk_lamp, light.turn_off, light.turn_on |
| 1673909236249 | Dyson Night Mode | single | time:22:00:00 | switch.pure_cool_night_mode, switch.turn_on |
| 1683826970594 | Tap 3 - dining | single | event:hue_event | light.kd_spots, light.turn_off, light.turn_on |
| 1683911066946 | Tap 2 - music room | single | event:hue_event | light.lounge_ceiling_lights, light.turn_off, light.turn_on |
| 1683972433242 | Tap 4 - dining wall lights | single | event:hue_event | light.dining_wall_lights, light.turn_off, light.turn_on |
| 1683972591632 | Tap 1 - lounge lamps | single | event:hue_event | light.lounge_wall_lights, light.lounges_wall_lamps, light.media_room_wall_lights, light.turn_off, light.turn_on |
| 1684702121322 | Hannah moving  | single | zone:device_tracker.hannahs_iphone, zone:device_tracker.hannahs_iphone, zone:device_tracker.hannahs_iphone, zone:device_ | device_tracker.hannahs_iphone, notify.all_android, zone.home, zone.school |
| 1690232792612 | Parents Presence  | single | state:['binary_sensor.monitor_mojgan_phone', 'binary_sensor.monitor_tongai_phone'] | binary_sensor.monitor_mojgan_phone, binary_sensor.monitor_tongai_phone, input_boolean.a_parent_home, input_boolean.all_parents_home, input_boolean.turn_off, input_boolean.turn_on |
| 1696798002604 | Hannah Phone Charging | single | time:18:30:00 | notify.all_phones, sensor.hannahs_iphone_battery_level, sensor.hannahs_iphone_battery_state |
| 1703931685757 | On air - Meta laptop | single | state:['binary_sensor.tongai_mbp_wk_camera_in_use'] | binary_sensor.tongai_mbp_wk_camera_in_use, binary_sensor.tongai_mbp_wk_focus, input_select.select_option, input_select.work_status, sensor.tongai_mbp_wk_active_camera, sensor.tongai_mbp_wk_primary_display_name |
| 1703934406917 | Work Status  | single | state:['input_select.work_status'] | input_select.work_status, light.loft32_desk_light, light.turn_off, light.turn_on, light.work_status_on_air_light |
| 1703971587073 | [out of date] On air desk button | single | state:['binary_sensor.loft32_desk_switch'], event:hue_event, event:hue_event, event:hue_event, event:hue_event | binary_sensor.loft32_desk_switch, input_select.select_next, input_select.select_option, input_select.work_status, light.hue_lightstrip_plus_1, light.litra_beam, light.loft32_desk_light, light.turn_off, light.turn_on, light.work_status_on_air_light |
| 1704060038348 | Ellie Nightlight goes off | single | time:22:00:00 | light.ellies_bedroom, light.turn_off |
| 1704312712410 | Manage Loft Blind | single | time:19:00:00, time:07:00:00 | switch.landing_blind_close_landing_blind, switch.landing_blind_open_landing_blind, switch.loft_blind_close_loft_suite_blind, switch.turn_on |
| 1704793770116 | Work Status Bookends | single | state:['sensor.study_presence_desk_sensor'], device:4f688294beda58b4f4a6a930a36e8d93, state:['binary_sensor.tongai_mbp_w | binary_sensor.tongai_mbp_wk_active, input_select.select_option, input_select.work_status, sensor.study_presence_desk_sensor, sensor.tongai_mbp_wk_primary_display_name |
| 1708505312139 | On-air - Family laptop | single | state:['binary_sensor.family_mbp_camera_in_use'] | binary_sensor.family_mbp_camera_in_use, binary_sensor.family_mbp_focus, input_select.select_option, input_select.work_status, sensor.family_mbp_active_camera, sensor.family_mbp_primary_display_name |
| 1709480751318 | Export optimiser | single | time:input_datetime.end_window, time:input_datetime.start_window, template, template, sun, sun | input_boolean.export_window, input_boolean.turn_off, input_boolean.turn_on, input_datetime.end_window, input_datetime.start_window, script.set_growatt_sph_mode_with_retry, sensor.growatt_sph_battery_state_of_charge, sensor.growatt_sph_load_power, sensor.growatt_sph_pv_power |
| 1709496362515 | Test temp | single | state:['input_number.battery_max_charge'] | input_number.battery_max_charge, input_number.daily_event_count, input_number.set_value |
| 1709909184554 | test temp wait | single | template | sensor.growatt_sph_load_power, sensor.growatt_sph_pv_power |
| 1710089973439 | Battery First Scheduler | single | time:03:00:00, time:05:30:00, state:['sensor.garage_vivo_charging_status'], state:['sensor.garage_vivo_charging_status'] | input_boolean.battery_charging_window, input_boolean.turn_off, input_boolean.turn_on, notify.mobile_app_tongaism25, script.set_growatt_sph_mode_with_retry, sensor.garage_vivo_charging_status |
| 1712681075907 | audio change | single | device | input_boolean.audio_switch, input_boolean.toggle, script.change_sound_output |
| 1736714739898 | downstairs off | single | time:23:00:00 | light.downstairs_lights, script.downstairs_lights_off |
| 1739571868760 | Dawn lamp | single | state:['input_boolean.dawn_lamp'] | input_boolean.dawn_lamp, light.study_desk_lamp, light.turn_off, light.turn_on |
| 1742664762678 | Run speedtest | single | state:['input_button.speedtest'] | input_button.speedtest |
| 1744811803504 | Force Litra Beam State Sync | single | time_pattern | sensor.litra_beam_power |
| 1749894430384 | Fingerprint Enrollment Management | restart | state:['input_button.enroll_fingerprint'], state:['input_button.delete_fingerprint'], state:['input_button.delete_all_fi | input_button.delete_all_fingerprints, input_button.delete_fingerprint, input_button.enroll_fingerprint, input_number.fp_delete_id, input_number.fp_enroll_id, input_number.fp_enroll_scans, input_select.fp_enroll_finger, input_select.select_option, input_text.fp_enroll_name, input_text.fp_metadata_sto |
| 1750269427938 | Sync FP Metadata to ESPHome on Boot | single | state:binary_sensor.fp_device_status | binary_sensor.fp_device_status, input_text.fp_metadata_store |
| 1752418954085 | bedside controller | single | event:hue_event, event:hue_event, event:hue_event, event:hue_event | climate.loft_suite_ac, climate.set_hvac_mode, climate.set_temperature, climate.turn_off, climate.turn_on, fan.pure_cool, fan.turn_off, fan.turn_on, input_boolean.ac_toggle, input_boolean.blinds_toggle, input_boolean.dyson_toggle, input_boolean.turn_off, input_boolean.turn_on, input_number.ac_temp_co |
| 1752419002586 | solar mode force | single | state:['select.growatt_sph_work_mode_priority'], state:['select.growatt_sph_work_mode_priority'], state:['select.growatt | notify.mobile_app_tongaism25, select.growatt_sph_work_mode_priority, select.select_option, sensor.growatt_sph_device_mode |
| 1764098343827 | Proxy to mock tap (combined, debounce, and reset) | parallel | state:['binary_sensor.front_step_proxy', 'binary_sensor.front_door_proxy'], state:['binary_sensor.garage_step_proxy', 'b | binary_sensor.front_door_proxy, binary_sensor.front_step_proxy, binary_sensor.garage_door_proxy, binary_sensor.garage_step_proxy, input_boolean.mock_tap_front_door, input_boolean.mock_tap_front_door_cooldown, input_boolean.mock_tap_garage, input_boolean.mock_tap_garage_cooldown, input_boolean.turn_o |
