from render.material import Material, MTL


class OBJ(object):
    def __init__(self, filename):
        self.__vertices = []
        self.__faces = []
        self.__normals = []
        self.__filename = filename
        self.__materials = None
        self.__material_faces = []
        self.__texture_vertices = []

    def load(self):
        print("Loading OBJ file...")
        file = open(self.__filename, "r")
        import os

        faces = []
        current_material, prev_material = "default", "default"
        face_index = 0
        material_index = []
        lines = file.readlines()
        last = lines[-1]

        for line in lines:
            line = line.rstrip().split(" ")
            # mtl location file
            if line[0] == "mtllib":
                mtl_file = MTL(os.path.dirname(file.name) + "/" + line[1])
                if mtl_file.is_file_opened():
                    mtl_file.load()
                    self.__materials = mtl_file.materials
                else:
                    self.__faces = []
            # mtl object
            elif line[0] == "usemtl":
                if self.__materials:
                    material_index.append(face_index)
                    prev_material = current_material
                    current_material = line[1]
                    if len(material_index) == 2:
                        self.__material_faces.append((material_index, prev_material))
                        material_index = [material_index[1] + 1]
            # vertices
            elif line[0] == "v":
                line.pop(0)
                i = 1 if line[0] == "" else 0
                self.__vertices.append(
                    (float(line[i]), float(line[i + 1]), float(line[i + 2]))
                )
            # normals
            elif line[0] == "vn":
                line.pop(0)
                i = 1 if line[0] == "" else 0
                self.__normals.append(
                    (float(line[i]), float(line[i + 1]), float(line[i + 2]))
                )
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
                self.__faces.append(face)
                face_index += 1
                face = []
            # texture vertices
            elif line[0] == "vt":
                line.pop(0)
                self.__texture_vertices.append((float(line[0]), float(line[1])))

        if len(material_index) < 2 and self.__materials:
            material_index.append(face_index)
            self.__material_faces.append((material_index, current_material))
            material_index = [material_index[1] + 1]
        file.close()
        print("OBJ file loaded")

    def get_materials(self):
        return self.__materials

    def get_faces(self):
        return self.__faces

    def get_vertices(self):
        return self.__vertices

    def get_normals(self):
        return self.__normals

    def get_material_faces(self):
        return self.__material_faces

    def get_texture_vertices(self):
        return self.__texture_vertices
