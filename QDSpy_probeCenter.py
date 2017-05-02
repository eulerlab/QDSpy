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
import pyglet.gl as GL
from math import sin, cos,pi

class ProbeCenter():
    
    def __init__(self, window, width=50, height=50, intensity=127, interval=1.0, nVertice = 100):
        self.window = window
        self.height = height
        self.width = width
        self.intensity = intensity
        self.interval = interval
        self.nVertice = nVertice
        self.vertices = self.getEllipseVertices() 
        self.shiftedVertices = self.vertices
        self.color = (128+intensity,128+intensity,128+intensity)*nVertice
        self.highIntensity = True

        pyglet.gl.glClearColor(.5,.5,.5,1)  
        
    def invertContrast(self,dt):
        self.highIntensity = not self.highIntensity
        if self.highIntensity:
            self.color = (128+self.intensity,128+self.intensity,128+self.intensity)*self.nVertice
        else:
            self.color = (128-self.intensity,128-self.intensity,128-self.intensity)*self.nVertice

    def setShiftedVertices(self,dx, dy):
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
            # Vertices are shifted off the screen to compensate the window's coordinates change
            # after a presentation of a stimulus.
            #I do the same changes to be consistent with the rest of the program
            originVertices += int(self.width/2 * cos(i*angle)- self.window.width/2), int(self.height/2 * sin(i*angle)-self.window.height/2)
        return originVertices

def probe_main(data,sync):
    for win in pyglet.app.windows:
        window = win # need to catch the window in a different way Will work only with the last window...

    probe = ProbeCenter(window,width=data[1],height=data[2],intensity=data[3])
    firstClick = True # First click is to focus the window, without ending the probe
    event_loop = pyglet.app.EventLoop()
       
    def cleanExit():        
        event_loop.exit()
        
        pyglet.clock.unschedule(checkCancel)
        pyglet.clock.unschedule(probe.invertContrast)        
        window.remove_handler("on_mouse_press",on_mouse_press)
        window.remove_handler("on_draw",on_draw)
        window.remove_handler("on_mouse_motion", on_mouse_motion)
        
        pyglet.gl.glClearColor(0,0,0,1) 
        window.clear()
        window.flip()
        window.clear()
        window.flip()
        window.set_mouse_visible(True)    
    
    def checkCancel(dt):
        if sync.Request.value in [mpr.CANCELING, mpr.TERMINATING]:
            sync.setStateSafe(mpr.CANCELING)
            cleanExit()
            
    @window.event        
    def on_mouse_press(x, y, button, modifiers):
        nonlocal firstClick
        if not firstClick:
            ssp.Log.write("DATA", "{receptiveFieldCenter: x:"+str(x)+" y:"+str(y)+"}")
            cleanExit()
        else:
            firstClick = False
     
    @window.event    
    def on_mouse_motion(x, y, dx, dy):
        probe.setShiftedVertices(x,y)
        
    @window.event
    def on_draw():
        window.clear()
        pyglet.graphics.draw(probe.nVertice, pyglet.gl.GL_POLYGON, ('v2i', probe.shiftedVertices), ('c3B', probe.color))
        
    pyglet.clock.schedule_interval(checkCancel, 0.1)
    pyglet.clock.schedule_interval(probe.invertContrast, data[4])
    window.set_mouse_visible(False)
    
    #Not exactly sure what i'm doing here with openGl but seems to fix the coordinate
    # system of the window, because renderer_opengl.py sometimes change it
    # I took the code from renderer_opengl.py
    GL.glMatrixMode(GL.GL_PROJECTION)
    GL.glLoadIdentity()
    GL.glOrtho(-window.width//2, window.width//2, 
               -window.height//2, window.height//2, -1, 1)
    GL.glMatrixMode(GL.GL_MODELVIEW)
    GL.glLoadIdentity()
    GL.glPushMatrix()
    
    event_loop.run()
    
    GL.glPopMatrix()
    
