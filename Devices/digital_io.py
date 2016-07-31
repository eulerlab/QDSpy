#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Digital I/O API

Digital I/O using Measurement Computing's Universal Library
http://www.mccdaq.com/daq-software/universal-library.aspx

Copyright (c) 2013-2016 Thomas Euler
All rights reserved.
"""
# ---------------------------------------------------------------------
__author__ 	= "code@eulerlab.de"

# ---------------------------------------------------------------------
import ctypes
from   ctypes                     import byref
from . import digital_io_UL_const as ULConst
# ---------------------------------------------------------------------
# Universal library(UL) devices (Measurement Computing)
#
class devTypeUL:
  none        = 0
  USB1024LS   = 118
  PCIDIO24    = 40

class devConst:
  NONE        = -1
  PORT_A      = 0
  PORT_B      = 1
  PORT_C_LO   = 2
  PORT_C_HI   = 3
  DIGITAL_IN  = 10
  DIGITAL_OUT = 11

dictUL        = dict([
  (devConst.PORT_A,      ULConst.FIRSTPORTA),
  (devConst.PORT_B,      ULConst.FIRSTPORTB),
  (devConst.PORT_C_LO,   ULConst.FIRSTPORTCL),
  (devConst.PORT_C_HI,   ULConst.FIRSTPORTCH),
  (devConst.DIGITAL_IN,  ULConst.DIGITALIN),
  (devConst.DIGITAL_OUT, ULConst.DIGITALOUT)])

# ---------------------------------------------------------------------
# I/O base class
# ---------------------------------------------------------------------
class devIO(object):
  def __init__(self, _funcLog):
    # Initializing and testing the device
    #
    self.isReady = False
    self.devName = "n/a"
    self.devType = None
    
    if _funcLog == None:
      self.log   = self.__log
    else:
      self.log   = _funcLog

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def _setIsReady(self):
    self.isReady   = True
    self.log("ok", "I/O device '{0}' is ready".format(self.devName))

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def configDPort(self, _port, _dir):
    # Configure digital port
    #
    pass

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def readDPort(self, _port):
    # Read byte from digital port
    #
    pass

  def writeDPort(self, _port, _val):
    # Write byte to digital port
    #
    pass
  
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def __log(self, _sHeader, _sMsg):
    # ...
    #
    print("{0!s:>8} {1}".format(_sHeader, _sMsg))
  

# =====================================================================
# I/O class using the Universal Library/Measurement Computing
# ---------------------------------------------------------------------
class devIO_UL(devIO, object):
  def __init__(self, _type, _boardNum, _devNum, _funcLog=None):
    super(devIO_UL, self).__init__(_funcLog)

    if   _type == devTypeUL.none:
      return 

    else:
      # Load respective hardware DLL
      #
      try:
        self.UL    = ctypes.windll.cbw64
      except WindowsError:
        self.log("ERROR", "Driver library 'cbw64.dll' not found")
        return 
        
      self.brdNum  = _boardNum
      self.devNum  = _devNum
      self.bData   = 0
      self.cbData  = ctypes.c_ushort(self.bData)
      dv           = 0
      cdv          = ctypes.c_int(dv)

      if   _type == devTypeUL.USB1024LS:
        self.devName = "USB-1024LS"
        self.devType = devTypeUL.USB1024LS

      elif _type == devTypeUL.PCIDIO24:
        self.devName = "PCI-DIO24"
        self.devType = devTypeUL.PCIDIO24

      else:
        self.log("ERROR", "Unknown digital I/O device")
        return

      # Configure device
      #
      self.UL.cbGetConfig(ULConst.BOARDINFO, self.brdNum, self.devNum,
                          ULConst.BIBOARDTYPE, ctypes.byref(cdv))
      if cdv.value == self.devType:
        # Requested device is connected
        #
        self.PORT_A      = ULConst.FIRSTPORTA
        self.PORT_B      = ULConst.FIRSTPORTB
        self.PORT_CLo    = ULConst.FIRSTPORTCL
        self.PORT_CHi    = ULConst.FIRSTPORTCH
        self.DIGITAL_IN  = ULConst.DIGITALIN
        self.DIGITAL_OUT = ULConst.DIGITALIN

        """
        # Get revision number of Universal Library
        #
        revNum    = ctypes.c_float()
        vxDRevNum = ctypes.c_float()
        UL.cbGetRevision(byref(revNum), byref(vxDRevNum))
        return revNum.value, vxDRevNum.value
        """
        #self.UL.cbFlashLED(self.brdNum)
        self._setIsReady()

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def configDPort(self, _port, _dir):
    self.UL.cbDConfigPort(self.brdNum, dictUL[_port], dictUL[_dir])

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def readDPort(self, _port):
    self.bData   = 0
    self.UL.cbDIn(self.brdNum, dictUL[_port], byref(self.cbData))
    return self.cbData.value

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def writeDPort(self, _port, _val):
    self.UL.cbDOut(self.brdNum, dictUL[_port], _val)
    
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def getPortFromStr(self, _portStr):
    if   _portStr.upper() == "A":
      return devConst.PORT_A
    if   _portStr.upper() == "B":
      return devConst.PORT_B
    if   _portStr.upper() == "CHI":
      return devConst.PORT_C_LO
    if   _portStr.upper() == "CLO":
      return devConst.PORT_C_HI
      
    return devConst.NONE   

# ---------------------------------------------------------------------
