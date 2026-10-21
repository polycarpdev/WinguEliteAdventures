from django import forms
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.cache import cache
from django.forms import inlineformset_factory, modelform_factory
from django.utils import timezone
from django.utils.text import slugify

from gallery.models import GalleryAlbum, GalleryImage
from itineraries.models import Itinerary, ItineraryDay


MAX_LOGIN_FAILURES = 5
LOCKOUT_SECONDS = 15 * 60


class StaffAuthenticationForm(AuthenticationForm):
    """Staff-only login with lockout after repeated failures (per IP and per username)."""

    def _keys(self):
        meta = self.request.META if self.request else {}
        ip = (meta.get('HTTP_X_FORWARDED_FOR') or meta.get('REMOTE_ADDR', '')).split(',')[0].strip()
        user = (self.data.get('username') or '').lower()[:150]
        return [f'login-fail:ip:{ip}', f'login-fail:user:{user}']

    def clean(self):
        keys = self._keys()
        if any(cache.get(k, 0) >= MAX_LOGIN_FAILURES for k in keys):
            raise forms.ValidationError('Too many failed attempts. Try again in 15 minutes.', code='locked')
        try:
            data = super().clean()
        except forms.ValidationError:
            for k in keys:
                cache.set(k, cache.get(k, 0) + 1, LOCKOUT_SECONDS)
            raise
        cache.delete_many(keys)
        return data

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_staff:
            raise forms.ValidationError('This account doesn’t have cockpit access.', code='no_staff')


class ImagePreviewInput(forms.ClearableFileInput):
    template_name = 'cockpit/widgets/image.html'


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput(attrs={'accept': 'image/*'}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single = super().clean
        if isinstance(data, (list, tuple)):
            return [single(d, initial) for d in data if d]
        return [single(data, initial)] if data else []


def style_widget(widget):
    """Give plain inputs/selects/textareas the design system's .input class."""
    if 'ckeditor' in widget.__class__.__module__ or getattr(widget, 'input_type', '') in ('checkbox', 'file', 'radio'):
        return
    widget.attrs['class'] = (widget.attrs.get('class', '') + ' input').strip()


class StyledFormSetMixin:
    def add_fields(self, form, index):
        super().add_fields(form, index)
        for f in form.fields.values():
            style_widget(f.widget)


class CockpitFormMixin:
    """Slugs auto-generate (and stay unique) when left blank; nicer widgets."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, f in self.fields.items():
            model_field = self._meta.model._meta.get_field(name)
            if model_field.is_relation and model_field.null:
                f.required = False  # nullable relations (e.g. blog category) are optional
            if isinstance(f, forms.ImageField):
                f.widget = ImagePreviewInput(attrs={'accept': 'image/*'})
            elif isinstance(f.widget, forms.DateTimeInput):
                f.widget = forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M')
            elif isinstance(f.widget, forms.DateInput):
                f.widget = forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')
            elif isinstance(f.widget, forms.Textarea) and 'ckeditor' not in f.widget.__class__.__module__:
                f.widget.attrs.setdefault('rows', 4)
            style_widget(f.widget)
        if 'slug' in self.fields:
            self.fields['slug'].required = False
            self.fields['slug'].help_text = 'Web address. Leave blank to create it from the name. Changing it breaks old links.'

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if slug:
            return slug
        source = self.cleaned_data.get('title') or self.cleaned_data.get('name') or ''
        base = slugify(source)[:180] or 'item'
        slug, n = base, 2
        qs = self._meta.model.objects.exclude(pk=self.instance.pk)
        while qs.filter(slug=slug).exists():
            slug, n = f'{base}-{n}', n + 1
        return slug

    def clean(self):
        data = super().clean()
        if 'is_published' in data and data.get('is_published') and not data.get('published_date'):
            data['published_date'] = timezone.now()
        return data


def form_for(ctype):
    return modelform_factory(ctype.model, form=type('Form', (CockpitFormMixin, forms.ModelForm), {}), fields=ctype.fields)


class _StyledInlineFormSet(StyledFormSetMixin, forms.BaseInlineFormSet):
    pass


DayFormSet = inlineformset_factory(
    Itinerary, ItineraryDay, formset=_StyledInlineFormSet,
    fields=['day_number', 'title', 'accommodation', 'meals', 'description'], extra=1, can_delete=True,
)

PhotoFormSet = inlineformset_factory(
    GalleryAlbum, GalleryImage, formset=_StyledInlineFormSet, fields=['caption'], extra=0, can_delete=True,
    widgets={'caption': forms.TextInput(attrs={'placeholder': 'Caption (optional)'})},
)


class PhotoUploadForm(forms.Form):
    photos = MultipleImageField(required=False, label='Add photos')


class BookingUpdateForm(forms.Form):
    status = forms.ChoiceField()
    admin_notes = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 5}))

    def __init__(self, *args, choices=(), **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].choices = choices


class StaffUserForm(forms.ModelForm):
    """Create/edit a cockpit login. Everyone here is staff; superusers can manage users."""
    password = forms.CharField(
        required=False, widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'input'}),
        help_text='Required for new users. Leave blank to keep the current password.')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active', 'is_superuser']
        labels = {'is_active': 'Can sign in', 'is_superuser': 'Can manage users'}

    def __init__(self, *args, current_user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_user = current_user
        for f in self.fields.values():
            style_widget(f.widget)
        self.fields['email'].required = True
        if not self.instance.pk:
            self.fields['password'].required = True

    def clean(self):
        data = super().clean()
        if self.instance.pk and self.instance == self.current_user:
            if not data.get('is_active') or not data.get('is_superuser'):
                raise forms.ValidationError('You can’t remove your own access.')
        if data.get('password'):
            validate_password(data['password'], self.instance)
        return data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = True
        if self.cleaned_data.get('password'):
            user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class OwnPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs['class'] = 'input'
