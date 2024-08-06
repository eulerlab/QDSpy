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
import time
import pickle
from datetime import timedelta
from multiprocessing import Process
import Libraries.multiprocess_helper as mpr
import QDSpy_stim as stm
import QDSpy_config as cfg
import QDSpy_GUI_support as gsu
import QDSpy_stage as stg
import QDSpy_global as glo
import QDSpy_core
import QDSpy_core_support as csp
from QDSpy_GUI_cam import CamWinClass
import Libraries.log_helper as _log
import Libraries.mqtt_client as mqtt
import Libraries.mqtt_globals as mgl

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

PLATFORM_WINDOWS = platform.system() == "Windows"
if not PLATFORM_WINDOWS:
    WindowsError = FileNotFoundError
    from ctypes import windll

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
# _____________________________________________________________________
if __name__ == "__main__":
    
    # Connect to MQTT broker 
    mqtt.Client.handler = msg_handler
    mqtt.Client.connect(ID=mgl.UUID)

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
