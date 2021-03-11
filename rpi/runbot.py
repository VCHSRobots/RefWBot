# runbot.py -- Main python program to run for water bot competition
# EPIC Robotz, dlb, Feb 2021

# Notes:
#  1. Possible modes are: "STOP", "TELEOP", "AUTO".  If any other mode is
#  received from the driver station, STOP is asserted.
#

import mqttrobot
import pca9685 as pca
import arduino_wb
import busmonitor 
import time

dstimeout = 3.0  # number of seconds before kill due to no msg received from driver station

class WaterBot():
  ''' WaterBot class is the main class for the program that controls the Water Bot. '''

  def __init__(self):
      ''' Initialization of the WaterBot. '''
      self.mqtt = mqttrobot.MqttRobot()
      self.ping_count = 0
      self.botmode = "STOP" # given from the driver station
      self.mode_switch = True 
      self.run_loop_count = 0
      self.ds_loop_count = 0
      self.time_to_run = 0.0  # As given from the driver station
      self.msg_timeout_count = 0  # number of times shut down because no driver station messages
      self.msg_err_count = 0 # number of decoding errors on input messages
      self.restart_count = 0 # number of times hardware was reset and restarted due to bus errors
      self.time_of_hw_fail_check = 0 # used to remember when restarts were tried.
      self.last_mode_cmd_time = time.monotonic() - 100.0
      self.mqtt.register_topic("wbot/mode", self.on_mode)
      self.mqtt.register_topic("wbot/joystick/buttons")
      self.mqtt.register_topic("wbot/joystick/xyz")
      self.mqtt.register_topic("wbot/joystick/ruv")
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
      self.xyz = (0.0, 0.0, 0.0)
      self.ruv = (0.0, 0.0, 0.0)
      self.buttons = (False for _ in range(12))

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
        self.restart_count += 1

  def get_control_inputs(self):
      ''' Gather all inputs '''
      okay, x, y, z = self.mqtt.get_3_floats("wbot/joystick/xyz")
      if okay: self.xyz = (x, y, z)
      okay, r, u, v = self.mqtt.get_3_floats("wbot/joystick/ruv")
      if okay: self.ruv = (r, u, v)
      okay, btns = self.mqtt.get_12_bools("wbot/joystick/buttons")
      if okay: self.buttons = tuple(btns)

  def report_status_to_term(self):
      ''' Reports the current status to the terminal once every 3 seconds. '''
      timenow = time.monotonic()
      if timenow - self.last_report_time_to_term < 3.000: return
      self.last_report_time_to_term = timenow
      print("")
      print("Robot Mode: %s" % self.botmode)
      print("Robot Time: %12.3f   Time_to_go: %6.1f" % (time.monotonic(), self.time_to_run))
      bat1 = bat2 = 0.0
      if self.hw_okay:
          _, bat1 = self.arduino.get_battery_voltage()
      print("Hardware okay: %s   i2c errors = %d" % (self.hw_okay, self.bus_monitor.get_total_error_count()))
      print("Main Battery: %6.1f volts,  Logic Battery: %6.1f" % (bat1, bat2) )
      print("Connected to MQTT: %s" % self.mqtt.is_connected())
      mqttcounts = self.mqtt.get_counts()
      print("MQTT messages received: %d " % mqttcounts["rx"])
      print("MQTT errors: %d" % mqttcounts["err"])
      print("XYZ: %5.3f, %5.3f, %5.3f" % self.xyz)
      print("RUV: %5.3f, %5.3f, %5.3f" % self.ruv)
      s = ""
      for b in self.buttons: 
        if b: s += "T "
        else: s += "F "
      print("Buttons: %s" % s)
      print("msgerr = %d, msgtmeouts = %d" % (self.msg_err_count, self.msg_timeout_count))

  def report_status_to_ds(self):
      ''' Reports the current status to the driver station, once every 1 second. '''
      timenow = time.monotonic()
      if timenow - self.last_report_time_to_ds < 1.000: return
      self.last_report_time_to_ds = timenow
      bat1 = bat2 = 0.0
      if self.hw_okay:
        _, bat1 = self.arduino.get_battery_voltage()
      i2c = self.bus_monitor.get_total_error_count()
      s = "%s %d %s %6.1f %6.1f %d %d" % ("okay", self.ds_loop_count, 
        self.hw_okay, bat1, bat2, i2c, self.restart_count)
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
    ## ******* Put shut down code below. 
    if self.run_loop_count == 0:
      print("**** Switching to STOP")
      # Kill all motors and actuators here...
      if self.hw_okay:
        try:
          self.pca.killall()
        except:
          pass

  def run_auto(self, loop_count, time_to_go):
    ''' Called repeatedly during auto.  On inital call after a mode switch,
    loop_count will be zero. Thereafter, it will increase by one. The
    time_to_go variable has the number of seconds that the driver station
    reports for the time till the end of the auto period.  Note that
    time_to_go may not decrease in keeping with actual time. '''
    ## ******* Put auto code below
    if loop_count == 0:
      # Initialize stuff here...
      print("**** Switching to Auto")
    pass

  def run_teleop(self, loop_count, time_to_go):
    ''' Called repeatedly during teleop.  On inital call after a mode switch,
    loop_count will be zero. Thereafter, it will increase by one. The
    time_to_go variable has the number of seconds that the driver station
    reports for the time till the end of the match.  Note that time_to_go may not
    decrease in keeping with actual time. '''
    # ********* Put teleop code below
    if loop_count == 0:
      #initalize stuff here...
      print("**** Switching to TeleOp")
    _, y, _ = self.xyz 
    self.pca.set_servo(15, y)
    if self.buttons[2]:
      raise Exception("Test Termination of Program...")

if __name__ == "__main__":
    wb = WaterBot()
    wb.run()

