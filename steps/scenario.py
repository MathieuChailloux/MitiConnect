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

from ..qgis_lib_mc.utils import CustomException, joinPath
from ..qgis_lib_mc.abstract_model import DictItem, DictModel, TableToDialogConnector, CheckableComboDelegate
# from ..algs.erc_tvb_algs_provider import ErcTvbAlgorithmsProvider
from ..qgis_lib_mc.qgsTreatments import applyProcessingAlg
from ..qgis_lib_mc import qgsTreatments, qgsUtils, feedbacks, styles
from ..ui.scenario_dialog import ScenarioItem, ScenarioDialog, ScenarioLanduseDialog
from ..ui.plot_window import PlotWindow

# Graphab utils

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
        'SIZEPATCHES' : 0 }
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
    params = { 'DISTUNIT' : 0,
        'DPARAMETER' : d,
        'GRAPHNAME' : graphName,
        'INPUT' : project,
        'METRICSNAME' : 0,
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
        


class GraphabWrapper:
    
    def __init__(self, pluginModel,scItem,spItem):
        self.pluginModel = pluginModel
        self.scItem = scItem
        self.spItem = spItem
        self.scName = scItem.getName()
        self.spName = scItem.getName()
        self.frictionFlag = False
        self.projectFlag = False
        self.linksetFlag = False
        self.graphFlag = False
        self.localFlag = False
        self.globalFlag = False
        
    def getNameSuffix(self,suffix):
        res = self.scName + "_" + self.spName + "_" + suffix
        return res
    def getBaseDir(self):
        scDir = self.pluginModel.getSubDir(self.scName)
        spDir = self.pluginModel.getSubDir(self.spName,baseDir=scDir)
        return spDir
    def getOutBase(self,suffix):
        spDir = self.getBaseDir()
        out_bname = self.getNameSuffix(suffix) + ".tif"
        return joinPath(spDir,out_bname)
    def getLandusePath(self):
        return self.getOutBase("landuse")
    def getFrictionPath(self):
        return self.getOutBase("friction")
    def getProjectName(self):
        return self.getNameSuffix("graphab")
    def getProjectDir(self):
        spDir = self.getBaseDir()
        out_bname = self.getProjectName()
        return joinPath(spDir,out_bname)
    def getProjectPath(self):
        baseDir = self.getProjectDir()
        out_bname = self.getProjectName() + ".xml"
        return joinPath(baseDir,out_bname)
    def getLinksetName(self):
        return self.getNameSuffix("linkset")
    def getGraphName(self):
        return self.getNameSuffix("graph")

# Scenario
        
class ScenarioModel(DictModel):

    def __init__(self, pluginModel):
        itemClass = getattr(sys.modules[__name__], ScenarioItem.__name__)
        super().__init__(itemClass,
            feedback=pluginModel.feedback,
            fields=ScenarioItem.FIELDS,
            display_fields=ScenarioItem.DISPLAY_FIELDS)
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
    def getItemBaseDir(self,scName,spName):
        scDir = self.pluginModel.getSubDir(scName)
        spDir = self.pluginModel.getSubDir(spName,baseDir=scDir)
        return self.normPath(spDir)
    def getItemOutBase(self,scName,spName,suffix=""):
        spDir = self.getItemBaseDir(scName,spName)
        out_bname = scName + "_" + spName+ "_" + suffix + ".tif"
        return self.normPath(joinPath(spDir,out_bname))
    def getItemLanduse(self,scName,spName):
        return self.getItemOutBase(scName,spName,suffix="landuse")
    def getItemFriction(self,scName,spName):
        return self.getItemOutBase(scName,spName,suffix="friction")
    def getItemGraphabProjectName(self,scName,spName):
        return self.getItemNameSuffix(scName,spName,"graphab")
    def getItemGraphabProjectDir(self,scName,spName):
        spDir = self.getItemBaseDir(scName,spName)
        out_bname = self.getItemGraphabProjectName(scName,spName)
        return self.normPath(joinPath(spDir,out_bname))
    def getItemGraphabProjectFile(self,scName,spName):
        baseDir = self.getItemGraphabProjectDir(scName,spName)
        out_bname = self.getItemGraphabProjectName(scName,spName) + ".xml"
        return self.normPath(joinPath(baseDir,out_bname))
    def getItemLinksetName(self,scName,spName):
        return self.getItemNameSuffix(scName,spName,"linkset")
    def getItemGraphName(self,scName,spName):
        return self.getItemNameSuffix(scName,spName,"graph")
        
    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled
        
    
    def applyItemWithContext(self,scItem,context,feedback):
        feedback.pushDebugInfo("applyItemLanduse")
        name = scItem.getName()
        if scItem.getStatusLanduse():
            msg = self.tr("Landuse layer already computed for scenario ")
            feedback.pushWarning(msg + str(name))
            return
        in_path = self.pluginModel.getOrigPath(scItem.getLayer())
        out_path = self.getItemLanduse(scItem)
        # out_path = 'C:/Users/mathieu.chailloux/Desktop/BousquetOrbExtended\\dummy.tif'
        if scItem.isLanduseMode():
            crs, extent, resolution = self.pluginModel.getRasterParams()
            self.pluginModel.paramsModel.normalizeRaster(
                in_path,out_path=out_path,
                context=context,
                feedback=feedback)
        else:
            assert(False)
        
    def applyItemLanduse(self, scItem, spItem,feedback=None):
        if feedback is None:
            feedback = self.feedback
        feedback.pushDebugInfo("applyItemLanduse " + str(scItem))
        name = scItem.getName()
        spName = spItem.getName()
        if scItem.getStatusLanduse():
            msg = self.tr("Landuse layer already computed for scenario ")
            feedback.pushWarning(msg + str(name))
            return
        base = scItem.getBase()
        # in_path = self.pluginModel.getOrigPath(scItem.getLayer())
        out_path = self.getItemLanduse(name,spName)
        # out_path = QgsProcessingUtils.generateTempFilename("out.tif")
        # out_path2 = QgsProcessingUtils.generateTempFilename("out2.tif")
        # out_gpkg = QgsProcessingUtils.generateTempFilename("out.gpkg")
        # out_shp = QgsProcessingUtils.generateTempFilename("out.shp")
        crs, extent, resolution = self.pluginModel.getRasterParams()
        if scItem.isLanduseMode():
            in_path = self.pluginModel.getLanduseOutLayerFromName(base)
            feedback.pushDebugInfo("Copying " + in_path + " to " + out_path)
            shutil.copy(in_path,out_path)
            # self.pluginModel.paramsModel.normalizeRaster(
                # in_path,out_path=out_path,
                # context=context,
                # feedback=self.feedback)

            # assert(False)
        else:
            baseItem = self.getItemFromName(base)
            in_path = self.getItemLanduse(base,spName)
            # Rasterize
            vector_rel_path = scItem.getLayer()
            vector_path = self.pluginModel.getOrigPath(vector_rel_path)
            raster_path = qgsUtils.mkTmpPath(name + "_raster.tif")
            mode = scItem.getMode()
            if mode == 1:
                # Fixed mode
                qgsTreatments.applyRasterization(vector_path,raster_path,
                    extent,resolution,burn_val=scItem.getBurnVal(),
                    feedback=feedback)
                path = raster_path
            elif mode == 2:
                # Field mode
                reclass_path = qgsUtils.mkTmpPath(name + "_reclass.tif")
                qgsTreatments.applyRasterization(vector_path,raster_path,
                    extent,resolution,field=scItem.getBurnField(),
                    feedback=feedback)
                qgsTreatments.applyReclassifyByTable(raster_path,
                    scItem.getReclassTable(),reclass_path,
                    feedback=feedback)
                path = reclass_path
            else:
                feedback.user_error("Unexpected scenario mode : " + str(mode))
                # Reclassify
            # Merge
            paths = [in_path, path]
            qgsTreatments.applyMergeRaster(paths,out_path,
                out_type=Qgis.Int16,feedback=feedback)
        qgsUtils.loadRasterLayer(out_path,loadProject=True)
         
    def applyItemFriction(self, item,species,feedback=None):
        if feedback is None:
            feedback = self.feedback
        feedback.pushDebugInfo("applyItemFriction")
        name = item.getName()
        if item.getStatusFriction():
            msg = self.tr("Friction layer already computed for scenario ")
            feedback.pushWarning(msg + str(name))
        else:
            # Reclassify
            frictionModel = self.pluginModel.frictionModel
            species_names = [sp.getName() for sp in species]
            reclass_matrixes = frictionModel.getReclassifyMatrixes(species_names)
            nb_items = len(reclass_matrixes)
            step_feedback = feedbacks.ProgressMultiStepFeedback(nb_items,feedback)
            cpt=0
            for specie, matrix in reclass_matrixes.items():
                feedback.pushDebugInfo("specie = " + str(specie))
                feedback.pushDebugInfo("matrix = " + str(matrix))
                in_path = self.getItemLanduse(name,specie)
                feedback.pushDebugInfo("in_path = " + str(in_path))
                out_path = self.getItemFriction(name,specie)
                feedback.pushDebugInfo("out_path = " + str(out_path))
                nodata = 65535
                inVals = qgsUtils.getRasterValsFromPath(in_path)
                mInVals, mOutVals = matrix[::3], matrix[2::3]
                feedback.pushDebugInfo("mInVals = " + str(mInVals))
                feedback.pushDebugInfo("mOutVals = " + str(mOutVals))
                naVals = [inV for inV, outV in zip(mInVals,mOutVals) if inV in inVals and outV == 0]
                self.feedback.pushWarning(self.tr("No friction value assigned to classes ") + str(naVals))
                qgsTreatments.applyReclassifyByTable(in_path,matrix,out_path,
                    out_type=Qgis.UInt16,nodata_val=65535,boundaries_mode=2,
                    feedback=step_feedback)
                loaded_layer = qgsUtils.loadRasterLayer(out_path,loadProject=True)
                styles.setRendererPalettedGnYlRd(loaded_layer)
                cpt+=1
                step_feedback.setCurrentStep(cpt)
            
    #{ 'DIRPATH' : 'TEMPORARY_OUTPUT', 'INPUT' : 'D:/IRSTEA/ERC/tests/BousquetOrbExtended/Source/CorineLandCover/CLC12_BOUSQUET_ORB.tif', 'LANDCODE' : '241', 'NAMEPROJECT' : 'Project1', 'NODATA' : None, 'SIZEPATCHES' : 0 }
    def applyItemGraphabProject(self, item,spItem,feedback=None):
        if feedback is None:
            feedback = self.feedback
        feedback.pushDebugInfo("applyItemGraph")
        name = item.getName()
        spName = spItem.getName()
        checkGraphabInstalled(feedback)
        projectName = self.getItemGraphabProjectName(name,spName)
        project = self.getItemGraphabProjectFile(name,spName)
        landuse = self.getItemLanduse(name,spName)
        friction = self.getItemFriction(name,spName)
        codes = spItem.getCodes()
        minArea = spItem.getMinArea()
        outDir = self.getItemBaseDir(name,spName)
        nodata = 65535
        createGraphabProject(landuse,codes,outDir,projectName,
            nodata=-nodata,patch_size=minArea,feedback=feedback)


    def applyItemGraphabLinkset(self, item,spItem,feedback=None):
        if feedback is None:
            feedback = self.feedback
        feedback.pushDebugInfo("applyItemGraphabLinkset")
        name = item.getName()
        spName = spItem.getName()
        checkGraphabInstalled(feedback)
        projName = self.getItemGraphabProjectName(name,spName)
        project = self.getItemGraphabProjectFile(name,spName)
        linksetName = self.getItemLinksetName(name,spName)
        friction = self.getItemFriction(name,spName)
        gProj = self.pluginModel.loadProject(project,retFlag=True)
        gProj = self.pluginModel.graphabPlugin.getProject(projName)
        if gProj:
            print("gproj")
            gProj.removeLinkset(linksetName)
        # assert(False)
        classes,array,nodata = qgsUtils.getRasterValsArrayND(friction)
        feedback.pushDebugInfo("classes = " + str(classes))
        feedback.pushDebugInfo("nodata = " + str(nodata))
        createGraphabLinkset(project,linksetName,friction,feedback=feedback)
            
            
    def applyItemGraphabGraph(self, item,spItem,feedback=None):
        if feedback is None:
            feedback = self.feedback
        feedback.pushDebugInfo("applyItemGraphabGraph")
        name = item.getName()
        spName = spItem.getName()
        checkGraphabInstalled(feedback)
        project = self.getItemGraphabProjectFile(name,spName)
        graphName = self.getItemGraphName(name,spName)
        linksetName = self.getItemLinksetName(name,spName)
        self.pluginModel.loadProject(project)
        createGraphabGraph(project,linksetName,
            graphName=graphName,feedback=feedback)
                
    def computeLocalMetric(self,item,spItem,feedback=None):
        if feedback is None:
            feedback = self.feedback
        name = item.getName()
        spName = spItem.getName()
        project = self.getItemGraphabProjectFile(name,spName)
        graphName = self.getItemGraphName(name,spName)
        self.pluginModel.loadProject(project)
        computeLocalMetric(project,graphName,feedback=feedback)
                
    def computeGlobalMetric(self,item,spItem,feedback=None):
        if feedback is None:
            feedback = self.feedback
        name = item.getName() 
        spName = spItem.getName()
        project = self.getItemGraphabProjectFile(name,spName)
        graphName = self.getItemGraphName(name,spName)
        self.pluginModel.loadProject(project)
        return computeGlobalMetric(project,graphName,feedback=feedback)
        
    def removeItems(self,indexes):
        names = [self.items[ind.row()].getName() for ind in indexes]
        super().removeItems(indexes)
        self.pluginModel.removeImports(names)

class ScenarioConnector(TableToDialogConnector):

    def __init__(self,dlg,model):
        self.dlg = dlg
        self.feedback = dlg.feedback
        super().__init__(model,self.dlg.scenarioView,
                         addButton=self.dlg.scenarioAdd,
                         removeButton=self.dlg.scenarioRemove)
        # super().__init__(model,self.dlg.scenarioView,
                         # addButton=self.dlg.scenarioAdd,
                         # removeButton=self.dlg.scenarioRemove,
                         # runButton=self.dlg.scLanduseRun)

    def refreshSpecies(self):   
        names = self.model.pluginModel.speciesModel.getNames()
        self.dlg.speciesSelection.clear()
        self.dlg.speciesSelection.insertItems(0,names)

    def connectComponents(self):
        super().connectComponents()
        self.dlg.scenarioUp.clicked.connect(self.upgradeItem)
        self.dlg.scenarioDown.clicked.connect(self.downgradeItem)
        self.dlg.scenarioAddLanduse.clicked.connect(self.openDialogLanduseNew)
        self.model.pluginModel.speciesModel.layoutChanged.connect(self.refreshSpecies)
        # speciesNames = [s.getName() for si in self.model.pluginModel.speciesModel.items]
        # self.dlg.speciesSelection.addItems(speciesNames)
        # model = CheckableComboDelegate(self.model.pluginModel.speciesModel)
        # self.dlg.speciesSelection.setModel(model)
        self.dlg.scLanduseRun.clicked.connect(self.landuseRun)
        self.dlg.scFrictionRun.clicked.connect(self.frictionRun)
        self.dlg.scProjectRun.clicked.connect(self.graphabProjectRun)
        self.dlg.scLinksetRun.clicked.connect(self.graphabLinksetRun)
        self.dlg.scGraphRun.clicked.connect(self.graphabGraphRun)
        self.dlg.localMetricsRun.clicked.connect(self.computeLocalMetric)
        self.dlg.compareScenariosRun.clicked.connect(self.computeGlobalMetric)
        
    def getSelectedScenarios(self):
        indexes = self.view.selectedIndexes()
        if not indexes:
            self.feedback.user_error("No scenario selected")
        rows = list(set([i.row() for i in indexes]))
        res = [self.model.items[i] for i in rows]
        return res
        
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
            for sp in species:
                func(sc,sp,feedback=step_feedback)
                cpt+=1
                step_feedback.setCurrentStep(cpt)
        
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
        
    
    def preDlg(self,item):
        self.feedback.pushDebugInfo("preDlg = " + str(item))
        if item is not None:
            self.pathFieldToAbs(item,ScenarioItem.LAYER)
            # if item.isLanduseMode():
                 # self.pathFieldToAbs(item,ScenarioItem.BASE)

    def postDlg(self,dlg_item):
        self.feedback.pushDebugInfo("postDlg = " + str(dlg_item))
        if dlg_item is not None:
            self.pathFieldToRel(dlg_item,ScenarioItem.LAYER)
            # if dlg_item.isLanduseMode():
                 # self.pathFieldToRel(dlg_item,ScenarioItem.BASE)
            self.updateFrictionFromDlg(dlg_item)
    
    # def openDialog(self,item): 
        # self.feedback.pushDebugInfo("item = " + str(item))
        # if not item or item.getBase():
            # scenarioNames = self.model.getScenarioNames()
            # if not scenarioNames:
                # msg = self.tr("No scenario in model : please create base scenario from landuse")
                # self.feedback.user_error(msg)
            # scenarioDlg = ScenarioDialog(self.dlg,item,scenarioModel=self.model,feedback=self.feedback)
        # else:
            # scenarioDlg = ScenarioLanduseDialog(self.dlg,item.dlg_item)
        # return scenarioDlg
    def openDialog(self,item): 
        self.feedback.pushDebugInfo("item = " + str(item))
        # self.feedback.pushDebugInfo("itemBase = " + str(b))
        # self.feedback.pushDebugInfo("item = " + str(item is None))
        # self.feedback.pushDebugInfo("itemBase = " + str((b is None)))
        # if (item is None) or (item.getBase() is None):
        if (item is None):
            # Specific openDialogLanduseNew otherwise 
            luFlag = False
        else:
            luFlag = item.isLanduseMode()
        if not luFlag:
            self.feedback.pushDebugInfo("openDialog overlap")
            scenarioNames = self.model.getScenarioNames()
            if not scenarioNames:
                msg = self.tr("No scenario in model : please create base scenario from landuse")
                self.feedback.user_error(msg)
            item_copy = item.__deepcopy__() if item else None
            scenarioDlg = ScenarioDialog(self.dlg,item_copy,
                model=self.model.pluginModel,feedback=self.feedback)
            # scenarioDlg = ScenarioDialog(self.dlg,item,scenarioModel=self.model,feedback=self.feedback)
        else:
            self.feedback.pushDebugInfo("openDialog landuse")   
            scenarioDlg = ScenarioLanduseDialog(self.dlg,item,
                feedback=self.feedback,luModel=self.model.pluginModel.landuseModel)
        return scenarioDlg
                        
    def openDialogLanduseNew(self):
        item_dlg = ScenarioLanduseDialog(self.dlg,None,
            feedback=self.feedback,luModel=self.model.pluginModel.landuseModel)
        dlg_item = item_dlg.showDialog()
        if dlg_item:
            # item = self.mkItemFromDlgItem(dlg_item)
            # self.model.addItem(item)
            self.model.addItem(dlg_item)
            self.model.layoutChanged.emit()
            
    
    def updateFromDlgItem(self,item,dlg_item):
        item.updateFromDlgItem(dlg_item)
            
    # def mkItemFromDlgItem(self,dlg_item): 
        # return ScenarioItem(dlg_item,feedback=self.feedback)
        
    def updateFrictionFromDlg(self,item):
        if item:
            if item.isLanduseMode():
                pass
            elif item.isFixedMode():
                burnVal = str(item.getBurnVal())
                self.model.pluginModel.frictionModel.updateScenario(item.getName(),[""],[burnVal])
            elif item.isFieldMode():
                values, classes = item.reclassModel.getValuesAndClasses()
                self.model.pluginModel.frictionModel.updateScenario(item.getName(),values,classes)
            self.model.pluginModel.frictionModel.layoutChanged.emit()
        else:
            self.feedback.pushDebugInfo("Empty item")
        
     

        
