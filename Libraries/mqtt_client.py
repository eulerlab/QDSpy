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
import Libraries.mqtt_globals as mgl

PLATFORM_WINDOWS = platform.system() == "Windows"
if not PLATFORM_WINDOWS:
    WindowsError = FileNotFoundError

# ---------------------------------------------------------------------
class QDS_MQTTClient(object):
    '''MQTT client class for QDSpy
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
            mgl.broker_address, mgl.broker_port, 
            mgl.broker_timeout_s
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
            f"MQTT|Connected to `{mgl.broker_address}`")
        sTopic = f"{mgl.topic_root}/{Client._UUID}"
        Client._client.subscribe(sTopic)


def _on_message(_client, userdata, msg):
    # The callback for when a PUBLISH message is received from the 
    # server.
    if Client._debug:
        data = msg.payload.decode("UTF8")
        Client.log("DEBUG", f"Message `{msg.topic}`, `{data}`")
    if Client._on_msg_handler:
        Client._on_msg_handler(msg)

# ---------------------------------------------------------------------
Client = QDS_MQTTClient()

# ---------------------------------------------------------------------
