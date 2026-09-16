# ha-config — redacted snapshots of both Home Assistant instances

Visibility repo for two Home Assistant OS boxes, so that config drift between them
can be diffed, audited and (eventually) reconciled. It is **not** a deployable
config: secrets are scrubbed, databases and integration source trees are left out.

| host    | hardware              | arch    | role                                |
|---------|-----------------------|---------|-------------------------------------|
| `pamba` | Raspberry Pi 4        | armv7   | current production (to be retired)  |
| `tanga` | Raspberry Pi 5        | aarch64 | migration target → future production|

## Layout

```
hosts/<host>/
  config/         *.yaml at the config root, packages/, blueprints/, esphome/*.yaml, misc small text files
  storage/        allow-listed .storage files (registries, helpers, dashboards, HACS state) — redacted
  integrations/   custom_components/*/manifest.json + hacs.json + services.yaml only, plus _sizes.txt
  addons/         /addon_configs/* text files (AppDaemon apps, Node-RED flows.json, …) — redacted
  meta/           ha CLI output (addons, supervisor, core, os, host, network), manifest, skipped list, redaction report
  digest/         GENERATED summaries sized for project knowledge — see below
tools/
  export.sh       run ON the box → /share/ha-config-export-<host>-<stamp>.tar.gz (redacted before tar)
  redact.py       stdlib-only scrubber used by export.sh (also usable standalone)
  import.sh       run in the repo → unpack tarball into hosts/<host>/, rebuild digest/, secret-scan
  digest.py       builds hosts/<host>/digest/*
```

Both hosts use the identical layout, so `diff -r hosts/pamba hosts/tanga` (or
`diff hosts/pamba/digest/integrations.md hosts/tanga/digest/integrations.md`)
is the drift report.

## Refreshing a snapshot

On the box, in the **Advanced SSH & Web Terminal** add-on shell:

```sh
apk add --no-cache python3        # only if `python3` is missing; not persisted, harmless
tar xzf /share/ha-config-tools.tar.gz -C /tmp    # or: git clone this repo into /tmp
bash /tmp/tools/export.sh pamba   # or tanga
```

Copy the tarball from `/share` (Samba, or the File editor) and then in this repo:

```sh
bash tools/import.sh ~/Downloads/ha-config-export-pamba-YYYYMMDD-HHMMSS.tar.gz
git add -A && git commit -m "pamba: snapshot YYYY-MM-DD"
```

`import.sh` replaces `hosts/<host>/{config,storage,integrations,addons,meta}`
wholesale, so files removed on the box show up as deletions in git.

## What is redacted vs excluded

**Redacted in place (keys kept, values → `<redacted>`)**

- `secrets.yaml`, `navimow_secrets.yaml`, any `*secrets*.yaml`
- `.storage/core.config_entries`: every entry keeps `entry_id / domain / title / source /
  version / unique_id / disabled_by / pref_*`; `data` and `options` become
  `{"_redacted_keys": [...]}` so you can still see *what* is configured
- any `password / token / secret / api_key / client_secret / webhook_id / psk / …` value in
  YAML, JSON or JS; ESPHome `key:`; JWTs; `Bearer …` strings
- known limitation: a secret written as a YAML block scalar (`password: >` + indented lines)
  is not caught — none were seen in the inventories, but check `meta/redaction-report.txt`

**Excluded entirely (listed in `meta/skipped.txt` per snapshot)**

- `.storage/auth*`, `http.auth`, `application_credentials`, `*_tokens`, `mobile_app`,
  `alexa_auth`, `.cloud`, `.sonoff.json`, `*.august.conf`, `androidtv_*` keys/certs, `.edgeos`,
  `smartthings`, `volvo_cars.*`, `sonoff`, `backup`, `bluetooth.*`, `core.restore_state`,
  `trace.saved_traces`, `hacs.data`, `nest.event_media`
- recorder DB (`home-assistant_v2.db*`), `zigbee.db*`, all logs, `get-pip.py`
- `custom_components/*` source (manifests only), `www/`, `nest/`, `llama/`, `deps/`
- `/addon_configs/core_matter_server` (fabric keys), Node-RED `flows_cred.json`,
  `.config.users.json`, `node_modules/`, `*.backup`

## Project-knowledge sync

The raw registries are several MB each (`core.entity_registry` ≈ 2.5–2.7 MB,
`hacs.repositories` ≈ 2.7–2.9 MB per host) and the knowledge base is capped at 2 MB
total, so syncing all of `hosts/*/config/` doesn't fit — with real data from both
boxes that alone came to ~1.7 MB before `digest/` is even added, mostly ESPHome
device-firmware YAML and old `espbck/` backups that don't help with HA-level
visibility. The filter that fits (~1.4 MB measured against the 2026-09-16 snapshots,
leaving headroom):

```
/README.md
/hosts/pamba/digest/
/hosts/pamba/config/*.yaml
/hosts/tanga/digest/
/hosts/tanga/config/*.yaml
```

i.e. `digest/` in full (that's the point of it) plus only the *top-level* YAML files
in `config/` (`configuration.yaml`, `automations.yaml`, `scripts.yaml`, `groups.yaml`,
etc.) — not `esphome/`, `espbck/`, `blueprints/`, `misc/`, `floorplan_repo/`, `rpi/`,
`panels/`. Everything excluded from the sync still lives in the repo for on-demand
reading; only the knowledge-base copy is trimmed.

## Known context (kept here so it travels with the repo)

- `navimow_pro` (github.com/ilguala/navimow_pro, via HACS custom repo) runs on pamba only;
  entity `lawn_mower.oppy`. Zone IDs: Garden B=3, D=6, C1=14, C2=16, C3=17; "Zone 1"=12 is
  an unused connector polygon. The mirror at github.com/tongaimaramba/navmow is the
  integration's *source*, not HA config.
- tanga has an orphan `navimow_secrets.yaml` at its config root with the integration not
  installed — origin unknown; inspect before reuse.
- pamba Supervisor reports `supported: false` (armv7); tanga is fully supported.
