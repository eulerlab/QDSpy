#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QDSpy module - support functions for stimulus generation and compilation

'rotateTranslate()'
  Rotate the coordinates by the given angle

'scaleRGB()'
'scaleRGBShader()'
  Scale color as RGBA depending on bit depth and color mode

'getHashStr()'
'getHashStrForFile()'
  Get hashes for strings or files

'Log'
  Class that allows program-wide flexible logging. Only one instance that
  is defined in this module. Writes log messages to stdout and/or sends
  messages via a pipe to the GUI process.

Copyright (c) 2013-2024 Thomas Euler
All rights reserved.

2021-10-15 - Account for LINUX console text coloring
"""
# ---------------------------------------------------------------------
__author__ 	= "code@eulerlab.de"

import platform
import numpy as  np
import QDSpy_stim as stm

PLATFORM_WINDOWS = platform.system() == "Windows"
if PLATFORM_WINDOWS:
  #from ctypes import windll
  import Libraries.color_console as con
else:
  import Libraries.color_console_linux as con

# ---------------------------------------------------------------------
Msg_Prior_DEBUG    = -1
Msg_Prior_None     =  0
Msg_Prior_Asterisk =  1
Msg_Prior_Ok       =  2
Msg_Prior_WARNING  =  3
Msg_Prior_ERROR    =  4
Msg_Prior_DATA     =  5

# ---------------------------------------------------------------------
def rotateTranslate(_coords, _rot_deg, _posxy):
  # Rotate the coordinates in the list ([x1,y1,x2,y2, ...]) by the
  # given angle
  #
  coords    = []
  a_rad     = np.radians(_rot_deg)
  for i in range(0, len(_coords), 2):
    x       =  _coords[i] *np.cos(a_rad) \
              +_coords[i+1] *np.sin(a_rad) +_posxy[0]
    y       = -_coords[i] *np.sin(a_rad) \
              +_coords[i+1] *np.cos(a_rad) +_posxy[1]
    coords  += [x, y]
  return coords

# ---------------------------------------------------------------------
def toInt(_coords):
  # Convert the coordinates in the list to integers
  #
  coords    = []
  for v in _coords:
    coords.append(int(v))
  return coords

# ---------------------------------------------------------------------
def completeRGBList(_RGBs):
  # Complete each RGBx2 tuple if incomplete in the given list
  #
  return [tuple(list(rgb) +[0]*(stm.RGB_MAX -len(rgb))) for rgb in _RGBs]


def completeRGBAList(_RGBAs):
  # Complete each RGBAx2 tuple if incomplete in the given list
  #
  res = []
  for obj in _RGBAs:
    res.append([rgba +(0,)*(stm.RGBA_MAX -len(rgba)) for rgba in obj])
  return res

# ---------------------------------------------------------------------
def scaleRGB(_Stim, _inRGBA):
  # Scale color (RGBA) depending on bit depth and color mode (format)
  #
  if _Stim.colorMode >= stm.ColorMode.LC_first:
    # One of the lightcrafter specific modes ...
    #
    if _Stim.colorMode == stm.ColorMode.LC_G9B9:
      RGBA = np.clip(_inRGBA, 0, 255)
      g    = 2**int(RGBA[1]/255.0 *8) -1
      b    = 2**int(RGBA[2]/255.0 *8) -1
      return 0,g,b, int(RGBA[3])

    else:
      return 255,255,255,255

  else:
    # One of the "normal" modes ...
    #
    if _Stim.colorMode == stm.ColorMode.range0_255:
      RGBA = np.clip(_inRGBA, 0, 255)
      dv   = 255.0
    elif _Stim.colorMode == stm.ColorMode.range0_1:
      RGBA = np.clip(_inRGBA, 0, 1)
      dv   = 1.0

    r      = int(RGBA[0]/dv *(2**_Stim.bitDepth[0] -1)) << _Stim.bitShift[0]
    g      = int(RGBA[1]/dv *(2**_Stim.bitDepth[1] -1)) << _Stim.bitShift[1]
    b      = int(RGBA[2]/dv *(2**_Stim.bitDepth[2] -1)) << _Stim.bitShift[2]
    RGB    = tuple(np.clip((r,g,b), 0, 255))
    return RGB +(int(RGBA[3]),)

# ---------------------------------------------------------------------
def scaleRGBShader(_Stim, _inRGBA):
  # Scale color (RGBA) depending on bit depth and color mode (format)
  # into shader compatible values (0...1)
  #
  r        = _inRGBA[0]/255.0
  g        = _inRGBA[1]/255.0
  b        = _inRGBA[2]/255.0
  a        = _inRGBA[3]/255.0
  RGBA     = tuple(np.clip((r,g,b,a), 0.0, 1.0))
  return RGBA

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
'''

# ---------------------------------------------------------------------
