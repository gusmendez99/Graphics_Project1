class MTL(object):
    def __init__(self, filename):
        self.__filename = filename
        self.__file = None
        self.materials = {}
        self.read_mtl()

    def read_mtl(self):
        try:
            self.__file = open(self.__filename, "r")
            self.__mtl_file = True
        except:
            self.__mtl_file = False

    def is_file_opened(self):
        return self.__mtl_file

    def load(self):
        print("Loading MTL file...")

        if self.is_file_opened():
            current_material = None
            ac, dc, sc, ec, t, s, i, o = 0, 0, 0, 0, 0, 0, 0, 0
            for line in self.__file.readlines():
                line = line.strip().split(" ")
                if line[0] == "newmtl":
                    current_material = line[1].rstrip()
                elif line[0] == "Ka":
                    ac = (float(line[1]), float(line[2]), float(line[3]))
                elif line[0] == "Kd":
                    dc = (float(line[1]), float(line[2]), float(line[3]))
                elif line[0] == "Ks":
                    sc = (float(line[1]), float(line[2]), float(line[3]))
                elif line[0] == "Ke":
                    ec = (float(line[1]), float(line[2]), float(line[3]))
                elif line[0] == "d" or line[0] == "Tr":
                    t = (float(line[1]), line[0])
                elif line[0] == "Ns":
                    s = float(line[1])
                elif line[0] == "illum":
                    i = int(line[1])
                elif line[0] == "Ni":
                    o = float(line[1])
                elif current_material:
                    self.materials[current_material] = Material(
                        current_material, ac, dc, sc, ec, t, s, i, o
                    )
            if current_material not in self.materials.keys():
                self.materials[current_material] = Material(
                    current_material, ac, dc, sc, ec, t, s, i, o
                )


class Material(object):
    def __init__(self, name, ac, dc, sc, ec, t, s, i, o):
        """
		Material stores:
			- ambient color
			- difduse color
			- emissive coeficient
			- transparency
			- shininess
			- illumination
			- optical density
		"""
        self.name = name.rstrip()
        self.ambient_color = ac
        self.diffuse_color = dc
        self.specular_color = sc
        self.emissive_coeficient = ec
        self.transparency = t
        self.shininess = s
        self.illumination = i
        self.optical_density = o
