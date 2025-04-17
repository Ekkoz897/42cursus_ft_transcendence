from functools import wraps
from django.shortcuts import redirect

def require_header(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'X-Template-Only' in request.headers:
            return view_func(request, *args, **kwargs)
        return redirect('/#pong')
    return wrapper