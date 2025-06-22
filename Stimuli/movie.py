#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ---------------------------------------------------------------------
import sys
import QDS

QDS.Initialize("movie", "Example for playing a movie")

# Define global stimulus parameters
#
p = {}
p['nTrials']   = 3                       # number of stimulus presentations
p['mScal']     = (2.0, 2.0)              # movie scaling (x, y)
p['mOrient']   = [0, 45, 90, 135]        # movie orientations
p['mAlpha']    = 250                     # transparency of movie

FrRefr_Hz = QDS.GetDefaultRefreshRate()

# Define objects
#
QDS.DefObj_Movie(1, "rabbit.jpg")

# Update parameter dictionary with the movie parameters
# -> "dxFr", "dyFr", "nFr"
#
movparams = QDS.GetMovieParameters(1)
if not movparams:
  print("Failed loading movie")
  sys.exit()

p.update(movparams)  

# Start of stimulus run
#
QDS.StartScript()
QDS.Scene_Clear(1.00, 0)

for iT in range(p['nTrials']):
  for iOrient in p['mOrient']:
    QDS.Start_Movie(1, (0,0), [0, 0, FrRefr_Hz, 1], 
                    p['mScal'], p['mAlpha'], iOrient)
    QDS.Scene_Clear(1.00, 0)
    
    QDS.Start_Movie(1, (0,0), [0,p['nFr']-1, 3, 1], 
                    p['mScal'], p['mAlpha'], iOrient)
    QDS.Scene_Clear(0.05, 1)
    QDS.Scene_Clear(1.95, 0)
    
    QDS.Start_Movie(1, (0,0), [p['nFr']-1, p['nFr']-1, 2*FrRefr_Hz, 1], 
                    p['mScal'], p['mAlpha'], iOrient)
    QDS.Scene_Clear(2.00, 0)

    QDS.Start_Movie(1, (0,0), [p['nFr']-1, p['nFr']-1, FrRefr_Hz,  1], 
                    p['mScal'], p['mAlpha'], iOrient)
    QDS.Scene_Clear(1.00, 0)
    
    QDS.Start_Movie(1, (0,0), [p['nFr']-1, 0, 3, 1], 
                    p['mScal'], p['mAlpha'], iOrient)
    QDS.Scene_Clear(0.05, 1)
    QDS.Scene_Clear(1.95, 0)
    
    QDS.Start_Movie(1, (0,0), [0, 0, 2*FrRefr_Hz, 1], 
                    p['mScal'], p['mAlpha'], iOrient)
    QDS.Scene_Clear(2.00, 0)

QDS.Scene_Clear(1.00, 0)

# Finalize stimulus
#
QDS.EndScript()

# -----------------------------------------------------------------------------

