# arduino_wb.py -- access to the arduino on the water bot
# EPIC Robotz, dlb, Mar 2021

import sys
from smbus import SMBus
import time
import arduino_reg_map as reg
import arduino_decode as decode

default_addr = 0x8 # bus address of ardunio
default_bus = 1 # indicates /dev/ic2-1

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

    def get_reg_names(self):
        '''Provides a list of registor names. '''
        return reg.get_reg_names()

    def adr2name(self, i):
        '''Returns a registor's name when given it's number.'''
        return reg.adr2name(i)

    def name2adr(self, n):
        '''Returns a registor's number when given it's name.'''
        return reg.name2adr(n)

    def get_version(self):
        id = self.readreg(reg.SIGV)
        return id

    def get_timestamp_bytes(self):
        ''' Returns the individule bytes that make up the timestamp '''
        u0 = self.readreg(reg.DTME1)
        u1 = self.readreg(reg.DTME2)
        u2 = self.readreg(reg.DTME3)
        u3 = self.readreg(reg.DTME4)
        return (u0, u1, u2, u3)

    def get_timestamp(self):
        ''' Returns the time count (ms since power up) from the arduino.  '''
        u0, u1, u2, u3 = self.get_timestamp_bytes()
        tt = decode.fourbytestolong(u3, u2, u1, u0)
        return tt

    def get_battery_voltage(self):
        ''' Returns the battery voltage from the arduino. '''
        batv = self.readreg(reg.BAT)
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
        for i in reg.analog_chans:
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
        dat = self.readreg(reg.SI)
        ibit = ipin - 3
        v = (dat >> ibit) & 0x01
        if v != 0: return True
        else: return False

    def clear_change_bits(self):
        ''' Clear all change bits on the digital inputs '''
        self.writereg(reg.SCC, 0)

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
            for i in reg.pwm_chans:
                self.writereg(i, iv)
            return
        okay = False
        for i in reg.pwm_chans:
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
        for i in reg.pwm_chans:
            if ichan == i: okay = True
        if not okay: raise Exception("Unknown or invalid channel.")
        iv = self.readreg(ichan)
        return (iv / 255.0)

    def get_all(self):
        ''' Reads all the registers in the arduino and returns them in a
        list of bytes. '''
        d = []
        for i in range(reg.LAST + 1):
            v = self.readreg(i)
            d.append(v)
        return d

