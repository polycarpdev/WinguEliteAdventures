import hashlib
import json
import re
from urllib.parse import urlsplit

from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import PageView

BOTS = re.compile(r'bot|crawl|spider|slurp|preview|headless|lighthouse|monitor|curl|wget|python|scrapy|facebookexternalhit|whatsapp', re.I)
SITE_HOSTS = {'wingueliteadventures.co.ke', 'www.wingueliteadventures.co.ke', 'localhost', '127.0.0.1'}

def _device(ua):
    if re.search(r'iPad|Tablet|Nexus (7|9|10)|SM-T', ua):
        return 'tablet'
    if re.search(r'Mobi|Android|iPhone', ua):
        return 'mobile'
    return 'desktop'

def _browser(ua):
    for name, pattern in (('Edge', r'Edg/'), ('Opera', r'OPR/'), ('Samsung', r'SamsungBrowser'),
                          ('Chrome', r'Chrome/'), ('Firefox', r'Firefox/'), ('Safari', r'Safari/')):
        if re.search(pattern, ua):
            return name
    return 'Other'

def _ip(request):
    fwd = request.META.get('HTTP_X_FORWARDED_FOR')
    return fwd.split(',')[0].strip() if fwd else request.META.get('REMOTE_ADDR', '')

@csrf_exempt
@require_POST
def hit(request):
    ua = request.META.get('HTTP_USER_AGENT', '')
    if not ua or BOTS.search(ua) or (request.user.is_authenticated and request.user.is_staff):
        return HttpResponse(status=204)
    try:
        data = json.loads(request.body[:2000] or b'{}')
        path = str(data.get('p', ''))[:300]
    except (ValueError, AttributeError):
        return HttpResponse(status=204)
    if not path.startswith('/') or path.startswith(('/cockpit', '/admin', '/api')):
        return HttpResponse(status=204)

    ref_host = urlsplit(str(data.get('r', ''))).hostname or ''
    internal = ref_host.lower() in SITE_HOSTS
    day = timezone.localdate().isoformat()
    visitor = hashlib.sha256(f'{settings.SECRET_KEY}|{day}|{_ip(request)}|{ua}'.encode()).hexdigest()[:16]

    PageView.objects.create(
        path=path.split('?')[0].split('#')[0] or '/',
        referrer='' if internal else ref_host.removeprefix('www.')[:200],
        visitor=visitor,
        device=_device(ua),
        browser=_browser(ua),
        timezone=str(data.get('tz', ''))[:60],
        language=str(data.get('l', ''))[:10],
        is_entry=not internal,
    )
    return HttpResponse(status=204)
