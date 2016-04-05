#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ---------------------------------------------------------------------
import  random
import  QDS
import  math

QDS.Initialize("Test2", "Test for Lightcrafter")
#QDS.setColorMode((8,7,7), (0,1,1), 0)
#QDS.setColorMode((8,8,8), (0,0,0), 0)
#QDS.setColorMode((0,0,0), (0,0,0), 2)

p = {}
p['nTrials']   = 120
p['dt_s']      = 1.0/60.0
p['dxScr']     = 580
p['dyScr']     = 580
p['useStripes']= 1

random.seed(1)

# gradient
#
if p['useStripes']:
  # Use stripes to generate gradient
  #
  nRows       = 48
  nCols       = 3
  Grad_boxDx  = p['dxScr']/float(nCols)
  Grad_boxDy  = p['dyScr']/float(nRows)
  Grad_Colors = [(0,255,0),(0,0,255),(0,255,255)]

  nB          = nRows*nCols
  for iB in range(1, nB+1):
    QDS.DefObj_Box(iB, Grad_boxDx, Grad_boxDy)

  Grad_indL = []
  Grad_posL = []
  Grad_colL = []
  Grad_alpL = []
  Grad_rotL = []
  Grad_magL = []

  for iX in range(nCols):
    for iY in range(nRows):
      iB = 1 +iX +iY*nCols
      x  = iX*Grad_boxDx +Grad_boxDx/2.0 -Grad_boxDx*nCols/2.0
      y  = iY*Grad_boxDy +Grad_boxDy/2.0 -Grad_boxDy*nRows/2.0
      r  = Grad_Colors[iX][0]*iY/nRows
      g  = Grad_Colors[iX][1]*iY/nRows
      b  = Grad_Colors[iX][2]*iY/nRows
      Grad_indL.append(iB)
      Grad_posL.append((x,y))
      Grad_colL.append((r,g,b))
      Grad_rotL.append(0)
      Grad_alpL.append(255)
      Grad_magL.append((1,1))

  QDS.SetObjColorEx(Grad_indL, Grad_colL, Grad_alpL)

else:
  # Use whole objects and set color by vertex
  #
  nRows       = 1
  nCols       = 3
  Grad_boxDx  = p['dxScr']/float(nCols)
  Grad_boxDy  = p['dyScr']/float(nRows)
  Grad_RGBA   = [(0,255,0, 255),(0,0,255, 255),(0,255,255, 255)]

  nB          = nRows*nCols
  for iB in range(1, nB+1):
    QDS.DefObj_Box(iB, Grad_boxDx, Grad_boxDy)

  Grad_indL = []
  Grad_posL = []
  Grad_colL = []
  Grad_rotL = []
  Grad_magL = []

  for iX in range(nCols):
    iB = iX +1
    x  = iX*Grad_boxDx +Grad_boxDx/2.0 -Grad_boxDx*nCols/2.0
    y  = 0
    r  = Grad_RGBA[iX][0]
    g  = Grad_RGBA[iX][1]
    b  = Grad_RGBA[iX][2]
    a  = Grad_RGBA[iX][3]
    Grad_indL.append(iB)
    Grad_posL.append((x,y))
    Grad_colL.append([(r,g,b,a),(r,g,b,a),(0,0,0,a),(0,0,0,a)])
    Grad_rotL.append(0)
    Grad_magL.append((1,1))


# center spots (sinusoidal and flicker)
#
Spot_ID_sinB  = nRows*nCols+2
Spot_ID_sinG  = Spot_ID_sinB +1
Spot_ID_sinW  = Spot_ID_sinB +2
Spot_ID_flck1 = Spot_ID_sinB +3
Spot_ID_flck2 = Spot_ID_sinB +4
Spot_ID_sect  = Spot_ID_sinB +5

Spot_r        = 150
Spot_SinPer_s = 2.0

isShad        = 0
QDS.DefObj_EllipseEx(Spot_ID_sinB, Spot_r, Spot_r, isShad)
QDS.DefObj_EllipseEx(Spot_ID_sinG, Spot_r, Spot_r, isShad)
QDS.DefObj_EllipseEx(Spot_ID_sinW, Spot_r, Spot_r, isShad)
QDS.DefObj_BoxEx(Spot_ID_flck1, Spot_r, Spot_r/2, isShad)
QDS.DefObj_BoxEx(Spot_ID_flck2, Spot_r, Spot_r/2, isShad)
QDS.DefObj_SectorEx(Spot_ID_sect, Spot_r*2, Spot_r/2, 225, 270, isShad)
#QDS.DefObj_EllipseEx(Spot_ID_sect, Spot_r*1, Spot_r*1, isShad)

Spots_indL = [Spot_ID_sinB, Spot_ID_sinG, Spot_ID_sinW,
              Spot_ID_flck1, Spot_ID_flck2, Spot_ID_sect]
Spots_posL = [(-Spot_r/2.0,-Spot_r/2.0), (Spot_r/2.0,-Spot_r/2.0),
              (-Spot_r/2.0, Spot_r/2.0), (Spot_r/2.0, Spot_r*3/4),
              ( Spot_r/2.0, Spot_r*1/4), (0,0)]
Spots_magL = [(1,1), (1,1), (1,1), (1,1), (1,1), (3,3)]
Spots_rotL = [0,0,0,0,0,0]
Spots_alpL = [255,255,255,255,255,128]


QDS.DefObj_Movie(1, "rabbit.png") 

# ---------------------------------------------------------------------
def myLoop():
  QDS.Start_Movie(1, (-200,-200), [0,39,15,2], (1.0,1.0), 128, 0)

  for iT in range(p['nTrials']):
    isMark   =  int((iT % 20) == 0)

    # Update colors of sinusoidal+flickering spots
    #
    per        = math.pi*2 *iT*p['dt_s']/Spot_SinPer_s
    iSin       = (math.sin(per) +1)/2
    iCos       = (math.cos(per) +1)/2
    Spots_colL = []
    r          = 0
    g          = 0
    b          = int(255 *iSin)
    Spots_colL.append((r,g,b))
    g          = int(255 *iSin)
    b          = 0
    Spots_colL.append((r,g,b))
    g          = int(255 *iCos)
    b          = g
    Spots_colL.append((r,g,b))

    g          = int(255 *(iT % 2))
    b          = g
    Spots_colL.append((r,g,b))
    g          = int(255 *(1- (iT % 2)))
    b          = g
    Spots_colL.append((r,g,b))
    Spots_colL.append((255,128,128))

    # Set colors and render
    #
    indL       = Grad_indL +Spots_indL
    magL       = Grad_magL +Spots_magL
    posL       = Grad_posL +Spots_posL
    rotL       = Grad_rotL +Spots_rotL
    """
    indL       = Spots_indL
    magL       = Spots_magL
    posL       = Spots_posL
    rotL       = Spots_rotL
    """
    QDS.SetObjColorEx(Spots_indL, Spots_colL, Spots_alpL)
    #QDS.SetObjColorAlphaByVertex([Spot_ID_sinW], [[(255,0,0,200),(0,55,0,128)]])
    if not(p['useStripes']):
      QDS.SetObjColorAlphaByVertex(Grad_indL, Grad_colL)
    QDS.Scene_RenderEx(p['dt_s'], indL, posL, magL, rotL, isMark)

# ---------------------------------------------------------------------
QDS.StartScript()
QDS.Start_Movie(1, (0,0), [0,0,1,1], (1.0,1.0), 0, 0)

QDS.Scene_Clear(2.0, 0)

QDS.Loop(5, myLoop)

QDS.Scene_Clear(1.0, 0)
QDS.EndScript()

# ---------------------------------------------------------------------
