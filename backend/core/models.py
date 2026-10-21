from django.db import models

class TeamMember(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    bio = models.TextField()
    photo = models.ImageField(upload_to='team/')
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    
    class Meta:
        ordering = ['order', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.role}"


class FAQ(models.Model):
    CATEGORY_CHOICES = [
        ('booking', 'Booking'),
        ('payment', 'Payment'),
        ('packing', 'Packing'),
        ('safari_tips', 'Safari Tips'),
        ('general', 'General'),
    ]
    
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    question = models.CharField(max_length=300)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['category', 'order']
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'
    
    def __str__(self):
        return self.question

MAX_HERO_SLIDES = 5


class HeroSlide(models.Model):
    """A slide in the home page hero. Desktop image 2560x1280, phone image 1080x2340."""
    eyebrow = models.CharField(max_length=60, blank=True, help_text='Small script line above the headline, e.g. "Karibu Kenya".')
    headline = models.CharField(max_length=90, help_text='Main line, e.g. "Luxury Kenya safaris,".')
    highlight = models.CharField(max_length=90, blank=True, help_text='Second line in gold italics, e.g. "crafted above the ordinary".')
    subtitle = models.CharField(max_length=220, blank=True)
    image_desktop = models.ImageField('Desktop image', upload_to='hero/',
                                      help_text='2560 × 1280 px (2:1). Keep the subject in the right half.')
    image_mobile = models.ImageField('Phone image', upload_to='hero/', blank=True,
                                     help_text='1080 × 2340 px (9:19.5). Keep the subject in the top half. '
                                               'Optional: the desktop image is cropped if missing.')
    alt = models.CharField('Image description', max_length=160, blank=True, help_text='For Google and screen readers.')
    button_label = models.CharField(max_length=40, default='Book Now')
    button_url = models.CharField(max_length=200, default='/bookings/', help_text='A page on the site, e.g. /packages/')
    second_label = models.CharField('Second button label', max_length=40, blank=True, default='Explore packages')
    second_url = models.CharField('Second button link', max_length=200, blank=True, default='/packages/')
    order = models.PositiveIntegerField(default=0, help_text='Lower numbers show first.')
    is_active = models.BooleanField('Show on website', default=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.headline} {self.highlight}'.strip()

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.is_active:
            live = HeroSlide.objects.filter(is_active=True).exclude(pk=self.pk).count()
            if live >= MAX_HERO_SLIDES:
                raise ValidationError(
                    f'The home page shows at most {MAX_HERO_SLIDES} slides. Untick “Show on website” on another slide first, '
                    'or save this one with it unticked.')
