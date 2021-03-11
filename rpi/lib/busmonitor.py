# busmonitor.py -- Provides monitor and alerts for I2C errors
# EPIC Robotz, dlb, Mar 2021

class BusMonitor():
    def __init__(self, alert_cb=None):
        self._alert_cb = alert_cb
        self.reset()

    def set_alert_callback(self, cb):
        ''' Set the callback for an alert. '''
        self._alert_cb = cb

    def reset(self):
        ''' Reset the monitor, usually called after a bus restart.'''
        self._total_err_count = 0
        self._total_success_count = 0   
        self._sequential_err_count = 0  # Number of errors in a row
        self._on_alert = False
    
    def on_success(self, activity="", nwrites=0, nreads=0):
        ''' Call this on success of bus read or write. '''
        self._total_success_count += 1
        self._sequential_err_count = 0
    
    def on_fail(self):
        ''' Call this on fail.  If conditions seem super bad, an
        alert will be raised. '''
        self._total_err_count += 1
        self._sequential_err_count += 1
        self.analyze()

    def analyze(self):
        ''' Analyzes the bus traffic. Will invoke the
            alert callback if bus seems like it is broken.'''
        if self._sequential_err_count > 10:
            self._on_alert = True
            if self._alert_cb:
                self._alert_cb() 
    
    def in_alert(self):
        ''' Returns True if an alert has been declared.'''
        return self._on_alert

    def get_total_error_count(self):
        ''' Returns the total error count. '''
        return self._total_err_count

    
