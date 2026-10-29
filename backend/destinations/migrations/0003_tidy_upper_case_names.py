from django.db import migrations

def tidy(apps, schema_editor):
    Destination = apps.get_model('destinations', 'Destination')
    for d in Destination.objects.all():
        letters = [c for c in d.name if c.isalpha()]
        if letters and all(c.isupper() for c in letters):
            d.name = d.name.title()
            d.save(update_fields=['name'])

class Migration(migrations.Migration):
    dependencies = [('destinations', '0002_regions_countries')]
    operations = [migrations.RunPython(tidy, migrations.RunPython.noop)]
