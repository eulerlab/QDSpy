#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QDSpy module - to manage all projection device-related parameters

'Stage' 
  This class manages all parameters concnerning the projection device
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
      (width, height)     = R.get_screen_size(self.scrIndex)
      if (glo.QDSpy_use_Lightcrafter and
          (width == lcr.LC_width) and (height == lcr.LC_height)):
        self.scrDevType   = ScrDevType.DLPLCR4500EVM
      else:
        self.scrDevType   = ScrDevType.generic
      self.scrDevName     = ScrDevStr[self.scrDevType]
      self.depth          = R.get_screen_depth(self.scrIndex)
      self.scrDevFreq_Hz  = R.get_screen_refresh(self.scrIndex)
      self.isFullScr      = (self.dxScr == 0) or (self.dyScr == 0)
      self.LEDs           = []
      
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
      self.depth          = _d["depth"]
      self.scrDevFreq_Hz  = _d["scrDevFreq_Hz"]
      self.isFullScr      = _d["isFullScr"]
      self.LEDs           = []
      
    # Generate gamma LUTs
    #
    self.LUT_linDefault   = gma.generateLinearLUT()      
    self.LUT_userDefined  = gma.generateInverseLUT()

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def logInfo(self):
    ssp.Log.write("ok", "Stage center: {0:d},{1:d} pixels, scale: {2:.2f},"
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
  def updateLEDs(self, _LCr, _Conf=None):
    self.LEDs = []
    if _LCr != None:
      res = _LCr.getLEDCurrents()
      if res[0] == lcr.ERROR.OK:
        for index, curr in enumerate(res[1]):
          if _Conf != None:
            self.LEDs.append([_Conf.LEDNames[index], curr, 0, 
                              _Conf.LEDPeakWLs[index], 
                              _Conf.LEDQtColors[index]])
          else:
            self.LEDs.append(["#{0}".format(index), curr, 0, 0, "black"])
      res = _LCr.getLEDEnabled()
      if res[0] == lcr.ERROR.OK:
        for index in range(len(self.LEDs)):
          self.LEDs[index][2] = res[1][index]          
    
  def setLEDName(self, _index, _nameStr):
    if _index < len(self.LEDs):
      self.LEDs[_index][0] = _nameStr
    
  def setLEDEnabled(self, _index, _state, _LCr=None):
    if _index < len(self.LEDs):
      self.LEDs[_index][2] = _state
      if _LCr != None:
        res = _LCr.getLEDEnabled()
        if res[0] == lcr.ERROR.OK:
          self.LEDs[_index][2] = res[1][_index]      

  def setLEDCurrent(self, _index, _current, _LCr=None):
    if _index < len(self.LEDs):
      self.LEDs[_index][1] = _current
      if _LCr != None:
        res = _LCr.getLEDCurrents()
        if res[0] == lcr.ERROR.OK:
          self.LEDs[_index][1] = res[1][_index]   

# ---------------------------------------------------------------------

