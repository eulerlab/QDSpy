#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ---------------------------------------------------------------------
import  QDS 

QDS.Initialize("Test2", "Test for Lightcrafter")
QDS.SetColorMode((8,7,7), (0,1,1), 0)

p = {}
p['nTrials']   = 60
p['dt_s']      = 0.0166666666 

QDS.DefObj_Sector(1, 100, 50, 180, 270)
#QDS.SetObjColorEx([1], [(255,128,128)], [255])
QDS.SetObjColorAlphaByVertex([1], [[(255,128,128,255),(128,128,255,0)]])
 
QDS.DefObj_Sector(2, 200, 0, 0, 350)
#QDS.SetObjColorEx([2], [(96,128,255)], [255])
QDS.SetObjColorAlphaByVertex([2], [[(128,255,128,255),(255,128,0,0)]])

# ---------------------------------------------------------------------
def myLoop():
  for iT in range(p['nTrials']):
    QDS.Scene_RenderEx(p['dt_s'], [1,2], [(0,0),(0,0)], [(1,1),(1,1)], [0,0], 0)

# ---------------------------------------------------------------------
QDS.StartScript()
QDS.Scene_Clear(1.0, 0)
QDS.Loop(100, myLoop)
QDS.Scene_Clear(1.0, 0)
QDS.EndScript()

# ---------------------------------------------------------------------