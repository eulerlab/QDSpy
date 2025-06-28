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
import numpy as np # type: ignore
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

# Default config
LC_width         = 1920
LC_height        = 1080
LC_hsync_pol     = dlp.Polarity.ActiveLow
LC_vsync_pol     = dlp.Polarity.ActiveLow

LC_IDStr         = "LCr"

LC_logStrMaskL   = "{0:<22}: "
LC_logStrMaskR   = "{0:>22}: "

# Maximal LED driver currents (from manual)
LC_MAX_R         = 810
LC_MAX_G         = 810
LC_MAX_B         = 810

# fmt: off
# ---------------------------------------------------------------------
# Error codes and messages
#
class ERROR:
    OK                 = 0
    OPEN_FAILED        = -1
    TIME_OUT           = -2
    NO_RESPONSE        = -3
    COULD_NOT_CONNECT  = -5
    INVALID_PARAMS     = -6
    DEVICE_NOT_FOUND   = -7
    NOT_IMPLEMENTED    = -9
    IS_NOT_CONNECTED   = -10     
    SET_MODE_FAILED    = -11


ErrorStr = dict([
    (ERROR.OK,                "ok"),
    (ERROR.OPEN_FAILED,       "Failed to open device"),
    (ERROR.TIME_OUT,          "Time-out"),
    (ERROR.NO_RESPONSE,       "No response from device"),
    (ERROR.COULD_NOT_CONNECT, "Could not connect to device"),
    (ERROR.INVALID_PARAMS,    "One or more parameters are invalid"),
    (ERROR.DEVICE_NOT_FOUND,  "Device with this index not found"),
    (ERROR.NOT_IMPLEMENTED,   "Not yet implemented"),
    (ERROR.IS_NOT_CONNECTED,  "Is not connected"),
    (ERROR.SET_MODE_FAILED,   "Setting mode failed")]
)

# Source selection
class SourceSel(Enum):
    Parallel    = 0
    FPDLink     = 3

SourceSelStr = dict([
    (SourceSel.Parallel,    "parallel GPIO interface"),
    (SourceSel.FPDLink,     "FPD link")]
)

# Source bit width
class SourcePar(Enum):
    Bit18 = 6

SourceParStr = dict([
    (SourcePar.Bit18, "18 bit")]
)

# fmt: on
# ---------------------------------------------------------------------
'''
class Set(Enum):
    Disabled = 0
    Enabled = 1
'''
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
        #self.devNum = 0
        self.isCheckOnly = _isCheckOnly
        self.lastMsgStr = ""
        self.funcLog = _funcLog
        self.logLevel = _logLevel
        self._initGPIO = _initGPIO
        self._delay_s = _i2c_delay_s
        self._isConnected = False
        self._i2c_busses = i2c.get_I2C_busses()
        self._i2CBus = None

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
            self, _addr: int = i2c.I2C_ADDRESS, _bus: int = i2c.I2C_BUS
        ) -> list:
        """
        Try connecting to a lightcrafter and return immediately with an
        error code if it fails. 

        =============== ==================================================
        Parameters:
        =============== ==================================================
        _addr           | I2C address
        _bus            | I2C bus
        =============== ==================================================
        """
        if not self.isCheckOnly:
            if not self._isConnected:
                # Try opening I2C connection 
                errC = ERROR.OK
                self.log(" ", "Trying to connect ...", 2)

                if self._i2CBus is not None:
                    # Use the bus that has already been found
                    busses = [self._i2CBus]
                elif _bus is not None:
                    # Use the bus that was given
                    busses = [_bus]
                else:
                    # No bus was given; try all existing
                    busses = self._i2c_busses

                for bus in busses:
                    self.log(" ", f"Testing I2C bus {bus} ...", 2)
                    self._i2c.connect(_addr=_addr, _bus=bus)
                    if self._i2c.is_connected:
                        # Make a test read
                        summary, shortStatus = dlp.ReadShortStatus()
                        self._isConnected = summary.Successful
                        if self._isConnected:
                            break

                if not self._isConnected:
                    # Report error
                    errC = ERROR.COULD_NOT_CONNECT
                    self.log("ERROR", f"{ErrorStr[errC]} ({errC})", 0)
                    return [errC]
                else:
                    # Remember I2C bus
                    self._i2CBus = bus

                    # Initialize GPIOs, if requested
                    if self._initGPIO: 
                        dlp_evm.initGPIO()

                    # Print short status report
                    self.logStatus(dlp_evm.reg2Dict(shortStatus))
                    self.log("ok", f"Connected to {LC_deviceName}", 2)

        return [ERROR.OK]

    '''
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def waitToConnect(
            self, _timeout: int = 10.0,
            _addr: int = i2c.I2C_ADDRESS, _bus: int = i2c.I2C_BUS
        ):
        """
        Try connecting to a lightcrafter until success or the timeout.
        Returns an error code if it fails. 

        =============== ==================================================
        Parameters:
        =============== ==================================================
        _timeout        | timeout in seconds
        _addr           | I2C address
        _bus            | I2C bus
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
    '''
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def disconnect(self) -> list:
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
    # Input source and mode selection
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setInputSource(
            self, _source, _bitDepth = SourcePar.Bit18,
            _width: int = LC_width, _height: int = LC_height,
            _hsync: Enum = LC_hsync_pol, _vsync: Enum = LC_vsync_pol
        ) -> list:
        """
        Defines the input source of the device. Use enum classes `SourceSel`
        and `SourcePar` for `_source` and `_bitDepth`, respectively.

        .. note:: Options are currently limited for LCr type `lcr230np`

        =============== ==================================================
        Parameters:
        =============== ==================================================
        _source         | 0=parallel interface,
                        | 3=FPD-link (currently not used)
        _bitDepth       | Parallel interface bit depth
                        | 6=18 bits
        _width, _height | Screen size in pixels
        _hsync, _vsync  | Sync polarity                       
        =============== ==================================================
        """
        errC = ERROR.OK
        name = LC_logStrMaskL.format(self.setInputSource.__name__)
        excp = None

        if self.isCheckOnly:
            return [errC]
        if (_source not in SourceSel) or (_bitDepth not in SourcePar):
            errC = ERROR.INVALID_PARAMS
        if not self._isConnected:
            errC = ERROR.IS_NOT_CONNECTED
        if not _source == SourceSel.Parallel:
            errC = ERROR.NOT_IMPLEMENTED    
        
        if errC == ERROR.OK:
            # Initializes the Raspberry Pi's GPIO lines to communicate 
            # with the DLPDLCR230NPEVM, and configures it to project 
            # RGB666 parallel video input received from the RPi.
            try:
                # Setting to parallel input from RPi ...
                dlp.WriteDisplayImageCurtain(1, dlp.Color.Black)
                dlp.WriteSourceSelect(
                    dlp.Source.ExternalParallelPort, Set.Disabled
                )
                dlp.WriteInputImageSize(LC_width, LC_height)

                # Configuring DLPC3436 source settings for RPi ...
                dlp.WriteActuatorGlobalDacOutputEnable(Set.Enabled)
                dlp.WriteExternalVideoSourceFormatSelect(
                    dlp.ExternalVideoFormat.Rgb666
                )
                dlp.WriteVideoChromaChannelSwapSelect(
                    dlp.ChromaChannelSwap.Cbcr
                )
                dlp.WriteParallelVideoControl(
                    dlp.ClockSample.FallingEdge, 
                    dlp.Polarity.ActiveHigh, 
                    # dlp.Polarity.ActiveLow, # 1920 x 1020 
                    # dlp.Polarity.ActiveLow
                    _hsync, _vsync
                )
                dlp.WriteColorCoordinateAdjustmentControl(0)
                # --> TE: Does not make any sense, as just entered parallel config?!
                '''
                summary, bitRate, pixelMapMode = dlp.ReadFpdLinkConfiguration()
                if bitRate == 0:
                    errC = ERROR.SET_MODE_FAILED
                '''
                dlp.WriteDelay(50)
                time.sleep(1)
                dlp.WriteDisplayImageCurtain(0, dlp.Color.Black)

            except IOError:    
                errC = ERROR.NO_RESPONSE

        if errC == ERROR.OK:
            self.log(
                " ",
                f"{name} {LC_deviceName} set to {SourceSelStr[_source]} "
                f"({SourceParStr[_bitDepth]}, {_width}x{_height},"
                f" {'n/a'}, {'n/a'})", 2
            )
            return [errC]
        else:
            self.log(
                "ERROR", 
                f"{name} Failed with error `{ErrorStr[errC]}` "
                f"({'n/a' if excp is None else excp})", 2
            )
            raise LCException(errC)

    # -------------------------------------------------------------------
    # LED-related
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getLEDCurrents(self) -> list:
        """
        Get LED currents and returns these as list [code, [r,g,b]] with:

        =============== ==================================================
        Result:
        =============== ==================================================
        code            | 0=ok or error code
        [r,g,b]         | LED currents as fraction of max. current (0..1)
        =============== ==================================================
        """
        errC = ERROR.OK
        name = LC_logStrMaskL.format(self.getLEDCurrents.__name__)
        excp = None
        r = g = b = -1

        if self.isCheckOnly:
            return [errC]
        if not self._isConnected:
            errC = ERROR.IS_NOT_CONNECTED

        if errC == ERROR.OK:
            try:
                summary, r,g,b = dlp.ReadRgbLedCurrent()
                rgb = (r /LC_MAX_R, g /LC_MAX_G, b /LC_MAX_B)
                #print(summary, r,g,b, rgb)

            except IOError:    
                errC = ERROR.NO_RESPONSE

        if errC == ERROR.OK:
            self.log(
                " ", 
                f"{name} LED currents, RGB = {r},{g},{b}"
                f" ({rgb[0]:.2f},{rgb[1]:.2f},{rgb[2]:.2f} " 
                " % max. current)", 2
            )
            return [errC, rgb]
        else:
            self.log(
                "ERROR", 
                f"{name} Failed with error `{ErrorStr[errC]}` "
                f"({'n/a' if excp is None else excp})", 2
            )
            raise LCException(errC)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setLEDCurrents(self, _rgb: list[float]) -> list:
        """
        Set LED currents. Values inreasing the maximal LED current (as 
        defined above) aree clipped for safety reasons.

        =============== ==================================================
        Parameters:
        =============== ==================================================
        _rgb            | [r,g,b] with LED currents as fraction of max.
                        | current (0..1)
        =============== ==================================================
        """
        errC = ERROR.OK
        name = LC_logStrMaskL.format(self.setLEDCurrents.__name__)
        excp = None

        if self.isCheckOnly:
            return [errC]
        if not self._isConnected:
            errC = ERROR.IS_NOT_CONNECTED

        if errC == ERROR.OK:
            try:
                max_curr = np.array([LC_MAX_R, LC_MAX_G, LC_MAX_B])
                newRGB = np.array(_rgb) *max_curr
                newRGB = np.array(np.clip(newRGB, 0, max_curr), dtype=int)
                summary, locm = dlp.ReadLedOutputControlMethod()
                dlp.WriteLedOutputControlMethod(dlp.LedControlMethod.Manual)
                dlp.WriteRgbLedMaxCurrent(LC_MAX_R, LC_MAX_G, LC_MAX_B)
                dlp.WriteRgbLedCurrent(newRGB[0], newRGB[1], newRGB[2])
                dlp.WriteLedOutputControlMethod(locm)

            except IOError:    
                errC = ERROR.NO_RESPONSE

        if errC == ERROR.OK:
            self.log(
                " ", 
                f"{name} New LED currents, RGB = "
                f"{newRGB[0]},{newRGB[1]},{newRGB[2]}", 2
            )
            return [errC]
        else:
            self.log(
                "ERROR", 
                f"{name} Failed with error `{ErrorStr[errC]}` "
                f"({'n/a' if excp is None else excp})", 2
            )
            raise LCException(errC)

      # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getLEDEnabled(self) -> list:
        """
        Returns state of LED pins (enabled/disabled) as list 
        [code, [isR,isG,isB]] with:
        
        =============== ==================================================
        Result:
        =============== ==================================================
        code            | 0=ok or error code
        [isR,isG,isB]   | list of boolean values, one for each LED
        =============== ==================================================
        """
        errC = ERROR.OK
        name = LC_logStrMaskL.format(self.getLEDEnabled.__name__)
        excp = None
        rgb = [-1] *3

        if self.isCheckOnly:
            return [errC]
        if not self._isConnected:
            errC = ERROR.IS_NOT_CONNECTED

        if errC == ERROR.OK:
            try:
                summary, r, g, b = dlp.ReadRgbLedEnable()
                rgb = [r,g,b]

            except IOError:    
                errC = ERROR.NO_RESPONSE

        if errC == ERROR.OK:
            self.log(
                " ", 
                f"{name} LEDs enabled, RGB = "
                f"{rgb[0]},{rgb[1]},{rgb[2]}", 2
            )
            return [errC, rgb]
        else:
            self.log(
                "ERROR", 
                f"{name} Failed with error `{ErrorStr[errC]}` "
                f"({'n/a' if excp is None else excp})", 2
            )
            raise LCException(errC)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setLEDEnabled(self, _rgb: list[bool]) -> list:
        """
        Enable or disable LEDs 

        =============== ==================================================
        Parameters:
        =============== ==================================================
        _rgb            | list of boolean values, one for each LED
        =============== ==================================================
        """
        errC = ERROR.OK
        name = LC_logStrMaskL.format(self.setLEDEnabled.__name__)
        excp = None

        if self.isCheckOnly:
            return [errC]
        if not self._isConnected:
            errC = ERROR.IS_NOT_CONNECTED

        if errC == ERROR.OK:
            try:
                dlp.WriteRgbLedEnable(_rgb[0], _rgb[1], _rgb[2])

            except IOError:    
                errC = ERROR.NO_RESPONSE

        if errC == ERROR.OK:
            self.log(
                " ", 
                f"{name} New LEDs enabled, RGB = "
                f"{_rgb[0]},{_rgb[1]},{_rgb[2]}", 2
            )
            return [errC]
        else:
            self.log(
                "ERROR", 
                f"{name} Failed with error `{ErrorStr[errC]}` "
                f"({'n/a' if excp is None else excp})", 2
            )
            raise LCException(errC)

    # -------------------------------------------------------------------
    # Logging
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def log(self, _sHeader, _sMsg, _logLevel):
        ''' Write message to log
        '''
        self.lastMsgStr = _sMsg
        if _logLevel <= self.logLevel:
            if self.funcLog is None:
                print(f"{_sHeader!s:>8} {_sMsg}")
            else:
                self.funcLog(_sHeader, LC_IDStr +"|" +_sMsg)


    def logStatus(self, _status):
        ''' Log status
        '''
        self.log(" ", "--- Status ---", 2)
        pairs = list(_status)
        for keyval in pairs:
            name = LC_logStrMaskL.format(keyval[0])
            self.log(" ", f"{name} {keyval[1]}", 2)

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
