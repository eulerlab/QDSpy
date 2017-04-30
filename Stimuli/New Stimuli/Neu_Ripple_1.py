# -*- coding: utf-8 -*-
"""
Created on Thu Apr  7 11:32:23 2016

@author: Luke
"""
import collections
from functools import partial
import QDS
import numpy as np
import random

# Define global stimulus parameters
p = {'_sName'          : "Ripple_0",
     '_sDescr'         : "Sine wave ripple",
     'seed'            : 1,
     "nTrials"         : 1, 
     "iHalf"           : 127,
     "iFull"           : 254,
     "dxStim_um"       : 100,   # Stimulus size
     "durFr_s"         : 1/60.0, # Frame duration
     'durRipple'       : 2,
     'contrast_max'    : 0.9,
     'contrast_min'    : 0.1,
     'contrast_n'      : 5,
     'frequency_max'   : 12,
     'frequency_min'   : 2,     
     'frequency_n'     : 10,
     "tSteadyMID_s"    : 2,    # Light at 50% for steps
     }
     
def buildStimulus(p):
    '''Set random seed. Generate sets of contrast and frequency values. Generate
    all permutations of these sets. Shuffle the order of the permutation set.
    Create single elliptical object, for which the freqeuency is modulated.'''
       
    random.seed(p['seed'])
    contrast_values = np.linspace(p['contrast_min'],p['contrast_max'],p['contrast_n'])
    frequency_values = np.linspace(p['frequency_min'],p['frequency_max'],p['frequency_n'])
    p['contfreq_pairs'] = [(x,y) for x in frequency_values for y in contrast_values]
    random.shuffle(p['contfreq_pairs'])
    
    # Define stimulus objects
    QDS.DefObj_Ellipse(1, p["dxStim_um"], p["dxStim_um"])

def iterateStimulus(p):
    '''Define function for single sine ripple, and conversion function to 
    generate RGB values. Generate timeseries for each value pair instance.
    Iterate over all value pairs, calculating the intensity change at each
    timepoint. Render the intensity change of the ellipse.'''
    
    for (frequency,contrast) in p['contfreq_pairs']:
        RGB = 3 *(p["iHalf"],)
        QDS.SetObjColor (1, [1], [RGB])
        QDS.Scene_Render(p["tSteadyMID_s"], 1, [1], [(0,0)], 0)
        
        for t_pnt in range(int(p['durRipple']/p['durFr_s'])):
            Intensity = np.sin(np.pi*frequency*t_pnt)*contrast*p["iHalf"]+p["iHalf"]
            RGB = 3 *(int(Intensity),) 
            QDS.SetObjColor(1, [1], [RGB])
            QDS.Scene_Render(p["durFr_s"], 1, [1], [(0,0)], 0)
# --------------------------------------------------------------------------
dispatcher = collections.OrderedDict([
    ('init', partial(QDS.Initialize,p['_sName'],p['_sDescr'])),
    ('log', partial(QDS.LogUserParameters,p)),
    ('build', partial(buildStimulus,p)),
    ('start', QDS.StartScript),
    ('clear1', partial(QDS.Scene_Clear,1.0, 0)),
    ('iter', partial(iterateStimulus,p)),
    ('clear2', partial(QDS.Scene_Clear,1.0, 0)),
    ('stop', QDS.EndScript)]                               
)

[dispatcher[process]() for process in list(dispatcher.keys())]