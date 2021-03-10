# joyprint.py -- Print joystick info to terminal
# EPIC Robotz, dlb, Mar 2021

import joystick
import sys

x = joystick.get_devices()

for y in x:
  print(y)

j = joystick.Joystick(style="XBox Gamepad")
if not j.is_connected(): sys.exit()

print("number axis=", j.get_number_axis())



