#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ---------------------------------------------------------------------
import  random
import  QDS 

QDS.Initialize("Test3", "Test for Lightcrafter")

nTrials   = 50
dt_s      = 0.050
dxScr     = 800
dyScr     = 600

random.seed(1)

# gradient
#
Grad_boxDx  = dxScr/4
Grad_boxDy  = dyScr/4
Grad_RGBA   = [(0,255,0, 255),(0,0,255, 255),(0,255,255, 255),(0,0,0, 255)]

QDS.DefObj_Box(1, Grad_boxDx, Grad_boxDy)
QDS.SetObjColorAlphaByVertex([1], [Grad_RGBA])
QDS.DefObj_Box(2, Grad_boxDx, Grad_boxDy)
QDS.SetObjColorEx([2], [(128,128,128)])

# ---------------------------------------------------------------------
QDS.StartScript()
QDS.Scene_Clear(1.0, 0)

# ---------------------------------------------------------------------
for iT in range(nTrials):                     
  QDS.Scene_RenderEx(dt_s, [1,2], [(-100,0),(+100,0)], [(1,1),(1,1)], [0,0], 0)
  #QDS.Scene_RenderEx(dt_s, [1], [(-100,0)], [(1,1)], [0], 0)

# ---------------------------------------------------------------------
QDS.Scene_Clear(1.0, 0)
QDS.EndScript()

# ---------------------------------------------------------------------
