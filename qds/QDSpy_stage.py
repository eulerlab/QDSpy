#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QDSpy module - to manage all projection device-related parameters

'Stage'
  This class manages all parameters concerning the projection device
  (e.g. screen, beamer), including scale, center of stimulation, global
  rotation angle, refresh rate, LED current etc.
  This class is a graphics API independent.

Copyright (c) 2013-2024 Thomas Euler
All rights reserved.

2024-08-10 - More lightcrafter types allowed; `lcr`import went to the
             end of the module
"""
# ---------------------------------------------------------------------
__author__ = "code@eulerlab.de"

import time
import qds.QDSpy_global as glo
import qds.libraries.log_helper as _log
import qds.QDSpy_gamma as gma
import qds.graphics.renderer_opengl as rdr

# ---------------------------------------------------------------------
class ScrDevType:
    generic = 0
    DLPLCR4500 = 1
    DLPLCR230NP = 2

ScrDevStr = dict(
    [(ScrDevType.generic, "generic"), 
     (ScrDevType.DLPLCR4500, "DLPLCR4500"),
     (ScrDevType.DLPLCR230NP, "DLPLCR230NP")]
)

# ---------------------------------------------------------------------
# Stimulus stage class
# ---------------------------------------------------------------------
class Stage(object):
    def __init__(self, _d, _isNew=False):
        '''Initialize stage object from parameters in dictionary (_d)
        '''
        self.dxScr = _d["dxScr"]
        self.dyScr = _d["dyScr"]
        self.scalX_umPerPix = _d["scalX_umPerPix"]
        self.scalY_umPerPix = _d["scalY_umPerPix"]
        self.rot_angle = _d["rot_angle"]
        self.centOffX_pix = _d["centOffX_pix"]
        self.centOffY_pix = _d["centOffY_pix"]
        self.centX0_pix = self.dxScr // 2
        self.centY0_pix = self.dyScr // 2
        self.centX_pix = self.centOffX_pix
        self.centY_pix = self.centOffY_pix
        self.scrReqFreq_Hz = _d["scrReqFreq_Hz"]
        self.dtFr_s = 1.0 / self.scrReqFreq_Hz
        self.scrIndex = _d["scrIndex"]
        self.scrIndexGUI = _d["scrIndGUI"]
        self.useScrOvl = _d["useScrOvl"]
        self.dxScr12 = _d["dxScr12"]
        self.dyScr12 = _d["dyScr12"]
        self.offXScr1_pix = _d["offXScr1_pix"]
        self.offYScr1_pix = _d["offYScr1_pix"]
        self.offXScr2_pix = _d["offXScr2_pix"]
        self.offYScr2_pix = _d["offYScr2_pix"]
        self.vFlipScr1 = -1 if _d["vFlipScr1"] else 1
        self.hFlipScr1 = -1 if _d["hFlipScr1"] else 1
        self.vFlipScr2 = -1 if _d["vFlipScr2"] else 1
        self.hFlipScr2 = -1 if _d["hFlipScr2"] else 1
        self.LEDs = []
        self.LCrStatus = [[], []]

        if _isNew:
            self.xWinLeft = _d["xWinLeft"]
            self.yWinTop = _d["yWinTop"]
            self.winXCorrFact = 1.0
            self.disFScrCmd = _d["disFScr"]

            # Determine the display device type
            R = rdr.Renderer()
            nScr = R.get_screen_count()
            if self.scrIndex >= nScr:
                self.scrIndex = nScr - 1
                _log.Log.write(
                    "WARNING",
                    "`int_screen_index_gui`=={0} but only {1} "
                    "screens were detected -> for fullscreen mode, screen "
                    "#{2} is used.".format(self.scrIndex + 1, nScr, self.scrIndex),
                )

            ver = self.getLCrFirmwareVer(0)
            if len(ver) > 0:
                self.scrDevType = self.getLCrDeviceType(0)
                self.LCrDevices = lcr.enumerateLightcrafters()
                self.LCrStatus[0] = self.getLCrStatus(0)
                self.isLEDSeqEnabled = [True] * len(lcr.LCrDeviceList)
            else:
                self.scrDevType = ScrDevType.generic
                ver = [0, 0, 0]
                self.isLEDSeqEnabled = [True]

            self.scrDevName = ScrDevStr[self.scrDevType]
            self.scrDevVersion = ver
            self.depth = R.get_screen_depth(self.scrIndex)
            self.scrDevFreq_Hz = R.get_screen_refresh(self.scrIndex)
            self.isFullScr = (self.dxScr == 0) or (self.dyScr == 0)

        else:
            self.xWinLeft = 0
            self.yWinTop = 0
            self.winXCorrFact = _d["winXCorrFact"]
            self.disFScrCmd = False

            self.scrDevName = _d["scrDevName"]
            self.scrDevType = _d["scrDevType"]
            self.scrDevVersion = _d["scrDevVersion"]
            self.depth = _d["depth"]
            self.scrDevFreq_Hz = _d["scrDevFreq_Hz"]
            self.isFullScr = _d["isFullScr"]
            self.isLEDSeqEnabled = _d["isLEDSeqEnabled"]

        # Generate gamma LUTs
        self.LUT_linDefault = gma.generateLinearLUT()
        self.LUT_userDefined = gma.generateInverseLUT()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def logInfo(self):
        _log.Log.write("INFO", "Display    : {0}".format(self.scrDevName))
        _log.Log.write(
            "ok",
            "Stage info : {0:d},{1:d} pixels, scale: {2:.2f},"
            "{3:.2f} {4}m/pix, rotation: {5:.0f}{6}, refresh: "
            "{7} Hz".format(
                int(self.centOffX_pix),
                int(self.centOffY_pix),
                self.scalX_umPerPix,
                self.scalY_umPerPix,
                "µ",
                self.rot_angle,
                "°",
                self.scrReqFreq_Hz,
            ),
        )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def logData(self):
        _log.Log.write(
            "DATA",
            {
                "scaling_x": self.scalX_umPerPix,
                "scaling_y": self.scalY_umPerPix,
                "offset_x": int(self.centOffX_pix),
                "offset_y": int(self.centOffY_pix),
                "rotation": self.rot_angle,
            }.__str__(),
        )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def durToFrames(self, _dur_s):
        if _dur_s > 0.0:
            dur = _dur_s * self.scrReqFreq_Hz
            return (round(dur), abs(dur - round(dur)) < glo.QDSpy_maxFrameDurDiff_s)
        else:
            return (-1, True)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getScaleOffsetAsDict(self):
        return {
            "centOffX_pix": self.centOffX_pix,
            "centOffY_pix": self.centOffY_pix,
            "scalX_umPerPix": self.scalX_umPerPix,
            "scalY_umPerPix": self.scalY_umPerPix,
            "rot_angle": self.rot_angle,
            "dxScr12": self.dxScr12,
            "dyScr12": self.dyScr12,
            "offXScr1_pix": self.offXScr1_pix,
            "offYScr1_pix": self.offYScr1_pix,
            "offXScr2_pix": self.offXScr2_pix,
            "offYScr2_pix": self.offYScr2_pix,
        }

    # -------------------------------------------------------------------
    # LED-related functions
    # -------------------------------------------------------------------
    def createLEDs(self, _Conf):
        """Create the LED dictionary from the configuration, if available
        """
        self.LEDs = []
        self.isLEDSeqEnabled = [True] * glo.QDSpy_MaxLightcrafterDev

        for iLED, LEDName in enumerate(_Conf.LEDNames):
            d = dict()
            d["name"] = LEDName
            d["current"] = _Conf.LEDDefCurr[iLED]
            d["max_current"] = _Conf.LEDMaxCurr[iLED]
            d["enabled"] = False
            d["peak_nm"] = _Conf.LEDPeakWLs[iLED]
            d["devIndex"] = _Conf.LEDDevIndices[iLED]
            d["LEDIndex"] = _Conf.LEDIndices[iLED]
            d["Qt_color"] = _Conf.LEDQtColors[iLED]
            self.LEDs.append(d)

        self.sendLEDChangesToLCr(_Conf)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def updateLEDs(self, _Conf):
        """Connect to lightcrafter to get LED currents and enabled state,
        and update LED dictionary
        """
        if not self.isLCrUsed(_Conf):
            return

        # Generate a new lightcrafter object
        seqEnabled = False
        LCr = lcr.Lightcrafter(
            _logLevel=glo.QDSpy_LCr_LogLevel, _funcLog=_log.Log.write
        )

        for iDev, Dev in enumerate(lcr.LCrDeviceList):
            try:
                result = LCr.connect(iDev)
                if result[0] == lcr.ERROR.OK:
                    # Get LED settings on the device(s)
                    current = [0] * 3
                    enabled = [False] * 3
                    result = LCr.getLEDCurrents()
                    if result[0] == lcr.ERROR.OK:
                        current = list(result[1])
                    result = LCr.getLEDEnabled()
                    if result[0] == lcr.ERROR.OK:
                        enabled = list(result[1])
                        seqEnabled = result[2]

                    self.isLEDSeqEnabled[iDev] = seqEnabled

                    for iCurr, Curr in enumerate(current):
                        for iLED, LED in enumerate(self.LEDs):
                            if (iDev == LED["devIndex"]) and (iCurr == LED["LEDIndex"]):
                                self.LEDs[iLED]["current"] = Curr
                                self.LEDs[iLED]["enabled"] = enabled[iCurr]
            finally:
                LCr.disconnect()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setLEDName(self, _index, _nameStr):
        if _index < len(self.LEDs):
            self.LEDs[_index]["name"] = _nameStr

    def setLEDEnabled(self, _index, _state):
        if _index < len(self.LEDs):
            self.LEDs[_index]["enabled"] = _state

    def setLEDCurrent(self, _index, _current):
        if _index < len(self.LEDs):
            self.LEDs[_index]["current"] = _current

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def sendLEDChangesToLCr(self, _Conf):
        """Connect to lightcrafter and update LED currents and enabled state
        """
        if not self.isLCrUsed(_Conf):
            return

        # Generate a new lightcrafter object
        LCr = lcr.Lightcrafter(
            _logLevel=glo.QDSpy_LCr_LogLevel, _funcLog=_log.Log.write
        )

        for iDev, Dev in enumerate(lcr.LCrDeviceList):
            try:
                result = LCr.connect(iDev)
                if result[0] == lcr.ERROR.OK:
                    # Set LEDs on the device(s)
                    #
                    currents = [0] * 3
                    enabled = [False] * 3
                    for iLED, LED in enumerate(self.LEDs):
                        if LED["devIndex"] == iDev:
                            currents[LED["LEDIndex"]] = LED["current"]
                            enabled[LED["LEDIndex"]] = LED["enabled"]

                    LCr.setLEDCurrents(currents[0:3])
                    LCr.setLEDEnabled(enabled[0:3], self.isLEDSeqEnabled[iDev])
            finally:
                LCr.disconnect()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def togglePatternSeq(self, _iLCr, _Conf, _doStart):
        """Connect to lightcrafter and start/stop the current pattern
        sequence
        """
        if not self.isLCrUsed(_Conf) and _iLCr not in [0, 1]:
            return

        LCr = lcr.Lightcrafter(_logLevel=2, _funcLog=_log.Log.write)
        result = LCr.connect(_iLCr)
        errC = result[0]
        if errC == lcr.ERROR.OK:
            try:
                if _doStart:
                    res = LCr.startPatternSequence()
                else:
                    res = LCr.stopPatternSequence()
                if res[0] is lcr.ERROR.OK:
                    done = False
                    n = 10
                    while not done and n > 0:
                        time.sleep(0.2)
                        res = LCr.getMainStatus(_logLev=3)
                        done = res[2]["SeqRunning"] is _doStart
                        n -= 1
                    if n == 0:
                        _log.Log.write("WARNING", "Toggle pattern sequence timeout")

            finally:
                LCr.disconnect()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def inquireLCrInfo(self, _iLCr, _Conf):
        """Connect to lightcrafter and inquire state
        """
        if not self.isLCrUsed and _iLCr not in [0, 1]:
            return

        self.LCrStatus[_iLCr] = self.getLCrStatus(_iLCr, _log.Log.write, 2)

    # -------------------------------------------------------------------
    # Lightcrafter-related functions
    # -------------------------------------------------------------------
    @staticmethod
    def isLCrUsed(_Conf):
        """Check configuration file and, if not available, also globals
        if the lightcrafter should be used
        """
        if _Conf is None:
            return glo.QDSpy_use_Lightcrafter
        else:
            return _Conf.useLCr

    @staticmethod
    def getLCrDeviceType(_devIndex):
        """Return device type
        """
        if glo.QDSpy_use_Lightcrafter:
            if glo.QDSpy_LCrDevTypeName == ScrDevStr[ScrDevType.DLPLCR4500]:
                return ScrDevType.DLPLCR4500
            elif glo.QDSpy_LCrDevTypeName == ScrDevStr[ScrDevType.DLPLCR230NP]:
                return ScrDevType.DLPLCR230NP
            else:
                return ScrDevType.generic

    @staticmethod
    def getLCrFirmwareVer(_devIndex):
        """Return firmware version of connected lightcrafter as list
        (e.g. [3,0,0]) or an empty list, if lightcrafter use is not
        enabled or device could not be connected
        """
        ver = []

        if glo.QDSpy_use_Lightcrafter:
            LCr = lcr.Lightcrafter(_logLevel=-1)
            result = LCr.connect(_devIndex)
            errC = result[0]
            if errC == lcr.ERROR.OK:
                try:
                    result = LCr.getFirmwareVersion()
                    errC = result[0]
                    if errC == lcr.ERROR.OK:
                        ver = result[2]["applicationSoftwareRev"]
                finally:
                    LCr.disconnect()

        return ver

    @staticmethod
    def getLCrStatus(_devIndex, _funcLog=None, _logLev=-1):
        """Return complete status of the lightcrafter as list of
        dictionaries
        """
        status = []

        if glo.QDSpy_use_Lightcrafter:
            LCr = lcr.Lightcrafter(_logLevel=_logLev, _funcLog=_funcLog)
            result = LCr.connect(_devIndex)
            errC = result[0]
            if errC == lcr.ERROR.OK:
                try:
                    hw_res = LCr.getHardwareStatus()
                    sys_res = LCr.getSystemStatus()
                    main_res = LCr.getMainStatus()
                    vid_res = LCr.getVideoSignalDetectStatus()
                    status = [hw_res, sys_res, main_res, vid_res]
                finally:
                    LCr.disconnect()

        return status

# ---------------------------------------------------------------------
if glo.QDSpy_use_Lightcrafter:
    dev = Stage.getLCrDeviceType(0)
    if dev == ScrDevType.DLPLCR4500:
        import qds.devices.lightcrafter_4500 as lcr
    elif dev == ScrDevType.DLPLCR230NP:
        import qds.devices.lightcrafter_230np as lcr

# ---------------------------------------------------------------------
