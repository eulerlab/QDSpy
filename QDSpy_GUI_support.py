#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
#  QDS_GUI_support.py
#
#  ...
#
#  Copyright (c) 2013-2015 Thomas Euler
#  All rights reserved.
#
# ---------------------------------------------------------------------
__author__ 	= "code@eulerlab.de"

import os
from   datetime           import datetime
from   PyQt4              import QtCore, QtGui
from   QDSpy_global       import *

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
    if (os.path.splitext(fName)[1]).lower() == QDSpy_stimFileExt:
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
  tPy    = datetime.fromtimestamp(os.path.getmtime(fName +QDSpy_stimFileExt))
  try:
    tPck = datetime.fromtimestamp(os.path.getmtime(fName +QDSpy_cPickleFileExt))
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
"""
def getDictKeySafe(_dict, _key):
  #
  #
  try:
    return _dict[_key]
  except KeyError:
    return None
"""

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
 