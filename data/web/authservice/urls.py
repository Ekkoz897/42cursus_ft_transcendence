from django.urls import path
from . import views
from .forms import CustomPasswordResetForm
from django.contrib.auth import views as auth_views


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

	# 2FA
	path('auth/2fa/update/', views.update_2fa, name='update_2fa'),

	# OAuth
	path('auth/oauth/callback/', views.oauth_callback, name='oauth-callback'),

	# Utility
	path('auth/get-host/', views.get_host, name='get-host'),

	# Password Reset URLs (already correctly prefixed)
	path('auth/password-reset/', auth_views.PasswordResetView.as_view(
		template_name='registration/password_reset_form.html',
		email_template_name='registration/password_reset_email.html',
		# subject_template_name not needed anymore since we hardcoded it
		success_url='/auth/password-reset/done/',
		form_class=CustomPasswordResetForm
	), name='password_reset'),

	path('auth/password-reset/done/', auth_views.PasswordResetDoneView.as_view(
		template_name='registration/password_reset_done.html'
	), name='password_reset_done'),

	path('auth/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
		template_name='registration/password_reset_confirm.html',
		success_url='/auth/reset/complete/'
	), name='password_reset_confirm'),

	path('auth/reset/complete/', auth_views.PasswordResetCompleteView.as_view(
		template_name='registration/password_reset_complete.html'
	), name='password_reset_complete'),
]
