from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from .models import User, Ladderboard
from pong.models import CompletedGame
from tournaments.models import Tournament
from tournaments.views import get_tournament_list, get_user_tournament_history
from django.utils.translation import activate, get_language

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

import logging

logger = logging.getLogger('pong')

import logging


def custom_activate(request): # not a view ^ ^ 
	user = request.user
	if user.is_authenticated:
		activate(user.language)
	else:
		activate(request.session.get('django_language', 'en'))


@ensure_csrf_cookie
@require_http_methods(["GET"])
def index(request):
	if not request.session.session_key:
		request.session.save()
	return render(request, 'index.html')


@require_http_methods(["GET"])
def home_view(request):
	custom_activate(request)    
	context = {
		'stats': {
			"players" : User.objects.count(),
			"games" : CompletedGame.objects.count(),
			"champions" : Tournament.objects.filter(status='COMPLETED').count(),
		}
	}
	return render(request, 'views/home-view.html', context)

@require_http_methods(["GET"])
def not_found_view(request):
	return render(request, 'views/not-found-view.html')

 
@require_http_methods(["GET"])
def nav_menu(request):
	custom_activate(request)
	return render(request, 'menus/nav-menu.html')

 
@require_http_methods(["GET"])
def login_menu(request):
    custom_activate(request)
    
    context = {
        'is_authenticated': False,
        'username': '',
        'profile_pic': '/static/images/nologin-thumb.png',
    }

    user = User.from_jwt_request(request)
    if user:
        context.update({
            'is_authenticated': True,
            'username': user.username,
            'profile_pic': str(user.profile_pic),
            'friends': {
                'pending_received': user.pending_received_requests,
            }
        })
    
    return render(request, 'menus/login-menu.html', context)

 
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def pong_view(request):
	logger.info(f"User {request.user.username} accessed pong view")
	return render(request, 'views/pong-view.html')


 
@api_view(['GET'])
@authentication_classes([]) 
def login_view(request):
	custom_activate(request)
	# Check JWT authentication but maintain redirect behavior
	if request.user and request.user.is_authenticated:
		return redirect('home-view')
	return render(request, 'views/login-view.html')


@api_view(['GET'])
@authentication_classes([]) 
def register_view(request):
	custom_activate(request)
	# Check JWT authentication but maintain redirect behavior
	if request.user and request.user.is_authenticated:
		return redirect('home-view')
	return render(request, 'views/register-view.html')

 
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def tournament_view(request):
	custom_activate(request)
	context = {
		**get_tournament_list(request.user),
		'tournament_history': get_user_tournament_history(request.user)
	}
	return render(request, 'views/tournament-view.html', context)


@require_http_methods(["GET"])
def twoFactor_view(request):
	custom_activate(request)
	user = request.user
	if user.is_authenticated:
		if not user.is_42_user and not user.two_factor_enable:
			return render(request, 'views/twoFactor-view.html')
		else:
			return redirect('home-view')
	return HttpResponseForbidden('Not authenticated')


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def ladderboard_view(request, page=None):
	custom_activate(request)
	users_per_page = 5
	total_users = Ladderboard.objects.count()
	total_pages = max(1, (total_users + users_per_page - 1) // users_per_page)

	try:
		page_num = int(page) if page is not None else 1
		if page_num < 1 or page_num > total_pages:
			page_num = 1
	except (ValueError, TypeError):
		page_num = 1

	start = (page_num - 1) * users_per_page
	leaderboard = Ladderboard.get_leaderboard(start, users_per_page)
	
	context = {
		'leaderboard': leaderboard,
		'current_page': page_num,
		'total_pages': range(1, total_pages + 1),
		'start_index': (page_num - 1) * users_per_page, 
	}
	
	return render(request, 'views/ladderboard-view.html', context)

 
def language_menu(request):
	custom_activate(request)
	return render(request, 'menus/language-menu.html')

