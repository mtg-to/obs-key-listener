import keyboard
import sys
import argparse
import output

class Binding(object):
	
	def __init__(self, name, bind_up, bind_down, bind_reset=None, start_at=0):
		self._name = name
		self._bind_up = bind_up
		self._bind_down = bind_down
		self._bind_reset = bind_reset
		self._start_at = start_at
	
	def name(self):
		return self._name
	
	def start_at(self):
		return self._start_at

	def register(self, gs):
		self._register(gs.adjust, self._bind_up, 1)
		self._register(gs.adjust, self._bind_down, -1)
		self._register(gs.set, self._bind_reset, self._start_at)

	def _register(self, func, hotkey, val):
		if hotkey is not None:
			print('Press (' + hotkey + ') to adjust "' + self._name + '" by ' + str(val))
			keyboard.add_hotkey(hotkey, func, args=(self._name, val))

class DefaultBinding(Binding):

	default_mod = "ctrl"

	def __init__(self, name, start_at=0):
		bind_up = " + ".join((self.default_mod, name[0], 'plus'))
		bind_down = " + ".join((self.default_mod, name[0], '-'))
		bind_reset = " + ".join((self.default_mod, name[0], '/'))
		super().__init__(name, bind_up, bind_down, bind_reset, start_at)



class GameState(object):
	
	def __init__(self, bindings, outputs):
		self.bindings = bindings
		self._outputs = outputs
		self.reset()

	def listen(self):
		keyboard.add_hotkey('ctrl + r', self.reset)
		[ b.register(self) for b in self.bindings ]
		keyboard.wait('ctrl + q')

	def reset(self):
		self.state = {b.name(): b.start_at() for b in self.bindings}
		self.record()

	def adjust(self, k, v):
		old = self.state.get(k)
		if old is not None:
			self.state[k] = old + v
			self.record()

	def set(self, k, v):
		self.state[k] = v
		self.record()

	def record(self):
		[o.record(self.state) for o in self._outputs]

def output_handler(path):
	print("Writing to file: " + path)
	return output.FileOutput(path) 

	
templates = {
	'edh': [
		Binding('life', '+', '-', None, 40),
		Binding('cast', '*', None),
		DefaultBinding('w'),
		DefaultBinding('u'),
		DefaultBinding('b'),
		DefaultBinding('r'),
		DefaultBinding('g'),
		DefaultBinding('0'),
		DefaultBinding('s')
	],
	'constructed': [
		Binding('life', '+', '-', None, 20),
		DefaultBinding('w'),
		DefaultBinding('u'),
		DefaultBinding('b'),
		DefaultBinding('r'),
		DefaultBinding('g'),
		DefaultBinding('0'),
		DefaultBinding('s')
	]
}

def main():
	parser = argparse.ArgumentParser(description="Use keyboard shortcuts to maintain the global state counters in Magic: the Gathering")
	parser.add_argument('-f', '--format', metavar='FMT', default='edh', choices=tuple(templates.keys()), help='selects the format of the game')
	parser.add_argument('-o', '--output', metavar='PATH', action='append', help='file to write the game state to (e.g. for OBS)', type=output_handler)
	args = parser.parse_args()

	outputs=[output.StdOutOutput()]
	outputs.extend(args.output)

	GameState(templates[args.format], outputs).listen()

if __name__ == "__main__":
	main()
