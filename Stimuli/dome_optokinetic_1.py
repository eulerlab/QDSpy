#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ---------------------------------------------------------------------
import QDS
import random

# Initialize QDS (allways needs to be called first)
QDS.Initialize("Optokinetic1", "Moving vertical bar gratings")

# ---------------------------------------------------------------------
# Define stimulus parameters
# (as a dictionary, to be able to write it easily to the log)
p = {}
p["nTrials"]   = 1
p["dxy"]       = (1200, 600)          # Stimulus size in um
p["pxy"]       = (0, 0)               # Stimulus centre position in um 
p["mxy"]       = (1.0, 1.0)           # Magnification factor
p["rot_deg"]   = 90                   # Rotation angle of grating in degrees

# Define grating parameters
p["dtTrial_s"] = 3.0                  # Duration of one trial in s
p["nPer"]      = [4, 8, 16]           # Periods per stimulus area
p["rContr"]    = [0.9, 0.5, 0.1]      # Contrast ratios
p["speed"]     = 25                   # Speed factor (TODO)
p["rSeed"]     = 1                    # Random seed for trial generation

# Define grating bar colors at max. contrast
p["minRGBA"]   = (0, 0, 0, 255)
p["maxRGBA"]   = (255, 255, 255, 255)

# Calculate background color (mean)
bkgCol = tuple(
    [int((p["maxRGBA"][i] -p["minRGBA"][i]) /2 +p["minRGBA"][i]) 
     for i in range(3)]
)

# ---------------------------------------------------------------------
# Define trials (as pairs of condition indices)
# First, generate a list of all possible conditions
allConds = [(iP, iC) for iP in range(len(p["nPer"])) for iC in range(len(p["rContr"]))]

# Then, generate a list of `nTrials` shuffeled copies of this list
random.seed(p["rSeed"] )
p["trials"] = []
for iT in range(p["nTrials"]):
    random.shuffle(allConds)
    p["trials"] += allConds

# Log parameters
QDS.LogUserParameters(p)

# ---------------------------------------------------------------------
# Define stimulus box object on which the shader will be applied
GRA_ID = 1
QDS.DefObj_BoxEx(GRA_ID, p["dxy"][0], p["dxy"][1], _enShader = 1)
col = [int((p["maxRGBA"][i] -p["minRGBA"][i]) /2 +p["minRGBA"][i]) for i in range(2)]
QDS.SetObjColorEx([GRA_ID], [bkgCol], [255])

BKG_ID = 2
QDS.DefObj_BoxEx(BKG_ID, p["dxy"][0], p["dxy"][1], _enShader = 0)
col = [int((p["maxRGBA"][i] -p["minRGBA"][i]) /2 +p["minRGBA"][i]) for i in range(2)]
QDS.SetObjColorEx([BKG_ID], [bkgCol], [255])

# Define shader
SHA_ID = 1
QDS.DefShader(SHA_ID, "SQUARE_WAVE_GRATING_MIX4")

# Link shader to object
QDS.SetObjShader([GRA_ID], [SHA_ID])

# ---------------------------------------------------------------------
# Start protocol and clear screen
QDS.StartScript()
QDS.Scene_Clear(1.0, 0)

# Wait for trigger
#QDS.AwaitTTL()

# Repeat stimulus `nTrials` times
for iT in range(p["nTrials"]):
    for iP, iC in p["trials"]:
        # Get condition parameters    
        perLen_um = p["dxy"][0] /p["nPer"][iP]
        perDur_s = 1 /p["speed"] *perLen_um /p["dtTrial_s"]
        mixA = 1 -p["rContr"][iC]

        # Present gray for 0.05 s with trigger
        QDS.SetShaderParams(
            SHA_ID, [perLen_um, perDur_s, 
             p["maxRGBA"] , p["maxRGBA"] , 0.5]
        )
        QDS.Scene_RenderEx(
            0.05, 
            [GRA_ID], [p["pxy"]], [p["mxy"]], [p["rot_deg"]], 1
        )

        # Present stimulus 
        QDS.SetShaderParams(
            SHA_ID, 
            [perLen_um, perDur_s, 
             p["minRGBA"] , p["maxRGBA"] , mixA]
        )
        QDS.Scene_RenderEx(
            p["dtTrial_s"] -0.05, 
            [GRA_ID], [p["pxy"]], [p["mxy"]], [p["rot_deg"]], 0
        )

# Clear screen and end protocol
QDS.Scene_Clear(1.0, 0)
QDS.EndScript()

# ---------------------------------------------------------------------
