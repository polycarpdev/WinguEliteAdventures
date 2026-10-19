import json
import tempfile
import time
from pathlib import Path
from datetime import date, timedelta

from django.core import mail
from django.core.cache import cache
from django.test import TestCase, override_settings

from bookings.models import Booking
from contact.models import ContactMessage
from destinations.models import Country, Destination

ORIGIN = 'http://localhost:4321'
_TMP = Path(tempfile.mkdtemp())


@override_settings(ALLOWED_HOSTS=['testserver'], CORS_ALLOWED_ORIGINS=[ORIGIN],
                   VAR_DIR=_TMP, REBUILD_FLAG=_TMP / 'rebuild.flag',
                   EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class FormApiTests(TestCase):
    def setUp(self):
        cache.clear()
        self.dest = Destination.objects.create(
            name='Masai Mara', country=Country.objects.get(slug='kenya'), description='x', short_description='x', featured_image='x.jpg')
        self.t = int(time.time() * 1000) - 10_000

    def post(self, url, payload, origin=ORIGIN):
        return self.client.post(url, json.dumps(payload), content_type='application/json', HTTP_ORIGIN=origin)

    def booking_payload(self, **kw):
        start = date.today() + timedelta(days=30)
        data = {
            '_t': self.t, 'full_name': 'Jane Doe', 'email': 'jane@example.com', 'phone': '+254700000000',
            'country': 'Kenya', 'destination': self.dest.slug, 'start_date': start.isoformat(),
            'end_date': (start + timedelta(days=5)).isoformat(), 'adults': 2, 'children': 0,
            'accommodation_preference': 'luxury',
        }
        data.update(kw)
        return data

    def test_booking_created_and_emails_sent(self):
        r = self.post('/api/bookings/', self.booking_payload())
        self.assertEqual(r.status_code, 200, r.content)
        self.assertEqual(Booking.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 2)  # admin notification + guest acknowledgement

    def test_booking_by_days_and_nights(self):
        payload = self.booking_payload(days=5, nights=4)
        payload.pop('end_date')
        r = self.post('/api/bookings/', payload)
        self.assertEqual(r.status_code, 200, r.content)
        b = Booking.objects.get()
        self.assertEqual((b.duration_days, b.duration_nights, (b.end_date - b.start_date).days), (5, 4, 4))

    def test_nights_must_match_days(self):
        r = self.post('/api/bookings/', self.booking_payload(days=5, nights=2))
        self.assertIn('nights', r.json()['errors'])

    def test_end_date_still_accepted(self):
        self.post('/api/bookings/', self.booking_payload())
        b = Booking.objects.get()
        self.assertEqual((b.duration_days, b.duration_nights), (6, 5))

    def test_booking_validation(self):
        r = self.post('/api/bookings/', self.booking_payload(
            email='bad', destination='nope', start_date='2020-01-01', adults=0, accommodation_preference='x'))
        self.assertEqual(r.status_code, 400)
        self.assertEqual(set(r.json()['errors']),
                         {'email', 'destination', 'start_date', 'adults', 'accommodation_preference'})
        self.assertEqual(Booking.objects.count(), 0)

    def test_end_before_start(self):
        r = self.post('/api/bookings/', self.booking_payload(end_date=date.today().isoformat()))
        self.assertIn('end_date', r.json()['errors'])

    def test_contact_ok(self):
        r = self.post('/api/contact/', {'_t': self.t, 'name': 'A', 'email': 'a@b.co', 'subject': 'Hi', 'message': 'Hello'})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_honeypot_and_too_fast_silently_dropped(self):
        ok = {'name': 'A', 'email': 'a@b.co', 'subject': 'Hi', 'message': 'Hello'}
        self.assertEqual(self.post('/api/contact/', {**ok, '_t': self.t, 'website': 'x'}).status_code, 200)
        self.assertEqual(self.post('/api/contact/', {**ok, '_t': int(time.time() * 1000)}).status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_foreign_origin_rejected(self):
        self.assertEqual(self.post('/api/contact/', {}, origin='https://evil.example').status_code, 403)

    def test_rate_limit(self):
        for _ in range(5):
            self.post('/api/contact/', {'_t': self.t})
        self.assertEqual(self.post('/api/contact/', {'_t': self.t}).status_code, 429)

    def test_content_change_sets_rebuild_flag(self):
        from django.conf import settings
        settings.REBUILD_FLAG.unlink(missing_ok=True)
        self.dest.save()
        self.assertTrue(settings.REBUILD_FLAG.exists())

    def test_get_not_allowed(self):
        self.assertEqual(self.client.get('/api/contact/').status_code, 405)


@override_settings(ALLOWED_HOSTS=['testserver'], DEBUG=False)
class NotFoundTests(TestCase):
    def test_unknown_url_uses_site_404(self):
        r = self.client.get('/no-such-page/')
        self.assertEqual(r.status_code, 404)
        self.assertIn(b'Wingu', r.content)

