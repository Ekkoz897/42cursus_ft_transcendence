from .models import Tournament
from django.apps import apps
from channels.db import database_sync_to_async
import asyncio, logging

logger = logging.getLogger('pong')

class TournamentManager:
	instance = None
	running = False
	task = None

	@database_sync_to_async
	def get_active_tournaments(self):
		return list(Tournament.objects.filter(status='IN_PROGRESS'))
	
	def start(self, loop):
		if not self.running:
			self.running = True
			self.loop = loop
			self.loop.create_task(self.poll_tournaments())
			logger.info('Tournament manager started')


	def stop(self):
		if self.running:
			self.running = False
			logger.info('Tournament manager stopped')


	async def poll_tournaments(self):
		while self.running:
			try:
				Tournament = apps.get_model('tournaments', 'Tournament')
				tournaments = await self.get_active_tournaments()
				
				for tournament in tournaments:
					await self.process_tournament(tournament)

			except Exception as e:
				logger.error(f'Error processing tournaments: {str(e)}')
			
			await asyncio.sleep(3)


	async def process_tournament(self, tournament : Tournament):
		if not tournament.rounds:
			return
		# logger.info(f'Processing tournament {tournament.tournament_id}')
		# logger.info(f"""
		# 	=========== Tournament Details ============
		# 	Tournament ID: {tournament.tournament_id}
		# 	Status: {tournament.status}
		# 	Players: {tournament.players}
		# 	Current Round: {tournament.current_round}
		# 	Max Players: {tournament.max_players}
		# 	Winner: {tournament.winner or 'None yet'}
		# 	Created: {tournament.created_at}
		# 	Updated: {tournament.updated_at}
		# 	=========================================""")
			
		# 	# Log details about the current round
		# if tournament.rounds and tournament.current_round < len(tournament.rounds):
		# 	current_round = tournament.rounds[tournament.current_round]
		# 	logger.info(f"""
		# 	---------- Current Round Matches ----------
		# 	Round: {tournament.current_round + 1}
		# 	Matches:""")
			
		# 	for i, match in enumerate(current_round):
		# 		logger.info(f"""
		# 		Match {i+1}:
		# 		- Player 1: {match.get('player1', 'N/A')}
		# 		- Player 2: {match.get('player2', 'N/A')}
		# 		- Status: {match.get('status', 'N/A')}
		# 		- Winner: {match.get('winner', 'None yet')}
		# 		- Game ID: {match.get('game_id', 'N/A')}
		# 			""")

			
