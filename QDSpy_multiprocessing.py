#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QDSpy module - to synchronize QDSpy processes

'Sync'
  Class to synchronize states and data (via a pipe) between the GUI process
  and the stimulus presenter process

Copyright (c) 2013-2024 Thomas Euler
All rights reserved.

2024-06-11 - Reformatted (using Ruff)
           - Suport sending stimulus time info back to client
"""
# ---------------------------------------------------------------------
__author__ = "code@eulerlab.de"

import time
from multiprocessing import Pipe, Value

# ---------------------------------------------------------------------
# Multiprocessing support
# ---------------------------------------------------------------------
UNDEFINED = 0
PRESENTING = 1
COMPILING = 2
CANCELING = 3
TERMINATING = 4
IDLE = 5
PROBING = 6

StateStr = dict(
    [
        (UNDEFINED, "Undefined"),
        (PRESENTING, "Presenting"),
        (COMPILING, "Compiling"),
        (CANCELING, "Canceling"),
        (TERMINATING, "Terminating"),
        (IDLE, "Idle"),
        (PROBING, "Probing"),
    ]
)


class PipeValType:
    toCli_log = 0
    toCli_displayInfo = 1
    toCli_IODevInfo = 2
    toCli_TEMP = 3
    toCli_time = 4
    toCli_playEndInfo = 5
    # ...
    toSrv_None = 9
    toSrv_fileName = 10
    toSrv_changedStage = 11
    toSrv_changedLEDs = 12
    toSrv_probeParams = 13
    toSrv_checkIODev = 14
    toSrv_setIODevPins = 15


# ---------------------------------------------------------------------
# Sync class
# ---------------------------------------------------------------------
class Sync:
    def __init__(self):
        """ Initializing
        """
        self.Request = Value("i", IDLE)
        self.State = Value("i", UNDEFINED)
        self.pipeCli, self.pipeSrv = Pipe()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setStateSafe(self, _newState):
        self.State.value = _newState

    def setRequestSafe(self, _newReq):
        self.Request.value = _newReq

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def waitForState(self, _targetState, _timeout_s=0.0, _updateProc=None):
        """ Wait for "mpState" to reach a certain state or for timeout, if given.
            Returns True, if stage was reached within the timeout period
        """
        timeout = False
        t_s = time.time()
        while not (self.State.value == _targetState) and not (timeout):
            if _updateProc is not None:
                _updateProc()
            time.sleep(0.05)
            if _timeout_s > 0.0:
                timeout = (time.time() - t_s) >= _timeout_s
        return not (timeout)


# --------------------------------------------------------------------
