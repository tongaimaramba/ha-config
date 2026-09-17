"""ha_config_sync.py — AppDaemon app that runs repo_sync.sh when a Lovelace button
fires an event, and reports success/failure back into Home Assistant so pressing
the button actually tells you something (rather than silently doing nothing if it
fails, which a background subprocess otherwise would).

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
   practice; listen_event is the well-supported one):

     ha_config_sync_pamba:
       alias: "Sync pamba config snapshot"
       sequence:
         - event: ha_config_sync
           event_data: {host: pamba}

     ha_config_sync_tanga:
       alias: "Sync tanga config snapshot"
       sequence:
         - event: ha_config_sync
           event_data: {host: tanga}

4. A Lovelace button card per host, tap_action calling script.ha_config_sync_pamba
   / _tanga (see the lovelace_card.yaml file next to this one).

IMPORTANT — this only works if the AppDaemon add-on's container can actually see
the box's real filesystem at /share (and /homeassistant, which export.sh needs to
read the live config). Check: Settings -> Add-ons -> AppDaemon -> Configuration,
look for a folder/map option that includes "share" (and ideally "homeassistant_config"
or "addon_configs") with read/write access, and enable it if it's off, then restart
the add-on. If those folders aren't mapped in, this app will log a clear error
(and raise a persistent_notification) rather than fail silently — check AppDaemon's
own log (Settings -> Add-ons -> AppDaemon -> Log) if the button doesn't do anything.
"""
import subprocess
import traceback

import appdaemon.plugins.hass.hassapi as hass

DEFAULT_REPO_DIR = "/share/ha-config-repo"
VALID_HOSTS = {"pamba", "tanga"}


class HAConfigSync(hass.Hass):
    def initialize(self):
        self.repo_dir = self.args.get("repo_dir", DEFAULT_REPO_DIR)
        self.listen_event(self.on_sync_event, "ha_config_sync")
        self.log(f"ha_config_sync ready, watching for 'ha_config_sync' events (repo_dir={self.repo_dir})")

    def on_sync_event(self, event_name, data, kwargs):
        host = (data or {}).get("host", "").strip()
        if host not in VALID_HOSTS:
            self._notify_error(f"ha_config_sync: bad or missing host in event data: {data!r}")
            return

        self.log(f"ha_config_sync: starting sync for {host}")
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
            self._notify_error(
                f"ha_config_sync: {script} not found. Is {self.repo_dir} mounted into the "
                f"AppDaemon container? Check the add-on's folder mappings (see this app's docstring)."
            )
            return
        except subprocess.TimeoutExpired:
            self._notify_error(f"ha_config_sync: timed out after 5 minutes syncing {host}")
            return
        except Exception:
            self._notify_error(f"ha_config_sync: unexpected error:\n{traceback.format_exc()}")
            return

        # Log everything either way — this is what to check first if something looks off.
        self.log(f"ha_config_sync[{host}] stdout:\n{result.stdout}")
        if result.stderr:
            self.log(f"ha_config_sync[{host}] stderr:\n{result.stderr}", level="WARNING")

        if result.returncode != 0:
            self._notify_error(
                f"ha_config_sync: {host} sync FAILED (exit {result.returncode}). "
                f"Check the AppDaemon log for details.\n\n{result.stdout[-500:]}"
            )
            return

        if "nothing to commit" in result.stdout:
            self._notify_ok(f"ha_config_sync: {host} snapshot unchanged — nothing new to push.")
        else:
            self._notify_ok(
                f"ha_config_sync: {host} snapshot committed locally on the box. "
                f"Run `bash tools/pull_and_push.sh {host}` on your Mac to publish it to GitHub."
            )

    def _notify_ok(self, message):
        self.log(message)
        self.call_service("persistent_notification/create", title="HA config sync", message=message,
                           notification_id="ha_config_sync")

    def _notify_error(self, message):
        self.error(message)
        self.call_service("persistent_notification/create", title="HA config sync FAILED", message=message,
                           notification_id="ha_config_sync")
