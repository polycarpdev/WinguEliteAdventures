from django.db import models
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field  # ← Correct
from destinations.models import Destination


class Itinerary(models.Model):
    DIFFICULTY_CHOICES = [('easy', 'Easy'), ('moderate', 'Moderate'), ('challenging', 'Challenging')]
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='itineraries')
    duration_days = models.PositiveIntegerField('Days')
    duration_nights = models.PositiveIntegerField('Nights', blank=True, help_text='Leave blank for days − 1.')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='moderate')
    max_group_size = models.PositiveIntegerField(default=10)
    price_from = models.DecimalField(max_digits=10, decimal_places=2)
    
    # FIXED: Use CKEditor5Field
    overview = CKEditor5Field('Overview', config_name='default')
    featured_image = models.ImageField(upload_to='itineraries/')
    includes = CKEditor5Field('Includes', config_name='default', blank=True)
    excludes = CKEditor5Field('Excludes', config_name='default', blank=True)
    
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_featured', '-created_at']
        verbose_name_plural = 'Itineraries'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.duration_nights is None:
            self.duration_nights = max(self.duration_days - 1, 0)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def duration_label(self):
        d, n = self.duration_days, self.duration_nights
        return f"{d} day{'s' if d != 1 else ''} / {n} night{'s' if n != 1 else ''}"


class ItineraryDay(models.Model):
    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE, related_name='days')
    day_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    
    # FIXED: Use CKEditor5Field
    description = CKEditor5Field('Description', config_name='default')
    
    class Meta:
        ordering = ['day_number']
        unique_together = ['itinerary', 'day_number']
    
    def __str__(self):
        return f"Day {self.day_number}: {self.title}"