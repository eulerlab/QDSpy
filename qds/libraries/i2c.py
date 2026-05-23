#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QDSpy module - I2C class 

Copyright (c) 2024 Thomas Euler
All rights reserved.

2024-08-03 - Initial version
"""
# ---------------------------------------------------------------------
__author__ 	= "code@eulerlab.de"

import platform
import os

# ---------------------------------------------------------------------
# fmt: off
I2C_ADDRESS     = 0x36  # 8-bit I2C slave address
I2C_BUS         = 22    # 11  

# fmt: on

# ---------------------------------------------------------------------
def get_I2C_busses():
    if not platform.system() == "Linux":
        return []
    
    busses = []
    for bus in os.listdir("/dev"):
        if bus.startswith("i2c-"):
            busses.append(int(bus[4:]))
    return busses        
    
# ---------------------------------------------------------------------
class I2C(object):

    def __init__(self, debug: bool = True):
        # Initialize
        self._i2c = None
        self._isReady = False
        self._addr = 0
        self._bus = 0
        self._debug = debug


    def connect(self, _addr: int = I2C_ADDRESS, _bus: int = I2C_BUS) -> None:
        """Connect to I2C bus device at `_addr`
        """
        self._i2c = None
        self._addr = _addr
        self._bus = _bus

        # Try opening I2C port
        if platform.system() == "Linux":
            import Libraries.i2c_linux as i2c_linux
            self._i2c = i2c_linux.LinuxI2C(self._bus, self._addr)
            self._i2c.open()
        else:
            print("i2c|Error: Only implemented for Linux")
    
    
    def terminate(self) -> None:
        """Terminate connection to I2C bus
        """
        if self._i2c:
            self._i2c.close()
            self._i2c = None


    @property
    def is_connected(self) -> bool:
        return self._i2c is not None

    @property    
    def address(self) -> int:
        return self._addr
    
    @property
    def debug(self) -> bool:
        return self._debug
    
    @debug.setter
    def debug(self, value: bool):
        self._debug = value
    

    def write(self, data: list[int]) -> None:
        """Write data
        """
        if self._debug:
            print(f"i2c|Debug, write: {self._get_hexlist(data)}")
        self._i2c.write(data)


    def read(self, _n_bytes: int) -> list[int]:
        """Read data
        """
        data = self._i2c.read(_n_bytes)
        if self._debug:
            print(f"i2c|Debug, read: {self._get_hexlist(data)}")
        return data


    @staticmethod
    def _get_hexlist(data):
        return '[%s]' % ', '.join([hex(b) for b in data])
    
# ---------------------------------------------------------------------    
