def bbox(*vertex_list):
    """
	Smallest possible bounding box
	"""
    xs = [vertices[0] for vertices in vertex_list]
    ys = [vertices[1] for vertices in vertex_list]
    xs.sort()
    ys.sort()
    return (xs[0], ys[0]), (xs[-1], ys[-1])


def barycentric(A, B, C, x, y):
    """
	Gets barycentric coords
	"""
    v1 = (C[0] - A[0], B[0] - A[0], A[0] - x)
    v2 = (C[1] - A[1], B[1] - A[1], A[1] - y)
    bary = cross(v1, v2)
    if abs(bary[2]) < 1:
        return -1, -1, -1

    return (1 - (bary[0] + bary[1]) / bary[2], bary[1] / bary[2], bary[0] / bary[2])


def norm(v0):
    v = length(v0)
    if not v:
        return [0, 0, 0]
    return [v0[0] / v, v0[1] / v, v0[2] / v]


def length(v0):
    return (v0[0] ** 2 + v0[1] ** 2 + v0[2] ** 2) ** 0.5


def point_inside_polygon(x, y, vertex_list):
    """
	Checks if (x, y) point is inside polygon 
	"""
    even_accumulator = 0
    point_1 = vertex_list[0]
    n = len(vertex_list)
    for i in range(n + 1):
        point_2 = vertex_list[i % n]
        if y > min(point_1[1], point_2[1]):
            if y <= max(point_1[1], point_2[1]):
                if point_1[1] != point_2[1]:
                    xinters = (y - point_1[1]) * (point_2[0] - point_1[0]) / (
                        point_2[1] - point_1[1]
                    ) + point_1[0]
                    if point_1[0] == point_2[0] or x <= xinters:
                        even_accumulator += 1
        point_1 = point_2
    if even_accumulator % 2 == 0:
        return False
    else:
        return True


def dot(v0, v1):
    """
	Dot product
	"""
    return v0[0] * v1[0] + v0[1] * v1[1] + v0[2] * v1[2]


def cross(v0, v1):
    """
	Cross product
	"""
    return [
        v0[1] * v1[2] - v0[2] * v1[1],
        v0[2] * v1[0] - v0[0] * v1[2],
        v0[0] * v1[1] - v0[1] * v1[0],
    ]


def vector(p, q):
    """
	Vector pq
	"""
    return [q[0] - p[0], q[1] - p[1], q[2] - p[2]]


def sub(v0, v1):
    """
	Vector subtraction
	"""
    return [v0[0] - v1[0], v0[1] - v1[1], v0[2] - v1[2]]


def get_zplane_value(vertex_list, x, y):
    """
	Gets z-coord in (x,y,z) found in the plane that passes through the first 3 points of vertex_list
	"""
    pq = vector(vertex_list[0], vertex_list[1])
    pr = vector(vertex_list[0], vertex_list[2])
    normal = cross(pq, pr)
    if normal[2]:
        z = (
            (normal[0] * (x - vertex_list[0][0]))
            + (normal[1] * (y - vertex_list[0][1]))
            - (normal[2] * vertex_list[0][2])
        ) / (-normal[2])
        return z
    else:
        return -float("inf")


class Matrix(object):
    def __init__(self, data):
        self.data = data
        self.row = len(data)
        self.col = len(data[0])

    def __mul__(self, m2):
        result = []
        for i in range(self.row):
            result.append([])
            for j in range(m2.col):
                result[-1].append(0)

        for i in range(self.row):
            for j in range(m2.col):
                for k in range(m2.row):
                    result[i][j] += self.data[i][k] * m2.data[k][j]

        return Matrix(result)

    def tolist(self):
        return self.data
