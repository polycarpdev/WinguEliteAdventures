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
# mkdir is atomic and needs no extra tools (CloudLinux CageFS lacks flock/rsync).
LOCK_DIR="$VAR/build.lock.d"
with_lock() {
  # A lock older than 30 minutes is from a crashed run.
  if [ -d "$LOCK_DIR" ] && [ -n "$(find "$LOCK_DIR" -maxdepth 0 -mmin +30 2>/dev/null)" ]; then rmdir "$LOCK_DIR"; fi
  if ! mkdir "$LOCK_DIR" 2>/dev/null; then log "Another deploy/build is running; skipping."; exit 0; fi
  trap 'rmdir "$LOCK_DIR" 2>/dev/null' EXIT
  "$@"
}

# Hash of a file, to skip reinstalling dependencies that didn't change.
changed() { # changed <file> <stamp-name>
  local sum; sum="$(sha256sum "$1" | cut -d' ' -f1)"
  if [ "$(cat "$VAR/$2" 2>/dev/null)" != "$sum" ]; then echo "$sum" > "$VAR/$2.new"; return 0; fi
  return 1
}
mark_done() { mv "$VAR/$1.new" "$VAR/$1"; }

# Merge our rules into the docroot .htaccess, keeping cPanel's Passenger and
# env blocks intact (cPanel rewrites those when the Python app is edited).
install_htaccess() {
  local target="$DOCROOT/.htaccess" tmp
  tmp="$(mktemp)"
  cat "$APP_DIR/deploy/htaccess" > "$tmp"
  echo >> "$tmp"
  if [ -f "$target" ]; then
    sed '/^# BEGIN WINGU/,/^# END WINGU/d' "$target" >> "$tmp"
  fi
  mv "$tmp" "$target"
  chmod 644 "$target"
}

# Copy the new build over the docroot, then delete files the build no longer has.
# New fingerprinted assets land first, so no page ever points at a missing file.
# Server-managed paths (.htaccess, media, static, .well-known, cgi-bin) are kept.
publish() {
  local src="$1" dest="$2" listn="$VAR/publish.new" listo="$VAR/publish.old"
  if [ -d "$src/_astro" ]; then mkdir -p "$dest/_astro" && cp -a "$src/_astro/." "$dest/_astro/"; fi
  cp -a "$src/." "$dest/"
  (cd "$src" && find . -mindepth 1 | sort) > "$listn"
  (cd "$dest" && find . -mindepth 1 \( -path ./media -o -path ./static -o -path ./.well-known \
      -o -path ./cgi-bin -o -path './.htaccess*' \) -prune -o -print | sort) > "$listo"
  comm -13 "$listn" "$listo" | sort -r | while IFS= read -r p; do rm -rf -- "$dest/${p#./}"; done
  rm -f "$listn" "$listo"
}

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
  publish dist.new "$DOCROOT"
  rm -rf dist && mv dist.new dist
  install_htaccess
  date +%s > "$VAR/last_build"
  log "Site published"
}
