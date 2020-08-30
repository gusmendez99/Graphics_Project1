from bmp import BMP
from obj import OBJ
from texture import Texture
from matrix import Matrix
from math import cos, sin


class Render(object):

	def __init__(self):
		"""
		Initializes render
		"""
		self.image = BMP(0,0)
		self.viewport_start = (0,0)
		self.viewport_size = (0,0)
		self.color = self.image.color(255,255,255)
		self.filename = "output.bmp"
		self.obj = None
		self.texture = None

	def set_image(self, bmp):
		"""
		Replace image with new BMP
		"""
		self.image = bmp

	def create_window(self, width, height):
		"""
		Sets window size
		"""
		self.image = BMP(width, height)
		self.viewport_size = (width, height)

	def viewport(self, x, y, width, height):
		"""
		Sets image size (inner size)
		"""
		self.viewport_start = (x, y)
		self.viewport_size = (width,height)

	def clear(self):
		"""
		Clears image color
		"""
		self.image.clear()

	def clear_color(self, r, g, b):
		"""
		Clears image color with rgb color passed
		"""
		self.image.clear(int(255*r), int(255*g), int(255*b))

	def vertex(self, x, y):
		"""
		Replaces color pixel inside viewport
		"""
		view_x = int(self.viewport_size[0] * (x+1) * (1/2) + self.viewport_start[0])
		view_y = int(self.viewport_size[1] * (y+1) * (1/2) + self.viewport_start[1])
		self.image.point(view_x, view_y, self.color)

	def set_color(self, r, g, b):
		"""
		Changes current color
		"""
		self.color = self.image.color(int(255*r), int(255*g), int(255*b))
		return self.color

	def finish(self):
		"""
		Writes final BMP file
		"""
		self.image.write(self.filename)

	def line(self, xo, yo, xf, yf):
		"""
		Places a new line between two points
		"""
		x1 = int(self.viewport_size[0] * (xo+1) * (1/2) + self.viewport_start[0])
		y1 = int(self.viewport_size[1] * (yo+1) * (1/2) + self.viewport_start[1])
		x2 = int(self.viewport_size[0] * (xf+1) * (1/2) + self.viewport_start[0])
		y2 = int(self.viewport_size[1] * (yf+1) * (1/2) + self.viewport_start[1])
		
		dy = abs(y2 - y1)
		dx = abs(x2 - x1)
		steep = dy > dx
		if steep:
			x1, y1 = y1, x1
			x2, y2 = y2, x2
		if (x1 > x2):
			x1, x2 = x2, x1
			y1, y2 = y2, y1
		dy = abs(y2 - y1)
		dx = abs(x2 - x1)
		offset = 0
		threshold = dx
		y = y1
		for x in range(x1, x2 + 1):
			if steep:
				self.image.point(y, x, self.color)
			else:
				self.image.point(x, y, self.color)

			offset += dy * 2
			if offset >= threshold:
				y +=1 if y1 < y2 else -1
				threshold += 2 * dx
	
	def set_filename(self, filename):
		"""
		Sets final render filename
		"""
		self.filename = filename

	def load_obj(self, filename, translate=(0, 0, 0), scale=(1, 1, 1), rotate=(0, 0, 0), fill=True, textured=None, shader=None):
		"""
		Loads .obj file
		"""
		self.model_matrix(translate, scale, rotate)
		self.obj = OBJ(filename)
		self.obj.load()
		print("Rendering... " + filename)
		
		light = self.norm((0,0,1))
		faces = self.obj.faces
		vertices = self.obj.vertices
		materials = self.obj.materials
		textures = self.obj.textures
		normals = self.obj.normals
		mat_faces = self.obj.material_faces
		self.texture = Texture(textured)

		if materials:
			for mats in mat_faces:
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
							self.triangle(a, b, c, base_color=color, shader=shader, normals=(nA, nB, nC))
						else:
							normal = self.norm(self.cross(self.sub(b,a), self.sub(c,a)))
							intensity = self.dot(normal, light)

							if not self.texture.is_textured():
								if intensity < 0:
									continue
								self.triangle(a, b, c,color=self.set_color(color[0]*intensity, color[1]*intensity, color[2]*intensity))

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
						self.triangle(a, b, c, base_color=color, shader=shader, normals=(nA, nB, nC))
					else:

						normal = self.norm(self.cross(self.sub(b,a), self.sub(c,a)))
						intensity = self.dot(normal, light)

						if not self.texture.is_textured():
							if intensity < 0:
								continue
							self.triangle(a, b, c,color=self.set_color(intensity, intensity, intensity))
						else:
							if self.texture.is_textured():
								t1 = face[0][-1] - 1
								t2 = face[1][-1] - 1
								t3 = face[2][-1] - 1
								tA = textures[t1]
								tB = textures[t2]
								tC = textures[t3]
								self.triangle(a, b, c, texture=self.texture.is_textured(), texture_coords=(tA, tB, tC), intensity=intensity)
				else:
					f1 = face[0][0] - 1
					f2 = face[1][0] - 1
					f3 = face[2][0] - 1
					f4 = face[3][0] - 1

					vertex_list = [
						self.transform(vertices[f1]),
						self.transform(vertices[f2]),
						self.transform(vertices[f3]),
						self.transform(vertices[f4])
					]
					
					normal = self.norm(self.cross(self.sub(vertex_list[0], vertex_list[1]), self.sub(vertex_list[1], vertex_list[2]))) 
					intensity = self.dot(normal, light)
					
					A, B, C, D = vertex_list

					if not textured:
						if intensity < 0:
							continue
						self.triangle(A, B, C, color=self.set_color(intensity, intensity, intensity))
						self.triangle(A, C, D, color=self.set_color(intensity, intensity, intensity))
					else:
						if self.texture.is_textured():
							t1 = face[0][-1] - 1
							t2 = face[1][-1] - 1
							t3 = face[2][-1] - 1
							t4 = face[3][-1] - 1

							tA = textures[t1]
							tB = textures[t2]
							tC = textures[t3]
							tD = textures[t4]
							self.triangle(A, B, C, texture=self.texture.is_textured(), texture_coords=(tA, tB, tC), intensity=intensity)
							self.triangle(A, C, D, texture=self.texture.is_textured(), texture_coords=(tA, tC, tD), intensity=intensity)


	def triangle(self, A, B, C, color=None, texture=None, texture_coords=(), intensity=1, normals=None, shader=None, base_color=(1,1,1)):
		"""
		Draws a triangle with ABC vertices
		"""
		bbox_min, bbox_max = self.bbox(A, B, C)

		for x in range(bbox_min[0], bbox_max[0] + 1):
			for y in range(bbox_min[1], bbox_max[1] + 1):
				w, v, u = self.barycentric(A, B, C, x, y)
				if w < 0 or v < 0 or u < 0:
					continue
				if texture:
					tA, tB, tC = texture_coords
					tx = tA[0] * w + tB[0] * v + tC[0] * u
					ty = tA[1] * w + tB[1] * v + tC[1] * u
					color = self.texture.get_color(tx, ty, intensity)
				elif shader:
					color = shader(self, bary=(w,u,v), normals=normals, base_color=base_color)
				z = A[2] * w + B[2] * v + C[2] * u
				if x<0 or y<0:
					continue
				if z > self.image.get_zbuffer_value(x,y):
					self.image.point(x, y, color)
					self.image.set_zbuffer_value(x,y,z)


	def bbox(self, *vertex_list):
		"""
		Smallest possible bounding box
		"""
		xs = [vertices[0] for vertices in vertex_list]
		ys = [vertices[1] for vertices in vertex_list]
		xs.sort()
		ys.sort()
		return (xs[0], ys[0]), (xs[-1], ys[-1])

	def load(self, filename, translate=(0, 0, 0), scale=(1, 1, 1), fill=True, textured=None, rotate=(0, 0, 0)):
		"""
		Loads OBJ file, but as Wireframe
		"""
		print("Rendering (wireframe)...")

		self.model_matrix(translate, scale, rotate)
		self.obj = OBJ(filename)
		self.obj.load()

		vertices = self.obj.vertices
		faces = self.obj.faces
		normals = self.obj.normals
		materials = self.obj.materials
		textures = self.obj.textures
		light = (0,0,1)
		
		if materials and not textured:
			mat_index = self.obj.material_faces
			for mat in mat_index:
				diffuse_color = materials[mat[1]].diffuse_color
				for i in range(mat[0][0], mat[0][1]):
					coords = []
					texture_coords = []
					for face in faces[i]:
						coord = ((vertices[face[0]-1][0] + translate[0]) * scale[0], (vertices[face[0]-1][1] + translate[1]) * scale[1], (vertices[face[0]-1][2] + translate[2]) * scale[2])
						coords.append(coord)
					if fill:
						inner_intensity = self.dot(normals[face[1]-1], light)
						if inner_intensity < 0:
							continue
						self.fill_polygon(coords, color=(inner_intensity*diffuse_color[0],inner_intensity*diffuse_color[1],inner_intensity*diffuse_color[2]))
					else:
						self.draw_polygon(coords)

		elif textured and not materials:
			for face in faces:
				coords = []
				texture_coords = []
				for inner_vertex in face:
					coord = ((vertices[inner_vertex[0]-1][0] + translate[0]) * scale[0], (vertices[inner_vertex[0]-1][1] + translate[1]) * scale[1], (vertices[inner_vertex[0]-1][2] + translate[2]) * scale[2])
					coords.append(coord)
					if len(inner_vertex) > 2:
						text = ((textures[inner_vertex[2]-1][0]+ translate[0]) * scale[0], (textures[inner_vertex[2]-1][1]+ translate[1]) * scale[1])
						texture_coords.append(text)
				if fill:
					inner_intensity = self.dot(normals[inner_vertex[1]-1], light)
					if inner_intensity < 0:
						continue
					self.fill_polygon(coords, intensity=inner_intensity, texture=textured, texture_coords=texture_coords)
				else:
					self.draw_polygon(coords)
				coords = []
		else:
			for face in faces:
				coords = []
				texture_coords = []
				for inner_vertex in face:
					coord = vertices[inner_vertex[0]-1]
					coords.append(coord)
				if fill:
					inner_intensity = self.dot(normals[inner_vertex[1]-1], light)
					if inner_intensity < 0:
						continue
					self.fill_polygon(coords, color=(inner_intensity,inner_intensity,inner_intensity))
				else:
					self.draw_polygon(coords)
				coords = []

	def draw_polygon(self, vertex_list):
		"""
		Draws a simple polygon based on vertex_list
		"""
		for i in range(len(vertex_list)):
			if i == len(vertex_list)-1:
				start = vertex_list[i]
				final = vertex_list[0]
			else:
				start = vertex_list[i]
				final = vertex_list[i+1]
			self.line(start[0], start[1], final[0], final[1])

	def fill_polygon(self, vertex_list, color=None, texture=None, intensity=1, texture_coords = (), z_val=True):
		"""
		Draws and Fills a simple polygon based on vertex_list
		"""
		if not texture:
			color = self.color if color == None else self.image.color(int(255*color[0]), int(255*color[1]), int(255*color[2]))
		else:
			if self.texture == None:
				text = Texture(texture)
				self.texture = text
			else:
				text = self.texture
		start_x = (sorted(vertex_list, key=lambda tup: tup[0])[0][0])
		finish_x = (sorted(vertex_list, key=lambda tup: tup[0], reverse = True)[0][0])

		start_y = (sorted(vertex_list, key=lambda tup: tup[1])[0][1])
		finish_y = (sorted(vertex_list, key=lambda tup: tup[1], reverse=True)[0][1])
		
		start_x = int(self.viewport_size[0] * (start_x+1) * (1/2) + self.viewport_start[0])
		finish_x = int(self.viewport_size[0] * (finish_x+1) * (1/2) + self.viewport_start[0])

		start_y = int(self.viewport_size[0] * (start_y+1) * (1/2) + self.viewport_start[0])
		finish_y = int(self.viewport_size[0] * (finish_y+1) * (1/2) + self.viewport_start[0])
		for x in range(start_x, finish_x+1):
			for y in range(start_y, finish_y+1):
				is_inside = self.point_inside_polygon(self.normalize_x(x), self.normalize_y(y), vertex_list)
				if is_inside:
					if texture:
						A = (self.normalize_inv_x(vertex_list[0][0]), self.normalize_inv_x(vertex_list[0][1]))
						B = (self.normalize_inv_x(vertex_list[1][0]), self.normalize_inv_x(vertex_list[1][1]))
						C = (self.normalize_inv_x(vertex_list[2][0]), self.normalize_inv_x(vertex_list[2][1]))
						w,v,u = self.barycentric(A, B, C, x, y)
						A = texture_coords[0]
						B = texture_coords[1]
						C = texture_coords[2]
						tx = A[0] * w + B[0] * v +  C[0] * u
						ty = A[1] * w + B[1] * v + C[1] * u
						color = text.get_color(tx, ty, intensity=intensity)
					z = self.get_zplane_value(vertex_list, x, y)
					if z > self.image.get_zbuffer_value(x,y):
						self.image.point(x, y, color)
						self.image.set_zbuffer_value(x,y,z)

	def barycentric(self, A, B, C, x, y):
		"""
		Gets barycentric coords
		"""
		v1 = (C[0]-A[0], B[0]-A[0],A[0]-x)
		v2 = (C[1]-A[1], B[1]-A[1],A[1]-y)		
		bary = self.cross(v1, v2)	
		if abs(bary[2])<1:
			return -1,-1,-1

		return ( 1 - (bary[0] + bary[1]) / bary[2], bary[1] / bary[2], bary[0] / bary[2])
	
	def normalize_x(self, x):
		"""
		Normalizes x coord
		"""
		normalize_x = ((2*x)/self.viewport_size[0]) - self.viewport_start[0] - 1
		return normalize_x

	def normalize_y(self, y):
		"""
		Normalizes y coord
		"""
		normalize_y = ((2*y)/self.viewport_size[1]) - self.viewport_start[1] - 1
		return normalize_y

	def normalize_inv_x(self, x):
		"""
		Normalizes x inv coord
		"""
		normalize_x = int(self.viewport_size[0] * (x+1) * (1/2) + self.viewport_start[0])
		return normalize_x

	def normalize_inv_y(self, y):
		"""
		Normalizes y inv coord
		"""
		normalize_y = int(self.viewport_size[0] * (y+1) * (1/2) + self.viewport_start[0])
		return normalize_y

	def norm(self, v0):
		v = self.length(v0)
		if not v:
			return [0,0,0]
		return [v0[0]/v, v0[1]/v, v0[2]/v]

	def length(self, v0):
		return (v0[0]**2 + v0[1]**2 + v0[2]**2)**0.5

	def point_inside_polygon(self,x, y, vertex_list):
		"""
		Checks if (x, y) point is inside polygon 
		"""
		even_accumulator = 0
		point_1 = vertex_list[0]
		n = len(vertex_list)
		for i in range(n+1):
			point_2 = vertex_list[i % n]
			if(y > min(point_1[1], point_2[1])):
				if(y <= max(point_1[1], point_2[1])):
					if(point_1[1] != point_2[1]):
						xinters = (y-point_1[1])*(point_2[0]-point_1[0])/(point_2[1]-point_1[1])+point_1[0]
						if(point_1[0] == point_2[0] or x <= xinters):
							even_accumulator += 1
			point_1 = point_2
		if(even_accumulator % 2 == 0):
			return False
		else:
			return True
			
	def dot(self, v0, v1):
		"""
		Dot product
		"""
		return v0[0] * v1[0] + v0[1] * v1[1] + v0[2] * v1[2]

	def cross(self, v0, v1):
		"""
		Cross product
		"""
		return [v0[1] * v1[2] - v0[2] * v1[1], v0[2] * v1[0] - v0[0] * v1[2], v0[0] * v1[1] - v0[1] * v1[0]]

	def vector(self, p, q):
		"""
		Vector pq
		"""
		return [q[0]-p[0], q[1]-p[1], q[2]-p[2]]

	def sub(self, v0, v1):
		"""
		Vector subtraction
		"""
		return [v0[0] - v1[0], v0[1] - v1[1], v0[2] - v1[2]]

	def get_zplane_value(self, vertex_list, x,y):
		"""
		Gets z-coord in (x,y,z) found in the plane that passes through the first 3 points of vertex_list
		"""
		pq = self.vector(vertex_list[0], vertex_list[1])
		pr = self.vector(vertex_list[0], vertex_list[2])
		normal = self.cross(pq, pr)
		if normal[2]:
			z = ((normal[0]*(x-vertex_list[0][0])) + (normal[1]*(y-vertex_list[0][1])) - (normal[2]*vertex_list[0][2]))/(-normal[2])
			return z
		else:
			return -float("inf")

	def finish_zbuffer(self, filename = None):
		"""
		Renders the z buffer stored
		"""
		if filename == None:
			filename = self.filename.split(".")[0] + "zbuffer.bmp"
		self.image.write(filename, zbuffer = True)

	def model_matrix(self, translate=(0, 0, 0), scale=(1, 1, 1), rotate=(0, 0, 0)):
		"""
		Generates model matrix
		"""
		translation_matrix = Matrix([[1, 0, 0, translate[0]],[0, 1, 0, translate[1]],[0, 0, 1, translate[2]],[0, 0, 0, 1],])
		a = rotate[0]
		rotation_matrix_x = Matrix([[1, 0, 0, 0],[0, cos(a), -sin(a), 0],[0, sin(a),  cos(a), 0],[0, 0, 0, 1]])
		a = rotate[1]
		rotation_matrix_y = Matrix([[cos(a), 0,  sin(a), 0],[0, 1, 0, 0],[-sin(a), 0,  cos(a), 0],[ 0, 0, 0, 1]])
		a = rotate[2]
		rotation_matrix_z = Matrix([[cos(a), -sin(a), 0, 0],[sin(a),  cos(a), 0, 0],[0, 0, 1, 0],[0, 0, 0, 1]])
		rotation_matrix = rotation_matrix_x * rotation_matrix_y * rotation_matrix_z
		scale_matrix = Matrix([[scale[0], 0, 0, 0],[0, scale[1], 0, 0],[0, 0, scale[2], 0],[0, 0, 0, 1],])
		self.Model = translation_matrix * rotation_matrix * scale_matrix

	def view_matrix(self, x, y, z, center):
		"""
		Generates view matrix
		"""
		m = Matrix([[x[0], x[1], x[2],  0],[y[0], y[1], y[2], 0],[z[0], z[1], z[2], 0],[0,0,0,1]])
		o = Matrix([[1, 0, 0, -center[0]],[0, 1, 0, -center[1]],[0, 0, 1, -center[2]],[0, 0, 0, 1]])
		self.View = m * o

	def projection_matrix(self, coeff):
		"""
		Generates projection matrix
		"""
		self.Projection = Matrix([[1, 0, 0, 0],[0, 1, 0, 0],[0, 0, 1, 0],[0, 0, coeff, 1]])

	def viewport_matrix(self, x=0, y =0):
		"""
		Generates viewport matrix
		"""
		self.Viewport =  Matrix([[self.image.width/2, 0, 0, x + self.image.width/2],[0, self.image.height/2, 0, y + self.image.height/2],[0, 0, 128, 128],[0, 0, 0, 1]])

	def look_at(self, eye, center, up):
		"""
		Defines camera position
		"""
		z = self.norm(self.sub(eye, center))
		x = self.norm(self.cross(up, z))
		y = self.norm(self.cross(z,x))
		self.view_matrix(x, y, z, center)
		self.projection_matrix(-1/self.length(self.sub(eye, center)))
		self.viewport_matrix()

	def transform(self, vertices):
		agv = Matrix([[vertices[0]],[vertices[1]],[vertices[2]],[1]])
		transformed_vertex = self.Viewport * self.Projection * self.View * self.Model * agv
		transformed_vertex = transformed_vertex.to_list()
		trans = [round(transformed_vertex[0][0]/transformed_vertex[3][0]), round(transformed_vertex[1][0]/transformed_vertex[3][0]), round(transformed_vertex[2][0]/transformed_vertex[3][0])]
		return trans
