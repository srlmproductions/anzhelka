#!/usr/bin/env python
# -*- coding: utf-8 -*-
# generated by wxGlade 0.6.3 on Tue Apr 10 00:14:55 2012

import wx

threadkillall = False #If true signals threads to kill themselves

# begin wxGlade: extracode
from anzhelka_terminal_serial import *
datagen = DataGen()
from anzhelka_terminal import *
from anzhelka_terminal_gui_extra import *
#from anzhelka_terminal_serial import *
##datagen = DataGen()
#from anzhelka_terminal import *
#from anzhelka_terminal_gui_extra import *
# end wxGlade



class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MyFrame.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.notebook_1 = wx.Notebook(self, id=100, style=0)
        self.notebook_1_pane_2 = wx.Panel(self.notebook_1, -1)
        self.notebook_2 = wx.Notebook(self.notebook_1_pane_2, id=200, style=0)
        self.notebook_2_pane_1 = wx.Panel(self.notebook_2, -1)
        self.notebook_2_pane_2 = wx.Panel(self.notebook_2, -1)
        self.notebook_2_pane_3 = wx.Panel(self.notebook_2, -1)
        self.panel_1 = wx.Panel(self.notebook_1, -1)
        self.label_7 = wx.StaticText(self.panel_1, -1, "USB Port")
        self.label_5 = wx.StaticText(self.panel_1, -1, "Port")
        self.combo_serial_port = wx.ComboBox(self.panel_1, -1, choices=["\\dev\ttyUSB0"], style=wx.CB_DROPDOWN|wx.CB_SORT)
        #self.bmp = wx.Image('..\..\doc\extra\tribal_phoenix.jpg',wx.BITMAP_TYPE_JPEG).ConvertToBitmap()
        #wx.StaticBitmap(self.panel_1, -1, self.bmp)
        self.label_6 = wx.StaticText(self.panel_1, -1, "Baud")
        self.combo_serial_baud = wx.ComboBox(self.panel_1, -1, choices=["9600", "19200", "38400", "57600", "115200"], style=wx.CB_DROPDOWN|wx.CB_SORT)
        self.toggle_serial_connect = wx.ToggleButton(self.panel_1, -1, "Connect")
        self.label_1_copy_2 = wx.StaticText(self.panel_1, -1, "Some Simple Text")
        self.label_1 = wx.StaticText(self.panel_1, -1, "Some Simple Text")
        self.label_1_copy_1 = wx.StaticText(self.panel_1, -1, "Some Simple Text")
        self.window_2 = RPMGraph(self.notebook_1_pane_2, -1, datagen)
        self.window_1 = MotorTable(self.notebook_2_pane_1, -1)
        
        #Added
        self.window_0 = AdjustmentTableSizer(self.notebook_2_pane_2, 2)
        self.window_3 = Quaternion(self.notebook_2_pane_3, -1)
        #self.window_0 = AdjustmentTable(self.notebook_2_pane_2, -1)
        #self.window_01 = AdjustmentTable(self.notebook_2_pane_2, -1)
        self.notebook_1_pane_3 = wx.Panel(self.notebook_1, -1)
        self.notebook_1_pane_4 = wx.Panel(self.notebook_1, -1)

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_TOGGLEBUTTON, self.OnPortConnect, self.toggle_serial_connect)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged1, id=100)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged2, id=200)
        # end wxGlade

    def OnPageChanged1(self, event):
        new = event.GetSelection()

    def OnPageChanged2(self, event):
        new = event.GetSelection()
        self.window_2.grid_control.changeChoices(int(new))
        print "Note2,",new

    def __set_properties(self):
        # begin wxGlade: MyFrame.__set_properties
        self.SetTitle("Anzhelka Terminal")
        self.SetSize((950, 879))
        self.combo_serial_port.SetToolTipString("Please enter your COM port as appropriate")
        self.combo_serial_port.SetSelection(0)
        self.combo_serial_baud.SetSelection(4)
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MyFrame.__do_layout
        grid_sizer_3 = wx.FlexGridSizer(3, 3, 0, 0)
        grid_sizer_5 = wx.FlexGridSizer(2, 1, 0, 0)
        grid_sizer_6 = wx.FlexGridSizer(1, 1, 0, 0)
        grid_sizer_7 = wx.FlexGridSizer(1, 1, 0, 0)
        grid_sizer_4 = wx.FlexGridSizer(3, 3, 0, 0)
        grid_sizer_2 = wx.FlexGridSizer(3, 1, 5, 0)
        grid_sizer_2_copy = wx.FlexGridSizer(2, 2, 5, 5)
        grid_sizer_2.Add(self.label_7, 0, 0, 0)
        grid_sizer_2_copy.Add(self.label_5, 0, 0, 0)
        grid_sizer_2_copy.Add(self.combo_serial_port, 0, 0, 0)
        grid_sizer_2_copy.Add(self.label_6, 0, 0, 0)
        grid_sizer_2_copy.Add(self.combo_serial_baud, 0, 0, 0)
        grid_sizer_2.Add(grid_sizer_2_copy, 1, wx.EXPAND, 0)
        grid_sizer_2.Add(self.toggle_serial_connect, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_4.Add(grid_sizer_2, 1, wx.EXPAND, 0)
        grid_sizer_4.Add(self.label_1_copy_2, 0, 0, 0)
        grid_sizer_4.Add(self.label_1, 0, 0, 0)
        grid_sizer_4.Add(self.label_1_copy_1, 0, 0, 0)
        self.panel_1.SetSizer(grid_sizer_4)
        grid_sizer_5.Add(self.window_2, 1, wx.EXPAND, 0)
        grid_sizer_5.Add(self.notebook_2, 1, wx.EXPAND, 0)
        grid_sizer_6.Add(self.window_1, 1, wx.EXPAND, 0)
        grid_sizer_7.Add(self.window_3, 1, wx.EXPAND, 0)
        #grid_sizer_7.Add(self.window_0, 1, wx.EXPAND, 0)
        #grid_sizer_7.Add(self.window_01, 1, wx.EXPAND, 0)
        self.notebook_1_pane_2.SetSizer(grid_sizer_5)
        self.notebook_2_pane_1.SetSizer(grid_sizer_6)
        self.notebook_2_pane_3.SetSizer(grid_sizer_7)
        #self.notebook_2_pane_2.SetSizer(grid_sizer_7)
        grid_sizer_5.AddGrowableRow(0)
        grid_sizer_5.AddGrowableRow(1)
        grid_sizer_5.AddGrowableCol(0)
        self.notebook_1.AddPage(self.panel_1, "Main")
        self.notebook_1.AddPage(self.notebook_1_pane_2, "Motors")
        self.notebook_2.AddPage(self.notebook_2_pane_1, "Data")
        self.notebook_2.AddPage(self.notebook_2_pane_2, "Vars")
        self.notebook_2.AddPage(self.notebook_2_pane_3, "Angles")
        self.notebook_1.AddPage(self.notebook_1_pane_3, "Inertial")
        self.notebook_1.AddPage(self.notebook_1_pane_4, "Control")
        grid_sizer_3.Add(self.notebook_1, 1, wx.EXPAND, 0)
        self.SetSizer(grid_sizer_3)
        grid_sizer_3.AddGrowableRow(1)
        grid_sizer_3.AddGrowableCol(1)
        self.Layout()
        # end wxGlade

    def OnPortConnect(self, event): # wxGlade: MyFrame.<event_handler>
        print "Event handler `OnPortConnect' not implemented!"
        event.Skip()

# end of class MyFrame


if __name__ == "__main__":
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    main_frame = MyFrame(None, -1, "")
    app.SetTopWindow(main_frame)
    main_frame.Show()
    app.MainLoop()

try:
        raise KeyboardInterrupt
finally:
        print 'Goodbye, world!'
        cleanup()
