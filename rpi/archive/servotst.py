# servotst.py -- See if we can control the PCA9685 board
# EPIC Robotz, dlb, Feb 2021

from smbus import SMBus
import time

addr = 0x4c # bus addres of PCA9685 board
bus = SMBus(1) # indicates /dev/ic2-1
masterfreq =  25000000  # discovered by experiments

#registors
r_mode1    = 0x00
r_mode2    = 0x01
r_subadr1  = 0x02
r_subadr2  = 0x03
r_subadr3  = 0x04
r_prescale = 0xFE
r_led0_on_L  = 0x06
r_led0_on_H  = 0x07
r_led0_off_L = 0x08
r_led0_off_H = 0x09

#bits in Mode1
b_restart = 1 << 7  # Used to awake from sleep.
b_extclk  = 1 << 6  # Enables (1) of external clock. Not needed by us.
b_ai      = 1 << 5  # Auto increment feature. Not needed by us.
b_sleep   = 1 << 4  # Setting this bit causes chip to sleep.  Must clear for operation.
b_allcall = 1 << 0  # Setting this bit enabled response to all-call. Not needed by us.

#bits in Mode2
b_invrt   = 1 << 4  # Enables inverted output state. Not needed by us.
b_och     = 1 << 3  # Controls with PWM settings take effect. We want 1 for immediate.
b_outdrv  = 1 << 2  # Sets totem pole (1) or Open Drain (0) outputs. We want 1.

usec_per_tick = 4.84  # This is recaluated below

def write_reg(reg, dat):
	bus.write_byte_data(addr, reg, dat)

def read_reg(reg):
	return bus.read_byte_data(addr, reg)

def set_servo(chan, pulsewidth_usec):
	global usec_per_tick
	offtime = int(round(pulsewidth_usec / usec_per_tick))
	print("offtime count = %d\n" % offtime)
	byteH = (offtime >> 8) & 0xFF
	byteL = offtime & 0xFF
	regnum = r_led0_on_L + (chan * 4)
	# Note: all 4 regs for the chan must be writen to cause effect
	write_reg(regnum + 0, 0)     # Low byte of on time
	write_reg(regnum + 1, 0)     # High byte of on time
	write_reg(regnum + 2, byteL) # Low byte of off time
	write_reg(regnum + 3, byteH) # High byte of off time

def set_frequency(hz):
	global usc_per_tick
	prescale = int(round(masterfreq / (4096.0 * hz)) -1)
	if prescale < 3:
		prescale = 3
	if prescale > 255:
		prescale = 255
	actualhz = (masterfreq / 4096) / (prescale + 1)
	print("prescale = %d, freq = %6.1f" % (prescale, actualhz))
	# to change preset, must put device in sleep mode!
	mode = read_reg(r_mode1)
	write_reg(r_mode1, (mode & ~b_sleep) | b_sleep)
	write_reg(r_prescale, prescale)
	write_reg(r_mode1, mode)
	time.sleep(0.0005)	# allow oscillator to get going again
	write_reg(r_mode1, mode | b_restart)  # reset the restart bit
	usec_per_tick = 1000000 / (masterfreq / prescale)
	print("usec_per_tick = %f" % usec_per_tick)

def board_init():
	# set overall modes with the two main registors
	write_reg(r_mode1, 0)
	write_reg(r_mode2, b_och | b_outdrv)
	time.sleep(0.0005)    # Time required to start the chips oscillator.
	# now we need to write zero to the sleep bit without distrubing the other bits
	mode = read_reg(r_mode1)
	write_reg(r_mode1, mode & ~b_sleep)
	time.sleep(0.0005)
	set_frequency(50)

board_init()
set_servo(15, 1000)
set_servo(14, 2000)
print("Servo Test. Servo 14 should be running at 2ms.\n")
print("Servo Test. Servo 15 should be running at 1ms.\n")



