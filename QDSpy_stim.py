#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QDSpy module - stimulus routines, classes, and compiler

'Stim'
  Class representing a visual stimulus
  This class is a graphics API independent.

Copyright (c) 2013-2024 Thomas Euler
All rights reserved.

2024-06-15 - Small fixes for PEP violations
           - Reformatted (using Ruff)
"""
# ---------------------------------------------------------------------
__author__ = "code@eulerlab.de"

import pickle
import numpy as np
import QDSpy_global as glo
import QDSpy_stim_support as ssp
import QDSpy_stim_draw as drw
import QDSpy_stim_movie as mov
import QDSpy_stim_video as vid
import QDSpy_core_shader as csh

if glo.QDSpy_use_Lightcrafter:
    import Devices.lightcrafter as lcr
    _LCr = lcr.Lightcrafter(_isCheckOnly=True, _funcLog=ssp.Log.write)
else:
    _LCr = None


# ---------------------------------------------------------------------
# fmt: off
class ColorMode:
    range0_255        = 0
    range0_1          = 1
    LC_first          = 2
    LC_G9B9           = 2

COL_bitDepthRGB_888   = (8,8,8)
COL_bitShiftRGB_000   = (0,0,0)

RGB_MAX               = 6
RGBA_MAX              = 8

# ---------------------------------------------------------------------
class StimObjType:
    box               = 101
    ellipse           = 102
    sector            = 103
    movie             = 104
    video             = 105
    shader            = 201
    # ...

Ellipse_maxTr         = 180 # 72
Sector_maxTr          = 360
Sector_maxStep        = 10

SO_field_type         = 0
SO_field_ID           = 1
SO_field_size         = 2
SO_field_fgRGB        = 3
SO_field_alpha        = 4
SO_field_doRGBAByVert = 5
SO_field_useShader    = 6
SO_field_shProgIndex  = 7

SH_field_type         = 0
SH_field_ID           = 1
SH_field_shaderType   = 2
SH_field_Params       = 3

SM_field_type         = 0
SM_field_ID           = 1
SM_field_movieFName   = 2
SM_field_nFr          = 3
SM_field_dxFr         = 4
SM_field_dyFr         = 5

SV_field_type         = 0
SV_field_ID           = 1
SV_field_videoFName   = 2
SV_field_nFr          = 3
SV_field_dxFr         = 4
SV_field_dyFr         = 5
SV_field_fps          = 6

# - - - - - -  - - - - - -  - - - - - -  - - - - - -  - - - - - -  - -
#SO_defaultFgRGB      = (255, 255, 255)
SO_defaultFgRGBEx     = (255,255,255, 255,255,255)
SO_defaultAlpha       = 255
SO_default_RGBAByVert = 0
SO_default_useShader  = 0

# ---------------------------------------------------------------------
class StimSceType:
    changeObjCol      = 201
    changeBkgCol      = 202
    changeShParams    = 203
    changeObjShader   = 204
    # ...
    clearSce          = 211
    renderSce         = 212
    startMovie        = 213
    startVideo        = 214
    awaitTTL          = 215
    beginLoop         = 220
    endLoop           = 221
    # ...
    sendCommandToLCr  = 300
    #
    logUserParams     = 400
    # ...
    getRandom         = 500


SC_field_type         = 0
SC_field_duration_s   = 1
SC_field_index        = 2
SC_field_marker       = 3
SC_field_IDs          = 4
SC_field_posXY        = 5
SC_field_magXY        = 6
SC_field_rot          = 7
'''
SC_field_screen       = 8
'''

SC_field_RGBs         = 5
SC_field_Alphas       = 6
SC_field_doRGBAByVert = 7

SC_field_nLoopTrials  = 4

SC_field_BkgRGB       = 4

SC_field_ShID         = 4
SC_field_ShParams     = 5

SC_field_ShIDs        = 5

SC_field_MovSeq       = 8
SC_field_MovTrans     = 9
SC_field_MovScreen    = 10

SC_field_VidTrans     = 8
SC_field_VidScreen    = 9

SC_field_LCrParams    = 4

SC_field_userParams   = 4

# - - - - - -  - - - - - -  - - - - - -  - - - - - -  - - - - - -  - -
#SC_defaultBgRGB      = (0, 0, 0)
SC_defaultBgRGBEx     = (0,0,0, 0,0,0)
SC_enableRGBAByVert   = 1
SC_disableRGBAByVert  = 0

SC_vertDataSame       = 0
SC_vertDataChanged    = 1

SC_ObjNewVer          = 0x01
SC_ObjNewiVer         = 0x02
SC_ObjNewRGBA         = 0x04
SC_ObjNewAll          = 0x07
SC_ObjNewNone         = 0x00

# ---------------------------------------------------------------------
class StimLCrCmd:
    """
    connect           = 0
    disconnect        = 1
    getHardwareStatus = 2
    getSystemStatus   = 3
    getMainStatus     = 4
    getVideoSigStatus = 5
    """
    softwareReset     = 6
    setInputSource    = 7
    setDisplayMode    = 8
    """
    setVideoGamma     = 9
    """
    setTestPattern    = 10
    """
    getLEDCurrents    = 11
    """
    setLEDCurrents    = 12
    setLEDEnabled     = 13
    getLEDEnabled     = 14
    # ...

# ---------------------------------------------------------------------
class StimErrC:
    ok                  = 0
    notYetImplemented   = -1

    invalidDimensions   = -10
    invalidDuration     = -11
    invalidParamType    = -12
    inconsistentParams  = -13
    invalidAngles       = -14

    existingID          = -20
    noMatchingID        = -21

    nothingToCompile    = -50
    noStimOrNotCompiled = -51
    wrongStimFileFormat = -52
    invalidFileNamePath = -53
    noDefsInRunSection  = -54
    noShadersInRunSect  = -55
    invalidShaderType   = -56
    notShaderObject     = -57
    noCompiledStim      = -58

    movieFileNotFound   = -60
    notMovieObject      = -61
    invalidMovieDesc    = -62
    inconsMovieDesc     = -63
    invalidMovieSeq     = -64
    invalidMovieFormat  = -65

    videoFileNotFound   = -70
    invalidVideoFormat  = -71

    DeviceError_LCr     = -99

    SetGammaLUTFailed   = -200
    # ...

StimErrStr	= dict([
    (StimErrC.ok,                 "ok"),
    (StimErrC.notYetImplemented,  "Not yet implemented"),
    (StimErrC.invalidDimensions,  "Invalid dimensions"),
    (StimErrC.invalidDuration,    "Invalid duration"),
    (StimErrC.invalidParamType,   "Invalid parameter type"),
    (StimErrC.inconsistentParams, "Inconsistent parameters"),
    (StimErrC.invalidAngles,      "Angle(s) <0 or >360"),
    (StimErrC.existingID,         "Object ID(s) already exist(s)"),
    (StimErrC.noMatchingID,       "Object ID(s) not found"),
    (StimErrC.nothingToCompile,   "No objects and/or scenes to compile"),
    (StimErrC.noStimOrNotCompiled,"No stimulus defined or not yet compiled"),
    (StimErrC.wrongStimFileFormat,"Wrong stimulus file format"),
    (StimErrC.invalidFileNamePath,"Invalid file name or path"),
    (StimErrC.noCompiledStim,     "Stimulus needs to be compiled"),
    (StimErrC.noDefsInRunSection, "No object definitions allowed in run section"),
    (StimErrC.noShadersInRunSect, "Shader must be assigned to objects before run section"),
    (StimErrC.invalidShaderType,  "Invalid shader type"),
    (StimErrC.notShaderObject,    "Object(s) in list not shader-enabled"),
    (StimErrC.movieFileNotFound,  "Movie file(s) not found"),
    (StimErrC.notMovieObject,     "Object is not a movie"),
    (StimErrC.invalidMovieDesc,   "Invalid movie description"),
    (StimErrC.inconsMovieDesc,    "Movie description does not match image"),
    (StimErrC.invalidMovieSeq,    "Invalid movie sequence"),
    (StimErrC.invalidMovieFormat, "Invalid movie format"),
    (StimErrC.DeviceError_LCr,    "Device error (Lightcrafter), code={0}"),
    (StimErrC.SetGammaLUTFailed,  "Failed to set gamma LUT")
    ])
# fmt: on

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class StimException(Exception):
    def __init__(self, value, subvalue=0):
        self.value = value
        if subvalue == 0:
            self.str = StimErrStr[value]
        else:
            self.str = StimErrStr[value].format(subvalue)

    def __str__(self):
        return self.str


# ---------------------------------------------------------------------
# Stimulus class
# ---------------------------------------------------------------------
class Stim:
    def __init__(self):
        """ Initializing
        """
        self.clear()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def clear(self):
        """ Pseudo code representation of the stimulus
        (with seconds and µms as units)
        """
        self.nameStr = "n/a"
        self.descrStr = "no description"
        self.fileName = ""
        self.ObjList = []
        self.ObjDict = dict()
        self.ShList = []
        self.ShDict = dict()
        self.MovList = []
        self.MovDict = dict()
        self.VidList = []
        self.VidDict = dict()
        self.SceList = []
        self.nSce = 0
        self.curBgRGB = SC_defaultBgRGBEx

        self.LastErrC = StimErrC.ok
        self.tStart = 0.0
        self.isComp = False
        self.isRunSect = False

        self.inLoop = False
        self.iLoopSce = -1

        self.colorMode = ColorMode.range0_255
        self.bitDepth = COL_bitDepthRGB_888
        self.bitShift = COL_bitShiftRGB_000

        self.Conf = None
        self.ShManager = None
        self.isUseLCr = False

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getLastErrC(self):
        return self.LastErrC

    def getLastErrStr(self):
        return StimErrStr[self.LastErrC]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def defObj_box(self, _ID, _dx_um, _dy_um, _enShader):
        """ Define a box object and add it to the stimulus object list
        (For parameters, see QDS.py)
        """
        if (_dx_um <= 0) or (_dy_um <= 0):
            self.LastErrC = StimErrC.invalidDimensions
            raise StimException(StimErrC.invalidDimensions)
        try:
            self.ObjDict[_ID]
        except KeyError:
            pass
        else:
            self.LastErrC = StimErrC.existingID
            raise StimException(self.LastErrC)

        newBox = [
            StimObjType.box,
            _ID,
            (float(_dx_um), float(_dy_um)),
            SO_defaultFgRGBEx,
            SO_defaultAlpha,
            SO_default_RGBAByVert,
            _enShader,
            -1,
        ]
        self.ObjDict[_ID] = len(self.ObjList)
        self.ObjList.append(newBox)
        self.LastErrC = StimErrC.ok

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def defObj_ellipse(self, _ID, _dx_um, _dy_um, _enShader):
        """ Define an ellipse object and add it to the stimulus object list
        (For parameters, see QDS.py)
        """
        if (_dx_um <= 0) or (_dy_um <= 0):
            self.LastErrC = StimErrC.invalidDimensions
            raise StimException(StimErrC.invalidDimensions)
        try:
            self.ObjDict[_ID]
        except KeyError:
            pass
        else:
            self.LastErrC = StimErrC.existingID
            raise StimException(self.LastErrC)

        newEllipse = [
            StimObjType.ellipse,
            _ID,
            (float(_dx_um), float(_dy_um)),
            SO_defaultFgRGBEx,
            SO_defaultAlpha,
            SO_default_RGBAByVert,
            _enShader,
            -1,
        ]
        self.ObjDict[_ID] = len(self.ObjList)
        self.ObjList.append(newEllipse)
        self.LastErrC = StimErrC.ok

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def defObj_sector(self, _ID, _r, _offs, _angle, _awidth, _astep, _enShader):
        """ Define a sector object and add it to the stimulus object list
        (For parameters, see QDS.py)
        """
        if (_r <= _offs) or (_r <= 0) or (_offs < 0):
            self.LastErrC = StimErrC.inconsistentParams
            raise StimException(StimErrC.inconsistentParams)

        if (_angle < 0) or (_angle > 360) or (_awidth <= 1) or (_awidth > 360):
            self.LastErrC = StimErrC.invalidAngles
            raise StimException(StimErrC.invalidAngles)

        if (_astep is not None) and ((_astep < 1) or (_astep > 90)):
            _astep = None

        try:
            self.ObjDict[_ID]
        except KeyError:
            pass
        else:
            self.LastErrC = StimErrC.existingID
            raise StimException(self.LastErrC)

        newSector = [
            StimObjType.sector,
            _ID,
            (float(_r), float(_offs), float(_angle), float(_awidth), _astep),
            SO_defaultFgRGBEx,
            SO_defaultAlpha,
            SO_default_RGBAByVert,
            _enShader,
            -1,
        ]
        self.ObjDict[_ID] = len(self.ObjList)
        self.ObjList.append(newSector)
        self.LastErrC = StimErrC.ok

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def defShader(self, _shID, _shType):
        """ Define a shader
        (For parameters, see QDS.py)

        Create shader manager, if not already existent, and check if
        shader type exists
        """
        if self.ShManager is None:
            _path = glo.getQDSpyPath()
            self.ShManager = csh.ShaderManager(self.Conf, _path)
        if _shType not in self.ShManager.getShaderTypes():
            self.LastErrC = StimErrC.invalidShaderType
            raise StimException(StimErrC.invalidShaderType)

        try:
            self.ShDict[_shID]
        except KeyError:
            pass
        else:
            self.LastErrC = StimErrC.existingID
            raise StimException(self.LastErrC)

        newShader = [
            StimObjType.shader,
            _shID,
            _shType,
            self.ShManager.getDefaultParams(_shType),
        ]
        self.ShDict[_shID] = len(self.ShList)
        self.ShList.append(newShader)
        self.LastErrC = StimErrC.ok

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def defObj_movie(self, _ID, _fName):
        """ Define a movie object and add it to the movie object list
        (For parameters, see QDS.py)
        """
        tempMovie = mov.Movie(self.Conf)
        self.LastErrC = tempMovie.load(self.Conf.pathStim + _fName)
        if self.LastErrC != StimErrC.ok:
            raise StimException(self.LastErrC)

        try:
            self.MovDict[_ID]
        except KeyError:
            pass
        else:
            self.LastErrC = StimErrC.existingID
            raise StimException(self.LastErrC)

        newMovie = [
            StimObjType.movie,
            _ID,
            _fName,
            tempMovie.nFr,
            tempMovie.dxFr,
            tempMovie.dyFr,
        ]
        self.MovDict[_ID] = len(self.MovList)
        self.MovList.append(newMovie)
        self.LastErrC = StimErrC.ok

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getMovieParams(self, _ID):
        """ Get movie object parameters
        (For parameters, see QDS.py)
        """
        try:
            iMvOb = self.MovDict[_ID]
            MvOb = self.MovList[iMvOb]
        except KeyError:
            self.LastErrC = StimErrC.noMatchingID
            raise StimException(self.LastErrC)

        d = dict()
        d["dxFr"] = MvOb[SM_field_dxFr]
        d["dyFr"] = MvOb[SM_field_dyFr]
        d["nFr"] = MvOb[SM_field_nFr]
        return d

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def defObj_video(self, _ID, _fName):
        """ Define a video object and add it to the video object list
        (For parameters, see QDS.py)
        """
        tempVideo = vid.Video(self.Conf)
        self.LastErrC = tempVideo.load(self.Conf.pathStim + _fName)
        if self.LastErrC != StimErrC.ok:
            raise StimException(self.LastErrC)

        try:
            self.VidDict[_ID]
        except KeyError:
            pass
        else:
            self.LastErrC = StimErrC.existingID
            raise StimException(self.LastErrC)

        newVideo = [
            StimObjType.video,
            _ID,
            _fName,
            tempVideo.nFr,
            tempVideo.dxFr,
            tempVideo.dyFr,
            tempVideo.fps,
        ]
        self.VidDict[_ID] = len(self.VidList)
        self.VidList.append(newVideo)
        self.LastErrC = StimErrC.ok

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getVideoParams(self, _ID):
        """ Get video object parameters
        (For parameters, see QDS.py)
        """
        try:
            iVdOb = self.VidDict[_ID]
            VdOb = self.VidList[iVdOb]
        except KeyError:
            self.LastErrC = StimErrC.noMatchingID
            raise StimException(self.LastErrC)

        d = dict()
        d["dxFr"] = VdOb[SV_field_dxFr]
        d["dyFr"] = VdOb[SV_field_dyFr]
        d["nFr"] = VdOb[SV_field_nFr]
        d["fps"] = VdOb[SV_field_fps]
        return d

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setObjColor(self, _IDs, _newRGBs, _newAlphas):
        """ Changes the color and the alpha values of one or more objects
        by creating a scene w/o duration
        Parameters:
        _IDs            := list of IDs
        _newRGBs        := list of RGB tuples (bytes)
        _newAlphas      := list of alpha values (byte)
        e.g.
        setObjColor([1,2], [(255,128,0), (0,63,128)], [128,255])
        """
        if (
            not (isinstance(_IDs, list))
            or not (isinstance(_newRGBs, list))
            or not (isinstance(_newRGBs[0], tuple))
            or not (isinstance(_newAlphas, list))
            or (len(_IDs) != len(_newRGBs))
            or (len(_IDs) != len(_newAlphas))
        ):
            self.LastErrC = StimErrC.invalidParamType
            raise StimException(self.LastErrC)

        for ID in _IDs:
            try:
                self.ObjDict[ID]
            except KeyError:
                self.LastErrC = StimErrC.noMatchingID
                raise StimException(self.LastErrC)

        RGBEx = ssp.completeRGBList(_newRGBs)
        newSce = [
            StimSceType.changeObjCol,
            -1,
            self.nSce,
            False,
            _IDs,
            RGBEx,
            _newAlphas,
            len(_IDs) * [SC_disableRGBAByVert],
        ]
        self.SceList.append(newSce)
        self.nSce += 1
        self.LastErrC = StimErrC.ok

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setObjColorAlphaByVertex(self, _IDs, _newRGBAs):
        """ Change the color(s) of the given object(s)
        (For parameters, see QDS.py)
        """
        if (
            not (isinstance(_IDs, list))
            or not (isinstance(_newRGBAs, list))
            or not (isinstance(_newRGBAs[0], list))
            or not (isinstance(_newRGBAs[0][0], tuple))
            or (len(_IDs) != len(_newRGBAs))
        ):
            self.LastErrC = StimErrC.invalidParamType
            raise StimException(self.LastErrC)

        for ID in _IDs:
            try:
                self.ObjDict[ID]
            except KeyError:
                self.LastErrC = StimErrC.noMatchingID
                raise StimException(self.LastErrC)

        RGBAEx = ssp.completeRGBAList(_newRGBAs)
        newSce = [
            StimSceType.changeObjCol,
            -1,
            self.nSce,
            False,
            _IDs,
            RGBAEx,
            len(_IDs) * [0],
            len(_IDs) * [SC_enableRGBAByVert],
        ]
        self.SceList.append(newSce)
        self.nSce += 1
        self.LastErrC = StimErrC.ok

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setColorLUTEntry(self, _index, _rgb):
        """ Change a color LUT entry
        (For parameters, see QDS.py)
        """
        if (
            (_index < 0)
            or (_index > 255)
            or not (isinstance(_rgb, tuple))
            or len(_rgb) not in [3, 6]
        ):
            self.LastErrC = StimErrC.invalidParamType
            raise StimException(self.LastErrC)

    # *********************
    # *********************
    # *********************
    # TODO
    # *********************
    # *********************
    # *********************

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setShaderParams(self, _shID, _shParams):
        """ Set or change the parameters of an existing shader
        (For parameters, see QDS.py)
        """
        if not (isinstance(_shID, int)) or not (isinstance(_shParams, list)):
            self.LastErrC = StimErrC.invalidParamType
            raise StimException(self.LastErrC)

        try:
            iSh = self.ShDict[_shID]
        except KeyError:
            self.LastErrC = StimErrC.noMatchingID
            raise StimException(self.LastErrC)

        shP = _shParams
        shType = self.ShList[iSh][SH_field_shaderType]
        try:
            iShD = self.ShManager.getShaderTypes().index(shType)
            ShD = self.ShManager.ShDesc[iShD]
        except ValueError:
            self.LastErrC = StimErrC.invalidShaderType
            raise StimException(self.LastErrC)

        # Convert RBG values for each shader parameter (uniform) that
        # contains the substring "rgb"
        for i, par in enumerate(ShD[1]):
            if (ShD[2][i] > 1) and ("rgb" in par.lower()):
                shP[i] = ssp.scaleRGBShader(self, shP[i])

        newSce = [StimSceType.changeShParams, -1, self.nSce, False, [_shID], shP]
        self.SceList.append(newSce)
        self.nSce += 1
        self.LastErrC = StimErrC.ok

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setObjShader(self, _IDs, _shIDs):
        """ Link object(s) with existing shader(s)
        (For parameters, see QDS.py)
        """
        if not (isinstance(_IDs, list)) or not (isinstance(_shIDs, list)):
            self.LastErrC = StimErrC.invalidParamType
            raise StimException(self.LastErrC)

        for ID in _IDs:
            try:
                # self.ObjDict[ID]
                if self.ObjList[self.ObjDict[ID]][SO_field_useShader] == 0:
                    self.LastErrC = StimErrC.notShaderObject
                    raise StimException(self.LastErrC)
            except KeyError:
                self.LastErrC = StimErrC.noMatchingID
                raise StimException(self.LastErrC)

        for ID in _shIDs:
            if ID < 0:
                continue
            try:
                self.ShDict[ID]
            except KeyError:
                self.LastErrC = StimErrC.noMatchingID
                raise StimException(self.LastErrC)

        newSce = [StimSceType.changeObjShader, -1, self.nSce, False, _IDs, _shIDs]
        self.SceList.append(newSce)
        self.nSce += 1
        self.LastErrC = StimErrC.ok

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setBkgColor(self, _newRGB):
        """ Changes the background color by creating a scene w/o duration
        Parameters:
        _newRGB         := RGB tuple (bytes)
        e.g.
        setBkgColor((255,128,0))
        """
        if not (isinstance(_newRGB, tuple)):
            self.LastErrC = StimErrC.invalidParamType
            raise StimException(self.LastErrC)

        RGBEx = ssp.completeRGBList([_newRGB])
        newSce = [StimSceType.changeBkgCol, -1, self.nSce, False, RGBEx[0]]
        self.SceList.append(newSce)
        self.nSce += 1
        self.LastErrC = StimErrC.ok

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def awaitTTL(self):
        """..."""
        newSce = [StimSceType.awaitTTL, -1, self.nSce, False]
        self.SceList.append(newSce)
        self.nSce += 1
        self.LastErrC = StimErrC.ok

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getRandom(self, _seed):
        """..."""
        newSce = [StimSceType.getRandom, -1, self.nSce, False, _seed]
        self.SceList.append(newSce)
        self.nSce += 1
        self.LastErrC = StimErrC.ok

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def logUserParameters(self, _dict):
        """ Writes a user-defined set of parameters to the log file
        (For parameters, see QDS.py)
        """
        if not (isinstance(_dict, dict)):
            self.LastErrC = StimErrC.invalidParamType
            raise StimException(self.LastErrC)

        # **************************************
        # **************************************
        # TODO: Check dict for large lists or data structures and if
        #       present, save right here as external stimulus files to
        #       keep the amount of text written into the log file and
        #       the history during the stimulus presentation at a
        #       minimum
        # **************************************
        # **************************************
        newSce = [StimSceType.logUserParams, -1, self.nSce, False, _dict]
        self.SceList.append(newSce)
        self.nSce += 1
        self.LastErrC = StimErrC.ok

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def clearScene(self, _dur_s, _isMarker=False):
        """ Clear the scene (the screen) using the current background color
        and present that scene for the given duration (if _dur_s > 0)
        
        NOTE that all special objects, like moving bars movies etc. that
        have not finished, are continued to be updated
        """
        if _dur_s < 0:
            self.LastErrC = StimErrC.invalidDuration
            raise StimException(self.LastErrC)
        elif _dur_s == 0:
            dur = -1
        else:
            dur = float(_dur_s)

        newSce = [StimSceType.clearSce, dur, self.nSce, _isMarker, self.curBgRGB]
        self.SceList.append(newSce)
        self.nSce += 1
        self.LastErrC = StimErrC.ok

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def loopBegin(self, _nTrials):
        """..."""
        if self.inLoop:
            return -1

        self.inLoop = True
        self.iLoopSce = self.nSce
        newSce = [
            StimSceType.beginLoop,
            -1,
            self.nSce,
            False,
            _nTrials if _nTrials > 0 else -1,
        ]
        self.SceList.append(newSce)
        self.nSce += 1
        self.LastErrC = StimErrC.ok

    def loopEnd(self):
        """..."""
        if not self.inLoop:
            return -1

        newSce = [StimSceType.endLoop, -1, self.nSce, False]
        self.SceList.append(newSce)
        self.nSce += 1
        self.inLoop = False
        self.iLoopSce = -1
        self.LastErrC = StimErrC.ok

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def processLCrCommand(self, _cmd, _p=None):
        """..."""
        if _p is None:
            _p = [0]
        if not self.Conf.useLCr:
            self.LastErrC = StimErrC.ok
            return

        # Check if parameters are valid for the respective lightcrafter
        # commands using a "dummy" LCr object
        # (Note that params[0] is always the lightcrafter device index;
        # necessary for the case that there are more than one devices
        # connected.)
        res = [lcr.ERROR.OK]
        if _cmd == StimLCrCmd.softwareReset:
            res = _LCr.softwareReset()
        elif _cmd == StimLCrCmd.setInputSource:
            res = _LCr.setInputSource(_p[1], _p[2])
        elif _cmd == StimLCrCmd.setDisplayMode:
            res = _LCr.setDisplayMode(_p[1])
        elif _cmd == StimLCrCmd.setTestPattern:
            res = _LCr.setTestPattern(_p[1])
        elif _cmd == StimLCrCmd.setLEDCurrents:
            res = _LCr.setLEDCurrents(_p[1])
        elif _cmd == StimLCrCmd.setLEDEnabled:
            res = _LCr.setLEDEnabled(_p[1], _p[2])

        if res[0] != lcr.ERROR.OK:
            self.LastErrC = StimErrC.DeviceError_LCr
            raise StimException(self.LastErrC)

        newSce = [StimSceType.sendCommandToLCr, -1, self.nSce, False, [_cmd] + _p]
        self.SceList.append(newSce)
        self.nSce += 1
        self.isUseLCr = True
        self.LastErrC = StimErrC.ok

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def renderScene(self, _dur_s, _IDs, _posXY, _magXY, _rot, _isMarker=False):
        """ Render objects and present that scene for the given duration.

        NOTE that all special objects, like moving bars movies etc. that
        have not finished, are continued to be updated
        Parameters:
        _dur_s          := scene duration in s
        _IDs            := list of object IDs to render
        _posXY          := list of x,y tuples as object positions in µm
        _magXY          := list of magnification factors (x,y tuples)
        _rot            := list of rotation angles in degrees
        e.g.
        renderScene(1.0, [1,3], [(0,0), (50,40)], [(1.0,1.0),(0.5,0.5)],
                    [90,180])
        """
        if (
            not (isinstance(_IDs, list))
            or not (isinstance(_posXY, list))
            or not (isinstance(_posXY[0], tuple))
            or not (isinstance(_magXY, list))
            or not (isinstance(_magXY[0], tuple))
            or not (isinstance(_rot, list))
            or (len(_IDs) != len(_posXY))
            or (len(_IDs) != len(_magXY))
            or (len(_IDs) != len(_rot))
        ):
            self.LastErrC = StimErrC.invalidParamType
            raise StimException(self.LastErrC)

        if _dur_s <= 0:
            self.LastErrC = StimErrC.invalidDuration
            raise StimException(self.LastErrC)

        for ID in _IDs:
            try:
                self.ObjDict[ID]
            except KeyError:
                self.LastErrC = StimErrC.noMatchingID
                raise StimException(self.LastErrC)

        newSce = [
            StimSceType.renderSce,
            float(_dur_s),
            self.nSce,
            _isMarker,
            _IDs,
            _posXY,
            _magXY,
            _rot,
        ]
        self.SceList.append(newSce)
        self.nSce += 1
        self.LastErrC = StimErrC.ok

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def startMovie(self, _ID, _posXY, _seq, _magXY, _trans, _rot, _screen=0):
        """ Start playing a movie object
        (For parameters, see QDS.py)
        """
        if (
            not (isinstance(_posXY, tuple))
            or not (isinstance(_magXY, tuple))
            or not (isinstance(_seq, list))
            or not (len(_seq) == 4)
            or (_trans < 0)
            or (_trans > 255)
            or (_screen < 0)
            or (_screen >= glo.QDSpy_maxNumberOfScreens)
        ):
            self.LastErrC = StimErrC.invalidParamType
            raise StimException(self.LastErrC)

        try:
            iMvOb = self.MovDict[_ID]
            # if not(self.MovList[iOb][SO_field_type] == StimObjType.movie):
            # self.LastErrC = StimErrC.notMovieObject
            # raise(StimException(self.LastErrC))
        except KeyError:
            self.LastErrC = StimErrC.noMatchingID
            raise StimException(self.LastErrC)

        tmpMCtr = mov.MovieCtrl(_seq, _ID, _nFr=self.MovList[iMvOb][SM_field_nFr])
        if not (tmpMCtr.check()):
            self.LastErrC = StimErrC.invalidMovieSeq
            raise StimException(self.LastErrC)

        newSce = [
            StimSceType.startMovie,
            -1,
            self.nSce,
            False,
            [_ID],
            _posXY,
            _magXY,
            _rot,
            _seq,
            _trans,
            _screen,
        ]
        self.SceList.append(newSce)
        self.nSce += 1
        self.LastErrC = StimErrC.ok

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def startVideo(self, _ID, _posXY, _magXY, _trans, _rot, _screen=0):
        """ Start playing a video object
        (For parameters, see QDS.py)
        """
        if (
            not (isinstance(_posXY, tuple))
            or not (isinstance(_magXY, tuple))
            or (_trans < 0)
            or (_trans > 255)
            or _screen not in [0, 1]
        ):
            self.LastErrC = StimErrC.invalidParamType
            raise StimException(self.LastErrC)

        try:
            _ = self.VidDict[_ID]
        except KeyError:
            self.LastErrC = StimErrC.noMatchingID
            raise StimException(self.LastErrC)

        newSce = [
            StimSceType.startVideo,
            -1,
            self.nSce,
            False,
            [_ID],
            _posXY,
            _magXY,
            _rot,
            _trans,
            _screen,
        ]
        self.SceList.append(newSce)
        self.nSce += 1
        self.LastErrC = StimErrC.ok

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def compile(self, _Stage):
        """ Compile the current stimulus for the given stage settings
        Parameters:
        _Pr  := an instance of the Present class
        """
        if (
            (len(self.ObjList) == 0)
            and (len(self.MovList) == 0)
            and (len(self.VidList) == 0)
        ) or (len(self.SceList) == 0):
            self.LastErrC = StimErrC.nothingToCompile
            raise StimException(self.LastErrC)

        # Clear compiled scene data
        # First, lists corresponding to SceList, then lists with entries
        # only for scenes with objects (indexed by cScOList)
        self.cScMarkList = []  # True=show marker
        self.cScDurList = []  # number of frames or 0
        self.cScOList = []  # index to cODr_xxx or -1

        # Vertex information
        # Each set contains one to multiple objects
        # {} indicate numpy arrays
        # All data are describing index triangle vertex with RGBA
        #
        # cODr_tr_iVert      := [[[mode, ObjID, {vertexIndexSet}], ...], ...]
        # cODr_tr_vertCoord  := [[[mode, ObjID, {vertices      }], ...], ...]
        # cODr_tr_vertRGBA   := [[[mode, ObjID, {vertexRGBASet }], ...], ...]
        # cODr_tr_hash       := [['', ObjHash, ObjHash, ...], ...]
        # with
        #   mode             := int,   1=use included data, 0=use previous data
        #   ObjID            := int,   QDS ID of object or -1 for collected not
        #                              shader-enabled vertex data
        #   ObjHash          := string, hash string (=unique object ID)
        #   vertexIndexSet   := int,   {v1,v2, ...}
        #   vertexSet        := float, {x1,y1,x2,y2, ...}
        #   vertexRGBSet     := byte,  {r1,g1,b1,r2,g2,b2, ...}
        #   vertexRGBASet    := byte,  {r1,g1,b1,a1,r2,g2,b2,a2, ...}
        # The first list after "n" contains all vertex/index/RGBA data of general
        # not shader-enabled objects. The following "n-1" list contain each one
        # shader-enabled object.
        #
        self.cODr_tr_iVert = []  # triangle vertex indices
        self.cODr_tr_vertCoord = []  # list of coordinate pair lists
        self.cODr_tr_vertRGBA = []  # list of color/alpha lists
        self.cODr_tr_vertRGBA2 = []  # list of color/alpha lists (screen2)
        self.cODr_tr_hash = []  # list of object hashes (=unique IDs)
        self.ncODr = 0
        # ...
        self.cFreq_Hz = _Stage.scrReqFreq_Hz
        self.maxShObjPerRender = 0
        self.lenStim_s = 0.0

        isInLoop = False

        # Analyze scene list
        for sc in self.SceList:
            # Progress message to user
            percent = sc[SC_field_index] * 100.0 / len(self.SceList)
            ssp.Log.write(
                "ok",
                "Scene {0} of {1}; {2:.0f}% compiled...".format(
                    sc[SC_field_index], len(self.SceList), percent
                ),
                True,
            )

            # If scene has a duration, convert it into number of refreshes
            (dur, isIntNumFrames) = _Stage.durToFrames(sc[SC_field_duration_s])
            self.cScDurList.append(dur)

            if not (isIntNumFrames):
                ssp.Log.write(
                    "WARNING",
                    "Scene #{0} duration unequals integer number" " of frames".format(
                        sc[SC_field_index]
                    ),
                )

            # Track the duration
            if sc[SC_field_type] == StimSceType.beginLoop:
                lenInLoop_s = 0
                nTrialsLoop = sc[SC_field_nLoopTrials]
                isInLoop = True

            if sc[SC_field_type] == StimSceType.endLoop:
                isInLoop = False
                self.lenStim_s += lenInLoop_s * nTrialsLoop

            if dur > 0:
                if isInLoop:
                    lenInLoop_s += sc[SC_field_duration_s]
                else:
                    self.lenStim_s += sc[SC_field_duration_s]

            # If scene request marker to be shown, set flag
            self.cScMarkList.append(sc[SC_field_marker])

            # Handle scene-type specifics ...
            icODrEntry = -1
            ObjIDs = []
            ObjNewMask = []
            ObjHash = []
            ObjPosXY = []
            ObjRot = []

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if sc[SC_field_type] == StimSceType.changeObjCol:
                # Change the foreground color of objects
                for iObj, ID in enumerate(sc[SC_field_IDs]):
                    iOb = self.ObjDict[ID]
                    ob = self.ObjList[iOb]
                    self.ObjList[iOb][SO_field_fgRGB] = sc[SC_field_RGBs][iObj]
                    self.ObjList[iOb][SO_field_alpha] = sc[SC_field_Alphas][iObj]
                    self.ObjList[iOb][SO_field_doRGBAByVert] = sc[
                        SC_field_doRGBAByVert
                    ][iObj]

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            elif sc[SC_field_type] == StimSceType.changeBkgCol:
                pass
            elif sc[SC_field_type] == StimSceType.clearSce:
                pass
            elif sc[SC_field_type] == StimSceType.startMovie:
                pass
            elif sc[SC_field_type] == StimSceType.startVideo:
                pass
            elif sc[SC_field_type] == StimSceType.sendCommandToLCr:
                pass

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            elif sc[SC_field_type] == StimSceType.renderSce:
                # Generate drawing instructions for all objects
                #
                # Lists containing vertex/index/RGBA data; the first list element
                # contains data for the not shader-enabled objects, all following
                # list elements are for shader-enabled objects
                iVertTr = [[]]
                vertTr = [[]]
                RGBATr = [[]]
                RGBATr2 = [[]]
                ObjIDs = [-1]
                ObjNewMask = [SC_ObjNewNone]
                ObjHash = [""]
                ObjPosXY = [(0, 0)]
                ObjRot = [0]
                nObjs = 1

                for iObj, ID in enumerate(sc[SC_field_IDs]):
                    iOb = self.ObjDict[ID]
                    ob = self.ObjList[iOb]
                    iNextVTr = 0
                    if ob[SO_field_useShader] == 0:
                        iNextVTr = len(vertTr[0]) / 2

                    if ob[SO_field_type] == StimObjType.box:
                        # Is box object ...
                        tmp = drw.box2vert(ob, iObj, sc, _Stage, self, iNextVTr)

                    elif ob[SO_field_type] == StimObjType.ellipse:
                        # Is ellipse object ...
                        tmp = drw.ell2vert(ob, iObj, sc, _Stage, self, iNextVTr)

                    elif ob[SO_field_type] == StimObjType.sector:
                        # Is sector object ...
                        tmp = drw.sct2vert(ob, iObj, sc, _Stage, self, iNextVTr)

                    else:
                        tmp = [[], [], [], [], "", (0, 0), 0]

                    newVert = tmp[0]
                    newiVTr = tmp[1]
                    newRGBA = tmp[2]
                    newRGBA2 = tmp[3]
                    if len(newRGBA) != len(newRGBA2):
                        print("LENGTH MISMATCH")

                    hStr = tmp[4]
                    posxy = tmp[5]
                    rot = tmp[6]

                    # Add object vertex etc. data to respective lists (see above)
                    if ob[SO_field_useShader]:
                        iVertTr.append(newiVTr)
                        vertTr.append(newVert)
                        RGBATr.append(newRGBA)
                        RGBATr2.append(newRGBA2)
                        ObjIDs.append(ID)
                        ObjNewMask.append(SC_ObjNewAll)
                        ObjHash.append(hStr)
                        ObjPosXY.append(posxy)
                        ObjRot.append(rot)
                        nObjs += 1
                    else:
                        iVertTr[0] += newiVTr
                        vertTr[0] += newVert
                        RGBATr[0] += newRGBA
                        RGBATr2[0] += newRGBA2
                        ObjNewMask[0] = SC_ObjNewAll

                # Keep track of the maximal number of objects per render call
                if (nObjs - 1) > self.maxShObjPerRender:
                    self.maxShObjPerRender = nObjs - 1

                # Add an entry with the draw instructions for the objects of the
                # current scene to the cODr_xxx lists (see above for details)
                _iVertTr = []
                _vertTr = []
                _RGBATr = []
                _RGBATr2 = []
                for iObj in range(nObjs):
                    np_iVertTr = np.array(iVertTr[iObj], dtype=int)
                    _iVertTr.append([SC_vertDataChanged, ObjIDs[iObj], np_iVertTr])
                    np_vertTr = np.array(vertTr[iObj], dtype=int)
                    _vertTr.append([SC_vertDataChanged, ObjIDs[iObj], np_vertTr])
                    np_RGBATr = np.array(RGBATr[iObj], dtype=np.uint8)
                    _RGBATr.append([SC_vertDataChanged, ObjIDs[iObj], np_RGBATr])
                    np_RGBATr2 = np.array(RGBATr2[iObj], dtype=np.uint8)
                    _RGBATr2.append([SC_vertDataChanged, ObjIDs[iObj], np_RGBATr2])

                    # Check if one or more aspects of the vertex data have remained
                    # the same compared to the previous set; if so don't save it
                    if (len(np_iVertTr) == 0) or (self.ncODr == 0):
                        # Is first set of vertex data or vertex list is empty, there
                        # is nothing to do ...
                        continue

                    # We only check for the general, not shader-enabeled object and
                    # assume that the remaining objects can be recreated (VBOs) for
                    # every change (checking if something stayed the same there is
                    # rather complex ...)
                    if iObj > 0:
                        continue

                    # First go back to the last data set that contained data ...
                    iLastODr = self.ncODr - 1
                    while self.cODr_tr_vertCoord[iLastODr][iObj][0] == SC_vertDataSame:
                        iLastODr -= 1

                    if len(np_vertTr) == len(self.cODr_tr_vertCoord[iLastODr][iObj][2]):
                        # The data arrays have the same length ...
                        if (
                            np_vertTr == self.cODr_tr_vertCoord[iLastODr][iObj][2]
                        ).all():
                            # Vertex data is the same (and also vertex indices should be
                            # the same), therefore skip saving this data and refer
                            # instead to the previous object drawing data
                            _vertTr[iObj] = [SC_vertDataSame, -1, []]
                            _iVertTr[iObj] = [SC_vertDataSame, -1, []]
                            ObjNewMask[iObj] = ObjNewMask[iObj] & ~SC_ObjNewVer
                            ObjNewMask[iObj] = ObjNewMask[iObj] & ~SC_ObjNewiVer

                        # Check also color data ...
                        iLastODr = self.ncODr - 1
                        while (
                            self.cODr_tr_vertRGBA[iLastODr][iObj][0] == SC_vertDataSame
                        ) and (
                            self.cODr_tr_vertRGBA2[iLastODr][iObj][0] == SC_vertDataSame
                        ):
                            iLastODr -= 1

                        if (
                            np_RGBATr == self.cODr_tr_vertRGBA[iLastODr][iObj][2]
                        ).all() and (
                            np_RGBATr2 == self.cODr_tr_vertRGBA2[iLastODr][iObj][2]
                        ).all():
                            _RGBATr[iObj] = [SC_vertDataSame, -1, []]
                            _RGBATr2[iObj] = [SC_vertDataSame, -1, []]
                            ObjNewMask[iObj] = ObjNewMask[iObj] & ~SC_ObjNewRGBA

                self.cODr_tr_vertCoord.append(_vertTr)
                self.cODr_tr_iVert.append(_iVertTr)
                self.cODr_tr_vertRGBA.append(_RGBATr)
                self.cODr_tr_vertRGBA2.append(_RGBATr2)
                self.cODr_tr_hash.append(ObjHash)
                icODrEntry = self.ncODr
                self.ncODr += 1

            # Append entries to the compiled scene lists
            # (index to entry in object draw lists, or -1)
            self.cScOList.append([icODrEntry, ObjNewMask, ObjIDs, ObjPosXY, ObjRot])

        # Finished compiling
        ssp.Log.write(
            "ok",
            "Stimulus '{0}' compiled for {1} Hz refresh".format(
                self.nameStr, self.cFreq_Hz
            ),
        )
        self.isComp = True
        self.LastErrC = StimErrC.ok

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def save(self, sFileName):
        """ Save the compiled stimulus
        """
        if not (self.isComp):
            ssp.Log.write("WARNING", "No stimulus defined or not yet compiled")
            self.LastErrC = StimErrC.noStimOrNotCompiled
            return

        ssp.Log.write(" ", "Saving stimulus...", True)
        with open(sFileName + glo.QDSpy_cPickleFileExt, "wb") as stimFile:
            stimPick = pickle.Pickler(stimFile, glo.QDSpy_cPickleProtocol)

            stimPick.dump(glo.QDSpy_fileVersionID)
            stimPick.dump(self.nameStr)
            stimPick.dump(self.descrStr)
            stimPick.dump(self.cFreq_Hz)
            stimPick.dump(self.isUseLCr)
            stimPick.dump(self.lenStim_s)
            stimPick.dump(self.maxShObjPerRender)
            stimPick.dump(self.ObjList)
            stimPick.dump(self.ObjDict)
            stimPick.dump(self.ShList)
            stimPick.dump(self.ShDict)
            stimPick.dump(self.MovList)
            stimPick.dump(self.MovDict)
            stimPick.dump(self.VidList)
            stimPick.dump(self.VidDict)
            stimPick.dump(self.SceList)
            stimPick.dump(self.curBgRGB)
            stimPick.dump(self.cScMarkList)
            stimPick.dump(self.cScDurList)
            stimPick.dump(self.cScOList)
            stimPick.dump(self.ncODr)
            stimPick.dump(self.cODr_tr_iVert)
            stimPick.dump(self.cODr_tr_vertCoord)
            stimPick.dump(self.cODr_tr_vertRGBA)
            stimPick.dump(self.cODr_tr_vertRGBA2)

        ssp.Log.write(
            "ok",
            "Stimulus '{0}' saved to '{1}'".format(
                self.nameStr, sFileName + glo.QDSpy_cPickleFileExt
            ),
        )
        self.LastErrC = StimErrC.ok

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def load(self, sFileName, _onlyInfo=False):
        """ Load the compiled stimulus
        """
        self.clear()
        if not (_onlyInfo):
            ssp.Log.write(" ", "Loading compiled stimulus...", True)

        try:
            with open(sFileName + glo.QDSpy_cPickleFileExt, "rb") as stimFile:
                self.fileName = sFileName.replace("\\\\", "\\")
                stimPick = pickle.Unpickler(stimFile)
                ID = stimPick.load()

                if ID != glo.QDSpy_fileVersionID:
                    self.LastErrC = StimErrC.wrongStimFileFormat
                    ssp.Log.write("ERROR", self.getLastErrStr())
                    raise StimException(self.LastErrC)

                self.nameStr = stimPick.load()
                self.descrStr = stimPick.load()
                self.cFreq_Hz = stimPick.load()
                self.isUseLCr = stimPick.load()
                self.lenStim_s = stimPick.load()
                if not (_onlyInfo):
                    self.maxShObjPerRender = stimPick.load()
                    self.ObjList = stimPick.load()
                    self.ObjDict = stimPick.load()
                    self.ShList = stimPick.load()
                    self.ShDict = stimPick.load()
                    self.MovList = stimPick.load()
                    self.MovDict = stimPick.load()
                    self.VidList = stimPick.load()
                    self.VidDict = stimPick.load()
                    self.SceList = stimPick.load()
                    self.curBgRGB = stimPick.load()
                    self.cScMarkList = stimPick.load()
                    self.cScDurList = stimPick.load()
                    self.cScOList = stimPick.load()
                    self.ncODr = stimPick.load()
                    self.cODr_tr_iVert = stimPick.load()
                    self.cODr_tr_vertCoord = stimPick.load()
                    self.cODr_tr_vertRGBA = stimPick.load()
                    self.cODr_tr_vertRGBA2 = stimPick.load()

        except IOError:
            self.LastErrC = StimErrC.noCompiledStim
            ssp.Log.write("ERROR", self.getLastErrStr())
            raise StimException(self.LastErrC)

        # Get hash for pickle file
        if not (_onlyInfo):
            self.md5Str = ssp.getHashStrForFile(sFileName + glo.QDSpy_cPickleFileExt)

        # Log some information
        if not (_onlyInfo):
            ssp.Log.write(
                "ok",
                "Stimulus '{0}' loaded".format(sFileName + glo.QDSpy_cPickleFileExt),
            )
            ssp.Log.write(" ", "Name       : {0}".format(self.nameStr))
            ssp.Log.write(" ", "Description: {0}".format(self.descrStr))
            ssp.Log.write(" ", "Frequency  : {0} Hz".format(self.cFreq_Hz))

        self.isComp = True
        self.LastErrC = StimErrC.ok

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    """ Is currently done at the vertex level
    def adjust(self, _Stage):
      # Adjust compiled stimulus to current stage parameters
      #
      ssp.Log.write(" ", "Adjusting stimulus to stage parameters...", True)

      for iVC in range(len(self.cODr_tr_vertCoord)):
        if self.cODr_tr_vertCoord[iVC][0] > 0:
          self.cODr_tr_vertCoord[iVC][1][0::2] /= float(_Stage.scalX_umPerPix)
          self.cODr_tr_vertCoord[iVC][1][1::2] /= float(_Stage.scalY_umPerPix)
          self.cODr_tr_vertCoord[iVC][1][0::2] += _Stage.centX_pix
          self.cODr_tr_vertCoord[iVC][1][1::2] += _Stage.centY_pix
          # *** TODO ***
          # Convert back to integer?
          # ************

      ssp.Log.write("ok", "Stimulus '{0}' adjusted to stage parameters"
                .format(self.nameStr))
      self.LastErrC = StimErrC.ok
    """


# ---------------------------------------------------------------------
