import django.db.models.deletion
from django.db import migrations, models

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('destinations', '0001_initial'),
        ('itineraries', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=20)),
                ('country', models.CharField(max_length=100)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('adults', models.PositiveIntegerField(default=1)),
                ('children', models.PositiveIntegerField(default=0)),
                ('accommodation_preference', models.CharField(choices=[('budget', 'Budget'), ('standard', 'Standard'), ('luxury', 'Luxury')], max_length=20)),
                ('special_requests', models.TextField(blank=True)),
                ('how_did_you_hear', models.CharField(blank=True, max_length=200)),
                ('status', models.CharField(choices=[('new', 'New'), ('contacted', 'Contacted'), ('quote_sent', 'Quote Sent'), ('confirmed', 'Confirmed'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='new', max_length=20)),
                ('admin_notes', models.TextField(blank=True)),
                ('replied_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('destination', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='destinations.destination')),
                ('itinerary', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='itineraries.itinerary')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
