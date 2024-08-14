#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QDSpy module - Support for logging

'Log'
  Class that allows program-wide flexible logging. Only one instance that
  is defined in this module. Writes log messages to stdout and/or sends
  messages via a pipe to the GUI process.

Copyright (c) 2013-2024 Thomas Euler
All rights reserved.

2021-10-15 - Account for LINUX console text coloring
2024-08-04 - `Log` moved into own module
2024-08-10 - Switched to `colorama` for console colors
           - Cleaned up
"""
# ---------------------------------------------------------------------
__author__ = "code@eulerlab.de"

import sys
import datetime
from colorama import Fore, Style
import Libraries.multiprocess_helper as mpr
import QDSpy_global as glo

# ---------------------------------------------------------------------
Msg_Prior_DEBUG = -1
Msg_Prior_None = 0
Msg_Prior_Asterisk = 1
Msg_Prior_Ok = 2
Msg_Prior_WARNING = 3
Msg_Prior_ERROR = 4
Msg_Prior_DATA = 5

# ---------------------------------------------------------------------
# Log class
# ---------------------------------------------------------------------
class Log:
    def __init__(self):
        # Initializing
        self.isRunFromGUI = False
        self.Sync = None
        self.stdFCol = Fore.WHITE
        self.noMsgToStdOut = not glo.QDSpy_workerMsgsToStdOut

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    '''
    def setGUISync(self, _Sync):
        # Define a synchronisation object to relay messages to the GUI
        if _Sync is not None:
            self.isRunFromGUI = True
            self.Sync = _Sync
            self.noMsgToStdOut = cfg.getParsedArgv().gui
    '''
    def setGUISync(self, _Sync, noStdOut=False):
        # Define a synchronisation object to relay messages to the GUI
        if _Sync is not None:
            self.isRunFromGUI = True
            self.Sync = _Sync
            self.noMsgToStdOut = noStdOut

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def write(self, _headerStr, _msgStr, _isProgress=False, _getStr=False, 
              _isWorker=True):
        # Log a message
        if (_headerStr.upper() == "DEBUG") and not glo.QDSpy_isDebug:
            return

        _msgStr = f"{'|' if _isWorker else ' '} {_msgStr}"
        if glo.QDSpy_doLogTimeStamps:
            # Generate a time stamp
            tStr = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        else:
            tStr = ""

        # Determine message status/priority
        if _headerStr.upper() == "DEBUG":
            msgPrior = Msg_Prior_DEBUG
            msgAttr = Fore.CYAN +Style.DIM
            msgCol = "darkCyan"
        elif _headerStr.upper() == "WARNING":
            msgPrior = Msg_Prior_WARNING
            msgAttr = Fore.YELLOW +Style.DIM
            msgCol = "#C76300"
        elif _headerStr.upper() == "ERROR":
            msgPrior = Msg_Prior_ERROR
            msgAttr = Fore.RED +Style.BRIGHT
            msgCol = "lightRed"
        elif _headerStr.upper() == "OK":
            msgPrior = Msg_Prior_Ok
            msgAttr = Fore.GREEN
            msgCol = "darkGreen"
        elif _headerStr.upper() == "***":
            msgPrior = Msg_Prior_Asterisk
            msgAttr = Fore.YELLOW
            msgCol = "yellow"
        elif _headerStr.upper() == "DATA":
            msgPrior = Msg_Prior_DATA
            msgAttr = Fore.MAGENTA
            msgCol = "darkMagenta"
        else:
            msgPrior = Msg_Prior_None
            msgAttr = self.stdFCol
            msgCol = "black"

        # Send message to log ...
        if not self.noMsgToStdOut:
            # ... to stdout ...
            if len(_headerStr) == 0:
                txt = f"\r{tStr}{_msgStr:70}{'' if _isProgress else '\n'}"
            else:
                txt = f"\r{tStr}{_headerStr:>8} {_msgStr}{'' if _isProgress else '\n'}"
            sys.stdout.write(msgAttr +txt +Style.RESET_ALL)
            sys.stdout.flush()

        if self.isRunFromGUI:
            # ... and via pipe to GUI
            if len(_headerStr) == 0:
                txt = f"{tStr}{_msgStr!s:70}"
            else:
                txt = f"{tStr}{_headerStr!s:>8} {_msgStr}"
            data = [mpr.PipeValType.toCli_log, tStr, txt, msgCol, msgPrior]
            if not _getStr:
                self.Sync.pipeSrv.send(data)
            else:
                return data


# ---------------------------------------------------------------------
Log = Log()

# ---------------------------------------------------------------------
