#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QDSpy module - defines video-related classes (ALPHA)

'Video' 
  A class that serves as a proxy for a streamed video

'VideoCtrl'
  The movie control class manages the streaming of the video

Copyright (c) 2013-2016 Thomas Euler
All rights reserved.

***********************************************************************
***********************************************************************
TODO: Still uses pyglet directly ...
***********************************************************************
***********************************************************************
"""
# ---------------------------------------------------------------------
__author__ = "code@eulerlab.de"

import os
import pyglet
import QDSpy_stim as stm
import QDSpy_global as glo

# ---------------------------------------------------------------------
# Video object class
# ---------------------------------------------------------------------
class Video:
  def __init__(self, _Config):
    # Initializing
    #
    self.isReady  = False
    self.dxFr     = 0
    self.dyFr     = 0
    self.nFr      = 0
    self.video    = None

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def __loadVideo(self):
    # Loads "real" movie file
    #
    # Check if movie file exists ...
    #
    if not(os.path.isfile(self.fNameVideo)):
      return stm.StimErrC.videoFileNotFound

    try: 
      # Load video
      #
      self.video = pyglet.media.load(self.fNameVideo, streaming=True)
      
    except IOError:  
      return stm.StimErrC.invalidVideoFormat
      
    # Retrieve video description
    #
    v_format     = self.video.video_format
    self.dxFr    = v_format.width
    self.dyFr    = v_format.height
    self.nFr     = round(v_format.frame_rate)*self.video.duration
      
    if self.isTestOnly:
      # Return here if the video was only loaded to test if it is ok
      #
      self.video.delete()
      return stm.StimErrC.ok
      
    self.isReady = True
    return stm.StimErrC.ok
    

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def load(self, _fName, _testOnly=False):
    # Reads a movie file (e.g. AVI); a description file is not needed
    # Returns an error of the QDSpy_stim.StimErrC class
    #
    tempDir         = os.path.dirname(_fName)
    if len(tempDir) > 0:
      tempDir      += "\\"
    self.fNameVideo = _fName
    self.fExtVideo  = os.path.splitext(_fName)[1].lower()
    self.isTestOnly = _testOnly
    
    if self.fExtVideo in glo.QDSpy_vidAllowedVideoExts:
      return self.__loadVideo()
    else:
      return stm.StimErrC.invalidVideoFormat      


# ---------------------------------------------------------------------
# Video control class object
# ---------------------------------------------------------------------
class VideoCtrl:
  def __init__(self, _Video, _order=2):
    # Initializing
    #
    self.Video  = _Video
    self.Sprite = None
    self.order  = _order
    self.reset()

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def reset(self):
    # Reset parameters, delete sprite and recreate it (this way it
    # looses its membership to a pyglet drawing batch)
    #
    self.posXY   = (0,0)
    self.magXY   = (1.0,1.0)
    self.rot     = 0.0
    self.trans   = 255
    self.isDone  = False
    self.isFirst = True

    self.kill()
    self.Group   = pyglet.graphics.OrderedGroup(self.order)
    self.isReady = self.check()

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def kill(self):
    # ...
    #
    self.isReady   = False
    if self.Sprite != None:
      self.Sprite.delete()
      self.Sprite  = None
      self.Group   = None
      self.Player.delete()
      self.Player  = None
      print("killed")

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def check(self):
    # Returns True if the video is valid
    #
    # *****************
    # *****************
    # TODO: Check really if video is valid
    # *****************
    # *****************
    return True

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def setSpriteProperties(self, _posXY, _magXY, _rot, _trans):
    # Set sprite properties
    #
    self.posXY     = (_posXY[0] -self.Video.dxFr//2 *_magXY[0],
                      _posXY[1] -self.Video.dyFr//2 *_magXY[1])
    self.magXY     = _magXY
    self.rot       = _rot
    self.trans     = _trans
    
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def setSpriteBatch(self, _batch):
    # Set sprite batch
    #
    if self.Sprite != None:
      self.Sprite.batch = _batch.currBatch        

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def getNextFrIndex(self):
    # ...
    #
    if self.isDone or not(self.isReady):
      return -1

    if self.isFirst:
      self.isFirst  = False
      self.iCurrFr  = 0
      self.Player   = pyglet.media.Player()
      print("now queue ...")
      self.Player.queue(self.Video.video)
      
    else:
      self.iCurrFr += 1
      self.isDone   = not(self.iCurrFr < self.Video.nFr-10)
      
    if not(self.isDone):
      if self.iCurrFr == 0:
        self.Player.play()
      tex = self.Player.get_texture()
      self.Sprite = pyglet.sprite.Sprite(tex, usage="stream", group=self.Group)
      self.Sprite.set_position(self.posXY[0], y=self.posXY[1])
      self.Sprite.scale    = self.magXY[0]
      self.Sprite.rotation = self.rot
      self.Sprite.opacity  = self.trans
      print(self.iCurrFr, self.Player.time, self.Player.playing)      
      
    else:  
      print("IS DONE")
      #self.Player.pause()
      #self.Player.delete()
      self.iCurrFr = -1
      
    return self.iCurrFr

# ---------------------------------------------------------------------
