import time
import Devices.lightcrafter_230np as _lcr

lcr = _lcr.Lightcrafter(_initGPIO=True)

# Connect ...
res = lcr.connect(_bus=None)

if res[0] == _lcr.ERROR.OK:
    try:
        # Get LED status ...
        res = lcr.getLEDEnabled()
        res = lcr.getLEDCurrents()
        time.sleep(1.0)

        # Set LED currents t0 20 %
        res = lcr.setLEDCurrents([0.2, 0.2, 0.2])
        res = lcr.getLEDCurrents()
        time.sleep(1.0)

        # Setting input source to parallel from RPi ...
        res = lcr.setInputSource(_lcr.SourceSel.Parallel)
        time.sleep(1.0)

    except _lcr.LCException as excp:
        s = _lcr.ErrorStr[excp.value]
        print(f"Exception `{s}` ocurred")

# Disconnect ...
lcr.disconnect()