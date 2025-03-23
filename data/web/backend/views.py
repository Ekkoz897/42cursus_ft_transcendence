from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib.auth.decorators import login_required
import json


@ensure_csrf_cookie
def index(request):
	if not request.session.session_key:
		request.session.save()
	return render(request, 'index.html')


def home_view(request):
		return render(request, 'views/home-view.html')


def nav_menu(request):
	return render(request, 'menus/nav-menu.html')

def pong_view(request):
	if request.user.is_authenticated:
		return render(request, 'views/pong-view.html')
	return HttpResponseForbidden('Not authenticated')


# def profile_view(request):
# 	if request.user.is_authenticated:
# 		return render(request, 'views/profile-view.html', {'user': request.user})
# 	return HttpResponseForbidden('Not authenticated')


def login_view(request):
	if request.user.is_authenticated:
		return redirect('home-view')
	return render(request, 'views/login-view.html')


def register_view(request):
	if request.user.is_authenticated:
		return redirect('home-view')
	return render(request, 'views/register-view.html')


def tournament_view(request):
	if request.user.is_authenticated:
		return render(request, 'views/tournament-view.html')
	return HttpResponseForbidden('Not authenticated')


@login_required
@require_POST
def update_2fa(request):
    try:
        data = json.loads(request.body)
        two_factor_enable = data.get('two_factor_enable', False)

        # Update the user's two_factor_enable field
        request.user.two_factor_enable = two_factor_enable
        request.user.save()

        return JsonResponse({
            'success': True,
            'message': f"Two-factor authentication {'enabled' if two_factor_enable else 'disabled'}"
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': "Invalid request format"
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

