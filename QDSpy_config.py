#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QDSpy module - to manage the configuration file

The 'Config' class manages the external configuration file 'QDSpy.ini'
using the configparser library. Use 'getParsedArg()' to parse arguments
for the command line version of QDSpy

Copyright (c) 2013-2024 Thomas Euler
All rights reserved.

2022-08-03 - Adapt to LINUX
2022-08-06 - Some reformatting
2024-06-12 - Reformatted (using Ruff)
           - Fix for breaking change in `configparser`; now using 
             `ConfigParser` instead of `RawConfigParser`
           - Small fixes for PEP violations  
2024-08-10 - LCr type added           
"""
# ---------------------------------------------------------------------
__author__ = "code@eulerlab.de"

import sys
import os
import platform
import argparse
import configparser
import QDSpy_stage as stg
import QDSpy_gamma as gma
import Libraries.log_helper as _log
import QDSpy_global as glo

PLATFORM_WINDOWS = platform.system() == "Windows"

# ---------------------------------------------------------------------
# Configuration file class
# ---------------------------------------------------------------------
class Config:
    def __init__(self):
        # Initialization
        #
        self.isLoaded = False
        self.conf = configparser.ConfigParser()
        # self.conf = configparser.RawConfigParser()

        # Get some information on the platform
        #
        self.isWindows = PLATFORM_WINDOWS
        self.pyVersion = sys.version_info[0] + sys.version_info[1] / 10
        self.iniPath = glo.QDSpy_iniFileName

        # Set configuration default values
        #
        self.incPP = glo.QDSpy_incProcessPrior
        self.fSync = glo.QDSpy_tryForcingFSync
        self.useDIO = glo.QDSpy_useUL_DIO
        self.DIObrdType = glo.QDSpy_UL_boardType
        self.DIObrd = glo.QDSpy_UL_boardNum
        self.DIOdev = glo.QDSpy_UL_deviceNum
        self.DIOportOut = glo.QDSpy_UL_portOut
        self.DIOportIn = glo.QDSpy_UL_portIn
        self.DIOportOut_User = glo.QDSpy_UL_portOut_User
        self.DIOpinMarker = glo.QDSpy_UL_pinMarkerOut
        self.DIOpinUserOut1 = glo.QDSpy_UL_pinUserOut1
        self.DIOpinUserOut2 = glo.QDSpy_UL_pinUserOut2
        self.disFScr = glo.QDSpy_disableFullScrCmd
        self.pathShader = glo.QDSpy_pathShader
        self.pathStim = glo.QDSpy_pathStimuli
        self.pathApp = glo.QDSpy_pathApplication
        self.isTrackTime = glo.QDSpy_trackTiming
        self.isWarnFrDrop = glo.QDSpy_warnDroppedFrames
        self.maxDtTr_ms = glo.QDSpy_FrDurThreshold_ms
        self.disGC = glo.QDSpy_disableGarbageCollect
        self.useLCr = glo.QDSpy_use_Lightcrafter
        self.LCrDevTypeName = glo.QDSpy_LCrDevTypeName
        self.LEDNames = glo.QDSpy_LEDNames_default
        self.LEDPeakWLs = glo.QDSpy_LEDPeakWLs_default
        self.LEDDevIndices = glo.QDSpy_LEDDevIndex_default
        self.LEDIndices = glo.QDSpy_LEDIndex_default
        self.LEDDefCurr = glo.QDSpy_LEDCurrents_default
        self.LEDMaxCurr = glo.QDSpy_LEDCurrents_max
        self.LEDQtColors = glo.QDSpy_LEDQtColors_default
        self.allowGammaLUT = glo.QDSpy_allowGammaLUT_default
        self.userLUTFName = glo.QDSpy_userGammaLUTFileName
        self.pathLogs = glo.QDSpy_pathLogFiles
        self.use3DTextures = glo.QDSpy_use3DTextures
        self.recordStim = glo.QDSpy_recordStim
        self.markShowOnScr = glo.QDSpy_markerShowOnScr
        self.antiMarkRGBA = glo.QDSpy_antiMarkerRGBA
        self.markRGBA = glo.QDSpy_markerRGBA
        self.markScrWidthFract = glo.QDSpy_markerScrWidthFract
        self.useCtrlWin = glo.QDSpy_useCtrlWin
        self.ctrlWinScale = glo.QDSpy_ctrlWinScale
        self.camWinGeom = glo.QDSpy_camWinGeometry
        self.allowCam = glo.QDSpy_allowCam
        self.guiTimeOut = glo.QDSpy_guiTimeOut

        if os.path.isfile(self.iniPath):
            # Config file exists
            self.conf.read(self.iniPath)

            self.incPP = self.getParam(
                "Timing", "bool_incr_process_prior", glo.QDSpy_incProcessPrior
            )
            self.fSync = self.getParam(
                "Timing", "bool_try_forcing_fsync", glo.QDSpy_tryForcingFSync
            )
            self.useDIO = self.getParam(
                "Timing", "bool_use_digitalIO", glo.QDSpy_useUL_DIO
            )
            self.DIObrdType = self.getParam(
                "Timing", "str_digitalio_board_type", glo.QDSpy_UL_boardType
            )
            self.DIObrd = self.getParam(
                "Timing", "int_digitalIO_board_num", glo.QDSpy_UL_boardNum
            )
            self.DIOdev = self.getParam(
                "Timing", "int_digitalIO_device_num", glo.QDSpy_UL_deviceNum
            )
            self.DIOportOut = self.getParam(
                "Timing", "str_digitalio_port_out", glo.QDSpy_UL_portOut
            )
            self.DIOportIn = self.getParam(
                "Timing", "str_digitalio_port_in", glo.QDSpy_UL_portIn
            )
            self.DIOportOut_User = self.getParam(
                "Timing", "str_digitalio_port_user_out", glo.QDSpy_UL_portOut_User
            )
            self.DIOpinMarker = self.getParam(
                "Timing", "int_digitalio_pin_markerOut", glo.QDSpy_UL_pinMarkerOut
            )
            self.DIOpinTrigIn = self.getParam(
                "Timing", "int_digitalio_pin_triggerin", glo.QDSpy_UL_pinTriggerIn
            )
            temp = self.getParam(
                "Timing", "str_digitalio_pin_userout1", glo.QDSpy_UL_pinUserOut1
            )
            self.DIOpinUserOut1 = temp.split(",")
            temp = self.getParam(
                "Timing", "str_digitalio_pin_userout2", glo.QDSpy_UL_pinUserOut2
            )
            self.DIOpinUserOut2 = temp.split(",")
            self.isTrackTime = self.getParam(
                "Timing", "bool_track_timing", glo.QDSpy_trackTiming
            )
            self.isWarnFrDrop = self.getParam(
                "Timing", "bool_warn_when_frames_dropped", glo.QDSpy_warnDroppedFrames
            )
            self.maxDtTr_ms = self.getParam(
                "Timing", "float_frame_dur_threshold_ms", glo.QDSpy_FrDurThreshold_ms
            )
            self.disGC = self.getParam(
                "Timing",
                "bool_disable_garbage_collector",
                glo.QDSpy_disableGarbageCollect,
            )
            self.guiTimeOut = self.getParam(
                "Timing", "float_gui_time_out", glo.QDSpy_guiTimeOut
            )

            self.pathShader = self.getParam("Paths", "str_shader", glo.QDSpy_pathShader)
            self.pathStim = self.getParam("Paths", "str_stimuli", glo.QDSpy_pathStimuli)
            self.pathApp = self.getParam(
                "Paths", "str_application", glo.QDSpy_pathApplication
            )
            self.pathLogs = self.getParam(
                "Paths", "str_logFiles", glo.QDSpy_pathLogFiles
            )

            self.useLCr = self.getParam(
                "Display", "bool_use_lightcrafter", glo.QDSpy_use_Lightcrafter
            )
            self.LCrDevTypeName = self.getParam(
                "Display", "str_lcr_device_type", glo.QDSpy_LCrDevTypeName
            ).upper()
            temp = self.getParam("Display", "str_LED_names", glo.QDSpy_LEDNames_default)
            self.LEDNames = temp.split(",")
            temp = self.getParam(
                "Display",
                "str_LED_filter_peak_wavelengths",
                glo.QDSpy_LEDPeakWLs_default,
            )
            self.LEDPeakWLs = [int(i) for i in temp.split(sep=",")]
            temp = self.getParam(
                "Display", "str_LED_device_indices", glo.QDSpy_LEDDevIndex_default
            )
            self.LEDDevIndices = [int(i) for i in temp.split(sep=",")]
            temp = self.getParam(
                "Display", "str_LED_indices", glo.QDSpy_LEDIndex_default
            )
            self.LEDIndices = [int(i) for i in temp.split(sep=",")]
            temp = self.getParam(
                "Display", "str_led_default_currents", glo.QDSpy_LEDCurrents_default
            )
            self.LEDDefCurr = [int(i) for i in temp.split(sep=",")]
            temp = self.getParam(
                "Display", "str_led_max_currents", glo.QDSpy_LEDCurrents_max
            )
            self.LEDMaxCurr = [int(i) for i in temp.split(sep=",")]
            temp = self.getParam(
                "Display", "str_LED_QtColor", glo.QDSpy_LEDQtColors_default
            )
            self.LEDQtColors = temp.split(sep=",")
            self.allowGammaLUT = self.getParam(
                "Display", "bool_allowGammaLUT", glo.QDSpy_allowGammaLUT_default
            )
            self.userLUTFName = self.getParam(
                "Display", "str_userGammaLUTFileName", glo.QDSpy_userGammaLUTFileName
            )
            self.markShowOnScr = self.getParam(
                "Display", "bool_markerShowOnScreen", glo.QDSpy_markerShowOnScr
            )
            temp = self.getParam("Display", "str_markerRGBA", glo.QDSpy_markerRGBA)
            self.markRGBA = [int(i) for i in temp.split(sep=",")]
            temp = self.getParam(
                "Display", "str_antiMarkerRGBA", glo.QDSpy_antiMarkerRGBA
            )
            self.antiMarkRGBA = [int(i) for i in temp.split(sep=",")]

            self.markScrWidthFract = self.getParam(
                "Display", "float_markerScrWidthFract", glo.QDSpy_markerScrWidthFract
            )

            self.useCtrlWin = self.getParam(
                "Display", "bool_use_control_window", glo.QDSpy_useCtrlWin
            )
            self.ctrlWinScale = self.getParam(
                "Display", "float_control_window_scale", glo.QDSpy_ctrlWinScale
            )

            self.use3DTextures = self.getParam(
                "Tweaking", "bool_use3DTextures", glo.QDSpy_use3DTextures
            )
            self.recordStim = self.getParam(
                "Tweaking", "bool_recordStim", glo.QDSpy_recordStim
            )

            self.rec_f_downsample_x = self.getParam(
                "Tweaking", "int_rec_f_downsample_x", glo.QDSpy_recordStim
            )
            self.rec_f_downsample_t = self.getParam(
                "Tweaking", "int_rec_f_downsample_t", glo.QDSpy_recordStim
            )
            # --> TE
            _id = self.getParam(
                "Tweaking", "int_rec_setup_id", glo.QDSpy_rec_setup_id
            )
            self.rec_setup_id = _id if _id >= 0 else None
            # <--

            temp = self.getParam(
                "Tweaking", "str_window_geometry_cam", glo.QDSpy_camWinGeometry
            )
            self.camWinGeom = [int(i) for i in temp.split(sep=",")]
            self.allowCam = self.getParam(
                "Tweaking", "bool_allow_camera", glo.QDSpy_allowCam
            )

        else:
            # Initialization file does not exist, recreate
            #
            _log.Log.write(
                "WARNING",
                "`QDSpy.ini`not found, generating new "
                "configuration file from default values",
            )

            self.conf.add_section("Stage")
            self.setParam("Stage", "float_refresh_frequency_Hz", glo.QDSpy_refresh_Hz)
            self.setParam("Stage", "int_screen_width_pix", glo.QDSpy_winWidth)
            self.setParam("Stage", "int_screen_height_pix", glo.QDSpy_winHeight)
            self.setParam("Stage", "int_center_offs_x_pix", 0)
            self.setParam("Stage", "int_center_offs_y_pix", 0)
            self.setParam("Stage", "float_center_rotation_deg", 0.0)
            self.setParam("Stage", "float_scale_x_um_per_pix", 1.0)
            self.setParam("Stage", "float_scale_y_um_per_pix", 1.0)
            self.setParam("Stage", "int_screen_index", glo.QDSpy_screenIndex)
            self.setParam(
                "Stage", "bool_disableFullScrCmd", glo.QDSpy_disableFullScrCmd
            )
            self.setParam("Stage", "int_window_left_pix", 0)
            self.setParam("Stage", "int_window_top_pix", 0)

            self.conf.add_section("Overlay")
            self.setParam(
                "Overlay", "bool_use_screen_overlay", glo.QDSpy_useScrOverlayMode
            )
            self.setParam("Overlay", "int_screen_index_GUI", glo.QDSpy_screenIndexGUI)
            self.setParam("Overlay", "int_screen1_2_width_pix", glo.QDSpy_winWidth1_2)
            self.setParam("Overlay", "int_screen1_2_height_pix", glo.QDSpy_winHeight1_2)
            self.setParam(
                "Overlay", "int_x_offset_screen1_pix", glo.QDSpy_xOffsetScr1_pix
            )
            self.setParam(
                "Overlay", "int_y_offset_screen1_pix", glo.QDSpy_yOffsetScr1_pix
            )
            self.setParam(
                "Overlay",
                "int_x_offset_screen2_center_pix",
                glo.QDSpy_xOffsetScr2Center_pix,
            )
            self.setParam(
                "Overlay",
                "int_y_offset_screen2_center_pix",
                glo.QDSpy_yOffsetScr2Center_pix,
            )
            self.setParam("Overlay", "bool_v_flip_screen1", glo.QDSpy_vFlipScr1)
            self.setParam("Overlay", "bool_h_flip_screen1", glo.QDSpy_hFlipScr1)
            self.setParam("Overlay", "bool_v_flip_screen2", glo.QDSpy_vFlipScr2)
            self.setParam("Overlay", "bool_h_flip_screen2", glo.QDSpy_hFlipScr2)

            self.conf.add_section("Timing")
            self.setParam(
                "Timing", "bool_incr_process_prior", glo.QDSpy_incProcessPrior
            )
            self.setParam("Timing", "bool_try_forcing_fsync", glo.QDSpy_tryForcingFSync)
            self.setParam(
                "Timing",
                "bool_disable_garbage_collector",
                glo.QDSpy_disableGarbageCollect,
            )
            self.setParam("Timing", "float_gui_time_out", glo.QDSpy_guiTimeOut)
            self.setParam("Timing", "bool_track_timing", glo.QDSpy_trackTiming)
            self.setParam(
                "Timing", "bool_warn_when_frames_dropped", glo.QDSpy_warnDroppedFrames
            )
            self.setParam(
                "Timing", "float_frame_dur_threshold_ms", glo.QDSpy_FrDurThreshold_ms
            )
            self.setParam("Timing", "bool_use_digitalIO", glo.QDSpy_useUL_DIO)
            self.setParam("Timing", "str_digitalio_board_type", glo.QDSpy_UL_boardType)
            self.setParam("Timing", "int_digitalIO_board_num", glo.QDSpy_UL_boardNum)
            self.setParam("Timing", "int_digitalIO_device_num", glo.QDSpy_UL_deviceNum)
            self.setParam("Timing", "str_digitalio_port_out", glo.QDSpy_UL_portOut)
            self.setParam("Timing", "str_digitalio_port_in", glo.QDSpy_UL_portIn)
            self.setParam(
                "Timing", "str_digitalio_port_user_out", glo.QDSpy_UL_portOut_User
            )
            self.setParam(
                "Timing", "int_digitalio_pin_markerOut", glo.QDSpy_UL_pinMarkerOut
            )
            self.setParam(
                "Timing", "int_digitalio_pin_triggerin", glo.QDSpy_UL_pinTriggerIn
            )
            self.setParam(
                "Timing", "str_digitalio_pin_userout1", glo.QDSpy_UL_pinUserOut1
            )
            self.setParam(
                "Timing", "str_digitalio_pin_userout2", glo.QDSpy_UL_pinUserOut2
            )

            self.conf.add_section("Paths")
            self.setParam("Paths", "str_shader", glo.QDSpy_pathShader)
            self.setParam("Paths", "str_stimuli", glo.QDSpy_pathStimuli)
            self.setParam("Paths", "str_application", glo.QDSpy_pathApplication)
            self.setParam("Paths", "str_logFiles", glo.QDSpy_pathLogFiles)

            self.conf.add_section("Display")
            self.setParam(
                "Display", "bool_use_lightcrafter", glo.QDSpy_use_Lightcrafter
            )
            self.setParam(
                "Display", "str_lcr_device_type", glo.QDSpy_LCrDevTypeName
            )
            self.setParam("Display", "str_LED_names", glo.QDSpy_LEDNames_default)
            self.setParam(
                "Display",
                "str_LED_filter_peak_wavelengths",
                glo.QDSpy_LEDPeakWLs_default,
            )
            self.setParam(
                "Display", "str_LED_device_indices", glo.QDSpy_LEDDevIndex_default
            )
            self.setParam("Display", "str_LED_indices", glo.QDSpy_LEDIndex_default)
            self.setParam(
                "Display", "str_led_default_currents", glo.QDSpy_LEDCurrents_default
            )
            self.setParam("Display", "str_led_max_currents", glo.QDSpy_LEDCurrents_max)
            self.setParam("Display", "str_LED_QtColor", glo.QDSpy_LEDQtColors_default)
            self.setParam(
                "Display", "bool_allowGammaLUT", glo.QDSpy_allowGammaLUT_default
            )
            self.setParam(
                "Display", "str_userGammaLUTFileName", glo.QDSpy_userGammaLUTFileName
            )
            self.setParam(
                "Display", "bool_markerShowOnScreen", glo.QDSpy_markerShowOnScr
            )
            self.setParam("Display", "str_markerRGBA", glo.QDSpy_markerRGBA)
            self.setParam("Display", "str_antiMarkerRGBA", glo.QDSpy_antiMarkerRGBA)
            self.setParam(
                "Display", "float_markerScrWidthFract", glo.QDSpy_markerScrWidthFract
            )
            self.setParam("Display", "bool_use_control_window", glo.QDSpy_useCtrlWin)
            self.setParam(
                "Display", "float_control_window_scale", glo.QDSpy_ctrlWinScale
            )

            self.conf.add_section("Tweaking")
            self.setParam("Tweaking", "bool_use3DTextures", glo.QDSpy_use3DTextures)
            self.setParam("Tweaking", "bool_recordStim", glo.QDSpy_recordStim)

            self.setParam(
                "Tweaking", "int_rec_f_downsample_x", glo.QDSpy_rec_f_downsample_x
            )
            self.setParam(
                "Tweaking", "int_rec_f_downsample_t", glo.QDSpy_rec_f_downsample_t
            )

            self.setParam(
                "Tweaking", "str_window_geometry_cam", glo.QDSpy_camWinGeometry
            )
            self.setParam("Tweaking", "bool_allow_camera", glo.QDSpy_allowCam)

            self.save()
 
        self.isLoaded = True

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def save(self):
        # Safe configuration file
        #
        with open(self.iniPath, "w") as confFile:
            self.conf.write(confFile)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def createStageFromConfig(self):
        # Generates a Stage instance from the current configuration
        # parameters
        #
        if self.isLoaded:
            d = {}
            d["scrReqFreq_Hz"] = self.conf.getfloat(
                "Stage", "float_refresh_frequency_Hz"
            )
            d["dxScr"] = self.conf.getint("Stage", "int_screen_width_pix")
            d["dyScr"] = self.conf.getint("Stage", "int_screen_height_pix")
            d["centOffX_pix"] = self.conf.getint("Stage", "int_center_offs_x_pix")
            d["centOffY_pix"] = self.conf.getint("Stage", "int_center_offs_y_pix")
            d["scalX_umPerPix"] = self.conf.getfloat("Stage", "float_scale_x_um_per_pix")
            d["scalY_umPerPix"] = self.conf.getfloat("Stage", "float_scale_y_um_per_pix")
            d["rot_angle"] = self.conf.getfloat("Stage", "float_center_rotation_deg")
            d["scrIndex"] = self.conf.getint("Stage", "int_screen_index")
            d["disFScr"] = self.conf.getboolean("Stage", "bool_disableFullScrCmd")
            d["xWinLeft"] = self.conf.getint("Stage", "int_window_left_pix")
            d["yWinTop"] = self.conf.getint("Stage", "int_window_top_pix")
            d["useScrOvl"] = self.conf.getboolean("Overlay", "bool_use_screen_overlay")
            d["scrIndGUI"] = self.conf.getint("Overlay", "int_screen_index_GUI")
            d["dxScr12"] = self.conf.getint("Overlay", "int_screen1_2_width_pix")
            d["dyScr12"] = self.conf.getint("Overlay", "int_screen1_2_height_pix")
            d["offXScr1_pix"] = self.conf.getint("Overlay", "int_x_offset_screen1_pix")
            d["offYScr1_pix"] = self.conf.getint("Overlay", "int_y_offset_screen1_pix")
            d["offXScr2_pix"] = self.conf.getint("Overlay", "int_x_offset_screen2_center_pix")
            d["offYScr2_pix"] = self.conf.getint("Overlay", "int_y_offset_screen2_center_pix")
            d["vFlipScr1"] = self.conf.getboolean("Overlay", "bool_v_flip_screen1")
            d["hFlipScr1"] = self.conf.getboolean("Overlay", "bool_h_flip_screen1")
            d["vFlipScr2"] = self.conf.getboolean("Overlay", "bool_v_flip_screen2")
            d["hFlipScr2"] = self.conf.getboolean("Overlay", "bool_h_flip_screen2")

            Stage = stg.Stage(d, _isNew=True)

            # Read user-define gamma LUT, if one is defined
            #
            if len(self.userLUTFName) > 0:
                Stage.LUT_userDefined = gma.loadGammaLUT(
                    self.pathApp + self.userLUTFName
                )
            return Stage

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def saveStageToConfig(self, _Stage):
        # Save the screen calibration parameters (center, offset, scaling,
        # rotation) from the Stage object to the ini file
        #
        if self.isLoaded and _Stage is not None:
            self.setParam("Stage", "int_center_offs_x_pix", _Stage.centOffX_pix)
            self.setParam("Stage", "int_center_offs_y_pix", _Stage.centOffY_pix)
            self.setParam("Stage", "float_center_rotation_deg", _Stage.rot_angle)
            self.setParam("Stage", "float_scale_x_um_per_pix", _Stage.scalX_umPerPix)
            self.setParam("Stage", "float_scale_y_um_per_pix", _Stage.scalY_umPerPix)
            self.setParam("Overlay", "int_screen1_2_width_pix", _Stage.dxScr12)
            self.setParam("Overlay", "int_screen1_2_height_pix", _Stage.dyScr12)
            self.setParam("Overlay", "int_x_offset_screen1_pix", _Stage.offXScr1_pix)
            self.setParam("Overlay", "int_y_offset_screen1_pix", _Stage.offYScr1_pix)
            self.setParam("Overlay", "int_x_offset_screen2_center_pix", _Stage.offXScr2_pix)
            self.setParam("Overlay", "int_y_offset_screen2_center_pix", _Stage.offYScr2_pix)
            self.save()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def saveWinPosToConfig(self):
        # Save window positions to the ini file
        #
        if self.isLoaded:
            self.setParam(
                "Tweaking", "str_window_geometry_cam", 
                self.camWinGeom.__str__()[1:-1]
            )
            self.save()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setParam(self, _section, _key, _default):
        # Wrapper for self.conf.set
        self.conf.set(_section, _key, str(_default))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getParam(self, _section, _key, _default):
        # Return value of key in given section; if it does not exist, add
        # this key and set it to the default value
        #
        if self.conf.has_option(_section, _key):
            typeStr = _key.split("_")[0].lower()
            if typeStr == "bool":
                return self.conf.getboolean(_section, _key)
            elif typeStr == "int":
                return self.conf.getint(_section, _key)
            elif typeStr == "float":
                return self.conf.getfloat(_section, _key)
            else:
                return self.conf.get(_section, _key)
        else:
            self.setParam(_section, _key, _default)
            return _default


# ---------------------------------------------------------------------
# Parsing command-line arguments
#
# ---------------------------------------------------------------------
def getParsedArgv():
    '''Return the parsed command-line arguments
    '''
    parser = argparse.ArgumentParser(description="Present a stimulus.")
    parser.add_argument(
        "-t",
        "--timing",
        type=int,
        choices=[0],
        default=glo.QDSpy_graphicsAPI,
        help="mechanism used for stimulus timing",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="show detailed analysis of timimg etc.",
    )
    parser.add_argument(
        "-c",
        "--compile",
        action="store_true",
        help="re-compile stimulus, even if up-to-date",
    )
    parser.add_argument(
        "-g", "--gui", action="store_true", help="send messages to GUI only"
    )
    parser.add_argument(
        "fNameStim",
        default="x",
        nargs="?",
        help="optional stimulus file name w/o file extension",
    )
    return parser.parse_args()

# ---------------------------------------------------------------------
