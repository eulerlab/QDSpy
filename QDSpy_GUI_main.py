#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QDSpy module - main program of the GUI version of QDSpy

Copyright (c) 2013-2025 Thomas Euler
All rights reserved.

2021-10-15 - Adapt to LINUX
2024-06-11 - Reformatted (using Ruff)
           - Small fixes for PEP violations
           - `int()` where Qt5 does not accept float
2024-06-19 - Ported from `PyQt5` to `PyQt6`
             (note that `QDSApp.setStyle("Fusion")` is needed to make
              the GUI designed for Qt5 look decent)   
2024-08-04 - `Log` moved into its own module       
2024-08-10 - Moved GUI-related methods from `QDSpy_GUI_support` to here
2025-01-28 - Sensor data via a serial port to log (pico-view support)  
2025-02-11 - Make sure that QDSpy detects if the pico-view device was
             unplugged and reconnect automatically
           - Write log file continuously such that it is not lost if
             QDSpy crashes  
2025-03-30 - Log file related changes (consistent w/ MQTT version)      
2025-05-31 - Under Linux: Sort stimulus names in GUI and display 
             current stimulus name w/o path
"""
# ---------------------------------------------------------------------
__author__ = "code@eulerlab.de"

import os
import sys
import time
import pickle
import json
import platform
from datetime import timedelta
from PyQt6 import uic  
from PyQt6.QtWidgets import QMessageBox, QMainWindow, QLabel, QApplication  
from PyQt6.QtWidgets import QFileDialog, QListWidgetItem, QWidget, QProgressBar  
from PyQt6.QtGui import QPalette, QColor, QBrush, QTextCharFormat, QTextCursor, QFontMetrics 
from PyQt6.QtCore import Qt, QRect, QSize, QTimer  
from multiprocessing import Process
import QDSpy_stim as stm
from Libraries.log_helper import Log
import QDSpy_config as cfg
import QDSpy_file_support as fsu
from QDSpy_GUI_cam import CamWinClass
import Libraries.multiprocess_helper as mpr
import QDSpy_stage as stg
import QDSpy_global as glo
import QDSpy_core
import QDSpy_core_support as csp
import serial
import serial.tools.list_ports

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

if csp.module_exists("cv2"):
    import Devices.camera as cam

PLATFORM_WINDOWS = platform.system() == "Windows"
if PLATFORM_WINDOWS:
    from ctypes import windll

# ---------------------------------------------------------------------
form_class = uic.loadUiType("QDSpy_GUI_main.ui")[0]

toggle_btn_style_str = "QPushButton:checked{background-color: lightGreen;border: none;}"
user_btn_style_str = "QPushButton:checked{background-color: orange;border: none;}"

# ---------------------------------------------------------------------
fStrPreRed = '<html><head/><body><p><span style="color:#ff0000;">'
fStrPreGreen = '<html><head/><body><p><span style="color:#00aa00;">'
fStrPost = "</span></p></body></html>"

# ---------------------------------------------------------------------
class State:
    undefined = 0
    idle = 1
    ready = 2
    loading = 3
    compiling = 4
    playing = 5
    canceling = 6
    probing = 7
    # ...

class Canceled(Exception):
    pass

# ---------------------------------------------------------------------
# Main application window
# ---------------------------------------------------------------------
class MainWinClass(QMainWindow, form_class):
    def __init__(self, parent=None):
        # Initialize
        self.HDMagFactor = 1.0
        self.Conf = cfg.Config()
        self.Stim = stm.Stim()
        self.currStimPath = self.Conf.pathStim
        self.currQDSPath = os.getcwd()
        self.currStimName = "n/a"
        self.currStimFName = ""
        self.isStimReady = False
        self.isStimCurr = False
        self.isViewReady = False
        self.isLCrUsed = False
        self.isIODevReady = None
        self.lastIOInfo = []
        self.IOCmdCount = 0
        self.Stage = None
        self.logFile = None
        self.noMsgToStdOut = cfg.getParsedArgv().gui

        # Open log file
        self.fNameLog = self._getNewLogFileName()
        if not glo.QDSpy_saveLogInTheEnd:
            self.logWrite(" ", "Saving log continuosly to '{0}' ...".format(self.fNameLog))
            self.logFile = open(self.fNameLog, "w")

        # For reporting the stimulus status during presentation
        self.Stim_tFrRel_s = 0
        self.Stim_nFrTotal = 0
        self.Stim_percent = 0
        self.Stim_completed = False
        self.Stim_soundVol = self.Conf.volume

        # GUI style-related
        cs = QDSApp.styleHints().colorScheme() 
        self.isDarkSchemeGUI = cs == Qt.ColorScheme.Dark 

        # Identify 
        self.logWrite(
            "***", 
            f"{glo.QDSpy_versionStr} GUI - {glo.QDSpy_copyrightStr}"
        )

        self.logWrite("DEBUG", "Initializing GUI")
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle(glo.QDSpy_versionStr)

        # Bind GUI ...
        self.btnRefreshStimList.clicked.connect(self.OnClick_btnRefreshStimList)
        self.listStim.itemClicked.connect(self.OnClick_listStim)
        self.listStim.itemDoubleClicked.connect(self.OnDblClick_listStim)
        self.btnStimPlay.clicked.connect(self.OnClick_btnStimPlay)
        self.btnStimCompile.clicked.connect(self.OnClick_btnStimCompile)
        self.btnStimAbort.clicked.connect(self.OnClick_btnStimAbort)
        self.btnChangeStimFolder.clicked.connect(self.OnClick_btnChangeStimFolder)
        self.checkShowHistory.clicked.connect(self.OnClick_checkShowHistory)

        self.pushButtonLED1.clicked.connect(self.OnClick_pushButtonLED)
        self.pushButtonLED2.clicked.connect(self.OnClick_pushButtonLED)
        self.pushButtonLED3.clicked.connect(self.OnClick_pushButtonLED)
        self.pushButtonLED4.clicked.connect(self.OnClick_pushButtonLED)
        self.pushButtonLED5.clicked.connect(self.OnClick_pushButtonLED)
        self.pushButtonLED6.clicked.connect(self.OnClick_pushButtonLED)

        self.btnIOUser1.clicked.connect(self.OnClick_IOUser1)
        self.btnIOUser1.setStyleSheet(user_btn_style_str)
        self.btnIOUser2.clicked.connect(self.OnClick_IOUser2)
        self.btnIOUser2.setStyleSheet(user_btn_style_str)

        self.pushButtonLED1.setStyleSheet(toggle_btn_style_str)
        self.pushButtonLED2.setStyleSheet(toggle_btn_style_str)
        self.pushButtonLED3.setStyleSheet(toggle_btn_style_str)
        self.pushButtonLED4.setStyleSheet(toggle_btn_style_str)
        self.pushButtonLED5.setStyleSheet(toggle_btn_style_str)
        self.pushButtonLED6.setStyleSheet(toggle_btn_style_str)

        self.spinBoxLED1.valueChanged.connect(self.OnClick_spinBoxLED_valueChanged)
        self.spinBoxLED2.valueChanged.connect(self.OnClick_spinBoxLED_valueChanged)
        self.spinBoxLED3.valueChanged.connect(self.OnClick_spinBoxLED_valueChanged)
        self.spinBoxLED4.valueChanged.connect(self.OnClick_spinBoxLED_valueChanged)
        self.spinBoxLED5.valueChanged.connect(self.OnClick_spinBoxLED_valueChanged)
        self.spinBoxLED6.valueChanged.connect(self.OnClick_spinBoxLED_valueChanged)
        self.btnSetLEDCurrents.clicked.connect(self.OnClick_btnSetLEDCurrents)
        self.btnRefreshDisplayInfo.clicked.connect(self.OnClick_btnRefreshDisplayInfo)

        self.btnToggleLEDEnable.clicked.connect(self.OnClick_btnToggleLEDEnable)
        self.btnToggleLEDEnable.setStyleSheet(toggle_btn_style_str)

        self.btnProbeStart.clicked.connect(self.OnClick_btnProbeStart)
        self.spinBox_probe_width.valueChanged.connect(
            self.OnClick_probeParam_valueChanged
        )
        self.spinBox_probe_height.valueChanged.connect(
            self.OnClick_probeParam_valueChanged
        )
        self.spinBox_probe_intensity.valueChanged.connect(
            self.OnClick_probeParam_valueChanged
        )
        self.spinBox_probe_interval.valueChanged.connect(
            self.OnClick_probeParam_valueChanged
        )

        self.btnLCrInfo0.clicked.connect(self.OnClick_btnLCrInfo0)
        self.btnLCrInfo1.clicked.connect(self.OnClick_btnLCrInfo1)

        self.btnToggleSeqControl0.clicked.connect(self.OnClick_btnToggleSeqControl0)
        self.btnToggleSeqControl0.setStyleSheet(toggle_btn_style_str)
        self.btnToggleSeqControl1.clicked.connect(self.OnClick_btnToggleSeqControl1)
        self.btnToggleSeqControl1.setStyleSheet(toggle_btn_style_str)

        self.btnLCrStartStop0.clicked.connect(self.OnClick_btnLCrStartStop0)
        self.btnLCrStartStop0.setStyleSheet(toggle_btn_style_str)
        self.btnLCrStartStop1.clicked.connect(self.OnClick_btnLCrStartStop1)
        self.btnLCrStartStop1.setStyleSheet(toggle_btn_style_str)

        self.winCam = None
        self.camList = []
        if self.Conf.allowCam and csp.module_exists("cv2"):
            self.camList = cam.get_camera_list()
            for c in self.camList:
                self.comboBoxCams.addItems([c["string"]])
            self.checkBoxCamEnable.clicked.connect(self.OnClick_checkBoxCamEnable)

        else:
            self.checkBoxCamEnable.setEnabled(False)

        self.checkBoxStageCSEnable.clicked.connect(self.OnClick_checkStageCSEnable)
        self.checkBoxDualScrCSEnable.clicked.connect(
            self.OnClick_checkBoxDualScrCSEnable
        )
        self.spinBoxStageCS_hOffs.valueChanged.connect(
            self.OnClick_spinBoxStageCS_hOffs_valueChanged
        )
        self.spinBoxStageCS_vOffs.valueChanged.connect(
            self.OnClick_spinBoxStageCS_vOffs_valueChanged
        )
        self.spinBoxStageCS_hScale.valueChanged.connect(
            self.OnClick_spinBoxStageCS_hScale_valueChanged
        )
        self.spinBoxStageCS_vScale.valueChanged.connect(
            self.OnClick_spinBoxStageCS_vScale_valueChanged
        )
        self.spinBoxStageCS_rot.valueChanged.connect(
            self.OnClick_spinBoxStageCS_rot_valueChanged
        )
        self.btnSaveStageCS.clicked.connect(self.OnClick_btnSaveStageCS)

        self.btnToggleWaitForTrigger.clicked.connect(
            self.OnClick_btnToggleWaitForTrigger
        )
        self.btnToggleWaitForTrigger.setStyleSheet(toggle_btn_style_str)

        self.stbarErrMsg = QLabel()
        self.stbarStimMsg = QLabel()
        self.prbarPresent = QProgressBar()
        self.prbarPresent.setRange(0, 100)
        self.prbarPresent.reset()
        self.statusbar.addWidget(self.stbarErrMsg, 2)
        self.statusbar.addWidget(self.stbarStimMsg, 2)
        self.statusbar.addPermanentWidget(self.prbarPresent, 2)
        self.lblSelStimName.setText(fsu.getFNameNoExt(self.currStimName))
        self.lineEditComment.returnPressed.connect(self.OnClick_AddComment)

        # Initialize Pico-view, if defined
        if glo.QDSpy_usePV:
            self._connectPVDevice()
            if self._pvSerial and self._pvSerial.is_open:
                # Set up timer for reading the pico-view data
                self._PVTimer = QTimer()
                self._PVTimer.timeout.connect(self._logPVEvents)
                dt_ms = int(max(glo.QDSpy_PV_rate_s, 0.1) *1_000)
                self._PVTimer.start(dt_ms)
                self._isPVReady = True
                self.logWrite("", "... done")                

        # Create status objects and a pipe for communicating with the
        # presentation process (see below)
        self.logWrite("DEBUG", "Creating sync object ...")
        self.state = State.undefined
        self.Sync = mpr.Sync()
        Log.setGUISync(self.Sync, noStdOut=self.noMsgToStdOut)
        self.logWrite("DEBUG", "... done")

        # Create process that opens a view (an OpenGL window) and waits for
        # instructions to play stimuli
        self.logWrite("DEBUG", "Creating worker thread ...")
        self.worker = Process(
            target=QDSpy_core.main, args=(self.currStimFName, True, self.Sync)
        )
        self.logWrite("DEBUG", "... done")
        self.worker.daemon = True
        self.logWrite("DEBUG", "Starting worker thread ...")
        self.worker.start()
        self.logWrite("DEBUG", "... done")

        self.isViewReady = True
        self.setState(State.idle, True)

        # Update GUI ...
        self.updateStimList()
        self.updateAll()

        if glo.QDSpy_useGUIScalingForHD:
            # If screen resolution is above a certain dpi levels (->HD), all GUI
            # elements are scaled in order to keep the GUI readable
            # (Needed for PyQt5 and lower)
            nHDScr = 0
            maxdpi = 0
            screens = QDSApp.screens()
            for s in screens:
                dpi = s.logicalDotsPerInch()
                if dpi > maxdpi:
                    maxdpi = dpi
                if dpi > glo.QDSpy_dpiThresholdForHD:
                    nHDScr += 1

            if nHDScr == 0:
                # "Normal" display
                self.HDMagFactor = 1.0

            else:
                # Scale all GUI elements to account for HD display
                self.HDMagFactor = maxdpi / 100.0
                listChildren = self.findChildren(QWidget)
                for child in listChildren:
                    rect = child.geometry().getRect()
                    child.setGeometry(
                        QRect(
                            int(rect[0] * self.HDMagFactor),
                            int(rect[1] * self.HDMagFactor),
                            int(rect[2] * self.HDMagFactor),
                            int(rect[3] * self.HDMagFactor),
                        )
                    )
                rect = self.minimumSize()
                self.setMinimumSize(
                    QSize(
                        int(rect.width() * self.HDMagFactor),
                        int(rect.height() * self.HDMagFactor),
                    )
                )
                rect = self.maximumSize()
                self.setMaximumSize(
                    QSize(
                        int(rect.width() * self.HDMagFactor),
                        int(rect.height() * self.HDMagFactor),
                    )
                )
                self.resize(self.maximumSize())
                self.logWrite(
                    "INFO",
                    "High display pixel density ({0} dpi), scaling GUI"
                    "by a factor of {1:.2f}".format(maxdpi, self.HDMagFactor),
                )

        # Check if worker process is still alive
        self.logWrite("DEBUG", "Check worker thread ...")
        time.sleep(1.0)
        if not (self.worker.is_alive()):
            sys.exit(0)
        self.logWrite("DEBUG", "... done")

        # Wait until the worker thread send info about the stage via the pipe
        self.logWrite("DEBUG", "Waiting for stage info from worker ...")
        while not self.Stage:
            self.processPipe()
            time.sleep(0.05)
        self.logWrite("DEBUG", "... done")

        # Update display info
        self.Stage.updateLEDs(self.Conf)
        self.currStimPath = os.path.abspath(self.currStimPath)
        self.updateDisplayInfo()

        # Update IO device info
        self.logWrite("DEBUG", "Waiting for IO device state from worker ...")
        self.Sync.pipeCli.send([mpr.PipeValType.toSrv_checkIODev, []])
        while self.isIODevReady is None:
            self.processPipe()
            time.sleep(0.05)
        self.updateIOInfo()
        self.logWrite("DEBUG", "... done")

        # Check if autorun stimulus file present and if so run it
        self.handleAutorun()

        # Update GUI
        self.Stim_soundVol = self.Conf.volume
        self.updateAll()
        self.updateProgressBar(-1)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __del__(self):
        pass

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def keyPressEvent(self, e):
        """ Allow pressing ESC to abort stimulus presentation ...
        """
        if e.key() in glo.QDSpy_KEY_KillPresent:
            if self.Sync.State.value in [mpr.PRESENTING, mpr.COMPILING, mpr.PROBING]:
                self.OnClick_btnStimAbort()

    # -----------------------------------------------------------------
    # Functions related to the log file
    # -----------------------------------------------------------------
    def _getNewLogFileName(self) -> str:
        """ Return a valid log file name
        """
        os.makedirs(self.Conf.pathLogs, exist_ok=True)
        fName = time.strftime("%Y%m%d_%H%M%S")
        fPath = fsu.getJoinedPath(self.Conf.pathLogs, fName)
        j = 0
        while os.path.exists(fPath +glo.QDSpy_logFileExtension):
            fPath = "{0}_{1:04d}".format(fPath, j)
            j += 1

        return fPath + glo.QDSpy_logFileExtension


    def writeLogFileLine(self, msg :str):
        """ Write line to log file
        """    
        if self.logFile:
            self.logFile.write(msg +"\n")
            self.logFile.flush()


    def saveLogFile(self):
        """ Save log file
        """    
        with open(self.fNameLog, "w") as logFile:
            logFile.write(str(self.textBrowserHistory.toPlainText()))


    def closeLogFile(self):
        """ Close log file
        """        
        if self.logFile:
            self.logFile.close()
            self.logFile = None

    # -----------------------------------------------------------------
    # Functions related to PV device
    # -----------------------------------------------------------------
    def _connectPVDevice(self):
        """ Connect to the pico-view device
        """
        port = glo.QDSpy_PV_serialPort
        baud = glo.QDSpy_PV_baud
        self._isPVReady = False
        self._pvSerial = None
        self.logWrite("", f"Initialize pico-view via `{port}` ...")
        try:
            self._pvSerial = serial.Serial(port=port, baudrate=baud)

        except serial.serialutil.SerialException as err:
            self.logWrite("WARNING", err)   

    
    def _disconnectPVDevice(self):
        """ Disconnect from the pico-view device
        """
        if self._pvSerial and self._pvSerial.is_open:
            self._pvSerial.close()
            self._isPVReady = False


    def _logPVEvents(self):
        """ Check if new data arrived at the PV serial and if so, write 
        it to the log file
        """
        port = glo.QDSpy_PV_serialPort.lower()
        ports = list(serial.tools.list_ports.comports())
        is_pv_connected = any(port.device == self._pvSerial.port for port in ports)
        if not is_pv_connected:
            # Connection lost - probably unplugged  
            self.logWrite("WARNING", f"Lost pico-view device on `{port}`")
            self._disconnectPVDevice()
        
        elif not self._pvSerial.is_open:
            # (Re)connect to the pico-view device
            self._connectPVDevice()

        if self._pvSerial and self._pvSerial.is_open:
            if self._pvSerial.in_waiting > 0:
                msg = self._pvSerial.readline()
                if len(msg) > 0 and msg[0] == ord(glo.QDSpy_PV_startCh):
                    # Valid message
                    data = json.loads(msg[1:].decode())
                    self.logWrite("SENSOR", data)

    # -----------------------------------------------------------------
    def handleAutorun(self):
        """ Check if autorun stimulus file present and if so run it
        """
        try:
            self.isStimCurr = False
            sf = glo.QDSpy_autorunStimFileName
            sd = glo.QDSpy_autorunDefFileName
            self.currStimFName = os.path.join(self.currStimPath, sf)
            isAutoRunExists = fsu.getStimExists(self.currStimFName)
            if isAutoRunExists:
                # Check if a  compiled version of the autorun file exists
                self.isStimCurr = fsu.getStimCompileState(self.currStimFName)

            if not isAutoRunExists or not self.isStimCurr:
                # Use default file as no compiled auto-run file is present
                self.currStimFName = os.path.join(self.currQDSPath, sd)
                self.logWrite(
                    "ERROR", 
                    f"No compiled `{sf}` in current stimulus folder"
                )
                self.logWrite("INFO", f"Using `{sd}` in `{self.currQDSPath}`.")

            # Run either autorun file ...
            self.logWrite("DEBUG", "Running {0} ...".format(self.currStimFName))
            self.Stim.load(self.currStimFName, _onlyInfo=True)
            self.setState(State.ready)
            self.isStimReady = True
            self.runStim()

        except:  # noqa: E722
            # Failed ...
            if self.Stim.getLastErrC() != stm.StimErrC.ok:
                self.logWrite(
                    "ERROR",
                    f"No compiled `{sf}` in current stimulus folder, "
                    f"and `{sd}.pickle` is not in `{self.currQDSPath}`. "
                )
                self.logWrite("ERROR", "Program is aborted.")                
                sys.exit(0)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def closeEvent(self, event):
        """ User requested to close the application
        """
        if glo.QDSpy_isGUIQuitWithDialog:
            result = QMessageBox.question(
                self,
                "Confirm closing QDSpy ...",
                "Are you sure you want to quit?",
                QMessageBox.Yes | QMessageBox.No,
            )
            event.ignore()
            if result == QMessageBox.No:
                event.ignore()
                return

        # Save position of camera window, and close it if open
        if self.winCam is not None:
            self.Conf.camWinGeom = self.winCam.geometry().getRect()
            self.winCam.close()

        # Save config
        self.Conf.saveWinPosToConfig()
        self.Conf.save()

        # Closing is immanent, stop stimulus, if running ...
        if self.Sync.State.value in [mpr.PRESENTING, mpr.COMPILING]:
            self.OnClick_btnStimAbort()

       # Close Pico-view link
        if glo.QDSpy_usePV and self._pvSerial and self._pvSerial.is_open:
            self._PVTimer.stop()
            self._disconnectPVDevice()

        # Save log
        if glo.QDSpy_saveLogInTheEnd:
            self.logWrite(" ", "Saving log file to '{0}' ...".format(self.fNameLog))
            self.saveLogFile()
        else:
            self.closeLogFile()    

        # ... and clean up
        self.logWrite("DEBUG", "Kill worker thread ...")
        self.Sync.setRequestSafe(mpr.TERMINATING)
        self.worker.join()
        while self.worker.is_alive():
            time.sleep(0.2)
        self.logWrite("DEBUG", "... done")
        event.accept()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setState(self, _newState, _doUpdateGUI=False):
        """ Update GUI state and GUI as well, if requested
        """
        self.state = _newState
        if _doUpdateGUI:
            self.updateAll()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def updateAll(self):
        """ Update the complete GUI
        """
        txt = self.getShortText(self.currStimPath, self.lblCurrStimFolder)
        self.lblCurrStimFolder.setText(txt)

        stateWorker = self.Sync.State.value
        if stateWorker == mpr.PRESENTING:
            self.state = State.playing
        elif stateWorker == mpr.COMPILING:
            self.state = State.compiling
        elif stateWorker == mpr.PROBING:
            self.state = State.probing
        elif stateWorker in [mpr.CANCELING, mpr.TERMINATING]:
            self.state = State.canceling
        elif stateWorker == mpr.IDLE:
            self.state = State.ready

        isStimSelPerm = self.state in {State.undefined, State.idle, State.ready}

        self.listStim.setEnabled(isStimSelPerm)
        self.btnRefreshStimList.setEnabled(isStimSelPerm)
        self.btnChangeStimFolder.setEnabled(isStimSelPerm)

        self.btnStimPlay.setText("Play")
        self.btnStimPlay.setEnabled(self.isStimReady)
        self.btnStimCompile.setText("Compile")
        self.btnStimCompile.setEnabled(not (self.isStimCurr))
        self.btnStimAbort.setText("Abort")
        self.btnStimAbort.setEnabled(
            (self.state == State.playing) or (self.state == State.probing)
        )
        self.btnProbeStart.setText("Start probing\ncenter")
        self.btnProbeStart.setEnabled(True)

        if self.state == State.loading:
            self.btnStimPlay.setText("Loading\n...")
            self.btnStimPlay.setEnabled(False)
            self.btnStimCompile.setEnabled(False)
            self.listStim.setEnabled(False)

        elif self.state == State.compiling:
            self.btnStimCompile.setText("Compi-\nling ...")
            self.btnStimCompile.setEnabled(False)
            self.btnStimPlay.setEnabled(False)
            self.listStim.setEnabled(False)

        elif self.state == State.canceling:
            self.btnStimAbort.setText("Aborting ...")
            self.btnStimPlay.setEnabled(False)
            self.listStim.setEnabled(False)

        elif self.state == State.playing:
            self.btnStimPlay.setText("Playing\n...")
            self.btnStimPlay.setEnabled(False)
            self.btnStimCompile.setEnabled(False)

        elif self.state == State.probing:
            self.btnProbeStart.setText("Probing\ncenter ...")
            self.btnProbeStart.setEnabled(False)
            self.btnStimPlay.setEnabled(False)
            self.btnStimCompile.setEnabled(False)

        if self.winCam is not None:
            self.checkBoxCamEnable.setCheckState(self.winCam.isHidden())

        if self.Stage is not None:
            enabledSeq = self.Stage.isLEDSeqEnabled[0]
        else:
            enabledSeq = True
        self.btnSetLEDCurrents.setEnabled(self.isLCrUsed)
        self.btnToggleLEDEnable.setEnabled(self.isLCrUsed)
        self.btnToggleSeqControl0.setEnabled(False)
        self.btnToggleSeqControl1.setEnabled(False)
        """
        enabledLEDs = self.btnToggleLEDEnable.isChecked()
        self.btnToggleSeqControl.setEnabled(self.isLCrUsed and not(enabledLEDs))
        """
        self.btnToggleSeqControl0.setChecked(enabledSeq)
        self.updateToggleButton(self.btnToggleSeqControl0)
        self.btnToggleSeqControl1.setChecked(enabledSeq)
        self.updateToggleButton(self.btnToggleSeqControl1)

        self.btnRefreshDisplayInfo.setEnabled(self.isLCrUsed)
        if self.Stage:
            for iLED, LED in enumerate(self.Stage.LEDs):
                [spinBoxLED, labelLED, btnLED] = self.getLEDGUIObjects(LED)
                spinBoxLED.setEnabled(self.isLCrUsed)
                spinBoxLED.setMaximum(LED["max_current"])
                btnLED.setEnabled(self.isLCrUsed and not (enabledSeq))
                if self.Stage is not None:
                    btnLED.setChecked(LED["enabled"])
                else:
                    btnLED.setChecked(True)
                self.updateToggleButton(btnLED)

        self.processPipe()
        self.updateStatusBar(mpr.StateStr[stateWorker])
        QApplication.processEvents()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def updateStimList(self):
        """ Update stimulus list widget
        """
        self.currStimFNames = fsu.getStimFileLists(self.currStimPath)
        if not PLATFORM_WINDOWS:
            self.currStimFNames = sorted(self.currStimFNames)
        self.listStim.clear()
        for stimFName in self.currStimFNames:
            self.listStim.addItem(fsu.getFNameNoExt(stimFName))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def updateStatusBar(self, _msg="Ready", _isErr=False):
        """ Update status bar
        """
        if _isErr:
            self.stbarErrMsg.setText(fStrPreRed + "Error: " + _msg + fStrPost)
        else:
            if self.state == State.playing:
                self.Stim_percent = int((self.Stim_tFrRel_s /self.Stim.lenStim_s) *100)
                self.updateProgressBar(self.Stim_percent)
                dt = timedelta(seconds=int(self.Stim.lenStim_s))
                t1 = timedelta(seconds=int(self.Stim_tFrRel_s))
                _msg += f" ({t1} of {dt})"
            else:
                if self.Stim_percent > 0:
                    if self.Stim_completed:
                        self.updateProgressBar(100, "Done")
                    else:
                        self.updateProgressBar(0, "Aborted", keep_val=True)
                self.Stim_percent = 0
            self.stbarErrMsg.setText(_msg)

        if (len(self.currStimName) > 0) and (self.isStimReady):
            self.stbarStimMsg.setText("Stimulus: " + self.currStimName)
        else:
            self.stbarStimMsg.setText("n/a")

    def updateProgressBar(self, val, msg="", keep_val=False):
        """ Update progress bar
        """
        if len(msg) > 0:
            self.prbarPresent.setFormat(msg +" (%p%)")    
        if keep_val:
            return
        if val < 0:
            self.prbarPresent.reset()
        else:    
            self.prbarPresent.setValue(val)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def updateIOInfo(self):
        """ Update IO device info and status
        """
        if self.Conf.useDIO:
            self.lblIODevName.setText(
                "{0}, board #{1}, device #{2} {3}".format(
                    self.Conf.DIObrdType,
                    self.Conf.DIObrd,
                    self.Conf.DIOdev,
                    "is ready" if self.isIODevReady else "NOT READY",
                )
            )
            self.lblIODevMarkerOut.setText(
                "port {0}, pin {1}".format(self.Conf.DIOportOut, self.Conf.DIOpinMarker)
            )
            self.lblIODevTriggerIn.setText(
                "port {0}, pin {1}".format(self.Conf.DIOportIn, self.Conf.DIOpinTrigIn)
            )
            self.lblIODevUserOut.setText(
                "port {0}, pins {1},{2}".format(
                    self.Conf.DIOportOut_User,
                    int(self.Conf.DIOpinUserOut1[0]),
                    int(self.Conf.DIOpinUserOut2[0]),
                )
            )

        self.groupBoxIODevInfo.setEnabled(self.isIODevReady)
        self.btnIOUser1.setEnabled(self.isIODevReady)
        self.btnIOUser1.setText("{0}\noff".format(self.Conf.DIOpinUserOut1[1]))
        self.btnIOUser2.setEnabled(self.isIODevReady)
        self.btnIOUser2.setText("{0}\noff".format(self.Conf.DIOpinUserOut2[1]))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def updateDisplayInfo(self):
        """ Update display info and status
        """
        try:
            self.lblDisplDevName.setText(
                "{0}, screen #{1}".format(self.Stage.scrDevName, self.Stage.scrIndex)
            )
            self.lblDisplDevRes.setText(
                "{0}x{1}, {2}bit, {3:.1f}({4:.1f}) Hz{5}".format(
                    self.Stage.dxScr,
                    self.Stage.dyScr,
                    self.Stage.depth,
                    self.Stage.scrDevFreq_Hz,
                    self.Stage.scrReqFreq_Hz,
                    ", full" if self.Stage.isFullScr else "",
                )
            )
            self.lblDisplDevInfo.setText(
                "{0:.2f}x{1:.2f} µm/pixel<br>offset: {2},{3}, angle: {4}°".format(
                    self.Stage.scalX_umPerPix,
                    self.Stage.scalY_umPerPix,
                    self.Stage.centX_pix,
                    self.Stage.centY_pix,
                    self.Stage.rot_angle,
                )
            )

            if len(self.Stage.LEDs) == 0:
                self.lblDisplDevLEDs.setText("n/a")

            else:
                sTemp = ""
                pal = QPalette()
                LEDsEnabled = self.btnToggleLEDEnable.isChecked()

                for iLED, LED in enumerate(self.Stage.LEDs):
                    sTemp += "{0}={1} ".format(LED["name"], LED["current"])
                    pal.setColor(QPalette.ColorRole.Window, QColor(LED["Qt_color"]))
                    pal.setColor(QPalette.ColorRole.WindowText, QColor("white"))
                    [spinBoxLED, labelLED, btnLED] = self.getLEDGUIObjects(LED)
                    spinBoxLED.setValue(LED["current"])
                    spinBoxLED.setEnabled(LEDsEnabled)
                    labelLED.setPalette(pal)
                    labelLED.setText(LED["name"])
                    btnLED.setEnabled(not LEDsEnabled)
                    btnLED.setText("")
                    self.updateToggleButton(btnLED)
                self.lblDisplDevLEDs.setText(sTemp)

            self.spinBoxStageCS_hOffs.setValue(self.Stage.centOffX_pix)
            self.spinBoxStageCS_vOffs.setValue(self.Stage.centOffY_pix)
            self.spinBoxStageCS_hScale.setValue(self.Stage.scalX_umPerPix)
            self.spinBoxStageCS_vScale.setValue(self.Stage.scalY_umPerPix)
            self.spinBoxStageCS_rot.setValue(int(self.Stage.rot_angle))

        except KeyError:
            pass

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def updateToggleButton(self, _btn, _txtList=["on", "off"]):
        s = _btn.text().split("\n")
        f = _btn.isChecked()
        if len(s) == 1:
            s = "{0}".format(_txtList[0] if f else _txtList[1])
        else:
            s = "{0}\n{1}".format(s[0], _txtList[0] if f else _txtList[1])
        _btn.setText(s)

    # ---------------------------------------------------------------------
    def getLEDGUIObjects(self, _LED):
        if (_LED["LEDIndex"] == 0) and (_LED["devIndex"] == 0):
            return [self.spinBoxLED1, self.label_LED1, self.pushButtonLED1]
        elif (_LED["LEDIndex"] == 1) and (_LED["devIndex"] == 0):
            return [self.spinBoxLED2, self.label_LED2, self.pushButtonLED2]
        elif (_LED["LEDIndex"] == 2) and (_LED["devIndex"] == 0):
            return [self.spinBoxLED3, self.label_LED3, self.pushButtonLED3]
        elif (_LED["LEDIndex"] == 0) and (_LED["devIndex"] == 1):
            return [self.spinBoxLED4, self.label_LED4, self.pushButtonLED4]
        elif (_LED["LEDIndex"] == 1) and (_LED["devIndex"] == 1):
            return [self.spinBoxLED5, self.label_LED5, self.pushButtonLED5]
        elif (_LED["LEDIndex"] == 2) and (_LED["devIndex"] == 1):
            return [self.spinBoxLED6, self.label_LED6, self.pushButtonLED6]
        else:
            return [None] * 3

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getShortText(self, _txt, _widget):
        metrics = QFontMetrics(self.font())
        return metrics.elidedText(
            _txt, Qt.TextElideMode.ElideRight, _widget.width()
        )

    # -------------------------------------------------------------------
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnClick_btnRefreshStimList(self):
        self.updateStimList()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnClick_btnChangeStimFolder(self):

        newPath = QFileDialog.getExistingDirectory(
            self,
            "Select new stimulus folder",
            self.currStimPath,
            #options=QFileDialog.ShowDirsOnly,
            options=QFileDialog.Option.ShowDirsOnly
        )
        if len(newPath) > 0:
            # Change path and update stimulus list ...
            self.currStimPath = newPath
            self.logWrite(" ", "New stimulus folder `{0}`".format(newPath))
            self.updateStimList()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnClick_listStim(self, _selItem):
        """ Show name of selected stimulus and some info
        """
        txtInfo = "n/a"
        txtCompState = "n/a"
        txtDuration = "n/a"
        self.isStimReady = False
        self.isStimCurr = False
        self.currStimName = _selItem.text()
        self.setState(State.idle)
        self.updateProgressBar(-1)

        iSel = self.listStim.currentRow()
        if iSel >= 0:
            # Try loading selected stimulus pickle file
            #
            self.currStimFName = self.currStimFNames[iSel]
            try:
                self.Stim.load(self.currStimFName, _onlyInfo=True)

                # Succeed, now get info
                self.setState(State.ready)
                self.isStimReady = True
                self.isStimCurr = fsu.getStimCompileState(self.currStimFName)
                if self.isStimCurr:
                    txtCompState = (
                        fStrPreGreen + "compiled (.pickle) is up-to-date" + fStrPost
                    )
                else:
                    txtCompState = "compiled (.pickle), pre-dates .py"
                txtInfo = self.Stim.descrStr
                mins, secs = divmod(self.Stim.lenStim_s, 60)
                hours, mins = divmod(mins, 60)
                txtDuration = "{0:.3f} s ({1:02d}:{2:02d}:{3:02d})".format(
                    self.Stim.lenStim_s, int(hours), int(mins), int(secs)
                )
                self.updateStatusBar()

            except:  # noqa: E722
                # Failed ...
                txtCompState = fStrPreRed + "not compiled (no .pickle)" + fStrPost
                if self.Stim.getLastErrC() != stm.StimErrC.ok:
                    self.updateStatusBar(self.Stim.getLastErrStr(), True)

            # Show info ...
            self.lblSelStimName.setText(fsu.getFNameNoExt(self.currStimName))
            self.lblSelStimInfo.setText(txtInfo)
            self.lblSelStimStatus.setText(txtCompState)
            self.lblSelStimDuration.setText(txtDuration)
            self.updateAll()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnClick_checkShowHistory(self, _checked):
        self.resize(self.maximumSize() if _checked else self.minimumSize())

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnClick_spinBoxLED_valueChanged(self, _val):
        self.btnSetLEDCurrents.setEnabled(True)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnClick_pushButtonLED(self):
        self.handleLEDStateChanged()

    def handleLEDStateChanged(self):
        enabled = []
        LEDsEnabled = not (self.btnToggleLEDEnable.isChecked())

        for iLED, LED in enumerate(self.Stage.LEDs):
            (spinBoxLED, labelLED, btnLED) = self.getLEDGUIObjects(LED)
            btnLED.setEnabled(LEDsEnabled)
            val = btnLED.isChecked()
            enabled.append(val)
            spinBoxLED.setEnabled(LEDsEnabled and not (val))
            self.Stage.setLEDEnabled(iLED, val)

        self.Sync.pipeCli.send(
            [
                mpr.PipeValType.toSrv_changedLEDs,
                [self.Stage.LEDs, self.Stage.isLEDSeqEnabled],
            ]
        )
        self.updateDisplayInfo()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnClick_AddComment(self):
        data = {"userComment": self.lineEditComment.text()}
        self.logWrite("DATA", data.__str__())
        self.lineEditComment.setText("")

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnClick_btnRefreshDisplayInfo(self):
        self.Stage.updateLEDs(_Conf=self.Conf)
        self.updateDisplayInfo()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnClick_btnToggleLEDEnable(self):
        checked = self.btnToggleLEDEnable.isChecked()
        for iLED, LED in enumerate(self.Stage.LEDs):
            self.Stage.LEDs[iLED]["enabled"] = checked

        self.Stage.isLEDSeqEnabled = [checked] * glo.QDSpy_MaxLightcrafterDev
        self.Sync.pipeCli.send(
            [
                mpr.PipeValType.toSrv_changedLEDs,
                [self.Stage.LEDs, self.Stage.isLEDSeqEnabled],
            ]
        )
        self.updateToggleButton(self.btnToggleLEDEnable)
        self.updateDisplayInfo()
        self.updateAll()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnClick_btnToggleSeqControl0(self):
        self.updateToggleButton(self.btnToggleSeqControl0)
        print("OnClick_btnToggleSeqControl0 - TO BE IMPLEMENTED")
        # *****************************
        # *****************************

    def OnClick_btnToggleSeqControl1(self):
        self.updateToggleButton(self.btnToggleSeqControl1)
        print("OnClick_btnToggleSeqControl1 - TO BE IMPLEMENTED")
        # *****************************
        # *****************************

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnClick_btnLCrStartStop0(self):
        self.handleLCrStartStopButton(self.btnLCrStartStop0, 0)

    def OnClick_btnLCrStartStop1(self):
        self.handleLCrStartStopButton(self.btnLCrStartStop1, 1)

    def handleLCrStartStopButton(self, _btn, _iLcr):
        self.updateToggleButton(_btn, ["running", "stopped"])
        checked = _btn.isChecked()
        self.Stage.togglePatternSeq(_iLcr, self.Conf, checked)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnClick_btnToggleWaitForTrigger(self):
        self.updateToggleButton(self.btnToggleWaitForTrigger)
        print("OnClick_btnToggleWaitForTrigger.TO BE IMPLEMENTED")
        # *****************************
        # *****************************

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnClick_IOUser1(self):
        self.handleIOUserButton(
            self.btnIOUser1,
            int(self.Conf.DIOpinUserOut1[0]),
            int(self.Conf.DIOpinUserOut1[2]) != 0,
        )

    def OnClick_IOUser2(self):
        self.handleIOUserButton(
            self.btnIOUser2,
            int(self.Conf.DIOpinUserOut2[0]),
            int(self.Conf.DIOpinUserOut2[2]) != 0,
        )

    def handleIOUserButton(self, _btn, _pin, _invert):
        self.updateToggleButton(_btn)
        self.IOCmdCount += 1
        data = dict(
            [
                ("port", self.Conf.DIOportOut_User),
                ("pin", _pin),
                ("invert", _invert),
                ("state", _btn.isChecked()),
                ("cmdCount", self.IOCmdCount),
            ]
        )
        self.Sync.pipeCli.send(
            [
                mpr.PipeValType.toSrv_setIODevPins,
                [
                    data["port"],
                    data["pin"],
                    data["invert"],
                    data["state"],
                    data["cmdCount"],
                ],
            ]
        )
        currIOCmdCount = self.IOCmdCount
        self.processPipe()
        if currIOCmdCount == self.IOCmdCount:
            self.logWrite("DATA", data.__str__())

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnClick_btnSetLEDCurrents(self):
        if len(self.Stage.LEDs) == 0:
            return

        curr = []
        for iLED, LED in enumerate(self.Stage.LEDs):
            (spinBoxLED, labelLED, btnLED) = self.getLEDGUIObjects(LED)
            val = spinBoxLED.value()
            curr.append(val)
            self.Stage.setLEDCurrent(iLED, val)

        self.Sync.pipeCli.send(
            [
                mpr.PipeValType.toSrv_changedLEDs,
                [self.Stage.LEDs, self.Stage.isLEDSeqEnabled],
            ]
        )
        self.btnSetLEDCurrents.setEnabled(False)
        self.updateDisplayInfo()

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def OnClick_btnLCrInfo0(self):
        self.handleLCrInfoButton(0)

    def OnClick_btnLCrInfo1(self):
        self.handleLCrInfoButton(1)

    def handleLCrInfoButton(self, _iLcr):
        self.Stage.inquireLCrInfo(_iLcr, self.Conf)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnClick_checkStageCSEnable(self, _checked):
        self.spinBoxStageCS_hOffs.setEnabled(_checked)
        self.spinBoxStageCS_vOffs.setEnabled(_checked)
        self.spinBoxStageCS_hScale.setEnabled(_checked)
        self.spinBoxStageCS_vScale.setEnabled(_checked)
        self.spinBoxStageCS_rot.setEnabled(_checked)
        self.btnSaveStageCS.setEnabled(_checked)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnClick_checkBoxDualScrCSEnable(self, _checked):
        self.spinBoxStageCS_hOffs_Scr1.setEnabled(_checked)
        self.spinBoxStageCS_vOffs_Scr1.setEnabled(_checked)
        self.spinBoxStageCS_hOffs_Scr2.setEnabled(_checked)
        self.spinBoxStageCS_vOffs_Scr2.setEnabled(_checked)
        self.spinBoxStageCS_wideScrHeight.setEnabled(_checked)
        self.spinBoxStageCS_wideScrWidth.setEnabled(_checked)
        self.btnSaveStageCS.setEnabled(_checked)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnClick_spinBoxStageCS_vOffs_valueChanged(self, _val):
        self.Stage.centOffY_pix = _val
        self.signalStageChange()

    def OnClick_spinBoxStageCS_hOffs_valueChanged(self, _val):
        self.Stage.centOffX_pix = _val
        self.signalStageChange()

    def OnClick_spinBoxStageCS_vScale_valueChanged(self, _val):
        self.Stage.scalY_umPerPix = _val
        self.signalStageChange()

    def OnClick_spinBoxStageCS_hScale_valueChanged(self, _val):
        self.Stage.scalX_umPerPix = _val
        self.signalStageChange()

    def OnClick_spinBoxStageCS_rot_valueChanged(self, _val):
        self.Stage.rot_angle = _val
        self.signalStageChange()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def signalStageChange(self):
        self.updateDisplayInfo()
        self.Sync.pipeCli.send(
            [mpr.PipeValType.toSrv_changedStage, self.Stage.getScaleOffsetAsDict()]
        )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnClick_probeParam_valueChanged(self, _val):
        self.signalProbeParamChange()

    def signalProbeParamChange(self):
        spot_width = int(self.spinBox_probe_width.value())
        spot_height = int(self.spinBox_probe_height.value())
        spot_intensity = int(self.spinBox_probe_intensity.value())
        spot_interval = float(self.spinBox_probe_interval.value())
        self.Sync.pipeCli.send(
            [
                mpr.PipeValType.toSrv_probeParams,
                glo.QDSpy_probing_center,
                [spot_width, spot_height, spot_intensity, spot_interval],
            ]
        )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnClick_btnSaveStageCS(self):
        self.Conf.saveStageToConfig(self.Stage)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnClick_btnStimPlay(self):
        self.runStim()

    def OnClick_btnStimCompile(self):
        self.compileStim()

    def OnClick_btnStimAbort(self):
        """ Send a request to the worker to cancel the presentation
        """
        self.setState(State.canceling)
        self.Sync.setRequestSafe(mpr.CANCELING)
        self.setState(State.canceling, True)

        # Wait for the worker to finish cancelling
        if self.Sync.waitForState(mpr.IDLE, self.Conf.guiTimeOut, self.updateAll):
            self.setState(State.ready, True)
        else:
            self.logWrite("DEBUG", "OnClick_btnStimAbort, timeout waiting for IDLE")

    def OnClick_btnProbeStart(self):
        self.probeCenter()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnDblClick_listStim(self, _selItem):
        self.runStim()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnClick_checkBoxCamEnable(self, _checked):
        if _checked:
            if self.winCam is None:
                self.winCam = CamWinClass(self, self.updateAll, self.logWrite)
                self.winCam.show()
                geo = self.Conf.camWinGeom
                self.winCam.setGeometry(geo[0], geo[1], geo[2], geo[3])
            else:
                self.winCam.show()

        else:
            if self.winCam is not None:
                self.winCam.close()

    # -------------------------------------------------------------------
    # Compiling and running stimuli
    # -------------------------------------------------------------------
    def compileStim(self):
        """ Send stimulus file name via pipe and signal worker thread to
            compile the stimulus
        """
        self.Sync.pipeCli.send(
            [mpr.PipeValType.toSrv_fileName, self.currStimFName, self.currStimPath]
        )
        self.Sync.setRequestSafe(mpr.COMPILING)
        self.logWrite(" ", "Compiling stimulus script ...")

        # Wait for the worker to start ...
        if self.Sync.waitForState(mpr.COMPILING, self.Conf.guiTimeOut, self.updateAll):
            self.setState(State.compiling, True)

            # Wait for the worker to finish the presentation, while keeping the
            # GUI alive
            self.Sync.waitForState(mpr.IDLE, 0.0, self.updateAll)
            self.OnClick_listStim(QListWidgetItem(self.currStimFName))
            self.updateAll()

        else:
            self.logWrite("DEBUG", "runStim, timeout waiting for COMPILING")

    # -------------------------------------------------------------------
    def runStim(self):
        """ Send stimulus file name via pipe and signal worker thread to
            start presenting the stimulus
        """
        self.updateProgressBar(0, "Presenting ...")
        self.Sync.pipeCli.send(
            [mpr.PipeValType.toSrv_fileName, self.currStimFName, self.currStimPath,
             self.Stim_soundVol]
        )
        self.Sync.setRequestSafe(mpr.PRESENTING)
        self.logWrite(" ", "Presenting stimulus ...")

        # Wait for the worker to start ...
        if self.Sync.waitForState(mpr.PRESENTING, self.Conf.guiTimeOut, self.updateAll):
            self.setState(State.playing, True)

            # Wait for the worker to finish the presentation, while keeping the
            # GUI alive
            self.Sync.waitForState(mpr.IDLE, 0.0, self.updateAll)

            # Update status                
            self.updateAll()

        else:
            self.logWrite("DEBUG", "runStim, timeout waiting for PRESENTING")

    # -------------------------------------------------------------------
    def probeCenter(self):
        """ Send parameters of the probe center via pipe and signal worker thread to
            start presenting the stimulus
        """
        self.signalProbeParamChange()
        self.Sync.setRequestSafe(mpr.PROBING)
        self.logWrite(" ", "Probing center ...")

        # Wait for the worker to start ...
        if self.Sync.waitForState(mpr.PROBING, self.Conf.guiTimeOut, self.updateAll):
            self.setState(State.playing, True)

            # Wait for the worker to finish the presentation, while keeping the
            # GUI alive
            self.Sync.waitForState(mpr.IDLE, 0.0, self.updateAll)
            self.updateAll()

        else:
            self.logWrite("DEBUG", "runStim, timeout waiting for PROBING")

    # -------------------------------------------------------------------
    # Communication with worker-thread
    # -------------------------------------------------------------------
    def processPipe(self):
        """ Read data from pipe to worker thread, if available
        """
        while self.Sync.pipeCli.poll():
            data = self.Sync.pipeCli.recv()
            
            if data[0] == mpr.PipeValType.toCli_log:
                # Handle log data -> write to history
                self.log(data)
                if not glo.QDSpy_saveLogInTheEnd:
                    self.writeLogFileLine(data[2])

            elif data[0] == mpr.PipeValType.toCli_displayInfo:
                # Handle display information data -> update GUI
                self.Stage = pickle._loads(data[1])
                self.isLCrUsed = self.Conf.useLCr and (
                    self.Stage.scrDevType == stg.ScrDevType.DLPLCR4500
                )
                self.updateAll()
                self.updateDisplayInfo()

            elif data[0] == mpr.PipeValType.toCli_IODevInfo:
                # Receive I/O device information
                self.isIODevReady = data[1][0]
                if self.isIODevReady is None:
                    self.isIODevReady = False
                self.lastIOInfo = data[1]
                self.updateIOInfo()

            elif data[0] == mpr.PipeValType.toCli_time:
                # Receive information about stimulus presentation progress
                self.Stim_tFrRel_s = data[1]
                self.Stim_nFrTotal = data[2]

            elif data[0] == mpr.PipeValType.toCli_playEndInfo:
                # Receive information about stimulus presentation end
                self.Stim_completed = data[1]

            else:
                # ***************************
                # ***************************
                # TODO: Other types of data need to be processed
                # ***************************
                # ***************************
                pass

    def waitForPipe(self, _func, _timeOut_s=1.0):
        """ Wait for the passed function to return True or for time-out
        """
        n = _timeOut_s / 0.05
        while not (_func()) and (n > 0):
            self.processPipe()
            time.sleep(0.05)
            n -= 1

    # -------------------------------------------------------------------
    # Logging-related
    # -------------------------------------------------------------------
    def logWrite(self, _hdr, _msg):
        """ Log a message to the appropriate output
        """
        data = Log.write(_hdr, _msg, _getStr=True, _isWorker=False)
        if data is not None:
            self.log(data)
            if not glo.QDSpy_saveLogInTheEnd:
                self.writeLogFileLine(data[2])


    def log(self, _data):
        msg = _data[2] + "\r"
        colStr = _data[3]
        if self.isDarkSchemeGUI: 
            colStr = "lightgray" if colStr == "black" else colStr
        cursor = self.textBrowserHistory.textCursor()
        form = QTextCharFormat()
        form.setForeground(QBrush(QColor(colStr)))
        if self.HDMagFactor > 1.0:
            form.setFontPointSize(glo.QDSpy_fontPntSizeHistoryHD)
        else:
            form.setFontPointSize(glo.QDSpy_fontPntSizeHistory)

        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.setCharFormat(form)
        cursor.insertText(msg)
        self.textBrowserHistory.setTextCursor(cursor)
        self.textBrowserHistory.ensureCursorVisible()


# ---------------------------------------------------------------------
# _____________________________________________________________________
if __name__ == "__main__":
    try:
        # Create GUI
        QDSApp = QApplication(sys.argv)
        QDSApp.setStyle("Fusion")
        QDSWin = MainWinClass(None)

        if PLATFORM_WINDOWS:
            # Make sure that Windows uses its icon in the task bar
            windll.shell32.SetCurrentProcessExplicitAppUserModelID(glo.QDSpy_appID)

        # Show window and start GUI handler
        QDSWin.show()
        QDSApp.exec()

    except Exception as e:
        print(f"Fatal error: {e}")

    finally:
        pass

# ---------------------------------------------------------------------
