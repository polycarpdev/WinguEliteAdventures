#!/usr/bin/env bash
# Pull the latest code and deploy everything. Run on the server:
#   ~/winguelite/deploy/deploy.sh
source "$(dirname "$0")/lib.sh"

deploy() {
  cd "$APP_DIR"
  log "Pulling $BRANCH"
  git fetch --quiet origin "$BRANCH"
  git reset --quiet --hard "origin/$BRANCH"

  if changed backend/requirements.txt pip.sha; then
    log "Installing Python requirements"
    $LOW "$PYTHON" -m pip install --quiet --disable-pip-version-check --only-binary=:all: -r backend/requirements.txt
    mark_done pip.sha
  fi

  log "Migrating database"
  $LOW "$PYTHON" backend/manage.py migrate --noinput
  log "Collecting admin/cockpit static files"
  $LOW "$PYTHON" backend/manage.py collectstatic --noinput --verbosity 0

  build_site

  # Apache serves media and Django's static files straight from disk.
  ln -sfn "$BACKEND/media" "$DOCROOT/media"
  ln -sfn "$BACKEND/staticfiles" "$DOCROOT/static"
  sed -e "s#__APP_DIR__#$APP_DIR#g" -e "s#__PYTHON__#$PYTHON#g" "$APP_DIR/deploy/htaccess" > "$DOCROOT/.htaccess"

  # Restart the Django (Passenger) app.
  mkdir -p "$BACKEND/tmp" && touch "$BACKEND/tmp/restart.txt"
  log "Deploy complete: $(git rev-parse --short HEAD)"
}

with_lock deploy
