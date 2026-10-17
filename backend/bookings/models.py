from django.db import models
from itineraries.models import Itinerary
from destinations.models import Destination

class Booking(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('quote_sent', 'Quote Sent'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    ACCOMMODATION_CHOICES = [
        ('budget', 'Budget'),
        ('standard', 'Standard'),
        ('luxury', 'Luxury'),
    ]
    
    # Personal Information
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    
    # Trip Details
    destination = models.ForeignKey(Destination, on_delete=models.SET_NULL, null=True)
    itinerary = models.ForeignKey(Itinerary, on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    adults = models.PositiveIntegerField(default=1)
    children = models.PositiveIntegerField(default=0)
    accommodation_preference = models.CharField(max_length=20, choices=ACCOMMODATION_CHOICES)
    
    # Additional Info
    special_requests = models.TextField(blank=True)
    how_did_you_hear = models.CharField(max_length=200, blank=True)
    
    # Admin fields
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    admin_notes = models.TextField(blank=True)
    replied_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.full_name} - {self.destination} ({self.status})"