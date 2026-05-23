#
# Copyright Tristam Macdonald 2008.
#
# Distributed under the Boost Software License, Version 1.0
# (see http://www.boost.org/LICENSE_1_0.txt)
#
# Adapted to python3x
#

import pyglet.gl as GL
import ctypes

class Shader:
    # vert, frag and geom take arrays of source strings
    # the arrays will be concattenated into one string by OpenGL
    def __init__(self, vert = [], frag = [], geom = []):
        # create the program handle
        self.handle = GL.glCreateProgram()
        # we are not linked yet
        self.linked  = False
        self.nErrors = 0
        self.errStrs = []

        # create the vertex shader
        self.createShader(vert, GL.GL_VERTEX_SHADER)
        # create the fragment shader
        self.createShader(frag, GL.GL_FRAGMENT_SHADER)
        # the geometry shader will be the same, once pyglet supports the extension
        # self.createShader(frag, GL_GEOMETRY_SHADER_EXT)

        # attempt to link the program
        self.link()
        
    def logError(self, _msg):
        msgList = _msg.decode("utf-8").split(sep='\n')
        for ln in msgList:
          if len(ln) > 0:
            self.nErrors  += 1
            self.errStrs.append(ln)   

    def createShader(self, strings, type):
        count = len(strings)
        # if we have no source code, ignore this shader
        if count < 1:
            return
        # create the shader handle
        shader = GL.glCreateShader(type)

        # convert the source strings into a ctypes pointer-to-char array, 
        # and upload them. This is deep, dark, dangerous black magick - 
        # don't try stuff like this at home!
        """ Next line added """
        strings = [s.encode("ascii") for s in strings]
        src = (ctypes.c_char_p * count)(*strings)
        GL.glShaderSource(shader, count, 
                          ctypes.cast(ctypes.pointer(src), 
                          ctypes.POINTER(ctypes.POINTER(ctypes.c_char))), None)

        # compile the shader
        GL.glCompileShader(shader)

        temp = ctypes.c_int(0)
        # retrieve the compile status
        GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS, ctypes.byref(temp))

        # if compilation failed, print the log
        if not temp:
            # retrieve the log length
            GL.glGetShaderiv(shader, GL.GL_INFO_LOG_LENGTH, ctypes.byref(temp))
            # create a buffer for the log
            buffer = ctypes.create_string_buffer(temp.value)
            # retrieve the log text
            GL.glGetShaderInfoLog(shader, temp, None, buffer)
            # print the log to the console
            self.logError(buffer.value)
        else:
            # all is well, so attach the shader to the program
            GL.glAttachShader(self.handle, shader);

    def link(self):
        # link the program
        GL.glLinkProgram(self.handle)

        temp = ctypes.c_int(0)
        # retrieve the link status
        GL.glGetProgramiv(self.handle, GL.GL_LINK_STATUS, ctypes.byref(temp))

        # if linking failed, print the log
        if not temp:
            #   retrieve the log length
            GL.glGetProgramiv(self.handle, GL.GL_INFO_LOG_LENGTH, 
                              ctypes.byref(temp))
            # create a buffer for the log
            buffer = ctypes.create_string_buffer(temp.value)
            # retrieve the log text
            GL.glGetProgramInfoLog(self.handle, temp, None, buffer)
            # print the log to the console
            self.logError(buffer.value)
            
        else:
            # all is well, so we are linked
            self.linked = True

    def bind(self):
        # bind the program
        GL.glUseProgram(self.handle)

    def unbind(self):
        # unbind whatever program is currently bound - not necessarily this program,
        # so this should probably be a class method instead
        GL.glUseProgram(0)

    # upload a floating point uniform
    # this program must be currently bound
    def uniformf(self, name, *vals):
        # check there are 1-4 values
        if len(vals) in range(1, 5):
            # select the correct function
            { 1 : GL.glUniform1f,
              2 : GL.glUniform2f,
              3 : GL.glUniform3f,
              4 : GL.glUniform4f
              # retrieve the uniform location, and set
            }[len(vals)](GL.glGetUniformLocation(self.handle, 
                                                 name.encode("ascii")), *vals)            

    # upload an integer uniform
    # this program must be currently bound
    def uniformi(self, name, *vals):
        # check there are 1-4 values
        if len(vals) in range(1, 5):
            # select the correct function
            { 1 : GL.glUniform1i,
              2 : GL.glUniform2i,
              3 : GL.glUniform3i,
              4 : GL.glUniform4i
              # retrieve the uniform location, and set
            }[len(vals)](GL.glGetUniformLocation(self.handle, 
                                                 name.encode("ascii")), *vals)            
    # upload a uniform matrix
    # works with matrices stored as lists,
    # as well as euclid matrices
    def uniform_matrixf(self, name, mat):
        # obtian the uniform location
        loc = GL.glGetUniformLocation(self.Handle, name)
        # uplaod the 4x4 floating point matrix
        GL.glUniformMatrix4fv(loc, 1, False, (ctypes.c_float * 16)(*mat))
        