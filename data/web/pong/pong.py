from channels.generic.websocket import AsyncWebsocketConsumer
from .pong_components import Paddle, Ball, Player, AIPlayer, ScoreBoard, GameField, GAME_SETTINGS
from .db_api import GameDB
import json
import asyncio
import time
import secrets

import logging

logger = logging.getLogger(__name__)
class PongGame():
	def __init__(self, mode='vs'):
		self.consumers = []
		self.mode = mode
		self.running : bool = False
		self.paddleLeft : Paddle = None
		self.paddleRight : Paddle = None
		self.player1 : Player = None 
		self.player2 : Player = None
		self.ball : Ball = None
		self.scoreBoard : ScoreBoard = None
		self.gamefield : GameField = None

	def add_consumer(self, consumer):
		self.consumers.append(consumer)

	def remove_consumer(self, consumer):
		if consumer in self.consumers:
			self.consumers.remove(consumer)


	async def init_game_components(self):
		self.paddleLeft = Paddle(GAME_SETTINGS['l_paddle']['start_x'], GAME_SETTINGS['l_paddle']['start_y'])
		self.paddleRight = Paddle(GAME_SETTINGS['r_paddle']['start_x'], GAME_SETTINGS['r_paddle']['start_y'])
		self.ball = Ball()
		self.gamefield = GameField()
		await self.setup_players()
		self.scoreBoard = ScoreBoard(self, self.player1, self.player2)
		
		
	async def setup_players(self): 
		self.player1 = Player(self.consumers[0].get_username(), self.paddleLeft)
		self.player2 = Player(self.consumers[0].get_username() + " (2)", self.paddleRight) if self.mode == 'vs' else AIPlayer('Marvin', self.paddleRight)


	def get_start_data(self):
		return {
			'player1_id': self.player1.player_id,
			'player2_id': self.player2.player_id,
			'player1_score': self.player1.score,
			'player2_score': self.player2.score,
			'player1_sets': self.player1.sets,
			'player2_sets': self.player2.sets,
			'field_width': self.gamefield.width,
			'field_height': self.gamefield.height,
			'l_paddle_y': self.paddleLeft.y,
			'l_paddle_x': self.paddleLeft.x,
			'r_paddle_y': self.paddleRight.y,
			'r_paddle_x': self.paddleRight.x,
			'paddle_width': GAME_SETTINGS['paddle']['width'],
			'paddle_height': GAME_SETTINGS['paddle']['height'],
			'ball_size': self.ball.size,
		}

	async def game_loop(self):
		self.ball.reset(self.scoreBoard, self.player1, self.player2)
		while self.running:
			await asyncio.sleep(1 / GAME_SETTINGS['display']['fps'])
			self.paddleLeft.update()
			self.paddleRight.update()
			self.ball.update(self.scoreBoard, self.player1, self.player2)
			await self.broadcast_game_state()
			if self.mode == 'ai': # SinglePongConsumer case
				self.player2.update(self.ball)
			if (winner := self.scoreBoard.end_match()):
				await self.scoreBoard.send()
				await self.broadcast_game_end(winner)
				await asyncio.sleep(0.1)
				break
		await self.end_game()


	async def start(self):
		self.running = True
		await self.broadcast_game_start()
		asyncio.create_task(self.game_loop())


	async def end_game(self):
		self.running = False
		for consumer in self.consumers:
			await consumer.close()

	
	async def broadcast_game_start(self):
		for consumer in self.consumers:
			await consumer.broadcast_game_start(self)

	async def broadcast_game_state(self):
		for consumer in self.consumers:
			await consumer.broadcast_game_state(self)

	async def broadcast_game_end(self, winner: Player):
		for consumer in self.consumers:
			await consumer.broadcast_game_end(winner)

	async def broadcast_game_score(self, score_data: dict):
		for consumer in self.consumers:
			await consumer.broadcast_game_score(score_data)


class MultiPongGame(PongGame):
	def __init__(self, game_id):
		super().__init__('vs') 
		self.game_id = game_id

	async def setup_players(self):
		self.player1 = Player(self.consumers[0].get_username(), self.paddleLeft)
		self.player2 = Player(self.consumers[1].get_username(), self.paddleRight)

class SinglePongConsumer(AsyncWebsocketConsumer):
	active_games = {}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.mode = 'vs'
		self.id = None
		self.game : PongGame = None

	
	def get_username(self):
		return self.scope["user"].username if self.scope["user"].is_authenticated else None


	async def connect(self):
		if not self.scope["user"].is_authenticated:
			await self.close()
			return
		self.id = self.get_username()
		if self.id in self.active_games:
			await self.close()
			return
		await self.accept()


	async def disconnect(self, close_code):
		self.running = False
		if self.id in self.active_games:
			if not self.game:
				return
			self.game.remove_consumer(self)
			del self.active_games[self.id]


	async def receive(self, text_data):
		data = json.loads(text_data)
		if 'action' not in data:
			return
		match data['action']:
			case 'connect':
				if self.id not in self.active_games:
					self.active_games[self.id] = self.id
				
				mode = 'ai' if data.get('mode') == 'ai' else 'vs'
				self.game = PongGame(mode)
				self.game.add_consumer(self)
				await self.game.init_game_components()
				await self.game.start()
				

			case 'paddle_move_start':
					paddle = self.game.paddleLeft if data.get('side') == 'left' else self.game.paddleRight
					paddle.direction = -1 if data.get('direction') == 'up' else 1
			case 'paddle_move_stop':
					paddle = self.game.paddleLeft if data.get('side') == 'left' else self.game.paddleRight
					paddle.direction = 0



	async def broadcast(self, message):
		await self.send(json.dumps(message))


	async def broadcast_game_start(self, game):
		await self.broadcast({
			'event': 'game_start',
			'state': game.get_start_data()
		})


	async def broadcast_game_state(self, game):
		await self.broadcast({
			'event': 'game_state',
			'state': {
				'l_paddle_y': game.paddleLeft.y,
				'r_paddle_y': game.paddleRight.y,
				'ball_x': game.ball.x,
				'ball_y': game.ball.y,
			}
		})


	async def broadcast_game_end(self, winner: Player):
		await self.broadcast({
			'event': 'game_end',
			'state': {
				'winner': winner.player_id
			}
		})


	async def broadcast_game_score(self, score_data: dict):
		await self.broadcast(score_data)


class MultiPongConsumer(SinglePongConsumer):
	active_games = {}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def get_username(self):
		return self.scope["user"].username if self.scope["user"].is_authenticated else None

	async def connect(self):
		if not self.scope["user"].is_authenticated:
			await self.close()
			return

		self.game_id = self.scope['url_route']['kwargs']['game_id']
		self.player_id = self.get_username()

		await self.accept()


	async def receive(self, text_data):
		data = json.loads(text_data)
		if 'action' not in data:
			return
			
		match data['action']:
			case 'connect':
				if self.game_id not in self.active_games:
					await self.create_game()
				else:
					await self.join_game()
					await self.active_games[self.game_id]['game'].start()
			
			case 'paddle_move_start':
				if paddle := self.get_player_paddle():
					paddle.direction = -1 if data.get('direction') == 'up' else 1
			
			case 'paddle_move_stop':
				if paddle := self.get_player_paddle():
					paddle.direction = 0


	async def disconnect(self, close_code):
		if not self.game:
			return

		if self.game_id in self.active_games:
			game_entry = self.active_games[self.game_id]
			if game_entry:
				# left player disconnecting
				if game_entry['left'] and game_entry['left']['id'] == self.player_id:
					game_entry['left'] = None
				# right player disconnecting
				elif game_entry['right'] and game_entry['right']['id'] == self.player_id:
					game_entry['right'] = None
				# only remove game if both players are gone
				if not game_entry['left'] and not game_entry['right']:
					#only post game to db if game is complete
					if (winner := game_entry['game'].scoreBoard.end_match()):
						await GameDB.complete_game(game_entry['game'].game_id, winner.player_id)
					await GameDB.delete_game(self.game_id)
					del self.active_games[self.game_id]


	def get_player_paddle(self):
		game = self.active_games.get(self.game_id)
		if not game:
			return None
		return (game['game'].paddleLeft if self.player_id == game['left']['id'] 
				else game['game'].paddleRight if self.player_id == game['right']['id'] 
				else None)
	

	async def create_game(self):
		self.active_games[self.game_id] = {
			'left': {'id': self.player_id, 'socket': self},
			'right': None,
			'game': MultiPongGame(self.game_id)
		}
		self.game = self.active_games[self.game_id]['game']
		self.active_games[self.game_id]['game'].add_consumer(self)


	async def join_game(self):
		game_entry = self.active_games[self.game_id]
		game_entry['right'] = {'id': self.player_id, 'socket': self}
		
		# Start game
		game = game_entry['game']
		self.game = game
		game.add_consumer(self)
		await game.init_game_components()
		await GameDB.create_game(self.game_id, game_entry['left']['id'], self.player_id)
	

class QuickLobby(AsyncWebsocketConsumer):
	queued_players = {}

	def generate_game_id(self) -> str:
		timestamp = int(time.time())
		token = secrets.token_hex(4)
		return f"{timestamp}:{token}"
	
	def get_username(self):
		return self.scope["user"].username if self.scope["user"].is_authenticated else None

	async def broadcast_player_count(self):
		for player in self.queued_players.values():
			await player.send(json.dumps({
				'event': 'player_count',
				'state': {
					'player_count': len(self.queued_players)
				}
			}))

	async def connect(self):
		if not self.scope["user"].is_authenticated:
			await self.close()
			return
		self.player_id = self.get_username()

		if ongoing_game := await GameDB.player_in_game(self.player_id):
			
			reconnect_data = {
				'event': 'match_found',
				'state': {
					'game_id': ongoing_game,
					'game_url': f'wss/mpong/game/{ongoing_game}/',
				}
			}
			await self.accept()
			await self.send(json.dumps(reconnect_data))
			await self.close()
			return

		await self.accept()
		
		self.queued_players[self.player_id] = self
		await self.broadcast_player_count()
		await self.try_match_players()


	async def disconnect(self, close_code):
		if hasattr(self, 'player_id') and self.player_id in self.queued_players:
			del self.queued_players[self.player_id]
			await self.broadcast_player_count()

	async def receive(self, text_data):
		data = json.loads(text_data)
		if 'action' not in data:
			return
		

	async def try_match_players(self):
		if len(self.queued_players) >= 2:
			players = list(self.queued_players.keys())[:2]
			game_id = f"{self.generate_game_id()}"
			
			# Send match data before removing from queue
			match_data = {
				'event': 'match_found',
				'state': {
					'game_id': game_id,
					'game_url': f'wss/mpong/game/{game_id}/',
					'player1_id': players[0],
					'player2_id': players[1]
				}
			}
			
			# Send match data and close connections
			player1 = self.queued_players[players[0]]
			player2 = self.queued_players[players[1]]
			
			await player1.send(json.dumps(match_data))
			await player2.send(json.dumps(match_data))
			
			# Remove from queue and close lobby connections
			del self.queued_players[players[0]]
			del self.queued_players[players[1]]
			await player1.close()
			await player2.close()
			