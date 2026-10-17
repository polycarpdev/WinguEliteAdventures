"""Mark the static site as stale whenever public content changes.

deploy/rebuild.sh (cron) rebuilds only when the flag exists, so editing
content in the admin never spawns a build from a web request.
"""
from django.conf import settings
from django.db.models.signals import post_delete, post_save

from blog.models import BlogCategory, BlogPost
from core.models import FAQ, TeamMember
from destinations.models import Destination
from gallery.models import GalleryAlbum, GalleryImage
from itineraries.models import Itinerary, ItineraryDay
from testimonials.models import Testimonial

CONTENT_MODELS = (
    Destination, Itinerary, ItineraryDay, BlogCategory, BlogPost,
    GalleryAlbum, GalleryImage, Testimonial, TeamMember, FAQ,
)


def mark_rebuild(**kwargs):
    if kwargs.get('raw'):  # loaddata
        return
    settings.VAR_DIR.mkdir(parents=True, exist_ok=True)
    settings.REBUILD_FLAG.touch()


for model in CONTENT_MODELS:
    post_save.connect(mark_rebuild, sender=model, dispatch_uid=f'rebuild-save-{model.__name__}')
    post_delete.connect(mark_rebuild, sender=model, dispatch_uid=f'rebuild-delete-{model.__name__}')
