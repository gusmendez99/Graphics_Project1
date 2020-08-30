"""
    Universidad del Valle de Guatemala
    Gustavo Mendez - 18500

    obj.py - parse a .obj file to simple array values
"""


class Obj(object):
    def __init__(self, filename):
        self.vertices = []
        self.tvertices = []
        self.normals = []
        self.faces = []
        self.matf = {}

        with open(filename) as f:
            self.lines = f.read().splitlines()
        self.read()

    def read(self):
        key = ""
        for idx,line in enumerate(self.lines):
            #print(idx)
            if line:
                prefix, value = line.split(" ", 1)

                if prefix == "usemtl":
                    key = value
                    self.matf[key] = []
                if prefix == "v":
                    self.vertices.append(list(map(float, value.split(" "))))
                if prefix == "vn":
                    self.normals.append(list(map(float, value.split(" "))))
                elif prefix == "vt":
                    self.tvertices.append(list(map(float, value.split(" "))))
                elif prefix == "f":
                    self.faces.append(
                        [list(map(int, filter(lambda word: word and word != " ", face.split("/")))) for face in value.split(" ")]
                    )
                    if key != "":
                        self.matf[key].append([list(map(int, filter(lambda word: word and word != " ", face.split("/")))) for face in value.split(' ')])
