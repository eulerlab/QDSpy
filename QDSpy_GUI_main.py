#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
#  QDS_GUI_main.py
#
#  ...
#
#  Copyright (c) 2013-2015 Thomas Euler
#  All rights reserved.
#
# ---------------------------------------------------------------------
__author__ 	= "code@eulerlab.de"

# ---------------------------------------------------------------------
import sys
import time
import os
import pickle
from   ctypes                 import windll
from   PyQt4                  import QtCore, QtGui, uic
from   multiprocessing        import Process
import QDSpy_stim             as stm
import QDSpy_stim_support     as ssp
import QDSpy_config           as cnf
import QDSpy_GUI_support      as gsu
import QDSpy_multiprocessing  as mpr
from   QDSpy_global           import *
import QDSpy_core

if QDSpy_use_Lightcrafter:
  import Devices.lightcrafter as lcr

# ---------------------------------------------------------------------
form_class   = uic.loadUiType("QDSpy_GUI_main.ui")[0]

# ---------------------------------------------------------------------
fStrPreRed   = '<html><head/><body><p><span style="color:#ff0000;">'
fStrPreGreen = '<html><head/><body><p><span style="color:#00aa00;">'
fStrPost     = '</span></p></body></html>'

# ---------------------------------------------------------------------
class State:
  undefined  = 0
  idle       = 1
  ready      = 2
  loading    = 3
  compiling  = 4
  playing    = 5
  canceling  = 6
  # ...

GUI_timeout  = 5.0

# ---------------------------------------------------------------------
class Canceled(Exception) :pass

# ---------------------------------------------------------------------
# Main application window
# ---------------------------------------------------------------------
class MainWinClass(QtGui.QMainWindow, form_class):
  def __init__(self, parent=None):
    # Initialize
    #
    self.Conf          = cnf.Config()
    self.Stim          = stm.Stim()
    self.currStimPath  = self.Conf.pathStim
    self.currQDSPath   = os.getcwd()
    self.currStimName  = "n/a"
    self.currStimFName = ""
    self.isStimReady   = False
    self.isStimCurr    = False
    self.isViewReady   = False
    self.Stage         = None

    QtGui.QMainWindow.__init__(self, parent)
    self.setupUi(self)
    
    # Bind GUI ...
    #
    self.btnRefreshStimList.clicked.connect(self.OnClick_btnRefreshStimList)
    self.listStim.itemClicked.connect(self.OnClick_listStim)
    self.listStim.itemDoubleClicked.connect(self.OnDblClick_listStim)
    self.btnStimPlay.clicked.connect(self.OnClick_btnStimPlay)
    self.btnStimCompile.clicked.connect(self.OnClick_btnStimCompile)
    self.btnStimAbort.clicked.connect(self.OnClick_btnStimAbort)
    self.checkShowHistory.clicked.connect(self.OnClick_checkShowHistory)
    
    self.spinBoxLED1.valueChanged.connect(self.OnClick_spinBoxLED_valueChanged)
    self.spinBoxLED2.valueChanged.connect(self.OnClick_spinBoxLED_valueChanged)
    self.spinBoxLED3.valueChanged.connect(self.OnClick_spinBoxLED_valueChanged)
    self.spinBoxLED4.valueChanged.connect(self.OnClick_spinBoxLED_valueChanged)
    self.btnSetLEDs.clicked.connect(self.OnClick_btnSetLEDs)
    self.btnSetLEDs.setEnabled(QDSpy_use_Lightcrafter)

    self.checkBoxStageCSEnable.clicked.connect(self.OnClick_checkStageCSEnable)
    self.spinBoxStageCS_hOffs.valueChanged.connect(
      self.OnClick_spinBoxStageCS_hOffs_valueChanged)
    self.spinBoxStageCS_vOffs.valueChanged.connect(
      self.OnClick_spinBoxStageCS_vOffs_valueChanged)
    self.spinBoxStageCS_hScale.valueChanged.connect(
      self.OnClick_spinBoxStageCS_hScale_valueChanged)
    self.spinBoxStageCS_vScale.valueChanged.connect(
      self.OnClick_spinBoxStageCS_vScale_valueChanged)
    self.spinBoxStageCS_rot.valueChanged.connect(
      self.OnClick_spinBoxStageCS_rot_valueChanged)
    self.btnSaveStageCS.clicked.connect(self.OnClick_btnSaveStageCS)

    self.stbarErrMsg   = QtGui.QLabel()
    self.stbarStimMsg  = QtGui.QLabel()
    self.statusbar.addWidget(self.stbarErrMsg, 2)
    self.statusbar.addPermanentWidget(self.stbarStimMsg, 2)
    self.lblSelStimName.setText(self.currStimName)
    
    self.lineEditComment.returnPressed.connect(self.OnClick_AddComment)
    
    # Create status objects and a pipe for communicating with the
    # presentation process (see below)    
    #
    self.state         = State.undefined
    self.Sync          = mpr.Sync()
    ssp.Log.setGUISync(self.Sync)
    
    # Create process that opens a view (an OpenGL window) and waits for
    # instructions to play stimululi
    #
    self.worker = Process(target=QDSpy_core.main,
                          args=(self.currStimFName, True, self.Sync))
    self.worker.daemon = True     
    self.worker.start()    
    self.isViewReady   = True
    self.setState(State.idle, True)

    # Update GUI ...
    #
    self.updateStimList()
    self.updateAll()

    # Check if autorun stimulus file present and if so run it
    #
    try:
      self.currStimFName = self.currStimPath +QDSpy_autorunStimFileName
      self.isStimCurr    = gsu.getStimCompileState(self.currStimFName)
      if not(self.isStimCurr):
        self.currStimFName = self.currQDSPath +"\\" +QDSpy_autorunDefFileName
        self.logWrite("ERROR", "No compiled `{0}` in current stimulus folder,"
                               " using `{1}` in `{2}`."
                               .format(QDSpy_autorunStimFileName, 
                                       QDSpy_autorunDefFileName, 
                                       self.currQDSPath))
      self.logWrite("DEBUG", "Running {0} ...".format(self.currStimFName))
      self.Stim.load(self.currStimFName, _onlyInfo=True)
      self.setState(State.ready)
      self.isStimReady = True
      self.runStim()

    except:
      # Failed ...
      #
      if(self.Stim.getLastErrC() != stm.StimErrC.ok):
        self.updateStatusBar(self.Stim.getLastErrStr(), True)
        ssp.Log.isRunFromGUI = False
        ssp.Log.write("ERROR", "No compiled `{0}` in current stimulus folder,"
                               " and `{1}.pickle` is not in `{2}`. Program is"
                               " aborted."
                               .format(QDSpy_autorunStimFileName, 
                                       QDSpy_autorunDefFileName, 
                                       self.currQDSPath))
        sys.exit(0)
    
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def __del__(self):
    # ...
    #
    pass
  
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def keyPressEvent(self, e):
    # Allow pressing ESC to abort stimulus presentation ...
    #
    if e.key() == QtCore.Qt.Key_Escape:
      if self.Sync.State.value in [mpr.PRESENTING, mpr.COMPILING]:
        self.OnClick_btnStimAbort()

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def closeEvent(self, event):
    # User requested to close the application
    #
    if QDSpy_isGUIQuitWithDialog:
      result = QtGui.QMessageBox.question(self, "Confirm closing QDSpy ...",
                                          "Are you sure you want to quit?",
                                          QtGui.QMessageBox.Yes | 
                                          QtGui.QMessageBox.No)
      event.ignore()
      if result == QtGui.QMessageBox.No:
        event.ignore()
        return
    
    # Closing is immanent, stop stimulus, if running ...
    #
    if self.Sync.State.value in [mpr.PRESENTING, mpr.COMPILING]:
      self.OnClick_btnStimAbort()
    
    # Save log 
    #
    os.makedirs(self.Conf.pathLogs, exist_ok=True)
    fName   = time.strftime("%Y%m%d_%H%M%S")
    j       = 0
    while os.path.exists(self.Conf.pathLogs +fName):
      fName = "{0}_{1:04d}".format(fName, j)
      j    += 1
      
    fPath   = self.Conf.pathLogs +fName +QDSpy_logFileExtension
    self.logWrite(" ", "Saving log file to '{0}' ...".format(fPath))
    
    with open(fPath, 'w') as logFile:
      logFile.write(str(self.textBrowserHistory.toPlainText()))  
    
    # ... and clean up
    #
    self.Sync.setRequestSafe(mpr.TERMINATING)    
    while self.worker.is_alive():
      time.sleep(0.2)
    event.accept()  

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def setState(self, _newState, _doUpdateGUI=False):
    # Update GUI state and GUI as well, if requested
    #
    self.state = _newState
    if _doUpdateGUI:
      self.updateAll()

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def updateAll(self):
    # Update the complete GUI
    #
    txt  = gsu.getShortText(self, self.currStimPath, self.lblCurrStimFolder)
    self.lblCurrStimFolder.setText(txt)

    stateWorker   = self.Sync.State.value
    if   stateWorker == mpr.PRESENTING:
      self.state  = State.playing
    elif stateWorker == mpr.COMPILING:  
      self.state  = State.compiling
    elif stateWorker in [mpr.CANCELING, mpr.TERMINATING]: 
      self.state  = State.canceling
    elif stateWorker == mpr.IDLE: 
      self.state  = State.ready
      
    isStimSelPerm = self.state in {State.undefined, State.idle, State.ready}
    
    self.listStim.setEnabled(isStimSelPerm)
    self.btnRefreshStimList.setEnabled(isStimSelPerm)
    """
    self.btnChangeStimFolder.setEnabled(isStimSelPerm)
    """

    self.btnStimPlay.setText("Play")
    self.btnStimPlay.setEnabled(self.isStimReady)
    self.btnStimCompile.setText("Compile")
    self.btnStimCompile.setEnabled(not(self.isStimCurr))
    self.btnStimAbort.setText("Abort")
    self.btnStimAbort.setEnabled(self.state == State.playing)

    if   self.state == State.loading:
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

    self.processPipe()
    self.updateStatusBar(stateWorker)
    QtGui.QApplication.processEvents()

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def updateStimList(self):
    # Update stimulus list widget
    #
    self.currStimFNames = gsu.getStimFileLists(self.currStimPath)
    self.listStim.clear()
    for stimFName in self.currStimFNames:
      self.listStim.addItem(gsu.getFNameNoExt(stimFName))

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def updateStatusBar(self, _msg="Ready", _isErr=False):
    # Update status bar
    #
    if _isErr:
      self.stbarErrMsg.setText(fStrPreRed +"Error: " +_msg +fStrPost)
    else:
      self.stbarErrMsg.setText(_msg)

    if (len(self.currStimName) > 0) and (self.isStimReady):
      self.stbarStimMsg.setText("Stimulus: " +self.currStimName)
    else:
      self.stbarStimMsg.setText("")

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def updateDisplayInfo(self):
    # Update display info and status
    #
    try:
      self.lblDisplDevName.setText(
        "{0}, screen #{1}".format(
          self.Stage.scrDevName, self.Stage.scrIndex))
      self.lblDisplDevRes.setText(
        "{0}x{1}, {2}bit, {3:.1f}({4:.1f}) Hz{5}".format(
          self.Stage.dxScr, self.Stage.dyScr,
          self.Stage.depth, 
          self.Stage.scrDevFreq_Hz, self.Stage.scrReqFreq_Hz,
          ", full" if self.Stage.isFullScr else ""))
      self.lblDisplDevInfo.setText(
        "{0:.2f}x{1:.2f} µm/pixel<br>offset: {2},{3}, angle: {4}°".format(
          self.Stage.scalX_umPerPix, 
          self.Stage.scalY_umPerPix,
          self.Stage.centX_pix, self.Stage.centY_pix,
          self.Stage.rot_angle))
      
      if len(self.Stage.LEDs) == 0:
        self.lblDisplDevLEDs.setText("n/a")
      else:  
        sTemp = ""
        pal   = QtGui.QPalette()
        for iLED, LED in enumerate(self.Stage.LEDs):
          sTemp += "{0}={1} ".format(LED[0], LED[1])
          pal.setColor(QtGui.QPalette.Window, QtGui.QColor(LED[4]))
          pal.setColor(QtGui.QPalette.WindowText, QtGui.QColor("white"))
          [spinBoxLED, label_LED] = gsu.getLEDGUIObjects(self, iLED)
          spinBoxLED.setValue(LED[1])
          spinBoxLED.setEnabled(True)
          label_LED.setPalette(pal)
          label_LED.setText(LED[0])
        self.lblDisplDevLEDs.setText(sTemp)      
        
      self.spinBoxStageCS_hOffs.setValue(self.Stage.centOffX_pix)
      self.spinBoxStageCS_vOffs.setValue(self.Stage.centOffY_pix)
      self.spinBoxStageCS_hScale.setValue(self.Stage.scalX_umPerPix)
      self.spinBoxStageCS_vScale.setValue(self.Stage.scalY_umPerPix)
      self.spinBoxStageCS_rot.setValue(self.Stage.rot_angle)

    except KeyError:
      pass

  # -------------------------------------------------------------------
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def OnClick_btnRefreshStimList(self):
    self.updateStimList()

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def OnClick_listStim(self, _selItem):
    # Show name of selected stimulus and some info
    #
    txtInfo            = "n/a"
    txtCompState       = "n/a"
    self.isStimReady   = False
    self.isStimCurr    = False
    self.currStimName  = _selItem.text()
    self.setState(State.idle)

    iSel = self.listStim.currentRow()
    if iSel >= 0:
      # Try loading selected stimulus pickle file
      #
      self.currStimFName = self.currStimFNames[iSel]
      try:
        self.Stim.load(self.currStimFName, _onlyInfo=True)

        # Succeed, now get info
        #
        self.setState(State.ready)
        self.isStimReady = True
        self.isStimCurr  = gsu.getStimCompileState(self.currStimFName)
        if self.isStimCurr:
          txtCompState   = fStrPreGreen +"compiled (.pickle) is up-to-date" +\
                           fStrPost
        else:
          txtCompState   = "compiled (.pickle) predates .py"
        txtInfo          = self.Stim.descrStr
        self.updateStatusBar()

      except:
        # Failed ...
        #
        txtCompState     = fStrPreRed +"not compiled (no .pickle)" +fStrPost
        if(self.Stim.getLastErrC() != stm.StimErrC.ok):
          self.updateStatusBar(self.Stim.getLastErrStr(), True)

      # Show info ...
      #
      self.lblSelStimName.setText(self.currStimName)
      self.lblSelStimInfo.setText(txtInfo)
      self.lblSelStimStatus.setText(txtCompState)
      self.updateAll()

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def OnClick_checkShowHistory(self, _checked):
    self.resize(self.maximumSize() if _checked else self.minimumSize())

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def OnClick_spinBoxLED_valueChanged(self, _val):
    self.btnSetLEDs.setEnabled(True)
    
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def OnClick_AddComment(self):
    data = {"userComment": self.lineEditComment.text()}
    self.logWrite("DATA", data.__str__())
    self.lineEditComment.setText("")    
    
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def OnClick_btnSetLEDs(self):
    if len(self.Stage.LEDs) == 0:
      return
    else:  
      curr  = []
      for iLED, LED in enumerate(self.Stage.LEDs):
        (spinBoxLED, label_LED) = gsu.getLEDGUIObjects(self, iLED)
        val = spinBoxLED.value()
        curr.append(val)
        self.Stage.setLEDCurrent(iLED, val)
        
    LCr    = lcr.Lightcrafter(_isCheckOnly=False, _isVerbose=False)
    result = LCr.connect()
    if result[0] == lcr.ERROR.OK:
      LCr.setLEDCurrents(curr[0:3])
      LCr.disconnect()   

    self.updateDisplayInfo()
    self.btnSetLEDs.setEnabled(False)    
    
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def OnClick_checkStageCSEnable(self, _checked):
    self.spinBoxStageCS_hOffs.setEnabled(_checked)
    self.spinBoxStageCS_vOffs.setEnabled(_checked)
    self.spinBoxStageCS_hScale.setEnabled(_checked)
    self.spinBoxStageCS_vScale.setEnabled(_checked)
    self.spinBoxStageCS_rot.setEnabled(_checked)
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
    self.Sync.pipeCli.send([mpr.PipeValType.toSrv_changedStage, 
                            self.Stage.getScaleOffsetAsDict()])
  
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def OnClick_btnSaveStageCS(self):  
    self.Conf.saveStageToConfig(self.Stage)
    
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def OnClick_btnStimPlay(self):
    self.runStim()

  def OnClick_btnStimCompile(self):
    self.compileStim()

  def OnClick_btnStimAbort(self):
    # Send a request to the worker to cancel the presentation 
    #
    self.setState(State.canceling)
    self.Sync.setRequestSafe(mpr.CANCELING)
    self.setState(State.canceling, True)
    
    # Wait for the worker to finish cancelling
    #
    if self.Sync.waitForState(mpr.IDLE, GUI_timeout, self.updateAll):
      self.setState(State.ready, True)
    else:
      self.logWrite("DEBUG", "OnClick_btnStimAbort, timeout waiting for IDLE")

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def OnDblClick_listStim(self, _selItem):
    self.runStim()


  # -------------------------------------------------------------------
  # Compiling and running stimuli 
  # -------------------------------------------------------------------
  def compileStim(self):
    # Send stimulus file name via pipe and signal worker thread to 
    # compile the stimulus
    #
    self.Sync.pipeCli.send([mpr.PipeValType.toSrv_fileName, self.currStimFName])
    self.Sync.setRequestSafe(mpr.COMPILING)
    self.logWrite(" ", "Compiling stimulus script ...")
    
    # Wait for the worker to start ...
    #
    if self.Sync.waitForState(mpr.COMPILING, GUI_timeout, self.updateAll):
      self.setState(State.compiling, True)
      
      # Wait for the worker to finish the presentation, while keeping the
      # GUI alive
      #
      self.Sync.waitForState(mpr.IDLE, 0.0, self.updateAll)
      self.OnClick_listStim(QtGui.QListWidgetItem(self.currStimFName))
      self.updateAll()
      
    else:
      self.logWrite("DEBUG", "runStim, timeout waiting for COMPILING")

  # -------------------------------------------------------------------
  def runStim(self):
    # Send stimulus file name via pipe and signal worker thread to 
    # start presenting the stimulus
    #
    self.Sync.pipeCli.send([mpr.PipeValType.toSrv_fileName, self.currStimFName])
    self.Sync.setRequestSafe(mpr.PRESENTING)
    self.logWrite(" ", "Presenting stimulus ...")
    
    # Wait for the worker to start ...
    #
    if self.Sync.waitForState(mpr.PRESENTING, GUI_timeout, self.updateAll):
      self.setState(State.playing, True)
      
      # Wait for the worker to finish the presentation, while keeping the
      # GUI alive
      #
      self.Sync.waitForState(mpr.IDLE, 0.0, self.updateAll)
      self.updateAll()
      
    else:
      self.logWrite("DEBUG", "runStim, timeout waiting for PRESENTING")


  # -------------------------------------------------------------------
  # Communication with worker-thread
  # -------------------------------------------------------------------
  def processPipe(self):
    # Read data from pipe to worker thread, if available
    # 
    while self.Sync.pipeCli.poll():
      data = self.Sync.pipeCli.recv()
      if   data[0] == mpr.PipeValType.toCli_log:
        # Handle log data -> write to history 
        #
        self.log(data)
        
      elif data[0] == mpr.PipeValType.toCli_displayInfo:
        # Handle display information data -> update GUI
        #
        self.Stage = pickle._loads(data[1])
        self.updateDisplayInfo()
        
      else:
        # ***************************
        # ***************************
        # TODO: Other types of data need to be processed
        # ***************************
        # ***************************
        pass

  # -------------------------------------------------------------------
  # Logging-related 
  # -------------------------------------------------------------------
  def logWrite(self, _headerStr, _msgStr):
    # Log a message to the appropriate output
    #
    if QDSpy_workerMsgsToStdOut:
      ssp.Log.write(_headerStr, _msgStr)
    else:  
      data   = ssp.Log.write(_headerStr, _msgStr, _getStr=True)
      if data != None:
        self.log(data)
    
  def log(self, _data):
    msg    = _data[2] +"\r"
    colStr = _data[3]
    cursor = self.textBrowserHistory.textCursor()
    form   = QtGui.QTextCharFormat() 
    form.setForeground(QtGui.QBrush(QtGui.QColor(colStr)))
    cursor.setCharFormat(form)
    cursor.insertText(msg)
    self.textBrowserHistory.setTextCursor(cursor)
    self.textBrowserHistory.ensureCursorVisible()
 
# ---------------------------------------------------------------------
# _____________________________________________________________________
if __name__ == "__main__":
  # Create GUI
  #
  QDSApp = QtGui.QApplication(sys.argv)
  QDSWin = MainWinClass(None)
  
  # Make sure that Windows uses its icon in the task bar
  #
  windll.shell32.SetCurrentProcessExplicitAppUserModelID(QDSpy_appID)    

  # Show window and start GUI handler
  #
  QDSWin.show()
  QDSApp.exec_()
  

# ---------------------------------------------------------------------
