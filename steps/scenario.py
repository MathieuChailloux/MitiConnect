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
from ..ui.scenario_dialog import ScenarioItem, ScenarioDialog, ScenarioLanduseDialog, ScenarioInitialStateDialog
from ..ui.plot_window import PlotWindow

from . import friction

# Scenario
        
class ScenarioModel(DictModel):

    IS_NAME = "INIT"

    def __init__(self, pluginModel):
        itemClass = getattr(sys.modules[__name__], ScenarioItem.__name__)
        super().__init__(itemClass,
            feedback=pluginModel.feedback,
            fields=ScenarioItem.FIELDS,
            display_fields=ScenarioItem.DISPLAY_FIELDS)
        # super().__init__(self,itemClass,feedback=pluginModel.feedback,
            # display_fields=ScenarioItem.DISPLAY_FIELDS)
        self.pluginModel = pluginModel
        self.addInitialState()
        
    def getScenarioNames(self):
        return [i.getName() for i in self.items]
    def getNames(self):
        return self.getScenarioNames()
    def getItemFromName(self,name):
        for i in self.items:
            if i.getName() == name:
                return i
        return None
        
    def scExists(self,name):
        i = self.getItemFromName(name)
        return (i is not None)

    def getItemDegree(self,item,acc=0):
        base = item.getBase()
        if base is None:
            return acc
        baseItem = self.getItemFromName(base)
        return self.getItemDegree(baseItem,acc=acc+1)
    def getItemHierarchy(self,item,acc=[]):
        self.feedback.pushDebugInfo("getItemHierarchy " + item.getName() + " - " + str(len(acc)))
        if item.isInitialState():
            return acc
        else:
            base = item.getBase()
            baseItem = self.getItemFromName(base)
            acc = acc + [item]
            return self.getItemHierarchy(baseItem,acc=acc)
    def getItemExtentLayers(self,item,acc=[]):
        self.feedback.pushDebugInfo("getItemExtentLayers " + item.getName() + " - " + str(acc))
        if item.isInitialState():
            return acc
        if item.useExtent():
            relLayer = item.getLayer()
            if relLayer:
                absLayer = self.pluginModel.getOrigPath(relLayer)
                acc = acc + [absLayer]
            else:
                self.feedback.user_error("No layer for item " + str(item))
        base = item.getBase()
        baseItem = self.getItemFromName(base)
        return self.getItemExtentLayers(baseItem,acc=acc)
    def getItemExtentSc(self,item,acc=[]):
        # item = self.getItemFromName(itemName)
        if item.useExtent():
            return item
        elif item.isLeaf():
            return item
        else:
            childName = item.getBase()
            childItem = self.getItemFromName(childName)
            if childName in acc:
                self.internal_error("Scenario auto reference " + str(childName))
            acc += childName
            return self.getItemExtentSc(childItem,acc=acc)
    def getItemExtentScLayer(self,item):
        if not item:
            self.feedback.internal_error("No scenario " + str(item))
        extentSc = self.getItemExtentSc(item)
        self.feedback.pushDebugInfo("extentSc " + str(extentSc))
        self.feedback.pushDebugInfo("extentSc name " + str(extentSc.getName()))
        extentScPath = extentSc.getLayer()
        self.feedback.pushDebugInfo("extentScPath " + str(extentScPath))
        # if extentScPath == "None" or extentScPath is None:
            # assert(False)
        if extentScPath is not None:
            extentScAbsPath = self.pluginModel.getOrigPath(extentScPath)
            return extentScAbsPath
        else:
            return self.pluginModel.paramsModel.getExtentLayer()
    # def getItemSpExtentPath(self,item)
        # assert(False)
    def getInitialState(self):
        for i in self.items:
            if i.isInitialState():
                return i
        return None
    def mkInitialState(self):
        descr = self.tr("Initial state scenario")
        return ScenarioItem.fromValues(self.IS_NAME,mode=3,
            descr=descr,feedback=self.feedback)
    def addInitialState(self):
        self.feedback.pushDebugInfo("addINitialState")
        existingInit = self.getInitialState()
        if existingInit is None:
            item = self.mkInitialState()
            self.addItem(item)
        else:
            self.pushInfo("Ignoring addInitialState as it already exists")
            
    def addItem(self,item):
        for i in self.items:
            self.feedback.pushDebugInfo("i1 = " + str(i.getName()))
        if item.isInitialState():
            self.items = [i for i in self.items if not i.isInitialState()]
            for i in self.items:
                self.feedback.pushDebugInfo("i = " + str(i.getName()))
        super().addItem(item)
        for i in self.items:
            self.feedback.pushDebugInfo("i2 = " + str(i.getName()))
    def addScenarioFromLayer(self,name,layer):
        self.feedback.pushDebugInfo("addScenarioFromLayer")
        item = ScenarioItem.fromValues(name,base=layer,
            feedback=self.feedback)
        self.addItem(item)
        self.layoutChanged.emit()
        
    def rasterizeLayer(self,item,feedback=None):
        if feedback is None:
            feedback = self.feedback
        absLayerPath = self.pluginModel.getOrigPath(item.getLayer())
        crs, maxExtent, resolution = self.pluginModel.getRasterParams()
        name = item.getName()
        toNormPath = qgsUtils.mkTmpPath(name + "_toNorm.tif")
        outPath = qgsUtils.mkTmpPath(name + ".tif")
        mode = item.getMode()
        baseType, nodataVal = self.pluginModel.baseType, self.pluginModel.nodataVal
        # Reproject if needed
        absLayer = qgsUtils.loadVectorLayer(absLayerPath)
        if absLayer.crs() != crs:
            reprojected = qgsUtils.mkTmpPath(name + "_reprojected.gpkg")
            qgsTreatments.applyReprojectLayer(absLayerPath,crs,reprojected,feedback=feedback)
            absLayerPath = reprojected
        if item.isFixedMode():
            # Fixed mode
            qgsTreatments.applyRasterization(absLayerPath,toNormPath,
                maxExtent,resolution,burn_val=item.getBurnVal(),
                nodata_val=nodataVal,out_type=baseType,feedback=feedback)
        elif item.isFieldMode():
            # Field mode
            rasterPath = qgsUtils.mkTmpPath(name + "_raster.tif")
            qgsTreatments.applyRasterization(absLayerPath,rasterPath,
                maxExtent,resolution,field=item.getBurnField(),
                nodata_val=nodataVal,out_type=baseType,feedback=feedback)
            reclassTable = self.pluginModel.getReclassTable(name)
            qgsTreatments.applyReclassifyByTable(rasterPath,
                reclassTable,toNormPath,
                boundaries_mode=2,feedback=feedback)
        else:
            feedback.user_error("Unexpected scenario mode : " + str(mode))
        self.pluginModel.paramsModel.normalizeRaster(toNormPath,out_path=outPath,feedback=feedback)
        return outPath
                                
    def updateFromXML(self,root,feedback=None):
        super().updateFromXML(root)
        if self.getInitialState() is None:
            self.addInitialState()
                                
    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def getHeaderString(self,col):
        h = [self.tr('Name'),
            self.tr('Description'),
            self.tr('Base scenario')]
        return h[col]

class ScenarioConnector(TableToDialogConnector):

    def __init__(self,dlg,model):
        self.dlg = dlg
        self.feedback = dlg.feedback
        super().__init__(model,self.dlg.scenarioView,
                         addButton=self.dlg.scenarioAdd,
                         removeButton=self.dlg.scenarioRemove)

    def connectComponents(self):
        super().connectComponents()
        self.dlg.scenarioUp.clicked.connect(self.upgradeItem)
        self.dlg.scenarioDown.clicked.connect(self.downgradeItem)
        self.dlg.scenarioAddLanduse.clicked.connect(self.openDialogLanduseNew)
                
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
            # self.updateFrictionFromDlg(dlg_item)
    def postDlgNew(self,dlg_item):
        self.feedback.pushDebugInfo("postDlgNew = " + str(dlg_item))
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
        if (item is None):
            # Specific openDialogLanduseNew otherwise 
            luFlag = False
        else:
            luFlag = item.isLanduseMode()
        if item is None or item.isStackedMode():
            self.feedback.pushDebugInfo("openDialog overlap")
            scenarioNames = self.model.getScenarioNames()
            if not scenarioNames:
                msg = self.tr("No scenario in model : please create base scenario from landuse")
                self.feedback.user_error(msg)
            item_copy = item.__deepcopy__() if item else None
            scenarioDlg = ScenarioDialog(self.dlg,item_copy,
                model=self.model.pluginModel,feedback=self.feedback)
            # scenarioDlg = ScenarioDialog(self.dlg,item,scenarioModel=self.model,feedback=self.feedback)
        elif item.isLanduseMode():
            self.feedback.pushDebugInfo("openDialog landuse")   
            dataNames = self.model.pluginModel.getDataNames()
            scenarioDlg = ScenarioLanduseDialog(self.dlg,item,
                feedback=self.feedback,dataNames=dataNames)
                #luModel=self.model.pluginModel.landuseModel)
        elif item.isInitialState():
            self.feedback.pushDebugInfo("Ignoring double click on initial state")
            scenarioDlg = ScenarioInitialStateDialog(self.dlg,item,
                feedback=self.feedback)
        else:
            self.feedback.internal_error("Unexpected scenario mode : "
                + str(scItem.getMode()))
        return scenarioDlg
                        
    def openDialogLanduseNew(self):
        dataNames = self.model.pluginModel.getDataNames()
        item_dlg = ScenarioLanduseDialog(self.dlg,None,
            feedback=self.feedback,dataNames=dataNames)
            #luModel=self.model.pluginModel.landuseModel)
        dlg_item = item_dlg.showDialog()
        if dlg_item:
            # item = self.mkItemFromDlgItem(dlg_item)
            # self.model.addItem(item)
            self.model.addItem(dlg_item)
            if dlg_item.shortMode:
                newName = "{}-short".format(dlg_item.getName())
                newItem = dlg_item.deepcopy()
                newItem.setName(newName)
                self.model.addItem(newItem)
            self.model.layoutChanged.emit()
    
    def updateFromDlgItem(self,item,dlgItem):
        initName, newName = item.getName(), dlgItem.getName()
        item.updateFromDlgItem(dlgItem)
        if initName != newName:
            for scItem in self.model.items:
                if scItem.getBase() == initName:
                    scItem.setBase(newName)
            self.model.pluginModel.renameClassImports(initName,newName)
            
    # def mkItemFromDlgItem(self,dlg_item): 
        # return ScenarioItem(dlg_item,feedback=self.feedback)
        
    # Updates friction model on scenario item modification
    def updateFrictionFromDlg(self,item):
        self.feedback.pushDebugInfo("updateFrictionFromDlg")
        if item:
            if item.isLanduseMode():
                pass
            elif item.isFixedMode():
                # burnVal = str(item.getBurnVal())
                # self.model.pluginModel.frictionModel.updateFromScenario(item.getName(),[""],[burnVal])
                # self.model.pluginModel.classModel.updateFromScenario(item.getName(),,burnVal)
                self.model.pluginModel.classModel.updateFromScenario2(item)
            elif item.isFieldMode():
                # newValStr = friction.NEW_VAL_STR
                # values, classes = item.reclassModel.getValuesAndClasses()
                # classes2 = [c.split(" - ")[0] for c in classes]
                # nbNew = classes2.count(newValStr)
                # freeVals = self.model.pluginModel.frictionModel.getFreeVals(nbNew)
                # classes3 = [int(freeVals.pop(0)) if c == newValStr else int(c) for c in classes2]
                # self.model.pluginModel.classModel.updateFromScenario(item.getName(),values,classes3)
                # self.model.pluginModel.classModel.updateFromScenario(item.getName(),item.getValues())
                self.model.pluginModel.classModel.updateFromScenario2(item)
            self.model.pluginModel.frictionModel.layoutChanged.emit()
        else:
            self.feedback.pushDebugInfo("Empty item")
        
     

        
