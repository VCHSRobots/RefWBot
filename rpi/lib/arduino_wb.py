# arduino_wb.py -- access to the arduino on the water bot
# EPIC Robotz, dlb, Mar 2021

import sys
from smbus import SMBus
import RPi.GPIO as gpio
import time
import arduino_reg_map as reg
import arduino_decode as decode
import random

default_addr = 0x8 # bus address of ardunio
default_bus = 1 # indicates /dev/ic2-1

# The D0 and D1 pins are used to restert the arduino in case of massive failure.
d1_pin = 7      # aux data pin D1 connected directly to Arduino
d0_pin = 11     # aux data pin D0 connected directly to Arduino

class Arduino_wb():
    ''' Manages arduino that is embedded in the water bot. '''
    def __init__(self, address=default_addr, bus_number=default_bus, bus_monitor=None):
        self._addr = address
        self._bus_number = bus_number
        self._bus = SMBus(bus_number)
        self._bus_monitor = bus_monitor
        gpio.setwarnings(False)
        gpio.setmode(gpio.BOARD)
        gpio.setup(d0_pin, gpio.OUT)
        gpio.setup(d1_pin, gpio.OUT)
        # Do not allow restart on arduino
        gpio.output(d0_pin, True)
        gpio.output(d1_pin, True)

    def reset_hardware(self):
        ''' Forces a soft reboot on the Arduino without using the I2C bus. This
        can be used to recover from I2C bus errors where the Arduino has locked
        the I2C bus.  If this command finishes successfully, the arduino's timestamp
        will have been reset, and it's PWM registers will be set to zero.  This
        function returns (okayflag, msg) where okayflag will be true if success,
        otherwise it will be False and msg will have a human readable reason for
        failure.  This function takes about 60 ms to run.'''
        gpio.output(d0_pin, False)
        gpio.output(d1_pin, False)
        time.sleep(0.035)   # allow time for arduino to read bits and start reset.
        gpio.output(d0_pin, True)
        gpio.output(d1_pin, True)
        time.sleep(0.025)  # allow time for the arduino to boot. (By experiment, it takes 1-2ms.)
        okay, tme = self.get_timestamp()
        if not okay: return (False, "Unable to get timestamp after reset.")
        okay = self.test_health()
        if not okay: return (False, "Health test fails after reset.")
        if tme > 1000: return (False, "Timestamp (%ld) too large for reset to have occured." % tme)
        return (True, "Reset seems to have occurred correctly.")

    def writereg(self, regadr, dat):
        ''' Reads a register from the arduino.  This is done without
        protection against errors on the I2C bus. '''
        try:
            self._bus.write_byte_data(self._addr, regadr, dat)
            if self._bus_monitor: self._bus_monitor.on_success()
        except IOError:
            if self._bus_monitor: self._bus_monitor.on_fail()
            raise
        except OSError:
            if self._bus_monitor: self._bus_monitor.on_fail()
            raise IOError()
    
    def readreg(self, regadr):
        ''' Writes to a register on the arduino.  This is done without
        protection against errors on the I2C bus. '''
        try:
            dat = self._bus.read_byte_data(self._addr, regadr)
            if self._bus_monitor: self._bus_monitor.on_success()
            return dat
        except IOError:    
            if self._bus_monitor: self._bus_monitor.on_fail()
            raise
        except OSError:
            if self._bus_monitor: self._bus_monitor.on_fail()
            raise IOError()

    def test_health(self):
        ''' Tests the health of the i2c bus and the arduino by writing
        to the spare register and reading it back.  If all okay,
        True is returned. '''
        v = random.randint(0,255)
        try:
            self.writereg(reg.XXX1, v)
            time.sleep(0.00025)
            vgot = self.readreg(reg.XXX1)
            if vgot != v: return False
            return True
        except OSError:
            return False

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
        ''' Returns the signature byte on the arduino as (okayflag, char)
        wehre okayflag is True if all is okay, and char is the signature byte.'''
        try:
            id = self.readreg(reg.SIGV)
        except IOError:
            return False, 0
        return True, id

    def get_timestamp_bytes(self):
        ''' Returns the individule bytes that make up the timestamp, 
        and returns (okayflag, tuple_of_bytes), where okayflag is True
        if all is okay, and tuple_of_bytes contains 4 bytes, with the
        LSB first. '''
        try:
            u0 = self.readreg(reg.DTME1)
            u1 = self.readreg(reg.DTME2)
            u2 = self.readreg(reg.DTME3)
            u3 = self.readreg(reg.DTME4)
        except IOError:
            return False, (0, 0, 0, 0)
        return True, (u0, u1, u2, u3)

    def get_timestamp(self):
        ''' Returns the time count (ms since power up) from the arduino
        as (okayflag, tme), where okayflag is True if all is okay, and
        tme is the timestamp from the arduino in milliseconds since 
        arduino powerup or reset.  '''
        okay, blist = self.get_timestamp_bytes()
        if not okay: return False, 0
        u0, u1, u2, u3 = blist
        tt = decode.fourbytestolong(u3, u2, u1, u0)
        return True, tt

    def get_battery_voltage(self, battype="M"):
        ''' Returns the battery voltage from the arduino as 
        (okayflag, batvolts) where okayflag is True if all is okay,
        and batvolts is the battery voltage.  For robots with multiple
        batteries, the battype selects which battery: "M" for
        motors, or "L" for logic.'''
        r = 0
        if battype == "M": r = reg.BAT_M
        if battype == "L": r = reg.BAT_L
        if r == 0:
            raise ValueError("Unknown battery type.")
        try:
            batv = self.readreg(r)
        except IOError:
            return False, 0.0
        batv = batv / 10.0
        return True, batv

    def get_battery_voltage_motors(self):
        ''' Returns the battery voltage for the motors from the arduino as 
        (okayflag, batvolts) where okayflag is True if all is okay,
        and batvolts is the battery voltage for the motors as a float.'''
        try:
            batv = self.readreg(reg.BAT_M)
        except IOError:
            return False, 0.0
        batv = batv / 10.0
        return True, batv

    def get_analog(self, channel):
        ''' Returns scaled analog reading from arduino, as (okayflag, val)
        where okayflag is True if all seems okay, and val is returned as
        a range between 0.0 and 1.0.  Channel number can be constants from
        the reg map, such as A6 or the string names can be used, such as "A6".  '''
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
        try:
            a = self.readreg(ichan)
        except IOError:
            return False, 0.0
        va = a / 255.0
        return True, va

    def get_digital(self, pin):
        ''' Returns (okayflag, bool) for the given pin name or number. 
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
        try: 
            dat = self.readreg(reg.SI)
        except IOError:
            return False, False
        ibit = ipin - 3
        v = (dat >> ibit) & 0x01
        if v != 0: return True, True
        else: return True, False

    def get_pi_bits(self):
        ''' Returns the PI data bits as (okayflag, data),  where the least significant 2
        bits in data are the aux command bits from the Rpi: D1, D0. '''
        try:
            dat = self.readreg(reg.SI)
        except IOError:
            return False, 0 
        return True, (dat >> 6) & (0x03)

    def clear_change_bits(self):
        ''' Clear all change bits on the digital inputs.  Returns 
        True if no error. '''
        try:
            self.writereg(reg.SCC, 0)
        except IOError:
            return False
        return True

    def set_pwm(self, chan, v):
        ''' Sets the pwm value on a channel.  
        The chan can be the string name of a registor such as "PWM10", or its 
        address from the table above.  If chan == "ALL" or 0, then all pwm
        channels are set.  The value is from 0.0 to 1.0.  If success,
        True is returned.'''
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
            try:
              for i in reg.pwm_chans:
                  self.writereg(i, iv)
            except IOError:
              return False
            return True
        okay = False
        for i in reg.pwm_chans:
            if ichan == i: okay = True
        if not okay: raise Exception("Unknown or invalid channel.")
        try:
            self.writereg(ichan, iv)
        except IOError:
            return False
        return True

    def get_pwm(self, chan):
        ''' Gets the current pwm setting (0-1) on the given chan and
        returns it as (okayflag, val), where okayflag is True if there
        is no error, and val is a number between 0.0 and 1.0.  The
        chan can be the string name of a registor such as "PWM10", or its 
        address from the register table. '''
        ichan = -1
        if type(chan) is str:
            ichan = self.name2adr(chan)
        if type(chan) is int:
            ichan = chan
        okay = False
        for i in reg.pwm_chans:
            if ichan == i: okay = True
        if not okay: raise Exception("Unknown or invalid channel.")
        try:
            iv = self.readreg(ichan)
        except IOError:
            return False, 0.0
        return True, (iv / 255.0)

    def get_all(self):
        ''' Reads all the registers in the arduino and returns them as
        (okayflag, bytes) where okayflag is True if nothing goes wrong,
        and bytes is a list of byte values. '''
        d = []
        try:
            for i in range(reg.LAST_V2 + 1):
                v = self.readreg(i)
                d.append(v)
        except:
            return (False, [0 for _ in range(reg.LAST_V2 + 1)])
        return True, d
