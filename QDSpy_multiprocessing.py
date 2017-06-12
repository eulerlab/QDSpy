#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QDSpy module - to synchronize QDSpy processes

'Sync'
  Class to synchronize states and data (via a pipe) between the GUI process 
  and the stimulus presenter process

Copyright (c) 2013-2016 Thomas Euler
All rights reserved.
"""
# ---------------------------------------------------------------------
__author__ 	= "code@eulerlab.de"

import time            
from   multiprocessing import Manager, Pipe 

# ---------------------------------------------------------------------
# Multiprocessing support
# ---------------------------------------------------------------------     
UNDEFINED, PRESENTING, COMPILING, CANCELING, TERMINATING, IDLE, PROBING \
= ("Undefined", "Presenting", "Compiling", "Canceling",  "Terminating", 
   "Idle", "Probing")
  
class PipeValType:
  toCli_log          = 0
  toCli_displayInfo  = 1
  toCli_TEMP         = 2
  # ...
  toSrv_None         = 9
  toSrv_fileName     = 10
  toSrv_changedStage = 11 
  toSrv_changedLEDs  = 12 
  toSrv_probeParams  = 13 

# ---------------------------------------------------------------------
# Sync class
# ---------------------------------------------------------------------     
class Sync:
  def __init__(self):
    # Initializing
    #
    self.Request       = Manager().Value("i", IDLE)
    self.State         = Manager().Value("i", UNDEFINED)
    self.pipeCli, self.pipeSrv = Pipe()
    
    """
    dx = 64  #912 //6
    dy = 128 #1140 //6
    self.FrameSize = (dx, dy)
    self.Frame     = Manager().Array("B", [0]*dx*dy*3)
    '''
    multiprocessing.sharedctypes.Array(typecode_or_type, size_or_initializer, *args[, lock])
    '''
    print("class Sync|_init__|len(self.Frame)=", len(self.Frame))
    """

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def setStateSafe(self, _newState):
    self.State.value   = _newState

  def setRequestSafe(self, _newReq):
    self.Request.value = _newReq

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def waitForState(self, _targetState, _timeout_s=0.0, _updateProc=None):
    # Wait for "mpState" to reach a certain state or for timeout, if given. 
    # Returns True, if stage was reached within the timeout period
    #
    timeout   = False
    t_s       = time.time()
    while not(self.State.value == _targetState) and not(timeout):
      if _updateProc != None:
        _updateProc()
      time.sleep(0.05)
      if _timeout_s > 0.0:
        timeout = (time.time() -t_s) >= _timeout_s
    return not(timeout) 
 
# --------------------------------------------------------------------