from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from backend.models import User
from .models import get_user, user_rank, user_status, user_about, user_stats, user_matches, format_matches, user_friends, user_picture
import json, logging

logger = logging.getLogger('pong')

@require_http_methods(["GET"])
def profile_view(request, username=None):
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
		'user': target_user,
		'own_profile': is_own_profile,
		'rank': user_rank(target_user),
		'status': user_status(target_user),
		'about': user_about(target_user),
		'stats': user_stats(username),
		'matches': formatted_matches,
		'friends': user_friends(target_user),
		'profile_pic': user_picture(target_user)
	}
	return render(request, 'views/profile-view.html', context)


