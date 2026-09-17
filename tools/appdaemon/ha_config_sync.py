"""ha_config_sync.py — AppDaemon app that runs repo_sync.sh when a Lovelace button
fires an event, and reports status both as a persistent_notification AND as a
sensor entity (sensor.ha_config_sync_<host>) you can put straight on the
dashboard — so pressing the button gives immediate, visible feedback without
having to open the AppDaemon log.

Setup (see repo README.md "Button + one-command sync" section for the full
one-time checklist):

1. This file goes in your AppDaemon apps directory, e.g. next to your other
   tongai_apps/*.py — wherever appdaemon.yaml's app_dir points.
2. Add to apps.yaml:

     ha_config_sync:
       module: ha_config_sync
       class: HAConfigSync
       repo_dir: /share/ha-config-repo    # only needs to be right if not the default

3. Add two small HA scripts (scripts.yaml) that just fire the event — this is the
   AppDaemon-recommended pattern (register_service turned out to be flaky in
   practice; listen_event is the well-supported one). Only add the ONE entry
   for this box's own host — see scripts_snippet.yaml.
4. A Lovelace button + status row per host (see lovelace_card.yaml) — again,
   only the rows for this box's own host, since pamba and tanga are separate
   HA instances and each can only see its own local entities.

STATUS ENTITY: sensor.ha_config_sync_<host> is created/updated by this app
directly (AppDaemon's set_state — no separate integration needed). Its
`state` is one of: idle | running | committed | unchanged | error. Its
`message` attribute is a short human-readable status line meant to be shown
on the dashboard via an "attribute" row (see lovelace_card.yaml). It updates
the moment the button is pressed (state -> running) rather than only once the
~40-second sync finishes, so a press always visibly registers immediately.

IMPORTANT — this only works if the AppDaemon add-on's container can actually see
the box's real filesystem at /share (and /homeassistant, which export.sh needs to
read the live config), and has `git` available (add it under the add-on's own
"System packages" config field if `git: command not found` shows up in the log).
"""
import subprocess
import traceback
from datetime import datetime

import appdaemon.plugins.hass.hassapi as hass

DEFAULT_REPO_DIR = "/share/ha-config-repo"
VALID_HOSTS = {"pamba", "tanga"}

# icon per status, shown on the dashboard row via the sensor's `icon` attribute
_ICONS = {
    "idle": "mdi:cloud-sync-outline",
    "running": "mdi:cloud-sync",
    "committed": "mdi:cloud-check-outline",
    "unchanged": "mdi:cloud-check",
    "error": "mdi:cloud-alert",
}


class HAConfigSync(hass.Hass):
    def initialize(self):
        self.repo_dir = self.args.get("repo_dir", DEFAULT_REPO_DIR)
        self.listen_event(self.on_sync_event, "ha_config_sync")
        # Create each host's status entity right away (idle), so the dashboard
        # row shows something sensible immediately after an AppDaemon restart
        # instead of "unavailable" until the first sync ever runs.
        for host in VALID_HOSTS:
            if self.get_state(f"sensor.ha_config_sync_{host}") is None:
                self._set_status(host, "idle", "Never run since AppDaemon last started")
        self.log(f"ha_config_sync ready, watching for 'ha_config_sync' events (repo_dir={self.repo_dir})")

    def on_sync_event(self, event_name, data, kwargs):
        host = (data or {}).get("host", "").strip()
        if host not in VALID_HOSTS:
            self._notify(None, "HA config sync FAILED", f"bad or missing host in event data: {data!r}")
            return

        self.log(f"ha_config_sync: starting sync for {host}")
        # Immediate feedback the moment the button is pressed — the sync itself
        # takes ~40s, so without this the dashboard shows nothing changing for
        # a while and it's unclear whether the press even registered.
        self._set_status(host, "running", "Sync in progress…")

        script = f"{self.repo_dir}/tools/repo_sync.sh"
        try:
            result = subprocess.run(
                ["bash", script, host],
                cwd=self.repo_dir,
                capture_output=True,
                text=True,
                timeout=300,
            )
        except FileNotFoundError:
            self._fail(host, f"{script} not found. Is {self.repo_dir} mounted into the "
                              f"AppDaemon container? Check the add-on's folder mappings.")
            return
        except subprocess.TimeoutExpired:
            self._fail(host, "timed out after 5 minutes")
            return
        except Exception:
            self._fail(host, f"unexpected error:\n{traceback.format_exc()}")
            return

        # Log everything either way — still useful for anything longer than fits
        # in the dashboard's status message.
        self.log(f"ha_config_sync[{host}] stdout:\n{result.stdout}")
        if result.stderr:
            self.log(f"ha_config_sync[{host}] stderr:\n{result.stderr}", level="WARNING")

        if result.returncode != 0:
            self._fail(host, f"exit {result.returncode} — check AppDaemon log.\n\n{result.stdout[-500:]}")
            return

        if "nothing to commit" in result.stdout:
            self._succeed(host, "unchanged", "No changes since last snapshot.")
        else:
            self._succeed(host, "committed",
                          f"Committed locally. Run: hasync {host}")

    def _set_status(self, host, state, message):
        self.set_state(
            f"sensor.ha_config_sync_{host}",
            state=state,
            attributes={
                "friendly_name": f"{host} config sync",
                "message": message,
                "last_updated_local": datetime.now().isoformat(timespec="seconds"),
                "icon": _ICONS.get(state, "mdi:cloud-sync-outline"),
            },
        )

    def _succeed(self, host, state, message):
        self.log(f"ha_config_sync: {host} {state}: {message}")
        self._set_status(host, state, message)
        self._notify(host, "HA config sync", message)

    def _fail(self, host, message):
        self.error(f"ha_config_sync: {host} FAILED: {message}")
        self._set_status(host, "error", message)
        self._notify(host, "HA config sync FAILED", message)

    def _notify(self, host, title, message):
        # One notification_id PER HOST — with a single shared id, pamba's and
        # tanga's notifications would overwrite each other if both ran close
        # together.
        notification_id = f"ha_config_sync_{host}" if host else "ha_config_sync"
        full_message = f"{host}: {message}" if host else message
        self.call_service("persistent_notification/create", title=title, message=full_message,
                           notification_id=notification_id)
