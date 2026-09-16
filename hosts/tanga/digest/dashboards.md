# tanga — Lovelace dashboards

## lovelace  — url `lovelace`  title `Mojgan`  (11278 bytes)

- view **Overview** — 7 cards (glance×3, entities×2, custom:auto-entities×2)
  - entities: binary_sensor.front_contact, binary_sensor.garage_out_contact, event.loft_pir_bedroom_presence_events, group.downstairs_lights, group.eating_lights, group.lounge_lamps, input_boolean.pump_timer, input_number.timer_length, light.bookshelf_lamp, light.isla_wall, light.m_side, light.t_side, lock.mudiki, lock.unlock, sensor.hannahs_iphone_battery_level, sensor.hannahs_iphone_battery_state, switch.sonoff_1000eced8f, switch.sonoff_100125dac5
- view **Heating** — 4 cards (thermostat×4)
  - entities: climate.downstairs, climate.friends, climate.main, climate.study
- view **all of it** — 3 cards (custom:auto-entities×3)
  - entities: sensor.batteries_battery_level
- view **Alarm** — 3 cards (picture-entity×2, custom:aarlo-glance×1)
  - entities: camera.aarlo_swings, camera.backyard, camera.camera, light.aarlo_front_light

## lovelace.dashboard_basics  — url `dashboard-basics`  title `Basics`  (21397 bytes)

- view **Home** — 8 cards (glance×3, entities×2, thermostat×1, gauge×1, vertical-stack×1)
  - entities: binary_sensor.front_contact, binary_sensor.garage_out_contact, climate.loft_suite_ac, group.fave_lights_downstairs, input_button.fp_lockout_reset, input_button.press, input_select.work_status, light.bookshelf_lamp, light.dining_wall_lights, light.downstairs_lights, light.lounge_pendant, light.lounge_wall_lights, light.media_room_wall_lights, light.toggle, lock.mudiki, lock.unlock, script.fp_reset, sensor.growatt_sph_grid_energy_in, sensor.growatt_sph_grid_energy_out, sensor.skoda_enyaq_battery_percentage, switch.sonoff_100125dac5
- view **Blinds** — 3 cards (entities×2, vertical-stack×1)
  - entities: cover.landing_blind_landing_blind, cover.loft_blind_loft_suite_blind, input_boolean.motion_recording_active, input_boolean.turn_off, input_boolean.turn_on, input_select.motion_travel_path
- view **Alarm** — 5 cards (picture-entity×2, entity-filter×2, custom:aarlo-glance×1)
  - entities: binary_sensor.bathroom_window_contact, binary_sensor.bay_party_wall_contact, binary_sensor.bay_window_contact, binary_sensor.front_contact, binary_sensor.garage_out_contact, binary_sensor.guest_win_contact, binary_sensor.kitchen_contact, binary_sensor.landing_window_contact, binary_sensor.loft_hatch_contact, binary_sensor.main_window_contact, binary_sensor.main_window_party_contact, binary_sensor.patio_door_contact, binary_sensor.utility_back_door_contact, camera.aarlo_swings, camera.backyard, camera.camera, light.aarlo_front_light, light.armchair_lamp, light.bathroom_sink, light.coats, light.dining_spotlights, light.hall_downlights, light.isla_downlight, light.isla_wall, light.kitchen_spotlights, light.kitchen_worktop, light.loft_main, light.lounge_dim_1, light.lounge_dim_2, light.lounge_lamp_1, light.lounge_lamp_2, light.m_side, light.main_downlights, light.movie_lamp, light.study_bedside_lamp, light.study_desk_lamp, light.t_side, light.utility
- view **TV** — 1 cards (custom:lg-remote-control×1)
  - entities: media_player.projector
- view **Solar System** — 2 cards (entities×1, vertical-stack×1)
  - entities: sensor.growatt_sph_battery_state_of_charge, sensor.growatt_sph_grid_energy_in, sensor.growatt_sph_grid_energy_out, sensor.growatt_sph_grid_power, sensor.growatt_sph_load_energy, sensor.growatt_sph_load_power, sensor.growatt_sph_pv_energy, sensor.growatt_sph_pv_power

## lovelace.lovelace_guest  — url `lovelace-guest`  title `Guest `  (1658 bytes)

- view **Home** — 1 cards (glance×1)
  - entities: binary_sensor.front_contact, binary_sensor.garage_out_contact, lock.mudiki, lock.unlock

## lovelace.lovelace_new  — url `lovelace-new`  title `Smarthome`  (16849 bytes)

- view **Overview** — 5 cards (glance×3, custom:auto-entities×2)
  - entities: binary_sensor.front_contact, binary_sensor.garage_out_contact, group.downstairs_lights, group.eating_lights, group.lounge_lamps, group.upstairs_lights, input_boolean.pump_timer, input_number.timer_length, light.bookshelf_lamp, light.isla_wall, light.m_side, light.t_side, lock.mudiki, lock.unlock, switch.sonoff_1000eced8f, switch.sonoff_100125dac5
- view **Heating** — 4 cards (thermostat×4)
  - entities: climate.downstairs, climate.friends, climate.main, climate.study
- view **House Lights** — 11 cards (entities×11)
  - entities: binary_sensor.loft_hatch_contact, group.downstairs_lights, group.hall_lights, group.isla_lights, group.kitchen_lights, group.lounge_lamps, group.lounge_spots, group.main_lights, group.upstairs_lights, group.utility_laundry_lights, group.utility_lights, group.utility_pantry_lights, light.armchair_lamp, light.bathroom_sink, light.bookshelf_lamp, light.coats, light.dining_spotlights, light.hall_spotlights, light.isla_spotlights, light.isla_wall, light.kitchen_spotlights, light.kitchen_worktop, light.loft_main, light.lounge_lamp_1, light.lounge_lamp_2, light.lounge_pendant, light.lounge_spotlights, light.m_side, light.main_spotlights, light.movie_lamp, light.study_desk_lamp, light.t_side, switch.sonoff_100125dac5
- view **Alarm** — 7 cards (entities×2, custom:auto-entities×2, picture-entity×2, custom:aarlo-glance×1)
  - entities: binary_sensor.bathroom_window_acceleration, binary_sensor.bay_party_wall_acceleration, binary_sensor.bay_window_acceleration, binary_sensor.front_acceleration, binary_sensor.garage_out_acceleration, binary_sensor.guest_win_acceleration, binary_sensor.kitchen_acceleration, binary_sensor.landing_window_acceleration, binary_sensor.main_window_acceleration, binary_sensor.main_window_party_acceleration, binary_sensor.patio_door_acceleration, binary_sensor.utility_back_door_acceleration, camera.aarlo_swings, camera.backyard, camera.camera, group.perimeter_contact, group.perimeter_movement, light.aarlo_front_light

## lovelace.lovelace_tab  — url `lovelace-tab`  title `tab`  (75477 bytes)

- view **Overview** — 10 cards (glance×4, picture-entity×2, entity-filter×2, weather-forecast×1, media-control×1)
  - entities: binary_sensor.bathroom_window_contact, binary_sensor.bay_party_wall_contact, binary_sensor.bay_window_contact, binary_sensor.front_contact, binary_sensor.garage_out_contact, binary_sensor.guest_win_contact, binary_sensor.kitchen_contact, binary_sensor.landing_window_contact, binary_sensor.loft_hatch_contact, binary_sensor.main_window_contact, binary_sensor.main_window_party_contact, binary_sensor.mukuru_contact, binary_sensor.patio_door_contact, binary_sensor.utility_back_door_contact, camera.camera, fan.bedroom, fan.upstairs, group.all_lights, group.downstairs_lights, group.fave_lights_downstairs, group.upstairs_lights, light.armchair_lamp, light.bathroom_sink, light.coats, light.dining_spotlights, light.hall_downlights, light.isla_downlight, light.isla_wall, light.kitchen_spotlights, light.kitchen_worktop, light.loft_main, light.lounge_dim_1, light.lounge_dim_2, light.lounge_lamp_1, light.lounge_lamp_2, light.m_side, light.main_downlights, light.movie_lamp, light.study_bedside_lamp, light.study_desk_lamp, light.t_side, light.utility, lock.mudiki, lock.mukuru, lock.unlock, media_player.roku_6225a6008928, script.bathtime_off, script.bathtime_on, script.study_boost, sensor.bedroom_temperature, sensor.upstairs_temperature, switch.sonoff_1000eced8f, weather.alexandra_drive
- view **Heating** — 9 cards (entities×3, thermostat×3, custom:mini-graph-card×2, glance×1)
  - entities: climate.bedroom, climate.downstairs, climate.friends, climate.main, climate.study, sensor.bathroom_temperature, sensor.bedroom_temperature, sensor.downstairs_temperature, sensor.friends_open_window, sensor.friends_temperature, sensor.guest_win_temperature_measurement, sensor.landing_temperature, sensor.main_open_window, sensor.main_temperature, sensor.study_open_window, sensor.study_temperature, sensor.upstairs_temperature
- view **Alarm** — 5 cards (picture-entity×2, entity-filter×2, custom:aarlo-glance×1)
  - entities: binary_sensor.bathroom_window_contact, binary_sensor.bay_party_wall_contact, binary_sensor.bay_window_contact, binary_sensor.front_contact, binary_sensor.garage_out_contact, binary_sensor.guest_win_contact, binary_sensor.kitchen_contact, binary_sensor.landing_window_contact, binary_sensor.loft_hatch_contact, binary_sensor.main_window_contact, binary_sensor.main_window_party_contact, binary_sensor.patio_door_contact, binary_sensor.utility_back_door_contact, camera.aarlo_swings, camera.backyard, camera.camera, light.aarlo_front_light, light.armchair_lamp, light.bathroom_sink, light.coats, light.dining_spotlights, light.hall_downlights, light.isla_downlight, light.isla_wall, light.kitchen_spotlights, light.kitchen_worktop, light.loft_main, light.lounge_dim_1, light.lounge_dim_2, light.lounge_lamp_1, light.lounge_lamp_2, light.m_side, light.main_downlights, light.movie_lamp, light.study_bedside_lamp, light.study_desk_lamp, light.t_side, light.utility
- view **all of it** — 4 cards (custom:auto-entities×3, entity-filter×1)
  - entities: light.armchair_lamp, light.bathroom_sink, light.coats, light.dining_spotlights, light.hall_downlights, light.isla_downlight, light.isla_wall, light.kitchen_spotlights, light.kitchen_worktop, light.loft_main, light.lounge_dim_1, light.lounge_dim_2, light.lounge_lamp_1, light.lounge_lamp_2, light.m_side, light.main_downlights, light.movie_lamp, light.study_bedside_lamp, light.study_desk_lamp, light.t_side, light.utility, sensor.batteries_battery_level
- view **Octopus** — 8 cards (custom:mini-graph-card×7, custom:auto-entities×1)
  - entities: sensor.elec_cost_daily, sensor.elec_cost_hourly, sensor.elec_usage_daily, sensor.elec_usage_hourly, sensor.energy_cost_daily, sensor.energy_cost_hourly, sensor.energy_usage_daily, sensor.energy_usage_hourly, sensor.gas_cost_daily, sensor.gas_cost_hourly, sensor.gas_usage_daily, sensor.gas_usage_hourly
- view **Dev** — 8 cards (entities×3, glance×2, custom:auto-entities×2, gauge×1)
  - entities: binary_sensor.monitor, input_select.guest_access, input_select.relationship, input_text.app_reload, input_text.guest_name, input_text.mac_addr, light.study_desk_lamp, light.t_bedside, script.manage_guest_access, script.relaunch_apps, sensor.cert_expiry_hass_tojgan_net, sensor.cert_expiry_timestamp_hass_tojgan_net, sensor.monitor, sensor.monitor_tongai_phone_frontdoor_conf, switch.sonoff_1000eced8f
- view **Swings** — 1 cards (custom:aarlo-glance×1)
  - entities: camera.aarlo_swings, light.aarlo_front_light
- view **house lights** — 14 cards (entities×14)
  - entities: binary_sensor.bathroom_window_acceleration, binary_sensor.bay_party_wall_acceleration, binary_sensor.bay_party_wall_contact, binary_sensor.bay_window_acceleration, binary_sensor.bay_window_contact, binary_sensor.front_acceleration, binary_sensor.front_contact, binary_sensor.garage_out_acceleration, binary_sensor.garage_out_contact, binary_sensor.guest_win_acceleration, binary_sensor.kitchen_acceleration, binary_sensor.landing_window_acceleration, binary_sensor.landing_window_contact, binary_sensor.loft_hatch_contact, binary_sensor.main_window_acceleration, binary_sensor.main_window_party_acceleration, binary_sensor.patio_door_acceleration, binary_sensor.utility_back_door_acceleration, group.downstairs_lights, group.hall_lights, group.isla_lights, group.kitchen_lights, group.lounge_lamps, group.lounge_spots, group.main_lights, group.perimeter_contact, group.perimeter_movement, group.upstairs_lights, group.utility_laundry_lights, group.utility_lights, group.utility_pantry_lights, light.armchair_lamp, light.bathroom_sink, light.bookshelf_lamp, light.coats, light.dining_spotlights_2, light.hall_spotlights_2, light.isla_spotlights, light.isla_wall, light.kitchen_spotlights, light.kitchen_worktop, light.loft_main, light.lounge_lamp_1, light.lounge_lamp_2, light.lounge_pendantt, light.lounge_spotlights_2, light.m_side, light.main_spotlights, light.movie_lamp, light.study_desk_lamp, light.t_side, switch.sonoff_100125dac5

## lovelace.map  — url `map`  title `Map`  (154 bytes)

_no views / strategy dashboard_


## lovelace.mdiindex  — url `mdiindex`  title `MDI Icon Index`  (265 bytes)

_no views / strategy dashboard_


## lovelace.tongai_test  — url `tongai-test`  title `Home`  (138102 bytes)

- view **Overview** — 15 cards (entities×5, glance×4, custom:auto-entities×2, picture-entity×1, gauge×1, weather-forecast×1, button×1)
  - entities: binary_sensor.front_contact, binary_sensor.garage_out_contact, binary_sensor.skoda_enyaq_vehicle_locked, camera.camera, climate.bathroom_2, climate.downstairs, climate.friends, climate.main, group.downstairs_lights, input_boolean.away_on_holiday, input_boolean.force_home_mode, input_boolean.loft_blind_is_open, input_boolean.morning_heater, input_boolean.pump_timer, input_boolean.toggle, input_datetime.weekday_shower, input_number.timer_length, input_select.room_heater, light.bookshelf_lamp, light.downstairs_lights, light.linkplus_led, light.loft_suite_spotlights, light.lounge_lamp_2, light.toggle, lock.mudiki, lock.unlock, script.home_fires, script.study_boost, sensor.alarm_mode, sensor.evie_location, sensor.hannah_locator, sensor.hannahs_iphone_battery_level, sensor.hannahs_iphone_battery_state, sensor.mojgan_locator, sensor.skoda_enyaq_battery_percentage, sensor.tongai_locator, switch.loft_blind_close_loft_suite_blind, switch.loft_blind_open_loft_suite_blind, switch.loft_blind_stop_loft_suite_blind, switch.sonoff_1000eced8f, switch.sonoff_100125dac5, weather.alexandra_drive
- view **Blinds** — 2 cards (markdown×2)
  - entities: sensor.ellie_today, sensor.ellie_tomorrow, sensor.hannah_today, sensor.hannah_tomorrow
- view **Location** — 4 cards (vertical-stack×3, entities×1)
  - entities: device_tracker.bermuda_tongai_phone_bermuda_tracker, device_tracker.hannah_iphone13_bermuda_tracker, device_tracker.mojgan_iphone11_bermuda_tracker, input_boolean.mock_door_locked, input_boolean.mock_led_amber, input_boolean.mock_led_green, input_boolean.mock_led_red, input_boolean.mock_tap_front_door, input_boolean.mock_tap_garage, input_boolean.motion_logger_start_hannah, input_boolean.motion_logger_start_mojgan, input_boolean.motion_logger_start_tongai, input_boolean.motion_logger_stop, input_boolean.turn_on, input_number.mock_ble_distance, input_select.calibration_location, input_select.mock_location_area, input_select.motion_travel_path, input_text.mock_user, light.kai_proxy_front_door_status_led, person.tongai, script.arrive_at_front_door, script.leave_to_away, script.take_calibration_snapshot, sensor.bermuda_tongai_phone_area, sensor.bermuda_tongai_phone_distance, sensor.hannah_iphone13_area, sensor.mojgan_iphone11_area
- view **Blinds** — 3 cards (entities×3)
  - entities: cover.landing_blind_landing_blind, cover.loft_blind_loft_suite_blind, input_text.ellie_today
- view **TV** — 6 cards (entities×2, glance×1, vertical-stack×1, custom:tv-card×1, custom:lg-remote-control×1)
  - entities: media_player.projector, media_player.tojgantv, remote.send_command, remote.shield, remote.turn_on, script.movie_lights
- view **Solar System** — 8 cards (entities×4, vertical-stack×2, history-graph×1, custom:more-info-card×1)
  - entities: automation.battery_first_scheduler, automation.export_optimiser, binary_sensor.peak_window, input_boolean.export_window, input_select.inverter_mode, script.set_growatt_mode_from_dropdown, select.growatt_sph_work_mode_priority, sensor.growatt_sph_battery_current, sensor.growatt_sph_battery_energy_in, sensor.growatt_sph_battery_energy_out, sensor.growatt_sph_battery_power, sensor.growatt_sph_battery_state_of_charge, sensor.growatt_sph_battery_temperature, sensor.growatt_sph_battery_voltage, sensor.growatt_sph_bus_voltage, sensor.growatt_sph_device_mode, sensor.growatt_sph_grid_energy_in, sensor.growatt_sph_grid_energy_out, sensor.growatt_sph_grid_frequency, sensor.growatt_sph_grid_power, sensor.growatt_sph_grid_voltage, sensor.growatt_sph_load_energy, sensor.growatt_sph_load_percentage, sensor.growatt_sph_load_power, sensor.growatt_sph_pv_current_1, sensor.growatt_sph_pv_current_2, sensor.growatt_sph_pv_energy, sensor.growatt_sph_pv_power, sensor.growatt_sph_pv_power_1, sensor.growatt_sph_pv_power_2, sensor.growatt_sph_pv_voltage_1, sensor.growatt_sph_pv_voltage_2, sensor.growatt_sph_response, sensor.growatt_sph_serial_number, sensor.growatt_sph_temperature, sensor.tojgan3_grid_import_today
- view **WFH** — 9 cards (entities×4, picture-entity×1, thermostat×1, weather-forecast×1, light×1, custom:mushroom-light-card×1)
  - entities: binary_sensor.evie_vehicle_moving, camera.camera, climate.study, input_select.room_heater, input_select.work_status, light.hue_lightstrip_plus_1, light.litra_beam, script.study_boost, sensor.evie_location, sensor.hannah_locator, sensor.litra_beam_power, sensor.mojgan_locator, sensor.tongai_locator, weather.alexandra_drive
- view **Eva** — 11 cards (grid×6, entities×2, picture×1, gauge×1, glance×1)
  - entities: binary_sensor.volvo_eva_brake_fluid_level_warning, binary_sensor.volvo_eva_brake_light_center_warning, binary_sensor.volvo_eva_brake_light_left_warning, binary_sensor.volvo_eva_brake_light_right_warning, binary_sensor.volvo_eva_coolant_level_warning, binary_sensor.volvo_eva_daytime_running_light_left_warning, binary_sensor.volvo_eva_daytime_running_light_right_warning, binary_sensor.volvo_eva_door_front_left, binary_sensor.volvo_eva_door_front_right, binary_sensor.volvo_eva_door_rear_left, binary_sensor.volvo_eva_door_rear_right, binary_sensor.volvo_eva_engine_status, binary_sensor.volvo_eva_fog_light_front_warning, binary_sensor.volvo_eva_fog_light_rear_warning, binary_sensor.volvo_eva_high_beam_left_warning, binary_sensor.volvo_eva_high_beam_right_warning, binary_sensor.volvo_eva_hood, binary_sensor.volvo_eva_low_beam_left_warning, binary_sensor.volvo_eva_low_beam_right_warning, binary_sensor.volvo_eva_oil_level_warning, binary_sensor.volvo_eva_position_light_front_left_warning, binary_sensor.volvo_eva_position_light_front_right_warning, binary_sensor.volvo_eva_position_light_rear_left_warning, binary_sensor.volvo_eva_position_light_rear_right_warning, binary_sensor.volvo_eva_registration_plate_light_warning, binary_sensor.volvo_eva_service_warning, binary_sensor.volvo_eva_side_mark_lights_warning, binary_sensor.volvo_eva_sunroof, binary_sensor.volvo_eva_tailgate, binary_sensor.volvo_eva_tank_lid, binary_sensor.volvo_eva_turn_indication_front_left_warning, binary_sensor.vol
- view **house lights** — 14 cards (entities×14)
  - entities: binary_sensor.bathroom_window_acceleration, binary_sensor.bay_party_wall_acceleration, binary_sensor.bay_party_wall_contact, binary_sensor.bay_window_acceleration, binary_sensor.bay_window_contact, binary_sensor.front_acceleration, binary_sensor.front_contact, binary_sensor.garage_out_acceleration, binary_sensor.garage_out_contact, binary_sensor.guest_win_acceleration, binary_sensor.kitchen_acceleration, binary_sensor.landing_window_acceleration, binary_sensor.landing_window_contact, binary_sensor.main_window_acceleration, binary_sensor.main_window_party_acceleration, binary_sensor.patio_door_acceleration, binary_sensor.utility_back_door_acceleration, group.car_security, group.downstairs_lights, group.hall_lights, group.isla_lights, group.kitchen_lights, group.lounge_lamps, group.lounge_spots, group.main_lights, group.perimeter_contact, group.perimeter_movement, group.upstairs_lights, group.utility_laundry_lights, group.utility_lights, group.utility_pantry_lights, light.armchair_lamp, light.bathroom_sink, light.bookshelf_lamp, light.coats, light.dining_spotlights, light.hall_spotlights, light.isla_spotlights, light.isla_wall, light.kitchen_spotlights, light.kitchen_worktop, light.loft_main, light.lounge_lamp_1, light.lounge_lamp_2, light.lounge_pendant, light.lounge_spotlights, light.m_side, light.main_spotlights, light.movie_lamp, light.study_desk_lamp, light.t_side, switch.sonoff_100125dac5, switch.sonoff_100140291c
- view **Door Auth** — 6 cards (vertical-stack×3, entities×2, history-graph×1)
  - entities: binary_sensor.fp_button_a, binary_sensor.fp_button_b, input_button.delete_all_fingerprints, input_button.delete_fingerprint, input_button.enroll_fingerprint, input_button.press, input_number.authentication_time_window, input_number.fp_delete_id, input_number.lockout_duration, input_number.max_lockout_attempts, input_select.fp_enroll_finger, input_text.fp_enroll_name, input_text.fp_metadata_store, input_text.valid_button_sequence, script.fp_reset, sensor.c3_stored_fingerprints, sensor.fp_authentication_status, sensor.fp_esp32_internal_temperature
- view **Dev** — 18 cards (entities×10, custom:auto-entities×3, glance×2, sensor×1, markdown×1, vertical-stack×1)
  - entities: binary_sensor.monitor, binary_sensor.monitor_tongai_phone, device_tracker.frontdoor_nmap, device_tracker.patio_nmap, device_tracker.swings_nmap, input_boolean.all_parents_home, input_boolean.boiler_anomaly_alert, input_boolean.motion_recording_active, input_boolean.test_bridge_from_rpi5, input_boolean.test_bridge_mirror, input_boolean.turn_off, input_boolean.turn_on, input_button.speedtest, input_select.guest_access, input_select.motion_travel_path, input_select.mqtt_messages, input_select.relationship, input_text.guest_name, input_text.mac_addr, input_text.mqtt_payload, input_text.n8n, script.manage_guest_access, sensor.boiler_temp_temperature_measurement, sensor.domane_phone, sensor.monitor, sensor.monitor_tongai_phone_frontdoor_conf, sensor.myups_battery_charge, sensor.myups_load, sensor.myups_status, sensor.speedtest_download, sensor.speedtest_ping, sensor.speedtest_upload, switch.loft_blind_close_loft_suite_blind, switch.loft_blind_open_loft_suite_blind, switch.loft_blind_stop_loft_suite_blind, switch.rpi_rebooter_reboot_switch, switch.rpi_rebooter_wlan0_restart
- view **Heating** — 12 cards (thermostat×7, entities×3, grid×2)
  - entities: climate.bathroom_2, climate.downstairs, climate.friends, climate.landing_2, climate.loft_suite_ac, climate.loft_suite_rad, climate.main, climate.pure_hot_cool, climate.study, fan.pure_cool, fan.pure_hot_cool, switch.loft_ac_power, switch.loft_ac_powerful, switch.loft_ac_quiet_fan, water_heater.hot_water
- view **all of it** — 1 cards (custom:auto-entities×1)
  - entities: sensor.batteries_battery_level
- view **Alarm** — 8 cards (glance×2, picture-entity×2, entity-filter×2, custom:aarlo-glance×1, entities×1)
  - entities: binary_sensor.bathroom_window_contact, binary_sensor.bay_party_wall_contact, binary_sensor.bay_window_contact, binary_sensor.front_contact, binary_sensor.garage_out_contact, binary_sensor.guest_win_contact, binary_sensor.kitchen_contact, binary_sensor.landing_window_contact, binary_sensor.loft_hatch_contact, binary_sensor.main_window_contact, binary_sensor.main_window_party_contact, binary_sensor.patio_door_contact, binary_sensor.utility_back_door_contact, camera.aarlo_garden_c, camera.backyard, camera.camera, input_boolean.a_parent_home, input_boolean.all_parents_home, input_boolean.away_on_holiday, input_boolean.disable_auto_modes, input_boolean.force_home_mode, input_boolean.mute_alarm, input_boolean.nearly_home, input_boolean.toggle, input_boolean.we_took_the_car, light.aarlo_garden_c, light.armchair_lamp, light.bathroom_sink, light.coats, light.dining_spotlights, light.hall_downlights, light.isla_downlight, light.isla_wall, light.kitchen_spotlights, light.kitchen_worktop, light.loft_main, light.lounge_dim_1, light.lounge_dim_2, light.lounge_lamp_1, light.lounge_lamp_2, light.m_side, light.main_downlights, light.movie_lamp, light.study_bedside_lamp, light.study_desk_lamp, light.t_side, light.utility, script.nearly_home, script.turn_on, sensor.alarm_mode, sensor.alarm_schedule
- view **Swings** — 5 cards (entity-filter×2, custom:aarlo-glance×1, picture-entity×1, glance×1)
  - entities: binary_sensor.bathroom_window_contact, binary_sensor.bay_party_wall_contact, binary_sensor.bay_window_contact, binary_sensor.front_contact, binary_sensor.garage_out_contact, binary_sensor.guest_win_contact, binary_sensor.kitchen_contact, binary_sensor.landing_window_contact, binary_sensor.loft_hatch_contact, binary_sensor.main_window_contact, binary_sensor.main_window_party_contact, binary_sensor.mukuru_contact, binary_sensor.patio_door_contact, binary_sensor.utility_back_door_contact, camera.aarlo_swings, light.aarlo_front_light, light.armchair_lamp, light.bathroom_sink, light.coats, light.dining_spotlights, light.hall_downlights, light.isla_downlight, light.isla_wall, light.kitchen_spotlights, light.kitchen_worktop, light.loft_main, light.lounge_dim_1, light.lounge_dim_2, light.lounge_lamp_1, light.lounge_lamp_2, light.m_side, light.main_downlights, light.movie_lamp, light.study_bedside_lamp, light.study_desk_lamp, light.t_side, light.toggle, light.utility
- view **Oppy Control** — 1 cards (vertical-stack×1)
  - entities: binary_sensor.oppy_online, sensor.oppy_battery, sensor.oppy_errors, sensor.oppy_status

## resources (custom cards JS)

- `/hacsfiles/lovelace-hass-aarlo/hass-aarlo.js?hacstag=1972451790261` (None)
- `/hacsfiles/fan-control-entity-row/fan-control-entity-row.js?hacstag=19166315022` (None)
- `/hacsfiles/lovelace-more-info-card/more-info-card.js?hacstag=1805289500994` (None)
- `/hacsfiles/group-element/group-element-bundle.js?hacstag=179491130092` (None)
- `/hacsfiles/group-card/group-card.js?hacstag=187245511006` (None)
- `/hacsfiles/lovelace-badge-card/badge-card.js` (None)
- `/hacsfiles/lovelace-text-input-row/lovelace-text-input-row.js?hacstag=1821137430010` (None)
- `/hacsfiles/lovelace-auto-entities/auto-entities.js?hacstag=1677445841130` (None)
- `/hacsfiles/mini-media-player/mini-media-player-bundle.js?hacstag=1485208381165` (None)
- `/hacsfiles/roku-card/roku-card.js?hacstag=164367214124` (None)
- `/hacsfiles/simple-thermostat/simple-thermostat.js?hacstag=158654878250` (None)
- `/hacsfiles/kiosk-mode/kiosk-mode.js?hacstag=303101606172` (None)
- `/hacsfiles/lovelace-battery-entity-row/battery-entity-row.js` (None)
- `/hacsfiles/mini-graph-card/mini-graph-card-bundle.js?hacstag=1512800620110` (None)
- `/hacsfiles/ha-floorplan/floorplan.js?hacstag=1883234941044` (None)
- `/hacsfiles/toggle-control-button-row/toggle-control-button-row.js?hacstag=32603392131` (None)
- `/hacsfiles/hass-bha-icons/hass-bha-icons.js?hacstag=17980857698057` (None)
- `/hacsfiles/lovelace-tempometer-gauge-card/tempometer-gauge-card.js?hacstag=203246690140` (None)
- `/hacsfiles/simple-clock-card/simple-clock-card.js?hacstag=34193126615` (None)
- `/hacsfiles/lovelace-notify-card/notify-card.js?hacstag=358962656993862` (None)
- `/hacsfiles/fan-percent-button-row/fan-percent-button-row.js?hacstag=34575320518` (None)
- `/hacsfiles/charger-card/charger-card.js?hacstag=3087524090014` (None)
- `/hacsfiles/lovelace-ha-dashboard/ha-dashboard.js?hacstag=329411371110` (None)
- `/hacsfiles/lovelace-entities-btn-group/entities-btn-group.js?hacstag=373857882105` (None)
- `/hacsfiles/timer-bar-card/timer-bar-card.js?hacstag=376904517110` (None)
- `/hacsfiles/Multiline-Entity-Card/multiline-entity-card.js?hacstag=351472550122` (None)
- `/hacsfiles/LG-WebOS-Remote-Control/lg-remote-control.js?hacstag=257005990202` (None)
- `/hacsfiles/tv-card/tv-card.js?hacstag=505459170052` (None)
- `/hacsfiles/LG-WebOS-Remote-Control/` (None)
- `/local/roku-card.js` (None)
- `/hacsfiles/octopus-energy-rates-card/octopus-energy-rates-card.js?hacstag=596085141012` (None)
- `/hacsfiles/lovelace-template-entity-row/template-entity-row.js?hacstag=231674882132` (None)
- `/hacsfiles/lovelace-card-templater/lovelace-card-templater.js?hacstag=1843331630017` (None)
- `/hacsfiles/config-template-card/config-template-card.js?hacstag=172177543136` (None)
- `Url /hacsfiles/lovelace-hass-aarlo/hass-aarlo.js` (None)
- `/hacsfiles/entity-attributes-card/entity-attributes-card.js?hacstag=187245461012` (None)
- `/hacsfiles/lovelace-multiple-entity-row/multiple-entity-row.js?hacstag=178921037451` (None)
- `/hacsfiles/flex-table-card/flex-table-card.js?hacstag=156292058075` (None)
- `/hacsfiles/room-card/room-card.js?hacstag=45444094910804` (None)
- `/hacsfiles/lovelace-mushroom/mushroom.js?hacstag=444350375440` (None)
- `/hacsfiles/light-entity-card/light-entity-card.js?hacstag=168744428613` (None)
- `/hacsfiles/lovelace-card-mod/card-mod.js?hacstag=190927524344` (None)
