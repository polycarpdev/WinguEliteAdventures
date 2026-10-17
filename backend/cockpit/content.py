"""Registry of editable content types. One entry drives the list, form and delete
screens, so adding a model to the cockpit is a few lines here."""
from dataclasses import dataclass, field
from typing import Callable

from blog.models import BlogCategory, BlogPost
from core.models import FAQ, TeamMember
from destinations.models import Destination
from gallery.models import GalleryAlbum
from itineraries.models import Itinerary
from testimonials.models import Testimonial


@dataclass
class ContentType:
    key: str
    model: type
    label: str
    plural: str
    icon: str
    fields: list
    columns: list                       # [(attr or callable, header)]
    search: list = field(default_factory=list)
    filters: dict = field(default_factory=dict)   # {param: (lookup, [(value, label)])}
    image: str | None = None
    public_url: Callable | None = None
    inline: str | None = None           # 'days' | 'photos'
    help: str = ''

    @property
    def title_attr(self):
        return self.columns[0][0]


def _bool_choices(yes, no):
    return [('1', yes), ('0', no)]


TYPES = [
    ContentType(
        key='safaris', model=Itinerary, label='Safari', plural='Safaris', icon='compass',
        fields=['title', 'slug', 'destination', 'duration_days', 'difficulty', 'max_group_size', 'price_from',
                'featured_image', 'is_featured', 'overview', 'includes', 'excludes'],
        columns=[('title', 'Safari'), ('destination', 'Destination'), ('duration_days', 'Days'),
                 (lambda o: f'${o.price_from:,.0f}', 'From'), ('is_featured', 'Featured')],
        search=['title', 'destination__name'],
        filters={'featured': ('is_featured', _bool_choices('Featured', 'Not featured'))},
        image='featured_image', inline='days',
        public_url=lambda o: f'/itineraries/{o.slug}/',
        help='Safari packages with a day-by-day itinerary. Featured safaris appear on the home page.',
    ),
    ContentType(
        key='destinations', model=Destination, label='Destination', plural='Destinations', icon='pin',
        fields=['name', 'slug', 'country', 'short_description', 'featured_image', 'is_featured', 'description'],
        columns=[('name', 'Destination'), ('get_country_display', 'Region'), ('is_featured', 'Featured')],
        search=['name', 'short_description'],
        filters={'country': ('country', Destination.COUNTRY_CHOICES),
                 'featured': ('is_featured', _bool_choices('Featured', 'Not featured'))},
        image='featured_image',
        public_url=lambda o: f'/destinations/detail/{o.slug}/',
        help='Parks, reserves and places. Each safari belongs to one destination.',
    ),
    ContentType(
        key='posts', model=BlogPost, label='Blog post', plural='Blog posts', icon='pen',
        fields=['title', 'slug', 'category', 'featured_image', 'excerpt', 'is_published', 'published_date', 'content'],
        columns=[('title', 'Title'), ('category', 'Category'), ('is_published', 'Published'), ('published_date', 'Date')],
        search=['title', 'excerpt'],
        filters={'published': ('is_published', _bool_choices('Published', 'Draft'))},
        image='featured_image',
        public_url=lambda o: f'/blog/{o.slug}/' if o.is_published else None,
        help='Journal articles. Drafts stay hidden until you tick “Published”.',
    ),
    ContentType(
        key='categories', model=BlogCategory, label='Blog category', plural='Blog categories', icon='tag',
        fields=['name', 'slug'],
        columns=[('name', 'Category'), (lambda o: o.posts.count(), 'Posts')],
        search=['name'],
        public_url=lambda o: f'/blog/category/{o.slug}/' if o.posts.filter(is_published=True).exists() else None,
    ),
    ContentType(
        key='gallery', model=GalleryAlbum, label='Album', plural='Gallery', icon='camera',
        fields=['name', 'slug', 'description', 'cover_image'],
        columns=[('name', 'Album'), (lambda o: o.images.count(), 'Photos'), ('created_at', 'Created')],
        search=['name', 'description'],
        image='cover_image', inline='photos',
        public_url=lambda o: f'/gallery/album/{o.slug}/',
        help='Photo albums. Upload many photos at once when editing an album.',
    ),
    ContentType(
        key='testimonials', model=Testimonial, label='Testimonial', plural='Testimonials', icon='quote',
        fields=['client_name', 'client_photo', 'trip', 'rating', 'date', 'is_featured', 'review'],
        columns=[('client_name', 'Guest'), ('trip', 'Safari'), ('rating', 'Rating'), ('is_featured', 'Featured'), ('date', 'Date')],
        search=['client_name', 'review'],
        filters={'featured': ('is_featured', _bool_choices('Featured', 'Not featured'))},
        image='client_photo',
        public_url=lambda o: '/testimonials/',
        help='Guest reviews. Featured ones appear on the home page.',
    ),
    ContentType(
        key='team', model=TeamMember, label='Team member', plural='Team', icon='users',
        fields=['name', 'role', 'photo', 'order', 'bio'],
        columns=[('name', 'Name'), ('role', 'Role'), ('order', 'Order')],
        search=['name', 'role'],
        image='photo',
        public_url=lambda o: '/team/',
    ),
    ContentType(
        key='faqs', model=FAQ, label='FAQ', plural='FAQs', icon='help',
        fields=['category', 'question', 'order', 'answer'],
        columns=[('question', 'Question'), ('get_category_display', 'Category'), ('order', 'Order')],
        search=['question', 'answer'],
        filters={'category': ('category', FAQ.CATEGORY_CHOICES)},
        public_url=lambda o: '/faqs/',
    ),
]

BY_KEY = {t.key: t for t in TYPES}
