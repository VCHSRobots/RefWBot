# hydromotor.py -- controls the "DYI Underwater Propeller Motor" from ebay
# EPIC Robotz, dlb, Mar 2021

import time
import utils

# Parameters that control motor 
pw_off_default = 1550   # Pulsewidth for off
pw_max_default = 2150   # Pulsewidth in max forward
pw_min_default = 900    # Pulsewidth in max reverse

class HydroMotor():
  def __init__(self, pca, chan, reversed=False, 
      pw_off=pw_off_default, pw_max=pw_max_default, pw_min=pw_min_default):
    self._chan = chan 
    self._pca = pca
    self._inited = False
    self._inwarmup = False
    self._reverse_flag = reversed
    self._time_warmup_start = 0.0
    self._pw_off = int(pw_off)
    self._pw_max = int(pw_max)
    self._pw_min = int(pw_min)

  def start_warmup(self):
    ''' Starts the warmup period for the motor if it hasn't been done
    already. '''
    if self._inited or self._inwarmup: return
    self._pca.set_pwm(self._chan, self._pw_off)
    self._inited = False
    self._inwarmup = True
    self._time_warmup_start = time.monotonic() 

  def set_speed(self, val):
    ''' Sets the motor speed. If it hasn't been warmup,
    that is initiated first.  Warmup takes about 1 second. '''
    if self._inwarmup:
        if time.monotonic() - self._time_warmup_start > 1.0:
          self._inited = True
          self._inwarmup = False
        else:
          return
    if not self._inited:
      self.start_warmup()
      return
    if self._reverse_flag: val = -val 
    if val > 0:
      if val > 1.0: val = 1.0
      span = self._pw_max - self._pw_off 
      pw = int(span * val) + self._pw_off
    else:
      if val < -1.0: val = -1.0
      span = self._pw_off - self._pw_min 
      pw = int(span * val) + self._pw_off
    self._pca.set_pwm(self._chan, pw)

  def shutdown(self):
    ''' Shuts down the motor, and puts it into standby.
    It should spin freely. To use it again, a warmup
    operation is required. '''
    self._inited = False
    self._inwarmup = False
    self._pca.set_pwm(self._chan, 0)

  def is_running(self):
    ''' Returns true if the motor is inited and
    warmed up. '''
    if self._inwarmup:
      if time.monotonic() - self._time_warmup_start > 1.0:
        self._inited = True
        self._inwarmup = False
    return self.inited

class HydroDrive():
    def __init__(self, motorleft, motorright):
      ''' Initialize the HydroDrive with two hydromotors.'''
      self.motor_left = motorleft
      self.motor_right = motorright

    def start(self):
      ''' Start the motors.  They will start warming up at zero power.'''
      self.motor_left.start_warmup()
      self.motor_right.start_warmup()
      self.motor_left.set_speed(0.0)
      self.motor_right.set_speed(0.0)

    def shutdown(self):
      self.motor_left.shutdown()
      self.motor_right.shutdown()

    def move(self, x, y):
      x, y = utils.clamp(x, -1.0, 1.0), utils.clamp(y, -1.0, 1.0)
      left = 0.5 * (x + y) 
      right = 0.5 * (x - y)
      self.motor_left.set_speed(left)
      self.motor_right.set_speed(right)
      


    



