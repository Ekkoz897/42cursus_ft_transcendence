from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from backend.models import User
import json, logging

logger = logging.getLogger('pong')

@login_required
@require_http_methods(["GET"])
def profile(request, username):
	logger.info(f"User {request.user.username} requested profile for {username}")
	
	response_data = {
		"username": username,
		"rank": 0,
		"status": "offline",
		"about": {
			"first_joined": "",
			"last_seen": "",
		},
		"stats": {
			"total": 0,
			"total_w": 0,
			"total_l": 0,
		},
		"matches": {
			"history": []
		},
		"Friends": {
			"list": []
		},
	}
	
	
	return JsonResponse({
		"request username": username,
		"request user": request.user.username
	})

