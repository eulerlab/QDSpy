#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ---------------------------------------------------------------------
import  random
import  QDS 

QDS.Initialize("Test3", "Test for Lightcrafter")

p = {}
p['nTrials']   = 50
p['dt_s']      = 0.050
p['dxScr']     = 800
p['dyScr']     = 600

random.seed(1)

# gradient
#
Grad_boxDx  = p['dxScr']/4
Grad_boxDy  = p['dyScr']/4
Grad_RGBA   = [(0,255,0, 255),(0,0,255, 255),(0,255,255, 255),(0,0,0, 255)]

QDS.DefObj_Box(1, Grad_boxDx, Grad_boxDy)
QDS.SetObjColorAlphaByVertex([1], [Grad_RGBA])
QDS.DefObj_Box(2, Grad_boxDx, Grad_boxDy)
QDS.SetObjColorEx([2], [(128,128,128)])

# ---------------------------------------------------------------------
QDS.StartScript()
QDS.Scene_Clear(1.0, 0)

# ---------------------------------------------------------------------
for iT in range(p['nTrials']):                     
  QDS.Scene_RenderEx(p['dt_s'], [1,2], [(-100,0),(+100,0)], [(1,1),(1,1)], [0,0], 0)
  #QDS.Scene_RenderEx(p['dt_s'], [1], [(-100,0)], [(1,1)], [0], 0)

# ---------------------------------------------------------------------
QDS.Scene_Clear(1.0, 0)
QDS.EndScript()

# ---------------------------------------------------------------------
