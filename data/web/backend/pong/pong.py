from channels.generic.websocket import AsyncWebsocketConsumer
import json
import asyncio
from .pong_components import Paddle, Ball, Player, AIPlayer, ScoreBoard, GameField, GAME_SETTINGS

class SinglePongConsumer(AsyncWebsocketConsumer):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.mode = 'vs'  
		self.running = False


	async def init_match(self):
		self.paddleLeft = Paddle(GAME_SETTINGS['l_paddle']['start_x'], GAME_SETTINGS['l_paddle']['start_y'])
		self.paddleRight = Paddle(GAME_SETTINGS['r_paddle']['start_x'], GAME_SETTINGS['r_paddle']['start_y'])
		self.player1 = Player(self.get_session_key(), self.paddleLeft)
		self.player2 = Player(self.get_session_key() + " (2)", self.paddleRight) if self.mode == 'vs' else AIPlayer('Marvin', self.paddleRight)
		self.scoreBoard = ScoreBoard(self, self.player1, self.player2)
		self.gamefield = GameField()
		self.ball = Ball()
		self.running = True
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
		await self.init_match()
		self.ball.reset(self.scoreBoard, self.player1, self.player2)
		while self.running:
			await asyncio.sleep(1 / GAME_SETTINGS['display']['fps'])
			self.paddleLeft.update()
			self.paddleRight.update()
			self.ball.update(self.scoreBoard, self.player1, self.player2)
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

			if (winner := self.scoreBoard.end_match()):
				await self.scoreBoard.send()
				await self.send(json.dumps({
					'event': 'game_end',
					'state': {
						'winner': winner.player_id
					}
				}))
				break
		await self.disconnect(1000)
	

	def get_session_key(self):
		session = self.scope.get("session", {})
		return session.session_key[:6] if session else None
	

	async def connect(self):
		await self.accept()


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
			# Get first two players
			player_ids = list(self.queued_players.keys())[:2]
			player1_id = player_ids[0]
			player2_id = player_ids[1]
			
			# Get their websocket connections
			player1 = self.queued_players[player1_id]
			player2 = self.queued_players[player2_id]
			
			# Remove from queue
			del self.queued_players[player1_id]
			del self.queued_players[player2_id]
			
			# Notify both players
			match_data = {
				'event': 'match_found',
				'state': {
					'player1_id': player1_id,
					'player2_id': player2_id,
				}
			}
			await player1.send(json.dumps(match_data))
			await player2.send(json.dumps(match_data))
			
			# Update remaining players count
			await self.broadcast_player_count()
