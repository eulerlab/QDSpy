#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Lightcrafter API

Note that this library requires firmware 3.0 and higher

Copyright (c) 2013-2017 Thomas Euler
All rights reserved.
"""
# ---------------------------------------------------------------------
__author__ = "thomas.euler@eulerlab.de"

# ---------------------------------------------------------------------
import numpy as np
import Devices.hid as hid

# ---------------------------------------------------------------------
LC_width             = 912
LC_height            = 1140

# ---------------------------------------------------------------------
LC_VID               = 0x0451
LC_PID               = 0x6401
LC_IDStr             = "LCr"
LC_Usage             = 65280

LC_MaxDataLen        = 64
LC_Timeout_ms        = 2000
LC_B1Flags_read      = 0b11000000   # bit7=1 read transaction,
                                    # bit6=1 reply requested
LC_B1Flags_write     = 0b00000000
LC_firstDataByte     = 4

# ---------------------------------------------------------------------
SOURCE_SEL_Parallel  = 0
SOURCE_SEL_Test      = 1
SOURCE_SEL_Flash     = 2
SOURCE_SEL_FPDLink   = 3

SOURCE_SEL_Par_30bit = 0
SOURCE_SEL_Par_24bit = 1
SOURCE_SEL_Par_20bit = 2
SOURCE_SEL_Par_16bit = 3
SOURCE_SEL_Par_10bit = 4
SOURCE_SEL_Par_8bit  = 5

DISP_MODE_Video      = 0x00
DISP_MODE_Pattern    = 0x01


# ---------------------------------------------------------------------
class ERROR:
  OK                 = 0
  OPEN_FAILED        = -1
  TIME_OUT           = -2
  NO_RESPONSE        = -3
  NAK_ERROR          = -4
  COULD_NOT_CONNECT  = -5
  INVALID_PARAMS     = -6
  DEVICE_NOT_FOUND   = -7

ErrorStr             = dict([
  (ERROR.OK,                "ok"),
  (ERROR.OPEN_FAILED,       "Failed to open device"),
  (ERROR.TIME_OUT,          "Time-out"),
  (ERROR.NO_RESPONSE,       "No reponse from device"),
  (ERROR.NAK_ERROR,         "Command not acknowledged"),
  (ERROR.COULD_NOT_CONNECT, "Could not connect to device"),
  (ERROR.INVALID_PARAMS,    "One or more parameters are invalid"),
  (ERROR.DEVICE_NOT_FOUND,  "Device with this index not found")
  ])

# ---------------------------------------------------------------------
class LCException(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

# ---------------------------------------------------------------------
class CMD_FORMAT_LIST:
  SOURCE_SEL         = [ 0x1A, 0x00, 0x01, 0]   # SOURCE_SEL
  PIXEL_FORMAT       = [ 0x1A, 0x02, 0x01, 0]   # PIXEL_FORMAT
  CLK_SEL            = [ 0x1A, 0x03, 0x01, 0]   # CLK_SEL
  CHANNEL_SWAP       = [ 0x1A, 0x37, 0x01, 0]   # CHANNEL_SWAP
  FPD_MODE           = [ 0x1A, 0x04, 0x01, 0]   # FPD_MODE
  #CURTAIN_COLOR     = [ 0, 0, 0]               # CURTAIN_COLOR
  POWER_CONTROL      = [ 0x02, 0x00, 0x01, 0]   # POWER_CONTROL,
  FLIP_LONG          = [ 0x10, 0x08, 0x01, 0]   # FLIP_LONG,
  FLIP_SHORT         = [ 0x10, 0x09, 0x01, 0]   # FLIP_SHORT,
  TPG_SEL            = [ 0x12, 0x03, 0x01, 0]   # TPG_SEL,
  PWM_INVERT         = [ 0x1A, 0x05, 0x01, 0]   # PWM_INVERT,
  LED_ENABLE         = [ 0x1A, 0x07, 0x01, 0]   # LED_ENABLE,
  GET_VERSION        = [ 0x02, 0x05, 0x00, 0]   # GET_VERSION,
  SW_RESET           = [ 0x08, 0x02, 0x00, 0]   # SW_RESET,
  #DMD_PARK          = [ 0, 0, 0]               # DMD_PARK,
  #BUFFER_FREEZE     = [ 0, 0, 0]               # BUFFER_FREEZE,
  VIDEO_SIG_DETECT   = [ 0x07, 0x1C, 0x1C, 0]   # VIDEO_SIG_DETECT

  STATUS_HW          = [ 0x1A, 0x0A, 0x00, 0]   # STATUS_HW,
  STATUS_SYS         = [ 0x1A, 0x0B, 0x00, 0]   # STATUS_SYS,
  STATUS_MAIN        = [ 0x1A, 0x0C, 0x00, 0]   # STATUS_MAIN,
  #CSC_DATA          = [ 0, 0, 0],              # CSC_DATA,
  GAMMA_CTL          = [ 0x1A, 0x0E, 0x01, 0]   # GAMMA_CTL,
  #BC_CTL            = [ 0, 0, 0],              # BC_CTL,
  PWM_ENABLE         = [ 0x1A, 0x10, 0x01, 0]   # PWM_ENABLE,
  PWM_SETUP          = [ 0x1A, 0x11, 0x06, 0]   # PWM_SETUP,
  PWM_CAPTURE_CONFIG = [ 0x1A, 0x12, 0x05, 0]   # PWM_CAPTURE_CONFIG,
  GPIO_CONFIG        = [ 0x1A, 0x38, 0x02, 0]   # GPIO_CONFIG,
  LED_CURRENT        = [ 0x0B, 0x01, 0x03, 0]   # LED_CURRENT,
  DISP_CONFIG        = [ 0x10, 0x00, 0x10, 0]   # DISP_CONFIG,
  #TEMP_CONFIG       = [ 0, 0, 0],              # TEMP_CONFIG,
  #TEMP_READ         = [ 0, 0, 0],              # TEMP_READ,
  """
  xxx                = [ 0x1A, 0x16, 0x09, 0]   # MEM_CONTROL,
  xxx                = [ 0, 0, 0],              # I2C_CONTROL,
  """
  LUT_VALID          = [ 0x1A, 0x1A, 0x01, 0]   # LUT_VALID,
  DISP_MODE          = [ 0x1A, 0x1B, 0x01, 0]   # DISP_MODE,
  """
  xxx                = [ 0x1A, 0x1D, 0x03, 0]   # TRIG_OUT1_CTL,
  xxx                = [ 0x1A, 0x1E, 0x03, 0]   # TRIG_OUT2_CTL,
  xxx                = [ 0x1A, 0x1F, 0x02, 0]   # RED_STROBE_DLY,
  xxx                = [ 0x1A, 0x20, 0x02, 0]   # GRN_STROBE_DLY,
  xxx                = [ 0x1A, 0x21, 0x02, 0]   # BLU_STROBE_DLY,
  """
  PAT_DISP_MODE      = [ 0x1A, 0x22, 0x01, 0]   # PAT_DISP_MODE,
  PAT_TRIG_MODE      = [ 0x1A, 0x23, 0x01, 0]   # PAT_TRIG_MODE,
  PAT_START_STOP     = [ 0x1A, 0x24, 0x01, 0]   # PAT_START_STOP,
  """
  xxx                = [ 0, 0, 0],              # BUFFER_SWAP,
  xxx                = [ 0, 0, 0],              # BUFFER_WR_DISABLE,
  xxx                = [ 0, 0, 0],              # CURRENT_RD_BUFFER,
  """
  PAT_EXPO_PRD       = [ 0x1A, 0x29, 0x08, 0]   # PAT_EXPO_PRD,
  #xxx               = [ 0x1A, 0x30, 0x01, 0]   # INVERT_DATA,
  PAT_CONFIG         = [ 0x1A, 0x31, 0x04, 0]   # PAT_CONFIG,
  MBOX_ADDRESS       = [ 0x1A, 0x32, 0x01, 0]   # MBOX_ADDRESS,
  MBOX_CONTROL       = [ 0x1A, 0x33, 0x01, 0]   # MBOX_CONTROL,
  MBOX_DATA          = [ 0x1A, 0x34, 0x00, 0]   # MBOX_DATA,
  """
  xxx                = [ 0x1A, 0x35, 0x04, 0]   # TRIG_IN1_DELAY,
  xxx                = [ 0, 0, 0],              # TRIG_IN2_CONTROL,
  xxx                = [ 0x1A, 0x39, 0x01, 0]   # SPLASH_LOAD,
  xxx                = [ 0x1A, 0x3A, 0x02, 0]   # SPLASH_LOAD_TIMING,
  xxx                = [ 0x08, 0x07, 0x03, 0]   # GPCLK_CONFIG,
  xxx                = [ 0, 0, 0],              # PULSE_GPIO_23,
  xxx                = [ 0, 0, 0],              # ENABLE_LCR_DEBUG,
  xxx                = [ 0x12, 0x04, 0x0C, 0]   # TPG_COLOR,
  xxx                = [ 0x1A, 0x13, 0x05, 0]   # PWM_CAPTURE_READ,
  xxx                = [ 0x30, 0x01, 0x00, 0]   # PROG_MODE,
  xxx                = [ 0x00, 0x00, 0x00, 0]   # BL_STATUS
  xxx                = [ 0x00, 0x23, 0x01, 0]   # BL_SPL_MODE
  xxx                = [ 0x00, 0x15, 0x01, 0]   # BL_GET_MANID,
  xxx                = [ 0x00, 0x15, 0x01, 0]   # BL_GET_DEVID,
  xxx                = [ 0x00, 0x15, 0x01, 0]   # BL_GET_CHKSUM,
  xxx                = [ 0x00, 0x29, 0x04, 0]   # BL_SETSECTADDR,
  xxx                = [ 0x00, 0x28, 0x00, 0]   # BL_SECT_ERASE,
  xxx                = [ 0x00, 0x2C, 0x04, 0]   # BL_SET_DNLDSIZE,
  xxx                = [ 0x00, 0x25, 0x00, 0]   # BL_DNLD_DATA,
  xxx                = [ 0x00, 0x2F, 0x01, 0]   # BL_FLASH_TYPE,
  xxx                = [ 0x00, 0x26, 0x00, 0]   # BL_CALC_CHKSUM,
  xxx                = [ 0x00, 0x30, 0x01, 0]   # BL_PROG_MODE,
  """

# ---------------------------------------------------------------------
def enumerateLightcrafters(_funcLog=None):
  """
  Enumerate ligtcrafter devices
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
  _isVerbose      | send messages to stdout
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
    if _isCheckOnly:
      return
    
    if not("LCrDeviceList" in globals()) or (len(LCrDeviceList) == 0): 
      #print("CALLED enumerateLightcrafters")
      LCrDeviceList  = enumerateLightcrafters(_funcLog)
     

  # -------------------------------------------------------------------
  # Connect and disconnect the device
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def connect(self, _devNum=-1):
    """
    Connect to lightcrafter. A device number (0,1,...) can be given if
    multiple lightcrafters are connected.
    """
    global LCrDeviceList
    
    if not(self.isCheckOnly):
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
            self.log(" ", "Trying to connect to LCr #{0}...".format(_devNum), 2)     

            self.LC = hid.device()
            self.LC.open_path(LCrDeviceList[_devNum][1])
            self.devNum = _devNum
          
          else:
            self.LC = None
            errC    = ERROR.DEVICE_NOT_FOUND
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
  
      self.log("ok", "Connected to {0} by {1}".format(self.sProduct, 
                                                      self.sManufacturer), 2)     
      if _devNum >= 0:
        self.log(" ", "as device #{0}".format(self.devNum), 2)    
      
    return [ERROR.OK]

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def disconnect(self):
    """
    Disconnects the lightcrafter.
    """
    if not(self.isCheckOnly):
      if self.LC != None:
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

    res    = self.readData(CMD_FORMAT_LIST.GET_VERSION)
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

      self.log(" ", "Firmware version: {0}.{1}.{2}"
                    .format(appVer[0], appVer[1], appVer[2]), 1)

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
      data       = res[1][LC_firstDataByte]
      initOK     = (data & 0x01) > 0
      DMDError   = (data & 0x04) > 0
      swapError  = (data & 0x08) > 0
      seqAbort   = (data & 0x40) > 0
      seqError   = (data & 0x80) > 0
      info       = {"initOK":initOK, "DMDError":DMDError,
                    "swapError":swapError, "seqAbort":seqAbort,
                    "seqError":seqError}

      self.log("ERROR", "Hardware errors : {0} {1} {2} {3} {4}"
               .format("-" if initOK else "init", 
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
      data       = res[1][LC_firstDataByte]
      MemoryOK   = (data & 0x01) > 0
      info       = {"MemoryOK":MemoryOK}
      
      self.log("ERROR", "System errors   : {0}"
               .format("-" if MemoryOK else "memory"), 1)
      
      return [ERROR.OK, data, info]
    else:
      raise LCException(res[0])

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def getMainStatus(self):
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

      self.log(" ", "Hardware status : {0} {1} {2} {3}"
                    .format("DMD_parked" if DMDParked else "DMD_active", 
                            "seq_running" if SeqRunning else "-", 
                            "frame_buffer_frozen" if FBufFrozen else "-", 
                            "gamma_on" if GammaEnab else "-"), 1)
                    
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
      PixClk_kHz = ((data[i+11] << 24) +(data[i+10] << 16) +\
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

      self.log(" ", "Video signal    : {0}".format("detected" if SigDetect else "-"), 1)
      self.log(" ", "Resolution      : {0} x {1}".format(HRes, VRes), 1)
      self.log(" ", "Polarity        : HSync={0}, VSync={1}".format(HSyncPol, VSyncPol), 1)
      self.log(" ", "Pixel clock     : {0} kHz".format(PixClk_kHz), 1)
      self.log(" ", "Frequency  [kHz]: HFreq={0}, VFreq={1}".format(HFreq_kHz, VFreq_Hz), 1)
      info       = {"SigDetect":SigDetect, "HRes":HRes, "VRes":VRes,
                    "HSyncPol":HSyncPol, "VSyncPol":VSyncPol,
                    "PixClk_kHz":PixClk_kHz, "HFreq_kHz":HFreq_kHz,
                    "VFreq_Hz":VFreq_Hz}
      return [ERROR.OK, info]
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
    if self.isCheckOnly:
      return [ERROR.OK]      

    res    = self.writeData(CMD_FORMAT_LIST.SW_RESET, [1])
    if res[0] == ERROR.OK:
      return [ERROR.OK]
    else:
      raise LCException(res[0])

  # -------------------------------------------------------------------
  # Input source and mode selection
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def setInputSource(self, _source, _bitDepth):
    """
    Defines the input source of the device.
     
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
    if not(_source in range(0,4)) or not(_bitDepth in range(0,6)):
      return [ERROR.INVALID_PARAMS]
    
    if self.isCheckOnly:
      return [ERROR.OK]      

    data   = (_source | (_bitDepth << 3))
    res    = self.writeData(CMD_FORMAT_LIST.SOURCE_SEL, [data])
    if res[0] == ERROR.OK:
      return [ERROR.OK]
    else:
      raise LCException(res[0])
      
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def setDisplayMode(self, _mode):
    """
    Sets the display mode of the device.
     
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
    if not(_mode in [0,1]):
      return [ERROR.INVALID_PARAMS]
    
    if self.isCheckOnly:
      return [ERROR.OK]      
    
    res    = self.writeData(CMD_FORMAT_LIST.DISP_MODE, [_mode])
    if res[0] == ERROR.OK:
      return [ERROR.OK]
    else:
      raise LCException(res[0])

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def validateDataCommandResponse(self):
    """
    The Validate Data command checks the programmed pattern display modes 
    and indicates any invalid settings.
     
    =============== ==================================================
    Result:
    =============== ==================================================
    data            | the original data byte returned by the device
    info            | a dictionary with following entry:
                    | PeriodSettingInvalid, LUTPatternNumberInvalid,
                    | TrigOut1Invalid, PostVectSettingsInvalid,
                    | FrPerExpDiffInvalid, isBusyValidating
    =============== ==================================================
    """
    if self.isCheckOnly:
      return [ERROR.OK]      
    '''
    res    = self.writeData(CMD_FORMAT_LIST.LUT_VALID, [0])
    if res[0] != ERROR.OK:
      raise LCException(res[0])
    '''  
    res    = self.readData(CMD_FORMAT_LIST.LUT_VALID)
    if res[0] == ERROR.OK:
      data = res[1][LC_firstDataByte]
      PeriodSettingInvalid    = int((data & 0x01) > 0)
      LUTPatternNumberInvalid = int((data & 0x02) > 0)
      TrigOut1Invalid         = int((data & 0x04) > 0)
      PostVectSettingsInvalid = int((data & 0x08) > 0)
      FrPerExpDiffInvalid     = int((data & 0x10) > 0)
      isBusyValidating        = int((data & 0x80) > 0)

      if isBusyValidating:
        self.log(" ", 
                 "DLPC350 is busy validating, once it is cleared, then, you"
                 " can interpret the rest of the bits", 1)
        info = {}
        
      else:
        self.log(" ", 
                 "Selected exposure or frame period settings are invalid                   : {0}\n"
                 "Selected pattern numbers in LUT are invalid                              : {1}\n"
                 "Warning, continuous Trigger Out1 request or overlapping black sectors    : {2}\n"
                 "Warning, post vector was not inserted prior to external triggered vector : {3}\n"
                 "Warning, frame period or exposure difference is less than 230usec        : {4}\n"
                 .format(PeriodSettingInvalid, LUTPatternNumberInvalid, 
                         TrigOut1Invalid, PostVectSettingsInvalid, 
                         FrPerExpDiffInvalid), 1) 
        info = {"PeriodSettingInvalid":PeriodSettingInvalid, 
                "LUTPatternNumberInvalid":LUTPatternNumberInvalid, 
                "TrigOut1Invalid":TrigOut1Invalid,
                "PostVectSettingsInvalid":PostVectSettingsInvalid, 
                "FrPerExpDiffInvalid":FrPerExpDiffInvalid}
    
      return [ERROR.OK, info]
    
    else:
      raise LCException(res[0])
      

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def setPatternTriggerMode(self, _mode):
    """
    Sets the Pattern Trigger Mode.
    
    Important: before executing this command, stop current pattern sequence
    and after execution of this command, validate before starting sequence.
    
    =============== ==================================================
    Parameters:
    =============== ==================================================
    _mode           | 0=VSYNC serves to trigger the pattern 
                    | display sequence
                    | 1=internally or externally generated triggers
                    | (TRIG_IN_1 and TRIG_IN_2)
                    | 2=TRIG_IN_1 alternates between two patterns, 
                    | while TRIG_IN_2 advances to next pair of
                    | patterns
                    | 3=internally or externally generated triggers
                    | for variable exposure sequence
                    | 4=VSYNC triggered for variable exposure 
                    | display sequence
    =============== ==================================================
    """
    if not(_mode in range(0,4)):
      return [ERROR.INVALID_PARAMS]
    
    if self.isCheckOnly:
      return [ERROR.OK]      
    
    res    = self.writeData(CMD_FORMAT_LIST.PAT_TRIG_MODE, [_mode])
    if res[0] == ERROR.OK:
      return [ERROR.OK]
    else:
      raise LCException(res[0])

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def setPatternDisplayDataInputSource(self, _src):
    """
    Sets the Pattern Data Input Source.
    
    Important: before executing this command, stop current pattern sequence
    and after execution of this command, validate before starting sequence.
    
    =============== ==================================================
    Parameters:
    =============== ==================================================
    _mode           | 0=Data is streamed through the 24bit RGB
                    | /FPD-link interface
                    | 3=Data is fetched from flash memory
    =============== ==================================================
    """
    if not(_src in [0x00, 0x11]):
      return [ERROR.INVALID_PARAMS]
    
    if self.isCheckOnly:
      return [ERROR.OK]      
    
    res    = self.writeData(CMD_FORMAT_LIST.PAT_DISP_MODE, [_src])
    if res[0] == ERROR.OK:
      return [ERROR.OK]
    else:
      raise LCException(res[0])
  
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def startPatternSequence(self):
    """
    Starts the programmed pattern sequence.
    
    Important: after executing this command, poll the system status..
    """
    if self.isCheckOnly:
      return [ERROR.OK]      
    
    res    = self.writeData(CMD_FORMAT_LIST.PAT_START_STOP, [0x10])
    if res[0] == ERROR.OK:
      return [ERROR.OK]
    else:
      raise LCException(res[0])
  
  def pausePatternSequence(self):
    """
    Pauses the programmed pattern sequence.
    
    Important: after executing this command, poll the system status..
    """
    if self.isCheckOnly:
      return [ERROR.OK]      
    
    res    = self.writeData(CMD_FORMAT_LIST.PAT_START_STOP, [0x01])
    if res[0] == ERROR.OK:
      return [ERROR.OK]
    else:
      raise LCException(res[0])

  def stopPatternSequence(self):
    """
    Stop the programmed pattern sequence.
    
    Important: after executing this command, poll the system status..
    """
    if self.isCheckOnly:
      return [ERROR.OK]      
    
    res    = self.writeData(CMD_FORMAT_LIST.PAT_START_STOP, [0x00])
    if res[0] == ERROR.OK:
      return [ERROR.OK]
    else:
      raise LCException(res[0])

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def setPatternExpTimeFrPer(self, _pet_us, _frp_us):
    """ 
    Set Pattern Exposure Time and Frame Period.
    
    The Pattern Exposure Time and Frame Period dictates the length of time
    a pattern is exposed and the frame period. Either the pattern exposure 
    time must be equivalent to the frame period, or the pattern exposure
    time must be less than the frame period by 230 μs.
    
    Important: before executing this command, stop current pattern sequence
    and after execution of this command, validate before starting sequence.

    =============== ==================================================
    Parameters:
    =============== ==================================================
    _pet_us         | pattern exposure time in [us]
    _frp_us         | frame period in [us]
    =============== ==================================================
    """
    if self.isCheckOnly:
      return [ERROR.OK]      

    if (_pet_us <= 0) or (_frp_us <= 0):
      return [ERROR.INVALID_PARAMS]
    
    data = [] 
    data.append(_pet_us & 0x000000FF)
    data.append(_pet_us & 0x000000FF)
    data.append(_pet_us & 0x000000FF)
    data.append(_pet_us & 0x000000FF)
    
    #HRes       = (data[i+2] << 8) +data[i+1]


    res    = self.writeData(CMD_FORMAT_LIST.PAT_EXPO_PRD, data)
    if res[0] == ERROR.OK:
      return [ERROR.OK]
    else:
      raise LCException(res[0])
      
  """
  NESCESSARY:
      
      PAT_EXPO_PRD
    
  2.4.3.4.3 Pattern Exposure Time and Frame Period
  (I2C: 0x66)
  (USB: CMD2: 0x1A, CMD3: 0x29)
  The Pattern Exposure Time and Frame Period dictates the length of time a pattern is exposed and the
  frame period. Either the pattern exposure time must be equivalent to the frame period, or the pattern
  exposure time must be less than the frame period by 230 μs. Before executing this command, stop the
  current pattern sequence. After executing this command, send the Validation command (I2C: 0x7D or
  USB: 0x1A1A) once before starting the pattern sequence.
  
  
  2.4.3.4.5 Pattern Display LUT Control
  (I2C: 0x75)
  (USB: CMD2: 0x1A, CMD3: 0x31)
  The Pattern Display LUT Control Command controls the execution of patterns stored in the lookup table.
  Before executing this command, stop the current pattern sequence. After executing this command, send
  the Validation command (I2C: 0x7D or USB: 0x1A1A) once before starting the pattern sequence.
  
  2.4.3.4.6 Pattern Display Look-Up Table
  The DLPC350 supports a Pattern Display Look-Up Table (LUT) that defines the pattern sequence and the
  configuration parameters for each pattern in the sequence. To create this LUT, the programmer must first
  setup the display mode, trigger mode, exposure, frame rate, and so forth, before writing data to the LUT.
  After properly configured, the Pattern Display LUT Access Control command writes the LUT.
  
  2.4.3.4.7 Pattern Display LUT Offset Pointer
  (I2C: 0x76)
  (USB: CMD2: 0x1A, CMD3: 0x32)
  The Pattern Display LUT Offset Pointer defines the location of the LUT entries in the DLPC350 memory
                                                                                       
  2.4.3.4.8 Pattern Display LUT Access Control
  (I2C: 0x77)
  (USB: CMD2: 0x1A, CMD3: 0x33)
  The LUT on the DLPC350 has a mailbox to send data to different registers, and this command selects
  which register will receive the data. To select the flash image indexes or define the patterns used in the
  pattern sequence for the pattern display mode, first open the mailbox for the appropriate function by
  writing the appropriate bit. Second, write the desired data to the mailbox using the Pattern Display LUT
  Data command (I2C: 0x78 or USB 0x1A34), then use this command to close the mailbox. Before executing
  this command, stop the current pattern sequence. After executing this command, send the Validation
  command (I2C: 0x7D or USB: 0x1A1A) once before starting the pattern sequence.
  
  2.4.3.4.9 Pattern Display LUT Data
  (I2C: 0x78)
  (USB: CMD2: 0x1A, CMD3: 0x34)
  The following parameters: display mode, trigger mode, exposure, and frame rate must be set-up
  before sending any mailbox data. If the Pattern Display Data Input Source is set to streaming, the
  image indexes do not need to be set. Regardless of the input source, the pattern definition must be set.
  If the mailbox was opened to define the flash image indexes, list the index numbers in the mailbox. For
  example, if image indexes 0 through 3 are desired, write 0x0 0x1 0x2 0x3 to the mailbox. Similarly, if the
  desired image index sequence is 0, 1, 2, 1, then write 0x0 0x1 0x2 0x1 to the mailbox.
  
  
  NEEDED?
  2.4.3.4.10 Pattern Display Variable Exposure LUT Offset Pointer
  (I2C: 0x5C)
  (USB: CMD2: 0x1A, CMD3: 0x3F)
  The Pattern Display Variable Exposure LUT Offset Pointer defines the location of the Variable Exposure
  LUT entries in the DLPC350 memory
  
  2.4.3.4.11 Pattern Display Variable Exposure LUT Control
  (I2C: 0x5B)
  (USB: CMD2: 0x1A, CMD3: 0x40)
  The Pattern Display Variable Exposure LUT Control Command controls the execution of patterns stored in
  the lookup table. Before executing this command, stop the current pattern sequence. After executing this
  command, send the Validation command (I2C: 0x7D or USB: 0x1A1A) once before starting the pattern
  sequence.
  
  2.4.3.4.12 Pattern Display Variable Exposure LUT Data
  (I2C: 0x5D)
  (USB: CMD2: 0x1A, CMD3: 0x3E)
  The following parameters: Display Pattern mode, Display Data Input Source, Variable Exposure
  Trigger mode, Variable Exposure Access Control, Variable Exposure LUT Control, and Variable
  Exposure Offset Pointer Control must be set-up before sending any mailbox data. For each LUT
  entry that is sent, the Variable Exposure Offset Pointer must be incremented. See Figure 2-12 for
  an example of sending a Variable Exposure Pattern Sequence. If the Pattern Display Data Input
  Source is set to streaming, the image indexes do not need to be set. Regardless of the input source,
  the pattern definition must be set.
  If the mailbox was opened to define the flash image indexes, list the index numbers in the mailbox. For
  example, if image indexes 0 through 3 are desired, write 0x0 0x1 0x2 0x3 to the mailbox. Similarly, if the
  desired image index sequence is 0, 1, 2, 1, then write 0x0 0x1 0x2 0x1 to the mailbox.
  
  
  
  
  """
      
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def setVideoGamma(self, _mode, _enabled):
    """ To be implemented
    """
    if not(_mode in range(0,4)):
      return [ERROR.INVALID_PARAMS]

    if self.isCheckOnly:
      return [ERROR.OK]      
      
    data  = (_mode & (_enabled << 7))
    #data = abs(data -255)
    res   = self.writeData(CMD_FORMAT_LIST.GAMMA_CTL, [data])
    if res[0] == ERROR.OK:
      return [ERROR.OK]
    else:
      raise LCException(res[0])
      
  # -------------------------------------------------------------------
  # Internal test pattern-related       
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def setTestPattern(self, _pattern):
    """ 
    Set test pattern.
     
    =============== ==================================================
    Parameters:
    =============== ==================================================
    _pattern        | 0x0 = Solid field
                    | 0x1 = Horizontal ramp
                    | 0x2 = Vertical ramp
                    | 0x3 = Horizontal lines
                    | 0x4 = Diagonal lines
                    | 0x5 = Vertical lines
                    | 0x6 = Grid
                    | 0x7 = Checkerboard
                    | 0x8 = RGB ramp
                    | 0x9 = Color bars
                    | 0xA = Step bars
    =============== ==================================================
    """
    if not(_pattern in range(0,10)):
      return [ERROR.INVALID_PARAMS]
    
    if self.isCheckOnly:
      return [ERROR.OK]      
    
    data   = _pattern
    res    = self.writeData(CMD_FORMAT_LIST.TPG_SEL, [data])
    if res[0] == ERROR.OK:
      return [ERROR.OK]
    else:
      raise LCException(res[0])
      
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
    if self.isCheckOnly:
      return [ERROR.OK]      

    res    = self.readData(CMD_FORMAT_LIST.LED_CURRENT)
    if res[0] == ERROR.OK:
      rgb  = 255 -np.array(res[1][LC_firstDataByte:LC_firstDataByte+3])
      self.log("ok", "getLEDCurrents " +rgb.__str__(), 1)
      return [ERROR.OK, rgb]
    else:
      raise LCException(res[0])


  def setLEDCurrents(self, _rgb):
    """ 
    Set LED currents.
    
    =============== ==================================================
    Parameters:
    =============== ==================================================
    _rgb            | [r,g,b] with LED currents as PWM, 0..255
    =============== ==================================================
    """
    if self.isCheckOnly:
      return [ERROR.OK]      

    newRGB = list(abs(np.clip(_rgb, 0,255) -255))
    res    = self.writeData(CMD_FORMAT_LIST.LED_CURRENT, newRGB)
    if res[0] == ERROR.OK:
      self.log("ok", "setLEDCurrents " +_rgb.__str__(), 1)
      return [ERROR.OK]
    else:
      raise LCException(res[0])

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
    if self.isCheckOnly:
      return [ERROR.OK]      
  
    res    = self.readData(CMD_FORMAT_LIST.LED_ENABLE)
    if res[0] == ERROR.OK:
      data = res[1][LC_firstDataByte]
      res1 = [int((data & 0x01)>0), int((data & 0x02)>0), int((data & 0x04)>0)]
      res2 = (data & 0x08)>0
      self.log("ok", "getLEDEnabled " +res1.__str__() +" " +res2.__str__(), 1)
      return [ERROR.OK, res1, res2]
    else:
      raise LCException(res[0])


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
    if self.isCheckOnly:
      return [ERROR.OK]      

    data   = _rgb[0] | (_rgb[1] << 1) | (_rgb[2] << 2) | (_enableSeqCtrl << 3)
    res    = self.writeData(CMD_FORMAT_LIST.LED_ENABLE, [data])
    if res[0] == ERROR.OK:
      self.log("ok", "setLEDEnabled " +_rgb.__str__() +
                     " " +_enableSeqCtrl.__str__(), 1)
      return [ERROR.OK]
    else:
      raise LCException(res[0])


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
    iSeq       = self.nSeq
    self.nSeq += 1
    LenLSB     = 2 +_Cmd[2]
    LenMSB     = 0
    res        = self.LC.write([0, LC_B1Flags_write, iSeq, LenLSB, LenMSB,
                                _Cmd[1], _Cmd[0]] +_Data[0:_Cmd[2]])
    if res <= 0:
      return [ERROR.NO_RESPONSE]
    else:
      # Device responded
      #
      if _Cmd[3] > 0:
        # Data is expected ...
        #
        res     = self.LC.read(LC_MaxDataLen+1, LC_Timeout_ms)
        flags   = res[0]
        length  = res[2]
        if ((flags & 0x20) > 0) or (length == 0):
          return [ERROR.NAK_ERROR]
    
    return [ERROR.OK]

  # -------------------------------------------------------------------
  # Helpers
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def verListFromInt32 (self, data, i):
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
        print("{0!s:>8} #{1}:{2}".format(_sHeader, self.devNum, _sMsg))
      else:
        if self.devNum >= 0:
          devStr = " #{0}".format(self.devNum)
        else:
          devStr = " unknown"
        self.funcLog(_sHeader, LC_IDStr +devStr +"|" +_sMsg)

# ---------------------------------------------------------------------

