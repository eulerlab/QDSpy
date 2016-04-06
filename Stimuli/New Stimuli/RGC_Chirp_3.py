#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
import collections
from functools import partial
import QDS
import math 

# Define global stimulus parameters
p = {'_sName'          : "RGC_Chirp",
     '_sDescr'         : "'chirp' in fingerprinting stimulus set",
     "nTrials"         : 1, 
     "chirpDur_s"      : 8.0,    # Rising chirp phase
     "chirpMaxFreq_Hz" : 8.0,    # Peak frequency of chirp (Hz)
     "ContrastFreq_Hz" : 2.0,    # Freqency at which contrast 
                                 # is modulated
     "tSteadyOFF_s"    : 3.0,    # Light OFF at beginning ...
     "tSteadyOFF2_s"   : 2.0,    # ... and end of stimulus
     "tSteadyON_s"     : 3.0,    # Light 100% ON before and 
                                 # after chirp
     "tSteadyMID_s"    : 2.0,    # Light at 50% for steps
     "IHalf"           : 127,
     "IFull"           : 254,
     "dxStim_um"       : 1000,   # Stimulus size
     "StimType"        : 2,      # 1 = Box, 2 = Circle/
     "durFr_s"         : 1/60.0, # Frame duration
     "nFrPerMarker"    : 3}
     
def buildStimulus(p):
    '''Chirp formula is f(t) = sin( 2pi*F0 + pi*K*t^2)), where:
        F0 is Starting Frequency
        K = Acceleration (Hz / s)
        t = time (s)'''
    
    p['nPntChirp']       = int(p["chirpDur_s"] /p["durFr_s"])
    p['K_HzPerSec']      = p["chirpMaxFreq_Hz"] /p["chirpDur_s"]  # acceleration in Hz/s
    p['durMarker_s']     = p["durFr_s"]*p["nFrPerMarker"]
    p['RGB_IHalf']       = 3 *(p["IHalf"],)
    p['RGB_IFull']       = 3 *(p["IFull"],)
    
    # Define stimulus objects
    QDS.DefObj_Box(1, p["dxStim_um"], p["dxStim_um"], 0)
    QDS.DefObj_Ellipse(2, p["dxStim_um"], p["dxStim_um"])

def iterateStimulus(p):
    for iL in range(p["nTrials"]):
      # Steady steps
      QDS.Scene_Clear(p['durMarker_s'], 1)
      QDS.Scene_Clear(p["tSteadyOFF2_s"] -p['durMarker_s'], 0)
    
      QDS.SetObjColor(1, [p["StimType"]], [p['RGB_IFull']])
      QDS.Scene_Render(p["tSteadyON_s"], 1, [p["StimType"]], [(0,0)], 0)
    
      QDS.Scene_Clear(p['durMarker_s'], 1)
      QDS.Scene_Clear(p["tSteadyOFF_s"] -p['durMarker_s'], 0)
    
      QDS.SetObjColor(1, [p["StimType"]], [p['RGB_IHalf']])
      QDS.Scene_Render(p["tSteadyMID_s"], 1, [p["StimType"]], [(0,0)], 0)
    
      # Frequency chirp
      for iT in range(p['nPntChirp']):
        t_s       = iT*p["durFr_s"] # in ms
        Intensity = math.sin(math.pi *p['K_HzPerSec'] *t_s**2) *p["IHalf"] +p["IHalf"]
        RGB       = 3 *(int(Intensity),)  # -> RGB tuple
        QDS.SetObjColor (1, [p["StimType"]], [RGB])
        QDS.Scene_Render(p["durFr_s"], 1, [p["StimType"]], [(0,0)], 0)
    
      # Gap between frequency chirp and contrast chirp
      QDS.SetObjColor (1, [p["StimType"]], [p['RGB_IHalf']])
      QDS.Scene_Render(p["tSteadyMID_s"], 1, [p["StimType"]], [(0,0)], 0)
    
      # Contrast chirp
      for iPnt in range(p['nPntChirp']):
        t_s       = iPnt*p["durFr_s"]
        IRamp     = int(p["IHalf"] *t_s /p["chirpDur_s"])
    
        Intensity = math.sin(2*math.pi *p["ContrastFreq_Hz"] *t_s) *IRamp +p["IHalf"]
        RGB       = 3 *(int(Intensity),)
        QDS.SetObjColor(1, [p["StimType"]], [RGB])
        QDS.Scene_Render(p["durFr_s"], 1, [p["StimType"]], [(0,0)], 0)
    
      # Gap after contrast chirp
      QDS.SetObjColor(1, [p["StimType"]], [p['RGB_IHalf']])
      QDS.Scene_Render(p["tSteadyMID_s"], 1, [p["StimType"]], [(0,0)], 0)
    
      QDS.Scene_Clear(p["tSteadyOFF_s"], 0)


# --------------------------------------------------------------------------
dispatcher = collections.OrderedDict([
    ('init', partial(QDS.Initialize,p['_sName'],p['_sDescr'])),
    ('log', partial(QDS.LogUserParameters,p)),
    ('build', partial(buildStimulus,p)),
    ('clear1', partial(QDS.Scene_Clear,1.0, 0)),
    ('start', QDS.StartScript),
    ('iter', partial(iterateStimulus,p)),
    ('clear2', partial(QDS.Scene_Clear,1.0, 0)),
    ('stop', QDS.EndScript)]                               
)

[dispatcher[process]() for process in list(dispatcher.keys())]