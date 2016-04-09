#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
import collections
from functools import partial
import QDS

# Define global stimulus parameters
p = {'_sName'          : "RGC_Noise",
     '_sDescr'         : "'noise' in fingerprinting stimulus set",
     'durStim_s'       : 0.200, 
     'boxDx_um'        : 40,  
     'boxDy_um'        : 40,   
     'fIntenW'         : 255, # intensity factor (pixel value(0,1) x fIntenW)
     'fNameNoise'      : 'RGC_BWNoise_official',
     'durFr_s'         : 1/60.0, # Frame duration
     'nFrPerMarker'    : 3
}
     
def buildStimulus(p):
    p['fPath']       = QDS.GetStimulusPath()
    p['durMarker_s'] = p['durFr_s'] *p['nFrPerMarker']
    
    '''Read file with M sequence'''
    try:
      f         = open(p['fPath'] +'\\' +p['fNameNoise'] +'.txt', 'r')
      iLn       = 0 
      p['Frames']    = []
        
      while 1:
        line    = f.readline()
        if not line:
          break
        parts   = line.split(',')
        if iLn == 0:
          p['nX'], p['nY'], p['nFr'] = int(parts[0]),int(parts[1]),int(parts[2])
          p['nB'] = p['nX']*p['nY']
        else:
          Frame = []
          for iB in range(1, p['nB']+1):
            r   = int(parts[iB-1]) *p['fIntenW']
            Frame.append((r,r,r))
          p['Frames'].append(Frame)
        iLn += 1
    finally:
      f.close()
    
    '''Define objects
    Create box objects, one for each field of the checkerboard, such that we
    can later just change their color to let them appear or disappear'''
    
    for iB in range(1, p['nB']+1):
      QDS.DefObj_Box(iB, p['boxDx_um'], p['boxDy_um'], 0)
    
    '''Create two lists, one with the indices of the box objects and one with
    their positions in the checkerboard; these lists later facilitate using
    the Scene_Render() command to display the checkerboard'''
    
    p['BoxIndList'],p['BoxPosList'] = [], []
    for iX in range(p['nX']):
      for iY in range(p['nY']):
        iB = 1 +iX +iY*p['nX']
        x  = iX*p['boxDx_um'] -(p['boxDx_um']*p['nX']/2)
        y  = iY*p['boxDy_um'] -(p['boxDy_um']*p['nY']/2)
        p['BoxIndList'].append(iB)
        p['BoxPosList'].append((x,y))

def iterateStimulus(p):
    for iF in range(p['nFr']):
       QDS.SetObjColor(p['nB'], p['BoxIndList'], p['Frames'][iF])
       QDS.Scene_Render(p['durMarker_s'], p['nB'], p['BoxIndList'], p['BoxPosList'], 1)
       QDS.Scene_Render(p['durStim_s'] -p['durMarker_s'], p['nB'], p['BoxIndList'], p['BoxPosList'], 0)

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
