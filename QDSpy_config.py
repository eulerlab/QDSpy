#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
#  QDSpy_config.py
#
#  The config stage class (Config) manages an external configuration
#  file using ConfigParser
#
#  Copyright (c) 2013-2015 Thomas Euler
#  All rights reserved.
#
# ---------------------------------------------------------------------
__author__ 	= "code@eulerlab.de"

import sys
import argparse
import configparser
import QDSpy_stage        as stg
import QDSpy_gamma        as gma
import QDSpy_stim_support as ssp
import QDSpy_global       as glo

# ---------------------------------------------------------------------
# Configuration file class
# ---------------------------------------------------------------------
class Config:
  def __init__(self):
    # Initialization
    #
    self.isLoaded     = False
    self.conf         = configparser.RawConfigParser()

    # Get some information on the platform
    #
    self.isWindows    = (sys.platform =='win32')
    self.pyVersion    = sys.version_info[0] +sys.version_info[1]/10

    # Set configuration default values
    #
    self.incPP        = glo.QDSpy_incProcessPrior
    self.fSync        = glo.QDSpy_tryForcingFSync
    self.useDIO       = glo.QDSpy_useUL_DIO
    self.DIObrd       = glo.QDSpy_UL_boardNum
    self.DIOdev       = glo.QDSpy_UL_deviceNum
    self.DIOportOut   = glo.QDSpy_UL_portOut
    self.DIOportIn    = glo.QDSpy_UL_portIn
    self.DIOpinMarker = glo.QDSpy_UL_pinMarkerOut
    self.disFScr      = glo.QDSpy_disableFullScrCmd
    self.pathShader   = glo.QDSpy_pathShader
    self.pathStim     = glo.QDSpy_pathStimuli
    self.pathApp      = glo.QDSpy_pathApplication
    self.isTrackTime  = glo.QDSpy_trackTiming
    self.isWarnFrDrop = glo.QDSpy_warnDroppedFrames    
    self.maxDtTr_ms   = glo.QDSpy_FrDurThreshold_ms
    self.disGC        = glo.QDSpy_disableGarbageCollect
    self.useLCr       = glo.QDSpy_use_Lightcrafter
    self.LEDNames     = glo.QDSpy_LEDNames_default
    self.LEDPeakWLs   = glo.QDSpy_LEDPeakWLs_default
    self.LEDQtColors  = glo.QDSpy_LEDQtColors_default
    self.allowGammaLUT= glo.QDSpy_allowGammaLUT_default
    self.userLUTFName = glo.QDSpy_userGammaLUTFileName
    self.pathLogs     = glo.QDSpy_pathLogFiles
    self.use3DTextures= glo.QDSpy_use3DTextures
    self.recordStim   = glo.QDSpy_recordStim
    self.markShowOnScr= glo.QDSpy_markerShowOnScr
    self.markRGBA     = glo.QDSpy_markerRGBA

    try:
      self.conf.readfp(open(glo.QDSpy_iniFileName))
  
      self.incPP        = self.conf.getboolean("Timing", "bool_incr_process_prior")
      self.fSync        = self.conf.getboolean("Timing", "bool_try_forcing_fsync")
      self.useDIO       = self.conf.getboolean("Timing", "bool_use_digitalIO")
      self.DIObrd       = self.conf.getint("Timing", "int_digitalIO_board_num")
      self.DIOdev       = self.conf.getint("Timing", "int_digitalIO_device_num")
      self.DIOportOut   = self.conf.get("Timing", "int_digitalio_port_out")
      self.DIOportIn    = self.conf.get("Timing", "int_digitalio_port_in")
      self.DIOpinMarker = self.conf.getint("Timing", "int_digitalio_pin_markerOut")
      self.isTrackTime  = self.conf.getboolean("Timing", "bool_track_timing")
      self.isWarnFrDrop = self.conf.getboolean("Timing", "bool_warn_when_frames_dropped")
      self.maxDtTr_ms   = self.conf.getfloat("Timing", "float_frame_dur_threshold_ms")
      self.disGC        = self.conf.getboolean("Timing", "bool_disable_garbage_collector")
      
      self.pathShader   = self.conf.get("Paths", "str_shader")
      self.pathStim     = self.conf.get("Paths", "str_stimuli")
      self.pathApp      = self.conf.get("Paths", "str_application")
      self.pathLogs     = self.conf.get("Paths", "str_logFiles")
      
      self.useLCr       = self.conf.getboolean("Display", "bool_use_lightcrafter")
      temp              = self.conf.get("Display", "str_LED_names")      
      self.LEDNames     = temp.split(sep=",")    
      temp              = self.conf.get("Display", "int_LED_filter_peak_wavelengths")      
      self.LEDPeakWLs   = [int(i) for i in temp.split(sep=",")]
      temp              = self.conf.get("Display", "int_LED_QtColor")      
      self.LEDQtColors  = temp.split(sep=",")
      self.allowGammaLUT= self.conf.getboolean("Display", "bool_allowGammaLUT")
      self.userLUTFName = self.conf.get("Display", "str_userGammaLUTFileName")
      self.markShowOnScr= self.conf.getboolean("Display", "bool_markerShowOnScreen")
      temp              = self.conf.get("Display", "int_markerRGBA")      
      self.markRGBA     = [int(i) for i in temp.split(sep=",")]
      
      self.use3DTextures= self.conf.getboolean("Tweaking", "bool_use3DTextures")
      self.recordStim   = self.conf.getboolean("Tweaking", "bool_recordStim")
      
    except IOError:
      # Initialization file does not exist, recreate
      #
      ssp.Log.write("WARNING", "`QDSpy.ini`not found, generating new "\
                               "configuration file from default values")    
    
      self.conf.add_section("Stage")
      self.conf.set("Stage", "float_refresh_frequency_Hz",
                    glo.QDSpy_refresh_Hz)
      self.conf.set("Stage", "int_screen_width_pix",      
                    glo.QDSpy_winWidth)
      self.conf.set("Stage", "int_screen_height_pix",     
                    glo.QDSpy_winHeight)
      self.conf.set("Stage", "int_center_offs_x_pix",     0)
      self.conf.set("Stage", "int_center_offs_y_pix",     0)
      self.conf.set("Stage", "float_center_rotation_deg", 0.0)
      self.conf.set("Stage", "float_scale_x_um_per_pix",  1.0)
      self.conf.set("Stage", "float_scale_y_um_per_pix",  1.0)
      self.conf.set("Stage", "int_screen_index",          
                    glo.QDSpy_screenIndex)
      self.conf.set("Stage", "bool_disableFullScrCmd",    
                    glo.QDSpy_disableFullScrCmd)
      self.conf.set("Stage", "int_window_left_pix",       0)
      self.conf.set("Stage", "int_window_top_pix",        0)

      self.conf.add_section("Timing")
      self.conf.set("Timing","bool_incr_process_prior",   
                    glo.QDSpy_incProcessPrior)
      self.conf.set("Timing","bool_try_forcing_fsync",    
                    glo.QDSpy_tryForcingFSync)
      self.conf.set("Timing","bool_disable_garbage_collector", 
                    glo.QDSpy_disableGarbageCollect)      
      self.conf.set("Timing","bool_track_timing",         
                    glo.QDSpy_trackTiming)
      self.conf.set("Timing","bool_warn_when_frames_dropped", 
                    glo.QDSpy_warnDroppedFrames)
      self.conf.set("Timing","float_frame_dur_threshold_ms", 
                    glo.QDSpy_FrDurThreshold_ms)
      self.conf.set("Timing","bool_use_digitalIO",        
                    glo.QDSpy_useUL_DIO)
      self.conf.set("Timing","int_digitalIO_board_num",   
                    glo.QDSpy_UL_boardNum)
      self.conf.set("Timing","int_digitalIO_device_num",  
                    glo.QDSpy_UL_deviceNum)
      self.conf.set("Timing","int_digitalio_port_out",    
                    glo.QDSpy_UL_portOut)
      self.conf.set("Timing","int_digitalio_port_in",     
                    glo.QDSpy_UL_portIn)
      self.conf.set("Timing","int_digitalio_pin_markerOut", 
                    glo.QDSpy_UL_pinMarkerOut)

      self.conf.add_section("Paths")
      self.conf.set("Paths", "str_shader",                
                    glo.QDSpy_pathShader)
      self.conf.set("Paths", "str_stimuli",               
                    glo.QDSpy_pathStimuli)
      self.conf.set("Paths", "str_application",           
                    glo.QDSpy_pathApplication)
      self.conf.set("Paths", "str_logFiles",              
                    glo.QDSpy_pathLogFiles)
      
      self.conf.add_section("Display")      
      self.conf.set("Display","bool_use_lightcrafter",   
                    glo.QDSpy_use_Lightcrafter)
      self.conf.set("Display","str_LED_names",            
                    glo.QDSpy_LEDNames_default)
      self.conf.set("Display","int_LED_filter_peak_wavelengths", 
                    glo.QDSpy_LEDPeakWLs_default)
      self.conf.set("Display","int_LED_QtColor",          
                    glo.QDSpy_LEDQtColors_default)
      self.conf.set("Display","bool_allowGammaLUT",       
                    glo.QDSpy_allowGammaLUT_default)
      self.conf.set("Display","str_userGammaLUTFileName", 
                    glo.QDSpy_userGammaLUTFileName)
      self.conf.set("Display","bool_markerShowOnScreen",  
                    glo.QDSpy_markerShowOnScr)
      self.conf.set("Display","int_markerRGBA",           
                    glo.QDSpy_markerRGBA)

      self.conf.add_section("Tweaking")      
      self.conf.set("Tweaking","bool_use3DTextures",      
                    glo.QDSpy_use3DTextures)
      self.conf.set("Tweaking","bool_recordStim",         
                    glo.QDSpy_recordStim)

      with open(glo.QDSpy_iniFileName, 'w') as confFile:
        self.conf.write(confFile)

    self.isLoaded   = True

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def save(self):
    # Safe configuration file
    #
    with open(glo.QDSpy_iniFileName, 'w') as confFile:
      self.conf.write(confFile)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def createStageFromConfig(self):
    # Generates a Stage instance from the current configuration
    # parameters
    #
    if self.isLoaded:
      rFreq   = self.conf.getfloat("Stage",  "float_refresh_frequency_Hz")
      winW    = self.conf.getint("Stage",    "int_screen_width_pix")
      winH    = self.conf.getint("Stage",    "int_screen_height_pix")
      offX    = self.conf.getint("Stage",    "int_center_offs_x_pix")
      offY    = self.conf.getint("Stage",    "int_center_offs_y_pix")
      scalX   = self.conf.getfloat("Stage",  "float_scale_x_um_per_pix")
      scalY   = self.conf.getfloat("Stage",  "float_scale_y_um_per_pix")
      rot     = self.conf.getfloat("Stage",  "float_center_rotation_deg")
      scrInd  = self.conf.getint("Stage",    "int_screen_index")
      disFScr = self.conf.getboolean("Stage","bool_disableFullScrCmd")
      winL    = self.conf.getint("Stage",    "int_window_left_pix")
      winT    = self.conf.getint("Stage",    "int_window_top_pix")

      Stage   = stg.Stage(winW, winH, winL, winT, scalX, scalY, offX, offY, 
                          rot, rFreq, scrInd, disFScr)
                          
      # Read user-define gamma LUT, if one is defined
      #                          
      if (len(self.userLUTFName) > 0):
        Stage.LUT_userDefined = gma.loadGammaLUT(self.pathApp +
                                                 self.userLUTFName)
                          
      return Stage
  
   # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def saveStageToConfig(self, _Stage):
    # Save the screen calibration parameters (center, offset, scaling, 
    # rotation) from the Stage object to the ini file
    #
    if self.isLoaded and (_Stage != None):
      self.conf.set("Stage", "int_center_offs_x_pix",     
                    _Stage.centOffX_pix)
      self.conf.set("Stage", "int_center_offs_y_pix",     
                    _Stage.centOffY_pix)
      self.conf.set("Stage", "float_center_rotation_deg", 
                    _Stage.rot_angle)
      self.conf.set("Stage", "float_scale_x_um_per_pix",  
                    _Stage.scalX_umPerPix)
      self.conf.set("Stage", "float_scale_y_um_per_pix",  
                    _Stage.scalY_umPerPix)
      self.save()
  
# ---------------------------------------------------------------------
# Parsing command-line arguments
#
# ---------------------------------------------------------------------
def getParsedArgv():
  # Return the parsed command-line arguments
  #
  parser    = argparse.ArgumentParser(description="Present a stimulus.")
  parser.add_argument("-t", "--timing", type=int, choices=[0],
                      default=glo.QDSpy_graphicsAPI,
                      help="mechanism used for stimulus timing")
  parser.add_argument("-v", "--verbose", action="store_true",
                      help="show detailed analysis of timimg etc.")
  parser.add_argument("-c", "--compile", action="store_true",
                      help="re-compile stimulus, even if up-to-date")
  parser.add_argument("-g", "--gui", action="store_true",
                      help="send messages to GUI only")
  parser.add_argument("fNameStim", default="x", nargs="?",
                      help="optional stimulus file name w/o file extension")

  return parser.parse_args()

# ---------------------------------------------------------------------
