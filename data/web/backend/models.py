from django.contrib.auth.models import AbstractUser
from django.db.models import JSONField
from django.db import models
from django.conf import settings
# from settings import MEDIA_URL
import uuid as uuid_lib

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
	profile_pic = models.CharField(default=f'https://{settings.WEB_HOST}{settings.MEDIA_URL}profile-pics/pfp-1.png' ,max_length=255)
	id_42 = models.IntegerField(default=0)
	uuid = models.UUIDField(default=uuid_lib.uuid4, editable=True, null=True)
	rank = models.IntegerField(default=0)
	status = models.BooleanField(default=False)
	friends = JSONField(default=list)
	two_factor_enable = models.BooleanField(default=False)
	pass
