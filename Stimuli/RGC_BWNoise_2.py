#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
import QDS
import os

# Initialize QDS
#
QDS.Initialize("RGC_Noise", "'noise' in fingerprinting stimulus set")

# Define global stimulus parameters
# 
p = {"durStim_s"       : 0.200, 
     "boxDx_um"        : 40,   
     "boxDy_um"        : 40,   
     "fIntenW"         : 255,    # intensity factor 
                                 # (pixel value(0,1) x fIntenW)
     "fNameNoise"      : "RGC_BWNoise_official",
     "durFr_s"         : 1/60.0, # Frame duration
     "nFrPerMarker"    : 3}
     
QDS.LogUserParameters(p)

# Do some calculations and preparations
#
fPath       = QDS.GetStimulusPath()
durMarker_s = p["durFr_s"] *p["nFrPerMarker"]

print(os.getcwd(), fPath)
# Read file with M sequence 
#
try:
  f         = open(fPath +"\\" +p["fNameNoise"] +'.txt', 'r')
  iLn       = 0 
  Frames    = []
    
  while 1:
    line    = f.readline()
    if not line:
      break
    parts   = line.split(',')
    if iLn == 0:
      nX    = int(parts[0])
      nY    = int(parts[1])
      nFr   = int(parts[2])
      nB    = nX*nY
    else:
      Frame = []
      for iB in range(1, nB+1):
        r   = int(parts[iB-1]) *p["fIntenW"]
        Frame.append((r,r,r))
      Frames.append(Frame)
    iLn += 1
finally:
  f.close()

# Define objects
#
# Create box objects, one for each field of the checkerboard, such that we
# can later just change their color to let them appear or disappear
#
for iB in range(1, nB+1):
  QDS.DefObj_Box(iB, p["boxDx_um"], p["boxDy_um"], 0)

# Create two lists, one with the indices of the box objects and one with
# their positions in the checkerboard; these lists later facilitate using
# the Scene_Render() command to display the checkerboard
#
BoxIndList = []
BoxPosList = []
for iX in range(nX):
  for iY in range(nY):
    iB = 1 +iX +iY*nX
    x  = iX*p["boxDx_um"] -(p["boxDx_um"]*nX/2)
    y  = iY*p["boxDy_um"] -(p["boxDy_um"]*nY/2)
    BoxIndList.append(iB)
    BoxPosList.append((x,y))

# Start of stimulus run
#
QDS.StartScript()
QDS.Scene_Clear(1.0, 0)

for iF in range(nFr):
   QDS.SetObjColor(nB, BoxIndList, Frames[iF])
   QDS.Scene_Render(durMarker_s, nB, BoxIndList, BoxPosList, 1)
   QDS.Scene_Render(p["durStim_s"] -durMarker_s, nB, BoxIndList, BoxPosList, 0)

QDS.Scene_Clear(1.0, 0)

# Finalize stimulus
#
QDS.EndScript()

# -----------------------------------------------------------------------------
