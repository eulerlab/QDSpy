#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QDSpy module - stimulus script API

This is a simple Python software for scripting and presenting stimuli
for visual neuroscience. It is based on QDS, currently uses OpenGL via
pyglet for graphics. It primarly targets Windows, but may also run on
other operating systems

Copyright (c) 2013-2024 Thomas Euler
All rights reserved.

2022-08-03 - Adapt to LINUX
2024-06-15 - Small fixes for PEP violations  
2024-07-12 - Detect user abort by Ctrl-C 
"""
# ---------------------------------------------------------------------
__author__ 	= "code@eulerlab.de"

import os
import time
import sys
from   datetime import datetime
import QDSpy_checks
import QDSpy_global as glo
import QDSpy_stim as stm
import QDSpy_stim_support as ssp
import QDSpy_config as cfg
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

PLATFORM_WINDOWS = sys.platform == "win32"
if not PLATFORM_WINDOWS:
  WindowsError = FileNotFoundError

# ---------------------------------------------------------------------
_Stim   = stm.Stim()

# ---------------------------------------------------------------------
def Initialize(_sName="noname", _sDescr="nodescription", _runMode=1):
  """ Initializes the QDS library. Needs to be called **before** any 
  other QDS command is used.

  =============== ==================================================
  Parameters:
  =============== ==================================================
  _sName          | stimulus name
  _sDescr         | description of stimulus (optional)
  _runMode        | 0=just re-compile,
                  | 1=run stimulus if script unchanged
  =============== ==================================================
  """
  _Stim.clear()
  _Stim.nameStr = _sName
  _Stim.descrStr = _sDescr
  _Stim.ErrC = stm.StimErrC.ok
  _Stim.tStart = time.time()
  _Stim.isRunSect = False
  _Stim.Conf = cfg.Config()

  # Parse command-line arguments
  fName = (os.path.splitext(os.path.basename(sys.argv[0])))[0]
  fNameOnlyDir = os.path.dirname(sys.argv[0])
  s = fNameOnlyDir +"/" +fName
  s = s if len(fNameOnlyDir) > 0 or PLATFORM_WINDOWS else s[1:]
  _Stim.fNameDir = s
  fNameDir_py = _Stim.fNameDir +".py"
  fNameDir_pk = _Stim.fNameDir +".pickle"
  args = cfg.getParsedArgv()
  
  # Display startup message and return if running the up-to-date stimulus
  # immediately is not requested
  ssp.Log.write(
      "***", glo.QDSpy_versionStr +
      " Compiler - " +glo.QDSpy_copyrightStr
    )
  ssp.Log.write(" ", "Initializing ...")
  if _runMode == 0:
    return

  # Check if pickle-file is current, if so, run the stimulus without
  # recompiling
  tLastUpt_py = datetime.fromtimestamp(os.path.getmtime(fNameDir_py))
  try:
    if os.path.isfile(fNameDir_pk):
      tLastUpt_pick = datetime.fromtimestamp(os.path.getmtime(fNameDir_pk))
      if tLastUpt_pick > tLastUpt_py and not args.compile:
        pythonPath = glo.getQDSpyPath()
        if len(pythonPath) > 0:
          pythonPath += "\\" if PLATFORM_WINDOWS else "/"
        
        ssp.Log.write("INFO", "Script has not changed, running stimulus now ...")
        s = "python {0}QDSpy_core.py -t={1} {2} {3}"
        os.system(s.format(
            pythonPath,
            args.timing, "-v" if args.verbose else "",
            _Stim.fNameDir)
          )
        '''
        os.system(s.format(
            pythonPath if PLATFORM_WINDOWS else "",
            args.timing, "-v" if args.verbose else "",
            fName if PLATFORM_WINDOWS else _Stim.fNameDir)
          )
        '''  
        exit()

  except KeyboardInterrupt:
    ssp.Log.write("INFO", "User abort.")
    sys.exit()
  
# ---------------------------------------------------------------------
def GetDefaultRefreshRate():
  """ Returns the refresh rate (in Hz) defined in the QDS configuration 
  files.
  """
  _Stage = cfg.Config().createStageFromConfig()
  return _Stage.scrReqFreq_Hz

# ---------------------------------------------------------------------
def GetStimulusPath():
  """ Returns the current path of the stimulus folder. Use this function
  to make sure that the script can locate user-provided accessory files
  (e.g. a random number series for a noise stimulus):

  .. code-block:: python

    path = QDS.getStimulusPath()
    file = open(path +"/parameters.txt", "r")
  """
  return os.path.split(os.path.abspath(_Stim.fNameDir))[0]

# ---------------------------------------------------------------------
def GetRandom(_seed):
  """ Returns a random number in the interval [0, 1) at runtime using
  the random.random() function.

  =============== ==================================================
  Parameters:
  =============== ==================================================
  _seed           | 'None' or an integer value (see random.seed()
                  | for more information)
  =============== ==================================================
  """
  try:
    _Stim.getRandom(_seed)

  except stm.StimException as e:
    ssp.Log.write("ERROR", "GetRandom: {0}, {1}".format(e.value, e))
  return _Stim.LastErrC

# ---------------------------------------------------------------------
def LogUserParameters(_dict):
  """ Writes a user-defined set of parameters to the history and log 
  file.

  =============== ==================================================
  Parameters:
  =============== ==================================================
  _dict           | dictionary with parameters
                  | as key-value pairs
  =============== ==================================================

  Example for such a user parameter entry as it appears in the history
  and log file:

  .. code-block:: python

    20151220_135948    DATA {'nTrials': 1, 'dxStim_um': 1000}
  """
  try:
    _Stim.logUserParameters(_dict)

  except stm.StimException as e:
    ssp.Log.write("ERROR", "logUserParameters: {0}, {1}".format(e.value, e))
  return _Stim.LastErrC

# ---------------------------------------------------------------------
def SetColorLUTEntry (_index, _rgb):
  """ Redefines an entry in the colour lookup table (LUT), allowing to 
  linearize the intensity range of a display.

  Note that it alters the gamma LUT at **run-time**
  (see section :doc:`how_QDSpy_works`) on the operation system-side, that is
  for *all* connected display devices, including the screen that shows the
  GUI.

  When the program ends, a linear gamma LUT will be automatically restored.

  While this adjustment is completely independent of the color mode setting
  (see :py:func:`QDS.setColorMode`), it is only meaningful for color modes
  0 and 1, and not for special lightcrafter modes. Therefore, LUT corrections
  will not be applied to stimuli using color modes >1.

  =============== ==================================================
  Parameters:
  =============== ==================================================
  _index          | LUT index, 0..255
  _rgb            | new LUT entries as tuple (r, g, b)
                  | with r,g,b in 0..255
  =============== ==================================================
  """
  try:
    _Stim.setColorLUTEntry(_index, _rgb)

  except stm.StimException as e:
    ssp.Log.write("ERROR", "LUT_changeEntry(Ex): {0}, {1}".format(e.value, e))
  return _Stim.LastErrC

# ---------------------------------------------------------------------
def SetColorMode(_depth_bit, _shift_bit=(0,0,0),
                 _mode=stm.ColorMode.range0_255):
  """ Set color mode and bit depth as well as bit offset.

  .. note:: Note that this conversion happens at **compile-time**
            (see section :doc:`how_QDSpy_works`). Changing the mode requires
            recompilation of the script to affect presentation.

  Bit depth and offset each are defined by color (as (r,b,b) tuple). All
  color values are scaled by the given bit depth and then bitwise left-
  shifted by the given offset. For example, when color mode is 0..255
  (see below), "red" is scaled:

  .. code-block:: python

    r_new = (r/255 x(2^BitDepth_r -1)) << BitShift_r

  =============== ==================================================
  Parameters:
  =============== ==================================================
  _depth_bit      | bit depth as tuple (dr, bg, bb)
  _shift_bit      | bit offsets are tuple (or, og, ob)
  _mode           | 0=color in "gun" values, 0..255
                  | 1=color as fraction, 0..1
                  | 2=LightCrafter mode B9G9
  =============== ==================================================

  **LightCrafter modes (EXPERIMENTAL)**

  (here, _depth_bit and _shift_bit are ignored.)

  * Mode B9G9: black+8 grey levels for green and blue LEDs (dichromatic), with
    blanks (=red LED) for laser-scanning (700 us LED +1400 us blank),
    8 lines (=16.667 ms) per stimulus frame (=60 Hz)
  * ...

  """
  if isinstance(_depth_bit, tuple) and len(_depth_bit) == 3:
    _Stim.bitDepth  = _depth_bit

  if isinstance(_shift_bit, tuple) and len(_shift_bit) == 3:
    _Stim.bitShift  = _shift_bit

  if _mode in [stm.ColorMode.range0_255, stm.ColorMode.range0_1,
               stm.ColorMode.LC_G9B9]:
    _Stim.colorMode = _mode

# ---------------------------------------------------------------------
def StartScript():
  """ Start of the stimulus run section. No definitions are allowed after
  this command. Must be called before QDS commands that generate stimulus 
  scenes are called.
  """
  # ...
  ssp.Log.write("ok", "{0} object(s) defined.".format(len(_Stim.ObjList)))
  ssp.Log.write("ok", "{0} shader(s) defined.".format(len(_Stim.ShList)))
  ssp.Log.write(" ",   "Generating scenes ...")
  _Stim.isRunSect = True
  return

# ---------------------------------------------------------------------
def Loop(_nRepeats, _func):
  """ Loops the stimulus sequence generated by the given function.

  Note that _func is called only once and the loop is coded in the
  actual compiled stimulus; this can be used to keep compilation time
  short and reduces the copiled stimulus file size.

  =============== ==================================================
  Parameters:
  =============== ==================================================
  _nRepeats       | >0 number of repeats, <0 indefinitely
  _func           | python function that scripts a stimulus
  =============== ==================================================
  """
  _Stim.loopBegin(_nRepeats)
  _func()
  _Stim.loopEnd()
  return

# ---------------------------------------------------------------------
def EndScript():
  """ Must be called after all stimulus scenes have been created, i.e.
  at the end of the script.
  """
  ssp.Log.write("ok", "{0} scene(s) defined.".format(_Stim.nSce))

  # Compile stimulus
  _Conf  = cfg.Config()
  _Stage = _Conf.createStageFromConfig()
  _Stim.compile(_Stage)

  # Save compiled stimulus code to a pickle file
  """
  sPath         = os.path.basename(main.__file__)
  sFName, sFExt = os.path.splitext(sPath)
  """
  _Stim.save(_Stim.fNameDir)

  ssp.Log.write("ok", "... done in {0:.3f} s"
                .format(time.time() -_Stim.tStart))

# ---------------------------------------------------------------------
def DefObj_BoxEx(_iobj, _dx, _dy, _enShader=0):
  """ Defines a box object and if shaders can be used for this object.

  =============== ==================================================
  Parameters:
  =============== ==================================================
  _iobj           | object index
  _dx,_dy         | box width and height in µm
  _enShader       | 0=disable shaders (default)
                  | 1=disable shaders,
                  | see :py:func:`QDS.SetObjShader`
  =============== ==================================================
  """
  try:
    if _Stim.isRunSect:
      _Stim.LastErrC = stm.StimErrC.noDefsInRunSection
      raise stm
    if len(_Stim.ObjList) == 0:
      ssp.Log.write(" ", "Defining objects ...")

    _Stim.defObj_box(_iobj, _dx, _dy, _enShader)

  except stm.StimException as e:
    ssp.Log.write("ERROR", "DefObj_Box(Ex): {0}, {1}".format(e.value, e))
  return _Stim.LastErrC

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def DefObj_Box(_iobj, _dx, _dy, _angle=0.0):
  """ See :py:func:`QDS.DefObj_BoxEx`

  .. note:: Note that "_angle" is depreciated and ignored in QDSpy. The
            angle of an object is now set in the render command.
  """
  if _angle != 0:
    ssp.Log.write("WARNING", "DefObj_Box: 'angle' is depreciated")
  DefObj_BoxEx(_iobj, _dx, _dy, 0)


# ---------------------------------------------------------------------
def DefObj_SectorEx(_iobj, _r, _offs, _angle, _awidth, _astep=None,
                    _enShader=0):
  """ Defines a sector object and if shaders can be used for this object.

  =============== ==================================================
  Parameters:
  =============== ==================================================
  _iobj           | object index
  _r              | outer radius (of disk) in um
  _offs           | inner radius (=radius of center "hole")
                  | in um (0 ≤ offs < r)
  _angle          | rotation angle in degrees
                  | (of the center of the arc)
  _awidth         | width of sector
                  | (angle, in degrees)
  _astep          | "smoothness" of the arc
                  | (1° <= _astep <= 90)
                  | if omitted, _astep is automatically optimized
  _enShader       | 0=disable shaders (default)
                  | 1=disable shaders,
                  | see :py:func:`QDS.SetObjShader`
  =============== ==================================================
  """
  if len(_Stim.ObjList) == 0:
    ssp.Log.write(" ", "Defining objects ...")

  try:
    _Stim.defObj_sector(_iobj, _r, _offs, _angle, _awidth, _astep,
                        _enShader)

  except stm.StimException as e:
    ssp.Log.write("ERROR", "DefObj_Sector(Ex): {0}, {1}".format(e.value, e))
  return _Stim.LastErrC

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def DefObj_Sector(_iobj, _r, _offs, _angle, _awidth, _astep=None):
  """ See :py:func:`QDS.DefObj_SectorEx`
  """
  DefObj_SectorEx(_iobj, _r, _offs, _angle, _awidth, _astep, 0)


# ---------------------------------------------------------------------
def DefObj_EllipseEx(_iobj, _dx, _dy, _enShader=0):
  """ Defines an ellipse object.

  =============== ==================================================
  Parameters:
  =============== ==================================================
  _iobj           | object index
  _dx,_dy         | ellipse diameters in µm
  _enShader       | 0=disable shaders (default)
                  | 1=disable shaders,
                  | see :py:func:`QDS.SetObjShader`
  =============== ==================================================
  """
  if len(_Stim.ObjList) == 0:
    ssp.Log.write(" ", "Defining objects ...")

  try:
    _Stim.defObj_ellipse(_iobj, _dx, _dy, _enShader)

  except stm.StimException as e:
    ssp.Log.write("ERROR", "DefObj_Ellipse: {0}, {1}".format(e.value, e))
  return _Stim.LastErrC

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def DefObj_Ellipse(_iobj, _dx, _dy, _angle=0.0):
  """ See :py:func:`QDS.DefObj_EllipseEx`

  .. note:: Note that "_angle" is depreciated and ignored in QDSpy. The
            angle of an object is now set in the render command.
  """
  if _angle != 0:
    ssp.Log.write("WARNING", "DefObj_Ellipse: 'angle' is depreciated")
  DefObj_EllipseEx(_iobj, _dx, _dy, 0)


# ---------------------------------------------------------------------
def DefObj_Movie(_iobj, _fName):
  """ Defines and loads a movie object.

  A movie object consists of two files that have the same name but
  different extensions: a text file (.txt) that describes the dimensions
  of a frame and the number of frames, and an image file that contains
  a montage of all frames (.png, .jpg, ...).

  .. note:: In contrast to QDS, QDSpy considers the **bottom-left frame of
            a montage the first frame** (in QDS it was to top-left frame).
            Therefore, movie montage files have to be adapted. This can
            be easily done in ImageJ:

            1) load the montage into ImageJ
            2) use `Image/Stacks/Tools/Montage To Stack...` to convert the
               montage into a stack
            3) use `Image/Transform/Flip Vertically` to mirror the stack
               along the x axis
            4) use `Image/Stacks/Make Montage...` to convert the stack back
               into a montage
            5) use `Image/Transform/Flip Vertically` again now to mirror the
               montage along the x axis. Now the frame sequence starts with
               the bottom-left frame.


  =============== ==================================================
  Parameters:
  =============== ==================================================
  _iobj           | object index
  _fName          | string with movie file name
                  | (with image file extension)
  =============== ==================================================
  """
  if len(_Stim.ObjList) == 0:
    ssp.Log.write(" ", "Defining objects ...")

  try:
    _Stim.defObj_movie(_iobj, _fName)

  except stm.StimException as e:
    ssp.Log.write("ERROR", "DefObj_Movie: {0}, {1}".format(e.value, e))
  return _Stim.LastErrC

# ---------------------------------------------------------------------
def GetMovieParameters(_iobj):
  """ Returns a list with the parameters of a movie object or `None`, if
  an error occurs. The movie object must have been loaded.

  =============== ==================================================
  Parameters:
  =============== ==================================================
  _iobj           | object index
  =============== ==================================================

  =============== ==================================================
  Returns:
  =============== ==================================================
  dictionary      | "dxFr", "dyFr", and "nFr"
                  | with dx,dy the frame size in pixels,
                  | and nFr the number of frames
  =============== ==================================================
  """
  params = None
  try:
    params = _Stim.getMovieParams(_iobj)

  except stm.StimException as e:
    ssp.Log.write("ERROR", "getMovieParameters: {0}, {1}".format(e.value, e))
  return params


# ---------------------------------------------------------------------
def DefObj_Video(_iobj, _fName):
  """ Defines and loads a video object.

  A video object consists of a single file; currently the following
  video format(s) is/are allowed: .avi

  =============== ==================================================
  Parameters:
  =============== ==================================================
  _iobj           | object index
  _fName          | string with video file name
  =============== ==================================================
  """
  if len(_Stim.ObjList) == 0:
    ssp.Log.write(" ", "Defining objects ...")

  try:
    _Stim.defObj_video(_iobj, _fName)

  except stm.StimException as e:
    ssp.Log.write("ERROR", "DefObj_Video: {0}, {1}".format(e.value, e))
  return _Stim.LastErrC

# ---------------------------------------------------------------------
def GetVideoParameters(_iobj):
  """ Returns a list with the parameters of a video object. The video
  object must have been loaded.

  =============== ==================================================
  Parameters:
  =============== ==================================================
  _iobj           | object index
  =============== ==================================================

  =============== ==================================================
  Returns:
  =============== ==================================================
  dictionary      | "dxFr", "dyFr", "nFr", and "fps"
                  | with dx,dy the frame size in pixels,
                  | nFr the number of frames, and fps
                  | refresh rate in frames per second
  =============== ==================================================
  """
  try:
    params = _Stim.getVideoParams(_iobj)

  except stm.StimException as e:
    ssp.Log.write("ERROR", "getVideoParams: {0}, {1}".format(e.value, e))
  return params

# ---------------------------------------------------------------------
def DefShader(_ishd, _shType):
  """ Defines a shader. For details, see :doc:`shaderfiles`.

  =============== ==================================================
  Parameters:
  =============== ==================================================
  _ishd           | shader index
  _shType         | string with shader type
                  | (from the shader folder)
  =============== ==================================================
  """
  try:
    if _Stim.isRunSect:
      _Stim.LastErrC = stm.StimErrC.noDefsInRunSection
      raise stm
    if len(_Stim.ObjList) == 0:
      ssp.Log.write(" ", "Defining shaders ...")

    _Stim.defShader(_ishd, _shType)

  except stm.StimException as e:
    ssp.Log.write("ERROR", "DefShader: {0}, {1}".format(e.value, e))
  return _Stim.LastErrC

# ---------------------------------------------------------------------
def SetObjColorEx(_iobjs, _ocols, _alphas=[]):
  """ Set color of object(s) (not defined for all object types).

  .. attention:: **Extended version**: Number of objects not anymore a
                 parameter - it is determined by the lenght of the object
                 index list -, and allows to define alpha (transparency)
                 values for each object.

  =============== ==================================================
  Parameters:
  =============== ==================================================
  _iobjs          | list of objects,
                  | [o1, o2, ...],
                  | with oX being valid object indices
  _ocols          | list of object colors in RGB values,
                  | [(r1,g1,b1{,u1,v1,w1}),(r2,g2,b2{,u2,v2,w2}), ...],
                  | with 0 <= r,g,b,u,v,w <= 255 and
                  | a tuple length between 3 and 6
  *_oalphas*      | *list of object alpha values, 0..255*
  =============== ==================================================

  In the parameter ``_ocols``, the values beyond ``r,g,b`` are optional;
  they are only relevant in "screen overlay mode" and otherwise ignored.

  *new or changed parameters*
  """
  try:
    if len(_alphas) == 0:
      _alphas = len(_iobjs) *[255]
    _Stim.setObjColor(_iobjs, _ocols, _alphas)

  except stm.StimException as e:
    ssp.Log.write("ERROR", "SetObjColor(Ex): {0}, {1}".format(e.value, e))
  return _Stim.LastErrC

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def SetObjColor(_nobj, _iobjs, _ocols):
  _alphas = len(_iobjs) *[255]
  SetObjColorEx(_iobjs, _ocols, _alphas)

# ---------------------------------------------------------------------
def SetObjColorAlphaByVertex(_iobjs, _oRGBAs):
  """ Set color and transparency (alpha) of object(s) by vertex
  (not defined for all object types).

  The number of objects is determined by the lenght of the object index list.
  Individual color (RGB) and alpha (A) values are expected as a tuples with 4
  elements (RGBA). For each object, a list of such RGBA tuples is expected,
  the number of tuples per object depends on the object type:

  * box, one RGBA tuple for each corner (n=4)
  * ellipse, RGBA[0]=center, RGBA[1]=circumfence, (n=2)
  * sector (actual sector), RGBA[0]=center, RGBA[1]=circumfence, (n=2)
  * sector (arc), RGBA[0]=outer, RGBA[1]=inner circumfence, (n=2)

  =============== ==================================================
  Parameters:
  =============== ==================================================
  _iobjs          | list of objects,
                  | [o1, o2, ...],
                  | with oX being valid object indices
  _oRGBAs         | list of object colors/transparency as RGBA,
                  | [o1List, o2List, ...],
                  | with o1List := [(r1,g2,b1,a1),(r2, ...), ...]
                  | and 0 <= r,g,b,a <= 255
  =============== ==================================================
  """
  try:
    _Stim.setObjColorAlphaByVertex(_iobjs, _oRGBAs)

  except stm.StimException as e:
    ssp.Log.write("ERROR", "SetObjColorAlphaByVertex: {0}, {1}"
                  .format(e.value, e))
  return _Stim.LastErrC

# ---------------------------------------------------------------------
def SetShaderParams(_ishd, _shParams):
  """ Sets or changes the parameters of a shader.

  =============== ==================================================
  Parameters:
  =============== ==================================================
  _ishd           | index of existing shader
                  | see :py:func:`QDS.DefShader`
  _shParams       | list of shader parameters,
                  | depending on shader type
  =============== ==================================================

  Parameters by shader type:

  * "SINE_WAVE_GRATING", drifting or stationary sine wave grating.
      [perLen_um, perDur_s, minRGBA, maxRGBA], with:

    - perLen_um, period length, in um
    - perDur_s, period duration, in seconds
    - minRGB, minimum color +tranparency (alpha)
    - maxRGB, maximum color +tranparency (alpha)

  * "SINE_WAVE_GRATING_MIX", like SINE_WAVE_GRATING, but in addition, the
    shader mixes the object color including transparency (RGBA) with the
    grating colours, enabling transparent shader objects.

  """
  try:
    _Stim.setShaderParams(_ishd, _shParams)

  except stm.StimException as e:
    ssp.Log.write("ERROR", "SetShaderParams: {0}, {1}".format(e.value, e))
  return _Stim.LastErrC

# ---------------------------------------------------------------------
def SetObjShader(_iobjs, _ishds):
  """ Attach shaders to the objects in the list.

  .. attention:: Other than object color, shader assignment cannot be
                 changed during the run section, that is after
                 :py:func:`QDS.StartScript` was called.

  =============== ==================================================
  Parameters:
  =============== ==================================================
  _iobjs          | list of objects,
                  | [o1, o2, ...],
                  | with oX being valid object indices
  _ishds          | list of existing shaders
                  | [s1, s2, ...],
                  | see :py:func:`QDS.DefShader`
                  | To detach a shader from an object
                  | set shader ID to -1
  =============== ==================================================
  """
  try:
    """
    if _Stim.isRunSect:
      _Stim.LastErrC = StimErrC.noShadersInRunSect
      raise(StimException(_Stim.LastErrC))
    """
    _Stim.setObjShader(_iobjs, _ishds)

  except stm.StimException as e:
    ssp.Log.write("ERROR", "SetObjShader: {0}, {1}".format(e.value, e))
  return _Stim.LastErrC

# ---------------------------------------------------------------------
def SetBkgColor(_col):
  """ Set color of background.

  =============== ==================================================
  Parameters:
  =============== ==================================================
  _col            | color in RGB values as tupple (r,g,b{,u,v,w})
  =============== ==================================================

  In the parameter ``_col``, the values beyond ``r,g,b`` are optional;
  they are only relevant in "screen overlay mode" and otherwise ignored.

  """
  try:
    _Stim.setBkgColor(_col)

  except stm.StimException as e:
    ssp.Log.write("ERROR", "SetBkgColor: {0}, {1}".format(e.value, e))
  return _Stim.LastErrC

# ---------------------------------------------------------------------
def Scene_Clear(_dur, _marker=0):
  """ Clear screen and wait.

  Enabling marker causes the display of a white square in the bottom
  left corner of the screen and/or the output of a TTL pulse via the
  DIO24 board, if installed).

  =============== ==================================================
  Parameters:
  =============== ==================================================
  _dur            | duration of scene in seconds
  _marker         | 0=no marker, 1=marker
  =============== ==================================================
  """
  try:
    _Stim.clearScene(_dur, (_marker==1))

  except stm.StimException as e:
    ssp.Log.write("ERROR", "Scene_Clear: {0}, {1}".format(e.value, e))
  return _Stim.LastErrC

# ---------------------------------------------------------------------
def Scene_RenderEx(_dur, _iobjs, _opos, _omag, _oang, _marker=0,
                   _screen=0):
  """ Draw objects and wait.

  Enabling marker causes the display of a white square in the bottom
  left corner of the screen and/or the output of a TTL pulse via the
  DIO24 board, if installed).

  .. attention:: **Extended version**: Number of objects not anymore a
                 parameter - it is determined by the lenght of the object
                 index list -, and allows to define magnification factors
                 and rotation angles for each object.

  =============== ==================================================
  Parameters:
  =============== ==================================================
  _dur            | duration of scene in seconds
  _iobjs          | object indices, as [i1, i2, ...]
  _opos           | object positions, as [(x1,y1), (x2,y2), ...]
  *_omag*         | *object magification as [(mx,my), ...]*
  *_oang*         | *object rotation angles in degree as [a1, ...]*
  _marker         | 0=no marker, 1=marker
  =============== ==================================================

  *new or changed parameters*
  """
  try:
    _Stim.renderScene(_dur, _iobjs, _opos, _omag, _oang, (_marker==1))

  except stm.StimException as e:
    ssp.Log.write("ERROR", "Scene_Render(Ex): {0}, {1}".format(e.value, e))
  return _Stim.LastErrC

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def Scene_Render(_dur, _nobjs, _iobjs, _opos, _marker=0):
  _omag   = len(_iobjs)*[(1.0, 1.0)]
  _oang   = len(_iobjs)*[0.0]
  Scene_RenderEx(_dur, _iobjs, _opos, _omag, _oang, _marker)

# ---------------------------------------------------------------------
def Start_Movie(_iobj, _opos, _seq, _omag, _trans, _oang, _screen=0):
  """ Start playing a movie object.

  =============== ==================================================
  Parameters:
  =============== ==================================================
  _iobj           | index of movie object
  _opos           | object positions, as (x1,y1)
  _seq            | sequence parameters, as
                  | [fr0, fr1, frreps, sqreps], with ...
                  | fr0=first, f1=last frame,
                  | frreps=number of frame repeats,
                  | sqreps=number of sequence repeats
  _omag           | object magification as (mx,my)
  _trans          | transparency, 0=transparent ... 255=opaque
  _oang           | object rotation angles in degree
  _screen         | 0=standard, 1=render on 2nd screen (=2nd half
                  | of wide screen) in screen overlay mode
  =============== ==================================================
  """
  try:
    _Stim.startMovie(_iobj, _opos, _seq, _omag, _trans, _oang, _screen)

  except stm.StimException as e:
    ssp.Log.write("ERROR", "Start_Movie: {0}, {1}".format(e.value, e))
  return _Stim.LastErrC

# ---------------------------------------------------------------------
def Start_Video(_iobj, _opos, _omag, _trans, _oang, _screen=0):
  """ Start playing a movie object.

  =============== ==================================================
  Parameters:
  =============== ==================================================
  _iobj           | index of movie object
  _opos           | object positions, as (x1,y1)
  _omag           | object magification as (mx,my)
  _trans          | transparency, 0=transparent ... 255=opaque
  _oang           | object rotation angles in degree
  _screen         | 0=standard, 1=render on 2nd screen (=2nd half
                  | of wide screen) in screen overlay mode
  =============== ==================================================
  """
  try:
    _Stim.startVideo(_iobj, _opos, _omag, _trans, _oang, _screen)

  except stm.StimException as e:
    ssp.Log.write("ERROR", "Start_Video: {0}, {1}".format(e.value, e))
  return _Stim.LastErrC

# =====================================================================
# Trigger-related commands
# ---------------------------------------------------------------------
def AwaitTTL():
  """ Wait for TTL signal. Returns the last error code or ``StimErrC.ok``.

  .. attention:: There is no time-out, as this would defeat
                 the purpose.

  .. attention:: Only for an Arduino board as digital I/O
                 device. Specifically, waits for the Arduino to signal
                 an event via serial USB. In the default Arduino code,
                 pin 2 waits for a **rising** signal edge.
  """
  try:
    _Stim.awaitTTL()
  except stm.StimException as e:
    ssp.Log.write("ERROR", "AwaitTTL: {0}, {1}".format(e.value, e))
  return _Stim.LastErrC

# =====================================================================
# Lightcrafter-related commands
# ---------------------------------------------------------------------
def LC_softwareReset(_devIndex):
  """ Signal the device (_devIndex) to do a software reset. This will 
  take a couple of seconds. After the reset the device is disconnected.

  =============== ==================================================
  Parameters:
  =============== ==================================================
  _devIndex       | index of device (starting with 0)
  =============== ==================================================
  """
  try:
    _Stim.processLCrCommand(stm.StimLCrCmd.softwareReset,
                            [_devIndex])
  except stm.StimException as e:
    ssp.Log.write("ERROR", "LC_softwareReset: {0}, {1}".format(e.value, e))
  return _Stim.LastErrC

# ---------------------------------------------------------------------
def LC_setInputSource(_devIndex, _source, _bitDepth):
  """ Defines the input source of the device.

  =============== ==================================================
  Parameters:
  =============== ==================================================
  _devIndex       | index of device (starting with 0)
  _source         | 0=parallel interface (PP),
                  | 1=internal test pattern,
                  | 2=Flash
                  | 3=FPD-link
  _bitDepth       | Parallel interface bit depth
                  | 0=30, 1=24, 2=20, 3=16, 4=10, 5=8 bits
  =============== ==================================================
  """
  try:
    _Stim.processLCrCommand(stm.StimLCrCmd.setInputSource,
                            [_devIndex, _source, _bitDepth])
  except stm.StimException as e:
    ssp.Log.write("ERROR", "LC_setInputSource: {0}, {1}"
                  .format(e.value, e))
  return _Stim.LastErrC

# ---------------------------------------------------------------------
def LC_setDisplayMode(_devIndex, _mode):
  """ Sets the display mode of the device.

  =============== ==================================================
  Parameters:
  =============== ==================================================
  _devIndex       | index of device (starting with 0)
  _mode           | 0=video display mode,
                  | Assumes streaming video image from the
                  | 30-bit RGB or FPD-link interface with a
                  | pixel resolution of up to 1280 × 800 up
                  | to 120 Hz.
                  | 1=Pattern display mode
                  | Assumes a 1-bit through 8-bit image with
                  | a pixel resolution of 912 × 1140 and
                  | bypasses all the image processing functions
                  | of the DLPC350.
  =============== ==================================================
  """
  try:
    """
    _Stim.processLCrCommand(stm.StimLCrCmd.setInputSource,
                            [_source, _bitDepth])
    """
    _Stim.processLCrCommand(stm.StimLCrCmd.setInputSource,
                            [_devIndex])

  except stm.StimException as e:
    ssp.Log.write("ERROR", "LC_setInputSource: {0}, {1}"
                  .format(e.value, e))
  return _Stim.LastErrC

# ---------------------------------------------------------------------
def LC_setLEDCurrents(_devIndex, _rgb):
  """ Sets the current of the LEDs.

  =============== ==================================================
  Parameters:
  =============== ==================================================
  _devIndex       | index of device (starting with 0)
  _rgb            | currents as a list [r,g,b]
                  | with 0 <= r,g,b <= 255
  =============== ==================================================
  """
  try:
    _Stim.processLCrCommand(stm.StimLCrCmd.setLEDCurrents,
                            [_devIndex, _rgb])
  except stm.StimException as e:
    ssp.Log.write("ERROR", "LC_setLEDCurrents: {0}, {1}"
                  .format(e.value, e))
  return _Stim.LastErrC

# ---------------------------------------------------------------------
def LC_setLEDEnabled(_devIndex, _rgb):
  """ Enable or disable the LEDs.

  =============== ==================================================
  Parameters:
  =============== ==================================================
  _devIndex       | index of device (starting with 0)
  _rgb            | state of LEDas a list [r,g,b]
                  | with True or False
  =============== ==================================================
  """
  try:
    _Stim.processLCrCommand(stm.StimLCrCmd.setLEDEnabled,
                            [_devIndex, _rgb])
  except stm.StimException as e:
    ssp.Log.write("ERROR", "LC_setLEDEnabled: {0}, {1}"
                  .format(e.value, e))
  return _Stim.LastErrC


# ---------------------------------------------------------------------
