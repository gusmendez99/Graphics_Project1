import random
from render.math import dot


def phong(render, light=(0, 0, 1), bary=(1, 1, 1), normals=0, base_color=(1, 1, 1)):

    # barycentric
    w, v, u = bary
    # normals
    nA, nB, nC = normals
    b, g, r = base_color

    iA, iB, iC = [dot(n, light) for n in (nA, nB, nC)]
    intensity = w * iA + v * iB + u * iC

    b *= intensity
    g *= intensity
    r *= intensity

    if intensity > 0:
        return render.set_color(r, g, b)
    else:
        return render.set_color(0, 0, 0)

def inverse(render, light=(0, 0, 1), bary=(1, 1, 1), normals=0, base_color=(1, 1, 1)):

    # barycentric
    w, v, u = bary
    # normals
    nA, nB, nC = normals
    b, g, r = base_color

    iA, iB, iC = [dot(n, light) for n in (nA, nB, nC)]
    intensity = w * iA + v * iB + u * iC

    b *= (1 - intensity)
    g *= (1 - intensity)
    r *= (1 - intensity)

    if intensity > 0:
        return render.set_color(r, g, b)
    else:
        return render.set_color(0, 0, 0)


def bright_shader(render, light=(0, 0, 1), bary=(1, 1, 1), normals=0, base_color=(1, 1, 1)):
    """
	Shader to make brighter
	"""
    base_color = (1, 0.85, 0)
    w, v, u = bary
    nA, nB, nC = normals
    light = (random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1))

    iA = dot(nA, light)
    iB = dot(nB, nA)
    iC = dot(nC, nB)

    b, g, r = base_color
    intensity = w * iA + v * iB + u * iC

    if intensity <= 0:
        intensity = 0.85
    elif intensity < 0.25:
        intensity = 0.75
    elif intensity < 0.75:
        intensity = 0.55
    elif intensity < 1:
        r, g, b = 1, 1, 0
        intensity = 0.80

    b *= intensity
    g *= intensity
    r *= intensity

    return render.set_color(r, g, b)


def smooth_shader(render, light=(0, 0, 1), bary=(1, 1, 1), normals=0, base_color=(1, 1, 1)):
    """
	Shader to smooth surfaces
	"""
    # barycentric
    w, v, u = bary
    # normals
    nA, nB, nC = normals
    # light intensity
    light = (1, 0, 1)

    b, g, r = base_color
    iA, iB, iC = [dot(n, light) for n in (nA, nB, nC)]
    intensity = w * iA + v * iB + u * iC

    b *= intensity
    g *= intensity
    r *= intensity

    return render.set_color(r, g, b)

def gradual_toon(render, light=(0, 0, 1), bary=(1, 1, 1), normals=0, base_color=(1, 1, 1)):

    u, v, w = bary
    nA, nB, nC = normals
    b, g, r = base_color

    iA, iB, iC = [dot(n, light) for n in (nA, nB, nC)]
    intensity = w * iA + v * iB + u * iC

    b *= intensity
    g *= intensity
    r *= intensity

    if intensity > 0:
        return render.set_color(round(r,1), round(g,1), round(b,1))
    else:
        return render.set_color(0, 0, 0)
