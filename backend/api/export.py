"""Serialise all public content into one JSON document for the Astro build."""
import re

from django.conf import settings
from django.utils import timezone

from blog.models import BlogCategory, BlogPost
from core.models import FAQ, HeroSlide, TeamMember
from destinations.models import Destination, Region
from gallery.models import GalleryAlbum
from itineraries.models import Itinerary
from testimonials.models import Testimonial

from .images import image_data

_IMG_TAG = re.compile(r'<img(?![^>]*\sloading=)', re.IGNORECASE)


_H1 = re.compile(r'<(/?)h1(\b[^>]*)>', re.IGNORECASE)


def rich(html):
    """CKEditor content: lazy-load images, and demote <h1> to <h2> (the page owns its single H1)."""
    html = _H1.sub(r'<\1h2\2>', html or '')
    return _IMG_TAG.sub('<img loading="lazy" decoding="async"', html)


def iso(dt):
    return dt.isoformat() if dt else None


def destination(d, full=True):
    data = {
        'id': d.id,
        'name': d.name,
        'slug': d.slug,
        'country': {'name': d.country.name, 'slug': d.country.slug},
        'region': {'name': d.country.region.name, 'slug': d.country.region.slug},
        'short_description': d.short_description,
        'image': image_data(d.featured_image, d.name),
        'is_featured': d.is_featured,
        'updated_at': iso(d.updated_at),
    }
    if full:
        data['description_html'] = rich(d.description)
    return data


def itinerary(i):
    return {
        'id': i.id,
        'title': i.title,
        'slug': i.slug,
        'destination': {
            'name': i.destination.name, 'slug': i.destination.slug,
            'country': i.destination.country.name, 'country_slug': i.destination.country.slug,
            'region_slug': i.destination.country.region.slug,
        },
        'duration_days': i.duration_days,
        'duration_nights': i.duration_nights,
        'duration_label': i.duration_label,
        'difficulty': i.difficulty,
        'difficulty_label': i.get_difficulty_display(),
        'max_group_size': i.max_group_size,
        'price_from': float(i.price_from) if i.price_from is not None else None,
        'summary': i.summary,
        'badge': i.badge,
        'overview_html': rich(i.overview),
        'includes_html': rich(i.includes),
        'excludes_html': rich(i.excludes),
        'image': image_data(i.featured_image, i.title),
        'is_featured': i.is_featured,
        'updated_at': iso(i.updated_at),
        'days': [
            {'day_number': d.day_number, 'title': d.title, 'description_html': rich(d.description),
             'accommodation': d.accommodation, 'meals': d.meals}
            for d in i.days.all()
        ],
    }


def post(p):
    return {
        'id': p.id,
        'title': p.title,
        'slug': p.slug,
        'author': p.author.get_full_name() or p.author.get_username(),
        'category': {'name': p.category.name, 'slug': p.category.slug} if p.category else None,
        'image': image_data(p.featured_image, p.title),
        'excerpt': p.excerpt,
        'content_html': rich(p.content),
        'published_date': iso(p.published_date or p.created_at),
        'updated_at': iso(p.updated_at),
    }


def testimonial(t):
    return {
        'id': t.id,
        'client_name': t.client_name,
        'photo': image_data(t.client_photo, t.client_name),
        'trip': {'title': t.trip.title, 'slug': t.trip.slug} if t.trip else None,
        'rating': t.rating,
        'review': t.review,
        'date': t.date.isoformat(),
        'is_featured': t.is_featured,
    }


def hero_slide(s):
    return {
        'eyebrow': s.eyebrow, 'headline': s.headline, 'highlight': s.highlight, 'subtitle': s.subtitle,
        'desktop': image_data(s.image_desktop, s.alt or str(s)),
        'mobile': image_data(s.image_mobile, s.alt or str(s)),
        'button': {'label': s.button_label, 'url': s.button_url},
        'second': {'label': s.second_label, 'url': s.second_url} if s.second_label and s.second_url else None,
    }


def build_content():
    posts = BlogPost.objects.filter(is_published=True).select_related('author', 'category')
    return {
        'generated_at': timezone.now().isoformat(),
        'site_url': settings.SITE_URL,
        'hero': [h for h in (hero_slide(s) for s in HeroSlide.objects.filter(is_active=True)) if h['desktop']][:5],
        'regions': [
            {
                'name': r.name, 'slug': r.slug, 'tagline': r.tagline, 'description': r.description,
                'image': image_data(r.image, r.name),
                'countries': [
                    {'name': c.name, 'slug': c.slug, 'intro': c.intro, 'image': image_data(c.image, c.name)}
                    for c in r.countries.all()
                ],
            }
            for r in Region.objects.prefetch_related('countries')
        ],
        'destinations': [destination(d) for d in Destination.objects.select_related('country__region')],
        'itineraries': [
            itinerary(i) for i in Itinerary.objects.select_related('destination__country__region').prefetch_related('days')
        ],
        'blog': {
            'categories': [
                {'name': c.name, 'slug': c.slug}
                for c in BlogCategory.objects.all()
            ],
            'posts': [post(p) for p in posts],
        },
        'gallery': [
            {
                'name': a.name,
                'slug': a.slug,
                'description': a.description,
                'cover': image_data(a.cover_image, a.name),
                'created_at': iso(a.created_at),
                'images': [
                    {'image': image_data(img.image, img.caption or a.name), 'caption': img.caption}
                    for img in a.images.all()
                ],
            }
            for a in GalleryAlbum.objects.prefetch_related('images')
        ],
        'testimonials': [testimonial(t) for t in Testimonial.objects.select_related('trip')],
        'team': [
            {'name': m.name, 'role': m.role, 'bio': m.bio, 'photo': image_data(m.photo, m.name)}
            for m in TeamMember.objects.all()
        ],
        'faq_categories': [{'value': v, 'label': l} for v, l in FAQ.CATEGORY_CHOICES],
        'faqs': [
            {'category': f.category, 'question': f.question, 'answer': f.answer}
            for f in FAQ.objects.all()
        ],
    }
