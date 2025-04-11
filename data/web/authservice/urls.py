from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
	path('register/', views.register_request, name='register'),
	path('login/', views.login_request, name='login'),
	path('logout/', views.logout_request, name='logout'),
	path('check-auth/', views.check_auth, name='check-auth'),
	path('oauth/callback/', views.oauth_callback, name='oauth-callback'),
	path('get-host/', views.get_host, name='get-host'),
	path('update-2fa/', views.update_2fa, name='update_2fa'),
	path('change-password/', views.change_password, name='change-password'),

# Password Reset URLs (Django built-ins)
	path('auth/password-reset/', auth_views.PasswordResetView.as_view(
		template_name='registration/password_reset_form.html',
		email_template_name='registration/password_reset_email.html',
		success_url='/auth/password-reset/done/'
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
