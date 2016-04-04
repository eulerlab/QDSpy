#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
#  QDSpy_core_GL_alter2.py
#
#  Copyright (c) 2013-2015 Thomas Euler
#  All rights reserved.
#
# ---------------------------------------------------------------------
__author__ 	= "code@eulerlab.de"

from    QDSpy_global        import *

from    OpenGL.GLUT         import *
from    OpenGL.GLU          import *
from    OpenGL.WGL          import *

import  pyglet
pyglet.options['debug_gl']  = QDSpy_doOpenGLErrorChecking
from    pyglet.gl           import *
from    pyglet.gl.gl_info   import GLInfo

if sys.platform == 'win32':
  from  win32api            import SetCursorPos

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

def getImplementationStr ():
  return "Timing     : timer-based (Pyglet)"

# ---------------------------------------------------------------------
def getScreens ():
  """
  platform = pyglet.window.get_platform()
  """
  platform = pyglet.canvas.get_platform()
  display  = platform.get_default_display()
  return display.get_screens()

# ---------------------------------------------------------------------
def getWindows (_Pre, _isFullScr):
  # Create a pyglet window
  #
  if _isFullScr:
    winPyglet = pyglet.window.Window(vsync=True, fullscreen=True,
                                     screen=_Pre.screens[_Pre.iScr],
                                     width=_Pre.winWidth, height=_Pre.winHeight,
                                     caption=QDSpy_versionStr)
  else:
    winPyglet = pyglet.window.Window(vsync=True,
                                     width=_Pre.winWidth, height=_Pre.winHeight,
                                     caption=_Pre.winTitle)
  return (winPyglet, winPyglet)

# ---------------------------------------------------------------------  
def setMouseVisible (_Pre, _visible):
  # Make mouse cursor visible/invisible
  #
  _Pre.winPresent.set_mouse_visible(_visible)
  if not(sys.platform == 'win32'):
    _Pre.winPresent.set_exclusive_mouse(not _visible)
  else:  
    if not(_visible):
      SetCursorPos((0,0))

# ---------------------------------------------------------------------
def forceVSync (_Pre):
  # Check of swap-control-extention is available and force vsync if
  # requested
  #
  result = -1
  if _Pre.Conf.isWindows:
    if(pyglet.gl.wgl_info.have_extension("WGL_EXT_swap_control")):
      result = 0
      if _Pre.Conf.fSync:
        if pyglet.gl.wglext_arb.wglSwapIntervalEXT(1):
          result = 1
  return result

# ---------------------------------------------------------------------
def getKillKeySymbol (_symbol):
  if _symbol == pyglet.window.key.Q:
    return

# ---------------------------------------------------------------------
def setEventHandlers (_Pre):
  # Define general event handlers
  #
  @_Pre.winPyglet.event
  def on_draw():
    pyglet.clock.tick()
    _Pre.onDraw()
    return pyglet.event.EVENT_HANDLED

  @_Pre.winPyglet.event
  def on_key_press(symbol, modifiers):
    """
    if   symbol == pyglet.window.key.ESCAPE:
      _Pre.onKeyboard(b"\x1B", 0, 0)
      return pyglet.event.EVENT_HANDLED
    el"""
    if symbol == QDSpy_KEY_KillPresentPyglet:
      _Pre.onKeyboard(QDSpy_KEY_KillPresent, 0, 0)

  @_Pre.winPyglet.event
  def on_resize(width, height):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-_Pre.winWidth/2, _Pre.winWidth/2,
            -_Pre.winHeight/2, _Pre.winHeight/2, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    return pyglet.event.EVENT_HANDLED

# ---------------------------------------------------------------------
def setStandardProperties (_Pre):
  # Set some general OpenGL properties
  #
  glClearColor(0., 0., 0., 0.)
  glClear(GL_COLOR_BUFFER_BIT)
  glColor3f(1., 1., 1.)
  glDisable(GL_DEPTH_TEST)
  glEnable(GL_BLEND)
  glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
  """
  glShadeModel(GL_FLAT) # GL_FLAT or GL_SMOOTH
  glEnable(GL_POINT_SMOOTH)
  """


# ---------------------------------------------------------------------
def clearScreen (_RGB=[]):
  # Clear screen; change background color, if requested
  #
  if len(_RGB) == 3:
    glClearColor(_RGB[0]/255.0, _RGB[1]/255.0, _RGB[2]/255.0, 0.0)
  else:
    glClear(GL_COLOR_BUFFER_BIT)

# ---------------------------------------------------------------------
def drawCurrentBatch (_Pre):
  # Draw current batch of vertices, acknowledging the scaling and
  # rotation of the current display
  #
  glPushMatrix()
  glScalef(_Pre.Stage.scalX_umPerPix, _Pre.Stage.scalY_umPerPix, 0.0)
  glRotatef(_Pre.Stage.rot_angle, 0, 0, 1)
  glTranslatef(_Pre.Stage.centOffX_pix, _Pre.Stage.centOffY_pix, 0)
  _Pre.currBatch.draw()
  glPopMatrix()

# ---------------------------------------------------------------------
def present (_View):
  # Swap display buffers to display new frame
  # => when timer based, nothing to do
  pass

# ---------------------------------------------------------------------
def startMainLoop (_Pre):
  # Starts the main application loop
  #
  pyglet.clock.schedule_interval(_Pre.onUpdate, 1/_Pre.Stage.rFreq_Hz)
  pyglet.app.run()

# ---------------------------------------------------------------------
def endMainLoop(_View):
  # End the main loop and destroy windows
  #
  _View.winPyglet.close()

# ---------------------------------------------------------------------





