#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QDSpy module - main program of command line-version of QDSpy

This is a simple Python software for scripting and presenting stimuli
for visual neuroscience. It is based on QDS, currently uses OpenGL via
pyglet for graphics. It primarly targets Windows, but may also run on 
other operating systems

Copyright (c) 2013-2017 Thomas Euler
All rights reserved.
"""
# ---------------------------------------------------------------------
__author__ 	= "code@eulerlab.de"

import time
import sys
import gc
import os
import subprocess
import pickle
from   multiprocessing import freeze_support
import QDSpy_global as glo
import QDSpy_stim as stm
import QDSpy_stim_support as ssp
import QDSpy_config as cnf
import QDSpy_core_presenter as cpr
import QDSpy_core_view as cvw
import QDSpy_core_support as csp
import QDSpy_multiprocessing as mpr
import QDSpy_gamma as gma
import QDSpy_probeCenter as pce
import Devices.digital_io as dio

if glo.QDSpy_use_Lightcrafter:
  import Devices.lightcrafter as lcr

# ---------------------------------------------------------------------
# Convinience functions
# ---------------------------------------------------------------------
def setPerformanceHigh(_Conf):
  if _Conf.disGC:
    gc.disable()
  if _Conf.incPP:
    csp.setHighProcessPrior()


def setPerformanceNormal(_Conf):
  if _Conf.incPP:
    csp.setNormalProcessPrior()
  if _Conf.disGC:
    gc.enable()
    
# ---------------------------------------------------------------------
def loadStimulus(_fNameStim, _Stim): 
  if len(_fNameStim) == 0:
    ssp.Log.write("FATAL", "No stimulus file name provided")
    return False
  try:
    _Stim.load(_fNameStim)
    return True
  except:
    if(_Stim.getLastErrC() != stm.StimErrC.ok):
      ssp.Log.write("FATAL", "Aborted ({0})".format(_Stim.getLastErrStr()))
      return False
  
# ---------------------------------------------------------------------
def connectLCrs(_Conf=None, _Stim=None):
  if not(_Stim is None) and not(_Stim.isUseLCr):
    return []
  if _Conf is None:
    if not(glo.QDSpy_use_Lightcrafter): 
      return []
  else:
    if not(_Conf.useLCr):
      return []
  LCrList = lcr.enumerateLightcrafters()
  LCrs     = []
  nLCrOk  = 0
  for iLCr, LCr in enumerate(LCrList):
    LCrs.append(lcr.Lightcrafter(_isCheckOnly=False, _funcLog=ssp.Log.write,
                                 _logLevel=glo.QDSpy_LCr_LogLevel))
    result = LCrs[iLCr].connect(iLCr)
    if result[0] != lcr.ERROR.OK:
      LCrs[iLCr] = None
    else:
      nLCrOk += 1 
  if nLCrOk == 0:      
    ssp.Log.write("WARNING", "This script requires a lightcrafter")
  return LCrs  
  

def disconnectLCrs(_LCrs):
  for LCr in _LCrs:
    if LCr != None:
      LCr.disconnect()
  return []
  
# ---------------------------------------------------------------------
def switchGammaLUTByColorMode(_Conf, _View, _Stage, _Stim):
  if _Conf.allowGammaLUT:
    if (_Stim != None):
      if (_Stim.colorMode in [stm.ColorMode._0_1, stm.ColorMode._0_255]):
        ssp.Log.write(" ", "Trying to set user-defined gamma LUT ...")
        gma.setGammaLUT(_View.winPre._dc, _Stage.LUT_userDefined)    
      else:
        ssp.Log.write(" ", "Special color mode (#{0}), setting linear gamma"
                      "LUT ...".format(_Stim.colorMode))
        gma.setGammaLUT(_View.winPre._dc, _Stage.LUT_linDefault)    

    
def restoreGammaLUT(_Conf, _View):  
  if _Conf.allowGammaLUT:
    ssp.Log.write(" ", "Restoring linear gamma LUT ...")
    gma.restoreGammaLUT(_View.winPre._dc)    
      
# ---------------------------------------------------------------------
# MAIN    
# _____________________________________________________________________
def main(_fNameStim, _isParentGUI, _Sync=None):
  # Run a stimulus file.
  #
  if _isParentGUI:
    ssp.Log.setGUISync(_Sync)

  # Load configuration ...
  #
  _Conf = cnf.Config()

  # Display startup message
  #
  ssp.Log.write("***", glo.QDSpy_versionStr +
                " Presenter - " +glo.QDSpy_copyrightStr)  
  ssp.Log.write("ok", "Initializing ...")
  ssp.Log.write(" ", "{0:11}: high process priority during presentation"
                .format("ENABLED" if _Conf.incPP else "disabled"))
  ssp.Log.write(" ", "{0:11}: automatic garbage collection"
                .format("DISABLED" if _Conf.disGC else "enabled"))

  # Generate stage and stimulus instances, as well as a view instance
  # (OpenGL window)
  #
  _Stage = _Conf.createStageFromConfig()
  _Stim  = stm.Stim()
  _View  = cvw.View(_Stage, _Conf)
  _View.createStimulusWindow()
  _Stage.logInfo()

  # Update representation of lightcrafter hardware, if present  
  #
  _Stage.createLEDs(_Conf)
  _Stage.updateLEDs(_Conf)

  # Initialize digital IO hardware, if requested
  #
  if _Conf.useDIO:
    _IO  = dio.devIO_UL(dio.devTypeUL.PCIDIO24, _Conf.DIObrd, _Conf.DIOdev)
    if not(_IO.isReady):
      ssp.Log.write("ERROR", "Universal Library not installed or no digital "+
                    "I/O card present. Set `bool_use_digitalio` in `QDSpy.in"+
                    "i` to False.")
      sys.exit(0)

    port = _IO.getPortFromStr(_Conf.DIOportOut)
    _IO.configDPort(port, dio.devConst.DIGITAL_OUT)
    _IO.writeDPort(port, 0)    
    port = _IO.getPortFromStr(_Conf.DIOportIn)    
    _IO.configDPort(port, dio.devConst.DIGITAL_IN)
  else:
    _IO = None  
    
  # Create a presenter instance
  #
  _Presenter = cpr.Presenter(_Stage, _IO, _Conf, _View)

  
  if not(_isParentGUI):
    # Called from the command line - - - - - - - - - - - - - - - - - - - - - 
    #
    # Load stimulus
    #
    if not(loadStimulus(_fNameStim, _Stim)):
      sys.exit(0)
      
    # Connect to lightcrafter, if required
    #
    _Presenter.LCr = connectLCrs(_Conf, _Stim)
      
    # Present stimulus, with increased process priority and 
    # disabled automatic garbage collector, if requested      
    #  
    try:
      _Presenter.prepare(_Stim)
      setPerformanceHigh(_Conf)
      _Presenter.run()
        
    finally:
      _Presenter.finish()
      setPerformanceNormal(_Conf)


  else:  
    # Called from the GUI  - - - - - - - - - - - - - - - - - - - - - - - - -
    #
    # Notify GUI of display parameters
    #
    _Sync.pipeSrv.send([mpr.PipeValType.toCli_displayInfo, 
                        pickle.dumps(_Stage)])
    
    # Start loop to process GUI (=client) requests
    #
    while(_Sync.Request.value != mpr.TERMINATING):
      try:
        # Check if new data is in the pipe
        #
        data = [mpr.PipeValType.toSrv_None]
        if _Sync.pipeSrv.poll():
          data = _Sync.pipeSrv.recv()
          
          if data[0] == mpr.PipeValType.toSrv_changedStage:
            # Stage parameter have changes, update immediately
            #
            _Stage.scalX_umPerPix = data[1]["scalX_umPerPix"]
            _Stage.scalY_umPerPix = data[1]["scalY_umPerPix"]
            _Stage.centOffX_pix   = data[1]["centOffX_pix"]
            _Stage.centOffY_pix   = data[1]["centOffY_pix"]
            _Stage.rot_angle      = data[1]["rot_angle"]
            _Stage.dxScr12        = data[1]["dxScr12"]
            _Stage.dyScr12        = data[1]["dyScr12"]
            _Stage.offXScr1_pix   = data[1]["offXScr1_pix"]
            _Stage.offYScr1_pix   = data[1]["offYScr1_pix"]
            _Stage.offXScr2_pix   = data[1]["offXScr2_pix"]
            _Stage.offYScr2_pix   = data[1]["offYScr2_pix"]
            data = [mpr.PipeValType.toSrv_None]

          if data[0] == mpr.PipeValType.toSrv_changedLEDs:
            # LED currents and/or enabled state have changes, update
            # immediately
            #
            _Stage.LEDs           = data[1][0]
            _Stage.isLEDSeqEnabled= data[1][1]
            _Stage.sendLEDChangesToLCr(_Conf)
            data = [mpr.PipeValType.toSrv_None]

       
        # Parse client's request
        #
        if _Sync.Request.value == mpr.PRESENTING:
          if data[0] == mpr.PipeValType.toSrv_fileName:
            # Retrieve stimulus file name from pipe and load stimulus
            #
            _fNameStim = os.path.normpath(data[1])
            data       = [mpr.PipeValType.toSrv_None]
            loadStimulus(_fNameStim, _Stim)
            _Sync.setStateSafe(mpr.PRESENTING)
              
            # Run stimulus ...
            #
            try:
              switchGammaLUTByColorMode(_Conf, _View, _Stage, _Stim)    
              _Presenter.LCr = connectLCrs(_Conf, _Stim)
              _Presenter.prepare(_Stim, _Sync)
              setPerformanceHigh(_Conf)
              _Presenter.run()

            finally:
              _Presenter.LCr = disconnectLCrs(_Presenter.LCr)
              _Presenter.finish()
              setPerformanceNormal(_Conf)
              '''
              _Sync.setStateSafe(mpr.IDLE)
              '''
          else:
            ssp.Log.write("DEBUG", "mpr.PRESENTING, unexpected client data")
          
          _Sync.setStateSafe(mpr.IDLE)  
        
          
        elif _Sync.Request.value == mpr.COMPILING:          
          if data[0] == mpr.PipeValType.toSrv_fileName:
            # Retrieve stimulus file name from pipe and compile stimulus
            #
            _fNameStim = os.path.abspath(data[1]) +".py"
            data       = [mpr.PipeValType.toSrv_None]
            _Sync.setStateSafe(mpr.COMPILING)
            try:
              subprocess.check_call(["python", _fNameStim])
              ssp.Log.write("ok", "... done")

            except subprocess.CalledProcessError:
              ssp.Log.write("ERROR", "... failed.")

          else:
            ssp.Log.write("DEBUG", "mpr.COMPILING, unexpected client data")
                
          _Sync.setStateSafe(mpr.IDLE)


        elif _Sync.Request.value == mpr.PROBING:
          if data[0] == mpr.PipeValType.toSrv_probeParams:
            # Change into interactive probing mode ...
            #
            _Sync.setStateSafe(mpr.PROBING)
            try:
              switchGammaLUTByColorMode(_Conf, _View, _Stage, _Stim)    
              _Presenter.LCr = connectLCrs(_Conf, _Stim)
              setPerformanceHigh(_Conf)
              if data[1] == glo.QDSpy_probing_center:
                # Currently only interactive center-probing is implemented
                #
                pce.probe_main(data[2],_Sync, _View, _Stage)
                
            finally:
              data = [mpr.PipeValType.toSrv_None]
              _Presenter.LCr = disconnectLCrs(_Presenter.LCr)
              _Presenter.finish()
              setPerformanceNormal(_Conf)
 
          else:
            ssp.Log.write("DEBUG", "mpr.PROBE_CENTER, unexpected client data")
                
          _Sync.setStateSafe(mpr.IDLE)

          
        elif not(_Sync.Request.value in [mpr.CANCELING, mpr.UNDEFINED]):
          # Unknown request
          #
          ssp.Log.write("DEBUG", "Request {0} unknown"
                        .format(_Sync.Request.value))


        if data[0] != mpr.PipeValType.toSrv_None:
          ssp.Log.write("DEBUG", "unexpected client data left after loop")
          
          
      finally:
        # Clear request
        #
        _Sync.setRequestSafe(mpr.UNDEFINED)  

      # Dispatch events for the OpenGL window and sleep for a bit
      #
      '''
      _View.dispatch_events()
      '''
      time.sleep(0.02) # 0.05

  # Restore gamma LUT, if nescessary
  #
  restoreGammaLUT(_Conf, _View)
      
  # Clean up
  #
  _View.killWindows()
  _Presenter.LCr = disconnectLCrs(_Presenter.LCr)
    
  ssp.Log.write("ok", "... done")

# ---------------------------------------------------------------------
if __name__ == '__main__':
  freeze_support()  
  args = cnf.getParsedArgv()
  main(args.fNameStim, False)

# ---------------------------------------------------------------------
