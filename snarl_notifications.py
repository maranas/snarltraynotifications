import win32con
import win32gui
import win32api
import win32process
import struct
import array
import time
import threading
import PySnarl
import os
import commctrl

# GUI imports
import wx
from wx import TaskBarIcon

# TODO: Clean up you code! GUI code is too ingrained with the logic. (Coded in 4 hours as proof of concept).
# TODO: Option to disable Windows system tray balloons only when our app is on.

# Settings. Planning on making this available in a Preferences... dialog via pop-up menu
# For now, they're fixed at these values              
REFRESH_TIME = 10
NOTIFY_TIMEOUT = 20

TTS_BALLOON = 0x40
TTS_ALWAYSTIP = 0x01
TTM_POP = win32con.WM_USER + 28
TTM_GETTITLE = win32con.WM_USER + 35

# Preference dialog class
class PrefDialog(wx.Dialog):
  def __init__(self):
    wx.Dialog.__init__(self, None, -1, "Preferences", size=(330,150))

    panel = wx.Panel(self, -1)
    vbox = wx.BoxSizer(wx.VERTICAL)

    timeout_box = wx.BoxSizer(wx.HORIZONTAL)
    st_text = wx.StaticText(self, -1, label="Display timeout (seconds):")
    self.tb_timeout = wx.TextCtrl(self, -1, str(NOTIFY_TIMEOUT))
    timeout_box.AddSpacer((10,10))
    timeout_box.Add(st_text, 1)
    timeout_box.Add(self.tb_timeout, 1, wx.LEFT, 5)
    
    cache_box = wx.BoxSizer(wx.HORIZONTAL)
    st2_text = wx.StaticText(self, -1, "Cache refresh time (seconds):")
    self.tb_cache = wx.TextCtrl(self, -1, str(REFRESH_TIME))
    cache_box.AddSpacer((10,10))
    cache_box.Add(st2_text, 1)
    cache_box.Add(self.tb_cache, 1, wx.LEFT, 5)

    hbox = wx.BoxSizer(wx.HORIZONTAL)
    okButton = wx.Button(self, -1, 'OK', size=(70, 30))
    closeButton = wx.Button(self, -1, 'Cancel', size=(70, 30))
    hbox.Add(okButton, 1)
    hbox.Add(closeButton, 1, wx.LEFT, 5)

    vbox.AddSpacer((10,10))
    vbox.Add(timeout_box)
    vbox.AddSpacer((10,10))
    vbox.Add(cache_box)
    vbox.AddSpacer((10,10))
    vbox.Add(hbox, 1, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 10)

    self.SetSizer(vbox)
    self.Bind(wx.EVT_BUTTON, self.OnOk, okButton)
    self.Bind(wx.EVT_BUTTON, self.OnCancel, closeButton)
    
  def OnOk(self, e):
    global NOTIFY_TIMEOUT, REFRESH_TIME
    timeout_value = self.tb_timeout.GetValue()
    refresh_value = self.tb_cache.GetValue()
    err = 0
    if timeout_value.isdigit():
      if int(timeout_value) > 0:
        NOTIFY_TIMEOUT = int(timeout_value)
    else:
      err = 1
    if refresh_value.isdigit():
      if int(refresh_value) > 0:
        REFRESH_TIME = int(refresh_value)
    else:
      err = 1
    if err != 0:
      wx.MessageBox("You entered invalid values. The changes won't be saved", "Error")
    self.Close()
  
  def OnCancel(self, e):
    self.Close()

class ddTaskBarIcon(TaskBarIcon):
#  def set_system_notifier(self, on):
#    value = 1
#    if on:
#      value = 0
#    value_name = "EnableBalloonTips"
#    subkey = "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
#    key = CreateKey(HKEY_CURRENT_USER, subkey)
#    SetValueEx(key, value_name, 0, REG_DWORD, value)

  def __init__(self, icon, tooltip, frame, app):
    TaskBarIcon.__init__(self)
    self.app = app
    self.SetIcon(icon, tooltip)
    self.frame = frame
    self.quitting = False
    threading.Thread(target=self.notifier_loop).start()
	
  def notify_snarl(self, buff_str, title, wnd):
    # Title not supported yet
	  # Icon path:
    icon_path = os.path.join(os.getcwd(), "icon.ico")
    title = 'Notification'
    if PySnarl.snGetVersion() != False:
      id = PySnarl.snShowMessage("Notification", buff_str, timeout=NOTIFY_TIMEOUT, iconPath=icon_path,
	                             replyWindow=wnd, replyMsg=win32con.WM_LBUTTONDOWN) # This isn't working; try TTM_RELAYEVENT
	      
  def notifier_loop(self):
    counter = 0
    message_list = {}
    while not self.quitting:
      lTaskBar = win32gui.FindWindowEx(0, 0, 'Shell_TrayWnd', None)
  
      thread, pidTaskBar = win32process.GetWindowThreadProcessId(lTaskBar)
  
      wnd = win32gui.FindWindowEx(0, 0, 'tooltips_class32', None)
      while wnd:
        thread, pidWnd = win32process.GetWindowThreadProcessId(wnd)
        if pidTaskBar == pidWnd:
          window_long = win32api.GetWindowLong(wnd, win32con.GWL_STYLE)
          if (window_long & TTS_BALLOON) == 0 or (window_long & TTS_ALWAYSTIP) == 0:
            break
          len = win32gui.SendMessage(wnd, win32con.WM_GETTEXTLENGTH, 0, 0)
          buff = array.array('c', '')
          for x in xrange(len + 1):
            buff.append(' ')
          buff_info = buff.buffer_info()
          addrText = buff_info[0]
          win32gui.SendMessage(wnd, win32con.WM_GETTEXT, buff_info[1], buff_info[0])
          buff_str =  buff.tostring().lstrip().rstrip().lstrip('\x00').rstrip('\x00')
          title = "Notification"

          if buff_str:
            if wnd not in message_list.keys():
              message_list[wnd] = buff_str
              win32gui.SendMessage(wnd, TTM_POP , 0, 0)
              self.notify_snarl(buff_str, title, wnd)
            else:
              if buff_str == message_list[wnd]:
                # don't print it. Wait for next refresh.
                pass
              else:
                message_list[wnd] = buff_str
                win32gui.SendMessage(wnd, TTM_POP , 0, 0)
                self.notify_snarl(buff_str, title, wnd)
        wnd = win32gui.FindWindowEx(0, wnd, 'tooltips_class32', None)
      time.sleep(0.01)
      counter = counter + 0.01
      if counter >= REFRESH_TIME:
        counter = 0
        # Time to reset the message cache
        for key in message_list.keys():
          del message_list[key]
	  
  def OnQuit(self, e):
    self.quitting = True
    self.RemoveIcon()
    app.Exit()

  def OnAbout(self, e):
    description = """Snarl Tray Notifications is a companion app to Snarl, the Growl-like notification
system for Windows. It captures notification messages from all of your system
tray apps, and re-displays the notifications using Snarl's better-looking pop-up           
balloons.

Also uses PySnarl (http://www.fullphat.net/snarl)
Copyright 2006-2008 Samuel Listopad II
Licensed under the Apache License, Version 2.0 (the "License"); you may not
use this file except in compliance with the License. You may obtain a copy
of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required
by applicable law or agreed to in writing, software distributed under the
License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS
OF ANY KIND, either express or implied. See the License for the specific
language governing permissions and limitations under the License.
"""

    licence = """The MIT License

Copyright (c) 2010 Moises Aranas

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE."""


    info = wx.AboutDialogInfo()

    info.SetIcon(wx.Icon(iconFile, wx.BITMAP_TYPE_ICO))
    info.SetName('Snarl Tray Notifications')
    info.SetVersion('0.5')
    info.SetDescription(description)
    info.SetCopyright('Copyright (c) 2010 Moises Aranas')
    info.SetWebSite('http://code.google.com/p/snarltraynotifications/')
    info.SetLicence(licence)
    info.AddDeveloper('Coding by Moises Aranas')
    info.AddArtist('Application icon by Olivier Charavel (http://sekkyumu.deviantart.com)')

    wx.AboutBox(info)
    
  def OnPref(self, e):
    pref_dialog = PrefDialog()
    pref_dialog.ShowModal()
    pref_dialog.Destroy()
    
  def CreatePopupMenu(self):
    self.popupmenu = wx.Menu()
    about_item = self.popupmenu.Append(-1, "About Snarl Tray Notifications")
    preferences_item = self.popupmenu.Append(-1, "Preferences...")
    self.popupmenu.AppendSeparator()
    quit_item = self.popupmenu.Append(-1, "Quit")
    self.Bind(wx.EVT_MENU, self.OnQuit, quit_item)
    self.Bind(wx.EVT_MENU, self.OnAbout, about_item)
    self.Bind(wx.EVT_MENU, self.OnPref, preferences_item)
    return self.popupmenu
	
app = wx.App(False, filename="log.txt")
frame = wx.Frame(None, -1, 'Snarl Tray Notifications')
iconFile = "icon.ico"
icon_handle = wx.Icon(iconFile, wx.BITMAP_TYPE_ICO)
app.trayicon = ddTaskBarIcon(icon_handle, "Snarl Tray Notifications", frame, app)
if not os.path.exists("settings.txt"):
  settings = open("settings.txt", "w")
  settings.write(str(REFRESH_TIME) + "\n")
  settings.write(str(NOTIFY_TIMEOUT) + "\n")
  settings.close()
print "Loading settings"
settings = open("settings.txt", "r")
r_t = settings.readline().rstrip().lstrip()
if r_t.isdigit():
  REFRESH_TIME = int(r_t)
n_t = settings.readline().rstrip().lstrip()
if n_t.isdigit():
  NOTIFY_TIMEOUT = int(n_t)
settings.close()

app.MainLoop()
print "Saving settings"
settings = open("settings.txt", "w")
settings.write(str(REFRESH_TIME) + "\n")
settings.write(str(NOTIFY_TIMEOUT) + "\n")
settings.close()
