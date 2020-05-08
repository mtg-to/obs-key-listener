import wx
from listener.ui.presenter import InputPresenter,MainPresenter,OutputPresenter,\
	KeyListenerPresenter

class KeyListenerDialog(wx.Dialog):
	
	def __init__(self, parent, model):
		super().__init__(parent, title='Listening for keyboard input...', style=wx.CAPTION|wx.PD_APP_MODAL)
		self._presenter = KeyListenerPresenter(self, model)
		panel = wx.Panel(self)
		self._sizer = wx.BoxSizer(wx.VERTICAL)
		txt = wx.StaticText(panel, label='Press ctrl+q to stop!', style=wx.ALIGN_CENTER_HORIZONTAL)
		self._stateOutput = wx.StaticText(panel, label="\n")
		self._stateOutput.SetForegroundColour('white')
		self._stateOutput.SetBackgroundColour('black')
		self._stateOutput.SetFont(wx.Font(wx.FONTSIZE_SMALL, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
		self._sizer.Add((0,0), wx.SizerFlags(1).Expand())
		self._sizer.Add(txt, wx.SizerFlags(0).Expand().Border(wx.ALL, 5))
		self._sizer.Add(self._stateOutput, wx.SizerFlags(0).Expand().Border(wx.ALL, 20))
		self._sizer.Add((0,0), wx.SizerFlags(1).Expand())
		panel.SetSizer(self._sizer)
		panel.Layout()
		self._presenter.ready()
		self.CenterOnParent()
		self.ShowModal()

	def Update(self, text):
		self._stateOutput.SetLabel(text)
		self._sizer.Layout()

class InputPanel(wx.Panel):

	def __init__(self, parent, presenter):
		super().__init__(parent)
		self._parent = parent
		self._presenter = InputPresenter(self, presenter)
		self.InitUI()

	def InitUI(self):
		topSizer = wx.StaticBoxSizer(wx.VERTICAL, self, "Listener Config")
		configPicker = wx.FilePickerCtrl(self,
			message="Select config file",
			wildcard="*.yml",
			style=wx.FLP_FILE_MUST_EXIST|wx.FLP_USE_TEXTCTRL)
		self._messageText = wx.StaticText(self, label='Please select a config file!', style=wx.ALIGN_CENTRE_HORIZONTAL|wx.ST_NO_AUTORESIZE)
		self._formatRadio = None
		self._radioSizer = wx.BoxSizer(wx.VERTICAL)
		topSizer.Add(configPicker, wx.SizerFlags(0).Expand())
		topSizer.Add(self._radioSizer, wx.SizerFlags(1).Expand())
		topSizer.Add(self._messageText, wx.SizerFlags(0).Expand().Border(wx.ALL, 5))
		self.SetSizer(topSizer)		

		self.Bind(wx.EVT_FILEPICKER_CHANGED, self._presenter.on_load_config, configPicker)


	def ResetFormatOptions(self):
		if self._formatRadio:
			self._radioSizer.Hide(self._formatRadio)
			self._radioSizer.Detach(self._formatRadio)
			self._formatRadio.Destroy()

	def SetFormatOptions(self, items):
		newFormatRadio = wx.RadioBox(self,
			label="Select Format",
			choices=items,
			style=wx.RA_SPECIFY_ROWS)
		self.ResetFormatOptions()
		self._radioSizer.Add(newFormatRadio, wx.SizerFlags(0).Expand().Border(wx.Left, 20))  
		self.Bind(wx.EVT_RADIOBOX, self._presenter.on_select_format, newFormatRadio)
		self._messageText.Hide()
		self._parent.Reflow()
		self._formatRadio = newFormatRadio
		self._presenter.on_select_format(None)
	
	def SetInvalidConfig(self, message):
		self.ResetFormatOptions()
		self._messageText.SetLabel('Invalid config file: ' + message)
		self._messageText.Show()
		self._parent.Reflow()

	def GetSelectedFormat(self):
		return self._formatRadio.GetStringSelection() if self._formatRadio is not None else None

class OutputPanel(wx.Panel):
	
	def __init__(self, parent, presenter):
		super().__init__(parent)
		self._presenter = OutputPresenter(self, presenter) 
		self.InitUI()

	def InitUI(self):
		topSizer = wx.StaticBoxSizer(wx.VERTICAL, self, "Output File")
		configPicker = wx.FilePickerCtrl(self,
			message="Select output file",
			wildcard="*.txt",
			path=self._presenter.default_path,
			style=wx.FLP_SAVE | wx.FLP_USE_TEXTCTRL )
		self._messageText = wx.StaticText(self, label='Output path: ' + self._presenter.default_path, style=wx.ALIGN_CENTRE_HORIZONTAL|wx.ST_NO_AUTORESIZE)
		topSizer.Add(configPicker, wx.SizerFlags(0).Expand())
		topSizer.Add(self._messageText, wx.SizerFlags(0).Expand().Border(wx.ALL, 5))
		self.SetSizer(topSizer)
		self.Bind(wx.EVT_FILEPICKER_CHANGED, self._presenter.on_save_output, configPicker)
		
		
	def SetMessageText(self, text):
		self._messageText.SetLabel('Output path: ' + text)


class MainPanel(wx.Panel):
	
	def __init__(self, parent):
		super().__init__(parent)
		self._parent = parent
		self._presenter = MainPresenter(self) 
		self.InitUI()

	def InitUI(self):
		
		sizer = wx.BoxSizer(wx.VERTICAL)

		text = wx.StaticText(self, label='Welcome to OBS Key Listener!', size=(400, 15), style=wx.ALIGN_CENTRE_HORIZONTAL)
		inputPanel = InputPanel(self, self._presenter)
		outputPanel = OutputPanel(self, self._presenter)
		launchBtn = wx.Button(self, label="Listen!")
				
		sizer.Add(text, wx.SizerFlags(0).FixedMinSize().Expand().Border(wx.ALL, 5))
		sizer.Add(inputPanel, wx.SizerFlags(0).Expand().Border(wx.ALL, 5))
		sizer.Add(outputPanel, wx.SizerFlags(0).Expand().Border(wx.ALL, 5))
		sizer.Add(launchBtn, wx.SizerFlags(0).Expand().Border(wx.ALL, 5))

		self.SetSizer(sizer)
		self.Bind(wx.EVT_BUTTON, self._presenter.on_launch, launchBtn)

	def ShowListeningDialog(self, model):
		KeyListenerDialog(self, model)

	def Reflow(self):
		self.GetSizer().Layout()
		self._parent.Reflow()
		
class MainFrame(wx.Frame):

	def __init__(self):
		super().__init__(None, title="OBS Key Listener", size=(400, 200))
		self.InitUI()
		self.Centre()
		self.Show()
		self.Reflow()
		

	def InitUI(self):
		self._panel = MainPanel(self)
		self._baseSizer = wx.BoxSizer(wx.HORIZONTAL)
		self._baseSizer.Add(self._panel, 1, flag=wx.EXPAND)
		self.SetSizer(self._baseSizer)

	def Reflow(self):
		self.Layout()
		self.Fit()


def init_ui():
	app = wx.App()
	MainFrame()
	app.MainLoop()

