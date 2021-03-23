# runbot.py -- Main python program to run for water bot competition
# EPIC Robotz, dlb, Feb 2021
#
# Verson 1.3 -- Added outside user class
#
# Notes:
#  1. Possible modes are: "STOP", "TELEOP", "AUTO".  If any other mode is
#  received from the driver station, STOP is asserted.
#

import os
import traceback
import mqttrobot
import pca9685 as pca
import arduino_wb
import busmonitor 
import hydromotor
import utils
import time

version = "v1"  # A version indicator for the driver station
dstimeout = 3.0  # number of seconds before kill due to no msg received from driver station

#  Attempt to load in the user code here.  The first module found with robot_*.py will
# be used.

def get_user_module():
  ''' Attempts to find the robot_xxx.py file that the user wants to 
  used for dynamic loading.  If found, the module is loaded and returned,
  but the interal WaterBot class is NOT initiated.'''
  ourplace = os.path.dirname(os.path.abspath(__file__))
  flst = os.listdir(ourplace)
  module_file = ""
  for f in flst:
      if f.endswith(".py") and f.startswith("robot_"):
          module_file = f
  if module_file == "":
      print("********************* User code not found!")
      return None
  module_name = module_file[:-3]
  try:
    user_module = __import__(module_name)
  except Exception as e:
    print("Error loading %s: " % module_name)
    traceback.print_exc()
    return None
  return user_module

class WaterBotBase():
  ''' WaterBot class is the main class for the program that controls the Water Bot. '''

  def __init__(self, user_module):
      ''' Initialization of the WaterBot. '''
      self.user_module = user_module
      self.mqtt = mqttrobot.MqttRobot()
      self.ping_count = 0
      self.botmode = "STOP" # given from the driver station
      self.mode_switch = True 
      self.run_loop_count = 0
      self.ds_loop_count = 0
      self.time_to_run = 0.0  # As given from the driver station
      self.msg_timeout_count = 0  # number of times shut down because no driver station messages
      self.msg_err_count = 0 # number of decoding errors on input messages
      self.recovered_count = 0 # number of times hardware recovered after bus error
      self.time_of_hw_fail_check = 0 # used to remember when restarts were tried.
      self.last_mode_cmd_time = time.monotonic() - 100.0
      self.mqtt.register_topic("wbot/mode", self.on_mode)
      self.mqtt.register_topic("wbot/joystick0/buttons")
      self.mqtt.register_topic("wbot/joystick0/axes")
      self.mqtt.register_topic("wbot/joystick0/pov")
      self.mqtt.register_topic("wbot/joystick1/buttons")
      self.mqtt.register_topic("wbot/joystick1/axes")
      self.mqtt.register_topic("wbot/joystick1/pov")
      self.mqtt.register_topic("wbot/pingbot", self.on_ping)
      self.hw_okay = True
      self.bus_monitor = busmonitor.BusMonitor()
      self.pca = pca.PCA9685(bus_monitor=self.bus_monitor)
      self.arduino = arduino_wb.Arduino_wb(bus_monitor=self.bus_monitor) 
      self.pca.killall()
      self.arduino.set_pwm("ALL", 0.0)
      if not self.arduino.test_health() or not self.pca.is_initialized():
        self.hw_okay = False
      self.last_report_time_to_ds = time.monotonic() - 5.0
      self.last_report_time_to_term = time.monotonic() - 5.0
      self.axes0 = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
      self.pov0 = (0,0)
      self.buttons0 = (False for _ in range(12))
      self.axes1 = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
      self.pov1 = (0,0)
      self.buttons1 = (False for _ in range(12))
      self.user_class = None
      self.user = None
      if self.user_module is not None:
        try:
          self.user_class = getattr(self.user_module, "WaterBot")
          self.user = self.user_class(self)
        except Exception:
          print("*** Unable to create user WaterBot object.")
          self.user_code_error = True
          self.user = None
      if self.user:
        try:
          self.user.initialize()
        except Exception as e:
          self.user_code_error = True
          print("**** Unable to call initialize on user Waterbot.")
          print("Exception = ", e)
          traceback.print_exc()
      self.user_code_error = self.user is None
    
  # -------------------------------------------------------------------
  # Callback Functions

  def on_ping(self, topic, data):
      ''' Called when a ping request is recevied. '''
      self.mqtt.publish("wbot/pingds", data)

  def on_mode(self, topic, data):
      ''' Called when a mode command/status msg is received. '''
      words = data.split()
      if len(words) < 3:
        self.time_to_run = 0.0
        self.msg_err_count += 1
        self.botmode = "STOP"
        self.mode_switch = True
        return 
      if len(words) >= 4:
        if words[3].lower() == "RestartArduino".lower():
          print("******* Restarting Arduino")
          self.arduino.reset_hardware()  
      try:
        self.ds_loop_count = int(words[1])
        self.time_to_run = float(words[2])
      except ValueError:
          self.time_to_run = 0.0
          self.msg_err_count += 1
          self.botmode = "STOP"
          self.mode_switch = True
          return       
      newmode = words[0]
      if newmode == "STOP" or newmode == "TELEOP" or newmode == "AUTO":
          self.last_mode_cmd_time = time.monotonic()
          if newmode != self.botmode: self.mode_switch = True
          self.botmode = newmode 
          return 
      else:
          self.time_to_run = 0.0
          self.msg_err_count += 1
          self.botmode = "STOP"
          self.mode_switch = True

  # -------------------------------------------------------------------
  # Main Run Loop 

  def run(self):
    ''' Main loop for water bot '''
    while True:
      self.check_i2cbus() 
      self.get_control_inputs()
      self.report_status_to_term()
      self.report_status_to_ds()
      self.control_bot()
      time.sleep(0.01)

  # -------------------------------------------------------------------
  # Major Task Functions that Main Loop calls apon.

  def check_i2cbus(self):
    timenow = time.monotonic()
    if self.hw_okay and self.bus_monitor.in_alert():
        self.time_of_hw_fail_check = timenow
        self.hw_okay = False 
        print("I2C Bus Failure!!!")
        ## If this proves to be a problem then we will try to figure out a way to restart the hardware.
        return
    if self.hw_okay:
      if not self.arduino.test_health():
        print("Arduino health fail!!!")
        self.hw_okay = False
        self.time_of_hw_fail_check = timenow
      return
    # Try to recover once per 1/2 sec
    if timenow - self.time_of_hw_fail_check < 0.5: return
    self.time_of_hw_fail_check = timenow 
    if self.arduino.test_health():
      self.pca.init()
      if self.pca.is_initialized():
        # Health check and pca init passes!  Reinstate hardware.
        print("Hardware reset successful!!!")
        self.hw_okay = True
        self.bus_monitor.reset() 
        self.recovered_count += 1

  def get_control_inputs(self):
      ''' Gather all inputs '''
      okay, btns = self.mqtt.get_12_bools("wbot/joystick0/buttons")
      if okay: self.buttons0 = tuple(btns)
      okay, btns = self.mqtt.get_12_bools("wbot/joystick1/buttons")
      if okay: self.buttons1 = tuple(btns)
      okay, axes = self.mqtt.get_6_floats("wbot/joystick0/axes")
      if okay: self.axes0 = axes
      okay, axes = self.mqtt.get_6_floats("wbot/joystick1/axes")
      if okay: self.axes1 = axes
      okay, pov = self.mqtt.get_2_ints("wbot/joystick0/pov")
      if okay: self.pov0 = pov
      okay, pov = self.mqtt.get_2_ints("wbot/joystick1/pov")
      if okay: self.pov1 = pov

  def report_status_to_term(self):
      ''' Reports the current status to the terminal once every 3 seconds. '''
      timenow = time.monotonic()
      if timenow - self.last_report_time_to_term < 3.000: return
      self.last_report_time_to_term = timenow
      print("")
      print("Robot Mode: %s" % self.botmode)
      print("Robot Time: %12.3f   Time_to_go: %6.1f" % (time.monotonic(), self.time_to_run))
      bat_m = bat_l = 0.0
      if self.hw_okay:
        _, bat_m = self.arduino.get_battery_voltage(battype="M")
        _, bat_l = self.arduino.get_battery_voltage(battype="L")
      print("Hardware okay: %s   i2c errors = %d  restarts = %d" % (self.hw_okay, 
        self.bus_monitor.get_total_error_count(), self.recovered_count))
      print("Main Battery: %6.1f volts,  Logic Battery: %6.1f" % (bat_m, bat_l) )
      print("Connected to MQTT: %s" % self.mqtt.is_connected())
      mqttcounts = self.mqtt.get_counts()
      print("MQTT messages received: %d " % mqttcounts["rx"])
      print("MQTT errors: %d" % mqttcounts["err"])
      print("Axes 0: %6.3f, %6.3f, %6.3f, %6.3f, %6.3f, %6.3f" % self.axes0)
      print("Axes 1: %6.3f, %6.3f, %6.3f, %6.3f, %6.3f, %6.3f" % self.axes1)
      s = ""
      for b in self.buttons0: 
        if b: s += "T "
        else: s += "F "
      print("Buttons0: %s" % s)
      s = ""
      for b in self.buttons1: 
        if b: s += "T "
        else: s += "F "
      print("Buttons1: %s" % s)
      x0, y0 = self.pov0
      x1, y1 = self.pov1
      print("POV0 = (%d, %d)   POV1 = (%d %d)" % (x0, y0, x1, y1))
      if self.user:
        print("User WaterBot class loaded from %s." % self.user_module.__name__)
      else:
        print("***  User Module Not Loaded!!")
      print("msgerr = %d, msgtmeouts = %d" % (self.msg_err_count, self.msg_timeout_count))

  def report_status_to_ds(self):
      ''' Reports the current status to the driver station, once every 1 second. '''
      timenow = time.monotonic()
      if timenow - self.last_report_time_to_ds < 1.000: return
      self.last_report_time_to_ds = timenow
      bat_m = bat_l = 0.0
      if self.hw_okay:
        _, bat_m = self.arduino.get_battery_voltage(battype="M")
        _, bat_l = self.arduino.get_battery_voltage(battype="L")
      i2c = self.bus_monitor.get_total_error_count()
      s_status = "okay"
      if self.user_code_error: s_status = "code_err"
      s = "%s %d %s %6.1f %6.1f %d %d %s" % (s_status, self.ds_loop_count, 
        self.hw_okay, bat_m, bat_l, i2c, self.recovered_count, version)
      self.mqtt.publish("wbot/status", s)
      if self.hw_okay:
        try:
          okay, dat = self.arduino.get_all()
          if okay:
            sout = ""
            for d in dat:
              sout += "%03d " % d
            self.mqtt.publish("wbot/arduino", sout) 
        except OSError:
          pass
      
  def control_bot(self):
    ''' Overall control loop for the robot. Dispatches to various modes. '''
    if time.monotonic() - self.last_mode_cmd_time > 2.5:
      if self.botmode != "STOP":
        self.botmode = "STOP"
        self.run_loop_count = -1
        self.time_to_run = 0.0
    self.run_loop_count += 1
    if self.mode_switch:
      self.run_loop_count = 0
      self.mode_switch = False
    if self.botmode == "STOP":
      self.stop(self.run_loop_count)
    if self.botmode == "AUTO":
      self.run_auto(self.run_loop_count, self.time_to_run)
    if self.botmode == "TELEOP":
      self.run_teleop(self.run_loop_count, self.time_to_run)

  # -------------------------------------------------------------------
  # Functions to execute according to robot mode.
  # User Code goes in these...

  def stop(self, loop_count):
    ''' Called in stop mode.  Here, all motors and actuators should be 
    shut off. '''
    if self.user:
      try:
        self.user.stop(loop_count)
      except Exception:
        if not self.user_code_error: 
          print("**** User Stop code Failed.")
          traceback.print_exc()
        self.user_code_error = True
        self.pca.killall()

  def run_auto(self, loop_count, time_to_go):
    ''' Called repeatedly during auto.  On inital call after a mode switch,
    loop_count will be zero. Thereafter, it will increase by one. The
    time_to_go variable has the number of seconds that the driver station
    reports for the time till the end of the auto period.  Note that
    time_to_go may not decrease in keeping with actual time. '''
    if self.user:
      try:
        self.user.auto(loop_count)
      except Exception:
        if not self.user_code_error: 
          print("**** User Auto code Failed.")
          traceback.print_exc()
        self.user_code_error = True 

  def run_teleop(self, loop_count, time_to_go):
    ''' Called repeatedly during teleop.  On inital call after a mode switch,
    loop_count will be zero. Thereafter, it will increase by one. The
    time_to_go variable has the number of seconds that the driver station
    reports for the time till the end of the match.  Note that time_to_go may not
    decrease in keeping with actual time. '''
    if self.user:
      try:
        self.user.teleop(loop_count)
      except Exception:
        if not self.user_code_error: 
          print("**** User Teleop Code Failed.")
          traceback.print_exc()
        self.user_code_error = True

if __name__ == "__main__":
    user_module = get_user_module()
    wb = WaterBotBase(user_module)
    wb.run()

