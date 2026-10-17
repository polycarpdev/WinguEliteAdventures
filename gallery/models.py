from django.db import models

class GalleryAlbum(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='gallery/albums/')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class GalleryImage(models.Model):
    album = models.ForeignKey(GalleryAlbum, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='gallery/images/')
    caption = models.CharField(max_length=300, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.album.name} - {self.caption[:50]}"