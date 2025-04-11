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

		subject = loader.render_to_string(subject_template_name, context)
		subject = ''.join(subject.splitlines())  # Email subject must be a single line
		body = loader.render_to_string(email_template_name, context)

		email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
		if html_email_template_name is not None:
			html_email = loader.render_to_string(html_email_template_name, context)
			email_message.attach_alternative(html_email, 'text/html')

		email_message.send()

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
		subject_template_name='registration/password_reset_email_subject.txt',
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
