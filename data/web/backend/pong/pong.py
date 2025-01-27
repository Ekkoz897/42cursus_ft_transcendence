from channels.generic.websocket import AsyncWebsocketConsumer
import json
import asyncio

# import logging
# import os

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# LOG_FILE = os.path.join(BASE_DIR, 'pong_debug.log')

# logging.basicConfig(
#     filename=LOG_FILE,
#     level=logging.DEBUG,
#     format='%(asctime)s - %(message)s'
# )
																												
GAME_SETTINGS = {
	'field': {
		'width': 1024,
		'height': 768,
	},
	'paddle': {
		'width': 15,
		'height': 100,
		'start_y': 384,
		'start_x': 40
	},
	'ball': {
		'size': 15,
		'start_x': 512,
		'start_y': 384,
		'velo_x': 5,
		'velo_y': 3
	},
	'display': {
		'fps': 60
	}
}

class Player:
	def __init__(self, session_key):
		self.player_id = session_key
		self.score = 0

class GameField:
	def __init__(self):
		self.width = GAME_SETTINGS['field']['width']
		self.height = GAME_SETTINGS['field']['height']

class Paddle:
	def __init__(self):
		self.y = GAME_SETTINGS['paddle']['start_y']
		self.x = GAME_SETTINGS['paddle']['start_x']
		self.width = GAME_SETTINGS['paddle']['width']
		self.height = GAME_SETTINGS['paddle']['height']

	def move(self, y):
		self.y = max(0, min(GAME_SETTINGS['field']['height'] - GAME_SETTINGS['paddle']['height'], y))

class Ball:
	def __init__(self):
		self.x = GAME_SETTINGS['ball']['start_x']
		self.y = GAME_SETTINGS['ball']['start_y']
		self.size = GAME_SETTINGS['ball']['size']
		self.dx = GAME_SETTINGS['ball']['velo_x']
		self.dy = GAME_SETTINGS['ball']['velo_y']

	def update(self, paddle):
		#position update
		self.x += self.dx
		self.y += self.dy

		#collision for top, bottom 
		if self.y <= 0 or self.y >= GAME_SETTINGS['field']['height'] - self.size:
			self.dy *= -1

		#colission for right
		if self.x >= GAME_SETTINGS['field']['width'] - self.size:
			self.dx *= -1

		#collision with paddles
		if (self.x <= paddle.x + paddle.width and 
			self.x + self.size >= paddle.x and
			self.y + self.size >= paddle.y and 
			self.y <= paddle.y + paddle.height):
			self.dx *= -1
			self.x = paddle.x + paddle.width

		#reset condition / left wall collision
		if self.x <= 0: #or self.x >= GAME_SETTINGS['field']['width']:
			self.x = GAME_SETTINGS['ball']['start_x']
			self.y = GAME_SETTINGS['ball']['start_y']
			self.dx = abs(self.dx)
		
class PongGameConsumer(AsyncWebsocketConsumer):

	def get_session_key(self):
		session = self.scope.get("session", {})
		return session.session_key[:6] if session else None

	async def connect(self):
		await self.accept()
		self.paddle = Paddle()
		self.gamefield = GameField()
		self.ball = Ball()
		self.player1 = Player(self.get_session_key())
		self.running = True
		#asyncio.create_task(self.game_loop())

	async def game_loop(self):
		# send first message with static components
		await self.send(json.dumps({
			'event': 'game_start',
			'state': {
				'player1_id': self.player1.player_id,
				'player1_score': self.player1.score,
				'player2_id': "Marvin",
				'player2_score': -1,
				'field_width': self.gamefield.width,
				'field_height': self.gamefield.height,
				'paddle_width': self.paddle.width,
				'paddle_height': self.paddle.height,
				'ball_size': self.ball.size,
			}
		}))
		while self.running: # send data for dynamic components only
			await asyncio.sleep(1 / GAME_SETTINGS['display']['fps'])
			self.ball.update(self.paddle)
			await self.send(json.dumps({
				'event': 'game_state',
				'state': {
					'player1_score': self.player1.score,
					'player2_score': -1,
					'paddle_y': self.paddle.y,
					'ball_x': self.ball.x,
					'ball_y': self.ball.y,
				}
			}))

	async def disconnect(self, close_code):
		self.running = False

	async def receive(self, text_data):
		data = json.loads(text_data)

		if data['action'] == 'connect':
			asyncio.create_task(self.game_loop())

		if data['action'] == 'move_paddle_up':
			self.paddle.move(self.paddle.y - 10)

		elif data['action'] == 'move_paddle_down':
			self.paddle.move(self.paddle.y + 10)

