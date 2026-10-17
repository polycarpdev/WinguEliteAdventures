# Copy to deploy/config.sh on the server and adjust. (config.sh is git-ignored.)

# Absolute path of this git checkout on the server.
APP_DIR="$HOME/winguelite"

# Apache document root of the domain (cPanel > Domains). The static site is synced here.
DOCROOT="$HOME/wingueliteadventures.co.ke"

# Python virtualenv made by cPanel "Setup Python App" (app root: $APP_DIR/backend).
PYTHON="$HOME/virtualenv/winguelite/backend/3.13/bin/python"

# Node made by cPanel "Setup Node.js App" (Node >= 22.12). Only used to build.
NODE_BIN_DIR="$HOME/nodevenv/winguelite/web/22/bin"

BRANCH="main"
