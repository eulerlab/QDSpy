#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ---------------------------------------------------------------------
import QDS

QDS.Initialize("movie_water1", "Water movie test")

# Define global stimulus parameters
#
FrRefr_Hz = QDS.GetDefaultRefreshRate()

p = {"nTrials"         : 1,           # number of stimulus presentations  
     "movScale"        : (4.0, 4.0),  # movie scaling (x, y)
     "movOrient"       : 0,           # movie orientation
     "movAlpha"        : 255,         # transparency of movie
     "MarkPer_s"       : 1.0,         # number of markers per second
     "durFr_s"         : 1/FrRefr_Hz, # frame duration
     "nFrPerMarker"    : 3,

     "movName"         : "water1_flipped.jpg",
     "rng_seed"        : 1,           # Random seed
     "tex_ydim"        : 90,          # Output resolution, Y dimension
     "tex_xdim"        : 128,         # Output resolution, X dimension
     "duration"        : 180,         # Stimulus duration (seconds)
     "yNodes"          : 6,           # Generator image, Y dimension
     "xNodes"          : 6,           # Generator image, X dimension
     "upFactor"        : 48,          # Upscaling factor
     "tempFreq"        : 2.5,         # Temporal frequency
     "tempKernelLength": 61,          # Length of temporal filter kernel
     "spatialFreq"     : 0.06,        # Spatial frequency [?]
     "fps"             : 60,          # Frame rate per second
     "screenSize"      : [64, 45],    # Screen resolution
     "compensator"     : 8}           # keep the spatial frequencies 
                                      # unchanged as the upscale factor 
                                      # changes
QDS.LogUserParameters(p)

# Define objects
#
QDS.DefObj_Movie(1, p["movName"])   
[dxFr, dyFr, nFr] = QDS.GetMovieParameters(1)
dFr               = 1 /FrRefr_Hz
nMark             = int(nFr /FrRefr_Hz /p["MarkPer_s"])
dMark_s           = p["nFrPerMarker"] *dFr

# Start of stimulus run
#
QDS.StartScript()
QDS.Scene_Clear(1.00, 0)

for iT in range(p["nTrials"]):
  QDS.Start_Movie(1, (0,0), [0, 0, FrRefr_Hz, 1], 
                  p["movScale"], p["movAlpha"], p["movOrient"])
  QDS.Scene_Clear(1.00, 0)
  QDS.Start_Movie(1, (0,0), [0, nFr-1, 1, 1], 
                  p["movScale"], p["movAlpha"], p["movOrient"])

  for iM in range(nMark):
    QDS.Scene_Clear(dMark_s, 1)
    QDS.Scene_Clear(p["MarkPer_s"] -dMark_s, 0)
      
QDS.Scene_Clear(1.00, 0)

# Finalize stimulus
#
QDS.EndScript()

# -----------------------------------------------------------------------------

