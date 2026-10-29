#!/usr/bin/env bash
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
  $LOW "$PYTHON" backend/manage.py createcachetable
  log "Collecting admin/cockpit static files"
  $LOW "$PYTHON" backend/manage.py collectstatic --noinput --verbosity 0

  build_site

  ln -sfn "$BACKEND/media" "$DOCROOT/media"
  ln -sfn "$BACKEND/staticfiles" "$DOCROOT/static"

  mkdir -p "$BACKEND/tmp" && touch "$BACKEND/tmp/restart.txt"
  log "Deploy complete: $(git rev-parse --short HEAD)"
}

with_lock deploy
