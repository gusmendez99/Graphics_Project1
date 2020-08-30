from material import MTL

class OBJ(object):
	"""
	OBJ class
	"""

	def __init__(self, filename):
		"""
		Initializes values
		"""
		self.vertices = []
		self.faces = []
		self.normals = []
		self.filename = filename
		self.materials = None
		self.material_faces = []
		self.textures = []

	def load(self):
		"""
		Loads obj file
		"""
		print("Loading obj file...")
		import os
		
		file = open(self.filename, "r")
		faces = []
		current_material, previous_material = "default", "default"
		face_index = 0
		material_index = []

		lines = file.readlines()
		last = lines[-1]

		for line in lines:
			line = line.rstrip().split(" ")
			# materials
			if line[0] == "mtllib":
				mtl_file = MTL(os.path.dirname(file.name) + "/" + line[1])
				if mtl_file.is_file_opened():
					mtl_file.load()
					#self.faces = {}
					self.materials = mtl_file.materials
				else:
					self.faces = []
			elif line[0] == "usemtl":
				if self.materials:
					material_index.append(face_index)
					previous_material = current_material
					current_material = line[1]
					if len(material_index) == 2:
						self.material_faces.append((material_index, previous_material))
						material_index= [material_index[1]+1]
			# vertices
			elif line[0] == "v":
				line.pop(0)
				i = 1 if line[0] == "" else 0
				self.vertices.append((float(line[i]), float(line[i+1]), float(line[i+2])))
			# normals
			elif line[0] == "vn":
				line.pop(0)
				i = 1 if line[0] == "" else 0
				self.normals.append((float(line[i]), float(line[i+1]), float(line[i+2])))
			# faces
			elif line[0] == "f":
				line.pop(0)
				face = []
				for i in line:
					i = i.split("/")
					if i[1] == "":
						face.append((int(i[0]), int(i[-1])))
					else:
						face.append((int(i[0]), int(i[-1]), int(i[1])))
				self.faces.append(face)
				face_index += 1
				face = []
				
			# texture vertices
			elif line[0] == "vt":
				line.pop(0)
				self.textures.append((float(line[0]), float(line[1])))
		if len(material_index) < 2 and self.materials:
			material_index.append(face_index)
			self.material_faces.append((material_index, current_material))
			material_index= [material_index[1]+1]
		file.close()
		print("OBJ file loaded successfully")
