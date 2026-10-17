from django.db import migrations, models
import django_ckeditor_5.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('destinations', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Itinerary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('slug', models.SlugField(blank=True, max_length=200, unique=True)),
                ('duration_days', models.PositiveIntegerField()),
                ('difficulty', models.CharField(choices=[('easy', 'Easy'), ('moderate', 'Moderate'), ('challenging', 'Challenging')], default='moderate', max_length=20)),
                ('max_group_size', models.PositiveIntegerField(default=10)),
                ('price_from', models.DecimalField(decimal_places=2, max_digits=10)),
                ('overview', django_ckeditor_5.fields.CKEditor5Field('Overview', config_name='default')),
                ('featured_image', models.ImageField(upload_to='itineraries/')),
                ('includes', django_ckeditor_5.fields.CKEditor5Field('Includes', blank=True, config_name='default')),
                ('excludes', django_ckeditor_5.fields.CKEditor5Field('Excludes', blank=True, config_name='default')),
                ('is_featured', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),  # ← FIXED
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('destination', models.ForeignKey(on_delete=models.CASCADE, related_name='itineraries', to='destinations.destination')),
            ],
            options={
                'verbose_name_plural': 'Itineraries',
                'ordering': ['-is_featured', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ItineraryDay',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_number', models.PositiveIntegerField()),
                ('title', models.CharField(max_length=200)),
                ('description', django_ckeditor_5.fields.CKEditor5Field('Description', config_name='default')),
                ('itinerary', models.ForeignKey(on_delete=models.CASCADE, related_name='days', to='itineraries.itinerary')),
            ],
            options={
                'ordering': ['day_number'],
                'unique_together': {('itinerary', 'day_number')},
            },
        ),
    ]
