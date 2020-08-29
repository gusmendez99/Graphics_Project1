"""
    Universidad del Valle de Guatemala
    Gustavo Mendez - 18500

    main.py - simple main file to create bmp files (render)
"""

from gl import Render
from obj import Texture
from utils.math import V3
from shaders import gourad

r = Render(1920, 1080)
#background = Texture('./models/farm.bmp')
#r.load_background(background)

man_texture = Texture("./models/model.bmp")
light = V3(0,1,1)
#r.active_shader = gourad
r.load("./models/model.obj", man_texture, (0.5, 0.2, 0.5), (0.4, 0.6, 1), (0,0,0), (0,1,5), (0,1,0),(0,0,0), light)


r.finish('scene.bmp')