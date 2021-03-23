# rawjoystick_win.py -- Interfaces with a gamepads and joysticks on Window's PC
# EPIC Robotz, dlb, March 2021
#
# Second Version -- uses better code to get more info for stuff like second axis and
# POV hat.  
#
# This interface must be identical to the linux version of the driver.  As follows:
#
#    get_devices()                   -- Returns a list of devices known
#    get_axis(name, instance)        -- Returns a list of 6 floats between -1.0 and 1.0 for axis
#    get_buttons(name, instance)     -- Returns a list of 16 booleans for button presses
#    get_pov(name, instance)         -- Returns an integer representing the direction of the POV hat
#    is_connected(name, instance)    -- Returns True if the joystick/gamepad is connected
#    get_auxinfo(name, instance)     -- Returns a dictionary of name/values items about a device
#
# The 'name' stands for one of the qualified names for known devices to EPIC robots.  Currently
# known devices are:
#
#       Logitech 3D Pro
#       XBox Gamepad
#       Generic USB Gamepad
#
# A ValueError exception should be raised if ANY Other name is used in the api. 
# 
# The 'instance' is an integer specifing which instance of the same device to access.  For
# example, if there are two XBox Gamepads and one Logitech 3D Pro joystick known to the system,
# then the XBox Gamepads would have instance numbers of 0 and 1, and the Logitech joystick would
# have an instance number of 0.  Note that instance numbers begin at zero, and increase by one.
# These are NOT the underlying system Id.  That is, this driver code is responsible for remapping the
# name/instance pair to whatever the operating system uses for the handle to the device.
#
# Note that it is okay to ask for an info about a device with a instance number that is
# currently out-of-range.  As devices are connected, the instance number may become valid.
# In the maintime, zeros and Falses will be returned from the get_axis() and get_buttons()
# functions.
# 
# get_devices() returns a list of tuples, where each tuple is (name, instance).  Only
# known devices will be returned.  It is okay to return devices that are not connected to the
# compter -- as a device can be considered "known" without being connected.  Note however,
# it is expected that the instance number will not change for a given device as it is unconnected
# and reconnected to the computer, at least when the same USB port is used.
#
# get_axis() always returns 6 floats, one float for each axis -- whither the axis for the 
# device exists or not. If the axis doesn't exist, zero is returned.  The floats are scaled
# so that -1.0 and 1.0 represents full range. Note, that this interface means the model for
# axes is one linear actuator per axis -- not the FRC model where an "axis" is
# defined as a control that delivers up to three numbers, one for each orthogonal direction. 
# Therefore, this interface must remap the info from the operating system into this system.
# It is up to the caller (the user) to know which of the floats coorespond to which control
# on the device.  If the device is unconnected, zeros are returns for all axes.
#
# get_buttons() returns a list of 12 booleans -- one for each button on the device.  True is
# returned for buttons that are pressed.  If a device has less than 12 buttons, then False
# is returned for buttons that are missing.  If a device is unconnected, False is returned
# for all buttons.
#
# get_pov() returns a 2-tuple of (x,y) that indicates the direction that the pov switch
# is pointed.  The values of x and y can be -1, 0, or 1 -- to give a posible 9 directions.
#
# is_connected() returns True if the device is connected to the computer and functioning 
# properly.  False otherwise.
#
# In  the future, we will implemnt get_auxinfo() which returns a dictionary with OS specific
# information about the device, such as Pid, Mid, NumOfButtons, NumOfAxis, GUID, Description.
# Only keys for which information is available need be returned. 
#
# Note that this code uses the ctypes package -- which allows interfacing to C libs.  On windows,
# this means that it can interface to Window DLLs.  This code connects to the winmm.dll, which
# provides direct system access to the joysticks.  (This is much leaner than using something like
# pygames, or directx)
#
# Notes on Joystick Idenification
# -------------------------------
# Joystick devices are Human Interface Devices (HID) which plug into a USB port, and as such
# they are identified with a Manufacture's ID and a Product ID, known as the MID and PID.
# From experiments, we have built the following table:
#
#    MID    PID   Name                 Description
#    ---    ---   ----                 -----------
#   1133  49685   Logitech 3D Pro      Logitech Extreme 3D Pro Joystick
#    121      6   Generic USB Gamepad  Noname copy of X-Box Gamepad
#   1118    767   XBox Gamepad         X Box Gamepad with removable USB wire
#
# The name and description are our own designations for the MID and PID that the OS interface
# (at least on Windows) provides.  We map the MID and PID to the names proviced by the
# caller (user).



import ctypes
import time
import ctypes
import winreg
from ctypes.wintypes import WORD, UINT, DWORD
from ctypes.wintypes import WCHAR as TCHAR

# Fetch function pointers
w_joyGetNumDevs = ctypes.windll.winmm.joyGetNumDevs
w_joyGetPos = ctypes.windll.winmm.joyGetPos
w_joyGetPosEx = ctypes.windll.winmm.joyGetPosEx
w_joyGetDevCaps = ctypes.windll.winmm.joyGetDevCapsW
winmmdll = ctypes.WinDLL('winmm.dll')

# Define constants
MAXPNAMELEN = 32
MAX_JOYSTICKOEMVXDNAME = 260

JOY_RETURNX = 0x1
JOY_RETURNY = 0x2
JOY_RETURNZ = 0x4
JOY_RETURNR = 0x8
JOY_RETURNU = 0x10
JOY_RETURNV = 0x20
JOY_RETURNPOV = 0x40
JOY_RETURNBUTTONS = 0x80
JOY_RETURNRAWDATA = 0x100
JOY_RETURNPOVCTS = 0x200
JOY_RETURNCENTERED = 0x400
JOY_USEDEADZONE = 0x800
JOY_RETURNALL = JOY_RETURNX | JOY_RETURNY | JOY_RETURNZ | JOY_RETURNR | JOY_RETURNU | JOY_RETURNV | JOY_RETURNPOV | JOY_RETURNBUTTONS

# Define some structures from WinMM that we will use in function calls.
class JOYCAPS(ctypes.Structure):
    _fields_ = [
        ('wMid', WORD),
        ('wPid', WORD),
        ('szPname', TCHAR * MAXPNAMELEN),
        ('wXmin', UINT),
        ('wXmax', UINT),
        ('wYmin', UINT),
        ('wYmax', UINT),
        ('wZmin', UINT),
        ('wZmax', UINT),
        ('wNumButtons', UINT),
        ('wPeriodMin', UINT),
        ('wPeriodMax', UINT),
        ('wRmin', UINT),
        ('wRmax', UINT),
        ('wUmin', UINT),
        ('wUmax', UINT),
        ('wVmin', UINT),
        ('wVmax', UINT),
        ('wCaps', UINT),
        ('wMaxAxes', UINT),
        ('wNumAxes', UINT),
        ('wMaxButtons', UINT),
        ('szRegKey', TCHAR * MAXPNAMELEN),
        ('szOEMVxD', TCHAR * MAX_JOYSTICKOEMVXDNAME),
    ]

class JOYINFO(ctypes.Structure):
    _fields_ = [
        ('wXpos', UINT),
        ('wYpos', UINT),
        ('wZpos', UINT),
        ('wButtons', UINT),
    ]

class JOYINFOEX(ctypes.Structure):
    _fields_ = [
        ('dwSize', DWORD),
        ('dwFlags', DWORD),
        ('dwXpos', DWORD),
        ('dwYpos', DWORD),
        ('dwZpos', DWORD),
        ('dwRpos', DWORD),
        ('dwUpos', DWORD),
        ('dwVpos', DWORD),
        ('dwButtons', DWORD),
        ('dwButtonNumber', DWORD),
        ('dwPOV', DWORD),
        ('dwReserved1', DWORD),
        ('dwReserved2', DWORD),
    ]

_known_devices = (
    ((1133, 49685), "Logitech 3D Pro", "Logitech Extreme 3D Pro Joystick"),
    ((121,      6), "Generic USB Gamepad", "Noname copy of X-Box Gamepad"),
    ((1118,  767), "XBox Gamepad", "X Box Gamepad with removable USB wire"))

_device_list = []  # devices known by the system: (name, instance, id, naxes, nbts)

def _get_device(name, instance):
    ''' Returns the device record, given name and instance. None returned if
    not found.'''
    for device in _device_list:
        n, i, _, _, _ = device
        if n == name and i == instance: return device
    return None

def _fill_device_list():
    ''' Fills our copy of known devices... '''
    global _device_list
    n = w_joyGetNumDevs() 
    newlist = []
    for id in range(n):
        caps = JOYCAPS()
        result = w_joyGetDevCaps(id, ctypes.pointer(caps), ctypes.sizeof(JOYCAPS))
        if result == 0:
            for midpid, name, _ in _known_devices:
                if midpid == (caps.wMid, caps.wPid):
                    instance = 0
                    for n, i, _, _, _ in newlist:
                        if n == name:
                            if i >= instance: instance = i + 1
                    newlist.append((name, instance, id, caps.wNumAxes, caps.wNumButtons))
    _device_list = newlist 

def _get_state(id, numaxes, numbuttons):
    ''' Gets the complete state of the joystick, returns all info in a tuple.
    of (okayflag, axes, buttons, pov)'''
    info = JOYINFOEX()
    info.dwSize = ctypes.sizeof(JOYINFOEX)
    info.dwFlags = JOY_RETURNBUTTONS | JOY_RETURNCENTERED | JOY_RETURNPOV | JOY_RETURNU | JOY_RETURNV | JOY_RETURNX | JOY_RETURNY | JOY_RETURNZ
    p_info = ctypes.pointer(info)
    axes = [0.0 for _ in range(6)]
    btns = [False for _ in range(12)]
    pov = (0,0)
    result = w_joyGetPosEx(id, p_info)
    if result != 0: return (False, axes, btns, pov)
    x = (info.dwXpos - 32767) / 32768.0
    y = (info.dwYpos - 32767) / 32768.0
    z = (info.dwZpos - 32767) / 32768.0
    r = (info.dwRpos - 32767) / 32768.0
    u = (info.dwUpos - 32767) / 32768.0
    v = (info.dwVpos - 32767) / 32768.0
    axes = [x, y, z, r, u, v]
    for ib in range(12):
        if ib < numbuttons:
            btns[ib] = (0 != (1 << ib) & info.dwButtons)
        else:
            btns[ib] = False
    if info.dwPOV == 65535: pov = (0, 0)
    else:
        ia = int(2 * info.dwPOV / 9000.0)
        dirs = ((0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1))
        pov = dirs[ia]
    return (True, axes, btns, pov)

def get_devices():
    ''' Returns a list of known devices in the system.  The list is composed of
    2-tuples in the form (name, instance) which uniquely identifies the device.'''
    global _device_list
    _fill_device_list()
    dlist = []
    for name, instance, _, _, _ in _device_list:
        dlist.append((name, instance))
    return dlist

def is_connected(name, instance):
    ''' Returns true if the device is connected.'''
    device = _get_device(name, instance)
    if device is None: _fill_device_list()
    device = _get_device(name, instance)
    if device is None: return False
    _, _, id, naxes, nbtns = device
    okayflag, _, _, _ = _get_state(id, naxes, nbtns)
    return okayflag

def is_known(name, instance):
    ''' Returns True if the name/instance is known to the system.  This usually
    means that the device has been previously connected to the computer.'''
    _fill_device_list()
    for n, i, _, _, _ in _device_list:
        if n == name and i == instance: return True
    return False
        
def get_axes(name, instance):
    ''' Returns (okayflag, floats) where okayflag is true if valid data was
    obtained, and floats is a list of six values that indicate the state of
    each axis on the device, where -1 to 1 is full range.'''
    device = _get_device(name, instance)
    if device is None: _fill_device_list()
    device = _get_device(name, instance)
    if device is None:
        return (False, [0.0 for _ in range(6)])
    _, _, id, naxes, nbtns = device
    okay, axes, _, _ = _get_state(id, naxes, nbtns)
    if not okay: 
        return (False, [0.0 for _ in range(6)])
    # Fix Logitech reversed axes here
    if name == "Logitech 3D Pro":
        x, y, z, r, u, v = axes 
        axes = (x, -y, -z, r, u, v)
    # Fix XBox here
    if name == "XBox Gamepad":
        x0, y0, w, y1, x1, v = axes
        z0 = max(-1.0,  w * 2 - 1.0)
        z1 = max(-1.0, -w * 2 - 1.0)
        axes = (x0, -y0, z0, x1, -y1, z1)
    return (True, axes)

def get_buttons(name, instance):
    ''' Returns (okayflag, bools) where okayflag is true if valid data was
    obtained, and bools is a list of 12 booleans that indicate which 
    buttons are being pressed.'''
    device = _get_device(name, instance)
    if device is None: _fill_device_list()
    device = _get_device(name, instance)
    if device is None:
        return (False, [False for _ in range(12)])
    _, _, id, naxes, nbtns = device
    okay, _, btns, _ = _get_state(id, naxes, nbtns)
    if not okay: 
        return (False, [False for _ in range(12)])
    return (True, btns)

def get_pov(name, instance):
    ''' Returns (okayflag, pov) where okayflag is true if valid data was
    obtained, and pov is a 2-tuple in the form of (x, y) where x and y
    can be -1, 0, or 1 -- giving the direction of the pov hat.'''
    device = _get_device(name, instance)
    if device is None: _fill_device_list()
    device = _get_device(name, instance)
    if device is None:
        return (False, (0, 0))
    _, _, id, naxes, nbtns = device
    okay, _, _, pov = _get_state(id, naxes, nbtns)
    if not okay: 
        return (False, (0, 0))
    return (True, pov)








#    get_devices()                          -- Returns a list of devices known
#    get_axis(name, instance_number)        -- Returns a list of 6 floats between -1.0 and 1.0 for axis
#    get_buttons(name, instance_number)     -- Returns a list of 16 booleans for button presses
#    get_pov(name, instance_number)         -- Returns an integer representing the direction of the POV hat
#    is_connected(name, instance_number)    -- Returns True if the joystick/gamepad is connected
#    get_auxinfo(name, instance_number)     -- Returns a dictionary of name/values items about a device

                     





