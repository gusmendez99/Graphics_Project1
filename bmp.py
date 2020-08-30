import struct

class BMP(object):
	"""
	BMP Class
	Attr: width (int) and height (int)
	"""

	def __init__(self, width, height):
		"""
		Initializes values
		"""
		self.width = abs(int(width))
		self.height = abs(int(height))
		self.framebuffer = []
		self.zbuffer = []
		self.clear()

	def clear(self, r=0, b=0, g=0):
		"""
		Clears bitmap color
		"""
		self.framebuffer = [
			[self.color(r, g, b) for x in range(self.width)] for y in range(self.height)
		]

		self.zbuffer = [
			[-float("inf") for x in range(self.width)] for y in range(self.height)
		]

	def color(self, r=0, g=0, b=0):
		"""
		Parses color values as bytes
		"""
		if (r > 255 or g > 255 or b > 255 or r < 0 or g < 0 or b <0):
			r = 0
			g = 0
			b = 0
		return bytes([b, g, r])

	def point(self, x, y, color):
		"""
		Changes pixel color
		"""
		if x < self.width and y < self.height:
			try:
				self.framebuffer[x][y] = color
			except Exception as e:
				print(e)
				pass

	def char(self, my_char):
		"""
		Returns encoded char
		"""
		return struct.pack("=c", my_char.encode("ascii"))

	def padding(self, base, c):
		"""
		Adds padding to a number
		"""
		if c % base == 0:
			return c
		else:
			while c % base:
				c += 1
			return c

	def word(self, my_char):
		"""
		Returns encoded word
		"""
		return struct.pack("=h", my_char)

	def dword(self, my_char):
		"""
		Returns encoded dword
		"""
		return struct.pack("=l", my_char)

	def write(self, filename, zbuffer=False):
		"""
		Writes BMP file
		"""
		BLACK = self.color(0, 0, 0)
		print("Writing bmp file with name: " + filename)
		import os

		os.makedirs(os.path.dirname(filename), exist_ok=True)
		file = open(filename, "bw")

		# File Header(14 bytes)
		file.write(self.char("B"))
		file.write(self.char("M"))  # BM
		file.write(self.dword(14 + 40 + self.width * self.height * 3))  # File size
		file.write(self.dword(0))
		file.write(self.dword(14 + 40))

		# Image Header (14 bytes)
		file.write(self.dword(40))
		file.write(self.dword(self.width))
		file.write(self.dword(self.height))
		file.write(self.word(1))
		file.write(self.word(24))
		file.write(self.dword(0))
		file.write(self.dword(self.width * self.height * 3))
		file.write(self.dword(0))
		file.write(self.dword(0))
		file.write(self.dword(0))
		file.write(self.dword(0))

		for x in range(self.width):
			for y in range(self.height):
				if x < self.width and y < self.height:
					if zbuffer:
						if self.zbuffer[y][x] == -float("inf"):
							file.write(BLACK)
						else:
							z = abs(int(self.zbuffer[y][x] * 255))
							file.write(self.color(z, z, z))
					else:
						file.write(self.framebuffer[y][x])
				else:
					file.write(self.char("c"))

		file.close()

	def load(self, filename):
		"""
		Loads BMP file
		"""
		file = open(filename, "rb")
		file.seek(10)
		headerSize = struct.unpack("=l", file.read(4))[0]
		file.seek(18)

		self.width = struct.unpack("=l", file.read(4))[0]
		self.height = struct.unpack("=l", file.read(4))[0]
		self.clear()
		for y in range(self.height):
			for x in range(self.width):
				if x < self.width and y < self.height:
					b, g, r = ord(file.read(1)), ord(file.read(1)), ord(file.read(1))
					self.point(x, y, self.color(r, g, b))
		file.close()

	def get_zbuffer_value(self, x, y):
		"""
		Get a value of (x,y) coordinates inside of the zbuffer
		"""
		if x < self.width and y < self.height:
			return self.zbuffer[x][y]
		else:
			return -float("inf")

	def set_zbuffer_value(self, x, y, z):
		"""
		Set z value on (x,y) coordinates on zbuffer
		"""
		if x < self.width and y < self.height:
			self.zbuffer[x][y] = z
			return 1
		else:
			return 0
