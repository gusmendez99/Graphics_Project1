"""
    Universidad del Valle de Guatemala
    Gustavo Mendez - 18500

    main.py - simple main file to create bmp files (render)
"""
from utils.math import V3

from gl import Render
from texture import Texture
from material import Material
from shaders import gourad

r = Render(1920, 1080)
# background = Texture('./models/farm.bmp')
# r.load_background(background)

""" man_texture = Texture("./textures/man.bmp")
# man_material = Material('./materials/pokedex.mtl')
light = V3(0, 1, 1)
r.active_texture = man_texture
# r.active_material = man_material
# r.active_shader = gourad
r.look_at(eye=(0, 1, 5), up=(0, 1, 0), center=(0, 0, 0))
r.load(
    "./models/man.obj", (0.5, 0.2, 0.5), (0.4, 0.6, 1), (0, 0, 0), light,
) """

#space_humster_material = Material('./models/delorean.mtl')
space_humster_texture = Texture("./textures/man.bmp")
light = V3(0, 1, 1)
r.active_texture = space_humster_texture
#r.active_material = space_humster_material
# r.active_shader = gourad
r.look_at(eye=(0, 1, 5), up=(0, 1, 0), center=(0, 0, 0))
r.load(
    "./models/man.obj", (0.5, 0.2, 0.5), (0.02, 0.02, 0.02 ), (0, 0, 0), light,
)

r.finish("scene.bmp")
