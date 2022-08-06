#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QDSpy module - support routines related to timing and priority

'Clock'
  Class that provides a high-precision clock and is based on 
  "clock.py", from PsychoPy library. 
  Copyright (C) 2015 Jonathan Peirce, Distributed under the
  terms of the GNU General Public License (GPL)

'setHighProcessPrior()', 'setNormalProcessPrior()'
  Routines to increase and reset process priority

Copyright (c) 2013-2022 Thomas Euler
Distributed under the terms of the GNU General Public License (GPL)

2021-10-15 - Adapt to LINUX
2022-08-06 - Some reformatting
"""
# ---------------------------------------------------------------------
__author__ 	= "code@eulerlab.de"

import os
import sys
import QDSpy_global as glb
from   pkgutil import iter_modules
from   operator import xor

if glb.QDSpy_incProcessPrior:
  import psutil
PLATFORM_WINDOWS = sys.platform == "win32"

# ---------------------------------------------------------------------
# Multiprocessing support
# ---------------------------------------------------------------------
WORKING, CANCELED, TERMINATING, IDLE = (
    "Working", "Canceled", "Terminating", "Idle"
  )

# ---------------------------------------------------------------------
# Set the default timing mechanism
# ---------------------------------------------------------------------
getTime  = None

if PLATFORM_WINDOWS:
  global _fcounter, _qpfreq, _winQPC
  from ctypes import byref, c_int64, windll
  _fcounter = c_int64()
  _qpfreq = c_int64()
  windll.Kernel32.QueryPerformanceFrequency(byref(_qpfreq))
  _qpfreq = float(_qpfreq.value)
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
# IO device-related helper
# ---------------------------------------------------------------------
def setIODevicePin(_IO, _portStr, _pin, _invert, _state):
  port = _IO.getPortFromStr(_portStr)
  mask = 0x01 << _pin
  data = _IO.readDPort(port)
  if xor(_state, _invert):
    data = data | mask
  else:
    data = data & ~mask
  _IO.writeDPort(port, data)

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
    if PLATFORM_WINDOWS:
      proc = psutil.Process(os.getpid())
      pyVersion = sys.version_info[0] +sys.version_info[1]/10
      if pyVersion <= 3.4:
        proc.set_nice(psutil.HIGH_PRIORITY_CLASS)
      else:
        proc.nice(psutil.HIGH_PRIORITY_CLASS)
      return True
  return False

def setNormalProcessPrior():
  if glb.QDSpy_incProcessPrior:
    if PLATFORM_WINDOWS:
      proc = psutil.Process(os.getpid())
      pyVersion = sys.version_info[0] +sys.version_info[1]/10
      if pyVersion <= 3.4:
        proc.set_nice(psutil.NORMAL_PRIORITY_CLASS)
      else:
        proc.nice(psutil.NORMAL_PRIORITY_CLASS)
      return True
  return False

# ---------------------------------------------------------------------
def module_exists(module_name):
  return module_name in (name for loader,name,ispkg in iter_modules())

# ---------------------------------------------------------------------
