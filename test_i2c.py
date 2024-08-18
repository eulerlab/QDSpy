import time
import Devices.lightcrafter_230np as _lcr

lcr = _lcr.Lightcrafter(_initGPIO=True)

res = lcr.connect()
if res[0] == _lcr.ERROR.OK:
    res = lcr.setInputSource(_lcr.SourceSel.Parallel)
    time.sleep(1.0)

lcr.disconnect()