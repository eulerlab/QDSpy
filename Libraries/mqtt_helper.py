#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QDSpy module - MQTT-related functions

Copyright (c) 2024 Thomas Euler
All rights reserved.

2024-08-03 - Initial version
"""
# ---------------------------------------------------------------------
__author__ 	= "code@eulerlab.de"

import platform
from types import FunctionType
import paho.mqtt.client as mqtt
import Libraries.log_helper as _log

PLATFORM_WINDOWS = platform.system == "Windows"
if not PLATFORM_WINDOWS:
    WindowsError = FileNotFoundError

# fmt: off
# MQTT broker settings
#broker_address  = "mqtt.eclipseprojects.io"
broker_address   = "broker.hivemq.com"
broker_port      = 1883
broker_timeout_s = 60
topic_root       = "qds"
# fmt: on

# ---------------------------------------------------------------------
class QDS_MQTT():
    '''MQTT class for QDSpy
    Use only instance of this class created in this module
    '''
    def __init__(self):
        # Create MQTT client instance 
        self._client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

        # Initialize and set callback functions
        self._debug = True
        self._is_running = False
        self._on_msg_handler = None
        self._client.on_connect = _on_connect
        self._client.on_message = _on_message

    def connect(self, ID: str):
        self._UUID = ID
        self.log("DEBUG", "MQTT|Connecting ...", _isProgress=True)
        self._client.connect(
            broker_address, broker_port, broker_timeout_s
        )

    def start(self) -> None:
        if not self._is_running:
            self.log("DEBUG", "MQTT|Start listening ...")
            self._client.loop_start()
            self._is_running = True

    def stop(self) -> None:
        if self._is_running:
            self.log("DEBUG", "MQTT|Stop listening")
            self._client.loop_stop()
            self._is_running = False

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @property
    def is_connected(self):
        self._client.is_connected()

    def handler(self, handler: FunctionType) -> None:
        self._on_msg_handler = handler

    handler = property(None, handler)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def log(self, header: str, msg: str, _isProgress: bool = False):
        if self._debug:
            _log.Log.write(header, msg, _isProgress=_isProgress)        

# ---------------------------------------------------------------------
# Callback functions
def _on_connect(client, userdata, flags, reason_code, properties):
    # Note: Subscribing in on_connect() means that if we lose the 
    # connection and reconnect then subscriptions will be renewed.
    if reason_code.is_failure:
        Client.log(
            "ERROR", 
            f"MQTT|Connection failed (`{reason_code}`)"
        )
    else:
        Client.log(
            "OK", 
            f"MQTT|Connected to `{broker_address}`")
        sTopic = f"{topic_root}/{Client._UUID}"
        Client._client.subscribe(sTopic)


def _on_message(client, userdata, msg):
    # The callback for when a PUBLISH message is received from the 
    # server.
    data = msg.payload.decode("UTF8")
    Client.log("DEBUG", f"Message `{msg.topic}`, `{data}`")
    print(data.split(","))
    if Client._on_msg_handler:
        Client._on_msg_handler(msg)

# ---------------------------------------------------------------------
Client = QDS_MQTT()

# ---------------------------------------------------------------------
