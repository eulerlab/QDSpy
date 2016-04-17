#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
#  QDSpy_global.py
#
#  Global definitions
#
#  Copyright (c) 2013-2016 Thomas Euler
#  All rights reserved.
#
# ---------------------------------------------------------------------
__author__ 	= "code@eulerlab.de"

import pyglet 

# ---------------------------------------------------------------------
QDSpy_versionStr            = "QDSpy v0.6 beta"
QDSpy_copyrightStr          = "(c) 2013-16 Thomas Euler"
QDSpy_appID                 = u"QDSpy3.v05beta.thomas_euler.eulerlab.de"
QDSpy_fullScrWinName        = "x" #QDSPY_STIMULUS"

QDSpy_isDebug               = True
QDSpy_isGUIQuitWithDialog   = False
QDSpy_workerMsgsToStdOut    = True
QDSpy_noStimArg             = False

QDSpy_winWidth              = 640
QDSpy_winHeight             = 480
QDSpy_screenIndex           = 1
QDSpy_disableFullScrCmd     = True

QDSpy_multiSamplingLevel    = 0
QDSpy_doOpenGLErrorChecking = False
QDSpy_graphicsAPI           = 0      # 0=default, 1=pygletOnly
QDSpy_use3DTextures         = 0
QDSpy_recordStim            = 0      # 0=normal presentation

QDSpy_showFPS               = False
QDSpy_trackTiming           = True
QDSpy_frRateStatsBufferLen  = 18000  # 0=continous, >0=circular buffer 
QDSpy_warnDroppedFrames     = True
QDSpy_showStimInfo          = False
QDSpy_incProcessPrior       = True
QDSpy_tryForcingFSync       = True
QDSpy_disableGarbageCollect = False
QDSpy_maxFrameDurDiff_s     = 0.0001 # used when compiling
QDSpy_FrDurThreshold_ms     = 5.0    # to detect dropped frames
QDSpy_refresh_Hz            = 60.0

QDSpy_cPickleProtocol       = 3
QDSpy_cPickleFileExt        = ".pickle"
QDSpy_fileVersionID         = 6
QDSpy_stimFileExt           = ".py"
QDSpy_pathStimuli           = ".\\Stimuli\\"
QDSpy_autorunStimFileName   = "__autorun"
QDSpy_autorunDefFileName    = "__autorun_default"

QDSpy_movDescFileExt        = ".txt"
QDSpy_movDescSect           = "QDSMovie2Description"
QDSpy_movFrWidth            = "FrWidth"
QDSpy_movFrHeight           = "FrHeight"
QDSpy_movFrCount            = "FrCount"
QDSpy_movComment            = "Comment"
QDSpy_movIsFirstFrBottLeft  = "isFirstFrBottomLeft"
QDSpy_movAllowedMovieExts   = [".png", ".jpg"]

QDSpy_vidAllowedVideoExts   = [".avi"]

QDSpy_pathApplication       = ".\\"
QDSpy_iniFileName           = "QDSpy.ini"

QDSpy_pathLogFiles          = ".\\Logs\\"
QDSpy_logFileExtension      = ".log"
QDSpy_doLogTimeStamps       = True

QDSpy_pathShader            = ".\\Shader\\"
QDSpy_shaderFileExt         = ".cl"
QDSpy_shaderFileCmdTok      = "#qds"
QDSpy_loadShadersOnce       = True

QDSpy_KEY_KillPresent       = b'q'
QDSpy_KEY_KillPresentPyglet = pyglet.window.key.Q

QDSpy_useUL_DIO             = True
QDSpy_UL_boardNum           = 0
QDSpy_UL_deviceNum          = 6
QDSpy_UL_portOut            = "A"
QDSpy_UL_portIn             = "B"
QDSpy_UL_pinMarkerOut       = 2  

QDSpy_markerRGBA            = "255,127,127,255"
QDSpy_markerScrWidthFract   = 16
QDSpy_markerShowOnScr       = True

QDSpy_use_Lightcrafter      = False
QDSpy_LEDNames_default      = "red, green, blue"
QDSpy_LEDPeakWLs_default    = "650, 510, 450"
QDSpy_LEDQtColors_default   = "darkRed, darkGreen, darkBlue"

QDSpy_allowGammaLUT_default = False
QDSpy_LUTFileExt            = ".txt"
QDSpy_userGammaLUTFileName  = "defaultGammaLUT"



# ---------------------------------------------------------------------





