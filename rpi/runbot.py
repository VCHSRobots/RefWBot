# runbot.py -- Main python program to run for water bot competition
# EPIC Robotz, dlb, Feb 2021

import mqttbot
import xpwm
import arduino
import time

class WaterBot():
  def __init__(self):
    self.mqtt = mqttbot.MqttBot()
    self.mqtt.register_topic("WBot/Joystick/Buttons")
    self.mqtt.register_topic("WBot/Joystick/xyz")
    self.mqtt.register_topic("WBot/Joystick/ruv")
    xpwm.board_init()
    xpwm.killall()
    self.arduino_okay = arduino.init()

  def rx_3_floats(self, topic):
    ''' Decodes three floats from MQTT topic. Returns:
    okay_flag, f1, f2, f3. '''
    okay, s, _ = self.mqtt.get_data(topic)
    if not okay:
      return False, 0, 0, 0
    slist = s.split() 
    if len(slist) != 3:
      return False, 0, 0, 0
    try:
      x, y, z = float(slist[0]), float(slist[1]), float(slist[2])
    except:
      return False, 0, 0, 0
    return True, x, y, z

  def rx_12_bools(self, topic):
    ''' Decodes 12 booleans from MQTT topic. Returns:
    okay_flag, vals[], where vals is a list of 12 booleans. '''
    okay, s, _ = self.mqtt.get_data(topic)
    if not okay:
      return False, [False for _ in range(12)]
    slist = s.split()
    if len(slist) != 12:
      return False, [False for _ in range(12)]
    btns = []
    for s in slist:
      if s == "T": btns.append(True)
      else: btns.append(False)
    return True, btns

  def run(self):
    ''' Main loop for water bot '''
    while True:
      okay, x, y, z = self.rx_3_floats("WBot/Joystick/xyz")
      print("okay, x,y,z = %s, %5.3f, %5.3f %5.3f" % (okay, x, y, z))
      time.sleep(0.1)

if __name__ == "__main__":
    wb = WaterBot()
    wb.run()

