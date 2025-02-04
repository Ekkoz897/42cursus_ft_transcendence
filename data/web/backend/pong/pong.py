from channels.generic.websocket import AsyncWebsocketConsumer
import json
import asyncio
import random

GAME_SETTINGS = {
	'field': {
		'width': 1024,
		'height': 768,
	},
	'paddle': {
		'width': 15,
		'height': 100,
		'velo': 5 
	},
	'l_paddle': {
		'start_y': 334,
		'start_x': 40,
	},
	'r_paddle': {
		'start_y': 334,
		'start_x': 969,
	},
	'ball': {
		'size': 15,
		'start_x': 512,
		'start_y': 384,
		'velo': 5,
	},
	'match': {
		'win_points': 3,
		'win_sets': 2
	},
	'display': {
		'fps': 60
	},
}

class Player:
	def __init__(self, session_key, paddle):
		self.player_id = session_key
		self.paddle = paddle
		self.score = 0
		self.sets = 0

	def score_point(self):
		self.score += 1
		
	def win_set(self):
		self.sets += 1

class GameField:
	def __init__(self):
		self.width = GAME_SETTINGS['field']['width']
		self.height = GAME_SETTINGS['field']['height']

class ScoreBoard:
	def __init__(self, instance, left_player: Player, right_player: Player):
		self.instance = instance
		self.left_player = left_player
		self.right_player = right_player
		self.last_scored = None

	def update(self, last_scored: Player = None):
		self.last_scored = last_scored
		if last_scored:
			asyncio.create_task(self.send())

	def new_set(self, winner : Player):
		winner.win_set()
		self.left_player.score = self.right_player.score = 0


	def end_match(self):
		if self.left_player.sets >= GAME_SETTINGS['match']['win_sets']:
			return self.left_player
		elif self.right_player.sets >= GAME_SETTINGS['match']['win_sets']:
			return self.right_player
		return None

	async def send(self):
		await self.instance.send(json.dumps({
			'event': 'score_update',
			'state': {
				'player1_score': self.left_player.score,
				'player2_score': self.right_player.score,
				'player1_sets': self.left_player.sets,
				'player2_sets': self.right_player.sets,
			}
		}))

class Paddle:
	def __init__(self, x=0, y=0):
		self.x = self.start_x = x
		self.y = self.start_y = y
		self.width = GAME_SETTINGS['paddle']['width']
		self.height = GAME_SETTINGS['paddle']['height']
		self.direction = 0

	def reset(self):
		self.x = self.start_x
		self.y = self.start_y
	
	def move(self, y):
		self.y = max(0, min(GAME_SETTINGS['field']['height'] - GAME_SETTINGS['paddle']['height'], y))

	def update(self):
		self.y += self.direction * GAME_SETTINGS['paddle']['velo']
		self.move(self.y)

class Ball:
	def __init__(self):
		self.x = GAME_SETTINGS['ball']['start_x']
		self.y = GAME_SETTINGS['ball']['start_y']
		self.size = GAME_SETTINGS['ball']['size']
		self.velo = GAME_SETTINGS['ball']['velo']
		self.dx = 0
		self.dy = 0
		self.wait_time = None
		self.is_waiting = False
	
	async def countdown(self, duration):
		await asyncio.sleep(duration)
		self.is_waiting = False

	def coin_toss(self):
		self.dx = 1 if random.random() > 0.5 else -1
		self.dy = 1 if random.random() > 0.5 else -1

	def reset(self, scoreBoard : ScoreBoard, leftPlayer : Player, rightPlayer : Player):
		self.x = GAME_SETTINGS['ball']['start_x']
		self.y = GAME_SETTINGS['ball']['start_y']
		if scoreBoard.last_scored is None:
			self.coin_toss()
		elif scoreBoard.last_scored: # Set direction towards scoring player, maybe swap ?
			self.dx = 1 if scoreBoard.last_scored == rightPlayer else -1
			self.dy = 1 if random.random() > 0.5 else -1
			
		self.is_waiting = True
		leftPlayer.paddle.reset()
		rightPlayer.paddle.reset()
		asyncio.create_task(self.countdown(3))

	def update(self, scoreBoard: ScoreBoard, leftPlayer: Player, rightPlayer: Player):
		if self.is_waiting:
			return
			
		# Position update
		self.x += self.velo * self.dx
		self.y += self.velo * self.dy

		# Collision with top and bottom walls
		if self.y <= 0 or self.y >= GAME_SETTINGS['field']['height'] - self.size:
			self.dy *= -1

		# Collision with left paddle
		if (self.x <= leftPlayer.paddle.x + leftPlayer.paddle.width and
			self.x + self.size >= leftPlayer.paddle.x and
			self.y + self.size >= leftPlayer.paddle.y and
			self.y <= leftPlayer.paddle.y + leftPlayer.paddle.height):
			self.dx *= -1
			self.x = leftPlayer.paddle.x + leftPlayer.paddle.width

		# Collision with right paddle
		if (self.x + self.size >= rightPlayer.paddle.x and
			self.y + self.size >= rightPlayer.paddle.y and
			self.y <= rightPlayer.paddle.y + rightPlayer.paddle.height):
			self.dx *= -1
			self.x = rightPlayer.paddle.x - self.size

		# Scoring and reset conditions
		if self.x <= 0:  
			rightPlayer.score_point()
			if rightPlayer.score >= GAME_SETTINGS['match']['win_points']:
				scoreBoard.update(rightPlayer)
				scoreBoard.new_set(rightPlayer)
			else:
				scoreBoard.update(rightPlayer)
			self.reset(scoreBoard, leftPlayer, rightPlayer)
		elif self.x >= GAME_SETTINGS['field']['width']: 
			leftPlayer.score_point()
			if leftPlayer.score >= GAME_SETTINGS['match']['win_points']:
				scoreBoard.update(leftPlayer)
				scoreBoard.new_set(leftPlayer)
			else:
				scoreBoard.update(leftPlayer)
			self.reset(scoreBoard, leftPlayer, rightPlayer)
		scoreBoard.update()
		
class AIPlayer(Player):
	def update(self, ball: Ball):
		paddle_center = self.paddle.y + (self.paddle.height / 2)
		ball_center = ball.y + (ball.size / 2)
		dead_zone = 20
		diff = ball_center - paddle_center
		if abs(diff) < dead_zone:
			self.paddle.direction = 0
		else:
			self.paddle.direction = 1 if diff > 0 else -1

class PongGameConsumer(AsyncWebsocketConsumer):
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



