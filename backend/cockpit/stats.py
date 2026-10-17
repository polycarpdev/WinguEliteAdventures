"""Query helpers for the dashboard, analytics and reports."""
from datetime import date, timedelta

from django.db.models import Count, F, Sum
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone

from analytics.models import PageView
from bookings.models import Booking

RANGES = {'7': 7, '30': 30, '90': 90, '365': 365}
RANGE_OPTIONS = [('7', '7 days'), ('30', '30 days'), ('90', '90 days'), ('365', '12 months')]


def range_days(request, default='30'):
    key = request.GET.get('range', default)
    key = key if key in RANGES else default
    return key, RANGES[key]


def since(days):
    return timezone.now() - timedelta(days=days)


def daily_series(qs, days, value='visitors'):
    """[{label, value, date}] for the last `days` days, zero-filled."""
    agg = Count('visitor', distinct=True) if value == 'visitors' else Count('id')
    rows = dict(qs.annotate(d=TruncDate('created_at')).values('d').annotate(v=agg).values_list('d', 'v'))
    today = timezone.localdate()
    out = []
    for i in range(days - 1, -1, -1):
        d = today - timedelta(days=i)
        out.append({'date': d, 'label': d.strftime('%d %b'), 'value': rows.get(d, 0)})
    return out


def monthly_series(qs, months=12, field='created_at'):
    rows = dict(qs.annotate(m=TruncMonth(field)).values('m').annotate(v=Count('id')).values_list('m', 'v'))
    rows = {(k.date() if hasattr(k, 'date') else k).replace(day=1): v for k, v in rows.items() if k}
    first = timezone.localdate().replace(day=1)
    out = []
    for i in range(months - 1, -1, -1):
        y, m = divmod(first.month - 1 - i, 12)
        d = date(first.year + y, m + 1, 1)
        out.append({'date': d, 'label': d.strftime('%b'), 'value': rows.get(d, 0)})
    return out


def traffic(days):
    qs = PageView.objects.filter(created_at__gte=since(days))
    prev = PageView.objects.filter(created_at__gte=since(days * 2), created_at__lt=since(days))
    visitors = visitors_count(qs)
    prev_visitors = visitors_count(prev)
    views = qs.count()
    return {
        'qs': qs,
        'visitors': visitors,
        'visitors_delta': delta(visitors, prev_visitors),
        'views': views,
        'views_delta': delta(views, prev.count()),
        'per_visitor': round(views / visitors, 1) if visitors else 0,
    }


def visitors_count(qs):
    # Visitor hashes rotate daily, so unique (day, visitor) pairs = visits.
    return qs.annotate(d=TruncDate('created_at')).values('d', 'visitor').distinct().count()


def delta(now, before):
    if not before:
        return None
    return round((now - before) * 100 / before)


def top(qs, field, n=8, exclude_blank=True):
    rows = qs.exclude(**{field: ''}) if exclude_blank else qs
    rows = list(rows.values(field).annotate(v=Count('id')).order_by('-v')[:n])
    peak = rows[0]['v'] if rows else 1
    return [{'label': r[field] or '(direct)', 'value': r['v'], 'pct': round(r['v'] * 100 / peak)} for r in rows]


def share(qs, field, choices=None):
    rows = list(qs.values(field).annotate(v=Count('id')).order_by('-v'))
    total = sum(r['v'] for r in rows) or 1
    labels = dict(choices or [])
    return [{'label': labels.get(r[field], r[field] or 'Other'), 'value': r['v'], 'pct': round(r['v'] * 100 / total)} for r in rows]


def booking_value(qs):
    """Estimated value: package 'from' price x adults, for bookings tied to a package."""
    return qs.filter(itinerary__isnull=False).aggregate(v=Sum(F('itinerary__price_from') * F('adults')))['v'] or 0


PIPELINE = ['new', 'contacted', 'quote_sent']
WON = ['confirmed', 'completed']


def funnel(qs):
    counts = dict(qs.values_list('status').annotate(v=Count('id')))
    total = sum(counts.values()) or 1
    return [
        {'value': s, 'label': label, 'count': counts.get(s, 0), 'pct': round(counts.get(s, 0) * 100 / total)}
        for s, label in Booking.STATUS_CHOICES
    ]
