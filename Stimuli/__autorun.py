#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ---------------------------------------------------------------------
import  QDS
import  Devices.lightcrafter as LCr

QDS.Initialize("__autorun", "")

"""
print("---")
dev     = LCr.Lightcrafter()
result  = dev.connect()
if result[0] == LCr.ERROR.OK:
  dev.getHardwareStatus()
  dev.getSystemStatus()
  dev.getMainStatus()
  dev.getVideoSignalDetectStatus()
  dev.disconnect()
else:
  print("WARNING: This script required a lightcrafter")
print("---")
"""

# Requires at least one (dummy) object
#
QDS.DefObj_Box(1, 10,10,) 

# Just clear screen
#
QDS.StartScript()

QDS.LC_setLEDCurrents([0,5,5])

QDS.SetBkgColor((0,0,0))
QDS.Scene_Clear(0.1, 0)

QDS.EndScript()

# ---------------------------------------------------------------------
