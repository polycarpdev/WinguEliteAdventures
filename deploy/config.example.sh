# Copy to deploy/config.sh on the server and adjust. (config.sh is git-ignored.)

# This git checkout on the server.
APP_DIR="$HOME/winguelite"

# The domain's document root. Only the built static site lives here.
DOCROOT="$HOME/wingueliteadventures.co.ke"

# Python of the cPanel "Setup Python App" virtualenv (app root: winguelite/backend).
PYTHON="$HOME/virtualenv/winguelite/backend/3.13/bin/python"

# Node >= 22.12 for the build. CloudLinux ships it here; no Node app needed.
NODE_BIN_DIR="/opt/alt/alt-nodejs22/root/usr/bin"

BRANCH="main"
