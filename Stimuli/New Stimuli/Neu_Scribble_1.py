# -*- coding: utf-8 -*-
"""
Created April 2016 @author: Luke Edward Rogerson, AG Euler

"""
import collections
from functools import partial
import numpy as np
import QDS
import scipy as sp
import scipy.interpolate
import seaborn as sns

p = {'_sName'          : "Scribble_0",
     '_sDescr'         : "Continuously varying sine wave",
     'rng_seed'        : 1,
     'pnt_seed'        : 500,
     'velocity'        : 0.33,
     'duration'        : 60,
     'frameRate'       : 60,
     'iHalf'           : 127,
     'contrast_max'    : 1,
     'contrast_min'    : 0,
     'frequency_max'   : 12,
     'frequency_min'   : 2,
     'dot_um'          : 100
}

def buildStimulus(p):
    # http://mathworld.wolfram.com/SpherePointPicking.html
    np.random.seed(seed=p['rng_seed'])
    theta = 2*np.pi*np.random.rand(p['pnt_seed'])
    phi = np.arccos(2*np.random.rand(p['pnt_seed'])-1)
    
    dX = np.cos(theta[1:])*np.sin(phi[1:]) - np.cos(theta[:-1])*np.sin(phi[:-1])
    dY = np.sin(theta[1:])*np.sin(phi[1:]) - np.sin(theta[:-1])*np.sin(phi[:-1])
    dT = np.cumsum(np.append(0,1/np.sqrt(dX**2 + dY**2))) # <- distance correction?
    
#    if p['velocity']*p['duration']/p['frameRate'] > dT.shape[0]: 
#        raise ValueError('Target trajectory exceeds seed trajectory')
        
    coord = np.append(np.expand_dims(theta,axis=1),np.expand_dims(phi,axis=1),axis=1)
    timepoints = np.linspace(0,p['duration'],p['duration']*p['frameRate'])
    coord_interp = sp.interpolate.interp1d(dT,coord,kind='cubic',axis=0)(timepoints)
    
    spherical_to_cartesian = lambda theta,phi: [np.cos(theta)*np.sin(phi),np.sin(theta)*np.sin(phi)]
    coord_xy = np.asarray(spherical_to_cartesian(coord_interp[:,0],coord_interp[:,1])).T
    
    coord_to_value = lambda value,parMax,parMin: (value+1)/2*(parMax-parMin)+parMin
    frequency = coord_to_value(coord_xy[:,0],p['frequency_max'],p['frequency_min'])
    contrast = coord_to_value(coord_xy[:,1],p['contrast_max'],p['contrast_min'])
    
    intensity = np.zeros((frequency.shape[0]))
    for itx in range(frequency.shape[0]):
        intensity[itx] = np.sin(2*np.pi*frequency[itx])*contrast[itx]*p['iHalf'] +p['iHalf']
    
    p['intensity'] = intensity
    # Define stimulus objects
    QDS.DefObj_Ellipse(1, p['dot_um'], p['dot_um'])
    
def iterateStimulus(p):
    for t_pnt in range(p['intensity'].shape[0]):
        RGB = 3 *(int(p['intensity'][t_pnt]),) 
        QDS.SetObjColor(1, [1], [RGB])
        QDS.Scene_Render(1/p["frameRate"], 1, [1], [(0,0)], 0)
        
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