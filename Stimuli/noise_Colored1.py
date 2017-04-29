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
p = {}
p['dtFr_s']    = 3/60.0  # presentation time per pattern
p['nTrials']   = 50      # # of repeats
p['nPrMark']   = 20      # present marker every p['nPrMark']*p['dtFr_s']
p['nRows']     = 30      # dimensions of pattern grid
p['nCols']     = 30
p['boxDx']     = 15      # box size in um
p['boxDy']     = 15
p['dRot_step'] = 0       # angle by which boxes are rotated

# Define objects
# Generate one box object per grid position
#
nB        = p['nRows']*p['nCols']
for iB in range(1, nB+1):
  QDS.DefObj_Box(iB, p['boxDx'], p['boxDy'])

# Fill list with parameters for every box object
#
BoxIndList = []
BoxPosList = []
BoxMagList = []
BoxRotList = []

for iX in range(p['nCols']):
  for iY in range(p['nRows']):
    iB = 1 +iX +iY*p['nCols']
    x  = iX*p['boxDx'] +p['boxDx']/2.0 -p['boxDx']*p['nCols']/2.0
    y  = iY*p['boxDy'] +p['boxDy']/2.0 -p['boxDy']*p['nRows']/2.0
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
for iT in range(p['nTrials']):
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
    rot += p['dRot_step']
  QDS.SetObjColorEx(BoxIndList, BoxColList, BoxAlpList)
  QDS.Scene_RenderEx(p['dtFr_s'], BoxIndList, BoxPosList, BoxMagList,
                     BoxRotList, int((iT % p['nPrMark']) == 0))

QDS.Scene_Clear(1.0, 0)

# Finalize stimulus
#
QDS.EndScript()

# ---------------------------------------------------------------------
