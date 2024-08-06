#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Digital I/O API

Digital I/O using different types of devices.
Supported are currently:
  - digital I/O card USB1024LS and PCIDIO24 from Measurement Computing
    (http://www.mccdaq.com/daq-software/universal-library.aspx)
  - Arduino (experimental)
  - Raspberry Pi (experimental)

Copyright (c) 2013-2024 Thomas Euler
All rights reserved.
"""
# ---------------------------------------------------------------------
__author__ = "code@eulerlab.de"

# ---------------------------------------------------------------------
import platform
import ctypes
from ctypes import byref
from . import digital_io_UL_const as ULConst
import serial

PLATFORM_WINDOWS = platform.system() == "Windows"
if not PLATFORM_WINDOWS:
    import gpiozero as gpio


# ---------------------------------------------------------------------
# General definitions
#
class devConst:
    NONE = -1
    PORT_A = 0
    PORT_B = 1
    PORT_C_LO = 2
    PORT_C_HI = 3
    DIGITAL_IN = 10
    DIGITAL_OUT = 11


# ---------------------------------------------------------------------
# Universal library(UL) devices (Measurement Computing)
#
class devTypeUL:
    none = 0
    USB1024LS = 118
    PCIDIO24 = 40


dictULDevices = dict([("USB1024LS", 118), ("PCIDIO24", 40)])

dictUL = dict(
    [
        (devConst.PORT_A, ULConst.FIRSTPORTA),
        (devConst.PORT_B, ULConst.FIRSTPORTB),
        (devConst.PORT_C_LO, ULConst.FIRSTPORTCL),
        (devConst.PORT_C_HI, ULConst.FIRSTPORTCH),
        (devConst.DIGITAL_IN, ULConst.DIGITALIN),
        (devConst.DIGITAL_OUT, ULConst.DIGITALOUT),
    ]
)


# ---------------------------------------------------------------------
# Arduino
#
class devTypeArduino:
    none = 0
    Uno = 1


# ---------------------------------------------------------------------
# Raspberry Pi
#
class devTypeRPi:
    none = 0
    RPi4B = 1


# ---------------------------------------------------------------------
# I/O base class
# ---------------------------------------------------------------------
class devIO(object):
    def __init__(self, _funcLog=None, _logLevel=2):
        # Initializing and testing the device
        #
        self.isReady = False
        self.devName = "n/a"
        self.devType = None
        self.funcLog = _funcLog
        self.logLevel = _logLevel

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _setIsReady(self):
        self.isReady = True
        self.log("ok", "I/O device '{0}' is ready".format(self.devName))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def configDPort(self, _port, _dir):
        # Configure digital port
        #
        pass

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def readDPort(self, _port):
        # Read byte from digital port
        #
        pass

    def writeDPort(self, _port, _val):
        # Write byte to digital port
        #
        pass

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def log(self, _sHeader, _sMsg, _logLevel=2):
        # Write message to log
        #
        self.lastMsgStr = _sMsg
        if _logLevel <= self.logLevel:
            if self.funcLog is None:
                print("{0!s:>8} #{1}:{2}".format(_sHeader, self.devName, _sMsg))
            else:
                self.funcLog(_sHeader, self.devName + "|" + _sMsg)


# =====================================================================
# I/O class for a Raspberry Pi using IO pins (experimental)
# ---------------------------------------------------------------------
class devIO_RPi(devIO, object):
    def __init__(self, _pinDin=26, _pinDOut=27, _funcLog=None):
        super(devIO_RPi, self).__init__(_funcLog)

        self.isReady = False
        self.devName = "Raspberry Pi"
        self.devType = devTypeRPi.RPi4B
        self._pinDIn = _pinDin
        self._pinDOut = _pinDOut
        self._DIn = gpio.Button(self._pinDIn)
        self._DOut = gpio.LED(self._pinDOut)
        self._setIsReady()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def configDPort(self, _port, _dir):
        # ...
        pass

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def readDPort(self, _port):
        if self.isReady:
            return self._DIn.is_pressed
        else:
            return 0

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def writeDPort(self, _port, _val):
        if self.isReady:
            self._DOut.value = _val > 0

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getPortFromStr(self, _portStr):
        # TODO
        return devConst.NONE


# =====================================================================
# I/O class using an Arduino
# ---------------------------------------------------------------------
class devIO_Arduino(devIO, object):
    def __init__(self, _boardNum, _baud, _funcLog=None):
        super(devIO_Arduino, self).__init__(_funcLog)

        self.isReady = False
        self.devName = "Arduino"
        self.devType = devTypeArduino.Uno
        self.COM = "COM{0}".format(_boardNum)
        self.baud = _baud

        try:
            self.serClient = serial.Serial(
                self.COM,
                self.baud,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=1.0,
                writeTimeout=None,
            )
            self.serClient.flushInput()
            self.serClient.flushOutput()
            if self.serClient.isOpen():
                self._setIsReady()
                return

        except serial.SerialException as e:
            pass

        self.log("ERROR", "Could not open {0}".format(self.COM))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def configDPort(self, _port, _dir):
        # ...
        pass

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def readDPort(self, _port):
        if self.isReady and self.serClient.in_waiting > 0:
            return 1 if self.serClient.read(1) == b"1" else 0
        return 0

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def writeDPort(self, _port, _val):
        if self.isReady:
            if _val > 0:
                self.serClient.write(b"1")
            else:
                self.serClient.write(b"0")

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getPortFromStr(self, _portStr):
        if _portStr.upper() == "A":
            return devConst.PORT_A
        return devConst.NONE


# =====================================================================
# I/O class using the Universal Library/Measurement Computing
# ---------------------------------------------------------------------
class devIO_UL(devIO, object):
    def __init__(self, _type, _boardNum, _devNum, _funcLog=None):
        super(devIO_UL, self).__init__(_funcLog)

        if _type == devTypeUL.none:
            return

        else:
            # Load respective hardware DLL
            #
            try:
                self.UL = ctypes.windll.cbw64
            except WindowsError:
                self.log("ERROR", "Driver library 'cbw64.dll' not found")
                return

            self.brdNum = _boardNum
            self.devNum = _devNum
            self.bData = 0
            self.cbData = ctypes.c_ushort(self.bData)
            dv = 0
            cdv = ctypes.c_int(dv)

            if _type == devTypeUL.USB1024LS:
                self.devName = "USB-1024LS"
                self.devType = devTypeUL.USB1024LS

            elif _type == devTypeUL.PCIDIO24:
                self.devName = "PCI-DIO24"
                self.devType = devTypeUL.PCIDIO24

            else:
                self.log("ERROR", "Unknown digital I/O device")
                return

            # Configure device
            #
            self.UL.cbGetConfig(
                ULConst.BOARDINFO,
                self.brdNum,
                self.devNum,
                ULConst.BIBOARDTYPE,
                ctypes.byref(cdv),
            )
            if cdv.value == self.devType:
                # Requested device is connected
                #
                self.PORT_A = ULConst.FIRSTPORTA
                self.PORT_B = ULConst.FIRSTPORTB
                self.PORT_CLo = ULConst.FIRSTPORTCL
                self.PORT_CHi = ULConst.FIRSTPORTCH
                self.DIGITAL_IN = ULConst.DIGITALIN
                self.DIGITAL_OUT = ULConst.DIGITALIN

                """
        # Get revision number of Universal Library
        #
        revNum    = ctypes.c_float()
        vxDRevNum = ctypes.c_float()
        UL.cbGetRevision(byref(revNum), byref(vxDRevNum))
        return revNum.value, vxDRevNum.value
        """
                # self.UL.cbFlashLED(self.brdNum)
                self._setIsReady()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def configDPort(self, _port, _dir):
        self.UL.cbDConfigPort(self.brdNum, dictUL[_port], dictUL[_dir])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def readDPort(self, _port):
        self.bData = 0
        self.UL.cbDIn(self.brdNum, dictUL[_port], byref(self.cbData))
        return self.cbData.value

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def writeDPort(self, _port, _val):
        self.UL.cbDOut(self.brdNum, dictUL[_port], _val)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getPortFromStr(self, _portStr):
        if _portStr.upper() == "A":
            return devConst.PORT_A
        if _portStr.upper() == "B":
            return devConst.PORT_B
        if _portStr.upper() == "CHI":
            return devConst.PORT_C_LO
        if _portStr.upper() == "CLO":
            return devConst.PORT_C_HI

        return devConst.NONE


# ---------------------------------------------------------------------
