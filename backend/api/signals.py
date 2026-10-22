"""Mark the static site as stale whenever public content changes.

deploy/rebuild.sh (cron) rebuilds only when the flag exists, so editing
content in the admin never spawns a build from a web request.
"""
import logging
import subprocess
import threading
import time

from django.conf import settings
from django.db.models.signals import post_delete, post_save

from blog.models import BlogCategory, BlogPost
from core.models import FAQ, HeroSlide, TeamMember
from destinations.models import Country, Destination, Region
from gallery.models import GalleryAlbum, GalleryImage
from itineraries.models import Itinerary, ItineraryDay
from testimonials.models import Testimonial

CONTENT_MODELS = (
    Destination, Itinerary, ItineraryDay, BlogCategory, BlogPost,
    GalleryAlbum, GalleryImage, Testimonial, TeamMember, FAQ, HeroSlide, Region, Country,
)


log = logging.getLogger(__name__)
_export_timer = None
_export_lock = threading.Lock()


def _export_now():
    """Local development: export immediately so `astro dev` refreshes by itself."""
    from django.core.management import call_command
    try:
        call_command('export_content', verbosity=0)
        settings.REBUILD_FLAG.unlink(missing_ok=True)
        (settings.VAR_DIR / 'last_build').write_text(str(int(time.time())))
    except Exception:
        log.exception('Local content export failed')


def _publish_now():
    """Production: start deploy/rebuild.sh in the background (it holds a lock, so
    only one build runs at a time, and it rebuilds again if more edits arrive)."""
    script = settings.REPO_DIR / 'deploy' / 'rebuild.sh'
    if not script.exists() or not (settings.REPO_DIR / 'deploy' / 'config.sh').exists():
        return
    log_file = open(settings.VAR_DIR / 'rebuild.log', 'a')
    subprocess.Popen(['bash', str(script)], stdout=log_file, stderr=subprocess.STDOUT,
                     stdin=subprocess.DEVNULL, start_new_session=True, close_fds=True)


def _schedule(fn):
    """Run fn ~1s after the last change, so a batch of saves triggers one run."""
    global _export_timer
    with _export_lock:
        if _export_timer:
            _export_timer.cancel()
        _export_timer = threading.Timer(1.0, fn)
        _export_timer.daemon = True
        _export_timer.start()


def mark_rebuild(**kwargs):
    if kwargs.get('raw'):  # loaddata
        return
    settings.VAR_DIR.mkdir(parents=True, exist_ok=True)
    settings.REBUILD_FLAG.touch()
    # Locally: export straight into the Astro dev server. In production: rebuild
    # and publish the static site right away (about 20-30 seconds).
    if getattr(settings, 'AUTO_EXPORT', False):
        _schedule(_export_now)
    elif getattr(settings, 'PUBLISH_ON_SAVE', False):
        _schedule(_publish_now)


for model in CONTENT_MODELS:
    post_save.connect(mark_rebuild, sender=model, dispatch_uid=f'rebuild-save-{model.__name__}')
    post_delete.connect(mark_rebuild, sender=model, dispatch_uid=f'rebuild-delete-{model.__name__}')
