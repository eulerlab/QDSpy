#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ---------------------------------------------------------------------
import  QDS

QDS.Initialize("Test_grating1", "stimulator test")

# Define global stimulus parameters
#
boxRGB  = (0,0,255)
scalRGB = (0,255,0)
nTrials = 10
dxScr   = 640
dyScr   = 480
nx      = 12
ny      = int(nx *dyScr/dxScr)
dxEdge  = 8
dyEdge  = 8
dxScal  = 200 # um
dyScal  = 200 # um

dxBox   = (dxScr -dxEdge*2)/nx
dyBox   = (dyScr -dyEdge*2)/ny

# Define objects
# Generate one box object per grid position
#
nB     = nx * ny
for iB in range(1, nB+1):
  QDS.DefObj_Box(iB, dxBox-2, dyBox-2)

QDS.DefObj_Box(1000, dxScr -dxEdge*2, dyScr -dyEdge*2)  
QDS.SetObjColorEx([1000], [boxRGB], [255])

# Define scaling elements
#
QDS.DefObj_Box(1001, dxScal, dxScal)  
QDS.SetObjColorEx([1001], [scalRGB], [80])
QDS.DefObj_Box(1002, dxScal-2, dxScal-2)  
QDS.SetObjColorEx([1002], [(0,0,0)], [80])

QDS.DefObj_Box(1003, dxScal/2, dxScal/2)  
QDS.SetObjColorEx([1003], [scalRGB], [160])
QDS.DefObj_Box(1004, dxScal/2-2, dxScal/2-2)  
QDS.SetObjColorEx([1004], [(0,0,0)], [160])

QDS.DefObj_Box(1005, dxScr, 2)  
QDS.SetObjColorEx([1005], [scalRGB], [255])
QDS.DefObj_Box(1006, 2, dyScr)  
QDS.SetObjColorEx([1006], [scalRGB], [255])

ScalIndList = [1001,1002,1003,1004, 1005,1006]
nScal =len(ScalIndList)

# Fill list with parameters for every box object
#
BoxIndList  = []
BoxPosList  = []
BoxMagList  = []
BoxRotList  = []
BoxColList  = []
BoxAlpList  = []

for iX in range(nx):
  for iY in range(ny):
    iB = 1 +iX +iY*nx
    x  = iX*dxBox +dxBox/2 -dxBox *nx/2.0
    y  = iY*dyBox +dyBox/2 -dyBox *ny/2.0
    BoxIndList.append(iB)
    BoxPosList.append((x,y))
    BoxMagList.append((1.0, 1.0))
    BoxRotList.append(0)
    BoxColList.append((0,0,0))
    BoxAlpList.append(255)

# Start of stimulus run
#
QDS.StartScript()
QDS.SetBkgColor((0,0,0))
QDS.Scene_Clear(1.0, 0)

QDS.SetObjColorEx(BoxIndList, BoxColList, BoxAlpList)

# Present grid
#
for iT in range(nTrials):
  
  QDS.Scene_RenderEx(60.0, [1000] +BoxIndList +ScalIndList, 
                     [(0,0)] +BoxPosList +[(0,0)]*nScal, 
                     [(1.0,1.0)] +BoxMagList +[(1.0,1.0)]*nScal, 
                     [0] +BoxRotList +[0]*nScal, 0)

QDS.Scene_Clear(1.0, 0)

# Finalize stimulus
#
QDS.EndScript()

# ---------------------------------------------------------------------
