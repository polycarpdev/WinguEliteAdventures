"""Regions > countries > destinations. Existing destinations move under Kenya
(East Africa); any marked 'international' go to an 'Other' place there."""
import django.db.models.deletion
from django.db import migrations, models

REGIONS = [
    ('East Africa', 'east-africa', 'Kenya, Tanzania, Uganda & Rwanda: the great migration, gorillas and the Swahili coast',
     'The cradle of the classic safari. Follow the great migration across the Masai Mara and Serengeti, '
     'trek to mountain gorillas in Uganda and Rwanda, then unwind on the white sands of the Indian Ocean.',
     ['Kenya', 'Tanzania', 'Zanzibar', 'Uganda', 'Rwanda']),
    ('Africa', 'africa', 'Egypt to the Cape: ancient wonders, wild deltas and winelands',
     'Beyond the east, a continent of contrasts: the pyramids and the Nile, Cape Town and the winelands, '
     'the Okavango Delta, Victoria Falls and the red dunes of Namibia.',
     ['Egypt', 'South Africa', 'Botswana', 'Namibia', 'Zambia', 'Zimbabwe', 'Morocco']),
    ('International', 'international', 'Dubai, the Maldives, Bali and beyond: handpicked escapes',
     'When you want to go further, we plan it with the same care: city lights in Dubai and Singapore, '
     'overwater villas in the Maldives, Bali’s temples and rice terraces, Malaysia’s islands and more.',
     ['Dubai', 'Maldives', 'Bali', 'Malaysia', 'Singapore', 'Thailand', 'Seychelles', 'Mauritius']),
]


def forwards(apps, schema_editor):
    Region = apps.get_model('destinations', 'Region')
    Country = apps.get_model('destinations', 'Country')
    Destination = apps.get_model('destinations', 'Destination')
    from django.utils.text import slugify

    countries = {}
    for r_order, (name, slug, tagline, description, places) in enumerate(REGIONS):
        region = Region.objects.create(name=name, slug=slug, tagline=tagline, description=description, order=r_order)
        for c_order, place in enumerate(places):
            countries[place] = Country.objects.create(region=region, name=place, slug=slugify(place), order=c_order)

    other = None
    for d in Destination.objects.all():
        if d.old_country == 'international':
            if other is None:
                other = Country.objects.create(region=Region.objects.get(slug='international'), name='Other', slug='other', order=99)
            d.country = other
        else:
            d.country = countries['Kenya']
        d.save(update_fields=['country'])


class Migration(migrations.Migration):
    dependencies = [('destinations', '0001_initial')]

    operations = [
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(blank=True, max_length=100, unique=True)),
                ('tagline', models.CharField(blank=True, help_text='One line shown in the menu and on cards.', max_length=200)),
                ('description', models.TextField(blank=True, help_text='Intro paragraph on the region page.')),
                ('image', models.ImageField(blank=True, upload_to='regions/')),
                ('order', models.PositiveIntegerField(default=0, help_text='Lower numbers come first.')),
            ],
            options={'ordering': ['order', 'name']},
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(blank=True, max_length=100, unique=True)),
                ('intro', models.TextField(blank=True, help_text='Intro paragraph on the country page.')),
                ('image', models.ImageField(blank=True, upload_to='countries/')),
                ('order', models.PositiveIntegerField(default=0, help_text='Lower numbers come first.')),
                ('region', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='countries', to='destinations.region')),
            ],
            options={'ordering': ['region__order', 'order', 'name'], 'verbose_name_plural': 'Countries'},
        ),
        migrations.RenameField('destination', 'country', 'old_country'),
        migrations.AddField(
            model_name='destination',
            name='country',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='destinations', to='destinations.country'),
        ),
        migrations.RunPython(forwards, migrations.RunPython.noop),
        migrations.RemoveField('destination', 'old_country'),
        migrations.AlterField(
            model_name='destination',
            name='country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='destinations', to='destinations.country'),
        ),
    ]
