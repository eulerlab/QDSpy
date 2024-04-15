#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QDSpy module - interprets and presents compiled stimuli

'Presenter'
  Presents a compiled stimulus.
  This class is a graphics API independent.

Copyright (c) 2013-2023 Thomas Euler
Distributed under the terms of the GNU General Public License (GPL)

2022-08-06 - Some reformatting (partially)
"""
# ---------------------------------------------------------------------
__author__ 	= "code@eulerlab.de"

import os
import pickle

import numpy as np
import pyglet
import PIL
import QDSpy_global as glo
import QDSpy_stim as stm
import QDSpy_stim_movie as mov
import QDSpy_stim_video as vid
import QDSpy_stim_draw as drw
import QDSpy_stim_support as ssp
import QDSpy_core_support as csp
import QDSpy_core_shader as csh
import QDSpy_config as cfg
import QDSpy_multiprocessing as mpr
import Devices.digital_io as dio

global Clock
Clock  = csp.defaultClock

# ---------------------------------------------------------------------
# Adjust global parameters depending on command line arguments
#
args = cfg.getParsedArgv()

global QDSpy_verbose
QDSpy_verbose = args.verbose
if QDSpy_verbose:
  import pylab

# =====================================================================
#
# ---------------------------------------------------------------------
class Presenter:
  """ Presenter class
  """
  def __init__(self, _Stage, _IO, _Conf, _View, _View2=None, _LCr=[]):
    # Initializing
    #
    self.Stage        = _Stage
    self.IO           = _IO
    self.Conf         = _Conf
    self.View         = _View
    self.LCr          = _LCr
    self.ShManager    = csh.ShaderManager(self.Conf)
    self.reset()

    self.dtFr_meas_s  = self.Stage.dtFr_s
    self.dtFr_thres_s = self.dtFr_meas_s +self.Conf.maxDtTr_ms /1000.0

    # Prepare recording of stimulus presentation, if requested
    #
    if self.Conf.recordStim:
      self.View.prepareGrabStim()

    # Define event handler(s)
    #
    self.View.setOnKeyboardHandler(self.onKeyboard)
    self.View.setOnDrawHandler(self.onDraw)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def reset(self):
    # Reset presenter
    #
    self.Stim         = None
    self.isReady      = False
    self.nFr          = 0
    self.is1FrOfSce   = False
    self.iSc          = 0
    self.isNextSce    = True
    self.isFirstSce   = True

    self.isEnd        = False
    self.isIdle       = True
    self.isUserAbort  = False

    self.isRunFromGUI = False
    self.Sync         = None

    self.IO_portOut   = dio.devConst.NONE
    self.IO_portIn    = dio.devConst.NONE
    self.IO_maskMark  = 0
    self.IO_isMarkSet = False

    self.nFrTotal     = 0
    self.tFrRel_s     = 0.0
    self.tFrRelOff_s  = 0.0
    self.avFrDur_s    = 0.0
    self.nRendTotal   = 0
    self.avPresDur_s  = 0.0
    self.avRendDur_s  = 0.0
    self.rendDur_s    = 0.0
    self.tFr          = 0.0
    self.tStart       = 0.0

    if glo.QDSpy_frRateStatsBufferLen > 0:
      self.dataDtFr   = np.zeros(glo.QDSpy_frRateStatsBufferLen, dtype=float)
    else:
      self.dataDtFr   = []
    self.dataDtFrLen  = 0
    self.dataDtFrOver = False
    self.nDroppedFr   = 0

    self.isInLoop     = False
    self.nLoopRepeats = 0
    self.iFirstLoopSc = -1

    self.vertTr       = np.array([], dtype=int)   # temporary vertex arrays
    self.iVertTr      = np.array([], dtype=int)   # temporary index arrays
    self.vRGBTr       = np.array([], dtype=np.uint8) # temporary RGBA arrays
    self.vRGBTr2      = np.array([], dtype=np.uint8)

    self.currShObjIDs = []    # list, IDs of current shader-enabled objects
    self.prevShObjIDs = []    # list, IDs of previously shown shader-enabled
                              # objects
    self.prevObjIDs   = []    # list, previously shown objects (all)
    self.ShProgList   = []    # list, available shader programs
                              # (ready to bind)
    self.MovieList    = []    # list, movie class objects
    self.MovieCtrlList= []    # list, movie control class objects
    self.VideoList    = []    # list, video class objects
    self.VideoCtrlList= []    # list, video control class objects

    self.markerVert, self.antiMarkerVert = drw.marker2vert(self.Stage, self.Conf)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def onKeyboard(self, _key, _x, _y):
    if not(self.isRunFromGUI) and _key in glo.QDSpy_KEY_KillPresent:
      self.isUserAbort = True
      self.stop()

  # --------------------------------------------------------------------
  # Scene rendering function
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def renderSce(self, _iSc, _nSc):
    # Renders the indexed scene
    #
    if self.Conf.isTrackTime:
      t0  = Clock.getTime_s()
    sc    = self.Stim.SceList[_iSc]
    drawn = True

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    if sc[stm.SC_field_type] == stm.StimSceType.awaitTTL:
      ssp.Log.write("INFO", "Waiting for trigger ...")
      while True:
        res = self.IO.readDPort(self.IO_portIn)
        if res > 0:
          break
        if self.Sync.Request.value in [mpr.CANCELING, mpr.TERMINATING]:
          self.Sync.setStateSafe(mpr.CANCELING)
          self.isUserAbort = True
          break

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    elif sc[stm.SC_field_type] == stm.StimSceType.beginLoop:
      # Begin of a loop
      #
      self.isInLoop        = True
      self.nLoopRepeats    = sc[stm.SC_field_nLoopTrials] -1
      self.iFirstLoopSc    = _iSc +1

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    elif sc[stm.SC_field_type] == stm.StimSceType.endLoop:
      # End of a loop
      #
      if (not(self.isInLoop) or (self.nLoopRepeats < 0)):
        pass
      if self.nLoopRepeats > 0:
        self.iSc           = self.iFirstLoopSc -1
        self.nLoopRepeats -= 1
      else:
        self.isInLoop      = False

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    elif   sc[stm.SC_field_type] == stm.StimSceType.clearSce:
      # Clear scene
      #
      self.View.clear()
      if self.Stage.useScrOvl:
        drawn = False

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    elif   sc[stm.SC_field_type] == stm.StimSceType.changeBkgCol:
      # Change background color
      #
      self.View.clear(sc[stm.SC_field_BkgRGB])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    elif   sc[stm.SC_field_type] == stm.StimSceType.sendCommandToLCr:
      # Change LED currents
      #
      _params = sc[stm.SC_field_LCrParams]
      if ((_params[0] == stm.StimLCrCmd.setLEDCurrents) and
          (_params[1] >= 0) and (_params[1] < len(self.LCr))):
        self.LCr[_params[1]].setLEDCurrents(_params[2])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    elif   sc[stm.SC_field_type] == stm.StimSceType.logUserParams:
      # Write user parameters to the log file
      #
      _userParams = sc[stm.SC_field_userParams]
      _userParams.update(stimFileName=self.Stim.fileName)
      # **************************************
      # **************************************
      # TODO: Copy also external stimulus files (containing large
      #       lists or data structures) to the log directory
      # **************************************
      # **************************************
      ssp.Log.write("DATA", _userParams.__str__())

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    elif   sc[stm.SC_field_type] == stm.StimSceType.changeShParams:
      # Change shader parameters
      #
      _ShID     = sc[stm.SC_field_ShID][0]
      _iSh      = self.Stim.ShDict[_ShID]
      self.Stim.ShList[_iSh][stm.SH_field_Params] = sc[stm.SC_field_ShParams]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    elif   sc[stm.SC_field_type] == stm.StimSceType.changeObjShader:
      # Change object shader
      #
      for i in range(len(sc[stm.SC_field_IDs])):
        _ObID   = sc[stm.SC_field_IDs][i]
        _iObj   = self.Stim.ObjDict[_ObID]
        _ShID   = sc[stm.SC_field_ShIDs][i]
        if _ShID < 0:
          _iSh  = -1
        else:
          _iSh  = self.Stim.ShDict[_ShID]
        self.Stim.ObjList[_iObj][stm.SO_field_shProgIndex] = _iSh
      """
      SO_field_shProgIndex

      newSce = [StimSceType.changeObjShader, -1, self.nSce, False,
                _IDs, _shIDs]
      SC_field_IDs          = 4
      SC_field_ShIDs        = 5

      #self.currIVShObjGr[0] = shd.ShaderBindGroup(shd.getStandardShader(), 0)
      #self.currIVShObjGr[2] = shd.ShaderBindGroup(shd.getStandardShader(), 2)

      newShader = [StimObjType.shader, _shID,
                   _shType, csh.SH_defaultParams[_shType], _shCode]
      self.ShDict[_shID] = len(self.ShList)
      self.ShList.append(newShader)
      self.ShProgList

      SH_field_type         = 0
      SH_field_ID           = 1
      SH_field_shaderType   = 2
      SH_field_Params       = 3
      SH_field_shaderCode   = 4

      newBox    = [StimObjType.box, _ID,
                   (float(_dx_um), float(_dy_um)),
	    		  SO_defaultFgRGB, SO_defaultAlpha, SO_default_RGBAByVert,
                   _enShader, -1]
      """
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    elif   sc[stm.SC_field_type] == stm.StimSceType.startMovie:
      # Start running movie ...
      #
      # Get movie object via movie ID
      #
      _MovID = sc[stm.SC_field_IDs][0]
      _iMov  = self.Stim.MovDict[_MovID]
      movOb  = self.MovieList[_iMov]

      # Create a new movie control object; this internally creates a
      # pyglet sprite, with the requested presentation properties
      #
      mCtOb  = mov.MovieCtrl(sc[stm.SC_field_MovSeq], _MovID, _Movie=movOb)
      mCtOb.iScr = sc[stm.SC_field_MovScreen]
      mCtOb.setSpriteProperties(sc[stm.SC_field_posXY],
                                sc[stm.SC_field_magXY],
                                sc[stm.SC_field_rot],
                                sc[stm.SC_field_MovTrans])

      # Add the move control object to the list of active movies; remove
      # previous one, if still present
      #
      iMC = 0
      while iMC < len(self.MovieCtrlList):
        if self.MovieCtrlList[iMC][3] == _MovID:
          temp = self.MovieCtrlList.pop(iMC)
          temp[0].kill()
        else:
          iMC += 1

      self.MovieCtrlList.append([mCtOb, _iSc, self.nFrTotal, _MovID])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    elif   sc[stm.SC_field_type] == stm.StimSceType.startVideo:
      # Start running video ...
      #
      # Get video object via video ID
      #
      _VidID = sc[stm.SC_field_IDs][0]
      _iVid  = self.Stim.VidDict[_VidID]
      vidOb  = self.VideoList[_iVid]

      # Create a new movie control object; this internally creates a
      # pyglet sprite, with the requested presentation properties
      #
      vCtOb  = vid.VideoCtrl(_Video=vidOb)
      vCtOb.iScr = sc[stm.SC_field_VidScreen]
      vCtOb.setSpriteProperties(sc[stm.SC_field_posXY],
                                sc[stm.SC_field_magXY],
                                sc[stm.SC_field_rot],
                                sc[stm.SC_field_VidTrans])

      # Add the video control object to the list of active videos; remove
      # previous one, if still present
      #
      iVC = 0
      while iVC < len(self.VideoCtrlList):
        if self.VideoCtrlList[iVC][3] == _VidID:
          temp = self.VideoCtrlList.pop(iVC)
          temp[0].kill()
        else:
          iVC += 1

      self.VideoCtrlList.append([vCtOb, _iSc, self.nFrTotal, _VidID])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    elif sc[stm.SC_field_type] == stm.StimSceType.renderSce:
      # Render objects in scene
      #
      self.View.clear()

      if self.Stim.cScOList[_iSc][0] >= 0:

        if self.is1FrOfSce: # _________________________________________
          # First frame of a new scene: Get index of object drawing list of
          # this scene and then get vertex data (or reuse previous data, if
          # nothing has changed)
          #
          iODr, ObjNewMask, ObjIDs, ObjPosXY, ObjRot = self.Stim.cScOList[_iSc]
          nObjs = len(self.Stim.cODr_tr_iVert[iODr])
          ObjNewMask = np.array(ObjNewMask)

          # Generate pyglet Groups to bind shaders to objects, if required
          #
          self.Batch.delete_shader_handles()

          for iObj, ObjID in enumerate(ObjIDs):
            if ObjID < 0:
              continue
            iObjList  = self.Stim.ObjDict[ObjID]
            iSh       = self.Stim.ObjList[iObjList][stm.SO_field_shProgIndex]
            if iSh >= 0:
              # Create Group object referencing to requested shader and set
              # shader parameters (uniforms)
              #
              shPar   = self.Stim.ShList[iSh][stm.SH_field_Params]
              shType  = self.Stim.ShList[iSh][stm.SH_field_shaderType]
              self.Batch.add_shader_handle(ObjID, self.ShProgList[iSh], shType)
              x       = ObjPosXY[iObj][0] +self.Stage.dxScr
              y       = ObjPosXY[iObj][1] +self.Stage.dyScr
              a_rad   = (ObjRot[iObj]+90.0)*np.pi/180.0
              self.tFrRelOff_s = self.tFrRel_s
              self.Batch.set_shader_time(ObjID, 0.0)
              self.Batch.set_shader_parameters(ObjID, [x,y], a_rad, shPar)

            else:
              # No shader
              #
              self.Batch.add_shader_handle(ObjID)

          # Check if vertex list(s) need(s) to be updated or re-created
          #
          # self.Stim.cODr_tr_xxx[iODr][iObj][0] := SC_vertDataChanged or not
          # self.Stim.cODr_tr_xxx[iODr][iObj][1] := Object ID or -1
          # self.Stim.cODr_tr_xxx[iODr][iObj][2] := numpy array with data
          #
          # Kill vertex data of previous shader-enabled objects
          #
          self.currShObjIDs = []
          self.Batch.delete_shader_object_data()

          for iObj in range(nObjs):
            self.iVertTr  = self.Stim.cODr_tr_iVert[iODr][iObj][2]
            self.vertTr   = self.Stim.cODr_tr_vertCoord[iODr][iObj][2]
            self.vRGBATr  = self.Stim.cODr_tr_vertRGBA[iODr][iObj][2]
            self.vRGBATr2 = self.Stim.cODr_tr_vertRGBA2[iODr][iObj][2]

            if iObj == 0:
              # Not shader-enabled objects ...
              #
              if ObjNewMask[iObj] == stm.SC_ObjNewAll:
                self.Batch.replace_object_data(self.iVertTr, self.vertTr,
                                               self.vRGBATr, self.vRGBATr2)
              else:
                if (ObjNewMask[iObj] & stm.SC_ObjNewiVer) > 0:
                  self.Batch.replace_object_data_indices(self.iVertTr)
                if (ObjNewMask[iObj] & stm.SC_ObjNewVer) > 0:
                  self.Batch.replace_object_data_vertices(self.vertTr)
                if (ObjNewMask[iObj] & stm.SC_ObjNewRGBA) > 0:
                  self.Batch.replace_object_data_colors(self.vRGBATr,
                                                        self.vRGBATr2)

            else:
              # For each shader-enabled object ...
              #
              self.currShObjIDs.append(ObjIDs[iObj])
              self.Batch.add_shader_object_data(ObjIDs[iObj], self.iVertTr,
                                                self.vertTr, self.vRGBATr,
                                                self.vRGBATr2)

          self.prevShObjIDs = self.currShObjIDs
          self.prevObjIDs   = ObjIDs

        else: # ______________________________________________________
          # Not first frame of a new scene, just update the shader
          # parameters, if any, ...
          #
          self.Batch.set_shader_time_all(self.tFrRel_s -self.tFrRelOff_s)

        # Indicate that the batch needs to be drawn
        #
        drawn = False


    if (_nSc > 0) and (not drawn\
       or (len(self.MovieCtrlList) > 0) or (len(self.VideoCtrlList) > 0)):
      # Keep movie control objects updated: Advance or kill, if finished
      #
      iMC = 0
      while iMC < len(self.MovieCtrlList):
        mCtOb, iScWhenStarted, iFrWhenStarted, ID = self.MovieCtrlList[iMC]
        if iScWhenStarted == _iSc:
          # Don't start playing the movie if we are still in the no-duration
          # scene that started the movie
          #
          '''
          ssp.Log.write("DEBUG", "Movie #{0} ID{1} ready, _iSc={2} iFr={3}"
                      .format(iMC, mCtOb.ID, _iSc, self.nFrTotal))
          '''
          iMC += 1
          continue

        res = mCtOb.getNextFrIndex()
        if res < 0:
          '''
          ssp.Log.write("DEBUG", "Movie #{0} ID{1} last,  _iSc={1} nFr={2}"
                        .format(iMC, mCtOb.ID, _iSc, self.nFrTotal -iFrWhenStarted))
          '''
          mCtOb, iScWhenStarted, iFrWhenStarted, ID = self.MovieCtrlList.pop(iMC)
          mCtOb.kill()

        else:
          mCtOb.setSpriteBatch(self.Batch)
          iMC += 1

      # Keep video control objects updated: Advance or kill, if finished
      #
      iVC = 0
      while iVC < len(self.VideoCtrlList):
        vCtOb, iScWhenStarted, iFrWhenStarted, ID = self.VideoCtrlList[iVC]
        if iScWhenStarted == _iSc:
          # Don't start playing the video if we are still in the no-duration
          # scene that started the video
          #
          iVC += 1
          continue

        res = vCtOb.getNextFrIndex()
        if res < 0:
          vCtOb, iScWhenStarted, iFrWhenStarted, ID = self.VideoCtrlList.pop(iVC)
          vCtOb.kill()

        else:
          vCtOb.setSpriteBatch(self.Batch)
          iVC += 1

      # Draw current triangle vertices, acknowledging the scaling and
      # rotation of the current display (stage settings)
      #
      self.Batch.draw(self.Stage, self.View,
                      sc[stm.SC_field_type] == stm.StimSceType.clearSce)

    # Show marker, if requested and present in the current scene
    #
    if self.Conf.markShowOnScr:
      if sc[stm.SC_field_marker]:
        self.Batch.add_rect_data(self.markerVert)
      else:
        self.Batch.add_rect_data(self.antiMarkerVert)

    # Track rendering timing, if requested
    #
    if self.Conf.isTrackTime:
      self.rendDur_s     = Clock.getTime_s() -t0
      self.avRendDur_s  += self.rendDur_s
    self.nRendTotal     += 1


  # --------------------------------------------------------------------
  # Frame refresh handler
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def onDraw(self):
    # Check if stimulus is defined
    #
    if self.Stim == None:
      self.View.clear()
      self.isEnd = True

      if self.isIdle:
        # Stimulus has already ended; nothing to do ...
        #
        ssp.Log.write("DEBUG", "Presenter.onDraw(), isIdle=True")
        self.finish()
        return

    # If run from GUI (as server) ...
    #
    if self.isRunFromGUI:
      # Check if GUI requests abort ...
      #
      if self.Sync.Request.value in [mpr.CANCELING, mpr.TERMINATING]:
        self.Sync.setStateSafe(mpr.CANCELING)
        self.isUserAbort = True
        self.stop()

      if self.Sync.pipeSrv.poll():
         data = self.Sync.pipeSrv.recv()
         if data[0] == mpr.PipeValType.toSrv_changedStage:
           # Stage properties were adjusted by the user, reflect
           # immediately in the stimulus presentation
           #
           self.Stage.scalX_umPerPix = data[1]["scalX_umPerPix"]
           self.Stage.scalY_umPerPix = data[1]["scalY_umPerPix"]
           self.Stage.centOffX_pix = data[1]["centOffX_pix"]
           self.Stage.centOffY_pix = data[1]["centOffY_pix"]
           self.Stage.rot_angle = data[1]["rot_angle"]
           self.Stage.dxScr12 = data[1]["dxScr12"]
           self.Stage.dyScr12 = data[1]["dyScr12"]
           self.Stage.offXScr1_pix = data[1]["offXScr1_pix"]
           self.Stage.offYScr1_pix = data[1]["offYScr1_pix"]
           self.Stage.offXScr2_pix = data[1]["offXScr2_pix"]
           self.Stage.offYScr2_pix = data[1]["offYScr2_pix"]

         if data[0] == mpr.PipeValType.toSrv_changedLEDs:
           # User changed LED currents and/or toggled LEDs, notify
           # lightcrafter immediately
           #
           self.Stage.LEDs = data[1][0]
           self.Stage.isLEDSeqEnabled = data[1][1]
           self.Stage.sendLEDChangesToLCr(self.Conf)

         if data[0] == mpr.PipeValType.toSrv_setIODevPins:
           # User pressed a user button, change IO device pins accordingly
           #
           csp.setIODevicePin(
              self.IO, data[1][0], data[1][1], data[1][2]
             )

    # Render scene
    #
    while self.isNextSce and not self.isEnd:
      # Load next scene ...
      #
      if not self.isFirstSce:
        # Increase scene index and check for end of stimulus ...
        #
        self.iSc += 1
        self.isEnd = self.iSc >= len(self.Stim.SceList)
        if self.isEnd:
          break

      else:
        #	... except it is the first scene
        #
        self.isFirstSce = False
        self.tStart = Clock.getTime_s()

      self.nFr = self.Stim.cScDurList[self.iSc]
      self.is1FrOfSce = True
      if self.nFr <= 0:
        # Scene w/o duration, handle immediately
        #
        self.renderSce(self.iSc, self.nFr)
        self.isNextSce = True

      else:
        # Scene has a duration, handle it below
        #
        self.isNextSce = False

    if self.isEnd:
      # No more scenes to display or aborted by used, in any case,
      # end presentation
      #
      isDone = (self.iSc >= len(self.Stim.SceList))
      ssp.Log.write("ok", "Done" if isDone else "Aborted by user")
      ssp.Log.write(
          "DATA", {"stimFileName": self.Stim.fileName,
          "stimState": "FINISHED" if isDone else "ABORTED"}.__str__()
        )
      self.Stim = None
      self.isIdle = True
      return

    if self.nFr > 0:
      # Scene has a duration, handle it ...
      #
      self.renderSce(self.iSc, self.nFr)
      self.nFr -= 1
      self.is1FrOfSce = False
      self.isNextSce = (self.nFr == 0)

      # Determine if marker should be shown ...
      # ************
      # TODO: first read port to be able to set/clear only the needed
      #       pin
      # ************
      isMaskChanged = False
      if self.IO is not None:
        if self.Stim.cScMarkList[self.iSc] > 0:
          # ...
          maskMark = self.IO_maskMark
          isMaskChanged = True
          self.IO_isMarkSet = True
        else:
          if self.IO_isMarkSet:
            # ...
            maskMark = 0
            isMaskChanged = True
            self.IO_isMarkSet = False

      # Flip display buffer ...
      #
      t1 = Clock.getTime_s()
      self.View.present()
      self.avPresDur_s += Clock.getTime_s() -t1

      # Send marker signal, if needed
      #
      if isMaskChanged:
        self.IO.writeDPort(self.IO_portOut, maskMark)

      # Record stimulus presentation, if requested
      #
      if self.recordStim:
        if self.nFrTotal % self.Conf.rec_f_downsample_t == 0:
          stimframe = self.View.grabStimFrame()
          self.recordedStim.append(stimframe)

    # Keep track of refresh duration
    #
    if self.Conf.isTrackTime:
      if self.nFrTotal == 0:
        self.tFr = Clock.getTime_s()
      else:
        t0 = Clock.getTime_s()
        dt = t0 -self.tFr
        self.avFrDur_s += dt
        self.tFr = t0
        self.dataDtFr[self.dataDtFrLen] = dt
        self.dataDtFrLen += 1
        if self.dataDtFrLen >= self.dataDtFr.size:
          self.dataDtFrOver = True
          self.dataDtFrLen = 0
        if self.Conf.isWarnFrDrop and (dt > self.dtFr_thres_s):
          self.nDroppedFr += 1
          ssp.Log.write(
              "WARNING", "dt of frame #{0} was {1:.3f} ms"
              .format(self.nFrTotal, dt *1000.0)
            )

    self.nFrTotal += 1
    self.tFrRel_s = self.nFrTotal*self.Stage.dtFr_s


  # --------------------------------------------------------------------
  def run(self):
    # Runs the OpenGL/pyglet event loop, thereby any loaded stimulus
    #
    if not self.isReady:
      return

    if self.Stim is None:
      ssp.Log.write("ok", "Ready.")
      return

    # Start stimulus ...
    #
    self.isEnd  = False
    ssp.Log.write("ok", "Running...")
    ssp.Log.write("DATA", {"stimFileName": self.Stim.fileName,
                           "stimState": "STARTED",
                           "stimMD5": self.Stim.md5Str}.__str__())

    # Prepare recording stimulus if requested
    self.recordStim = self.Conf.recordStim and self.Stim is not None and not self.Stim.nameStr.startswith('__')

    if self.recordStim:
      self.View.prepareGrabStim()
      self.recordedStim = []
      self.recordedStimName = self.Stim.nameStr

    self.Stage.logData()
    self.View.startRenderingLoop(self)

    if self.recordStim:
      self.save_stim_to_file()

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def stop(self):
    # Signals event loop to stop
    #
    self.isEnd = True
    ssp.Log.write("DEBUG", "Presenter.stop()")

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def finish(self):
    # Finish presentation
    #
    if not self.isReady:
      return

    if self.isUserAbort:
      # Clear screen
      #
      self.View.clear()
      self.View.present()
      ssp.Log.write("ABORT", "User aborted program")

    else:
      ssp.Log.write("ok", "Program finished")

    # Log timing information
    #
    if self.Conf.isTrackTime:
      self.avRendDur_s  = self.avRendDur_s /self.nRendTotal
      self.avPresDur_s  = self.avPresDur_s /self.nRendTotal
      self.avFrDur_s = self.avFrDur_s /self.nFrTotal
      ssp.Log.write(
          "INFO", "{0:.3f} ms/frame ({1:.3f} Hz), rendering: "
          "{2:.3f} ms/frame ({3} frames in total)"
          .format(self.avFrDur_s*1000.0, 1/self.avFrDur_s,
                  self.avRendDur_s*1000.0, self.nFrTotal)
        )
      ssp.Log.write(
          "INFO", "presenting: {0:.3f} ms/frame"
          .format(self.avPresDur_s*1000.0)
        )

      if glo.QDSpy_frRateStatsBufferLen > 0:
        if not self.dataDtFrOver:
          data = self.dataDtFr[:self.dataDtFrLen]
        else:
          data = self.dataDtFr
      else:
        data = np.array(self.dataDtFr)
      av = data.mean() *1000.0
      std = data.std() *1000.0
      ssp.Log.write(
          "INFO", "{0:.3f} +/- {1:.3f} ms/frame (over the last {2}"
          " frames) = {3:.3} Hz"
          .format(av, std, len(data), 1000.0/av)
        )
      if self.nDroppedFr > 0:
        pcDrFr = 100.0*self.nDroppedFr/self.nFrTotal
        ssp.Log.write(
            "WARNING", "{0} frames dropped (={1:.3f} %)"
            .format(self.nDroppedFr, pcDrFr)
          )

      ssp.Log.write(
          "DATA", {"avgFreq_Hz": 1/self.avFrDur_s,
          "nFrames": self.nFrTotal,
          "nDroppedFrames": self.nDroppedFr}.__str__()
        )

      if QDSpy_verbose:
        # Generate a plot ...
        #
        ssp.Log.write("WARNING", "Code needs to be updated")
        '''
        pylab.title("Timing")
        pylab.subplot(2,1,1)
        pylab.plot(list(range(len(data))), data*1000, "-")
        xArr    = [0, len(data)-1]
        dtFr_ms = self.dtFr_meas_s*1000
        yMin    = dtFr_ms +self.Conf.maxDtTr_ms
        yMax    = dtFr_ms -self.Conf.maxDtTr_ms
        pylab.plot(xArr, [yMin, yMin], "k--")
        pylab.plot(xArr, [yMax, yMax], "k--")
        pylab.ylabel("frame duration [ms]")
        pylab.xlabel("frame #")
        pylab.xlim([10,len(data)])
        pylab.ylim([dtFr_ms-10,dtFr_ms+10])
        pylab.subplot(2,1,2)
        n, bins, pat = pylab.hist(data*1000, 100, histtype="bar", rwidth=0.9)
        pylab.setp(pat, 'facecolor', 'b', 'alpha', 0.75)
        #pylab.xlim([dtFr_ms-5,dtFr_ms+5])
        pylab.ylabel("# frames")
        pylab.xlabel("frame duration [ms]")
        pylab.tight_layout()
        pylab.show()
        '''

  @staticmethod
  def stim_to_pil_image(image: pyglet.image.ImageData, f_downsample: int = 1) -> PIL.Image.Image:
    img_data = image.get_data()

    pil_image = PIL.Image.new(mode="RGBA", size=(image.width, image.height))
    pil_image.frombytes(img_data)

    if f_downsample > 1:
      pil_image = pil_image.resize(tuple(s // f_downsample for s in pil_image.size))

    pil_image = pil_image.convert('RGB')
    pil_image = pil_image.transpose(PIL.Image.Transpose.FLIP_TOP_BOTTOM)

    return pil_image

  @staticmethod
  def adapt_stimulus_recording_to_setup(stimulus_stack: np.array, setup_id: int) -> np.array:
    """ Tweak stimulus according to https://cin-10.medizin.uni-tuebingen.de/eulerwiki/index.php/Orientation
        stimulus_stack.shape: frame, y, x, color
    """
    # for both setups the x and y plane is swapped
    if setup_id == 1:
      # swap x and y
      stimulus_stack = stimulus_stack.transpose(0, 2, 1, 3)
    elif setup_id == 3:
      # swap x and y
      stimulus_stack = stimulus_stack.transpose(0, 2, 1, 3)
      # flip direction in y-axis
      stimulus_stack = np.flip(stimulus_stack, axis=1)
    else:
      raise ValueError(f"Unknown setup: {setup_id=}")

    return stimulus_stack

  def save_stim_to_file(self) -> None:
      ssp.Log.write("DEBUG", f"Prepare saving {len(self.recordedStim)} stimulus frames")
      stim_folder = "RecordedStimuli"
      if not os.path.isdir(stim_folder):
        os.mkdir(stim_folder)

      pil_image_array = [self.stim_to_pil_image(s, f_downsample=self.Conf.rec_f_downsample_x)
                         for s in self.recordedStim]
      recorded_stimulus_stack = np.stack(pil_image_array)
      if self.Conf.rec_setup_id is not None:
        recorded_stimulus_stack = self.adapt_stimulus_recording_to_setup(
          recorded_stimulus_stack, self.Conf.rec_setup_id)

      file_name = f"{stim_folder}/{self.recordedStimName}.pickle"
      with open(file_name, 'wb') as file:
        pickle.dump(recorded_stimulus_stack, file, protocol=pickle.HIGHEST_PROTOCOL)

      ssp.Log.write("DEBUG", f"Successfully saved stimulus recording to {file_name}")

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def prepare(self, _Stim, _Sync=None):
    # Prepare a stimulus, to be started with the run() function
    #
    self.reset()
    self.Stim = _Stim
    self.isReady = True

    if _Sync is not None:
      self.isRunFromGUI = True
      self.Sync = _Sync

    if self.Stim is None:
      self.isReady = False

    else:
      # Setup digital I/O, if used
      #
      if self.IO is not None:
        self.IO_portOut = self.IO.getPortFromStr(self.Conf.DIOportOut)
        self.IO_maskMark = 0x01 << self.Conf.DIOpinMarker

      # Load and generate shader(s), if any
      #
      self.ShProgList = []
      if not glo.QDSpy_loadShadersOnce:
        self.ShManager = csh.ShaderManager(self.Conf)

      if len(self.Stim.ShList) > 0:
        for iSh, Sh in enumerate(self.Stim.ShList):
          shType = Sh[stm.SH_field_shaderType]
          if shType in self.ShManager.getShaderTypes():
            # Create shader program
            #
            shader = self.ShManager.createShader(shType)
            if shader is not None:
              self.ShProgList.append(shader)
            else:
              self.isReady = False
              ssp.Log.write(
                  "ERROR", "Stimulus '{0}' uses shader '{1}' that "
                  "could not be compiled"
                  .format(_Stim.nameStr, shType)
                )
          else:
            # A shaders that is not in the shader folder is required
            #
            self.isReady  = False
            ssp.Log.write(
                "ERROR", "Stimulus '{0}' uses shader '{1}' that "
                "cannot be found".format(_Stim.nameStr, shType)
              )

      # Load movie files, if any
      #
      self.MovieList = []
      if len(self.Stim.MovList) > 0:
        for Mov in self.Stim.MovList:
          movOb = mov.Movie(self.Conf)
          res = movOb.load(
              self.Conf.pathStim +Mov[stm.SM_field_movieFName]
            )
          if res == stm.StimErrC.ok:
            # Add movie class object to list
            #
            self.MovieList.append(movOb)

          else:
            # The movie file(s) could not be loaded
            #
            self.isReady = False
            ssp.Log.write(
                "ERROR", "Stimulus '{0}' uses movie '{1}' that "
                "cannot be found".format(
                _Stim.nameStr,Mov[stm.SM_field_movieFName])
              )

      # Load videos, if any
      #
      self.VideoList = []
      if len(self.Stim.VidList) > 0:
        for Vid in self.Stim.VidList:
          vidOb = vid.Video(self.Conf)
          res = vidOb.load(
              self.Conf.pathStim +Vid[stm.SV_field_videoFName]
            )
          if res == stm.StimErrC.ok:
            # Add video class object to list
            #
            self.VideoList.append(vidOb)

          else:
            # The video file(s) could not be loaded
            #
            self.isReady = False
            ssp.Log.write(
                "ERROR", "Stimulus '{0}' uses video '{1}' that "
                "cannot be found".format(
                _Stim.nameStr, Vid[stm.SV_field_videoFName])
              )

      # Create batch object for rendering objects
      #
      self.Batch = self.View.createBatch(_isScrOvl=self.Stage.useScrOvl)
      self.Batch.set_shader_manager(self.ShManager)

      if self.isReady:
        ssp.Log.write(
            "ok", "Stimulus '{0}' prepared".format(_Stim.nameStr)
          )

# ---------------------------------------------------------------------
