"""
    Universidad del Valle de Guatemala
    Gustavo Mendez - 18500
    math.py - @denn1s math functions
"""
from collections import namedtuple

V2 = namedtuple("Vertex2", ["x", "y"])
V3 = namedtuple("Vertex3", ["x", "y", "z"])

def sum(v0, v1):
    """
        Input: 2 size 3 vectors
        Output: Size 3 vector with the per element sum
    """
    return V3(v0.x + v1.x, v0.y + v1.y, v0.z + v1.z)


def sub(v0, v1):
    """
        Input: 2 size 3 vectors
        Output: Size 3 vector with the per element substraction
    """
    return V3(v0.x - v1.x, v0.y - v1.y, v0.z - v1.z)


def mul(v0, k):
    """
        Input: 2 size 3 vectors
        Output: Size 3 vector with the per element multiplication
    """
    return V3(v0.x * k, v0.y * k, v0.z * k)


def dot(v0, v1):
    """
        Input: 2 size 3 vectors
        Output: Scalar with the dot product
    """
    return v0.x * v1.x + v0.y * v1.y + v0.z * v1.z


def length(v0):
    """
        Input: 1 size 3 vector
        Output: Scalar with the length of the vector
    """
    return (v0.x ** 2 + v0.y ** 2 + v0.z ** 2) ** 0.5


def norm(v0):
    """
        Input: 1 size 3 vector
        Output: Size 3 vector with the normal of the vector
    """
    v0length = length(v0)

    if not v0length:
        return V3(0, 0, 0)

    return V3(v0.x / v0length, v0.y / v0length, v0.z / v0length)


def bbox(*vertices):
    xs = [vertex.x for vertex in vertices]
    ys = [vertex.y for vertex in vertices]

    xs.sort()
    ys.sort()

    xmin = int(xs[0])    
    xmax = int(xs[-1])
    ymin = int(ys[0])    
    ymax = int(ys[-1])

    return V2(xmin, ymin), V2(xmax, ymax)


def cross(v1, v2):
    return V3(
        v1.y * v2.z - v1.z * v2.y, v1.z * v2.x - v1.x * v2.z, v1.x * v2.y - v1.y * v2.x,
    )


def barycentric(A, B, C, P):
    cx, cy, cz = cross(
        V3(B.x - A.x, C.x - A.x, A.x - P.x), V3(B.y - A.y, C.y - A.y, A.y - P.y),
    )

    if abs(cz) < 1:
        return -1, -1, -1

    u = cx / cz
    v = cy / cz
    w = 1 - (cx + cy) / cz

    return w, v, u


# Transformations 

def matrix_mul(A, B):
    # If A-matrix just have one row
    rows_matrix_a = len(A)
    try: 
        columns_matrix_a = len(A[0])
    except(TypeError):
        columns_matrix_a = 1
    
    #If B-matrix just have one row
    try: 
        columns_matrix_b = len(B[0])
    except(TypeError):
        columns_matrix_b = 1

    # Final matrix
    
    C = []
    try: 
        for i in range(rows_matrix_a):
            C.append([0] * columns_matrix_b)

        # A * B, stores result on C matrix  
        for i in range(rows_matrix_a):
            for j in range(columns_matrix_b):
                for k in range(columns_matrix_a):
                    C[i][j] += A[i][k] * B[k][j]
    
    except(RuntimeError, TypeError, NameError) as error:
        print(error)
    return C

