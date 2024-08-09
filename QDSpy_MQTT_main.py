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
#import pickle
#from datetime import timedelta
from multiprocessing import Process
import Libraries.multiprocess_helper as mpr
import QDSpy_stim as stm
import QDSpy_config as cfg
import QDSpy_file_support as fsu
#import QDSpy_stage as stg
import QDSpy_global as glo
import QDSpy_core
#import QDSpy_core_support as csp
import Libraries.log_helper as _log
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
        log("ERROR", f"Invalid command (`{data[0]}`)")
        # TODO
    else:    
        # Execute command
        print(data)

# ---------------------------------------------------------------------
def log(header: str, msg: str, _isProgress: bool = False):
    _log.Log.write(header, msg, _isProgress=_isProgress)

# ---------------------------------------------------------------------
# Main class
# ---------------------------------------------------------------------
class MainAppMQTT(object):

    def __init__(self):
        # Initialize
        self.Conf = cfg.Config()
        self.Stim = stm.Stim()
        '''
        self.currStimPath = self.Conf.pathStim
        '''
        self.currStimPath = os.path.abspath(self.Conf.pathStim)
        self.currQDSPath = os.getcwd()
        self.currStimName = "n/a"
        self.currStimFName = ""
        self.isStimReady = False
        self.isStimCurr = False
        self.isViewReady = False
        # TODO: Needs to allow for other DLP types
        self.isLCrUsed = False 
        self.isIODevReady = None
        self.lastIOInfo = []
        self.IOCmdCount = 0
        self.Stage = None
        self.noMsgToStdOut = False

        # For reporting the stimulus status during presentation
        self.Stim_tFrRel_s = 0
        self.Stim_nFrTotal = 0
        self.Stim_percent = 0
        self.Stim_completed = False
        self.Stim_soundVol = 0

        # Create status objects and a pipe for communicating with the
        # presentation process (see below)
        # Note: it is called `setGUISync` but this is GUI-independent
        self.logWrite("DEBUG", "Creating sync object ...")
        self.state = State.undefined
        self.Sync = mpr.Sync()
        _log.Log.isRunFromGUI = False
        _log.Log.setGUISync(self.Sync, noStdOut=self.noMsgToStdOut)
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
        self.setState(State.idle, True)

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
        self.updateIOInfo()
        self.logWrite("DEBUG", "... done")

        # Connect to MQTT broker 
        # TODO: Error handling
        mqtt.Client.handler = msg_handler
        mqtt.Client.connect(ID=mgl.UUID)

        # Check if autorun stimulus file present and if so run it
        try:
            self.isStimCurr = False
            self.currStimFName = os.path.join(
                self.currStimPath, glo.QDSpy_autorunStimFileName
            )
            isAutoRunExists = fsu.getStimExists(self.currStimFName)
            if isAutoRunExists:
                # Check if a current compiled version of the autorun file
                # exists
                self.isStimCurr = fsu.getStimCompileState(self.currStimFName)

            if not isAutoRunExists or not self.isStimCurr:
                # No current compiled auto-run file present, so use default file
                self.currStimFName = os.path.join(
                    self.currQDSPath, glo.QDSpy_autorunDefFileName
                )
                self.logWrite(
                    "ERROR",
                    "No compiled `{0}` in current stimulus "
                    "folder, using `{1}` in `{2}`.".format(
                        glo.QDSpy_autorunStimFileName,
                        glo.QDSpy_autorunDefFileName,
                        self.currQDSPath,
                    ),
                )

            # Run either autorun file ...
            self.logWrite("DEBUG", "Running {0} ...".format(self.currStimFName))
            self.Stim.load(self.currStimFName, _onlyInfo=True)
            self.setState(State.ready)
            self.isStimReady = True
            self.runStim()

        except:  # noqa: E722
            # Failed ...
            if self.Stim.getLastErrC() != stm.StimErrC.ok:
                _log.Log.write(
                    "ERROR",
                    "No compiled `{0}` in current stimulus folder,"
                    " and `{1}.pickle` is not in `{2}`. Program is"
                    " aborted.".format(
                        glo.QDSpy_autorunStimFileName,
                        glo.QDSpy_autorunDefFileName,
                        self.currQDSPath,
                    ),
                )
                sys.exit(0)

# ---------------------------------------------------------------------
# _____________________________________________________________________
if __name__ == "__main__":
    
    # Create main app instance
    QDSApp = MainAppMQTT()
    
    # Main loop (tentative)
    try:
        mqtt.Client.start()
        while True:
            try:
                time.sleep(0.02)
            except KeyboardInterrupt:
                log("INFO", "User abort")
                break
    finally:
        mqtt.Client.stop()                

    log("OK", "Done")

# ---------------------------------------------------------------------
