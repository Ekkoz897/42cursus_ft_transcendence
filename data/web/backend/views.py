from django.shortcuts import render, redirect
from .forms import UserRegistrationForm
from .models import User

def index(request):
	if not request.session.session_key:
		request.session.save()
	return render(request, 'index.html')
