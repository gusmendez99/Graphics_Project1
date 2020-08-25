"""
    Universidad del Valle de Guatemala
    Gustavo Mendez - 18500

    gl.py - all logic to create a bmp file
"""

from utils.color import color, normalize_color
from math import cos, sin
from utils.encoder import char, dword, word
from utils.math import *

from obj import Obj

BLACK = 0, 0, 0
# Saturn color intervals, up to center
MELON = 136, 195, 222
BROWN = 105, 145, 170
LAVENDER = 156, 152, 164

class Render(object):
    # glInit dont needed, 'cause we have an __init__ func
    def __init__(self):
        self.active_shader = None
        self.active_texture = None
        self.framebuffer = []
        self.width = 800
        self.height = 800
        self.viewport_x = 0
        self.viewport_y = 0
        self.viewport_width = 800
        self.viewport_height = 800
        self.clear()

        self.zbuffer = [
            [-float('inf') for x in range(self.width)] for y in range(self.height)
        ]
        # For shader use
        self.shape = None

    def point(self, x, y, color):
        self.framebuffer[y][x] = color

    def create_window(self, width, height):
        self.height = height
        self.width = width

    def viewport(self, x, y, width, height):
        # Setting viewport initial values
        self.viewport_x = x
        self.viewport_y = y
        self.viewport_height = height
        self.viewport_width = width

    def clear(self):
        r, g, b = BLACK
        bg_color = color(r, g, b)
        self.framebuffer = [
            [bg_color for x in range(self.width)] for y in range(self.height)
        ]

    def clear_color(self, r=1, g=1, b=1):
        # get normalized colors as array
        normalized = normalize_color([r, g, b])
        clearColor = color(normalized[0], normalized[1], normalized[2])

        self.framebuffer = [
            [clearColor for x in range(self.width)] for y in range(self.height)
        ]

    def triangle(self, A, B, C):
        xmin, xmax, ymin, ymax = bbox(A, B, C)

        for x in range(xmin, xmax + 1):
            for y in range(ymin, ymax + 1):
                P = V2(x, y)
                w, v, u = barycentric(A, B, C, P)
                if w < 0 or v < 0 or u < 0:
                    # point is outside
                    continue

                z = A.z * u + B.z * v + C.z * w

                r, g, b = self.shader(
                    x, y
                )

                shader_color = color(r, g, b)

                if z > self.zbuffer[y][x]:
                    self.point(x, y, shader_color)
                    self.zbuffer[y][x] = z

    # Loads initial model matrix 
    def load_model_matrix(self, translate, scale, rotate):
        translate = Vector3(*translate)
        rotate = Vector3(*rotate)
        scale = Vector3(*scale)
        translate_matrix = [
            [1.0,0.0,0.0,translate.x],
            [0.0,1.0,0.0,translate.y],
            [0.0,0.0,1.0,translate.z],
            [0.0,0.0,0.0,1.0],
        ]
        scale_matrix = [
            [scale.x,0.0,0.0,0.0],
            [0.0,scale.y,0.0,0.0],
            [0.0,0.0,scale.z,0.0],
            [0.0,0.0,0.0,1.0],
        ]

        rotation_matrix_x = [
            [1.0,0.0,0.0,0.0],
            [0.0,cos(rotate.x),-sin(rotate.x),0.0],
            [0.0,sin(rotate.x), cos(rotate.x),0.0],
            [0.0,0.0,0.0,1.0]
        ]
        rotation_matrix_y = [
            [cos(rotate.y),0.0,sin(rotate.y),0.0],
            [0.0,1.0,0.0,0.0],
            [-sin(rotate.y),0.0, cos(rotate.y),0.0],
            [0.0,0.0,0.0,1.0]
        ]
        rotation_matrix_z = [
            [cos(rotate.z),-sin(rotate.z),0.0,0.0],
            [sin(rotate.z), cos(rotate.z),0.0,0.0],
            [0.0,0.0,1.0,0.0],
            [0.0,0.0,0.0,1.0]
        ]
        
        rotation_matrix = matrix_mul(matrix_mul(rotation_matrix_x, rotation_matrix_y), rotation_matrix_z)
        self.model = matrix_mul(matrix_mul(translate_matrix, rotation_matrix), scale_matrix)


    

    # loads view matrix
    def load_view_matrix(self, x, y, z, center):
        M = [
            [x.x, x.y, x.z,0.0],
            [y.x, y.y, y.z,0.0],
            [z.x, z.y, z.z,0.0],
            [0.0,0.0,0.0,1.0]

        ]

        O = [
            [1.0,0.0,0.0,-center.x],
            [0.0,1.0,0.0,-center.y],
            [0.0,0.0,1.0,-center.z],
            [0.0,0.0,0.0,1.0]

        ]

        self.view = matrix_mul(M, O)
    
    # loads projection matrix
    def load_projection_matrix(self, coefficient):
        self.projection = [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, -coefficient, 1.0],
        ]

    # loads viewport matrix
    def load_viewport_matrix(self, x=0, y=0):
        self.viewport = [
            [self.width/2, 0.0, 0.0, y + (self.width/2)],
            [0.0, self.height/2, 0.0, x + (self.height/2)],
            [0.0, 0.0, 128.0, 128.0],
            [0.0, 0.0, 0.0, 1.0],
        ]
    
    """
    eye: xyz camera location 
    center: camera center view
    up: vector over camera
    """
    def look_at(self, eye, up, center):
        
        #z vector comes from center to eye
        z = norm(sub(eye,center))
        x = norm(cross(up,z))
        y = norm(cross(z,x))

        self.load_view_matrix(x, y, z, center)
        self.load_projection_matrix(-1.0 / length(sub(eye,center)))
        self.load_viewport_matrix()
    
    # draw just shape of model
    def draw_arrays(self, polygon):
        if polygon == 'TRIANGLES':
        try:
            while True:
                self.triangle()
        except StopIteration:
            print('Done.')

    # loads background image
    def load_background(self, texture= None):
        for x in range(self.width):
            for y in range (self.height):
                color = texture.pixels[y][x]
                self.point(x, y, color)
    
    def load(self, filename="default.obj", translate=[0, 0], scale=[1, 1], shape=None):
        model = Obj(filename)
        self.shape = shape

        for face in model.faces:
            vcount = len(face)

            if vcount == 3:
                face1 = face[0][0] - 1
                face2 = face[1][0] - 1
                face3 = face[2][0] - 1

                v1 = model.vertices[face1]
                v2 = model.vertices[face2]
                v3 = model.vertices[face3]

                x1 = round((v1[0] * scale[0]) + translate[0])
                y1 = round((v1[1] * scale[1]) + translate[1])
                z1 = round((v1[2] * scale[2]) + translate[2])

                x2 = round((v2[0] * scale[0]) + translate[0])
                y2 = round((v2[1] * scale[1]) + translate[1])
                z2 = round((v2[2] * scale[2]) + translate[2])

                x3 = round((v3[0] * scale[0]) + translate[0])
                y3 = round((v3[1] * scale[1]) + translate[1])
                z3 = round((v3[2] * scale[2]) + translate[2])

                a = V3(x1, y1, z1)
                b = V3(x2, y2, z2)
                c = V3(x3, y3, z3)

                vn0 = model.normals[face[0][2] - 1]
                vn1 = model.normals[face[1][2] - 1]
                vn2 = model.normals[face[2][2] - 1]

                self.triangle(a, b, c)

            else:
                face1 = face[0][0] - 1
                face2 = face[1][0] - 1
                face3 = face[2][0] - 1
                face4 = face[3][0] - 1

                v1 = model.vertices[face1]
                v2 = model.vertices[face2]
                v3 = model.vertices[face3]
                v4 = model.vertices[face4]

                x1 = round((v1[0] * scale[0]) + translate[0])
                y1 = round((v1[1] * scale[1]) + translate[1])
                z1 = round((v1[2] * scale[2]) + translate[2])

                x2 = round((v2[0] * scale[0]) + translate[0])
                y2 = round((v2[1] * scale[1]) + translate[1])
                z2 = round((v2[2] * scale[2]) + translate[2])

                x3 = round((v3[0] * scale[0]) + translate[0])
                y3 = round((v3[1] * scale[1]) + translate[1])
                z3 = round((v3[2] * scale[2]) + translate[2])

                x4 = round((v4[0] * scale[0]) + translate[0])
                y4 = round((v4[1] * scale[1]) + translate[1])
                z4 = round((v4[2] * scale[2]) + translate[2])

                a = V3(x1, y1, z1)
                b = V3(x2, y2, z2)
                c = V3(x3, y3, z3)
                d = V3(x4, y4, z4)

                self.triangle(a, b, c)
                self.triangle(a, c, d)

    def finish(self, filename="out.bmp"):
        # starts creating a new bmp file
        f = open(filename, "bw")

        f.write(char("B"))
        f.write(char("M"))
        f.write(dword(14 + 40 + self.width * self.height * 3))
        f.write(dword(0))
        f.write(dword(14 + 40))

        # image header
        f.write(dword(40))
        f.write(dword(self.width))
        f.write(dword(self.height))
        f.write(word(1))
        f.write(word(24))
        f.write(dword(0))
        f.write(dword(self.width * self.height * 3))
        f.write(dword(0))
        f.write(dword(0))
        f.write(dword(0))
        f.write(dword(0))

        # Finishing placing points
        try:
            for x in range(self.height):
                for y in range(self.width):
                    f.write(self.framebuffer[x][y])
        except:
            print("Your obj file is too big. Try another scale/translate values")

        f.close()
