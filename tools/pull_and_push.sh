#!/usr/bin/env bash
# pull_and_push.sh — run THIS ON YOUR MAC, from inside your local ha-config clone,
# after pressing the Lovelace sync button (or running repo_sync.sh by hand on a box).
#
# It fetches the commit repo_sync.sh made LOCALLY on the box, over the same SSH
# access you already use to reach it (no GitHub credential ever touches the box),
# merges it, and pushes to GitHub — the one command that finishes the job.
#
#     bash tools/pull_and_push.sh pamba
#     bash tools/pull_and_push.sh tanga
#
# One-time config (edit the two lines below, or export HA_PAMBA_SSH / HA_TANGA_SSH
# in your shell profile instead): the SSH target for each box's SSH add-on, as you'd
# pass to `ssh`. Find the port in the add-on's own config page if it's not 22.

PAMBA_SSH="${HA_PAMBA_SSH:-root@pamba.local}"     # e.g. "root@pamba.local -p 22222"
TANGA_SSH="${HA_TANGA_SSH:-root@tanga.local}"

set -euo pipefail
HOST="${1:-}"
case "$HOST" in
  pamba) TARGET="$PAMBA_SSH" ;;
  tanga) TARGET="$TANGA_SSH" ;;
  *) echo "usage: bash pull_and_push.sh <pamba|tanga>" >&2; exit 2 ;;
esac

if [[ ! -d .git ]] || [[ "$(basename "$(git rev-parse --show-toplevel)")" != "ha-config" ]]; then
  echo "run this from inside your local ha-config clone" >&2
  exit 3
fi

# Split "user@host -p 2222" into a proper ssh:// URL's pieces.
read -r USERHOST <<<"${TARGET%% -p*}"
PORT="22"
[[ "$TARGET" == *-p* ]] && PORT="${TARGET##*-p }"
REMOTE_URL="ssh://${USERHOST}:${PORT}//share/ha-config-repo"

echo "== fetching $HOST's local commit from $REMOTE_URL"
git fetch "$REMOTE_URL" "main:sync-$HOST-incoming" --force

echo "== fast-forwarding main onto it"
git checkout main
if ! git merge --ff-only "sync-$HOST-incoming"; then
  echo
  echo "!! not a fast-forward — main has diverged from what the box has."
  echo "   Left the fetched commit on branch 'sync-$HOST-incoming' for you to look at:"
  echo "     git log main..sync-$HOST-incoming"
  echo "     git merge sync-$HOST-incoming     # once you're happy, or"
  echo "     git rebase main sync-$HOST-incoming"
  exit 1
fi
git branch -d "sync-$HOST-incoming"

echo "== pushing to GitHub"
git push origin main
echo "== done: $HOST's latest snapshot is on GitHub."
