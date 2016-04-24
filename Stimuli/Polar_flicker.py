# -*- coding: utf-8 -*-
"""
Created on April 19th 2016 @author: Luke Edward Rogerson, AG Euler
"""
import collections
from functools import partial
import matplotlib.pyplot as plt
import numpy as np
import QDS
import seaborn as sns

p = {'_sName'          : "Polar_flicker_0",
     '_sDescr'         : "Noise flicker distributed over a polar grid",
     'rng_seed'        : 1,
     'frameRate'       : 60,
     'duration'        : 20,
     'radius_max'      : 200,
     'radius_itx'      : 6, #2,
     'azimuth_max'     : 2*np.pi, 
     'azimuth_itx'     : 18, #3
     'iFull'           : 255,
}

def buildStimulus(p):
    radius = np.linspace(0,p['radius_max'],p['radius_itx']+1)
    azimuth = np.linspace(0,p['azimuth_max'],p['azimuth_itx']+1)    
    rad_to_degree = lambda rad: rad*180/np.pi
    np.random.seed(seed=p['rng_seed'])
    
    domain = []
    for a in range(p['radius_itx']): 
        for b in range(p['azimuth_itx']):
            domain.append((radius[a]+1,
                           radius[a+1],
                           rad_to_degree(azimuth[b]),
                           rad_to_degree(azimuth[b+1] -azimuth[b]) -1))
    
    p['domain'] = domain
    p['rand_streams'] = np.random.rand(len(domain),p['duration']*p['frameRate'])
 
    for itx in range(len(domain)):
        QDS.DefObj_Sector(itx,domain[itx][1],domain[itx][0],domain[itx][2],domain[itx][3])
        print(itx,domain[itx][1],domain[itx][0],domain[itx][2],domain[itx][3])
         
def iterateStimulus(p):
    for t_pnt in range(p['rand_streams'].shape[1]):
        IND,RGB,POS,MAG,ANG = [],[],[],[],[]
        for itx in range(len(p['domain'])):
            IND.append(itx,)     
            RGB.append(3*(int(p['rand_streams'][itx,t_pnt]*p['iFull']),))
            POS.append((0,0),)
            MAG.append((1,1),)
            ANG.append(0,)
            QDS.SetObjColor(itx,[IND[itx]],[RGB[itx]])

        QDS.Scene_RenderEx(1/p["frameRate"],IND,POS,MAG,ANG,0)

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