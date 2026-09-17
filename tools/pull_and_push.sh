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

PAMBA_SSH="${HA_PAMBA_SSH:-hassio@192.168.179.41}"     # e.g. "root@pamba.local -p 22222"
TANGA_SSH="${HA_TANGA_SSH:-hassio@192.168.179.199}"

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

echo "== merging into main"
git checkout -q main
# A plain merge, not --ff-only: main always has Mac-side commits (tools/ edits,
# earlier merges) the box never sees, so a fast-forward is never possible in
# practice. --allow-unrelated-histories covers the first-ever sync from a box
# that was seeded with a fresh `git init` rather than a clone.
if ! git merge --no-edit --allow-unrelated-histories "sync-$HOST-incoming"; then
  conflicted="$(git diff --name-only --diff-filter=U)"
  if [[ -z "$conflicted" ]]; then
    echo "!! merge failed for a reason other than conflicts (see above). Fetched commit is on branch 'sync-$HOST-incoming'." >&2
    exit 1
  fi
  if grep -qv "^hosts/$HOST/" <<<"$conflicted"; then
    echo >&2
    echo "!! conflicts outside hosts/$HOST/ — not auto-resolving these, look at them by hand:" >&2
    grep -v "^hosts/$HOST/" <<<"$conflicted" >&2
    echo "   (git merge --abort  to back out, or resolve + git commit)" >&2
    exit 1
  fi
  # Every conflict is inside hosts/$HOST/. The box is the source of truth for its
  # own snapshot by definition, so its version wins.
  echo "== conflicts only under hosts/$HOST/ — taking the box's version"
  git diff --name-only --diff-filter=U -z | while IFS= read -r -d '' f; do
    if git cat-file -e ":3:$f" 2>/dev/null; then
      git checkout --theirs -- "$f"     # box has the file: use its content
    else
      git rm -q -- "$f"                 # box deleted it: deletion wins
    fi
  done
  git add "hosts/$HOST"
  git commit -q --no-edit
fi
git branch -D "sync-$HOST-incoming" >/dev/null

echo "== pushing to GitHub"
git push origin main
echo "== done: $HOST's latest snapshot is on GitHub."
