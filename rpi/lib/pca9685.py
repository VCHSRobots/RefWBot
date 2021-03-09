# pca9685.py -- Driver for PCA9685 module. 
# EPIC Robotz, dlb, Feb 2021

from smbus import SMBus
import time

default_addr = 0x4c # bus addres of PCA9685 board
default_bus_num = 1 # SMBus(1) # indicates /dev/ic2-1
default_masterfreq =  25000000  # acording to the specs

# Registors
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

# Bits in Mode1
b_restart = 1 << 7  # Used to awake from sleep.
b_extclk  = 1 << 6  # Enables (1) of external clock. Not needed by us.
b_ai      = 1 << 5  # Auto increment feature. Not needed by us.
b_sleep   = 1 << 4  # Setting this bit causes chip to sleep.  Must clear for operation.
b_allcall = 1 << 0  # Setting this bit enabled response to all-call. Not needed by us.

# Bits in Mode2
b_invrt   = 1 << 4  # Enables inverted output state. Not needed by us.
b_och     = 1 << 3  # Controls with PWM settings take effect. We want 1 for immediate.
b_outdrv  = 1 << 2  # Sets totem pole (1) or Open Drain (0) outputs. We want 1.

class PCA9685():
    def __init__(self, addr=default_addr, bus_num=default_bus_num, skipinit=False):
        self._addr = default_addr
        self._bus_num = default_bus_num
        self._bus = SMBus(self._bus_num)
        self._inited = False
        self._usec_per_tick = 4.84  # Recalculated when frequency is set.
        if skipinit:
            self._inited = True
        else:
            self.init()

    def write_reg(self, reg, dat):
        ''' Writes to a register in the PCA9685 module. '''
        self._bus.write_byte_data(self._addr, reg, dat)

    def read_reg(self, reg):
        ''' Reads from a register in the PCA9685 module. '''
        return self._bus.read_byte_data(self._addr, reg)

    def set_pwm(self, chan, pulsewidth_usec):
        ''' Sets a channel's pulsewidth, given in usecs. '''
        if not self._inited: return
        offtime = int(round(pulsewidth_usec / self._usec_per_tick))
        byteH = (offtime >> 8) & 0xFF
        byteL = offtime & 0xFF
        regnum = r_led0_on_L + (chan * 4)
        # Note: all 4 regs for the chan must be writen to cause effect
        self.write_reg(regnum + 0, 0)     # Low byte of on time
        self.write_reg(regnum + 1, 0)     # High byte of on time
        self.write_reg(regnum + 2, byteL) # Low byte of off time
        self.write_reg(regnum + 3, byteH) # High byte of off time

    def set_frequency(self, hz, masterfreq=2500000):
        ''' Sets the PWM frequency for all channels. Default is 50 Hz. '''
        prescale = int(round(masterfreq / (4096.0 * hz)) -1)
        if prescale < 3: prescale = 3
        if prescale > 255: prescale = 255
        #print("prescale=%f" % prescale)
        # to change preset, must p ut device in sleep mode!
        mode = self.read_reg(r_mode1)
        self.write_reg(r_mode1, (mode & ~b_sleep) | b_sleep)
        self.write_reg(r_prescale, prescale)
        self.write_reg(r_mode1, mode)
        time.sleep(0.0005)	# allow oscillator to get going again
        self.write_reg(r_mode1, mode | b_restart)  # reset the restart bit
        self._usec_per_tick = 1000000 / (masterfreq / prescale)
        # print("usec_per_tick=%f" % self._usec_per_tick)

    def init(self, masterfreq = default_masterfreq):
        ''' Initialize PWM module -- must be called before setting pwm signals. 
            Currently, this is being done when the object is created.'''
        # set overall modes with the two main registors
        self.write_reg(r_mode1, 0)
        self.write_reg(r_mode2, b_och | b_outdrv)
        time.sleep(0.0005) # Time required to start the chips oscillator.
        # now we need to write zero to the sleep bit without distrubing the other bits
        mode = self.read_reg(r_mode1)
        self.write_reg(r_mode1, mode & ~b_sleep)
        time.sleep(0.0005)
        self.set_frequency(50, masterfreq=masterfreq)
        self._inited = True 

    def set_servo(self, chan, rotation, minpw=800, maxpw=2200):
        ''' Set servo rotation from -1 (lowest angle) to 1 (highest angle).
        You can control the extreme settings for pulsewidth with minpw, maxpw.'''
        span = int(maxpw - minpw)
        center = int(minpw + span/2)
        move = int(rotation * (span / 2))
        usec = center + move
        if usec > maxpw: usec = maxpw 
        if usec < minpw: usec = minpw
        self.set_pwm(chan, usec)
    
    def killall(self):
        ''' Shuts down pwm on all channels. '''
        for i in range(16):
            self.set_pwm(i, 0)
