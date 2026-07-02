from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from .models import Profile


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            profile, _ = Profile.objects.get_or_create(user=request.user, defaults={'role': 'CLIENT'})
            if profile.role not in roles:
                messages.error(request, "Vous n'avez pas l'autorisation d'accéder à cette page.")
                return redirect('dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
