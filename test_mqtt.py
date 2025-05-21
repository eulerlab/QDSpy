#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test program for MQTT version of QDSpy

Copyright (c) 2024-2025 Thomas Euler
All rights reserved.

2024-08-03 - Initial version
2025-03-30 - Use `QDSpy.ini`
"""
# ---------------------------------------------------------------------
__author__ 	= "code@eulerlab.de"

import platform
import time
import sys
import Libraries.mqtt_client as mqtt
import Libraries.mqtt_globals as mgl
import QDSpy_config as cfg

PLATFORM_WINDOWS = platform.system() == "Windows"
if not PLATFORM_WINDOWS:
    WindowsError = FileNotFoundError

# ---------------------------------------------------------------------
def handleMsg(_msg) -> None:
    pass

# ---------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) == 1:
        # If no command line argument, exit
        print("No arguments")
        sys.exit()

    # Load configuration, if any
    UUID = mgl.UUID
    broker = mgl.broker_address
    Conf = cfg.Config()
    if Conf.isLoaded:
        UUID = Conf.UUID
        broker = Conf.broker_address
    
    # Initialize
    iMsg = 0
    mqtt.Client.handler = handleMsg
    mqtt.Client.connect(_broker=broker, _ID=UUID, _isServ=False)
    mqtt.Client.start()

    # Convert command line arguments
    arg = sys.argv[1].split(",")
    msg = f"{arg[0]},{iMsg}"
    if len(arg[1:]) > 0:
        msg = msg +"," +",".join(arg[1:])
    mqtt.Client.publish(msg, _doWait=True)

    tDone = time.time() +1.0
    while tDone > time.time():
        time.sleep(0.02)

    mqtt.Client.stop()

# ---------------------------------------------------------------------
