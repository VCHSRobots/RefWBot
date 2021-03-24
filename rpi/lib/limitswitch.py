# limitswitch.py -- LimitSwitch class -- controls a limit switch.
# EPIC Robots, dlb, Mar 2021
#

class LimitSwitch():
  def __init__(self, arduino, pin):
    ''' The pin can be 3-8, or "D3" - "D8".  See
    arduino_wb.py for more info'''
    self.arduino = arduino
    self.pin = pin
  
  def get_value(self):
    ''' Returns the condition of the limit switch.'''
    _, val = self.arduino.get_digital(self.pin)
    return val