from channels.generic.websocket import AsyncWebsocketConsumer
import json
import logging
                                                                                                                  
GAME_SETTINGS = {
	'field': {
		'width': 1024,
		'height': 768,
		'score': -1
	},
	'paddle': {
		'width': 10,
		'height': 80,
		'start_y': 384
	},
}

class Paddle:
	def __init__(self):
		self.y = GAME_SETTINGS['paddle']['start_y']


	def move(self, y):
		self.y = max(0, min(GAME_SETTINGS['field']['height'] - GAME_SETTINGS['paddle']['height'], y))

class PongGameConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		self.paddle = Paddle()
		await self.accept()


	async def disconnect(self, close_code):
		pass


	async def receive(self, text_data):
		data = json.loads(text_data)

		if data['action'] == 'move_paddle_up':
			self.paddle.move(self.paddle.y - 10)

		elif data['action'] == 'move_paddle_down':
			self.paddle.move(self.paddle.y + 10)

		await self.send(json.dumps({
			'event': 'game_state',
			'state': {
				'field_width': GAME_SETTINGS['field']['width'],
				'field_height': GAME_SETTINGS['field']['height'],
				'field_score': GAME_SETTINGS['field']['score'],
				'paddle_width': GAME_SETTINGS['paddle']['width'],
				'paddle_height': GAME_SETTINGS['paddle']['height'],
				'paddle_y': self.paddle.y,
			}
		}))

	#async update N frames per second ?