#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ---------------------------------------------------------------------
import  random
import  QDS

QDS.Initialize("noise_Colored1", "Example for random-colored boxes flickering")

# Set random generator seed 
#
random.seed(1)

# Define global stimulus parameters
#
dtFr_s    = 3/60.0  # presentation time per pattern
nTrials   = 500     # # of repeats
nPrMark   = 20      # present marker every nPrMark *dtFr_s
nRows     = 30      # dimensions of pattern grid
nCols     = 30
boxDx     = 15      # box size in um
boxDy     = 15
dRot_step = 0       # angle by which boxes are rotated

# Define objects
# Generate one box object per grid position
#
nB        = nRows*nCols
for iB in range(1, nB+1):
  QDS.DefObj_Box(iB, boxDx, boxDy)

# Fill list with parameters for every box object
#
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

# Start of stimulus run
#
QDS.StartScript()
QDS.Scene_Clear(1.0, 0)

# Present grid
#
rot	= 0.0
for iT in range(nTrials):
  BoxColList = []
  BoxAlpList = []
  BoxRotList = []
  for iB in range(1, nB+1):
    r = random.randint(5, 250)
    g = random.randint(5, 250)
    b = random.randint(5, 250)
    BoxColList.append((r, g, b))
    BoxAlpList.append(255)
    BoxRotList.append(rot)
    rot += dRot_step
  QDS.SetObjColorEx(BoxIndList, BoxColList, BoxAlpList)
  QDS.Scene_RenderEx(dtFr_s, BoxIndList, BoxPosList, BoxMagList,
                     BoxRotList, int((iT % nPrMark) == 0))

QDS.Scene_Clear(1.0, 0)

# Finalize stimulus
#
QDS.EndScript()

# ---------------------------------------------------------------------
