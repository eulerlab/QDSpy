#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Graphics-API dependent classes for rendering visual stimuli in QDSpy

'Renderer'
  A class for initializing the graphics system (currently OpenGL via
  pyglet) and manages the windows.
  A local instance should be used to inquire about the graphics
  systems, number of screens, screen size etc. But only one global
  instance must for managing the windows.

'Window'
  A class that encapsulates the actual graphics API windows.

Copyright (c) 2013-2026 Thomas Euler
All rights reserved.

2022-08-06 - Some reformatting
2024-06-12 - Fixed a bug that prevented using the probe spot tool
           - Reformatted (using Ruff)
           - Fixed a bug when using `pyglet` higher than v1.5.7
2024-08-04 - Helper functions for `QDSpy_stim_movie.py` added to remove
             direct calls to `pyglet`  in that module
2025-04-03 - Added the option to apply a "distortion" fragment shader
             to the whole stimulus
2025-06-01 - Catch error generating 3D texture in RPi5 (image size?)
2026-09-23 - Ported from `pyglet` 1.5.x to 2.x. `pyglet` 2.x dropped the
             legacy fixed-function OpenGL pipeline (matrix stack,
             immediate mode, `Batch.add`/`add_indexed`), so the stage
             transform is now computed explicitly as a `pyglet.math.Mat4`
             and fed as an `mvp` uniform to the flat-color batch shader
             and to every bound per-object (`.cl`) shader; `pyglet.canvas`
             renamed to `pyglet.display`; sprites now need a 3D position
             and no longer take a `usage` hint
"""
# ---------------------------------------------------------------------
__author__ = "code@eulerlab.de"

import sys
import ctypes
import math
import platform
import pyglet
import numpy as np
import pyglet.gl as GL
from pyglet.gl.gl_info import GLInfo
from pyglet.image import ImageData
from pyglet.graphics.shader import Shader as PygletShader, ShaderProgram
from pyglet.math import Mat4, Vec3

pyglet.options["debug_gl"] = False
PYGLET_VER = float(pyglet.version[0:3])

PLATFORM_WINDOWS = platform.system() == "Windows"
if PLATFORM_WINDOWS:
    from win32api import SetCursorPos # type: ignore

# ---------------------------------------------------------------------
timing_implementation_str = "vsync-based (pyglet calls)"

VERT_VERT = 0
VERT_INDICES = 1
VERT_RGBA = 2
VERT_COUNT = 3

MODE_TRIANGLE = GL.GL_TRIANGLES

# ---------------------------------------------------------------------
class RendererException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

# =====================================================================
# Renderer class
# ---------------------------------------------------------------------
class Renderer:
    """ Initializes the graphics API and manages the windows
    """
    def __init__(
            self, _View :object =None,
            _KeysExit :list =[ord(b"Q"), ord(b"q")],
        ):
        """ Initialize graphics API
        """
        # Determine some system properties
        display = pyglet.display.get_display()
        self.Screens = display.get_screens()
        self.winList = []
        self.View = _View
        self.iRecWin = -1
        self.bufMan = None
        self.isReady = True
        self.keysExit = _KeysExit
        self.isFirst = True

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def get_info_renderer_str(self) -> str:
        if not self.isReady:
            sMsg = ""
        else:
            info = GLInfo()
            info.set_active_context()
            sMsg = "Renderer   : " + info.get_renderer() + " by "
            sMsg += info.get_vendor()
        return sMsg


    def get_info_GL_str(self) -> str:
        if not self.isReady:
            sMsg = ""
        else:
            info = GLInfo()
            info.set_active_context()
            sMsg = "OpenGL     : v" + info.get_version_string()
        return sMsg


    def get_info_GLSL_str(self) -> str:
        if not self.isReady:
            sMsg = ""
        else:
            val = GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION)
            sMsg = "GLSL       : v" + ctypes.string_at(val).decode()
        return sMsg


    def get_implementation_str(self) -> str:
        return "Timing     : " + timing_implementation_str


    def get_screen_count(self) -> int:
        return len(self.Screens)


    def get_info_screen_str(self) -> str:
        return "screen={0}".format(self.Screens)


    def get_screen_size(self, _iScr) -> list:
        if _iScr < 0 or _iScr >= len(self.Screens):
            return (0, 0)
        else:
            return self.Screens[_iScr].width, self.Screens[_iScr].height


    def get_screen_depth(self, _iScr) -> list:
        if _iScr >= 0 and _iScr < len(self.Screens):
            mode = self.Screens[_iScr].get_mode()
            if mode:
                return mode.depth
        return 0


    def get_screen_refresh(self, _iScr) -> float:
        if _iScr >= 0 and _iScr < len(self.Screens):
            mode = self.Screens[_iScr].get_mode()
            if mode:
                return mode.rate
        return 0

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def force_vSync(self) -> int:
        """ Force VSync
            Check of swap-control-extention is available and force vsync,
            if requested
        """
        result = -1
        if self.isReady:
            if PLATFORM_WINDOWS:
                if GL.wgl_info.have_extension("WGL_EXT_swap_control"):
                    result = 0
                    if self.View and self.View.Conf.fSync:
                        if GL.wglext_arb.wglSwapIntervalEXT(1):
                            result = 1
        return result

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def create_window(
            self, _iScr :int =0, _title :str ="",
            _dx :int =0, _dy :int =0, _left :int =0, _top :int =0,
            _scale :float =1.0,
            _isScrOvl :bool =False, _iScrGUI :int =0,
            _offset :tuple =(0, 0),
        ) -> object:
        """ Create window
            If the renderer was initialized, create a window instance and
            store it in the internal window list. For parameters, see
            Window class.
        """
        if self.isReady:
            self.winList.append(
                Window(
                    self, _iScr, _title, _dx, _dy, _left, _top, _scale,
                    _isScrOvl, _iScrGUI, _offset,
                )
            )
            GL.glClearColor(0.0, 0.0, 0.0, 0.0)
            GL.glDisable(GL.GL_DEPTH_TEST)
            GL.glEnable(GL.GL_BLEND)
            GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

            return self.winList[-1]
        else:
            return None

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def clear_windows(self, _RGB :list =[]):
        """ Clear all windows
        """
        for win in pyglet.app.windows:
            win.switch_to()
            win.clear(_RGB)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def present(self, flip :bool =True):
        """ Swap display buffers to display new frame in multiple windows
        """
        pyglet.clock.tick(poll=True)
        for win in pyglet.app.windows:
            win.switch_to()
            if len(pyglet.app.windows) == 1:
                win.dispatch_events()
            if flip:
                win.flip()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def start_main_loop(self, _Pre :object):
        """ Starts the main application loop
        """
        while not _Pre.isEnd:
            _Pre.onDraw()


    def end_main_loop(self):
        """ End the main loop and destroy windows
        """
        for win in list(pyglet.app.windows):
            win.switch_to()
            win.set_mouse_visible(True)
            win.close()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def prepare_record_win(self):
        """ Prepare grabbing of window content for a recording of the stimulus
        """
        self.bufMan = pyglet.image.get_buffer_manager()


    def grab_frame(self) -> ImageData:
        """ Grabe current stimulus frame
        """
        colBuf = self.bufMan.get_color_buffer()
        image = colBuf.get_image_data()
        return image

# =====================================================================
#
# ---------------------------------------------------------------------
class Window(pyglet.window.Window):
    """ Window class
        Encapsulates the actual graphics API windows
    """
    def __init__(
            self, _Renderer, _iScr, _title,
            _dx, _dy, _left, _top, _scale, _isScrOvl, _iScrGUI,
            _offset,
        ):
        """ Generate new window
            _Renderer  := reference of Renderer instance
            _iScr      := index of screen (only for full-screen)
            _title     := title string
            _dx,_dy    := window size in pixels or (0,0) for
                          full-screen
            _left,_top := coordinates of top-left corner in pixels
            _isScrOvl  := if True, generates an large window across
                          two devices
            _iScrGUI   := index of GUI screen
            _offset    := additional x-y offset to correct large
                          window position (in pixels)
        """
        self.isPresent = not (_scale < 1.0)
        # Note: pyglet 2.x's own `Window` class now defines a read-only
        # `scale` property (DPI scaling), so QDSpy's window-scale factor
        # is kept under its own name to avoid the collision
        self.winScale = _scale
        self.bufferMan = None
        self.Renderer = _Renderer
        self.isFullScr = _isScrOvl or ((_dx == 0) or (_dy == 0))
        self.isScrOvl = _isScrOvl
        self.Scr2Vert = ()

        # TODO: Calculate top left positions of all screens

        if self.isFullScr and self.isPresent:
            if _isScrOvl:
                # Screen overlay mode
                super().__init__(
                    vsync=True, fullscreen=False,
                    width=_dx, height=_dy, caption=_title,
                    style=pyglet.window.Window.WINDOW_STYLE_BORDERLESS,
                )
                self.set_location(
                    self.Renderer.Screens[_iScrGUI].width +_offset[0],
                    _offset[1]
                )

                # Define a rectangle that covers screen 2 to be able to set the
                # background colour independently
                rect = [-_dx //4, -_dy //2, _dx //4, _dy //2]
                self.Scr2Vert = vertFromRect(rect, (0, 0), (0, 0, 0, 255))

            else:
                # Standard full-screen mode
                dx = self.Renderer.Screens[_iScr].width
                dy = self.Renderer.Screens[_iScr].height
                super().__init__(
                    vsync=True, fullscreen=True,
                    screen=self.Renderer.Screens[_iScr],
                    width=dx, height=dy, caption=_title,
                )

        else:
            # Window mode
            super().__init__(
                vsync=True, width=_dx, height=_dy, caption=_title,
                style=pyglet.window.Window.WINDOW_STYLE_BORDERLESS,
            )
            self.set_location(_left, _top)

        self.switch_to()
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        self.isReady = True

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def on_key_press(self, symbol, modifiers):
        self.switch_to()
        if self.Renderer.View and (symbol in self.Renderer.keysExit):
            self.Renderer.View.onKeyboard(symbol, 0, 0)
            return pyglet.event.EVENT_HANDLED

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def set_mouse_visible(self, _visible :bool):
        """ Toggle visibility of mouse cursor
        """
        if self.isReady:
            self.switch_to()
            super().set_mouse_visible(_visible)
            if not PLATFORM_WINDOWS:
                self.set_exclusive_mouse(not _visible)
            else:
                if not (_visible):
                    SetCursorPos((0, 0))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def clear(self, _RGB :list =[]):
        """ Clear window; change background color, if requested
        """
        self.switch_to()

        isColor = len(_RGB) > 0
        if isColor:
            RGB = [c / 255.0 for c in _RGB]
            GL.glClearColor(RGB[0], RGB[1], RGB[2], 0.0)
            GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        else:
            GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        if self.isPresent and self.isScrOvl:
            if isColor:
                RGBA2 = (_RGB[3], _RGB[4], _RGB[5], 255)
                self.Scr2Vert[VERT_RGBA] = RGBA2 * self.Scr2Vert[VERT_COUNT]

# =====================================================================
# Shared flat-color shader program
#
# Used for stimulus objects that have no per-object (`.cl`) shader
# assigned, and as a vertex-format factory for shader-enabled objects
# (their vertex data lives in a VBO built from this program; which
# actual shader executes at draw time is decided by the bound Group,
# see `NoneGroup`/`ShaderBindGroup` below). All vertex shaders that can
# end up rendering this data (this one and every `.cl` shader) agree on
# `layout(location = 0) in vec2 position` (and, where used,
# `layout(location = 1) in vec4 colors`), so the same VBO/VAO can be
# drawn by whichever shader is bound.
# ---------------------------------------------------------------------
_FLAT_VERTEX_SRC = """#version 330 core
layout(location = 0) in vec2 position;
layout(location = 1) in vec4 colors;

out vec4 vertex_colors;

uniform mat4 mvp;

void main()
{
    gl_Position = mvp * vec4(position, 0.0, 1.0);
    vertex_colors = colors;
}
"""

_FLAT_FRAGMENT_SRC = """#version 330 core
in vec4 vertex_colors;
out vec4 final_colors;

void main()
{
    final_colors = vertex_colors;
}
"""

def _createFlatShaderProgram() -> ShaderProgram:
    """ Compile and link the shared flat-color shader program
    """
    vert = PygletShader(_FLAT_VERTEX_SRC, "vertex")
    frag = PygletShader(_FLAT_FRAGMENT_SRC, "fragment")
    return ShaderProgram(vert, frag)

# ---------------------------------------------------------------------
class Batch:
    """ Encapsulates a batch of OpenGL drawing commands
    """
    def __init__(
        self, _isScrOvl :bool,
        _distort_frag :str ="", distort_vert :str =""
    ):
        """ Generate new batch
        """
        self.isScrOvl = _isScrOvl
        self.flatProgram = _createFlatShaderProgram()
        self.Batch = pyglet.graphics.Batch()
        self.BatchSpr = pyglet.graphics.Batch()
        if _isScrOvl:
            self.Batch2 = pyglet.graphics.Batch()
            self.Batch2Spr = pyglet.graphics.Batch()

        # indexed VBO, not shader-enabled objects only
        self.IV = None
        self.IV2 = None

        # list of current indexed VBOs for shader-enabled objects,
        # one VBO entry per object
        self.IVShObj = []
        self.IVShObj2 = []

        # pyglet Group object for 'currIV' VBO (shared between screen 1
        # and 2, matching the shader-object groups below)
        self.IVGr = NoneGroup(self.flatProgram)
        self.IVGr2 = self.IVGr if _isScrOvl else None

        # pyglet Group object for 'currIVShObj' VBOs
        self.IVShObjGr = {}
        self.IVShObjGr2 = {}

        # Reset shader manager
        self.shaderManager = None
        self.sprite = None

        # Small standalone (not batched) rectangle used to draw the
        # screen-2 backdrop and the marker/anti-marker overlay
        self._rectVL = self.flatProgram.vertex_list_indexed(
            4, GL.GL_TRIANGLES, (0, 1, 2, 0, 2, 3),
            position=("f", (0.0,) * 8), colors=("Bn", (0,) * 16),
        )
        self._lastProjection = Mat4()

        # Get distortion shaders if requested
        self.doDistort = False
        if len(_distort_frag) > 0 and len(distort_vert) > 0:
            self.distortProgram = self.load_distort_shader(
                distort_vert, _distort_frag
            )
            self.doDistort = True

            # Static full-screen quad (NDC space, no transform needed)
            self._distortQuadVL = self.distortProgram.vertex_list_indexed(
                4, GL.GL_TRIANGLES, (0, 1, 2, 0, 2, 3),
                position=("f", (-1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0)),
                tex_coord=("f", (0.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 1.0)),
            )

            # Prepare frame buffer and texture
            self._fbo = ctypes.c_uint()
            GL.glGenFramebuffers(1, ctypes.byref(self._fbo))

            self._fbo_texture = ctypes.c_uint()
            GL.glGenTextures(1, ctypes.byref(self._fbo_texture))

            # Initialize texture with specific size
            GL.glBindTexture(GL.GL_TEXTURE_2D, self._fbo_texture.value)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)

            # Allocate storage for texture - use a default size initially
            # (will be resized in draw())
            GL.glTexImage2D(
                GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, 1920, 1080, 0,
                GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, None
            )

            # Set up framebuffer
            GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self._fbo.value)
            GL.glFramebufferTexture2D(
                GL.GL_FRAMEBUFFER, GL.GL_COLOR_ATTACHMENT0,
                GL.GL_TEXTURE_2D, self._fbo_texture.value, 0
            )

            # Check initial setup
            status = GL.glCheckFramebufferStatus(GL.GL_FRAMEBUFFER)
            if status != GL.GL_FRAMEBUFFER_COMPLETE:
                raise RuntimeError(f"Distortion frame buffer failed ({status})")

            # Unbind
            GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)
            GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
            self._fboSize = (1920, 1080)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def set_shader_manager(self, _shMan :object):
        self.shaderManager = _shMan

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def replace_object_data(
            self, _indices :list, _tri :list, _RGBA :list, _RGBA2 :list
        ):
        """ Replace current indexed triangle vertex data in current batch
        """
        self.delete_object_data()
        nV = len(_tri) //2
        mode = GL.GL_TRIANGLES
        self.IV = self.flatProgram.vertex_list_indexed(
            nV, mode, _indices, batch=self.Batch, group=self.IVGr,
            position=("f", _tri), colors=("Bn", _RGBA),
        )
        if self.isScrOvl:
            self.IV2 = self.flatProgram.vertex_list_indexed(
                nV, mode, _indices, batch=self.Batch2, group=self.IVGr2,
                position=("f", _tri), colors=("Bn", _RGBA2),
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def replace_object_data_non_indexed(
        self, _indices, _tri, _RGBA, _RGBA2, _mode=GL.GL_TRIANGLES
    ):
        """ Replace the current vertex data in current batch
        """
        self.delete_object_data()
        nV = len(_tri) // 2
        self.IV = self.flatProgram.vertex_list(
            nV, _mode, batch=self.Batch, group=self.IVGr,
            position=("f", _tri), colors=("Bn", _RGBA),
        )
        if self.isScrOvl:
            self.IV2 = self.flatProgram.vertex_list(
                nV, _mode, batch=self.Batch2, group=self.IVGr2,
                position=("f", _tri), colors=("Bn", _RGBA2),
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def delete_object_data(self):
        if self.IV is not None:
            self.IV.delete()
            self.IV = None
        if self.isScrOvl:
            if self.IV2 is not None:
                self.IV2.delete()
                self.IV2 = None


    def replace_object_data_indices(self, _iVertTr :list):
        self.IV.indices = _iVertTr
        if self.isScrOvl:
            self.IV2.indices = _iVertTr


    def replace_object_data_vertices(self, _vertTr :list):
        self.IV.position[:] = _vertTr
        if self.isScrOvl:
            self.IV2.position[:] = _vertTr


    def replace_object_data_colors(self, _vRGBATr :list, _vRGBATr2 :list):
        self.IV.colors[:] = _vRGBATr
        if self.isScrOvl:
            self.IV2.colors[:] = _vRGBATr2

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def add_shader_object_data(
            self, _objID :int, _indices :list, _tri :list,
            _RGBA :list, _RGBA2 :list
        ):
        """ Add vertex triangle data for shader objects to current batch
        """
        self.IVShObj.append(
            self.flatProgram.vertex_list_indexed(
                len(_tri) // 2, GL.GL_TRIANGLES, _indices,
                batch=self.Batch, group=self.IVShObjGr[_objID],
                position=("f", _tri), colors=("Bn", _RGBA),
            )
        )
        if self.isScrOvl:
            self.IVShObj2.append(
                self.flatProgram.vertex_list_indexed(
                    len(_tri) // 2, GL.GL_TRIANGLES, _indices,
                    batch=self.Batch2, group=self.IVShObjGr2[_objID],
                    position=("f", _tri), colors=("Bn", _RGBA2),
                )
            )


    def delete_shader_object_data(self):
        for i in range(len(self.IVShObj)):
            self.IVShObj.pop().delete()
        if self.isScrOvl:
            for i in range(len(self.IVShObj2)):
                self.IVShObj2.pop().delete()


    def delete_shader_handles(self):
        self.IVShObjGr = {}
        if self.isScrOvl:
            self.IVShObjGr2 = {}


    def add_shader_handle(
            self, _objID :int, _shader :object =None, _shType :str =""
        ):
        if _shader is None:
            shOGr = NoneGroup(self.flatProgram, _order=_objID, _parent=CommonShaderParent)
        else:
            shOGr = ShaderBindGroup(
                _shader, _shType, _objID,
                self.shaderManager
            )
        self.IVShObjGr[_objID] = shOGr
        if self.isScrOvl:
            self.IVShObjGr2[_objID] = shOGr


    def set_shader_time(self, _objID :int, _t_s :float):
        if _objID in self.IVShObjGr:
            self.IVShObjGr[_objID].set_time(_t_s)
            if self.isScrOvl:
                self.IVShObjGr2[_objID].set_time(_t_s)


    def set_shader_time_all(self, _t_s :float):
        for key in self.IVShObjGr:
            shOGr = self.IVShObjGr[key]
            if self.isScrOvl:
                shOGr2 = self.IVShObjGr2[key]
            if shOGr.__class__ is ShaderBindGroup:
                shOGr.set_time(_t_s)
                if self.isScrOvl:
                    shOGr2.set_time(_t_s)


    def set_shader_parameters(
            self, _objID :int, _pos :list, _a_rad :float, _param :list
        ):
        if _objID in self.IVShObjGr:
            self.IVShObjGr[_objID].set_params(_pos, _a_rad, _param)
            if self.isScrOvl:
                self.IVShObjGr2[_objID].set_params(_pos, _a_rad, _param)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def winCoordToStageCoord(
            self, _Win :object, _Stage :object, _pos :list
        ) -> list:
        xScale = _Stage.scalX_umPerPix * _Stage.winXCorrFact * _Win.winScale
        yScale = _Stage.scalY_umPerPix * _Stage.winXCorrFact * _Win.winScale
        return (
            int((_pos[0] - _Win.width / 2) / xScale),
            int((_pos[1] - _Win.height / 2) / yScale),
        )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def load_distort_shader(
            self, vertex_path :str, fragment_path :str
        ) -> ShaderProgram:
        """ Load the shader for the stimulus distortion and returns
            the compiled and linked shader program
        """
        with open(vertex_path, "r") as f:
            v_src = f.read()
        with open(fragment_path, "r") as f:
            f_src = f.read()

        vert = PygletShader(v_src, "vertex")
        frag = PygletShader(f_src, "fragment")
        return ShaderProgram(vert, frag)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _setGroupMatrices(self, _mvp :Mat4, _forScreen2 :bool =False):
        """ Push the current model-view-projection matrix to the flat
            batch shader and to every currently bound per-object shader
        """
        ivGr = self.IVGr2 if _forScreen2 else self.IVGr
        grDict = self.IVShObjGr2 if _forScreen2 else self.IVShObjGr
        if ivGr is not None:
            ivGr.set_matrix(_mvp)
        for gr in grDict.values():
            gr.set_matrix(_mvp)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def draw(self, _Stage :object, _View :object, _isClear :bool =False):
        """ Draw current batch of triangle vertices, acknowledging the
            scaling and rotation of the current display (stage settings)
        """
        for iWin, win in enumerate(pyglet.app.windows):
            win.switch_to()

            xScale = _Stage.scalX_umPerPix *_Stage.winXCorrFact *win.winScale
            yScale = _Stage.scalY_umPerPix *_Stage.winXCorrFact *win.winScale
            yWin_5 = win.height //2
            xWin_5 = win.width //2
            xWin_25 = win.width //4

            assert len(win.caption) > 0, "Report to TE"

            if _Stage.useScrOvl:
                # - - - - - - - - - - - - - - - - - - - - - - - -
                # Screen overlay mode
                # (Does not currently support distortion shader)
                # - - - - - - - - - - - - - - - - - - - - - - - -
                # Draw on first (left) screen
                GL.glViewport(0, 0, win.width // 2, win.height)
                ortho = Mat4.orthogonal_projection(
                    -xWin_25 * _Stage.hFlipScr1, xWin_25 * _Stage.hFlipScr1,
                    -yWin_5 * _Stage.vFlipScr1, yWin_5 * _Stage.vFlipScr1,
                    -1, 1,
                )
                stage = _makeStageTransform(
                    _Stage.centOffX_pix, _Stage.centOffY_pix,
                    xScale, yScale, _Stage.rot_angle,
                )
                self._lastProjection = ortho
                win.projection = ortho
                win.view = stage
                self._setGroupMatrices(ortho @ stage, _forScreen2=False)
                if not _isClear:
                    self.Batch.draw()
                self.BatchSpr.draw()

                # Draw on second (right) screen
                GL.glViewport(win.width // 2, 0, win.width // 2, win.height)
                ortho2 = Mat4.orthogonal_projection(
                    -xWin_25 * _Stage.hFlipScr2, xWin_25 * _Stage.hFlipScr2,
                    -yWin_5 * _Stage.vFlipScr2, yWin_5 * _Stage.vFlipScr2,
                    -1, 1,
                )
                self._lastProjection = ortho2
                win.projection = ortho2
                self.add_rect_data(win.Scr2Vert)

                x = _Stage.centOffX_pix + _Stage.offXScr2_pix
                y = _Stage.centOffY_pix + _Stage.offYScr2_pix
                stage2 = _makeStageTransform(x, y, xScale, yScale, _Stage.rot_angle)
                win.view = stage2
                self._setGroupMatrices(ortho2 @ stage2, _forScreen2=True)
                if not _isClear:
                    self.Batch2.draw()
                self.Batch2Spr.draw()

            else:
                # - - - - - - - - - - - - - - - - - - - - - - - -
                # Single-screen / window mode
                # - - - - - - - - - - - - - - - - - - - - - - - -
                ortho = Mat4.orthogonal_projection(
                    -xWin_5, xWin_5, -yWin_5, yWin_5, -1, 1
                )
                stage = _makeStageTransform(
                    _Stage.centOffX_pix, _Stage.centOffY_pix,
                    xScale, yScale, _Stage.rot_angle,
                )
                self._lastProjection = ortho
                mvp = ortho @ stage

                if not self.doDistort:
                    win.projection = ortho
                    win.view = stage
                    self._setGroupMatrices(mvp, _forScreen2=False)
                    if not _isClear:
                        self.Batch.draw()
                    self.BatchSpr.draw()

                else:
                    # Render the scene into the off-screen framebuffer,
                    # then post-process it onto the screen with the
                    # distortion shader
                    GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self._fbo)
                    GL.glViewport(0, 0, win.width, win.height)

                    if self._fboSize != (win.width, win.height):
                        # Only (re)allocate the texture's storage when the
                        # window size actually changed. Redoing this every
                        # frame left the color attachment's content
                        # undefined right after the *previous* `glClear()`
                        # call below, so frame N's clear was wasted on
                        # storage that got replaced afterwards -- any
                        # region a frame didn't fully redraw kept showing
                        # whatever was previously in that (recycled) video
                        # memory, including remnants of an earlier stimulus
                        GL.glBindTexture(GL.GL_TEXTURE_2D, self._fbo_texture)
                        GL.glTexImage2D(
                            GL.GL_TEXTURE_2D, 0, GL.GL_RGBA,
                            win.width, win.height, 0,
                            GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, None
                        )
                        GL.glFramebufferTexture2D(
                            GL.GL_FRAMEBUFFER, GL.GL_COLOR_ATTACHMENT0,
                            GL.GL_TEXTURE_2D, self._fbo_texture, 0
                        )
                        self._fboSize = (win.width, win.height)

                    GL.glClear(GL.GL_COLOR_BUFFER_BIT)

                    win.projection = ortho
                    win.view = stage
                    self._setGroupMatrices(mvp, _forScreen2=False)
                    if not _isClear:
                        self.Batch.draw()
                    self.BatchSpr.draw()

                    # Now render to screen with post-processing
                    GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)
                    GL.glViewport(0, 0, win.width, win.height)
                    GL.glClear(GL.GL_COLOR_BUFFER_BIT)

                    GL.glActiveTexture(GL.GL_TEXTURE0)
                    GL.glBindTexture(GL.GL_TEXTURE_2D, self._fbo_texture.value)

                    self.distortProgram.use()
                    if "framebuffer_texture" in self.distortProgram.uniforms:
                        self.distortProgram["framebuffer_texture"] = 0
                    if "resolution" in self.distortProgram.uniforms:
                        self.distortProgram["resolution"] = (
                            float(win.width), float(win.height)
                        )
                    self._distortQuadVL.draw(GL.GL_TRIANGLES)
                    self.distortProgram.stop()

                    GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def add_rect_data(self, _Vert :list):
        """ Draw rectangle described by _Vert immediately (not part of
            the persistent batch), using the current (i.e. last set)
            projection and an identity view (no stage transform)
        """
        self._rectVL.position[:] = _Vert[VERT_VERT]
        self._rectVL.colors[:] = _Vert[VERT_RGBA]
        self._rectVL.indices = _Vert[VERT_INDICES]
        self.flatProgram.use()
        self.flatProgram["mvp"] = self._lastProjection
        self._rectVL.draw(GL.GL_TRIANGLES)
        self.flatProgram.stop()

# =====================================================================
#
# ---------------------------------------------------------------------
class CommonParentGroup(pyglet.graphics.Group):
    """ Parent class for all groups, based on a pyglet group
    """
    def __init__(self):
        super().__init__(order=0, parent=None)
        self.iObj = 0


class CommonShaderParentGroup(pyglet.graphics.Group):
    """ Parent class for a shader object group
    """
    def __init__(self):
        super().__init__(order=1, parent=CommonParent)

# ---------------------------------------------------------------------
CommonParent = CommonParentGroup()
CommonShaderParent = CommonShaderParentGroup()

# ---------------------------------------------------------------------
# Group that renders using the shared flat-color shader (used for
# objects without a custom `.cl` shader)
# ---------------------------------------------------------------------
class NoneGroup(pyglet.graphics.Group):
    """ Pyglet group for non-shader objects
    """
    def __init__(self, _program, _order=0, _parent=None):
        super().__init__(order=_order, parent=_parent or CommonParent)
        self.iObj = 0
        self.program = _program
        self.mvp = Mat4()

    def set_matrix(self, _mvp :Mat4):
        self.mvp = _mvp

    def set_state(self):
        self.program.use()
        self.program["mvp"] = self.mvp

    def unset_state(self):
        self.program.stop()

    # pyglet's default Group equality is structural (class, order,
    # parent), meant for a few static, reused Group singletons. QDSpy
    # instead creates a fresh Group per stimulus object on every scene
    # change, reusing the same order (the object index) each time -- with
    # structural equality, a new Group would compare equal to the (still
    # not yet pruned) previous scene's Group at that same order, and
    # pyglet would keep dispatching draws through the stale one, freezing
    # animated/parameterized shader objects after their first update. So
    # these groups use identity-based equality instead.
    def __eq__(self, other):
        return self is other

    def __hash__(self):
        return id(self)

# ---------------------------------------------------------------------
# Shader bind/unbind group
# ---------------------------------------------------------------------
class ShaderBindGroup(pyglet.graphics.Group):
    """ Pyglet group to bind/unbind shader objects
    """
    def __init__(self, _shader, _shType, _iObj, _ShMan):
        super().__init__(order=_iObj, parent=CommonShaderParent)

        self.t_s = 0.0
        self.iObj = _iObj
        self.posXY = (0, 0)
        self.xy = (0, 0)
        self.rot = 0.0
        self.mvp = Mat4()
        self.shader = _shader
        self.shType = _shType
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
        self.xy = _ObjPosXY
        self.rot = _ObjRot
        self.pVals = _paramVals


    def set_time(self, _t_s):
        self.t_s = _t_s


    def set_matrix(self, _mvp :Mat4):
        self.mvp = _mvp


    def set_state(self):
        self.shader.bind()
        self.shader.uniform_matrixf("mvp", self.mvp)
        self.shader.uniformf("time_s", self.t_s)
        self.shader.uniformf("obj_xy_rot", self.xy[0], self.xy[1], self.rot)
        for i, key in enumerate(self.pKeys):
            if self.pSize[i] == 1:
                self.shader.uniformf(self.pKeys[i], self.pVals[i])
            elif self.pSize[i] == 2:
                self.shader.uniformf(self.pKeys[i], self.pVals[i][0], self.pVals[i][1])
            elif self.pSize[i] == 3:
                self.shader.uniformf(
                    self.pKeys[i], self.pVals[i][0], self.pVals[i][1], self.pVals[i][2]
                )
            elif self.pSize[i] == 4:
                self.shader.uniformf(
                    self.pKeys[i],
                    self.pVals[i][0],
                    self.pVals[i][1],
                    self.pVals[i][2],
                    self.pVals[i][3],
                )


    def unset_state(self):
        self.shader.unbind()

    # See `NoneGroup.__eq__` -- identity-based equality so a new scene's
    # Group is never aliased to the previous scene's (same-order) one.
    def __eq__(self, other):
        return self is other

    def __hash__(self):
        return id(self)

# ---------------------------------------------------------------------
# Support functions
# ---------------------------------------------------------------------
def _makeStageTransform(
        _x :float, _y :float, _xScale :float, _yScale :float, _rot_deg :float
    ) -> Mat4:
    """ Combined translate/scale/rotate transform matrix, replacing the
        `glTranslatef`/`glScalef`/`glRotatef` sequence of the legacy
        fixed-function pipeline (rotate, then scale, then translate)
    """
    T = Mat4.from_translation(Vec3(_x, _y, 0.0))
    S = Mat4.from_scale(Vec3(_xScale, _yScale, 1.0))
    R = Mat4.from_rotation(math.radians(_rot_deg), Vec3(0.0, 0.0, 1.0))
    return T @ S @ R

# ---------------------------------------------------------------------
def vertFromRect(
        _rect :list, _pos :list, _RGBA :list, _angle :float =0
    ) -> list:
    """ Generates vertex data for a rectangle
    """
    newVert = [
        _rect[0],
        _rect[1],
        _rect[2],
        _rect[1],
        _rect[2],
        _rect[3],
        _rect[0],
        _rect[3],
    ]
    newVert = rotateTranslate(newVert, _angle, _pos)
    newVert = [int(v) for v in newVert]
    newiVTr = (0, 1, 2, 0, 2, 3)
    nVert = len(newVert) //2
    newRGBA = _RGBA *nVert
    return [newVert, newiVTr, newRGBA, nVert]

# ---------------------------------------------------------------------
def rotateTranslate(_c :list, _rot_deg :float, _pxy :list) -> list:
    """ Rotate and translate
        Rotate the coordinates in the list ([x1,y1,x2,y2, ...]) by the
        given angle and then translates the coordinates to the given
        position
    """
    nc = []
    a_rad = np.radians(_rot_deg)
    for i in range(0, len(_c), 2):
        x = _c[i] * np.cos(a_rad) + _c[i + 1] * np.sin(a_rad) + _pxy[0]
        y = -_c[i] * np.sin(a_rad) + _c[i + 1] * np.cos(a_rad) + _pxy[1]
        nc += [x, y]
    return nc

# ---------------------------------------------------------------------
# Support functions related to QDSpy "movies"
# ---------------------------------------------------------------------
def imageLoad(fName):
    return pyglet.image.load(fName)

def getImageData(dx, dy, img_format, data_as_str, pitch):
    return pyglet.image.ImageData(
        dx, dy, img_format, data_as_str, pitch
    )

def getImageGrid(img, nx, ny):
    return pyglet.image.ImageGrid(img, nx, ny)

def getTextureSequence(img, use_3d=False):
    if use_3d:
        try:
            return pyglet.image.Texture3D.create_for_image_grid(img)
        except pyglet.gl.lib.GLException:
            raise RendererException(
                "`getTextureSequence`: image too large for Texture3D?"
            )
    else:
        return pyglet.image.TextureGrid(img)

def getOrderedGroup(order):
    return pyglet.graphics.Group(order=order)

def getSprite(img, usage, group):
    return pyglet.sprite.Sprite(img, group=group)

# ---------------------------------------------------------------------
