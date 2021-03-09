# arduino_wb.py -- access to the arduino on the water bot
# EPIC Robotz, dlb, Mar 2021

import sys
from smbus import SMBus
import time

default_addr = 0x8 # bus address of ardunio
default_bus = 1 # indicates /dev/ic2-1

# This table should match the code in the arduino.
SIGV    =  0   #  RO  Device Signature/Version.  Currently: 'e'
BAT     =  1   #  RO  Battery Voltage (in units of 10ths of volts)
DTME1   =  2   #  RO  Device Time, Milliseconds, Byte 0, MSB
DTME2   =  3   #  RO  Device Time, Milliseconds, Byte 1
DTME3   =  4   #  RO  Device Time, Milliseconds, Byte 2
DTME4   =  5   #  RO  Device Time, Milliseconds, Byte 3, LSB
A1      =  6   #  RO  Voltage on pin A1, 0-255.  (Read once every 20ms)
A2      =  7   #  R0  Voltage on pin A2, 0-255.  (Read once every 20ms)
A3      =  8   #  R0  Voltage on pin A3, 0-255.  (Read once every 20ms)
A6      =  9   #  R0  Voltage on pin A6, 0-255.  (Read once every 20ms)
A7      = 10   #  R0  Voltage on pin A7, 0-255.  (Read once every 20ms)
SI      = 11   #  R0  Sensor Inputs, 8 bits maped as:  [0|0|D8|D7|D6|D5|D4|D3]
SC      = 12   #  RO  Sensor Changes, 8 bits maped as: [0|0|D8|D7|D6|D5|D4|D3]
SCC     = 13   #  RW  Sensor Change Clear: 0=clear, 1=keep for each bit.
PWM9    = 14   #  RW  PWM Output on D9: 0-255
PWM10   = 15   #  RW  PWM Output on D10: 0-255
PWM11   = 16   #  RW  PWM Output on D11: 0-255
XXX0    = 17   #  RW  Spare 1
XXX1    = 18   #  RW  Spare 2
XXX2    = 19   #  RW  Spare 3
LAST    = 19   #  ** Last Registor
RW0     = 13   #  ** First Registor where writing is allowed.

# One feature of the arduino code is that it keeps track if a digital input
# changes on D3-D8.  This is reported in REG_SC.  Note that any change
# (LOW -> HIGH, or HIGH -> LOW) on these pins will cause the corresponding
# bin in REG_SC to go high.  To clear a change bit, write a 0 to the 
# corresponding bit in the REG_SCC registor.  
#
# Also note that the value read from REG_SCC is meaningless, it is just
# the actual write operation that matters.
#
# Finally, note that a "change" on inputs is defined as a stable condition
# that lasts at least 10 msec. Pulses less than 10 msec in width may or may
# not be captured.

reg_table = ((SIGV,"SIGV"), (BAT,"BAT"), (DTME1,"DTME1"), (DTME2,"DTME2"),
    (DTME3,"DTME3"), (DTME4,"DTME4"), (A1,"A1"), (A2,"A2"), (A3,"A3"),
    (A6, "A6"), (A7,"A7"), (SI,"SI"), (SC,"SC"), (SCC,"SCC"), (PWM9,"PWM9"),
    (PWM10,"PWM10"), (PWM11,"PWM11"), (XXX0,"XXX0"), (XXX1,"XXX1"), (XXX2,"XXX2"))

analog_chans = (A1, A2, A3, A6, A7)
pwm_chans = (PWM9, PWM10, PWM11)

def get_reg_names():
    '''Provides a list of registor names. '''
    names = []
    for r in reg_table:
        _ , n = r 
        names.append(n)
    return names

def adr2name(i):
    '''Returns a registor's name when given it's number.'''
    for r in reg_table:
        ii, n = r
        if ii == i: return n
    return "?" 

def name2adr(n):
    '''Returns a registor's number when given it's name.'''
    i = 0
    for r in reg_table:
        i, nn = r 
        if n == nn: return i 
    return -1

class Arduino_wb():
    ''' Manages arduino that is embedded in the water bot. '''
    def __init__(self, address=default_addr, bus_number=default_bus):
        self._addr = address
        self._bus_number = bus_number
        self._bus = SMBus(bus_number)
        self._bus_err_count = 0
        self._bus_fail_callback = None

    def writereg(self, regadr, dat):
        ''' Reads a register from the arduino.  This is done without
        protection against errors on the I2C bus. '''
        self._bus.write_byte_data(self._addr, regadr, dat)

    def readreg(self, regadr):
        ''' Writes to a register on the arduino.  This is done without
        protection against errors on the I2C bus. '''
        return self._bus.read_byte_data(self._addr, regadr)

    def _fourbytestolong(self, u3, u2, u1, u0):
	    x = (u3 << 24) + (u2 << 16) + (u1 << 8) + u0
	    return x

    def get_reg_names(self):
        '''Provides a list of registor names. '''
        return get_reg_names()

    def adr2name(self, i):
        '''Returns a registor's name when given it's number.'''
        return adr2name(i)

    def name2adr(self, n):
        '''Returns a registor's number when given it's name.'''
        return name2adr(n)

    def get_version(self):
        id = self.readreg(SIGV)
        return id

    def get_timestamp_bytes(self):
        ''' Returns the individule bytes that make up the timestamp '''
        u0 = self.readreg(DTME1)
        u1 = self.readreg(DTME2)
        u2 = self.readreg(DTME3)
        u3 = self.readreg(DTME4)
        return (u0, u1, u2, u3)

    def get_timestamp(self):
        ''' Returns the time count (ms since power up) from the arduino.  '''
        u0, u1, u2, u3 = self.get_timestamp_bytes()
        tt = self._fourbytestolong(u3, u2, u1, u0)
        return tt

    def get_battery_voltage(self):
        ''' Returns the battery voltage from the arduino. '''
        batv = self.readreg(BAT)
        batv = batv / 10.0
        return batv

    def get_analog(self, channel):
        ''' Returns scaled analog reading from arduino
        
            Channel number can be constants from the reg map, such as A6
            or the string names can be used, such as "A6".   
            Return range: 0.0 to 1.0''' 
        ichan = -1
        if type(channel) is str: 
            ichan = self.name2adr(channel)
        if type(channel) is int:
            ichan = channel
        if ichan < 0: raise Exception("Bad input arg.")
        okay = False
        for i in analog_chans:
            if i == ichan: okay = True 
        if not okay: raise Exception("Unknown analog channel.")
        a = self.readreg(ichan)
        va = a / 255.0
        return va

    def get_digital(self, pin):
        ''' Returns a boolean for the given pin name or number. 
        
            Possible pin names are: D8, D7, D6, D5, D4, D3.  
            Possible pin numbers are 8, 7, 6, 5, 4, and 3. '''
        ipin = -1
        if type(pin) is str:
            for x in (("D8", 8), ("D7", 7), ("D6", 6), ("D5", 5), ("D4", 4), ("D3", 3)):
                n, i = x 
                if pin == n: ipin == i
        if type(pin) is int:
            ipin = pin
        if ipin < 3 or ipin > 8 : raise Exception("Bad input arg.")
        dat = self.readreg(SI)
        ibit = ipin - 3
        v = (dat >> ibit) & 0x01
        if v != 0: return True
        else: return False

    def clear_change_bits(self):
        ''' Clear all change bits on the digital inputs '''
        self.writereg(SCC, 0)

    def set_pwm(self, chan, v):
        ''' Sets the pwm value on a channel.  

        The chan can be the string name of a registor such as "PWM10", or its 
        address from the table above.  If chan == "ALL" or 0, then all pwm
        channels are set.  The value is from 0.0 to 1.0. '''
        iv = int(v * 255)
        if iv < 0: iv = 0
        if iv > 255: iv = 255
        ichan = -1
        if type(chan) is str:
            if chan == "ALL" or chan == "all" or chan == "All": ichan = 0
            else: ichan = self.name2adr(chan)
        if type(chan) is int:
            ichan = chan
        if ichan == 0: 
            for i in pwm_chans:
                self.writereg(i, iv)
            return
        okay = False
        for i in pwm_chans:
            if ichan == i: okay = True
        if not okay: raise Exception("Unknown or invalid channel.")
        self.writereg(ichan, iv)

    def get_pwm(self, chan):
        ''' Gets the current pwm setting (0-1) on the given chan.
        The chan can be the string name of a registor such as "PWM10", or its 
        address from the table above. '''
        ichan = -1
        if type(chan) is str:
            ichan = self.name2adr(chan)
        if type(chan) is int:
            ichan = chan
        okay = False
        for i in pwm_chans:
            if ichan == i: okay = True
        if not okay: raise Exception("Unknown or invalid channel.")
        iv = self.readreg(ichan)
        return (iv / 255.0)

    def get_all(self):
        ''' Reads all the registers in the arduino and returns them in a
        list of bytes. '''
        d = []
        for i in range(LAST + 1):
            v = self.readreg(i)
            d.append(v)
        return d

