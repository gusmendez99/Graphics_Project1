class Matrix(object):
	"""
	Helper class representing a Matrix
	"""
	def __init__(self, data):
		"""
		Data must be a multidimensional list
		"""
		self.data = data
		self.row = len(data)
		self.col = len(data[0])

	def __mul__(self, m2):
		"""
		Common linealg matrix multiplication
		"""
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

	def to_list(self):
		"""
		Returns multidimensional matrix as list
		"""
		return self.data