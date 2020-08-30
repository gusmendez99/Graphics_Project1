from bmp import BMP

class Texture(object):
	"""
	Texture class
	"""

	def __init__(self, filename):
		"""
		Initialized texture values
		"""
		self.filename = filename
		self.active_texture = None
		self.load()

	def load(self):
		"""
		Loads Texture
		"""
		print("Loading texture...")
		self.active_texture = BMP(0, 0)
		try:
			self.active_texture.load(self.filename)
		except:
			print("No texture found.")
			self.active_texture = None

	def write(self):
		"""
		Writes texture (if needed as BMP)
		"""
		self.active_texture.write(self.filename[:len(self.filename)-4]+"text.bmp")

	def get_color(self, tx, ty, intensity=1):
		"""
		Gets color from texture coords
		"""
		x = self.active_texture.width -1 if ty == 1 else int(ty*self.active_texture.width)
		y = self.active_texture.height -1 if tx == 1 else int(tx*self.active_texture.height)
		return bytes(map(lambda b: round(b*intensity) if b*intensity > 0 else 0, self.active_texture.framebuffer[y][x]))

	def is_textured(self):
		return self.active_texture != None