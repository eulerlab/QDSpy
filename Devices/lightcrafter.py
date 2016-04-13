#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
#  lightcrafter.py
#
#  ...
#
# ---------------------------------------------------------------------
#  Internal:
#
#
#  Copyright (c) 2014-2016 Thomas Euler
#  All rights reserved.
#
# ---------------------------------------------------------------------
__author__ = "thomas.euler@eulerlab.de"

# ---------------------------------------------------------------------
import Devices.hid as hid
import numpy       as np

# ---------------------------------------------------------------------
LC_width             = 912
LC_height            = 1140

# ---------------------------------------------------------------------
LC_VID               = 0x0451
LC_PID               = 0x6401

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

ErrorStr             = dict([
  (ERROR.OK,                "ok"),
  (ERROR.OPEN_FAILED,       "Failed to open device"),
  (ERROR.TIME_OUT,          "Time-out"),
  (ERROR.NO_RESPONSE,       "No reponse from device"),
  (ERROR.NAK_ERROR,         "Command not acknowledged"),
  (ERROR.COULD_NOT_CONNECT, "Could not connect to device"),
  (ERROR.INVALID_PARAMS,    "One or more parameters are invalid")
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
  xxx                = [ 0x1A, 0x1A, 0x01, 0]   # LUT_VALID,
  """
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
  xxx                = [ 0x1A, 0x29, 0x08, 0]   # PAT_EXPO_PRD,
  xxx                = [ 0x1A, 0x30, 0x01, 0]   # INVERT_DATA,
  xxx                = [ 0x1A, 0x31, 0x04, 0]   # PAT_CONFIG,
  xxx                = [ 0x1A, 0x32, 0x01, 0]   # MBOX_ADDRESS,
  xxx                = [ 0x1A, 0x33, 0x01, 0]   # MBOX_CONTROL,
  xxx                = [ 0x1A, 0x34, 0x00, 0]   # MBOX_DATA,
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
  
  def __init__(self, _isCheckOnly=False, _isVerbose=True):
    self.LC          = None
    self.nSeq        = 0
    self.isVerbose   = _isVerbose
    self.isCheckOnly = _isCheckOnly
    self.lastMsgStr  = ""

  # -------------------------------------------------------------------
  # Connect and disconnect the device
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def connect(self, _devNum=0):
    """
    Connect to lightcrafter.
    """
    if not(self.isCheckOnly):
      try:
        self.log("Trying to connect ...")            
        self.LC = hid.device()
        self.LC.open(LC_VID, LC_PID)

      except IOError as ex:
        self.LC = None
        self.log("Error ({0})".format(ex))      
        return [ERROR.COULD_NOT_CONNECT]

      self.LC.set_nonblocking(1)
      self.sManufacturer = self.LC.get_manufacturer_string()
      self.sProduct      = self.LC.get_product_string()
      self.sSN           = self.LC.get_serial_number_string()
  
      self.log("Connected to {0} by {1}".format(self.sProduct, 
                                                self.sManufacturer))      
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
        self.log("Disconnected")         
        
    return [ERROR.OK]    

  # -------------------------------------------------------------------
  # Hardware and system status-related
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

      self.log("Hardware errors : {0} {1} {2} {3} {4}"
               .format("-" if initOK else "init", 
                       "DMD" if DMDError else "-", 
                       "swap" if swapError else "-", 
                       "seq_abort" if seqAbort else "-",
                       "sequence" if seqError else "-"))
      
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
      
      self.log("System errors   : {0}".format("-" if MemoryOK else "memory"))
      
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

      self.log("Hardware status : {0} {1} {2} {3}"
               .format("DMD_parked" if DMDParked else "DMD_active", 
                       "seq_running" if SeqRunning else "-", 
                       "frame_buffer_frozen" if FBufFrozen else "-", 
                       "gamma_on" if GammaEnab else "-"))
                    
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

      self.log("Video signal    : {0}\n"
               "Resolution      : {1} x {2}\n"
               "Polarity        : HSync={3}, VSync={4}\n"
               "Pixel clock     : {5} kHz\n"
               "Frequency  [kHz]: HFreq={6}, VFreq={7}"
               .format("detected" if SigDetect else "-", HRes, VRes, 
                       HSyncPol, VSyncPol, PixClk_kHz, HFreq_kHz, VFreq_Hz)) 

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











      
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def setVideoGamma(self, _mode, _enabled):
    # to be implemented
    #
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
    # Set test pattern
    # _pattern : 0x0 = Solid field
    #            0x1 = Horizontal ramp
    #            0x2 = Vertical ramp
    #            0x3 = Horizontal lines
    #            0x4 = Diagonal lines
    #            0x5 = Vertical lines
    #            0x6 = Grid
    #            0x7 = Checkerboard
    #            0x8 = RGB ramp
    #            0x9 = Color bars
    #            0xA = Step bars
    #
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
    # Returns the LED currents
    # [ErrC, [r,g,b]] with r,g,b in 0...255
    #
    if self.isCheckOnly:
      return [ERROR.OK]      

    res    = self.readData(CMD_FORMAT_LIST.LED_CURRENT)
    if res[0] == ERROR.OK:
      rgb  = 255 -np.array(res[1][LC_firstDataByte:LC_firstDataByte+3])
      return [ERROR.OK, rgb]
    else:
      raise LCException(res[0])


  def setLEDCurrents(self, rgb):
    #
    #
    if self.isCheckOnly:
      return [ERROR.OK]      

    newRGB = list(abs(np.clip(rgb, 0,255) -255))
    res    = self.writeData(CMD_FORMAT_LIST.LED_CURRENT, newRGB)
    if res[0] == ERROR.OK:
      return [ERROR.OK]
    else:
      raise LCException(res[0])

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def getLEDEnabled(self):
    # Returns the LED status
    # [ErrC, [isR,isG,isB, isSeqControlled]]
    #
    if self.isCheckOnly:
      return [ERROR.OK]      
  
    res    = self.readData(CMD_FORMAT_LIST.LED_ENABLE)
    if res[0] == ERROR.OK:
      data = res[1][LC_firstDataByte]
      return [ERROR.OK, [int((data & 0x01)>0), int((data & 0x02)>0),
                         int((data & 0x04)>0), (data & 0x08)>0]]
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

      return [ERROR.OK, res]

  # -------------------------------------------------------------------
  # Logging
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def log(self, _msg):
    # ...
    #
    self.lastMsgStr = _msg
    if self.isVerbose:
      print(_msg)

# ---------------------------------------------------------------------

