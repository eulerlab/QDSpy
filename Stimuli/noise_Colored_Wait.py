#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ---------------------------------------------------------------------
import  random
import  QDS

# ---------------------------------------------------------------------
def presentGrid():
  # Present grid
  #
  QDS.AwaitTTL() 

  rot	= 0.0
  for iT in range(p['nFr']):
    BoxColList = []
    BoxAlpList = []
    BoxRotList = []
    for iB in range(1, nB+1):
      r = random.randint(5, 250)
      g = random.randint(5, 250)
      b = random.randint(5, 250)
      BoxColList.append((r, g, b))
      BoxAlpList.append(127)
      BoxRotList.append(rot)
    rot += p['dRot_step']
    QDS.SetObjColorEx(BoxIndList, BoxColList, BoxAlpList)
    QDS.Scene_RenderEx(p['dtFr_s'], BoxIndList, BoxPosList, BoxMagList,
                       BoxRotList, int((iT % p['nPrMark']) == 0))

# ---------------------------------------------------------------------
QDS.Initialize("noise_Colored_wait", "Example for await trigger")

# Set random generator seed
#
random.seed(1)

# Define global stimulus parameters
#
p = {}
p['dtFr_s']    = 3/60.0  # presentation time per pattern
p['nFr']       = 50     # # of frames per trial
p['nTrials']   = 5       # # of trials
p['nPrMark']   = 20      # present marker every p['nPrMark']*p['dtFr_s']
p['nRows']     = 20      # dimensions of pattern grid
p['nCols']     = 20
p['boxDx']     = 25      # box size in um
p['boxDy']     = 25
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
    BoxMagList.append((2.0, 1.0))
    BoxRotList.append(0)

# Start of stimulus run
#
QDS.StartScript()
QDS.Scene_Clear(1.0, 0)

QDS.Loop(p["nTrials"], presentGrid)

QDS.Scene_Clear(1.0, 0)

# Finalize stimulus
#
QDS.EndScript()

# ---------------------------------------------------------------------
