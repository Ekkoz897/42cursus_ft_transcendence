from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm
import json

@ensure_csrf_cookie
def index(request):
	if not request.session.session_key:
		request.session.save()
	return render(request, 'index.html')


@ensure_csrf_cookie
def register(request):
	if request.user.is_authenticated:
		return JsonResponse({'error': 'Already authenticated'}, status=403)
	
	if request.method == 'POST':
		data = json.loads(request.body)
		form = UserRegistrationForm(data)
		if form.is_valid():
			user = form.save(commit=False)
			user.set_password(form.cleaned_data['password'])
			user.save()
			return JsonResponse({'message': 'Registration successful'})
		return JsonResponse(form.errors, status=400)
	return JsonResponse({'error': 'Invalid request'}, status=400)


@ensure_csrf_cookie
def login_view(request):
	if request.user.is_authenticated:
		return JsonResponse({'error': 'Already authenticated'}, status=403)
	
	if request.method == 'POST':
		data = json.loads(request.body)
		username = data.get('username')
		password = data.get('password')
		
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			return JsonResponse({
				'message': 'Login successful',
				'user': {
					'username': user.username,
					'email': user.email
				}
			})
		return JsonResponse({'error': 'Invalid credentials'}, status=401)
	return JsonResponse({'error': 'Invalid request'}, status=400)


# @login_required
# def logout_view(request):
# 	logout(request)
# 	return JsonResponse({'message': 'Logged out successfully'})

def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        return JsonResponse({'message': 'Logged out successfully'})
    return JsonResponse({'message': 'Already logged out'}, status=200)


@ensure_csrf_cookie
def check_auth(request):
	if request.user.is_authenticated:
		return JsonResponse({
			'isAuthenticated': True,
			'user': {
				'username': request.user.username,
				'email': request.user.email
			}
		})
	return JsonResponse({'isAuthenticated': False})