#!/usr/bin/env bash
source "$(dirname "$0")/lib.sh"
[ -f "$VAR/rebuild.flag" ] || exit 0

build_until_clean() {
  for _ in 1 2 3; do
    [ -f "$VAR/rebuild.flag" ] || break
    build_site
  done
}
with_lock build_until_clean
