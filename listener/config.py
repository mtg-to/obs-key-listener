import logging
import keyboard
import yaml

def yamlobj(tag):
    def wrapper(cls):
        def constructor(loader, node):
            fields = loader.construct_mapping(node)
            return cls(**fields)
        yaml.add_constructor(tag, constructor)
        return cls
    return wrapper

@yamlobj('!Full')
class Binding(yaml.YAMLObject):

	def __init__(self, name, bind_up, bind_down, bind_reset=None, start_at=0):
		self.name = name
		self.bind_up = bind_up
		self.bind_down = bind_down
		self.bind_reset = bind_reset
		self.start_at = start_at
	
	def get_name(self):
		return self.name
	
	def get_start_at(self):
		return self.start_at

	def register(self, gs):
		self._register(gs.adjust, self.bind_up, 1)
		self._register(gs.adjust, self.bind_down, -1)
		self._register(gs.set, self.bind_reset, self.start_at)

	def _register(self, func, hotkey, val):
		if hotkey is not None:
			print('Press (' + hotkey + ') to adjust "' + self.name + '" by ' + str(val))
			keyboard.add_hotkey(hotkey, func, args=(self.name, val))

@yamlobj('!Counter')
class DefaultBinding(Binding):

	default_mod = 'ctrl'

	def __init__(self, name, start_at=0):
		bind_up = " + ".join((self.default_mod, name[0], 'plus'))
		bind_down = " + ".join((self.default_mod, name[0], '-'))
		bind_reset = " + ".join((self.default_mod, name[0], '/'))
		super().__init__(name, bind_up, bind_down, bind_reset, start_at)

class ConfigError(Exception):
	pass


def parse_yaml(path):
	logging.info("Reading config from: %s", path)
	try:
		return yaml.full_load(open(path, 'r'))
	except yaml.YAMLError as ye:
		logging.error("Malformed config: %s", ye)
		raise ConfigError()
	except IOError as ioe:
		logging.error("Could not read config file: %s", ioe)
		raise ConfigError()

