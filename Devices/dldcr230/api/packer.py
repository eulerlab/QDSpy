import math

_packervalue = 0

def packerinit(initvalue = 0):
    global _packervalue
    _packervalue = initvalue

def setbits (newvalue, numbits, startindex):
    global _packervalue
    if (newvalue != 0):
        assert math.ceil(math.log(newvalue) / math.log(2)) <= (numbits)
    # set new value
    _packervalue = _packervalue | (newvalue<<startindex)
    return _packervalue

def getbits(numbits,startindex):
    global _packervalue
    return (_packervalue >> startindex) & (2**(numbits) - 1)

def convertfloattofixed (value, scale):
    return value * scale
    
def convertfixedtofloat (value, scale):
    return value / scale
