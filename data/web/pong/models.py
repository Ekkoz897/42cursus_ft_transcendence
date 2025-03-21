from django.db import models
from backend.models import User
from django.contrib.postgres.fields import ArrayField, HStoreField
from django.contrib.postgres.operations import HStoreExtension
import random, secrets, time



class Game(models.Model):
	game_id = models.CharField(max_length=100, unique=True)
	player_ids = HStoreField()
	player1_username = models.CharField(max_length=150)
	player1_sets = models.IntegerField(default=0)
	player2_username = models.CharField(max_length=150)
	player2_sets = models.IntegerField(default=0)
	created_at = models.DateTimeField(auto_now_add=True)

	@classmethod
	def find_by_id(cls, game_id: str):
		try:
			return cls.objects.get(game_id=game_id)
		except cls.DoesNotExist:
			return None

	@classmethod
	def map_players(cls, user):
		return {str(user.uuid): user.username}

	class Meta:
		abstract = True

class OngoingGame(Game):
	@classmethod
	def create_game(cls, game_id, username1, username2=None):
		user1 = User.objects.get(username=username1)
		player_mapping = cls.map_players(user1)  
		
		if username2:
			user2 = User.objects.get(username=username2)
			player_mapping.update(cls.map_players(user2))  
		return cls.objects.create(
			game_id=game_id,
			player_ids=player_mapping,
			player1_username=username1,
			player2_username=username2
		)

	@classmethod
	def player_in_game(cls, player_id):
		return cls.objects.filter(
			player_ids__has_key=player_id
		).values_list('game_id', flat=True).first()

	@classmethod
	def delete_game(cls, game_id):
		cls.objects.filter(game_id=game_id).delete()

	@classmethod
	def update_score(cls, game_id : str, player1_sets : int, player2_sets : int):
		game = cls.objects.get(game_id=game_id)
		if not game:
			return
		game.player1_sets = player1_sets
		game.player2_sets = player2_sets
		game.save()

class CompletedGame(Game):
	winner_username = models.CharField(max_length=150)
	completed_at = models.DateTimeField(auto_now_add=True)

	@classmethod
	def create_from_ongoing(cls, ongoing_game, winner: str):
		return cls.objects.create(
			game_id=ongoing_game.game_id,
			player_ids=ongoing_game.player_ids,
			player1_username=ongoing_game.player1_username,
			player2_username=ongoing_game.player2_username,
			player1_sets=ongoing_game.player1_sets,
			player2_sets=ongoing_game.player2_sets,
			winner_username=winner
		)
	
	@classmethod
	def is_duplicate_id(cls, game_id):
		return cls.objects.filter(game_id=game_id).exists()
	
