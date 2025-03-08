from channels.db import database_sync_to_async
from .models import OngoingGame, CompletedGame
from dashboard.models import GameSessionStats, UserStats, MatchHistory
from django.db import models

class GameDB:
	## ====== ONGOING & COMPLETED GAMES ====== ##

	@staticmethod
	async def create_game(game_id: str, player1_id: str, player2_id: str = None):
		return await database_sync_to_async(OngoingGame.create_game)(
			game_id, player1_id, player2_id
		)

	@staticmethod
	async def update_score(game_id: str, player1_sets: int, player2_sets: int):
		return await database_sync_to_async(OngoingGame.update_score)(game_id, player1_sets, player2_sets)

	@staticmethod
	async def player_in_game(username: str):
		return await database_sync_to_async(OngoingGame.player_in_game)(username)

	@staticmethod
	async def delete_game(game_id: str):
		return await database_sync_to_async(OngoingGame.delete_game)(game_id)

	@staticmethod
	async def complete_game(game_id: str, winner: str):
		try:
			ongoing = await database_sync_to_async(OngoingGame.objects.get)(game_id=game_id)
			completed_game = await database_sync_to_async(CompletedGame.create_from_ongoing)(ongoing, winner)
			return completed_game
		except OngoingGame.DoesNotExist:
			return None


	@staticmethod
	async def is_duplicate_game_id(game_id: str):
		return await database_sync_to_async(CompletedGame.is_duplicate_id)(game_id)

	## ====== GAME SESSION, USER & MATCH HISTORY STATS ====== ##

	@staticmethod
	async def create_game_stats(game_id: str, username1: str, username2: str = None):
		return await database_sync_to_async(GameSessionStats.create_stats)(
			game_id, username1, username2
		)

	@staticmethod
	async def update_game_stats(game_id: str, paddle_touches: int):
		return await database_sync_to_async(GameSessionStats.update_stats)(game_id, paddle_touches)

	@staticmethod
	async def get_game_stats(game_id: str):
		return await database_sync_to_async(lambda: GameSessionStats.objects.filter(game_id=game_id).first())()


	@staticmethod
	async def update_user_stats(username: str):
		return await database_sync_to_async(UserStats.update_user_stats)(username)

	@classmethod
	def get_user_stats(cls, username):
		return cls.objects.filter(username=username).first()


	@staticmethod
	async def create_match_history(completed_game):
		return await database_sync_to_async(MatchHistory.create_from_completed)(completed_game)

	@staticmethod
	async def get_match_history(game_id: str):
		return await database_sync_to_async(MatchHistory.find_match)(game_id)

	@staticmethod
	async def get_all_matches_for_user(username: str):
		return await database_sync_to_async(
			lambda: MatchHistory.objects.filter(
				models.Q(player1_username=username) | models.Q(player2_username=username)
			)
		)()


