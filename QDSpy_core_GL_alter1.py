#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
#  QDSpy_core_GL_alter1.py
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
  glutInit()

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
  return "Timing     : vsync-based (direct GL calls)"

# ---------------------------------------------------------------------
def getScreens ():
  platform = pyglet.window.get_platform()
  display  = platform.get_default_display()
  return display.get_screens()

# ---------------------------------------------------------------------
def getWindows (_View, _isFullScr):
  # Create an invisible pyglet window to be able to use pyglet's
  # convinient OpenGL drawing API without having to use pyglets
  # application framework (timing is unreliable?)
  #
  if _isFullScr:
    winPyglet  = pyglet.window.Window(visible=False, vsync=True,
                                      screen=_View.screens[_View.iScr])
  else:
    winPyglet  = pyglet.window.Window(visible=False, vsync=True)

  glutInitWindowSize(_View.winWidth, _View.winHeight)
  if _isFullScr:
    # Create a fullscreen display directly; it will be the active
    # OpenGL context
    #
    winPresent = glutCreateWindow(QDSpy_versionStr)
    glutPositionWindow(_View.screens[_View.iScr].x,_View.screens[_View.iScr].y)
    if not(_View.Stage.disFScrCmd):
      glutFullScreen()
  else:
    # Create a window directly; this will be the active OpenGL context
    #
    winPresent = glutCreateWindow(_View.winTitle)

  glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
  """
  if sys.platform =='win32':
    _View._hw_handle = winPresent._view_hwnd
  """
  return (winPyglet, winPresent)

# ---------------------------------------------------------------------
def setMouseVisible (_View, _visible):
  # Make mouse cursor visible/invisible
  # ****************
  # TODO
  # ****************
  """
  _Pre.winPresent.set_mouse_visible(_visible)
  if not(sys.platform == 'win32'):
    _Pre.winPresent.set_exclusive_mouse(not _visible)
  else:
    if not(_visible):
      SetCursorPos((0,0))
  """
  pass

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
def setEventHandlers (_View):
  # Define general event handlers
  #
  glutDisplayFunc(_View.onDraw)
  glutIdleFunc(_View.onDraw)
  glutKeyboardFunc(_View.onKeyboard)
  """
  glutReshapeFunc()
  glutOnSpecialFunc()
  """

# ---------------------------------------------------------------------
def setStandardProperties (_View):
  # Set some general OpenGL properties
  #
  glClearColor(0., 0., 0., 0.)
  glClear(GL_COLOR_BUFFER_BIT)
  glColor3f(1., 1., 1.)
  glMatrixMode(GL_PROJECTION)
  glLoadIdentity()
  gluOrtho2D(-_View.winWidth/2, _View.winWidth/2,
             -_View.winHeight/2, _View.winHeight/2)
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
def present (_View):
  # Swap display buffers to display new frame
  #
  glFinish()
  glutSwapBuffers()

# ---------------------------------------------------------------------
def startMainLoop (_Pre):
  glutMainLoop()

# ---------------------------------------------------------------------
def endMainLoop(_View):
  _View.winPyglet.close()
  glutDestroyWindow(_View.winPresent)

# ---------------------------------------------------------------------





