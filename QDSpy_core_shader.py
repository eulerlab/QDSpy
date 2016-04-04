#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
#  QDSpy_core_shader.py
#
#  GLSL shader related routines - work in progress
#
#  Copyright (c) 2013-2015 Thomas Euler
#  All rights reserved.
#
# ---------------------------------------------------------------------
__author__ 	= "code@eulerlab.de"

import os
import QDSpy_stim_support as ssp
from   QDSpy_global       import *
from   Libraries.shader   import Shader
from   pyglet.gl          import *

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
      if (os.path.splitext(fName)[1]).lower() == QDSpy_shaderFileExt:
        self.ShFileList.append(self.Conf.pathShader +"\\" +fName)
    
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
          pos = line.lower().find(QDSpy_shaderFileCmdTok)
          if pos >= 0:
            # QDS command token found, get parameters into a list ...
            #
            tmp = (line[pos+len(QDSpy_shaderFileCmdTok):]).strip().split("=")
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
# Parent classes for different object classes
# ---------------------------------------------------------------------
class CommonParentGroup(pyglet.graphics.OrderedGroup):

  def __init__(self):
    self.iObj      = 0
    self.parent    = None
    self.order     = 0


class CommonShaderParentGroup(pyglet.graphics.OrderedGroup):

  def __init__(self):
    super(CommonShaderParentGroup, self).__init__(order=1, parent=CommonParent)


CommonParent       = CommonParentGroup()
CommonShaderParent = CommonShaderParentGroup()

# ---------------------------------------------------------------------
# Shader bind/unbind class
# ---------------------------------------------------------------------
class ShaderBindGroup(pyglet.graphics.Group):

  def __init__(self, _shader, _shType, _iObj, _ShMan):
    # ******************
    # ******************  
    # TODO: Ordering the shader objects does not work as expected;
    #       they stop being updated when using OrderedGroup as parent ...
    #       Need to be fixed. 
    #super(ShaderBindGroup, self).__init__(order=_iObj, parent=CommonParent)
    #super(ShaderBindGroup, self).__init__(parent=CommonParent)
    super(ShaderBindGroup, self).__init__(parent=CommonShaderParent)
    self.parent.order = _iObj    
    # ******************
    # ******************  
    
    self.t_s       = 0.0
    self.iObj      = _iObj
    self.posXY     = (0,0)
    self.shader    = _shader
    self.shType    = _shType
    self.iShType   = _ShMan.getShaderTypeIndex(_shType)
    if self.iShType >= 0:
      self.pKeys   = _ShMan.ShDesc[self.iShType][1]
      self.pSize   = _ShMan.ShDesc[self.iShType][2]
      self.pVals   = _ShMan.getDefaultParams(self.shType)
    else:
      self.pKeys   = []
      self.pSize   = []
      self.pVals   = []

  def set_params(self, _ObjPosXY, _ObjRot, _paramVals):
    self.xy        = _ObjPosXY
    self.rot       = _ObjRot
    self.pVals     = _paramVals

  def set_time(self, _t_s):
    self.t_s       = _t_s

  def set_state(self):
    glEnable(GL_TEXTURE_2D)
    self.shader.bind()
    self.shader.uniformf("time_s", self.t_s)
    self.shader.uniformf("obj_xy_rot", self.xy[0], self.xy[1], self.rot)
    for i, key in enumerate(self.pKeys):
      if   self.pSize[i] == 1:
        self.shader.uniformf(self.pKeys[i], self.pVals[i])
      elif self.pSize[i] == 2: 
        self.shader.uniformf(self.pKeys[i], self.pVals[i][0], 
                             self.pVals[i][1])
      elif self.pSize[i] == 3: 
        self.shader.uniformf(self.pKeys[i], self.pVals[i][0], 
                             self.pVals[i][1], self.pVals[i][2])
      elif self.pSize[i] == 4: 
        self.shader.uniformf(self.pKeys[i], self.pVals[i][0], 
                             self.pVals[i][1], self.pVals[i][2],
                             self.pVals[i][3])

  def unset_state(self):
    glDisable(GL_TEXTURE_2D)
    self.shader.unbind()
    
  def __cmp__(self, other):
    return cmp(self.order, other.order)

  """
  def __eq__(self, other):
    res =  (self.__class__ is other.__class__ and
            self.shader.handle == other.shader.handle and
            self.iObj == other.iObj)
    print("eq=", res, self.iObj, other.iObj)
    return res
    '''
    return (self.__class__ is other.__class__ and
            self.shader.handle == other.shader.handle and
            self.__hash__() == other.__hash__())
            # self.parent == other.parent)
    '''
  """
  """
  def __hash__(self):
    res = hash((self.iObj, self.shader.handle))
    #print(res)
    return res #hash((self.iObj, self.shader.handle))
  """
  """
  def __cmp__(self, other):
    res = cmp(self.iObj, other.iObj)
    print(res, self.iObj, other.iObj)
    return res #cmp(self.iObj, other.iObj)
  """  

# ---------------------------------------------------------------------
"""  
class TextureEnableGroup(pyglet.graphics.Group):

  def __init__(self):
    super(TextureEnableGroup, self).__init__(parent=CommonParent)
    self.iObj      = 0
    self.parent    = None

  def set_state(self):
    glEnable(GL_TEXTURE_2D)

  def unset_state(self):
    glDisable(GL_TEXTURE_2D)

TextureEnableGroupParent = TextureEnableGroup()


# ---------------------------------------------------------------------
class TextureBindGroup(pyglet.graphics.Group):

  def __init__(self, _iObj):
    super(TextureBindGroup, self).__init__(parent=TextureEnableGroupParent)
    self.iObj      = _iObj
    self.texture   = texture

  def set_state(self):
    glBindTexture(GL_TEXTURE_2D, self.texture.id)

  def __eq__(self, other):
    return (self.__class__ is other.__class__ and
            self.texture.id == other.texture.id and
            self.texture.target == other.texture.target and
            self.parent == other.parent)

  def __hash__(self):
    return hash((self.texture.id, self.texture.target))

  def __cmp__(self, other):
    return cmp(self.iObj, other.iObj)

"""
# ---------------------------------------------------------------------
class NoneGroup(pyglet.graphics.OrderedGroup):

  def __init__(self):
    super(NoneGroup, self).__init__(order=0, parent=CommonParent)
    self.iObj      = 0

  def __cmp__(self, other):
    return cmp(self.order, other.order)

# ---------------------------------------------------------------------