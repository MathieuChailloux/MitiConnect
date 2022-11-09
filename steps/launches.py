# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ErcTvbPluginDialog
                                 A QGIS plugin
 MitiConnect integrates ecological Connectivity in Mitigation Hierarchy
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2021-08-25
        git sha              : $Format:%H$
        copyright            : (C) 2021 by INRAE
        email                : mathieu.chailloux@inrae.fr
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os, sys, shutil, time

import qgis
from qgis.PyQt import uic, QtWidgets
from qgis.PyQt.QtCore import Qt
from qgis.core import Qgis, QgsProcessingContext, QgsProcessingUtils

from ..qgis_lib_mc import utils
from ..qgis_lib_mc.utils import CustomException, joinPath
from ..qgis_lib_mc.abstract_model import DictItem, DictModel, TableToDialogConnector, CheckableComboDelegate
# from ..algs.erc_tvb_algs_provider import ErcTvbAlgorithmsProvider
from ..qgis_lib_mc.qgsTreatments import applyProcessingAlg
from ..qgis_lib_mc import qgsTreatments, qgsUtils, feedbacks, styles
from ..ui.scenario_dialog import ScenarioItem, ScenarioDialog, ScenarioLanduseDialog
from ..ui.plot_window import PlotWindow
from . import scenario

# Graphab utils

# nodata_val = 65535

def checkGraphabInstalled(feedback):
    return True
    # plugins = qgis.utils.available_plugins
    # installed = 'graphab4qgis' in plugins
    # if not installed:
        # feedback.user_error("Graphab is not installed")

#{ 'DIRPATH' : 'TEMPORARY_OUTPUT', 'INPUT' : 'D:/IRSTEA/ERC/tests/BousquetOrbExtended/Source/CorineLandCover/CLC12_BOUSQUET_ORB.tif', 'LANDCODE' : '241', 'NAMEPROJECT' : 'Project1', 'NODATA' : None, 'SIZEPATCHES' : 0 }

def getLinkset(gProj,linksetName):
    for linkset in gProj.project.costLinks:
        if linkset.name == linksetName:
            return linkset
    return None
def getGraph(gProj,graphName):
    for graph in gProj.project.graphs:
        if graph.name == graphName:
            return graph
    return None
    
PROVIDER = 'mitiConnect'
# TODO : grapha wrappers in erc_tvb_algs_provider ?
def createGraphabProject(landuse,codes,out_dir,project_name,
        nodata=None,patch_size=0,feedback=None):
    code_str = ",".join(codes)
    params = {
        'DIRPATH' : out_dir,
        'INPUT' : landuse,
        'LANDCODE' : code_str,
        'NAMEPROJECT' : project_name,
        'NODATA' : nodata,
        'SIZEPATCHES' : patch_size }
    return applyProcessingAlg(PROVIDER,'create_project',params,feedback=feedback)
def createGraphabLinkset(project,name,frictionPath,feedback=None):
    params = { 'CODE' : '',
        'EXTCOST' : frictionPath,
        'INPUT' : project,
        'NAME' : name,
        #'TYPE' : 1 }
        'TYPE' : 1 }
    return applyProcessingAlg(PROVIDER,'create_linkset',params,feedback=feedback)
def createGraphabGraph(project,linkset,unit=0,dist=0,graphName="",
        feedback=None):
    params = { 'DIST' : dist,
        'DISTUNIT' : unit,
        'INPUT' : project,
        'NAMEGRAPH' : graphName,
        'NAMELINKSET' : linkset }
    return applyProcessingAlg(PROVIDER,'create_graph',params,feedback=feedback)
def computeMetric(project,graphName,metricName=0,unit=0,
        d=1000,p=0,localMetric=True,feedback=None):
    params = { 'DISTUNIT' : unit,
        'DPARAMETER' : d,
        'GRAPHNAME' : graphName,
        'INPUT' : project,
        'METRICSNAME' : metricName,
        'PPARAMETER' : p }
    alg_name = 'local_metric' if localMetric else 'global_metric'
    return applyProcessingAlg(PROVIDER,alg_name,params,feedback=feedback)
def computeLocalMetric(project,graphName,metricName=0,unit=0,
        d=1000,p=0,feedback=None):
    return computeMetric(project,graphName,metricName=metricName,unit=unit,
        d=d,p=p,localMetric=True,feedback=feedback)
def computeGlobalMetric(project,graphName,metricName=0,unit=0,
        d=1000,p=0,feedback=None):
    return computeMetric(project,graphName,metricName=metricName,unit=unit,
        d=d,p=p,localMetric=False,feedback=feedback)
        


class LaunchItem(DictItem):

    SCENARIO = 'SCENARIO'
    SPECIE = 'SPECIE'
    EXTENT = 'EXTENT'
    
    FIELDS = [ SCENARIO, SPECIE, EXTENT ]
    DISPLAY_FIELDS = FIELDS
    
    def __init__(self,dict,pluginModel=None,feedback=None):
        super().__init__(dict,feedback=feedback)
        self.pluginModel = pluginModel
        
    @classmethod
    def fromValues(cls,scName,spName,extent,pluginModel=None,feedback=None):
        dict = { cls.SCENARIO : scName, cls.SPECIE : spName,
            cls.EXTENT : extent}
        return cls(dict,pluginModel=pluginModel,feedback=feedback)
    @classmethod
    def fromDict(cls,dict,feedback=None):
        if cls.EXTENT not in dict:
            dict[cls.EXTENT] = None
        castDict = utils.castDict(dict)
        return cls(castDict,feedback=feedback)
        
    def getScName(self):
        return self.dict[self.SCENARIO]
    def getSpName(self):
        return self.dict[self.SPECIE]
    def getExtName(self):
        return self.dict[self.EXTENT]
    def setExtName(self,val):
        self.dict[self.EXTENT] = val
    def getScSpNames(self):
        return (self.getScName(), self.getSpName())
    def getNames(self):
        return (self.getScName(), self.getSpName(), self.getExtName())
        
    def equals(self,other):
        selfNames = self.getNames()
        otherNames = other.getNames()
        return selfNames == otherNames


# Scenario
        
class LaunchModel(DictModel):

    def __init__(self, pluginModel):
        itemClass = getattr(sys.modules[__name__], LaunchItem.__name__)
        super().__init__(itemClass,
            feedback=pluginModel.feedback,
            fields=LaunchItem.FIELDS,
            display_fields=LaunchItem.DISPLAY_FIELDS)
        # super().__init__(self,itemClass,feedback=pluginModel.feedback,
            # display_fields=ScenarioItem.DISPLAY_FIELDS)
        self.pluginModel = pluginModel
        
    # Add metric field if needed
    def addItem(self,item):
        for f in item.dict.keys():
            if f not in self.fields:
                self.addField(f)
        super().addItem(item)
    def mkItemFromDict(self,dict,feedback=None):
        feedback.pushDebugInfo("mkItemFromDict " + str(dict))
        for f in dict.keys():
            if f not in self.fields:
                self.addField(f)
        return self.itemClass.fromDict(dict,feedback=feedback)
        
    # Item getters
    def getScenarioNames(self):
        return [i.getName() for i in self.items]
    def getItemFromName(self,name):
        for i in self.items:
            if i.getName() == name:
                return i
        return None
    def getScItemFromName(self,scName):
        return self.pluginModel.scenarioModel.getItemFromName(scName)
    def getSpItemFromName(self,spName):
        return self.pluginModel.speciesModel.getItemFromName(spName)
    def getItems(self,item):
        scName, spName, extName = item.getNames()
        scItem = self.getScItemFromName(scName)
        spItem = self.getSpItemFromName(spName)
        extItem = self.getScItemFromName(extName)
        return (scItem, spItem, extItem)
    def getItemFromNames(self,scName,spName,extName):
        for i in self.items:
            iScName, iSpName, iExtName = i.getNames()
            if iScName == scName and iSpName == spName:
                if extName is None or extName == iExtName:
                    return i
        return None
    def scExists(self,name):
        i = self.getItemFromName(name)
        return (i is not None)
                 
    # Item base path getters
    def normPath(self,fname):
        return os.path.normcase(fname)
    def getItemNameSuffix(self,item,suffix):
        scName, spName, extName = item.getNames()
        if extName:
            suffix = "ext" + extName + "_" + suffix
        res = scName + "_" + spName + "_" + suffix
        return res
    def getScDirFromName(self,scName):
        scDir = self.getItemSpDir(scName)
        return self.normPath(scDir)
    def getItemExtentScDir(self,extName):
        dirname = "extent_" + str(extName)
        return self.pluginModel.getSubDir(dirname)
    def getItemExtentSpDir(self,item):
        scName, spName, extName = item.getNames()
        extentScDir = self.getItemExtentScDir(extName)
        spDir = self.pluginModel.getSubDir(spName,baseDir=extentScDir)
        return self.normPath(spDir)
    def getItemExtentPath(self,item):
        extentDir = self.getItemExtentSpDir(item)
        return self.normPath(joinPath(extentDir,"extent.shp"))
    def getItemBaseDir(self,item):
        scName = item.getScName()
        spDir = self.getItemExtentSpDir(item)
        scDir = self.pluginModel.getSubDir(scName,baseDir=spDir)
        return self.normPath(scDir)
    def getItemOutBase(self,item,suffix=""):
        spDir = self.getItemBaseDir(item)
        out_bname = self.getItemNameSuffix(item,suffix) + ".tif"
        return self.normPath(joinPath(spDir,out_bname))
    def getSpBaseLanduse(self,spItem):
        return self.pluginModel.speciesModel.getItemLandusePath(spItem)
        
    # Extent computing
    def computeItemExtent(self,item,eraseFlag=True,feedback=None):
        if feedback is None:
            feedback = self.feedback
        scName, spName, extName = item.getNames()
        scItem, spItem, extItem = self.getItems(item)
        self.feedback.pushDebugInfo("computeItemExtent " + str(extName))
        crs = self.pluginModel.paramsModel.getCrsStr()
        maxExtent = self.pluginModel.paramsModel.getExtentLayer()
        # Check out path
        out_path = self.getItemExtentPath(item)
        if utils.fileExists(out_path):
            if eraseFlag:
                qgsUtils.removeLayerFromPath(out_path)
            else:
                return out_path
        # Union of scenario and children
        scExtentLayers = self.pluginModel.scenarioModel.getItemExtentLayers(extItem)
        self.feedback.pushDebugInfo("scExtentLayers " + str(scExtentLayers))
        if not scExtentLayers:
            extPath = maxExtent
        else:
            extPath = qgsUtils.mkTmpPath("extentsMerged.gpkg")
            qgsTreatments.mergeVectorLayers(scExtentLayers,crs,extPath,feedback=feedback)
        # Apply specie extent mode
        spLanduse = self.getSpBaseLanduse(spItem)
        if spItem.isMaxExtentMode():
            self.feedback.pushDebugInfo("copymode")
            shutil.copy(extPath,out_path)
        elif spItem.isBufferMode():
            # bufferVal = float(spItem.getExtentVal
            bufferMulVal, maxDisp = float(spItem.getExtentVal()), int(spItem.getMaxDisp())
            if bufferMulVal == 0:
                self.feedback.user_error("Empty buffer for specie " + str(spName))
            if maxDisp == 0:
                self.feedback.user_error("Empty dispersal distance for specie " + str(spName))
            bufferVal = bufferMulVal * maxDisp
            extent = qgsTreatments.applyBufferFromExpr(extPath,
                bufferVal,out_path,feedback=feedback)
        elif spItem.isCustomLayerMode():
            self.internal_error("Custom extent layer mode not implemented yet")
        else:
            self.internal_error("Unexpected specie mode " + str(spItem))
        return out_path
        
    # Item getters for each step
    def getItemLanduse(self,item):
        return self.getItemOutBase(item,suffix="landuse")
    def getItemFriction(self,item):
        return self.getItemOutBase(item,suffix="friction")
    def getItemGraphabProjectName(self,item):
        return self.getItemNameSuffix(item,"graphab")
    def getItemGraphabProjectDir(self,item):
        spDir = self.getItemBaseDir(item)
        out_bname = self.getItemGraphabProjectName(item)
        return self.normPath(joinPath(spDir,out_bname))
    def getItemGraphabProjectFile(self,item):
        baseDir = self.getItemGraphabProjectDir(item)
        out_bname = self.getItemGraphabProjectName(item) + ".xml"
        return self.normPath(joinPath(baseDir,out_bname))
    def getItemLinksetName(self,item):
        return self.getItemNameSuffix(item,"linkset")
    def getItemGraphName(self,item):
        return self.getItemNameSuffix(item,"graph")
        
    # Table flags
    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled
        
    def reload(self):
        scModel = self.pluginModel.scenarioModel
        self.items = []
        for scItem in scModel.items:
            scName = scItem.getName()
            extentSc = scModel.getItemExtentSc(scItem)
            extName = extentSc.getName() if extentSc else extentSc
            for spItem in self.pluginModel.speciesModel.items:
                spName = spItem.getName()
                # existingItem = self.getItemFromNames(scName,spName,extName)
                # if existingItem:
                    # if existingItem.getExtName() != extName:
                        # existingItem.setName(extName)
                # else:
                launchItem = LaunchItem.fromValues(scName,spName,extName,
                    pluginModel=self.pluginModel,feedback=self.feedback)
                self.addItem(launchItem)
                if not scItem.isInitialState():
                    isScItem = scModel.getInitialState()
                    isScName = isScItem.getName()
                    isItem = LaunchItem.fromValues(isScName,spName,extName,
                    pluginModel=self.pluginModel,feedback=self.feedback)
                    self.addItem(isItem)
        self.layoutChanged.emit()
        
    def clearFile(self,filename):
        if utils.fileExists(filename):
            qgsUtils.removeLayerFromPath(filename)
            qgsUtils.removeRaster(filename)
    def clearStep(self,item,step=1):
        if step <= 7:
            metricStr = self.pluginModel.paramsModel.getGlobalMetricStr()
            if metricStr in self.fields:
                for i in self.items:
                    i.dict[metricStr] = None
        if step <= 6:
            metricStr = self.pluginModel.paramsModel.getLocalMetricStr()
            if metricStr in self.fields:
                for i in self.items:
                    i.dict[metricStr] = None
        projName = self.getItemGraphabProjectName(item)
        gProj = self.pluginModel.graphabPlugin.getProject(projName)
        if gProj:
            if step <= 5:
                graphName = self.getItemGraphName(item)
                # graph = getGraph(gProj,graphName)
                # if graph:
                    # qgsUtils.removeGroups(graphName)
                gProj.removeGraph(graphName)
                # assert(False)
            if step <= 4:
                self.feedback.pushDebugInfo("proj")
                linksetName = self.getItemLinksetName(item)
                # linkset = getLinkset(gProj,linksetName)
                # if linkset:
                gProj.removeLinkset(linksetName)
        if step <=3:
            project = self.getItemGraphabProjectFile(item)
            if os.path.isfile(project):
                projName = self.getItemGraphabProjectName(item)
                qgsUtils.removeGroups(projName)
        if step <= 2:
            frPath = self.getItemFriction(item)
            self.clearFile(frPath)
        if step <= 1:
            luPath = self.getItemLanduse(item)
            self.clearFile(luPath)


        
        
    def applyItemLanduse(self,item,feedback=None,eraseFlag=False):
        if feedback is None:
            feedback = self.feedback
        scName, spName, extName = item.getNames()
        scItem, spItem, extItem = self.getItems(item)
        feedback.pushDebugInfo("applyItemLanduse " + str(scItem) + " " + str(spItem))
        # Check out path
        out_path = self.getItemLanduse(item)
        if utils.fileExists(out_path):
            if eraseFlag:
                self.clearStep(item,1)
                # qgsUtils.removeLayerFromPath(out_path)
                # qgsUtils.removeRaster(out_path)
            # else:
                # qgsUtils.loadRasterLayer(out_path,loadProject=True)
                # return
        # Prepare Params
        spLanduse = self.getSpBaseLanduse(spItem)
        crs, maxExtent, resolution = self.pluginModel.getRasterParams()
        baseType, nodataVal = self.pluginModel.baseType, self.pluginModel.nodataVal
        # Main action
        if scItem.isInitialState() or scItem.isLanduseMode():
            luPath = spLanduse
        elif scItem.isStackedMode():
            feedback.pushDebugInfo("LU2")
            # Get base layer
            isSc = self.pluginModel.scenarioModel.getInitialState()
            isName = isSc.getName()
            isItem = self.getItemFromNames(isName,spName,isName)
            isLayer = self.getItemLanduse(isItem)
            if not os.path.isfile(isLayer):
                feedback.user_error("Landuse layer does not exit for " + str(isItem))
            # Apply landuse modifications
            scHierarchy = self.pluginModel.scenarioModel.getItemHierarchy(scItem)
            feedback.pushDebugInfo("scHierarchy = %s"%([s.getName() for s in scHierarchy]))
            nbSc, cpt = len(scHierarchy), 0
            scLayers = [isLayer]
            mfeedback = feedbacks.ProgressMultiStepFeedback(nbSc,feedback)
            for sc in reversed(scHierarchy):
                scLayer = self.pluginModel.scenarioModel.rasterizeLayer(sc,mfeedback)
                scLayers.append(scLayer)
            # luPath = qgsUtils.mkTmpPath("%s_%s_%s_reclass.tif"%(scName,spName,extName))
            # Merge       
            luPath = qgsUtils.mkTmpPath(spName + "_landuse.tif")
            # qgsUtils.removeLayerFromPath(luPath)
            # qgsUtils.removeRaster(luPath)
            qgsTreatments.applyMergeRaster(scLayers,luPath,
                out_type=baseType,nodata_val=nodataVal,feedback=feedback)
        # Extent
        extentPath = self.getItemExtentPath(item)
        self.computeItemExtent(item,feedback=feedback)
        # Clip
        dst_crs = self.pluginModel.paramsModel.getCrsStr()
        qgsTreatments.clipRasterFromVector(luPath,extentPath,out_path,
            resolution=resolution,nodata=nodataVal,
            feedback=feedback)
        return out_path
        # qgsUtils.loadRasterLayer(out_path,loadProject=True)
         
    def applyItemFriction(self,item,feedback=None,  eraseFlag=False):
        if feedback is None:
            feedback = self.feedback
        feedback.pushDebugInfo("applyItemFriction")
        scName, spName, extName = item.getNames()
        scItem, spItem, extItem = self.getItems(item)
        # Check in path
        in_path = self.getItemLanduse(item)
        feedback.pushDebugInfo("in_path = " + str(in_path))
        if not utils.fileExists(in_path):
            self.feedback.user_error("No landuse file %s for specie %s in scenario %s"%(in_path,spName,scName))
        # Check out path
        out_path = self.getItemFriction(item)
        feedback.pushDebugInfo("out_path = " + str(out_path))
        if utils.fileExists(out_path):
            if eraseFlag:
                self.clearStep(item,2)
                # qgsUtils.removeLayerFromPath(out_path)
                # qgsUtils.removeRaster(out_path)
            else:
                loaded_layer = qgsUtils.loadRasterLayer(out_path,loadProject=True)
                styles.setRendererPalettedGnYlRd(loaded_layer)
                return
        # Prepare matrix
        baseType, nodataVal = self.pluginModel.baseType, self.pluginModel.nodataVal
        frictionModel = self.pluginModel.frictionModel
        matrixes = frictionModel.getReclassifyMatrixes([spName])
        feedback.pushDebugInfo("matrixes = " + str(matrixes))
        matrix = matrixes[spName]
        feedback.pushDebugInfo("matrix = " + str(matrix))
        # Get non assigned values
        inVals = qgsUtils.getRasterValsFromPath(in_path)
        mInVals, mOutVals = matrix[::3], matrix[2::3]
        feedback.pushDebugInfo("mInVals = " + str(mInVals))
        feedback.pushDebugInfo("mOutVals = " + str(mOutVals))
        naVals = [inV for inV, outV in zip(mInVals,mOutVals) if inV in inVals and outV == 0]
        self.feedback.pushWarning(self.tr("No friction value assigned to classes ") + str(naVals))
        # Call reclassify
        qgsTreatments.applyReclassifyByTable(in_path,matrix,out_path,
            out_type=baseType,nodata_val=nodataVal,boundaries_mode=2,
            feedback=feedback)
        loaded_layer = qgsUtils.loadRasterLayer(out_path,loadProject=True)
        styles.setRendererPalettedGnYlRd(loaded_layer)
            
    #{ 'DIRPATH' : 'TEMPORARY_OUTPUT', 'INPUT' : 'D:/IRSTEA/ERC/tests/BousquetOrbExtended/Source/CorineLandCover/CLC12_BOUSQUET_ORB.tif', 'LANDCODE' : '241', 'NAMEPROJECT' : 'Project1', 'NODATA' : None, 'SIZEPATCHES' : 0 }
    def applyItemGraphabProject(self,item,eraseFlag=False,feedback=None):
        if feedback is None:
            feedback = self.feedback
        feedback.pushDebugInfo("applyItemGraphabProject " + str(item))
        scName, spName, extName = item.getNames()
        scItem, spItem, extItem = self.getItems(item)
        checkGraphabInstalled(feedback)
        projName = self.getItemGraphabProjectName(item)
        project = self.getItemGraphabProjectFile(item)
        landuse = self.getItemLanduse(item)
        friction = self.getItemFriction(item)
        if not utils.fileExists(landuse):
            self.feedback.user_error("No landuse file %s for specie %s in scenario %s"%(landuse,spName,scName))
        if not utils.fileExists(friction):
            self.feedback.user_error("No friction file %s for specie %s in scenario %s"%(friction,spName,scName))
        codes = spItem.getCodesVal()
        if not codes:
            self.feedback.user_error("No habitat code specified for specie "
                + str(spName))
        minArea = spItem.getMinArea()
        # Get outputs
        outDir = self.getItemBaseDir(item)
        projectFolder = os.path.dirname(project)
        self.feedback.pushDebugInfo("project = " + str(project))
        self.feedback.pushDebugInfo("projName = " + str(projName))
        if os.path.isfile(project):
            if eraseFlag:
                self.clearStep(item,3)
                # qgsUtils.removeGroups(projName)
                # time.sleep(5)
                # qgsUtils.removeFolder(projectFolder)
            else:
                self.feedback.pushInfo("Graphab file " + str(project) + " already exists")
                self.pluginModel.loadProject(project)
                return
        createGraphabProject(landuse,codes,outDir,projName,
            nodata=-self.pluginModel.nodataVal,patch_size=minArea,feedback=feedback)


    def applyItemGraphabLinkset(self,item,eraseFlag=False,feedback=None):
        if feedback is None:
            feedback = self.feedback
        feedback.pushDebugInfo("applyItemGraphabLinkset")
        scName, spName, extName = item.getNames()
        scItem, spItem, extItem = self.getItems(item)
        checkGraphabInstalled(feedback)
        projName = self.getItemGraphabProjectName(item)
        project = self.getItemGraphabProjectFile(item)
        linksetName = self.getItemLinksetName(item)
        friction = self.getItemFriction(item)
        self.pluginModel.loadProject(project)
        gProj = self.pluginModel.graphabPlugin.getProject(projName)
        if gProj:
            self.feedback.pushDebugInfo("gproj")
            self.feedback.pushDebugInfo("linkset = " + str(linksetName))
            self.feedback.pushDebugInfo("linksets = " + str([l.name for l in gProj.project.costLinks]))
            linkset = getLinkset(gProj,linksetName)
            if linkset:
                if eraseFlag:
                    self.clearStep(item,4)
                    # gProj.removeLinkset(linksetName)
                else:
                    linksetGroup = gProj.projectGroup.children()[1]
                    for layer in linksetGroup.children():
                        if layer.name() == linksetName:
                            layer.setItemVisibilityChecked(True)
                            return
                    # gProj.reloadLinksetCSV(linksetName)
        # assert(False)
        classes,array,nodata = qgsUtils.getRasterValsArrayND(friction)
        feedback.pushDebugInfo("classes = " + str(classes))
        feedback.pushDebugInfo("nodata = " + str(nodata))
        createGraphabLinkset(project,linksetName,friction,feedback=feedback)
            
            
    def applyItemGraphabGraph(self,item,eraseFlag=False,feedback=None):
        if feedback is None:
            feedback = self.feedback
        feedback.pushDebugInfo("applyItemGraphabGraph")
        scName, spName, extName = item.getNames()
        scItem, spItem, extItem = self.getItems(item)
        maxDisp = spItem.getMaxDisp()
        checkGraphabInstalled(feedback)
        projName = self.getItemGraphabProjectName(item)
        project = self.getItemGraphabProjectFile(item)
        graphName = self.getItemGraphName(item)
        linksetName = self.getItemLinksetName(item)
        self.pluginModel.loadProject(project)
        gProj = self.pluginModel.graphabPlugin.getProject(projName)
        if gProj:
            feedback.pushDebugInfo("gProj")
            graph = getGraph(gProj,graphName)
            if graph:
                feedback.pushDebugInfo("graph")
                if eraseFlag:
                    self.clearStep(item,5)
                    # feedback.pushDebugInfo("erase")
                    # qgsUtils.removeGroups(graphName)
                    # gProj.removeGraph(graphName)
                    # assert(False)
                else:
                    graphsGroup = gProj.projectGroup.children()[0]
                    graphsGroup.setItemVisibilityChecked(True)
                    for graphGroup in graphsGroup.children():
                        if graphGroup.name() == graphName:
                            graphGroup.setItemVisibilityChecked(True)
                    return
        createGraphabGraph(project,linksetName,
            dist=maxDisp,graphName=graphName,feedback=feedback)
                
    def computeLocalMetric(self,item,eraseFlag=False,feedback=None):
        if feedback is None:
            feedback = self.feedback
        scName, spName, extName = item.getNames()
        scItem, spItem, extItem = self.getItems(item)
        projName = self.getItemGraphabProjectName(item)
        project = self.getItemGraphabProjectFile(item)
        graphName = self.getItemGraphName(item)
        self.pluginModel.loadProject(project)
        gProj = self.pluginModel.graphabPlugin.getProject(projName)
        metricStr = self.pluginModel.paramsModel.getLocalMetricStr()
        l, g, d, p = self.pluginModel.paramsModel.getGraphabParams()
        self.feedback.pushDebugInfo("l = " + str(l))
        # Compute metric value
        if eraseFlag or metricStr not in self.fields:
            val = computeLocalMetric(project,graphName,metricName=l,d=d,p=p,feedback=feedback)
        else:
            val = item.dict[metricStr]
            if not val:
                val = computeLocalMetric(project,graphName,
                    metricName=l,d=d,p=p,feedback=feedback)
        # Update table
        self.addField(metricStr)
        item.dict[metricStr] = val
        self.layoutChanged.emit()
        return val
                
    def computeGlobalMetric(self,item,eraseFlag=False,feedback=None):
        if feedback is None:
            feedback = self.feedback
        scName, spName = item.getScSpNames()
        projName = self.getItemGraphabProjectName(item)
        project = self.getItemGraphabProjectFile(item)
        graphName = self.getItemGraphName(item)
        self.pluginModel.loadProject(project)
        l, g, d, p = self.pluginModel.paramsModel.getGraphabParams()
        metricStr = self.pluginModel.paramsModel.getGlobalMetricStr()
        # Check graph
        # projName = self.getItemGraphabProjectName(item)
        # gProj = self.pluginModel.graphabPlugin.getProject(projName)
        # if gProj:
            # graph = getGraph(gProj,graphName)
        # else:
            # pass
        # Compute metric value
        if eraseFlag or metricStr not in self.fields:
            val = computeGlobalMetric(project,graphName,metricName=g,d=d,p=p,feedback=feedback)
        else:
            val = item.dict[metricStr]
            if not val:
                val = computeGlobalMetric(project,graphName,
                    metricName=g,d=d,p=p,feedback=feedback)
        # Update table
        self.addField(metricStr)
        item.dict[metricStr] = val
        self.layoutChanged.emit()
        return val
        
    def removeItems(self,indexes):
        names = [self.items[ind.row()].getName() for ind in indexes]
        super().removeItems(indexes)
        self.pluginModel.removeImports(names)

class LaunchConnector(TableToDialogConnector):

    def __init__(self,dlg,model):
        self.dlg = dlg
        self.feedback = dlg.feedback
        super().__init__(model,self.dlg.launchesView)
        self.refreshScenarios()

    def refreshSpecies(self):   
        names = self.model.pluginModel.speciesModel.getNames()
        self.dlg.speciesSelection.clear()
        self.dlg.speciesSelection.insertItems(0,names)

    def refreshScenarios(self):   
        names = self.model.pluginModel.scenarioModel.getNames()
        self.dlg.scenariosSelection.clear()
        self.dlg.scenariosSelection.insertItems(0,names)

    def connectComponents(self):
        super().connectComponents()
        self.model.pluginModel.speciesModel.layoutChanged.connect(self.refreshSpecies)
        self.model.pluginModel.scenarioModel.layoutChanged.connect(self.refreshScenarios)
        self.dlg.landuseRun.clicked.connect(self.landuseRun)
        self.dlg.frictionRun.clicked.connect(self.frictionRun)
        self.dlg.projectRun.clicked.connect(self.graphabProjectRun)
        self.dlg.linksetRun.clicked.connect(self.graphabLinksetRun)
        self.dlg.graphRun.clicked.connect(self.graphabGraphRun)
        self.dlg.localMetricsRun.clicked.connect(self.computeLocalMetric)
        self.dlg.compareScenariosRun.clicked.connect(self.computeGlobalMetric)
        self.dlg.reloadButton.clicked.connect(self.reload)
        # self.model.pluginModel.speciesModel.layoutChanged.connect(self.reload)
        # self.model.pluginModel.scenarioModel.layoutChanged.connect(self.reload)
        
    def reload(self):
        self.items = []
        self.model.reload()
        self.model.layoutChanged.emit()
        
    def getSelectedScenarios(self):
        scNames = self.dlg.scenariosSelection.checkedItems()
        self.feedback.pushDebugInfo("scNames = " + str(scNames))
        if not scNames:
            self.feedback.user_error("No scenario selected")
        items = [self.model.pluginModel.scenarioModel.getItemFromName(s) for s in scNames]
        self.feedback.pushDebugInfo("scNames 2 = " + str(len(items)))
        self.feedback.pushDebugInfo("scNames 3 = " + str(items))
        return items
        # indexes = self.view.selectedIndexes()
        # if not indexes:
            # self.feedback.user_error("No scenario selected")
        # rows = list(set([i.row() for i in indexes]))
        # res = [self.model.items[i] for i in rows]
        # return res
        
    def getSelectedSpecies(self):
        speciesNames = self.dlg.speciesSelection.checkedItems()
        self.feedback.pushDebugInfo("spNames = " + str(speciesNames))
        if not speciesNames:
            self.feedback.user_error("No specie selected")
        items = [self.model.pluginModel.speciesModel.getItemFromName(s) for s in speciesNames]
        return items
        
    def iterateRun(self,func):
        scenarios = self.getSelectedScenarios()
        species = self.getSelectedSpecies()
        nb_steps = len(scenarios) * len(species)
        step_feedback = feedbacks.ProgressMultiStepFeedback(nb_steps,self.feedback)
        cpt=0
        step_feedback.setCurrentStep(cpt)
        for sc in scenarios:
            self.feedback.pushDebugInfo("sc " + str(sc))
            for sp in species:
                func(sc,sp,feedback=step_feedback)
                cpt+=1
                step_feedback.setCurrentStep(cpt)
                
    def groupByExtent(self,scenarios):
        scModel = self.model.pluginModel.scenarioModel
        isSc = scModel.getInitialState()
        scMap = {}
        cpt = 0
        scenariosOrd = sorted(scenarios,key=lambda i: scModel.getItemDegree(i))
        for sc in scenariosOrd:
            baseSc = self.model.pluginModel.scenarioModel.getItemExtentSc(sc)
            self.feedback.pushDebugInfo("sc = " + str(sc.getName()))
            self.feedback.pushDebugInfo("scMap = " + str(scMap))
            if baseSc in scMap:
                self.feedback.pushDebugInfo("scMap(base) = " + str(scMap[baseSc]))
                self.feedback.pushDebugInfo("scMap(type) = " + str(scMap[baseSc].__class__.__name__))
                scMap[baseSc].append(sc)
            else:
                scMap[baseSc] = [sc]
            cpt += 1
        for baseSc, scList in scMap.items():
            sc0 = scList[0]
            if not sc0.isInitialState():
                scList.insert(0,isSc)
                self.feedback.pushDebugInfo("scenarios ordered with IS : " + str([sc.getName() for sc in scList]))
                cpt += 1
            # scMap[baseSc] = scenariosOrdered
        return (scMap, cpt)
        
    def iterateRunExtent(self,func):
        scenarios = self.getSelectedScenarios()
        species = self.getSelectedSpecies()
        eraseFlag = self.dlg.eraseResults.isChecked()
        # Build scMap
        scMap, nbSc = self.groupByExtent(scenarios)
        
        # nb steps feedback
        nb_steps = nbSc * len(species)
        step_feedback = feedbacks.ProgressMultiStepFeedback(nb_steps,self.feedback)
        cpt=0
        step_feedback.setCurrentStep(cpt)
        # Iteration
        for baseSc, scenarios in scMap.items():
            extName = baseSc.getName()
            for sp in species:
                spName = sp.getName()
                for sc in scenarios:
                    scName = sc.getName()
                    li = self.model.getItemFromNames(scName,spName,extName)
                    if li is None:
                        self.feedback.internal_error("No item found for "
                            + extName + " - " + spName + " - " + scName)
                    func(li,eraseFlag=eraseFlag,feedback=step_feedback)
                    cpt+=1
                    step_feedback.setCurrentStep(cpt)
    
    def landuseItemRun(self,item,feedback=None,eraseFlag=None):
        out_path = self.model.getItemLanduse(item)
        if utils.fileExists(out_path):
            if eraseFlag:
                self.model.clearStep(item,1)
                # qgsUtils.removeLayerFromPath(out_path)
                # qgsUtils.removeRaster(out_path)
            else:
                qgsUtils.loadRasterLayer(out_path,loadProject=True)
                return out_path
        self.model.applyItemLanduse(item,feedback=feedback)
        qgsUtils.loadRasterLayer(out_path,loadProject=True)
    def landuseRun(self):
        self.feedback.beginSection("Computing land use layer(s)")
        # self.iterateRunExtent(self.model.applyItemLanduse)
        self.iterateRunExtent(self.landuseItemRun)
        self.feedback.endSection()
        
    def frictionRun(self):
        self.feedback.beginSection("Computing friction layer(s)")
        self.iterateRunExtent(self.model.applyItemFriction)
        # step_feedback = feedbacks.ProgressMultiStepFeedback(len(scenarios),self.feedback)
        # for cpt, sc in enumerate(scenarios,start=1):
            # self.model.applyItemFriction(sc,species,feedback=step_feedback)
            # step_feedback.setCurrentStep(cpt)
        self.feedback.endSection()
            # for sp in species:
                # self.feedback.pushDebugInfo("TODO : friction Run "
                    # + sc.getName() + " - " + sp.getName())
    def graphabProjectRun(self):
        self.feedback.beginSection("Creating Graphab project(s)")
        self.iterateRunExtent(self.model.applyItemGraphabProject)
        self.feedback.endSection()
    def graphabLinksetRun(self):
        self.feedback.beginSection("Creating linkset(s)")
        self.iterateRunExtent(self.model.applyItemGraphabLinkset)
        self.feedback.endSection()
    def graphabGraphRun(self):
        self.feedback.beginSection("Creating graphs(s)")
        self.iterateRunExtent(self.model.applyItemGraphabGraph)
        self.feedback.endSection()
    def computeLocalMetric(self):
        self.feedback.beginSection("Computing local metric(s)")
        self.iterateRunExtent(self.model.computeLocalMetric)
        self.feedback.endSection()
    def computeGlobalMetric(self):
        self.feedback.beginSection("Computing global metric(s)")
        # Get UI state
        scenarios = self.getSelectedScenarios()
        species = self.getSelectedSpecies()
        cmpInit = self.dlg.cmpInit.isChecked()
        percentFlag = self.dlg.cmpPerc.isChecked()
        # Prepare feedback
        scMap, nbSc = self.groupByExtent(scenarios)
        nb_steps = nbSc * len(species)
        step_feedback = feedbacks.ProgressMultiStepFeedback(nb_steps,self.feedback)
        values = {}
        cpt = 0
        # Loop
        for baseSc, scenarios in scMap.items():
            extName = baseSc.getName()
            for sp in species:
                spName = sp.getName()
                initVal = -1
                for sc in scenarios:
                    scName = sc.getName()
                    item = self.model.getItemFromNames(scName,spName,extName)
                    val = self.model.computeGlobalMetric(item,feedback=step_feedback)
                    if sc.isInitialState():
                        initVal = val
                    elif initVal == -1:
                        assert(False)
                    elif initVal == 0:
                        self.internal_error("Empty value for global metric of initial state")
                    else:
                        if cmpInit:
                            if percentFlag:
                                finalVal = (val - initVal) / initVal
                            else:
                                finalVal = val - initVal
                        else:
                            finalVal = val
                        if scName not in values:
                            values[scName] = {}
                        values[scName][spName] = finalVal
                    cpt += 1
                    step_feedback.setCurrentStep(cpt)
        self.feedback.endSection()
                # step_feedback.setCurrentStep(cpt)
        # Plot results in new window
        globalMetric = self.model.pluginModel.paramsModel.getGlobalMetricStr()
        window = PlotWindow(values,cmpInit,percentFlag,globalMetric,self.feedback)
        window.show()
        while window.exec_():
            pass


