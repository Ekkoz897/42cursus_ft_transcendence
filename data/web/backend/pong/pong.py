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
		'velo': 22.2 # 1000px / 45fps
	},
	'l_paddle': {
		'start_y': 334, #field height / 2 - paddle height / 2
		'start_x': 40,
	},
	'r_paddle': {
		'start_y': 334, #field height / 2 - paddle height / 2
		'start_x': 969, #field width - 40 - paddle width
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
	def __init__(self, x=0, y=0):
		self.y = y
		self.x = x
		self.width = GAME_SETTINGS['paddle']['width']
		self.height = GAME_SETTINGS['paddle']['height']
		self.velo = GAME_SETTINGS['paddle']['velo']

	def move(self, y):
		self.y = max(0, min(GAME_SETTINGS['field']['height'] - GAME_SETTINGS['paddle']['height'], y))


class Ball:
	def __init__(self):
		self.x = GAME_SETTINGS['ball']['start_x']
		self.y = GAME_SETTINGS['ball']['start_y']
		self.size = GAME_SETTINGS['ball']['size']
		self.dx = GAME_SETTINGS['ball']['velo_x']
		self.dy = GAME_SETTINGS['ball']['velo_y']
		self.wait_time = None
		self.is_waiting = False
	
	async def countdown(self, duration):
		await asyncio.sleep(duration)
		self.is_waiting = False

	def reset(self):
		self.x = GAME_SETTINGS['ball']['start_x']
		self.y = GAME_SETTINGS['ball']['start_y']
		self.dx = abs(self.dx)
		self.is_waiting = True
		asyncio.create_task(self.countdown(3))

	def update(self, paddle):
		if self.is_waiting:
			return
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
			self.x = paddle.x + paddle.width #what is this ? xD
		#reset condition / left wall collision
		if self.x <= 0: #or self.x >= GAME_SETTINGS['field']['width']:
			self.reset()
		
class PongGameConsumer(AsyncWebsocketConsumer):

	def get_session_key(self):
		session = self.scope.get("session", {})
		return session.session_key[:6] if session else None

	async def connect(self):
		await self.accept()
		self.paddleLeft = Paddle(GAME_SETTINGS['l_paddle']['start_x'], GAME_SETTINGS['l_paddle']['start_y'])
		self.paddleRight = Paddle(GAME_SETTINGS['r_paddle']['start_x'], GAME_SETTINGS['r_paddle']['start_y'])
		self.gamefield = GameField()
		self.ball = Ball()
		self.player1 = Player(self.get_session_key())
		self.player2 = Player("Marvin")
		self.running = True
		#asyncio.create_task(self.game_loop())

	async def game_loop(self):
		# send first message with static components
		await self.send(json.dumps({
			'event': 'game_start',
			'state': {
				'player1_id': self.player1.player_id,
				'player1_score': self.player1.score,
				'player2_id': self.player2.player_id,
				'player2_score': self.player2.score,
				'field_width': self.gamefield.width,
				'field_height': self.gamefield.height,
				'l_paddle_y': self.paddleLeft.y,
				'l_paddle_x': self.paddleLeft.x,
				'r_paddle_y': self.paddleRight.y,
				'r_paddle_x': self.paddleRight.x,
				'paddle_width': GAME_SETTINGS['paddle']['width'],
				'paddle_height': GAME_SETTINGS['paddle']['height'],
				'paddle_velo': GAME_SETTINGS['paddle']['velo'],
				'ball_size': self.ball.size,
			}
		}))
		self.ball.reset()
		while self.running: # send data for dynamic components only
			await asyncio.sleep(1 / GAME_SETTINGS['display']['fps'])
			self.ball.update(self.paddleLeft)
			await self.send(json.dumps({
				'event': 'game_state',
				'state': {
					'player1_score': self.player1.score,
					'player2_score': self.player2.score,
					'l_paddle_y': self.paddleLeft.y,
					'r_paddle_y': self.paddleRight.y,
					'ball_x': self.ball.x,
					'ball_y': self.ball.y,
				}
			}))

	async def disconnect(self, close_code):
		self.running = False

	async def receive(self, text_data):
		data = json.loads(text_data)

		if 'action' not in data:
			return

		match data['action']: # in a mp game side should be tracked with the user id or session key
			case 'connect':
				asyncio.create_task(self.game_loop())
			case 'move_paddle_up':
				paddle = self.paddleLeft if data.get('side') == 'left' else self.paddleRight
				paddle.move(paddle.y - 10)
			case 'move_paddle_down':
				paddle = self.paddleLeft if data.get('side') == 'left' else self.paddleRight
				paddle.move(paddle.y + 10)

