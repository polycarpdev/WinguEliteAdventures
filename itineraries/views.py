from django.shortcuts import render, get_object_or_404
from .models import Itinerary
from destinations.models import Destination

def itinerary_list(request):
    itineraries = Itinerary.objects.all()
    destinations = Destination.objects.all()
    
    # Filtering
    destination_filter = request.GET.get('destination')
    difficulty_filter = request.GET.get('difficulty')
    
    if destination_filter:
        itineraries = itineraries.filter(destination__slug=destination_filter)
    
    if difficulty_filter:
        itineraries = itineraries.filter(difficulty=difficulty_filter)
    
    context = {
        'itineraries': itineraries,
        'destinations': destinations,
    }
    return render(request, 'itineraries/list.html', context)

def itinerary_detail(request, slug):
    itinerary = get_object_or_404(Itinerary, slug=slug)
    days = itinerary.days.all()
    related_testimonials = itinerary.testimonials.all()[:3]
    
    context = {
        'itinerary': itinerary,
        'days': days,
        'related_testimonials': related_testimonials,
    }
    return render(request, 'itineraries/detail.html', context)