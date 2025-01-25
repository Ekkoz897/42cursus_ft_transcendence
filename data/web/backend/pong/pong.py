import json
import asyncio
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

# # Configure logging
# logging.basicConfig(
# 	filename="pong_debug.log",
# 	level=logging.DEBUG,
# 	format="%(asctime)s - %(message)s"
# )
# logger = logging.getLogger(__name__)

# Game settings
GAME_SETTINGS = {
	'field': {
		'width': 1024,
		'height': 768,
		'score': 0
	},
	'paddle': {
		'width': 15,
		'height': 100,
		'speed': 20,
		'distance': 50
	},
	'ball': {
		'size': 10,
		'start_x': 512,
		'start_y': 384,
		'velo_x': 5,
		'velo_y': 3
	},
	'display': {
		'fps': 60
	}
}


# Game components
class GameField:
	def __init__(self):
		self.width = GAME_SETTINGS['field']['width']
		self.height = GAME_SETTINGS['field']['height']
		self.score = GAME_SETTINGS['field']['score']


class Paddle:
	def __init__(self):
		self.width = GAME_SETTINGS['paddle']['width']
		self.height = GAME_SETTINGS['paddle']['height']
		self.speed = GAME_SETTINGS['paddle']['speed']
		self.y = GAME_SETTINGS['field']['height'] // 2

	def move(self, new_y):
		self.y = max(0, min(GAME_SETTINGS['field']['height'] - self.height, new_y))


class leftPaddle(Paddle):
	def __init__(self):
		super().__init__()
		self.x = GAME_SETTINGS['paddle']['distance']


class rightPaddle(Paddle):
	def __init__(self):
		super().__init__()
		self.x = GAME_SETTINGS['field']['width'] - GAME_SETTINGS['paddle']['distance']


class Ball:
	def __init__(self):
		self.x = GAME_SETTINGS['ball']['start_x']
		self.y = GAME_SETTINGS['ball']['start_y']
		self.dx = GAME_SETTINGS['ball']['velo_x']
		self.dy = GAME_SETTINGS['ball']['velo_y']
		self.size = GAME_SETTINGS['ball']['size']

	def update(self, left_paddle, right_paddle):
		# Update ball position
		self.x += self.dx
		self.y += self.dy

		# Collision with top and bottom walls
		if self.y <= 0 or self.y >= GAME_SETTINGS['field']['height'] - self.size:
			self.dy *= -1

		# Collision with left paddle
		if (self.x <= left_paddle.x + left_paddle.width and
				self.y + self.size >= left_paddle.y and
				self.y <= left_paddle.y + left_paddle.height):
			self.dx *= -1
			self.x = left_paddle.x + left_paddle.width

		# Collision with right paddle
		if (self.x + self.size >= right_paddle.x and
				self.y + self.size >= right_paddle.y and
				self.y <= right_paddle.y + right_paddle.height):
			self.dx *= -1
			self.x = right_paddle.x - self.size

		# Reset when the ball goes past the left or right side
		if self.x <= 0 or self.x >= GAME_SETTINGS['field']['width']:
			self.x = GAME_SETTINGS['ball']['start_x']
			self.y = GAME_SETTINGS['ball']['start_y']
			self.dx *= -1


# WebSocket consumer
class PongGameConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		self.running = True
		self.gamefield = GameField()
		self.left_paddle = leftPaddle()
		self.right_paddle = rightPaddle()
		self.ball = Ball()
		await self.accept()

	async def disconnect(self, close_code):
		self.running = False

	async def receive(self, text_data):
		data = json.loads(text_data)
		action = data.get("action")

		if action == "connect":
			await self.send_initial_state()

			# Start the game loop
			asyncio.create_task(self.game_loop())

		elif action == "move_left_paddle_up":
			self.left_paddle.move(self.left_paddle.y - self.left_paddle.speed)
		elif action == "move_left_paddle_down":
			self.left_paddle.move(self.left_paddle.y + self.left_paddle.speed)
		elif action == "move_right_paddle_up":
			self.right_paddle.move(self.right_paddle.y - self.right_paddle.speed)
		elif action == "move_right_paddle_down":
			self.right_paddle.move(self.right_paddle.y + self.right_paddle.speed)

	async def send_initial_state(self):
		"""Send the initial state of the game to the client."""
		await self.send(json.dumps({
			'event': 'init_game',
			'state': {
				'field_width': self.gamefield.width,
				'field_height': self.gamefield.height,
				'paddle_width': self.left_paddle.width,
				'paddle_height': self.left_paddle.height,
				'ball_size': self.ball.size,
				'field_score': self.gamefield.score,
				'left_paddle_y': self.left_paddle.y,
				'right_paddle_y': self.right_paddle.y,
				'ball_x': self.ball.x,
				'ball_y': self.ball.y,
			}
		}))

	async def game_loop(self):
		while self.running:
			await asyncio.sleep(1 / GAME_SETTINGS['display']['fps'])
			await self.send_game_state()

	async def send_game_state(self):
		self.ball.update(self.left_paddle, self.right_paddle)
		await self.send(json.dumps({
			'event': 'game_state',
			'state': {
				'left_paddle_y': self.left_paddle.y,
				'right_paddle_y': self.right_paddle.y,
				'ball_x': self.ball.x,
				'ball_y': self.ball.y,
				'field_score': self.gamefield.score,
			}
		}))



