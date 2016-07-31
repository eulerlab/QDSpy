#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QDSpy module - to manage all projection device-related parameters

'Stage' 
  This class manages all parameters concerning the projection device
  (e.g. screen, beamer), including scale, center of stimulation, global 
  rotation angle, refresh rate, LED current etc.
  This class is a graphics API independent.

Copyright (c) 2013-2016 Thomas Euler
All rights reserved.
"""
# ---------------------------------------------------------------------
__author__ 	= "code@eulerlab.de"

import QDSpy_global as glo
import QDSpy_stim_support as ssp
import QDSpy_gamma as gma
import Graphics.renderer_opengl as rdr

if glo.QDSpy_use_Lightcrafter:
  import Devices.lightcrafter as lcr

# ---------------------------------------------------------------------
class ScrDevType:
  generic             = 0
  DLPLCR4500EVM       = 1

ScrDevStr             = dict([
  (ScrDevType.generic,       "generic"),
  (ScrDevType.DLPLCR4500EVM, "DLPLCR4500EVM")])

# ---------------------------------------------------------------------
# Stimulus stage class
# ---------------------------------------------------------------------
class Stage:
  def __init__(self, _winWidth, _winHeight, _winLeft, _winTop, 
               _scalX, _scalY, _offX, _offY, _rot, _rFreq, _scr, 
               _disFSC, _d=None):
    # Initialize stage object from parameters or from dictionary (_d)
    #
    if _d == None:               
      self.dxScr          = _winWidth
      self.dyScr          = _winHeight
      self.xWinLeft       = _winLeft
      self.yWinTop        = _winTop
      self.scalX_umPerPix = _scalX
      self.scalY_umPerPix = _scalY
      self.winXCorrFact   = 1.0
      self.rot_angle      = _rot
      self.centOffX_pix   = _offX
      self.centOffY_pix   = _offY
      self.centX0_pix     = self.dxScr//2
      self.centY0_pix     = self.dyScr//2
      self.centX_pix      = self.centOffX_pix
      self.centY_pix      = self.centOffY_pix
      self.scrReqFreq_Hz  = _rFreq
      self.dtFr_s         = 1.0 /self.scrReqFreq_Hz
      self.disFScrCmd     = _disFSC
      self.scrIndex       = _scr

      # Determine the display device type
      #
      R = rdr.Renderer()
      if self.scrIndex >= R.get_screen_count():
        self.scrIndex     = 0
      ver                 = self.getLCrFirmwareVer()  
      if len(ver) > 0:
        self.scrDevType   = ScrDevType.DLPLCR4500EVM
      else:
        self.scrDevType   = ScrDevType.generic
        ver               = [0,0,0]        
      self.scrDevName     = ScrDevStr[self.scrDevType]
      self.scrDevVersion  = ver
      self.depth          = R.get_screen_depth(self.scrIndex)
      self.scrDevFreq_Hz  = R.get_screen_refresh(self.scrIndex)
      self.isFullScr      = (self.dxScr == 0) or (self.dyScr == 0)
      self.LEDs           = []
      self.isLEDSeqEnabled= True
      
    else:  
      self.dxScr          = _d["dxScr"]
      self.dyScr          = _d["dyScr"]
      self.xWinLeft       = 0
      self.yWinTop        = 0
      self.scalX_umPerPix = _d["scalX_umPerPix"]
      self.scalY_umPerPix = _d["scalY_umPerPix"]
      self.winXCorrFact   = _d["winXCorrFact"]
      self.rot_angle      = _d["rot_angle"]
      self.centOffX_pix   = _d["centX_pix"]
      self.centOffY_pix   = _d["centY_pix"]
      self.centX0_pix     = self.dxScr//2
      self.centY0_pix     = self.dyScr//2
      self.centX_pix      = self.centOffX_pix
      self.centY_pix      = self.centOffY_pix
      self.scrReqFreq_Hz  = _d["scrReqFreq_Hz"]
      self.dtFr_s         = 1.0 /self.scrReqFreq_Hz
      self.disFScrCmd     = False
      self.scrIndex       = _d["scrIndex"]
      
      self.scrDevName     = _d["scrDevName"]
      self.scrDevType     = _d["scrDevType"]
      self.scrDevVersion  = _d["scrDevVersion"]
      self.depth          = _d["depth"]
      self.scrDevFreq_Hz  = _d["scrDevFreq_Hz"]
      self.isFullScr      = _d["isFullScr"]
      self.LEDs           = []
      self.isLEDSeqEnabled= _d["isLEDSeqEnabled"]
      
    # Generate gamma LUTs
    #
    self.LUT_linDefault   = gma.generateLinearLUT()      
    self.LUT_userDefined  = gma.generateInverseLUT()

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def logInfo(self):
    ssp.Log.write("INFO", "Display    : {0}".format(self.scrDevName))
    ssp.Log.write("ok", "Stage info : {0:d},{1:d} pixels, scale: {2:.2f},"
                  "{3:.2f} {4}m/pix, rotation: {5:.0f}{6}, refresh: "
                  "{7} Hz"
                  .format(int(self.centX_pix), int(self.centY_pix),
                          self.scalX_umPerPix, self.scalY_umPerPix,
                          u'µ', self.rot_angle, u'°', self.scrReqFreq_Hz))

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def durToFrames(self, _dur_s):
    if _dur_s > 0.0:
      dur = _dur_s *self.scrReqFreq_Hz
      return (round(dur), 
              abs(dur -round(dur)) < glo.QDSpy_maxFrameDurDiff_s)
    else:
      return (-1, True)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def getScaleOffsetAsDict(self):
    return {"centOffX_pix":   self.centOffX_pix,
            "centOffY_pix":   self.centOffY_pix,
            "scalX_umPerPix": self.scalX_umPerPix,
            "scalY_umPerPix": self.scalY_umPerPix,
            "rot_angle":      self.rot_angle}
      
  # -------------------------------------------------------------------
  # LED-related functions      
  # -------------------------------------------------------------------    
  def createLEDs(self, _Conf):
    """ Create the LED dictionary from the configuration, if available
    """
    self.LEDs = []
    self.isLEDSeqEnabled = True

    if _Conf is None:
      d = {}
      d["name"]     = "n/a"
      d["current"]  = 0
      d["enabled"]  = False
      d["peak_nm"]  = 0
      d["Qt_color"] = "black"
      self.LEDs.append(d)
    
    else:
      for iLED, LEDName in enumerate(_Conf.LEDNames):
        d = {}
        d["name"]     = LEDName
        d["current"]  = 0
        d["enabled"]  = False
        d["peak_nm"]  = _Conf.LEDPeakWLs[iLED]
        d["Qt_color"] = _Conf.LEDNames[iLED]
        self.LEDs.append(d)
    
      
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -      
  def updateLEDs(self, _LCr=None, _Conf=None):
    """ Connect to lightcrafter to get LED currents and enabled state, 
        und update LED dictionary
    """    
    # Check configuration file and, if not available, also globals if 
    # the lightcrafter should be used
    #
    if _Conf is None:
      if not(glo.QDSpy_use_Lightcrafter): 
        return
    else:
      if not(_Conf.useLCr):
        return
     
    # Use lightcrafter object if available or generate new one
    #
    if _LCr is None:
      LCr = lcr.Lightcrafter(_logLevel=glo.QDSpy_LCr_LogLevel)
    else:
      LCr = _LCr
    
    # Connect to lightcrafter and change LED settings
    #      
    result = LCr.connect()
    errC   = result[0]
    if errC == lcr.ERROR.OK:
      try:
        current = LCr.getLEDCurrents()
        enabled = LCr.getLEDEnabled()
        self.isLEDSeqEnabled = enabled[2]
        
        for iLED, LED in enumerate(self.LEDs):
          self.LEDs[iLED]["current"] = current[1][iLED]
          self.LEDs[iLED]["enabled"] = enabled[1][iLED]
      finally:    
        LCr.disconnect()   
    
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -    
  def setLEDName(self, _index, _nameStr):
    if _index < len(self.LEDs):
      self.LEDs[_index]["name"]    = _nameStr
   
  def setLEDEnabled(self, _index, _state):
    if _index < len(self.LEDs):
      self.LEDs[_index]["enabled"] = _state

  def setLEDCurrent(self, _index, _current):
    if _index < len(self.LEDs):
      self.LEDs[_index]["current"] = _current

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def sendLEDChangesToLCr(self, _LCr=None, _Conf=None):
    """ Connect to lightcrafter and update LED currents and enabled state
    """
    # Check configuration file and, if not available, also globals if 
    # the lightcrafter should be used
    #
    if _Conf is None:
      if not(glo.QDSpy_use_Lightcrafter): 
        return
    else:
      if not(_Conf.useLCr):
        return
     
    # Use lightcrafter object if available or generate new one
    #
    if _LCr is None:
      LCr = lcr.Lightcrafter(_logLevel=glo.QDSpy_LCr_LogLevel)
    else:
      LCr = _LCr
    
    # Connect to lightcrafter and change LED settings
    #      
    result = LCr.connect()
    errC   = result[0]
    if errC == lcr.ERROR.OK:
      try:
        currents = []
        enabled  = []
        for LED in self.LEDs:
          currents.append(LED["current"])
          enabled.append(LED["enabled"])
        LCr.setLEDCurrents(currents[0:3])
        LCr.setLEDEnabled(enabled[0:3], self.isLEDSeqEnabled)

      finally:    
        LCr.disconnect()   
    
  # -------------------------------------------------------------------
  # Lightcrafter-related functions      
  # -------------------------------------------------------------------      
  def getLCrFirmwareVer(self):
    """ Return firmware version of connected lightcrafter as list
        (e.g. [3,0,0]) or an empty list, if lightcrafter use is not 
        enabled or device could not be connected
    """    
    ver = []
    
    if glo.QDSpy_use_Lightcrafter: 
      LCr = lcr.Lightcrafter(_logLevel=0)
      result = LCr.connect()
      errC   = result[0]
      if errC == lcr.ERROR.OK:
        try:
          result = LCr.getFirmwareVersion()
          errC   = result[0]
          if errC == lcr.ERROR.OK:
            ver  = result[2]["applicationSoftwareRev"]
        finally:    
          LCr.disconnect()   

    return ver

# ---------------------------------------------------------------------

