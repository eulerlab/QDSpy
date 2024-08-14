#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QDSpy module - support routines for file handling

Copyright (c) 2013-2024 Thomas Euler
All rights reserved.

2024-06-19 - Ported from `PyQt5` to `PyQt6`
           - Reformatted (using Ruff)
2024-08-10 - GUI-related routines moved to `QDSpy_GUI_main`
           - Moved hash support functions here 
"""
# ---------------------------------------------------------------------
__author__ = "code@eulerlab.de"

import os
import platform
import hashlib
from datetime import datetime
import QDSpy_global as glo

PLATFORM_WINDOWS = platform.system() == "Windows"
if not PLATFORM_WINDOWS:
    WindowsError = FileNotFoundError


# ---------------------------------------------------------------------
def getStimFileLists(_path):
    """ Make a list of the stimulus files (including path) present in the
        given path
    """
    f = []
    stimFNames = []
    for dirpath, dirnames, filenames in os.walk(_path):
        f.extend(filenames)
        break
    for fName in f:
        if (os.path.splitext(fName)[1]).lower() == glo.QDSpy_stimFileExt:
            fName = (os.path.splitext(os.path.basename(fName)))[0]
            stimFNames.append(os.path.join(_path, fName))
    return stimFNames


# ---------------------------------------------------------------------
def getFNameNoExt(_fName):
    """ Extract just file name, no path nor extension
    """
    return (os.path.splitext(os.path.basename(_fName)))[0]

# ---------------------------------------------------------------------
def getStimCompileState(_fName: str) -> bool:
    """ Check if pickle-file is current
    """
    _fName = os.path.splitext(_fName)[0]
    fPath = repairPath(_fName)
    print(fPath)
    try:
        tStamp = os.path.getmtime(fPath + glo.QDSpy_stimFileExt)
        tPy = datetime.fromtimestamp(tStamp)
        tStamp = os.path.getmtime(fPath + glo.QDSpy_cPickleFileExt)
        tPck = datetime.fromtimestamp(tStamp)
        return tPck > tPy
    
    except WindowsError:
        pass

    return False

# ---------------------------------------------------------------------
def getStimExists(_fName):
    """ Check if stimulus file (.py) exists
    """
    fPath = repairPath(_fName) + glo.QDSpy_stimFileExt
    print(fPath)
    return os.path.isfile(fPath)

# ---------------------------------------------------------------------
def getQDSpyPath() -> str:
    """Get QDSpy path from `PYTHONPATH`
    """
    _pathQDSpy = ""
    pList = os.environ['PYTHONPATH'].split(";")
    for p in pList:
        pParts = os.path.split(p)
        if pParts[-1].lower() == "qdspy":
            _pathQDSpy = p
    return _pathQDSpy        

# ---------------------------------------------------------------------
def repairPath(_path: str) -> str:
    """Repair path if necessary
    """
    if platform.system() == "Linux":
        _path = _path.replace("\\", "/").replace(".", "")
        _path = _path[1:] if _path[0] == ":" else _path
    return _path

# ---------------------------------------------------------------------
'''
def getShortText(_win, _txt, _widget):
    metrics = QtGui.QFontMetrics(_win.font())
    return metrics.elidedText(_txt, QtCore.Qt.TextElideMode.ElideRight, _widget.width())


# ---------------------------------------------------------------------
def getLEDGUIObjects(_this, _LED):
    if (_LED["LEDIndex"] == 0) and (_LED["devIndex"] == 0):
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
        return [None] * 3


# ---------------------------------------------------------------------
def updateToggleButton(_btn, _txtList=["on", "off"]):
    s = _btn.text().split("\n")
    f = _btn.isChecked()
    if len(s) == 1:
        s = "{0}".format(_txtList[0] if f else _txtList[1])
    else:
        s = "{0}\n{1}".format(s[0], _txtList[0] if f else _txtList[1])
    _btn.setText(s)
'''
# ---------------------------------------------------------------------
def getHashStr(_str):
  #
  #
  m = hashlib.md5()
  m.update(_str.encode('utf-8'))
  return m.hexdigest()

# ---------------------------------------------------------------------
def getHashStrForFile(_sFName):
  #
  #
  m = hashlib.md5()
  with open(_sFName, "rb") as f:
    while True:
      data = f.read(65536)
      if not data:
        break
      m.update(data)
  return m.hexdigest()

# ---------------------------------------------------------------------
