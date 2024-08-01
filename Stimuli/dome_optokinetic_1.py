#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ---------------------------------------------------------------------
import QDS
import random

QDS.Initialize("Optokinetic1", "Moving vertical bar gratings")

p = {}
p["nTrials"] = 150
p["dt_s"] = 1.0  # 1/60.0
p["nRows"] = 1
p["nCols"] = 1

boxDx = max(30, 500.0 / p["nCols"])
boxDy = max(30, 500.0 / p["nRows"])
nObj = p["nRows"] * p["nCols"]

ObjShaList = []
ObjIndList = []
ObjPosList = []
ObjMagList = []
ObjRotList = []

for iObj in range(1, nObj + 1):
    isShaObj = int(((iObj % 2) > 0))
    if isShaObj:
        ObjShaList.append(iObj)
    QDS.DefObj_EllipseEx(iObj, boxDx, boxDy, isShaObj)
    # QDS.DefObj_BoxEx(iObj, boxDx, boxDy, isShaObj)
    r = random.randint(5, 250)
    g = random.randint(5, 250)
    b = random.randint(5, 250)
    QDS.SetObjColorEx([iObj], [(r, g, b)], [255])

    ObjIndList.append(iObj)
    ObjMagList.append((1.0, 1.0))
    ObjRotList.append(10.0 * iObj - 1)

border = 1.2
for iX in range(p["nCols"]):
    for iY in range(p["nRows"]):
        x = (iX + 0.5 - p["nCols"] / 2.0) * boxDx * border
        y = (iY + 0.5 - p["nRows"] / 2.0) * boxDy * border
        ObjPosList.append((x, y))

QDS.DefShader(1, "SQUARE_WAVE_GRATING_MIX4")

perLen_um = 30.0
perDur_s = 0.5
mixA = 0.2
"""
minRGBA   = (0, 200, 0, 255)
maxRGBA   = (200, 0, 0, 255)
"""
minRGBA = (0, 0, 0, 255)
maxRGBA = (255, 255, 255, 255)
QDS.SetShaderParams(1, [perLen_um, perDur_s, minRGBA, maxRGBA, mixA])

QDS.SetObjShader(ObjShaList, len(ObjShaList) * [1])


# ---------------------------------------------------------------------
def myLoop():
    for iT in range(p["nTrials"]):
        mixA = random.random()
        perLen_um = random.randint(10, 500)
        QDS.SetShaderParams(1, [perLen_um, perDur_s, minRGBA, maxRGBA, mixA])
        ObjRotList = [random.randint(0, 359)] * nObj
        QDS.Scene_RenderEx(p["dt_s"], ObjIndList, ObjPosList, ObjMagList, ObjRotList, 0)


# ---------------------------------------------------------------------
QDS.StartScript()
QDS.Scene_Clear(1.0, 0)
QDS.Loop(300, myLoop)
QDS.Scene_Clear(1.0, 0)
QDS.EndScript()

# ---------------------------------------------------------------------
