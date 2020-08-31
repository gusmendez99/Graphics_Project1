from render.gl import Render
image = Render()
image.create_window(1500, 1500)
image.look_at((-1,3,5), (0,0,0), (0,1,0))
image.viewport(0,0,1500,1500)
image.set_filename("./final.bmp")

image.load_obj("./models/astronaut.obj", translate=(0.80,-1,0), scale=(0.05,0.05,0.05), rotate=(-1,0.5,0), fill=True)

image.finish()
