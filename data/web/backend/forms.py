from django import forms
from .models import User
from django.core.exceptions import ValidationError
import re

class UserRegistrationForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ['username', 'first_name', 'last_name', 'email', 'password',
		]
		widgets = {
			'password': forms.PasswordInput(),
		}

	def clean_username(self):
		username = self.cleaned_data.get('username')

		# Check if empty
		if not username or username.strip() == '':
			raise ValidationError("Username cannot be empty.")

		# Check minimum length
		if len(username.strip()) < 3:
			raise ValidationError("Username must be at least 3 characters long.")

		# Check maximum length
		if len(username.strip()) > 20:
			raise ValidationError("Username cannot exceed 20 characters.")

		# Check for valid characters (letters, numbers, underscores, hyphens only)
		if not re.match(r'^[a-zA-Z0-9_-]+$', username):
			raise ValidationError("Username can only contain letters, numbers, underscores and hyphens.")

		# Check if username starts with a letter
		if not username[0].isalpha():
			raise ValidationError("Username must start with a letter.")

		return username
