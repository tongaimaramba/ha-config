# pamba — scripts.yaml (22 scripts)

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
| script.downstairs_lights_off | Downstairs Lights Off | single | light.turn_off, switch.turn_off | light.downstairs_lights, light.hue_lightstrip_plus_1, light.loft32_desk_light, light.movie_lamp, light.turn_off, light.work_status_on_air_light, switch.sonoff_lights, switch.turn_off |
| script.ignore_ac_automation_for_1_hour | Ignore AC Automation for 1 Hour | single | input_boolean.turn_on, input_datetime.set_datetime, persistent_notification.create | input_boolean.ignore_ac_automation, input_boolean.turn_on, input_datetime.ignore_until, input_datetime.set_datetime |
| script.reset_all_ac_flags | Reset All AC Flags | single | input_boolean.turn_off, input_datetime.set_datetime, light.turn_off | input_boolean.ignore_ac_automation, input_boolean.turn_off, input_datetime.ignore_until, input_datetime.set_datetime, light.scenario_1_light, light.scenario_2_light, light.scenario_3_light, light.turn_off |
| script.set_growatt_sph_mode_with_retry | Set Growatt SPH Mode with Retry | single | mqtt.publish | sensor.growatt_sph_device_mode |
| script.set_growatt_mode_from_dropdown | Set Growatt Mode From Dropdown | single | script.set_growatt_sph_mode_with_retry | input_select.inverter_mode, script.set_growatt_sph_mode_with_retry |
| script.print_entities_to_file | Print Entities To File | single | notify.entity_log | notify.entity_log |
| script.oppy_mow_daily | Oppy - Daily mow (D-flag aware) | single | input_boolean.turn_off, navimow_pro.mow | input_boolean.garden_d_cleared, input_boolean.turn_off |
| script.oppy_mow_all | Oppy - Mow all zones (ad hoc) | single | navimow_pro.mow |  |
