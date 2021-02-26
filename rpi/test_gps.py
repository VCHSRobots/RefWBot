# test_gps.py -- Shows that the GPS is working
# EPIC Robotz, dlb, Feb 2021

from micropyGPS import MicropyGPS
import sys
import threading
import time
gps = MicropyGPS()


# --------------------------------------------
# Background task to keep reading the gps and
# processing it.

gps_state = ("No Fix", (0,0,0), (0,0,0), 0, 0)
print_update = False
quit_background = False

def run_gps():
    global gps_state, print_update
    try:
        f = open("/dev/serial0", "rb", buffering=0)
    except:
        print("Unable to open gps serial input.\n")
        sys.exit()
    nerr = 0
    while True: 
        if quit_background: return
        x = f.read(10)
        for ix in x: 
            try:
                c = chr(ix)
                gps.update(str(c))
            except:
                nerr += 1
        if print_update:
            print_update = False
            print("Valid = ", gps.valid)
            print("Date = ", gps.date)
            print("Timestamp = ", gps.timestamp)
            print("Fix Time = ", gps.fix_time)
            print("Fix Type = ", gps.fix_type)
            print("Latitude = ", gps.latitude)
            print("Longitude = ", gps.longitude)
            print("Sat data = ", gps.satellite_data)
            print("Sats used = ", gps.satellites_used)
            print("Sats vis = ", gps.satellites_visible)
            print("Total sv sentences = ", gps.total_sv_sentences)
            print("Total number of error chars = ", nerr)

        
bg = threading.Thread(target=run_gps, name="background-gps")
bg.start()
print("Test GPS\n cr = print update. x = exit\n")

while True:
    x = input(">>")
    if len(x) > 0:
        if x[0] == 'x':
            quit_background = True 
            sys.exit()
    print_update = True
