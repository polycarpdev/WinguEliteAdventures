from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HeroSlide',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('eyebrow', models.CharField(blank=True, help_text='Small script line above the headline, e.g. "Karibu Kenya".', max_length=60)),
                ('headline', models.CharField(help_text='Main line, e.g. "Luxury Kenya safaris,".', max_length=90)),
                ('highlight', models.CharField(blank=True, help_text='Second line in gold italics, e.g. "crafted above the ordinary".', max_length=90)),
                ('subtitle', models.CharField(blank=True, max_length=220)),
                ('image_desktop', models.ImageField(help_text='2560 × 1280 px (2:1). Keep the subject in the right half.', upload_to='hero/', verbose_name='Desktop image')),
                ('image_mobile', models.ImageField(blank=True, help_text='1080 × 2340 px (9:19.5). Keep the subject in the top half. Optional: the desktop image is cropped if missing.', upload_to='hero/', verbose_name='Phone image')),
                ('alt', models.CharField(blank=True, help_text='For Google and screen readers.', max_length=160, verbose_name='Image description')),
                ('button_label', models.CharField(default='Book Now', max_length=40)),
                ('button_url', models.CharField(default='/bookings/', help_text='A page on the site, e.g. /packages/', max_length=200)),
                ('second_label', models.CharField(blank=True, default='Explore packages', max_length=40, verbose_name='Second button label')),
                ('second_url', models.CharField(blank=True, default='/packages/', max_length=200, verbose_name='Second button link')),
                ('order', models.PositiveIntegerField(default=0, help_text='Lower numbers show first.')),
                ('is_active', models.BooleanField(default=True, verbose_name='Show on website')),
            ],
            options={
                'ordering': ['order', 'id'],
            },
        ),
    ]
