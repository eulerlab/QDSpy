#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QDSpy module - GLSL shader related class

'ShaderManager'
  Class to manage available user-defined shaders
  This class is a graphics API independent.

Copyright (c) 2013-2016 Thomas Euler
All rights reserved.
"""
# ---------------------------------------------------------------------
__author__ 	= "code@eulerlab.de"

import os
import QDSpy_stim_support as ssp
import QDSpy_global as glo
from   Graphics.shader_opengl import Shader

# ---------------------------------------------------------------------  
class ShaderFileCmd:
  ShaderName          = "shadername"
  ShaderParamNames    = "shaderparamnames"
  ShaderParamLengths  = "shaderparamlengths"
  ShaderParamDefaults = "shaderparamdefaults"  
  ShaderVertexStart   = "shadervertexstart"
  ShaderVertexEnd     = "shadervertexend"
  ShaderFragmentStart = "shaderfragmentstart"
  ShaderFragmentEnd   = "shaderfragmentend"

# ---------------------------------------------------------------------
# Shader manager class
# ---------------------------------------------------------------------
class ShaderManager:
  def __init__(self, _Conf):
    # Initializing
    #
    self.Conf       = _Conf
    self.ShFileList = []
    self.ShDesc     = []
    self.ShTypes    = []
    self.ShVertCode = []
    self.ShFragCode = []
    
    # Make a list of the available shader files ...
    #
    f = []
    for (dirpath, dirnames, filenames) in os.walk(self.Conf.pathShader):
      f.extend(filenames)
      break
    for fName in f:
      if (os.path.splitext(fName)[1]).lower() == glo.QDSpy_shaderFileExt:
        self.ShFileList.append(os.path.join(self.Conf.pathShader, fName))
    
    # Parse each shader file ...
    #    
    isInVert = False    
    isInFrag = False
    
    for fName in self.ShFileList:
      shName    = ""
      shPara    = []
      shParaLen = []
      shParaDef = []
      strShVert = []
      strShFrag = []
      
      with open(fName, 'r') as fRef:
        for line in fRef:
          pos = line.lower().find(glo.QDSpy_shaderFileCmdTok)
          if pos >= 0:
            # QDS command token found, get parameters into a list ...
            #
            tmp = (line[pos+len(glo.QDSpy_shaderFileCmdTok):]).strip().split("=")
            cmd = [tmp[0].strip()]
            if len(tmp) > 1:
              tmp = tmp[1].split(";")
              for par in tmp:
                cmd.append(par.strip())
 
            # Interpret command ...
            #   
            if   cmd[0].lower() == ShaderFileCmd.ShaderName:
              shName    = cmd[1] 
            elif cmd[0].lower() == ShaderFileCmd.ShaderParamNames: 
              shPara    = cmd[1:] 
            elif cmd[0].lower() == ShaderFileCmd.ShaderParamLengths: 
              for tmp in cmd[1:]:
                shParaLen.append(int(tmp))
            elif cmd[0].lower() == ShaderFileCmd.ShaderParamDefaults: 
              shParaDef = cmd[1:]
            elif cmd[0].lower() == ShaderFileCmd.ShaderVertexStart: 
              isInVert  = True
            elif cmd[0].lower() == ShaderFileCmd.ShaderVertexEnd: 
              isInVert  = False
            elif cmd[0].lower() == ShaderFileCmd.ShaderFragmentStart: 
              isInFrag  = True
            elif cmd[0].lower() == ShaderFileCmd.ShaderFragmentEnd: 
              isInFrag  = False
            
          else:
            if isInVert:
              strShVert.append(line)
            elif isInFrag:
              strShFrag.append(line)
            
      # Close file and append shader description and code to the lists
      #      
      fRef.close()
      self.ShDesc.append([shName, shPara, shParaLen, shParaDef])
      self.ShVertCode.append(strShVert)
      self.ShFragCode.append(strShFrag)
      self.ShTypes.append(shName)
    
    ssp.Log.write("{0:8}".format(
                  " WARNING" if len(self.ShTypes) == 0 else " "), 
                  "{0} shader type(s) found".format(len(self.ShTypes)))

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def getShaderTypes(self):
    # Returns list of loaded shader types
    #
    return self.ShTypes

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def getShaderTypeIndex(self, _shType):
    # Returns index of shader type
    #
    try:
      return self.ShTypes.index(_shType)
    except ValueError:
      return -1

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def getDefaultParams(self, _shType):
    # Returns list of default parameter vales for the shader type
    #
    res    = []  
    try:
      iShD = self.ShTypes.index(_shType)
      for i, par in enumerate(self.ShDesc[iShD][3]):
        if self.ShDesc[iShD][2][i] == 1:
          # Is singular value
          #
          res.append(float(par))
        
        else:
          # Multiple values, add as tuple
          #
          tmp = par.strip("()").split(",")        
          sub = []
          for elem in tmp:
            sub.append(float(elem))
          res.append(tuple(sub))
    except ValueError:
      pass
    
    return res      

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def createShader(self, _shType):
    # Load a pair of vertex and fragment shader from the standard
    # folder, create a shader program, compile and link the shader
    # code and return reference
    #
    shader   = None
    try:
      iShD   = self.ShTypes.index(_shType)
      shader = Shader(self.ShVertCode[iShD], self.ShFragCode[iShD])       
    except ValueError:
      pass
    
    if shader.nErrors > 0:
      ssp.Log.write("ERROR", "Creating shader(s) failed:")
      for msg in shader.errStrs:
        ssp.Log.write(" ", msg)
      return None

    return shader

# ---------------------------------------------------------------------
