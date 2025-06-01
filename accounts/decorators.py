from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required

def role_required(required_role):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if request.user.role == required_role:
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("You are not authorized to view this page.")
        return login_required(wrapper)
    return decorator
