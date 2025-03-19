from django.urls import path
from . import views

urlpatterns = [
    path('profile-view/<str:username>/', views.profile_view, name='profile-view'),
    path('profile-view/', views.profile_view, name='profile-view-self'),
]