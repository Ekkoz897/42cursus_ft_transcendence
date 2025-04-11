from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template import loader
from backend.models import User
from django import forms

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

		try:
			self.clean_email(to_email)
		except forms.ValidationError:
			# If the email is invalid, we don't want to send the email
			return

		# Hardcode the email subject instead of using a template
		subject = "Password reset for your Transcendence account"
		body = loader.render_to_string(email_template_name, context)

		email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
		if html_email_template_name is not None:
			html_email = loader.render_to_string(html_email_template_name, context)
			email_message.attach_alternative(html_email, 'text/html')

		email_message.send()

	def clean_email(self):
		email = self.cleaned_data.get('email')
		# Check if this email belongs to a 42 user
		try:
			user = User.objects.get(email=email)
			if user.is_42_user:
				raise forms.ValidationError(
					("42 School accounts cannot reset passwords. Please use 42 OAuth login."),
					code="42_user_no_reset"
				)
		except User.DoesNotExist:
			# We'll let the parent class handle this case
			pass
		return email