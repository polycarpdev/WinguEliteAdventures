from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('itineraries', '0002_duration_nights'),
    ]

    operations = [
        migrations.AddField(
            model_name='itinerary',
            name='badge',
            field=models.CharField(blank=True, default='', help_text='Optional label on the card photo, e.g. “Most requested”, “Combined”, “Beach”.', max_length=30),
        ),
        migrations.AddField(
            model_name='itinerary',
            name='summary',
            field=models.CharField(blank=True, default='', help_text='One or two lines for package cards. Leave blank to use the overview.', max_length=180),
        ),
        migrations.AddField(
            model_name='itineraryday',
            name='accommodation',
            field=models.CharField(blank=True, default='', help_text='e.g. Masai Mara Sopa Lodge (or similar)', max_length=150),
        ),
        migrations.AddField(
            model_name='itineraryday',
            name='meals',
            field=models.CharField(blank=True, default='', help_text='e.g. Full board, Breakfast & dinner', max_length=60),
        ),
        migrations.AlterField(
            model_name='itinerary',
            name='price_from',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Per person, USD. Leave blank to show “On Request”.', max_digits=10, null=True),
        ),
    ]
