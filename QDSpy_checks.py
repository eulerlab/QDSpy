#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QDSpy module - to check critical stuff while being imported

Copyright (c) 2024 Thomas Euler
All rights reserved.

2024-07-28 - First version
"""
# ---------------------------------------------------------------------
__author__ = "code@eulerlab.de"

import sys
import platform
import pyglet

PLATFORM_WINDOWS = platform.system() == "Windows"
if not PLATFORM_WINDOWS:
    # Check if screens exist under Linux
    try: 
        import pyglet.gl as GL  
    except pyglet.canvas.xlib.NoSuchDisplayException:
        print("FATAL ERROR: No dislay devices detected")
        sys.exit()

# ---------------------------------------------------------------------