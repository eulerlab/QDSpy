#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
import QDS

QDS.Initialize("RGC_BG_3s", "'B/G' in fingerprinting stimulus set")

# Define global stimulus parameters
#
p = {"nTrials"         : 3, 
     "dxStim_um"       : 1000,   # Stimulus size
     "durFr_s"         : 1/60.0, # Frame duration
     "nFrPerMarker"    : 3,
     "RGB_green"       : (0,255,0),
     "RGB_blue"        : (0,0,255)}
QDS.LogUserParameters(p)

# Do some calculations
#
durMarker_s    = p["durFr_s"] *p["nFrPerMarker"]

# Define stimulus objects
#
QDS.DefObj_Ellipse(1, p["dxStim_um"], p["dxStim_um"])

# Start of stimulus run
#
QDS.StartScript() 

for iT in range(p["nTrials"]):
  QDS.SetObjColor (1, [1], [p["RGB_green"]])
  QDS.Scene_Render(durMarker_s, 1, [1], [(0,0)], 1)
  QDS.Scene_Render(3.0 -durMarker_s, 1, [1], [(0,0)], 0)

  QDS.Scene_Clear(3.0, 0)

  QDS.SetObjColor (1, [1], [p["RGB_blue"]])
  QDS.Scene_Render(durMarker_s, 1, [1], [(0,0)], 1)
  QDS.Scene_Render(3.0-durMarker_s, 1, [1], [(0,0)], 0)

  QDS.Scene_Clear(3.0, 0)

# Finalize stimulus
#
QDS.EndScript()

# --------------------------------------------------------------------------
