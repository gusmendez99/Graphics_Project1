####################################
#
#   FINAL PROJECT - CUSTOM SCENE
#
####################################
import random
from render.gl import Render
from render.shaders import bright_shader, smooth_shader, phong, inverse, gradual_toon

render = Render()
render.create_window(1600, 1600)
render.look_at((-1, 3, 5), (0, 0, 0), (0, 1, 0))
render.create_window(1600, 1600)
render.set_filename("./final.bmp")

render.set_background('./textures/background.bmp')

# Stars - skipped with current background
""" for i in range(random.randint(100, 1500)):
    x = random.uniform(-1, 1)
    y = random.uniform(-1, 1)
    render.flood_vertex(x, y)
 """
# Asteroids
for i in range(random.randint(1, 6)):
    x = random.uniform(-0.7, 0.7)
    y = random.uniform(-0.7, 0.7)
    render.load_obj(
        "./models/asteroid.obj",
        translate=(round(x, 1), round(y, 1), -0.30),
        scale=(0.1, 0.1, 0.1),
        rotate=(0.35, 0.28, -0.1),
        fill=True,
        shader=gradual_toon
    )


# Loading moon
render.load_obj(
    "./models/planet.obj",
    translate=(-0.65, -1, -0.2),
    scale=(0.70, 0.70, 0.70),
    rotate=(0, 0, 0.5),
    fill=True,
    shader=smooth_shader,
) 


# Loading space ship
render.load_obj(
    "./models/space_ship.obj",
    translate=(-0.30, -0.75, -0.15),
    scale=(0.16, 0.16, 0.16),
    rotate=(0.25, 0.8, -0.45),
    fill=True,
    shader=phong,
)

# Loading astronaut
render.load_obj(
    "./models/astronaut.obj",
    translate=(-0.65, -1, -0.45),
    scale=(0.05, 0.05, 0.05),
    rotate=(-1, -0.75, 0.15),
    fill=True,
    shader=inverse,
)

# Loading space station
render.load_obj(
    "./models/space_station.obj",
    translate=(0.25, -0.75, 0.3),
    scale=(0.08, 0.08, 0.08),
    rotate=(-0.50, -0.80, 0.2),
    fill=True,
    shader=gradual_toon,
)

# Loading sun
render.load_obj(
    "./models/planet.obj",
    translate=(0.75, 1, 0),
    scale=(0.20, 0.20, 0.20),
    shader=bright_shader,
)

render.finish()
