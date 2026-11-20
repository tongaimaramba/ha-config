# tanga — YAML files in config root

| file | bytes | top-level keys |
|---|---|---|
| aarlo.yaml | 21 | version, aarlo |
| automations.yaml | 44884 | list[33] |
| binary_sensors.yaml | 626 | list[3] |
| configuration.yaml | 15596 | default_config, automation, group, script, notify, logger, homeassistant, lovelace, ble_monitor, alexa, http, binary_sensor, recorder, device_tracker, stream |
| customize.yaml | 1099 | zone.home, sensor.sph_pv1_voltage, sensor.sph_pv2_voltage, sensor.sph_pv1_energy_total, sensor.sph_pv2_energy_total |
| floorplan.yaml | 1885 | name, image, stylesheet, warnings, pan_zoom, hide_app_toolbar, date_format, last_motion_entity, last_motion_class, groups |
| frontend.yaml | 67 | extra_html_url |
| gpio.yaml | 429 | switch |
| groups.yaml | 6770 | cameras, kitchen_lights, landing_lights, isla_lights, main_lights, upstairs_lights, fave_lights_downstairs, bedtime_lights, tado_rads, batteries |
| navimow_secrets.yaml | 88 | client_id, client_secret, imei |
| notify.yaml | 576 | list[4] |
| panel_custom.yaml | 136 | list[1] |
| recorder_config.yaml | 1279 | purge_keep_days, exclude |
| scenes.yaml | 791 | list[2] |
| scratch.yaml | 156 | _parse_error |
| scripts.yaml | 24979 | manage_guest_access, relaunch_apps, lock_nuki_momentary, unlock_nuki_momentary, open_nuki_momentary, movie_lights, home_fires, nearly_home, change_sound_output, downstairs_lights_off, fp_delete_finger |
| secrets.yaml | 728 | some_password, arlo_password, gen_un, dyson_pw, miele_id, miele_secret, owm_key, sdm_secret, sonoff_pw, wifi_ssid, wifi_password, tilepw, ota_password, oppy_client_id, oppy_client_secret |
| espbck/doorstep-presence.yaml | 797 | esphome, esp8266, logger, api, ota, wifi, captive_portal, sensor |
| espbck/driveway-detector.yaml | 1022 | esphome, esp32, logger, api, ota, wifi, captive_portal, sensor, light |
| espbck/landing-blind.yaml | 2268 | esphome, esp32, logger, api, ota, wifi, captive_portal, sensor, cover, switch |
| espbck/loft-blind.yaml | 2153 | esphome, esp8266, logger, api, ota, wifi, captive_portal, sensor, cover, switch |
| espbck/loft32.yaml | 1117 | esphome, esp32, logger, api, ota, wifi, captive_portal, light, binary_sensor |
| espbck/rpi-rebooter.yaml | 832 | esphome, esp32, logger, api, ota, wifi, captive_portal, switch |
| espbck/secrets.yaml | 79 | wifi_ssid, wifi_password |
| espbck/test.yaml | 2607 | sensor, cover, switch |
| espbck/trash/car.yaml | 581 | esphome, esp8266, logger, api, ota, wifi, captive_portal, light |
| espbck/trash/kitchen-nfc.yaml | 231 | substitutions, packages, esphome, wifi |
| espbck/trash/landing-blind.yaml | 2273 | esphome, esp32, logger, api, ota, wifi, captive_portal, sensor, cover, switch |
| espbck/trash/loft-blind.yaml | 1275 | esphome, esp8266, logger, api, ota, wifi, captive_portal, switch |
| espbck/trash/office-door.yaml | 510 | esphome, esp32, logger, api, ota, wifi, captive_portal |
| espbck/trash/office-esp.yaml | 507 | esphome, esp32, logger, api, ota, wifi, captive_portal |
| espbck/trash/office.yaml | 981 | esphome, esp8266, logger, api, ota, wifi, captive_portal, switch |
| espbck/trash/on-air.yaml | 503 | esphome, esp32, logger, api, ota, wifi, captive_portal |
| espbck/trash/rpi-rebooter.yaml | 513 | esphome, esp32, logger, api, ota, wifi, captive_portal |
| espbck/trash/tagreader-4edbea.yaml | 234 | substitutions, packages, esphome, wifi |
| packages/ac_shadow.yaml | 3448 | input_boolean, automation |
| packages/alarm_shadow.yaml | 856 | input_boolean, input_select |
| packages/alexa_routines.yaml | 30015 | input_boolean, input_text, timer, light, homeassistant, script, automation |
| packages/auto_unlock_shadow.yaml | 847 | input_boolean |
| packages/battery_forecast.yaml | 899 | input_boolean |
| packages/beacon_check.yaml | 2359 | input_boolean, automation |
| packages/boiler_alert.yaml | 7692 | input_boolean, input_number, template, automation |
| packages/call_check.yaml | 330 | input_boolean |
| packages/car_climate.yaml | 3260 | input_button, script, template |
| packages/chores.yaml | 2174 | input_boolean, input_text, input_select, script |
| packages/climate_health.yaml | 19766 | input_boolean, template, automation |
| packages/comfort.yaml | 514 | input_boolean |
| packages/connections_health.yaml | 7387 | input_boolean, template, automation |
| packages/digest.yaml | 297 | input_boolean |
| packages/door_buttons.yaml | 3250 | input_boolean, script |
| packages/heating_boost.yaml | 11396 | input_boolean, input_select, input_text, timer, script, automation |
| packages/heating_buttons.yaml | 18205 | input_boolean, input_text, counter, timer, template, script, automation |
| packages/homework.yaml | 5141 | input_boolean, template |
| packages/house_modes.yaml | 2227 | input_boolean |
| packages/kiosk.yaml | 18203 | input_boolean, input_button, template, script, automation |
| packages/kiosk_board.yaml | 15630 | input_select, input_datetime, automation, template |
| packages/lighting.yaml | 13907 | input_boolean, script, automation |
| packages/modbus_write_alert.yaml | 3014 | input_boolean, automation |
| packages/nfc.yaml | 6358 | input_boolean, script, automation |
| packages/notification_router.yaml | 5037 | input_boolean, input_select, input_button, script |
| packages/panic.yaml | 58681 | input_boolean, input_text, input_button, template, automation |
| packages/perimeter.yaml | 2403 | template |
| packages/presence.yaml | 24964 | input_boolean, template, script, automation |
| packages/quick_actions.yaml | 412 | group |
| packages/quick_notes.yaml | 4056 | input_text, input_select, input_datetime, input_boolean, script, template |
| packages/room_boost.yaml | 9242 | input_boolean, template, script |
| packages/room_climate.yaml | 459 | input_boolean |
| packages/room_sensors.yaml | 4376 | binary_sensor, input_boolean, automation |
| packages/school_briefing.yaml | 7535 | input_boolean, input_select, input_text, input_datetime, script, template |
| packages/security_health.yaml | 11191 | input_boolean, automation |
| packages/security_map.yaml | 18107 | template |
| packages/smartthings_heal.yaml | 20748 | input_boolean, counter, input_datetime, input_text, template, automation |
| packages/solar_control.yaml | 2956 | input_boolean, automation |
| packages/solar_controls.yaml | 11902 | input_boolean, input_datetime, script, automation, template |
| packages/solar_health.yaml | 19427 | input_boolean, automation |
| packages/solar_modbus.yaml | 20602 | input_boolean, automation, input_text, modbus, template |
| packages/solar_watch.yaml | 554 | input_boolean |
| packages/stars.yaml | 8979 | input_boolean, template, automation |
| packages/study_ac_button.yaml | 3061 | input_boolean, automation |
| packages/system_log.yaml | 351 | system_log |
| packages/tado_cloud.yaml | 898 | input_boolean, input_button |
| packages/tado_pamba_view.yaml | 6608 | template |
| packages/visitors.yaml | 19580 | input_boolean, input_datetime, template, script, automation |
| floorplan_repo/binary_sensors.yaml | 239 | list[2] |
| floorplan_repo/configuration.yaml | 323 | homeassistant, frontend, panel_custom, binary_sensor |
| floorplan_repo/customize.yaml | 116 | binary_sensor.floorplan |
| floorplan_repo/floorplan.yaml | 4172 | name, image, stylesheet, last_motion_entity, last_motion_class, groups |
| floorplan_repo/frontend.yaml | 67 | extra_html_url |
| floorplan_repo/panel_custom.yaml | 136 | list[1] |
| blueprints/automation/homeassistant/motion_light.yaml | 1219 | blueprint, mode, max_exceeded, trigger, action |
| blueprints/automation/homeassistant/notify_leaving_zone.yaml | 1260 | blueprint, trigger, variables, condition, action |
| blueprints/template/homeassistant/inverted_binary_sensor.yaml | 971 | blueprint, variables, binary_sensor |
| blueprints/script/homeassistant/confirmable_notification.yaml | 2164 | blueprint, mode, sequence |
| esphome/doorstep-presence.yaml | 761 | esphome, esp8266, logger, api, ota, wifi, captive_portal, sensor |
| esphome/driveway-detector.yaml | 986 | esphome, esp32, logger, api, ota, wifi, captive_portal, sensor, light |
| esphome/e-panic.yaml | 9705 | substitutions, esphome, esp32, logger, api, ota, wifi, captive_portal, globals, light, script, interval, binary_sensor |
| esphome/garden-proxy.yaml | 1546 | esphome, esp32, logger, api, ota, ethernet, esp32_ble_tracker, bluetooth_proxy, sensor, text_sensor, button |
| esphome/h-panic.yaml | 10231 | substitutions, esphome, esp32, logger, api, ota, wifi, captive_portal, globals, light, script, interval, binary_sensor |
| esphome/kai-proxy.yaml | 808 | esphome, esp32, logger, api, ota, wifi, web_server, esp32_ble_tracker, bluetooth_proxy, captive_portal, light |
| esphome/l-panic.yaml | 10025 | substitutions, esphome, esp32, logger, api, ota, wifi, captive_portal, globals, light, script, interval, binary_sensor |
| esphome/landing-blind.yaml | 2232 | esphome, esp32, logger, api, ota, wifi, captive_portal, sensor, cover, switch |
| esphome/loft-blind.yaml | 2119 | esphome, esp8266, logger, api, ota, wifi, captive_portal, sensor, cover, switch |
| esphome/loft-pir.yaml | 3810 | substitutions, esphome, esp32, logger, api, ota, wifi, web_server, esp32_ble_tracker, bluetooth_proxy, captive_portal, binary_sensor, number, event |
| esphome/loft32.yaml | 1260 | esphome, esp32, logger, api, ota, wifi, web_server, esp32_ble_tracker, bluetooth_proxy, captive_portal, light, binary_sensor |
| esphome/nya-proxy.yaml | 664 | esphome, esp32, logger, api, ota, wifi, web_server, esp32_ble_tracker, bluetooth_proxy, captive_portal |
| esphome/rpi-rebooter.yaml | 824 | esphome, esp32, logger, api, ota, wifi, web_server, captive_portal, switch |
| esphome/secrets.yaml | 1843 | wifi_ssid, wifi_password, c3_ap_password, c3_api_key, c3_mqtt_password, c3_ota_password, doorstep_presence_ap_password, doorstep_presence_api_key, doorstep_presence_ota_password, driveway_detector_ap_ |
| esphome/zane-proxy.yaml | 653 | esphome, esp32, logger, api, ota, wifi, esp32_ble_tracker, bluetooth_proxy, captive_portal |
