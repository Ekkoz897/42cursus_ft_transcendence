
GAME_SETTINGS = {
	'field': {
		'width': 800,
		'height': 600
	},
	'paddle': {
		'width': 20,
		'height': 100,
		'start_y': 250
	},
	'ball': {
		'size': 10,
		'start_x': 400,
		'start_y': 300,
	}
}

class GameObject:
	def __init__(self, x=0, y=0, width=0, height=0):
		self.position = (x, y)
		self.velocity = (0, 0)
		self.width = 0
		self.height = 0

	def update(self):
		x, y = self.position
		dx, dy = self.velocity
		self.position = (x + dx, y + dy)

	def to_dict(self):
		return {
			'x': self.position[0],
			'y': self.position[1],
			'dx': self.velocity[0],
			'dy': self.velocity[1],
			'width': self.width,
			'height': self.height
		}

class Paddle(GameObject):
	def __init__(self):
		super().__init__(
			x=GAME_SETTINGS['paddle']['start_x'],
			y=GAME_SETTINGS['paddle']['start_y'],
			width=GAME_SETTINGS['paddle']['width'],
			height=GAME_SETTINGS['paddle']['height']
		)

