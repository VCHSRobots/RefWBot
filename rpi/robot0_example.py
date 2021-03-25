# robot_ref.py -- Reference Robot -- User Code
#
# This file is an example -- You should rename it to something
# like robot_my_team_name.py, and change the contents for
# your bot.  
#
# The runbot.py code will call your code that you place in
# this file to run the robot.  For this to work, you must
# follow the structure in this example.  That is, you cannot
# change the class name, and you must provide the functions
# in the class.

import hydromotor
import toggle
import motor775
import electromagnet
import limitswitch

class WaterBot():
    def __init__(self, base_sys):
        ''' This inits your custom class -- do nothing here
        as the base code has not started up yet.'''
        self.base = base_sys

    def initialize(self):
        ''' Called during initialization.  This is the place
        that you should create the objects that control the 
        robot.  The base system is already mostly initialized
        so that you can access the features of the base code.'''
        self.left_motor = hydromotor.HydroMotor(self.base.pca, 4)
        self.right_motor = hydromotor.HydroMotor(self.base.pca, 5)
        self.hydrodrive = hydromotor.HydroDrive(self.left_motor, self.right_motor)
        self.elecmag = electromagnet.ElectroMagnet(self.base.arduino, 10)
        self.switch = limitswitch.LimitSwitch(self.base.arduino, 3)
        self.hydrodrive.shutdown()
        self.elecmag.turn_off()

    def stop(self, loop_count):
        ''' Called repeatedly when the robot is in stop mode.'''
        if loop_count == 0:
          print("**** Switching to STOP")
          self.base.pca.killall()
          self.elecmag.turn_off()

    def auto(self, loop_count):
        ''' Called repeatedly when the robot is in auto mode.
        On the first call after a mode change, loopcount is zero,
        and then it increases by one for succeding calls.'''
        if loop_count == 0:
          print("**** Switching to AUTO")
          self.base.pca.killall()
          self.elecmag.turn_off()
    
    def teleop(self, loop_count):
        ''' Called repeatedly when the robot is in teleop mode.
        On the first call after a mode change, loopcount is zero,
        and then it increases by one for succeding calls.'''
        if loop_count == 0:
            print("**** Switching to TELEOP")
            self.hydrodrive.start()
            self.elecmag.turn_off()
        x, y, z, _, _, _ = self.base.axes0
        self.base.pca.set_servo(15, z)
        self.hydrodrive.move(x, y)
        if self.switch.get_value():
          self.elecmag.turn_on()
        else:
          self.elecmag.turn_off()
