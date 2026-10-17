import io
import json
import shutil
import tempfile
from datetime import date, timedelta
from pathlib import Path

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image

from analytics.models import PageView
from blog.models import BlogPost
from bookings.models import Booking
from contact.models import ContactMessage
from destinations.models import Destination
from gallery.models import GalleryAlbum
from itineraries.models import Itinerary

from .content import TYPES

MEDIA = tempfile.mkdtemp()
VAR = Path(tempfile.mkdtemp())


def jpeg(name='p.jpg'):
    buf = io.BytesIO()
    Image.new('RGB', (40, 30), (120, 110, 40)).save(buf, 'JPEG')
    return SimpleUploadedFile(name, buf.getvalue(), content_type='image/jpeg')


@override_settings(ALLOWED_HOSTS=['testserver'], MEDIA_ROOT=MEDIA,
                   PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'], VAR_DIR=VAR, REBUILD_FLAG=VAR / 'rebuild.flag',
                   STORAGES={'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
                             'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'}})
class CockpitTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA, ignore_errors=True)

    def setUp(self):
        self.staff = User.objects.create_user('staff', password='pw-12345!', is_staff=True, first_name='Amina')
        self.client.force_login(self.staff)
        self.dest = Destination.objects.create(name='Masai Mara', description='<p>x</p>', short_description='x', featured_image=jpeg())
        self.trip = Itinerary.objects.create(title='Mara Classic', destination=self.dest, duration_days=3,
                                             price_from=900, overview='<p>x</p>', featured_image=jpeg())
        start = date.today() + timedelta(days=20)
        self.booking = Booking.objects.create(full_name='Jane Doe', email='jane@example.com', phone='+254 700 000 000',
                                              country='UK', destination=self.dest, itinerary=self.trip, start_date=start,
                                              end_date=start + timedelta(days=3), adults=2, accommodation_preference='luxury')
        self.msg = ContactMessage.objects.create(name='Tom', email='tom@example.com', subject='Hi', message='Hello')

    def test_login_required_and_non_staff_blocked(self):
        self.client.logout()
        r = self.client.get('/cockpit/')
        self.assertRedirects(r, '/cockpit/login/?next=/cockpit/', fetch_redirect_response=False)
        User.objects.create_user('guest', password='pw-12345!')
        r = self.client.post('/cockpit/login/', {'username': 'guest', 'password': 'pw-12345!'})
        self.assertContains(r, 'cockpit access')
        r = self.client.post('/cockpit/login/', {'username': 'staff', 'password': 'pw-12345!'})
        self.assertRedirects(r, '/cockpit/', fetch_redirect_response=False)

    def test_overview_pages_render(self):
        PageView.objects.create(path='/', visitor='abc', device='mobile', referrer='google.com', is_entry=True)
        for url in ['/cockpit/', '/cockpit/analytics/?range=7', '/cockpit/reports/?range=90',
                    '/cockpit/bookings/', '/cockpit/bookings/?status=new&q=jane', f'/cockpit/bookings/{self.booking.pk}/',
                    '/cockpit/messages/', f'/cockpit/messages/{self.msg.pk}/']:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)
        self.assertContains(self.client.get('/cockpit/'), 'Karibu, Amina')

    def test_every_content_type_lists_and_opens_forms(self):
        for t in TYPES:
            with self.subTest(t=t.key):
                self.assertEqual(self.client.get(f'/cockpit/content/{t.key}/').status_code, 200)
                self.assertEqual(self.client.get(f'/cockpit/content/{t.key}/new/').status_code, 200)
        self.assertEqual(self.client.get(f'/cockpit/content/safaris/{self.trip.pk}/').status_code, 200)
        self.assertEqual(self.client.get('/cockpit/content/nope/').status_code, 404)

    def test_create_post_sets_author_slug_and_rebuild_flag(self):
        (VAR / 'rebuild.flag').unlink(missing_ok=True)
        r = self.client.post('/cockpit/content/posts/new/', {
            'title': 'Best Time to Visit', 'slug': '', 'excerpt': 'When to go', 'content': '<p>Body</p>',
            'is_published': 'on', 'published_date': '', 'featured_image': jpeg(),
        })
        self.assertRedirects(r, '/cockpit/content/posts/', fetch_redirect_response=False)
        post = BlogPost.objects.get()
        self.assertEqual((post.slug, post.author, post.is_published), ('best-time-to-visit', self.staff, True))
        self.assertIsNotNone(post.published_date)
        self.assertTrue((VAR / 'rebuild.flag').exists())

    def test_duplicate_name_gets_unique_slug(self):
        self.client.post('/cockpit/content/destinations/new/', {
            'name': 'Masai Mara', 'slug': '', 'country': 'kenya', 'short_description': 's',
            'description': '<p>d</p>', 'featured_image': jpeg()})
        self.assertTrue(Destination.objects.filter(slug='masai-mara-2').exists())

    def test_safari_with_days(self):
        r = self.client.post(f'/cockpit/content/safaris/{self.trip.pk}/', {
            'title': 'Mara Classic', 'slug': self.trip.slug, 'destination': self.dest.pk, 'duration_days': 3,
            'difficulty': 'easy', 'max_group_size': 6, 'price_from': '950', 'overview': '<p>o</p>',
            'includes': '', 'excludes': '',
            'days-TOTAL_FORMS': '1', 'days-INITIAL_FORMS': '0', 'days-MIN_NUM_FORMS': '0', 'days-MAX_NUM_FORMS': '1000',
            'days-0-day_number': '1', 'days-0-title': 'Arrival', 'days-0-description': '<p>Fly in</p>',
        })
        self.assertEqual(r.status_code, 302, r.content[:2000])
        self.trip.refresh_from_db()
        self.assertEqual((self.trip.price_from, self.trip.days.count()), (950, 1))

    def test_album_multi_upload(self):
        album = GalleryAlbum.objects.create(name='Mara', cover_image=jpeg())
        r = self.client.post(f'/cockpit/content/gallery/{album.pk}/', {
            'name': 'Mara', 'slug': album.slug, 'description': '',
            'photos-TOTAL_FORMS': '0', 'photos-INITIAL_FORMS': '0', 'photos-MIN_NUM_FORMS': '0', 'photos-MAX_NUM_FORMS': '1000',
            'photos': [jpeg('a.jpg'), jpeg('b.jpg'), jpeg('c.jpg')],
        })
        self.assertEqual(r.status_code, 302)
        self.assertEqual(album.images.count(), 3)

    def test_delete_warns_about_cascade(self):
        r = self.client.get(f'/cockpit/content/destinations/{self.dest.pk}/delete/')
        self.assertContains(r, 'itineraries')
        self.client.post(f'/cockpit/content/destinations/{self.dest.pk}/delete/')
        self.assertFalse(Destination.objects.exists())

    def test_booking_status_update_sets_replied(self):
        self.client.post(f'/cockpit/bookings/{self.booking.pk}/', {'status': 'quote_sent', 'admin_notes': 'Sent PDF'})
        self.booking.refresh_from_db()
        self.assertEqual((self.booking.status, self.booking.admin_notes), ('quote_sent', 'Sent PDF'))
        self.assertIsNotNone(self.booking.replied_at)

    def test_message_marked_read_on_open(self):
        self.client.get(f'/cockpit/messages/{self.msg.pk}/')
        self.msg.refresh_from_db()
        self.assertEqual(self.msg.status, 'read')

    def test_csv_export(self):
        r = self.client.get('/cockpit/bookings/export.csv?status=new')
        self.assertEqual(r['Content-Type'], 'text/csv')
        self.assertIn('Jane Doe', r.content.decode())


@override_settings(ALLOWED_HOSTS=['testserver'])
class BeaconTests(TestCase):
    UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1'

    def hit(self, payload, ua=UA):
        return self.client.post('/api/hit/', json.dumps(payload), content_type='text/plain', HTTP_USER_AGENT=ua)

    def test_records_view(self):
        self.assertEqual(self.hit({'p': '/itineraries/?x=1', 'r': 'https://www.google.com/', 'tz': 'Europe/London', 'l': 'en-GB'}).status_code, 204)
        v = PageView.objects.get()
        self.assertEqual((v.path, v.referrer, v.device, v.is_entry, v.timezone), ('/itineraries/', 'google.com', 'mobile', True, 'Europe/London'))

    def test_internal_navigation_not_entry(self):
        self.hit({'p': '/about/', 'r': 'https://wingueliteadventures.co.ke/'})
        self.assertFalse(PageView.objects.get().is_entry)

    def test_ignores_bots_staff_and_private_paths(self):
        self.hit({'p': '/'}, ua='Googlebot/2.1')
        self.hit({'p': '/cockpit/'})
        self.hit({'p': 'not-a-path'})
        self.client.force_login(User.objects.create_user('s', is_staff=True))
        self.hit({'p': '/'})
        self.assertEqual(PageView.objects.count(), 0)
