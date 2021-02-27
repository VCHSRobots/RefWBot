# i2ctst.py -- test the i2c connection
# EPIC Robotz, dlb, Feb 2021

import time
import sys
import arduino
import arduino_reg_map as reg
import random

okay = arduino.init()
if not okay:
  print("Init failed.")
  sys.exit()

data_errcnt = 0
bus_errcnt = 0
ncnt = 0

dx0 = dx1 = dx2 = 0
arduino.writereg(reg.XXX0, dx0)
arduino.writereg(reg.XXX0, dx1)
arduino.writereg(reg.XXX0, dx2)

wregs = [reg.PWM9, reg.PWM10, reg.PWM11, reg.XXX0, reg.XXX1, reg.XXX2]
wdat  = [0, 0, 0, 0, 0, 0]
for r in wregs:
  arduino.writereg(r, 0)

while True:
  ncnt += 1
  try:
    ipath = random.randint(0,5)
    r = wregs[ipath]
    wdat[ipath] = d = random.randint(0, 255)
    arduino.writereg(r, d)
    x = arduino.get_battery_voltage()
    if x < 9 or x > 12.5:
      data_errcnt += 1
    ipath = random.randint(0, 5)
    r, d = wregs[ipath], wdat[ipath]
    d0 = arduino.readreg(r)
    if d != d0:
      data_errcnt += 1
      if data_errcnt < 10: print("Data error found! Wrote 0x%02x Read 0x%02x ." % (d, d0))
  except:
    bus_errcnt += 1
    if bus_errcnt < 10: print("Bus error found!")
  time.sleep(0.020)
  if ncnt % 50 == 0:
    print("Loop Count: %d,  Bus Errors: %d,  Data Errors: %d" % (ncnt, bus_errcnt, data_errcnt))
