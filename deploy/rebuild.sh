#!/usr/bin/env bash
# Rebuilds the static site when content changed (backend/var/rebuild.flag).
# Started automatically by Django the moment something is saved in the cockpit.
# Optional safety-net cron (costs nothing when there's nothing to do):
#   */5 * * * * $HOME/winguelite/deploy/rebuild.sh >> $HOME/winguelite/backend/var/rebuild.log 2>&1
source "$(dirname "$0")/lib.sh"
[ -f "$VAR/rebuild.flag" ] || exit 0

# Edits made while a build runs set the flag again: build once more (max 3).
build_until_clean() {
  for _ in 1 2 3; do
    [ -f "$VAR/rebuild.flag" ] || break
    build_site
  done
}
with_lock build_until_clean
