#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QDSpy module - support routines for the GUI version of QDSpy

Copyright (c) 2013-2016 Thomas Euler
All rights reserved.
"""
# ---------------------------------------------------------------------
__author__ 	= "code@eulerlab.de"

import os
from   datetime import datetime
from   PyQt4 import QtCore, QtGui
import QDSpy_global as glo

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
      stimFNames.append(_path +"\\" +fName)
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
  tStamp = os.path.getmtime(fName +glo.QDSpy_stimFileExt)
  tPy    = datetime.fromtimestamp(tStamp)
  try:
    tStamp = os.path.getmtime(fName +glo.QDSpy_cPickleFileExt)
    tPck   = datetime.fromtimestamp(tStamp)
    return (tPck > tPy)
  except WindowsError:  
    pass
  return False
  
# ---------------------------------------------------------------------
def getShortText(_win, _txt, _widget):
  #
  #
  metrics = QtGui.QFontMetrics(_win.font())
  return metrics.elidedText(_txt, QtCore.Qt.ElideRight, _widget.width())
  
# ---------------------------------------------------------------------
def getLEDGUIObjects(_this, _index):
  #
  #
  if   _index == 0:
    return [_this.spinBoxLED1, _this.label_LED1]
  elif _index == 1:
    return [_this.spinBoxLED2, _this.label_LED2]
  elif _index == 2:
    return [_this.spinBoxLED3, _this.label_LED3]
  elif _index == 3:
    return [_this.spinBoxLED4, _this.label_LED4]
  else:
    return [None, None]
 
 # ---------------------------------------------------------------------
 