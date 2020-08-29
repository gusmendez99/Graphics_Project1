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
from shaders import gourad

BLACK = color(0, 0, 0)
WHITE = color(255, 255, 255)


class Render(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.current_color = WHITE
        self.light = V3(0, 0, 1)
        self.active_shader = None
        self.active_texture = None
        self.active_vertex_array = []
        self.clear()

    def clear(self):
        self.framebuffer = [[BLACK for x in range(self.width)] for y in range(self.height)]
        self.zbuffer = [
            [-float("inf") for x in range(self.width)] for y in range(self.height)
        ]

    def point(self, x, y, color):
        self.framebuffer[y][x] = color

    """ def clear_color(self):
        r, g, b = BLACK
        bg_color = color(r, g, b)
        self.framebuffer = [
            [bg_color for x in range(self.width)] for y in range(self.height)
        ] """

    def clear_color(self, r=1, g=1, b=1):
        # get normalized colors as array
        normalized = normalize_color([r, g, b])
        clearColor = color(normalized[0], normalized[1], normalized[2])

        self.framebuffer = [
            [clearColor for x in range(self.width)] for y in range(self.height)
        ]

    def triangle(self, A, B, C, color= BLACK, texture= None, texture_coords=(), intensity=1, normals=(None, None, None), light = V3(0,1,1)):
        bbox_min, bbox_max = bbox(A, B, C)

        fill_color = color
        
        for x in range(bbox_min.x, bbox_max.x + 1):
            for y in range (bbox_min.y, bbox_max.y + 1):
                w, v, u = barycentric(A,B,C, V2(x,y))
                if w< 0 or v <0 or u<0:
                    continue
                
                if texture and x>=0 and y >=0 and x < self.width and y< self.height:
                    tA, tC, tB = texture_coords
                    tx = tA.x*w + tB.x*v + tC.x*u
                    ty = tA.y*w + tB.y*v + tC.y*u
                    if self.active_shader != None:
                        fill_color = self.active_shader(self, x, y, bary_coords=(w,v,u), normals=normals, light = light, texture_coords = (tx, ty))
                    else:
                        fill_color = texture.get_color(tx, ty, intensity)

                    z = A.z * w + B.z * v  + C.z * u
                    
                    if z > self.zbuffer[y][x]:
                        self.point(x, y, fill_color)
                        self.zbuffer[y][x] = z

                if not texture and x>=0 and y >=0 and x < self.width and y< self.height:
                    fill_color = color(fill_color[0],fill_color[1],fill_color[2])
                    z = A.z * w + B.z * v  + C.z * u
                    if z > self.zbuffer[x][y]:
                        self.point(x,y,fill_color)
                        self.zbuffer[x][y] = z

    def transform(self, vertex):
        augmented = [[float(vertex[0])], [float(vertex[1])], [float(vertex[2])], [1.0]]

        # matrix mul from outside -> inside
        vertices = matrix_mul(
            matrix_mul(
                matrix_mul(matrix_mul(self.Viewport, self.Projection), self.View),
                self.Model,
            ),
            augmented,
        )

        vf = V3(
            round(vertices[0][0] / vertices[3][0]),
            round(vertices[1][0] / vertices[3][0]),
            round(vertices[2][0] / vertices[3][0]),
        )
        return vf

    # Loads initial model matrix
    def load_model_matrix(self, translate, scale, rotate):
        translate = V3(*translate)
        rotate = V3(*rotate)
        scale = V3(*scale)
        translate_matrix = [
            [1.0, 0.0, 0.0, translate.x],
            [0.0, 1.0, 0.0, translate.y],
            [0.0, 0.0, 1.0, translate.z],
            [0.0, 0.0, 0.0, 1.0],
        ]
        scale_matrix = [
            [scale.x, 0.0, 0.0, 0.0],
            [0.0, scale.y, 0.0, 0.0],
            [0.0, 0.0, scale.z, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ]

        rotation_matrix_x = [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, cos(rotate.x), -sin(rotate.x), 0.0],
            [0.0, sin(rotate.x), cos(rotate.x), 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ]
        rotation_matrix_y = [
            [cos(rotate.y), 0.0, sin(rotate.y), 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [-sin(rotate.y), 0.0, cos(rotate.y), 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ]
        rotation_matrix_z = [
            [cos(rotate.z), -sin(rotate.z), 0.0, 0.0],
            [sin(rotate.z), cos(rotate.z), 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ]

        rotation_matrix = matrix_mul(
            matrix_mul(rotation_matrix_x, rotation_matrix_y), rotation_matrix_z
        )
        self.Model = matrix_mul(
            matrix_mul(translate_matrix, rotation_matrix), scale_matrix
        )

    # loads view matrix
    def load_view_matrix(self, x, y, z, center):
        M = [
            [x.x, x.y, x.z, 0.0],
            [y.x, y.y, y.z, 0.0],
            [z.x, z.y, z.z, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ]

        O = [
            [1.0, 0.0, 0.0, -center.x],
            [0.0, 1.0, 0.0, -center.y],
            [0.0, 0.0, 1.0, -center.z],
            [0.0, 0.0, 0.0, 1.0],
        ]

        self.View = matrix_mul(M, O)

    # loads projection matrix
    def load_projection_matrix(self, coefficient):
        self.Projection = [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, -coefficient, 1.0],
        ]

    # loads viewport matrix
    def load_viewport_matrix(self, x=0, y=0):
        self.Viewport = [
            [self.width / 2, 0.0, 0.0, y + (self.width / 2)],
            [0.0, self.height / 2, 0.0, x + (self.height / 2)],
            [0.0, 0.0, 128.0, 128.0],
            [0.0, 0.0, 0.0, 1.0],
        ]

    """
    eye: xyz camera location 
    center: camera center view
    up: camera vector
    """

    def look_at(self, eye, up, center):

        # z vector comes from center to eye
        z = norm(sub(eye, center))
        x = norm(cross(up, z))
        y = norm(cross(z, x))

        self.load_view_matrix(x, y, z, center)
        self.load_projection_matrix(-1.0 / length(sub(eye, center)))
        self.load_viewport_matrix()

    # draw just shape of model
    def draw_arrays(self, polygon):
        if polygon == "TRIANGLES":
            try:
                while True:
                    self.triangle()
            except StopIteration:
                print("Done.")

    # loads background image
    def load_background(self, texture=None):
        for x in range(self.width):
            for y in range(self.height):
                color = texture.pixels[y][x]
                self.point(x, y, color)

    def load(self, filename, texture, translate =(0,0,0), scale= (1, 1, 1), rotate = (0,0,0),
            eye = (0,0.5,0.5), up = (0,1,0), center=(0,0,0), light = V3(0,0,1)):
        
        self.active_texture = texture
        #self.active_shader = gourad

        model = Obj(filename)

        self.load_viewport_matrix()
        self.load_model_matrix(translate, scale, rotate)
        self.look_at(V3(*eye), V3(*up), V3(*center))

        for face in model.faces:
            vcount = len(face)

            if vcount == 3:    
                n1 = face[0][2] -1
                n2 = face[1][2] -1
                n3 = face[2][2] -1

                na = V3(*model.normals[n1])
                nb = V3(*model.normals[n2])
                nc = V3(*model.normals[n3])
                
                f1 = face[0][0] -1
                f2 = face[1][0] -1
                f3 = face[2][0] -1

                a = self.transform(model.vertices[f1])
                b = self.transform(model.vertices[f2])
                c = self.transform(model.vertices[f3])

                normal = norm(cross(sub(b,a), sub(c, a)))
                intensity = dot(normal, light)
                shade = round(255 * intensity)

                if shade <0 :
                    continue
                elif shade > 255:
                    shade = 255

                if intensity > 1.0:
                    intensity = 1

                        
                if not texture:
                    self.triangle(
                        a,b,c, 
                        texture = None, 
                        texture_coords = (),
                        intensity = intensity,
                        normals = (na, nc, nb),
                        light=light
                    )
                    
                else:
                    vertex_buffer_object = []
                    for facepart in face:
                        if len(model.tvertices[facepart[1]-1]) == 2:
                            tvertex = V2(*model.tvertices[facepart[1]-1])
                        elif len(model.tvertices[facepart[1]-1]) == 3:
                            tvertex = V3(*model.tvertices[facepart[1]-1])
                        vertex_buffer_object.append(tvertex)

                    t1 = face[0][1]-1
                    t2 = face[1][1]-1
                    t3 = face[2][1]-1

                    tA = vertex_buffer_object[0]
                    tB = vertex_buffer_object[1]
                    tC = vertex_buffer_object[2]

                    if self.active_shader != None:
                        self.triangle(
                            a,b,c,
                            texture=texture,
                            texture_coords= (tA, tB, tC), 
                            intensity = intensity,
                            normals = (na, nc, nb),
                            light=light
                        )
                    else:
                        self.triangle(
                            a,b,c,
                            texture=texture,
                            texture_coords= (tA, tB, tC), 
                            intensity = intensity,
                        )

    # starts creating a new bmp file
    def finish(self, filename="out.bmp"):
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
