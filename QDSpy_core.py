#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
#  QDSpy_core.py
#
#  Command-line presentation program
#
#  This is a simple Python software for scripting and presenting stimuli
#  for visual neuroscience. It is based on QDS, uses OpenGL via pyglet
#  and primarly targets Windows, but may also run on other operating
#  systems.
#
#  Copyright (c) 2013-2015 Thomas Euler
#  All rights reserved.
#
# ---------------------------------------------------------------------
__author__ 	= "code@eulerlab.de"

# ---------------------------------------------------------------------
import time
import sys
import gc
import subprocess
import pickle
from   multiprocessing        import freeze_support
from   QDSpy_global           import *
import QDSpy_stim             as stm
import QDSpy_stim_support     as ssp
import QDSpy_config           as cnf
import QDSpy_core_presenter   as cpr
import QDSpy_core_view        as cvw
import QDSpy_core_support     as csp
import QDSpy_multiprocessing  as mpr
import QDSpy_gamma            as gma
import Devices.digital_io     as dio

if QDSpy_use_Lightcrafter:
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
  
      
def connectLCr(_confirm=True):
  if not(QDSpy_use_Lightcrafter) or not(_confirm):
    _LCr = None
  else:
    ssp.Log.write(" ", "Trying to connect lightcrafter ...")
    _LCr   = lcr.Lightcrafter(_isCheckOnly=False, _isVerbose=False)
    result = _LCr.connect()
    if result[0] != lcr.ERROR.OK:
      ssp.Log.write(" ", "... failed")
      ssp.Log.write("WARNING", "This script requires a lightcrafter")
      _LCr = None
    else:
      ssp.Log.write("ok", "... done")
  return _LCr  


def disconnectLCr(_LCr):
  if _LCr != None:
    ssp.Log.write("ok", "Lightcrafter disconnected")
    _LCr.disconnect()
  return None
  

def switchGammaLUTByColorMode(_Conf, _View, _Stage, _Stim):
  if _Conf.allowGammaLUT:
    if (_Stim != None):
      if (_Stim.colorMode in [stm.ColorMode._0_1, stm.ColorMode._0_255]):
        ssp.Log.write(" ", "Trying to set user-defined gamma LUT ...")
        gma.setGammaLUT(_View.winPresent._dc, _Stage.LUT_userDefined)    
      else:
        ssp.Log.write(" ", "Special color mode (#{0}), setting linear gamma"
                      "LUT ...".format(_Stim.colorMode))
        gma.setGammaLUT(_View.winPresent._dc, _Stage.LUT_linDefault)    

    
def restoreGammaLUT(_Conf, _View):  
  if _Conf.allowGammaLUT:
    ssp.Log.write(" ", "Restoring linear gamma LUT ...")
    gma.restoreGammaLUT(_View.winPresent._dc)    
      
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
  _Conf  = cnf.Config()

  # Display startup message
  #
  ssp.Log.write("***", QDSpy_versionStr +" Presenter - " +QDSpy_copyrightStr)  
  ssp.Log.write("ok", "Initializing ...")
  ssp.Log.write(" ", "{0:11}: high process priority during presentation"
                .format("ENABLED" if _Conf.incPP else "disabled"))
  ssp.Log.write(" ", "{0:11}: automatic garbage collection"
                .format("DISABLED" if _Conf.disGC else "enabled"))

  # Generate stage and stimulus instances, as well as a view instance
  # (OpenGL window)
  #
  _Stage  = _Conf.createStageFromConfig()
  _Stim   = stm.Stim()
  _View   = cvw.View(_Stage, _Conf)
  _View.createWindow()
  _Stage.logInfo()

  # Initialize digital IO hardware, if requested
  #
  if _Conf.useDIO:
    _IO  = dio.devIO_UL(dio.devTypeUL.PCIDIO24, _Conf.DIObrd, _Conf.DIOdev)
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
    _Presenter.LCr = connectLCr(_Conf.useLCr and _Stim.isUseLCr)
      
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
    _LCr = connectLCr(_Conf.useLCr)
    _Stage.updateLEDs(_LCr, _Conf)
    _LCr = disconnectLCr(_LCr)
    _Sync.pipeSrv.send([mpr.PipeValType.toCli_displayInfo, 
                        pickle.dumps(_Stage)])
    
    # Start loop to process GUI (=client) requests
    #
    while(_Sync.Request.value != mpr.TERMINATING):
      try:
        # Parse client's request
        #
        if _Sync.Request.value == mpr.PRESENTING:
          # Retrieve stimulus file name from pipe and load stimulus
          #
          if _Sync.pipeSrv.poll():
            data = _Sync.pipeSrv.recv()
            if data[0] == mpr.PipeValType.toSrv_fileName:
              _fNameStim = data[1]
              loadStimulus(_fNameStim, _Stim)
              _Sync.setStateSafe(mpr.PRESENTING)
            else:
              ssp.Log.write("DEBUG", "mpr.PRESENTING, unexpected client data")
            
            # Run stimulus ...
            #
            try:
              switchGammaLUTByColorMode(_Conf, _View, _Stage, _Stim)    
              _Presenter.LCr = connectLCr(_Conf.useLCr and _Stim.isUseLCr)
              _Presenter.prepare(_Stim, _Sync)
              setPerformanceHigh(_Conf)
              _Presenter.run()

            finally:
              _Presenter.LCr = disconnectLCr(_Presenter.LCr)
              _Presenter.finish()
              setPerformanceNormal(_Conf)
              _Sync.setStateSafe(mpr.IDLE)

          
        elif _Sync.Request.value == mpr.COMPILING:          
          # Retrieve stimulus file name from pipe and compile stimulus
          #
          if _Sync.pipeSrv.poll():
            data = _Sync.pipeSrv.recv()
            if data[0] == mpr.PipeValType.toSrv_fileName:
              _fNameStim = data[1] +".py"
              _Sync.setStateSafe(mpr.COMPILING)
              try:
                subprocess.check_call(["python", _fNameStim])
                ssp.Log.write("ok", "... done")

              except subprocess.CalledProcessError:
                ssp.Log.write("ERROR", "... failed.")
                
            else:
              ssp.Log.write("DEBUG", "mpr.COMPILING, unexpected client data")
            
          _Sync.setStateSafe(mpr.IDLE)
          
          
        elif not(_Sync.Request.value in [mpr.CANCELING, mpr.UNDEFINED]):
          # Unknown request
          #
          ssp.Log.write("DEBUG", "Request {0} unknown"
                        .format(_Sync.Request.value))

      finally:
        # Clear request
        #
        _Sync.setRequestSafe(mpr.UNDEFINED)  

      # Dispatch events for the OpenGL window and sleep for a bit
      #
      _View.winPresent.dispatch_events() 
      time.sleep(0.05)

  # Restore gamma LUT, if nescessary
  #
  restoreGammaLUT(_Conf, _View)
      
  # Clean up
  #
  _View.killWindow()
  _Presenter.LCr = disconnectLCr(_Presenter.LCr)
    
  ssp.Log.write("ok", "... done")

# ---------------------------------------------------------------------
if __name__ == '__main__':
  freeze_support()  
  args = cnf.getParsedArgv()
  main(args.fNameStim, False)

# ---------------------------------------------------------------------
