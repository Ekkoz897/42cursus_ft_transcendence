from django.db import models
from django.contrib.postgres.fields import ArrayField
import random, secrets, time

class Tournament(models.Model):
	TOURNAMENT_STATUS = [
		('REGISTERING', 'Registering'),
		('IN_PROGRESS', 'In Progress'),
		('COMPLETED', 'Completed'),
	]

	tournament_id = models.CharField(max_length=100, unique=True)
	max_players = models.IntegerField(default=4)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	winner = models.CharField(max_length=150, null=True)
	players = ArrayField(models.CharField(max_length=150), default=list)
	rounds = ArrayField(ArrayField(models.JSONField(default=dict), default=list), default=list)
	current_round = models.IntegerField(default=0)
	status = models.CharField(
		max_length=20,
		choices=TOURNAMENT_STATUS,
		default='REGISTERING'
	)

	@classmethod
	def create_tournament(cls, tournament_id: str, players: list):
		return cls.objects.create(
			tournament_id=tournament_id,
			players=players,
			rounds=[], 
			current_round=0
		)
	
	@classmethod
	def player_in_tournament(cls, username: str) -> bool:
		return cls.objects.filter(
			players__contains=[username],
			status__in=['REGISTERING', 'IN_PROGRESS']
		).exists()
	

	def generate_game_id(self) -> str:
		timestamp = int(time.time())
		token = secrets.token_hex(4)
		return f"tg:{timestamp}:{token}"


	def start_tournament(self):
		if self.status != 'REGISTERING' or len(self.players) != self.max_players:
			return False
			
		if self.max_players % 2 != 0:
			return False
			
		players = self.players.copy()
		random.shuffle(players)
		
		matches = []
		for i in range(0, len(players), 2):
			matches.append({
				'player1': players[i],
				'player2': players[i + 1],
				'winner': None,
				'game_id': self.generate_game_id(),
				'status': 'PENDING'
			})
		
		self.rounds = [matches]
		self.status = 'IN_PROGRESS'
		self.save()
		return True
