#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QDSpy module - Main program of the MQTT version of QDSpy

Copyright (c) 2024 Thomas Euler
All rights reserved.

2024-08-03 - Initial version
2024-08-11 - Now uses the QDSpy application class
"""
# ---------------------------------------------------------------------
__author__ 	= "code@eulerlab.de"

import platform
import time
import os
from collections import deque
import QDSpy_global as glo
import QDSpy_stim as stm
import QDSpy_file_support as fsu
from QDSpy_app import QDSpyApp, State, StateStr
import Libraries.mqtt_client as mqtt
import Libraries.mqtt_globals as mgl
"""
import Devices.lightcrafter_230np as _lcr
"""
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

PLATFORM_WINDOWS = platform.system() == "Windows"
if not PLATFORM_WINDOWS:
    WindowsError = FileNotFoundError

# ---------------------------------------------------------------------
# Main class
# ---------------------------------------------------------------------
class AppMQTT(QDSpyApp):

    def __init__(self):
        # Initialize queue for MQTT messages
        self._msgQueue = deque([])

        # Initialize
        super().__init__("MQTT client")
        self._isExitCmd = False

        # Lightcrafter instance
        '''
        self.LCr = _lcr.Lightcrafter(_initGPIO=False)
        '''

        # Connect to MQTT broker 
        self.logWrite("DEBUG", "Initiating MQTT ...")
        mqtt.Client.handler = self.handleMsg
        mqtt.Client.connect(ID=mgl.UUID, _isServ=True)
        self.logWrite("DEBUG", "... done")

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def updateAll(self, _onlyUpdate=False) -> None:
        """ Update the status
        In the MQTT version, it also needs to check for and handle new
        MQTT messages, otherwise the presentation cannot be interrupted
        """
        super().updateAll()
        if not _onlyUpdate:
            self.processMsg()
        
    # -------------------------------------------------------------------
    # Handle and process incoming MQTT messages
    # -------------------------------------------------------------------
    def handleMsg(self, _msg) -> None:
        """Handle incoming MQTT messages
        """
        self._isNewMsg = False
        sMsg = _msg.payload.decode("UTF8")
        data = sMsg.split(",")
        if mqtt.Client.checkCmd(data[0]):
            # Command is invalid
            # TODO: Publish an error message
            self.logWrite("ERROR", f"Invalid command (`{data[1]}`)")
           
        else:    
            # Add message to queue
            cmd = mgl.Command(data[0])
            self._msgQueue.append([cmd, data[1:]])


    def publishReply(self, _iMsg, 
                     _errC: stm.StimErrC = stm.StimErrC.ok
        ):
        """Publish a reply. If `_errC` is ok, the just send and "ok",
        otherwise send "error", an error code and an error message. 
        In both cases, the index of the message to which this is the reply
        is added
        """
        if _errC == stm.StimErrC.ok:
            mqtt.Client.publish(f"{mgl.Command.OK.value},{_iMsg}")
        else:                          
            mqtt.Client.publish(
                f"{mgl.Command.ERROR.value},{_iMsg},{_errC:d},"
                f"{self.Stim.getLastErrStr(_errC=_errC)}"
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def processMsg(self) -> None:
        """Takes a message from the queue, if there are any, and process
        it. Processes only one message at a time.
        """
        if not self._msgQueue or len(self._msgQueue) == 0:
            return

        msg = self._msgQueue.popleft()
        iMsg = msg[1][0]
        isAnswered = False
        errC = stm.StimErrC.ok

        if msg[0] == mgl.Command.LOAD:
            if self.state in [State.idle, State.ready]:  
                # Try loading the stimulus
                # "load,<msg index>,<stimulus file name>"
                fName = fsu.getQDSpyPath() +self.Conf.pathStim +msg[1][1]
                errC = self.loadStim(fName)

        elif msg[0] == mgl.Command.PLAY:
            # Play the currently loaded stimulus
            # "play,<msg index>"
            if self.state == State.ready:
                if not self.isStimReady or not self.isStimCurr:
                    # Error: Stimulus is not current and/or compiled
                    errC = stm.StimErrC.noStimOrNotCompiled
                else:        
                    # Stimulus is ready (=can be loaded) and is compiled
                    self.runStim()

        elif msg[0] == mgl.Command.STOP:
            # Stop stimulus if running
            if self.state == State.playing:
                self.abortStim()  

        elif msg[0] == mgl.Command.STATE:
            # Publish current state
            mqtt.Client.publish(
                f"{mgl.Command.STATE.value},{iMsg},{self.state:d},"
                f"{StateStr[self.state]}"
            )
            isAnswered = True

        elif msg[0] == mgl.Command.EXIT:
            # Exit programm
            if self.state == State.playing:
                self.abortStim()  
            self._isExitCmd = True

        elif msg[0] == mgl.Command.OPEN_LCR:
            # Open I2C connection to LCr
            if self.state not in [State.undefined, State.idle, State.canceling]:
                pass
                '''
                res = self.LCr.connect()
                if res[0] is not _lcr.ERROR.OK:        
                    errC = stm.StimErrC.DeviceError_LCr
                '''    

        elif msg[0] == mgl.Command.CLOSE_LCR:
            # Close I2C connection to LCr
            pass
            '''
            if self.state not in [State.undefined, State.idle]:
                res = self.LCr.disconnect()
            '''
            """
        elif msg[0] == mgl.Command.GET_LEDS:
            # Retrieve LED enabled/currents
            if not self.state in [State.undefined, State.idle, State.canceling]:
            """

        else:
            # Should not happen ...
            self.logWrite("ERROR", "processMsg, unknown command?")
            errC = stm.StimErrC.notYetImplemented

        if not isAnswered:
            # Publish a reply
            self.publishReply(iMsg, _errC=errC)
    

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
            isRunning = True
            while isRunning:
                try:
                    # Process any items in MQTT message queue
                    self.processMsg()
                    isRunning = not(self._isExitCmd)

                    # Process messages in the pipe to the worker and
                    # sleep for a bit    
                    self.processPipe()
                    time.sleep(glo.QDSpy_loop_sleep_s)

                    '''
                    if not mqtt.Client.is_connected:
                        pass
                    '''    
                    
                except KeyboardInterrupt:
                    self.logWrite("INFO", "User abort")
                    break

        finally:
            # Clean up
            self.closeEvent()
            
            # Stop MQTT client and close log file
            mqtt.Client.stop()                
            self.closeLogFile(self._logFile)

# ---------------------------------------------------------------------
# _____________________________________________________________________
if __name__ == "__main__":
    
    # Create main app instance and run main loop
    QDSApp = AppMQTT()
    QDSApp.loop()

# ---------------------------------------------------------------------
