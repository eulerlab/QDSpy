# -*- coding: utf-8 -*-
"""
Created on April 7th 2016 @author: Luke Edward Rogerson, AG Euler

This stimulus is intended to be a natural expansion on the chirp. While the 
chirp has several attractive properties (clearly identifies polarity, extracts
sufficient frequency and contrast sensitivities for classification), it does 
not provide a comprehensive exploration of the frequency and contrast parameter
space.

It is this latter problem which this stimulus seeks to resolve. The ripple 
stimulus presents a sequence of sine waves, each governed by two parameters,
one for frequency and another for contrast. The full parameter space is defined
by a grid of possible parameter pairs, which are explored at random. The sine 
wave is presented for a short time for each pair (approximately 3 seconds).
"""
import collections
from functools import partial
import QDS
import numpy as np
import random

# Define global stimulus parameters
p = {'_sName'          : "Ripple_0",
     '_sDescr'         : "Sine wave ripples, varying frequency and contrast",
     'seed'            : 1,
     "nTrials"         : 1, 
     "IHalf"           : 127,
     "dxStim_um"       : 1000,   # Stimulus size
     "durFr_s"         : 1/60.0, # Frame duration
     'durRipple'       : 3,
     'contrast_max'    : 1,
     'contrast_n'      : 5,
     'frequency_max'   : 8,
     'frequency_n'     : 10,
     }
     
def buildStimulus(p):
    '''Set random seed. Generate sets of contrast and frequency values. Generate
    all permutations of these sets. Shuffle the order of the permutation set.
    Create single elliptical object, for which the freqeuency is modulated.'''
       
    random.seed(p['seed'])
    contrast_values = np.linspace(p['contrast_max']/p['contrast_n'],p['contrast_max'],p['contrast_n'])
    frequency_values = np.linspace(p['frequency_max']/p['frequency_n'],p['frequency_max'],p['frequency_n'])
    p['contfreq_pairs'] = random.shuffle([(x,y) for x in frequency_values for y in contrast_values])
    
    # Define stimulus objects
    QDS.DefObj_Ellipse(1, p["dxStim_um"], p["dxStim_um"])

def iterateStimulus(p):
    '''Define function for single sine ripple, and conversion function to 
    generate RGB values. Generate timeseries for each value pair instance.
    Iterate over all value pairs, calculating the intensity change at each
    timepoint. Render the intensity change of the ellipse.'''
    
    ripple = lambda t, frequency, contrast: np.sin(np.pi*frequency*t)*contrast
    rgb = lambda intensity, iHalf: 3*(int(intensity+iHalf),)
    
    for (frequency,contrast) in p['contfreq_pairs']:
        for t_pnt in np.linspace(0,p['durRipple'],p['durRipple']/p['durFr_s']):
            RGB = [rgb(ripple(t_pnt,frequency,contrast),p['iHalf'])]
            QDS.SetObjColor(1, [p["StimType"]], [RGB])
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

# [dispatcher[process]() for process in list(dispatcher.keys())]