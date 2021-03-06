# utils.py -- Utilities for the drive station
# EPIC Robotz, dlb, Mar 2021

def same_in_tolerance(a, b, tol=0.05):
    ''' Checks to see if the tuples/lists in a and b are the same
    to within a tolarance. '''
    if len(a) != len(b): return False
    for i in range(len(a)):
        delta = a[i] - b[i]
        if delta < 0.0: delta = -delta
        if delta > tol: return False
    return True

  