from django.db import models

class ActiveGame(models.Model):
    game_id = models.CharField(max_length=100, unique=True)
    player1_username = models.CharField(max_length=150)
    player2_username = models.CharField(max_length=150, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create_game(cls, game_id, username1, username2=None):
        return cls.objects.create(
            game_id=game_id,
            player1_username=username1,
            player2_username=username2
        )

    @classmethod
    def player_in_game(cls, username):
        return cls.objects.filter(
            models.Q(player1_username=username) | 
            models.Q(player2_username=username)
        ).exists()

    @classmethod
    def delete_game(cls, game_id):
        cls.objects.filter(game_id=game_id).delete()