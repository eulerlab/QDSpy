#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
#  QDSpy_core_view.py
#
#  The view class provides an OpenGL window/context
#
##  Copyright (c) 2013-2016 Thomas Euler
#  All rights reserved.
#
# ---------------------------------------------------------------------
__author__ 	= "code@eulerlab.de"

from   QDSpy_global          import *
import QDSpy_stim_support    as ssp
import QDSpy_config          as cfg
import pyglet
pyglet.options['debug_gl'] = QDSpy_doOpenGLErrorChecking

# ---------------------------------------------------------------------
# Determine from command line argument which OpenGL solution to use
# for timing and what reporting level is set
#
global  QDSpy_verbose

args              = cfg.getParsedArgv()
QDSpy_verbose     = args.verbose
QDSpy_graphicsAPI = args.timing

if   QDSpy_graphicsAPI == 0:
  import  QDSpy_core_GL_default as grx
"""
elif QDSpy_graphicsAPI == 1:
  import  QDSpy_core_GL_alter1  as grx
elif QDSpy_graphicsAPI == 2:
  import  QDSpy_core_GL_alter2  as grx
"""

# ---------------------------------------------------------------------
# View class
# (based on pyOpenGL and pyglet)
# ---------------------------------------------------------------------
class View:
  def __init__(self, _Stage, _Conf):
    # Initializing
    #
    self.Stage          = _Stage
    self.Conf           = _Conf
    self.winMirror      = None
    self.__reset()

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def __reset(self):
    # Resets internal states; don't use
    #
    self.onKeyboardProc = None
    self.onDrawProc     = None
    self.isWinAvailable = False
    # ...

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def createWindow(self):
    # Create OpenGL window(s) ...
    #
    # Initialize OpenGL
    #
    grx.init()

    # Log some information about OpenGL on this machine
    #
    ssp.Log.write("INFO", grx.getInfoGLStr())
    ssp.Log.write("INFO", grx.getInfoGLSLStr())
    ssp.Log.write("INFO", grx.getInfoRendererStr())
    ssp.Log.write("INFO", grx.getImplementationStr())
    if QDSpy_graphicsAPI == 1:
      ssp.Log.write("INFO", "Requested  : {0:.1f} Hz"
                    .format(self.Stage.rFreq_Hz))

    # Check if window or fullscreen mode is requested
    #
    self.isFullScr     = ((self.Stage.dxScr <= 0) or (self.Stage.dyScr <= 0))
    self.screens       = grx.getScreens()
    if self.isFullScr:
      # Fullscreen mode, determine number of screens; if a dual screen
      # configuration is detected, the second screen is used, otherwise
      # the primary screeen
      #
      if self.Stage.scrIndex < len(self.screens):
        self.iScr      = self.Stage.scrIndex
      else:
        self.iScr      = len(self.screens) -1
      self.winWidth    = self.screens[self.iScr].width
      self.winHeight   = self.screens[self.iScr].height
      self.Stage.winXCorrFact   = 1.0
      ssp.Log.write("INFO", "screen={0}".format(self.screens))
      self.winPresent  = grx.getWindows(self, True)
      grx.setMouseVisible(self, False)
      ssp.Log.write("ok", "Fullscreen mode, {0}x{1} pixels, on screen #{2}"
                    .format(self.winWidth, self.winHeight, self.iScr))

    else:
      # Window mode
      #
      self.winWidth    = self.Stage.dxScr
      self.winHeight   = self.Stage.dyScr
      self.winLeft     = self.Stage.xWinLeft
      self.winTop      = self.Stage.yWinTop
      self.winTitle    = QDSpy_versionStr
      
      # Adjust scaling factor such that presentation in window is
      # to scale; assuming that 1 pix = 1um is true for the current
      # screen's maximal resolution
      #
      self.iScr        = 0
      self.screens     = grx.getScreens()
      """
      self.Stage.winXCorrFact   = float(self.winWidth) /self.screens[0].width
      """
      self.winPresent  = grx.getWindows(self, False)
      ssp.Log.write("ok", "Window mode, {0}x{1} pixels"
                    .format(self.winWidth, self.winHeight))
    
    """                    
    self.winMirror     = pyglet.window.Window()
    """

    # Update stage object
    #
    self.Stage.dxScr   = self.winWidth
    self.Stage.dyScr   = self.winHeight
    self.Stage.isFullScr = self.isFullScr   

    # Try to force vsync, if requested
    #
    result = grx.forceVSync(self)
    if   result < 0:
      ssp.Log.write("WARNING", "SwapIntervalEXT() not supported")
    elif result >= 0:
      ssp.Log.write(" ", "{0:11}: forced fsync"
                    .format("ENABLED" if self.Conf.fSync else "disabled"))
      if result == 1:
        ssp.Log.write("ok", "SwapIntervalEXT() reported success")

    # Define event handlers and some general OpenGL properties
    #
    grx.setStandardProperties(self)
    grx.setEventHandlers(self)

    # Success ...
    #
    self.isWinAvailable = True

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def clear(self):
    grx.clearScreen()
    grx.present(self)
    
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def setOnKeyboardHandler(self, _onKeybProc):
    if self.isWinAvailable:
      self.onKeyboardProc = _onKeybProc

  def setOnDrawHandler(self, _onDrawProc):
    if self.isWinAvailable:
      self.onDrawProc     = _onDrawProc

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def onKeyboard(self, _key, _x, _y):
    if not(self.onKeyboardProc == None):
      self.onKeyboardProc(_key, _x, _y)

  def onDraw(self):
    if not(self.onDrawProc == None):
      self.onDrawProc()

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def killWindow(self):
    # Kill OpenGL window(s) ...
    #
    if self.isWinAvailable:
      # Restore mouse pointer, and exit main loop, which kills the
      # window(s)
      #
      grx.setMouseVisible(self, True)
      grx.endMainLoop(self)
      self.__reset()

# ---------------------------------------------------------------------
