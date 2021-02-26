# test_joystick.py -- simple program to test the pc's joystick
# EPIC Robotz, dlb, Feb 2021

import joystick
import sys

gotpad = joystick.openGamepad()
if not gotpad:     
    print("No gamepad detected.")
    sys.exit()

print("Gamepad detected. Use x to exit. Current status on each CR:")
while True:
    s = input(">>")
    if len(s) >= 1:
        if s[0] == 'x' : sys.exit()
    btns = joystick.getGamepadButtons()
    print("buttons: ", btns)
    axisXYZ = joystick.getGamepadAxis()
    print("axis: [%5.3f, %5.3f, %5.3f]" % axisXYZ)
    axisRUV = joystick.getGamepadRot()
    print("axis: [%5.3f, %5.3f, %5.3f]" % axisRUV)
    
