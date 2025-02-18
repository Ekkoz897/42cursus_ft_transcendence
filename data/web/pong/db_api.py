from channels.db import database_sync_to_async
from .models import ActiveGame

class GameDB:
    @staticmethod
    async def create_game(game_id: str, player1_id: str, player2_id: str = None):
        return await database_sync_to_async(ActiveGame.create_game)(
            game_id, player1_id, player2_id
        )

    @staticmethod
    async def check_player_in_game(username: str):
        return await database_sync_to_async(ActiveGame.player_in_game)(username)

    @staticmethod
    async def delete_game(game_id: str):
        return await database_sync_to_async(ActiveGame.delete_game)(game_id)