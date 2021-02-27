# run_servo_motors.py -- runs the servo motors on the demo board
# EPIC Robotz, dlb, Feb 2021

import sys
import arduino
import time
import threading
import xpwm

# Set channel assignments here
tallon_chan = 2
esc_chan = 3
tallon_chan_t = 4
esc_chan_t = 5

stopit = False

def run_in_background():
    errcnt = 0
    cnt = 0
    while True:
        try:
            a1 = 2.0 * (arduino.get_analog("A1") - 0.5)
            a2 = 2.0 * (arduino.get_analog("A2") - 0.5)
        except:
            errcnt += 1
            print("Bus error. %d" % errcnt)
            continue
        if stopit: return
        cnt += 1
        if cnt % 50: print("Please Zero. Loop Count= %d, A1, A2 = %5.3f %5.3f  Errs = %ld" % (cnt, a1, a2, errcnt))
        time.sleep(0.02)
        if a1 > -0.05 and a1 < 0.05 and a2 > -0.05 and a2 < 0.05: break
    print("")
    print("Starting Control...")

    cnt = 0
    while True:
        if stopit:
            xpwm.set_pwm(tallon_chan, 1500) 
            xpwm.set_pwm(esc_chan, 850)
            xpwm.set_pwm(tallon_chan_t, 1500) 
            xpwm.set_pwm(esc_chan_t, 850)
            return
        cnt += 1
        try: 
            a1 = 2.0 * (arduino.get_analog("A1") - 0.5)
            a2 = 2.0 * (arduino.get_analog("A2") - 0.5)
            tv = 1500 + (a1*700)
            xpwm.set_pwm(tallon_chan, tv)
            xpwm.set_pwm(tallon_chan_t, tv)
            ev = 850 + a2*1200
            if a2 < 0: ev = 850
            xpwm.set_pwm(esc_chan, ev)
            xpwm.set_pwm(esc_chan_t, ev)
            if cnt % 10 == 0: print("loop count: %d. A1, A2 = %5.3f (%6.1f) %5.3f (%6.1f)  Errs = %ld" % (cnt, a1, tv, a2, ev, errcnt))
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
arduino.set_pwm("ALL", 0)
xpwm.board_init(masterfreq=27843706)  # Found by experimenting on demo board
xpwm.set_pwm(tallon_chan, 1500) 
xpwm.set_pwm(esc_chan, 850)
xpwm.set_pwm(tallon_chan_t, 1500) 
xpwm.set_pwm(esc_chan_t, 850)
bg = threading.Thread(target=run_in_background, name="background-control.")
bg.start()
print("Press ENTER to quit the program.")
print("")
input("")
stopit = True
