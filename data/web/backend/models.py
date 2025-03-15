from django.contrib.auth.models import AbstractUser
from django.db.models import JSONField
from django.db import models

class User(AbstractUser):  # Inherits all these fields:
	# Username
	# First name
	# Last name
	# Email
	# Password
	# Groups
	# User permissions
	# Is staff
	# Is active
	# Is superuser
	# Last login
	# Date joined
	is_42_user = models.BooleanField(default=False)
	id_42 = models.IntegerField(default=0)
	uuid : models.UUIDField = None
	rank = models.IntegerField(default=0)
	status = models.BooleanField(default=False)
	friends = JSONField(default=list)
	pass