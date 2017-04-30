#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QDSpy module - support routines for the GUI version of QDSpy

Copyright (c) 2013-2017 Thomas Euler
All rights reserved.
"""
# ---------------------------------------------------------------------
__author__ 	= "code@eulerlab.de"

import os
from   datetime import datetime
from   PyQt5 import QtCore, QtGui
import QDSpy_global as glo
'''
if glo.QDSpy_use_Lightcrafter:
  import Devices.lightcrafter as lcr
'''  

# ---------------------------------------------------------------------
def getStimFileLists(_path):
  # Make a list of the stimulus files (including path) present in the 
  # given path
  #
  f          = []
  stimFNames = []
  for (dirpath, dirnames, filenames) in os.walk(_path):
    f.extend(filenames)
    break
  for fName in f:
    if (os.path.splitext(fName)[1]).lower() == glo.QDSpy_stimFileExt:
      fName  = (os.path.splitext(os.path.basename(fName)))[0]
      stimFNames.append(os.path.join(_path, fName))
  return stimFNames

# ---------------------------------------------------------------------
def getFNameNoExt(_fName):
  # Extract just file name, no path nor extension
  #
  return (os.path.splitext(os.path.basename(_fName)))[0]

# ---------------------------------------------------------------------
def getStimCompileState(_fName):  
  # Check if pickle-file is current
  #
  fName  = os.path.splitext(_fName)[0]
  try:
    tStamp = os.path.getmtime(fName +glo.QDSpy_stimFileExt)
    tPy    = datetime.fromtimestamp(tStamp)
    tStamp = os.path.getmtime(fName +glo.QDSpy_cPickleFileExt)
    tPck   = datetime.fromtimestamp(tStamp)
    return (tPck > tPy)
  except WindowsError:  
    pass
  return False

# ---------------------------------------------------------------------
def getStimExists(_fName):  
  # Check if stimulus file (.py) exists
  #
  return os.path.isfile(_fName +glo.QDSpy_stimFileExt)
  
# ---------------------------------------------------------------------
def getShortText(_win, _txt, _widget):
  #
  #
  metrics = QtGui.QFontMetrics(_win.font())
  return metrics.elidedText(_txt, QtCore.Qt.ElideRight, _widget.width())
  
# ---------------------------------------------------------------------
def getLEDGUIObjects(_this, _LED):
  #
  #
  if   (_LED["LEDIndex"] == 0) and (_LED["devIndex"] == 0):
    return [_this.spinBoxLED1, _this.label_LED1, _this.pushButtonLED1]
  elif (_LED["LEDIndex"] == 1) and (_LED["devIndex"] == 0):
    return [_this.spinBoxLED2, _this.label_LED2, _this.pushButtonLED2]
  elif (_LED["LEDIndex"] == 2) and (_LED["devIndex"] == 0):
    return [_this.spinBoxLED3, _this.label_LED3, _this.pushButtonLED3]
  elif (_LED["LEDIndex"] == 0) and (_LED["devIndex"] == 1):
    return [_this.spinBoxLED4, _this.label_LED4, _this.pushButtonLED4]
  elif (_LED["LEDIndex"] == 1) and (_LED["devIndex"] == 1):
    return [_this.spinBoxLED5, _this.label_LED5, _this.pushButtonLED5]
  elif (_LED["LEDIndex"] == 2) and (_LED["devIndex"] == 1):
    return [_this.spinBoxLED6, _this.label_LED6, _this.pushButtonLED6]
  else:
    return [None]*3
  
# ---------------------------------------------------------------------
def updateToggleButton(_btn):
  s = _btn.text().split("\n")
  if len(s) == 1:
    _btn.setText("{0}".format("on" if _btn.isChecked() else "off"))
  else:  
    _btn.setText("{0}\n{1}"
                 .format(s[0], "on" if _btn.isChecked() else "off"))

# --------------------------------------------------------------------- 