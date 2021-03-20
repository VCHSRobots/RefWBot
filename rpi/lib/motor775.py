# motor775.py -- driver for 775 motor
# IK March 2021

#
# Note, the motor should be off at a pulsewidth of
# 1500 usec, as shown below.  However your motor might
# be different, so you will need experiment to find the
# pulsewidth that turns the motor off, and pass that vaule
# for pw_off when you creae the Motor775 object.

pw_off_default = 1500   # Pulsewidth for off
pw_max_default = 2150   # Pulsewidth in max forward
pw_min_default = 900    # Pulsewidth in max reverse

class Motor775():
    def __init__(self, pca, chan, pw_off=pw_off_default,
            pw_max=pw_max_default, pw_min=pw_min_default):
        self._chan = chan 
        self._pca = pca
        self._pw_off = int(pw_off)
        self._pw_max = int(pw_max)
        self._pw_min = int(pw_min)   

    def set_speed(self, val):
        ''' Sets the motor speed.  '''
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
        It should spin freely.  '''
        self._pca.set_pwm(self._chan, 0)


