# arduino.py -- access the arduino on the water bot
# EPIC Robots, dlb, Feb 2021

import sys
from smbus import SMBus
import arduino_reg_map as reg
import time

addr = 0x8 # bus address of ardunio
bus = SMBus(1) # indicates /dev/ic2-1

def writereg(regadr, dat):
	bus.write_byte_data(addr, regadr, dat)

def readreg(regadr):
	return bus.read_byte_data(addr, regadr)

def fourbytestolong(u3, u2, u1, u0):
	x = (u3 << 24) + (u2 << 16) + (u1 << 8) + u0
	return x

def init():
    ''' Initializes software. Checks bus. Returns True if all okay. '''
    try:
        id = readreg(reg.SIGV)
        if id != ord('e'):
            # print("bad return: ", id)
            return False
    except:
        return False 
    return True

def get_version():
    id = readreg(reg.SIGV)
    return id

def get_timestamp_bytes():
    ''' Returns the individule bytes that make up the timestamp '''
    u0 = readreg(reg.DTME1)
    u1 = readreg(reg.DTME2)
    u2 = readreg(reg.DTME3)
    u3 = readreg(reg.DTME4)
    return (u0, u1, u2, u3)

def get_timestamp():
    ''' Returns the time count (ms since power up) from the arduino.  '''
    u0, u1, u2, u3 = get_timestamp_bytes()
    tt = fourbytestolong(u3, u2, u1, u0)
    return tt

def get_battery_voltage():
    ''' Returns the battery voltage from the arduino. '''
    batv = readreg(reg.BAT)
    batv = batv / 10.0
    return batv

def get_analog(channel):
    ''' Returns scaled analog reading from arduino
    
        Channel number can be constants from the reg map, such as reg.A6
        or the string names can be used, such as "A6".   
        Return range: 0.0 to 1.0''' 
    ichan = -1
    if type(channel) is str: 
        ichan = reg.name2adr(channel)
    if type(channel) is int:
        ichan = channel
    if ichan < 0: raise Exception("Bad input arg.")
    okay = False
    for i in reg.analog_chans:
        if i == ichan: okay = True 
    if not okay: raise Exception("Unknown analog channel.")
    a = readreg(ichan)
    va = a / 255.0
    return va

def get_digital(pin):
    ''' Returns a boolean for the given pin name or number. 
    
        Possible pin names are: D8, D7, D6, D5, D4, D3.  
        Possible pin numbers are 8, 7, 6, 5, 4, and 3. '''
    ipin = -1
    if type(pin) is str:
        for x in (("D8", 8), ("D7", 7), ("D6", 6), ("D5", 5), ("D4", 4), ("D3", 3)):
            n, i = x 
            if pin == n: ipen == i
    if type(pin) is int:
        ipin = pin
    if ipin < 3 or ipin > 8 : raise Exception("Bad input arg.")
    dat = readreg(reg.SI)
    ibit = ipin - 3
    v = (dat >> ibit) & 0x01
    if v != 0: return True
    else: return False

def set_pwm(chan, v):
    ''' Sets the pwm value on a channel.  

    The chan can be the string name of a registor such as "PWM10", or its 
    address from the arduino_reg_map, such as reg.PWM10.
    If chan == "ALL" or 0, then all pwm channels are set.
    The value is from 0.0 to 1.0. '''
    ichan = -1
    if type(chan) is str:
        if chan == "ALL" or chan == "all" or chan == "All": ichan = 0
        else: ichan = reg.name2adr(chan)
    if type(chan) is int:
        ichan = chan
    if ichan == 0: 
        for i in reg.pwm_chans:
            writereg(i, v)
        return
    okay = False
    for i in reg.pwm_chans:
        if ichan == i: okay = True
    if not okay: raise Exception("Unknown or invalid channel.")
    iv = int(v * 255)
    if iv < 0: iv = 0
    if iv > 255: iv = 255
    writereg(ichan, iv)






