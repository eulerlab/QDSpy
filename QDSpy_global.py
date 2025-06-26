#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QDSpy module - global definitions

Copyright (c) 2013-2025 Thomas Euler
All rights reserved.

2024-06-15 - Fix for breaking change in `configparser`; now using
             `ConfigParser` instead of `RawConfigParser`
2025-01-28 - Sensor data via a serial port to log           
2025-04-08 - Distortion shader parameters added 
"""
# ---------------------------------------------------------------------
__author__ 	= "code@eulerlab.de"

from QDSpy_file_support import getQDSpyPath, getCompletePath

# fmt: off
# ---------------------------------------------------------------------
QDSpy_versionStr            = "QDSpy v0.9.6"
QDSpy_copyrightStr          = "(c) 2013-25 Thomas Euler"
QDSpy_appID                 = u"QDSpy3.v0.9.6.thomas_euler.eulerlab.de"
QDSpy_fullScrWinName        = "QDSPY_STIMULUS"
QDSpy_path                  = getQDSpyPath()

# Log messages etc.
QDSpy_isDebug               = True
QDSpy_isGUIQuitWithDialog   = False
QDSpy_workerMsgsToStdOut    = True
QDSpy_noStimArg             = False
QDSpy_loop_sleep_s          = 0.01

# Sounds
QDSpy_isUseSound            = False
QDSpy_pathSounds            = getCompletePath("Sounds")
QDSpy_soundStimStart        = "stim_start.mp3"
QDSpy_soundStimEnd          = "stim_end.mp3"
QDSpy_soundError            = "error.mp3" 
QDSpy_soundOk               = "ok.mp3" 
QDSpy_volume                = 0.1

# GUI settings
QDSpy_dpiThresholdForHD     = 110
QDSpy_useGUIScalingForHD    = False  # not needed in PyQt6
QDSpy_fontPntSizeHistoryHD  = 9
QDSpy_fontPntSizeHistory    = 8

# Stimulus window defaults
QDSpy_winWidth              = 640
QDSpy_winHeight             = 480
QDSpy_screenIndex           = 1
QDSpy_disableFullScrCmd     = True
QDSpy_maxNumberOfScreens    = 3

# Renderer
QDSpy_multiSamplingLevel    = 0
QDSpy_graphicsAPI           = 0      # 0=default, 1=pygletOnly
QDSpy_use3DTextures         = 0
QDSpy_recordStim            = 0      # 0=normal presentation
QDSpy_rec_f_downsample_x    = 10
QDSpy_rec_f_downsample_t    = 100
QDSpy_rec_setup_id          = -1     # -1=n/a

# Mirror stimulus in control window (beta)
QDSpy_useCtrlWin            = False
QDSpy_ctrlWinScale          = 0.2

# Timing related parameters (tuning)
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
QDSpy_guiTimeOut            = 5.0
QDSpy_saveLogInTheEnd       = False

# Compiled stimulus file settings
QDSpy_cPickleProtocol       = 3
QDSpy_cPickleFileExt        = ".pickle"
QDSpy_fileVersionID         = 8
QDSpy_stimFileExt           = ".py"
QDSpy_pathStimuli           = getCompletePath("Stimuli")
QDSpy_autorunStimFileName   = "__autorun"
QDSpy_autorunDefFileName    = "__autorun_default_DO_NOT_DELETE"

# Movie stimulus-related settings
QDSpy_movDescFileExt        = ".txt"
QDSpy_movDescSect           = "QDSMovie2Description"
QDSpy_movFrWidth            = "FrWidth"
QDSpy_movFrHeight           = "FrHeight"
QDSpy_movFrCount            = "FrCount"
QDSpy_movComment            = "Comment"
QDSpy_movIsFirstFrBottLeft  = "isFirstFrBottomLeft"
QDSpy_movAllowedMovieExts   = [".png", ".jpg"]

# Video stimulus-related settings
QDSpy_vidAllowedVideoExts   = [".avi"]
QDSpy_vid_useIter           = True    # Experimental
# If False, tries to load videos completely to avoid timing
# issue with re-iterating the video object ...

# Paths 
QDSpy_pathApplication       = getQDSpyPath()
QDSpy_iniFileName           = "QDSpy.ini"

QDSpy_pathLogFiles          = getCompletePath("Logs")
QDSpy_logFileExtension      = ".log"
QDSpy_doLogTimeStamps       = True

QDSpy_pathShader            = getCompletePath("Shader")
QDSpy_shaderFileExt         = ".cl"
QDSpy_shaderFileCmdTok      = "#qds"
QDSpy_loadShadersOnce       = True

QDSpy_KEY_KillPresent       = [ord(b'Q'), ord(b'q')]

# Marker/trigger timing
# (For more details, see http://qdspy.eulerlab.de/inifile.html#timing)
QDSpy_useUL_DIO             = False
QDSpy_UL_boardType          = "PCIDIO24" # "Arduino", "USB1024LS", "RaspberryPi"
QDSpy_UL_boardNum           = 0
QDSpy_UL_deviceNum          = 6
QDSpy_UL_portOut            = "A"
QDSpy_UL_portIn             = "CLO"
QDSpy_UL_portOut_User       = "B"
QDSpy_UL_pinMarkerOut       = 2
QDSpy_UL_pinTriggerIn       = 0
QDSpy_UL_pinUserOut1        = "3, USER1, 0"
QDSpy_UL_pinUserOut2        = "4, USER2, 0"
QDSpy_Arduino_baud          = 230400

# Pico-view - Logging data received via a serial port
QDSpy_usePV                 = False
QDSpy_PV_serialPort         = "COM9"
QDSpy_PV_baud               = 230400
QDSpy_PV_rate_s             = 1.0
QDSpy_PV_startCh            = ">"

# Distortion shader
QDSpy_useDistort            = False
QDSpy_distort_vertex        = "distort_vertex_shader.glsl"
QDSpy_distort_fragment      = "distort_barrel.frag"
'''
QDSpy_distort_vertex        = "distort_vertex_shader.glsl"
QDSpy_distort_fragment      = "distort_barrel_rp5.frag"
'''

# Marker in screen
QDSpy_markerRGBA            = "255,127,127,255"
QDSpy_antiMarkerRGBA        = "0,0,0,255"
QDSpy_markerScrWidthFract   = 16
QDSpy_markerShowOnScr       = True

# Overlay mode
QDSpy_useScrOverlayMode     = False
QDSpy_screenIndexGUI        = 0
QDSpy_winWidth1_2           = 1280
QDSpy_winHeight1_2          = 480

QDSpy_xOffsetScr1_pix       = 0
QDSpy_yOffsetScr1_pix       = 0
QDSpy_xOffsetScr2Center_pix = 0
QDSpy_yOffsetScr2Center_pix = 0

QDSpy_vFlipScr1             = False
QDSpy_hFlipScr1             = False
QDSpy_vFlipScr2             = False
QDSpy_hFlipScr2             = False

# Lightcrafter settings
QDSpy_MaxLightcrafterDev    = 2
QDSpy_use_Lightcrafter      = True
QDSpy_LCrDevTypeName        = "DLPLCR4500" # "DLPLCR230NP"
QDSpy_LEDNames_default      = "red, green, blue"
QDSpy_LEDPeakWLs_default    = "650, 510, 450"
QDSpy_LEDDevIndex_default   = "0, 0, 0"
QDSpy_LEDIndex_default      = "0, 1, 2"
QDSpy_LEDCurrents_default   = "10, 10, 10"
QDSpy_LEDCurrents_max       = "100, 100, 100"
QDSpy_LEDQtColors_default   = "darkRed, darkGreen, darkBlue"
QDSpy_LCr_LogLevel          = 0 #0=only errors, 1=important 2=all

# Gamma correction (deprecated)
QDSpy_allowGammaLUT_default = False
QDSpy_LUTFileExt            = ".txt"
QDSpy_userGammaLUTFileName  = "defaultGammaLUT"

# Camera (beta)
QDSpy_allowCam              = False
QDSpy_camWinGeometry        = "20,30,300,200"

# Centre probing tool
QDSpy_probing_center        = 1
# fmt: on

# ---------------------------------------------------------------------
