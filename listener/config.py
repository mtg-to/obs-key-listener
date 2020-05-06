import logging, functools
import keyboard
import yaml

class _BindingsBuilder(object):

	def __init__(self):
		self._bindings = []	

	def add(self, key, func, help_text):
		if key: self._bindings.append((key, func, help_text))
		return self

	def build(self):
		return self._bindings

class StateFactory(object):

	def __init__(self, state, bindings):
		self._state = state
		self._bindings = bindings

	def get_bindings(self):
		return (self._state, self._bindings)

class State(object):

	def serialize(self):
		raise NotImplementedError()

	def reset(self):
		raise NotImplementedError()

class _Caption(State):

	def __init__(self, name):
		self._name = name

	def serialize(self):
		return self._name

	def reset(self):
		pass

class _Bar(State):

	def __init__(self, name, total, empty='[ ]'):
		self._name = name
		self._total = total
		self._empty = empty
		self._groups = []

	def add_group(self, starting, marker='[0]'):
		self._groups.append((marker, starting, starting))

	def serialize(self):
		full = functools.reduce(lambda v,t: v + t, [ g[0] * g[1] for g in self._groups ])
		empty = self._empty * (self._total - self._current())
		return '%s\n  %s%s' % (self._name, full, empty)

	def _current(self):
		return functools.reduce(lambda v,t: v + t[1], self._groups, 0)

	def gain(self, lvl):
		old = self._groups[lvl]
		if self._current() < self._total: self._groups[lvl] = (old[0], old[1] + 1, old[2])
 

	def use(self, lvl):
		old = self._groups[lvl]
		if self._current() > 0: self._groups[lvl] = (old[0], old[1] - 1, old[2])

	def reset(self):
		self._groups = [(g[0],g[2],g[2]) for g in self._groups]

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
            fields = loader.construct_mapping(node, deep=True)
            return cls(**fields)
        yaml.add_constructor(tag, constructor)
        return cls
    return wrapper

@yamlobj('!Caption')
class _CaptionBinding(yaml.YAMLObject, StateFactory):

	def __init__(self, name):
		self._name = name

	def get_bindings(self):
		return (_Caption(self._name), [])


@yamlobj('!Bar')
class _BarBinding(yaml.YAMLObject, StateFactory):

	def __init__(self, name, total, starting, bind_gain, bind_use, bind_reset=None, full='[0]', empty='[ ]'):
		bar = _Bar(name, total, empty)
		bar.add_group(starting, full)
		bindings = _BindingsBuilder()\
			.add(bind_gain, lambda: bar.gain(0), 'Gain ' + name)\
			.add(bind_use, lambda: bar.use(0), 'Use ' + name)\
			.add(bind_reset, bar.reset, 'Reset ' + name)\
			.build()
		super().__init__(bar, bindings)

@yamlobj('!MultiBar')
class _MultiBarBinding(yaml.YAMLObject, StateFactory):
	
	def __init__(self, name, total, groups, bind_reset=None, empty='[ ]'):
		bar = _Bar(name, total, empty)
		builder = _BindingsBuilder()\
			.add(bind_reset, bar.reset, 'Reset ' + name)

		for idx, g in enumerate(groups):
			mark = g.get('full', '[0]')
			bar.add_group(g.get('starting', 0), mark)
			builder.add(g.get('bind_gain'), lambda lvl=idx: bar.gain(lvl), 'Gain ' + mark + ' in ' + name)
			builder.add(g.get('bind_use'), lambda lvl=idx: bar.use(lvl), 'Use ' + mark + ' in ' + name)
			
		super().__init__(bar, builder.build())


@yamlobj('!Full')
class _CounterBinding(yaml.YAMLObject, StateFactory):

	def __init__(self, name, bind_up, bind_down, bind_reset=None, start_at=0):
		self.name = name
		counter = _Counter(name, start_at)
		bindings = _BindingsBuilder()\
			.add(bind_up, counter.inc, 'Increment %s' % name)\
			.add(bind_down, counter.dec, 'Decrement %s' % name)\
			.add(bind_reset, counter.reset, 'Reset %s' % name)\
			.build()
		super().__init__(counter, bindings)

				

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

