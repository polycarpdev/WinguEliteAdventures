from functools import wraps

from django.contrib.auth.views import redirect_to_login

def staff_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not (request.user.is_authenticated and request.user.is_staff):
            return redirect_to_login(request.get_full_path())
        return view(request, *args, **kwargs)
    return wrapper
