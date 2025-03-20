from django.urls import path
from . import views

urlpatterns = [
	# path('profile/<str:username>/', views.profile, name='profile'),

	path('profile-view/<str:username>/', views.profile_view, name='profile-view'),
	path('profile-view/', views.profile_view, name='profile-view-self'),
	path('profile/update/', views.update_profile, name='profile-update'),
	path('profile/change-password/', views.change_password, name='change-password'),
]
