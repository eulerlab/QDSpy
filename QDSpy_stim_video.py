#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QDSpy module - defines video-related classes (ALPHA)

'Video'
  A class that serves as a proxy for a streamed video

'VideoCtrl'
  The movie control class manages the streaming of the video

Copyright (c) 2013-2024 Thomas Euler
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
import platform
import pyglet
import QDSpy_stim as stm
import QDSpy_stim_support as ssp
import QDSpy_global as glo
import moviepy.editor as mpe
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

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __loadVideo(self):
        """Loads a "real" movie file
        """
        # Check if movie file exists ...
        if not (os.path.isfile(self.fNameVideo)):
            return stm.StimErrC.videoFileNotFound

        try:
            # Load video
            self.video = mpe.VideoFileClip(self.fNameVideo)

        except IOError:
            return stm.StimErrC.invalidVideoFormat

        # Retrieve video description
        self.dxFr = self.video.size[0]
        self.dyFr = self.video.size[1]
        self.nFr = self.video.duration * self.video.fps
        self.fps = self.video.fps
        ssp.Log.write(
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
        self.frames = self.video.iter_frames()
        self.isReady = True
        return stm.StimErrC.ok

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def load(self, _fName, _testOnly=False):
        """Reads a movie file (e.g. AVI); a description file is not needed
        Returns an error of the QDSpy_stim.StimErrC class
        """
        tempStr = (os.path.splitext(os.path.basename(_fName)))[0]
        self.fExtVideo = os.path.splitext(_fName)[1].lower()
        self.isTestOnly = _testOnly

        if PLATFORM_WINDOWS:
            tempDir = os.path.dirname(_fName)
            if len(tempDir) > 0:
                tempDir += "\\"
            self.fNameVideo = _fName
        else:
            tempDir = os.getcwd()
            self.fNameVideo = glo.repairPath(tempDir + tempStr) + self.fExtVideo

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
        """Resets parameters, delete sprite and recreate it (this way it
        looses its membership to a pyglet drawing batch)
        """
        self.posXY = (0, 0)
        self.magXY = (1.0, 1.0)
        self.rot = 0.0
        self.trans = 255
        self.isDone = False
        self.isFirst = True

        self.kill()
        self.Group = pyglet.graphics.OrderedGroup(self.order)
        self.isReady = self.check()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def kill(self):
        """Kill internal objects
        """
        self.isReady = False
        if self.Sprite is not None:
            self.Sprite.delete()
            self.Sprite = None
            self.Group = None

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def check(self):
        """Returns True if the video is valid
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
        """Set sprite properties
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
        """Set sprite batch
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
        """Retrieve next frame index
        """
        if self.isDone or not self.isReady:
            return -1

        if self.isFirst:
            self.isFirst = False
            self.iCurrFr = 0

        else:
            self.iCurrFr += 1
            self.isDone = not (self.iCurrFr < self.Video.nFr)

        if not (self.isDone):
            frame = next(self.Video.frames)
            pyglet_img = pyglet.image.ImageData(
                self.Video.dxFr,
                self.Video.dyFr,
                "RGB",
                frame.tostring(),
                pitch=self.Video.dxFr * 3,
            )
            self.Sprite = pyglet.sprite.Sprite(
                pyglet_img.get_texture(), usage="stream", group=self.Group
            )

            if rdr.PYGLET_VER < 1.4:
                self.Sprite.set_position(self.posXY[0], y=self.posXY[1])
            else:
                self.Sprite.position = self.posXY
            self.Sprite.scale = self.magXY[0]
            self.Sprite.rotation = self.rot
            self.Sprite.opacity = self.trans

        else:
            self.iCurrFr = -1

        return self.iCurrFr


# ---------------------------------------------------------------------
