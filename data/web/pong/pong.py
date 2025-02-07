from channels.generic.websocket import AsyncWebsocketConsumer
import json
import asyncio
from .pong_components import Paddle, Ball, Player, AIPlayer, ScoreBoard, GameField, GAME_SETTINGS

class PongGameConsumer(AsyncWebsocketConsumer):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.running = False
		self.paddleLeft = None
		self.paddleRight = None
		self.player1 = None 
		self.player2 = None
		self.ball = None
		self.scoreBoard = None
		self.gamefield = None

	async def init_game_components(self):
		self.paddleLeft = Paddle(GAME_SETTINGS['l_paddle']['start_x'], GAME_SETTINGS['l_paddle']['start_y'])
		self.paddleRight = Paddle(GAME_SETTINGS['r_paddle']['start_x'], GAME_SETTINGS['r_paddle']['start_y'])
		self.ball = Ball()
		self.gamefield = GameField()
		await self.setup_players()  # Abstract method
		self.scoreBoard = ScoreBoard(self, self.player1, self.player2)
		self.running = True
		await self.broadcast_game_start()

	async def broadcast_game_start(self):
		await self.send(json.dumps({
			'event': 'game_start',
			'state': {
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
		}))

	async def game_loop(self):
		await self.init_game_components()
		self.ball.reset(self.scoreBoard, self.player1, self.player2)
		while self.running:
			await asyncio.sleep(1 / GAME_SETTINGS['display']['fps'])
			self.paddleLeft.update()
			self.paddleRight.update()
			self.ball.update(self.scoreBoard, self.player1, self.player2)
			await self.broadcast_game_state()

			if (winner := self.scoreBoard.end_match()):
				await self.broadcast_game_end(winner)
				break
		await self.disconnect(1000)

	async def setup_players(self):
		raise NotImplementedError()

	async def broadcast_game_state(self):
		raise NotImplementedError()

	async def broadcast_game_end(self, winner):
		raise NotImplementedError()

	def get_session_key(self):
		session = self.scope.get("session", {})
		return session.session_key[:6] if session else None

class SinglePongConsumer(PongGameConsumer):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.mode = 'vs'

	async def setup_players(self):
		self.player1 = Player(self.get_session_key(), self.paddleLeft)
		self.player2 = Player(self.get_session_key() + " (2)", self.paddleRight) if self.mode == 'vs' else AIPlayer('Marvin', self.paddleRight)

	async def broadcast_game_state(self):
		if self.mode == 'ai':
			self.player2.update(self.ball)
		await self.send(json.dumps({
			'event': 'game_state',
			'state': {
				'l_paddle_y': self.paddleLeft.y,
				'r_paddle_y': self.paddleRight.y,
				'ball_x': self.ball.x,
				'ball_y': self.ball.y,
			}
		}))

	async def broadcast_game_end(self, winner):
		await self.scoreBoard.send()
		await self.send(json.dumps({
			'event': 'game_end',
			'state': {
				'winner': winner.player_id
			}
		}))

	async def connect(self):
		await self.accept() # could be in parent class?

	async def disconnect(self, close_code):
		self.running = False

	async def receive(self, text_data):
		data = json.loads(text_data)
		if 'action' not in data:
			return
		match data['action']:
			case 'connect':
				self.mode = 'ai' if data.get('mode') == 'ai' else 'vs'
				asyncio.create_task(self.game_loop())
			case 'paddle_move_start':
				paddle = self.paddleLeft if data.get('side') == 'left' else self.paddleRight
				paddle.direction = -1 if data.get('direction') == 'up' else 1
			case 'paddle_move_stop':
				paddle = self.paddleLeft if data.get('side') == 'left' else self.paddleRight
				paddle.direction = 0


class MultiPongConsumer(PongGameConsumer):
	active_games = {}  # {game_id: {players: {left: socket, right: socket}, running: bool}}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.game_id = None
		self.player_side = None

	async def connect(self): 
		pass

	async def disconnect(self, close_code): 
		self.running = False


	async def setup_players(self):
		game = MultiPongConsumer.active_games[self.game_id]
		left_socket = game['players']['left']
		right_socket = game['players']['right']
		
		self.player1 = Player(left_socket.get_session_key(), self.paddleLeft)
		self.player2 = Player(right_socket.get_session_key(), self.paddleRight)
		self.player1.side = 'left'
		self.player2.side = 'right'

	async def broadcast_game_state(self): 
		game = MultiPongConsumer.active_games[self.game_id]
		state = {
			'event': 'game_state',
			'state': {
				'l_paddle_y': self.paddleLeft.y,
				'r_paddle_y': self.paddleRight.y,
				'ball_x': self.ball.x,
				'ball_y': self.ball.y,
			}
		}
		#broadcast to all sockets
		await game['players']['left'].send(json.dumps(state))
		await game['players']['right'].send(json.dumps(state))

	async def broadcast_game_end(self, winner): 
		game = MultiPongConsumer.active_games[self.game_id]
		await self.scoreBoard.send()
		state = {
			'event': 'game_end',
			'state': {
				'winner': winner.player_id
			}
		}
		#broadcast to all sockets
		await game['players']['left'].send(json.dumps(state))
		await game['players']['right'].send(json.dumps(state))

	async def receive(self, text_data):
		data = json.loads(text_data)
		if 'action' not in data:
			return

		match data['action']:
			case 'connect':
				pass
			case 'paddle_move_start':
				if self.player_side == 'left':
					self.paddleLeft.direction = -1 if data.get('direction') == 'up' else 1
				else:
					self.paddleRight.direction = -1 if data.get('direction') == 'up' else 1
			case 'paddle_move_stop':
				if self.player_side == 'left':
					self.paddleLeft.direction = 0
				else:
					self.paddleRight.direction = 0




class QuickLobby(AsyncWebsocketConsumer):
	queued_players = {}

	def get_session_key(self):
		session = self.scope.get("session", {})
		return session.session_key[:6] if session else None

	async def broadcast_player_count(self):
		for player in self.queued_players.values():
			await player.send(json.dumps({
				'event': 'player_count',
				'state': {
					'player_count': len(self.queued_players)
				}
			}))

	async def connect(self):
		await self.accept()
		self.player_id = self.get_session_key()
		self.queued_players[self.player_id] = self
		await self.broadcast_player_count()
		await self.try_match_players()

	async def disconnect(self, close_code):
		if self.player_id in self.queued_players:
			del self.queued_players[self.player_id]
			await self.broadcast_player_count()

	async def receive(self, text_data):
		data = json.loads(text_data)
		if 'action' not in data:
			return
		
	async def try_match_players(self):
		if len(self.queued_players) >= 2:
			players = list(self.queued_players.keys())[:2]
			game_id = f"game_{players[0]}_{players[1]}"
			
			# Send match data before removing from queue
			match_data = {
				'event': 'match_found',
				'state': {
					'game_id': game_id,
					'game_url': f'ws/mpong/game/{game_id}/',
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
			
			await self.broadcast_player_count()