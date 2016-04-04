#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ---------------------------------------------------------------------
import  QDS
import  random

QDS.Initialize("Test6", "Test for Lightcrafter")
#QDS.setColorMode((8,7,7), (0,1,1), 0)

random.seed(1)

nTrials    = 5 
dt_s       = 10.0 #1/60.0
nRows      = 5
nCols      = 5

boxDx      = max(30, 500.0/nCols)
boxDy      = max(30, 500.0/nRows)
nObj       = nRows*nCols

ObjShaList = []
ObjIndList = []
ObjPosList = []
ObjMagList = []
ObjRotList = []

for iObj in range(1, nObj+1):
  isShaObj = int(((iObj % 2) == 0))
  if isShaObj:
    ObjShaList.append(iObj)
  QDS.DefObj_EllipseEx(iObj, boxDx, boxDy, isShaObj)
  #QDS.DefObj_BoxEx(iObj, boxDx, boxDy, isShaObj)
  r        = random.randint(5, 250)
  g        = random.randint(5, 250)
  b        = random.randint(5, 250)
  QDS.SetObjColorEx([iObj], [(r,g,b)], [255])

  ObjIndList.append(iObj)
  ObjMagList.append((1.0,1.0))
  ObjRotList.append(10.0 *iObj-1)

border     = 1.2
for iX in range(nCols):
  for iY in range(nRows):
    x  = (iX+0.5 -nCols/2.0)*boxDx*border
    y  = (iY+0.5 -nRows/2.0)*boxDy*border
    ObjPosList.append((x,y))

QDS.DefShader(1, "SINE_WAVE_GRATING_MIX")

perLen_um = 30.0
perDur_s  = 0.5
"""
minRGBA   = (0, 200, 0, 255)
maxRGBA   = (200, 0, 0, 255)
"""
minRGBA   = ( 20, 20, 20, 255)
maxRGBA   = (235,235,235, 255)
QDS.SetShaderParams(1, [perLen_um, perDur_s, minRGBA, maxRGBA])

QDS.SetObjShader(ObjShaList, len(ObjShaList)*[1])

# ---------------------------------------------------------------------
def myLoop():
  for iT in range(nTrials):
    """
    QDS.SetObjShader(ObjShaList, len(ObjShaList)//2*[1,1])    
    QDS.Scene_RenderEx(dt_s, ObjIndList, ObjPosList, ObjMagList, ObjRotList, 0)
    QDS.SetObjShader(ObjShaList, len(ObjShaList)//2*[-1,-1])    
    """
    QDS.Scene_RenderEx(dt_s, ObjIndList, ObjPosList, ObjMagList, ObjRotList, 0)

# ---------------------------------------------------------------------
QDS.StartScript()
QDS.Scene_Clear(1.0, 0)
QDS.Loop(300, myLoop)
QDS.Scene_Clear(1.0, 0)
QDS.EndScript()

# ---------------------------------------------------------------------