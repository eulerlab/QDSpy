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
#import QDSpy_stim
import Libraries.log_helper as _log
import Libraries.mqtt_helper as mqtt

PLATFORM_WINDOWS = platform.system == "Windows"
if not PLATFORM_WINDOWS:
    WindowsError = FileNotFoundError

UUID  = 'd6d09beb68a3448aa0d44747386e3fef'

# ---------------------------------------------------------------------
def msg_handler(msg):
    pass

# ---------------------------------------------------------------------
def log(header: str, msg: str, _isProgress: bool = False):
    _log.Log.write(header, msg, _isProgress=_isProgress)

# ---------------------------------------------------------------------
# _____________________________________________________________________
if __name__ == "__main__":
    
    # Connect to MQTT broker 
    mqtt.Client.handler = msg_handler
    mqtt.Client.connect(ID=UUID)

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
