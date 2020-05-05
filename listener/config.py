import logging
import keyboard
import yaml

class StateFactory(object):

	def get_bindings(self):
		raise NotImplementedError()

class State(object):
	
	def serialize(self):
		raise NotImplementedError()

	def reset(self):
		raise NotImplementedError()

class _Counter(State):

	def __init__(self, name, zero = 0):
		self._name = name
		self._zero = zero
		self._value = zero
		
	def inc(self):
		self._value += 1

	def dec(self):
		self._value -= 1

	def reset(self):
		self._value = self._zero

	def serialize(self):
		return '%s: %d' % (self._name, self._value)

def yamlobj(tag):
    def wrapper(cls):
        def constructor(loader, node):
            fields = loader.construct_mapping(node)
            return cls(**fields)
        yaml.add_constructor(tag, constructor)
        return cls
    return wrapper

@yamlobj('!Full')
class _CounterBinding(yaml.YAMLObject, StateFactory):

	def __init__(self, name, bind_up, bind_down, bind_reset=None, start_at=0):
		self.name = name
		self.bind_up = bind_up
		self.bind_down = bind_down
		self.bind_reset = bind_reset
		self.start_at = start_at

	def get_bindings(self):
		counter = _Counter(self.name, self.start_at)
		bindings = []
		if self.bind_up: bindings.append((self.bind_up, counter.inc, 'Increment %s' % self.name))
		if self.bind_down: bindings.append((self.bind_down, counter.dec, 'Decrement %s' % self.name))
		if self.bind_reset: bindings.append((self.bind_reset, counter.reset, 'Reset %s' % self.name))
		return (counter, bindings)
				

@yamlobj('!Counter')
class _DefaultCounterBinding(_CounterBinding):

	def __init__(self, name, start_at=0):
		bind_up = ' + '.join((name[0], 'plus'))
		bind_down = ' + '.join((name[0], '-'))
		bind_reset = ' + '.join((name[0], '/'))
		super().__init__(name, bind_up, bind_down, bind_reset, start_at)

class ConfigError(Exception):
	pass


def parse_yaml(path):
	logging.info('Reading config from: %s', path)
	try:
		return yaml.full_load(open(path, 'r'))
	except yaml.YAMLError as ye:
		logging.error('Malformed config: %s', ye)
		raise ConfigError()
	except IOError as ioe:
		logging.error('Could not read config file: %s', ioe)
		raise ConfigError()

