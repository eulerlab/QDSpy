#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
#  thorlabs_motion_control.py
#
#  Simple class implementing access to Thorlabs' Kinesis API, here
#  specifically for KCube DC servo motors, but in principle the class 
#  can be generalized
# 
#  For the MTS25-Z8 (MTS25/M-Z8), there are 512 encoder counts per 
#  revolution of the motor. The output shaft of the motor goes into a 
#  67:1 planetary gear head. This requires the motor to rotate 67 times 
#  to rotate the 1.0 mm pitch lead screw one revolution. The end result
#  is the lead screw advances by 1.0 mm. 
#  The linear displacement of the actuator per encoder count is given by
#    512 x 67 = 34,304 encoder counts per revolution of the lead screw,
#  whereas the linear displacement of the lead screw per encoder count 
#  is given by
#    1.0 mm / 34,304 counts = 2.9 x 10-5 mm (29 nm).
#
#  Copyright (c) 2016 Thomas Euler
#  All rights reserved.
#
# ---------------------------------------------------------------------
__author__ 	= "code@eulerlab.de"

import os
import ctypes
import time

# ---------------------------------------------------------------------
TL_cBufSize        = 255

# ---------------------------------------------------------------------
class TL_devIDs:
  KCubeDCServo_ID  = 27
  # ...
  
TL_dllName         = 0
TL_stepsPerRev     = 1
TL_gearBoxRatio    = 2
TL_pitch           = 3   

TL_devConfigs    	  = dict([
  (TL_devIDs.KCubeDCServo_ID, 
   # DLL name, steps per revolution, gear box ratio, pitch of lead screw
   ["Thorlabs.MotionControl.KCube.DCServo.dll", 512.0, 67.0, 1.0])
  # ...
  ])


# ---------------------------------------------------------------------
class TLabs_Motor():
  def __init__(self, devID, serNr, verbose=True, funcLog=None):
    """
    Initialize an object representing a Thorlabs motor device
      devID         : type ID of motor device 
      serNr         : unique serial number of the specific device
      verbose       : True=extensive log messages
      funcLog       : reference to log function, f(strHeader, strMsg)
    """
    if funcLog == None:
      self.log = self.__log
    else:
      self.log = funcLog
  
    # Check ID
    #
    try:
      self.dllName = TL_devConfigs[devID][TL_dllName]
    except KeyError:
      self.log("ERROR", "Type {0} devices not yet supported".format(devID))
      return
  
    # Initialize
    #
    self.Connected    = False
    self.isReady      = False
    self.serNr        = serNr
    self.serNrStr     = ctypes.c_char_p(serNr.__str__().encode("ascii"))
    self.devID        = devID
    self.errC         = 0
    self.isVerbose    =  verbose
    self.poll_ms      = 200
    self.pos          = 0
    self.pos_mm       = 0.0

    # Retrieve motor parameters (from specs on the Thorlabs website)
    #
    self.stepsPerRev  = TL_devConfigs[devID][TL_stepsPerRev]
    self.gearBoxRatio = TL_devConfigs[devID][TL_gearBoxRatio]
    self.pitch        = TL_devConfigs[devID][TL_pitch]

    # Check for Thorlabs Kinesis DLLs
    #
    if not os.path.exists(self.dllName):
      self.log("ERROR", "DLL `{0}` not found".format(self.dllName))
      return

    self.TL = ctypes.windll.LoadLibrary(self.dllName)
    self.log("", "Connecting to Thorlabs type-{0} device with S/N {1} ..."
                 .format(self.devID, self.serNr))
 
    # Check for requested device    
    #
    if self.TL.TLI_BuildDeviceList() == 0:
      nDev = self.TL.TLI_GetDeviceListSize()
      if nDev == 0:
        self.log("ERROR", "No devices found")
        return
  
      # Devices found, next look for S/Ns by device type
      #  
      sBuf = ctypes.c_buffer(TL_cBufSize)
      if self.TL.TLI_GetDeviceListByTypeExt(sBuf, TL_cBufSize, devID) != 0:
        self.log("ERROR", "No devices of type {0} found".format(devID))
        return
        
      self.serNrStrList = sBuf.value.decode().rsplit(",")[0:-1]
      if not(self.serNr.__str__() in self.serNrStrList):
        self.log("ERROR", "No device with S/N {0} found".format(serNr))
        return  

      # Device with the requested S/N found, now try to open it
      #
      self.log("", "... found")
      self.errC = self.TL.CC_Open(self.serNrStr)
      if self.errC != 0:
        self.log("ERROR", "#{0}, opening device failed".format(self.errC))
        return

      # Get motor parameters for the conversion of unit to real-world units
      #
      # ************************
      # ************************
      # TODO: Cannot get the motor parameters from the driver, would be
      #       better than using parameters from the specs
      """
      stepsPerRev  = ctypes.c_double()
      gearBoxRatio = ctypes.c_double()
      pitch        = ctypes.c_double()
      self.TL.CC_GetMotorParamsExt(self.serNrStr, ctypes.byref(stepsPerRev), 
                                   ctypes.byref(gearBoxRatio), 
                                   ctypes.byref(pitch))
      self.stepsPerRev  = stepsPerRev.value
      self.gearBoxRatio = gearBoxRatio.value
      self.pitch        = pitch.value
      print(stepsPerRev, gearBoxRatio, pitch)
      """
      # ************************
      # ************************

      self.TL.CC_Close(self.serNrStr)  
      self.Connected = True
      self.log("", "... connected")
    
    return      
      
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def openDevice(self):
    """
    Open the motor device and start polling status messages
    """
    self.errC = None
  
    if not(self.Connected):
      self.log("ERROR", "Device not connected")
    else:  
      if self.isReady:
        self.log("WARNING", "Device still open")
      else:  
        self.errC = self.TL.CC_Open(self.serNrStr)
        if self.errC == 0:
          self.TL.CC_StartPolling(self.serNrStr, self.poll_ms)
          time.sleep(0.5)
          
          if self.TL.CC_NeedsHoming(self.serNrStr):
            self.log("", "Device needs homing ...")
            self.TL.CC_Home(self.serNrStr)
            time.sleep(2.0)
            self.log("ok", "... homing done")
            
          self.isReady = True
          if self.isVerbose:
            self.log("ok", "Device S/N {0} ready".format(self.serNr))

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def __mm_to_deviceUnits(self, pos_mm):
    newPos = pos_mm /self.pitch *self.stepsPerRev *self.gearBoxRatio
    return int(newPos)
    
  def __deviceUnits_to_mm(self, pos):
    return float(pos) /self.stepsPerRev /self.gearBoxRatio *self.pitch

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def getPosition(self):
    """
    Return current position in abslute device units
    """ 
    if not(self.isReady):
      return 0
    else:  
      self.pos = self.TL.CC_GetPosition(self.serNrStr)
      self.pos_mm = self.__deviceUnits_to_mm(self.pos)
      return self.pos

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def getPosition_mm(self):
    """
    Return current position in [mm]
    """
    self.getPosition()
    return self.pos_mm

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def moveToPosition(self, newPos):
    """
    Move to a position and wail until the target position is reached.
      newPos        : new position in absolute device units
    """
    if self.isReady:
      # Initialize
      #
      self.errC = None
      done      = False
      newPos_mm = self.__deviceUnits_to_mm(newPos)
      
      # Move ... 
      #
      self.TL.CC_ClearMessageQueue(self.serNrStr)
      self.TL.CC_MoveToPosition(self.serNrStr, newPos)
      if self.isVerbose:
        self.log("", "Moving to {0:.3f} mm ({1}) ..."
                     .format(newPos_mm, newPos))

      # ... and then wait until the movement has completed      
      #
      while not(done):
        while self.TL.CC_MessageQueueSize(self.serNrStr) == 0:
          time.sleep(0.100)
        msgType = ctypes.c_uint32()
        msgID   = ctypes.c_uint32()
        msgData = ctypes.c_uint64()
        self.TL.CC_GetNextMessage(self.serNrStr, ctypes.pointer(msgType), 
                                  ctypes.pointer(msgID), 
                                  ctypes.pointer(msgData))
        done = (msgType.value == 2) or (msgID == 1)
        
      self.pos    = self.TL.CC_GetPosition(self.serNrStr)  
      self.pos_mm = self.__deviceUnits_to_mm(self.pos)  
      self.errC   = 0
      if self.isVerbose:
        self.log("ok", "... reached {0:.3f} mm ({1})"
                       .format(self.pos_mm, self.pos))

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def moveToPosition_mm(self, newPos_mm):
    """
    Move to a position and wail until the target position is reached.
      newPos        : new position in [mm]
    """
    print(newPos_mm)
    self.moveToPosition(self.__mm_to_deviceUnits(newPos_mm))

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def closeDevice(self):
    """
    Stop polling status messages and close motor device
    """
    self.errC = None
  
    if not(self.Connected):
      self.log("ERROR", "Device not connected")
    else:  
      if not(self.isReady):
        self.log("WARNING", "Device is not open")
      else:  
        self.TL.CC_StopPolling(self.serNrStr)
        self.TL.CC_Close(self.serNrStr)
        self.errC    = 0
        self.isReady = False
        if self.isVerbose:
          self.log("ok", "Device S/N {0} closed".format(self.serNr))
     
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def __log (self, sHeader, sMsg):
    print("{0!s:>8} {1}".format(sHeader, sMsg))

# ---------------------------------------------------------------------
      
