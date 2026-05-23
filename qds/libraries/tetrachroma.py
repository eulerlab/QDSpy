#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
tetrachromatic stimulus API

Copyright (c) 2017-2024 Thomas Euler
All rights reserved.
"""
# ---------------------------------------------------------------------
__author__ = "code@eulerlab.de"


# ---------------------------------------------------------------------
class Tetrachroma:
    """Methods to program and sync two lightcrafters and for mapping
    tetrachromatic stimuli into RGB
    """

    def __init__(self, _bitDepths, _bitOffsets, _blackBit):
        """
        '_bitDepths' is a 4-value tuple, giving the number of bits 
        (1..8) for the respective tetrachromatic color channel r,g,b,uv.
        The bit sum must be 23 for '_blackBit'> 0 and 24 for 
        '_blackBit' == 0

        '_bitOffsets' ...

        '_blackBit' is a bit mask that indicates which bit is always 
        set to zero (may be needed for dual LCr configuration); if 0 
        then ignored.
        """
        self.bitDepths = _bitDepths
        self.bitOffsets = _bitOffsets
        self.blackBit = _blackBit

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def toRGB(self, _rgbu):
        """Converts a tetrachromatic color r,g,b,uv ("_rgbu, 0..1") 
        into a 24 bit RGB value and returns it as a 3-value tuple 
        (0..255 per gun).
        """
        newRGB = 0
        for iVal, val in enumerate(_rgbu):
            if self.bitDepths[iVal] > 0:
                depth = 2 ** self.bitDepths[iVal]
                newVal = min(depth - 1, int(val * depth))
                newRGB = newRGB | (newVal << self.bitOffsets[iVal])
                # print("0x{:06X}".format(newRGB))

        if self.blackBit > 0:
            newRGB = newRGB & ~self.blackBit

        rgb = []
        rgb.append(int(newRGB & 0x0000FF))
        rgb.append(int((newRGB & 0x00FF00) >> 8))
        rgb.append(int((newRGB & 0xFF0000) >> 16))

        # print(_rgbu, "0x{:024b}".format(newRGB), rgb)
        return (tuple(rgb), newRGB)


# ---------------------------------------------------------------------
