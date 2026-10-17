import json
import time
from datetime import date, timedelta

from django.core import mail
from django.core.cache import cache
from django.test import TestCase, override_settings

from bookings.models import Booking
from contact.models import ContactMessage
from destinations.models import Destination

ORIGIN = 'http://localhost:4321'


@override_settings(ALLOWED_HOSTS=['testserver'], CORS_ALLOWED_ORIGINS=[ORIGIN],
                   EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class FormApiTests(TestCase):
    def setUp(self):
        cache.clear()
        self.dest = Destination.objects.create(
            name='Masai Mara', country='kenya', description='x', short_description='x', featured_image='x.jpg')
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

    def test_get_not_allowed(self):
        self.assertEqual(self.client.get('/api/contact/').status_code, 405)
