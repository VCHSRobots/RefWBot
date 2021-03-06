# runbot.py -- Main python program to run for water bot competition
# EPIC Robotz, dlb, Feb 2021

import mqttrobot
import xpwm
import arduino
import time

class WaterBot():
  def __init__(self):
      self.mqtt = mqttrobot.MqttRobot()
      self.ping_count = 0
      self.mqtt.register_topic("WBot/Joystick/Buttons")
      self.mqtt.register_topic("WBot/Joystick/xyz")
      self.mqtt.register_topic("WBot/Joystick/ruv")
      self.mqtt.register_topic("WBot/PingBot", self.on_ping)
      xpwm.board_init()
      xpwm.killall()
      self.arduino_okay = arduino.init()
      self.last_report_time = time.monotonic() - 5.0
      self.xyz = (0.0, 0.0, 0.0)
      self.ruv = (0.0, 0.0, 0.0)
      self.buttons = (False for _ in range(12))

  def on_ping(self, topic, data):
      ''' Called when a ping request is recevied. '''
      self.mqtt.publish("WBot/PingDS", data)
      self.ping_count += 1

  def report_status(self):
      ''' Reports the current status to the terminal once every 3 seconds. '''
      timenow = time.monotonic()
      if timenow - self.last_report_time < 3.000: return
      self.last_report_time = timenow
      print("")
      print("Robot Time: %12.3f" % time.monotonic())
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

  def get_control_inputs(self):
      ''' Gather all inputs '''
      okay, x, y, z = self.mqtt.get_3_floats("WBot/Joystick/xyz")
      if okay: self.xyz = (x, y, z)
      okay, r, u, v = self.mqtt.get_3_floats("WBot/Joystick/ruv")
      if okay: self.ruv = (r, u, v)
      okay, btns = self.mqtt.get_12_bools("WBot/Joystick/Buttons")
      if okay: self.buttons = tuple(btns)

  def control_bot(self):
    ''' Control code goes here. '''
    _, y, z = self.xyz
    xpwm.set_servo(15, y)

  def run(self):
    ''' Main loop for water bot '''
    while True:
      self.get_control_inputs()
      self.report_status()
      self.control_bot()
      time.sleep(0.01)

if __name__ == "__main__":
    wb = WaterBot()
    wb.run()

