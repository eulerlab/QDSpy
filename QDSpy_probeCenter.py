#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QDSpy module - program that generate and display on live the probe center

Copyright (c) 2017 Tom Boissonnet
All rights reserved.
"""
# ---------------------------------------------------------------------
import QDSpy_stim_support as ssp
import QDSpy_multiprocessing as mpr
import pyglet
import Graphics.renderer_opengl as rdr
from math import sin, cos, pi

# ---------------------------------------------------------------------
class ProbeCenter(object):
    
    def __init__(self, _View, width=50, height=50, intensity=127, interval=1.0, 
                 nVertice = 100):
        self.View = _View
        self.winWidth = self.View.winPre.width
        self.winHeight = self.View.winPre.height
        self.height = height
        self.width = width
        self.intensity = intensity
        self.interval = interval
        self.nVertice = nVertice
        self.vertices = self.getEllipseVertices() 
        self.shiftedVertices = self.vertices
        self.dxLast = 0
        self.dyLast = 0
        self.color = (128+intensity,128+intensity,128+intensity,255)*nVertice
        self.highIntensity = True
        self.View.clear(_RGB=[127,127,127])
        
    def invertContrast(self,dt):
        self.highIntensity = not self.highIntensity
        if self.highIntensity:
            self.color = (128+self.intensity,128+self.intensity,
                          128+self.intensity,255)*self.nVertice
        else:
            self.color = (128-self.intensity,128-self.intensity,
                          128-self.intensity,255)*self.nVertice

    def setShiftedVertices(self, dx, dy):
        self.dxLast = dx
        self.dyLast = dy
        newVertices = ()
        for i in range(len(self.vertices)):
            if i%2 == 0:
                newVertices += (self.vertices[i]+dx,)
            else:
                newVertices += (self.vertices[i]+dy,)
        self.shiftedVertices = newVertices
    
    def getEllipseVertices(self):
        angle = 2*pi/self.nVertice
        originVertices = ()
        for i in range(self.nVertice):
            originVertices += int(self.width/2 * cos(i*angle)),\
                              int(self.height/2 * sin(i*angle))
        return originVertices
      
    def updateEllipseVertices(self):  
        self.vertices = self.getEllipseVertices() 
        self.shiftedVertices = self.vertices
        self.setShiftedVertices(self.dxLast, self.dyLast)


# ---------------------------------------------------------------------
def probe_main(data, _Sync, _View, _Stage):
  
    Win   = _View.winPre
    Batch = _View.createBatch(_isScrOvl=False)
    probe = ProbeCenter(_View,width=data[0],height=data[1],intensity=data[2])
    """
    firstClick = True # First click is to focus the window, without ending the probe
    """
    event_loop = pyglet.app.EventLoop()
       
    
    def cleanExit():        
        event_loop.exit()
        
        pyglet.clock.unschedule(checkCancel)
        pyglet.clock.unschedule(probe.invertContrast)        
        Win.remove_handler("on_mouse_press",on_mouse_press)
        Win.remove_handler("on_draw",on_draw)
        Win.remove_handler("on_mouse_drag", on_mouse_drag)
        """
        Win.remove_handler("on_mouse_motion", on_mouse_motion)
        """
        _View.clear(_RGB=[0,0,0])
        _View.present()
        _View.winPre.set_mouse_visible(False)
    
    def checkCancel(dt):
        nonlocal probe
        # Check if GUI requests terminating the program
        #
        if _Sync.Request.value in [mpr.CANCELING, mpr.TERMINATING]:
            _Sync.setStateSafe(mpr.CANCELING)
            cleanExit()
            _Sync.setStateSafe(mpr.IDLE)
        
        # Check if probe parameters have changed and if so, change probe
        #
        if _Sync.pipeSrv.poll():
          data = _Sync.pipeSrv.recv()
          if data[0] == mpr.PipeValType.toSrv_probeParams:
              probe.width     = data[2][0] 
              probe.height    = data[2][1]
              probe.intensity = data[2][2]
              probe.updateEllipseVertices()
              pyglet.clock.unschedule(probe.invertContrast)
              pyglet.clock.schedule_interval(probe.invertContrast, data[2][3])
            
    @Win.event        
    def on_mouse_press(x, y, button, modifiers):
        """
        nonlocal firstClick
        if not firstClick:
            ssp.Log.write("DATA", "{receptiveFieldCenter: x:"+str(x)+" y:"+str(y)+"}")
            #cleanExit()
        else:
            firstClick = False
        """
        if button & pyglet.window.mouse.RIGHT:
            ssp.Log.write("DATA", "{receptiveFieldCenter: x:"+str(x)+" y:"+str(y)+"}")
            cleanExit()
            
    ''' 
    @Win.event    
    def on_mouse_motion(_x, _y, dx, dy):
        (x, y) = Batch.winCoordToStageCoord(Win, _Stage, (_x, _y))
        probe.setShiftedVertices(x, y)
    '''        

    @Win.event    
    def on_mouse_drag(_x, _y, dx, dy, buttons, modifiers):
        if buttons & pyglet.window.mouse.LEFT:
          (x, y) = Batch.winCoordToStageCoord(Win, _Stage, (_x, _y))
          probe.setShiftedVertices(x, y)
        
    @Win.event
    def on_draw():
        _View.clear(_RGB=[127,127,127])       
        Batch.replace_object_data_non_indexed([], probe.shiftedVertices, 
                                              probe.color, probe.color, 
                                              _mode=rdr.MODE_POLYGON)
        Batch.draw(_Stage, _View, False)
        
        
    pyglet.clock.schedule_interval(checkCancel, 0.1)
    pyglet.clock.schedule_interval(probe.invertContrast, data[3])
    Win.set_mouse_visible(True)    
    '''
    cursor = Win.get_system_mouse_cursor(Win.CURSOR_CROSSHAIR)
    Win.set_mouse_cursor(cursor)
    '''
    event_loop.run()

# ---------------------------------------------------------------------