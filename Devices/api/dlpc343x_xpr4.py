#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) 2020 Texas Instruments Incorporated 
# http://www.ti.com/
#
# ---------------------------------------------------------------------
# NOTE: This file is auto generated from a command definition file.
#       Please do not modify the file directly.                    
#
# Command Spec Version : 1.0
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
#   documentation and/or other materials provided with the
#   distribution.
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
import struct
from enum import Enum
import sys
import os.path
from Devices.api.packer import *

python_dir = (os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(python_dir)

# ---------------------------------------------------------------------
class Source(Enum):
    FpgaTestPattern = 0
    ExternalParallelPort = 1
    ExternalFpdLink = 2
    SplashScreen = 3

class ChromaChannelSwap(Enum):
    Cbcr = 0
    Crcb = 1

class Enable(Enum):
    Disable = 0
    Enable = 1

class Polarity(Enum):
    ActiveLow = 0
    ActiveHigh = 1

class ClockSample(Enum):
    FallingEdge = 0
    RisingEdge = 1

class PassFail(Enum):
    Failed = 0
    Passed = 1

class ControllerDeviceId(Enum):
    Dlpc3430 = 0
    Dlpc3433 = 1
    Dlpc3432 = 2
    Dlpc3434 = 3
    Dlpc3435 = 4
    Dlpc3438 = 5
    Dlpc3436 = 6
    Dlpc3437 = 7
    Dlpc3472 = 8
    Dlpc3439 = 9
    Dlpc3440 = 10
    Dlpc3478 = 11
    Dlpc3479 = 12
    Dlpc3470 = 15

class ExternalVideoFormat(Enum):
    Rgb888 = 0
    Rgb565 = 1
    Rgb666 = 2
    YcbCr422 = 3
    YcbCr444 = 4
    YcbCr565 = 5
    YcbCr666 = 6

class Color(Enum):
    Black = 0
    Red = 1
    Green = 2
    Blue = 3
    Cyan = 4
    Magenta = 5
    Yellow = 6
    White = 7

class FpgaTestPatternColor(Enum):
    Black = 0
    Blue = 1
    Red = 2
    Magenta = 3
    Green = 4
    Cyan = 5
    Yellow = 6
    White = 7

class PixelFormats(Enum):
    Rgb888 = 0
    Rgb888P = 1
    Rgb565 = 2
    Ycbcr422 = 3

class CompressionTypes(Enum):
    Uncompressed = 0
    RgbRleCompressed = 1
    UserDefined = 2
    YuvRleCompressed = 3

class ColorOrders(Enum):
    Rgb = 0
    Grb = 1

class ChromaOrders(Enum):
    CrFirst = 0
    CbFirst = 1

class ByteOrders(Enum):
    LittleEndian = 0
    BigEndian = 1

class ImageFlip(Enum):
    ImageNotFlipped = 0
    ImageFlipped = 1

class DmdSequencerSyncMode(Enum):
    AutoSync = 0
    ForceLockToInternalVsync = 1

class SystemAutoSyncSetting(Enum):
    LockToExternalVsync = 0
    LockToInternalVsync = 1

class LedControlMethod(Enum):
    Manual = 0
    Automatic = 1

class LabbControl(Enum):
    Disabled = 0
    Manual = 1
    Automatic = 2

class CaicWpcControl(Enum):
    Disabled = 0
    Enabled = 1

class CaicModulationControl(Enum):
    Independent = 0
    Balanced = 1

class CaicGainControl(Enum):
    P1024 = 0
    P512 = 1

class SystemInit(Enum):
    NotComplete = 0
    Complete = 1

class Error(Enum):
    NoError = 0
    Error = 1

class FlashErase(Enum):
    Complete = 0
    NotComplete = 1

class Application(Enum):
    BootApp = 0
    MainApp = 1

class LedState(Enum):
    LedOff = 0
    LedOn = 1

class PowerSupply(Enum):
    SupplyVoltageNormal = 0
    SupplyVoltageLow = 1

class WatchdogTimeout(Enum):
    NoTimeoutError = 0
    TimeoutError = 1

class SubframeFiltered(Enum):
    NoSubframeFilterError = 0
    SubframeFilterError = 1

class MirrorLockOptions(Enum):
    DmdInterfaceReserved = 0
    DmdInterfaceLock = 1
    DmdInterfaceUnlock = 2
    DmdInterfaceUnlockDelay100MsDmdInterfaceLock = 3

class DmdDataSelection(Enum):
    DmdDeviceId = 0
    DmdFuseGroup0 = 1
    DmdFuseGroup1 = 2
    DmdFuseGroup2 = 3
    DmdFuseGroup3 = 4

class FpgaTestPattern(Enum):
    SolidField = 0
    Grid = 1
    HorizontalRamp = 2
    VerticalRamp = 3
    Checkerboard = 4
    HorizontalLines = 5
    VerticalLines = 6
    DiagonalLines = 7
    ActuatorCalibrationPattern = 8
    TestPattern3D = 9
    ColorBars = 10
    FrameAndCross = 11

class FpgaXprMode(Enum):
    NonXprMode = 0
    XprMode = 1

class Summary:
    Command: str
    CommInterface: str
    Successful: bool

class ProtocolData:
    CommandDestination: int
    OpcodeLength: int
    BytesRead: int

class SplashScreenHeader:
     WidthInPixels: int
     HeightInPixels: int
     SizeInBytes: int                       # long
     PixelFormat: PixelFormats
     CompressionType: CompressionTypes
     ColorOrder: ColorOrders
     ChromaOrder: ChromaOrders
     ByteOrder: ByteOrders

class AutoFramingInformation:
     VsyncRate: int                         # long
     TotalPixelsPerLine: int
     TotalLinesPerFrame: int
     TotalActivePixelsPerLine: int
     TotalActiveLinesPerFrame: int
     ReferenceClockRate: int

class SequenceHeaderAttributes:
     LookRedDutyCycle: float
     LookGreenDutyCycle: float
     LookBlueDutyCycle: float
     LookMaxFrameTime: float
     LookMinFrameTime: float
     LookMaxSequenceVectors: int
     SeqRedDutyCycle: float
     SeqGreenDutyCycle: float
     SeqBlueDutyCycle: float
     SeqMaxFrameTime: float
     SeqMinFrameTime: float
     SeqMaxSequenceVectors: int

class CaicImageProcessingControl:
     CaicWpcControl: CaicWpcControl
     CaicColorModulationControl: CaicModulationControl
     CaicGainControl: CaicGainControl
     CaicGainDisplayEnable: bool
     CaicMaxLumensGain: float
     CaicClippingThreshold: float

class ShortStatus:
     SystemInitialized: SystemInit
     CommunicationError: Error
     SystemError: Error
     FlashEraseComplete: FlashErase
     FlashError: Error
     Application: Application

class SystemStatus:
     DmdDeviceError: Error
     DmdInterfaceError: Error
     DmdTrainingError: Error
     RedLedState: LedState
     GreenLedState: LedState
     BlueLedState: LedState
     RedLedError: Error
     GreenLedError: Error
     BlueLedError: Error
     SequenceAbortError: Error
     SequenceError: Error
     SequenceBinNotFoundError: Error
     DcPowerSupply: PowerSupply
     ActuatorDriveEnable: Enable
     ActuatorPwmGenSource1080POnly: Enable
     ActuatorConfigurationError: Error
     ActuatorWatchdogTimerTimeout: WatchdogTimeout
     ActuatorSubframeFilteredStatus: SubframeFiltered

class CommunicationStatus:
     InvalidCommandError: Error
     InvalidCommandParameterValue: Error
     CommandProcessingError: Error
     FlashBatchFileError: Error
     ReadCommandError: Error
     InvalidNumberOfCommandParameters: Error
     BusTimeoutByDisplayError: Error
     AbortedOpCode: int

# ---------------------------------------------------------------------
_readcommand = None
_writecommand = None

# ---------------------------------------------------------------------
# Initialization
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def DLPC343X_XPR4init(readcommandcb, writecommandcb):
    global _readcommand
    global _writecommand
    _readcommand = readcommandcb
    _writecommand = writecommandcb

    global Summary
    Summary.CommInterface = "DLPC343X_XPR4"

    global PortocolData
    ProtocolData.CommandDestination = 0
    ProtocolData.OpcodeLength = 0
    ProtocolData.BytesRead = 0

# ---------------------------------------------------------------------
# Select image source
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def WriteSourceSelect(Source,  ExternalCalibrationEnable):
    """Selects the source of the image to be displayed.
    """
    global Summary
    Summary.Command = "Write Source Select"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',5))
        ProtocolData.OpcodeLength = 1;
        packerinit()
        value = setbits(Source.value, 3, 0)
        writebytes.extend(list(struct.pack('B',value)))
        packerinit()
        value = setbits(ExternalCalibrationEnable.value, 1, 0)
        writebytes.extend(list(struct.pack('B',value)))
        _writecommand(writebytes, ProtocolData)
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful == False
    finally:
        return Summary

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def ReadSourceSelect():
    """Reads the source of the image being displayed
    """
    global Summary
    Summary.Command = "Read Source Select"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',6))
        ProtocolData.OpcodeLength = 1;
        readbytes = _readcommand(2, writebytes, ProtocolData)
        readdata = struct.unpack_from ('B', bytearray(readbytes), 0)[0]
        packerinit(readdata)
        SourceObj = getbits(4, 0);
        readdata = struct.unpack_from ('B', bytearray(readbytes), 1)[0]
        packerinit(readdata)
        ExternalCalibrationEnableObj = getbits(1, 0);
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful = False
    finally:
        return Summary, Source(SourceObj), Enable(ExternalCalibrationEnableObj)

# ---------------------------------------------------------------------
# Image data size and parameters
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def WriteInputImageSize(PixelsPerLine,  LinesPerFrame):
    """Specifies the active data size of the external input image
    """
    global Summary
    Summary.Command = "Write Input Image Size"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',96))
        ProtocolData.OpcodeLength = 1;
        writebytes.extend(list(struct.pack('H',PixelsPerLine)))
        writebytes.extend(list(struct.pack('H',LinesPerFrame)))
        _writecommand(writebytes, ProtocolData)
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful == False
    finally:
        return Summary

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def ReadInputImageSize():
    """Reads the specified data size of the external input image
    """
    global Summary
    Summary.Command = "Read Input Image Size"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',97))
        ProtocolData.OpcodeLength = 1;
        readbytes = _readcommand(4, writebytes, ProtocolData)
        PixelsPerLine = struct.unpack_from ('H', bytearray(readbytes), 0)[0]
        LinesPerFrame = struct.unpack_from ('H', bytearray(readbytes), 2)[0]
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful = False
    finally:
        return Summary, PixelsPerLine, LinesPerFrame

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def WriteParallelVideoControl(
        PixelsClockSamplingEdge, IvalidPolarity,  
        HsyncPolarity, VsyncPolarity
    ):
    """Specifies the polarity of syncs and sampling edge of the pixel 
    clock
    """
    global Summary
    Summary.Command = "Write Parallel Video Control"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',107))
        ProtocolData.OpcodeLength = 1;
        packerinit()
        value = setbits(PixelsClockSamplingEdge.value, 1, 0)
        value = setbits(IvalidPolarity.value, 1, 1)
        value = setbits(HsyncPolarity.value, 1, 2)
        value = setbits(VsyncPolarity.value, 1, 3)
        writebytes.extend(list(struct.pack('B',value)))
        _writecommand(writebytes, ProtocolData)
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful == False
    finally:
        return Summary

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def ReadParallelVideoControl():
    """Specifies the polarity of syncs and sampling edge of the pixel 
    clock.
    """
    global Summary
    Summary.Command = "Read Parallel Video Control"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',108))
        ProtocolData.OpcodeLength = 1;
        readbytes = _readcommand(1, writebytes, ProtocolData)
        readdata = struct.unpack_from ('B', bytearray(readbytes), 0)[0]
        packerinit(readdata)
        PixelsClockSamplingEdgeObj = getbits(1, 0);
        IvalidPolarityObj = getbits(1, 1);
        HsyncPolarityObj = getbits(1, 2);
        VsyncPolarityObj = getbits(1, 3);
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful = False
    finally:
        return Summary, ClockSample(PixelsClockSamplingEdgeObj), \
            Polarity(IvalidPolarityObj), Polarity(HsyncPolarityObj), \
            Polarity(VsyncPolarityObj)

# ---------------------------------------------------------------------
# Splash screen related
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def WriteSplashScreenSelect(SplashScreenIndex):
    """Writes the index of a splash screen stored in flash
    """
    global Summary
    Summary.Command = "Write Splash Screen Select"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',13))
        ProtocolData.OpcodeLength = 1;
        writebytes.extend(list(struct.pack('B',SplashScreenIndex)))
        _writecommand(writebytes, ProtocolData)
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful == False
    finally:
        return Summary

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def ReadSplashScreenSelect():
    """Reads the index of a splash screen stored in flash
    """
    global Summary
    Summary.Command = "Read Splash Screen Select"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',14))
        ProtocolData.OpcodeLength = 1;
        readbytes = _readcommand(1, writebytes, ProtocolData)
        SplashScreenIndex = struct.unpack_from ('B', bytearray(readbytes), 0)[0]
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful = False
    finally:
        return Summary, SplashScreenIndex

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def ReadSplashScreenHeader(SplashScreenNumber):
    """Read Splash screen header
    """
    global Summary
    Summary.Command = "Read Splash Screen Header"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',15))
        ProtocolData.OpcodeLength = 1;
        writebytes.extend(list(struct.pack('B',SplashScreenNumber)))
        readbytes = _readcommand(13, writebytes, ProtocolData)
        SplashScreenHeader.WidthInPixels = struct.unpack_from ('H', bytearray(readbytes), 0)[0]
        SplashScreenHeader.HeightInPixels = struct.unpack_from ('H', bytearray(readbytes), 2)[0]
        SplashScreenHeader.SizeInBytes = struct.unpack_from ('I', bytearray(readbytes), 4)[0]
        SplashScreenHeader.PixelFormat = struct.unpack_from ('B', bytearray(readbytes), 8)[0]
        SplashScreenHeader.CompressionType = struct.unpack_from ('B', bytearray(readbytes), 9)[0]
        SplashScreenHeader.ColorOrder = struct.unpack_from ('B', bytearray(readbytes), 10)[0]
        SplashScreenHeader.ChromaOrder = struct.unpack_from ('B', bytearray(readbytes), 11)[0]
        SplashScreenHeader.ByteOrder = struct.unpack_from ('B', bytearray(readbytes), 12)[0]
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful = False
    finally:
        return Summary, SplashScreenHeader

# ---------------------------------------------------------------------
# External video format and FPD link
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def WriteExternalVideoSourceFormatSelect(VideoFormat):
    """Specifies the external video data format
    """
    global Summary
    Summary.Command = "Write External Video Source Format Select"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',109))
        ProtocolData.OpcodeLength = 1;
        writebytes.extend(list(struct.pack('B',VideoFormat.value)))
        _writecommand(writebytes, ProtocolData)
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful == False
    finally:
        return Summary

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def ReadExternalVideoSourceFormatSelect():
    """Reads the external video data format
    """
    global Summary
    Summary.Command = "Read External Video Source Format Select"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',110))
        ProtocolData.OpcodeLength = 1;
        readbytes = _readcommand(1, writebytes, ProtocolData)
        VideoFormatObj = struct.unpack_from ('B', bytearray(readbytes), 0)[0]
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful = False
    finally:
        return Summary, ExternalVideoFormat(VideoFormatObj)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def WriteFpdLinkConfiguration(BitRate,  PixelMapMode):
    """Specifies the FPD Link bit rate and pixel map mode
    """
    global Summary
    Summary.Command = "Write Fpd Link Configuration"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',75))
        ProtocolData.OpcodeLength = 1;
        writebytes.extend(list(struct.pack('H',BitRate)))
        writebytes.extend(list(struct.pack('B',PixelMapMode)))
        _writecommand(writebytes, ProtocolData)
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful == False
    finally:
        return Summary

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def ReadFpdLinkConfiguration():
    """Reads the FPD Link bit rate and pixel map mode
    """
    global Summary
    Summary.Command = "Read Fpd Link Configuration"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',76))
        ProtocolData.OpcodeLength = 1;
        readbytes = _readcommand(3, writebytes, ProtocolData)
        BitRate = struct.unpack_from ('H', bytearray(readbytes), 0)[0]
        PixelMapMode = struct.unpack_from ('B', bytearray(readbytes), 2)[0]
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful = False
    finally:
        return Summary, BitRate, PixelMapMode

# ---------------------------------------------------------------------
# Chroma channels
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def WriteVideoChromaChannelSwapSelect(ChromaChannelSwap):
    """Specifies the chroma channel swap to be applied to an incoming 
    YUV422 source
    """
    global Summary
    Summary.Command = "Write Video Chroma Channel Swap Select"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',77))
        ProtocolData.OpcodeLength = 1;
        packerinit()
        value = setbits(ChromaChannelSwap.value, 1, 3)
        writebytes.extend(list(struct.pack('B',value)))
        _writecommand(writebytes, ProtocolData)
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful == False
    finally:
        return Summary

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def ReadVideoChromaChannelSwapSelect():
    """Reads the chroma channel swap being applied to an incoming 
    YUV22 source
    """
    global Summary
    Summary.Command = "Read Video Chroma Channel Swap Select"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',78))
        ProtocolData.OpcodeLength = 1;
        readbytes = _readcommand(1, writebytes, ProtocolData)
        readdata = struct.unpack_from ('B', bytearray(readbytes), 0)[0]
        packerinit(readdata)
        ChromaChannelSwapObj = getbits(1, 3);
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful = False
    finally:
        return Summary, ChromaChannelSwap(ChromaChannelSwapObj)

# ---------------------------------------------------------------------
# Frame sync-related
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def ReadAutoFramingInformation():
    """Reads VSYNC rate, total pixel, and total lines for the display 
    module
    """
    global Summary
    Summary.Command = "Read Auto Framing Information"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',186))
        ProtocolData.OpcodeLength = 1;
        readbytes = _readcommand(14, writebytes, ProtocolData)
        AutoFramingInformation.VsyncRate = struct.unpack_from ('I', bytearray(readbytes), 0)[0]
        AutoFramingInformation.TotalPixelsPerLine = struct.unpack_from ('H', bytearray(readbytes), 4)[0]
        AutoFramingInformation.TotalLinesPerFrame = struct.unpack_from ('H', bytearray(readbytes), 6)[0]
        AutoFramingInformation.TotalActivePixelsPerLine = struct.unpack_from ('H', bytearray(readbytes), 8)[0]
        AutoFramingInformation.TotalActiveLinesPerFrame = struct.unpack_from ('H', bytearray(readbytes), 10)[0]
        AutoFramingInformation.ReferenceClockRate = struct.unpack_from ('H', bytearray(readbytes), 12)[0]
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful = False
    finally:
        return Summary, AutoFramingInformation

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def ReadDmdSequencerSyncMode():
    """Reads the state of the DMD sequencer sync mode function of the 
    display module
    """
    global Summary
    Summary.Command = "Read Dmd Sequencer Sync Mode"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',44))
        ProtocolData.OpcodeLength = 1;
        readbytes = _readcommand(1, writebytes, ProtocolData)
        readdata = struct.unpack_from ('B', bytearray(readbytes), 0)[0]
        packerinit(readdata)
        DmdSequencerSyncModeObj = getbits(1, 0);
        SystemAutoSyncSettingObj = getbits(1, 1);
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful = False
    finally:
        return Summary, DmdSequencerSyncMode(DmdSequencerSyncModeObj), \
            SystemAutoSyncSetting(SystemAutoSyncSettingObj)

# ---------------------------------------------------------------------
# Image orientation, curtain, freeze, mirror lock etc.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def WriteDisplayImageOrientation(
        LongAxisImageFlip,  ShortAxisImageFlip
    ):
    """Specifies the image orientation of the displayed image for the 
    display module
    """
    global Summary
    Summary.Command = "Write Display Image Orientation"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',20))
        ProtocolData.OpcodeLength = 1;
        packerinit()
        value = setbits(LongAxisImageFlip.value, 1, 1)
        value = setbits(ShortAxisImageFlip.value, 1, 2)
        writebytes.extend(list(struct.pack('B',value)))
        _writecommand(writebytes, ProtocolData)
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful == False
    finally:
        return Summary

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def ReadDisplayImageOrientation():
    """Reads the state of the displayed image orientation function for 
    the display module
    """
    global Summary
    Summary.Command = "Read Display Image Orientation"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',21))
        ProtocolData.OpcodeLength = 1;
        readbytes = _readcommand(1, writebytes, ProtocolData)
        readdata = struct.unpack_from ('B', bytearray(readbytes), 0)[0]
        packerinit(readdata)
        LongAxisImageFlipObj = getbits(1, 1);
        ShortAxisImageFlipObj = getbits(1, 2);
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful = False
    finally:
        return Summary, ImageFlip(LongAxisImageFlipObj), ImageFlip(ShortAxisImageFlipObj)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def WriteDisplayImageCurtain(Enable,  Color):
    """Controls the display image curtain for the display module
    """
    global Summary
    Summary.Command = "Write Display Image Curtain"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',22))
        ProtocolData.OpcodeLength = 1;
        packerinit()
        value = setbits(int(Enable), 1, 0)
        value = setbits(Color.value, 3, 1)
        writebytes.extend(list(struct.pack('B',value)))
        _writecommand(writebytes, ProtocolData)
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful == False
    finally:
        return Summary

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def ReadDisplayImageCurtain():
    """Reads the state of the image curtain control function for the 
    display module
    """
    global Summary
    Summary.Command = "Read Display Image Curtain"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',23))
        ProtocolData.OpcodeLength = 1;
        readbytes = _readcommand(1, writebytes, ProtocolData)
        readdata = struct.unpack_from ('B', bytearray(readbytes), 0)[0]
        packerinit(readdata)
        Enable = getbits(1, 0);
        ColorObj = getbits(3, 1);
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful = False
    finally:
        return Summary, Enable, Color(ColorObj)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def WriteImageFreeze(Enable):
    """Enables or disables the image freeze function for the display 
    module
    """
    global Summary
    Summary.Command = "Write Image Freeze"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',26))
        ProtocolData.OpcodeLength = 1;
        writebytes.extend(list(struct.pack('B',Enable)))
        _writecommand(writebytes, ProtocolData)
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful == False
    finally:
        return Summary

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def ReadImageFreeze():
    """Reads the state of the image freeze function for the display 
    module
    """
    global Summary
    Summary.Command = "Read Image Freeze"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',27))
        ProtocolData.OpcodeLength = 1;
        readbytes = _readcommand(1, writebytes, ProtocolData)
        Enable = struct.unpack_from ('?', bytearray(readbytes), 0)[0]
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful = False
    finally:
        return Summary, Enable

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def WriteMirrorLock(MirrorLockOption):
    """This command is used to lock/unlock the DMD interface for 
    optical alignment
    """
    global Summary
    Summary.Command = "Write Mirror Lock"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',57))
        ProtocolData.OpcodeLength = 1;
        packerinit()
        value = setbits(MirrorLockOption.value, 2, 0)
        writebytes.extend(list(struct.pack('B',value)))
        _writecommand(writebytes, ProtocolData)
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful == False
    finally:
        return Summary

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def ReadMirrorLock():
    """Reads the lock/unlock state of the DMD interface for optical 
    alignment
    """
    global Summary
    Summary.Command = "Read Mirror Lock"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',58))
        ProtocolData.OpcodeLength = 1;
        readbytes = _readcommand(1, writebytes, ProtocolData)
        readdata = struct.unpack_from ('B', bytearray(readbytes), 0)[0]
        packerinit(readdata)
        MirrorLockOptionObj = getbits(2, 0);
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful = False
    finally:
        return Summary, MirrorLockOptions(MirrorLockOptionObj)

# ---------------------------------------------------------------------
# Keysstone projection control
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def WriteKeystoneProjectionPitchAngle(PitchAngle):
    """Specifies the projection pitch angle for the display module
    """
    global Summary
    Summary.Command = "Write Keystone Projection Pitch Angle"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',187))
        ProtocolData.OpcodeLength = 1;
        writebytes.extend(list(struct.pack('H',int(convertfloattofixed(PitchAngle,256)))))
        _writecommand(writebytes, ProtocolData)
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful == False
    finally:
        return Summary

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def ReadKeystoneProjectionPitchAngle():
    """Reads the specified projection pitch angle for the display 
    module
    """
    global Summary
    Summary.Command = "Read Keystone Projection Pitch Angle"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',188))
        ProtocolData.OpcodeLength = 1;
        readbytes = _readcommand(2, writebytes, ProtocolData)
        PitchAngle = convertfixedtofloat(struct.unpack_from ('H', bytearray(readbytes), 0)[0], 256)
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful = False
    finally:
        return Summary, PitchAngle

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def WriteKeystoneCorrectionControl(
        KeystoneCorrectionEnable,  OpticalThrowRatio,  OpticalDmdOffset,  
        AnchorControlSteps
    ):
    "Controls the keystone correction image processing functionality for the display module."
    global Summary
    Summary.Command = "Write Keystone Correction Control"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',136))
        ProtocolData.OpcodeLength = 1;
        writebytes.extend(list(struct.pack('B',KeystoneCorrectionEnable)))
        writebytes.extend(list(struct.pack('H',int(convertfloattofixed(OpticalThrowRatio,256)))))
        writebytes.extend(list(struct.pack('H',int(convertfloattofixed(OpticalDmdOffset,256)))))
        writebytes.extend(list(struct.pack('H',AnchorControlSteps)))
        _writecommand(writebytes, ProtocolData)
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful == False
    finally:
        return Summary

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def ReadKeystoneCorrectionControl():
    """Reads the state of the keystone correction image processing 
    within the display module
    """
    global Summary
    Summary.Command = "Read Keystone Correction Control"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',137))
        ProtocolData.OpcodeLength = 1;
        readbytes = _readcommand(7, writebytes, ProtocolData)
        KeystoneCorrectionEnable = struct.unpack_from ('?', bytearray(readbytes), 0)[0]
        OpticalThrowRatio = convertfixedtofloat(struct.unpack_from ('H', bytearray(readbytes), 1)[0], 256)
        OpticalDmdOffset = convertfixedtofloat(struct.unpack_from ('H', bytearray(readbytes), 3)[0], 256)
        AnchorControlSteps = struct.unpack_from ('H', bytearray(readbytes), 5)[0]
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful = False
    finally:
        return Summary, KeystoneCorrectionEnable, OpticalThrowRatio, OpticalDmdOffset, AnchorControlSteps

# ---------------------------------------------------------------------
# Flash related
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def WriteExecuteFlashBatchFile(BatchFileNumber):
    """Executes a flash batch file
    """
    global Summary
    Summary.Command = "Write Execute Flash Batch File"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',45))
        ProtocolData.OpcodeLength = 1;
        writebytes.extend(list(struct.pack('B',BatchFileNumber)))
        _writecommand(writebytes, ProtocolData)
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful == False
    finally:
        return Summary


# ---------------------------------------------------------------------
# Timing control (?)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def WriteDelay(DelayInMicroseconds):
    """Delays for the specified number of microseconds
    """
    global Summary
    Summary.Command = "Write Delay"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',219))
        ProtocolData.OpcodeLength = 1;
        writebytes.extend(list(struct.pack('B',DelayInMicroseconds)))
        _writecommand(writebytes, ProtocolData)
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful == False
    finally:
        return Summary

# ---------------------------------------------------------------------
# LED related
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def WriteLedOutputControlMethod(LedControlMethod):
    """Specifies the method for controlling the LED outputs for the 
    display module
    """
    global Summary
    Summary.Command = "Write Led Output Control Method"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',80))
        ProtocolData.OpcodeLength = 1;
        writebytes.extend(list(struct.pack('B',LedControlMethod.value)))
        _writecommand(writebytes, ProtocolData)
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful == False
    finally:
        return Summary

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def ReadLedOutputControlMethod():
    """Reads the state of the LED output control method for the 
    display module
    """
    global Summary
    Summary.Command = "Read Led Output Control Method"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',81))
        ProtocolData.OpcodeLength = 1;
        readbytes = _readcommand(1, writebytes, ProtocolData)
        LedControlMethodObj = struct.unpack_from ('B', bytearray(readbytes), 0)[0]
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful = False
    finally:
        return Summary, LedControlMethod(LedControlMethodObj)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def WriteRgbLedEnable(
        RedLedEnable,  GreenLedEnable,  BlueLedEnable
    ):
    """Enables the LEDs for the display module
    """
    global Summary
    Summary.Command = "Write Rgb Led Enable"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',82))
        ProtocolData.OpcodeLength = 1;
        packerinit()
        value = setbits(int(RedLedEnable), 1, 0)
        value = setbits(int(GreenLedEnable), 1, 1)
        value = setbits(int(BlueLedEnable), 1, 2)
        writebytes.extend(list(struct.pack('B',value)))
        _writecommand(writebytes, ProtocolData)
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful == False
    finally:
        return Summary

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def ReadRgbLedEnable():
    """Reads the state of the LED enables for the display module
    """
    global Summary
    Summary.Command = "Read Rgb Led Enable"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',83))
        ProtocolData.OpcodeLength = 1;
        readbytes = _readcommand(1, writebytes, ProtocolData)
        readdata = struct.unpack_from ('B', bytearray(readbytes), 0)[0]
        packerinit(readdata)
        RedLedEnable = getbits(1, 0);
        GreenLedEnable = getbits(1, 1);
        BlueLedEnable = getbits(1, 2);
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful = False
    finally:
        return Summary, RedLedEnable, GreenLedEnable, BlueLedEnable

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def WriteRgbLedCurrent(RedLedCurrent,  GreenLedCurrent,  BlueLedCurrent):
    """Sets the current for the red, green, and blue LEDs of the 
    display module
    """
    global Summary
    Summary.Command = "Write Rgb Led Current"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',84))
        ProtocolData.OpcodeLength = 1;
        writebytes.extend(list(struct.pack('H',RedLedCurrent)))
        writebytes.extend(list(struct.pack('H',GreenLedCurrent)))
        writebytes.extend(list(struct.pack('H',BlueLedCurrent)))
        _writecommand(writebytes, ProtocolData)
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful == False
    finally:
        return Summary

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def ReadRgbLedCurrent():
    """Reads the state of the current for the red, green, and blue 
    LEDs of the display module
    """
    global Summary
    Summary.Command = "Read Rgb Led Current"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',85))
        ProtocolData.OpcodeLength = 1;
        readbytes = _readcommand(6, writebytes, ProtocolData)
        RedLedCurrent = struct.unpack_from ('H', bytearray(readbytes), 0)[0]
        GreenLedCurrent = struct.unpack_from ('H', bytearray(readbytes), 2)[0]
        BlueLedCurrent = struct.unpack_from ('H', bytearray(readbytes), 4)[0]
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful = False
    finally:
        return Summary, RedLedCurrent, GreenLedCurrent, BlueLedCurrent

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def ReadCaicLedMaxAvailablePower():
    """Reads the specified maximum LED power allowed for the display 
    module
    """
    global Summary
    Summary.Command = "Read Caic Led Max Available Power"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',87))
        ProtocolData.OpcodeLength = 1;
        readbytes = _readcommand(2, writebytes, ProtocolData)
        MaxLedPower = convertfixedtofloat(struct.unpack_from ('H', bytearray(readbytes), 0)[0], 100)
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful = False
    finally:
        return Summary, MaxLedPower

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def WriteRgbLedMaxCurrent(
        MaxRedLedCurrent,  MaxGreenLedCurrent,  MaxBlueLedCurrent
    ):
    """Specifies the maximum LED current allowed for each LED in the 
    display module
    """
    global Summary
    Summary.Command = "Write Rgb Led Max Current"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',92))
        ProtocolData.OpcodeLength = 1;
        writebytes.extend(list(struct.pack('H',MaxRedLedCurrent)))
        writebytes.extend(list(struct.pack('H',MaxGreenLedCurrent)))
        writebytes.extend(list(struct.pack('H',MaxBlueLedCurrent)))
        _writecommand(writebytes, ProtocolData)
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful == False
    finally:
        return Summary

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def ReadRgbLedMaxCurrent():
    """Reads the specified maximum LED current allowed for each LED in 
    the display module
    """
    global Summary
    Summary.Command = "Read Rgb Led Max Current"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',93))
        ProtocolData.OpcodeLength = 1;
        readbytes = _readcommand(6, writebytes, ProtocolData)
        MaxRedLedCurrent = struct.unpack_from ('H', bytearray(readbytes), 0)[0]
        MaxGreenLedCurrent = struct.unpack_from ('H', bytearray(readbytes), 2)[0]
        MaxBlueLedCurrent = struct.unpack_from ('H', bytearray(readbytes), 4)[0]
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful = False
    finally:
        return Summary, MaxRedLedCurrent, MaxGreenLedCurrent, MaxBlueLedCurrent

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def ReadCaicRgbLedCurrent():
    """Reads the state of the current for the red, green, and blue LEDs of 
    the display module
    """
    global Summary
    Summary.Command = "Read Caic Rgb Led Current"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',95))
        ProtocolData.OpcodeLength = 1;
        readbytes = _readcommand(6, writebytes, ProtocolData)
        RedLedCurrent = struct.unpack_from ('H', bytearray(readbytes), 0)[0]
        GreenLedCurrent = struct.unpack_from ('H', bytearray(readbytes), 2)[0]
        BlueLedCurrent = struct.unpack_from ('H', bytearray(readbytes), 4)[0]
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful = False
    finally:
        return Summary, RedLedCurrent, GreenLedCurrent, BlueLedCurrent

# ---------------------------------------------------------------------
# Image presentation
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def WriteLookSelect(LookNumber):
    """Specifies the LOOK for the image on the display module. 
    A LOOK typically specifies a target white point
    """
    global Summary
    Summary.Command = "Write Look Select"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',34))
        ProtocolData.OpcodeLength = 1;
        writebytes.extend(list(struct.pack('B',LookNumber)))
        _writecommand(writebytes, ProtocolData)
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful == False
    finally:
        return Summary

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def ReadLookSelect():
    """Reads the state of the LOOK select command for the display 
    module
    """
    global Summary
    Summary.Command = "Read Look Select"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',35))
        ProtocolData.OpcodeLength = 1;
        readbytes = _readcommand(6, writebytes, ProtocolData)
        LookNumber = struct.unpack_from ('B', bytearray(readbytes), 0)[0]
        SequenceIndex = struct.unpack_from ('B', bytearray(readbytes), 1)[0]
        SequenceFrameTime = convertfixedtofloat(struct.unpack_from ('I', bytearray(readbytes), 2)[0], 15)
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful = False
    finally:
        return Summary, LookNumber, SequenceIndex, SequenceFrameTime
    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def WriteCmtSelect(DegammaCmtIndex):
    """Specifies the Degamma/CMT LUT for the display module
    """
    global Summary
    Summary.Command = "Write Cmt Select"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',39))
        ProtocolData.OpcodeLength = 1;
        writebytes.extend(list(struct.pack('B',DegammaCmtIndex)))
        _writecommand(writebytes, ProtocolData)
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful == False
    finally:
        return Summary

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def ReadCmtSelect():
    """Reads the selected Degamma/CMT LUT for the display module
    """
    global Summary
    Summary.Command = "Read Cmt Select"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',40))
        ProtocolData.OpcodeLength = 1;
        readbytes = _readcommand(1, writebytes, ProtocolData)
        DegammaCmtIndex = struct.unpack_from ('B', bytearray(readbytes), 0)[0]
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful = False
    finally:
        return Summary, DegammaCmtIndex

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def ReadSequenceHeaderAttributes():
    """Reads sequence header information for the active sequence of 
    the display module
    """
    global Summary
    Summary.Command = "Read Sequence Header Attributes"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',38))
        ProtocolData.OpcodeLength = 1;
        readbytes = _readcommand(30, writebytes, ProtocolData)
        SequenceHeaderAttributes.LookRedDutyCycle = convertfixedtofloat(struct.unpack_from ('H', bytearray(readbytes), 0)[0], 255)
        SequenceHeaderAttributes.LookGreenDutyCycle = convertfixedtofloat(struct.unpack_from ('H', bytearray(readbytes), 2)[0], 255)
        SequenceHeaderAttributes.LookBlueDutyCycle = convertfixedtofloat(struct.unpack_from ('H', bytearray(readbytes), 4)[0], 255)
        SequenceHeaderAttributes.LookMaxFrameTime = convertfixedtofloat(struct.unpack_from ('I', bytearray(readbytes), 6)[0], 15)
        SequenceHeaderAttributes.LookMinFrameTime = convertfixedtofloat(struct.unpack_from ('I', bytearray(readbytes), 10)[0], 15)
        SequenceHeaderAttributes.LookMaxSequenceVectors = struct.unpack_from ('B', bytearray(readbytes), 14)[0]
        SequenceHeaderAttributes.SeqRedDutyCycle = convertfixedtofloat(struct.unpack_from ('H', bytearray(readbytes), 15)[0], 255)
        SequenceHeaderAttributes.SeqGreenDutyCycle = convertfixedtofloat(struct.unpack_from ('H', bytearray(readbytes), 17)[0], 255)
        SequenceHeaderAttributes.SeqBlueDutyCycle = convertfixedtofloat(struct.unpack_from ('H', bytearray(readbytes), 19)[0], 255)
        SequenceHeaderAttributes.SeqMaxFrameTime = convertfixedtofloat(struct.unpack_from ('I', bytearray(readbytes), 21)[0], 15)
        SequenceHeaderAttributes.SeqMinFrameTime = convertfixedtofloat(struct.unpack_from ('I', bytearray(readbytes), 25)[0], 15)
        SequenceHeaderAttributes.SeqMaxSequenceVectors = struct.unpack_from ('B', bytearray(readbytes), 29)[0]
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful = False
    finally:
        return Summary, SequenceHeaderAttributes

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def WriteLocalAreaBrightnessBoostControl(
        LabbControl,  SharpnessStrength,  LabbStrengthSetting
    ):
    """Controls the local area brightness boost image processing 
    functionality for the display module
    """
    global Summary
    Summary.Command = "Write Local Area Brightness Boost Control"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',128))
        ProtocolData.OpcodeLength = 1;
        packerinit()
        value = setbits(LabbControl.value, 2, 0)
        value = setbits(int(SharpnessStrength), 4, 4)
        writebytes.extend(list(struct.pack('B',value)))
        writebytes.extend(list(struct.pack('B',LabbStrengthSetting)))
        _writecommand(writebytes, ProtocolData)
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful == False
    finally:
        return Summary

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def ReadLocalAreaBrightnessBoostControl():
    """Reads the state of the local area brightness boost image 
    processing functionality for the display module
    """
    global Summary
    Summary.Command = "Read Local Area Brightness Boost Control"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',129))
        ProtocolData.OpcodeLength = 1;
        readbytes = _readcommand(3, writebytes, ProtocolData)
        readdata = struct.unpack_from ('B', bytearray(readbytes), 0)[0]
        packerinit(readdata)
        LabbControlObj = getbits(2, 0);
        SharpnessStrength = getbits(4, 4);
        LabbStrengthSetting = struct.unpack_from ('B', bytearray(readbytes), 1)[0]
        LabbGainValue = struct.unpack_from ('B', bytearray(readbytes), 2)[0]
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful = False
    finally:
        return Summary, LabbControl(LabbControlObj), \
            SharpnessStrength, LabbStrengthSetting, LabbGainValue

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def WriteCaicImageProcessingControl(CaicImageProcessingControl):
    """Controls the CAIC functionality for the display module
    """
    global Summary
    Summary.Command = "Write Caic Image Processing Control"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',132))
        ProtocolData.OpcodeLength = 1;
        packerinit()
        value = setbits(CaicImageProcessingControl.CaicWpcControl.value, 3, 0)
        value = setbits(CaicImageProcessingControl.CaicColorModulationControl.value, 1, 3)
        value = setbits(CaicImageProcessingControl.CaicGainControl.value, 1, 6)
        value = setbits(int(CaicImageProcessingControl.CaicGainDisplayEnable), 1, 7)
        writebytes.extend(list(struct.pack('B',value)))
        writebytes.extend(list(struct.pack('B',int(convertfloattofixed(CaicImageProcessingControl.CaicMaxLumensGain,31)))))
        writebytes.extend(list(struct.pack('B',int(convertfloattofixed(CaicImageProcessingControl.CaicClippingThreshold,63)))))
        _writecommand(writebytes, ProtocolData)
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful == False
    finally:
        return Summary

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def ReadCaicImageProcessingControl():
    """Reads the state of the CAIC functionality within the display 
    module
    """
    global Summary
    Summary.Command = "Read Caic Image Processing Control"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',133))
        ProtocolData.OpcodeLength = 1;
        readbytes = _readcommand(3, writebytes, ProtocolData)
        readdata = struct.unpack_from ('B', bytearray(readbytes), 0)[0]
        packerinit(readdata)
        CaicImageProcessingControl.CaicWpcControl = getbits(3, 0);
        CaicImageProcessingControl.CaicColorModulationControl = getbits(1, 3);
        CaicImageProcessingControl.CaicGainControl = getbits(1, 6);
        CaicImageProcessingControl.CaicGainDisplayEnable = getbits(1, 7);
        CaicImageProcessingControl.CaicMaxLumensGain = convertfixedtofloat(struct.unpack_from ('B', bytearray(readbytes), 1)[0], 31)
        CaicImageProcessingControl.CaicClippingThreshold = convertfixedtofloat(struct.unpack_from ('B', bytearray(readbytes), 2)[0], 63)
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful = False
    finally:
        return Summary, CaicImageProcessingControl

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def WriteColorCoordinateAdjustmentControl(CcaEnable):
    """Controls the CCA image processing functionality for the display
    module
    """
    global Summary
    Summary.Command = "Write Color Coordinate Adjustment Control"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',134))
        ProtocolData.OpcodeLength = 1;
        writebytes.extend(list(struct.pack('B',CcaEnable)))
        _writecommand(writebytes, ProtocolData)
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful == False
    finally:
        return Summary

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def ReadColorCoordinateAdjustmentControl():
    """Reads the state of the CCA image processing within the display
    module
    """
    global Summary
    Summary.Command = "Read Color Coordinate Adjustment Control"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',135))
        ProtocolData.OpcodeLength = 1;
        readbytes = _readcommand(1, writebytes, ProtocolData)
        CcaEnable = struct.unpack_from ('?', bytearray(readbytes), 0)[0]
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful = False
    finally:
        return Summary, CcaEnable

# ---------------------------------------------------------------------
# System status
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def ReadShortStatus():
    """Provides a short system status for the display module
    """
    global Summary
    Summary.Command = "Read Short Status"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0
    try:
        writebytes=list(struct.pack('B',208))
        ProtocolData.OpcodeLength = 1
        readbytes = _readcommand(1, writebytes, ProtocolData)
        readdata = struct.unpack_from ('B', bytearray(readbytes), 0)[0]
        packerinit(readdata)
        ShortStatus.SystemInitialized = getbits(1, 0)
        ShortStatus.CommunicationError = getbits(1, 1)
        ShortStatus.SystemError = getbits(1, 3)
        ShortStatus.FlashEraseComplete = getbits(1, 4)
        ShortStatus.FlashError = getbits(1, 5)
        ShortStatus.Application = getbits(1, 7)
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful = False
    finally:
        return Summary, ShortStatus
    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def ReadSystemStatus():
    """Reads system status information for the display module
    """
    global Summary
    Summary.Command = "Read System Status"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',209))
        ProtocolData.OpcodeLength = 1;
        readbytes = _readcommand(4, writebytes, ProtocolData)
        readdata = struct.unpack_from ('B', bytearray(readbytes), 0)[0]
        packerinit(readdata)
        SystemStatus.DmdDeviceError = getbits(1, 0);
        SystemStatus.DmdInterfaceError = getbits(1, 1);
        SystemStatus.DmdTrainingError = getbits(1, 2);
        readdata = struct.unpack_from ('B', bytearray(readbytes), 1)[0]
        packerinit(readdata)
        SystemStatus.RedLedState = getbits(1, 0);
        SystemStatus.GreenLedState = getbits(1, 1);
        SystemStatus.BlueLedState = getbits(1, 2);
        SystemStatus.RedLedError = getbits(1, 3);
        SystemStatus.GreenLedError = getbits(1, 4);
        SystemStatus.BlueLedError = getbits(1, 5);
        readdata = struct.unpack_from ('B', bytearray(readbytes), 2)[0]
        packerinit(readdata)
        SystemStatus.SequenceAbortError = getbits(1, 0);
        SystemStatus.SequenceError = getbits(1, 1);
        SystemStatus.SequenceBinNotFoundError = getbits(1, 2);
        SystemStatus.DcPowerSupply = getbits(1, 3);
        readdata = struct.unpack_from ('B', bytearray(readbytes), 3)[0]
        packerinit(readdata)
        SystemStatus.ActuatorDriveEnable = getbits(1, 0);
        SystemStatus.ActuatorPwmGenSource1080POnly = getbits(1, 1);
        SystemStatus.ActuatorConfigurationError = getbits(1, 4);
        SystemStatus.ActuatorWatchdogTimerTimeout = getbits(1, 5);
        SystemStatus.ActuatorSubframeFilteredStatus = getbits(1, 6);
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful = False
    finally:
        return Summary, SystemStatus

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def ReadCommunicationStatus():
    """Reads communication status information for the display module
    """
    global Summary
    Summary.Command = "Read Communication Status"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',211))
        ProtocolData.OpcodeLength = 1;
        valueArray = [0x02]
        writebytes.extend(valueArray)
        readbytes = _readcommand(6, writebytes, ProtocolData)
        readdata = struct.unpack_from ('B', bytearray(readbytes), 4)[0]
        packerinit(readdata)
        CommunicationStatus.InvalidCommandError = getbits(1, 0);
        CommunicationStatus.InvalidCommandParameterValue = getbits(1, 1);
        CommunicationStatus.CommandProcessingError = getbits(1, 2);
        CommunicationStatus.FlashBatchFileError = getbits(1, 3);
        CommunicationStatus.ReadCommandError = getbits(1, 4);
        CommunicationStatus.InvalidNumberOfCommandParameters = getbits(1, 5);
        CommunicationStatus.BusTimeoutByDisplayError = getbits(1, 6);
        CommunicationStatus.AbortedOpCode = struct.unpack_from ('B', bytearray(readbytes), 5)[0]
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful = False
    finally:
        return Summary, CommunicationStatus

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def ReadSystemSoftwareVersion():
    """Reads the main application software version information for the 
    display module
    """
    global Summary
    Summary.Command = "Read System Software Version"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',210))
        ProtocolData.OpcodeLength = 1;
        readbytes = _readcommand(4, writebytes, ProtocolData)
        PatchVersion = struct.unpack_from ('H', bytearray(readbytes), 0)[0]
        MinorVersion = struct.unpack_from ('B', bytearray(readbytes), 2)[0]
        MajorVersion = struct.unpack_from ('B', bytearray(readbytes), 3)[0]
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful = False
    finally:
        return Summary, PatchVersion, MinorVersion, MajorVersion

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def ReadControllerDeviceId():
    """Reads the controller device ID for the display module
    """
    global Summary
    Summary.Command = "Read Controller Device Id"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',212))
        ProtocolData.OpcodeLength = 1;
        readbytes = _readcommand(1, writebytes, ProtocolData)
        DeviceIdObj = struct.unpack_from ('B', bytearray(readbytes), 0)[0]
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful = False
    finally:
        return Summary, ControllerDeviceId(DeviceIdObj)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def ReadDmdDeviceId(DmdDataSelection):
    """Reads the DMD device ID or DMD fuse data for the display module
    """
    global Summary
    Summary.Command = "Read Dmd Device Id"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',213))
        ProtocolData.OpcodeLength = 1;
        writebytes.extend(list(struct.pack('B',DmdDataSelection.value)))
        readbytes = _readcommand(4, writebytes, ProtocolData)
        DeviceId = struct.unpack_from ('I', bytearray(readbytes), 0)[0]
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful = False
    finally:
        return Summary, DeviceId

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def ReadFirmwareBuildVersion():
    """Reads the controller firmware version for the display module
    """
    global Summary
    Summary.Command = "Read Firmware Build Version"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',217))
        ProtocolData.OpcodeLength = 1;
        readbytes = _readcommand(4, writebytes, ProtocolData)
        PatchVersion = struct.unpack_from ('H', bytearray(readbytes), 0)[0]
        MinorVersion = struct.unpack_from ('B', bytearray(readbytes), 2)[0]
        MajorVersion = struct.unpack_from ('B', bytearray(readbytes), 3)[0]
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful = False
    finally:
        return Summary, PatchVersion, MinorVersion, MajorVersion

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def ReadFpgaVersion():
    """Read Fpga version
    """
    global Summary
    Summary.Command = "Read Fpga Version"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',100))
        ProtocolData.OpcodeLength = 1;
        readbytes = _readcommand(6, writebytes, ProtocolData)
        FpgaVersion = struct.unpack_from ('I', bytearray(readbytes), 0)[0]
        FpgaEcoRevision = struct.unpack_from ('B', bytearray(readbytes), 4)[0]
        FpgaArmSwVersion = struct.unpack_from ('B', bytearray(readbytes), 5)[0]
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful = False
    finally:
        return Summary, FpgaVersion, FpgaEcoRevision, FpgaArmSwVersion

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def ReadFpgaStatus():
    """Read Fpga status
    """
    global Summary
    Summary.Command = "Read Fpga Status"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',111))
        ProtocolData.OpcodeLength = 1;
        readbytes = _readcommand(1, writebytes, ProtocolData)
        readdata = struct.unpack_from ('B', bytearray(readbytes), 0)[0]
        packerinit(readdata)
        DisplayModeObj = getbits(1, 1);
        FpgaKeyingStatusObj = getbits(1, 0);
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful = False
    finally:
        return Summary, FpgaXprMode(DisplayModeObj), PassFail(FpgaKeyingStatusObj)

# ---------------------------------------------------------------------
# Flash-related
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def WriteFlashDataLength(FlashDataLength):
    """Specifies the length in bytes of data that will be written/read 
    from the flash
    """
    global Summary
    Summary.Command = "Write Flash Data Length"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',223))
        ProtocolData.OpcodeLength = 1;
        writebytes.extend(list(struct.pack('H',FlashDataLength)))
        _writecommand(writebytes, ProtocolData)
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful == False
    finally:
        return Summary

# ---------------------------------------------------------------------
# Test patterns
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def WriteFpgaTestPatternSelect(
        TestPatternBorder,  Color,  PatternSelect,  Size
    ):
    """Selects a test pattern from the FPGA as the image source
    """
    global Summary
    Summary.Command = "Write Fpga Test Pattern Select"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',103))
        ProtocolData.OpcodeLength = 1;
        packerinit()
        value = setbits(TestPatternBorder.value, 1, 7)
        value = setbits(Color.value, 3, 4)
        value = setbits(PatternSelect.value, 4, 0)
        writebytes.extend(list(struct.pack('B',value)))
        writebytes.extend(list(struct.pack('B',Size)))
        _writecommand(writebytes, ProtocolData)
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful == False
    finally:
        return Summary

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def ReadFpgaTestPatternSelect():
    """Reads back the host-specified parameters for an FPGA test 
    pattern
    """
    global Summary
    Summary.Command = "Read Fpga Test Pattern Select"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',104))
        ProtocolData.OpcodeLength = 1;
        readbytes = _readcommand(2, writebytes, ProtocolData)
        readdata = struct.unpack_from ('B', bytearray(readbytes), 0)[0]
        packerinit(readdata)
        TestPatternBorderObj = getbits(1, 7);
        ColorObj = getbits(3, 4);
        PatternSelectObj = getbits(4, 0);
        Size = struct.unpack_from ('B', bytearray(readbytes), 1)[0]
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful = False
    finally:
        return Summary, Enable(TestPatternBorderObj), \
            FpgaTestPatternColor(ColorObj), \
            FpgaTestPattern(PatternSelectObj), Size

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def WriteFpgaSolidField(Color):
    """Write Fpga solid field
    """
    global Summary
    Summary.Command = "Write Fpga Solid Field"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',103))
        ProtocolData.OpcodeLength = 1;
        packerinit()
        value = setbits(1, 1, 7)
        value = setbits(Color.value, 3, 4)
        value = setbits(0, 4, 0)
        writebytes.extend(list(struct.pack('B',value)))
        valueArray = [0x00]
        writebytes.extend(valueArray)
        _writecommand(writebytes, ProtocolData)
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful == False
    finally:
        return Summary

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def WriteFpgaGrid():
    """Write Fpga grid
    """
    global Summary
    Summary.Command = "Write Fpga Grid"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',103))
        ProtocolData.OpcodeLength = 1;
        packerinit()
        value = setbits(1, 1, 7)
        value = setbits(0, 3, 4)
        value = setbits(1, 4, 0)
        writebytes.extend(list(struct.pack('B',value)))
        valueArray = [0x00]
        writebytes.extend(valueArray)
        _writecommand(writebytes, ProtocolData)
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful == False
    finally:
        return Summary

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def WriteFpgaHorizontalRamp():
    """Write Fpga horizontal ramp
    """
    global Summary
    Summary.Command = "Write Fpga Horizontal Ramp"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',103))
        ProtocolData.OpcodeLength = 1;
        packerinit()
        value = setbits(1, 1, 7)
        value = setbits(0, 3, 4)
        value = setbits(2, 4, 0)
        writebytes.extend(list(struct.pack('B',value)))
        valueArray = [0xFF]
        writebytes.extend(valueArray)
        _writecommand(writebytes, ProtocolData)
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful == False
    finally:
        return Summary

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def WriteFpgaVerticalRamp():
    """Write Fpga vertical ramp
    """
    global Summary
    Summary.Command = "Write Fpga Vertical Ramp"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',103))
        ProtocolData.OpcodeLength = 1;
        packerinit()
        value = setbits(1, 1, 7)
        value = setbits(0, 3, 4)
        value = setbits(3, 4, 0)
        writebytes.extend(list(struct.pack('B',value)))
        valueArray = [0xFF]
        writebytes.extend(valueArray)
        _writecommand(writebytes, ProtocolData)
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful == False
    finally:
        return Summary

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def WriteFpgaCheckerboard():
    """Write Fpga checkerboard
    """
    global Summary
    Summary.Command = "Write Fpga Checkerboard"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',103))
        ProtocolData.OpcodeLength = 1;
        packerinit()
        value = setbits(1, 1, 7)
        value = setbits(7, 3, 4)
        value = setbits(4, 4, 0)
        writebytes.extend(list(struct.pack('B',value)))
        valueArray = [0x14]
        writebytes.extend(valueArray)
        _writecommand(writebytes, ProtocolData)
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful == False
    finally:
        return Summary

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def WriteFpgaHorizontalLines():
    """Write Fpga horizontal lines
    """
    global Summary
    Summary.Command = "Write Fpga Horizontal Lines"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',103))
        ProtocolData.OpcodeLength = 1;
        packerinit()
        value = setbits(1, 1, 7)
        value = setbits(0, 3, 4)
        value = setbits(5, 4, 0)
        writebytes.extend(list(struct.pack('B',value)))
        valueArray = [0x00]
        writebytes.extend(valueArray)
        _writecommand(writebytes, ProtocolData)
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful == False
    finally:
        return Summary

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def WriteFpgaVerticalLines():
    """Write Fpga vertical lines
    """
    global Summary
    Summary.Command = "Write Fpga Vertical Lines"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',103))
        ProtocolData.OpcodeLength = 1;
        packerinit()
        value = setbits(1, 1, 7)
        value = setbits(0, 3, 4)
        value = setbits(6, 4, 0)
        writebytes.extend(list(struct.pack('B',value)))
        valueArray = [0x00]
        writebytes.extend(valueArray)
        _writecommand(writebytes, ProtocolData)
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful == False
    finally:
        return Summary

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def WriteFpgaDiagonalLines():
    """Write Fpga diagonal lines
    """
    global Summary
    Summary.Command = "Write Fpga Diagonal Lines"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',103))
        ProtocolData.OpcodeLength = 1;
        packerinit()
        value = setbits(1, 1, 7)
        value = setbits(0, 3, 4)
        value = setbits(7, 4, 0)
        writebytes.extend(list(struct.pack('B',value)))
        valueArray = [0x00]
        writebytes.extend(valueArray)
        _writecommand(writebytes, ProtocolData)
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful == False
    finally:
        return Summary

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def WriteFpgaActuatorCalibrationPattern():
    """Write Fpga actuator calibration pattern
    """
    global Summary
    Summary.Command = "Write Fpga Actuator Calibration Pattern"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',103))
        ProtocolData.OpcodeLength = 1;
        packerinit()
        value = setbits(1, 1, 7)
        value = setbits(0, 3, 4)
        value = setbits(8, 4, 0)
        writebytes.extend(list(struct.pack('B',value)))
        valueArray = [0x00]
        writebytes.extend(valueArray)
        _writecommand(writebytes, ProtocolData)
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful == False
    finally:
        return Summary

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def WriteFpga3DTestPattern():
    """Write Fpga 3D test pattern
    """
    global Summary
    Summary.Command = "Write Fpga 3 D Test Pattern"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',103))
        ProtocolData.OpcodeLength = 1;
        packerinit()
        value = setbits(1, 1, 7)
        value = setbits(0, 3, 4)
        value = setbits(9, 4, 0)
        writebytes.extend(list(struct.pack('B',value)))
        valueArray = [0x00]
        writebytes.extend(valueArray)
        _writecommand(writebytes, ProtocolData)
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful == False
    finally:
        return Summary

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def WriteFpgaColorBarTestPattern():
    """Write Fpga color bar test pattern
    """
    global Summary
    Summary.Command = "Write Fpga Color Bar Test Pattern"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',103))
        ProtocolData.OpcodeLength = 1;
        packerinit()
        value = setbits(1, 1, 7)
        value = setbits(0, 3, 4)
        value = setbits(10, 4, 0)
        writebytes.extend(list(struct.pack('B',value)))
        valueArray = [0x00]
        writebytes.extend(valueArray)
        _writecommand(writebytes, ProtocolData)
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful == False
    finally:
        return Summary

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def WriteFpgaFrameAndCrossTestPattern():
    """Write Fpga frame and cross test pattern
    """
    global Summary
    Summary.Command = "Write Fpga Frame And Cross Test Pattern"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',103))
        ProtocolData.OpcodeLength = 1;
        packerinit()
        value = setbits(1, 1, 7)
        value = setbits(0, 3, 4)
        value = setbits(11, 4, 0)
        writebytes.extend(list(struct.pack('B',value)))
        packerinit()
        value = setbits(8, 4, 4)
        value = setbits(8, 4, 0)
        writebytes.extend(list(struct.pack('B',value)))
        _writecommand(writebytes, ProtocolData)
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful == False
    finally:
        return Summary
# ---------------------------------------------------------------------
# DAC-related
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def WriteActuatorGlobalDacOutputEnable(ActuatorDacOutputEnable):
    """Enables the actuator DAC output
    """
    global Summary
    Summary.Command = "Write Actuator Global DAC Output Enable"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',174))
        ProtocolData.OpcodeLength = 1;
        writebytes.extend(list(struct.pack('B',ActuatorDacOutputEnable.value)))
        _writecommand(writebytes, ProtocolData)
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful == False
    finally:
        return Summary

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def ReadActuatorGlobalDacOutputEnable():
    """Reads the enable state of the actuator DAC output
    """
    global Summary
    Summary.Command = "Read Actuator Global DAC Output Enable"
    Summary.Successful = True
    global ProtocolData
    ProtocolData.CommandDestination = 0;
    try:
        writebytes=list(struct.pack('B',175))
        ProtocolData.OpcodeLength = 1;
        readbytes = _readcommand(1, writebytes, ProtocolData)
        ActuatorDacOutputEnableObj = struct.unpack_from ('B', bytearray(readbytes), 0)[0]
    except ValueError as ve:
        print("Exception Occurred ", ve)
        Summary.Successful = False
    finally:
        return Summary, Enable(ActuatorDacOutputEnableObj)

# ---------------------------------------------------------------------