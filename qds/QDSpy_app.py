#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QDSpy module - Application class

Copyright (c) 2024-2025 Thomas Euler
All rights reserved.

2024-08-03 - Initial version
2025-03-30 - Log file handing update (similar to GUI version)
           - Compile non-current stimuli after loading 
"""
# ---------------------------------------------------------------------
__author__ 	= "code@eulerlab.de"

import platform
import time
import os
import sys
import pickle
from typing import TextIO
from multiprocessing import Process
import qds.libraries.multiprocess_helper as mpr
import qds.QDSpy_stim as stm
import qds.QDSpy_config as cfg
import qds.QDSpy_file_support as fsu
import qds.QDSpy_stage as stg
import qds.QDSpy_global as glo
import qds.QDSpy_core
from qds.libraries.log_helper import Log

PLATFORM_WINDOWS = platform.system() == "Windows"
if not PLATFORM_WINDOWS:
    WindowsError = FileNotFoundError

# ---------------------------------------------------------------------
class State:
    undefined = 0
    idle = 1
    ready = 2
    loading = 3
    compiling = 4
    playing = 5
    canceling = 6
    probing = 7
    # ...

StateStr = [
    "undefined", "idle", "ready", "loading", "compiling", "playing",
    "canceling", "probing"
]    

class Canceled(Exception):
    pass

# ---------------------------------------------------------------------
# Main QDSpy application class
# ---------------------------------------------------------------------
class QDSpyApp(object):

    def __init__(self, _title: str):
        # Initialize
        self._title = _title
        self.Conf = cfg.Config()
        self.Stim = stm.Stim()
        self.currStimPath = os.path.abspath(self.Conf.pathStim)
        self.currQDSPath = os.getcwd()
        self.currStimName = "n/a"
        self.currStimFName = ""
        self.isStimReady = False
        self.isStimCurr = False
        self.isViewReady = False
        self.isLCrUsed = False 
        self.isIODevReady = None
        self.lastIOInfo = []
        self.IOCmdCount = 0
        self.Stage = None
        self.noMsgToStdOut = False
        self._logFile = None

        # For reporting the stimulus status during presentation
        self.Stim_tFrRel_s = 0
        self.Stim_nFrTotal = 0
        self.Stim_percent = 0
        self.Stim_completed = False
        self.Stim_soundVol = self.Conf.volume

        # Open log file
        self.fNameLog = self._getNewLogFileName()
        if not glo.QDSpy_saveLogInTheEnd:
            self.logWrite(" ", "Saving log continuosly to '{0}' ...".format(self.fNameLog))
            self.logFile = open(self.fNameLog, "w")
        '''
        self._logFile, fn = self.openLogFile(self.Conf.pathLogs)
        self.logWrite(" ", f"Saving log file to `{fn}` ...")
        '''
                
        # Identify 
        self.logWrite(
            "***", 
            f"{glo.QDSpy_versionStr} {self._title} - {glo.QDSpy_copyrightStr}"
        )

        # Create status objects and a pipe for communicating with the
        # presentation process (see below)
        self.logWrite("DEBUG", "Creating sync object ...")
        self.state = State.undefined
        self.Sync = mpr.Sync()
        #
        # Tell the Log object that we need to receive messages from the worker
        # for the log file
        Log.isRunFromGUI = True
        Log.setGUISync(self.Sync, noStdOut=self.noMsgToStdOut)
        self.logWrite("DEBUG", "... done")

        # Create process that opens a view (an OpenGL window) and waits for
        # instructions to play stimuli
        self.logWrite("DEBUG", "Creating worker thread ...")
        self.worker = Process(
            target=qds.QDSpy_core.main, args=(self.currStimFName, True, self.Sync)
        )
        self.logWrite("DEBUG", "... done")
        self.worker.daemon = True
        self.logWrite("DEBUG", "Starting worker thread ...")
        self.worker.start()
        self.logWrite("DEBUG", "... done")

        self.isViewReady = True
        self.setState(State.idle)

        # Check if worker process is still alive
        self.logWrite("DEBUG", "Check worker thread ...")
        time.sleep(1.0)
        if not (self.worker.is_alive()):
            sys.exit(0)
        self.logWrite("DEBUG", "... done")

        # Wait until the worker thread send info about the stage via the pipe
        self.logWrite("DEBUG", "Waiting for stage info from worker ...")
        while not self.Stage:
            self.processPipe()
            time.sleep(0.05)
        self.logWrite("DEBUG", "... done")

        # Update LED setting
        self.Stage.updateLEDs(self.Conf)

        # Update IO device info
        self.logWrite("DEBUG", "Waiting for IO device state from worker ...")
        self.Sync.pipeCli.send([mpr.PipeValType.toSrv_checkIODev, []])
        while self.isIODevReady is None:
            self.processPipe()
            time.sleep(0.05)
        self.logWrite("DEBUG", "... done")

        # Check if autorun stimulus file present and if so run it
        self.handleAutorun()

    # -----------------------------------------------------------------
    def handleAutorun(self):
        '''Check if autorun stimulus file present and if so run it
        '''
        try:
            self.isStimCurr = False
            sf = glo.QDSpy_autorunStimFileName
            sd = glo.QDSpy_autorunDefFileName
            self.currStimFName = os.path.join(self.currStimPath, sf)
            isAutoRunExists = fsu.getStimExists(self.currStimFName)
            if isAutoRunExists:
                # Check if a  compiled version of the autorun file exists
                self.isStimCurr = fsu.getStimCompileState(self.currStimFName)

            if not isAutoRunExists or not self.isStimCurr:
                # Use default file as no compiled auto-run file is present
                self.currStimFName = os.path.join(self.currQDSPath, glo.QDSpy_codePath, sd)
                self.logWrite(
                    "ERROR", 
                    f"No compiled `{sf}` in current stimulus folder"
                )
                self.logWrite("INFO", f"Using `{sd}` in `{self.currQDSPath}`.")

            # Run either autorun file ...
            self.logWrite("DEBUG", "Running {0} ...".format(self.currStimFName))
            self.Stim.load(self.currStimFName, _onlyInfo=True)
            self.setState(State.ready)
            self.isStimReady = True
            self.runStim()

        except:  # noqa: E722
            # Failed ...
            if self.Stim.getLastErrC() != stm.StimErrC.ok:
                self.logWrite(
                    "ERROR",
                    f"No compiled `{sf}` in current stimulus folder, "
                    f"and `{sd}.pickle` is not in `{self.currQDSPath}`. "
                )
                self.logWrite("ERROR", "Program is aborted.")                
                sys.exit(0)

    # -------------------------------------------------------------------
    # Loading, compiling, running, and aborting stimuli
    # -------------------------------------------------------------------
    def loadStim(self, _fName: str) -> int:
        """ Load stimulus from file `_fName`, returns an error code if 
            the stimulus was not found or needs to be compiled
        """
        self.isStimReady = False
        self.isStimCurr = False
        errC = stm.StimErrC.ok

        if not fsu.getStimExists(_fName):
            # Stimulus file does not exist
            errC = stm.StimErrC.invalidFileNamePath
        
        else:
            try:
                # Try loading compiled stimulus file ...
                self.Stim.load(_fName, _onlyInfo=False)
                self.isStimCurr = fsu.getStimCompileState(_fName)
                self.currStimFName = _fName
                self.setState(State.ready)
                self.isStimReady = True
                
            except stm.StimException:
                # Failed ... 
                errC = self.Stim.getLastErrC()

        self.updateAll()        
        return errC

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def compileStim(self, _fName :str ="", _doRun :bool =True) -> None:
        """ Send stimulus file name via pipe and signal worker thread to
            compile the stimulus
        """
        errC = stm.StimErrC.ok
        fName = _fName if len(_fName) > 0 else self.currStimFName

        self.Sync.pipeCli.send(
            [mpr.PipeValType.toSrv_fileName, fName, self.currStimPath]
        )
        self.Sync.setRequestSafe(mpr.COMPILING)
        self.logWrite(" ", "Compiling stimulus script ...")

        # Wait for the worker to start ...
        if self.Sync.waitForState(mpr.COMPILING, self.Conf.guiTimeOut, self.updateAll):
            self.setState(State.compiling, True)
            
            # Wait for the worker to finish the compilation, while keeping the
            # GUI alive
            self.Sync.waitForState(mpr.IDLE, 0.0, self.updateAll)

        else:
            self.logWrite(
                "DEBUG", 
                "compileStim, timeout waiting for COMPILING"
            )
            errC = stm.StimErrC.noCompiledStim

        self.updateAll()
        return errC

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def runStim(self) -> None:
        """ Send stimulus file name via pipe and signal worker thread to
            start presenting the stimulus; wait for the stimulus to end ...
        """
        #print("runStim", self.currStimFName, self.currStimPath)
        self.Sync.pipeCli.send(
            [mpr.PipeValType.toSrv_fileName, self.currStimFName, self.currStimPath,
             self.Stim_soundVol]
        )
        self.Sync.setRequestSafe(mpr.PRESENTING)
        self.logWrite(" ", "Presenting stimulus ...")

        # Wait for the worker to start ...
        if self.Sync.waitForState(mpr.PRESENTING, self.Conf.guiTimeOut, self.updateAll):
            self.setState(State.playing, True)

            # Wait for the worker to finish the presentation, while keeping the
            # GUI alive
            self.Sync.waitForState(mpr.IDLE, 0.0, self.updateAll)
            self.updateAll()

        else:
            self.logWrite(
                "DEBUG", 
                "runStim, timeout waiting for PRESENTING"
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def abortStim(self):
        """ Send a request to the worker to cancel the presentation
        """
        self.setState(State.canceling)
        self.Sync.setRequestSafe(mpr.CANCELING)
        self.setState(State.canceling, True)

        # Wait for the worker to finish cancelling
        res = self.Sync.waitForState(
            mpr.IDLE, self.Conf.guiTimeOut, self.updateAll
        )
        if res:
            self.setState(State.ready, True)
        else:
            self.logWrite(
                "DEBUG", 
                "abortStimulus, timeout waiting for IDLE"
            )

    # -------------------------------------------------------------------
    # Application control-related
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def closeEvent(self):
        """ User requested to close the application
        """
        # Save config
        self.Conf.saveWinPosToConfig()
        self.Conf.save()

        # Closing is immanent, stop stimulus, if running ...
        if self.Sync.State.value in [mpr.PRESENTING, mpr.COMPILING]:
            self.abortStim()

        # ... and clean up
        self.logWrite("DEBUG", "Kill worker thread ...")
        self.Sync.setRequestSafe(mpr.TERMINATING)
        self.worker.join()
        while self.worker.is_alive():
            time.sleep(0.2)
        self.logWrite("DEBUG", "... done")

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def updateAll(self) -> None:
        """ Update the status
        """
        stateWorker = self.Sync.State.value
        if stateWorker == mpr.PRESENTING:
            self.state = State.playing
        elif stateWorker == mpr.COMPILING:
            self.state = State.compiling
        elif stateWorker == mpr.PROBING:
            self.state = State.probing
        elif stateWorker in [mpr.CANCELING, mpr.TERMINATING]:
            self.state = State.canceling
        elif stateWorker == mpr.IDLE:
            self.state = State.ready

        self.processPipe()
        #print(StateStr[self.state])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setState(self, _newState, _doUpdateGUI=False):
        """ Update state
        """
        self.state = _newState

    # -------------------------------------------------------------------
    # Communication with worker-thread
    # -------------------------------------------------------------------
    def processPipe(self):
        """ Read data from pipe to worker thread, if available
        """
        while self.Sync.pipeCli.poll():
            data = self.Sync.pipeCli.recv()
            if data[0] == mpr.PipeValType.toCli_log:
                # Handle log data -> write to history
                self.log(data)
            
            elif data[0] == mpr.PipeValType.toCli_displayInfo:
                # Handle display information data -> update
                self.Stage = pickle._loads(data[1])
                isLCrDev = not self.Stage.scrDevType == stg.ScrDevType.generic
                self.isLCrUsed = self.Conf.useLCr and isLCrDev
                '''
                self.updateAll()
                '''

            elif data[0] == mpr.PipeValType.toCli_IODevInfo:
                # Receive I/O device information
                self.isIODevReady = data[1][0]
                if self.isIODevReady is None:
                    self.isIODevReady = False
                self.lastIOInfo = data[1]

            elif data[0] == mpr.PipeValType.toCli_time:
                # Receive information about stimulus presentation progress
                self.Stim_tFrRel_s = data[1]
                self.Stim_nFrTotal = data[2]

            elif data[0] == mpr.PipeValType.toCli_playEndInfo:
                # Receive information about stimulus presentation end
                self.Stim_completed = data[1]

            else:
                # ***************************
                # TODO: Other types of data need to be processed
                # ***************************
                pass

    def waitForPipe(self, _func, _timeOut_s=1.0):
        """ Wait for the passed function to return True or for time-out
        """
        n = _timeOut_s / 0.05
        while not (_func()) and (n > 0):
            self.processPipe()
            time.sleep(0.05)
            n -= 1

    # -------------------------------------------------------------------
    # Logging- and log file-related
    # -------------------------------------------------------------------
    def logWrite(self, _hdr: str, _msg: str, _isProg: bool = False):
        """ Log a message to the appropriate output
        """
        data = Log.write(_hdr, _msg, _isProg, _getStr=True, _isWorker=False)
        if data is not None:
            self.log(data)

    def log(self, _data):
        if len(_data) > 2 and not glo.QDSpy_saveLogInTheEnd:
            self.writeLogFileLine(_data[2])        

    # -----------------------------------------------------------------
    # Functions related to the log file
    # -----------------------------------------------------------------
    def _getNewLogFileName(self) -> str:
        """ Return a valid log file name
        """
        os.makedirs(self.Conf.pathLogs, exist_ok=True)
        fName = time.strftime("%Y%m%d_%H%M%S")
        fPath = fsu.getJoinedPath(self.Conf.pathLogs, fName)
        j = 0
        while os.path.exists(fPath +glo.QDSpy_logFileExtension):
            fPath = "{0}_{1:04d}".format(fPath, j)
            j += 1

        return fPath + glo.QDSpy_logFileExtension


    def writeLogFileLine(self, msg :str):
        """ Write line to log file
        """    
        if self.logFile:
            self.logFile.write(msg +"\n")
            self.logFile.flush()


    def saveLogFile(self):
        """ Save log file
        """    
        with open(self.fNameLog, "w") as logFile:
            logFile.write(str(self.textBrowserHistory.toPlainText()))


    def closeLogFile(self):
        """ Close log file
        """        
        if self.logFile:
            self.logFile.close()
            self.logFile = None            
    
# ---------------------------------------------------------------------
