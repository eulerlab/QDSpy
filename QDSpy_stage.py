#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QDSpy module - to manage all projection device-related parameters

'Stage'
  This class manages all parameters concerning the projection device
  (e.g. screen, beamer), including scale, center of stimulation, global
  rotation angle, refresh rate, LED current etc.
  This class is a graphics API independent.

Copyright (c) 2013-2019 Thomas Euler
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
  def __init__(self, _d, _isNew=False):
    # Initialize stage object from parameters in dictionary (_d)
    #
    self.dxScr               = _d["dxScr"]
    self.dyScr               = _d["dyScr"]
    self.scalX_umPerPix      = _d["scalX_umPerPix"]
    self.scalY_umPerPix      = _d["scalY_umPerPix"]
    self.rot_angle           = _d["rot_angle"]
    self.centOffX_pix        = _d["centOffX_pix"]
    self.centOffY_pix        = _d["centOffY_pix"]
    self.centX0_pix          = self.dxScr//2
    self.centY0_pix          = self.dyScr//2
    self.centX_pix           = self.centOffX_pix
    self.centY_pix           = self.centOffY_pix
    self.scrReqFreq_Hz       = _d["scrReqFreq_Hz"]
    self.dtFr_s              = 1.0 /self.scrReqFreq_Hz
    self.scrIndex            = _d["scrIndex"]
    self.scrIndexGUI         = _d["scrIndGUI"]
    self.useScrOvl           = _d["useScrOvl"]
    self.dxScr12             = _d["dxScr12"]
    self.dyScr12             = _d["dyScr12"]
    self.offXScr1_pix        = _d["offXScr1_pix"]
    self.offYScr1_pix        = _d["offYScr1_pix"]
    self.offXScr2_pix        = _d["offXScr2_pix"]
    self.offYScr2_pix        = _d["offYScr2_pix"]
    self.vFlipScr1           = -1 if _d["vFlipScr1"] else 1
    self.hFlipScr1           = -1 if _d["hFlipScr1"] else 1
    self.vFlipScr2           = -1 if _d["vFlipScr2"] else 1
    self.hFlipScr2           = -1 if _d["hFlipScr2"] else 1
    self.LEDs                = []

    if _isNew:
      self.xWinLeft          = _d["xWinLeft"]
      self.yWinTop           = _d["yWinTop"]
      self.winXCorrFact      = 1.0
      self.disFScrCmd        = _d["disFScr"]

      # Determine the display device type
      #
      R    = rdr.Renderer()
      nScr = R.get_screen_count()
      if self.scrIndex >= nScr:
        self.scrIndex        = nScr -1
        ssp.Log.write("WARNING", "`int_screen_index_gui`=={0} but only {1} "
                      "screens were detected -> for fullscreen mode, screen "
                      "#{2} is used."
                      .format(self.scrIndex +1, nScr, self.scrIndex))

      ver                    = self.getLCrFirmwareVer(0)
      if len(ver) > 0:
        self.scrDevType      = ScrDevType.DLPLCR4500EVM
        self.LCrDevices      = lcr.enumerateLightcrafters()
        self.isLEDSeqEnabled = [True] *len(lcr.LCrDeviceList)
      else:
        self.scrDevType      = ScrDevType.generic
        ver                  = [0,0,0]
        self.isLEDSeqEnabled = [True]

      self.scrDevName        = ScrDevStr[self.scrDevType]
      self.scrDevVersion     = ver
      self.depth             = R.get_screen_depth(self.scrIndex)
      self.scrDevFreq_Hz     = R.get_screen_refresh(self.scrIndex)
      self.isFullScr         = (self.dxScr == 0) or (self.dyScr == 0)

    else:
      self.xWinLeft          = 0
      self.yWinTop           = 0
      self.winXCorrFact      = _d["winXCorrFact"]
      self.disFScrCmd        = False

      self.scrDevName        = _d["scrDevName"]
      self.scrDevType        = _d["scrDevType"]
      self.scrDevVersion     = _d["scrDevVersion"]
      self.depth             = _d["depth"]
      self.scrDevFreq_Hz     = _d["scrDevFreq_Hz"]
      self.isFullScr         = _d["isFullScr"]
      self.isLEDSeqEnabled   = _d["isLEDSeqEnabled"]

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
                  .format(int(self.centOffX_pix), int(self.centOffY_pix),
                          self.scalX_umPerPix, self.scalY_umPerPix,
                          u'µ', self.rot_angle, u'°', self.scrReqFreq_Hz))
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def logData(self):
    ssp.Log.write("DATA", {"scaling_x": self.scalX_umPerPix,
                           "scaling_y": self.scalY_umPerPix,
                           "offset_x": int(self.centOffX_pix),
                           "offset_y": int(self.centOffY_pix),
                           "rotation": self.rot_angle}.__str__()) 
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
            "rot_angle":      self.rot_angle,
            "dxScr12":        self.dxScr12,
            "dyScr12":        self.dyScr12,
            "offXScr1_pix":   self.offXScr1_pix,
            "offYScr1_pix":   self.offYScr1_pix,
            "offXScr2_pix":   self.offXScr2_pix,
            "offYScr2_pix":   self.offYScr2_pix}

  # -------------------------------------------------------------------
  # LED-related functions
  # -------------------------------------------------------------------
  def createLEDs(self, _Conf):
    """ Create the LED dictionary from the configuration, if available
    """
    self.LEDs = []
    self.isLEDSeqEnabled = [True] *glo.QDSpy_MaxLightcrafterDev

    for iLED, LEDName in enumerate(_Conf.LEDNames):
      d = {}
      d["name"]        = LEDName
      d["current"]     = _Conf.LEDDefCurr[iLED]
      d["max_current"] = _Conf.LEDMaxCurr[iLED]
      d["enabled"]     = False
      d["peak_nm"]     = _Conf.LEDPeakWLs[iLED]
      d["devIndex"]    = _Conf.LEDDevIndices[iLED]
      d["LEDIndex"]    = _Conf.LEDIndices[iLED]
      d["Qt_color"]    = _Conf.LEDQtColors[iLED]
      self.LEDs.append(d)

    self.sendLEDChangesToLCr(_Conf)


  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def updateLEDs(self, _Conf):
    """ Connect to lightcrafter to get LED currents and enabled state,
        und update LED dictionary
    """
    # Check configuration file and, if not available, also globals if
    # the lightcrafter should be used
    #
    if (_Conf is None) or not(_Conf.useLCr) or not(glo.QDSpy_use_Lightcrafter):
      return

    # Generate a new lightcrafter object
    #
    LCr = lcr.Lightcrafter(_logLevel=glo.QDSpy_LCr_LogLevel,
                           _funcLog=ssp.Log.write)

    for iDev, Dev in enumerate(lcr.LCrDeviceList):
      try:
        result = LCr.connect(iDev)
        if result[0] == lcr.ERROR.OK:
          # Get LED settings on the device(s)
          #
          current = [0]*3
          enabled = [False]*3
          result  = LCr.getLEDCurrents()
          if result[0] == lcr.ERROR.OK:
            current = list(result[1])
          result  = LCr.getLEDEnabled()
          if result[0] == lcr.ERROR.OK:
            enabled = list(result[1])
            seqEnabled = result[2]

          self.isLEDSeqEnabled[iDev] = seqEnabled

          for iCurr, Curr in enumerate(current):
            for iLED, LED in enumerate(self.LEDs):
              if (iDev == LED["devIndex"]) and (iCurr == LED["LEDIndex"]):
                self.LEDs[iLED]["current"] = Curr
                self.LEDs[iLED]["enabled"] = enabled[iCurr]
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
  def sendLEDChangesToLCr(self, _Conf):
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

    # Generate a new lightcrafter object
    #
    LCr = lcr.Lightcrafter(_logLevel=glo.QDSpy_LCr_LogLevel,
                           _funcLog=ssp.Log.write)

    for iDev, Dev in enumerate(lcr.LCrDeviceList):
      try:
        result = LCr.connect(iDev)
        if result[0] == lcr.ERROR.OK:
          # Set LEDs on the device(s)
          #
          currents = [0] *3
          enabled  = [False] *3
          for iLED, LED in enumerate(self.LEDs):
            if LED["devIndex"] == iDev:
              currents[LED["LEDIndex"]] = LED["current"]
              enabled[LED["LEDIndex"]]  = LED["enabled"]

          LCr.setLEDCurrents(currents[0:3])
          LCr.setLEDEnabled(enabled[0:3], self.isLEDSeqEnabled[iDev])
      finally:
        LCr.disconnect()

  # -------------------------------------------------------------------
  # Lightcrafter-related functions
  # -------------------------------------------------------------------
  def getLCrFirmwareVer(self, _devIndex):
    """ Return firmware version of connected lightcrafter as list
        (e.g. [3,0,0]) or an empty list, if lightcrafter use is not
        enabled or device could not be connected
    """
    ver = []

    if glo.QDSpy_use_Lightcrafter:
      LCr = lcr.Lightcrafter(_logLevel=-1)
      result = LCr.connect(_devIndex)
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
