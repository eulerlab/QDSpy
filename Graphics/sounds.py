#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Classes for sounds in QDSpy

Copyright (c) 2024 Thomas Euler
All rights reserved.

2022-08-06 - First version
"""
# ---------------------------------------------------------------------
__author__ = "code@eulerlab.de"

import time
import pygame
from pathlib import Path 
from enum import Enum

class Sounds(Enum):
    OK = 0
    ERROR = -1
    STIM_START = 1
    STIM_END = 2

# ---------------------------------------------------------------------
# Sound-related functions
# ---------------------------------------------------------------------
class SoundPlayer():
    """ Play predefined audio signals 
    """
    def __init__(self):
        self._sounds = {}
        pygame.mixer.init()
        self._ready = True
        self.setVol(0.1)

    def __del__(self):
        self._sounds = None
        if self._ready:
            pygame.mixer.music.unload()

    def add(self, id, fname):    
        if id in Sounds:
            sndfile = Path(fname)
            if sndfile.is_file():
                self._sounds.update({id: fname})

    def play(self, id):
        try:
            pygame.mixer.music.load(self._sounds[id])
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.02)

        except KeyError:
            pass

    def setVol(self, vol):
        vol = min(max(0, vol), 1)
        pygame.mixer.music.set_volume(vol)


# ---------------------------------------------------------------------
