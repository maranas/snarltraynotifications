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

# GUI imports
import wx
from wx import TaskBarIcon
from _winreg import CreateKey, SetValueEx, REG_DWORD, HKEY_CURRENT_USER

# TODO: Clean up you code! GUI code is too ingrained with the logic. (Coded in 4 hours as proof of concept).
# TODO: Option to disable Windows system tray balloons only when our app is on.

# Settings. Planning on making this available in a Preferences... dialog via pop-up menu
# For now, they're fixed at these values              
REFRESH_TIME = 10
NOTIFY_TIMEOUT = 20

TTS_BALLOON = 0x40
TTS_ALWAYSTIP = 0x01
TTM_POP = win32con.WM_USER + 28

class ddTaskBarIcon(TaskBarIcon):
  def set_system_notifier(self, on):
    value = 1
    if on:
      value = 0
    value_name = "EnableBalloonTips"
    subkey = "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
    key = CreateKey(HKEY_CURRENT_USER, subkey)
    SetValueEx(key, value_name, 0, REG_DWORD, value)

  def __init__(self, icon, tooltip, frame, app):
    TaskBarIcon.__init__(self)
    self.app = app
    self.SetIcon(icon, tooltip)
    self.frame = frame
    self.quitting = False
    threading.Thread(target=self.notifier_loop).start()
	
  def notify_snarl(self, buff_str, title):
    # Title not supported yet
	# Icon path:
    icon_path = os.path.join(os.getcwd(), "icon.ico")
    title = 'Notification'
    if PySnarl.snGetVersion() != False:
      id = PySnarl.snShowMessage("Notification", buff_str, timeout=NOTIFY_TIMEOUT, iconPath=icon_path)
	      
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
          title = win32gui.GetWindowText(wnd).lstrip().rstrip().lstrip('\x00').rstrip('\x00')
          if buff_str:
            if wnd not in message_list.keys():
              message_list[wnd] = buff_str
              win32gui.SendMessage(wnd, TTM_POP , 0, 0)
              self.notify_snarl(buff_str, title)
            else:
              if buff_str == message_list[wnd]:
                # don't print it. Wait for next refresh.
                pass
              else:
                message_list[wnd] = buff_str
                win32gui.SendMessage(wnd, TTM_POP , 0, 0)
                self.notify_snarl(buff_str, title)
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
    
  def CreatePopupMenu(self):
    self.popupmenu = wx.Menu()
    about_item = self.popupmenu.Append(-1, "About Snarl Tray Notifications")
    self.popupmenu.AppendSeparator()
    quit_item = self.popupmenu.Append(-1, "Quit")
    self.Bind(wx.EVT_MENU, self.OnQuit, quit_item)
    self.Bind(wx.EVT_MENU, self.OnAbout, about_item)
    return self.popupmenu
	
app = wx.App()
frame = wx.Frame(None, -1, 'Snarl Tray Notifications')
iconFile = "icon.ico"
icon_handle = wx.Icon(iconFile, wx.BITMAP_TYPE_ICO)
app.trayicon = ddTaskBarIcon(icon_handle, "Snarl Tray Notifications", frame, app)
app.MainLoop()