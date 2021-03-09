# arduino_reg_map.py -- Map of Arduino Registers for the Water Bot
# EPIC Robotz, dlb, Mar 2021

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