#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QDSpy module - defines movie-related classes

'Movie'
  A class that contains a movie image as a 3D texture.

'MovieCtrl'
  The movie control class manages the presentation of a movie according to
  the presentation parameters

Copyright (c) 2013-2025 Thomas Euler
All rights reserved.

2024-06-15 - Fix for breaking change in `configparser`; now using
             `ConfigParser` instead of `RawConfigParser`
2024-08-04 - `pyglet` calls encapsulated in `renderer_opengl.py`             
2025-04-05 - Cleaning up
"""
# ---------------------------------------------------------------------
__author__ = "code@eulerlab.de"

import os.path
import platform
import configparser
import qds.QDSpy_stim as stm
import qds.QDSpy_global as glo
import qds.QDSpy_file_support as fsu
import qds.libraries.log_helper as _log
import qds.graphics.renderer_opengl as rdr

PLATFORM_WINDOWS = platform.system() == "Windows"

# ---------------------------------------------------------------------
# Movie object class
# ---------------------------------------------------------------------
class Movie:
    def __init__(self, _Config :object):
        """ Initializing
        """
        self.isReady = False
        self.dxFr = 0
        self.dyFr = 0
        self.nFr = 0
        self.comment = "n/a"
        self.is1FrBL = True
        self.nFrX = 0
        self.nFrY = 0
        self.img = None
        self.imgSeq = None
        self.movie = None
        self.movTex = None
        self.use3DTex = _Config.use3DTextures

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __loadMontage(self) -> object:
        """ Check if image montage and description files exist ...
        """
        # *****************
        # *****************
        # TODO: Check also if image montage file format is compatible
        #       use self.fExtImg
        # *****************
        # *****************
        if not (os.path.isfile(self.fNameImg)) or not (os.path.isfile(self.fNameDesc)):
            return stm.StimErrC.movieFileNotFound

        # Read description file
        self.Desc = configparser.ConfigParser()
        try:
            self.Desc.read(self.fNameDesc)
            self.dxFr = self.Desc.getint(glo.QDSpy_movDescSect, glo.QDSpy_movFrWidth)
            self.dyFr = self.Desc.getint(glo.QDSpy_movDescSect, glo.QDSpy_movFrHeight)
            self.nFr = self.Desc.getint(glo.QDSpy_movDescSect, glo.QDSpy_movFrCount)
            self.comment = self.Desc.get(glo.QDSpy_movDescSect, glo.QDSpy_movComment)
            self.is1FrBL = self.Desc.getboolean(
                glo.QDSpy_movDescSect, glo.QDSpy_movIsFirstFrBottLeft
            )
            _log.Log.write(
                "DEBUG", 
                f"__loadMontage: {self.nFr} frames, {self.dxFr} x {self.dyFr} pixels"
            )

        except IOError:
            # Error parsing the description file
            return stm.StimErrC.invalidMovieDesc

        # Load and check image data
        self.img = rdr.imageLoad(self.fNameImg)
        _log.Log.write(
            "DEBUG", 
            f"__loadMontage: image is {self.img.width} x {self.img.height} pixels"
        )
        self.nFrX = self.img.width // self.dxFr
        self.nFrY = self.img.height // self.dyFr
        n = self.nFrX * self.nFrY
        if (
            ((self.img.width % self.dxFr) > 0)
            or ((self.img.height % self.dyFr) > 0)
            or (n != self.nFr)
        ):
            # Image size is not consistent with frame size
            return stm.StimErrC.inconsMovieDesc

        if self.isTestOnly:
            # Return here if the movie was only loaded to test if it is ok
            # (safe time by avoiding the rest of the movie preparations)
            return stm.StimErrC.ok

        if not self.is1FrBL:
            # The first frame is not the bottom-left as expected by pyglet, but
            # the top-left, therefore, image data needs to be reshaped
            # *****************
            # *****************
            # TODO: ...
            # *****************
            # *****************
            pass

        # Create a 3D texture (basically an image sequence) from the montage
        try:
            tmpSeq = rdr.getImageGrid(self.img, self.nFrY, self.nFrX)
            self.imgSeq = rdr.getTextureSequence(tmpSeq, use_3d=self.use3DTex)
        except rdr.RendererException as ev:
            raise stm.StimException(stm.StimErrC.RendererError, ev)

        # *****************
        # *****************
        # TODO: Texture3D is supposed to be faster but I could not get rid of
        #       blending (interpolation) between texture layers.
        #       When using get_image_data(self.iCurrFr) to update sprite,
        #       blending is gone but anchoring is incorrect ...
        #       The disadvantage of the current solution is that the edges of
        #       the movie frames are slightly blended with the neighboring
        #       frames (does not happen with Texture3D)
        # *****************
        # *****************

        # Set anchor position to center to for all frames
        for iFr in range(self.nFr):
            self.imgSeq[iFr].anchor_x = self.dxFr / 2
            self.imgSeq[iFr].anchor_y = self.dyFr / 2

        self.isReady = True
        return stm.StimErrC.ok

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def load(self, _fName, _testOnly=False) -> object:
        """ Reads an image file (a montage of frames) and the 
            description file (same name but .txt extension)
            Returns an error of the QDSpy_stim.StimErrC class
        """
        self.fExtImg = fsu.getFileExt(_fName)
        self.isTestOnly = _testOnly
        path = fsu.getCurrentPath() 
        fname_desc = fsu.getPathReplacedExt(_fName, glo.QDSpy_movDescFileExt)
        self.fNameDesc = fsu.getJoinedPath(path, fname_desc)
        self.fNameImg = fsu.getJoinedPath(path, _fName)
        if self.fExtImg in glo.QDSpy_movAllowedMovieExts:
            return self.__loadMontage()
        else:
            return stm.StimErrC.invalidMovieFormat

# ---------------------------------------------------------------------
# Movie control class object
# ---------------------------------------------------------------------
class MovieCtrl:
    def __init__(
            self, _seq :list, _ID :int, _Movie :object =None, 
            _nFr :int =0, _order :int =2
        ):
        """ Initializing
        """
        self.Movie = _Movie
        self.fr0 = _seq[0]     # first frame
        self.fr1 = _seq[1]     # last frame
        self.frreps = _seq[2]  # number of frame repeats
        self.sqreps = _seq[3]  # number of sequence repeats
        self.iScr = 0
        self.ID = _ID

        self.isReverse = self.fr0 > self.fr1
        self.order = _order
        self.Sprite = None
        if self.Movie is not None:
            self.nFr = self.Movie.nFr
        else:
            self.nFr = _nFr
        self.reset()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def reset(self):
        """ Reset parameters, delete sprite and recreate it (this way it
            looses its membership to a pyglet drawing batch)
        """
        self.posXY = (0, 0)
        self.magXY = (1.0, 1.0)
        self.rot = 0.0
        self.trans = 255
        self.isDone = False
        self.isFirst = True

        self.kill()
        if self.Movie is not None:
            self.Group = rdr.getOrderedGroup(self.order)
            self.Sprite = rdr.getSprite(
                self.Movie.imgSeq[0], "dynamic", self.Group
            )
            self._offsXY = (self.Sprite.width //2, self.Sprite.height //2)

        self.isReady = self.check()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def kill(self):
        self.isReady = False
        if self.Sprite is not None:
            self.Sprite.delete()
            self.Sprite = None
            self.Group = None
            self.Player = None

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def check(self) -> bool:
        """ Returns True if the sequence is valid
        """
        return (
            (self.fr0 >= 0)
            and (self.fr1 >= 0)
            and (self.frreps >= 1)
            and (self.sqreps >= 1)
            and (self.fr1 < self.nFr)
        )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setSpriteProperties(
            self, _posXY :list, _magXY :list, _rot :float, _trans :int
        ):
        """ Set sprite properties
        """
        if self.Movie.use3DTex:    
            xy = [-self._offsXY[0] *_magXY[0], -self._offsXY[1] *_magXY[1]]
            self.posXY = rdr.rotateTranslate(xy, _rot, [0,0])
        else:    
            self.posXY = _posXY
        self.magXY = _magXY
        self.rot = _rot
        self.trans = _trans

        if self.Sprite is not None:
            self.Sprite.position = self.posXY
            self.Sprite.scale = self.magXY[0]
            self.Sprite.rotation = self.rot
            self.Sprite.opacity = self.trans

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setSpriteBatch(self, _batch :object):
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
    def getNextFrIndex(self) -> int:
        if self.isDone or not self.isReady:
            return -1

        if self.isFirst:
            self.isFirst = False
            self.iCurrFr = self.fr0
            self.nFrReps = self.frreps - 1
            self.nSqReps = self.sqreps - 1

        else:
            if self.nFrReps > 0:
                self.nFrReps -= 1
            else:
                self.nFrReps = self.frreps - 1

                if self.isReverse:
                    self.iCurrFr -= 1
                    if self.iCurrFr < self.fr1:
                        if self.nSqReps > 0:
                            self.iCurrFr = self.fr0
                            self.nSqReps -= 1
                        else:
                            self.isDone = True
                            return -1

                else:
                    self.iCurrFr += 1
                    if self.iCurrFr > self.fr1:
                        if self.nSqReps > 0:
                            self.iCurrFr = self.fr0
                            self.nSqReps -= 1
                        else:
                            self.isDone = True
                            return -1

        if self.Sprite is not None:
            if self.Movie.use3DTex:
                self.Sprite.image = self.Movie.imgSeq.get_image_data(
                    self.iCurrFr
                )
            else:
                self.Sprite.image = self.Movie.imgSeq[self.iCurrFr]
            # *****************
            # *****************
            # TODO: see Movie.load()
            # *****************
            # *****************

        return self.iCurrFr

# ---------------------------------------------------------------------
