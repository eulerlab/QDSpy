#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Lightcrafter 230NP API
Implements a Python class that covers a the subset of LCr functions

Copyright (c) 2024 Thomas Euler
All rights reserved.
"""
# ---------------------------------------------------------------------
__author__ = "thomas.euler@eulerlab.de"

# ---------------------------------------------------------------------
import time
#import platform
#import sys
#import os.path
from enum import Enum
from typing import List, Any
from types import FunctionType
import Devices.api.dlpc343x_xpr4 as dlp
import Devices.api.dlpc343x_xpr4_evm as dlp_evm
import Libraries.i2c as i2c

'''
python_dir = (os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
print("python_dir", python_dir)
sys.path.append(python_dir)
'''

class Set(Enum):
    Disabled = 0
    Enabled = 1

# fmt: off
# ---------------------------------------------------------------------
LC_deviceName    = "lcr230np"
LC_width         = 1920
LC_height        = 1080

LC_IDStr         = "LCr"

# fmt: on
# ---------------------------------------------------------------------
# Error codes and messages
#
class ERROR:
    OK                 = 0
    OPEN_FAILED        = -1
    TIME_OUT           = -2
    NO_RESPONSE        = -3
    NAK_ERROR          = -4
    COULD_NOT_CONNECT  = -5
    INVALID_PARAMS     = -6
    DEVICE_NOT_FOUND   = -7
    NOT_IMPLEMENTED    = -9


ErrorStr = dict([
    (ERROR.OK,                "ok"),
    (ERROR.OPEN_FAILED,       "Failed to open device"),
    (ERROR.TIME_OUT,          "Time-out"),
    (ERROR.NO_RESPONSE,       "No response from device"),
    (ERROR.NAK_ERROR,         "Command not acknowledged"),
    (ERROR.COULD_NOT_CONNECT, "Could not connect to device"),
    (ERROR.INVALID_PARAMS,    "One or more parameters are invalid"),
    (ERROR.DEVICE_NOT_FOUND,  "Device with this index not found"),
    (ERROR.NOT_IMPLEMENTED,   "Not yet implemented")]
)

# ---------------------------------------------------------------------
class Set(Enum):
    Disabled = 0
    Enabled = 1

# ---------------------------------------------------------------------
class LCException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

'''
# fmt: off
# ---------------------------------------------------------------------
class CMD_FORMAT_LIST:
    SOURCE_SEL         = [ 0x1A, 0x00, 0x01, 0]   # SOURCE_SEL
  # ...
'''

# fmt: on
# ---------------------------------------------------------------------
LCrDeviceList: List[Any] = []

# ---------------------------------------------------------------------
def enumerateLightcrafters(_funcLog: FunctionType = None):
    """Enumerate lightcrafter devices
    """
    if _funcLog:
        _funcLog("WARNING", f"Not implemented for `{LC_deviceName}`", 2)
    return []

# ---------------------------------------------------------------------
# Class representing a lightcrafter device
# ---------------------------------------------------------------------
class Lightcrafter:
    """
    Create and initialize lightcrafter object.

    =============== ==================================================
    Parameters:
    =============== ==================================================
    _isCheckOnly    | all functions only check parameters
    _funcLog        | external function for logging of the format:
                    | log(_sHeader, _sMsg, _logLevel)
    _logLevel       |
    _initGPIO       | if True, (re)configure GPIOs everytime a 
                    | connection is made (default: False)
    _i2c_delay_s    | if > 0, introduces a delay in the I2C 
                    | communication (default: 0)
    =============== ==================================================
    """
    def __init__(
            self, _isCheckOnly: bool = False, 
            _funcLog: FunctionType = None, _logLevel: int = 2,
            _initGPIO: bool = False, _i2c_delay_s: float = 0
        ):
        #self.LC = None
        #self.nSeq = 0
        self.devNum = 0
        self.isCheckOnly = _isCheckOnly
        self.lastMsgStr = ""
        self.funcLog = _funcLog
        self.logLevel = _logLevel
        self._initGPIO = _initGPIO
        self._delay_s = _i2c_delay_s
        self._isConnected = False

        # Create I2C instance and register the read/write Command in 
        # the library
        self._i2c = i2c.I2C(debug=False)
        self.protocoldata = dlp.ProtocolData()
        dlp.DLPC343X_XPR4init(self._read_command, self._write_command)

        if _isCheckOnly:
            return

    # -------------------------------------------------------------------
    # Connect and disconnect the device
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def connect(
            self, _devNum: int = -1, _addr: int = i2c.I2C_ADDRESS,
            _bus: int = i2c.I2C_BUS
        ):
        """
        Try connecting to a lightcrafter and return immediately with an
        error code if it fails. A device number (`_devNum`) can be given
        if multiple lightcrafters are connected.

        .. note:: Device number is ignored for LCr type `lcr230np`

        =============== ==================================================
        Parameters:
        =============== ==================================================
        _devNum         | device number (0,1,...)
        _addr           | I2C address
        _bus            | I2C bus
        =============== ==================================================
        """
        if not self.isCheckOnly:
            if not self._isConnected:
                # Try opening I2C connection 
                errC = ERROR.OK
                self.log(" ", "Trying to connect ...", 2)
                self._i2c.connect(_addr=_addr, _bus=_bus)

                # Initialize GPIOs, if requested
                if self._initGPIO: 
                    dlp_evm.initGPIO()

                if self._i2c.is_connected:
                    # Make a test read
                    summary, shortStatus = dlp.ReadShortStatus()
                    self._isConnected = summary.Successful
                    
                if not self._isConnected:
                    # Report error
                    errC = ERROR.COULD_NOT_CONNECT
                    self.log("ERROR", f"{ErrorStr[errC]} ({errC})", 0)
                    return [errC]
                else:
                    # Print short status report
                    print("----------------------")
                    print("Short Status Register:")
                    dlp_evm.printReg(shortStatus)
                    self.log("ok", f"Connected to {LC_deviceName}", 2)

        return [ERROR.OK]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def waitToConnect(
            self, _devNum: int = -1, _timeout: int = 10.0,
            _addr: int = i2c.I2C_ADDRESS, _bus: int = i2c.I2C_BUS
        ):
        """
        Try connecting to a lightcrafter until success or the timeout.
        Returns an error code if it fails. A device number (`_devNum`) can
        be given if multiple lightcrafters are connected.

        .. note:: Device number is ignored for LCr type `lcr230np`

        =============== ==================================================
        Parameters:
        =============== ==================================================
        _devNum         | device number (0,1,...)
        _timeout        | timeout in seconds
        =============== ==================================================
        """
        if self.isCheckOnly:
            return [ERROR.OK]

        t0 = time.time()
        res = [ERROR.OPEN_FAILED]
        lgl = self.logLevel
        self.logLevel = 1
        while (res[0] is not ERROR.OK) and (time.time() < t0 +_timeout):
            time.sleep(1.0)
            res = self.connect(_devNum=0, _addr=_addr, _bus=_bus)
        self.logLevel = lgl
        return res

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def disconnect(self):
        """
        Disconnects the lightcrafter.
        """
        if not self.isCheckOnly:
            if self._isConnected:
                self._i2c.terminate()
                self._isConnected = False
                self.log("ok", "Disconnected", 2)

        return [ERROR.OK]

    # -------------------------------------------------------------------
    def init_parallel_mode(self):
        """
        Initializes the Raspberry Pi's GPIO lines to communicate with the 
        DLPDLCR230NPEVM, and configures the DLPDLCR230NPEVM to project 
        RGB666 parallel video input received from the Raspberry Pi.
        It is recommended to execute this script upon booting the Raspberry 
        Pi.        
        """
        if self._isConnected:
            self.log(
                "INFO", 
                "Setting DLPC3436 Input Source to RPi...", 2
            )
            dlp.WriteDisplayImageCurtain(1, dlp.Color.Black)
            dlp.WriteSourceSelect(
                dlp.Source.ExternalParallelPort, Set.Disabled
            )
            dlp.WriteInputImageSize(1920, 1080)

            self.log(
                "INFO", 
                "Configuring DLPC3436 Source Settings for RPi...", 2
            )
            dlp.WriteActuatorGlobalDacOutputEnable(Set.Enabled)
            dlp.WriteExternalVideoSourceFormatSelect(
                dlp.ExternalVideoFormat.Rgb666
            )
            dlp.WriteVideoChromaChannelSwapSelect(
                dlp.ChromaChannelSwap.Cbcr
            )
            dlp.WriteParallelVideoControl(
                dlp.ClockSample.FallingEdge, 
                dlp.Polarity.ActiveHigh, dlp.Polarity.ActiveLow, 
                dlp.Polarity.ActiveLow
            )
            dlp.WriteColorCoordinateAdjustmentControl(0)
            summary, bitRate, pixelMapMode = dlp.ReadFpdLinkConfiguration()
            print("summary, bitRate, pixelMapMode", summary, bitRate, pixelMapMode)
            dlp.WriteDelay(50)
            time.sleep(1)
            dlp.WriteDisplayImageCurtain(0, dlp.Color.Black)

    # -------------------------------------------------------------------
    # Logging
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def log(self, _sHeader, _sMsg, _logLevel):
        # Write message to log
        #
        self.lastMsgStr = _sMsg
        if _logLevel <= self.logLevel:
            if self.funcLog is None:
                print(f"{_sHeader!s:>8} #{self.devNum:>2}:{_sMsg}")
            else:
                if self.devNum >= 0:
                    devStr = f" #{self.devNum}"
                else:
                    devStr = " unknown"
                self.funcLog(_sHeader, LC_IDStr +devStr +"|" +_sMsg)


    # =======================================================================
    # Read/write routines
    # -----------------------------------------------------------------------
    def _write_command(self, writebytes, protocoldata):
        """
        Issues a command over the software I2C bus to the DLPDLCR230NP EVM.
        Set to write to Bus 7 by default
        Some commands, such as Source Select (splash mode) may perform 
        asynchronous access to the EVM's onboard flash memory. If such 
        commands are used, it is recommended to provide appropriate command 
        delay to prevent I2C bus hangups.
        """
        #print("Write Command writebytes ", [hex(x) for x in writebytes])
        if self._delay_s > 0: 
            time.sleep(self._delay_s)
        try:            
            self._i2c.write(writebytes)       
        except IOError as err:
            raise ValueError(err)    


    def _read_command(self, readbytecount, writebytes, protocoldata):
        """
        Issues a read command over the software I2C bus to the DLPDLCR230NP
        EVM. Set to read from Bus 7 by default. Some commands, such as Source
        Select (splash mode) may perform asynchronous access to the EVM's 
        onboard flash memory. If such commands are used, it is recommended 
        to provide appropriate command delay to prevent I2C bus hangups.
        """
        #print("Read Command writebytes ", [hex(x) for x in writebytes])
        if self._i2c.is_connected:
            if self._delay_s > 0: 
                time.sleep(self._delay_s)  
            try:            
                self._i2c.write(writebytes) 
                readbytes = self._i2c.read(readbytecount)
                return readbytes
            except IOError as err:
                raise ValueError(err)    
            
        else:
            return None       

# ---------------------------------------------------------------------
