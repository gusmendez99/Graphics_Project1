from utils.math import V3, dot
from utils.color import color

def gourad(render, x, y, **kwargs):
    w,v,u = kwargs["bary_coords"]
    nA, nB, nC = kwargs["normals"]
    light = kwargs["light"]
    tx, ty = kwargs["texture_coords"]
    
    normal_x = nA.x*w + nB.x*v + nC.x*u 
    normal_y = nA.y*w + nB.y*v + nC.y*u 
    normal_z = nA.z*w + nB.z*v + nC.z*u 
    normal = V3(normal_x, normal_y, normal_z)
    intensity = dot(normal, light)

    if intensity < 0:
        intensity = 0
    if intensity > 1:
        intensity = 1    
    elif intensity < 0.3:
        intensity = 0
    elif intensity > 0.3:
        intensity = 0.3
    elif intensity > 0.6:
        intensity = 0.6
    elif intensity > 0.8:
        intensity = 0.8
    elif intensity > 0.9:
        intensity = 0.9
    else:
        intensity = 1.0

    tcolor = render.active_texture.get_simple_color(tx,ty)
    return color(
        round(tcolor[2] * intensity),
        round(tcolor[1] * intensity),
        round(tcolor[0] * intensity)
    )