# robot_example.py -- experiment with loading modules on the fly...

class WaterBot():
    ''' This class defines custom code for your water robot.'''
    def __init__(self, base_sys):
        print("Initing the WaterBot Class")
        self.base = base_sys

    def tryfunc(self):
        print("in Try Func.")
        self.base.back_to_you()

