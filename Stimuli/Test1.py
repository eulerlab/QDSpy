#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ---------------------------------------------------------------------
import  random 
import  QDS
import  Devices.lightcrafter as LCr

QDS.Initialize("Test1", "Test for Lightcrafter")

print("---")
dev     = LCr.Lightcrafter()
result  = dev.connect()
if result[0] == LCr.ERROR.OK:
  dev.getHardwareStatus()
  dev.getSystemStatus()
  dev.getMainStatus()
  dev.getVideoSignalDetectStatus()
  dev.disconnect()
else:
  print("WARNING: This script required a lightcrafter")
print("---")

QDS.LC_setLEDCurrents([0,50,0])

nTrials = 20
random.seed(1)

nRows     = 2
nCols     = 2
boxDx     = 50
boxDy     = 50

nB        = nRows*nCols
for iB in range(1, nB+1):
  QDS.DefObj_Box(iB, boxDx, boxDy)

BoxIndList = []
BoxPosList = []
BoxMagList = []
BoxRotList = []

for iX in range(nCols):
  for iY in range(nRows):
    iB = 1 +iX +iY*nCols
    x  = iX*boxDx +boxDx/2.0 -boxDx*nCols/2.0
    y  = iY*boxDy +boxDy/2.0 -boxDy*nRows/2.0
    BoxIndList.append(iB)
    BoxPosList.append((x,y))
    BoxMagList.append((1.0, 1.0))
    BoxRotList.append(0)


QDS.StartScript()
QDS.SetBkgColor((32,16,64))
QDS.Scene_Clear(0.1, 0)

rot	= 0.0
phase = 0
for iT in range(nTrials):
  BoxColList = []
  BoxAlpList = []
  BoxRotList = []
  for iB in range(1, nB+1):
    r = 0
    g = 0
    b = 0
    if   phase == 0:
      if iB == 1 or iB == 3:
        b = 255
    elif phase == 1:
      if iB == 1 or iB == 4:
        g = 255
    if iB == 2:
      r = 128
      g = 128
      b = 128

    BoxColList.append((r, g, b))
    BoxAlpList.append(255)
    BoxRotList.append(rot)
    rot += 0.005
  QDS.SetObjColorEx(BoxIndList, BoxColList, BoxAlpList)
  QDS.Scene_RenderEx(0.050, BoxIndList, BoxPosList, BoxMagList,
                     BoxRotList, int((iT % 20) == 0))
  phase += 1
  if phase > 1:
    phase = 0

QDS.Scene_Clear(0.1, 0)
QDS.EndScript()

# ---------------------------------------------------------------------
