# joystick.py -- Provides access to the joystick
# EPIC Robots, dlb, Feb 2021
#
# This code is intended to provide a platform independent api for 
# obtaining joystick information.  However, currently it 
# entirely depends on rawjoystick_win -- meaning, for now, 
# only Windows is supported.
#
# Notes on Idenification
# ----------------------
# Joystick devices are Human Interface Devices (HID) which plug
# into a USB port, and as such they are identified with a Manufacture's ID and
# a Product ID, known as the MID and PID. From experiments, we have built the
# following table:
#
#    MID    PID   Style           Description
#    ---    ---   -----           -----------
#   1133  49685   Logitech 3D     Logitech Extreme 3D Pro Joystick
#    121      6   Noname Gamepad  Noname copy of X-Box Gamepad
#   1118    767   XBox Gamepad    X Box Gamepad with removable USB wire
#
# The style and description are our own designations for the MID
# and PID.  They are returned by the get_style() and 
# get_description() functions, and appear in the tuple returned from
# get_devices().
#  

import rawjoystick_win as js 

known_devices = (
    ((1133, 49685), "Logitech 3D", "Logitech Extreme 3D Pro Joystick"),
    ((121,      6), "Noname Gamepad", "Noname copy of X-Box Gamepad"),
    ((1118,  767), "XBox Gamepad", "X Box Gamepad with removable USB wire"))

def get_devices():
    ''' Returns a list of joystick devices, where each device is
        a tuple in the form (id, name, mid, pid, style, desc), where id is
        the identifier given by the OS, name is the name 
        found in the driver for the device, mid is the
        manufacture's id, pid is the product id, style is the known
        model name, and desc is the description of the device. Style
        and description are obtianed from an internal table derived by
        experimentation. '''
    num = js.joyGetNumDevs()
    x = []
    for id in range(num):
        okay, caps = js.joyGetDevCaps(id)
        if okay:
            style, desc = "", ""
            for midpid, s, d in known_devices:
                if midpid == (caps.wMid, caps.wPid):
                    style, desc = s, d
                    break
            x.append((id, caps.szPname, caps.wMid, caps.wPid, style, desc))
    return x

class Joystick():
    def __init__(self, id=-1, style=""):
        ''' Initializes this object to work with the given joystick id or style.
        If neither the id nor style is given, then the first joystick found on the 
        system is used.  If the id is given, then it is used.  Otherwise, if
        style is given, the first joystick with that style is used.'''
        self._isconnected = False
        self._is_inited = False    
        self._errcount = 0
        self._id = id
        self._style = style
        self._desired_midpid = (0, 0)
        if self._style != "":
            found = False
            for midpid, n, _ in known_devices:
                if self._style == n: 
                    self._desired_midpid = midpid
                    found = True
            if not found:
                raise ValueError("Unknown Joystick Style: %s" % self._style)
        self._name = ""
        self._numaxis = 0
        self._numbtns = 0
        self._midpid = (0, 0)
        self.reset()

    def _findjoystick(self):
        ''' Attemps to find the proper joystick's system id '''
        if self._id >= 0: return
        joylist = get_devices()
        if self._desired_midpid != (0, 0):
            for i, _ , mid, pid, _, _ in joylist:
                if (mid, pid) == self._desired_midpid:
                    self._id = i
                    return
            return
        if len(joylist) > 0:
            self._id = joylist[0][0]
        
    def reset(self):
        ''' Attempts to reconnect and re-init the joystick.'''
        if self._id < 0:
            self._findjoystick()
            if self._id < 0: return
        okay, caps = js.joyGetDevCaps(self._id)
        if not okay: return
        self._is_inited = True
        self._name = caps.szPname
        self._numbtns = caps.wNumButtons
        self._numaxis = caps.wNumAxes
        self._midpid = (caps.wMid, caps.wPid)
        self.get_axis()

    def is_initialized(self):
        ''' Returns True if the joystick is known to the system
        weither or not it is connected.  The joystick must be
        known for the other get functions to be valid.'''
        return self._is_inited
    
    def is_connected(self):
        ''' Returns true if the joystick seems to be connected. '''
        self.get_axis()
        return self._isconnected

    def get_id(self): 
        ''' Returns the system id for device. '''
        return self._id

    def get_name(self):
        ''' Returns the system name for the device.  If the
        joystick is not connected, or there is some other
        error, a blank string is returned.'''
        if not self._is_inited: self.reset()
        return self._name

    def get_midpid(self):
        ''' Returns a tuple of the device's MID and PID. See
        comments above for more explaniation. '''
        if not self._is_inited: self.reset()
        return self._midpid

    def get_style(self):
        ''' Returns a style designator for the device, if known.'''
        if not self._is_inited: self.reset()
        for midpid, style, _ in known_devices:
            if midpid == self._midpid: return style
        return "Unknown"

    def get_description(self):
        ''' Returns a description of the device, if known.'''
        if not self._is_inited: self.reset()
        for midpid, _, desc in known_devices:
            if midpid == self._midpid: return desc
        return "(blank)"

    def get_number_of_buttons(self):
        ''' Returns the number of known buttons on the connected
        joystick.  If the joystick is not initialized, or there is
        some other error, zero is returned.'''
        if not self._is_inited: self.reset()
        return self._numbtns

    def get_number_of_axes(self):
        ''' Returns the number of known axes on the connected
        joystick.  If the joystick is not initalized, or there is
        some other error, zero is returned.'''
        if not self._is_inited: self.reset()
        return self._numaxis
    
    def get_buttons(self):
        ''' Returns a list of at least 12 booleans that indicate 
        the state of the buttons on the joystick.  If the joystick
        is not connected, or there is an error -- False for each
        button is returned.'''
        if not self._is_inited: self.reset()
        if not self._is_inited:
            return [False for i in range(12)]
        okay, info = js.joyGetPosEx(self._id)
        if not okay:
            self._isconnected = False
            return [False for i in range(12)]
        self._isconnected = True
        btns = [(1<<i) & info.dwButtons != 0 for i in range(self._numbtns)]
        if len(btns) < 12:
            n = 12 - len(btns)
            for _ in range(n): btns.append(False)
        return btns
    
    def get_axis(self):
        ''' Returns a list of three floats (-1 to +1) describing the joystick's XYZ axis.
        If there is an error or the joystick is not connected, zeros are returned. '''
        if not self._is_inited: self.reset()
        if not self._is_inited: 
            return [0, 0, 0]
        okay, info = js.joyGetPosEx(self._id)
        if not okay:
            self._isconnected = False
            return [0.0, 0.0, 0.0]
        self._isconnected = True
        x,y,z = (info.dwXpos - 32678)/32768.0, (info.dwYpos - 32678)/32768.0, (info.dwZpos - 32678)/32768.0
        x,y,z = -x, -y, -z  
        return (x, y, z)

    def get_ruv(self):
        ''' Returns a list of three floats (-1 to +1) describing the joystick's rotational axis.
        For Logitech this is the second set of axis.  If there is an error, or the joystick is
        not connected, zeros are returned. '''
        if not self._is_inited: self.reset()
        if not self._is_inited: 
            return [0, 0, 0]
        okay, info = js.joyGetPosEx(self._id)
        if not okay: 
            self._isconnected = False
            return [0.0, 0.0, 0.0]
        r, u, v = (info.dwRpos - 32678)/32768.0, (info.dwUpos - 32678)/32768.0, (info.dwVpos - 32678)/32768.0
        return (r, u, v)
