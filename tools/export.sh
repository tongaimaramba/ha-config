#!/usr/bin/env bash
# export.sh — snapshot one Home Assistant instance into a redacted tarball.
#
# Run this ON THE HA BOX, in the "Advanced SSH & Web Terminal" (or "Terminal & SSH")
# add-on shell, as root:
#
#     bash export.sh <hostname>            e.g.  bash export.sh pamba
#
# Output: /share/ha-config-export-<hostname>-<timestamp>.tar.gz
# (/share is visible from the Samba add-on and from the File editor, so it is
#  easy to pull off the box and attach.)
#
# What it does:
#   1. Copies an allow-listed set of config files into a staging dir.
#   2. Runs redact.py over the staging dir (secrets values, config-entry data,
#      tokens) BEFORE anything is tarred, so the tarball never holds live secrets.
#   3. Captures Supervisor metadata via the `ha` CLI.
#   4. Writes a manifest of everything included, with sizes, and a list of what
#      was deliberately skipped.
#
# Requirements: bash, tar, python3 (`apk add --no-cache python3` in the add-on
# if missing — it is not persisted across add-on restarts, that's fine).

set -euo pipefail

HOST="${1:-}"
INPLACE_DIR="${2:-}"   # optional: write the redacted tree straight to <INPLACE_DIR>/<HOST>
                        # (e.g. a git checkout's hosts/ dir) instead of building a tarball.
                        # Overwrites that directory's config/storage/integrations/addons/meta.
if [[ -z "$HOST" ]]; then
  echo "usage: bash export.sh <hostname> [in-place-dir]   (pamba | tanga)" >&2
  echo "  no 2nd arg : writes /share/ha-config-export-<host>-<stamp>.tar.gz (default, manual use)" >&2
  echo "  2nd arg    : writes redacted tree straight to <dir>/<host>/ , no tarball, for repo_sync.sh" >&2
  exit 2
fi
if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required for redaction. In the SSH add-on run:  apk add --no-cache python3" >&2
  exit 3
fi

CFG="${HA_CONFIG_DIR:-/homeassistant}"
[[ -d "$CFG" ]] || CFG=/config
ADDON_CFG="${HA_ADDON_CONFIGS_DIR:-/addon_configs}"
STAMP="$(date +%Y%m%d-%H%M%S)"
if [[ -n "$INPLACE_DIR" ]]; then
  WORK=""   # nothing to clean up on this path
  OUT="$INPLACE_DIR/$HOST"
  rm -rf "$OUT"   # full replacement, same as import.sh does for a tarball — deletions show up
else
  WORK="$(mktemp -d /tmp/ha-export.XXXXXX)"
  OUT="$WORK/$HOST"
fi
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REDACT="$SCRIPT_DIR/redact.py"
[[ -f "$REDACT" ]] || { echo "redact.py must sit next to export.sh" >&2; exit 4; }

mkdir -p "$OUT"/{config,storage,integrations,addons,meta}
SKIPPED="$OUT/meta/skipped.txt"
: > "$SKIPPED"

copy() {  # copy <src> <dest-dir>   (silently skip if src missing)
  local src="$1" dst="$2"
  if [[ -e "$src" ]]; then
    mkdir -p "$dst"
    cp -a "$src" "$dst/"
  fi
}

copytree() {  # copytree <srcdir> <dstdir> [find filters...]  — busybox-safe (no cp --parents)
  # Always prunes .git directories: some add-ons (ESPHome Device Builder) git-init
  # their own working dirs, and copying that in verbatim makes git see the copy as
  # an embedded repo (a gitlink) instead of files — the real content silently never
  # gets committed. See if a rogue nested .git ever slips through:
  #   git ls-tree -r HEAD | awk '$1=="160000"'   (should print nothing)
  local src="$1" dst="$2"; shift 2
  ( cd "$src" && find . -type f -not -path '*/.git/*' "$@" -print0 ) | while IFS= read -r -d '' rel; do
    mkdir -p "$dst/$(dirname "$rel")"
    cp -a "$src/$rel" "$dst/$rel"
  done
}

echo "== $HOST: config root ($CFG)"
# --- 1. Root-level YAML and small text files ---------------------------------
# Every *.yaml at the root, plus any other root-level regular file that is small
# (<256K) and not a database/log/binary.  Big or binary things are listed in
# skipped.txt so the omission is visible.
for f in "$CFG"/* "$CFG"/.HA_VERSION; do
  [[ -f "$f" ]] || continue
  name="$(basename "$f")"
  size=$(stat -c %s "$f")
  case "$name" in
    *.db|*.db-shm|*.db-wal|*.log|*.log.*|*.fault|get-pip.py|*.pickle|*.pyc|*.lock)
      echo "$name ($size bytes) — db/log/binary" >> "$SKIPPED"; continue ;;
    *.august.conf|.cloud|.sonoff.json)
      echo "$name ($size bytes) — credential store" >> "$SKIPPED"; continue ;;
  esac
  if (( size > 262144 )); then
    echo "$name ($size bytes) — over 256K" >> "$SKIPPED"; continue
  fi
  cp -a "$f" "$OUT/config/"
done

# --- 2. Root-level directories worth having whole -----------------------------
for d in packages blueprints esphome misc rpi panels scratchpad floorplan_repo espbck downloads; do
  if [[ -d "$CFG/$d" ]]; then
    # text only, skip anything big
    copytree "$CFG/$d" "$OUT/config/$d" -size -256k \
        ! -name '*.pyc' ! -name '*.db*' ! -name '*.log' ! -name '*.bin' ! -name '*.png' ! -name '*.jpg'
  fi
done

# --- 3. custom_components: manifests + hacs.json only ---------------------------
if [[ -d "$CFG/custom_components" ]]; then
  for cc in "$CFG"/custom_components/*/; do
    n="$(basename "$cc")"
    mkdir -p "$OUT/integrations/$n"
    copy "$cc/manifest.json" "$OUT/integrations/$n"
    copy "$cc/hacs.json"     "$OUT/integrations/$n"
    copy "$cc/services.yaml" "$OUT/integrations/$n"
  done
  # sizes, so we know how big the source trees are without carrying them
  du -sk "$CFG"/custom_components/*/ | sort -k2 > "$OUT/integrations/_sizes.txt"
fi

# --- 4. .storage: allow-list ----------------------------------------------------
S="$CFG/.storage"
STORAGE_ALLOW=(
  core.config core.area_registry core.device_registry core.entity_registry
  core.config_entries core.label_registry core.logger core.uuid
  counter timer zone person tag
  input_boolean input_button input_datetime input_number input_select input_text
  lovelace lovelace_dashboards lovelace_resources
  emulated_hue.ids homeassistant.exposed_entities
  hacs.hacs hacs.repositories hacs.critical
  energy camera map panel_iframe assist_pipeline.pipelines onboarding hassio
  repairs.issue_registry
)
for k in "${STORAGE_ALLOW[@]}"; do copy "$S/$k" "$OUT/storage"; done
# pattern-matched families
for f in "$S"/lovelace.* "$S"/frontend.user_data_* "$S"/navimow_pro_* "$S"/esphome.dashboard; do
  [[ -f "$f" ]] && copy "$f" "$OUT/storage"
done
[[ -d "$S/hacs" ]] && copy "$S/hacs" "$OUT/storage"
# everything else in .storage is recorded as skipped (auth, tokens, runtime state)
for f in "$S"/* "$S"/.[!.]*; do
  [[ -e "$f" ]] || continue
  b="$(basename "$f")"
  [[ -e "$OUT/storage/$b" ]] || echo ".storage/$b — not in allow-list" >> "$SKIPPED"
done

# --- 5. Add-on configs --------------------------------------------------------
if [[ -d "$ADDON_CFG" ]]; then
  for a in "$ADDON_CFG"/*/; do
    n="$(basename "$a")"
    case "$n" in
      core_matter_server) echo "addon_configs/$n — fabric keys, excluded" >> "$SKIPPED"; continue ;;
    esac
    mkdir -p "$OUT/addons/$n"
    copytree "$a" "$OUT/addons/$n" -size -512k \
        ! -path './node_modules/*' ! -path './compiled/*' ! -path './logs/*' ! -path './www/*' \
        ! -path './web/*' ! -path './namespaces/*' ! -path './lib/*' \
        ! -name '*.db*' ! -name '*.log' ! -name '*.pyc' ! -name 'flows_cred.json' \
        ! -name '*.backup' ! -name '.config.users.json' ! -name 'package-lock.json'
  done
fi

# --- 6. Supervisor / core metadata via `ha` CLI ----------------------------------
sup_api() {  # sup_api <path> — GET Supervisor REST API <path>, same JSON shape as `ha ... --raw-json`
  local path="$1"
  SUP_TOKEN="${SUPERVISOR_TOKEN:-${HASSIO_TOKEN:-}}" python3 - "$path" <<'PYEOF'
import os, sys, urllib.request
path = sys.argv[1]
token = os.environ.get("SUP_TOKEN")
if not token:
    sys.exit("no SUPERVISOR_TOKEN/HASSIO_TOKEN in environment")
req = urllib.request.Request(f"http://supervisor{path}", headers={"Authorization": f"Bearer {token}"})
with urllib.request.urlopen(req, timeout=10) as r:
    sys.stdout.write(r.read().decode())
PYEOF
}

if command -v ha >/dev/null 2>&1; then
  ha addons --raw-json        > "$OUT/meta/ha-addons.json"     2>/dev/null || true
  ha supervisor info --raw-json > "$OUT/meta/ha-supervisor.json" 2>/dev/null || true
  ha core info --raw-json     > "$OUT/meta/ha-core.json"       2>/dev/null || true
  ha os info --raw-json       > "$OUT/meta/ha-os.json"         2>/dev/null || true
  ha host info --raw-json     > "$OUT/meta/ha-host.json"       2>/dev/null || true
  ha network info --raw-json  > "$OUT/meta/ha-network.json"    2>/dev/null || true
elif [[ -n "${SUPERVISOR_TOKEN:-}${HASSIO_TOKEN:-}" ]]; then
  # No `ha` CLI here (e.g. running from AppDaemon's container), but a Supervisor
  # token is present — the CLI is just a thin wrapper over this same REST API,
  # so hit it directly instead of shelling out.
  echo "ha CLI not available — using Supervisor REST API instead (token present)" >> "$SKIPPED"
  fetch_meta() {  # fetch_meta <api-path> <out-file> — on failure, log it and leave no
                  # (or no new) file rather than a 0-byte one that could clobber /
                  # conflict with a good snapshot from an earlier successful export.
    local path="$1" out="$2"
    if ! sup_api "$path" > "$out.tmp" 2>>"$SKIPPED"; then
      echo "Supervisor API GET $path failed" >> "$SKIPPED"
      rm -f "$out.tmp"
      return
    fi
    mv "$out.tmp" "$out"
  }
  fetch_meta /addons          "$OUT/meta/ha-addons.json"
  fetch_meta /supervisor/info "$OUT/meta/ha-supervisor.json"
  fetch_meta /core/info       "$OUT/meta/ha-core.json"
  fetch_meta /os/info         "$OUT/meta/ha-os.json"
  fetch_meta /host/info       "$OUT/meta/ha-host.json"
  fetch_meta /network/info    "$OUT/meta/ha-network.json"
else
  echo "ha CLI not available and no SUPERVISOR_TOKEN/HASSIO_TOKEN in environment — meta/*.json not captured" >> "$SKIPPED"
fi
{
  echo "host: $HOST"; echo "exported_at: $(date -Iseconds)"; echo "config_dir: $CFG"
  echo "ha_version: $(cat "$CFG/.HA_VERSION" 2>/dev/null || echo unknown)"
  echo "uname: $(uname -a)"
} > "$OUT/meta/export-info.yaml"

# --- 7. Redact in place, then manifest ---------------------------------------
echo "== redacting"
python3 "$REDACT" "$OUT" | tee "$OUT/meta/redaction-report.txt"

( cd "$OUT" && find . -type f -exec stat -c '%s	%n' {} + | sort -k2 ) > "$OUT/meta/manifest.tsv"

if [[ -n "$INPLACE_DIR" ]]; then
  echo
  echo "== done: wrote redacted tree straight to $OUT (no tarball)"
  echo "   review $OUT/meta/redaction-report.txt and meta/skipped.txt before committing/pushing."
else
  OUTDIR="${HA_EXPORT_DIR:-/share}"
  [[ -d "$OUTDIR" ]] || OUTDIR="$CFG"
  TARBALL="$OUTDIR/ha-config-export-$HOST-$STAMP.tar.gz"
  tar -C "$WORK" -czf "$TARBALL" "$HOST"
  rm -rf "$WORK"

  echo
  echo "== done: $TARBALL ($(du -h "$TARBALL" | cut -f1))"
  echo "   files: $(wc -l < <(tar -tzf "$TARBALL"))"
  echo "   review meta/redaction-report.txt and meta/skipped.txt inside before sharing."
fi
