#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ---------------------------------------------------------------------
import QDS

QDS.Initialize("dome_grid_sphere", "Grid to visualize stimulus in dome")

# fmt: off
# Define global stimulus parameters
gridRGB = (255, 255, 255)
bkgRGB  = (0, 0, 0)
dxScr   = 1920 //2
dyScr   = 1080 //2
nx      = 12
ny      = int(nx * dyScr / dxScr)
nTrials = 200
dtTrial = 1.0

dxBox   = dxScr / nx
dyBox   = dxBox
x0      = 0
y0      = 0 
# fmt: on

# Define objects
# Generate one box object per grid position
nB = nx * ny
for iB in range(1, nB + 1):
    QDS.DefObj_Box(iB, dxBox - 2, dyBox - 2)

QDS.DefObj_EllipseEx(1000, dxBox, dyBox)
QDS.DefObj_EllipseEx(1001, dxBox +10, dyBox +10)
QDS.DefObj_EllipseEx(1002, dxBox /5, dyBox /5)

# Fill list with parameters for every box object
BoxIndList = []
BoxPosList = []
BoxMagList = []
BoxRotList = []
BoxColList = []
BoxAlpList = []

for iX in range(nx):
    for iY in range(ny):
        iB = 1 + iX + iY * nx
        x = iX * dxBox + dxBox / 2 - dxBox * nx / 2.0
        y = iY * dyBox + dyBox / 2 - dyBox * ny / 2.0
        BoxIndList.append(iB)
        BoxPosList.append((x, y))
        BoxMagList.append((1.0, 1.0))
        BoxRotList.append(0)
        BoxColList.append(gridRGB if ((iB +iY) % 2) > 0 else bkgRGB)
        BoxAlpList.append(255)


QDS.DefObj_Box(2000, 500, 500, True)
QDS.DefShader(2000, "SPHERE")

# Start of stimulus run
QDS.StartScript()
QDS.SetBkgColor(bkgRGB)
QDS.Scene_Clear(1.0, 0)

QDS.SetObjColorEx(BoxIndList, BoxColList, BoxAlpList)
QDS.SetObjColorEx([1001], [(128,128,128)], [255])

# Present grid
for iT in range(nTrials):
    QDS.SetObjColorEx(
        [1000, 1002], 
        [gridRGB, bkgRGB] if (iT % 2) > 0 else [bkgRGB, gridRGB],
        [255] *2
    )
    QDS.Scene_RenderEx(
        dtTrial, 
        BoxIndList +[1001, 1000, 1002, 2000], 
        BoxPosList +[(x0, y0)] *4, 
        BoxMagList +[(1, 1)] *4, 
        BoxRotList +[0] *4, 
        0,
    )

QDS.Scene_Clear(1.0, 0)

# Finalize stimulus
QDS.EndScript()

# ---------------------------------------------------------------------
