from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from bookings.models import Booking
from contact.models import ContactMessage

from ..forms import BookingUpdateForm
from . import staff_required


def _status_tabs(model, current):
    counts = dict(model.objects.values_list('status').annotate(n=Count('id')))
    tabs = [{'value': '', 'label': 'All', 'count': sum(counts.values()), 'active': not current}]
    tabs += [{'value': v, 'label': l, 'count': counts.get(v, 0), 'active': current == v} for v, l in model.STATUS_CHOICES]
    return tabs


def filtered_bookings(request):
    qs = Booking.objects.all()
    if status := request.GET.get('status'):
        qs = qs.filter(status=status)
    if q := request.GET.get('q', '').strip():
        qs = qs.filter(Q(full_name__icontains=q) | Q(email__icontains=q) | Q(country__icontains=q) | Q(phone__icontains=q))
    return qs


@staff_required
def booking_list(request):
    qs = filtered_bookings(request).select_related('destination', 'itinerary', 'trip_country')
    page = Paginator(qs, 25).get_page(request.GET.get('page'))
    return render(request, 'cockpit/bookings/list.html', {
        'page': page, 'tabs': _status_tabs(Booking, request.GET.get('status', '')), 'q': request.GET.get('q', ''),
    })


def _update(request, obj, url_name):
    form = BookingUpdateForm(request.POST, choices=obj.STATUS_CHOICES)
    if form.is_valid():
        before = obj.status
        obj.status = form.cleaned_data['status']
        obj.admin_notes = form.cleaned_data['admin_notes']
        if obj.status in ('contacted', 'quote_sent', 'replied') and not obj.replied_at:
            obj.replied_at = timezone.now()
        obj.save()
        messages.success(request, 'Saved.' if before == obj.status else f'Status changed to “{obj.get_status_display()}”.')
    return redirect(url_name, pk=obj.pk)


@staff_required
def booking_detail(request, pk):
    b = get_object_or_404(Booking.objects.select_related('destination', 'itinerary', 'trip_country'), pk=pk)
    if request.method == 'POST':
        return _update(request, b, 'cockpit:booking_detail')
    others = Booking.objects.filter(email__iexact=b.email).exclude(pk=b.pk)[:5]
    return render(request, 'cockpit/bookings/detail.html', {
        'b': b, 'others': others,
        'form': BookingUpdateForm(initial={'status': b.status, 'admin_notes': b.admin_notes}, choices=Booking.STATUS_CHOICES),
        'nights': (b.end_date - b.start_date).days if b.start_date and b.end_date else None,
        'whatsapp': ''.join(c for c in b.phone if c.isdigit()),
    })


@staff_required
def message_list(request):
    qs = ContactMessage.objects.all()
    if status := request.GET.get('status'):
        qs = qs.filter(status=status)
    if q := request.GET.get('q', '').strip():
        qs = qs.filter(Q(name__icontains=q) | Q(email__icontains=q) | Q(subject__icontains=q) | Q(message__icontains=q))
    page = Paginator(qs, 25).get_page(request.GET.get('page'))
    return render(request, 'cockpit/messages/list.html', {
        'page': page, 'tabs': _status_tabs(ContactMessage, request.GET.get('status', '')), 'q': request.GET.get('q', ''),
    })


@staff_required
def message_detail(request, pk):
    m = get_object_or_404(ContactMessage, pk=pk)
    if request.method == 'POST':
        return _update(request, m, 'cockpit:message_detail')
    if m.status == 'new':
        m.status = 'read'
        m.save(update_fields=['status', 'updated_at'])
    return render(request, 'cockpit/messages/detail.html', {
        'm': m,
        'form': BookingUpdateForm(initial={'status': m.status, 'admin_notes': m.admin_notes}, choices=ContactMessage.STATUS_CHOICES),
        'bookings': Booking.objects.filter(email__iexact=m.email)[:5],
    })
