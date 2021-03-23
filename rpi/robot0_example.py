# robot0_example.py -- Example user code for a Water Bot
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
#

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
        pass

    def stop(self, loopcount):
        ''' Called repeatedly when the robot is in stop mode.'''
        pass

    def auto(self, loopcount):
        ''' Called repeatedly when the robot is in auto mode.
        On the first call after a mode change, loopcount is zero,
        and then it increases by one for succeding calls.'''
        pass
    
    def teleop(self, loopcount):
        ''' Called repeatedly when the robot is in teleop mode.
        On the first call after a mode change, loopcount is zero,
        and then it increases by one for succeding calls.'''
        pass