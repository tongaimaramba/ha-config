# pamba — add-ons & supervisor

- Core: `2025.11.2` (latest `2025.11.3`)  arch `armv7`
- Supervisor: `2025.11.5`  channel `stable`  healthy `True`  supported `False`
- OS: `15.0`  board `rpi4`

## add-ons

| name | slug | version | latest | state | update? |
|---|---|---|---|---|---|
| Advanced SSH & Web Terminal | a0d7b954_ssh | 21.0.2 | 24.1.4 | started | yes |
| AppDaemon | a0d7b954_appdaemon | 0.16.7 | 0.19.2 | started | yes |
| Cloudflared | 9074a9fa_cloudflared | 6.0.5 | 6.0.5 | started |  |
| File editor | core_configurator | 5.8.0 | 6.1.0 | started | yes |
| Get HACS | cb646a50_get | 1.3.1 | 1.3.1 | stopped |  |
| Home Assistant Google Drive Backup | cebe7a76_hassio_google_drive_backup | 0.112.1 | 0.112.1 | started |  |
| Let's Encrypt | core_letsencrypt | 5.0.5 | 6.5.0 | unknown | yes |
| Mosquitto broker | core_mosquitto | 6.5.2 | 7.1.1 | started | yes |
| NGINX Home Assistant SSL proxy | core_nginx_proxy | 3.13.0 | 4.5.1 | started | yes |
| Network UPS Tools | ccf28a08_nut | 0.16.1 | 0.18.1 | error | yes |
| Node-RED | a0d7b954_nodered | 18.0.4 | 22.0.6 | unknown | yes |
| SQLite Web | a0d7b954_sqlite-web | 4.4.1 | 6.1.1 | started | yes |
| Samba share | core_samba | 12.5.4 | 12.10.0 | started | yes |
| Speedtest | 6b87c29e_speedtest_addon | 1.6.2 | 1.6.2 | stopped |  |
| Terminal & SSH | core_ssh | 9.20.1 | 10.5.0 | started | yes |
| deCONZ | core_deconz | 6.23.0 | 8.8.0 | stopped | yes |

## add-on config files captured

- `addons/a0d7b954_appdaemon/appdaemon.yaml` (2089 bytes)
- `addons/a0d7b954_appdaemon/dashboards/Hello.dash` (201 bytes)
- `addons/a0d7b954_appdaemon/apps/Autounlockyaml.off` (2707 bytes)
- `addons/a0d7b954_appdaemon/apps/Homepresenceappyaml.off` (3007 bytes)
- `addons/a0d7b954_appdaemon/apps/alarm_app_v2.old` (8721 bytes)
- `addons/a0d7b954_appdaemon/apps/alarm_app_yaml.old` (2893 bytes)
- `addons/a0d7b954_appdaemon/apps/apps.yaml` (5404 bytes)
- `addons/a0d7b954_appdaemon/apps/ha_bridge.yaml` (822 bytes)
- `addons/a0d7b954_appdaemon/apps/octopus.yaml` (666 bytes)
- `addons/a0d7b954_appdaemon/apps/solar_app.yaml` (1112 bytes)
- `addons/a0d7b954_appdaemon/apps/tongai_apps/alarm_app.py` (37964 bytes)
- `addons/a0d7b954_appdaemon/apps/tongai_apps/alarm_app_py.old` (29266 bytes)
- `addons/a0d7b954_appdaemon/apps/tongai_apps/aut.py` (11371 bytes)
- `addons/a0d7b954_appdaemon/apps/tongai_apps/auto_unlock.py` (39124 bytes)
- `addons/a0d7b954_appdaemon/apps/tongai_apps/boiler_alert.py` (11824 bytes)
- `addons/a0d7b954_appdaemon/apps/tongai_apps/boiler_alert_orig_sep18.old` (10852 bytes)
- `addons/a0d7b954_appdaemon/apps/tongai_apps/boiler_alert_temp_triggered.py` (6044 bytes)
- `addons/a0d7b954_appdaemon/apps/tongai_apps/client.py` (1040 bytes)
- `addons/a0d7b954_appdaemon/apps/tongai_apps/client_mqtt.py` (1648 bytes)
- `addons/a0d7b954_appdaemon/apps/tongai_apps/device_zones.py` (1214 bytes)
- `addons/a0d7b954_appdaemon/apps/tongai_apps/gpio_mqtt.py` (2185 bytes)
- `addons/a0d7b954_appdaemon/apps/tongai_apps/guest_access.py` (2420 bytes)
- `addons/a0d7b954_appdaemon/apps/tongai_apps/ha_bridge.py` (21301 bytes)
- `addons/a0d7b954_appdaemon/apps/tongai_apps/hci_monitor.py` (1312 bytes)
- `addons/a0d7b954_appdaemon/apps/tongai_apps/iftt.py` (8698 bytes)
- `addons/a0d7b954_appdaemon/apps/tongai_apps/loo.py` (1565 bytes)
- `addons/a0d7b954_appdaemon/apps/tongai_apps/monit-dash.py` (3519 bytes)
- `addons/a0d7b954_appdaemon/apps/tongai_apps/octopus.py` (11992 bytes)
- `addons/a0d7b954_appdaemon/apps/tongai_apps/park_junk.lot` (7874 bytes)
- `addons/a0d7b954_appdaemon/apps/tongai_apps/pump.py` (6531 bytes)
- `addons/a0d7b954_appdaemon/apps/tongai_apps/rebegin_app.py` (1241 bytes)
- `addons/a0d7b954_appdaemon/apps/tongai_apps/reboot_by_mqtt.py` (2349 bytes)
- `addons/a0d7b954_appdaemon/apps/tongai_apps/reboot_monitor.py` (928 bytes)
- `addons/a0d7b954_appdaemon/apps/tongai_apps/solar_app.py` (8130 bytes)
- `addons/a0d7b954_appdaemon/apps/tongai_apps/solar_work_mode_logger.py` (3334 bytes)
- `addons/a0d7b954_appdaemon/apps/tongai_apps/tado_nest.py` (3148 bytes)
- `addons/a0d7b954_appdaemon/apps/tongai_apps/tado_offset.py` (3346 bytes)
- `addons/a0d7b954_appdaemon/apps/tongai_apps/test_app.py` (31836 bytes)
- `addons/a0d7b954_appdaemon/apps/home_presence_app/home_pres.v233` (54949 bytes)
- `addons/a0d7b954_appdaemon/apps/home_presence_app/home_pres.v234` (63014 bytes)
- `addons/a0d7b954_appdaemon/apps/home_presence_app/home_pres.v241` (68205 bytes)
- `addons/a0d7b954_appdaemon/apps/home_presence_app/home_presence_app.py` (69260 bytes)
- `addons/a0d7b954_nodered/.config.nodes.json` (45298 bytes)
- `addons/a0d7b954_nodered/.config.runtime.json` (39 bytes)
- `addons/a0d7b954_nodered/flows.json` (197876 bytes)
- `addons/a0d7b954_nodered/node-red-contrib-home-assistant-websocket.json` (17 bytes)
- `addons/a0d7b954_nodered/package.json` (195 bytes)
- `addons/a0d7b954_nodered/settings.js` (7663 bytes)
