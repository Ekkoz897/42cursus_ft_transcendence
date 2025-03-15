from django.db import models
from backend.models import User
from pong.models import Game, OngoingGame, CompletedGame
from tournaments.models import Tournament

# def get_user(username):
# 	try:
# 		user = User.objects.get(username=username)
# 		return user
# 	except User.DoesNotExist:
# 		return None
	
