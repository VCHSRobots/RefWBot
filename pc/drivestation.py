# drivestation.py -- Drive Station Program for Reference Water Bot
# Epic Robotz, dlb, Mar 2021
#
# Version 1.0: Fully working with one or two joystick/gamepad inputs.
# Version 1.1: Revamped joystick driver code
#
# NOTE: This version supports ONE or TWO joysticks/gamepad inputs.
# The widget layout changes accordingly.  With one joystick, the layout
# is fully vertical, but with two, the layout has left and right
# widgets.

# -- System imports...
import sys
import configparser
import tkinter as tk
import tkinter.font as tkFont
import threading
import time

# -- Our imports...
import joystick
import mqttrobot
import gameclockwidget
import joystickwidget_logitech as joystick_logitech
import joystickwidget_xbox as joystick_xbox
import hardwarestatuswidget
import commstatuswidget
import botstatuswidget
import arduinostatuswidget
import arduino_decode as adec
import dscolors
from utils import *

LOGITECH = "Logitech 3D Pro"
XBOX = "XBox Gamepad"
winsize_1_joystick = (270, 860)
winsize_2_joystick = (530, 610)
winsize = winsize_1_joystick  # Default

class DSConfiguration():
  def __init__(self):
    parser = configparser.ConfigParser()
    parser["Robot"] = {"TeamName": "EPIC RefBot"}
    try:
      parser.read("dsconfig.txt")
      self.teamname = parser["Robot"]["TeamName"]
      self.title = parser["Robot"].get("Title", "EPIC Robotz")
      self.teamname = parser["Robot"].get("TeamName", "Ref Bot")
      self.bat_logic_warning = parser["Robot"].getfloat("LogicBatteryWarning", 9.75)
      self.bat_logic_error = parser["Robot"].getfloat("LogicBatteryError", 9.0)
      self.bat_motor_warning = parser["Robot"].getfloat("MotorBatteryWarning", 9.75)
      self.bat_motor_error = parser["Robot"].getfloat("MotorBatteryError", 9.0)
      self.number_of_joysticks = parser["Robot"].getint("NumberOfJoysticks", 1)
      self.joystick_port_1 = parser["Robot"].get("JoystickPort1", "Logitech")
      self.joystick_port_2 = parser["Robot"].get("JoystickPort2", "XBox")
    except Exception as e:
      print("Error in configuration file.")
      print(e)
      sys.exit()

class DriveStation(tk.Frame):
    def __init__(self, parent, config, enable_mqtt=True):
        tk.Frame.__init__(self, parent)
        self.config = config

         # Setup the Comm and Joysticks
        self.setup_mqtt(enable_mqtt)
        self.bot_status0 = self.bot_status1 = ("", 0)  # Last two bot status msg
        # Get joystick devices
        self.joysticks = []
        if self.config.number_of_joysticks < 1 or self.config.number_of_joysticks > 2:
          print("Invalid number of joysticks (%d). Only 1 or 2 allowed." % self.config.number_of_joysticks)
          print("Please fix configuration file.")
          sys.exit()
        if self.config.joystick_port_1 == "Logitech":
          self.joysticks.append(joystick.Joystick(LOGITECH, 0))
        elif self.config.joystick_port_1 == "XBox":
          self.joysticks.append(joystick.Joystick(XBOX, 0))
        else:
          print("Invalid joystick on port 1 (%s). Valid joysticks are: Logitech or XBox." % 
            self.config.joystick_port_1)
          print("Please fix configuration file.")
          sys.exit()
        if self.config.number_of_joysticks == 2:
          if self.config.joystick_port_2 == "Logitech":
            instance = 0
            if self.config.joystick_port_1 == "Logitech": instance = 1
            self.joysticks.append(joystick.Joystick(LOGITECH, instance))
          elif self.config.joystick_port_2 == "XBox":
            instance = 0
            if self.config.joystick_port_1 == "XBox": instance = 1
            self.joysticks.append(joystick.Joystick(XBOX, instance))
          else:
            print("Invalid joystick on port 2 (%s). Valid joysticks are: Logitech or XBox." % 
              self.config.joystick_port_2)
            print("Please fix configuration file.")
            sys.exit()
        
        # Setup runtime variables...
        self.ping_setup()
        self.last_cmd_send_time = time.monotonic() - 100.0
        self.last_arduino_status = time.monotonic() - 100.0
        self.last_arduino_ui_update = time.monotonic() - 100.0
        self.arduino_data = None
        self.arduino_reset_flag = False
        self.run_loop_cnt = 0
        self.quitbackgroundtasks = False
        self.bg_count = 0
        self.last_btns = [[], []]
        self.last_axes = [[], []]
        self.last_pov = [(0, 0), (0,0)]
        
        # Setup the GUI...
        self.titlefont = tkFont.Font(family="Copperplate Gothic Bold", size=24)
        self.namefont = tkFont.Font(family="Copperplate Gothic Light", size=20)
        self.titlelabel = tk.Label(self, text=self.config.title, anchor="center", font=self.titlefont)
        self.namelabel = tk.Label(self, text=self.config.teamname, anchor="center", font=self.namefont)
        self.hwstatus = hardwarestatuswidget.HardwareStatusWidget(self)
        self.gameclock = gameclockwidget.GameClockWidget(self)
        self.commstatus = commstatuswidget.CommStatusWidget(self)
        self.botstatus = botstatuswidget.BotStatusWidget(self, reset_callback=self.do_arduino_reset)
        self.arduinostatus = arduinostatuswidget.ArduinoStatusWidget(self)
        self.joystick_widgets = []
        for joy in self.joysticks:
          if joy.get_name() == LOGITECH:
            self.joystick_widgets.append(joystick_logitech.JoystickWidget(self))
          elif joy.get_name() == XBOX:
            self.joystick_widgets.append(joystick_xbox.JoystickWidget(self))
          else:
            print("Unknown joystick detected. Defaulting to Logitech widget.")
            self.joystick_widgets.append(joystick_logitech.JoystickWidget(self))
        if len(self.joystick_widgets) < 1:
          raise("Internal Consistancy Check Error.  Programming Problem.")
        if self.config.number_of_joysticks == 1:
          self.layout_for_one_joystick()
        elif self.config.number_of_joysticks == 2:
          self.layout_for_two_joysticks()
        else:
          print("Invalid Number of Joysticks!  Fix configuration file.")
          sys.exit()
        self.set_mqtt_fields_off() 


    def layout_for_one_joystick(self):
        ''' Do the layout for one joystick '''
        wx, _ = winsize
        xpad = 10 # This is the padding on the left
        y = 5
        self.titlelabel.place(x=0, y=y, width=wx, height=30)
        y += 30
        self.namelabel.place(x=0, y=y, width=wx, height=30)
        y += 40
        w, h = self.hwstatus.get_size()
        x = xpad 
        self.hwstatus.place(x=x, y=y, width=w, height=h)
        y += h + 10
        w, h = self.gameclock.get_size()
        self.gameclock.place(x=x, y=y, width=w, height=h)
        y += h + 10
        joystk = self.joystick_widgets[0]
        w, h = joystk.get_size()
        joystk.place(x=x, y=y, width=w, height=h)
        y += h + 10
        w, h = self.commstatus.get_size()
        self.commstatus.place(x=x, y=y, width=w, height=h)  
        x2 = x + w + 5
        w2, h2 = self.botstatus.get_size()
        self.botstatus.place(x=x2, y=y, width=w2, height=h2)
        if h2 > h: y += h2 + 10
        else: y += h + 10
        w, h = self.arduinostatus.get_size()
        self.arduinostatus.place(x=x, y=y, width=w, height=h)
  
    def layout_for_two_joysticks(self):
        ''' Do the layout for two joysticks '''
        wx, wy = winsize
        xpad = 10 # This is the padding on the left
        y = 5
        self.titlelabel.place(x=0, y=y, width=wx, height=30)
        y += 30
        self.namelabel.place(x=0, y=y, width=wx, height=30)
        y += 40
        x = xpad 
        w, h1 = self.gameclock.get_size()
        self.gameclock.place(x=x, y=y, width=w, height=h1)
        x1 = x + w + xpad
        w, h2 = self.hwstatus.get_size()
        self.hwstatus.place(x=x1, y=y, width=w, height=h2)
        h = max(h1, h2)
        y += h + 10
        joystk0 = self.joystick_widgets[0]
        joystk1 = self.joystick_widgets[1]
        w, h = joystk0.get_size()
        w1, h1 = joystk1.get_size() 
        joystk0.place(x=x, y=y, width=w, height=h)
        x1 = x + w + xpad 
        joystk1.place(x=x1, y=y, width=w1, height=h1)
        if h < h1: h = h1
        y += h + 10
        w, h = self.commstatus.get_size()
        self.commstatus.place(x=x, y=y, width=w, height=h)  
        x2 = x + w + 5
        w2, h2 = self.botstatus.get_size()
        self.botstatus.place(x=x2, y=y, width=w2, height=h2)
        x3 = x2 + w2 + xpad
        w, h = self.arduinostatus.get_size()
        self.arduinostatus.place(x=x3, y=y, width=w, height=h)

    def set_mqtt_fields_off(self):
        # Do this once here to avoid stupid updates in the background loop
        if self.mqtt == None:
            self.commstatus.set_field("Status", "Disabled")
            self.commstatus.set_field("Msg Tx", "0")
            self.commstatus.set_field("Msg Rx", "0")
            self.commstatus.set_field("Ping", "--- ms")
            self.commstatus.set_field("Lst Msg", "-- sec")
            self.commstatus.set_field("Errors", "0")  
            self.hwstatus.set_status("Comm", "red")
            self.botstatus.set_field("Bat1", "---")
            self.botstatus.set_field("Bat2", "---")
            self.botstatus.set_field("I2CErrs", "---")
            self.botstatus.set_field("Recovers", "---")
            self.botstatus.set_field("CodeVer", "---")

    def setup_mqtt(self, enable):
      ''' Do the setup for MQTT. '''
      if not enable: 
        self.mqtt = None
        return
      self.mqtt = mqttrobot.MqttRobot()
      self.mqtt.register_topic("wbot/status", self.on_bot_status)
      self.mqtt.register_topic("wbot/arduino", self.on_arduino_data)

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

    def on_arduino_data(self, topic, data):
      self.last_arduino_status = time.monotonic() 
      self.arduino_data = data
    
    def do_arduino_reset(self):
      self.arduino_reset_flag = True
      
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
      if (s0 != "okay" and s0 != "code_err") or (s1 != "okay" and s1 != "code_err"):
        self.hwstatus.set_status("Code", dscolors.status_error)    
        self.hwstatus.set_status("I2C Bus", dscolors.indicator_bg)
        self.hwstatus.set_status("Bat M", dscolors.indicator_bg)
        self.hwstatus.set_status("Bat L", dscolors.indicator_bg)
        self.botstatus.set_field("Bat1", "---")
        self.botstatus.set_field("Bat2", "---")
        self.botstatus.set_field("I2CErrs", "---")
        self.botstatus.set_field("Recovers", "---")
        self.botstatus.set_field("CodeVer",  "---")
        return
      timenow = time.monotonic()
      if timenow - t0 > 10.0 or timenow - t1 > 9.0:
        self.hwstatus.set_status("Code", dscolors.status_error)
        self.hwstatus.set_status("I2C Bus", dscolors.indicator_bg)
        self.hwstatus.set_status("Bat M", dscolors.indicator_bg)
        self.hwstatus.set_status("Bat L", dscolors.indicator_bg)
        self.botstatus.set_field("Bat1", "---")
        self.botstatus.set_field("Bat2", "---")
        self.botstatus.set_field("I2CErrs", "---")
        self.botstatus.set_field("Recovers", "---")
        self.botstatus.set_field("CodeVer",  "---")
        return
      elif timenow - t0 > 4.0 or timenow - t1 > 3.0:
        self.hwstatus.set_status("Code", dscolors.status_warn)
      else:
        if s0 == "code_err" or s1 == "code_err":
          self.hwstatus.set_status("Code", dscolors.status_warn)
        else:
          self.hwstatus.set_status("Code", dscolors.status_okay)
      words = d1.split()
      if len(words) < 7:
        self.hwstatus.set_status("I2C Bus", dscolors.status_error)
        self.hwstatus.set_status("Bat M", dscolors.status_error)
        self.hwstatus.set_status("Bat L", dscolors.status_error)
        self.botstatus.set_field("Bat M", "---")
        self.botstatus.set_field("Bat L", "---")
        self.botstatus.set_field("I2CErrs", "---")
        self.botstatus.set_field("Recovers", "---")
        self.botstatus.set_field("CodeVer",  "---")
        return
      bat_m = bat_l = 0.0
      try:
        bat_m = float(words[3])
        bat_l = float(words[4])
      except ValueError:
        bat_m = bat_l = 0.0 
      try: 
        i2cerrs = int(words[5])
      except ValueError:
        i2cerrs = -1
      try: 
        recovers = int(words[6])
      except ValueError:
        recovers = -1
      if bat_m > self.config.bat_motor_warning: 
        self.hwstatus.set_status("Bat M", dscolors.status_okay)
      elif bat_m > self.config.bat_motor_error:
        self.hwstatus.set_status("Bat M", dscolors.status_warn)
      else:
        self.hwstatus.set_status("Bat M", dscolors.status_error)
      if bat_l > self.config.bat_logic_warning: 
        self.hwstatus.set_status("Bat L", dscolors.status_okay)
      elif bat_l >  self.config.bat_logic_warning:
        self.hwstatus.set_status("Bat L", dscolors.status_warn)
      else:
        self.hwstatus.set_status("Bat L", dscolors.status_error)
      hwokay = str_to_bool(words[2])
      if not hwokay or i2cerrs > 15 or i2cerrs < 0:
        self.hwstatus.set_status("I2C Bus", dscolors.status_error)
      elif i2cerrs > 0:
        self.hwstatus.set_status("I2C Bus", dscolors.status_warn)
      else:
        self.hwstatus.set_status("I2C Bus", dscolors.status_okay)
      if i2cerrs == -1:
        self.botstatus.set_field("I2CErrs", "---")
      else:
        self.botstatus.set_field("I2CErrs", "%d" % i2cerrs)
      if recovers == -1:
        self.botstatus.set_field("Recovers", "---")
      else:
        self.botstatus.set_field("Recovers", "%d" % recovers)
      if len(words) >= 8:
        self.botstatus.set_field("CodeVer", words[7])
      else:
        self.botstatus.set_field("CodeVer", "---")

    def monitor_arduino(self):
      timenow = time.monotonic()
      if timenow - self.last_arduino_ui_update < 1.0: return
      self.last_arduino_ui_update = timenow
      if timenow - self.last_arduino_status > 4.0 or self.arduino_data == None:
        self.botstatus.set_field("Bat M", "---")
        self.botstatus.set_field("Bat L", "---")
        self.arduinostatus.set_all_fields("---")
        return
      d = adec.data_to_dict(self.arduino_data)
      if "BAT_M" in d:
        self.botstatus.set_field("Bat M", "%5.1f" % d["BAT_M"])
      else:
        self.botstatus.set_field("Bat M ", "---")
      if "BAT_L" in d:
        self.botstatus.set_field("Bat L", "%5.1f" % d["BAT_L"])
      else:
        self.botstatus.set_field("Bat L ", "---")
      if "SIGV" in d: 
        self.arduinostatus.set_field("Sigv", "%c" % d["SIGV"])
      else: 
        self.arduinostatus.set_field("Sigv", "---")
      if "DTME" in d:
        ft = d["DTME"] / 1000.0
        self.arduinostatus.set_field("Time", "%12.3f" % ft)
      else:
        self.arduinostatus.set_field("Time", "---")
      if "A1" in d and "A2" in d and "A3" in d and "A6" in d and "A7" in d:
        a = d["A1"], d["A2"], d["A3"], d["A6"], d["A7"]
        self.arduinostatus.set_field("Analog", "%5.2f %5.2f %5.2f %5.2f %5.2f" % a)
      else:
        self.arduinostatus.set_field("Analog", "---")
      if "SI" in d:
        bits = d["SI"]
        s = ""
        for i in range(6):
          if bits & (1 << (5 - i)) != 0: s += "T "
          else: s += "F "
        self.arduinostatus.set_field("Digital", s)
      else:
        self.arduinostatus.set_field("Digital", "---")
      if "PWM9" in d and "PWM10" in d and "PWM11" in d:
        dd = d["PWM9"], d["PWM10"], d["PWM11"]
        self.arduinostatus.set_field("PWM", "%5.2f %5.2f %5.2f" % dd)
      else:
        self.arduinostatus.set_field("PWM", "---")
      if "XXX0" in d and "XXX1" in d and "XXX2" in d:
        dd = d["XXX0"], d["XXX1"], d["XXX2"]
        self.arduinostatus.set_field("XXX", "%3d %3d %3d" % dd)
      else:
        self.arduinostatus.set_field("XXX", "---")

    def send_loop_cmd(self):
      ''' Sends loop command to bot if we have mqtt.  Send the
      loop command once every 0.5 seconds. '''
      if not self.mqtt: return
      timenow = time.monotonic()
      if timenow - self.last_cmd_send_time < 0.50 and not self.arduino_reset_flag: return
      self.last_cmd_send_time = timenow 
      cmdstr, tme_to_go = self.gameclock.get_botcmd()
      auxcmd = "NoOp"
      if self.arduino_reset_flag: auxcmd = "RestartArduino"
      self.arduino_reset_flag = False
      s = ("%s %d %7.2f %s" % (cmdstr, self.run_loop_cnt, tme_to_go, auxcmd))
      self.mqtt.publish("wbot/mode", s)
  
    def background_run(self):
        ''' Runs in the background, doing the main activity: sending
        joystick inputs to the pi, and keeping the ui up to date. '''
        while True:
            self.run_loop_cnt += 1
            self.monitor_mqtt()
            self.monitor_botstatus()
            self.monitor_arduino()
            joysticks_okay = True
            btns_list = []
            axes_list = []
            pov_list = []
            for ij in range(self.config.number_of_joysticks):
                btns = self.joysticks[ij].get_buttons()
                axes = self.joysticks[ij].get_axes()
                pov = self.joysticks[ij].get_pov()
                haveconnection = self.joysticks[ij].is_connected()
                if haveconnection: 
                    self.joystick_widgets[ij].set_mode('active')
                else: 
                    self.joystick_widgets[ij].set_mode('invalid')
                    joysticks_okay = False
                self.joystick_widgets[ij].set_axes(*axes)
                self.joystick_widgets[ij].set_buttons(*btns)
                self.joystick_widgets[ij].set_pov(pov)
                btns_list.append(btns)
                axes_list.append(axes)
                pov_list.append(pov)
            
            while len(btns_list) < 2:
              btns = [False for _ in range(12)]
              axes = [0.0 for _ in range(6)]
              pov = (0, 0)
              btns_list.append(btns)
              axes_list.append(axes)
              pov_list.append(pov)

            if joysticks_okay:
                self.hwstatus.set_status("Joystick", dscolors.status_okay)
            else:
                self.hwstatus.set_status("Joystick", dscolors.status_error)
            if self.mqtt:
                self.send_loop_cmd()
                # send out joystick values to robot here...
                for i in range(2):
                  btns = btns_list[i]
                  axes = axes_list[i]
                  pov = pov_list[i]
                  if btns != self.last_btns[i]:
                    self.last_btns[i] = btns
                    s = ""
                    for ib in btns:
                        if ib: s += "T " 
                        else: s += "F "
                    self.mqtt.publish("wbot/joystick%d/buttons" % i, s)
                  if not same_in_tolerance(axes, self.last_axes[i]):
                    self.last_axes[i] = axes
                    s = "%7.4f %7.4f %7.4f %7.4f %7.4f %7.4f" % tuple(axes)
                    self.mqtt.publish("wbot/joystick%d/axes" % i, s)
                  if pov != self.last_pov[i]:
                    self.last_pov[i] = pov
                    s = "%d %d" % pov
                    self.mqtt.publish("wbot/joystick%d/pov" % i, s)
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

    config = DSConfiguration()
    if config.number_of_joysticks == 1: winsize = winsize_1_joystick 
    if config.number_of_joysticks == 2: winsize = winsize_2_joystick
    wx, wy = winsize
    root = tk.Tk()
    root.title("Driver Station for Water Bot")
    root.geometry("%dx%d" % winsize)
    ds = DriveStation(root, config, enable_mqtt=enable_mqtt)
    ds.place(x=0, y=0, width=wx, height=wy) 
    ds.start_background()
    root.mainloop()
    ds.stop_all()
