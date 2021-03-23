# joystick.py -- Provides access to the joystick
# EPIC Robots, dlb, Feb 2021
#
# March 2021 -- rewriten to make it simpler.
#
# This code is intended to provide a platform independent api for 
# obtaining joystick information.  However, currently it 
# entirely depends on rawjoystick_win -- meaning, for now, 
# only Windows is supported.  

import platform
import sys

if platform.system() == "Windows":
    import rawjoystick_win as js 
elif platform.system() == "Linux":
    ### TODO: must rewrite joystick_linux to be rawjoystick_linux!!
    ### import rawjoystick_linux as js
    print("rawjoystick_linux.py not implemented.")
    sys.exit()
else:
    print("Unknown Platform -- no Joystick Driver Implemented.")
    sys.exit()


known_devices = ("Logitech 3D Pro", "XBox Gamepad", "Generic USB Gamepad")

def get_devices():
    ''' Returns a list of joystick devices, where each device is
        a tuple in the form (name, instance) which uniquely identifies
        a usable joystick that is known to the system. This does not
        mean that the joystick is actually connected to the system. '''
    return js.get_devices()

class Joystick():
    def __init__(self, name, instance):
        ''' Initializes this object to work with a joystick/gamepad device
        with the given name and instance.  The first instance of a named 
        device is zero, and the second is one, and so forth.  This class
        may be instantiated for a device not yet connected to the system.'''
        self._name = name
        self._instance = instance
    
    def is_initialized(self):
        ''' Returns True if the joystick is known to the system
        weither or not it is connected.  The joystick must be
        known for the other get functions to be valid.'''
        return js.is_known(self._name, self._instance)
    
    def is_connected(self):
        ''' Returns true if the joystick seems to be connected. '''
        return js.is_connected(self._name, self._instance)

    def get_name(self):
        ''' Returns the name for the device.'''
        return self._name

    def get_buttons(self):
        ''' Returns a list of at least 12 booleans that indicate 
        the state of the buttons on the joystick.  If the joystick
        is not connected, or there is an error -- False for each
        button is returned.'''
        _, btns = js.get_buttons(self._name, self._instance)
        return btns
  
    def get_axes(self):
        ''' Returns a list of six floats (-1 to +1) describing the joystick's axis.
        If there is an error or the joystick is not connected or the axis doesn't exist,
        zeros are returned. If the axis does not exist, zero are provided. '''
        _, axes = js.get_axes(self._name, self._instance)
        return axes
  
    def get_pov(self):
        ''' Returns the x-y position of the joystick's pov hat. If there is an error, 
        the joystick is not connected, or the joystick does not have a hat,
        zeros are returned. '''
        _, pov = js.get_pov(self._name, self._instance)
        return pov
