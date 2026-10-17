from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Booking
from destinations.models import Destination
from itineraries.models import Itinerary

def booking_create(request):
    if request.method == 'POST':
        booking = Booking.objects.create(
            full_name=request.POST.get('full_name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            country=request.POST.get('country'),
            destination_id=request.POST.get('destination'),
            itinerary_id=request.POST.get('itinerary') if request.POST.get('itinerary') else None,
            start_date=request.POST.get('start_date'),
            end_date=request.POST.get('end_date'),
            adults=request.POST.get('adults'),
            children=request.POST.get('children', 0),
            accommodation_preference=request.POST.get('accommodation_preference'),
            special_requests=request.POST.get('special_requests', ''),
            how_did_you_hear=request.POST.get('how_did_you_hear', ''),
        )
        
        # Send email notification to admin
        subject = f'New Booking Request from {booking.full_name}'
        message = f'''
        New booking request received:
        
        Name: {booking.full_name}
        Email: {booking.email}
        Phone: {booking.phone}
        Destination: {booking.destination}
        Dates: {booking.start_date} to {booking.end_date}
        Travelers: {booking.adults} adults, {booking.children} children
        
        View details in the admin panel.
        '''
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMIN_EMAIL],
                fail_silently=False,
            )
        except:
            pass
        
        messages.success(request, 'Your booking request has been submitted successfully! We will contact you shortly.')
        return redirect('bookings:success')
    
    destinations = Destination.objects.all()
    itineraries = Itinerary.objects.all()
    
    context = {
        'destinations': destinations,
        'itineraries': itineraries,
    }
    return render(request, 'bookings/create.html', context)

def booking_success(request):
    return render(request, 'bookings/success.html')