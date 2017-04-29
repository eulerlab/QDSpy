#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ---------------------------------------------------------------------
import QDS

QDS.Initialize("video_perlin32_ovl", "Perlin noise test")

# Define global stimulus parameters
#
FrRefr_Hz = QDS.GetDefaultRefreshRate()

p = {"nTrials"         : 1,           # number of stimulus presentations  
     "vidScale"        : (3.0, 3.0),  # movie scaling (x, y)
     "vidOrient"       : 0,           # movie orientation
     "vidAlpha"        : 255,         # transparency of movie
     "MarkPer_s"       : 1.0,         # number of markers per second
     "durFr_s"         : 1/FrRefr_Hz, # frame duration
     "nFrPerMarker"    : 3,
     "vidName"         : "Perlin32.avi"}

QDS.LogUserParameters(p)

# Define objects
# 
QDS.DefObj_Video(1, p["vidName"])   
QDS.DefObj_Video(2, p["vidName"]) 
vidparams         = QDS.GetVideoParameters(1)
p["vidparams"]    = vidparams
dFr               = 1 /FrRefr_Hz
nMark             = int(vidparams["nFr"] /FrRefr_Hz /p["MarkPer_s"])
dMark_s           = p["nFrPerMarker"] *dFr
dInterval_s       = 1.0/p["MarkPer_s"]

nMark             = 10

# Start of stimulus run
#
QDS.StartScript()
QDS.Scene_Clear(1.00, 0)

for iT in range(p["nTrials"]):
  QDS.Start_Video(1, (0,0), p["vidScale"], p["vidAlpha"], p["vidOrient"],
                  _screen=0) 
  QDS.Start_Video(2, (0,0), p["vidScale"], p["vidAlpha"], p["vidOrient"],
                  _screen=1) 
  
  for iM in range(nMark):
    QDS.Scene_Clear(dMark_s, 1)
    QDS.Scene_Clear(dInterval_s -dMark_s, 0)
      
QDS.Scene_Clear(1.00, 0)

# Finalize stimulus
#
QDS.EndScript()

# -----------------------------------------------------------------------------
