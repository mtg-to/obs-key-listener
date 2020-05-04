import sys,os,argparse,logging
import keyboard
import output
import config

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
		self.state = {b.get_name(): b.get_start_at() for b in self.bindings}
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
	logging.info("Writing to file: %s", path)
	return output.FileOutput(path) 
	
def main():
	default_bindings_path = os.path.join(os.path.dirname(__file__), 'default_bindings.yml')

	parser = argparse.ArgumentParser(description="Use keyboard shortcuts to maintain the global state counters in Magic: the Gathering")
	parser.add_argument('-f', '--format', metavar='FMT', default='edh', help='selects the format of the game')
	parser.add_argument('-o', '--output', metavar='PATH', action='append', default=[output.StdOutOutput()], help='file to write the game state to (e.g. for OBS)', type=output_handler)
	parser.add_argument('-c', '--config', metavar='PATH', default=default_bindings_path, help='path to the yaml config file')
	args = parser.parse_args()

	try:
		cfg = config.parse_yaml(args.config)
		GameState(cfg[args.format], args.output).listen()
	except config.ConfigError as err:
		logging.error("Failed to load config, exitting.")

if __name__ == "__main__":
	main()
