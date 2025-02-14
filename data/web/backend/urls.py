from django.urls import path
from . import views

urlpatterns = [
	path('', views.index, name='index'),
	path('register/', views.register_request, name='register'),
	path('login/', views.login_request, name='login'),
	path('logout/', views.logout_request, name='logout'),
	path('check-auth/', views.check_auth, name='check-auth'),
	path('pong-view/', views.serve_pong_view, name='pong-view')
]


