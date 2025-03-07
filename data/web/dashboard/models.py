from django.db import models
from django.contrib.postgres.fields import ArrayField
import random, secrets, time
from pong.models import CompletedGame

class GameSessionStats(models.Model):
	game_id = models.CharField(max_length=100, unique=True)
	player1_username = models.CharField(max_length=150)
	player2_username = models.CharField(max_length=150, null=True, blank=True)
	paddle_touches = models.IntegerField(default=0)
	fastest_ball_speed = models.FloatField(default=0.0)
	avg_reaction_time = models.FloatField(default=0.0)
	created_at = models.DateTimeField(auto_now_add=True)

	@classmethod
	def create_stats(cls, game_id, username1, username2=None):
		return cls.objects.create(
			game_id=game_id,
			player1_username=username1,
			player2_username=username2
		)

	@classmethod
	def update_stats(cls, game_id: str, paddle_touches: int, fastest_speed: float, avg_reaction_time: float):
		stats = cls.objects.get(game_id=game_id)
		stats.paddle_touches = paddle_touches
		stats.fastest_ball_speed = fastest_speed
		stats.avg_reaction_time = avg_reaction_time
		stats.save()

	def __str__(self):
		return f"Stats for Game {self.game_id}"


class UserStats(models.Model):
	username = models.CharField(max_length=150, unique=True)
	most_touches = models.IntegerField(default=0)
	most_wins = models.IntegerField(default=0)
	longest_win_streak = models.IntegerField(default=0)
	time_played = models.DurationField(default=0)

	@classmethod
	def update_user_stats(cls, username):
		games = CompletedGame.objects.filter(models.Q(player1_username=username) | models.Q(player2_username=username))

		most_touches = max((game.player1_sets + game.player2_sets for game in games), default=0)
		most_wins = games.filter(winner_username=username).count()
		longest_streak = cls.calculate_win_streak(username)
		total_time = sum((game.completed_at - game.created_at for game in games), start=time.timedelta())

		user_stats, created = cls.objects.get_or_create(username=username)
		user_stats.most_touches = most_touches
		user_stats.most_wins = most_wins
		user_stats.longest_win_streak = longest_streak
		user_stats.time_played = total_time
		user_stats.save()

	@classmethod
	def calculate_win_streak(cls, username):
		"""Calculates the longest consecutive win streak"""
		streak = 0
		max_streak = 0
		for game in CompletedGame.objects.filter(models.Q(player1_username=username) | models.Q(player2_username=username)).order_by('completed_at'):
			if game.winner_username == username:
				streak += 1
				max_streak = max(max_streak, streak)
			else:
				streak = 0
		return max_streak

	def __str__(self):
		return f"Stats for {self.username}"


class MatchHistory(models.Model):
	game_id = models.CharField(max_length=100, unique=True)
	player1_username = models.CharField(max_length=150)
	player2_username = models.CharField(max_length=150, null=True, blank=True)
	outcome_choices = [
		("Win", "Win"),
		("Loss", "Loss"),
		("Draw", "Draw"),
	]
	outcome = models.CharField(max_length=10, choices=outcome_choices)
	score_player1 = models.IntegerField(default=0)
	score_player2 = models.IntegerField(default=0)
	created_at = models.DateTimeField(auto_now_add=True)

	@classmethod
	def create_from_completed(cls, completed_game):
		return cls.objects.create(
			game_id=completed_game.game_id,
			player1_username=completed_game.player1_username,
			player2_username=completed_game.player2_username,
			outcome="Win" if completed_game.winner_username == completed_game.player1_username else "Loss",
			score_player1=completed_game.player1_sets,
			score_player2=completed_game.player2_sets
		)

	@classmethod
	def find_match(cls, game_id):
		return cls.objects.filter(game_id=game_id).first()

	def __str__(self):
		return f"Match {self.game_id}: {self.player1_username} vs {self.player2_username if self.player2_username else 'AI'} - {self.outcome}"
