#!/usr/bin/env python
# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------
import QDS
import math, random

# --------------------------------------------------------------------------
def MoveBarSeq():
  """ A function that presents the moving bar in the given number of
      directions (= moving bar sequence)
  """
  for rot_deg in p["DirList"]:
    # Calculate rotation angle and starting position of bar
    rot_rad = (rot_deg -90)/360.0 *2 *math.pi
    x = math.cos(rot_rad) *( moveDist_um /2.0)
    y = math.sin(rot_rad) *(-moveDist_um /2.0)

    # Move the bar stepwise across the screen (as smooth as permitted
    # by the refresh frequency)
    #QDS.Scene_Clear(durMarker_s, 1)
    iFr = 0
    for iStep in range(round(nFrToMove)):
      if iFr % nFrPerNoise == 0:
        updateNoise()
      QDS.Scene_RenderEx(
        p["durFr_s"], BoxIndList +[1],
        BoxPosList +[(x,y)],
        [(1.0,1.0)]*(nB+1),
        [0]*nB +[rot_deg],
        iStep < p["nFrPerMarker"]
        )
      x -= math.cos(rot_rad) *umPerFr
      y += math.sin(rot_rad) *umPerFr
      iFr += 1

def updateNoise():
  """ Draw background noise
  """
  #global BoxIndList, BoxPosList, nB, p
  BoxColList = []
  for iB in range(2, nB+2):
    r = 0
    g = random.randint(p["noiseG"][0], p["noiseG"][1])
    b = random.randint(p["noiseUV"][0], p["noiseUV"][1])
    a = int(max(min(255, 255*p["noiseAlpha"]), 0))
    if (p["noiseVAtten"] != 1) and (iB-2 < nB/2):
      g = int(g *p["noiseVAtten"])
      b = int(b *p["noiseVAtten"])
    BoxColList.append((r, g, b))
  QDS.SetObjColorEx(BoxIndList, BoxColList, [a]*nB)

# --------------------------------------------------------------------------
# Main script
# --------------------------------------------------------------------------
QDS.Initialize("Cricket_2", "")

# Define global stimulus parameters
#
p = {
  "nTrials"      : 5,
  "DirList"      : [0,180, 45,225, 90,270, 135,315],
  "tMoveDur_s"   : 3.0,    # duration of movement (-> traveled distance)
  "barDx_um"     : 75.0,   # "cricket" dimensions in um (Johnson et al., 2021)
  "barDy_um"     : 195.0,
  "vel_umSec"    : 650.0,  # speed of "cricket" in um/sec
  "bkgColor"     : (10,20,30, 30,20,10),
  "barColor"     : (0,0,0),
  "durFr_s"      : 1/60.0,
  "nFrPerMarker" : 3,
  "noiseRows"    : 8,      # Noise grid dimensions
  "noiseCols"    : 12,
  "noisePixDx"   : 50,     # Noise pixel size in um
  "noisePixDy"   : 50,
  "noiseUV"      : [50,255],
  "noiseG"       : [50,255],
  "noiseAlpha"   : 1,
  "noiseFreq_Hz" : 5,
  "noiseVAtten"  : 0.3
  }
QDS.LogUserParameters(p)

# Do some calculations
durMarker_s = p["durFr_s"]*p["nFrPerMarker"]
freq_Hz = round(1.0 /p["durFr_s"])
umPerFr = float(p["vel_umSec"]) /freq_Hz
moveDist_um = p["vel_umSec"] *p["tMoveDur_s"]
nFrToMove = float(moveDist_um) /umPerFr
nFrPerNoise = freq_Hz /p["noiseFreq_Hz"]

# Define stimulus objects
# "cricket"
QDS.DefObj_Box(1, p["barDx_um"], p["barDy_um"])

# Background noise
BoxIndList = []
BoxPosList = []
nB = p['noiseRows']*p['noiseCols']
for iB in range(2, nB+2):
  BoxIndList.append(iB)
  QDS.DefObj_Box(iB, p['noisePixDx'], p['noisePixDy'])

for iY in range(p['noiseRows']):
  for iX in range(p['noiseCols']):
    iB = 1 +iX +iY*p['noiseCols']
    dx = p['noisePixDx']
    dy = p['noisePixDy']
    x = iX*dx +dx/2.0 -dx*p['noiseCols']/2.0
    y = iY*dy +dy/2.0 -dy*p['noiseRows']/2.0
    BoxPosList.append((x,y))


# Start of stimulus run
QDS.StartScript()

QDS.SetObjColor(1, [1], [p["barColor"]])
QDS.SetBkgColor(p["bkgColor"])
QDS.Scene_Clear(3.0, 0)

# Loop the moving bar sequence nTrial times
QDS.Loop(p["nTrials"], MoveBarSeq)

# Finalize stimulus
QDS.Scene_Clear(1.0, 0)
QDS.EndScript()

# --------------------------------------------------------------------------
