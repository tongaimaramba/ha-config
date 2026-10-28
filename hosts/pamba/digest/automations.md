# pamba — automations.yaml (35 automations)

| id | alias | mode | triggers | entities referenced |
|---|---|---|---|---|
| 1642112099034 | Morning  | single | time:input_datetime.weekday_shower | input_boolean.morning_heater, input_datetime.weekday_shower, light.hue_smart_plug_1, sensor.bathroom_temperature_2 |
| 1656705377102 | Audio | single | device | media_player.projector |
| 1669496534955 | Study lamp | single | time:21:00:00, time:06:30:00 | light.study_desk_lamp, light.turn_off, light.turn_on |
| 1683826970594 | Tap 3 - dining | single | event:hue_event | light.kd_spots, light.turn_off, light.turn_on |
| 1683911066946 | Tap 2 - music room | single | event:hue_event | light.lounge_ceiling_lights, light.turn_off, light.turn_on |
| 1683972433242 | Tap 4 - dining wall lights | single | event:hue_event | light.dining_wall_lights, light.turn_off, light.turn_on |
| 1683972591632 | Tap 1 - lounge lamps | single | event:hue_event | light.lounge_wall_lights_switch, light.media_room_wall_lights_switch, light.turn_off, light.turn_on |
| 1684702121322 | Hannah moving  | single | zone:device_tracker.hannahs_iphone, zone:device_tracker.hannahs_iphone, zone:device_tracker.hannahs_iphone, zone:device_ | device_tracker.hannahs_iphone, notify.all_android, zone.home, zone.school |
| 1696798002604 | Hannah Phone Charging | single | time:18:30:00 | notify.all_phones, sensor.hannahs_iphone_battery_level, sensor.hannahs_iphone_battery_state |
| 1703931685757 | On air - Meta laptop | single | state:['binary_sensor.tongai_mbp_2_camera_in_use'] | binary_sensor.tongai_mbp_2_camera_in_use, binary_sensor.tongai_mbp_2_focus, input_select.select_option, input_select.work_status, sensor.tongai_mbp_2_active_camera, sensor.tongai_mbp_2_primary_display_name |
| 1703934406917 | Work Status  | single | state:['input_select.work_status'] | input_select.work_status, light.loft32_desk_light, light.turn_off, light.turn_on, light.work_status_on_air_light |
| 1703971587073 | On air desk button | single | state:['binary_sensor.loft32_desk_switch'], event:hue_event, event:hue_event, event:hue_event, event:hue_event | binary_sensor.loft32_desk_switch, climate.set_temperature, climate.study_ac, climate.toggle, climate.turn_off, input_select.select_next, input_select.select_option, input_select.work_status, light.hue_lightstrip_plus_1, light.loft32_desk_light, light.turn_off, light.turn_on, light.work_status_on_air |
| 1704793770116 | Work Status Bookends | single | state:['sensor.study_presence_desk_sensor'], device:4f688294beda58b4f4a6a930a36e8d93, state:['binary_sensor.tongai_mbp_2 | binary_sensor.tongai_mbp_2_active, input_select.select_option, input_select.work_status, sensor.study_presence_desk_sensor, sensor.tongai_mbp_2_primary_display_name |
| 1708505312139 | On-air - Family laptop | single | state:['binary_sensor.family_mbp_camera_in_use'] | binary_sensor.family_mbp_camera_in_use, binary_sensor.family_mbp_focus, input_select.select_option, input_select.work_status, sensor.family_mbp_active_camera, sensor.family_mbp_primary_display_name |
| 1709496362515 | Test temp | single | state:['input_number.battery_max_charge'] | input_number.battery_max_charge, input_number.daily_event_count, input_number.set_value |
| 1709909184554 | test temp wait | single | template | sensor.growatt_sph_load_power, sensor.growatt_sph_pv_power |
| 1710089973439 | Battery First Scheduler | single | time:03:00:00, time:05:30:00, state:['sensor.volvo_eva_charging_system_status'], state:['sensor.volvo_eva_charging_syste | input_boolean.battery_charging_window, input_boolean.turn_off, input_boolean.turn_on, notify.mobile_app_tongaism25, script.set_growatt_sph_mode_with_retry, sensor.volvo_eva_charging_system_status |
| 1712681075907 | audio change | single | device | input_boolean.audio_switch, input_boolean.toggle, script.change_sound_output |
| 1722015002107 | Domane alarm | single | state:['sensor.bike'] | notify.mobile_app_tongaism25, sensor.bike, sensor.domane_phone |
| 1722017723783 | Domane alert | single | state:['sensor.bike'] | notify.mobile_app_tongaism25, sensor.bike |
| 1736714739898 | downstairs off | single | time:23:30:00 | light.downstairs_lights, script.downstairs_lights_off |
| 1739571868760 | Dawn lamp | single | state:['input_boolean.dawn_lamp'] | input_boolean.dawn_lamp, light.bookshelf_lamp, light.study_desk_lamp, light.turn_off, light.turn_on |
| 1742664762678 | Run speedtest | single | state:['input_button.speedtest'] | input_button.speedtest |
| 1760567174817 | N8n | single | event:n8n_test | notify.mobile_app_tongai22 |
| 1760820131800 | Kitchen auto light | single | state:['binary_sensor.hue_motion_sensor_2_motion'], state:['binary_sensor.hue_motion_sensor_2_motion'] | binary_sensor.hue_motion_sensor_2_motion, light.hall_spotlights, light.kd_spots, light.kitchen_spotlights, light.turn_off, light.turn_on, light.wall_lamps |
| pump_timer | Pump timer | restart | state:input_boolean.pump_timer | input_boolean.pump_timer, input_boolean.turn_off, input_number.timer_length, switch.sonoff_1000eced8f, switch.turn_off, switch.turn_on |
| pump_timer | Pump timer | restart | state:input_boolean.pump_timer | input_boolean.pump_timer, input_boolean.turn_off, input_number.timer_length, switch.sonoff_1000eced8f, switch.turn_off, switch.turn_on |
| pumps_timer | Pumps timer | restart | state:input_boolean.pump_timer | input_boolean.pump_timer, input_boolean.turn_off, input_number.timer_length, switch.sonoff_1000eced8f, switch.turn_off, switch.turn_on |
| 1763912142229 | Pump timer | restart | state:input_boolean.pump_timer | input_boolean.pump_timer, input_boolean.turn_off, input_number.timer_length, switch.sonoff_1000eced8f, switch.turn_off, switch.turn_on |
| 1765661624272 | Garden Christmas Lights | single | sun, time:22:00:00, sun, time:06:00:00 | switch.sonoff_1000eced8f, switch.turn_off, switch.turn_on |
| 1779736395156 | AC on with door open (all rooms) | parallel | state:binary_sensor.closed_s, state:['binary_sensor.closed_h'], state:binary_sensor.closed_e, state:binary_sensor.closed | binary_sensor.closed_e, binary_sensor.closed_h, binary_sensor.closed_l, binary_sensor.closed_s, climate.ellie_ac, climate.hannah_ac, climate.loft_suite_ac, climate.study_ac, notify.mobile_app_tongaism25 |
| 1779736476465 | AC on with room empty (all rooms) | parallel | state:binary_sensor.pres_s, state:binary_sensor.pres_h, state:binary_sensor.pres_e, state:binary_sensor.pres_l, state:bi | binary_sensor.pres_e, binary_sensor.pres_h, binary_sensor.pres_l, binary_sensor.pres_s, climate.ellie_ac, climate.hannah_ac, climate.loft_suite_ac, climate.study_ac, notify.mobile_app_tongaism25 |
| 1779737140407 | AC on, room empty, door ALSO open (all rooms) | parallel | state:binary_sensor.pres_s, state:binary_sensor.pres_h, state:binary_sensor.pres_e, state:binary_sensor.pres_l, state:bi | binary_sensor.closed_, binary_sensor.closed_e, binary_sensor.closed_h, binary_sensor.closed_l, binary_sensor.closed_s, binary_sensor.pres_, binary_sensor.pres_e, binary_sensor.pres_h, binary_sensor.pres_l, binary_sensor.pres_s, climate.ellie_ac, climate.hannah_ac, climate.loft_suite_ac, climate.stud |
| 1789553957447 | Oppy - Daily mow | single | time:input_datetime.oppy_mow_time | input_boolean.oppy_schedule_enabled, input_datetime.oppy_mow_time, script.oppy_mow_daily |
| 1789556105052 | Garden D cleared - auto expire after 30 min | restart | state:input_boolean.garden_d_cleared | input_boolean.garden_d_cleared, input_boolean.turn_off |
