class Material(object):
    def __init__(self, filename):

        self.rgb_dict = {}  # diccionario con valores rgb de los materiales
        with open(filename) as f:
            self.lines = f.read().splitlines()
        self.read()

    # se realiza la lectura del archivo obj
    def read(self):
        key = ""
        for line in self.lines:
            if line:
                prefix, value = line.split(" ", 1)
                if prefix == "newmtl":
                    key = value
                if prefix == "Kd":
                    kd_list = list(map(float, value.split(" ")))
                    self.rgb_dict[key] = (kd_list[0], kd_list[1], kd_list[2])
