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
		# Update context with our custom domain
		domain = settings.WEB_HOST or 'localhost:4443'
		context.update({
			'domain': domain,
			'site_name': domain,
			'protocol': 'https',
		})

		# Hardcode the subject line instead of using a template
		subject = "Password reset for your Transcendence account"
		body = loader.render_to_string(email_template_name, context)

		email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
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
