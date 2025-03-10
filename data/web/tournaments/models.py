from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.db.models import JSONField
from django.utils import timezone
import random, secrets, time, logging

logger = logging.getLogger('pong')

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
	rounds = JSONField(default=list)
	current_round = models.IntegerField(default=0)
	current_round_created_at = models.DateTimeField(auto_now_add=True)
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


	def start_tournament(self) -> bool:
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
		self.current_round_created_at = timezone.now()
		self.status = 'IN_PROGRESS'
		self.save()
		return True


	def create_next_round(self) -> bool:
		if self.status != 'IN_PROGRESS':
			return False

		current_round = self.rounds[self.current_round]
		
		if not all(match['status'] == 'COMPLETED' for match in current_round):
			return False

		players = [match['winner'] for match in current_round]
		if len(players) == 1:
			self.status = 'COMPLETED'
			self.winner = players[0]
			self.save()
			return True

		next_round = []
		for i in range(0, len(players), 2):
			next_round.append({
				'player1': players[i],
				'player2': players[i + 1] if i + 1 < len(players) else None,
				'winner': None,
				'game_id': self.generate_game_id(),
				'status': 'PENDING'
			})
		
		self.rounds.append(next_round)
		self.current_round += 1
		self.current_round_created_at = timezone.now()
		self.save()
		return True


	# def start_tournament(self) -> bool:
	# 	if self.status != 'REGISTERING' or len(self.players) != self.max_players:
	# 		return False
			
	# 	players = self.players.copy()
	# 	random.shuffle(players)
		
	# 	# calculate number of byes needed
	# 	total_spots = 2
	# 	while total_spots < len(players):
	# 		total_spots *= 2
	# 	num_byes = total_spots - len(players)
		
	# 	matches = []
	# 	player_idx = 0
		
	# 	# create matches, handling byes
	# 	while player_idx < len(players):
	# 		if num_byes > 0:
	# 			# player gets a bye - no game needed
	# 			matches.append({
	# 				'player1': players[player_idx],
	# 				'player2': None,  # Bye
	# 				'winner': players[player_idx],  # advance
	# 				'game_id': None,  # No game for byes
	# 				'status': 'COMPLETED'  # Auto-complete bye matches
	# 			})
	# 			player_idx += 1
	# 			num_byes -= 1
	# 		else:
	# 			# match between two players
	# 			matches.append({
	# 				'player1': players[player_idx],
	# 				'player2': players[player_idx + 1],
	# 				'winner': None,
	# 				'game_id': self.generate_game_id(),
	# 				'status': 'PENDING'
	# 			})
	# 			player_idx += 2
		
	# 	self.rounds = [matches]
	# 	self.current_round_created_at = timezone.now()
	# 	self.status = 'IN_PROGRESS'
	# 	self.save()
	# 	return True


	# def create_next_round(self) -> bool:
	# 	if self.status != 'IN_PROGRESS':
	# 		return False

	# 	current_round = self.rounds[self.current_round]
		
	# 	# if all non-bye matches are completed
	# 	if not all(match['status'] == 'COMPLETED' for match in current_round):
	# 		return False

	# 	# winners from current round
	# 	players = [match['winner'] for match in current_round if match['winner']]
		
	# 	if len(players) == 1:
	# 		self.status = 'COMPLETED'
	# 		self.winner = players[0]
	# 		self.save()
	# 		return True

	# 	next_round = []
	# 	for i in range(0, len(players), 2):
	# 		# odd number of players in next round
	# 		if i + 1 >= len(players):
	# 			next_round.append({
	# 				'player1': players[i],
	# 				'player2': None,  # bye
	# 				'winner': players[i],  # advance
	# 				'game_id': None,  # no game id for byes
	# 				'status': 'COMPLETED'
	# 			})
	# 		else:
	# 			next_round.append({
	# 				'player1': players[i],
	# 				'player2': players[i + 1],
	# 				'winner': None,
	# 				'game_id': self.generate_game_id(),
	# 				'status': 'PENDING'
	# 			})
		
	# 	self.rounds.append(next_round)
	# 	self.current_round += 1
	# 	self.current_round_created_at = timezone.now()
	# 	self.save()
	# 	return True