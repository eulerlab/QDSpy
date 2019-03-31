#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QDSpy module - gamma correction functions

Copyright (c) 2013-2019 Thomas Euler
All rights reserved.
"""
# ---------------------------------------------------------------------
__author__ 	= "code@eulerlab.de"

import numpy
import sys
import time
from   ctypes             import windll
import QDSpy_global       as glo
import QDSpy_stim_support as ssp
import QDSpy_stim         as stm

# ---------------------------------------------------------------------
def generateLinearLUT ():
  # Return a linear LUT (see setGammaLUT for details)
  #
  tempLUT = []
  for j in range(3):
    temp = list(range(256))
    temp = [float(v)/255.0 for v in temp]
    tempLUT.append(temp)

  newLUT = numpy.array(tempLUT)
  newLUT = (255*newLUT).astype(numpy.uint16)
  newLUT.byteswap(True)
  return newLUT

# ---------------------------------------------------------------------
def generateInverseLUT ():
  # ... for testing purposes
  #
  tempLUT = []
  for j in range(3):
    temp = list(range(255,-1,-1))
    temp =[float(v)/255.0 for v in temp]
    tempLUT.append(temp)

  newLUT = numpy.array(tempLUT)
  newLUT = (255*newLUT).astype(numpy.uint16)
  newLUT.byteswap(True)
  return newLUT

# ---------------------------------------------------------------------
def setGammaLUT (_winDC, _LUT):
  # Set a look-up table (LUT) that allows to correct all presented color
  # values, e.g. if the presentation device is not linear
  #
  # _LUT has to be an uint16-type 3x256 numpy array.
  #
  if not(sys.platform=='win32'):
    return stm.StimErrC.notYetImplemented

  if (len(_LUT) != 3) or (len(_LUT[0]) != 256):
    return stm.StimErrC.invalidDimensions

  # For some unclear reason it fails to return a valid result when called
  # for the first time ...
  #
  for j in range(5):
    try:
      res = windll.gdi32.SetDeviceGammaRamp(_winDC & 0xFFFFFFFF, _LUT.ctypes)
    except TypeError:
      res = windll.gdi32.SetDeviceGammaRamp(_winDC, _LUT.ctypes)
    time.sleep(0.1)
    if res:
      break

  if res:
    ssp.Log.write("OK", "SetDeviceGammaRamp worked")
    return stm.StimErrC.ok
  else:
    ssp.Log.write("ERROR", "SetDeviceGammaRamp failed")
    return stm.StimErrC.SetGammaLUTFailed

# ---------------------------------------------------------------------
def restoreGammaLUT (_winDC):
  # ...
  #
  return setGammaLUT(_winDC, generateLinearLUT())

# ---------------------------------------------------------------------
def loadGammaLUT (_fName):
  # ...
  #
  ssp.Log.write(" ", "Loading user-defined gamma LUT file ...")

  try:
    rgb = []
    r   = []
    g   = []
    b   = []
    fName   = _fName +glo.QDSpy_LUTFileExt
    with open(fName, 'r') as LUTFile:
      for line in LUTFile:
        rgb = [int(v.strip()) for v in line.split(",")]
        r.append(rgb[0])
        g.append(rgb[1])
        b.append(rgb[2])

    newLUT = numpy.array([r,g,b])
    newLUT = newLUT.astype(numpy.uint16)
    ssp.Log.write("ok", "... done")
    return newLUT

  except IOError:
    ssp.Log.write("ERROR", "gamma LUT file `{0}` not found".format(fName))
    return generateLinearLUT()

# ---------------------------------------------------------------------
