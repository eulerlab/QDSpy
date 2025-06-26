#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QDSpy module - defines video-related classes

'Video'
  A class that serves as a proxy for a streamed video

'VideoCtrl'
  The movie control class manages the streaming of the video

Copyright (c) 2013-2025 Thomas Euler
All rights reserved.

2024-08-04 - `pyglet` calls encapsulated in `renderer_opengl.py`             
2025-04-05 - Cleaning up
2025-06-24 - Adapted to current `moviepy` (>= version 2)
           - Fixed a few bugs that prevented restarting the same video
"""
# ---------------------------------------------------------------------
__author__ = "code@eulerlab.de"

import os
import platform
import QDSpy_stim as stm
import QDSpy_global as glo
import QDSpy_file_support as fsu
import Libraries.log_helper as _log
'''
import moviepy.editor as mpe
'''
from moviepy import VideoFileClip
import Graphics.renderer_opengl as rdr

PLATFORM_WINDOWS = platform.system() == "Windows"

# ---------------------------------------------------------------------
# Video object class
# ---------------------------------------------------------------------
class Video:
    def __init__(self, _Config):
        # Initializing
        self.isReady = False
        self.dxFr = 0
        self.dyFr = 0
        self.nFr = 0
        self.video = None
        self._useIter = glo.QDSpy_vid_useIter

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __loadVideo(self):
        """Loads a "real" movie file
        """
        # Check if movie file exists ...
        if not (os.path.isfile(self.fNameVideo)):
            return stm.StimErrC.videoFileNotFound

        try:
            # Load video
            '''
            self.video = mpe.VideoFileClip(self.fNameVideo)
            '''
            self.video = VideoFileClip(self.fNameVideo)

        except IOError:
            return stm.StimErrC.invalidVideoFormat

        # Retrieve video description
        self.dxFr = self.video.size[0]
        self.dyFr = self.video.size[1]
        self.nFr = self.video.duration * self.video.fps
        self.fps = self.video.fps
        _log.Log.write(
            "DEBUG",
            "stim_video: {0}x{1} pixel, {2} frames, {3} fps".format(
                self.dxFr, self.dyFr, self.nFr, self.fps
            ),
        )

        if self.isTestOnly:
            # Return here if the video was only loaded to test if it is ok
            self.video = None
            return stm.StimErrC.ok

        # Load movie frames (note that frames is a generator!)
        if self._useIter:
            self._reiterate()

        self.isReady = True
        return stm.StimErrC.ok

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _reiterate(self):
        self.frames = self.video.iter_frames()
    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def load(self, _fName, _testOnly=False):
        """ Reads a movie file (e.g. AVI); a description file is not 
            needed. Returns an error of the QDSpy_stim.StimErrC class
        """
        self.fExtVideo = fsu.getFileExt(_fName)
        self.isTestOnly = _testOnly
        self.fNameVideo = fsu.getJoinedPath(
            fsu.getCurrentPath(), _fName
        )
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
        self.Video = _Video
        self.Sprite = None
        self.order = _order
        self.reset()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def reset(self):
        """ Resets parameters, delete sprite and recreate it (this way it
            looses its membership to a pyglet drawing batch)
        """
        self.posXY = (0, 0)
        self.magXY = (1.0, 1.0)
        self.rot = 0.0
        self.trans = 255
        self.isDone = False
        self.isFirst = True
        self.iCurrFr = -1

        self.kill()
        self.Group = rdr.getOrderedGroup(self.order)
        self.isReady = self.check()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def kill(self):
        """ Kill internal objects
        """
        self.isReady = False
        if self.Sprite is not None:
            self.Sprite.delete()
            self.Sprite = None
            self.Group = None

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def check(self):
        """ Returns True if the video is valid
        """
        #
        # *****************
        # *****************
        # TODO: Check really if video is valid
        # *****************
        # *****************
        return True

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setSpriteProperties(self, _posXY, _magXY, _rot, _trans):
        """ Set sprite properties
        """
        self.posXY = (
            _posXY[0] - self.Video.dxFr // 2 * _magXY[0],
            _posXY[1] - self.Video.dyFr // 2 * _magXY[1],
        )
        self.magXY = _magXY
        self.rot = _rot
        self.trans = _trans

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setSpriteBatch(self, _batch):
        """ Set sprite batch
        """
        if self.Sprite is not None:
            if _batch.isScrOvl:
                if self.iScr == 0:
                    self.Sprite.batch = _batch.BatchSpr
                else:
                    self.Sprite.batch = _batch.Batch2Spr
            else:
                self.Sprite.batch = _batch.BatchSpr

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getNextFrIndex(self):
        """ Retrieve next frame index
        """
        '''
        print(self.isDone, self.isReady, self.isFirst, self.iCurrFr)
        '''
        if self.isDone or not self.isReady:
            return -1

        if self.isFirst:
            self.isFirst = False
            self.iCurrFr = 0

        else:
            self.iCurrFr += 1
            self.isDone = not (self.iCurrFr < self.Video.nFr)

        if not (self.isDone):
            if self.Video._useIter:
                frame = next(self.Video.frames)
            else:
                frame = self.Video.video.get_frame(self.iCurrFr /60)

            tmpImg = rdr.getImageData(
                self.Video.dxFr, self.Video.dyFr, "RGB",
                frame.tostring(), pitch=self.Video.dxFr *3,
            )
            self.Sprite = rdr.getSprite(
                tmpImg.get_texture(), "stream", self.Group
            )
            self.Sprite.position = self.posXY
            self.Sprite.scale = self.magXY[0]
            self.Sprite.rotation = self.rot
            self.Sprite.opacity = self.trans

        else:
            if self.Video._useIter:
                self.Video._reiterate()
            self.isFirst = True

        return self.iCurrFr

# ---------------------------------------------------------------------
