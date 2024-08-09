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
import platform
from enum import Enum
from typing import List, Any

PLATFORM_WINDOWS = platform.system() == "Windows"
if PLATFORM_WINDOWS:
  import Devices.hid as hid
else:
  import hid # type: ignore

# fmt: off
# ---------------------------------------------------------------------
LC_deviceName    = "lcr230np"

'''
LC_width         = 912
LC_height        = 1140

# ---------------------------------------------------------------------
LC_VID           = 0x0451
LC_PID           = 0x6401
LC_IDStr         = "LCr"
LC_Usage         = 65280
'''

# fmt: on
# ---------------------------------------------------------------------
# Error codes and messages
#
class ERROR:
    OK = 0
    # ...


ErrorStr = dict([
    (ERROR.OK, "ok")
])

# ---------------------------------------------------------------------
class LCException(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

# fmt: off
# ---------------------------------------------------------------------
class CMD_FORMAT_LIST:
  SOURCE_SEL         = [ 0x1A, 0x00, 0x01, 0]   # SOURCE_SEL
  # ...

# fmt: on
# ---------------------------------------------------------------------
LCrDeviceList: List[Any] = []

'''
# ---------------------------------------------------------------------
def enumerateLightcrafters(_funcLog=None):
  """
  Enumerate lightcrafter devices
  """
  nLCrFound = 0
  LCrList   = []
  hidList   = hid.enumerate()
  for iDev, dev in enumerate(hidList):
    if ((dev["product_id"] == LC_PID) and (dev["vendor_id"] == LC_VID) and
        (dev["usage"] == LC_Usage)):
      if _funcLog:
        _funcLog("ok", "Found lightcrafter device #{0}".format(iDev), 2)
        _funcLog(" ",  "Device path=`{0}`".format(dev["path"]), 2)
      LCrList.append((iDev, dev["path"]))
      nLCrFound += 1
  return LCrList
'''

'''
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
  =============== ==================================================
  """
  def __init__(self, _isCheckOnly=False, _funcLog=None, _logLevel=2):
    global LCrDeviceList

    self.LC          = None
    self.nSeq        = 0
    self.isCheckOnly = _isCheckOnly
    self.lastMsgStr  = ""
    self.funcLog     = _funcLog
    self.logLevel    = _logLevel
    self.devNum      = -1
    self.mBoxState   = MailboxCmd.Close
    if _isCheckOnly:
      return

    if "LCrDeviceList" not in globals() or (len(LCrDeviceList) == 0):
      LCrDeviceList  = enumerateLightcrafters(_funcLog)

  # -------------------------------------------------------------------
  # Connect and disconnect the device
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def connect(self, _devNum=-1):
    """
    Try connecting to a lightcrafter and return immediately with an
    error code if it fails. A device number (`_devNum`) can be given
    if multiple lightcrafters are connected.

    =============== ==================================================
    Parameters:
    =============== ==================================================
    _devNum         | device number (0,1,...)
    =============== ==================================================
    """
    global LCrDeviceList

    if not self.isCheckOnly:
      try:
        if _devNum < 0:
          # Using the first device that is available
          #
          self.log(" ", "Trying to connect ...", 2)

          self.LC = hid.device()
          self.LC.open(LC_VID, LC_PID)
          self.devNum = 0

        else:
          if _devNum < len(LCrDeviceList):
            # Look for a specific device (in case there are multiple LCrs
            # connected)
            #
            msg = "Trying to connect to LCr #{0}...".format(_devNum)
            self.log(" ", msg, 2)

            self.LC = hid.device()
            self.LC.open_path(LCrDeviceList[_devNum][1])
            self.devNum = _devNum

          else:
            self.LC = None
            if len(LCrDeviceList) > 0:
              errC = ERROR.DEVICE_NOT_FOUND
            else:
              errC = ERROR.NO_DEVICES
            self.log("ERROR", ErrorStr[errC], 0)
            return [errC]

      except IOError as ex:
        self.LC = None
        errC    = ERROR.COULD_NOT_CONNECT
        self.log("ERROR", ErrorStr[errC] +", Code '{0}'".format(ex), 0)
        return [errC]

      self.LC.set_nonblocking(1)
      self.sManufacturer = self.LC.get_manufacturer_string()
      self.sProduct      = self.LC.get_product_string()
      self.sSN           = self.LC.get_serial_number_string()

      msg = "Connected to {0} by {1}".format(self.sProduct, self.sManufacturer)
      self.log("ok", msg, 2)
      if _devNum >= 0:
        self.log(" ", "as device #{0}".format(self.devNum), 2)

    return [ERROR.OK]

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def waitToConnect(self, _devNum=-1, _timeout=10.0):
    """
    Try connecting to a lightcrafter until success or the timeout.
    Returns an error code if it fails. A device number (`_devNum`) can
    be given if multiple lightcrafters are connected.

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
      res = self.connect()
    self.logLevel = lgl
    return res

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def disconnect(self):
    """
    Disconnects the lightcrafter.
    """
    if not self.isCheckOnly:
      if self.LC is not None:
        self.LC.close()
        self.LC = None
        self.log("ok", "Disconnected", 2)

    return [ERROR.OK]

  # -------------------------------------------------------------------
  # Hardware and system status-related
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def getFirmwareVersion(self):
    """
    Get firmware version

    =============== ==================================================
    Result:
    =============== ==================================================
    code            | 0=ok or error code
    data            | the original data byte(s) returned by the device
    info            | a dictionary with following entries:
                    | applicationSoftwareRev, APISoftwareRevision,
                    | softwareConfigurationRevision,
                    | sequenceConfigurationRevision
    =============== ==================================================
    """
    if self.isCheckOnly:
      return [ERROR.OK]

    res = self.readData(CMD_FORMAT_LIST.GET_VERSION)
    if res[0] == ERROR.OK:
      data    = res[1][LC_firstDataByte:]
      appVer  = self.verListFromInt32(data, 0)
      APIVer  = self.verListFromInt32(data, 4)
      confVer = self.verListFromInt32(data, 8)
      seqVer  = self.verListFromInt32(data, 12)
      info    = {"applicationSoftwareRev": appVer,
                 "APISoftwareRevision": APIVer,
                 "softwareConfigurationRevision": confVer,
                 "sequenceConfigurationRevision": seqVer}
      self.log(" ", (LC_logStrMaskR +"{1}.{2}.{3}")
                    .format("Firmware version",
                            appVer[0], appVer[1], appVer[2]), 1)
      return [ERROR.OK, data, info]
    else:
      raise LCException(res[0])

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def getHardwareStatus(self):
    """
    Requests the device's hardware status and returns a list with up
    to three elements:

    =============== ==================================================
    Result:
    =============== ==================================================
    code            | 0=ok or error code
    data            | the original data byte(s) returned by the device
    info            | a dictionary with following entries:
                    | initOK, DMDError, swapError, seqAbort,
                    | seqError
    =============== ==================================================
    """
    if self.isCheckOnly:
      return [ERROR.OK]

    res    = self.readData(CMD_FORMAT_LIST.STATUS_HW)
    if res[0] == ERROR.OK:
      data      = res[1][LC_firstDataByte]
      initOK    = (data & 0x01) > 0
      DMDError  = (data & 0x04) > 0
      swapError = (data & 0x08) > 0
      seqAbort  = (data & 0x40) > 0
      seqError  = (data & 0x80) > 0
      info      = {"initOK":initOK, "DMDError":DMDError,
                   "swapError":swapError, "seqAbort":seqAbort,
                   "seqError":seqError}
      self.log("ERROR" if not initOK else "ok",
               (LC_logStrMaskR +"{1} {2} {3} {4} {5}")
               .format("Hardware errors",
                       "-" if initOK else "init",
                       "DMD" if DMDError else "-",
                       "swap" if swapError else "-",
                       "seq_abort" if seqAbort else "-",
                       "sequence" if seqError else "-"), 1)
      return [ERROR.OK, data, info]
    else:
      raise LCException(res[0])

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def getSystemStatus(self):
    """
    Requests the device's system status and returns a list with up
    to three elements:

    =============== ==================================================
    Result:
    =============== ==================================================
    code            | 0=ok or error code
    data            | the original data byte(s) returned by the device
    info            | a dictionary with following entry:
                    | MemoryOK
    =============== ==================================================
    """
    if self.isCheckOnly:
      return [ERROR.OK]

    res    = self.readData(CMD_FORMAT_LIST.STATUS_SYS)
    if res[0] == ERROR.OK:
      data     = res[1][LC_firstDataByte]
      MemoryOK = (data & 0x01) > 0
      info     = {"MemoryOK":MemoryOK}
      self.log("ERROR" if not MemoryOK else "ok",
               (LC_logStrMaskR +"{1}")
               .format("System errors",
                       "-" if MemoryOK else "memory"), 1)
      return [ERROR.OK, data, info]
    else:
      raise LCException(res[0])

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def getMainStatus(self, _logLev=1):
    """
    Requests the device's main status and returns a list with up
    to three elements:

    =============== ==================================================
    Result:
    =============== ==================================================
    code            | 0=ok or error code
    data            | the original data byte(s) returned by the device
    info            | a dictionary with following entry:
                    | DMDParked, SeqRunning, FBufFrozen,
                    | FBufFrozen, GammaEnab
    =============== ==================================================
    """
    if self.isCheckOnly:
      return [ERROR.OK]

    res    = self.readData(CMD_FORMAT_LIST.STATUS_MAIN)
    if res[0] == ERROR.OK:
      data       = res[1][LC_firstDataByte]
      DMDParked  = (data & 0x01) > 0
      SeqRunning = (data & 0x02) > 0
      FBufFrozen = (data & 0x04) > 0
      GammaEnab  = (data & 0x08) > 0
      info       = {"DMDParked":DMDParked, "SeqRunning":SeqRunning,
                    "FBufFrozen":FBufFrozen, "GammaEnab":GammaEnab}
      self.log(" ", (LC_logStrMaskR +"{1} {2} {3} {4}")
                    .format("Hardware status",
                            "DMD_parked" if DMDParked else "DMD_active",
                            "seq_running" if SeqRunning else "-",
                            "frame_buffer_frozen" if FBufFrozen else "-",
                            "gamma_on" if GammaEnab else "-"), _logLev)
      return [ERROR.OK, data, info]
    else:
      raise LCException(res[0])

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def getVideoSignalDetectStatus(self):
    """
    Requests the status of the video signal received by the device and
    returns a list with up to three elements:

    =============== ==================================================
    Result:
    =============== ==================================================
    code            | 0=ok or error code
    data            | the original data byte(s) returned by the device
    info            | a dictionary with following entry:
                    | SigDetect, HRes, VRes, HSyncPol, VSyncPol,
                    | PixClk_kHz, HFreq_kHz, VFreq_Hz
    =============== ==================================================
    """
    if self.isCheckOnly:
      return [ERROR.OK]

    res    = self.readData(CMD_FORMAT_LIST.VIDEO_SIG_DETECT)
    if res[0] == ERROR.OK:
      data       = res[1]
      i          = LC_firstDataByte
      SigDetect  = data[i]
      HRes       = (data[i+2] << 8) +data[i+1]
      VRes       = (data[i+4] << 8) +data[i+3]
      HSyncPol   = data[i+6]
      VSyncPol   = data[i+7]
      PixClk_kHz = ((data[i+11] << 24) +(data[i+10] << 16) +
                   (data[i+9] << 8) +data[i+8])/100.0
      HFreq_kHz  = ((data[i+13] << 8) +data[i+12])/100.0
      VFreq_Hz   = ((data[i+15] << 8) +data[i+14])/100.0
      """
      17:16 15:0 Total Pixels Per Line
      19:18 15:0 Total Lines Per Frame
      21:20 15:0 Active Pixels Per Line
      23:22 15:0 Active Lines Per Frame
      25:24 15:0 First pixel (beginning of active pixel in the Line)
      27:26 15:0 First Line (beginning of active line in the Frame)
      """
      self.log(" ", (LC_logStrMaskR +"{1}")
                    .format("Video signal",
                            "detected" if SigDetect else "-"), 1)
      self.log(" ", (LC_logStrMaskR +"{1} x {2}")
                    .format("Resolution", HRes, VRes), 1)
      self.log(" ", (LC_logStrMaskR +"HSync={1}, VSync={2}")
                    .format("Polarity", HSyncPol, VSyncPol), 1)
      self.log(" ", (LC_logStrMaskR +"{1} kHz")
                    .format("Pixel clock", PixClk_kHz), 1)
      self.log(" ", (LC_logStrMaskR +"HFreq={1}, VFreq={2}")
                    .format("Frequency [kHz]", HFreq_kHz, VFreq_Hz), 1)
      info       = {"SigDetect":SigDetect, "HRes":HRes, "VRes":VRes,
                    "HSyncPol":HSyncPol, "VSyncPol":VSyncPol,
                    "PixClk_kHz":PixClk_kHz, "HFreq_kHz":HFreq_kHz,
                    "VFreq_Hz":VFreq_Hz}
      return ERROR.OK, info
    else:
      raise LCException(res[0])

  # -------------------------------------------------------------------
  # Software reset
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def softwareReset(self):
    """
    Signal the device to do a software reset. This will take a couple
    of seconds. After the reset the device is disconnected.
    """
    errC = ERROR.OK
    s0   = self.softwareReset.__name__

    if not self.isCheckOnly:
      res  = self.writeData(CMD_FORMAT_LIST.SW_RESET, [1])
      errC = res[0]

    if errC == ERROR.OK:
      self.log(" ", (LC_logStrMaskL +"done").format(s0), 2)
      return [errC]
    else:
      self.log("ERROR", LC_logStrMaskErr.format(s0, ErrorStr[errC]), 2)
      raise LCException(errC)

  # -------------------------------------------------------------------
  # Input source and mode selection
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def setInputSource(self, _source, _bitDepth):
    """
    Defines the input source of the device. Use enum classes `SourceSel`
    and `SourcePar` for `_source` and `_bitDepth`, respectively.

    =============== ==================================================
    Parameters:
    =============== ==================================================
    _source         | 0=parallel interface (PP),
                    | 1=internal test pattern,
                    | 2=Flash
                    | 3=FPD-link
    _bitDepth       | Parallel interface bit depth
                    | 0=30, 1=24, 2=20, 3=16, 4=10, 5=8 bits
    =============== ==================================================
    """
    errC = ERROR.OK
    s0   = self.setInputSource.__name__

    if (_source not in SourceSel) or (_bitDepth not in SourcePar):
      errC = ERROR.INVALID_PARAMS
    elif not self.isCheckOnly:
      data = (int(_source.value) | (int(_bitDepth.value) << 3))
      res  = self.writeData(CMD_FORMAT_LIST.SOURCE_SEL, [data])
      errC = res[0]

    if errC == ERROR.OK:
      s1  = SourceSelStr[_source] +" "
      s1 += SourceParStr[_bitDepth] if _source == SourceSel.HDMI else ""
      self.log(" ", (LC_logStrMaskL +"{1}").format(s0, s1), 2)
      return [errC]
    else:
      self.log("ERROR", LC_logStrMaskErr.format(s0, ErrorStr[errC]), 2)
      raise LCException(errC)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def setDisplayMode(self, _mode):
    """
    Sets the display mode of the device. Use enum class `DispMode` for
    `_mode`.

    =============== ==================================================
    Parameters:
    =============== ==================================================
    _mode           | 0=video display mode,
                    | Assumes streaming video image from the
                    | 30-bit RGB or FPD-link interface with a
                    | pixel resolution of up to 1280 × 800 up
                    | to 120 Hz.
                    | 1=Pattern display mode
                    | Assumes a 1-bit through 8-bit image with
                    | a pixel resolution of 912 × 1140 and
                    | bypasses all the image processing functions
                    | of the DLPC350.
    =============== ==================================================
    """
    errC = ERROR.OK
    s0   = self.setDisplayMode.__name__

    if _mode not in DispMode:
      errC = ERROR.INVALID_PARAMS
    elif not self.isCheckOnly:
      data = [int(_mode.value)]
      res  = self.writeData(CMD_FORMAT_LIST.DISP_MODE, data)
      errC = res[0]

    if errC == ERROR.OK:
      s1 = DispModeStr[_mode]
      self.log(" ", (LC_logStrMaskL +"{1}").format(s0, s1), 2)
      return [errC]
    else:
      self.log("ERROR", LC_logStrMaskErr.format(s0, ErrorStr[errC]), 2)
      raise LCException(errC)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def validateDataCommandResponse(self):
    """
    The Validate Data command checks the programmed pattern display modes
    and indicates any invalid settings.

    =============== ==================================================
    Result:
    =============== ==================================================
    code            | 0=ok or error code
    data            | the original data byte returned by the device
    validated       | True if no error nor warning occurred
    info            | a dictionary with following entry:
                    | PeriodSettingInvalid, LUTPatternNumberInvalid,
                    | TrigOut1Invalid, PostVectSettingsInvalid,
                    | FrPerExpDiffInvalid, isBusyValidating
    =============== ==================================================
    """
    errC                    = ERROR.OK
    PeriodSettingInvalid    = False
    LUTPatternNumberInvalid = False
    TrigOut1Invalid         = False
    PostVectSettingsInvalid = False
    FrPerExpDiffInvalid     = False
    isBusyValidating        = True
    isSomeIssue             = False
    data                    = 0

    if not self.isCheckOnly:
      res  = self.writeData(CMD_FORMAT_LIST.LUT_VALID, [0])
      errC = res[0]
      if errC == ERROR.OK:
        while isBusyValidating:
          res = self.readData(CMD_FORMAT_LIST.LUT_VALID)
          if res[0] == ERROR.OK:
            data = res[1][LC_firstDataByte]
            PeriodSettingInvalid    = int((data & 0x01) > 0)
            LUTPatternNumberInvalid = int((data & 0x02) > 0)
            TrigOut1Invalid         = int((data & 0x04) > 0)
            PostVectSettingsInvalid = int((data & 0x08) > 0)
            FrPerExpDiffInvalid     = int((data & 0x10) > 0)
            isBusyValidating        = int((data & 0x80) > 0)
            isSomeIssue             = int((data & 0x1F) > 0)
          if isBusyValidating:
            self.log(" ", "Validating ...", 1)
            time.sleep(0.1)

    self.log("ERROR" if isSomeIssue else "ok",
             (LC_logStrMaskR +"{1} {2} {3} {4} {5}")
             .format("Validation",
                     "Selected exposure or frame period settings are invalid"
                     if PeriodSettingInvalid else "-",
                     "Selected pattern numbers in LUT are invalid"
                     if LUTPatternNumberInvalid else "-",
                     "Warning, continuous Trigger Out1 request or overlapping black sectors"
                     if TrigOut1Invalid else "-",
                     "Warning, post vector was not inserted prior to external triggered vector"
                     if PostVectSettingsInvalid else "-",
                     "Warning, frame period or exposure difference is less than 230 us"
                     if FrPerExpDiffInvalid else "-"), 1)
    info = {"PeriodSettingInvalid":PeriodSettingInvalid,
            "LUTPatternNumberInvalid":LUTPatternNumberInvalid,
            "TrigOut1Invalid":TrigOut1Invalid,
            "PostVectSettingsInvalid":PostVectSettingsInvalid,
            "FrPerExpDiffInvalid":FrPerExpDiffInvalid}

    if errC == ERROR.OK:
      return [ERROR.OK, not isSomeIssue, data, info]
    else:
      raise LCException(errC)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def setPatternTriggerMode(self, _mode):
    """
    Sets the Pattern Trigger Mode. Use enum class `PatTrigMode` for
    `_mode`.

    .. important:: Before executing this command, stop current pattern
                   sequence and after execution of this command,
                   validate before starting sequence.

    =============== ==================================================
    Parameters:
    =============== ==================================================
    _mode           | 0=VSYNC serves to trigger the pattern display
                    | sequence
                    | 1=internally or externally generated triggers
                    | (TRIG_IN_1 and TRIG_IN_2)
                    | 2=TRIG_IN_1 alternates between two patterns,
                    | while TRIG_IN_2 advances to next pair of
                    | patterns
                    | 3=internally or externally generated triggers
                    | for variable exposure sequence
                    | 4=VSYNC triggered for variable exposure display
                    | sequence
    =============== ==================================================
    """
    errC = ERROR.OK
    s0   = self.setPatternTriggerMode.__name__

    if _mode not in PatTrigMode:
      errC = ERROR.INVALID_PARAMS
    elif not self.isCheckOnly:
      data = [int(_mode.value)]
      res  = self.writeData(CMD_FORMAT_LIST.PAT_TRIG_MODE, data)
      errC = res[0]

    if errC == ERROR.OK:
      s1 = PatTrigModeStr[_mode]
      self.log(" ", (LC_logStrMaskL +"{1}").format(s0, s1), 2)
      return [errC]
    else:
      self.log("ERROR", LC_logStrMaskErr.format(s0, ErrorStr[errC]), 2)
      raise LCException(errC)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def setPatternDisplayDataInputSource(self, _src):
    """
    Sets the Pattern Data Input Source. Use enum class `SourcePat` for
    `_src`.

    .. important:: Before executing this command, stop current pattern
                   sequence and after execution of this command,
                   validate before starting sequence.

    =============== ==================================================
    Parameters:
    =============== ==================================================
    _mode           | 0=Data is streamed through the 24bit RGB
                    | /FPD-link interface
                    | 3=Data is fetched from flash memory
    =============== ==================================================
    """
    errC = ERROR.OK
    s0   = self.setPatternDisplayDataInputSource.__name__

    if _src not in SourcePat:
      errC = ERROR.INVALID_PARAMS
    elif not self.isCheckOnly:
      data = [int(_src.value)]
      res  = self.writeData(CMD_FORMAT_LIST.PAT_DISP_MODE, data)
      errC = res[0]

    if errC == ERROR.OK:
      s1 = SourcePatStr[_src]
      self.log(" ", (LC_logStrMaskL +"{1}").format(s0, s1), 2)
      return [errC]
    else:
      self.log("ERROR", LC_logStrMaskErr.format(s0, ErrorStr[errC]), 2)
      raise LCException(errC)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def __patternSequence(self, _s, _cmd):
    errC = ERROR.OK
    if not self.isCheckOnly:
      data = [int(_cmd.value)]
      res  = self.writeData(CMD_FORMAT_LIST.PAT_START_STOP, data)
      errC = res[0]

    if errC == ERROR.OK:
      self.log(" ", (LC_logStrMaskL +"done").format(_s), 2)
      return [errC]
    else:
      self.log("ERROR", LC_logStrMaskErr.format(_s, ErrorStr[errC]), 2)
      raise LCException(errC)

  def startPatternSequence(self):
    """
    Starts the programmed pattern sequence.

    .. important:: After executing this command, poll the system status.
    """
    s0 = self.startPatternSequence.__name__
    return self.__patternSequence(s0, PatSeqCmd.Start)

  def pausePatternSequence(self):
    """
    Pauses the programmed pattern sequence.

    .. important:: After executing this command, poll the system status.    """
    s0 = self.pausePatternSequence.__name__
    return self.__patternSequence(s0, PatSeqCmd.Pause)

  def stopPatternSequence(self):
    """
    Stop the programmed pattern sequence.

    .. important:: After executing this command, poll the system status.
    """
    s0 = self.stopPatternSequence.__name__
    return self.__patternSequence(s0, PatSeqCmd.Stop)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def setPatternExpTimeFrPer(self, _pet_us, _frp_us):
    """
    Set Pattern Exposure Time and Frame Period.

    The pattern exposure time (`_pet_us`) and frame period (`_frp_us`)
    dictates the length of time a pattern is exposed and the frame
    period.

    Either `_pet_us` == `_frp_us`, or `_pet_us` < (`_frp_us` -230 μs).

    .. important:: Before executing this command, stop current pattern
                   sequence and after execution of this command,
                   validate before starting sequence.

    =============== ==================================================
    Parameters:
    =============== ==================================================
    _pet_us         | pattern exposure time in [us]
    _frp_us         | frame period in [us]
    =============== ==================================================
    """
    errC = ERROR.OK
    s0   = self.setPatternExpTimeFrPer.__name__

    if (_pet_us <= 0) or (_frp_us <= 0):
      errC = ERROR.INVALID_PARAMS
    elif not self.isCheckOnly:
      data = [ int(_pet_us) & 0xFF,
              (int(_pet_us) & 0xFF00) >> 8,
              (int(_pet_us) & 0xFF0000) >> 16,
              (int(_pet_us) & 0xFF000000) >> 24,
               int(_frp_us) & 0xFF,
              (int(_frp_us) & 0xFF00) >> 8,
              (int(_frp_us) & 0xFF0000) >> 16,
              (int(_frp_us) & 0xFF000000) >> 24]
      res  = self.writeData(CMD_FORMAT_LIST.PAT_EXPO_PRD, data)
      errC = res[0]

    if errC == ERROR.OK:
      self.log(" ", (LC_logStrMaskL +
                     "{1} us pattern exposure, {2} us frame period")
                    .format(s0, _pet_us, _frp_us), 2)
      return [errC]
    else:
      self.log("ERROR", LC_logStrMaskErr.format(s0, ErrorStr[errC]), 2)
      raise LCException(errC)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def setPatternDispLUTControl(self, _nEntr, _repeat, _nPatt, _nImgInd):
    """
    The Pattern Display LUT Control Command controls the execution of
    patterns stored in the lookup table (LUT).

    .. important:: Before executing this command, stop current pattern
                   sequence and after execution of this command,
                   validate before starting sequence.

    =============== ==================================================
    Parameters:
    =============== ==================================================
    _nEntr          | number of entries in the LUT
    _repeat         | True=repeat sequence or False=play once
    _nPatt          | number of patterns per sequence
    _nImgInd        | number of Image Index LUT Entries (Flash mode)
    =============== ==================================================
    """
    errC = ERROR.OK
    s0   = self.setPatternDispLUTControl.__name__

    if (_nEntr < 1) or (_nEntr > 128) or \
       (_nPatt < 1) or (_nPatt > 256) or \
       (_nImgInd < 1) or (_nImgInd > 64):
      errC = ERROR.INVALID_PARAMS
    elif not self.isCheckOnly:
      data = [int(_nEntr -1), 1 if _repeat else 0, int(_nPatt -1),
              int(_nImgInd -1)]
      res  = self.writeData(CMD_FORMAT_LIST.PAT_CONFIG, data)
      errC = res[0]

    if errC == ERROR.OK:
      self.log(" ", (LC_logStrMaskL +
                     "{1} LUT {2}, {3} pattern(s)/sequence, {4}")
                    .format(s0, _nEntr,
                            "entries" if _nEntr > 1 else "entry",
                            _nPatt,
                            "repeat" if _repeat else "once"), 2)
      return [errC]
    else:
      self.log("ERROR", LC_logStrMaskErr.format(s0, ErrorStr[errC]), 2)
      raise LCException(errC)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def setPatternDispLUTOffsetPointer(self, _offs):
    """
    The Pattern Display LUT offset pointer defines the location of the
    LUT entries in the memory of the DLPC350.

    =============== ==================================================
    Parameters:
    =============== ==================================================
    _offs           | LUT entry index, 0..255
    =============== ==================================================
    """
    errC = ERROR.OK
    s0   = self.setPatternDispLUTOffsetPointer.__name__

    if (_offs < 0) or (_offs > 255):
      errC = ERROR.INVALID_PARAMS
    elif not self.isCheckOnly:
      data = [int(_offs)]
      res  = self.writeData(CMD_FORMAT_LIST.MBOX_ADDRESS, data)
      errC = res[0]

    if errC == ERROR.OK:
      self.log(" ", (LC_logStrMaskL +"LUT entry #{1}")
                    .format(s0, _offs), 2)
      return [errC]
    else:
      self.log("ERROR", LC_logStrMaskErr.format(s0, ErrorStr[errC]), 2)
      raise LCException(errC)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def setPatternDispLUTAccessControl(self, _cmd):
    """
    The LUT on the DLPC350 contains a mailbox to send data to different
    registers. This command selects which register receives the data.
    To select the flash image indexes or define the patterns used in
    the pattern sequence for the pattern display mode:

    1. Open the mailbox for the appropriate function by sending the
       appropriate command (for `_cmd`, use from enum class `MailboxCmd`
       either `OpenImageIndex`, `OpenPat` or `OpenPatVarExp`)
    2. Write the desired data to the mailbox using the
       `setPatternDispLUTData` method.
    3. Use this command (with `MailboxCmd.Close`) to close the mailbox.

    .. important:: Before executing this command, stop current pattern
                   sequence and after execution of this command,
                   validate before starting sequence.

    =============== ==================================================
    Parameters:
    =============== ==================================================
    _cmd            | 0=close
                    | 1=open for flash mode
                    | 2=open for pattern mode
                    | 3=open for variable exposure pattern mode
    =============== ==================================================
    """
    errC = ERROR.OK
    s0   = self.setPatternDispLUTAccessControl.__name__

    if _cmd not in MailboxCmd:
      errC = ERROR.INVALID_PARAMS
    elif not self.isCheckOnly:
      self.mBoxState = _cmd
      data = [int(_cmd.value)]
      res  = self.writeData(CMD_FORMAT_LIST.MBOX_CONTROL, data)
      errC = res[0]

    if errC == ERROR.OK:
      self.log(" ", (LC_logStrMaskL +"{1}")
                    .format(s0, MailboxCmdStr[_cmd]), 2)
      return [errC]
    else:
      self.log("ERROR", LC_logStrMaskErr.format(s0, ErrorStr[errC]), 2)
      raise LCException(errC)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def setPatternDispLUTData(self, _iImgOrPat,
                            _trigType=MailboxTrig.Internal, _bitDepth=1,
                            _LED=MailboxLED.None_, _invert=False,
                            _blackFill=False, _bufSwap=False,
                            _trigOut1High=False):
    """
    Define a LUT entry in a pattern display sequence.

    The parameters display mode, trigger mode, exposure, and frame rate
    must be set up before sending any mailbox data. If the Pattern
    Display Data Input Source is set to streaming, the image indexes
    are not required to be set. Regardless of the input source, the
    pattern definition must be set.

    If the mailbox is opened to define the flash image indexes, list
    the index numbers in the mailbox. For example, if image indexes 0
    through 3 are desired, write 0x0 0x1 0x2 0x3 to the mailbox.
    Similarly, if the desired image index sequence is 0, 1, 2, 1, then
    write 0x0 0x1 0x2 0x1 to the mailbox. Only the parameter
    `_iImgOrPat` is relevant.

    If the mailbox is opened to define the individual patterns, all
    parameters are relevant.

    For `_iImgOrPat` (in pattern mode), `_trigType`, and `_LED`  use
    the respective enum classes.

    =============== ==================================================
    Parameters:
    =============== ==================================================
    _iImgOrPat      | flash mode: image index (0..255)
                    | pattern mode: pattern index (`MailboxPat`)
    _trigType       | from `MailboxTrig`
    _bitDepth       | bit depth, 1..8
    _LED            | LED combination, from `MailboxLED`
    _invert         | True=invert pattern
    _blackFill      | True=Insert black-fill after current pattern
    _bufSwap        | True=Perform a buffer swap
    _trigOut1High   | True=TriggerOut1 will continue to be high,
                    | allows sharing time between patterns
    =============== ==================================================
    """
    errC = ERROR.OK
    s0   = self.setPatternDispLUTData.__name__
    data = []

    if self.mBoxState == MailboxCmd.OpenImageIndex:
      if (_iImgOrPat < 0) or (_iImgOrPat > 255):
        errC = ERROR.INVALID_PARAMS
    elif self.mBoxState == MailboxCmd.OpenPat:
      if (_trigType not in MailboxTrig) or\
         (_iImgOrPat not in MailboxPat) or\
         (_bitDepth < 1) or (_bitDepth > 8) or\
         (_LED not in MailboxLED):
        errC = ERROR.INVALID_PARAMS
    elif self.mBoxState == MailboxCmd.Close:
      errC = ERROR.MAILBOX_NOT_OPEN
    else:
      errC = ERROR.NOT_IMPLEMENTED

    if errC == ERROR.OK and not self.isCheckOnly:
      if self.mBoxState == MailboxCmd.OpenImageIndex:
        data   = [int(_iImgOrPat.value)]
        cmd    = CMD_FORMAT_LIST.MBOX_DATA
        cmd[2] = 1
      elif self.mBoxState == MailboxCmd.OpenPat:
        byte0  = int(_trigType.value) | (int(_iImgOrPat.value) << 2)
        byte1  = int(_bitDepth) | (int(_LED.value) << 4)
        byte2  = 0x01 if _invert else 0
        byte2 |= 0x02 if _blackFill else 0
        byte2 |= 0x04 if _bufSwap else 0
        byte2 |= 0x08 if _trigOut1High else 0
        data   = [byte0, byte1, byte2]
        cmd    = CMD_FORMAT_LIST.MBOX_DATA
        cmd[2] = 3
      res  = self.writeData(CMD_FORMAT_LIST.MBOX_DATA, data)
      errC = res[0]

    if errC == ERROR.OK:
      self.log(" ", (LC_logStrMaskL +"{1} bit(s), pattern={2}, "
                     "LED={3}, {4} {5} {6} {7} {8}")
                    .format(s0, _bitDepth, _iImgOrPat.value,
                            _LED.value,
                            MailboxTrigStr[_trigType],
                            "inverted" if _invert else "-",
                            "blackfill" if _blackFill else "-",
                            "buffer-swap" if _bufSwap else "-",
                            "shared-exposure"
                            if _trigOut1High else "-"), 2)
      return [errC]
    else:
      self.log("ERROR", LC_logStrMaskErr.format(s0, ErrorStr[errC]), 2)
      raise LCException(errC)

  # -------------------------------------------------------------------
  # LED-related
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def getLEDCurrents(self):
    """
    Get LED currents and returns these as list [code, [r,g,b]] with:

    =============== ==================================================
    Result:
    =============== ==================================================
    code            | 0=ok or error code
    [r,g,b]         | LED currents as PWM, 0..255
    =============== ==================================================
    """
    errC = ERROR.OK
    s0   = self.getLEDCurrents.__name__
    rgb  = [-1] * 3

    if not self.isCheckOnly:
      res  = self.readData(CMD_FORMAT_LIST.LED_CURRENT)
      errC = res[0]
      if errC == ERROR.OK:
        rgb = 255 -np.array(res[1][LC_firstDataByte:LC_firstDataByte+3])

    if errC == ERROR.OK:
      self.log(" ", (LC_logStrMaskL + "RGB currents {1}")
                    .format(s0, rgb.__str__()), 2)
      return [errC, rgb]
    else:
      self.log("ERROR", LC_logStrMaskErr.format(s0, ErrorStr[errC]), 2)
      raise LCException(errC)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def setLEDCurrents(self, _rgb):
    """
    Set LED currents.

    =============== ==================================================
    Parameters:
    =============== ==================================================
    _rgb            | [r,g,b] with LED currents as PWM, 0..255
    =============== ==================================================
    """
    errC = ERROR.OK
    s0   = self.setLEDCurrents.__name__

    if not self.isCheckOnly:
      newRGB = abs(np.clip(_rgb, 0,255) -255).tolist()
      res    = self.writeData(CMD_FORMAT_LIST.LED_CURRENT, newRGB)
      errC   = res[0]

    if errC == ERROR.OK:
      self.log(" ", (LC_logStrMaskL + "new RGB currents {1}")
                    .format(s0, _rgb.__str__()), 2)
      return [errC]
    else:
      self.log("ERROR", LC_logStrMaskErr.format(s0, ErrorStr[errC]), 2)
      raise LCException(errC)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def getLEDEnabled(self):
    """
    Returns state of LED pins (enabled/disabled) and if the sequence
    controls these pins as list [code, [isR,isG,isB], isSeqCtrl]]
    with:

    =============== ==================================================
    Result:
    =============== ==================================================
    code            | 0=ok or error code
    [isR,isG,isB]   | list of boolean values, one for each LED
    isSeqCtrl       | if True, the all LED enables are controlled
                    | by the sequencer and _rgb is ignored
    =============== ==================================================
    """
    errC = ERROR.OK
    s0   = self.getLEDEnabled.__name__
    res1 = [-1] *3
    res2 = 0

    if not self.isCheckOnly:
      res  = self.readData(CMD_FORMAT_LIST.LED_ENABLE)
      errC = res[0]
      if errC == ERROR.OK:
        data = res[1][LC_firstDataByte]
        res1 = [int((data & 0x01)>0),
                int((data & 0x02)>0),
                int((data & 0x04)>0)]
        res2 = (data & 0x08)>0

    if errC == ERROR.OK:
      self.log(" ", (LC_logStrMaskL + "{1}, {2}")
                    .format(s0, "enabled=" +res1.__str__(),
                            "sequence controlled"
                            if res2 else "manual"), 2)
      return [ERROR.OK, res1, res2]
    else:
      self.log("ERROR", LC_logStrMaskErr.format(s0, ErrorStr[errC]), 2)
      raise LCException(errC)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def setLEDEnabled(self, _rgb, _enableSeqCtrl):
    """
    Enable or disable LEDs or allow sequencer to control LED pins

    =============== ==================================================
    Parameters:
    =============== ==================================================
    _rgb            | list of boolean values, one for each LED
    _enableSeqCtrl  | if True, the all LED enables are controlled
                    | by the sequencer and _rgb is ignored
    =============== ==================================================
    """
    errC = ERROR.OK
    s0   = self.setLEDEnabled.__name__

    if not self.isCheckOnly:
      data = _rgb[0] | (_rgb[1] << 1) | (_rgb[2] << 2) | \
             (_enableSeqCtrl << 3)
      res  = self.writeData(CMD_FORMAT_LIST.LED_ENABLE, [data])
      errC = res[0]

    if errC == ERROR.OK:
      self.log(" ", (LC_logStrMaskL + "{1}, {2}")
                    .format(s0, "enabled=" +_rgb.__str__(),
                            "sequence controlled"
                            if _enableSeqCtrl else "manual"), 2)
      return [ERROR.OK]
    else:
      self.log("ERROR", LC_logStrMaskErr.format(s0, ErrorStr[errC]), 2)
      raise LCException(errC)

  # ===================================================================
  # Read/write routines
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def readData(self, _Cmd):
    # Read data from the device
    #
    iSeq       = 0
    LenLSB     = 2
    LenMSB     = 0
    wres       = self.LC.write([0, LC_B1Flags_read, iSeq, LenLSB, LenMSB,
                                _Cmd[1], _Cmd[0]])
    if wres <= 0:
      return [ERROR.NO_RESPONSE]
    else:
      # Device responded
      #
      res      = self.LC.read(LC_MaxDataLen+1, LC_Timeout_ms)
      flags    = res[0]
      length   = res[2]
      if ((flags & 0x20) > 0) or (length == 0):
        return [ERROR.NAK_ERROR]

    return [ERROR.OK, res]

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def writeData(self, _Cmd, _Data):
    # Write data to the device
    # TODO: Expand to data larger than one package
    #
    iSeq = self.nSeq
    LSB  = 2 +_Cmd[2]
    MSB  = 0
    cmd  = [0, LC_B1Flags_write, iSeq, LSB, MSB, _Cmd[1], _Cmd[0]] +_Data
    res  = self.LC.write(cmd)
    self.nSeq += 1

    if res <= 0:
      return [ERROR.NO_RESPONSE]
    else:
      # Device responded
      #
      if _Cmd[3] > 0:
        # Data is expected ...
        #
        res    = self.LC.read(LC_MaxDataLen+1, LC_Timeout_ms)
        flags  = res[0]
        length = res[2]
        if ((flags & 0x20) > 0) or (length == 0):
          return [ERROR.NAK_ERROR]

    return [ERROR.OK]

  # -------------------------------------------------------------------
  # Helpers
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  @staticmethod
  def verListFromInt32 (data, i):
    ver = (data[i+3] << 24) | (data[i+2] << 16) | (data[i+1] << 8) | data[i]
    return [(ver & 0xFF000000) >> 24, (ver & 0xFF0000) >> 16, ver & 0xFFFF]

  # -------------------------------------------------------------------
  # Logging
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def log(self, _sHeader, _sMsg, _logLevel):
    # Write message to log
    #
    self.lastMsgStr = _sMsg
    if _logLevel <= self.logLevel:
      if self.funcLog is None:
        print("{0!s:>8} #{1:>2}:{2}".format(_sHeader, self.devNum, _sMsg))
      else:
        if self.devNum >= 0:
          devStr = " #{0}".format(self.devNum)
        else:
          devStr = " unknown"
        self.funcLog(_sHeader, LC_IDStr +devStr +"|" +_sMsg)
'''
# ---------------------------------------------------------------------
