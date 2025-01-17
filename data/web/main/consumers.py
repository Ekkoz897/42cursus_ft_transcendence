from channels.generic.websocket import AsyncWebsocketConsumer
from asyncio import sleep
import json

class PongGameConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		self.paddle_y = 250  # Initial paddle position
		await self.accept()

	async def disconnect(self, close_code):
		pass

	async def receive(self, text_data):
		data = json.loads(text_data)
		if data['action'] == 'move_paddle':
			self.paddle_y = data['paddle_y']
			# Send back the new position
			await self.send(json.dumps({
				'event': 'game_state',
				'state': {
					'paddle_y': self.paddle_y
				}
			}))