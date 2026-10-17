# Shared helpers for deploy.sh and rebuild.sh. Sourced, not executed.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[ -f "$HERE/config.sh" ] || { echo "Missing $HERE/config.sh (copy config.example.sh)"; exit 1; }
# shellcheck source=/dev/null
source "$HERE/config.sh"

BACKEND="$APP_DIR/backend"
WEB="$APP_DIR/web"
VAR="$BACKEND/var"
mkdir -p "$VAR"
export PATH="$NODE_BIN_DIR:$PATH"

# --- Be a good neighbour on shared hosting ---------------------------------
# Lowest CPU/IO priority and as few threads as the tools allow, so builds
# never trip the account's process (nproc) or CPU limits.
export GOMAXPROCS=1              # esbuild (Go) worker threads
export UV_THREADPOOL_SIZE=1      # Node libuv pool
export NODE_OPTIONS="--max-old-space-size=768"
export npm_config_maxsockets=2 npm_config_fund=false npm_config_audit=false npm_config_update_notifier=false
export ASTRO_TELEMETRY_DISABLED=1
export PYTHONDONTWRITEBYTECODE=1
LOW="nice -n 19"
command -v ionice >/dev/null 2>&1 && LOW="$LOW ionice -c3"

log() { printf '[%s] %s\n' "$(date '+%F %T')" "$*"; }

# Run "$@" while holding an exclusive lock; skip (exit 0) if another run is active.
with_lock() {
  exec 9>"$VAR/build.lock"
  if ! flock -n 9; then log "Another deploy/build is running; skipping."; exit 0; fi
  "$@"
}

# Hash of a file, to skip reinstalling dependencies that didn't change.
changed() { # changed <file> <stamp-name>
  local sum; sum="$(sha256sum "$1" | cut -d' ' -f1)"
  if [ "$(cat "$VAR/$2" 2>/dev/null)" != "$sum" ]; then echo "$sum" > "$VAR/$2.new"; return 0; fi
  return 1
}
mark_done() { mv "$VAR/$1.new" "$VAR/$1"; }

build_site() {
  log "Exporting content from Django"
  rm -f "$VAR/rebuild.flag"   # edits made during the build re-set it
  $LOW "$PYTHON" "$BACKEND/manage.py" export_content

  cd "$WEB"
  if [ ! -d node_modules ] || changed package-lock.json npm.sha; then
    log "Installing frontend dependencies (npm ci)"
    $LOW npm ci --no-audit --no-fund --loglevel=error
    [ -f "$VAR/npm.sha.new" ] && mark_done npm.sha
  fi

  log "Building static site"
  rm -rf dist.new
  $LOW npx astro build --outDir dist.new --silent

  log "Publishing to $DOCROOT"
  mkdir -p "$DOCROOT"
  # Copy fingerprinted assets first, then pages, then delete stale files, so a
  # visitor never gets a page whose CSS/JS isn't there yet.
  $LOW rsync -a dist.new/_astro/ "$DOCROOT/_astro/"
  $LOW rsync -a --delete-after \
    --exclude='.htaccess' --exclude='media' --exclude='static' \
    --exclude='.well-known' --exclude='cgi-bin' --exclude='_astro/' \
    dist.new/ "$DOCROOT/"
  $LOW rsync -a --delete-after dist.new/_astro/ "$DOCROOT/_astro/"
  rm -rf dist && mv dist.new dist
  date +%s > "$VAR/last_build"
  log "Site published"
}
