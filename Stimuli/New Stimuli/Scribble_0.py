# -*- coding: utf-8 -*-
"""
Created on April 13th 2016 @author: Luke Edward Rogerson, AG Euler

The scribble stimulus is designed to explore the range of frequencies and 
contrasts to which a cell might be sensitive. Unlike it's sister stimulus, the
Ripple, the Scribble stimulus continuously explores the parameter space. 

This provides a trajectory through parameter space which might allow the 
frequency and contrast sensitivities to be explored in more detail. The 
trajectory has several potentially valuable properties. Notably, a constant 
rate of motion, a generally smooth trajectory, and an approximately even 
sampling of parameter space. 

~~ Algorithm ~~

i.   Random points are chosen on a sphere. 
ii.  A trajectory is drawn by interpolating between these points.
iii. The sphere is projected onto a 2d plane. This is equivalent to 
     disregarding the Z-dimension in Cartesian coordinates.
iv.  The points are interpolated on the 2d plane to regularise the underlying
     rate of motion.
v.   The points are interpolated to the desired rate of motion.
vi.  The points are mapped from their arbitrary initial scales (a circle, r=1)
     to the space of their respective parameters.

~~ Notes ~~

The initial projection (sphere -> circle) is needed for the generation of the
continuous trajectories. Simply interpolating between points on a circle 
creates a large amount of central bias in both the points which are sampled and
the paths of the trajectories. Viewed from above, the random movement at a 
constant rate on a sphere has a slight bias towards edges, but this bias is
easily corrected for.

It may be possible to combine iv. and v., though it is not so straightforward
to calculate the distance between steps before the interpolation. It should
also be possible, in principle, to convert the distance correction factor to 
spherical coordinates, and perform the correction before the projection. In 
concert, this would reduce the number of interpolation operations from 3 -> 1.
This should go some way towards clarifying the contribution of the scaling
parameters.

Several factors give rise to the number of steps in the final stimulus:

~ nSteps = nPoints*p['interpRatio_1']*p['interpRatio_2']*p['gradient_ratio']

The first three factors are prespecified, while the last depends on several 
parameters. While there does not necessarily have to be a tradeoff here, it 
will take some thought to redesign the function such that the length and rate
can be prespecified.

Due to the use of cubic spline interpolation (which makes the trajectories
smooth), artefacts sometimes arise where parameters outside of the defined 
circle appear on the trajectory. One can check for this using some of the 
plotting functions provided for at the end of the script.

TODO: Provide full parameter descriptions.
TODO: Interpolation reduction.
TODO: Spherical projected-motion correction.
TODO: Parameterise length completely.
TODO: Clean up distance calculations.

"""
import collections
from functools import partial
import matplotlib.pyplot as plt
import numpy as np
import numpy.random
import QDS
import scipy as sp
import scipy.interpolate
import seaborn as sns

# Define global stimulus parameters
p = {'_sName'          : "Scribble_0",
     '_sDescr'         : "Continuously varying sine wave",
     'seed'            : 1,
     'dxStim_um'       : 100,
     'nPoints'         : 30,
     'interpRatio_1'   : 10,
     'interpRatio_2'   : 5,
     'sphere_unit'     : 1,
     'target_gradient' : 0.33,
     'contrast_max'    : 1,
     'contrast_min'    : 0,
     'contrast_rate'   : 0.5,
     'frequency_max'   : 6,
     'frequency_min'   : 1,
     'frequency_rate'  : 0.5,
     'iHalf'           : 127,
     'durFr_s'         : 1/60.0, # Frame duration
     'mode'            : '' # Set to trace to return array
}

# --------------------------------------------------------------------------
# Define equations for generating spherical coordinates
_r = lambda x,y,z: np.sqrt(np.sum(np.power([x,y,z],2)))
_theta = lambda x,y: np.arctan(y/x)
_phi = lambda z,r: np.arccos(z/r)
cartesian_to_sphere = lambda x,y,z: [_r(x,y,z),
                                     _theta(x,y),
                                     _phi(z,_r(x,y,z))]

# Define equations for generating cartesian coordinates
_x = lambda r,theta,phi: r*np.cos(theta)*np.sin(phi)
_y = lambda r,theta,phi: r*np.sin(theta)*np.sin(phi)
_z = lambda r,phi: r*np.cos(phi)
sphere_to_cartesian = lambda r,theta,phi: [_x(r,theta,phi),
                                           _y(r,theta,phi),
                                           _z(r,phi)]
# --------------------------------------------------------------------------

def buildStimulus(p):
    # Generate a set of random vectors, corresponding to cartesian coordinates
    np.random.seed(seed=p['seed'])
    theta = np.random.rand(p['nPoints'])*180
    phi = np.random.rand(p['nPoints'])*360
    
    # Interpolate between points on the sphere
    initPointSpace = np.linspace(1,p['nPoints'],p['nPoints'])
    targPointSpace = np.linspace(1,p['nPoints'],p['nPoints']*p['interpRatio_1'])
    r_interp = np.ones(p['nPoints']*p['interpRatio_1'])*p['sphere_unit'] # R assumed to be 1
    theta_interp = sp.interpolate.interp1d(initPointSpace,theta,kind='cubic')(targPointSpace)
    phi_interp = sp.interpolate.interp1d(initPointSpace,phi,kind='cubic')(targPointSpace)
    
    # Generate cartesian coordinates
    cart_coord = [sphere_to_cartesian(r_interp[itx],theta_interp[itx],phi_interp[itx]) \
                  for itx in range(p['interpRatio_1']*p['nPoints'])]
    
    # Extract x and y coordinates
    x_coord = np.array(list(zip(*cart_coord))[0])
    y_coord = np.array(list(zip(*cart_coord))[1])
    
    # Normalise vector relative to the x,y plane
    p['xy_distance_1'] = [np.sqrt(np.sum(p['frequency_rate']*(np.diff(x_coord)[itx])**2 + p['contrast_rate']*(np.diff(y_coord)[itx])**2)) \
                   for itx in range(x_coord.shape[0]-1)]
    xy_t_points = np.append([0],np.cumsum(p['xy_distance_1']))
    
    # Interpolate x,y coordinates to generate a high resolution trajectory
    t_space = np.linspace(xy_t_points[0],xy_t_points[-1],xy_t_points.shape[0]*p['interpRatio_2'])
    p['x_interp'] = sp.interpolate.interp1d(xy_t_points,x_coord,kind='cubic')(t_space)
    p['y_interp'] = sp.interpolate.interp1d(xy_t_points,y_coord,kind='cubic')(t_space)
    p['xy_distance_2'] = [np.sqrt(np.sum(p['frequency_rate']*(np.diff(p['x_interp'])[itx])**2 + p['contrast_rate']*(np.diff(p['y_interp'])[itx])**2)) \
                   for itx in range(p['x_interp'].shape[0]-1)]
    xy_t_points = np.append([0],np.cumsum(p['xy_distance_2']))                   
    
    # Smooth trajectory and reconstruct at the target gradient rate
    p['gradient_ratio'] = p['target_gradient']/np.mean(p['xy_distance_2'])
    t_space = np.linspace(xy_t_points[0],xy_t_points[-1],xy_t_points.shape[0]*p['gradient_ratio'])
    p['x_interp_2'] = sp.interpolate.interp1d(xy_t_points,p['x_interp'],kind='cubic')(t_space)
    p['y_interp_2'] = sp.interpolate.interp1d(xy_t_points,p['y_interp'],kind='cubic')(t_space)
    
    # Map x,y coordinates onto the frequency and contrast parameter space
    parameter_map = lambda value,parMax,parMin: (value+1)/2*(parMax-parMin)+parMin
    p['frequency_map'] = np.array([parameter_map(value,p['frequency_max'],p['frequency_min']) for value in p['x_interp_2']])
    p['contrast_map'] = np.array([parameter_map(value,p['contrast_max'],p['contrast_min']) for value in p['y_interp_2']])

    # Define stimulus objects
    QDS.DefObj_Ellipse(1, p["dxStim_um"], p["dxStim_um"])
    
def iterateStimulus(p):
    Intensity = np.ndarray((p['frequency_map'].shape[0],))
    for t_pnt in range(p['frequency_map'].shape[0]):
        frequency = np.log(p['frequency_map'][t_pnt])
        contrast = p['contrast_map'][t_pnt]
        Intensity[t_pnt] = np.sin(np.pi*frequency*t_pnt)*contrast*p["iHalf"]+p["iHalf"]
        if p['mode'] != 'trace':
            RGB = 3 *(int(Intensity[t_pnt]),) 
            QDS.SetObjColor(1, [1], [RGB])
            QDS.Scene_Render(p["durFr_s"], 1, [1], [(0,0)], 0)
    if p['mode'] is 'trace':
        return Intensity
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

# --------------------------------------------------------------------------
      
#grid = sns.JointGrid(x_coord, y_coord, space=0, size=6, ratio=50)
#grid.plot_joint(plt.scatter, color="g")
#grid.plot_marginals(sns.rugplot, height=1, color="g")

#grid = sns.JointGrid(p['x_interp'], p['y_interp'], space=0, size=6, ratio=50)
#grid.plot_joint(plt.scatter, color="g")
#grid.plot_marginals(sns.rugplot, height=1, color="g")

#plt.plot(p['x_interp'],p['y_interp'])
#plt.xlim(-1.5, 1.5)
#plt.ylim(-1.5, 1.5)
#plt.gca().set_aspect('equal', adjustable='box')
#plt.draw()

#grid = sns.JointGrid(p['contrast_map'], p['frequency_map'], space=0, size=6, ratio=50)
#grid.plot_joint(plt.scatter, color="g")
#grid.plot_marginals(sns.rugplot, height=1, color="g")

#plt.plot(p['contrast_map'],p['frequency_map'])
#plt.ylim(-p['frequency_min']-0.5, p['frequency_max']+0.5)
#plt.xlim(-p['contrast_min']-0.5, p['contrast_max']+0.5)
#plt.gca() 
#plt.draw()