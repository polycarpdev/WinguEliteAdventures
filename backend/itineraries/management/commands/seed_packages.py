from django.core.management.base import BaseCommand
from django.db import transaction

from destinations.models import Country, Destination
from itineraries.models import Itinerary, ItineraryDay

def ul(*items):
    return '<ul>' + ''.join(f'<li>{i}</li>' for i in items) + '</ul>'

def p(*paragraphs):
    return ''.join(f'<p>{x}</p>' for x in paragraphs)

INCLUDES = (
    'Accommodation on full board as listed (or similar)',
    'All park entrance fees and government taxes',
    'Private 4x4 safari vehicle with pop-up roof',
    'Professional English-speaking driver-guide',
    'Game drives and activities as listed',
    'Bottled drinking water on safari',
    'Hotel or airport pick-up and drop-off in Nairobi',
    '24/7 support from the Wingu team while you travel',
)
EXCLUDES = (
    'International flights and visa fees',
    'Travel insurance (strongly recommended)',
    'Optional activities not listed (e.g. hot-air balloon)',
    'Alcoholic and soft drinks',
    'Tips for your guide (around $10 per day is customary)',
    'Personal expenses and anything not mentioned above',
)

TSAVO = {
    'slug': 'tsavo-east-national-park',
    'name': 'Tsavo East National Park',
    'short_description': 'Kenya’s largest wilderness: red-dust elephants, wide open plains, Lugard Falls and Mudanda Rock.',
    'description': p(
        'Tsavo East is one of the oldest and largest national parks in Kenya, famous for its herds of elephants dusted '
        'red by the local soil. The open landscape makes for wonderful game viewing: lion, buffalo, giraffe, zebra and '
        'the rare fringe-eared oryx.',
        'Highlights include the Galana River and Lugard Falls, Mudanda Rock where wildlife gathers to drink, and the '
        'Aruba Dam. Tsavo is an easy add-on to a Mombasa or Diani beach holiday.',
    ),
}

PACKAGES = [
    {
        'slug': 'lake-nakuru-flamingo-rhino-safari-2-days',
        'title': '2-Day Lake Nakuru Flamingo & Rhino Safari',
        'destination': 'lake-nakuru-national-park',
        'days': 2, 'difficulty': 'easy', 'badge': 'Short break',
        'summary': 'Rhinos, flamingo-fringed shores and tree-climbing lions, an easy escape from Nairobi.',
        'overview': p(
            'A relaxed overnight safari to Lake Nakuru, one of the best places in Kenya to see both black and white '
            'rhino. Pink flamingos line the soda lake, Rothschild giraffes browse the acacia woodland, and lions are '
            'often found resting in the trees.',
        ),
        'days_detail': [
            ('Nairobi to Lake Nakuru, afternoon game drive', 'Lake Nakuru Lodge (or similar)', 'Lunch & dinner',
             'Morning pick-up in Nairobi and a scenic drive into the Great Rift Valley, with a stop at the escarpment '
             'viewpoint. Arrive for lunch, then head out on an afternoon game drive along the lake shore in search of '
             'rhino, buffalo and flamingos.'),
            ('Baboon Cliff, Makalia Falls and return to Nairobi', '', 'Breakfast & lunch',
             'An early game drive up to Baboon Cliff for sweeping views over the lake, then on to Makalia Falls. '
             'After brunch, drive back to Nairobi, arriving late afternoon.'),
        ],
    },
    {
        'slug': 'hells-gate-lake-naivasha-adventure-2-days',
        'title': '2-Day Hell’s Gate & Lake Naivasha Adventure',
        'destination': 'hells-gate-national-park',
        'days': 2, 'difficulty': 'moderate', 'badge': 'Active',
        'summary': 'Cycle among zebra and giraffe, hike the gorge, then cruise Lake Naivasha to see hippos.',
        'overview': p(
            'One of the few parks in Kenya you can explore by bike or on foot. Ride past grazing zebra and giraffe '
            'beneath Fischer’s Tower, walk through the dramatic Ol Njorowa gorge, then unwind with a boat ride on '
            'Lake Naivasha among hippos and fish eagles.',
        ),
        'days_detail': [
            ('Nairobi to Naivasha, boat ride and Crescent Island walk', 'Lake Naivasha Sopa Resort (or similar)',
             'Lunch & dinner',
             'Drive from Nairobi to Lake Naivasha (about 2 hours). After lunch, take a boat out to see hippos and '
             'birdlife, then land on Crescent Island for a guided walk among giraffe, zebra and wildebeest.'),
            ('Cycling and gorge hike in Hell’s Gate, return to Nairobi', '', 'Breakfast & lunch',
             'Enter Hell’s Gate National Park by bicycle (or vehicle), passing Fischer’s Tower and the steaming '
             'geothermal vents. Hike down into the gorge with a local guide, then drive back to Nairobi.'),
        ],
    },
    {
        'slug': 'lake-bogoria-hot-springs-escape-2-days',
        'title': '2-Day Lake Bogoria Hot Springs & Flamingo Escape',
        'destination': 'lake-bogoria-national-reserve',
        'days': 2, 'difficulty': 'easy', 'badge': '',
        'summary': 'Geysers, steaming hot springs and huge flocks of flamingos in the northern Rift Valley.',
        'overview': p(
            'Lake Bogoria is one of the Rift Valley’s most striking sights: geysers shooting from the shoreline, '
            'boiling springs and, in season, tens of thousands of lesser flamingos. Look out for the shy greater '
            'kudu in the bushland around the lake.',
        ),
        'days_detail': [
            ('Nairobi to Lake Bogoria', 'Lake Bogoria Spa Resort (or similar)', 'Lunch & dinner',
             'Drive north through the Rift Valley (about 5 hours) with a stop at the equator crossing. Afternoon visit '
             'to the hot springs and geysers on the western shore, and a relaxing soak in the resort’s natural spa.'),
            ('Flamingos and return to Nairobi', '', 'Breakfast & lunch',
             'Morning walk and drive along the lake shore to see the flamingos at their best, then return to Nairobi '
             'via Nakuru.'),
        ],
    },
    {
        'slug': 'amboseli-elephants-kilimanjaro-3-days',
        'title': '3-Day Amboseli Elephants & Kilimanjaro Views',
        'destination': 'amboseli-national-park',
        'days': 3, 'difficulty': 'easy', 'badge': 'Most requested',
        'summary': 'Big-tusked elephants beneath snow-capped Kilimanjaro, Africa’s most photographed view.',
        'overview': p(
            'Amboseli is famous for its large elephant herds set against the backdrop of Mount Kilimanjaro. Swamps fed '
            'by the mountain’s snowmelt draw elephants, buffalo, hippo and hundreds of bird species, while lion and '
            'cheetah hunt on the open plains.',
        ),
        'days_detail': [
            ('Nairobi to Amboseli, afternoon game drive', 'Amboseli Sopa Lodge (or similar)', 'Lunch & dinner',
             'Morning drive from Nairobi to Amboseli (about 4–5 hours). Check in for lunch, then enjoy your first '
             'game drive as the afternoon light settles over Kilimanjaro.'),
            ('Full day in Amboseli', 'Amboseli Sopa Lodge (or similar)', 'Full board',
             'Early morning game drive, the best time to see Kilimanjaro free of cloud. Visit Observation Hill for '
             'views over the swamps, and spend the afternoon with the elephant families. Optional visit to a Maasai '
             'village.'),
            ('Morning game drive and return to Nairobi', '', 'Breakfast & lunch',
             'A final sunrise game drive, breakfast at the lodge, then drive back to Nairobi.'),
        ],
    },
    {
        'slug': 'tsavo-east-red-elephants-3-days',
        'title': '3-Day Tsavo East Red Elephants Safari',
        'destination': 'tsavo-east-national-park',
        'days': 3, 'difficulty': 'easy', 'badge': 'Combined + beach',
        'summary': 'Red-dusted elephants and vast open plains. Easy to combine with Mombasa or Diani.',
        'overview': p(
            'Tsavo East is Kenya’s largest wilderness, home to the famous “red elephants” coloured by the rich soil. '
            'Expect big open landscapes, lion, buffalo and giraffe, plus Lugard Falls and Mudanda Rock. Start from '
            'Nairobi or Mombasa, and extend to the coast for a safari-and-beach holiday.',
        ),
        'days_detail': [
            ('Nairobi to Tsavo East', 'Voi Safari Lodge (or similar)', 'Lunch & dinner',
             'Travel from Nairobi to Voi by road or the Madaraka Express train. Afternoon game drive and sundowner '
             'overlooking the waterhole from the lodge.'),
            ('Full day in Tsavo East', 'Voi Safari Lodge (or similar)', 'Full board',
             'Explore along the Galana River to Lugard Falls, stop at Mudanda Rock where elephants come to drink, and '
             'visit Aruba Dam in the afternoon.'),
            ('Morning game drive and departure', '', 'Breakfast & lunch',
             'Final game drive after breakfast, then continue to Nairobi, Mombasa or your beach hotel in Diani.'),
        ],
    },
    {
        'slug': 'heart-of-masai-mara-3-days',
        'title': '3-Day Heart of Masai Mara Safari',
        'destination': 'masai-mara-national-reserve',
        'days': 3, 'difficulty': 'easy', 'badge': 'Classic', 'featured': False,
        'summary': 'Big Five game drives, the great plains and a visit to a Maasai village.',
        'overview': p(
            'Three days in Kenya’s most celebrated reserve: thrilling game drives across the Mara plains, a chance to '
            'see the Big Five, and an afternoon with the Maasai learning about their traditions.',
        ),
        'days_detail': [
            ('Nairobi to Masai Mara, afternoon game drive', 'Masai Mara Sopa Lodge (or similar)', 'Lunch & dinner',
             'Pick-up from your Nairobi hotel at 7:00 AM and a scenic 5–6 hour drive through the Great Rift Valley. '
             'Lunch at the lodge, then your first game drive in search of zebra, giraffe, buffalo, lion and cheetah.'),
            ('Full day in the Masai Mara and Maasai village', 'Masai Mara Sopa Lodge (or similar)', 'Full board',
             'Early morning game drive at 6:00 AM, prime time for predators. Midday visit to a Maasai village to learn '
             'about their culture, dances and crafts. Afternoon game drive across the plains.'),
            ('Breakfast and return to Nairobi', '', 'Breakfast',
             'A relaxed breakfast at the lodge, then the drive back to Nairobi, arriving in the afternoon.'),
        ],
    },
]

class Command(BaseCommand):
    help = 'Create the core Kenya packages (Nakuru, Hell’s Gate, Bogoria, Amboseli, Tsavo, Masai Mara) if missing.'

    @transaction.atomic
    def handle(self, *args, **opts):
        kenya = Country.objects.get(slug='kenya')
        tsavo, made = Destination.objects.get_or_create(
            slug=TSAVO['slug'],
            defaults={'name': TSAVO['name'], 'country': kenya, 'short_description': TSAVO['short_description'],
                      'description': TSAVO['description'], 'is_featured': True},
        )
        if made:
            self.stdout.write(self.style.WARNING('Created Tsavo East destination: upload its photo in the cockpit.'))

        mk = Itinerary.objects.filter(destination__slug='mount-kenya-national-park').first()
        if mk:
            mk.is_featured = True
            mk.summary = mk.summary or 'Summit Point Lenana at sunrise on a classic trek through forest and moorland.'
            mk.badge = mk.badge or 'Trek'
            mk.save()

        created = 0
        for pkg in PACKAGES:
            if Itinerary.objects.filter(slug=pkg['slug']).exists():
                continue
            dest = Destination.objects.get(slug=pkg['destination'])
            itinerary = Itinerary.objects.create(
                slug=pkg['slug'], title=pkg['title'], destination=dest,
                duration_days=pkg['days'], duration_nights=pkg['days'] - 1,
                difficulty=pkg['difficulty'], max_group_size=7, price_from=None,
                summary=pkg['summary'], badge=pkg['badge'], overview=pkg['overview'],
                featured_image=dest.featured_image.name if dest.featured_image else '',
                includes=ul(*INCLUDES), excludes=ul(*EXCLUDES),
                is_featured=pkg.get('featured', True),
            )
            for n, (title, stay, meals, text) in enumerate(pkg['days_detail'], start=1):
                ItineraryDay.objects.create(itinerary=itinerary, day_number=n, title=title,
                                            accommodation=stay, meals=meals, description=p(text))
            created += 1
        self.stdout.write(self.style.SUCCESS(f'Created {created} package(s). Prices show “On Request” until set.'))
