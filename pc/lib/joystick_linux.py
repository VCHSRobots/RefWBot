# joystick_linux.py -- Interfaces with a Logitech joystick on Linux
# hp Feb 2021

import ctypes

from inputs import devices

import pygame

#Known styles and guids
#The first part of the guid is taken as the mid and the latter half is taken as the pid
known_devices = {
    "Holiday's Xbox": ("03000000c62400001", "a56000001010000"),
    "Logitech 3D": "",
    "Noname Gamepad": "",
}

pygame.init()

def get_devices():
    return [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]

def openGamepad(j=0):
    global joy
    ''' Opens the first suitable gamepad found connected to the computer.  
        Returns True if a suitable gamepad is opened. False otherwise. '''
    if len(joysticks) > j:
        joy = joysticks[j]
        joy.init()
        return True
    else:
        return False

def haveGamepad():
    ''' Returns True if a valid gamepad is opened. False otherwise. '''
    return joy is not None

def getGamepadButtons():
    ''' Return a list of at list 12 booleans describing the joystick's button status '''
    if not haveGamepad(): return [False for i in range(12)]
    pygame.event.get()
    btns = [joy.get_button(x) for x in range(joy.get_numbuttons())] #TODO
    if len(btns) < 12:
        n = 12 - len(btns)
        for i in range(n): btns.append(False)
    return btns

def getGamepadAxis():
    ''' Return a list of three floats (-1 to +1) describing the joystick's XYZ axis '''
    if not haveGamepad(): return (0, 0, 0)
    pygame.event.get()
    axes = [joy.get_axis(x) for x in range(joy.get_numaxes())]
    x, y, z = axes[0], axes[1], axes[2]
    return (x, y, z)

def getGamepadRot():
    ''' Return a list of three floats (-1 to +1) describing the joystick's rotational axis '''
    if not haveGamepad(): return (0, 0, 0)
    #TODO
    r, u, v = (0, 0, 0)
    return (r, u, v)

def printEvents():
    while True:
        events = device.device.read()
        for event in events:
            print(event.ev_type, event.code, event.state)

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
        self._desired_midpid = ("", "")
        if self._style != "":
            print(known_devices)
            for n in known_devices:
                if self._style == n: self._desired_midpid = known_devices[n]
        self._name = style
        self._numaxis = 0
        self._numbtns = 0
        self._midpid = ("", "")
        #Stored joystick object for this class
        #Sholud never be none if the joystick is inited
        self.joy = None
        self.reset()

    def _findjoystick(self):
        ''' Attemps to find the proper joystick's system id '''
        joylist = get_devices()
        if self._desired_midpid != (0, 0):
            for i in range(len(joylist)):
                joy = joylist[i]
                guid = joy.get_guid()
                mid = guid[:16]
                pid = guid[16:]
                if (mid, pid) == self._desired_midpid:
                    self._id = i
                    self.joy = joy
                    return
        if self._id >= 0:
            joy = joylist[self._id]
            self.joy = joy
            joy.init()
            return
        if len(joylist) > 0:
            self._id = 0
            self.joy = joylist[0]
            self.joy.init()
            return
        
    def reset(self):
        ''' Attempts to reconnect and re-init the joystick.'''
        if self.joy is not None:
            self.joy.quit()
        self._findjoystick()
        self._is_inited = True
        self._name = self._style
        self._numbtns = self.joy.get_numbuttons()
        self._numaxis = self.joy.get_numaxes()
        guid = self.joy.get_guid()
        self._midpid = (guid[:16], guid[16:])
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
        self._is_inited = self.joy.get_init()
        if not self._is_inited: self.reset()
        if not self._is_inited:
            return [False for i in range(12)]
        self._isconnected = True
        pygame.event.get()
        btns = [self.joy.get_button(x) for x in range(self._numbtns)]
        if len(btns) < 12:
            n = 12 - len(btns)
            for i in range(n): btns.append(False)
        return btns
    
    def get_axis(self, axis_number=0, axis_interval = 3):
        ''' Returns a list of three floats (-1 to +1) describing the joystick's XYZ axis.
        If there is an error or the joystick is not connected, zeros are returned. '''
        vals = [0, 0, 0]
        self._is_inited = self.joy.get_init() 
        
        if not self._is_inited: self.reset()
        if not self._is_inited: 
            return [0, 0, 0]
        self._isconnected = True
        pygame.event.get()
        axes = [self.joy.get_axis(x) for x in range(self._numaxis)[axis_number*3:(axis_number+1)*axis_interval]]
        for i in range(len(axes[:3])):
            vals[i] = axes[i]
        return vals

    def get_ruv(self):
        ''' Returns a list of three floats (-1 to +1) describing the joystick's rotational axis.
        For Logitech this is the second set of axis.  If there is an error, or the joystick is
        not connected, zeros are returned. '''
        #Call updated get_axis function so old code doesn't break
        return self.get_axis(1)

    def get_hat(self, hat=0):
        ''' Returns the x-y position of the joystick's hat. Only applicable to the XBox Controller
        If there is an error, the joystick is not connected, or the joystick does not have a hat,
        zeros are returned. '''
        self._is_inited = self.joy.get_init()
        if not self._is_inited: self.reset()
        if not self._is_inited:
            return [0, 0]
        pygame.event.get()
        x, y = self.joy.get_hat(hat)
        return (x, y)
