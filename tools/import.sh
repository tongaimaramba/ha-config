#!/usr/bin/env bash
# import.sh — unpack an export tarball into hosts/<host>/ and rebuild its digests.
#
#     bash tools/import.sh /path/to/ha-config-export-pamba-YYYYMMDD-HHMMSS.tar.gz
#
# Replaces hosts/<host>/{config,storage,integrations,addons,meta} wholesale so that
# files deleted on the box disappear here too (git shows them as deletions).
# Then runs digest.py and a last-line-of-defence secret scan.
set -euo pipefail
TARBALL="${1:?usage: import.sh <tarball>}"
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOST="$(tar -tzf "$TARBALL" | sed -n '1p' | cut -d/ -f1)"   # sed, not head: head + pipefail = SIGPIPE exit
[[ -n "$HOST" ]] || { echo "cannot determine host from tarball" >&2; exit 1; }
DEST="$REPO/hosts/$HOST"
mkdir -p "$DEST"
for d in config storage integrations addons meta; do rm -rf "$DEST/$d"; done
tar -xzf "$TARBALL" -C "$REPO/hosts"
python3 "$REPO/tools/digest.py" "$DEST"
echo "== secret scan (should be empty):"
grep -rInE '(eyJ[A-Za-z0-9_-]{15,}\.|-----BEGIN [A-Z ]*PRIVATE KEY|"(access_token|refresh_token|password|client_secret)"\s*:\s*"[^<"]{4,}"|^[[:space:]]*[a-z_]*(password|token|api_key|secret)[[:space:]]*:[[:space:]]*[^!<[:space:]].{3,})' \
  "$DEST" --include='*.yaml' --include='*.yml' --include='*.json' --include='*.js' --include='*.conf' --include='*.txt' \
  | grep -v '/digest/' | grep -vE '!secret|<redacted' || true
echo "== done: hosts/$HOST refreshed. Review 'git status' then commit."
