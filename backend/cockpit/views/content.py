from django.contrib import messages
from django.contrib.admin.utils import NestedObjects
from django.core.paginator import Paginator
from django.db import router, transaction
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from gallery.models import GalleryImage

from ..content import BY_KEY, TYPES
from ..forms import DayFormSet, PhotoFormSet, PhotoUploadForm, form_for
from . import staff_required


def _ctype(key):
    try:
        return BY_KEY[key]
    except KeyError:
        raise Http404


def _cell(obj, attr):
    value = attr(obj) if callable(attr) else getattr(obj, attr)
    return value() if callable(value) else value


def _related(ct):
    return [f.name for f in ct.model._meta.get_fields() if f.many_to_one and f.name in ct.fields]


@staff_required
def content_list(request, key):
    ct = _ctype(key)
    qs = ct.model.objects.all()
    q = request.GET.get('q', '').strip()
    if q and ct.search:
        cond = Q()
        for f in ct.search:
            cond |= Q(**{f'{f}__icontains': q})
        qs = qs.filter(cond)
    active = {}
    for param, (lookup, _) in ct.filters.items():
        if (v := request.GET.get(param)) not in (None, ''):
            qs = qs.filter(**{lookup: (v == '1') if lookup.startswith('is_') else v})
            active[param] = v
    page = Paginator(qs.select_related(*_related(ct)), 24).get_page(request.GET.get('page'))
    rows = [{
        'obj': o,
        'cells': [_cell(o, attr) for attr, _ in ct.columns],
        'image': getattr(o, ct.image) if ct.image else None,
        'url': ct.public_url(o) if ct.public_url else None,
    } for o in page]
    filters = {param: (lookup, choices() if callable(choices) else choices) for param, (lookup, choices) in ct.filters.items()}
    return render(request, 'cockpit/content/list.html', {
        'ct': ct, 'types': TYPES, 'page': page, 'rows': rows, 'q': q, 'active': active, 'filters': filters,
        'headers': [h for _, h in ct.columns],
    })


@staff_required
def content_edit(request, key, pk=None):
    ct = _ctype(key)
    obj = get_object_or_404(ct.model, pk=pk) if pk else None
    Form = form_for(ct)
    form = Form(request.POST or None, request.FILES or None, instance=obj)
    inline = upload = None
    if ct.inline == 'days':
        inline = DayFormSet(request.POST or None, instance=obj or ct.model(), prefix='days')
    elif ct.inline == 'photos':
        inline = PhotoFormSet(request.POST or None, instance=obj or ct.model(), prefix='photos')
        upload = PhotoUploadForm(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        valid = form.is_valid() and (inline is None or inline.is_valid()) and (upload is None or upload.is_valid())
        if valid:
            with transaction.atomic():
                if ct.key == 'posts' and not form.instance.author_id:
                    form.instance.author = request.user
                saved = form.save()
                if inline is not None:
                    inline.instance = saved
                    inline.save()
                if upload is not None:
                    for f in upload.cleaned_data['photos']:
                        GalleryImage.objects.create(album=saved, image=f)
            messages.success(request, f'{ct.label} “{saved}” saved. The website updates within a few minutes.')
            if 'continue' in request.POST:
                return redirect('cockpit:content_edit', key=key, pk=saved.pk)
            return redirect('cockpit:content_list', key=key)
        messages.error(request, 'Please fix the highlighted fields.')

    return render(request, 'cockpit/content/form.html', {
        'ct': ct, 'types': TYPES, 'obj': obj, 'form': form, 'inline': inline, 'upload': upload,
        'url': ct.public_url(obj) if obj and ct.public_url else None,
        # Media objects de-duplicate when added, so the editor script loads once.
        'media': form.media + inline.media if inline is not None else form.media,
    })


@staff_required
def content_delete(request, key, pk):
    ct = _ctype(key)
    obj = get_object_or_404(ct.model, pk=pk)
    collector = NestedObjects(using=router.db_for_write(ct.model))
    collector.collect([obj])
    affected = [
        {'label': m._meta.verbose_name_plural, 'count': len(objs)}
        for m, objs in collector.model_objs.items() if m is not ct.model and objs
    ]
    protected = [str(o) for o in list(collector.protected)[:8]]
    if request.method == 'POST' and not protected:
        name = str(obj)
        obj.delete()
        messages.success(request, f'{ct.label} “{name}” deleted.')
        return redirect('cockpit:content_list', key=key)
    return render(request, 'cockpit/content/delete.html', {
        'ct': ct, 'types': TYPES, 'obj': obj, 'affected': affected, 'protected': protected,
        'protected_more': max(0, len(collector.protected) - len(protected)),
    })
