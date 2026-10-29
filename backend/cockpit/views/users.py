from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from ..forms import OwnPasswordForm, StaffUserForm
from . import staff_required

def _superuser(request):
    if not request.user.is_superuser:
        raise PermissionDenied

@staff_required
def user_list(request):
    _superuser(request)
    return render(request, 'cockpit/users/list.html', {
        'users': User.objects.filter(is_staff=True).order_by('-is_active', 'username'),
    })

@staff_required
def user_edit(request, pk=None):
    _superuser(request)
    obj = get_object_or_404(User, pk=pk, is_staff=True) if pk else None
    form = StaffUserForm(request.POST or None, instance=obj, current_user=request.user)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        if user == request.user and form.cleaned_data.get('password'):
            update_session_auth_hash(request, user)
        messages.success(request, f'User “{user.username}” saved.')
        return redirect('cockpit:users')
    return render(request, 'cockpit/users/form.html', {'form': form, 'obj': obj})

@staff_required
def account(request):
    form = OwnPasswordForm(request.user, request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        update_session_auth_hash(request, form.user)
        messages.success(request, 'Password changed.')
        return redirect('cockpit:account')
    return render(request, 'cockpit/users/account.html', {'form': form})
