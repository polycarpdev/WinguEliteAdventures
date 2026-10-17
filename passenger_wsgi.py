#!/usr/bin/env python3
import os
import sys
import signal
import threading

# Add your project directory to the sys.path
sys.path.insert(0, os.path.dirname(__file__))

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ['DJANGO_SETTINGS_MODULE'] = 'winguelite.settings'

# Import your Django application
from django.core.wsgi import get_wsgi_application

# Get the Django WSGI application
application = get_wsgi_application()

# Graceful restart handling
_restart = threading.Event()

def _restart_handler(signum, frame):
    _restart.set()

signal.signal(signal.SIGUSR1, _restart_handler)

def when_ready():
    if _restart.is_set():
        application.unload()
        application = get_wsgi_application()
    return application