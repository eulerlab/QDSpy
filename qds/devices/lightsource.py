#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Light source base class

Copyright (c) 2025 Thomas Euler
All rights reserved.
"""
# ---------------------------------------------------------------------
__author__ = "thomas.euler@eulerlab.de"

# ---------------------------------------------------------------------
from types import FunctionType

# fmt: off
class ErrCodes:
    OK              = 0
    NOT_READY       = -1
    COMMAND_UNKNOWN = -2
    PARAMS_INVALID  = -3
    UNKNOWN_ERROR   = -99
# fmt: on

# ---------------------------------------------------------------------
class LightSource(object):
    def __init__(self, _funcLog :FunctionType =None):    
        """
        Create and initialize light source object.

        =============== ==================================================
        Parameters:
        =============== ==================================================
        _funcLog        | external function for logging of the format:
                        | log(_sHeader, _sMsg, _logLevel)
        =============== ==================================================
        """
        self.isReady = False
        self._funcLog = _funcLog
        self._chanMap = []        
        self._devInfo = {
            "name": "n/a", "model": "n/a", "version": "n/a"
        }


    @property
    def deviceInfo(self):
        """ 
        Retrieve device information and status as dictionary
        """
        return self._devInfo        

    @property
    def channelMap(self):
        """ 
        Retrieve channel map with status information as dictionary
        """
        return self._chanMap        

    # -------------------------------------------------------------------
    # Helper
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def log(self, _sHeader :str, _sMsg :str):
        """ Write message to log """
        self.lastMsgStr = _sMsg
        dev = self._devInfo["name"]
        if self._funcLog:
            self._funcLog(_sHeader, dev +"|" +_sMsg)
        else:
            print(f"{_sHeader!s:>8} #{dev}: {_sMsg}")

# ---------------------------------------------------------------------