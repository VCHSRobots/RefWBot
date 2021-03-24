# i2ctst.py -- test the i2c connection
# EPIC Robotz, dlb, Feb 2021

import time
import sys
import arduino_wb
import arduino_reg_map as reg
import random

arduino = arduino_wb.Arduino_wb()

data_errcnt = 0
bus_errcnt = 0
ncnt = 0

wregs = [reg.PWM9, reg.PWM10, reg.PWM11, reg.XXX0, reg.XXX1, reg.XXX2]
wdat  = [0, 0, 0, 0, 0, 0]
for r in wregs:
  try:
    arduino.writereg(r, 0)
  except IOError as err:
    print("Unable to init.  \nErr= ", err)
    sys.exit()

while True:
  ncnt += 1
  try:
    ipath = random.randint(0,5)
    r = wregs[ipath]
    wdat[ipath] = d = random.randint(0, 255)
    arduino.writereg(r, d)
    okay, x = arduino.get_battery_voltage(battype="L")
    if not okay or x < 9 or x > 14.5:
      print("Battery Voltage = %6.3f" % x)
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
  time.sleep(0.010)
  if ncnt % 50 == 0:
    print("Loop Count: %d,  Bus Errors: %d,  Data Errors: %d" % (ncnt, bus_errcnt, data_errcnt))
