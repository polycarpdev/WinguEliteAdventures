from django.shortcuts import render, get_object_or_404
from .models import Destination

def destination_list(request, country_type):
    destinations = Destination.objects.filter(country=country_type)
    
    context = {
        'destinations': destinations,
        'country_type': country_type,
    }
    return render(request, 'destinations/list.html', context)

def destination_detail(request, slug):
    destination = get_object_or_404(Destination, slug=slug)
    related_itineraries = destination.itineraries.all()[:4]
    
    context = {
        'destination': destination,
        'related_itineraries': related_itineraries,
    }
    return render(request, 'destinations/detail.html', context)