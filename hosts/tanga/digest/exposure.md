# tanga — entity exposure (emulated_hue, assistants)

## emulated_hue.ids (Alexa via Hue emulation)

- 1: button.landing_blind_close
- 2: switch.landing_blind_close_landing_blind
- 3: switch.landing_blind_stop_landing_blind
- 4: switch.landing_blind_open_landing_blind
- 5: switch.loft_blind_close_loft_suite_blind
- 6: switch.loft_blind_stop_loft_suite_blind
- 7: switch.loft_blind_open_loft_suite_blind

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
```

## exposed to assistants (9)

| entity_id | assistants |
|---|---|
| binary_sensor.everyone_home | conversation |
| binary_sensor.monitor_f965 | conversation |
| binary_sensor.monitor_hannah_phone | conversation |
| binary_sensor.monitor_mojgan_phone | conversation |
| binary_sensor.monitor_tongai_phone | conversation |
| binary_sensor.monitor_venu | conversation |
| binary_sensor.nobody_home | conversation |
| binary_sensor.somebody_is_home | conversation |
| light.litra_beam | conversation |
