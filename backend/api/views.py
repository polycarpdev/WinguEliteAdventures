"""JSON endpoints for the two public forms. The site itself is static."""
import json
import logging
import time
from datetime import date

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.http import HttpResponseNotFound, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from bookings.models import Booking
from contact.models import ContactMessage
from destinations.models import Destination
from itineraries.models import Itinerary

log = logging.getLogger(__name__)

RATE_LIMIT = 5          # submissions
RATE_WINDOW = 10 * 60   # per 10 minutes per IP
MIN_FILL_SECONDS = 3    # humans don't fill a form in under 3s


class FormError(Exception):
    def __init__(self, errors, status=400):
        self.errors, self.status = errors, status


def _client_ip(request):
    fwd = request.META.get('HTTP_X_FORWARDED_FOR')
    return fwd.split(',')[0].strip() if fwd else request.META.get('REMOTE_ADDR', '')


def _guard(request):
    """Origin check, rate limit and bot traps. Returns parsed JSON body."""
    origin = request.headers.get('Origin')
    if origin and origin.rstrip('/') not in settings.CORS_ALLOWED_ORIGINS:
        raise FormError({'__all__': 'Origin not allowed.'}, 403)

    key = f'form-rate:{_client_ip(request)}'
    hits = cache.get(key, 0)
    if hits >= RATE_LIMIT:
        raise FormError({'__all__': 'Too many submissions. Please try again in a few minutes.'}, 429)
    cache.set(key, hits + 1, RATE_WINDOW)

    try:
        data = json.loads(request.body or b'{}')
    except ValueError:
        raise FormError({'__all__': 'Invalid request.'})
    if not isinstance(data, dict):
        raise FormError({'__all__': 'Invalid request.'})

    # Honeypot field and fill-time trap: pretend success to bots.
    started = data.get('_t')
    too_fast = isinstance(started, (int, float)) and (time.time() * 1000 - started) < MIN_FILL_SECONDS * 1000
    if data.get('website') or too_fast:
        raise FormError(None, 200)
    return data


def _text(data, errors, name, label, max_len, required=True):
    value = str(data.get(name) or '').strip()
    if required and not value:
        errors[name] = f'{label} is required.'
    elif len(value) > max_len:
        errors[name] = f'{label} must be at most {max_len} characters.'
    return value


def _email(data, errors):
    value = _text(data, errors, 'email', 'Email', 254)
    if value and 'email' not in errors:
        try:
            validate_email(value)
        except ValidationError:
            errors['email'] = 'Enter a valid email address.'
    return value


def _int(data, errors, name, label, lo, hi, default):
    raw = data.get(name, default)
    try:
        value = int(raw)
    except (TypeError, ValueError):
        errors[name] = f'{label} must be a number.'
        return default
    if not lo <= value <= hi:
        errors[name] = f'{label} must be between {lo} and {hi}.'
    return value


def _date(data, errors, name, label):
    try:
        return date.fromisoformat(str(data.get(name) or ''))
    except ValueError:
        errors[name] = f'{label} is required.'
        return None


def _notify(subject, body, reply_to, ack_to=None, ack_subject=None, ack_body=None):
    try:
        EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, [settings.ADMIN_EMAIL],
                     reply_to=[reply_to]).send()
        if ack_to:
            EmailMessage(ack_subject, ack_body, settings.DEFAULT_FROM_EMAIL, [ack_to]).send()
    except Exception:  # never lose a saved enquiry because SMTP hiccuped
        log.exception('Failed to send notification email: %s', subject)


def _respond(handler):
    @csrf_exempt
    @require_POST
    def view(request):
        try:
            data = _guard(request)
            return JsonResponse({'ok': True, **(handler(data) or {})})
        except FormError as exc:
            if exc.status == 200:
                return JsonResponse({'ok': True})
            return JsonResponse({'ok': False, 'errors': exc.errors}, status=exc.status)
    return view


def _booking(data):
    errors = {}
    full_name = _text(data, errors, 'full_name', 'Full name', 200)
    email = _email(data, errors)
    phone = _text(data, errors, 'phone', 'Phone', 20)
    country = _text(data, errors, 'country', 'Country', 100)
    start = _date(data, errors, 'start_date', 'Start date')
    end = _date(data, errors, 'end_date', 'End date')
    adults = _int(data, errors, 'adults', 'Adults', 1, 50, 1)
    children = _int(data, errors, 'children', 'Children', 0, 50, 0)
    accommodation = str(data.get('accommodation_preference') or '')
    special = _text(data, errors, 'special_requests', 'Special requests', 3000, required=False)
    heard = _text(data, errors, 'how_did_you_hear', 'This field', 200, required=False)

    if accommodation not in dict(Booking.ACCOMMODATION_CHOICES):
        errors['accommodation_preference'] = 'Choose an accommodation level.'
    if start and start < date.today():
        errors['start_date'] = 'Start date cannot be in the past.'
    if start and end and end < start:
        errors['end_date'] = 'End date must be after the start date.'

    destination = Destination.objects.filter(slug=data.get('destination') or '').first()
    if not destination:
        errors['destination'] = 'Choose a destination.'
    itinerary = None
    if data.get('itinerary'):
        itinerary = Itinerary.objects.filter(slug=data['itinerary']).first()
        if not itinerary:
            errors['itinerary'] = 'Unknown safari package.'

    if errors:
        raise FormError(errors)

    b = Booking.objects.create(
        full_name=full_name, email=email, phone=phone, country=country,
        destination=destination, itinerary=itinerary, start_date=start, end_date=end,
        adults=adults, children=children, accommodation_preference=accommodation,
        special_requests=special, how_did_you_hear=heard,
    )
    _notify(
        f'New booking request: {b.full_name} ({b.destination})',
        f'Name: {b.full_name}\nEmail: {b.email}\nPhone: {b.phone}\nCountry: {b.country}\n'
        f'Destination: {b.destination}\nPackage: {b.itinerary or "-"}\n'
        f'Dates: {b.start_date} to {b.end_date}\nTravellers: {b.adults} adults, {b.children} children\n'
        f'Accommodation: {b.get_accommodation_preference_display()}\n\n{b.special_requests}\n\n'
        f'Open in cockpit: {settings.SITE_URL}/cockpit/bookings/{b.pk}/',
        reply_to=b.email,
        ack_to=b.email,
        ack_subject='We received your safari request - Wingu Elite Adventures',
        ack_body=(
            f'Hi {b.full_name},\n\nThank you for choosing Wingu Elite Adventures. We have received your '
            f'request for {b.destination} ({b.start_date} to {b.end_date}) and a safari specialist will '
            f'get back to you within 24 hours with a tailored quote.\n\nKaribu!\nWingu Elite Adventures\n'
            f'{settings.SITE_URL}'
        ),
    )
    return {'id': b.pk}


def _contact(data):
    errors = {}
    name = _text(data, errors, 'name', 'Name', 200)
    email = _email(data, errors)
    phone = _text(data, errors, 'phone', 'Phone', 20, required=False)
    subject = _text(data, errors, 'subject', 'Subject', 200)
    message = _text(data, errors, 'message', 'Message', 5000)
    if errors:
        raise FormError(errors)

    m = ContactMessage.objects.create(name=name, email=email, phone=phone, subject=subject, message=message)
    _notify(
        f'New message: {m.subject}',
        f'From: {m.name} <{m.email}>\nPhone: {m.phone or "-"}\n\n{m.message}\n\n'
        f'Open in cockpit: {settings.SITE_URL}/cockpit/messages/{m.pk}/',
        reply_to=m.email,
    )
    return {'id': m.pk}


booking = _respond(_booking)
contact = _respond(_contact)


def health(request):
    return JsonResponse({'ok': True})


def not_found(request, exception=None):
    """Serve the static site's designed 404 page for any URL Django doesn't own."""
    try:
        html = (settings.STATIC_SITE_DIR / '404.html').read_text(encoding='utf-8')
    except OSError:
        html = '<h1>Page not found</h1><p><a href="/">Back to Wingu Elite Adventures</a></p>'
    return HttpResponseNotFound(html)
