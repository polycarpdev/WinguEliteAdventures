import csv

from django.db.models import Count, Sum
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from analytics.models import PageView
from bookings.models import Booking
from contact.models import ContactMessage

from .. import stats
from . import staff_required


@staff_required
def dashboard(request):
    t = stats.traffic(30)
    bookings_30 = Booking.objects.filter(created_at__gte=stats.since(30))
    prev_bookings = Booking.objects.filter(created_at__gte=stats.since(60), created_at__lt=stats.since(30)).count()
    n_bookings = bookings_30.count()
    return render(request, 'cockpit/dashboard.html', {
        'traffic': t,
        'series': stats.daily_series(t['qs'], 30),
        'n_bookings': n_bookings,
        'bookings_delta': stats.delta(n_bookings, prev_bookings),
        'conversion': round(n_bookings * 100 / t['visitors'], 1) if t['visitors'] else None,
        'pipeline_value': stats.booking_value(Booking.objects.filter(status__in=stats.PIPELINE)),
        'top_pages': stats.top(t['qs'], 'path', 6),
        'top_referrers': stats.top(t['qs'].filter(is_entry=True), 'referrer', 6),
        'recent_bookings': Booking.objects.select_related('destination', 'itinerary')[:6],
        'recent_messages': ContactMessage.objects.all()[:5],
        'upcoming': Booking.objects.filter(status__in=stats.WON, start_date__gte=timezone.localdate())
                                   .select_related('destination').order_by('start_date')[:5],
    })


@staff_required
def analytics(request):
    key, days = stats.range_days(request)
    t = stats.traffic(days)
    qs = t['qs']
    return render(request, 'cockpit/analytics.html', {
        'range': key, 'options': stats.RANGE_OPTIONS,
        'traffic': t,
        'series': stats.daily_series(qs, min(days, 90)),
        'views_series': stats.daily_series(qs, min(days, 90), value='views'),
        'top_pages': stats.top(qs, 'path', 12),
        'entry_pages': stats.top(qs.filter(is_entry=True), 'path', 8),
        'referrers': stats.top(qs.filter(is_entry=True), 'referrer', 10),
        'devices': stats.share(qs, 'device', PageView.DEVICE_CHOICES),
        'browsers': stats.share(qs, 'browser'),
        'regions': stats.top(qs, 'timezone', 10),
        'languages': stats.top(qs, 'language', 6),
    })


def _travellers(qs):
    t = qs.aggregate(a=Sum('adults'), c=Sum('children'))
    a, c = t['a'] or 0, t['c'] or 0
    return {'adults': a, 'children': c, 'total': a + c}


@staff_required
def reports(request):
    key, days = stats.range_days(request, default='365')
    qs = Booking.objects.filter(created_at__gte=stats.since(days))
    won = qs.filter(status__in=stats.WON)
    return render(request, 'cockpit/reports.html', {
        'range': key, 'options': stats.RANGE_OPTIONS,
        'total': qs.count(),
        'won': won.count(),
        'win_rate': round(won.count() * 100 / qs.count()) if qs.count() else None,
        'travellers': _travellers(qs),
        'won_value': stats.booking_value(won),
        'pipeline_value': stats.booking_value(qs.filter(status__in=stats.PIPELINE)),
        'monthly': stats.monthly_series(Booking.objects.all(), 12),
        'funnel': stats.funnel(qs),
        'by_destination': stats.top(qs.filter(destination__isnull=False), 'destination__name', 8, exclude_blank=False),
        'by_package': stats.top(qs.filter(itinerary__isnull=False), 'itinerary__title', 8, exclude_blank=False),
        'sources': stats.top(qs, 'how_did_you_hear', 8),
        'countries': stats.top(qs, 'country', 8),
        'accommodation': stats.share(qs, 'accommodation_preference', Booking.ACCOMMODATION_CHOICES),
        'messages_count': ContactMessage.objects.filter(created_at__gte=stats.since(days)).count(),
    })


@staff_required
def bookings_csv(request):
    from .enquiries import filtered_bookings
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="bookings-{timezone.localdate()}.csv"'
    w = csv.writer(response)
    w.writerow(['Received', 'Status', 'Name', 'Email', 'Phone', 'Country', 'Destination', 'Package',
                'Start', 'End', 'Days', 'Nights', 'Adults', 'Children', 'Accommodation', 'Source', 'Requests', 'Notes'])
    for b in filtered_bookings(request).select_related('destination', 'itinerary', 'trip_country'):
        w.writerow([timezone.localtime(b.created_at).strftime('%Y-%m-%d %H:%M'), b.get_status_display(), b.full_name,
                    b.email, b.phone, b.country, b.place, b.itinerary or '', b.start_date, b.end_date,
                    b.duration_days or '', b.duration_nights or '', b.adults, b.children, b.get_accommodation_preference_display(), b.how_did_you_hear,
                    b.special_requests, b.admin_notes])
    return response
