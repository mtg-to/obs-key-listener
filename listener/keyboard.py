import logging
import keyboard

class Listener(object):
	
	def __init__(self, bindings, outputs):
		self._state, self._bindings = zip(*[b.get_bindings() for b in bindings])
		self._outputs = outputs
		self.record()

	def listen(self):
		[ self._add_hotkey(k, f, help_text) for sub in self._bindings for k,f,help_text in sub ]
		self._add_hotkey('ctrl + r', self.reset, 'Reset All');
		logging.info('ctrl + q: quit')
		keyboard.wait('ctrl + q')
	
	def _add_hotkey(self, k, f, help_text):
		logging.info('%s: %s' % (k, help_text))
		keyboard.add_hotkey(k, lambda : self._update(f))

	def _update(self, f):
		f()
		self.record()

	def reset(self):
		[b.reset() for b in self._state]	
		self.record()

	def record(self):
		[o.record(self._state) for o in self._outputs]

