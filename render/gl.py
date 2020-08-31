from math import cos, sin

from render.bmp import BMP
from render.obj import OBJ
from render.texture import Texture
from render.math import (
    Matrix,
    norm,
    sub,
    dot,
    cross,
    get_zplane_value,
    barycentric,
    bbox,
    point_inside_polygon,
    vector,
    length,
)

class Render(object):
    def __init__(self):
        self.__image = BMP(0, 0)
        self.__viewport_start = (0, 0)
        self.__viewport_size = (0, 0)
        self.__color = self.__image.color(255, 255, 255)
        self.__filename = "out.bmp"
        self.__obj = None
        self.__active_texture = None

    def create_window(self, width, height):
        self.__image = BMP(width, height)
        self.__viewport_size = (width, height)

    def viewport(self, x, y, width, height):
        self.__viewport_start = (x, y)
        self.__viewport_size = (width, height)

    def clear(self):
        self.__image.clear()

    def clear_color(self, r, g, b):
        self.__image.clear(int(255 * r), int(255 * g), int(255 * b))

    def vertex(self, x, y):
        viewport_x = int(
            self.__viewport_size[0] * (x + 1) * (1 / 2) + self.__viewport_start[0]
        )
        viewport_y = int(
            self.__viewport_size[1] * (y + 1) * (1 / 2) + self.__viewport_start[1]
        )
        self.__image.point(viewport_x, viewport_y, self.__color)

    def flood_vertex(self, x, y):
        viewport_x = int(
            self.__viewport_size[0] * (x + 1) * (1 / 2) + self.__viewport_start[0]
        )
        viewport_y = int(
            self.__viewport_size[1] * (y + 1) * (1 / 2) + self.__viewport_start[1]
        )
        self.__image.point(viewport_x, viewport_y, self.__color)
        self.__image.point(viewport_x, viewport_y + 1, self.__color)
        self.__image.point(viewport_x + 1, viewport_y, self.__color)
        self.__image.point(viewport_x + 1, viewport_y + 1, self.__color)

    def set_color(self, r, g, b):
        self.__color = self.__image.color(int(255 * r), int(255 * g), int(255 * b))
        return self.__image.color(int(255 * r), int(255 * g), int(255 * b))

    def finish(self):
        self.__image.write(self.__filename)

    def line(self, xo, yo, xf, yf):
        """
		Draws a line between two coords
		"""
        x1 = int(self.__viewport_size[0] * (xo + 1) * (1 / 2) + self.__viewport_start[0])
        y1 = int(self.__viewport_size[1] * (yo + 1) * (1 / 2) + self.__viewport_start[1])
        x2 = int(self.__viewport_size[0] * (xf + 1) * (1 / 2) + self.__viewport_start[0])
        y2 = int(self.__viewport_size[1] * (yf + 1) * (1 / 2) + self.__viewport_start[1])
        dy = abs(y2 - y1)
        dx = abs(x2 - x1)
        steep = dy > dx
        if steep:
            x1, y1 = y1, x1
            x2, y2 = y2, x2
        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
        dy = abs(y2 - y1)
        dx = abs(x2 - x1)
        offset = 0
        threshold = dx
        y = y1
        for x in range(x1, x2 + 1):
            if steep:
                self.__image.point(y, x, self.__color)
            else:
                self.__image.point(x, y, self.__color)

            offset += dy * 2
            if offset >= threshold:
                y += 1 if y1 < y2 else -1
                threshold += 2 * dx

    def set_filename(self, filename):
        self.__filename = filename

    def load_obj(
        self,
        filename,
        translate=(0, 0, 0),
        scale=(1, 1, 1),
        fill=True,
        textured=None,
        rotate=(0, 0, 0),
        shader=None,
    ):
        """
		Loads OBJ file
		"""
        self.model_matrix(translate, scale, rotate)
        self.__obj = OBJ(filename)
        self.__obj.load()
        light = norm((0, 0, 1))
        faces = self.__obj.get_faces()
        vertices = self.__obj.get_vertices()
        materials = self.__obj.get_materials()
        text_vertices = self.__obj.get_texture_vertices()
        normals = self.__obj.get_normals()
        material_faces = self.__obj.get_material_faces()
        self.__active_texture = Texture(textured)

        print("Rendering " + filename + " ...")

        if materials:
            for mats in material_faces:
                start, stop = mats[0]
                color = materials[mats[1]].diffuse_color
                for index in range(start, stop):
                    face = faces[index]
                    vcount = len(face)

                    if vcount == 3:
                        f1 = face[0][0] - 1
                        f2 = face[1][0] - 1
                        f3 = face[2][0] - 1

                        a = self.transform(vertices[f1])
                        b = self.transform(vertices[f2])
                        c = self.transform(vertices[f3])

                        if shader:
                            t1 = face[0][1] - 1
                            t2 = face[1][1] - 1
                            t3 = face[2][1] - 1
                            nA = normals[t1]
                            nB = normals[t2]
                            nC = normals[t3]
                            self.triangle(
                                a,
                                b,
                                c,
                                base_color=color,
                                shader=shader,
                                normals=(nA, nB, nC),
                            )
                        else:
                            normal = norm(cross(sub(b, a), sub(c, a)))
                            intensity = dot(normal, light)

                            if not self.__active_texture.has_valid_texture():
                                if intensity < 0:
                                    continue
                                self.triangle(
                                    a,
                                    b,
                                    c,
                                    color=self.set_color(
                                        color[0] * intensity,
                                        color[1] * intensity,
                                        color[2] * intensity,
                                    ),
                                )

        else:
            print("No materials")
            for face in faces:
                vcount = len(face)

                if vcount == 3:
                    f1 = face[0][0] - 1
                    f2 = face[1][0] - 1
                    f3 = face[2][0] - 1

                    a = self.transform(vertices[f1])
                    b = self.transform(vertices[f2])
                    c = self.transform(vertices[f3])

                    if shader:
                        nA = normals[f1]
                        nB = normals[f2]
                        nC = normals[f3]
                        self.triangle(
                            a,
                            b,
                            c,
                            base_color=color,
                            shader=shader,
                            normals=(nA, nB, nC),
                        )
                    else:

                        normal = norm(cross(sub(b, a), sub(c, a)))
                        intensity = dot(normal, light)

                        if not self.__active_texture.has_valid_texture():
                            if intensity < 0:
                                continue
                            self.triangle(
                                a,
                                b,
                                c,
                                color=self.set_color(intensity, intensity, intensity),
                            )
                        else:
                            if self.__active_texture.has_valid_texture():
                                t1 = face[0][-1] - 1
                                t2 = face[1][-1] - 1
                                t3 = face[2][-1] - 1
                                tA = text_vertices[t1]
                                tB = text_vertices[t2]
                                tC = text_vertices[t3]
                                self.triangle(
                                    a,
                                    b,
                                    c,
                                    texture=self.__active_texture.has_valid_texture(),
                                    texture_coords=(tA, tB, tC),
                                    intensity=intensity,
                                )
                else:
                    f1 = face[0][0] - 1
                    f2 = face[1][0] - 1
                    f3 = face[2][0] - 1
                    f4 = face[3][0] - 1

                    vertex_list = [
                        self.transform(vertices[f1]),
                        self.transform(vertices[f2]),
                        self.transform(vertices[f3]),
                        self.transform(vertices[f4]),
                    ]
                    normal = norm(
                        cross(
                            sub(vertex_list[0], vertex_list[1]),
                            sub(vertex_list[1], vertex_list[2]),
                        )
                    )
                    intensity = dot(normal, light)
                    A, B, C, D = vertex_list
                    if not textured:
                        if intensity < 0:
                            continue
                        self.triangle(
                            A,
                            B,
                            C,
                            color=self.set_color(intensity, intensity, intensity),
                        )
                        self.triangle(
                            A,
                            C,
                            D,
                            color=self.set_color(intensity, intensity, intensity),
                        )
                    else:
                        if self.__active_texture.has_valid_texture():
                            t1 = face[0][-1] - 1
                            t2 = face[1][-1] - 1
                            t3 = face[2][-1] - 1
                            t4 = face[3][-1] - 1
                            tA = text_vertices[t1]
                            tB = text_vertices[t2]
                            tC = text_vertices[t3]
                            tD = text_vertices[t4]
                            self.triangle(
                                A,
                                B,
                                C,
                                texture=self.__active_texture.has_valid_texture(),
                                texture_coords=(tA, tB, tC),
                                intensity=intensity,
                            )
                            self.triangle(
                                A,
                                C,
                                D,
                                texture=self.__active_texture.has_valid_texture(),
                                texture_coords=(tA, tC, tD),
                                intensity=intensity,
                            )

    def triangle(
        self,
        A,
        B,
        C,
        color=None,
        texture=None,
        texture_coords=(),
        intensity=1,
        normals=None,
        shader=None,
        base_color=(1, 1, 1),
    ):
        """
		Draws a triangle ABC
		"""
        bbox_min, bbox_max = bbox(A, B, C)

        for x in range(bbox_min[0], bbox_max[0] + 1):
            for y in range(bbox_min[1], bbox_max[1] + 1):
                w, v, u = barycentric(A, B, C, x, y)
                if w < 0 or v < 0 or u < 0:
                    continue
                if texture:
                    tA, tB, tC = texture_coords
                    tx = tA[0] * w + tB[0] * v + tC[0] * u
                    ty = tA[1] * w + tB[1] * v + tC[1] * u
                    color = self.__active_texture.get_color(tx, ty, intensity)
                elif shader:
                    color = shader(
                        self, bary=(w, u, v), normals=normals, base_color=base_color
                    )
                z = A[2] * w + B[2] * v + C[2] * u
                if x < 0 or y < 0:
                    continue
                if z > self.__image.get_zbuffer_value(x, y):
                    self.__image.point(x, y, color)
                    self.__image.set_zbuffer_value(x, y, z)

    def load(
        self,
        filename,
        translate=(0, 0, 0),
        scale=(1, 1, 1),
        fill=True,
        textured=None,
        rotate=(0, 0, 0),
    ):
        """
		Loads OBJ file, but as a Wireframe
		"""
        light = (0, 0, 1)
        self.model_matrix(translate, scale, rotate)
        self.__obj = OBJ(filename)
        self.__obj.load()
        vertices = self.__obj.get_vertices()
        faces = self.__obj.get_faces()
        normals = self.__obj.get_normals()
        materials = self.__obj.get_materials()
        text_vertices = self.__obj.get_texture_vertices()
        print("Rendering " + filename + " (as wireframe)...")

        if materials and not textured:
            material_index = self.__obj.get_material_faces()
            for mat in material_index:
                diffuse_color = materials[mat[1]].diffuse_color
                for i in range(mat[0][0], mat[0][1]):
                    coord_list = []
                    texture_coords = []
                    for face in faces[i]:
                        coo = (
                            (vertices[face[0] - 1][0] + translate[0]) * scale[0],
                            (vertices[face[0] - 1][1] + translate[1]) * scale[1],
                            (vertices[face[0] - 1][2] + translate[2]) * scale[2],
                        )
                        coord_list.append(coo)
                    if fill:
                        curr_intensity = dot(normals[face[1] - 1], light)
                        if curr_intensity < 0:
                            continue
                        self.fill_polygon(
                            coord_list,
                            color=(
                                curr_intensity * diffuse_color[0],
                                curr_intensity * diffuse_color[1],
                                curr_intensity * diffuse_color[2],
                            ),
                        )
                    else:
                        self.draw_polygon(coord_list)

        elif textured and not materials:
            for face in faces:
                coord_list = []
                texture_coords = []
                for vertexN in face:
                    coo = (
                        (vertices[vertexN[0] - 1][0] + translate[0]) * scale[0],
                        (vertices[vertexN[0] - 1][1] + translate[1]) * scale[1],
                        (vertices[vertexN[0] - 1][2] + translate[2]) * scale[2],
                    )
                    coord_list.append(coo)
                    if len(vertexN) > 2:
                        text = (
                            (text_vertices[vertexN[2] - 1][0] + translate[0]) * scale[0],
                            (text_vertices[vertexN[2] - 1][1] + translate[1]) * scale[1],
                        )
                        texture_coords.append(text)
                if fill:
                    curr_intensity = dot(normals[vertexN[1] - 1], light)
                    if curr_intensity < 0:
                        continue
                    self.fill_polygon(
                        coord_list,
                        intensity=curr_intensity,
                        texture=textured,
                        texture_coords=texture_coords,
                    )
                else:
                    self.draw_polygon(coord_list)
                coord_list = []
        else:
            for face in faces:
                coord_list = []
                texture_coords = []
                for vertexN in face:
                    coo = vertices[vertexN[0] - 1]
                    coord_list.append(coo)
                if fill:
                    curr_intensity = dot(normals[vertexN[1] - 1], light)
                    if curr_intensity < 0:
                        continue
                    self.fill_polygon(coord_list, color=(curr_intensity, curr_intensity, curr_intensity))
                else:
                    self.draw_polygon(coord_list)
                coord_list = []

    def draw_polygon(self, vertex_list):
        """
		Draws a polygon
		"""
        for i in range(len(vertex_list)):
            if i == len(vertex_list) - 1:
                start = vertex_list[i]
                final = vertex_list[0]
            else:
                start = vertex_list[i]
                final = vertex_list[i + 1]
            self.line(start[0], start[1], final[0], final[1])

    def fill_polygon(
        self,
        vertex_list,
        color=None,
        texture=None,
        intensity=1,
        texture_coords=(),
        zVal=True,
    ):
        """
		Draws and fills a polygon
		"""
        curr_intensity = intensity
        if not texture:
            color = (
                self.__color
                if color == None
                else self.__image.color(
                    int(255 * color[0]), int(255 * color[1]), int(255 * color[2])
                )
            )
        else:
            if self.__active_texture == None:
                text = Texture(texture)
                self.__active_texture = text
            else:
                text = self.__active_texture
        start_x = sorted(vertex_list, key=lambda tup: tup[0])[0][0]
        final_x = sorted(vertex_list, key=lambda tup: tup[0], reverse=True)[0][0]

        start_y = sorted(vertex_list, key=lambda tup: tup[1])[0][1]
        final_y = sorted(vertex_list, key=lambda tup: tup[1], reverse=True)[0][1]

        start_x = int(
            self.__viewport_size[0] * (start_x + 1) * (1 / 2) + self.__viewport_start[0]
        )
        final_x = int(
            self.__viewport_size[0] * (final_x + 1) * (1 / 2) + self.__viewport_start[0]
        )

        start_y = int(
            self.__viewport_size[0] * (start_y + 1) * (1 / 2) + self.__viewport_start[0]
        )
        final_y = int(
            self.__viewport_size[0] * (final_y + 1) * (1 / 2) + self.__viewport_start[0]
        )
        for x in range(start_x, final_x + 1):
            for y in range(start_y, final_y + 1):
                is_inside = point_inside_polygon(self.normalize_x(x), self.normalize_y(y), vertex_list)
                if is_inside:
                    if texture:
                        A = (
                            self.normalize_inv_x(vertex_list[0][0]),
                            self.normalize_inv_x(vertex_list[0][1]),
                        )
                        B = (
                            self.normalize_inv_x(vertex_list[1][0]),
                            self.normalize_inv_x(vertex_list[1][1]),
                        )
                        C = (
                            self.normalize_inv_x(vertex_list[2][0]),
                            self.normalize_inv_x(vertex_list[2][1]),
                        )
                        w, v, u = barycentric(A, B, C, x, y)
                        A = texture_coords[0]
                        B = texture_coords[1]
                        C = texture_coords[2]
                        tx = A[0] * w + B[0] * v + C[0] * u
                        ty = A[1] * w + B[1] * v + C[1] * u
                        color = text.get_color(tx, ty, intensity=curr_intensity)
                    z = get_zplane_value(vertex_list, x, y)
                    if z > self.__image.get_zbuffer_value(x, y):
                        self.__image.point(x, y, color)
                        self.__image.set_zbuffer_value(x, y, z)

    def normalize_x(self, x):
        """
		Normalizes x coord
		"""
        normalize_x = ((2 * x) / self.__viewport_size[0]) - self.__viewport_start[0] - 1
        return normalize_x

    def normalize_y(self, y):
        """
		Normalizes y coord
		"""
        normalize_y = ((2 * y) / self.__viewport_size[1]) - self.__viewport_start[1] - 1
        return normalize_y

    def normalize_inv_x(self, x):
        """
		Normalizes x inv coord
		"""
        normalize_x = int(self.__viewport_size[0] * (x + 1) * (1 / 2) + self.__viewport_start[0])
        return normalize_x

    def normalize_inv_y(self, y):
        """
		Normalizes y inv coord
		"""
        normalize_y = int(self.__viewport_size[0] * (y + 1) * (1 / 2) + self.__viewport_start[0])
        return normalize_y

    def render_zbuffer(self, filename=None):
        """
		Renders the z buffer stored
		"""
        if filename == None:
            filename = self.__filename.split(".")[0] + "ZBuffer.bmp"
        self.__image.write(filename, zbuffer=True)

    def model_matrix(self, translate=(0, 0, 0), scale=(1, 1, 1), rotate=(0, 0, 0)):
        """
		Generates model matrix
		"""
        translation_matrix = Matrix(
            [
                [1, 0, 0, translate[0]],
                [0, 1, 0, translate[1]],
                [0, 0, 1, translate[2]],
                [0, 0, 0, 1],
            ]
        )
        a = rotate[0]
        rotation_matrix_x = Matrix(
            [
                [1, 0, 0, 0],
                [0, cos(a), -sin(a), 0],
                [0, sin(a), cos(a), 0],
                [0, 0, 0, 1],
            ]
        )
        a = rotate[1]
        rotation_matrix_y = Matrix(
            [
                [cos(a), 0, sin(a), 0],
                [0, 1, 0, 0],
                [-sin(a), 0, cos(a), 0],
                [0, 0, 0, 1],
            ]
        )
        a = rotate[2]
        rotation_matrix_z = Matrix(
            [
                [cos(a), -sin(a), 0, 0],
                [sin(a), cos(a), 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1],
            ]
        )
        rotation_matrix = rotation_matrix_x * rotation_matrix_y * rotation_matrix_z
        scale_matrix = Matrix(
            [
                [scale[0], 0, 0, 0],
                [0, scale[1], 0, 0],
                [0, 0, scale[2], 0],
                [0, 0, 0, 1],
            ]
        )
        self.Model = translation_matrix * rotation_matrix * scale_matrix

    def view_matrix(self, x, y, z, center):
        """
		Generates view matrix
		"""
        m = Matrix(
            [
                [x[0], x[1], x[2], 0],
                [y[0], y[1], y[2], 0],
                [z[0], z[1], z[2], 0],
                [0, 0, 0, 1],
            ]
        )
        o = Matrix(
            [
                [1, 0, 0, -center[0]],
                [0, 1, 0, -center[1]],
                [0, 0, 1, -center[2]],
                [0, 0, 0, 1],
            ]
        )
        self.View = m * o

    def projection_matrix(self, coeff):
        """
		Generates projection matrix
		"""
        self.Projection = Matrix(
            [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, coeff, 1]]
        )

    def viewport_matrix(self, x=0, y=0):
        """
		Generates viewport matrix
		"""
        self.Viewport = Matrix(
            [
                [self.__image.width / 2, 0, 0, x + self.__image.width / 2],
                [0, self.__image.height / 2, 0, y + self.__image.height / 2],
                [0, 0, 128, 128],
                [0, 0, 0, 1],
            ]
        )

    def look_at(self, eye, center, up):
        """
		Defines camera position
		"""
        z = norm(sub(eye, center))
        x = norm(cross(up, z))
        y = norm(cross(z, x))
        self.view_matrix(x, y, z, center)
        self.projection_matrix(-1 / length(sub(eye, center)))
        self.viewport_matrix()

    def transform(self, vertices):
        """
		Transforms with augmented matrix
		"""
        augmented = Matrix([[vertices[0]], [vertices[1]], [vertices[2]], [1]])
        transformed_vertex = (
            self.Viewport * self.Projection * self.View * self.Model * augmented
        )
        transformed_vertex = transformed_vertex.tolist()
        transformed = [
            round(transformed_vertex[0][0] / transformed_vertex[3][0]),
            round(transformed_vertex[1][0] / transformed_vertex[3][0]),
            round(transformed_vertex[2][0] / transformed_vertex[3][0]),
        ]
        return transformed
