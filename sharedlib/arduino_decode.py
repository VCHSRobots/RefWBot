# arduino_decode.py -- Translate raw data from the arduino
# EPIC Robotz, dlb, Mar 2021

import arduino_reg_map as reg

def fourbytestolong(u3, u2, u1, u0):
    ''' Convert four bytes into a long.  Note the order of the bytes:
    the MSB is the first argument, and the LSB is the last argument. ''' 
    x = (u3 << 24) + (u2 << 16) + (u1 << 8) + u0
    return x

def dat_to_battery_voltage(dat):
    f = dat / 10.0
    return  f

def bit_to_bool(dat, bit):
    ''' Returns a boolean for the given bit in dat. '''
    mask = 1 << bit
    if dat & mask != 0: return True
    return False

def data_to_dict(strdata):
    ''' Converts the input list of bytes from the arduino's registers
    to a dictionary containing  parameter values.  The Key names
    mostly follow the register names.  See code below for actual
    key names. '''
    data = []
    words = strdata.split()
    for w in words:
        try:
            v = int(w)
        except ValueError:
            v = 0
        data.append(v)
    dout = {}
    if len(data) >= reg.SIGV:
        dout["SIGV"] = "%c" % data[reg.SIGV]
    if len(data) >= reg.BAT:
        dout["BAT"] = dat_to_battery_voltage(data[reg.BAT])
    if len(data) >= reg.DTME4:
        u0, u1, u2, u3 = data[reg.DTME1], data[reg.DTME2], data[reg.DTME3], data[reg.DTME4]
        dout["DTME"] = fourbytestolong(u3, u2, u1, u0)
    if len(data) >= reg.A1:
        dout["A1"] = data[reg.A1] / 255.0
    if len(data) >= reg.A2:
        dout["A2"] = data[reg.A2] / 255.0
    if len(data) >= reg.A3:
        dout["A3"] = data[reg.A3] / 255.0
    if len(data) >= reg.A6:
        dout["A6"] = data[reg.A6] / 255.0
    if len(data) >= reg.A7:
        dout["A7"] = data[reg.A7] / 255.0
    if len(data) >= reg.SI:
        dout["SI"] = data[reg.SI]
        dout["D3"] = bit_to_bool(data[reg.SI], 0)
        dout["D4"] = bit_to_bool(data[reg.SI], 1)
        dout["D5"] = bit_to_bool(data[reg.SI], 2)
        dout["D6"] = bit_to_bool(data[reg.SI], 3)
        dout["D7"] = bit_to_bool(data[reg.SI], 4)
        dout["D8"] = bit_to_bool(data[reg.SI], 5)
    if len(data) >= reg.SC:
        dout["SC"] = data[reg.SC]
    if len(data) >= reg.SCC:
        dout["SCC"] = data[reg.SCC]
    if len(data) >= reg.PWM9:
        dout["PWM9"] = data[reg.PWM9] / 255.0 
    if len(data) >= reg.PWM10:
        dout["PWM10"] = data[reg.PWM10] / 255.0 
    if len(data) >= reg.PWM11:
        dout["PWM11"] = data[reg.PWM11] / 255.0 
    return dout
    


 




