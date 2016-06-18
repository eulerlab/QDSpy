#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QDSpy module - support routines related to timing and priority

'Clock' 
  Class that provides a high-precision clock and is based on "clock.py", from 
  PsychoPy library Copyright (C) 2015 Jonathan Peirce, Distributed under the
  terms of the GNU General Public License (GPL)
  
'setHighProcessPrior()', 'setNormalProcessPrior()'   
  Routines to increase and reset process priority

Copyright (c) 2013-2016 Thomas Euler
Distributed under the terms of the GNU General Public License (GPL)
"""
# ---------------------------------------------------------------------
__author__ 	= "code@eulerlab.de"

import os
import sys
import QDSpy_global as glb

if glb.QDSpy_incProcessPrior:
  import psutil

# ---------------------------------------------------------------------
# Multiprocessing support
# ---------------------------------------------------------------------     
WORKING, CANCELED, TERMINATING, IDLE = ("Working", "Canceled",
                                        "Terminating", "Idle")
 
# ---------------------------------------------------------------------
# Set the default timing mechanism
# ---------------------------------------------------------------------     
getTime  = None

if sys.platform == 'win32':
  global _fcounter, _qpfreq, _winQPC
  from ctypes import byref, c_int64, windll
  _fcounter = c_int64()
  _qpfreq   = c_int64()
  windll.Kernel32.QueryPerformanceFrequency(byref(_qpfreq))
  _qpfreq   = float(_qpfreq.value)
  _winQPC=windll.Kernel32.QueryPerformanceCounter

  def getTime():
    _winQPC(byref(_fcounter))
    return  _fcounter.value/_qpfreq
    
else:
  cur_pyver = sys.version_info
  if cur_pyver[0]==2 and cur_pyver[1]<=6:
    import time
    getTime = time.time
  else:
    import timeit
    getTime = timeit.default_timer
    
# ---------------------------------------------------------------------
# A high-precision clock
# ---------------------------------------------------------------------
class Clock:
  def __init__(self):
    self.t0_s = getTime()

  def getTime_s(self):
    return getTime() -self.t0_s

  def getOffset_s(self):
    return self.t0_s

defaultClock = Clock()
  
# ---------------------------------------------------------------------
# Increase/decrease process priority
# ---------------------------------------------------------------------  
# psutil.ABOVE_NORMAL_PRIORITY_CLASS
# psutil.BELOW_NORMAL_PRIORITY_CLASS
# psutil.HIGH_PRIORITY_CLASS
# psutil.IDLE_PRIORITY_CLASS
# psutil.NORMAL_PRIORITY_CLASS
# psutil.REALTIME_PRIORITY_CLASS
#
def setHighProcessPrior():
  if glb.QDSpy_incProcessPrior:
    proc      = psutil.Process(os.getpid())
    pyVersion = sys.version_info[0] +sys.version_info[1]/10
    if pyVersion <= 3.4:
      proc.set_nice(psutil.HIGH_PRIORITY_CLASS)
    else:  
      proc.nice(psutil.HIGH_PRIORITY_CLASS)

def setNormalProcessPrior():
  if glb.QDSpy_incProcessPrior:
    proc      = psutil.Process(os.getpid())
    pyVersion = sys.version_info[0] +sys.version_info[1]/10
    if pyVersion <= 3.4:
      proc.set_nice(psutil.NORMAL_PRIORITY_CLASS)
    else:  
      proc.nice(psutil.NORMAL_PRIORITY_CLASS)

# ---------------------------------------------------------------------
