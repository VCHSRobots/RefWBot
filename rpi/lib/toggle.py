# toggle.py -- toggle for buttons
# IK March 2021

class Toggle():
  def  __init__(self):
      self.state = False
      self.last_reading = False

  def update(self, reading):
        ''' Call to update the state of the toggle.  This must be called
        repeatedly, usually once each time the robot's main loop runs. '''
        if reading == self.last_reading:
            return
        if reading == False and self.last_reading == True:
            self.state = not self.state
        self.last_reading = reading

  def set_state(self, state):
      ''' Sets the state of the toggle.  Usually done at init, or shutdown. '''
      self.state = state

  def get_state(self):
      ''' Returns the value of the toggle. '''
      return self.state

