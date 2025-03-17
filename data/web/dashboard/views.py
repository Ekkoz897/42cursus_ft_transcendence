from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from backend.models import User
from .models import profile_data, get_user
import json, logging

logger = logging.getLogger('pong')

@login_required
@require_http_methods(["GET"])
def profile(request, username):
	logger.info(f"User {request.user.username} requested profile for {username}")
	
	if username is None or not get_user(username):
		response_data = profile_data(request.user.username)
	else:
		response_data = profile_data(username)
	return JsonResponse(response_data)


