#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QDSpy module - main program of command line-version of QDSpy

This is a simple Python software for scripting and presenting stimuli
for visual neuroscience. It is based on QDS, currently uses OpenGL via
pyglet for graphics. It primarly targets Windows, but may also run on
other operating systems

Copyright (c) 2013-2024 Thomas Euler
All rights reserved.

2022-08-03 - Adapt to LINUX
2022-08-06 - Some reformatting
2024-05-12 - Catch if `conda` is not installed
           - Reformatted (using Ruff)
           - Sound volume as parameter of `prepare`
2024-08-08 - New digital I/O device added ("RaspberryPi")           

Note1: `pyglet`is imported but only to determine if it is installed
"""
# ---------------------------------------------------------------------
__author__ = "code@eulerlab.de"

import time
import sys
import gc
import os
import platform
import subprocess
import pickle
from multiprocessing import freeze_support
import qds.QDSpy_global as glo
import qds.QDSpy_stim as stm
import qds.QDSpy_config as cfg
import qds.QDSpy_core_presenter as cpr
import qds.QDSpy_core_view as cvw
import qds.QDSpy_core_support as csp
import qds.libraries.multiprocess_helper as mpr
from qds.libraries.log_helper import Log
import qds.QDSpy_gamma as gma
import qds.QDSpy_probeCenter as pce
import qds.devices.digital_io as dio
from qds.QDSpy_stage import Stage, ScrDevType

PLATFORM_WINDOWS = platform.system() == "Windows"
if PLATFORM_WINDOWS:
    from distutils.spawn import find_executable # type: ignore

if glo.QDSpy_use_Lightcrafter:
    dev = Stage.getLCrDeviceType(0)
    if dev == ScrDevType.DLPLCR4500:
        import qds.devices.lightcrafter_4500 as lcr
    elif dev == ScrDevType.DLPLCR230NP:
        import qds.devices.lightcrafter_230np as lcr

# ---------------------------------------------------------------------
# Convenience functions
# ---------------------------------------------------------------------
def logGraphModuleInfo():
    try:
        import pyglet
        import moviepy.version as mpv

        Log.write("INFO", "{0:11}: v{1}".format("pyglet", pyglet.version))
        Log.write("INFO", "{0:11}: v{1}".format("moviepy", mpv.__version__))

    except ModuleNotFoundError:
        Log.write("WARNING", "pyglet and/or moviepy not present")

# ---------------------------------------------------------------------
def setPerformanceHigh(_Conf):
    if _Conf.disGC:
        gc.disable()
    if _Conf.incPP:
        csp.setHighProcessPrior()

def setPerformanceNormal(_Conf):
    if _Conf.incPP:
        csp.setNormalProcessPrior()
    if _Conf.disGC:
        gc.enable()

# ---------------------------------------------------------------------
def loadStimulus(_fNameStim, _Stim):
    if len(_fNameStim) == 0:
        Log.write("FATAL", "No stimulus file name provided")
        return False
    try:
        _Stim.load(_fNameStim)
        return True
    except:  # noqa: E722
        if _Stim.getLastErrC() != stm.StimErrC.ok:
            _sErr = _Stim.getLastErrStr()
            Log.write("FATAL", "Aborted ({0})".format(_sErr))
            return False

# ---------------------------------------------------------------------
def connectLCrs(_Conf=None, _Stim=None):
    if _Stim is not None and not _Stim.isUseLCr:
        return []
    if _Conf is None:
        if not glo.QDSpy_use_Lightcrafter:
            return []
    else:
        if not _Conf.useLCr:
            return []
    LCrList = lcr.enumerateLightcrafters()
    LCrs = []
    nLCrOk = 0
    for iLCr, LCr in enumerate(LCrList):
        LCrs.append(
            lcr.Lightcrafter(
                _isCheckOnly=False,
                _funcLog=Log.write, _logLevel=glo.QDSpy_LCr_LogLevel,
            )
        )
        result = LCrs[iLCr].connect(iLCr)
        if result[0] != lcr.ERROR.OK:
            LCrs[iLCr] = None
        else:
            nLCrOk += 1
    if nLCrOk == 0:
        Log.write("WARNING", "This script requires a lightcrafter")
    return LCrs


def disconnectLCrs(_LCrs):
    for LCr in _LCrs:
        if LCr is not None:
            LCr.disconnect()
    return []

# ---------------------------------------------------------------------
def switchGammaLUTByColorMode(_Conf, _View, _Stage, _Stim):
    if _Conf.allowGammaLUT:
        if _Stim is not None:
            _modes = [stm.ColorMode.range0_1, stm.ColorMode.range0_255]
            if _Stim.colorMode in _modes:
                Log.write(" ", "Trying to set user-defined gamma LUT ...")
                gma.setGammaLUT(_View.winPre._dc, _Stage.LUT_userDefined)
            else:
                Log.write(
                    " ",
                    f"Special color mode (#{_Stim.colorMode}), "
                    "setting linear gamma LUT ..."
                )
                gma.setGammaLUT(_View.winPre._dc, _Stage.LUT_linDefault)

def restoreGammaLUT(_Conf, _View):
    if _Conf.allowGammaLUT:
        Log.write(" ", "Restoring linear gamma LUT ...")
        gma.restoreGammaLUT(_View.winPre._dc)

# ---------------------------------------------------------------------
# MAIN
# _____________________________________________________________________
def main(_fNameStim, _isParentGUI, _Sync=None):
    """ Run a stimulus file.
    """
    if _isParentGUI:
        Log.setGUISync(_Sync, noStdOut=cfg.getParsedArgv().gui)
    
    # Load configuration ...
    _Conf = cfg.Config()
    
    # Display startup message
    Log.write(
        "***", 
        glo.QDSpy_versionStr + " Presenter - " + glo.QDSpy_copyrightStr
    )
    Log.write("ok", "Initializing ...")
    s = 'ENABLED' if _Conf.incPP else 'DISABLED'
    Log.write(" ", f"{s:11}: high process priority during presentation")
    s = 'DISABLED' if _Conf.disGC else 'ENABLED'
    Log.write(" ", f"{s:11}: automatic garbage collection")

    # Log info about the relevant software packages
    v = sys.version_info
    txt = f"{v[0]}.{v[1]}.{v[2]}"
    Log.write("INFO", f"{'Python':11}: v{txt}")
    if PLATFORM_WINDOWS:
        if find_executable("conda") is not None:
            txt = subprocess.Popen(
                "conda -V", shell=True, stdout=subprocess.PIPE
            ).stdout.read()
            Log.write(
                "INFO", 
                f"{'Conda':11}: v{txt.decode()[6:12]}"
            )
    logGraphModuleInfo()

    # Generate stage and stimulus instances, as well as a view instance
    # (OpenGL window)
    _Stage = _Conf.createStageFromConfig()
    _Stim = stm.Stim()
    _View = cvw.View(_Stage, _Conf)
    _View.createStimulusWindow()
    _Stage.logInfo()

    # Update representation of lightcrafter hardware, if present
    _Stage.createLEDs(_Conf)
    _Stage.updateLEDs(_Conf)

    # Initialize digital IO hardware, if requested
    if _Conf.useDIO:
        if _Conf.DIObrdType.lower() == "arduino":
            _IO = dio.devIO_Arduino(
                _Conf.DIObrd, glo.QDSpy_Arduino_baud, _funcLog=Log.write
            )
            Log.write(
                "WARNING",
                f"Ensure that Arduino BAUD rate is {glo.QDSpy_Arduino_baud}"
            )
        elif _Conf.DIObrdType.lower() == "raspberrypi":    
            # Note: Currently works only with the default pins 
            # (GPIO26 for trigger-in and GPIO27 for marker-out)
            _IO = dio.devIO_RPi(_funcLog=Log.write)
            Log.write(
                "INFO", 
                "Raspberry Pi: GPIO26 for trigger-in and GPIO27 for marker-out"
            )
        else:
            try:
                ULID = dio.dictULDevices[_Conf.DIObrdType.upper()]
                _IO = dio.devIO_UL(
                    ULID, _Conf.DIObrd, _Conf.DIOdev, _funcLog=Log.write
                )
            except KeyError:
                _IO = None

        if not (_IO):
            Log.write("ERROR", "I/O hardware device name not recognized.")

        elif not _IO.isReady:
            Log.write(
                "ERROR",
                "I/O hardware could not be initialized. Set "
                + "`bool_use_digitalio` in `QDSpy.ini` to False.",
            )
        else:
            if not _Conf.DIObrdType.lower() in ["arduino", "raspberrypi"]:
                # Measurement Computing hardware is used, and needs to be 
                # configured ...
                port = _IO.getPortFromStr(_Conf.DIOportOut)
                _IO.configDPort(port, dio.devConst.DIGITAL_OUT)
                _IO.writeDPort(port, 0)
                port = _IO.getPortFromStr(_Conf.DIOportIn)
                _IO.configDPort(port, dio.devConst.DIGITAL_IN)
                port = _IO.getPortFromStr(_Conf.DIOportOut_User)
                _IO.configDPort(port, dio.devConst.DIGITAL_OUT)
                _IO.writeDPort(port, 0)

                # Set user pins to the resting state
                # TODO: Change to correct log message
                print(
                    _IO,
                    _Conf.DIOportOut_User,
                    int(_Conf.DIOpinUserOut1[0]),
                    int(_Conf.DIOpinUserOut1[2]),
                )
                csp.setIODevicePin(
                    _IO,
                    _Conf.DIOportOut_User,
                    int(_Conf.DIOpinUserOut1[0]),
                    int(_Conf.DIOpinUserOut1[2]) != 0,
                    False,
                )
                csp.setIODevicePin(
                    _IO,
                    _Conf.DIOportOut_User,
                    int(_Conf.DIOpinUserOut2[0]),
                    int(_Conf.DIOpinUserOut2[2]) != 0,
                    False,
                )

    else:
        _IO = None

    # Create a presenter instance
    _Presenter = cpr.Presenter(_Stage, _IO, _Conf, _View)
    
    if not _isParentGUI:
        # Called from the command line - - - -- - - - - - - - - - - - - - -
        # Load stimulus
        if not loadStimulus(_fNameStim, _Stim):
            sys.exit(0)

        # Connect to lightcrafter, if required
        _Presenter.LCr = connectLCrs(_Conf, _Stim)

        # Present stimulus, with increased process priority and
        # disabled automatic garbage collector, if requested
        try:
            _Presenter.prepare(_Stim)
            setPerformanceHigh(_Conf)
            try:
                _Presenter.run()
            except KeyboardInterrupt:
                Log.write(" ", "Aborted by user.")

        finally:
            _Presenter.finish()
            setPerformanceNormal(_Conf)

    else:
        # Called from the GUI  - - - - - - - - - - -- - - - - - - - - - - -
        # Notify GUI of display parameters
        _Sync.pipeSrv.send(
            [mpr.PipeValType.toCli_displayInfo, pickle.dumps(_Stage)]
        )

        # Start loop to process GUI (=client) requests
        while _Sync.Request.value is not mpr.TERMINATING:
            try:
                try:
                    # Check if new data is in the pipe
                    data = [mpr.PipeValType.toSrv_None]
                    if _Sync.pipeSrv.poll():
                        data = _Sync.pipeSrv.recv()

                        if data[0] == mpr.PipeValType.toSrv_changedStage:
                            # Stage parameter have changes, update immediately
                            _Stage.scalX_umPerPix = data[1]["scalX_umPerPix"]
                            _Stage.scalY_umPerPix = data[1]["scalY_umPerPix"]
                            _Stage.centOffX_pix = data[1]["centOffX_pix"]
                            _Stage.centOffY_pix = data[1]["centOffY_pix"]
                            _Stage.rot_angle = data[1]["rot_angle"]
                            _Stage.dxScr12 = data[1]["dxScr12"]
                            _Stage.dyScr12 = data[1]["dyScr12"]
                            _Stage.offXScr1_pix = data[1]["offXScr1_pix"]
                            _Stage.offYScr1_pix = data[1]["offYScr1_pix"]
                            _Stage.offXScr2_pix = data[1]["offXScr2_pix"]
                            _Stage.offYScr2_pix = data[1]["offYScr2_pix"]
                            data = [mpr.PipeValType.toSrv_None]

                        if data[0] == mpr.PipeValType.toSrv_changedLEDs:
                            # LED currents and/or enabled state have changes, 
                            # update immediately
                            _Stage.LEDs = data[1][0]
                            _Stage.isLEDSeqEnabled = data[1][1]
                            _Stage.sendLEDChangesToLCr(_Conf)
                            data = [mpr.PipeValType.toSrv_None]

                        if data[0] == mpr.PipeValType.toSrv_checkIODev:
                            # Return readiness of IO device
                            _Sync.pipeSrv.send(
                                [mpr.PipeValType.toCli_IODevInfo,
                                [_IO and _IO.isReady, dio.devConst.NONE, 0],]
                            )
                            data = [mpr.PipeValType.toSrv_None]

                        if data[0] == mpr.PipeValType.toSrv_setIODevPins:
                            # Change IO device pins
                            csp.setIODevicePin(_IO, *data[1][0:4])
                            _Sync.pipeSrv.send(
                                [mpr.PipeValType.toCli_IODevInfo,
                                [_IO and _IO.isReady, data],]
                            )
                            data = [mpr.PipeValType.toSrv_None]

                    # Parse client's request
                    if _Sync.Request.value == mpr.PRESENTING:
                        if data[0] == mpr.PipeValType.toSrv_fileName:
                            # Retrieve stimulus file name from pipe and load 
                            # stimulus
                            _fNameStim = os.path.normpath(data[1])
                            _vol = data[3]
                            data = [mpr.PipeValType.toSrv_None]
                            loadStimulus(_fNameStim, _Stim)
                            _Sync.setStateSafe(mpr.PRESENTING)

                            # Run stimulus ...
                            try:
                                switchGammaLUTByColorMode(_Conf, _View, _Stage, _Stim)
                                _Presenter.LCr = connectLCrs(_Conf, _Stim)
                                _Presenter.prepare(_Stim, _Sync, _vol)
                                setPerformanceHigh(_Conf)
                                _Presenter.run()

                            finally:
                                _Presenter.LCr = disconnectLCrs(_Presenter.LCr)
                                _Presenter.finish()
                                setPerformanceNormal(_Conf)

                        else:
                            # Should not happen ...
                            Log.write(
                                "DEBUG", 
                                "mpr.PRESENTING, unexpected client data"
                            )
                        _Sync.setStateSafe(mpr.IDLE)

                    elif _Sync.Request.value == mpr.COMPILING:
                        if data[0] == mpr.PipeValType.toSrv_fileName:
                            # Retrieve stimulus file name from pipe and compile 
                            # stimulus
                            _fNameStim = os.path.abspath(data[1]) + ".py"
                            data = [mpr.PipeValType.toSrv_None]
                            _Sync.setStateSafe(mpr.COMPILING)
                            try:
                                #subprocess.check_call(["python", _fNameStim])
                                subprocess.check_call([sys.executable, _fNameStim])
                                Log.write("ok", "... done")

                            except subprocess.CalledProcessError:
                                Log.write("ERROR", "... failed.")

                        else:
                            Log.write(
                                "DEBUG", 
                                "mpr.COMPILING, unexpected client data"
                            )
                        _Sync.setStateSafe(mpr.IDLE)

                    elif _Sync.Request.value == mpr.PROBING:
                        if data[0] == mpr.PipeValType.toSrv_probeParams:
                            # Change into interactive probing mode ...
                            _Sync.setStateSafe(mpr.PROBING)
                            try:
                                switchGammaLUTByColorMode(_Conf, _View, _Stage, _Stim)
                                _Presenter.LCr = connectLCrs(_Conf, _Stim)
                                setPerformanceHigh(_Conf)
                                if data[1] == glo.QDSpy_probing_center:
                                    # Currently only interactive center-probing is 
                                    # implemented
                                    pce.probe_main(data[2], _Sync, _View, _Stage)

                            finally:
                                data = [mpr.PipeValType.toSrv_None]
                                _Presenter.LCr = disconnectLCrs(_Presenter.LCr)
                                _Presenter.finish()
                                setPerformanceNormal(_Conf)

                        else:
                            Log.write(
                                "DEBUG", 
                                "mpr.PROBE_CENTER, unexpected client data"
                            )
                        _Sync.setStateSafe(mpr.IDLE)

                    elif _Sync.Request.value not in [mpr.CANCELING, mpr.UNDEFINED, mpr.IDLE]:
                        # Unknown request
                        Log.write(
                            "DEBUG", 
                            f"Request {_Sync.Request.value} unknown"
                        )

                    if data[0] != mpr.PipeValType.toSrv_None:
                        Log.write("DEBUG", "unexpected client data left after loop")
                
                finally:
                    # Clear request
                    _Sync.setRequestSafe(mpr.UNDEFINED)

                # Sleep for a bit
                time.sleep(glo.QDSpy_loop_sleep_s)  

            except KeyboardInterrupt:
                # Ignore here, wait for `mpr.TERMINATING` request
                pass

    # Restore gamma LUT, if necessary
    restoreGammaLUT(_Conf, _View)

    # Clean up
    _View.killWindows()
    _Presenter.LCr = disconnectLCrs(_Presenter.LCr)

    Log.write("ok", "... done")


# ---------------------------------------------------------------------
if __name__ == "__main__":
    freeze_support()
    args = cfg.getParsedArgv()
    main(args.fNameStim, False)

# ---------------------------------------------------------------------
