#!/usr/bin/env bash
# Cron job (every 5 minutes). Rebuilds the static site only when content was
# changed in the admin, which sets backend/var/rebuild.flag. Otherwise it exits
# immediately and costs nothing.
#   */5 * * * * $HOME/winguelite/deploy/rebuild.sh >> $HOME/winguelite/backend/var/rebuild.log 2>&1
source "$(dirname "$0")/lib.sh"
[ -f "$VAR/rebuild.flag" ] || exit 0
with_lock build_site
