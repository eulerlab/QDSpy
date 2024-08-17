import Devices.lightcrafter_230np as lcr
dev = lcr.Lightcrafter(_initGPIO=True)
dev.connect()