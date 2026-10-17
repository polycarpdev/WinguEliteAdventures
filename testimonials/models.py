from django.db import models
from itineraries.models import Itinerary

class Testimonial(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    
    client_name = models.CharField(max_length=100)
    client_photo = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    trip = models.ForeignKey(Itinerary, on_delete=models.SET_NULL, null=True, blank=True, related_name='testimonials')
    rating = models.IntegerField(choices=RATING_CHOICES, default=5)
    review = models.TextField()
    date = models.DateField()
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_featured', '-date']
    
    def __str__(self):
        return f"{self.client_name} - {self.rating} stars"