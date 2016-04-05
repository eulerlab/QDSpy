#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
import collections
from functools import partial
import QDS

# Define global stimulus parameters
p = {'_sName'          : 'RGC_BG_3s',
     '_sDescr'         : "'B/G' in fingerprinting stimulus set",
     'nTrials'         : 3, 
     'dxStim_um'       : 1000,   # Stimulus size
     'durFr_s'         : 1/60.0, # Frame duration
     'nFrPerMarker'    : 3,
     'RGB_green'       : (0,255,0),
     'RGB_blue'        : (0,0,255)}
     
def buildStimulus(p):
    # Do some calculations
    p['durMarker_s']    = p['durFr_s'] *p['nFrPerMarker']
    
    # Define stimulus objects
    QDS.DefObj_Ellipse(1, p['dxStim_um'], p['dxStim_um'])
        
def iterateStimulus(p):
    # Generate stimulus by iterating over function calls
    for iT in range(p['nTrials']):
      QDS.SetObjColor (1, [1], [p['RGB_green']])
      QDS.Scene_Render(p['durMarker_s'], 1, [1], [(0,0)], 1)
      QDS.Scene_Render(3.0 -p['durMarker_s'], 1, [1], [(0,0)], 0)
      QDS.Scene_Clear(3.0, 0)
    
      QDS.SetObjColor (1, [1], [p['RGB_blue']])
      QDS.Scene_Render(p['durMarker_s'], 1, [1], [(0,0)], 1)
      QDS.Scene_Render(3.0-p['durMarker_s'], 1, [1], [(0,0)], 0)
      QDS.Scene_Clear(3.0, 0)

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