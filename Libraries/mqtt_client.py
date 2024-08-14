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
from enum import Enum
import paho.mqtt.client as mqtt
from Libraries.log_helper import Log
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
        # Initialize 
        self._debug = True
        self._is_running = False
        self._isServer = False
        self._topic = f"{mgl.topic_root}/{mgl.UUID}/"

        # Create MQTT client instance 
        self._client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

        # Set callback functions and other stuff
        self._unacked_publish = set()
        self._client.user_data_set(self._unacked_publish)
        self._on_msg_handler = None
        self._client.on_publish = _on_publish
        self._client.on_connect = _on_connect
        self._client.on_message = _on_message

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def connect(self, ID: str, _isServ: bool):
        self._UUID = ID
        self._isServ = _isServ
        self.log("DEBUG", "MQTT|Connecting ...")
        try:
            self._client.connect(
                mgl.broker_address, mgl.broker_port, 
                mgl.broker_timeout_s
            )
        except TimeoutError:
            self.log("ERROR", "MQTT|Timeout on connecting")
            #raise TimeoutError("MQTT timed-out")

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
    def publish(self, _msg: str, _doWait: bool = True) -> None:
        """Publish string `_msg` under the predefined topic
        (see `mqtt_globals.py`)
        """
        topic = self._topic +f"{mgl.topic_serv[not self._isServ]}"
        msg_info = self._client.publish(topic, _msg, qos=1)
        self._unacked_publish.add(msg_info.mid)
        if _doWait:
            msg_info.wait_for_publish()
        self.log("INFO", f"MQTT|<- `{topic} {_msg}`")

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @property
    def is_connected(self):
        self._client.is_connected()

    def handler(self, handler: FunctionType) -> None:
        self._on_msg_handler = handler

    handler = property(None, handler)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def checkCmd(self, _cmd: Enum):
        return _cmd not in [c.value for c in mgl.Command]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def log(self, _hdr: str, _msg: str, _isProg: bool = False):
        if self._debug:
            Log.write(_hdr, _msg, _isProgress=_isProg, _isWorker=False)        

# ---------------------------------------------------------------------
# Callback functions
def _on_connect(_client, userdata, flags, reason_code, properties):
    # Note: Subscribing in on_connect() means that if we lose the 
    # connection and reconnect then subscriptions will be renewed.
    if reason_code.is_failure:
        Client.log(
            "ERROR", 
            f"MQTT|Connection failed (`{reason_code}`)"
        )
    else:
        Client.log(
            "ok", 
            f"MQTT|Connected to `{mgl.broker_address}`")
        topic = Client._topic +f"{mgl.topic_serv[Client._isServ]}"
        Client._client.subscribe(topic)


def _on_message(_client, userdata, msg):
    # The callback for when a PUBLISH message is received from the 
    # server.
    if Client._debug:
        data = msg.payload.decode("UTF8")
        Client.log("INFO", f"MQTT|-> `{msg.topic} {data}`")
    if Client._on_msg_handler:
        Client._on_msg_handler(msg)


def _on_publish(_client, userdata, mid, reason_code, properties):
    # Note: `Reason_code` and `properties`` will only be present in
    #  MQTTv5. It's always unset in MQTTv3
    try:
        userdata.remove(mid)
    except KeyError:
        Client.log(
            "ERROR", 
            "`mid` not present in `unacked_publish`"
        )

# ---------------------------------------------------------------------
Client = QDS_MQTTClient()

# ---------------------------------------------------------------------
