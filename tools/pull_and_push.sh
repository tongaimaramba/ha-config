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
  # Resolution rule, straight from how this repo is meant to work:
  #   inside  hosts/$HOST/ -> the box wins  (it is the source of truth for its own snapshot)
  #   anywhere else        -> main wins     (tools/ etc. are authored on the Mac and flow
  #                                          TO the box via hadeploy, never back; the box
  #                                          only ever has them from its one-time seed commit)
  # Stage 2 = ours (main), stage 3 = theirs (the box). If the winning side has no
  # copy of the file, the winner's deletion stands.
  echo "== resolving conflicts:"
  git diff --name-only --diff-filter=U -z | while IFS= read -r -d '' f; do
    if [[ "$f" == hosts/$HOST/* ]]; then side=theirs; stage=3; who="box"
    else                                side=ours;   stage=2; who="main"
    fi
    if git cat-file -e ":$stage:$f" 2>/dev/null; then
      git checkout -q --"$side" -- "$f" && git add -- "$f"
    else
      git rm -q -- "$f"
    fi
    printf '   %-5s wins  %s\n' "$who" "$f"
  done
  git commit -q --no-edit
fi
git branch -D "sync-$HOST-incoming" >/dev/null

echo "== pushing to GitHub"
git push origin main
echo "== done: $HOST's latest snapshot is on GitHub."
