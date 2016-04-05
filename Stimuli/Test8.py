#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ---------------------------------------------------------------------
import QDS

QDS.Initialize("stimLCTest8", "")

QDS.DefObj_Box(1, 1000, 1000)

QDS.StartScript()
QDS.Scene_Clear(1.00, 0)
QDS.SetObjColorEx([1], [(0,200,0)], [255])

p = {}
p['dFr'] = 1.0/60.0
 
#def procLoop():
for j in range(0, 1000): 
  QDS.Scene_RenderEx(p['dFr'], [1], [(0,0)], [(1,1)], [0], 1)
  QDS.Scene_RenderEx(0.050 -p['dFr'], [1], [(0,0)], [(1,1)], [0], 1)
  QDS.Scene_Clear(0.150, 0)
  """
  QDS.Scene_RenderEx(p['dFr'], [1], [(0,0)], [(1,1)], [0], 1)
  QDS.Scene_Clear(p['dFr'], 0)
  """
  
#QDS.Loop(10000, procLoop) 

QDS.Scene_Clear(1.00, 0)
QDS.EndScript()

# -----------------------------------------------------------------------------
