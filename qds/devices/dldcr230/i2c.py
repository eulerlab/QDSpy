# i2c.py
#
# I2C interface that runs on Windows (using DeVaSys Adapter) or Linux
#
# Copyright (C) 2017 Texas Instruments Incorporated - http://www.ti.com/
#
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#   Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#
#   Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#
#   Neither the name of Texas Instruments Incorporated nor the names of
#   its contributors may be used to endorse or promote products derived
#   from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import sys
from logging import log, DEBUG

DEFAULT_SLAVE_ADDRESS = 0x36  # 8-bit I2C slave address
DEFAULT_I2C_BUS = 22  # 7 for SW-based I2C bus

_slave_address = DEFAULT_SLAVE_ADDRESS
_i2c = None
_debug = False


def initialize(slave_address=DEFAULT_SLAVE_ADDRESS, i2c_bus=DEFAULT_I2C_BUS):
    """
    :param slave_address: 8-bit I2C slave address.  For DPP2607, should be 0x34 or 0x36.
    :param i2c_bus: I2C bus number, for Linux only.
    """
    global _i2c, _slave_address
    if sys.platform == 'win32':
        import devasys
        _i2c = devasys.DeVaSys(slave_address)
        _i2c.open()
    else:
        import linuxi2c
        _i2c = linuxi2c.LinuxI2C(i2c_bus, slave_address)
        _i2c.open()
    _slave_address = slave_address


def terminate():
    global _i2c
    if _i2c:
        _i2c.close()
        _i2c = None


def write(data):
    """
    write to I2C port
    :type data: list[int]
    :rtype: None
    """
    if _debug:
        print(DEBUG, 'I2C.write: %s', _hexlist(data))
    _i2c.write(data)


def read(numbytes):
    """
    read from I2C port
    :type numbytes: int
    :rtype: list[int]
    """
    data = _i2c.read(numbytes)
    if _debug:
        print(DEBUG, 'I2C.read: %s', _hexlist(data))
    return data


def get_slave_address():
    return _slave_address


def set_debug(debug):
    global _debug
    _debug = debug


def get_debug():
    return _debug


def _hexlist(data):
    return '[%s]' % ', '.join([hex(b) for b in data])
