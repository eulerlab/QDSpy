#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
#  QDSpy_stim_draw.py
#
#  Copyright (c) 2013-2015 Thomas Euler
#  All rights reserved.
#
# ---------------------------------------------------------------------
__author__ 	= "code@eulerlab.de"

# ---------------------------------------------------------------------
import numpy              as np
import QDSpy_stim         as stm
import QDSpy_stim_support as sup
from   QDSpy_global       import *

# ---------------------------------------------------------------------
def box2vert (_ob, _iob, _sc, _Stage, _stim, _nextiV):
  # Generate vertices for a box object from the description in _ob
  #
  (dx, dy)  = _ob[stm.SO_field_size]
  (mx, my)  = _sc[stm.SC_field_magXY][_iob]
  dx2       = dx *mx /2.0
  dy2       = dy *my /2.0
  rot_deg   = _sc[stm.SC_field_rot][_iob]
  pxy       = _sc[stm.SC_field_posXY][_iob]
  rect      = [-dx2, -dy2, dx2, dy2]
  newVert   = [rect[0], rect[1], rect[2], rect[1],
               rect[2], rect[3], rect[0], rect[3]]
  newVert   = sup.rotateTranslate(newVert, rot_deg, pxy)
  newVert   = sup.toInt(newVert)
  newiVTr   = [_nextiV, _nextiV+1, _nextiV+2, _nextiV, _nextiV+2, _nextiV+3]
  if _ob[stm.SO_field_doRGBAByVert]:
    newRGBA = sup.scaleRGB(_stim, _ob[stm.SO_field_fgRGB][0]) +\
              sup.scaleRGB(_stim, _ob[stm.SO_field_fgRGB][1]) +\
              sup.scaleRGB(_stim, _ob[stm.SO_field_fgRGB][2]) +\
              sup.scaleRGB(_stim, _ob[stm.SO_field_fgRGB][3])
  else:
    tmpRGBA = _ob[stm.SO_field_fgRGB] +(_ob[stm.SO_field_alpha],)
    newRGBA = len(newVert)//2 *sup.scaleRGB(_stim, tmpRGBA)

  hList     = [stm.StimObjType.box, dy,dy, mx,my, rot_deg, pxy]
  hStr      = sup.getHashStr(hList.__str__())

  return (newVert, newiVTr, newRGBA, hStr, pxy, rot_deg)


# ---------------------------------------------------------------------
def ell2vert (_ob, _iob, _sc, _Stage, _stim, _nextiV):
  # Generate vertices for an ellipse object from the description in _ob
  #
  (dx, dy)  = _ob[stm.SO_field_size]
  (mx, my)  = _sc[stm.SC_field_magXY][_iob]
  rot_deg   = _sc[stm.SC_field_rot][_iob]
  pxy       = _sc[stm.SC_field_posXY][_iob]

  # Determine center and radii, then calculate number of triangles
  # and vertices
  #
  rx        = dx *mx /2.0
  ry        = dy *my /2.0
  rm        = (rx+ry) /2.0
  nTri      = int(min(max(5, round(rm/1.5)), stm.Ellipse_maxTr))
  nPnts     = nTri +1
  dAng      = 2*np.pi/nTri

  # Center vertex, then points on perimeter
  #
  ang       = 0
  newVert   = [0, 0]
  for i in range(1, nPnts):
    newVert.append(round(rx*np.sin(ang)))
    newVert.append(round(ry*np.cos(ang)))
    ang     += dAng
  newVert   = sup.rotateTranslate(newVert, rot_deg, pxy)
  newVert   = sup.toInt(newVert)

  newiVTr   = []
  for i in range(nTri):
    newiVTr += [_nextiV, _nextiV+i+1, _nextiV+i+2]
  newiVTr[len(newiVTr)-1] = newiVTr[1]

  if _ob[stm.SO_field_doRGBAByVert]:
    # *************
    # *************    
    # TODO: Currently uses only the first RGBA for the center and the
    #       second RGBA for the circumfence. It would be better, if RGBA[1:]
    #       were interpolated and arranged arround the circumfence ...
    # *************
    # *************
    newRGBA = sup.scaleRGB(_stim, _ob[stm.SO_field_fgRGB][0])
    tmpRGBA = (len(newVert)-1)//2 \
               *sup.scaleRGB(_stim, _ob[stm.SO_field_fgRGB][1])
    newRGBA += tmpRGBA
  else:
    tmpRGBA = _ob[stm.SO_field_fgRGB] +(_ob[stm.SO_field_alpha],)
    newRGBA = len(newVert)//2 *sup.scaleRGB(_stim, tmpRGBA)

  hList     = [stm.StimObjType.ellipse, dy,dy, mx,my, rot_deg, pxy]
  hStr      = sup.getHashStr(hList.__str__())

  return (newVert, newiVTr, newRGBA, hStr, pxy, rot_deg)


# ---------------------------------------------------------------------
def sct2vert (_ob, _iob, _sc, _Stage, _stim, _nextiV):
  # Generate vertices for a sector object from the description in _ob
  #
  (r,offs,acenter,awidth,astep) = _ob[stm.SO_field_size]
  (mx, my)  = _sc[stm.SC_field_magXY][_iob]
  rot_deg   = _sc[stm.SC_field_rot][_iob]
  pxy       = _sc[stm.SC_field_posXY][_iob]

  acenter   = -2*np.pi *acenter/360.0 +np.pi
  awidth    = 2*np.pi *awidth/360.0
  astep     = 2*np.pi *astep/360.0
  nSteps    = int(min(max(5, round(awidth/astep)), stm.Sector_maxTr))

  if offs > 0:
    # Is arc ...
    #
    nPnts   = 2*nSteps +2
    ang     = acenter -awidth/2.0
    i       = 0
    newVert = []
    while i < (nPnts-1):
      newVert.append(r *np.sin(ang))
      newVert.append(-r *np.cos(ang))
      i     += 1
      newVert.append(offs *np.sin(ang))
      newVert.append(-offs *np.cos(ang))
      i     += 1
      ang   += astep

    newiVTr = []
    for i in range(nSteps*2):
      newiVTr += [_nextiV+i, _nextiV+i+1, _nextiV+i+2]

    if _ob[stm.SO_field_doRGBAByVert]:
      RGBAout = sup.scaleRGB(_stim, _ob[stm.SO_field_fgRGB][0])
      RGBAin  = sup.scaleRGB(_stim, _ob[stm.SO_field_fgRGB][1])
      newRGBA = []
      for i in range(len(newVert)//4):
        newRGBA += RGBAout
        newRGBA += RGBAin
    else:
      tmpRGBA = _ob[stm.SO_field_fgRGB] +(_ob[stm.SO_field_alpha],)
      newRGBA = len(newVert)//2 *sup.scaleRGB(_stim, tmpRGBA)

  else:
    # Is sector ...
    #
    nPnts   = nSteps +2
    ang     = acenter -awidth/2.0
    newVert = [0, 0]
    for i in range(1, nPnts):
      newVert.append(round(r *np.sin(ang)))
      newVert.append(round(-r *np.cos(ang)))
      ang   += astep

    newiVTr   = []
    for i in range(nSteps*2):
      newiVTr += [_nextiV, _nextiV+i+1, _nextiV+i+2]
    newiVTr[len(newiVTr)-1] = newiVTr[1]

    if _ob[stm.SO_field_doRGBAByVert]:
      newRGBA = sup.scaleRGB(_stim, _ob[stm.SO_field_fgRGB][0])
      tmpRGBA = (len(newVert)-1)//2 \
                 *sup.scaleRGB(_stim, _ob[stm.SO_field_fgRGB][1])
      newRGBA += tmpRGBA
    else:
      tmpRGBA = _ob[stm.SO_field_fgRGB] +(_ob[stm.SO_field_alpha],)
      newRGBA = len(newVert)//2 *sup.scaleRGB(_stim, tmpRGBA)

  newVert   = sup.rotateTranslate(newVert, rot_deg, pxy)
  newVert   = sup.toInt(newVert)

  hList     = [stm.StimObjType.sector, r,offs,acenter,awidth,astep, mx,my,
               rot_deg, pxy]
  hStr      = sup.getHashStr(hList.__str__())

  return (newVert, newiVTr, newRGBA, hStr, pxy, rot_deg)

# ---------------------------------------------------------------------
