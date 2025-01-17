#!/usr/bin/python

#To profile code use the following command:
# python -m cProfile -s calls ./tool/anzhelka_terminal_gui.py



#A bug to deal with later:
#Traceback (most recent call last):
#  File "/home/clewis/class/ee175/anzhelka/software/spin/tool/anzhelka_terminal_gui_extra.py", line 313, in on_redraw_timer
#    self.draw_plot()
#  File "/home/clewis/class/ee175/anzhelka/software/spin/tool/anzhelka_terminal_gui_extra.py", line 202, in draw_plot
#    ymin = round(min(self.data), 0) - 1
#ValueError: min() arg is an empty sequence

# TODO: figure out how graph euler angles

import wx
import matplotlib
matplotlib.use('WXAgg')
import math
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
	FigureCanvasWxAgg as FigCanvas, \
	NavigationToolbar2WxAgg as NavigationToolbar
import pylab
import numpy as np
from anzhelka_terminal_serial import *

REFRESH_INTERVAL_MS = 50
paused = False

global angle_selectionS
angle_selectionS = False

motor_num = 4
angle_num = 4
motor_settings = ["Motor", "NIM", "DRPS", "Volts", "Amps", "ESC(uS)", "Thrust", "Torque", "KP", "KI", "KD"]
angle_settings = ["Number", "QDI", "QII", "QEI", "Identity","EDI", "EII", "EEI", "KPH", "KIH", "KDH"]

adjustment0 = "PWM 1"
adjustment1 = "PWM 2"
adjustment2 = "PWM 3"
adjustment3 = "PWM 4"

graph0 = "NIM 1"
graph1 = "NIM 1"
graph2 = "NIM 1"
graph3 = "NIM 1"

motor_selection = ["MKP 1", "MKP 2", "MKP 3", "MKP 4", \
                   "MKI 1", "MKI 2", "MKI 3", "MKI 4", \
                   "MKD 1", "MKD 2", "MKD 3", "MKD 4", \
                   "NID 1", "NID 2", "NID 3", "NID 4", \
                   "FZZ 1", \
                   "MOM 1", "MOM 2", "MOM 3", "MOM 4", \
                   "PWM 1", "PWM 2", "PWM 3", "PWM 4", \
                   "MPP 1", "MPP 2", \
                   "QDI 1", "QDI 2", "QDI 3", \
                   "KPH 1", "KPH 2", "KPH 3", \
                   "KIH 1", "KIH 2", "KIH 3", \
                   "KDH 1", "KDH 2", "KDH 3"]

angle_selection = ["EDI Roll", "EDI Pitch", "EDI Yaw", \
                   "EII Roll", "EII Pitch", "EII Yaw", \
                   "EEI Roll", "EEI Pitch", "EEI Yaw"]
                   
motor_adjustments = {}
# Layout          NAME     MIN, MAX, 10^, STR Front, STR Back, Matchlist Name, Array Num, Default Value
motor_adjustments["MKP 1"] = [0, 10, 3, '$ACSDR MKP,', ',*,*,*', "$ADMKP", 0, 1]
motor_adjustments["MKP 2"] = [0, 10, 3, '$ACSDR MKP,*,', ',*,*', "$ADMKP", 1, 1]
motor_adjustments["MKP 3"] = [0, 10, 3, '$ACSDR MKP,*,*,', ',*', "$ADMKP", 2, 1]
motor_adjustments["MKP 4"] = [0, 10, 3, '$ACSDR MKP,*,*,*,', '', "$ADMKP", 3, 1]
motor_adjustments["MKI 1"] = [0, 30, 3, '$ACSDR MKI,', ',*,*,*', "$ADMKI", 0, 0.1]
motor_adjustments["MKI 2"] = [0, 30, 3, '$ACSDR MKI,*,', ',*,*', "$ADMKI", 1, 0.1]
motor_adjustments["MKI 3"] = [0, 30, 3, '$ACSDR MKI,*,*,', ',*', "$ADMKI", 2, 0.1]
motor_adjustments["MKI 4"] = [0, 30, 3, '$ACSDR MKI,*,*,*,', '', "$ADMKI", 3, 0.1]
motor_adjustments["MKD 1"] = [0, 30, 3, '$ACSDR MKD,', ',*,*,*', "$ADMKD", 0, 0.5]
motor_adjustments["MKD 2"] = [0, 30, 3, '$ACSDR MKD,*,', ',*,*', "$ADMKD", 1, 0.5]
motor_adjustments["MKD 3"] = [0, 30, 3, '$ACSDR MKD,*,*,', ',*', "$ADMKD", 2, 0.5]
motor_adjustments["MKD 4"] = [0, 30, 3, '$ACSDR MKD,*,*,*,', '', "$ADMKD", 3, 0.5]
motor_adjustments["NID 1"] = [0, 160, 3, '$ACSDR NID,', ',*,*,*', "$ADNID", 0, 80]
motor_adjustments["NID 2"] = [0, 160, 3, '$ACSDR NID,*,', ',*,*', "$ADNID", 1, 80]
motor_adjustments["NID 3"] = [0, 160, 3, '$ACSDR NID,*,*,', ',*', "$ADNID", 2, 80]
motor_adjustments["NID 4"] = [0, 160, 3, '$ACSDR NID,*,*,*,', '', "$ADNID", 3, 80]
motor_adjustments["FZZ 1"] = [0, 300, 3, '$ACSDR FZZ,', '', "$ADFZZ", 0, 50]
motor_adjustments["MOM 1"] = [-50, 50, 3, '$ACSDR MOM,', ',*,*', "$ADMOM", 0, 0]
motor_adjustments["MOM 2"] = [-50, 50, 3, '$ACSDR MOM,*,', ',*', "$ADMOM", 1, 0]
motor_adjustments["MOM 3"] = [-25, 25, 3, '$ACSDR MOM,*,*,', '', "$ADMOM", 2, 0]
motor_adjustments["NIM 1"] = [0, 200, 3, '$ACSDR NIM,', ',*,*,*', "$ADNIM", 0, 0]
motor_adjustments["NIM 2"] = [0, 200, 3, '$ACSDR NIM,*,', ',*,*', "$ADNIM", 1, 0]
motor_adjustments["NIM 3"] = [0, 200, 3, '$ACSDR NIM,*,*,', ',*', "$ADNIM", 2, 0]
motor_adjustments["NIM 4"] = [0, 200, 3, '$ACSDR NIM,*,*,*,', '', "$ADNIM", 3, 0]
motor_adjustments["PWM 1"] = [1000, 2000, 1, '$ACSDR PWM,', ',*,*,*', "$ADPWM", 0, 1000]
motor_adjustments["PWM 2"] = [1000, 2000, 1, '$ACSDR PWM,*,', ',*,*', "$ADPWM", 1, 1000]
motor_adjustments["PWM 3"] = [1000, 2000, 1, '$ACSDR PWM,*,*,', ',*', "$ADPWM", 2, 1000]
motor_adjustments["PWM 4"] = [1000, 2000, 1, '$ACSDR PWM,*,*,*,', '', "$ADPWM", 3, 1000]
motor_adjustments["MPP 1"] = [0, 1, 4,   '$ACSDR MPP,', ',*', "$ADMPP", 0, .21568]
motor_adjustments["MPP 2"] = [0, 500, 3, '$ACSDR MPP,*,', '', "$ADMPP", 1, 220.770]
motor_adjustments["KPH 1"] = [0, 1, 3, '$ACSDR KPH,', ',*,*', "$ADKPH", 0, 0.4]
motor_adjustments["KPH 2"] = [0, 1, 3, '$ACSDR KPH,*,', ',*', "$ADKPH", 1, 0.4]
motor_adjustments["KPH 3"] = [0, 1, 3, '$ACSDR KPH,*,*,', '', "$ADKPH", 2, 0.4]
motor_adjustments["KIH 1"] = [0, 1, 3, '$ACSDR KIH,', ',*,*', "$ADKIH", 0, 0.4]
motor_adjustments["KIH 2"] = [0, 1, 3, '$ACSDR KIH,*,', ',*', "$ADKIH", 1, 0.4]
motor_adjustments["KIH 3"] = [0, 1, 3, '$ACSDR KIH,*,*,', '', "$ADKIH", 2, 0.4]
motor_adjustments["KDH 1"] = [0, 1, 3, '$ACSDR KDH,', ',*,*', "$ADKDH", 0, 0.4]
motor_adjustments["KDH 2"] = [0, 1, 3, '$ACSDR KDH,*,', ',*', "$ADKDH", 1, 0.4]
motor_adjustments["KDH 3"] = [0, 1, 3, '$ACSDR KDH,*,*,', '', "$ADKDH", 2, 0.4]
#TODO
#QDI  NEEDS TO BE ABLE TO SEND ALL 4 OR SEND JUST 1
#QII
#QEI 
motor_adjustments["QDI 1"] = [-1,1, 3, '$ACSDR QDI,',',*,*,*,', "$ADQDI", 1, 1]
motor_adjustments["QDI 2"] = [-1,1, 3, '$ACSDR QDI,*,', ',*,*', "$ADQDI", 1, 0]
motor_adjustments["QDI 3"] = [-1,1, 3, '$ACSDR QDI,*,*,', ',*', "$ADQDI", 1, 0]
motor_adjustments["QDI 4"] = [-1,1, 3, '$ACSDR QDI,*,*,*,', '', "$ADQDI", 1, 0]

global vartobegraphed
global vartobegraphed2
global vartobegraphed3
global vartobegraphed4
vartobegraphed = "$ADNIM"
vartobegraphed2 = "$ADNIM"
vartobegraphed3 = "$ADNIM"
vartobegraphed4 = "$ADNIM"
global graphedarraynum
global graphedarraynum2
global graphedarraynum3
global graphedarraynum4
graphedarraynum = 0
graphedarraynum2 = 0
graphedarraynum3 = 0
graphedarraynum4 = 0

class BoundControlBox(wx.Panel):
	""" A static box with a couple of radio buttons and a text
		box. Allows to switch between an automatic mode and a 
		manual mode with an associated value.
	"""
	def __init__(self, parent, ID, label, initval):
		wx.Panel.__init__(self, parent, ID)
		
		self.value = initval
		

		
		box = wx.StaticBox(self, -1, label)
		sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
		
		self.radio_auto = wx.RadioButton(self, -1, 
			label="Auto", style=wx.RB_GROUP)
		self.radio_manual = wx.RadioButton(self, -1,
			label="Manual")
		self.manual_text = wx.TextCtrl(self, -1, 
			size=(35,-1),
			value=str(initval),
			style=wx.TE_PROCESS_ENTER)
		
		self.Bind(wx.EVT_UPDATE_UI, self.on_update_manual_text, self.manual_text)
		self.Bind(wx.EVT_TEXT_ENTER, self.on_text_enter, self.manual_text)
		
		manual_box = wx.BoxSizer(wx.HORIZONTAL)
		manual_box.Add(self.radio_manual, flag=wx.ALIGN_CENTER_VERTICAL)
		manual_box.Add(self.manual_text, flag=wx.ALIGN_CENTER_VERTICAL)
		
		sizer.Add(self.radio_auto, 0, wx.ALL, 10)
		sizer.Add(manual_box, 0, wx.ALL, 10)
		
		self.SetSizer(sizer)
		sizer.Fit(self)
	
	def on_update_manual_text(self, event):
		self.manual_text.Enable(self.radio_manual.GetValue())
	
	def on_text_enter(self, event):
		self.value = self.manual_text.GetValue()
	
	def is_auto(self):
		return self.radio_auto.GetValue()
		
	def manual_value(self):
		return self.value


class GraphBox(wx.Panel):
	def __init__(self, parent, id):
		wx.Panel.__init__(self, parent, -1)

		topSizer = wx.BoxSizer(wx.VERTICAL)
		
		sizer = wx.GridBagSizer(hgap=4, vgap=3)

		self.outputstring = ''

		choices1 = list(sorted(motor_adjustments.keys()))

		self.dropbox = wx.ComboBox(self, 1, choices=choices1, style=wx.CB_DROPDOWN|wx.CB_SORT)
		self.dropbox2 = wx.ComboBox(self, 2, choices=choices1, style=wx.CB_DROPDOWN|wx.CB_SORT)
		self.dropbox3 = wx.ComboBox(self, 3, choices=choices1, style=wx.CB_DROPDOWN|wx.CB_SORT)
		self.dropbox4 = wx.ComboBox(self, 4, choices=choices1, style=wx.CB_DROPDOWN|wx.CB_SORT)
		self.display = wx.TextCtrl(self, -1, style=wx.TE_RIGHT | wx.TE_PROCESS_ENTER)
		self.sliderbox = wx.Slider(self, -1, 1, 500, 2000, wx.DefaultPosition, (250,-1), wx.SL_AUTOTICKS | wx.SL_HORIZONTAL | wx.SL_LABELS)
		self.sliderbox.SetTickFreq(200, 1)
		self.sliderboxval = self.sliderbox.GetValue()
		#self.button1 = wx.Button(self, 1, 'Update')
		#self.button2 = wx.Button(self, 2, 'Box2Slider')
		self.display.SetValue(str(self.sliderboxval))

		#Color of graphs corispond to Box Color
		self.dropbox.SetBackgroundColour(wx.Colour(255, 255, 0))
		self.dropbox2.SetBackgroundColour(wx.Colour(255, 0, 0))
		self.dropbox3.SetBackgroundColour(wx.Colour(255, 255, 255))
		self.dropbox4.SetBackgroundColour(wx.Colour(255, 0, 255))

		#TODO Set the default variables to be graphed
		self.setDefault()
		
		sizer.Add(self.dropbox, pos=(0,0), span=(1,1), flag=wx.EXPAND | wx.ALIGN_CENTRE, border=5)
		sizer.Add(self.dropbox2, pos=(0,1), span=(1,1), flag=wx.EXPAND | wx.ALIGN_CENTRE, border=5)
		sizer.Add(self.dropbox3, pos=(0,2), span=(1,1), flag=wx.EXPAND | wx.ALIGN_CENTRE, border=5)
		sizer.Add(self.dropbox4, pos=(0,3), span=(1,1), flag=wx.EXPAND | wx.ALIGN_CENTRE, border=5)
		sizer.Add(self.display, pos=(1,0), span=(1,4), flag=wx.EXPAND | wx.ALIGN_CENTRE, border=5)
		sizer.Add(self.sliderbox, pos=(2,0), span=(1,4), flag=wx.EXPAND | wx.ALIGN_CENTRE, border=5)
		#sizer.Add(self.button1, pos=(3,0), span=(1,1), flag=wx.EXPAND | wx.ALIGN_CENTRE, border=1)
		#sizer.Add(self.button2, pos=(3,2), span=(1,1), flag=wx.EXPAND | wx.ALIGN_CENTRE, border=1)
		
		#self.Bind(wx.EVT_BUTTON, self.OnUpdate, id=1)
		#self.Bind(wx.EVT_BUTTON, self.OnBox2Slider, id=2)
		self.Bind(wx.EVT_TEXT, self.sliderBoxAuto)
		self.Bind(wx.EVT_SLIDER, self.sliderUpdate)
		self.Bind(wx.EVT_COMBOBOX, self.comboSelection1, id=1)
		self.Bind(wx.EVT_COMBOBOX, self.comboSelection2, id=2)
		self.Bind(wx.EVT_COMBOBOX, self.comboSelection3, id=3)
		self.Bind(wx.EVT_COMBOBOX, self.comboSelection4, id=4)
		self.Bind(wx.EVT_TEXT_ENTER, self.OnEnter)
		
		topSizer.Add(sizer, 0, wx.ALL|wx.EXPAND, 5)

		self.SetSizer(topSizer)

		topSizer.Fit(self)

	def setOutputString(self, value):
		self.outputstring = value

	def changeChoices(self, value):
		if value == 2:
			self.dropbox.SetItems(angle_selection)
			self.dropbox2.SetItems(angle_selection)
			self.dropbox3.SetItems(angle_selection)
			self.dropbox4.SetItems(angle_selection)
			global angle_selectionS
			angle_selectionS = True
		else:
                        if angle_selectionS:
				self.dropbox.SetItems(motor_selection)
				self.dropbox2.SetItems(motor_selection)
				self.dropbox3.SetItems(motor_selection)
				self.dropbox4.SetItems(motor_selection)
				global angle_selectionS
				angle_selectionS = False

	def OnEnter(self, event):
		self.displaynum = self.display.GetValue()
		global userselectedxwidth
		userselectedxwidth = self.displaynum	

	def OnUpdate(self, event):
		self.displaynum = self.display.GetValue()
		global userselectedxwidth
		userselectedxwidth = self.displaynum

	def OnBox2Slider(self, event):
		self.sliderboxval = self.display.GetValue()
		self.sliderbox.SetValue(float(self.sliderboxval))

	def sliderUpdate(self, event):
		self.pos = self.sliderbox.GetValue()
		self.display.SetValue(str(float(self.pos)))
		global userselectedxwidth
		userselectedxwidth = self.pos

	def sliderBoxAuto(self, event):
		self.thiskey = self.dropbox.GetValue()
		self.sliderboxval = self.display.GetValue()
		self.sliderbox.SetValue(int(float(self.sliderboxval)))

	def setDefault(self):
		self.dropbox.SetValue(graph0)
		self.dropbox2.SetValue(graph1)
		self.dropbox3.SetValue(graph2)
		self.dropbox4.SetValue(graph3)
		self.comboSelection1(self)
		self.comboSelection2(self)
		self.comboSelection3(self)
		self.comboSelection4(self)

	def comboSelection1(self, event):
		self.thiskey = self.dropbox.GetValue()
		self.name = motor_adjustments[self.thiskey][5]
		self.num = motor_adjustments[self.thiskey][6]
		global vartobegraphed
		vartobegraphed = str(self.name)
		global graphedarraynum
		graphedarraynum = int(self.num)
		print "Vars being graphed: ", vartobegraphed,"[",graphedarraynum,"]"

	def comboSelection2(self, event):
		self.thiskey = self.dropbox2.GetValue()
		self.name = motor_adjustments[self.thiskey][5]
		self.num = motor_adjustments[self.thiskey][6]
		global vartobegraphed2
		vartobegraphed2 = str(self.name)
		global graphedarraynum2
		graphedarraynum2 = int(self.num)
		print "Vars being graphed: ", vartobegraphed2,"[",graphedarraynum2,"]"

	def comboSelection3(self, event):
		self.thiskey = self.dropbox3.GetValue()
		self.name = motor_adjustments[self.thiskey][5]
		self.num = motor_adjustments[self.thiskey][6]
		global vartobegraphed3
		vartobegraphed3 = str(self.name)
		global graphedarraynum3
		graphedarraynum3 = int(self.num)
		print "Vars being graphed: ", vartobegraphed3,"[",graphedarraynum3,"]"

	def comboSelection4(self, event):
		self.thiskey = self.dropbox4.GetValue()
		self.name = motor_adjustments[self.thiskey][5]
		self.num = motor_adjustments[self.thiskey][6]
		global vartobegraphed4
		vartobegraphed4 = str(self.name)
		global graphedarraynum4
		graphedarraynum4 = int(self.num)
		print "Vars being graphed: ", vartobegraphed4,"[",graphedarraynum4,"]"


class RPMGraph(wx.Panel):
#	""" The main frame of the application
#	"""
#	title = 'Demo: dynamic matplotlib graph'
	
	def __init__(self, arg1, arg2, datagen):
		wx.Panel.__init__(self, arg1, -1)

		self.rx_last_read = 0
#		self.datagen = DataGen()
		self.datagen = datagen
#		self.data = [self.datagen.next()]
		self.data = []
		self.data2 = []
		self.data3 = []
		self.data4 = []
		self.datatime = []
		self.datatime2 = []
		self.datatime3 = []
		self.datatime4 = []
		paused = False
		
		#TODO Better name needed
		global userselectedxwidth
		userselectedxwidth = 500

		
#		self.create_menu()
#		self.create_status_bar()
#		self.create_main_panel()

		self.redraw_timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.on_redraw_timer, self.redraw_timer)		
		self.redraw_timer.Start(REFRESH_INTERVAL_MS)

#	def create_menu(self):
#		self.menubar = wx.MenuBar()
#		
#		menu_file = wx.Menu()
#		m_expt = menu_file.Append(-1, "&Save plot\tCtrl-S", "Save plot to file")
#		self.Bind(wx.EVT_MENU, self.on_save_plot, m_expt)
#		menu_file.AppendSeparator()
#		m_exit = menu_file.Append(-1, "E&xit\tCtrl-X", "Exit")
#		self.Bind(wx.EVT_MENU, self.on_exit, m_exit)
#				
#		self.menubar.Append(menu_file, "&File")
#		self.SetMenuBar(self.menubar)

#	def create_main_panel(selfi):
#		self.panel = wx.Panel(self)

		self.init_plot()
		self.canvas = FigCanvas(self, -1, self.fig)

		self.xmin_control = BoundControlBox(self, -1, "X min", 0)
		self.xmax_control = BoundControlBox(self, -1, "X max", 50)
		self.ymin_control = BoundControlBox(self, -1, "Y min", 0)
		self.ymax_control = BoundControlBox(self, -1, "Y max", 100)
		self.grid_control = GraphBox(self, -1)


		self.pause_button = wx.Button(self, -1, "Pause")
		self.Bind(wx.EVT_BUTTON, self.on_pause_button, self.pause_button)
		self.Bind(wx.EVT_UPDATE_UI, self.on_update_pause_button, self.pause_button)

		self.cb_grid = wx.CheckBox(self, -1, 
			"Show Grid",
			style=wx.ALIGN_RIGHT)
		self.Bind(wx.EVT_CHECKBOX, self.on_cb_grid, self.cb_grid)
		self.cb_grid.SetValue(True)
		
		self.cb_xlab = wx.CheckBox(self, -1, 
			"Show X labels",
			style=wx.ALIGN_RIGHT)
		self.Bind(wx.EVT_CHECKBOX, self.on_cb_xlab, self.cb_xlab)		
		self.cb_xlab.SetValue(True)

		self.colorBox1 = wx.Button(self, -1, "Line 1")
		self.colorBox1.SetBackgroundColour(wx.Colour(255, 255, 0))
		self.colorBox2 = wx.Button(self, -1, "Line 2")
		self.colorBox2.SetBackgroundColour(wx.Colour(255, 0, 0))
		self.colorBox3 = wx.Button(self, -1, "Line 3")
		self.colorBox3.SetBackgroundColour(wx.Colour(255, 255, 255))
		self.colorBox4 = wx.Button(self, -1, "Line 4")
		self.colorBox4.SetBackgroundColour(wx.Colour(255, 0, 255))
		#I am here

		self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		self.hbox1.Add(self.pause_button, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
		self.hbox1.AddSpacer(20)
		self.hbox1.Add(self.cb_grid, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
		self.hbox1.AddSpacer(10)
		self.hbox1.Add(self.cb_xlab, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
		self.hbox1.AddSpacer(10)
		self.hbox1.Add(self.colorBox1, border=1, flag=wx.ALL | wx.ALIGN_CENTRE)
		self.hbox1.Add(self.colorBox2, border=1, flag=wx.ALL | wx.ALIGN_CENTRE)
		self.hbox1.Add(self.colorBox3, border=1, flag=wx.ALL | wx.ALIGN_CENTRE)
		self.hbox1.Add(self.colorBox4, border=1, flag=wx.ALL | wx.ALIGN_CENTRE)
		
		self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		self.hbox2.Add(self.xmin_control, border=5, flag=wx.ALL)
		self.hbox2.Add(self.xmax_control, border=5, flag=wx.ALL)
		self.hbox2.AddSpacer(24)
		self.hbox2.Add(self.ymin_control, border=5, flag=wx.ALL)
		self.hbox2.Add(self.ymax_control, border=5, flag=wx.ALL)
		self.hbox2.AddSpacer(24)
		self.hbox2.Add(self.grid_control, border=5, flag=wx.ALL)

		self.vbox = wx.BoxSizer(wx.VERTICAL)
		self.vbox.Add(self.canvas, 1, flag=wx.LEFT | wx.TOP | wx.GROW)		
		self.vbox.Add(self.hbox1, 0, flag=wx.ALIGN_LEFT | wx.TOP)
		self.vbox.Add(self.hbox2, 0, flag=wx.ALIGN_LEFT | wx.TOP)
		
		self.SetSizer(self.vbox)
		self.vbox.Fit(self)
	
#	def create_status_bar(self):
#		self.statusbar = self.CreateStatusBar()

	def init_plot(self):
		self.dpi = 100
		self.fig = Figure((3.0, 3.0), dpi=self.dpi)

		self.axes = self.fig.add_subplot(111)
		self.axes.set_axis_bgcolor('black')
		self.axes.set_title('Serial Data', size=12)
		
		pylab.setp(self.axes.get_xticklabels(), fontsize=8)
		pylab.setp(self.axes.get_yticklabels(), fontsize=8)

		# plot the data as a line series, and save the reference 
		# to the plotted line series
		#
		self.plot_data = self.axes.plot(
			self.data, 
			linewidth=1,
			color=(1, 1, 0),
			)[0]
		self.plot_data2 = self.axes.plot(
			self.data2, 
			linewidth=1,
			color=(1, 0, 0),
			)[0]
		self.plot_data3 = self.axes.plot(
			self.data3, 
			linewidth=1,
			color=(1, 1, 1),
			)[0]
		self.plot_data4 = self.axes.plot(
			self.data4, 
			linewidth=1,
			color=(1, 0, 1),
			)[0]

	def draw_plot(self):
		""" Redraws the plot
		"""
		# when xmin is on auto, it "follows" xmax to produce a 
		# sliding window effect. therefore, xmin is assigned after
		# xmax.
		#
		
		if len(self.data) == 0 or len(self.data2) == 0:
			return
			
			
		if self.xmax_control.is_auto():
			xmax = self.datatime[-1] if len(self.data) > 50 else 50
		else:
			xmax = int(self.xmax_control.manual_value())
			
		if self.xmin_control.is_auto():			
			xmin = xmax - userselectedxwidth #TODO: Make this a slider option
		else:
			xmin = int(self.xmin_control.manual_value())

		# for ymin and ymax, find the minimal and maximal values
		# in the data set and add a mininal margin.
		# 
		# note that it's easy to change this scheme to the 
		# minimal/maximal value in the current display, and not
		# the whole data set.
		# 
		if self.ymin_control.is_auto():
			ymin = round(min(self.data), 0) - 1
		else:
			ymin = int(self.ymin_control.manual_value())
		if self.ymax_control.is_auto():
			ymax = round(max(self.data), 0) + 1
		else:
			ymax = int(self.ymax_control.manual_value())
		self.axes.set_xbound(lower=xmin, upper=xmax)
		self.axes.set_ybound(lower=ymin, upper=ymax)
		
		# anecdote: axes.grid assumes b=True if any other flag is
		# given even if b is set to False.
		# so just passing the flag into the first statement won't
		# work.
		#
		if self.cb_grid.IsChecked():
			self.axes.grid(True, color='gray')
		else:
			self.axes.grid(False)

		# Using setp here is convenient, because get_xticklabels
		# returns a list over which one needs to explicitly 
		# iterate, and setp already handles this.
		#  
		pylab.setp(self.axes.get_xticklabels(), 
			visible=self.cb_xlab.IsChecked())
		
#		temp = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

		#print "self.data: ", self.data[len(self.data)-1]	
		
		#self.plot_data.set_xdata(np.arange(len(self.data2)))
		#self.plot_data.set_ydata(np.array(self.data2))
		self.plot_data.set_data(self.datatime, self.data)
		self.plot_data2.set_data(self.datatime2, self.data2)
		self.plot_data3.set_data(self.datatime3, self.data3)
		self.plot_data4.set_data(self.datatime4, self.data4)
#		self.plot_data.set_xdata(np.arange(len(temp)))
#		self.plot_data.set_ydata(np.array(temp))
		
		
		self.canvas.draw()
	
	def on_pause_button(self, event):
		global paused
		paused = not paused
	
	def on_update_pause_button(self, event):
		label = "Resume" if paused else "Pause"
		self.pause_button.SetLabel(label)
	
	def on_cb_grid(self, event):
		self.draw_plot()
	
	def on_cb_xlab(self, event):
		self.draw_plot()
	
	def on_save_plot(self, event):
		file_choices = "PNG (*.png)|*.png"
		
		dlg = wx.FileDialog(
			self, 
			message="Save plot as...",
			defaultDir=os.getcwd(),
			defaultFile="plot.png",
			wildcard=file_choices,
			style=wx.SAVE)
		
		if dlg.ShowModal() == wx.ID_OK:
			path = dlg.GetPath()
			self.canvas.print_figure(path, dpi=self.dpi)
			self.flash_status_message("Saved to %s" % path)
	
	
	
	
	
	
#	def serial_parse_ADRPS(self, line):
#		#Returns a list with the four motor speeds, or an empty list
#		if line.find("$ADRPS ") != -1: #String matches
#			line = line[8:] #Get rid of "$ADRPS "
#			nums = line.split(",")
#			try:
#				for i in range(len(nums)):
#					nums[i] = float(nums[i])
#			except ValueError:
#				print "Could not parse $ADRPS String"
#				return []
#				
#			return nums
#		else:
#			return []
		
	
	def on_redraw_timer(self, event):
		# if paused do not add data, but still redraw the plot
		# (to respond to scale modifications, grid change, etc.)
		#
		global rx_buffer_lock
		global rx_buffer
		global serial_parse_ADRPS
		
		rxparser = RxParser()
		tobegraphed = []
		
		if not paused:
			if not rx_buffer_lock.acquire(False):
				pass
			else:
				try:
					i = 0
					#Go through all the received strings and add whatever is relevant.
					
					while self.rx_last_read < len(rx_buffer):
#						print "self.rx_last_read == ", self.rx_last_read
#						print "len(rx_buffer) == ", len(rx_buffer)		
#						print "Reading last i == ", i
#						i += 1
						tobegraphed = rxparser.match(rx_buffer[self.rx_last_read], vartobegraphed)
						tobegraphed2 = rxparser.match(rx_buffer[self.rx_last_read], vartobegraphed2)
						tobegraphed3 = rxparser.match(rx_buffer[self.rx_last_read], vartobegraphed3)
						tobegraphed4 = rxparser.match(rx_buffer[self.rx_last_read], vartobegraphed4)
						self.rx_last_read += 1
						if len(tobegraphed) != 0:
							self.data.append(float(tobegraphed[int(graphedarraynum)])) #Get first graph info...
							if len(self.datatime) == 0:
 								self.datatime.append(int(0))
							else:
								self.datatime.append(self.datatime[-1]+1)
							if len(self.data) > 2200:
								self.data.pop(0)
								self.datatime.pop(0)
                                                                #print "Data length: ", len(self.data), "\nDatatime length: ", len(self.datatime)
						if len(tobegraphed2) != 0:
							self.data2.append(float(tobegraphed2[int(graphedarraynum2)])) #Get second graph info...
							if len(self.datatime2) == 0:
								self.datatime2.append(int(0))
							else:
								self.datatime2.append(self.datatime2[-1]+1)
							if len(self.data2) > 2200:
								self.data2.pop(0)
								self.datatime2.pop(0)
						if len(tobegraphed3) != 0:
							self.data3.append(float(tobegraphed3[int(graphedarraynum3)])) #Get second graph info...
							if len(self.datatime3) == 0:
								self.datatime3.append(int(0))
							else:
								self.datatime3.append(self.datatime3[-1]+1)
							if len(self.data3) > 2200:
								self.data3.pop(0)
								self.datatime3.pop(0)
						if len(tobegraphed4) != 0:
							self.data4.append(float(tobegraphed4[int(graphedarraynum4)])) #Get second graph info...
							if len(self.datatime4) == 0:
								self.datatime4.append(int(0))
							else:
								self.datatime4.append(self.datatime4[-1]+1)
							if len(self.data4) > 2200:
								self.data4.pop(0)
								self.datatime4.pop(0)

				finally:
					rx_buffer_lock.release()

		
		self.draw_plot()
	
	
	
	
	
	
	
	
	
	def on_exit(self, event):
		self.Destroy()
		
	
	def flash_status_message(self, msg, flash_len_ms=1500):
		self.statusbar.SetStatusText(msg)
		self.timeroff = wx.Timer(self)
		self.Bind(
			wx.EVT_TIMER, 
			self.on_flash_status_off, 
			self.timeroff)
		self.timeroff.Start(flash_len_ms, oneShot=True)
	
	def on_flash_status_off(self, event):
		self.statusbar.SetStatusText('')


class AdjustmentTableSizer(wx.Panel):
	def __init__(self, parent, id):
		wx.Panel.__init__(self, parent, -1)

		topSizer = wx.BoxSizer(wx.VERTICAL)
		
		sizer = wx.GridBagSizer(hgap=16, vgap=7)
		
		self.box0 = AdjustmentTable(self, -1)
		self.box1 = AdjustmentTable(self, -1)
		self.box2 = AdjustmentTable(self, -1)
		self.box3 = AdjustmentTable(self, -1)

		#TODO This is used to set the default Adjustments
		self.box0.setDefault(adjustment0)
		self.box1.setDefault(adjustment1)
		self.box2.setDefault(adjustment2)
		self.box3.setDefault(adjustment3)
		
		self.button1 = wx.Button(self, 1, 'Update')
		self.button2 = wx.Button(self, 10, 'STOP ALL')
		self.button2.SetBackgroundColour(wx.RED)
		self.button2.SetForegroundColour(wx.WHITE)
		font = wx.Font(family=wx.FONTFAMILY_DEFAULT, style=wx.FONTSTYLE_NORMAL, weight=wx.FONTWEIGHT_NORMAL, pointSize=18)
		self.button2.SetFont(font)
		#print self.button2.GetValue()
		self.outputstring = ''
		self.stopped = False

		sizer.Add(self.box0, pos=(0,0), span=(5,4), flag=wx.EXPAND | wx.ALIGN_CENTRE, border=5)
		sizer.Add(self.box1, pos=(0,4), span=(5,4), flag=wx.EXPAND | wx.ALIGN_CENTRE, border=5)
		sizer.Add(self.box2, pos=(0,8), span=(5,4), flag=wx.EXPAND | wx.ALIGN_CENTRE, border=5)
		sizer.Add(self.box3, pos=(0,12), span=(5,4), flag=wx.EXPAND | wx.ALIGN_CENTRE, border=5)
		sizer.Add(self.button1, pos=(5,6), span=(2,2), flag=wx.EXPAND | wx.ALIGN_CENTRE, border=5)
		sizer.Add(self.button2, pos=(5,8), span=(5,5), flag=wx.EXPAND | wx.ALIGN_CENTRE, border=5)
		
		self.Bind(wx.EVT_BUTTON, self.OnUpdate, id=1)
		self.Bind(wx.EVT_BUTTON, self.OnStopAll, id=10)
		
		topSizer.Add(sizer, 0, wx.ALL|wx.EXPAND, 5)

		self.SetSizer(topSizer)

		topSizer.Fit(self)


	def OnUpdate(self, event):
		self.box0.OnUpdate(self)
		self.box1.OnUpdate(self)
		self.box2.OnUpdate(self)
		self.box3.OnUpdate(self)

	def OnStopAll(self, event):
		if self.stopped == False:
                        self.outputstring = "$ACSTP EMG\n"
                        self.stopped = True
                        self.button2.SetBackgroundColour(wx.GREEN)
                        self.button2.SetLabel('Resume')
                else:
                        self.outputstring = "$ACSTP RES\n"
                        self.stopped = False
                        self.button2.SetBackgroundColour(wx.RED)
                        self.button2.SetLabel('STOP ALL')
		print self.outputstring
		sending(ser, self.outputstring)



class AdjustmentTable(wx.Panel):
	def __init__(self, parent, id):
		wx.Panel.__init__(self, parent, -1)

		topSizer = wx.BoxSizer(wx.VERTICAL)
		
		sizer = wx.GridBagSizer(hgap=5, vgap=5)

		self.outputstring = ''

		self.dropbox = wx.ComboBox(self, -1, choices=list(sorted(motor_selection)), style=wx.CB_DROPDOWN|wx.CB_SORT)
		self.display = wx.TextCtrl(self, 3, style=wx.TE_RIGHT | wx.TE_PROCESS_ENTER)
		self.display1 = wx.TextCtrl(self, 4, style=wx.TE_LEFT)
		self.display2 = wx.TextCtrl(self, 5, style=wx.TE_RIGHT)
		self.sliderbox = wx.Slider(self, -1, 1, 20, 10000, wx.DefaultPosition, (250,-1), wx.SL_AUTOTICKS | wx.SL_HORIZONTAL | wx.SL_TOP)
		self.sliderbox.SetTickFreq(1000, 1)
		self.sliderboxval = self.sliderbox.GetValue()
		self.button1 = wx.Button(self, 1, 'Update')
		self.button2 = wx.Button(self, 2, 'Defaults')
		self.display.SetValue(str(self.sliderboxval))
		
		sizer.Add(self.dropbox, pos=(0,0), span=(1,4), flag=wx.EXPAND | wx.ALIGN_CENTRE, border=5)
		sizer.Add(self.display, pos=(1,0), span=(1,4), flag=wx.EXPAND | wx.ALIGN_CENTRE, border=5)
		sizer.Add(self.display1, pos=(2,0), span=(1,1), flag=wx.EXPAND | wx.ALIGN_CENTRE, border=5)
		sizer.Add(self.display2, pos=(2,2), span=(1,1), flag=wx.EXPAND | wx.ALIGN_CENTRE, border=5)
		sizer.Add(self.sliderbox, pos=(3,0), span=(1,4), flag=wx.EXPAND | wx.ALIGN_CENTRE, border=5)
		sizer.Add(self.button1, pos=(4,0), span=(1,1), flag=wx.EXPAND | wx.ALIGN_CENTRE, border=1)
		sizer.Add(self.button2, pos=(4,2), span=(1,1), flag=wx.EXPAND | wx.ALIGN_CENTRE, border=1)
		
		self.Bind(wx.EVT_BUTTON, self.OnUpdate, id=1)
		self.Bind(wx.EVT_BUTTON, self.setToDefault, id=2)
		self.Bind(wx.EVT_TEXT, self.sliderBoxAuto, id=3)
		self.Bind(wx.EVT_TEXT, self.sliderBoxBounds, id=4)
		self.Bind(wx.EVT_TEXT, self.sliderBoxBounds, id=5)
		self.Bind(wx.EVT_SLIDER, self.sliderUpdate)
		self.Bind(wx.EVT_COMBOBOX, self.comboSelection)
		self.Bind(wx.EVT_TEXT_ENTER, self.OnEnter)
		
		topSizer.Add(sizer, 0, wx.ALL|wx.EXPAND, 5)

		self.SetSizer(topSizer)

		topSizer.Fit(self)

	def setDefault(self, value):
		self.dropbox.SetValue(value)
		self.comboSelection(self)

	def setToDefault(self, event):
		self.thiskey = self.dropbox.GetValue()
		self.display.SetValue(str((motor_adjustments[self.thiskey])[7]))
		self.sliderUpdate(self)
                
	def OnEnter(self, event):
		self.displaynum = self.display.GetValue()
		self.outputstring = (motor_adjustments[self.thiskey])[3] + self.displaynum + (motor_adjustments[self.thiskey])[4]
		sending(ser, self.outputstring)

	def OnUpdate(self, event):
		self.displaynum = self.display.GetValue()
		self.outputstring = (motor_adjustments[self.thiskey])[3] + self.displaynum + (motor_adjustments[self.thiskey])[4]
		sending(ser, self.outputstring)

	def OnBox2Slider(self, event):
		self.sliderboxval = self.display.GetValue()
		self.sliderbox.SetValue(float(self.sliderboxval))

	def sliderUpdate(self, event):
		self.pos = self.sliderbox.GetValue()
		self.devideby = pow(10,(motor_adjustments[self.thiskey])[2])
		self.display.SetValue(str(float(self.pos)/self.devideby))

	def sliderBoxAuto(self, event):
		self.thiskey = self.dropbox.GetValue()
		self.sliderboxval = self.display.GetValue()
		self.multiplyby = pow(10,(motor_adjustments[self.thiskey])[2])
		self.sliderbox.SetValue(int(float(self.sliderboxval)*self.multiplyby))

	def sliderBoxBounds(self, event):
		self.thiskey = self.dropbox.GetValue()
		self.sliderboxlower = float(self.display1.GetValue())
		self.sliderboxupper = float(self.display2.GetValue())
		self.multiplyby = pow(10,(motor_adjustments[self.thiskey])[2])
		self.sliderbox.SetRange(int(float(self.sliderboxlower)*self.multiplyby),int(float(self.sliderboxupper)*self.multiplyby))

	def comboSelection(self, event):
		self.thiskey = self.dropbox.GetValue()
		self.minpos = (motor_adjustments[self.thiskey])[0]*pow(10,(motor_adjustments[self.thiskey])[2])
		self.maxpos = (motor_adjustments[self.thiskey])[1]*pow(10,(motor_adjustments[self.thiskey])[2])
		self.sliderbox.SetRange(self.minpos, self.maxpos)
		self.devideby = pow(10,(motor_adjustments[self.thiskey])[2])
		self.display1.SetValue(str(float(self.minpos)/self.devideby))
		self.display2.SetValue(str(float(self.maxpos)/self.devideby))
		self.setToDefault(self)

	def updateMotor(motor, value):
		self.maxpos = 20 #Get Value from TABLE
		



def reverseenum(string, l):
	#returns the index value based on the string passed in
	for i in range(len(l)):
		if string == l[i]:
			return i
	return -1 #no match


class MotorTable(wx.Panel):
	def __init__(self, parent, id):
		wx.Panel.__init__(self, parent, -1)

		self.rx_last_read = 0

		self.rxparser = RxParser()
		
		self.motor_table = []


		self.motor_table.append([])
		for i in motor_settings:
			self.motor_table[0].append(wx.StaticText(self, -1, i))
	
		for i in range(motor_num):
			print "Motor Table init i value: ", i
			self.motor_table.append([])
			for j in range(len(motor_settings)):
				if j == reverseenum("Motor", motor_settings): # Motor number
					self.motor_table[i+1].append(wx.TextCtrl(self, -1, str(i)))
				elif j == reverseenum("NIM", motor_settings): # Motor number
					self.motor_table[i+1].append(wx.TextCtrl(self, -1, "---"))
				elif j == reverseenum("Volts", motor_settings): # Motor number
					self.motor_table[i+1].append(wx.TextCtrl(self, -1, "---"))
				elif j == reverseenum("Amps", motor_settings): # Motor number
					self.motor_table[i+1].append(wx.TextCtrl(self, -1, "---"))
				elif j == reverseenum("ESC(uS)", motor_settings): # Motor number
					self.motor_table[i+1].append(wx.TextCtrl(self, -1, "---"))
				elif j == reverseenum("Thrust", motor_settings): # Motor number
					self.motor_table[i+1].append(wx.TextCtrl(self, -1, "---"))
				elif j == reverseenum("Torque", motor_settings): # Motor number
					self.motor_table[i+1].append(wx.TextCtrl(self, -1, "---"))
				else:
					self.motor_table[i+1].append(wx.TextCtrl(self, -1, "generic"))

		grid_sizer = wx.FlexGridSizer(motor_num+1, len(motor_settings), 10, 10)		
		for i in self.motor_table:
			for j in i:
				grid_sizer.Add(j)

		self.SetSizer(grid_sizer)
		
		self.redraw_timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.on_redraw_timer, self.redraw_timer)		
		self.redraw_timer.Start(REFRESH_INTERVAL_MS)

	
		
	def update_field(self, code, enum_field):
		matchlist = self.rxparser.match(rx_buffer[self.rx_last_read], code)
		#print "Matchlist: ", matchlist
		for i in range(len(matchlist)): # != 0:
			self.motor_table[i+1][reverseenum(enum_field, motor_settings)].SetValue(str(matchlist[i]))
			#print "Self.Motor_table[i+1]: ", str(self.motor_table[i+1])
			
	def on_redraw_timer(self, event):
		# if paused do not add data, but still redraw the plot
		# (to respond to scale modifications, grid change, etc.)
		#
		global rx_buffer_lock
		global rx_buffer
#		rxparser = RxParser()
		
		if not paused:
			if not rx_buffer_lock.acquire(False):
				pass
			else:
				try:
					#Go through all the received strings and add whatever is relevant.
					while self.rx_last_read < len(rx_buffer):
						#First is the header of string, second is Colomn on motor table heading
						self.update_field("$ADNID", "DRPS")
						self.update_field("$ADNIM", "NIM")
						self.update_field("$ADMIA", "Amps")
						self.update_field("$ADMVV", "Volts")
						self.update_field("$ADPWM", "ESC(uS)")
						self.update_field("$ADMTH", "Thrust")
						self.update_field("$ADMTQ", "Torque")
						self.update_field("$ADMKP", "KP")
						self.update_field("$ADMKI", "KI")
						self.update_field("$ADMKD", "KD")
						
						
						
#						motor_amp = self.rxparser.match(rx_buffer[self.rx_last_read], "$ADMIA")
#						for i in range(len(motor_amp)): # != 0:
#							self.motor_table[i+1][reverseenum("Amps", motor_settings)].SetValue(str(motor_amp[i]))

						self.rx_last_read += 1

				finally:
					rx_buffer_lock.release()


class Quaternion(wx.Panel):
	def __init__(self, parent, id):
		wx.Panel.__init__(self, parent, -1)

		self.rx_last_read = 0

		self.rxparser = RxParser()
		
		self.angle_table = []


		self.angle_table.append([])
		for i in angle_settings:
			self.angle_table[0].append(wx.StaticText(self, -1, i))
		eulernames = ["Roll", "Pitch", "Yaw", "N/A"]
		for i in range(angle_num):
			print "Angle Table init i value: ", i
			self.angle_table.append([])
			for j in range(len(angle_settings)):
				if j == reverseenum("Number", angle_settings): # angle number
					self.angle_table[i+1].append(wx.TextCtrl(self, -1, str(i+1)))
				elif j == reverseenum("QDI", angle_settings): # angle number
					self.angle_table[i+1].append(wx.TextCtrl(self, -1, "---"))
				elif j == reverseenum("QII", angle_settings): # angle number
					self.angle_table[i+1].append(wx.TextCtrl(self, -1, "---"))
				elif j == reverseenum("QEI", angle_settings): # angle number
					self.angle_table[i+1].append(wx.TextCtrl(self, -1, "---"))
				elif j == reverseenum("Identity", angle_settings): # angle number
					self.angle_table[i+1].append(wx.TextCtrl(self, -1, str(eulernames[i])))
				elif j == reverseenum("EDI", angle_settings): # angle number
					self.angle_table[i+1].append(wx.TextCtrl(self, -1, "---"))
				elif j == reverseenum("EII", angle_settings): # angle number
					self.angle_table[i+1].append(wx.TextCtrl(self, -1, "---"))
				elif j == reverseenum("EEI", angle_settings): # angle number
					self.angle_table[i+1].append(wx.TextCtrl(self, -1, "---"))
				elif j == reverseenum("KPH", angle_settings): # angle number
					self.angle_table[i+1].append(wx.TextCtrl(self, -1, "---"))
				elif j == reverseenum("KIH", angle_settings): # angle number
					self.angle_table[i+1].append(wx.TextCtrl(self, -1, "---"))
				elif j == reverseenum("KDH", angle_settings): # angle number
					self.angle_table[i+1].append(wx.TextCtrl(self, -1, "---"))
				else:
					self.angle_table[i+1].append(wx.TextCtrl(self, -1, "generic"))

		grid_sizer = wx.FlexGridSizer(angle_num+1, len(angle_settings), 10, 10)		
		for i in self.angle_table:
			for j in i:
				grid_sizer.Add(j, flag=wx.EXPAND | wx.ALIGN_CENTRE, border=5)

		self.SetSizer(grid_sizer)
		
		self.redraw_timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.on_redraw_timer, self.redraw_timer)		
		self.redraw_timer.Start(REFRESH_INTERVAL_MS)

	
		
	def update_field(self, code, enum_field):
		matchlist = self.rxparser.match(rx_buffer[self.rx_last_read], code)
		#print "Matchlist: ", matchlist
		for i in range(len(matchlist)): # != 0:
			self.angle_table[i+1][reverseenum(enum_field, angle_settings)].SetValue(str(matchlist[i]))

	def update_fieldq(self, code, enum_field):
		matchlist = self.rxparser.match(rx_buffer[self.rx_last_read], code)
		#print "Matchlist: ", matchlist
		for i in range(len(matchlist)): # != 0:
			self.angle_table[i+1][reverseenum(enum_field, angle_settings)].SetValue(str(matchlist[i]))
		if len(matchlist) != 4:
                        return
		yaw = math.atan2(2*matchlist[1]*matchlist[0]- \
                                     2*matchlist[0]*matchlist[3], \
                                     2*matchlist[1]*matchlist[1]- \
                                     2*matchlist[3]*matchlist[3])
		pitch = math.asin(2*matchlist[0]*matchlist[1]+ \
                                     2*matchlist[3]*matchlist[2])
		roll = math.atan2(2*matchlist[0]*matchlist[2]- \
                                  2*matchlist[1]*matchlist[3], \
                                  1-2*matchlist[0]*matchlist[0] - \
                                  2*matchlist[3]*matchlist[3])
		eulerlist = [yaw, pitch, roll, 0]
		euler_field = ''
		if enum_field == "QDI":
                        euler_field = "EDI"
                if enum_field == "QII":
                        euler_field = "EII"
                if enum_field == "QEI":
                        euler_field = "EEI"
		for i in range(len(eulerlist)): # != 0:
                        self.angle_table[i+1][reverseenum(euler_field, angle_settings)].SetValue(str(eulerlist[i]))
			

	def on_redraw_timer(self, event):
		# if paused do not add data, but still redraw the plot
		# (to respond to scale modifications, grid change, etc.)
		#
		global rx_buffer_lock
		global rx_buffer
#		rxparser = RxParser()
		
		if not paused:
			if not rx_buffer_lock.acquire(False):
				pass
			else:
				try:
					#Go through all the received strings and add whatever is relevant.
					while self.rx_last_read < len(rx_buffer):
						#First is the header of string, second is Colomn on angle table heading
						self.update_fieldq("$ADQDI", "QDI")
						self.update_fieldq("$ADQII", "QII")
						self.update_fieldq("$ADQEI", "QEI")
						self.update_field("$ADKPH", "KPH")
						self.update_field("$ADKIH", "KIH")
						self.update_field("$ADKDH", "KDH")
						#self.update_field("$ADMTQ", "Torque")
						#self.update_field("$ADMKP", "KP")
						#self.update_field("$ADMKI", "KI")
						#self.update_field("$ADMKD", "KD")
						
						
						
#						angle_amp = self.rxparser.match(rx_buffer[self.rx_last_read], "$ADMIA")
#						for i in range(len(angle_amp)): # != 0:
#							self.angle_table[i+1][reverseenum("Amps", angle_settings)].SetValue(str(angle_amp[i]))

						self.rx_last_read += 1

				finally:
					rx_buffer_lock.release()


if __name__=='__main__':
	print "Please note this is not intended to be run standalone. Please run ./anzhelka_terminal_gui.py instead."

