from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from bookings.models import Booking
from contact.models import ContactMessage

@login_required
def dashboard(request):
    recent_bookings = Booking.objects.all()[:10]
    recent_contacts = ContactMessage.objects.all()[:10]
    
    # Stats
    new_bookings = Booking.objects.filter(status='new').count()
    new_messages = ContactMessage.objects.filter(status='new').count()
    
    context = {
        'recent_bookings': recent_bookings,
        'recent_contacts': recent_contacts,
        'new_bookings': new_bookings,
        'new_messages': new_messages,
    }
    return render(request, 'cockpit/dashboard.html', context)

@login_required
def booking_list(request):
    bookings = Booking.objects.all()
    
    # Filtering
    status_filter = request.GET.get('status')
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    
    context = {'bookings': bookings}
    return render(request, 'cockpit/booking_list.html', context)

@login_required
def booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_status':
            booking.status = request.POST.get('status')
            booking.save()
            messages.success(request, 'Booking status updated successfully!')
        
        elif action == 'add_note':
            booking.admin_notes = request.POST.get('admin_notes')
            booking.save()
            messages.success(request, 'Note added successfully!')
        
        return redirect('cockpit:booking_detail', pk=pk)
    
    context = {'booking': booking}
    return render(request, 'cockpit/booking_detail.html', context)

@login_required
def contact_list(request):
    contacts = ContactMessage.objects.all()
    
    # Filtering
    status_filter = request.GET.get('status')
    if status_filter:
        contacts = contacts.filter(status=status_filter)
    
    context = {'contacts': contacts}
    return render(request, 'cockpit/contact_list.html', context)

@login_required
def contact_detail(request, pk):
    contact = get_object_or_404(ContactMessage, pk=pk)
    
    # Mark as read
    if contact.status == 'new':
        contact.status = 'read'
        contact.save()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_status':
            contact.status = request.POST.get('status')
            contact.save()
            messages.success(request, 'Contact status updated successfully!')
        
        elif action == 'add_note':
            contact.admin_notes = request.POST.get('admin_notes')
            contact.save()
            messages.success(request, 'Note added successfully!')
        
        return redirect('cockpit:contact_detail', pk=pk)
    
    context = {'contact': contact}
    return render(request, 'cockpit/contact_detail.html', context)