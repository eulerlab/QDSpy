#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ---------------------------------------------------------------------
import QDS

QDS.Initialize("movie", "Example for playing a movie")

# Define global stimulus parameters
#
nTrials   = 3                       # number of stimulus presentations
mScal     = (2.0, 2.0)              # movie scaling (x, y)
mOrient   = [0, 45, 90, 135]        # movie orientations
mAlpha    = 250                     # transparency of movie

FrRefr_Hz = QDS.GetDefaultRefreshRate()

# Define objects
#
QDS.DefObj_Movie(1, "rabbit.jpg")
[dxFr, dyFr, nFr] = QDS.GetMovieParameters(1)

# Start of stimulus run
#
QDS.StartScript()
QDS.Scene_Clear(1.00, 0)

for iT in range(nTrials):
  for iOrient in mOrient:
    QDS.Start_Movie(1, (0,0), [0, 0, FrRefr_Hz, 1], mScal, mAlpha, iOrient)
    QDS.Scene_Clear(1.00, 0)
    QDS.Start_Movie(1, (0,0), [0,nFr-1, 3, 1], mScal, mAlpha, iOrient)
    QDS.Scene_Clear(0.05, 1)
    QDS.Scene_Clear(1.95, 0)
    QDS.Start_Movie(1, (0,0), [nFr-1, nFr-1, 2*FrRefr_Hz, 1], mScal, mAlpha, iOrient)
    QDS.Scene_Clear(2.00, 0)

    QDS.Start_Movie(1, (0,0), [nFr-1, nFr-1, FrRefr_Hz,  1], mScal, mAlpha, iOrient)
    QDS.Scene_Clear(1.00, 0)
    QDS.Start_Movie(1, (0,0), [nFr-1, 0, 3, 1], mScal, mAlpha, iOrient)
    QDS.Scene_Clear(0.05, 1)
    QDS.Scene_Clear(1.95, 0)
    QDS.Start_Movie(1, (0,0), [0, 0, 2*FrRefr_Hz, 1], mScal, mAlpha, iOrient)
    QDS.Scene_Clear(2.00, 0)

QDS.Scene_Clear(1.00, 0)

# Finalize stimulus
#
QDS.EndScript()

# -----------------------------------------------------------------------------

