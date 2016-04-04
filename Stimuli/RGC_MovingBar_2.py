#!/usr/bin/env python
# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------
import QDS
import math

# --------------------------------------------------------------------------
def MoveBarSeq():
  # A function that presents the moving bar in the given number of 
  # directions (= moving bar sequence)
  #
  for rot_deg in p["DirList"]:
    # Calculate rotation angle and starting position of bar
    #
    rot_rad = (rot_deg -90)/360.0 *2 *math.pi
    x       = math.cos(rot_rad) *( moveDist_um /2.0)
    y       = math.sin(rot_rad) *(-moveDist_um /2.0)

    # Move the bar stepwise across the screen (as smooth as permitted
    # by the refresh frequency)
    #
    QDS.Scene_Clear(durMarker_s, 1)
    for iStep in range(int(nFrToMove)):
      QDS.Scene_RenderEx(p["durFr_s"], [1], [(x,y)], [(1.0,1.0)], [rot_deg], 0)
      x    -= math.cos(rot_rad) *umPerFr
      y    += math.sin(rot_rad) *umPerFr

# --------------------------------------------------------------------------
# Main script
# --------------------------------------------------------------------------
QDS.Initialize("RGC_MovingBar", "'moving bar' in fingerprinting stimulus set")

# Define global stimulus parameters
#
p = {"nTrials"         : 2, 
     "DirList"         : [0,180, 45,225, 90,270, 135,315],   

     "vel_umSec"       : 1000.0, # speed of moving bar in um/sec
     "tMoveDur_s"      : 4.0,    # duration of movement (defines distance
                                 # the bar travels, not its speed)
     "barDx_um"        : 300.0,  # bar dimensions in um
     "barDy_um"        : 1000.0,
     "bkgColor"        : (0,0,0),       # background color
     "barColor"        : (255,255,255), # bar color
     "durFr_s"         : 1/60.0, # Frame duration
     "nFrPerMarker"    : 3
    }
QDS.LogUserParameters(p)

# Do some calculations
#
durMarker_s    = p["durFr_s"]*p["nFrPerMarker"]
freq_Hz        = round(1.0 /p["durFr_s"])
umPerFr        = float(p["vel_umSec"]) /freq_Hz
moveDist_um    = p["vel_umSec"] *p["tMoveDur_s"]
nFrToMove      = float(moveDist_um) /umPerFr

# Define stimulus objects
#
QDS.DefObj_Box(1, p["barDx_um"], p["barDy_um"])

# Start of stimulus run
#
QDS.StartScript()

QDS.SetObjColor(1, [1], [p["barColor"]])
QDS.SetBkgColor(p["bkgColor"])
QDS.Scene_Clear(3.0, 0)

# Loop the moving bar sequence nTrial times
#
QDS.Loop(p["nTrials"], MoveBarSeq)

QDS.Scene_Clear(1.0, 0)

# Finalize stimulus
#
QDS.EndScript()

# --------------------------------------------------------------------------
