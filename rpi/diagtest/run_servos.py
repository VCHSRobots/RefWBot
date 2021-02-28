# run_servos.py -- runs the servoss on the demo board
# EPIC Robotz, dlb, Feb 2021
#
#  A1 is attached to servo on channel 15
#  A2 is attached to the servo on channel 14
#
#  The servo signals are copied to channels 12 and 13.

import sys
import arduino
import time
import threading
import xpwm

# Set channel assignments here
servo_1_chan = 15
servo_2_chan = 14
servo_1_copy_chan = 13
servo_2_copy_chan = 12

stopit = False

def run_in_background():
    errcnt = 0
    cnt = 0
    print("")
    print("Starting Control...")

    cnt = 0
    while True:
        if stopit:
            xpwm.killall()
            return
        cnt += 1
        try: 
          a1 = arduino.get_analog("A1") 
          a2 = arduino.get_analog("A2")
          xpwm.set_servo(servo_1_chan, a1)
          xpwm.set_servo(servo_1_copy_chan, a1)
          xpwm.set_servo(servo_2_chan, a2)
          xpwm.set_servo(servo_2_copy_chan, a2)
          if cnt % 10 == 0: print("loop count: %ld. A1, A2 = %5.3f %5.3f  Errs = %ld" % (cnt, a1, a2, errcnt))
        except:
          errcnt += 1
          print("Bus error. %d" % errcnt)
        time.sleep(0.02)

print("run_servo_motors")
print("Use the knobs to control the pwm motors.")
print("Start by zeroing them out.")

okay = arduino.init()
if not okay:
    print("Failed to talk to arduino.")
    sys.exit()
xpwm.board_init(masterfreq=27843706)  # Found by experimenting on demo board
xpwm.killall()
bg = threading.Thread(target=run_in_background, name="background-control.")
bg.start()
print("Press ENTER to quit the program.")
print("")
input("")
stopit = True
