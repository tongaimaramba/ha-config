# tanga — scripts.yaml (19 scripts)

| entity_id | alias | mode | actions | entities referenced |
|---|---|---|---|---|
| script.manage_guest_access | manage_guests | single | input_number.set_value, notify.all_android | input_number.monitor_action, input_number.set_value, input_select.guest_access, input_select.relationship, input_text.guest_name, input_text.mac_addr, notify.all_android |
| script.relaunch_apps | Relaunch Apps | single | input_boolean.toggle | input_boolean.relaunch, input_boolean.toggle |
| script.lock_nuki_momentary | Lock Nuki - momentary | single | switch.turn_off, switch.turn_on | switch.lock_nuki, switch.turn_off, switch.turn_on |
| script.unlock_nuki_momentary | Unlock Nuki - momentary | single | switch.turn_off, switch.turn_on | switch.turn_off, switch.turn_on, switch.unlock_nuki |
| script.open_nuki_momentary | Open Nuki - momentary | single | switch.turn_off, switch.turn_on | switch.open_nuki, switch.turn_off, switch.turn_on |
| script.movie_lights | Movie Lights | single | light.turn_off | light.dining_spotlights_3, light.lounge_lamp_1, light.movie_lamp, light.turn_off |
| script.home_fires | Home Fires | single | light.turn_off, light.turn_on | group.downstairs_lights, light.lounge_lamp_2, light.movie_lamp, light.turn_off, light.turn_on |
| script.nearly_home | Nearly Home | single | input_boolean.turn_off, input_boolean.turn_on | input_boolean.away_on_holiday, input_boolean.nearly_home, input_boolean.turn_off, input_boolean.turn_on |
| script.change_sound_output | change sound output | single | webostv.select_sound_output | input_boolean.audio_switch, media_player.projector |
| script.downstairs_lights_off | Downstairs Lights Off | single | light.turn_off, switch.turn_off | light.downstairs_lights, light.movie_lamp, light.study_desk_lamp, light.turn_off, switch.sonoff_lights, switch.turn_off |
| script.fp_delete_fingerprint | Delete Single Fingerprint | single | esphome.fp_delete_fingerprint, input_text.set_value | input_number.fp_enroll_id, input_text.fp_metadata, input_text.set_value |
| script.fp_delete_all_fingerprints | Delete All Fingerprints | single | esphome.fp_delete_all_fingerprints, input_text.set_value | input_text.fp_metadata, input_text.set_value |
| script.fp_enroll_fingerprint | fp_enroll_fingerprint | single | esphome.fp_enroll, input_text.set_value | input_number.fp_enroll_id, input_number.fp_enroll_scans, input_text.fp_enroll_finger, input_text.fp_enroll_name, input_text.fp_metadata, input_text.set_value |
| script.fp_reset | fp reset | single | esphome.fp_reset_lockout |  |
| script.auto_allocate_fingerprint_id | Auto-select Next Fingerprint ID | single | input_number.set_value, notify.mobile_app_tongai_s22 | input_number.fp_enroll_id, input_number.set_value, input_text.fp_metadata_store, notify.mobile_app_tongai_s22 |
| script.debug_fingerprint_id_parser | Enhanced Debug Fingerprint ID Parser | single | notify.mobile_app_tongai_s22 | notify.mobile_app_tongai_s22, sensor.fp_auth_fingerprint_metadata_part_1, sensor.fp_auth_fingerprint_metadata_part_2, sensor.fp_auth_fingerprint_metadata_part_3 |
| script.manage_fp_metadata | Manage FP Metadata | single | input_text.set_value | input_text.fp_metadata_store, input_text.set_value, script.manage_fp_metadata |
| script.set_growatt_sph_mode_with_retry | Set Growatt SPH Mode with Retry | single | homeassistant.update_entity, input_text.set_value, modbus.write_register | binary_sensor.octopus_energy_00000000_0009_4000_8020_000000069f30_intelligent_dispatching, input_boolean.solar_modbus_writes_enabled, input_text.set_value, input_text.solar_mode_requested, sensor.sph_ac_charge_raw, sensor.sph_battery_first_slot_1_enabled_raw, sensor.sph_battery_first_slot_1_end_raw, |
| script.ha_config_sync_tanga | Sync tanga config snapshot | single |  |  |
