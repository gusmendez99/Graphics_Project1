"""
    Universidad del Valle de Guatemala
    Gustavo Mendez - 18500

    obj.py - parse a .obj file to simple array values
"""
import struct
from utils.color import color


class Obj(object):
    def __init__(self, filename):
        self.vertices =[] 
        self.tvertices = []
        self.normals =[]
        self.faces = []
        with open(filename) as f:
            self.lines = f.read().splitlines()
        self.read()

    def read(self):
        key = ""
        for line in self.lines:
            if line:
                prefix, value = line.split(' ', 1)

                """ if prefix == "usemtl":
                    key = value
                    self.matf[key] = [] """
                if prefix == "v":
                    self.vertices.append(list(map(float, value.split(' '))))
                if prefix == "vn":
                    self.normals.append(list(map(float, value.split(' '))))
                elif prefix == "vt":
                    self.tvertices.append(list(map(float, value.split(' '))))
                elif prefix == "f":
                    self.faces.append([list(map(int, face.split('/'))) for face in value.split(' ')])
                    #self.matf[key].append([list(map(int, face.split('/'))) for face in value.split(' ')])



class Texture(object):
    def __init__(self, path):
        self.path = path
        self.read()

    def read(self):
        img = open(self.path, "rb")
        img.seek(2 + 4 + 4)
        header_size = struct.unpack("=l", img.read(4))[0]
        img.seek(2 + 4 + 4 + 4 + 4)
        self.width = struct.unpack("=l", img.read(4))[0]
        self.height = struct.unpack("=l", img.read(4))[0]
        self.pixels = []
        img.seek(header_size)

        # 24-bits bmp
        for y in range(self.height):
            self.pixels.append([])
            for x in range(self.width):
                b = ord(img.read(1))  # ord se usa para obtener el numero de un char
                g = ord(img.read(1))
                r = ord(img.read(1))
                self.pixels[y].append(color(r, g, b))

        img.close()

    # gets color (from normalized coords)
    def get_color(self, tx, ty, intensity):
        x = int(tx * self.width)
        y = int(ty * self.height)
        return bytes(map(lambda b: round(b*intensity) if (b *intensity > 0) else 0,(self.pixels[y][x])))
    
    def get_simple_color(self, tx, ty):
        x = int(tx * self.width)
        y = int(ty * self.height)
        return bytes(map(lambda b: round(b) if (b > 0) else 0,(self.pixels[y][x])))
