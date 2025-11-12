#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ---------------------------------------------------------------------
import QDS                        
import random             
import numpy as np 
import os

QDS.Initialize("MouseCam_Left") 

# Define global stimulus parameters
# 
FrRefr_Hz = QDS.GetDefaultRefreshRate()

p = {"nTrials"         : 1,           # number of stimulus presentations 
     "movScale"        : (12.5, 12.5),  # movie scaling (x, y)
     "movOrient"       : 0,           # movie orientation
     "movAlpha"        : 255,         # transparency of movie
     "durSnippet_s"    : 5.0,         # duration of snippet
     "FrameRateMovie"  : 30.0,
     "durFr_s"         : 1/FrRefr_Hz, # frame duration
     "nFrPerMarker"    : 3,           # -> 50 ms markers
     "nFrRepeats"      : 2,           # -> 30 fps
     "movName_Test"    : "EW2/test_images_rand_left.jpg",
     "movName_Train"   : "EW2/train_images_left.jpg",
     "IndexName"       : "EW2/RandomSequences"} 

""" 
Preparation of movie montages in ImageJ (Fiji):
1. Open stack
2. image -> transform -> flip vertically
3. image -> stacks -> make montage
   If possible take values for columns and rows that fit all frames and
   result in a rather square image.
   scale factor=1, remaining parameters can stay as set by default
4. Resulting montage: image -> transform -> flip vertically
5. Save montage as .jpg (or .png, if montage is not too large)
6. Under the same name as the montage, make a text file (.txt) with
   the content analogous to this:
     
   [QDSMovie2Description] 
   QDSVersionID=xQDS
   FrWidth=64
   FrHeight=64
   FrCount=750
   isFirstFrBottomLeft=True
   Comment=movies_test
    
"""
QDS.LogUserParameters(p) 
                                                      
# Define objects

Indices = np.loadtxt("stimuli/EW2/RandomSequences.txt")
UseColumn = random.randint(0,19)
RandomValue = {"SequenceUsed" : UseColumn}
QDS.LogUserParameters(RandomValue)

print(os.getcwd())

QDS.DefObj_Movie(1, p["movName_Test"])
QDS.DefObj_Movie(2, p["movName_Train"])      
movparams_Test      = QDS.GetMovieParameters(1)
p["movparams_Test"] = movparams_Test
movparams_Train     = QDS.GetMovieParameters(2)
p["movparams_Train"]= movparams_Train
dFr                 = 1 /FrRefr_Hz
nMark_Test          = int(movparams_Test["nFr"]/(p["durSnippet_s"] *FrRefr_Hz /p["nFrRepeats"]))
nMark_Train         = int(movparams_Train["nFr"]/(p["durSnippet_s"] *FrRefr_Hz /p["nFrRepeats"]))                        
dMark_s             = p["nFrPerMarker"] *dFr
nFr_Sequ            = int(p["durSnippet_s"]*p["FrameRateMovie"])

# Start of stimulus run
#
QDS.StartScript()
QDS.Scene_Clear(1.00, 0)

# Test set #1

QDS.Start_Movie(1, (0,0), [0, movparams_Test["nFr"]-1, p["nFrRepeats"], 1], p["movScale"], p["movAlpha"], p["movOrient"])

for iM in range(nMark_Test):
  QDS.Scene_Clear(dMark_s, 1)
  QDS.Scene_Clear(p["durSnippet_s"] -dMark_s, 0)

# First half of training set

for iF in range(int(nMark_Train/2)):
  FrameStart = int(Indices[iF][UseColumn])*nFr_Sequ
  FrameEnd = (int(Indices[iF][UseColumn])+1)*nFr_Sequ-1
  QDS.Start_Movie(2, (0,0), [FrameStart, FrameEnd, p["nFrRepeats"], 1], p["movScale"], p["movAlpha"], p["movOrient"])
  QDS.Scene_Clear(dMark_s, 1)
  QDS.Scene_Clear(p["durSnippet_s"] -dMark_s, 0)

# Test set #2

QDS.Start_Movie(1, (0,0), [0, movparams_Test["nFr"]-1, p["nFrRepeats"], 1], p["movScale"], p["movAlpha"], p["movOrient"])

for iM in range(nMark_Test):
  QDS.Scene_Clear(dMark_s, 1)
  QDS.Scene_Clear(p["durSnippet_s"] -dMark_s, 0)

# Second half of training set

for iF in range(int(nMark_Train/2)):
  a = iF + int(nMark_Train/2)
  FrameStart = int(Indices[a][UseColumn])*nFr_Sequ
  FrameEnd = (int(Indices[a][UseColumn])+1)*nFr_Sequ-1
  QDS.Start_Movie(2, (0,0), [FrameStart, FrameEnd, p["nFrRepeats"], 1], p["movScale"], p["movAlpha"], p["movOrient"])
  QDS.Scene_Clear(dMark_s, 1)
  QDS.Scene_Clear(p["durSnippet_s"] -dMark_s, 0)
  
#QDS.Start_Movie(2, (0,0), [int((movparams_Train["nFr"]/2)), movparams_Train["nFr"]-1, p["nFrRepeats"], 1], p["movScale"], p["movAlpha"], p["movOrient"])
    
#for iM in range(int(nMark_Train/2)):
#  QDS.Scene_Clear(dMark_s, 1)
#  QDS.Scene_Clear(p["durSnippet_s"] -dMark_s, 0)

# Test set #3
  
QDS.Start_Movie(1, (0,0), [0, movparams_Test["nFr"]-1, p["nFrRepeats"], 1], p["movScale"], p["movAlpha"], p["movOrient"])

for iM in range(nMark_Test):
  QDS.Scene_Clear(dMark_s, 1)
  QDS.Scene_Clear(p["durSnippet_s"] -dMark_s, 0)

QDS.Scene_Clear(1.00, 0)

# Finalize stimulus
#
QDS.EndScript()

# -----------------------------------------------------------------------------

