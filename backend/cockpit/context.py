from django.conf import settings

from bookings.models import Booking
from contact.models import ContactMessage

from .content import TYPES


def cockpit(request):
    """Sidebar badges and site publish status, only for cockpit pages."""
    if not request.path.startswith('/cockpit/') or not request.user.is_authenticated:
        return {}
    last_build = settings.VAR_DIR / 'last_build'
    try:
        built_at = int(last_build.read_text().strip())
    except (OSError, ValueError):
        built_at = None
    return {
        'nav_new_bookings': Booking.objects.filter(status='new').count(),
        'nav_new_messages': ContactMessage.objects.filter(status='new').count(),
        'site_pending': settings.REBUILD_FLAG.exists(),
        'site_built_at': built_at,
        'nav_types': TYPES,
    }
