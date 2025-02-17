from django.urls import path
from . import views

urlpatterns = [
	path('', views.index, name='index'),
	path('home-view/', views.home_view, name='home-view'),
	path('profile-view/', views.profile_view, name='profile-view'),
	path('pong-view/', views.pong_view, name='pong-view'),
	path('login-view/', views.login_view, name='login-view'),
	path('register-view/', views.register_view, name='register-view'),


	# path('register/', views.register_request, name='register'),
	# path('login/', views.login_request, name='login'),
	# path('logout/', views.logout_request, name='logout'),
	# path('check-auth/', views.check_auth, name='check-auth'),
]


