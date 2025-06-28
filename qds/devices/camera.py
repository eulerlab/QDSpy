#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
USB cam API

Simple API to control an USB camera using OpenCV

Copyright (c) 2013-2016 Thomas Euler
All rights reserved.
"""
# ---------------------------------------------------------------------
__author__ 	= "code@eulerlab.de"

# ---------------------------------------------------------------------
import numpy as np
import cv2

# ---------------------------------------------------------------------
CameraList = []
maxCamera  = 10

# ---------------------------------------------------------------------
def get_camera_list():
  """ Search for available cameras and generate a list with their 
      properties
  """    
  global CameraList
  
  CameraList = []
  for iCam in range(maxCamera):
    Cam = cv2.VideoCapture(iCam)
    if Cam.isOpened():
      desc = {}
      desc["index"]      = iCam
      desc["width"]      = int(Cam.get(cv2.CAP_PROP_FRAME_WIDTH))
      desc["height"]     = int(Cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
      desc["rate_Hz"]    = Cam.get(cv2.CAP_PROP_FPS)
      desc["exposure_s"] = Cam.get(cv2.CAP_PROP_EXPOSURE)
      desc["string"]     = "#{0} {1}x{2}".format(iCam, desc["width"], 
                                                 desc["height"])
      """
      CAP_PROP_BRIGHTNESS Brightness of the image (only for cameras).
      CAP_PROP_CONTRAST Contrast of the image (only for cameras).
      CAP_PROP_SATURATION Saturation of the image (only for cameras).
      CAP_PROP_HUE Hue of the image (only for cameras).
      CAP_PROP_GAIN Gain of the image (only for cameras).
      CAP_PROP_CONVERT_RGB Boolean flags indicating whether images should be converted to RGB.
      """     
      CameraList.append(desc)
      Cam.release()
  return CameraList    

# =====================================================================
#
# ---------------------------------------------------------------------
class Camera:
  """ Initializes a USB camera object
  """
  def __init__(self, _funcLog=None):
    self.__reset()
    if _funcLog == None:
      self.log = self.__log
    else:
      self.log = _funcLog
      
  def __reset(self):
    self.cam    = None
    self.index  = -1
    self.width  = 0
    self.height = 0
    
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def connect(self, _index):
    """ Connect to the camera with the given index; returns True if
        successful
    """
    if self.cam != None:
      self.cam.release()
    self.cam = cv2.VideoCapture(_index) 
    '''
    self.cam = cv2.VideoCapture("E:\\User\\Dropbox\\__QDSpy3\\Stimuli\\waterAvi _SAFE.avi")
    '''
    if self.cam.isOpened():
      self.index   = _index
      self.width   = int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH))
      self.height  = int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
      self.winName = "Cam{0}".format(self.index)
      self.log("ok", "Camera #{0} ({1}x{2}) connected"
                     .format(_index, self.width, self.height))      
    else:
      self.__reset()
      self.log("ERROR", "Failed to connect to camera #{0}".format(_index))
    
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def disconnect(self):
    if self.cam != None:
      self.cam.release()
      self.__reset()
      self.log("ok", "Camera disconnected")
      
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def grab(self):
    """ Grab and return a frame
    """
    if self.cam != None:
      res, frame = self.cam.read()
      if res:
        #***        
        frameOut = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frameOut  
    return np.array([], dtype=np.uint8)

  
  def show(self):
    """ Open a window and show a the camera frames life until the 'q'
        key is pressed
    """    
    if self.cam != None:
      while True:
        res, frame = self.cam.read()
        if res:
          cv2.imshow(self.winName, frame)
          if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        else:
          break
      if res:
        cv2.destroyWindow(self.winName)   
        
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def __log(self, _sHeader, _sMsg):
    print("{0!s:>8} {1}".format(_sHeader, _sMsg))
  
# ---------------------------------------------------------------------
"""
cap = cv2.VideoCapture(0)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    print(frame)

    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Display the resulting frame
    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
"""
