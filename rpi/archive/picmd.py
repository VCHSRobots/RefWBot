# picmd.py -- simple program to test i2c link between pi and ardunio
# EPIC Robotz, dlb, Feb 2021

from smbus import SMBus
import time

addr = 0x8 # bus address
bus = SMBus(1) # indicates /dev/ic2-1

def fourbytestolong(u0, u1, u2, u3):
	x = (u0 << 24) + (u1 << 16) + (u2 << 8) + u3
	return x

def print_status():
	id = bus.read_byte_data(addr, 0)
	bat = bus.read_byte_data(addr, 1)
	time.sleep(0.01)
	u0 = bus.read_byte_data(addr, 2)
	time.sleep(0.01)
	u1 = bus.read_byte_data(addr, 3)
	time.sleep(0.01)
	u2 = bus.read_byte_data(addr, 4)
	time.sleep(0.01)
	u3 = bus.read_byte_data(addr, 5)
	bat = bat / 10.0
	tt = fourbytestolong(u3, u2, u1, u0)
	print("Device Id = %c\n" % id)
	print("Battery Voltage = %f\n" % bat)
	print("Device Time = %d\n" % tt)

numb = 1
print("Program to Test Ardunio/Pi I2C Interface")
print("Menu: ")
print("  x -- exit the program")
print("  s -- get status")
print("  r -- set reg 8 to 111")
print("  q -- set reg 8 to 222")
print("  g -- get contents of reg 8")

while True:
	cc = input(">>>>  ")
	if len(cc) <= 0:
		continue
	c = ord(cc[0])
	if c == ord('x'):
		break
	if c == ord('g'):
		y = bus.read_byte_data(addr, 8)
		print("Registor 8 = %d\n" % y)
		yy = bus.read_byte(addr)
		print("Second read = %d\n" % yy)
	if c == ord('r'):
		bus.write_byte_data(addr, 8, 111)
		print("Wrote 111 to reg 8.\n")
	if c == ord('q'):
		bus.write_byte_data(addr, 8, 222)
		print("Wrote 222 to reg 8.\n")
	if c == ord('s'):
		print_status()


