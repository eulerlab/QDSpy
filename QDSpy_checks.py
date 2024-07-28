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
from pyglet.canvas.xlib import NoSuchDisplayException

PLATFORM_WINDOWS = sys.platform == "win32"

if not PLATFORM_WINDOWS:
    # Check if screens exist under Linux
    try: 
        import pyglet.gl as GL  
    except NoSuchDisplayException:
        print("FATAL ERROR: No dislay devices detected")
        sys.exit()

# ---------------------------------------------------------------------