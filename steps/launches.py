# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ErcTvbPluginDialog
                                 A QGIS plugin
 ERC-TVB integrates ecological continuities in Avoid, Minimize, Mitigate sequence
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

import os, sys, shutil

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
    return applyProcessingAlg('erc_tvb','create_project',params,feedback=feedback)
def createGraphabLinkset(project,name,frictionPath,feedback=None):
    params = { 'CODE' : '',
        'EXTCOST' : frictionPath,
        'INPUT' : project,
        'NAME' : name,
        #'TYPE' : 1 }
        'TYPE' : 1 }
    return applyProcessingAlg('erc_tvb','create_linkset',params,feedback=feedback)
def createGraphabGraph(project,linkset,unit=0,dist=0,graphName="",
        feedback=None):
    params = { 'DIST' : dist,
        'DISTUNIT' : unit,
        'INPUT' : project,
        'NAMEGRAPH' : graphName,
        'NAMELINKSET' : linkset }
    return applyProcessingAlg('erc_tvb','create_graph',params,feedback=feedback)
def computeMetric(project,graphName,metricName=0,unit=0,
        d=1000,p=0,localMetric=True,feedback=None):
    params = { 'DISTUNIT' : unit,
        'DPARAMETER' : d,
        'GRAPHNAME' : graphName,
        'INPUT' : project,
        'METRICSNAME' : metricName,
        'PPARAMETER' : p }
    alg_name = 'local_metric' if localMetric else 'global_metric'
    return applyProcessingAlg('erc_tvb',alg_name,params,feedback=feedback)
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
    FIELDS = [ SCENARIO, SPECIE ]
    DISPLAY_FIELDS = FIELDS
    
    def __init__(self,dict,pluginModel=None,feedback=None):
        super().__init__(dict,feedback=feedback)
        self.pluginModel = pluginModel
        self.frictionFlag = False
        self.projectFlag = False
        self.linksetFlag = False
        self.graphFlag = False
        self.localFlag = False
        self.globalFlag = False
        
    @classmethod
    def fromValues(cls,scName,spName,pluginModel=None,feedback=None):
        dict = { cls.SCENARIO : scName, cls.SPECIE : spName }
        return cls(dict,pluginModel=pluginModel,feedback=feedback)
        
    def getScName(self):
        return self.dict[self.SCENARIO]
    def getSpName(self):
        return self.dict[self.SPECIE]
    # def getNameSuffix(self,suffix):
        # res = self.scName + "_" + self.spName + "_" + suffix
        # return res
    # def getBaseDir(self):
        # scDir = self.pluginModel.getSubDir(self.scName)
        # spDir = self.pluginModel.getSubDir(self.spName,baseDir=scDir)
        # return spDir
    # def getOutBase(self,suffix):
        # spDir = self.getBaseDir()
        # out_bname = self.getNameSuffix(suffix) + ".tif"
        # return joinPath(spDir,out_bname)
    # def getLandusePath(self):
        # return self.getOutBase("landuse")
    # def getFrictionPath(self):
        # return self.getOutBase("friction")
    # def getProjectName(self):
        # return self.getNameSuffix("graphab")
    # def getProjectDir(self):
        # spDir = self.getBaseDir()
        # out_bname = self.getProjectName()
        # return joinPath(spDir,out_bname)
    # def getProjectPath(self):
        # baseDir = self.getProjectDir()
        # out_bname = self.getProjectName() + ".xml"
        # return joinPath(baseDir,out_bname)
    # def getLinksetName(self):
        # return self.getNameSuffix("linkset")
    # def getGraphName(self):
        # return self.getNameSuffix("graph")

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
    def scExists(self,name):
        i = self.getItemFromName(name)
        return (i is not None)
                        
    # Returns absolute path of 'item' output layer
    # def getItemSubElement
    # def getScenarioDir(self,name)
    def normPath(self,fname):
        return os.path.normcase(fname)
    def getItemNameSuffix(self,scName,spName,suffix):
        res = scName + "_" + spName + "_" + suffix
        return res
    def getItemSpDir(self,spName):
        spDir = self.pluginModel.getSubDir(spName)
        return self.normPath(spDir)
    def getItemExtentScDir(self,scItem,spItem):
        extentSc = self.pluginModel.scenarioModel.getItemExtentSc(scItem)
        extentScName, spName = extentSc.getName(), spItem.getName()
        spDir = self.getItemSpDir(spName)
        return self.normPath(joinPath(spDir,extentScName))
    def getItemExtentPath(self,scItem,spItem):
        extentDir = self.getItemExtentScDir(scItem,spItem)
        return self.normPath(joinPath(extentDir,"extent.shp"))
    def getItemBaseDir(self,scItem,spItem):
        extentDir = self.getItemExtentScDir(scItem,spItem)
        scName = scItem.getName()
        itemDir = self.pluginModel.getSubDir(scName,baseDir=extentDir)
        return self.normPath(itemDir)
    def getItemOutBase(self,scItem,spItem,suffix=""):
        spDir = self.getItemBaseDir(scItem,spItem)
        scName, spName = scItem.getName(), spItem.getName()
        out_bname = scName + "_" + spName+ "_" + suffix + ".tif"
        return self.normPath(joinPath(spDir,out_bname))
    def getSpBaseLanduse(self,spItem):
        return self.pluginModel.speciesModel.getItemLandusePath(spItem)
        
    def computeItemExtent(self,scItem,spItem):
        scName, spName = scItem.getName(), spItem.getName()
        self.feedback.pushDebugInfo("sc Item " + str(scItem))
        # assert(False)
        extentScLayer = self.pluginModel.scenarioModel.getItemExtentScLayer(scItem)
        if extentScLayer is None:
        spLanduse = self.getSpBaseLanduse(spItem)
        out_path = self.getItemExtentPath(scItem,spItem)
        if spItem.isBufferMode():
            # bufferVal = float(spItem.getExtentVal
            bufferMulVal, maxDisp = float(spItem.getExtentVal()), int(spItem.getMaxDisp())
            if bufferMulVal == 0:
                self.feedback.user_error("Empty buffer for specie " + str(spName))
            if maxDisp == 0:
                self.feedback.user_error("Empty dispersal distance for specie " + str(spName))
            bufferVal = bufferMulVal * maxDisp
            extent = qgsTreatments.applyBufferFromExpr(extentScLayer,
                bufferVal,out_path,feedback=self.feedback)
        elif spItem.isMaxExtentMode():
            shutil.copy(extentScLayer,out_path)
        elif spItem.isCustomLauerMode():
            self.internal_error("Custom extent layer mode not implemented yet")
        else:
            assert(False)
        return out_path
    def getItemLanduse(self,scItem,spItem):
        # scItem = self.pluginModel.scenarioModel.getItemFromName(scName)
        scName, spName = scItem.getName(), spItem.getName()
        if not scItem:
            self.feedback.internal_error("No scenario found for " + str(scName))
        if scItem is None:
            self.feedback.internal_error("No scenario named " + str(scName))
        if scItem.isInitialState():
            path = self.getSpBaseLanduse(spItem)
        elif scItem.isLanduseMode():
            base = scItem.getBase()
            path = self.pluginModel.getDataOutPathFromName(base)
        elif scItem.isStackedMode():
            path = self.getItemOutBase(scItem,spItem,suffix="landuse")
        else:
            self.feedback.internal_error("Unexpected scenario mode : "
                + str(scItem.getMode()))
        return path
    def getItemFriction(self,scItem,spItem):
        return self.getItemOutBase(scItem,spItem,suffix="friction")
    def getItemGraphabProjectName(self,scItem,spItem):
        scName, spName = scItem.getName(), spItem.getName()
        return self.getItemNameSuffix(scName,spName,"graphab")
    def getItemGraphabProjectDir(self,scItem,spItem):
        spDir = self.getItemBaseDir(scItem,spItem)
        out_bname = self.getItemGraphabProjectName(scItem,spItem)
        return self.normPath(joinPath(spDir,out_bname))
    def getItemGraphabProjectFile(self,scItem,spItem):
        baseDir = self.getItemGraphabProjectDir(scItem,spItem)
        out_bname = self.getItemGraphabProjectName(scItem,spItem) + ".xml"
        return self.normPath(joinPath(baseDir,out_bname))
    def getItemLinksetName(self,scName,spName):
        return self.getItemNameSuffix(scName,spName,"linkset")
    def getItemGraphName(self,scName,spName):
        return self.getItemNameSuffix(scName,spName,"graph")
        
    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled
        
    def reload(self):
        for scItem in self.pluginModel.scenarioModel.items:
            scName = scItem.getName()
            for spItem in self.pluginModel.speciesModel.items:
                spName = spItem.getName()
                launchItem = LaunchItem.fromValues(scName,spName,
                    pluginModel=self.pluginModel,feedback=self.feedback)
                self.addItem(launchItem)
        self.layoutChanged.emit()
        # self.feedback.internal_error("reload not yet implemented")
    
    # def applyItemWithContext(self,scItem,context,feedback):
        # feedback.pushDebugInfo("applyItemWithContext")
        # name = scItem.getName()
        # if scItem.getStatusLanduse():
            # msg = self.tr("Landuse layer already computed for scenario ")
            # feedback.pushWarning(msg + str(name))
            # return
        # in_path = self.pluginModel.getOrigPath(scItem.getLayer())
        # out_path = self.getItemLanduse(scItem)
        # if scItem.isLanduseMode():
            # crs, extent, resolution = self.pluginModel.getRasterParams()
            # self.pluginModel.paramsModel.normalizeRaster(
                # in_path,out_path=out_path,
                # context=context,
                # feedback=feedback)
        # else:
            # assert(False)
        
    def applyItemLanduse(self, scItem, spItem,feedback=None):
        if feedback is None:
            feedback = self.feedback
        feedback.pushDebugInfo("applyItemLanduse " + str(scItem))
        scName, spName = scItem.getName(), spItem.getName()
        if scItem.getStatusLanduse():
            msg = self.tr("Landuse layer already computed for scenario ")
            feedback.pushWarning(msg + str(scName))
            return
        base = scItem.getBase()
        baseItem = self.getScItemFromName(base)
        # in_path = self.pluginModel.getOrigPath(scItem.getLayer())
        spLanduse = self.getSpBaseLanduse(spItem)
        out_path = self.getItemLanduse(scItem,spItem)
        # out_path = QgsProcessingUtils.generateTempFilename("out.tif")
        # out_path2 = QgsProcessingUtils.generateTempFilename("out2.tif")
        # out_gpkg = QgsProcessingUtils.generateTempFilename("out.gpkg")
        # out_shp = QgsProcessingUtils.generateTempFilename("out.shp")
        crs, extent, resolution = self.pluginModel.getRasterParams()
        baseType, nodataVal = self.pluginModel.baseType, self.pluginModel.nodataVal
        if scItem.isInitialState() or scItem.isLanduseMode():
            luPath = spLanduse
        # elif scItem.isLanduseMode():
            # self.feedback.pushDebugInfo("LU1")
            # in_path = self.pluginModel.getDataOutPathFromName(base)
            # if not utils.fileExists(in_path):
                # feedback.user_error("File '"+ str(in_path) + " does not exist"
                    # + ", launch " + str(base) + " in step 2")
        elif scItem.isStackedMode():
            self.feedback.pushDebugInfo("LU2")
            luPath = QgsProcessingUtils.generateTempFilename(spName + "_landuse.tif")
            qgsUtils.removeLayerFromPath(luPath)
            qgsUtils.removeRaster(luPath)
            # baseItem = self.pluginModel.scenarioModel.getItemFromName(base)
            in_path = self.getItemLanduse(baseItem,spItem)
            if not utils.fileExists(in_path):
                feedback.user_error("File '"+ str(in_path) + " does not exist"
                    + ", launch scenario " + str(base) + " landuse")
            # Rasterize
            vector_rel_path = scItem.getLayer()
            vector_path = self.pluginModel.getOrigPath(vector_rel_path)
            raster_path = qgsUtils.mkTmpPath(scName + "_raster.tif")
            mode = scItem.getMode()
            if scItem.isFixedMode():
                # Fixed mode
                qgsTreatments.applyRasterization(vector_path,raster_path,
                    extent,resolution,burn_val=scItem.getBurnVal(),
                    nodata_val=nodataVal,out_type=baseType,feedback=feedback)
                path = raster_path
            elif scItem.isFieldMode():
                # Field mode
                reclass_path = qgsUtils.mkTmpPath(scName + "_reclass.tif")
                qgsTreatments.applyRasterization(vector_path,raster_path,
                    extent,resolution,field=scItem.getBurnField(),
                    nodata_val=nodataVal,out_type=baseType,feedback=feedback)
                qgsTreatments.applyReclassifyByTable(raster_path,
                    scItem.getReclassTable(),reclass_path,
                    boundaries_mode=2,feedback=feedback)
                path = reclass_path
            else:
                feedback.user_error("Unexpected scenario mode : " + str(mode))
                # Reclassify
            # Merge
            paths = [in_path, path]
            qgsTreatments.applyMergeRaster(paths,luPath,#nodata_input=0,
                out_type=baseType,nodata_val=nodataVal,feedback=feedback)
        extentPath = self.getItemExtentPath(scItem,spItem)
        if utils.fileExists(extentPath):
            qgsUtils.removeVectorLayer(extentPath)
        self.computeItemExtent(scItem,spItem)
        qgsUtils.removeLayerFromPath(out_path)
        qgsUtils.removeRaster(out_path)
        dst_crs = self.pluginModel.paramsModel.getCrsStr()
        qgsTreatments.clipRasterFromVector(luPath,extentPath,out_path,
            resolution=resolution,nodata=nodataVal,
            feedback=feedback)
        # qgsTreatments.clipRasterAllTouched(luPath,extentPath,dst_crs,
            # out_path=out_path,feedback=self.feedback)
        # extentRasterPath = qgsUtils.mkTmpPath(scName + "_" + spName + "_extent_raster.tif")
        # extentExtent = qgsUtils.getExtentStrFromPath(extentPath)
        # qgsTreatments.applyRasterization(extentPath,out_path,
            # extentExtent,resolution,
            # burn_val=1,nodata_val=255,out_type=Qgis.Byte,
            # feedback=feedback)
        qgsUtils.loadRasterLayer(out_path,loadProject=True)
         
    def applyItemFriction(self, scItem,species,feedback=None):
        if feedback is None:
            feedback = self.feedback
        feedback.pushDebugInfo("applyItemFriction")
        name = scItem.getName()
        if scItem.getStatusFriction():
            msg = self.tr("Friction layer already computed for scenario ")
            feedback.pushWarning(msg + str(name))
        else:
            # Reclassify
            baseType, nodataVal = self.pluginModel.baseType, self.pluginModel.nodataVal
            frictionModel = self.pluginModel.frictionModel
            species_names = [sp.getName() for sp in species]
            reclass_matrixes = frictionModel.getReclassifyMatrixes(species_names)
            nb_items = len(reclass_matrixes)
            step_feedback = feedbacks.ProgressMultiStepFeedback(nb_items,feedback)
            cpt=0
            for specie, matrix in reclass_matrixes.items():
                spItem = self.getSpItemFromName(specie)
                feedback.pushDebugInfo("specie = " + str(specie))
                feedback.pushDebugInfo("matrix = " + str(matrix))
                in_path = self.getItemLanduse(scItem,spItem)
                feedback.pushDebugInfo("in_path = " + str(in_path))
                out_path = self.getItemFriction(scItem,spItem)
                feedback.pushDebugInfo("out_path = " + str(out_path))
                qgsUtils.removeLayerFromPath(out_path)
                inVals = qgsUtils.getRasterValsFromPath(in_path)
                mInVals, mOutVals = matrix[::3], matrix[2::3]
                feedback.pushDebugInfo("mInVals = " + str(mInVals))
                feedback.pushDebugInfo("mOutVals = " + str(mOutVals))
                naVals = [inV for inV, outV in zip(mInVals,mOutVals) if inV in inVals and outV == 0]
                self.feedback.pushWarning(self.tr("No friction value assigned to classes ") + str(naVals))
                qgsTreatments.applyReclassifyByTable(in_path,matrix,out_path,
                    out_type=baseType,nodata_val=nodataVal,boundaries_mode=2,
                    feedback=step_feedback)
                loaded_layer = qgsUtils.loadRasterLayer(out_path,loadProject=True)
                styles.setRendererPalettedGnYlRd(loaded_layer)
                cpt+=1
                step_feedback.setCurrentStep(cpt)
            
    #{ 'DIRPATH' : 'TEMPORARY_OUTPUT', 'INPUT' : 'D:/IRSTEA/ERC/tests/BousquetOrbExtended/Source/CorineLandCover/CLC12_BOUSQUET_ORB.tif', 'LANDCODE' : '241', 'NAMEPROJECT' : 'Project1', 'NODATA' : None, 'SIZEPATCHES' : 0 }
    def applyItemGraphabProject(self, scItem,spItem,feedback=None):
        if feedback is None:
            feedback = self.feedback
        feedback.pushDebugInfo("applyItemGraph")
        scName, spName = scItem.getName(), spItem.getName()
        checkGraphabInstalled(feedback)
        projName = self.getItemGraphabProjectName(scItem,spItem)
        project = self.getItemGraphabProjectFile(scItem,spItem)
        landuse = self.getItemLanduse(scItem,spItem)
        friction = self.getItemFriction(scItem,spItem)
        codes = spItem.getCodesVal()
        if not codes:
            self.feedback.user_error("No habitat code specified for specie "
                + str(spName))
        minArea = spItem.getMinArea()
        outDir = self.getItemBaseDir(scItem,spItem)
        qgsUtils.removeGroup(projName)
        projectFolder = os.path.dirname(project)
        qgsUtils.removeFolder(projectFolder)
        createGraphabProject(landuse,codes,outDir,projName,
            nodata=-self.pluginModel.nodataVal,patch_size=minArea,feedback=feedback)


    def applyItemGraphabLinkset(self, scItem,spItem,feedback=None):
        if feedback is None:
            feedback = self.feedback
        feedback.pushDebugInfo("applyItemGraphabLinkset")
        scName, spName = scItem.getName(), spItem.getName()
        checkGraphabInstalled(feedback)
        projName = self.getItemGraphabProjectName(scItem,spItem)
        project = self.getItemGraphabProjectFile(scItem,spItem)
        linksetName = self.getItemLinksetName(scName,spName)
        friction = self.getItemFriction(scItem,spItem)
        self.pluginModel.loadProject(project)
        gProj = self.pluginModel.graphabPlugin.getProject(projName)
        if gProj:
            print("gproj")
            gProj.removeLinkset(linksetName)
        # assert(False)
        classes,array,nodata = qgsUtils.getRasterValsArrayND(friction)
        feedback.pushDebugInfo("classes = " + str(classes))
        feedback.pushDebugInfo("nodata = " + str(nodata))
        createGraphabLinkset(project,linksetName,friction,feedback=feedback)
            
            
    def applyItemGraphabGraph(self, scItem,spItem,feedback=None):
        if feedback is None:
            feedback = self.feedback
        feedback.pushDebugInfo("applyItemGraphabGraph")
        scName, spName = scItem.getName(), spItem.getName()
        maxDisp = spItem.getMaxDisp()
        checkGraphabInstalled(feedback)
        projName = self.getItemGraphabProjectName(scItem,spItem)
        project = self.getItemGraphabProjectFile(scItem,spItem)
        graphName = self.getItemGraphName(scName,spName)
        linksetName = self.getItemLinksetName(scName,spName)
        self.pluginModel.loadProject(project)
        gProj = self.pluginModel.graphabPlugin.getProject(projName)
        if gProj:
            print("grpoj")
            gProj.removeGraph(graphName)
        createGraphabGraph(project,linksetName,
            dist=maxDisp,graphName=graphName,feedback=feedback)
                
    def computeLocalMetric(self,scItem,spItem,feedback=None):
        if feedback is None:
            feedback = self.feedback
        scName, spName = scItem.getName(), spItem.getName()
        project = self.getItemGraphabProjectFile(scItem,spItem)
        graphName = self.getItemGraphName(scName,spName)
        self.pluginModel.loadProject(project)
        l, g, d, p = self.pluginModel.paramsModel.getGraphabParams()
        self.feedback.pushDebugInfo("l = " + str(l))
        computeLocalMetric(project,graphName,metricName=l,d=d,p=p,feedback=feedback)
                
    def computeGlobalMetric(self,scItem,spItem,feedback=None):
        if feedback is None:
            feedback = self.feedback
        scName, spName = scItem.getName(), spItem.getName()
        project = self.getItemGraphabProjectFile(scItem,spItem)
        graphName = self.getItemGraphName(scName,spName)
        self.pluginModel.loadProject(project)
        l, g, d, p = self.pluginModel.paramsModel.getGraphabParams()
        return computeGlobalMetric(project,graphName,metricName=g,d=d,p=p,feedback=feedback)
        
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
    # def iterateRunExtent(self,func):
        # scenarios = self.getSelectedScenarios()
        # scMap = {}
        # for sc in scenarios:
            # baseSc = self.pluginModel.scenarioModel.getItemExtentSc(sc)
            # if baseSc in scMap:
                # scMap[baseSc] += sc
            # else:
                # scMap[baseSc] = [sc]
        # for baseSc, scenarios in scMap:
            # isSc = self.pluginModel.scenarioModel.mkInitialState()
            # scenarios.insert(0,isSc)
        # species = self.getSelectedSpecies()
        # nb_steps = len(scenarios) * len(species)
        # step_feedback = feedbacks.ProgressMultiStepFeedback(nb_steps,self.feedback)
        # cpt=0
        # step_feedback.setCurrentStep(cpt)
        # for sc in scenarios:
            # self.feedback.pushDebugInfo("sc " + str(sc))
            # for sp in species:
                # func(sc,sp,feedback=step_feedback)
                # cpt+=1
                # step_feedback.setCurrentStep(cpt)
        
    def landuseRun(self):
        self.feedback.beginSection("Computing land use layer(s)")
        self.iterateRun(self.model.applyItemLanduse)
        self.feedback.endSection()
        
    def frictionRun(self):
        self.feedback.beginSection("Computing friction layer(s)")
        scenarios = self.getSelectedScenarios()
        species = self.getSelectedSpecies()
        step_feedback = feedbacks.ProgressMultiStepFeedback(len(scenarios),self.feedback)
        for cpt, sc in enumerate(scenarios,start=1):
            self.model.applyItemFriction(sc,species,feedback=step_feedback)
            step_feedback.setCurrentStep(cpt)
        self.feedback.endSection()
            # for sp in species:
                # self.feedback.pushDebugInfo("TODO : friction Run "
                    # + sc.getName() + " - " + sp.getName())
    def graphabProjectRun(self):
        self.feedback.beginSection("Creating Graphab project(s)")
        self.iterateRun(self.model.applyItemGraphabProject)
        self.feedback.endSection()
    def graphabLinksetRun(self):
        self.feedback.beginSection("Creating linkset(s)")
        self.iterateRun(self.model.applyItemGraphabLinkset)
        self.feedback.endSection()
    def graphabGraphRun(self):
        self.feedback.beginSection("Creating graphs(s)")
        self.iterateRun(self.model.applyItemGraphabGraph)
        self.feedback.endSection()
    def computeLocalMetric(self):
        self.feedback.beginSection("Computing local metric(s)")
        self.iterateRun(self.model.computeLocalMetric)
        self.feedback.endSection()
    def computeGlobalMetric(self):
        self.feedback.beginSection("Computing global metric(s)")
        scenarios = self.getSelectedScenarios()
        species = self.getSelectedSpecies()
        nb_steps = len(scenarios) * len(species)
        step_feedback = feedbacks.ProgressMultiStepFeedback(nb_steps,self.feedback)
        # res = { sc.getName() : {sp.getName() : None for sp in species} for sc in scenarios }
        values = {}
        cpt = 0
        for sc in scenarios:
            values[sc.getName()] = {} 
            for sp in species:
                val = self.model.computeGlobalMetric(sc,sp,
                    feedback=step_feedback) 
                values[sc.getName()][sp.getName()] = val
                cpt+=1
                step_feedback.setCurrentStep(cpt)
        self.feedback.endSection()
        window = PlotWindow(values,self.feedback)
        window.show()
        while window.exec_():
            pass


