import listener.config as config
import listener.output as output
from listener import Listener
from listener.output import TextCallbackOutput
from threading import Thread


class WorkerThread(Thread):

	def __init__(self, workload, on_finish):
		"""Init Worker Thread Class."""
		Thread.__init__(self)
		self._on_finish = on_finish
		self._workload = workload
		self.start()

	def run(self):
		try:
			self._workload()
		finally:
			self._on_finish()

class InputPresenter:

	def __init__(self, view, parent):
		self._view = view
		self._parent = parent
		self._cfg = None

	def on_load_config(self, evt):
		try: 
			path = evt.GetPath()
			self._cfg = config.parse_yaml(path)
			self._view.SetFormatOptions(list(self._cfg.keys()))
		except Exception as e:
			self._view.SetInvalidConfig(e.message)

	def on_select_format(self, evt):
		self._format = self._view.GetSelectedFormat()
		self._parent.set_config(self._cfg[self._format])

class OutputPresenter:
	
	default_path = 'obs.txt'
	
	def __init__(self, view, parent):
		self._view = view
		self._parent = parent
		self.make_output(self.default_path)
	
	def on_save_output(self, evt):
		path = evt.GetPath()
		self.make_output(path)
		self._view.SetMessageText(path)
		
	def make_output(self, path):
		out = output.FileOutput(path)
		self._parent.set_output(out)


class MainPresenter:

	def __init__(self, view):
		self._view = view
		self._config = None
		self._output = None
		
	def set_config(self, cfg):
		self._config = cfg
		
	def set_output(self, output):
		self._output = output

	def on_launch(self, evt):
		if self._config and self._output:
			self._view.ShowListeningDialog((self._config, self._output))
			
			
class KeyListenerPresenter:
	
	def __init__(self, view, model):
		self._view = view
		self._config = model[0]
		self._output = model[1]
	
	def ready(self):
		listener = Listener(self._config, [self._output, TextCallbackOutput(self._view.Update)])
		WorkerThread(listener.listen, self._view.Destroy)
		


