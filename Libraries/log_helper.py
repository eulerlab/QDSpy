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
"""

# ---------------------------------------------------------------------
__author__ = "code@eulerlab.de"

import sys
import platform
import datetime
import Libraries.multiprocess_helper as mpr
import QDSpy_global as glo

PLATFORM_WINDOWS = platform.system() == "Windows"
if PLATFORM_WINDOWS:
    # from ctypes import windll
    import Libraries.color_console as con
else:
    import Libraries.color_console_linux as con

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
        self.stdFCol = con.get_text_attr()
        self.stdBCol = self.stdFCol & 0x0070
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
    def write(self, _headerStr, _msgStr, _isProgress=False, _getStr=False):
        # Log a message
        if (_headerStr.upper() == "DEBUG") and not glo.QDSpy_isDebug:
            return

        if glo.QDSpy_doLogTimeStamps:
            # Generate a time stamp
            tStr = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        else:
            tStr = ""

        # Determine message status/priority
        if _headerStr.upper() == "DEBUG":
            msgPrior = Msg_Prior_DEBUG
            msgAttr = con.FOREGROUND_CYAN | self.stdBCol
            msgCol = "darkBlue"
        elif _headerStr.upper() == "WARNING":
            msgPrior = Msg_Prior_WARNING
            msgAttr = con.FOREGROUND_YELLOW | con.FOREGROUND_INTENSITY | self.stdBCol
            msgCol = "#C76300"
        elif _headerStr.upper() == "ERROR":
            msgPrior = Msg_Prior_ERROR
            msgAttr = con.FOREGROUND_RED | con.FOREGROUND_INTENSITY | self.stdBCol
            msgCol = "darkRed"
        elif _headerStr.upper() == "OK":
            msgPrior = Msg_Prior_Ok
            msgAttr = con.FOREGROUND_GREEN | self.stdBCol
            msgCol = "darkGreen"
        elif _headerStr.upper() == "***":
            msgPrior = Msg_Prior_Asterisk
            msgAttr = con.FOREGROUND_CYAN | con.FOREGROUND_INTENSITY | self.stdBCol
            msgCol = "darkCyan"
        elif _headerStr.upper() == "DATA":
            msgPrior = Msg_Prior_DATA
            msgAttr = con.FOREGROUND_MAGENTA | con.FOREGROUND_INTENSITY | self.stdBCol
            msgCol = "darkMagenta"
        else:
            msgPrior = Msg_Prior_None
            msgAttr = self.stdBCol | self.stdFCol
            msgCol = "black"

        # Send message to log ...
        #
        if not self.noMsgToStdOut:
            # ... to stdout ...
            #
            con.set_text_attr(msgAttr)
            if len(_headerStr) == 0:
                sys.stdout.write(
                    "\r{0}{1:70}{2}".format(tStr, _msgStr, "" if _isProgress else "\n")
                )
            else:
                sys.stdout.write(
                    "\r{0}{1:>8} {2}{3}".format(
                        tStr, _headerStr, _msgStr, "" if _isProgress else "\n"
                    )
                )
            con.set_text_attr(self.stdBCol | self.stdFCol)
            sys.stdout.flush()

        if self.isRunFromGUI:
            # ... and via pipe to GUI
            #
            if len(_headerStr) == 0:
                txt = "{0}{1!s:70}".format(tStr, _msgStr)
            else:
                txt = "{0}{1!s:>8} {2}".format(tStr, _headerStr, _msgStr)

            data = [mpr.PipeValType.toCli_log, tStr, txt, msgCol, msgPrior]
            if not _getStr:
                self.Sync.pipeSrv.send(data)
            else:
                return data


# ---------------------------------------------------------------------
Log = Log()

# ---------------------------------------------------------------------
