# utils.py -- Utilities for the water bot software
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

def str_to_bool(s):
    if s.upper() == "TRUE": return True
    return False

def extendstr(s, n):
    ''' Extends s so that it is n chars long.  Spaces are 
    added to extend the string. If the length of s is 
    already greater than or equal to n, nothing is done.'''
    nadd = n - len(s)
    if nadd <= 0: return s 
    sext = ""
    for _ in range(nadd):
        sext += " "
    return s + sext

def abs(x):
  ''' Returns the absolute value of a number. '''
  if x < 0.0: return -x  
  else: return x

def clamp(v, v0, v1):
  ''' Returns a clammped value.  If v is less then v0,
  v0 is returned. If v is greater then v1, v1 is returned.
  Otherwize, v is returned unchanged. '''
  if v > v1: return v1
  if v < v0: return v0
  return v



    

  