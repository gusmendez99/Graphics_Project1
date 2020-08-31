from render.bmp import BMP


class Texture(object):
    """
	"""

    def __init__(self, filename):
        """
		"""
        self.__filename = filename
        self.__active_texture = None
        self.load()

    def load(self):
        """
		"""
        print("Loading texture...")
        self.__active_texture = BMP(0, 0)
        try:
            self.__active_texture.load(self.__filename)
        except:
            print("No texture found.")
            self.__active_texture = None

    def write(self):
        """
		"""
        self.__active_texture.write(
            self.__filename[: len(self.__filename) - 4] + "texture.bmp"
        )

    def get_color(self, tx, ty, intensity=1):
        """
		"""
        x = (
            self.__active_texture.width - 1
            if ty == 1
            else int(ty * self.__active_texture.width)
        )
        y = (
            self.__active_texture.height - 1
            if tx == 1
            else int(tx * self.__active_texture.height)
        )
        return bytes(
            map(
                lambda b: round(b * intensity) if b * intensity > 0 else 0,
                self.__active_texture.framebuffer[y][x],
            )
        )

    def has_valid_texture(self):
        return self.__active_texture != None
