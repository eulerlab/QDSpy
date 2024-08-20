#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QDSpy module - MQTT-related global definitions  

Copyright (c) 2024 Thomas Euler
All rights reserved.

2024-08-03 - Initial version
"""
# ---------------------------------------------------------------------
__author__ 	= "code@eulerlab.de"

from enum import Enum

# fmt: off
# MQTT broker settings
broker_address   = "test.mosquitto.org" #"broker.hivemq.com"
broker_port      = 1883
broker_timeout_s = 60
topic_root       = "qds"
topic_serv       = ["cli", "srv"]

#UUID            = 'd6d09beb68a3448aa0d44747386e3fef'
UUID             = 'd6d09beb68a3448a'

class Command(Enum):
    LOAD      = "load"
    PLAY      = "play"
    STOP      = "stop"
    STATE     = "state"
    EXIT      = "exit"
    OPEN_LCR  = "open_lcr"
    CLOSE_LCR = "close_lcr"
    GET_LEDS  = "get_leds"
    SET_LEDS  = "set_leds"
    ERROR     = "error"
    OK        = "ok"

# fmt: on
# ---------------------------------------------------------------------
