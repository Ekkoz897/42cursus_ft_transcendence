from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import EmailMultiAlternatives
from django.template import loader

# Custom password reset form to override send_mail with our custom domain logic
class CustomPasswordResetForm(PasswordResetForm):
	def send_mail(self, subject_template_name, email_template_name,
				  context, from_email, to_email, html_email_template_name=None):
		"""
		Override the send_mail method to use custom domain from settings.WEB_HOST
		"""
		# Force localhost:4443 for development
		domain = 'localhost:4443'
		context.update({
			'domain': domain,
			'site_name': 'ft_transcendence',
			'protocol': 'https',
		})

		# Get the subject from settings, with a hardcoded fallback
		subject = getattr(settings, 'PASSWORD_RESET_SUBJECT', "Password reset on ft_transcendence")
		body = loader.render_to_string(email_template_name, context)

		# Apply custom headers to ensure subject is used
		email_message = EmailMultiAlternatives(
			subject=subject,
			body=body,
			from_email=from_email,
			to=[to_email],
			headers={'X-Custom-Subject': subject}  # Add header to ensure subject persistence
		)

		if html_email_template_name is not None:
			html_email = loader.render_to_string(html_email_template_name, context)
			email_message.attach_alternative(html_email, 'text/html')

		email_message.send()

urlpatterns = [
	# Core authentication endpoints
	path('auth/register/', views.register_request, name='register'),
	path('auth/login/', views.login_request, name='login'),
	path('auth/logout/', views.logout_request, name='logout'),
	path('auth/status/', views.check_auth, name='check-auth'),
	path('auth/change-password/', views.change_password, name='change-password'),

	# 2FA
	path('auth/2fa/update/', views.update_2fa, name='update_2fa'),

	# OAuth
	path('auth/oauth/callback/', views.oauth_callback, name='oauth-callback'),

	# Utility
	path('auth/get-host/', views.get_host, name='get-host'),

	# Password Reset URLs (standard Django views - still needed for email links)
	path('auth/password-reset/', auth_views.PasswordResetView.as_view(
		template_name='registration/password_reset_form.html',
		email_template_name='registration/password_reset_email.html',
		subject_template_name=None,  # Use the subject from our custom form
		success_url='/auth/password-reset/done/',
		form_class=CustomPasswordResetForm,
		extra_email_context={'site_name': 'ft_transcendence'}  # Add this to override site_name
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

	# SPA Password Reset Templates
	path('auth/password-reset-spa/', views.password_reset_spa, name='password_reset_spa'),
	path('auth/password-reset-done-spa/', views.password_reset_done_spa, name='password_reset_done_spa'),
	path('auth/reset-spa/<uidb64>/<token>/', views.password_reset_confirm_spa, name='password_reset_confirm_spa'),
	path('auth/reset-complete-spa/', views.password_reset_complete_spa, name='password_reset_complete_spa'),

	# SPA Password Reset APIs
	path('auth/password-reset/api/', views.password_reset_api, name='password_reset_api'),
	path('auth/reset/<uidb64>/<token>/api/', views.password_reset_confirm_api, name='password_reset_confirm_api'),

	# Legacy URLs for backward compatibility - redirect to new paths
	path('register/', views.redirect_to_auth_register, name='legacy_register'),
	path('login/', views.redirect_to_auth_login, name='legacy_login'),
	path('logout/', views.redirect_to_auth_logout, name='legacy_logout'),
	path('check-auth/', views.redirect_to_auth_status, name='legacy_check_auth'),
	path('change-password/', views.redirect_to_auth_change_password, name='legacy_change_password'),
	path('update-2fa/', views.redirect_to_auth_2fa_update, name='legacy_update_2fa'),
	path('oauth/callback/', views.redirect_to_auth_oauth_callback, name='legacy_oauth_callback'),
	path('get-host/', views.redirect_to_auth_get_host, name='legacy_get_host'),
]
