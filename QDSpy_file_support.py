#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QDSpy module - support routines for file handling

Copyright (c) 2013-2025 Thomas Euler
All rights reserved.

2024-06-19 - Ported from `PyQt5` to `PyQt6`
           - Reformatted (using Ruff)
2024-08-10 - GUI-related routines moved to `QDSpy_GUI_main`
           - Moved hash support functions here 
2025-01-08 - removed dependency of `QDSpy_global.py` by copying the 
             needed definitions here; not great but allows using 
             general file-related functions from this module in 
             `QDSpy_global.py`           
"""
# ---------------------------------------------------------------------
__author__ = "code@eulerlab.de"

import os
import platform
import hashlib
from pathlib import Path
from datetime import datetime

PLATFORM_WINDOWS = platform.system() == "Windows"
if not PLATFORM_WINDOWS:
    WindowsError = FileNotFoundError

# fmt: off
QDSpy_stimFileExt    = ".py"    
QDSpy_cPickleFileExt = ".pickle"
# fmt: on
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
        if (os.path.splitext(fName)[1]).lower() == QDSpy_stimFileExt:
            fName = (os.path.splitext(os.path.basename(fName)))[0]
            stimFNames.append(os.path.join(_path, fName))
    return stimFNames

# ---------------------------------------------------------------------
def getFNameNoExt(_fName :str) -> str:
    """ Extract just file name, no path nor extension
    """
    return Path(_fName).with_suffix("").stem


def getPathReplacedExt(_fName :str, _ext :str) -> str:
    """ Replace file extension with `_ext`
    """
    return Path(_fName).with_suffix(_ext).__str__()


def getPathNoFileName(_fName :str) -> str:
    """ Extract path w/o file name
    """
    return Path(_fName).parents[0].__str__()


def getFileExt(_fname :str) -> str:
    """ Get only file extension
    """
    return Path(_fname).suffix.__str__()

# ---------------------------------------------------------------------
def getFileTimeStamp(_fName: str) -> float:
    """ Get the files time stamp
    """
    fobj = Path(_fName).resolve()
    tStamp = fobj.stat().st_mtime
    return datetime.fromtimestamp(tStamp)


def getStimCompileState(_fName: str) -> bool:
    """ Check if pickle-file is current
    """
    fname_py = Path(_fName).with_suffix(QDSpy_stimFileExt).__str__()
    fname_pk = Path(_fName).with_suffix(QDSpy_cPickleFileExt).__str__()
    if getFileExists(fname_py) and getFileExists(fname_pk):
        tPy = getFileTimeStamp(fname_py)
        tPk = getFileTimeStamp(fname_pk)
        return tPk > tPy
    else:
        False

# ---------------------------------------------------------------------
def getStimExists(_fName :str) -> bool:
    """ Check if stimulus file (.py) exists
    """
    return Path(_fName).with_suffix(QDSpy_stimFileExt).is_file()


def getFileExists(_fName :str) -> bool:
   """ Check if a file `_fName` exists
   """
   return Path(_fName).is_file()
   
# ---------------------------------------------------------------------
def getQDSpyPath() -> str:
    """ Get QDSpy path 
    """
    '''
    _pathQDSpy = ""
    pList = os.environ['PYTHONPATH'].split(";")
    for p in pList:
        pParts = os.path.split(p)
        if pParts[-1].lower() == "qdspy":
            _pathQDSpy = p
    return _pathQDSpy        
    '''
    return Path(__file__).parents[0].__str__()


def getCurrentPath() -> str:
   """ Get working directory
   """
   return Path().cwd().__str__()

# ---------------------------------------------------------------------
def getCompletePath(path :str) -> str:
   """ Complete path 
   """
   return Path(path).resolve().__str__()


def getJoinedPath(path0 :str, path1 :str, path2 :str = "") ->str:
   """ Join two paths
   """
   return Path(path0, path1, path2).__str__()

'''
def repairPath(_path: str) -> str:
    """Repair path if necessary
    """
    if platform.system() == "Linux":
        _path = _path.replace("\\", "/").replace(".", "")
        _path = _path[1:] if _path[0] == ":" else _path
    return _path
'''
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
