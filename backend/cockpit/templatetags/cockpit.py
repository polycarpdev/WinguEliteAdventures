from datetime import datetime, timezone as dt_tz

from django import template
from django.db.models.fields.files import FieldFile
from django.utils import timezone
from django.utils.html import format_html, escape
from django.utils.safestring import mark_safe
from django.utils.timesince import timesince

register = template.Library()

ICONS = {
    'home': '<path d="m3 10 9-7 9 7v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 22V12h6v10"/>',
    'chart': '<path d="M3 3v18h18"/><path d="m7 15 4-4 3 3 5-6"/>',
    'report': '<rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 7h8M8 11h8M8 15h5"/>',
    'calendar': '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
    'mail': '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 6L2 7"/>',
    'compass': '<circle cx="12" cy="12" r="10"/><path d="m16.2 7.8-2.1 6.3-6.3 2.1 2.1-6.3z"/>',
    'pin': '<path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
    'pen': '<path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z"/>',
    'tag': '<path d="M20.6 13.4 13.4 20.6a2 2 0 0 1-2.8 0L3 13V3h10l7.6 7.6a2 2 0 0 1 0 2.8Z"/><circle cx="7.5" cy="7.5" r="1.5"/>',
    'camera': '<path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3z"/><circle cx="12" cy="13" r="3"/>',
    'quote': '<path d="M3 21c3 0 7-1 7-8V5H3v8h4c0 3-2 5-4 5z"/><path d="M14 21c3 0 7-1 7-8V5h-7v8h4c0 3-2 5-4 5z"/>',
    'users': '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    'help': '<circle cx="12" cy="12" r="10"/><path d="M9.1 9a3 3 0 0 1 5.8 1c0 2-3 3-3 3"/><path d="M12 17h.01"/>',
    'external': '<path d="M15 3h6v6"/><path d="M10 14 21 3"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>',
    'plus': '<path d="M12 5v14M5 12h14"/>',
    'search': '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    'edit': '<path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z"/>',
    'trash': '<path d="M3 6h18"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>',
    'download': '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="m7 10 5 5 5-5"/><path d="M12 15V3"/>',
    'phone': '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/>',
    'whatsapp': '<path d="M3 21l1.65-3.8a9 9 0 1 1 3.4 2.9L3 21"/>',
    'menu': '<path d="M4 7h16M4 12h16M4 17h10"/>',
    'x': '<path d="M18 6 6 18M6 6l12 12"/>',
    'logout': '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><path d="m16 17 5-5-5-5"/><path d="M21 12H9"/>',
    'settings': '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1Z"/>',
    'arrow-left': '<path d="M19 12H5"/><path d="m12 19-7-7 7-7"/>',
    'check': '<path d="M20 6 9 17l-5-5"/>',
    'star': '<path d="M12 2.5l2.9 6 6.6.9-4.8 4.6 1.2 6.5L12 17.4l-5.9 3.1 1.2-6.5L2.5 9.4l6.6-.9z" fill="currentColor" stroke="none"/>',
    'globe': '<circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>',
    'map': '<path d="m3 6 6-3 6 3 6-3v15l-6 3-6-3-6 3z"/><path d="M9 3v15M15 6v15"/>',
    'image': '<rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-5-5L5 21"/>',
}

@register.simple_tag
def icon(name, cls=''):
    return mark_safe(
        f'<svg class="i {escape(cls)}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" '
        f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS.get(name, "")}</svg>'
    )

@register.simple_tag
def bar_chart(series, height=180, color='var(--olive)', unit=''):
    n = len(series) or 1
    peak = max((p['value'] for p in series), default=0) or 1
    w = 100 / n
    gap = min(w * 0.25, 0.8)
    bars, labels = [], []
    step = max(1, n // 8)
    for i, p in enumerate(series):
        h = p['value'] / peak * 100
        x = i * w + gap / 2
        tip = f"{p['label']}: {p['value']:,}{unit}"
        bars.append(
            f'<rect x="{x:.3f}%" y="{100 - h:.3f}%" width="{w - gap:.3f}%" height="{max(h, 0.6):.3f}%" rx="2" '
            f'fill="{color}" opacity="{0.35 if p["value"] == 0 else 1}"><title>{escape(tip)}</title></rect>'
        )
        if i % step == 0 or i == n - 1:
            labels.append(f'<span style="left:{(i + 0.5) * w:.3f}%">{escape(p["label"])}</span>')
    gridlines = ''.join(f'<line x1="0" x2="100%" y1="{y}%" y2="{y}%"/>' for y in (0, 50, 100))
    return mark_safe(
        f'<figure class="chart" style="--h:{height}px">'
        f'<div class="chart__peak">{peak:,}{unit}</div>'
        f'<svg class="chart__svg" preserveAspectRatio="none" role="img" aria-label="Bar chart">'
        f'<g class="chart__grid">{gridlines}</g>{"".join(bars)}</svg>'
        f'<div class="chart__labels">{"".join(labels)}</div></figure>'
    )

@register.filter
def thumb(fieldfile):
    if not isinstance(fieldfile, FieldFile) or not fieldfile.name:
        return ''
    from pathlib import Path
    from django.conf import settings
    p = Path(fieldfile.name)
    rel = f'_r/{p.parent.as_posix()}/{p.stem}.w480.webp'
    if (Path(settings.MEDIA_ROOT) / rel).exists():
        return settings.MEDIA_URL + rel
    return fieldfile.url

@register.filter
def money(value):
    try:
        return f'${float(value):,.0f}'
    except (TypeError, ValueError):
        return '—'

@register.filter
def ago(value):
    if not value:
        return ''
    if isinstance(value, int):
        value = datetime.fromtimestamp(value, tz=dt_tz.utc)
    return timesince(value, timezone.now()).split(',')[0] + ' ago'

@register.simple_tag
def delta(value):
    if value is None:
        return ''
    cls = 'up' if value > 0 else 'down' if value < 0 else 'flat'
    arrow = '↑' if value > 0 else '↓' if value < 0 else '→'
    return format_html('<span class="delta delta--{}">{} {}%</span>', cls, arrow, abs(value))

@register.filter
def is_bool(value):
    return isinstance(value, bool)

@register.filter
def status_class(value):
    return {
        'new': 'new', 'contacted': 'progress', 'quote_sent': 'progress', 'read': 'progress',
        'confirmed': 'ok', 'completed': 'ok', 'replied': 'ok', 'cancelled': 'muted', 'archived': 'muted',
    }.get(value, 'muted')
