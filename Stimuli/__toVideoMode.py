# -*- coding: utf-8 -*-

import Devices.lightcrafter as lcr
import time

# Generate lightcrafter object and try to connect to it
dev = lcr.Lightcrafter(_isCheckOnly=False, _logLevel=3)
res = dev.connect()
if res[0] is not lcr.ERROR.OK:
  # No connection
  exit()

# Print report and video signal status
dev.getFirmwareVersion()
dev.getHardwareStatus()
dev.getMainStatus()
dev.getSystemStatus()
dev.getVideoSignalDetectStatus()

dev.stopPatternSequence()

# Go back to normal video mode
dev.setInputSource(lcr.SourceSel.HDMI, lcr.SourcePar.Bit24)
dev.setDisplayMode(lcr.DispMode.Video)

dev.getMainStatus()
dev.getSystemStatus()

dev.disconnect()



