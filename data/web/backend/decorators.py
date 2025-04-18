from functools import wraps
from django.shortcuts import redirect
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.http import JsonResponse


def require_header(view_func):
	@wraps(view_func)
	def wrapper(request, *args, **kwargs):
		if 'X-Template-Only' in request.headers:
			return view_func(request, *args, **kwargs)
		return redirect('/')
	return wrapper


def jwt_auth_required(view_func):
	@wraps(view_func)
	def wrapped_view(request, *args, **kwargs):
		auth = JWTAuthentication()
		try:
			user, _ = auth.authenticate(request)
			request.user = user
		except AuthenticationFailed:
			return JsonResponse({'error': 'Authentication failed'}, status=401)
		return view_func(request, *args, **kwargs)
	return wrapped_view
#
