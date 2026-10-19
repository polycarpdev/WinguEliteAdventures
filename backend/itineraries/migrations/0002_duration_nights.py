from django.db import migrations, models


def fill_nights(apps, schema_editor):
    Itinerary = apps.get_model('itineraries', 'Itinerary')
    for i in Itinerary.objects.all():
        i.duration_nights = max(i.duration_days - 1, 0)
        i.save(update_fields=['duration_nights'])


class Migration(migrations.Migration):
    dependencies = [('itineraries', '0001_initial')]

    operations = [
        migrations.AlterField('itinerary', 'duration_days', models.PositiveIntegerField(verbose_name='Days')),
        migrations.AddField('itinerary', 'duration_nights', models.PositiveIntegerField(null=True, blank=True, verbose_name='Nights')),
        migrations.RunPython(fill_nights, migrations.RunPython.noop),
        migrations.AlterField(
            'itinerary', 'duration_nights',
            models.PositiveIntegerField(blank=True, help_text='Leave blank for days − 1.', verbose_name='Nights'),
        ),
    ]
