import random

def star(render, light=(0, 0, 1), bary=(1, 1, 1), normals=0, base_color=(1, 1, 1)):

	"""
	Shader to look like the sun
	"""
	base_color = (1, 0.8431, 0)
	w, v, u = bary
	nA, nB, nC = normals
	light = (random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1))

	iA = render.dot(nA, light)
	iB = render.dot(nB, nA)
	iC = render.dot(nC, nB)

	intensity = w * iA + v * iB + u * iC

	if intensity <= 0:
		intensity = 0.85
	elif intensity < 0.25:
		intensity = 0.75
	elif intensity < 0.75:
		intensity = 0.55
	elif intensity < 1:
		base_color = (1, 1, 0)
		intensity = 0.80

	r = intensity * base_color[0]
	g = intensity * base_color[1]
	b = intensity * base_color[2]

	return render.set_color(r, g, b)


def moon(render, light=(0, 0, 1), bary=(1, 1, 1), normals=0, base_color=(1, 1, 1)):
	"""
	Shader to smooth the surfaces and give a look like the moon
	"""
	w, v, u = bary
	# normals
	nA, nB, nC = normals
	light = (0, 1, -2)
	# light intensity
	iA, iB, iC = [render.dot(n, light) for n in (nA, nB, nC)]
	intensity = w * iA + v * iB + u * iC
	return render.set_color(
		base_color[2] * intensity, base_color[1] * intensity, base_color[0] * intensity
	)
