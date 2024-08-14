#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QDSpy module - main program of the MQTT version of QDSpy

Copyright (c) 2024 Thomas Euler
All rights reserved.

2024-08-03 - Initial version
"""
# ---------------------------------------------------------------------
__author__ 	= "code@eulerlab.de"

import platform
import time
import os
import sys
import pickle
#from datetime import timedelta
from typing import TextIO
from multiprocessing import Process
import Libraries.multiprocess_helper as mpr
import QDSpy_stim as stm
import QDSpy_config as cfg
import QDSpy_file_support as fsu
import QDSpy_stage as stg
import QDSpy_global as glo
import QDSpy_core
#import QDSpy_core_support as csp
from Libraries.log_helper import Log
import Libraries.mqtt_client as mqtt
import Libraries.mqtt_globals as mgl

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

PLATFORM_WINDOWS = platform.system() == "Windows"
if not PLATFORM_WINDOWS:
    WindowsError = FileNotFoundError

# ---------------------------------------------------------------------
# TODO: Remove redundancy; `State`and `Canceled` are also defined 
# in `QDSpy_GUI_main.py`
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

class Canceled(Exception):
    pass

# ---------------------------------------------------------------------
# MQTT-related
# ---------------------------------------------------------------------
def msg_handler(msg):
    '''Handle incoming messages
    '''
    # Check if command (in `data[0]` is valid
    data = msg.payload.decode("UTF8").split(",")
    if data[0] not in [cmd.value for cmd in mgl.Command]:
        MainAppMQTT.logWrite("ERROR", f"Invalid command (`{data[0]}`)")
        # TODO
    else:    
        # Execute command
        print(data)

# ---------------------------------------------------------------------
# Main class
# ---------------------------------------------------------------------
class MainAppMQTT(object):

    def __init__(self):
        # Initialize
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
        self.Stim_soundVol = 0

        # Open log file
        self._logFile, fn = self.openLogFile(self.Conf.pathLogs)
        self.logWrite(" ", f"Saving log file to `{fn}` ...")
                
        # Identify 
        self.logWrite(
            "***", 
            f"{glo.QDSpy_versionStr} MQTT client - {glo.QDSpy_copyrightStr}"
        )

        # Create status objects and a pipe for communicating with the
        # presentation process (see below)
        self.logWrite("DEBUG", "Creating sync object ...")
        self.state = State.undefined
        self.Sync = mpr.Sync()
        #
        # Note: We are not using the GUI but the main MQTT application;
        # historically, it is called `setGUISync` etc.
        Log.isRunFromGUI = True
        Log.setGUISync(self.Sync, noStdOut=self.noMsgToStdOut)
        self.logWrite("DEBUG", "... done")

        # Create process that opens a view (an OpenGL window) and waits for
        # instructions to play stimuli
        self.logWrite("DEBUG", "Creating worker thread ...")
        self.worker = Process(
            target=QDSpy_core.main, args=(self.currStimFName, True, self.Sync)
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

        # Connect to MQTT broker 
        # TODO: Error handling
        self.logWrite("DEBUG", "Initiating MQTT ...")
        mqtt.Client.handler = msg_handler
        mqtt.Client.connect(ID=mgl.UUID)
        self.logWrite("DEBUG", "... done")

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
                self.currStimFName = os.path.join(self.currQDSPath, sd)
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
    def loadStim(self, _fName: str):
        """Load stimulus from file `_fName`
        """
        self.isStimReady = False
        try:
            # Try loading stimulus file and get info, if successful
            self.Stim.load(_fName, _onlyInfo=True)
            self.setState(State.ready)
            self.isStimCurr = fsu.getStimCompileState(_fName)
            '''
            if self.isStimCurr:
                txtCompState = (
                    fStrPreGreen + "compiled (.pickle) is up-to-date" + fStrPost
                )
            else:
                txtCompState = "compiled (.pickle), pre-dates .py"
            txtInfo = self.Stim.descrStr
            mins, secs = divmod(self.Stim.lenStim_s, 60)
            hours, mins = divmod(mins, 60)
            txtDuration = "{0:.3f} s ({1:02d}:{2:02d}:{3:02d})".format(
                self.Stim.lenStim_s, int(hours), int(mins), int(secs)
            )
            '''
            self.currStimFName = _fName
            self.isStimReady = True                        

        except:  # noqa: E722
            # Failed ...
            '''
            txtCompState = fStrPreRed + "not compiled (no .pickle)" + fStrPost
            if self.Stim.getLastErrC() != stm.StimErrC.ok:
                self.updateStatusBar(self.Stim.getLastErrStr(), True)
            '''
            pass

        self.updateAll()        

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def compileStim(self):
        """Send stimulus file name via pipe and signal worker thread to
        compile the stimulus
        """
        self.Sync.pipeCli.send(
            [mpr.PipeValType.toSrv_fileName, self.currStimFName, self.currStimPath]
        )
        self.Sync.setRequestSafe(mpr.COMPILING)
        self.logWrite(" ", "Compiling stimulus script ...")

        # Wait for the worker to start ...
        if self.Sync.waitForState(mpr.COMPILING, self.Conf.guiTimeOut, self.updateAll):
            self.setState(State.compiling, True)

            # Wait for the worker to finish the compilation, while keeping the
            # GUI alive
            self.Sync.waitForState(mpr.IDLE, 0.0, self.updateAll)
            self.updateAll()

        else:
            self.logWrite(
                "DEBUG", 
                "compileStim, timeout waiting for COMPILING"
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def runStim(self):
        """Send stimulus file name via pipe and signal worker thread to
        start presenting the stimulus
        """
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
        """Send a request to the worker to cancel the presentation
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
    # Running and closing the application 
    # -------------------------------------------------------------------
    def loop(self):
        """Main application loop
        """
        try:
            # Start MQTT client
            mqtt.Client.start()

            # Run main loop
            while True:
                try:

                    # Process messages in the pipe to the worker and
                    # sleep for a bit    
                    self.processPipe()
                    time.sleep(glo.QDSpy_loop_sleep_s)
                    
                except KeyboardInterrupt:
                    self.logWrite("INFO", "User abort")
                    self.closeEvent()
                    break
        finally:
            # Stop MQTT client and close log file
            mqtt.Client.stop()                
            self.closeLogFile(self._logFile)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def closeEvent(self):
        """User requested to close the application
        """
        # Save config
        self.Conf.saveWinPosToConfig()
        self.Conf.save()

        # Closing is immanent, stop stimulus, if running ...
        if self.Sync.State.value in [mpr.PRESENTING, mpr.COMPILING]:
            self.abortStimulus()

        # ... and clean up
        self.logWrite("DEBUG", "Kill worker thread ...")
        self.Sync.setRequestSafe(mpr.TERMINATING)
        self.worker.join()
        while self.worker.is_alive():
            time.sleep(0.2)
        self.logWrite("DEBUG", "... done")

    # -------------------------------------------------------------------
    def updateAll(self):
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

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setState(self, _newState):
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
                self.updateAll()

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
                # ***************************
                # TODO: Other types of data need to be processed
                # ***************************
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
        """Log a message to the appropriate output
        """
        data = Log.write(_hdr, _msg, _isProg, _getStr=True, _isWorker=False)
        if data:
            self.log(data)

    def log(self, _data):
        if len(_data) > 2:
            self.writeToLogFile(self._logFile, _data[2])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @staticmethod
    def openLogFile(_fPath) -> TextIO:
        """Open a log file
        """
        os.makedirs(_fPath, exist_ok=True)
        fName = time.strftime("%Y%m%d_%H%M%S")
        j = 0
        while os.path.exists(_fPath + fName):
            fName = f"{fName}_{j:04d}"
            j += 1

        sf = _fPath + fName + glo.QDSpy_logFileExtension
        return open(sf, "w"), sf

    @staticmethod
    def writeToLogFile(_file, _line):
        """Write text in `_line` to file `_file`
        """
        if _file:
            _file.write(_line +"\r")

    @staticmethod
    def closeLogFile(_file: TextIO):
        """Close the log file
        """
        if _file:
            _file.close()
    
# ---------------------------------------------------------------------
# _____________________________________________________________________
if __name__ == "__main__":
    
    # Create main app instance and run main loop
    QDSApp = MainAppMQTT()
    QDSApp.loop()

# ---------------------------------------------------------------------
