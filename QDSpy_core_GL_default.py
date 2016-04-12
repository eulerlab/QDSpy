#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
#  QDSpy_core_GL_default.py
#
#  Copyright (c) 2013-2015 Thomas Euler
#  All rights reserved.
#
# ---------------------------------------------------------------------
__author__ 	= "code@eulerlab.de"

import sys
import ctypes
from   QDSpy_global      import *
from   OpenGL.GLUT       import *
from   OpenGL.GLU        import *
from   OpenGL.WGL        import *
import pyglet
from   pyglet.gl         import *
from   pyglet.gl.gl_info import GLInfo
pyglet.options['debug_gl']  = QDSpy_doOpenGLErrorChecking

if sys.platform == 'win32':
  from win32api          import SetCursorPos
  
# ---------------------------------------------------------------------
def init ():
  pass

# ---------------------------------------------------------------------
def getInfoRendererStr ():
  info     = GLInfo()
  info.set_active_context()
  return "Renderer   : " +info.get_renderer() +" by " +info.get_vendor()

def getInfoGLStr ():
  info     = GLInfo()
  info.set_active_context()
  return "OpenGL     : v" +info.get_version()

def getInfoGLSLStr ():
  val = pyglet.gl.glGetString(pyglet.gl.GL_SHADING_LANGUAGE_VERSION)
  return "GLSL       : v" +ctypes.string_at(val).decode()

def getImplementationStr ():
  return "Timing     : vsync-based (Pyglet calls), DEFAULT"

# ---------------------------------------------------------------------
def getScreens ():
  platform = pyglet.window.get_platform()
  display  = platform.get_default_display()
  return display.get_screens()

# ---------------------------------------------------------------------
def getWindows (_View, _isFullScr):
  # Create a pyglet window
  #
  if _isFullScr:
    winPyglet = pyglet.window.Window(vsync=True, fullscreen=True,
                                     screen=_View.screens[_View.iScr],
                                     width=_View.winWidth,
                                     height=_View.winHeight,
                                     caption=QDSpy_fullScrWinName)
    
  else:
    winPyglet = pyglet.window.Window(vsync=True,
                                     width=_View.winWidth,
                                     height=_View.winHeight,
                                     caption=_View.winTitle,
                                     style=pyglet.window.Window.WINDOW_STYLE_TOOL)
    winPyglet.set_location(_View.winLeft, _View.winTop)

  return winPyglet

# ---------------------------------------------------------------------
def setMouseVisible (_View, _visible):
  # Make mouse cursor visible/invisible
  #
  #_View.winPresent.switch_to()
  _View.winPresent.set_mouse_visible(_visible)
  if not(sys.platform == 'win32'):
    _View.winPresent.set_exclusive_mouse(not _visible)
  else:
    if not(_visible):
      SetCursorPos((0,0))

# ---------------------------------------------------------------------
def forceVSync (_View):
  # Check of swap-control-extention is available and force vsync if
  # requested
  #
  result = -1
  if _View.Conf.isWindows:
    if(pyglet.gl.wgl_info.have_extension("WGL_EXT_swap_control")):
      result = 0
      if _View.Conf.fSync:
        if pyglet.gl.wglext_arb.wglSwapIntervalEXT(1):
          result = 1
  return result

# ---------------------------------------------------------------------
def getKillKeySymbol (_symbol):
  if _symbol == pyglet.window.key.Q:
    return

# ---------------------------------------------------------------------
def setEventHandlers (_View):
  # Define general event handlers
  #
  """
  @_View.winPresent.event
  def on_draw():
    print("on_draw")
    #pyglet.clock.tick()
    _View.onDraw()
    return pyglet.event.EVENT_HANDLED
  """  


  @_View.winPresent.event
  def on_key_press(symbol, modifiers):
    if _View.winMirror:
      _View.winMirror.switch_to()
      # ...
      
    _View.winPresent.switch_to()    
    """
    if   symbol == pyglet.window.key.ESCAPE:
      _View.onKeyboard(b"\x1B", 0, 0)
      return pyglet.event.EVENT_HANDLED
    el"""
    if symbol == QDSpy_KEY_KillPresentPyglet:
      _View.onKeyboard(QDSpy_KEY_KillPresent, 0, 0)


  @_View.winPresent.event
  def on_resize(width, height):
    if _View.winMirror:
      _View.winMirror.switch_to()
      # ...
      
    _View.winPresent.switch_to()    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-_View.winWidth/2, _View.winWidth/2,
            -_View.winHeight/2, _View.winHeight/2, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    return pyglet.event.EVENT_HANDLED
    
# ---------------------------------------------------------------------
def setStandardProperties (_View):
  # Set some general OpenGL properties
  #
  if _View.winMirror:
    _View.winMirror.switch_to()
    # ...
    
  _View.winPresent.switch_to()    
  glClearColor(0., 0., 0., 0.)
  glClear(GL_COLOR_BUFFER_BIT)
  glColor3f(1., 1., 1.)
  glDisable(GL_DEPTH_TEST)
  glEnable(GL_BLEND)
  glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
  """
  glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
  glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
  """
  """
  glShadeModel(GL_FLAT) # GL_FLAT or GL_SMOOTH
  glEnable(GL_POINT_SMOOTH)
  """
  
# ---------------------------------------------------------------------
def clearScreen (_View, _RGB=[]):
  # Clear screen; change background color, if requested
  #
  if _View.winMirror:
    _View.winMirror.switch_to()
    # ...
    
  _View.winPresent.switch_to()    
  if len(_RGB) == 3:
    glClearColor(_RGB[0]/255.0, _RGB[1]/255.0, _RGB[2]/255.0, 0.0)
  else:
    glClear(GL_COLOR_BUFFER_BIT)

# ---------------------------------------------------------------------
def present (_View):
  # Swap display buffers to display new frame
  #
  pyglet.clock.tick()
  """
  for iWin, window in enumerate(pyglet.app.windows):
    window.switch_to()
    window.dispatch_events()
    #window.dispatch_event('on_draw')
    window.flip()

  if _View.winMirror:
    _View.winMirror.switch_to()
    # ...
  _View.winPresent.switch_to()    
  """ 
  _View.winPresent.dispatch_events()
  _View.winPresent.flip()
  glLoadIdentity()
  glBegin(GL_POINTS)
  glColor4f(0, 0, 0, 0)
  glVertex2i(10, 10)
  glEnd()
  glFinish()

# ---------------------------------------------------------------------
def startMainLoop (_Pre):
  # Starts the main application loop
  #
  while not(_Pre.isEnd):
    _Pre.onDraw()

# ---------------------------------------------------------------------
def endMainLoop(_View):
  # End the main loop and destroy windows
  #
  _View.winPresent.close()
  
# ---------------------------------------------------------------------





