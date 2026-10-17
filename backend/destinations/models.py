from django.db import models
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field  # ← Correct: CKEditor 5


class Destination(models.Model):
    COUNTRY_CHOICES = [('kenya', 'Kenya'), ('international', 'International')]
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    country = models.CharField(max_length=20, choices=COUNTRY_CHOICES, default='kenya')
    
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