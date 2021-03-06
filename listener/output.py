class StdOutOutput:

	def record(self, state):
		print("Game State: ")
		[print(s.serialize()) for s in state]
		
class TextCallbackOutput:
	
	def __init__(self, callback):
		self._callback = callback
		
	def record(self, state):
		self._callback("\n".join([s.serialize() for s in state]))
		
class FileOutput:

	def __init__(self, path):
		self._path = path

	def record(self, state):
		with open(self._path, 'w') as f:
			f.writelines(['%s\n' % s.serialize() for s in state])
