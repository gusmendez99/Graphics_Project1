from gl import Render
from shaders import moon, star

# Initializing render
r = Render()
r.create_window(1500, 1500)
r.look_at(eye=(-1, 3, 5), up=(0, 0, 0), center=(0, 1, 0))
r.viewport(0, 0, 1500, 1500)
r.set_filename("./scene.bmp")

# Loading spaceship
""" r.loadOBJ(
	"./models/space_ship.obj",
	translate=(0.25, -0.75, 0.3),
	scale=(0.08, 0.08, 0.08),
	rotate=(0.25, 0.8, -0.25),
	fill=True,
) """
# Loading astronaut
r.load_obj(
	"./models/astronaut.obj",
	translate=(0.80,-1,0), scale=(0.05,0.05,0.05), rotate=(-1,0.5,0), fill=True
)

r.finish()
