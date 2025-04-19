from django.urls import path
from . import views
from . import forms
from .forms import CustomPasswordResetForm
from django.contrib.auth import views as auth_views
# from .forms import CustomPasswordResetForm
# from django.contrib.auth import views as auth_views
from rest_framework_simplejwt.views import (
	TokenObtainPairView,
	TokenRefreshView,
	TokenVerifyView
)


urlpatterns = [
	path('twoFactor/', views.twoFactor, name='twoFactor'),
	path('verify_2fa_enable/', views.verify_2fa_enable, name='verify_2fa_enable'),
	path('verify_2fa_login/', views.verify_2fa_login, name='verify_2fa_login'),
	path('disable_2fa/', views.disable_2fa, name='disable_2fa'),
	
	# Core authentication endpoints
	path('auth/register/', views.register_request, name='register'),
	path('auth/login/', views.login_request, name='login'),
	path('auth/logout/', views.logout_request, name='logout'),
	path('auth/status/', views.check_auth, name='check-auth'),
	path('auth/change-password/', views.change_password, name='change-password'),
	path('auth/delete-account/', views.delete_account, name='delete-account'),

	# Password Reset
	path('auth/password-reset/', views.password_reset, name='password_reset'),
	path('auth/reset/<uidb64>/<token>/', views.password_reset_confirm ,name='password_reset_confirm'),
	
	# 2FA
	path('auth/2fa/update/', views.update_2fa, name='update_2fa'),

	# OAuth
	path('oauth/callback/', views.oauth_callback, name='oauth-callback'),

	# Utility
	path('auth/get-host/', views.get_host, name='get-host'),

	# Password Reset URLs (already correctly prefixed)
	# JWT Token URLs
	path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
	path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
	path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

]
