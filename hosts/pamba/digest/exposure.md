# pamba — entity exposure (emulated_hue, assistants)

## emulated_hue.ids (Alexa via Hue emulation)

- 1: button.landing_blind_close
- 2: switch.landing_blind_close_landing_blind
- 3: switch.landing_blind_stop_landing_blind
- 4: switch.landing_blind_open_landing_blind
- 5: switch.loft_blind_close_loft_suite_blind
- 6: switch.loft_blind_stop_loft_suite_blind
- 7: switch.loft_blind_open_loft_suite_blind
- 8: light.scenario_1_light
- 9: light.scenario_2_light
- 10: light.scenario_3_light
- 11: light.loft_door_closed
- 12: light.alexa_started_ac
- 13: input_boolean.away_on_holiday
- 14: binary_sensor.loft_pir_bedroom_door
- 15: input_boolean.ac_hi_lo_speed
- 16: input_boolean.garden_d_cleared
- 17: script.oppy_mow_all

## emulated_hue.yaml

```yaml
switch.landing_blind_close_landing_blind:
  name: "LB Down"
  hidden: false
switch.landing_blind_stop_landing_blind:
  name: "LB Stop"
  hidden: false
switch.landing_blind_open_landing_blind:
  name: "LB Up"
  hidden: false
switch.loft_blind_close_loft_suite_blind:
  name: "RB Down"
  hidden: false
switch.loft_blind_stop_loft_suite_blind:
  name: "RB Stop"
  hidden: false
switch.loft_blind_open_loft_suite_blind:
  name: "RB Up"
  hidden: false
light.scenario_1_light:
  name: "AC On + Room Empty"
  hidden: false
light.scenario_2_light:
  name: "AC On + Door Open"
  hidden: false
light.scenario_3_light:
  name: "Turning AC On + Door Open"
  hidden: false
light.alexa_started_ac:
  name: "Quick Chill"
  hidden: false
binary_sensor.loft_pir_bedroom_door:
  name: "loftdoorcontact"
  hidden: false
input_boolean.ac_hi_lo_speed:
  name: "AC Fan Speed High"
  hidden: false
input_boolean.garden_d_cleared:
  name: "Garden D Cleared"
  hidden: false
script.oppy_mow_all:
  name: "Oppy"
  hidden: false```

## exposed to assistants (16)

| entity_id | assistants |
|---|---|
| binary_sensor.everyone_home | conversation |
| binary_sensor.monitor_f965 | conversation |
| binary_sensor.monitor_hannah_phone | conversation |
| binary_sensor.monitor_mojgan_phone | conversation |
| binary_sensor.monitor_old_hannah_phone | conversation |
| binary_sensor.monitor_tongai_phone | conversation |
| binary_sensor.monitor_tongais22 | conversation |
| binary_sensor.monitor_venu | conversation |
| binary_sensor.nobody_home | conversation |
| binary_sensor.somebody_is_home | conversation |
| light.alexa_started_ac | conversation |
| light.loft_door_closed | conversation |
| light.loft_door_open | conversation |
| light.scenario_1_light | conversation |
| light.scenario_2_light | conversation |
| light.scenario_3_light | conversation |
