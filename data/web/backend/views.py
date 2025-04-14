from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

#Friend Info for chat
from backend.models import User
from dashboard.models import (
    get_user, user_about, user_status, user_stats, user_matches, 
	format_matches, user_friends, user_pending_sent, 
	user_pending_received, friendship_status
)
import os, json, logging

@ensure_csrf_cookie
def index(request):
	if not request.session.session_key:
		request.session.save()
	return render(request, 'index.html')

def get_friend_context(request, username=None):
	
	if not request.user.is_authenticated:
		return HttpResponseForbidden('Not authenticated')

	if username is None or not get_user(username):
		target_user = request.user
		is_own_profile = True
		username = request.user.username
	else:
		target_user = get_user(username)
		is_own_profile = (request.user.username == username)

	matches_data = user_matches(username)
	formatted_matches = format_matches(matches_data)
	

	context = {

		 'own_profile': is_own_profile,
		'friends': {
			'friendship_status': friendship_status(request.user, target_user),
			'list': user_friends(target_user),
			'pending_sent': user_pending_sent(target_user),
			'pending_received': user_pending_received(target_user)
		},
		
	}
	return(context)

def home_view(request, username=None):

	return render(request, 'views/home-view.html', get_friend_context(request, username=None))


def nav_menu(request):
	return render(request, 'menus/nav-menu.html')


@require_http_methods(["GET"])
def login_menu(request):
	context = {
		'is_authenticated': request.user.is_authenticated,
		'username': request.user.username if request.user.is_authenticated else '',
		'profile_pic': request.user.profile_pic if request.user.is_authenticated else '/static/images/nologin-thumb.png',
	}
	if request.user.is_authenticated:
		context['friends'] = {
			'pending_received': request.user.pending_received_requests,
		}
	return render(request, 'menus/login-menu.html', context)


def pong_view(request):
	if request.user.is_authenticated:
		return render(request, 'views/pong-view.html', get_friend_context(request, username=None))
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
		return render(request, 'views/tournament-view.html', get_friend_context(request, username=None))
	return HttpResponseForbidden('Not authenticated')



