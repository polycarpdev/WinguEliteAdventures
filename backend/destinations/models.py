from django.db import models
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field  # ← Correct: CKEditor 5


RESERVED_SLUGS = {'detail'}  # /destinations/detail/<slug>/ is the destination page URL


class Region(models.Model):
    """Top-level grouping in the Destinations menu, e.g. East Africa, Africa, International."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    tagline = models.CharField(max_length=200, blank=True, help_text='One line shown in the menu and on cards.')
    description = models.TextField(blank=True, help_text='Intro paragraph on the region page.')
    image = models.ImageField(upload_to='regions/', blank=True)
    order = models.PositiveIntegerField(default=0, help_text='Lower numbers come first.')

    class Meta:
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if self.slug in RESERVED_SLUGS:
            self.slug = f'{self.slug}-region'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Country(models.Model):
    """A country or place inside a region (Kenya, Tanzania, Dubai, Bali...)."""
    region = models.ForeignKey(Region, on_delete=models.PROTECT, related_name='countries')
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    intro = models.TextField(blank=True, help_text='Intro paragraph on the country page.')
    image = models.ImageField(upload_to='countries/', blank=True)
    order = models.PositiveIntegerField(default=0, help_text='Lower numbers come first.')

    class Meta:
        ordering = ['region__order', 'order', 'name']
        verbose_name_plural = 'Countries'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} ({self.region})'


class Destination(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.PROTECT, related_name='destinations')
    
    # FIXED: Use CKEditor5Field
    description = CKEditor5Field('Description', config_name='default')
    
    short_description = models.TextField(max_length=300)
    featured_image = models.ImageField(upload_to='destinations/')
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_featured', '-created_at']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name