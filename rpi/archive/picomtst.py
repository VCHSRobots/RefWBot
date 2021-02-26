# picomtst.py -- simple program to test the communications between ardunio and pi
# EPIC Robotz, dlb, Feb 2021

from smbus import SMBus
import random
import time

addr = 0x8 # bus address of ardunio
bus = SMBus(1) # indicates /dev/ic2-1

adr_range = [6,7,8,9]  # registers to test
regs = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

def readreg(regadr):
	x = bus.read_byte_data(addr, regadr)
	#time.sleep(0.01)
	return x

def writereg(regadr, dat):
	bus.write_byte_data(addr, regadr, dat)
	#time.sleep(0.01)

# start with know values
for a in adr_range:
	writereg(a, regs[a])

errcount = 0
ntry = 0
nworked = 0
for i in range(1000):
	ntry += 1
	# write random data to a random reg and keep track of it
	ia = random.randint(0,len(adr_range) - 1)
	a = adr_range[ia]
	d = random.randint(0, 255)
	regs[a] = d
	writereg(a, d)
	# read a random reg and see if it matchs what we think it should be
	ia = random.randint(0, len(adr_range) - 1)
	a = adr_range[ia]
	dd = readreg(a)
	if dd != regs[a]:
		errcount += 1
		print("Mismatch on try %d. Reg %d. Found %d. Should be %d.\n" % (i, a, dd, regs[a]))
		fix  = (dd << 1) + 1
		if fix == regs[a]:
			#print("Fix Worked");
			nworked += 1

# last check
for a in adr_range:
	dd = readreg(a)
	if dd != regs[a]:
		print("Final check failed on reg %d. Found %d. Should be %d.\n" % (a, dd, regs[a]))

if errcount == 0:
	print("No errors.  Success!!")
else:
	print("Finished. Number of Errors after %d trys: %d\n" % (ntry, errcount))
	print("Final reg state should be: ")
	for a in adr_range:
		v = regs[a]
		print(v)
	print("\n")
	print("Number of times the fix worked: %d\n" % nworked)
