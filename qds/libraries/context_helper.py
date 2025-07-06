#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QDSpy module - context helper 

Used to suppress output to `stderr`

Copyright (c) 2025 Thomas Euler
All rights reserved.

2025-07-06 - First version
"""
# ---------------------------------------------------------------------
__author__ = "code@eulerlab.de"

import sys
import os
from contextlib import contextmanager

# ---------------------------------------------------------------------
@contextmanager
def suppress_stderr():
    """ Temporarily suppress warning to `stderr`
    """
    stderr_fileno = sys.stderr.fileno()
    with open(os.devnull, 'w') as devnull:
        old_stderr = os.dup(stderr_fileno)
        os.dup2(devnull.fileno(), stderr_fileno)
        try:
            yield
        finally:
            os.dup2(old_stderr, stderr_fileno)
            os.close(old_stderr)

# --------------------------------------------------------------------
