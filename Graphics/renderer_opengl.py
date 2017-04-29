#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Graphics-API dependent classes for rendering visual stimuli in QDSpy

'Renderer'  
  A class for initializing the graphics system (currently OpenGL via pyglet) 
  and manages the windows. 
  A local instance should be used to inquire about the graphics systems, 
  number of screens, screen size etc. But only one global instance must for
  managing the windows.
  
'Window' 
  A class that encapsulates the actual graphics API windows.

Copyright (c) 2013-2017 Thomas Euler
All rights reserved.
"""
# ---------------------------------------------------------------------
__author__ 	= "code@eulerlab.de"

import sys
import ctypes
import pyglet
import numpy as np
'''
import scipy
import PIL
'''
pyglet.options["debug_gl"] = True
import pyglet.gl as GL
from   pyglet.gl.gl_info import GLInfo

if sys.platform == "win32":
  from win32api import SetCursorPos
'''
from   pkgutil import iter_modules  
if "cv2" in (name for loader, name, ispkg in iter_modules()):
  import cv2
'''  

# ---------------------------------------------------------------------  
timing_implementation_str  = "vsync-based (pyglet calls)"

VERT_VERT                  = 0
VERT_INDICES               = 1
VERT_RGBA                  = 2
VERT_COUNT                 = 3

# =====================================================================
#
# ---------------------------------------------------------------------
class Renderer:
  """ Initializes the graphics API and manages the windows
  """
  def __init__(self, _View=None, _KeysExit=[ord(b'Q'), ord(b'q')]):
    # Initialize graphics API
    #
    # Determine some system properties
    #    
    platform = pyglet.window.get_platform()
    display  = platform.get_default_display()
    self.Screens  = display.get_screens()
    self.winList  = []
    self.View     = _View
    self.iRecWin  = -1
    self.bufMan   = None
    self.isReady  = True
    self.keysExit = _KeysExit
    
    self.isFirst  = True
    
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def get_info_renderer_str(self):
    if not(self.isReady):
      sMsg = ""
    else:  
      info = GLInfo()
      info.set_active_context()
      sMsg = "Renderer   : " +info.get_renderer() +" by " +info.get_vendor()
    return sMsg  

  def get_info_GL_str(self):
    if not self.isReady:
      sMsg = ""
    else:  
      info = GLInfo()
      info.set_active_context()
      sMsg = "OpenGL     : v" +info.get_version()
    return sMsg  

  def get_info_GLSL_str(self):
    if not self.isReady:
      sMsg = ""
    else:  
      val  = GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION)
      sMsg = "GLSL       : v" +ctypes.string_at(val).decode()
    return sMsg  

  def get_implementation_str(self):
    return "Timing     : " +timing_implementation_str

  def get_screen_count(self):
    return len(self.Screens)

  def get_info_screen_str(self):
    return "screen={0}".format(self.Screens)    
    
  def get_screen_size(self, _iScr):
    if _iScr < 0  or _iScr >= len(self.Screens):
      return (0, 0)
    else:
      return (self.Screens[_iScr].width, self.Screens[_iScr].height)

  def get_screen_depth(self, _iScr):
    if _iScr < 0  or _iScr >= len(self.Screens):
      return 0
    else:
      mode = self.Screens[_iScr].get_mode() 
      return mode.depth

  def get_screen_refresh(self, _iScr):
    if _iScr < 0  or _iScr >= len(self.Screens):
      return 0
    else:
      mode = self.Screens[_iScr].get_mode() 
      return mode.rate
    
    
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -        
  def force_vSync(self):
    """ Check of swap-control-extention is available and force vsync if
        requested
    """
    result = -1
    if self.isReady:
      if sys.platform == 'win32':
        if(GL.wgl_info.have_extension("WGL_EXT_swap_control")):
          result = 0
          if self.View and self.View.Conf.fSync:
            if GL.wglext_arb.wglSwapIntervalEXT(1):
              result = 1
    return result

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -        
  def create_window(self, _iScr=0, _title="", _dx=0, _dy=0, _left=0, _top=0,
                    _scale=1.0, _isScrOvl=False, _iScrGUI=0, _offset=(0,0)):
    """ If the renderer was initialized, create a window instance and store
        it in the internal window list. For parameters, see Window class.
    """
    if self.isReady:
      self.winList.append(Window(self, _iScr, _title, _dx, _dy, _left, _top,
                                 _scale, _isScrOvl, _iScrGUI, _offset))    
      '''
      if len(self.winList) == 1:
      # Is the first window, set some general OpenGL properties
      #
      '''
      GL.glClearColor(0., 0., 0., 0.)
      GL.glColor3f(1., 1., 1.)
      GL.glDisable(GL.GL_DEPTH_TEST)
      GL.glEnable(GL.GL_BLEND)
      GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
      '''
      GL.glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
      GL.glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
  
      GL.glShadeModel(GL_FLAT) # GL_FLAT or GL_SMOOTH
      GL.glEnable(GL_POINT_SMOOTH)
      '''
      return self.winList[-1]
    else:  
      return None
      
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -                  
  def clear_windows(self, _RGB=[]):
    """ Clear all windows
    """
    for win in pyglet.app.windows:     
      win.switch_to()
      win.clear(_RGB)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -        
  def present(self):
    """ Swap display buffers to display new frame in multiple windows
    """
    pyglet.clock.tick(poll=True)
    for win in pyglet.app.windows:
      win.switch_to()

      if len(pyglet.app.windows) == 1:
        win.dispatch_event("on_draw")      
        win.dispatch_events()
        
      # ******************************      
      # ******************************
      # ******************************
      '''
      if self.isFirst:
        self.isFirst = False
        self.bufMan  = pyglet.image.get_buffer_manager()
        self.pil_img_data = None
      '''  
      # ******************************      
      # ******************************      
      # ******************************      
        
      win.flip()      
      """
      if win.isPresent:
        GL.glLoadIdentity()
        GL.glBegin(GL.GL_POINTS)
        GL.glColor4f(0, 0, 0, 0)
        GL.glVertex2i(10, 10)
        GL.glEnd()
        GL.glFinish()
      """  
      # ******************************      
      # ******************************      
      # ******************************      
      """  
      if win.isPresent:  
        colBuf  = self.bufMan.get_color_buffer()
        imgData = colBuf.get_image_data()
        dx      = imgData.width
        dy      = imgData.height

        #np_img  = np.fromstring(imgData.data, np.uint8).reshape(dx, dy, 4)
        #scp_img = scipy.
        '''
        np_img2 = np.delete(np_img, np.s_[3], 2) # slow!!!
        '''
        
        #print(" def present(self)", np_img.shape)
        
        '''
        pil_img = PIL.Image.frombytes('RGBA', (dx, dy), imgData.data)
        pil_img_small = pil_img.resize((dx//2,dy//2), PIL.Image.NEAREST)
        pil_img_small2 = pil_img_small.convert("RGB")
        self.pil_img_data = pil_img_small2.tobytes()
        #print(" def present(self)", len(self.pil_img_data))
        '''
        #cv2.
        #res = cv2.resize cv2.resize(img,(2*width, 2*height), interpolation = cv2.INTER_AREA)
      """
      # ******************************      
      # ******************************      
      # ******************************      
        
  
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -        
  '''     
  def dispatch_events(self):
    pass
  '''
     
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -        
  def start_main_loop(self, _Pre):
    """ Starts the main application loop
    """
    while not(_Pre.isEnd):
      _Pre.onDraw()

  def end_main_loop(self):
    """ End the main loop and destroy windows
    """
    for win in pyglet.app.windows:     
      win.switch_to()
      win.set_mouse_visible(True)
      win.close()
      
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -                  
  def prepare_grabbing_win(self, _iWin):
    """ Prepare grabbing of window content for a recording of the stimulus
    """
    self.bufMan  = pyglet.image.get_buffer_manager()
    self.iRecWin = _iWin
    # **********************
    # **********************
    # TODO: 
    # **********************
    # **********************

  def grab_frame(self):
    """ Prepare recording of window content
    """
    # **********************
    # **********************
    # TODO:
    # something like function(image, self.nFr), containing something like
    '''
    colBuf    = self.bufMan.get_color_buffer()
    image     = colBuf.image_data.get_image_data()
    pil_image = Image.fromstring(image.format, (image.width, image.height), 
                                 image.get_data(image.format, image.pitch))
    pil_image = pil_image.transpose(Image.FLIP_TOP_BOTTOM)
    pil_image = pil_image.convert('RGB')
    pil_image.save("D:\SCRATCH\MOVIE\{0:06d}.png".format(self.nFrTotal), "PNG")
    '''
    # **********************
    # **********************
    pass

# =====================================================================
#
# ---------------------------------------------------------------------
class Window(pyglet.window.Window):
  """
  Encapsulates the actual graphics API windows
  """
  def __init__(self, _Renderer, _iScr, _title, _dx, _dy, _left, _top, _scale,
               _isScrOvl, _iScrGUI, _offset):
    """ Generate new window
          _Renderer  := reference of Renderer instance
          _iScr      := index of screen (only for full-screen)
          _title     := title string
          _dx,_dy    := window size in pixels or (0,0) for full-screen
          _left,_top := coordinates of top-left corner in pixels
          _isScrOvl  := if True, generates an large window across two devices
          _iScrGUI   := index of GUI screen
          _offset    := additional x-y offset to correct large window position
                        (in pixels)
    """  
    self.isPresent = not(_scale < 1.0)
    self.scale     = _scale
    self.bufferMan = None
    self.Renderer  = _Renderer
    self.isFullScr = _isScrOvl or ((_dx == 0) or (_dy == 0))
    self.isScrOvl  = _isScrOvl
    self.Scr2Vert  = ()

    if self.isFullScr and self.isPresent:
      if _isScrOvl:
        # Screen overlay mode
        #
        super().__init__(vsync=True, fullscreen=False,
                         width=_dx, height=_dy,
                         caption=_title,
                         style=pyglet.window.Window.WINDOW_STYLE_BORDERLESS)
        self.set_location(self.Renderer.Screens[_iScrGUI].width +_offset[0], 
                          _offset[1])     
        
        # Define a rectangle that covers screen 2 to be able to set the 
        # background colour independently
        #
        rect = [-_dx//4, -_dy//2, _dx//4, _dy//2]
        self.Scr2Vert = vertFromRect(rect, (0,0), (0,0,0,255))         
        
      else:  
        # Standard full-screen mode
        #
        super().__init__(vsync=True, fullscreen=True,
                         screen=self.Renderer.Screens[_iScr],
                         width=self.Renderer.Screens[_iScr].width, 
                         height=self.Renderer.Screens[_iScr].height,
                         caption=_title)
        
    else:
      # Window mode
      #
      super().__init__(vsync=True,
                       width=_dx, height=_dy, 
                       caption=_title,
                       style=pyglet.window.Window.WINDOW_STYLE_TOOL)
      self.set_location(_left, _top)
      
    self.switch_to()
    GL.glClear(pyglet.gl.GL_COLOR_BUFFER_BIT)
    self.isReady = True                                  
    
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -        
  def on_key_press(self, symbol, modifiers):
    self.switch_to()
    if self.Renderer.View and (symbol in self.Renderer.keysExit):
      self.Renderer.View.onKeyboard(symbol, 0, 0)
      return pyglet.event.EVENT_HANDLED

  ''' 
  def on_draw(self):
    self.switch_to()
    print("on_draw")
    return pyglet.event.EVENT_HANDLED
  '''  
    
  '''
  # *************
  # *************
  # Moved into Batch.draw(...)
  # *************
  # *************
  def on_resize(self, width, height):
    #super(Window, self).on_resize(width, height)
    self.switch_to()
    
    GL.glMatrixMode(GL.GL_PROJECTION)
    GL.glLoadIdentity()
    GL.glOrtho(-self.width//2, self.width//2, 
               -self.height//2, self.height//2, -1, 1)
    GL.glMatrixMode(GL.GL_MODELVIEW)
    GL.glLoadIdentity()
    return pyglet.event.EVENT_HANDLED
  '''  
  
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -   
  '''     
  def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers): 
    return pyglet.event.EVENT_HANDLED
    
  def on_mouse_enter(self, x, y): 
    print("enter")
    return pyglet.event.EVENT_HANDLED
    
  def on_mouse_leave(self, x, y):
    print("leave")
    return pyglet.event.EVENT_HANDLED
    
  def on_mouse_motion(self, x, y, dx, dy):
    return pyglet.event.EVENT_HANDLED
    
  def on_mouse_press(self, x, y, button, modifiers):
    return pyglet.event.EVENT_HANDLED
    
  def on_mouse_release(sef, x, y, button, modifiers):
    return pyglet.event.EVENT_HANDLED
  '''
  
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -        
  def set_mouse_visible(self, _visible):
    """ Toggle visibility of mouse cursor
    """
    if self.isReady:
      self.switch_to()
      super().set_mouse_visible(_visible)
      if not(sys.platform == 'win32'):
        self.set_exclusive_mouse(not _visible)
      else:
        if not(_visible):
          SetCursorPos((0,0))
          
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -                  
  def clear(self, _RGB=[]):
    """ Clear window; change background color, if requested
    """
    self.switch_to()    
    
    isColor = (len(_RGB) > 0)
    if isColor:
      RGB = [c/255.0 for c in _RGB]
      GL.glClearColor(RGB[0], RGB[1], RGB[2], 0.0)
      GL.glClear(GL.GL_COLOR_BUFFER_BIT)
    else:  
      GL.glClear(GL.GL_COLOR_BUFFER_BIT)
      
    if self.isPresent and self.isScrOvl:
      if isColor:
        RGBA2 = (_RGB[3], _RGB[4], _RGB[5], 255)
        self.Scr2Vert[VERT_RGBA] = RGBA2 *self.Scr2Vert[VERT_COUNT]

    '''
    if self.isPresent and self.isScrOvl:
      # Is presentation window in screen overlay mode, therefore set colour
      # of each half seperately
      #
      GL.glEnable(GL.GL_SCISSOR_TEST)
      
      GL.glScissor(0, 0, self.width//2, self.height)
      if isColor:
        GL.glClearColor(RGB[0], RGB[1], RGB[2], 0.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
      else:  
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

      #GL.glDisable(GL.GL_SCISSOR_TEST)
      #GL.glEnable(GL.GL_SCISSOR_TEST)
     
      GL.glScissor(self.width//2, 0, self.width//2, self.height)
      """
      if isColor:
        GL.glClearColor(RGB[3], RGB[4], RGB[5], 0.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
      else:  
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
      """  
      GL.glDisable(GL.GL_SCISSOR_TEST)

    else:
      # Window or standard full-screen mode, set colour normally
      #
      if isColor:
        GL.glClearColor(RGB[0], RGB[1], RGB[2], 0.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
      else:  
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
    '''  
     
# =====================================================================
#
# ---------------------------------------------------------------------
class Batch:
  """
  Encapsulates a batch of OpenGL drawing commands
  """
  def __init__(self, _isScrOvl):
    """ Generate new batch
    """  
    self.isScrOvl      = _isScrOvl
    self.Batch         = pyglet.graphics.Batch()
    self.BatchSpr      = pyglet.graphics.Batch()
    if _isScrOvl:
      self.Batch2      = pyglet.graphics.Batch()
      self.Batch2Spr   = pyglet.graphics.Batch()

    self.IV            = None # indexed VBO, not shader-enabled objects only
    self.IV2           = None
    self.IVShObj       = []   # list of current indexed VBOs for shader-
                              # enabled objects, one VBO entry per object
    self.IVShObj2      = [] 
    self.IVGr          = None # pyglet Group object for 'currIV' VBO
    self.IVGr2         = None 
    self.IVShObjGr     = {}   # pyglet Group object for 'currIVShObj' VBOs
    self.IVShObjGr2    = {}  
    
    self.shaderManager = None
    self.sprite        = None

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -                     
  def set_shader_manager(self, _shMan):
    self.shaderManager = _shMan

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -                     
  def replace_object_data(self, _indices, _tri, _RGBA, _RGBA2):
    """ Replace the current vertex triangle data in current batch
    """
    self.delete_object_data()
    self.IV = self.Batch.add_indexed(len(_tri)//2, GL.GL_TRIANGLES, 
                                     self.IVGr, _indices, 
                                     ("v2i/stream", _tri), 
                                     ("c4B/stream", _RGBA))
    if self.isScrOvl:
      self.IV2 = self.Batch2.add_indexed(len(_tri)//2, GL.GL_TRIANGLES, 
                                         self.IVGr2, _indices, 
                                         ("v2i/stream", _tri), 
                                         ("c4B/stream", _RGBA2))

  def delete_object_data(self):
    if self.IV != None:
      self.IV.delete()
      self.IV = None
    if self.isScrOvl:
      if self.IV2 != None:
        self.IV2.delete()
        self.IV2 = None


  def replace_object_data_indices(self, _iVertTr):
    self.IV.indices    = _iVertTr
    if self.isScrOvl:
      self.IV2.indices = _iVertTr

      
  def replace_object_data_vertices(self, _vertTr):
    self.IV.vertices    = _vertTr
    if self.isScrOvl:
      self.IV2.vertices = _vertTr


  def replace_object_data_colors(self, _vRGBATr, _vRGBATr2):
    self.IV.colors    = _vRGBATr
    if self.isScrOvl:
      self.IV2.colors = _vRGBATr2

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -                     
  def add_shader_object_data(self, _objID, _indices, _tri, _RGBA, _RGBA2):
    """ Add vertex triangle data for shader objects to current batch
    """
    self.IVShObj.append(
      self.Batch.add_indexed(len(_tri)//2, GL.GL_TRIANGLES, 
                             self.IVShObjGr[_objID], _indices,
                             ("v2i/stream", _tri), ("c4B/stream", _RGBA)))
    if self.isScrOvl:
      self.IVShObj2.append(
        self.Batch2.add_indexed(len(_tri)//2, GL.GL_TRIANGLES, 
                                self.IVShObjGr2[_objID], _indices,
                                ("v2i/stream", _tri), ("c4B/stream", _RGBA2)))
    
  
  def delete_shader_object_data(self):
    for i in range(len(self.IVShObj)):
      self.IVShObj.pop().delete()
    if self.isScrOvl:
      for i in range(len(self.IVShObj2)):
        self.IVShObj2.pop().delete()  
      
      
  def delete_shader_handles(self):
    self.IVShObjGr    = {}
    if self.isScrOvl:
      self.IVShObjGr2 = {}


  def add_shader_handle(self, _objID, _shader=None, _shType=""):    
    if _shader == None:   
      shOGr = NoneGroup()
    else:
      shOGr = ShaderBindGroup(_shader, _shType, _objID, self.shaderManager)
    self.IVShObjGr[_objID]   = shOGr
    if self.isScrOvl:    
      self.IVShObjGr2[_objID] = shOGr

      
  def set_shader_time(self, _objID, _t_s):
    if _objID in self.IVShObjGr:
       self.IVShObjGr[_objID].set_time(_t_s)
       if self.isScrOvl:    
         self.IVShObjGr2[_objID].set_time(_t_s)


  def set_shader_time_all(self, _t_s):
    for key in self.IVShObjGr:
      shOGr    = self.IVShObjGr[key]
      if self.isScrOvl:  
        shOGr2 = self.IVShObjGr2[key]
      if shOGr.__class__ is ShaderBindGroup:
        shOGr.set_time(_t_s)
        if self.isScrOvl:   
          shOGr2.set_time(_t_s)


  def set_shader_parameters(self, _objID, _pos, _a_rad, _param):
    if _objID in self.IVShObjGr:
      self.IVShObjGr[_objID].set_params(_pos, _a_rad, _param)
      if self.isScrOvl:  
        self.IVShObjGr2[_objID].set_params(_pos, _a_rad, _param)
      
      
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -                     
  def draw(self, _Stage, _View, _isClear=False):      
    """ Draw current batch of triangle vertices, acknowledging the scaling
        and rotation of the current display (stage settings)
    """
    for iWin, win in enumerate(pyglet.app.windows):     
      win.switch_to()

      xScale  = _Stage.scalX_umPerPix *_Stage.winXCorrFact *win.scale
      yScale  = _Stage.scalY_umPerPix *_Stage.winXCorrFact *win.scale
      yWin_5  = win.height//2
      xWin_5 = win.width//2  
      xWin_25 = win.width//4
      
      if _Stage.useScrOvl:      
        # Draw on first (left) screen
        #
        GL.glViewport(0, 0, win.width//2, win.height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(-xWin_25, xWin_25, -yWin_5, yWin_5, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glPushMatrix()
        x = _Stage.centOffX_pix 
        y = _Stage.centOffY_pix
        GL.glTranslatef(x, y, 0)
        GL.glScalef(xScale, yScale, 0.0)
        GL.glRotatef(_Stage.rot_angle, 0, 0, 1)
        if not(_isClear):
          self.Batch.draw()    
        self.BatchSpr.draw() 
        GL.glPopMatrix()

        # Draw on second (right) screen
        #
        GL.glViewport(win.width//2, 0, win.width//2, win.height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(-xWin_25, xWin_25, -yWin_5, yWin_5, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glPushMatrix()
        
        self.add_rect_data(win.Scr2Vert)
        
        x = _Stage.centOffX_pix +_Stage.offXScr2_pix
        y = _Stage.centOffY_pix +_Stage.offYScr2_pix 
        GL.glTranslatef(x, y, 0)
        GL.glScalef(xScale, yScale, 0.0)
        GL.glRotatef(_Stage.rot_angle, 0, 0, 1)
        if not(_isClear):
          self.Batch2.draw()   
        self.Batch2Spr.draw()     
        GL.glPopMatrix()
        
      else:  
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(-xWin_5, xWin_5, -yWin_5, yWin_5, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glPushMatrix()
        GL.glTranslatef(_Stage.centOffX_pix, _Stage.centOffY_pix, 0)
        GL.glScalef(xScale, yScale, 0.0)
        GL.glRotatef(_Stage.rot_angle, 0, 0, 1)
        if not(_isClear):
          self.Batch.draw()    
        self.BatchSpr.draw() 
        GL.glPopMatrix()


  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -                     
  def add_rect_data(self, _Vert):   
    """ Add rectangle described by _Vert to lined up rendering commands
    """
    pyglet.graphics.draw_indexed(_Vert[VERT_COUNT], GL.GL_TRIANGLES,
                                 _Vert[VERT_INDICES],
                                 ("v2i/stream", _Vert[VERT_VERT]),
                                 ("c4B/stream", _Vert[VERT_RGBA]))

# =====================================================================
#
# ---------------------------------------------------------------------
class CommonParentGroup(pyglet.graphics.OrderedGroup):
  """ Parent class for all groups, based on a pyglet group
  """
  def __init__(self):
    self.iObj      = 0
    self.parent    = None
    self.order     = 0

class CommonShaderParentGroup(pyglet.graphics.OrderedGroup):
  """ Parent class for a shader object group 
  """
  def __init__(self):
    super(CommonShaderParentGroup, self).__init__(order=1, parent=CommonParent)

# ---------------------------------------------------------------------
CommonParent       = CommonParentGroup()
CommonShaderParent = CommonShaderParentGroup()

# ---------------------------------------------------------------------
# Shader bind/unbind class
# ---------------------------------------------------------------------
class ShaderBindGroup(pyglet.graphics.Group):
  """ Pyglet group to bind/unbind shader objects
  """
  def __init__(self, _shader, _shType, _iObj, _ShMan):
    super(ShaderBindGroup, self).__init__(parent=CommonShaderParent)
    self.parent.order = _iObj    
    
    self.t_s     = 0.0
    self.iObj    = _iObj
    self.posXY   = (0,0)
    self.shader  = _shader
    self.shType  = _shType
    self.iShType = _ShMan.getShaderTypeIndex(_shType)
    if self.iShType >= 0:
      self.pKeys = _ShMan.ShDesc[self.iShType][1]
      self.pSize = _ShMan.ShDesc[self.iShType][2]
      self.pVals = _ShMan.getDefaultParams(self.shType)
    else:
      self.pKeys = []
      self.pSize = []
      self.pVals = []

  def set_params(self, _ObjPosXY, _ObjRot, _paramVals):
    self.xy    = _ObjPosXY
    self.rot   = _ObjRot
    self.pVals = _paramVals

  def set_time(self, _t_s):
    self.t_s   = _t_s

  def set_state(self):
    GL.glEnable(GL.GL_TEXTURE_2D)
    self.shader.bind()
    self.shader.uniformf("time_s", self.t_s)
    self.shader.uniformf("obj_xy_rot", self.xy[0], self.xy[1], self.rot)
    for i, key in enumerate(self.pKeys):
      if   self.pSize[i] == 1:
        self.shader.uniformf(self.pKeys[i], self.pVals[i])
      elif self.pSize[i] == 2: 
        self.shader.uniformf(self.pKeys[i], self.pVals[i][0], 
                             self.pVals[i][1])
      elif self.pSize[i] == 3: 
        self.shader.uniformf(self.pKeys[i], self.pVals[i][0], 
                             self.pVals[i][1], self.pVals[i][2])
      elif self.pSize[i] == 4: 
        self.shader.uniformf(self.pKeys[i], self.pVals[i][0], 
                             self.pVals[i][1], self.pVals[i][2],
                             self.pVals[i][3])

  def unset_state(self):
    GL.glDisable(GL.GL_TEXTURE_2D)
    self.shader.unbind()
  
  def __cmp__(self, other):
    if self.order < other.order:
      return -1
    elif self.order == other.order:
      return 0
    else:
      return 1

# ---------------------------------------------------------------------
class NoneGroup(pyglet.graphics.OrderedGroup):
  """ Pyglet group for non-shader objects
  """
  def __init__(self):
    super(NoneGroup, self).__init__(order=0, parent=CommonParent)
    self.iObj = 0

  def __cmp__(self, other):
    if self.order < other.order:
      return -1
    elif self.order == other.order:
      return 0
    else:
      return 1

# ---------------------------------------------------------------------
# Support functions
# ---------------------------------------------------------------------
def vertFromRect(_rect, _pos, _RGBA, _angle=0):
  """ Generates vertex data for a rectangle
  """  
  newVert = [_rect[0], _rect[1], _rect[2], _rect[1],
             _rect[2], _rect[3], _rect[0], _rect[3]]
  newVert = rotateTranslate(newVert, _angle, _pos)
  newVert = [int(v) for v in newVert]        
  newiVTr = (0, 1, 2, 0, 2, 3)
  nVert   = len(newVert)//2
  newRGBA = _RGBA *nVert
  return [newVert, newiVTr, newRGBA, nVert]

# ---------------------------------------------------------------------
def rotateTranslate(_c, _rot_deg, _pxy):
  """ Rotate the coordinates in the list ([x1,y1,x2,y2, ...]) by the
      given angle and then translates the coordinates to the given 
      position
  """
  nc    = []
  a_rad = np.radians(_rot_deg)
  for i in range(0, len(_c), 2):
    x   =  _c[i] *np.cos(a_rad) +_c[i+1] *np.sin(a_rad) +_pxy[0]
    y   = -_c[i] *np.sin(a_rad) +_c[i+1] *np.cos(a_rad) +_pxy[1]
    nc += [x, y]
  return nc


# ---------------------------------------------------------------------
