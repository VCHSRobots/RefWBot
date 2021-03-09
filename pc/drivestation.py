# drivestation.py -- Drive Station Program for Reference Water Bot
# Epic Robotz, dlb, Mar 2021

import sys
import tkinter as tk
import tkinter.font as tkFont
import mqttrobot
import gameclockwidget
import joystickwidget
import hardwarestatuswidget
import commstatuswidget
import dscolors
import joystick
import threading
import time
from utils import *

title = "EPIC ROBOTZ"
teamname = "Reference Bot"
wx, wy = 300, 750

class DriveStation(tk.Frame):

    def __init__(self, parent, enable_mqtt=True):
        tk.Frame.__init__(self, parent)
        
        # Hardware setup
        self.setup_mqtt(enable_mqtt)
        self.bot_status0 = self.bot_status1 = ("", 0)  # Last two bot status msg
        self.joystick_device = joystick.Joystick(style="Logitech 3D")
        # self.joystick_device = joystick.Joystick(style="Noname Gamepad")
        self.ping_setup()
        self.last_cmd_send_time = time.monotonic() - 100.0
        self.run_loop_cnt = 0

        # GUI setup
        self.titlefont = tkFont.Font(family="Copperplate Gothic Bold", size=24)
        self.namefont = tkFont.Font(family="Copperplate Gothic Light", size=20)
        self.titlelabel = tk.Label(self, text=title, anchor="center", font=self.titlefont)
        self.namelabel = tk.Label(self, text=teamname, anchor="center", font=self.namefont)
        self.hwstatus = hardwarestatuswidget.HardwareStatusWidget(self)
        self.gameclock = gameclockwidget.GameClockWidget(self)
        self.joystick_ui = joystickwidget.JoystickWidget(self)
        self.commstatus = commstatuswidget.CommStatusWidget(self)

        # Layout, do it manually to get exactly what we want.
        y = 5
        self.titlelabel.place(x=0, y=y, width=wx, height=30)
        y += 30
        self.namelabel.place(x=0, y=y, width=wx, height=30)
        y += 40
        w, h = self.hwstatus.get_size()
        x = int((wx-w)/2)  # Use size of hwstatus to establish x margin for all widgets
        self.hwstatus.place(x=x, y=y, width=w, height=h)
        y += h + 10
        w, h = self.gameclock.get_size()
        self.gameclock.place(x=x, y=y, width=w, height=h)
        y += h + 10
        w, h = self.joystick_ui.get_size()
        self.joystick_ui.place(x=x, y=y, width=w, height=h)
        y += h + 10
        w, h = self.commstatus.get_size()
        self.commstatus.place(x=x, y=y, width=w, height=h)  
        y += h + 10

        self.quitbackgroundtasks = False
        self.bg_count = 0
        self.last_btns = []
        self.last_xyz = []
        self.last_ruv = []

        # Do this once here to avoid stupid updates in the background loop
        if self.mqtt == None:
            self.commstatus.set_field("Status", "Disabled")
            self.commstatus.set_field("Msg Tx", "0")
            self.commstatus.set_field("Msg Rx", "0")
            self.commstatus.set_field("Ping", "--- ms")
            self.commstatus.set_field("Lst Msg", "-- sec")
            self.commstatus.set_field("Errors", "0")  
            self.hwstatus.set_status("Comm", "red")

    def setup_mqtt(self, enable):
      ''' Do the setup for MQTT. '''
      if not enable: 
        self.mqtt = None
        return
      self.mqtt = mqttrobot.MqttRobot()
      time.sleep(0.1)  # Found by experimenting!  Must have a delay here.
      self.mqtt.register_topic("wbot/status", self.on_bot_status)

    def ping_setup(self):
        ''' Sets up the variables for the ping test. '''
        self.ping_time_of_last_test = 0
        self.ping_count = 0
        self.ping_last_data = ""
        self.ping_last_timestamp = 0
        self.ping_inflight = False
        self.ping_report = "---"
        self.ping_rec_cnt = 0
        self.ping_err_cnt = 0
        self.ping_last_complete_time = 0
        if self.mqtt:
          self.mqtt.register_topic("wbot/pingds", self.on_ping)

    def ping_test(self):
        ''' Conducts the background ping test once per second. '''
        timenow = time.monotonic()
        if timenow - self.ping_time_of_last_test < 1.0: return
        if self.ping_inflight:
          if timenow - self.ping_time_of_last_test > 5.0:
            self.ping_err_cnt += 1
            self.ping_inflight = False
        if self.ping_inflight: return 
        self.ping_time_of_last_test = timenow
        self.ping_count += 1
        self.ping_last_data = "%06d" % self.ping_count
        self.ping_last_timestamp = timenow
        self.ping_inflight = True
        self.mqtt.publish("wbot/pingbot", self.ping_last_data)

    def on_ping(self, topic, data):
      self.ping_last_complete_time = time.monotonic()
      self.ping_rec_cnt += 1
      if data != self.ping_last_data: return
      if not self.ping_inflight: return
      delay = time.monotonic() - self.ping_last_timestamp
      self.ping_inflight = False 
      ms = int(delay * 1000)
      if ms < 999:
        self.ping_report = "%d ms" % ms
      elif ms < 99999:
        sec = int(ms / 1000)
        self.ping_report = "%d secs" % sec 
      else:
        self.ping_report = ">99 secs"

    def on_bot_status(self, topic, data):
      self.bot_status0 = self.bot_status1
      self.bot_status1 = data, time.monotonic()

    def monitor_mqtt(self):
        ''' Monitors activity of mqtt, and reports it to the ui. '''
        if self.mqtt == None: return
        if self.mqtt.is_connected():
          self.ping_test()
          self.hwstatus.set_status("Comm", dscolors.status_okay)
          self.commstatus.set_field("Status", "Connected")
        else:
          self.hwstatus.set_status("Comm", "red")
          self.commstatus.set_field("Status", "Comm Err")
        counts = self.mqtt.get_counts()
        mt = int(self.mqtt.time_since_last_rx() * 1000)
        if mt < 999:
          smt = "%d ms" % mt
        else:
          mt = int(mt / 1000)
          if mt > 999: mt = 999
          smt = "%d sec" % mt
        if counts["rx"] <= 0: smt= '---'
        spr = self.ping_report 
        if time.monotonic() - self.ping_last_complete_time > 4.0: spr = "---"
        self.commstatus.set_field("Msg Tx", "%d" % counts["tx"])
        self.commstatus.set_field("Msg Rx", "%d" % counts["rx"])
        self.commstatus.set_field("Ping", spr)
        self.commstatus.set_field("Lst Msg", smt)
        self.commstatus.set_field("Errors", "%d" % counts["err"])

    def monitor_botstatus(self):
      d0, t0 = self.bot_status0
      d1, t1 = self.bot_status1
      try:
        s0 = d0.split()[0]
        s1 = d1.split()[0]
      except: 
        s0 = s1 = ""
      if s0 != "okay" or s1 != "okay":
        self.hwstatus.set_status("Code", dscolors.status_error)
        return
      timenow = time.monotonic()
      if timenow - t0 > 10.0 or timenow - t1 > 9.0:
        self.hwstatus.set_status("Code", dscolors.status_error)
        return
      if timenow - t0 > 3.0 or timenow - t1 > 2.5:
        self.hwstatus.set_status("Code", dscolors.status_warn)
        return
      self.hwstatus.set_status("Code", dscolors.status_okay)

    def send_loop_cmd(self):
      ''' Sends loop command to bot if we have mqtt.  Send the
      loop command once every 0.5 seconds. '''
      if not self.mqtt: return
      timenow = time.monotonic()
      if timenow - self.last_cmd_send_time < 0.50: return
      self.last_cmd_send_time = timenow 
      cmdstr, tme_to_go = self.gameclock.get_botcmd()
      s = ("%s %d %7.2f" % (cmdstr, self.run_loop_cnt, tme_to_go))
      self.mqtt.publish("wbot/mode", s)
      
    def background_run(self):
        ''' Runs in the background, doing the main activity: sending
        joystick inputs to the pi, and keeping the ui up to date. '''
        while True:
            self.run_loop_cnt += 1
            self.monitor_mqtt()
            self.monitor_botstatus()
            btns = self.joystick_device.get_buttons()
            xyz = self.joystick_device.get_axis()
            ruv = self.joystick_device.get_ruv()
            haveconnection = self.joystick_device.is_connected()
            if haveconnection: 
                self.joystick_ui.set_mode('active')
                self.hwstatus.set_status("Joystick", dscolors.status_okay)
            else: 
                self.joystick_ui.set_mode('invalid')
                self.hwstatus.set_status("Joystick", dscolors.status_error)
            self.joystick_ui.set_axis(*xyz)
            self.joystick_ui.set_ruv(*ruv)
            self.joystick_ui.set_buttons(*btns)
            if self.mqtt:
                self.send_loop_cmd()
                # send out joystick values to robot here...
                if self.last_btns != btns:
                    self.last_btns = btns
                    s = ""
                    for i in btns:
                        if i: s += "T " 
                        else: s += "F "
                    self.mqtt.publish("wbot/joystick/buttons", s)
                    #print("Publishing Buttons = %s" % s)
                if not same_in_tolerance(xyz, self.last_xyz):
                    self.last_xyz = xyz
                    s = "%7.4f %7.4f %7.4f" % tuple(xyz)
                    self.mqtt.publish("wbot/joystick/xyz", s)
                    #print("Publishing xyz = %s" % s)
                if not same_in_tolerance(ruv, self.last_ruv):
                    self.last_ruv = ruv
                    s = "%7.4f %7.4f %7.4f" % tuple(ruv)
                    #Off due to broken input...
                    #self.mqtt.publish("wbot/joystick/ruv", s)
                    #print("Publishing ruv = %s " %s )
            self.bg_count += 1
            # if self.bg_count % 100 == 0: print("Background Loop: %d." % self.bg_count)
            if self.quitbackgroundtasks: 
              print("Quitting the joystick thread.")
              return
            time.sleep(0.050)
    
    def start_background(self):
        self.bgid = threading.Thread(target=self.background_run, name="background-joystick")
        self.bgid.daemon = True  # KLUGH -- Should not need this!  Bug in the shutdown code for this program.
        self.bgid.start()

    def stop_all(self):
        self.quitbackgroundtasks = True
        if self.mqtt: 
            if self.mqtt.is_connected(): self.mqtt.close()

if __name__ == "__main__":
    enable_mqtt = True
    for a in sys.argv[1:]:
      if a == "nomqtt":
        print("MQTT disabled.")
        enable_mqtt = False

    root = tk.Tk()
    root.title("Driver Station for Water Bot")
    root.geometry("%dx%d" % (wx, wy))
    ds = DriveStation(root, enable_mqtt=enable_mqtt)
    ds.place(x=0, y=0, relwidth=1, relheight=1)
    ds.start_background()
    root.mainloop()
    ds.stop_all()
