# electromagnet.py -- Driver for electromagnet
# EPIC Robots, dlb, Mar 2021

class ElectroMagnet():
  def __init__(self, arduino, pwmnum):
    ''' The pwmnum can be 9, 10, or 11 or it can be
    the string name, such as "PWM10".''''
    self.arduino = arduino
    if type(pwmnum) is str:
      self.pwmpin = pwmnum
    else if type(pwmnum) is int:
      self.pwmpin = "PWM%d" % pwmnum
    else:
      raise ValueError("Bad pwm pin number.")

  def turn_on(self):
    self.arduino.set_pwm(self.pwmpin, 1.0)

  def turn_off(self):
    self.aeduino.set_pwm(self.pwmpin, 0.0)