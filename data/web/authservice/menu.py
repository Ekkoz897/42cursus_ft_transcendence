from django.shortcuts import render


from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from backend.models import User
import json, requests, logging

logger = logging.getLogger('pong')

@require_http_methods(["GET"])
def login_menu(request):
    context = {
        'is_authenticated': request.user.is_authenticated,
        'username': request.user.username if request.user.is_authenticated else '',
        'profile_pic': request.user.profile_pic if request.user.is_authenticated else '/static/images/nologin-thumb.png'
    }
    return render(request, 'menus/login-menu.html', context)