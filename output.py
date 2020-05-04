class StdOutOutput:

	def record(self, state):
		print("Game State: ")
		for k,v in state.items():
			print(k + ': ' + str(v))
		


class FileOutput:

	def __init__(self, path):
		self._path = path

	def record(self, state):
		with open(self._path, 'w') as f:
			f.writelines(["%s: %d\n" % (k,v) for k,v in state.items()])
