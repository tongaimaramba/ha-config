# pamba — YAML files in config root

| file | bytes | top-level keys |
|---|---|---|
| aarlo.yaml | 21 | version, aarlo |
| automations.yaml | 65237 | list[50] |
| binary_sensors.yaml | 396 | list[3] |
| configuration.yaml | 11094 | default_config, automation, group, script, notify, homeassistant, http, binary_sensor, recorder, device_tracker, stream, tts, sonoff, rest, rest_command |
| customize.yaml | 71 | zone.home |
| emulated_hue.yaml | 1002 | switch.landing_blind_close_landing_blind, switch.landing_blind_stop_landing_blind, switch.landing_blind_open_landing_blind, switch.loft_blind_close_loft_suite_blind, switch.loft_blind_stop_loft_suite_ |
| floorplan.yaml | 1885 | name, image, stylesheet, warnings, pan_zoom, hide_app_toolbar, date_format, last_motion_entity, last_motion_class, groups |
| frontend.yaml | 67 | extra_html_url |
| gpio.yaml | 429 | switch |
| groups.yaml | 7045 | cameras, kitchen_lights, landing_lights, isla_lights, main_lights, upstairs_lights, fave_lights_downstairs, bedtime_lights, tado_rads, batteries |
| notify.yaml | 685 | list[5] |
| panel_custom.yaml | 136 | list[1] |
| recorder_config.yaml | 21 | purge_keep_days |
| scenes.yaml | 791 | list[2] |
| scratch.yaml | 156 | _parse_error |
| scripts.yaml | 10571 | manage_guest_access, bathtime_on, bathtime_off, study_boost, relaunch_apps, lock_nuki_momentary, unlock_nuki_momentary, open_nuki_momentary, movie_lights, home_fires, nearly_home, boost_downstairs, gr |
| secrets.yaml | 433 | some_password, arlo_password, gen_un, dyson_pw, miele_id, miele_secret, owm_key, sdm_secret, sonoff_pw, wifi_ssid, wifi_password, tilepw, ota_password |
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
| esphome/doorstep-presence.yaml | 761 | esphome, esp8266, logger, api, ota, wifi, captive_portal, sensor |
| esphome/driveway-detector.yaml | 986 | esphome, esp32, logger, api, ota, wifi, captive_portal, sensor, light |
| esphome/landing-blind.yaml | 2232 | esphome, esp32, logger, api, ota, wifi, captive_portal, sensor, cover, switch |
| esphome/loft-blind.yaml | 2117 | esphome, esp8266, logger, api, ota, wifi, captive_portal, sensor, cover, switch |
| esphome/loft32.yaml | 1081 | esphome, esp32, logger, api, ota, wifi, captive_portal, light, binary_sensor |
| esphome/rpi-rebooter.yaml | 796 | esphome, esp32, logger, api, ota, wifi, captive_portal, switch |
| esphome/secrets.yaml | 79 | wifi_ssid, wifi_password |
| esphome/test.yaml | 2607 | sensor, cover, switch |
| esphome/trash/car.yaml | 545 | esphome, esp8266, logger, api, ota, wifi, captive_portal, light |
| esphome/trash/kitchen-nfc.yaml | 231 | substitutions, packages, esphome, wifi |
| esphome/trash/landing-blind.yaml | 2273 | esphome, esp32, logger, api, ota, wifi, captive_portal, sensor, cover, switch |
| esphome/trash/loft-blind.yaml | 1239 | esphome, esp8266, logger, api, ota, wifi, captive_portal, switch |
| esphome/trash/office-door.yaml | 474 | esphome, esp32, logger, api, ota, wifi, captive_portal |
| esphome/trash/office-esp.yaml | 471 | esphome, esp32, logger, api, ota, wifi, captive_portal |
| esphome/trash/office.yaml | 945 | esphome, esp8266, logger, api, ota, wifi, captive_portal, switch |
| esphome/trash/on-air.yaml | 467 | esphome, esp32, logger, api, ota, wifi, captive_portal |
| esphome/trash/rpi-rebooter.yaml | 477 | esphome, esp32, logger, api, ota, wifi, captive_portal |
| esphome/trash/tagreader-4edbea.yaml | 234 | substitutions, packages, esphome, wifi |
| floorplan_repo/binary_sensors.yaml | 239 | list[2] |
| floorplan_repo/configuration.yaml | 323 | homeassistant, frontend, panel_custom, binary_sensor |
| floorplan_repo/customize.yaml | 116 | binary_sensor.floorplan |
| floorplan_repo/floorplan.yaml | 4172 | name, image, stylesheet, last_motion_entity, last_motion_class, groups |
| floorplan_repo/frontend.yaml | 67 | extra_html_url |
| floorplan_repo/panel_custom.yaml | 136 | list[1] |
| blueprints/automation/homeassistant/motion_light.yaml | 1219 | blueprint, mode, max_exceeded, trigger, action |
| blueprints/automation/homeassistant/notify_leaving_zone.yaml | 1260 | blueprint, trigger, variables, condition, action |
| blueprints/script/homeassistant/confirmable_notification.yaml | 2164 | blueprint, mode, sequence |
| blueprints/template/homeassistant/inverted_binary_sensor.yaml | 971 | blueprint, variables, binary_sensor |
