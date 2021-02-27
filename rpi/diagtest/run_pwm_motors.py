# run_pwm_motors.py -- runs the pwm motors on the demo board
# EPIC Robotz, dlb, Feb 2021

import sys
import arduino
import time
import threading

stopit = False

def run_in_background():
    errcnt = 0
    while True:
        try:
            a1 = arduino.get_analog("A1")
            a2 = arduino.get_analog("A2")
        except:
            errcnt += 1
            print("Bus error. %d" % errcnt)
            continue
        if stopit: return
        time.sleep(0.02)
        if a1 < 0.05 and a2 < 0.05: break
    print("")
    print("Starting Control...")

    cnt = 0
    while True:
        if stopit:
            arduino.set_pwm("ALL", 0)
            return
        cnt += 1
        if cnt % 50 == 0: print("loop count: %d. A1, A2 = %5.3f %5.3f  Errs = %ld" % (cnt, a1, a2, errcnt))
        try: 
            a1 = arduino.get_analog("A1")
            a2 = arduino.get_analog("A2")
            arduino.set_pwm("PWM10", a1)
            arduino.set_pwm("PWM11", a2)
        except:
            errcnt += 1
            print("Bus error. %d" % errcnt)
        time.sleep(0.02)

print("run_pwm_motors")
print("Use the knobs to control the pwm motors.")
print("Start by zeroing them out.")

okay = arduino.init()
if not okay:
    print("Failed to talk to arduino.")
    sys.exit()
arduino.set_pwm("ALL", 0)
bg = threading.Thread(target=run_in_background, name="background-control.")
bg.start()
print("Press ENTER to quit the program.")
print("")
input("")
stopit = True
