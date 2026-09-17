#!/usr/bin/env bash
# repo_sync.sh — runs ON THE BOX. Refreshes this host's snapshot straight into a
# local git checkout, redacts, digests, and commits LOCALLY. Never touches GitHub
# and never needs a GitHub credential on this box — see tools/pull_and_push.sh,
# which runs on your Mac and fetches this commit over the SSH access you already
# have, then pushes it to GitHub from there.
#
# One-time setup on the box (see README.md "Button + one-command sync"):
#   apk add --no-cache git python3
#   mkdir -p /share/ha-config-repo && cd /share/ha-config-repo && git init -b main
#   git config receive.denyCurrentBranch updateInstead   # lets a remote push update the checkout
#   # then copy tools/ in once (Samba, or scp from your Mac) and commit it:
#   git add -A && git commit -m "seed tools"
#
# Called two ways:
#   1. By hand over SSH:  bash /share/ha-config-repo/tools/repo_sync.sh pamba
#   2. By the AppDaemon app (ha_config_sync.py) when the Lovelace button fires.

set -euo pipefail

HOST="${1:-}"
if [[ -z "$HOST" ]]; then
  echo "usage: bash repo_sync.sh <hostname>   (pamba | tanga)" >&2
  exit 2
fi

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ ! -d "$REPO/.git" ]]; then
  echo "$REPO doesn't look like a git checkout — see the one-time setup in this script's header" >&2
  exit 3
fi

cd "$REPO"

echo "== exporting $HOST straight into the checkout (no tarball)"
bash "$REPO/tools/export.sh" "$HOST" "$REPO/hosts"

echo "== building digest/"
python3 "$REPO/tools/digest.py" "$REPO/hosts/$HOST"

echo "== secret scan (should be empty) =="
grep -rInE '(eyJ[A-Za-z0-9_-]{15,}\.|-----BEGIN [A-Z ]*PRIVATE KEY|"(access_token|refresh_token|password|client_secret)"[[:space:]]*:[[:space:]]*"[^<"]{4,}"|^[[:space:]]*[a-z_]*(password|token|api_key|secret)[[:space:]]*:[[:space:]]*[^!<[:space:]].{3,})' \
  "$REPO/hosts/$HOST" --include='*.yaml' --include='*.yml' --include='*.json' --include='*.js' --include='*.conf' --include='*.txt' --include='*.py' \
  2>/dev/null | grep -v '/digest/' | grep -vE '!secret|<redacted' || true

git add "hosts/$HOST"
if git diff --cached --quiet; then
  echo "== no changes since last snapshot of $HOST — nothing to commit"
  exit 0
fi
git commit -q -m "auto: $HOST snapshot $(date -Iseconds) (via repo_sync.sh, uncommitted push)"

echo
echo "== committed locally on this box. NOT pushed to GitHub (this box has no GitHub"
echo "   credential, by design). From your Mac, run:"
echo "     bash tools/pull_and_push.sh $HOST"
