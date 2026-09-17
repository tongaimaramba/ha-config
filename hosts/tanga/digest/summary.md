# tanga — snapshot summary

```
host: tanga
exported_at: 2026-09-17T14:55:53+01:00
config_dir: /homeassistant
ha_version: 2025.11.1
uname: Linux a0d7b954-appdaemon 6.6.74-haos-raspi #1 SMP PREEMPT Mon Apr 14 16:31:30 UTC 2025 aarch64 GNU/Linux
```

- config entries: 140  (custom components on disk: 29)
- devices: 421
- entities: 2945 across 56 platforms
- areas: 34

## entities per platform

| platform | entities |
|---|---|
| ibeacon | 875 |
| mobile_app | 337 |
| hue | 313 |
| hassio | 137 |
| hacs | 134 |
| accuweather | 132 |
| bermuda | 124 |
| esphome | 103 |
| garmin_connect | 87 |
| volvo_cars | 70 |
| mqtt | 65 |
| lightwave2 | 61 |
| automation | 60 |
| growatt_server_api | 37 |
| input_boolean | 36 |
| aarlo | 31 |
| script | 30 |
| nut | 27 |
| ble_monitor | 27 |
| group | 24 |
| dyson_local | 23 |
| tile | 22 |
| input_text | 19 |
| input_number | 15 |
| sonoff | 15 |
| roomba | 15 |
| input_select | 12 |
| nest | 11 |
| tag | 11 |
| sun | 10 |
| private_ble_device | 10 |
| nmap_tracker | 7 |
| input_datetime | 6 |
| input_button | 6 |
| person | 5 |
| eventsensor | 5 |
| rpi_gpio | 5 |
| places | 5 |
| backup | 5 |
| zone | 3 |
| template | 3 |
| speedtestdotnet | 3 |
| dyson | 2 |
| androidtv_remote | 2 |
| energy | 2 |
| tod | 2 |
| tuya | 2 |
| updater | 1 |
| attributes | 1 |
| rpi_power | 1 |
| momentary | 1 |
| webostv | 1 |
| cert_expiry | 1 |
| counter | 1 |
| file | 1 |
| ollama | 1 |

## files deliberately not exported

```
home-assistant.log.1 (5354857 bytes) — db/log/binary
home-assistant.log.fault (0 bytes) — db/log/binary
home-assistant.log.old (535979 bytes) — db/log/binary
home-assistant_v2.db (16729014272 bytes) — db/log/binary
home-assistant_v2.db-shm (32768 bytes) — db/log/binary
home-assistant_v2.db-wal (4499072 bytes) — db/log/binary
.storage/alexa — not in allow-list
.storage/alexa_auth — not in allow-list
.storage/androidtv_adbkey — not in allow-list
.storage/androidtv_adbkey.pub — not in allow-list
.storage/androidtv_remote_cert.pem — not in allow-list
.storage/androidtv_remote_key.pem — not in allow-list
.storage/application_credentials — not in allow-list
.storage/auth — not in allow-list
.storage/auth.session — not in allow-list
.storage/auth_provider.homeassistant — not in allow-list
.storage/backup — not in allow-list
.storage/bluetooth.passive_update_processor — not in allow-list
.storage/bluetooth.remote_scanners — not in allow-list
.storage/core.restore_state — not in allow-list
.storage/esphome.01JN651AFQ9YV7DYKM67HTC3EQ — not in allow-list
.storage/esphome.01JWP5KZY9YY4KJ5EPJG875S89 — not in allow-list
.storage/esphome.01JYGCJEAPF1CNTJKS33MV7W2C — not in allow-list
.storage/esphome.01JYTZKYH4DB11ZFDBC0MMGP3T — not in allow-list
.storage/esphome.01K9SMD0N2XK81TW4JY7E2A5CH — not in allow-list
.storage/esphome.01K9ZCAWGKG7HZTP4QA157BYAK — not in allow-list
.storage/esphome.01KAQ1SN0PBA2SKVC9C5E079N4 — not in allow-list
.storage/esphome.01KBJ34A95VAG6DK4BT5538TWT — not in allow-list
.storage/esphome.39a67c9db005c4430e20ccafb0012f4c — not in allow-list
.storage/esphome.5f3decfc9356c5b361239eabda83a811 — not in allow-list
.storage/esphome.9986fbb44afda2ba99006372152f47da — not in allow-list
.storage/esphome.e1e592d082198849a059824bcde4b588 — not in allow-list
.storage/esphome.e295d2aea7b3dc61103352d812f7808d — not in allow-list
.storage/esphome.f75455c1399f06b3538717e1df7b35b9 — not in allow-list
.storage/hacs.data — not in allow-list
.storage/http — not in allow-list
.storage/http.auth — not in allow-list
.storage/mobile_app — not in allow-list
.storage/nest.event_media — not in allow-list
.storage/smartthings — not in allow-list
.storage/sonoff — not in allow-list
.storage/trace.saved_traces — not in allow-list
.storage/volvo_cars.YV1XZEHR5T2686253 — not in allow-list
.storage/volvo_cars.data — not in allow-list
.storage/zz.tongai_test_old — not in allow-list
.storage/zzz_old - dash list — not in allow-list
.storage/.edgeos — not in allow-list
ha CLI not available — using Supervisor REST API instead (token present)
Traceback (most recent call last):
  File "<stdin>", line 7, in <module>
  File "/usr/local/share/uv/python/cpython-3.13.15-linux-aarch64-gnu/lib/python3.13/urllib/request.py", line 189, in urlopen
    return opener.open(url, data, timeout)
           ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/share/uv/python/cpython-3.13.15-linux-aarch64-gnu/lib/python3.13/urllib/request.py", line 495, in open
    response = meth(req, response)
  File "/usr/local/share/uv/python/cpython-3.13.15-linux-aarch64-gnu/lib/python3.13/urllib/request.py", line 604, in http_response
    response = self.parent.error(
        'http', request, response, code, msg, hdrs)
  File "/usr/local/share/uv/python/cpython-3.13.15-linux-aarch64-gnu/lib/python3.13/urllib/request.py", line 533, in error
    return self._call_chain(*args)
           ~~~~~~~~~~~~~~~~^^^^^^^
  File "/usr/local/share/uv/python/cpython-3.13.15-linux-aarch64-gnu/lib/python3.13/urllib/request.py", line 466, in _call_chain
    result = func(*args)
  File "/usr/local/share/uv/python/cpython-3.13.15-linux-aarch64-gnu/lib/python3.13/urllib/request.py", line 613, in http_error_default
    raise HTTPError(req.full_url, code, msg, hdrs, fp)
urllib.error.HTTPError: HTTP Error 403: Forbidden
Supervisor API GET /addons failed
Traceback (most recent call last):
  File "<stdin>", line 7, in <module>
  File "/usr/local/share/uv/python/cpython-3.13.15-linux-aarch64-gnu/lib/python3.13/urllib/request.py", line 189, in urlopen
    return opener.open(url, data, timeout)
           ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/share/uv/python/cpython-3.13.15-linux-aarch64-gnu/lib/python3.13/urllib/request.py", line 495, in open
    response = meth(req, response)
  File "/usr/local/share/uv/python/cpython-3.13.15-linux-aarch64-gnu/lib/python3.13/urllib/request.py", line 604, in http_response
    response = self.parent.error(
        'http', request, response, code, msg, hdrs)
  File "/usr/local/share/uv/python/cpython-3.13.15-linux-aarch64-gnu/lib/python3.13/urllib/request.py", line 533, in error
    return self._call_chain(*args)
           ~~~~~~~~~~~~~~~~^^^^^^^
  File "/usr/local/share/uv/python/cpython-3.13.15-linux-aarch64-gnu/lib/python3.13/urllib/request.py", line 466, in _call_chain
    result = func(*args)
  File "/usr/local/share/uv/python/cpython-3.13.15-linux-aarch64-gnu/lib/python3.13/urllib/request.py", line 613, in http_error_default
    raise HTTPError(req.full_url, code, msg, hdrs, fp)
urllib.error.HTTPError: HTTP Error 403: Forbidden
Supervisor API GET /supervisor/info failed
Traceback (most recent call last):
  File "<stdin>", line 7, in <module>
  File "/usr/local/share/uv/python/cpython-3.13.15-linux-aarch64-gnu/lib/python3.13/urllib/request.py", line 189, in urlopen
    return opener.open(url, data, timeout)
           ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/share/uv/python/cpython-3.13.15-linux-aarch64-gnu/lib/python3.13/urllib/request.py", line 495, in open
    response = meth(req, response)
  File "/usr/local/share/uv/python/cpython-3.13.15-linux-aarch64-gnu/lib/python3.13/urllib/request.py", line 604, in http_response
    response = self.parent.error(
        'http', request, response, code, msg, hdrs)
  File "/usr/local/share/uv/python/cpython-3.13.15-linux-aarch64-gnu/lib/python3.13/urllib/request.py", line 533, in error
    return self._call_chain(*args)
           ~~~~~~~~~~~~~~~~^^^^^^^
  File "/usr/local/share/uv/python/cpython-3.13.15-linux-aarch64-gnu/lib/python3.13/urllib/request.py", line 466, in _call_chain
    result = func(*args)
  File "/usr/local/share/uv/python/cpython-3.13.15-linux-aarch64-gnu/lib/python3.13/urllib/request.py", line 613, in http_error_default
    raise HTTPError(req.full_url, code, msg, hdrs, fp)
urllib.error.HTTPError: HTTP Error 403: Forbidden
Supervisor API GET /core/info failed
Traceback (most recent call last):
  File "<stdin>", line 7, in <module>
  File "/usr/local/share/uv/python/cpython-3.13.15-linux-aarch64-gnu/lib/python3.13/urllib/request.py", line 189, in urlopen
    return opener.open(url, data, timeout)
           ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/share/uv/python/cpython-3.13.15-linux-aarch64-gnu/lib/python3.13/urllib/request.py", line 495, in open
    response = meth(req, response)
  File "/usr/local/share/uv/python/cpython-3.13.15-linux-aarch64-gnu/lib/python3.13/urllib/request.py", line 604, in http_response
    response = self.parent.error(
        'http', request, response, code, msg, hdrs)
  File "/usr/local/share/uv/python/cpython-3.13.15-linux-aarch64-gnu/lib/python3.13/urllib/request.py", line 533, in error
    return self._call_chain(*args)
           ~~~~~~~~~~~~~~~~^^^^^^^
  File "/usr/local/share/uv/python/cpython-3.13.15-linux-aarch64-gnu/lib/python3.13/urllib/request.py", line 466, in _call_chain
    result = func(*args)
  File "/usr/local/share/uv/python/cpython-3.13.15-linux-aarch64-gnu/lib/python3.13/urllib/request.py", line 613, in http_error_default
    raise HTTPError(req.full_url, code, msg, hdrs, fp)
urllib.error.HTTPError: HTTP Error 403: Forbidden
Supervisor API GET /os/info failed
Traceback (most recent call last):
  File "<stdin>", line 7, in <module>
  File "/usr/local/share/uv/python/cpython-3.13.15-linux-aarch64-gnu/lib/python3.13/urllib/request.py", line 189, in urlopen
    return opener.open(url, data, timeout)
           ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/share/uv/python/cpython-3.13.15-linux-aarch64-gnu/lib/python3.13/urllib/request.py", line 495, in open
    response = meth(req, response)
  File "/usr/local/share/uv/python/cpython-3.13.15-linux-aarch64-gnu/lib/python3.13/urllib/request.py", line 604, in http_response
    response = self.parent.error(
        'http', request, response, code, msg, hdrs)
  File "/usr/local/share/uv/python/cpython-3.13.15-linux-aarch64-gnu/lib/python3.13/urllib/request.py", line 533, in error
    return self._call_chain(*args)
           ~~~~~~~~~~~~~~~~^^^^^^^
  File "/usr/local/share/uv/python/cpython-3.13.15-linux-aarch64-gnu/lib/python3.13/urllib/request.py", line 466, in _call_chain
    result = func(*args)
  File "/usr/local/share/uv/python/cpython-3.13.15-linux-aarch64-gnu/lib/python3.13/urllib/request.py", line 613, in http_error_default
    raise HTTPError(req.full_url, code, msg, hdrs, fp)
urllib.error.HTTPError: HTTP Error 403: Forbidden
Supervisor API GET /host/info failed
Traceback (most recent call last):
  File "<stdin>", line 7, in <module>
  File "/usr/local/share/uv/python/cpython-3.13.15-linux-aarch64-gnu/lib/python3.13/urllib/request.py", line 189, in urlopen
    return opener.open(url, data, timeout)
           ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/share/uv/python/cpython-3.13.15-linux-aarch64-gnu/lib/python3.13/urllib/request.py", line 495, in open
    response = meth(req, response)
  File "/usr/local/share/uv/python/cpython-3.13.15-linux-aarch64-gnu/lib/python3.13/urllib/request.py", line 604, in http_response
    response = self.parent.error(
        'http', request, response, code, msg, hdrs)
  File "/usr/local/share/uv/python/cpython-3.13.15-linux-aarch64-gnu/lib/python3.13/urllib/request.py", line 533, in error
    return self._call_chain(*args)
           ~~~~~~~~~~~~~~~~^^^^^^^
  File "/usr/local/share/uv/python/cpython-3.13.15-linux-aarch64-gnu/lib/python3.13/urllib/request.py", line 466, in _call_chain
    result = func(*args)
  File "/usr/local/share/uv/python/cpython-3.13.15-linux-aarch64-gnu/lib/python3.13/urllib/request.py", line 613, in http_error_default
    raise HTTPError(req.full_url, code, msg, hdrs, fp)
urllib.error.HTTPError: HTTP Error 403: Forbidden
Supervisor API GET /network/info failed
```

## digests written

- integrations.md
- entities.tsv
- devices.tsv
- areas.md
- helpers.md
- automations.md
- scripts.md
- yaml-files.md
- dashboards.md
- exposure.md
- addons.md
- hacs.md
- summary.md
