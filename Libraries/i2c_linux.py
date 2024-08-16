# ---------------------------------------------------------------------
# linuxi2c.py
#
# Linux-compatible I2C interface using ioctl
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
# ---------------------------------------------------------------------
import os
import fcntl

# ---------------------------------------------------------------------
class LinuxI2C(object):
    """Simple Linux I2C port access
    """
    # fmt: off
    I2C_ADDR   = 0x0703
    I2C_TENBIT = 0x0704
    # fmt: on

    def __init__(self, bus: int, addr: int) -> None:
        super(LinuxI2C, self).__init__()
        self._bus = bus
        self._addr = addr
        self._fd = None

    def open(self) -> None:
        self._fd = os.open(f"/dev/i2c-{self._bus:d}", os.O_RDWR)
        if self._fd < 0:
            raise IOError("Could not open I2C interface")
        self._set_address(self._addr)

    def close(self) -> None:
        if self._fd > 0:
            os.close(self._fd)
        self._fd = None

    def _set_addr(self, _addr: int) -> None:
        if self._fd > 0:
            if fcntl.ioctl(self._fd, self.I2C_TENBIT, 0) < 0:
                raise IOError("Cannot set 7 bit I2C addressing")
            if fcntl.ioctl(self._fd, self.I2C_SLAVE, _addr >> 1) < 0:
                raise IOError("Cannot set slave address")
        else:
            raise IOError("I2C interface is not open")

    def write(self, data: list[int]) -> None: 
        if self._fd > 0:
            wrbuff = bytearray(data)
            if os.write(self._fd, wrbuff) < 0:
                raise IOError("Cannot write to I2C interface")
        else:
            raise IOError("I2C interface is not open")

    def read(self, n_bytes: int) -> None:
        if self._fd > 0:
            rdbuff = os.read(self._fd, n_bytes)
            return list(bytearray(rdbuff))
        else:
            raise IOError("I2C interface is not open")

# ---------------------------------------------------------------------

