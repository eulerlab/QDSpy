#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QDSpy module - camera dialog

Copyright (c) 2013-2024 Thomas Euler
All rights reserved.

2024-06-19 - Ported from `PyQt5` to `PyQt6`
"""
# ---------------------------------------------------------------------
__author__ 	= "code@eulerlab.de"

from   PyQt6 import QtGui, QtCore, uic
from   PyQt6.QtCore import QTimer
from   PyQt6.QtWidgets import QDialog
import qds.QDSpy_core_support as csp

if csp.module_exists("cv2"):
  import qds.devices.camera as cam
  
# ---------------------------------------------------------------------
form_class       = uic.loadUiType("qds/QDSpy_GUI_cam.ui")[0]
grab_interval_ms = 50

# ---------------------------------------------------------------------
# Camera dialog window
# ---------------------------------------------------------------------
class CamWinClass(QDialog, form_class):
  def __init__(self, parent=None, _funcUpdate=None, _funcLog=None):
    QtGui.QDialog.__init__(self, parent)
    
    # Initialize GUI ...
    #
    self.setupUi(self)
    self.btnPause.clicked.connect(self.OnClick_btnPause)
    self.funcUpdate = _funcUpdate

    # Generate camera object
    #
    self.cam = cam.Camera(_funcLog)
    
    # Generate timer object for continous video grabbing
    #
    self.timer = QTimer()
    self.timer.setInterval(grab_interval_ms)
    self.timer.timeout.connect(self.grab)
    
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def showEvent(self, event):
    # Camera window is (re)shown
    #
    super().showEvent(event)
    
    # Connect a camera and start timer to grab continously new frames
    #
    self.cam.connect(0)
    self.timer.start()
        
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def closeEvent(self, event):
    # Camera window is being closed
    #
    # Stop timer and disconnect camera
    #
    self.timer.stop()
    self.cam.disconnect()
    
    # Update parent 
    #
    if self.parent is not None and self.funcUpdate is not None:
      self.funcUpdate()
      
    self.accept()    
    
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def grab(self):
    frame = self.cam.grab()
    if len(frame) > 0:
      height, width, channel = frame.shape
      bytesPerLine = 3 * width
      qImg = QtGui.QImage(frame.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)
      pix = QtGui.QPixmap(qImg)
      self.label_CamFrame.setPixmap(pix.scaled(self.label_CamFrame.size(), 
                                               QtCore.Qt.KeepAspectRatio, 
                                               QtCore.Qt.FastTransformation))

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def OnClick_btnPause(self):
    if self.timer.isActive():
      self.timer.stop()
      self.btnPause.setText("Play")
    else:
      self.timer.start()
      self.btnPause.setText("Pause")
      
# ---------------------------------------------------------------------        