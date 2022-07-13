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

import os, sys

from qgis.PyQt import uic, QtWidgets
from qgis.PyQt.QtCore import Qt
from qgis.core import QgsProcessingContext, QgsProcessingUtils

from ..qgis_lib_mc.utils import CustomException, joinPath
from ..qgis_lib_mc.abstract_model import DictItem, DictModel, TableToDialogConnector
from ..algs.erc_tvb_algs_provider import ErcTvbAlgorithmsProvider
from ..qgis_lib_mc.qgsTreatments import applyProcessingAlg
from ..qgis_lib_mc import qgsTreatments, qgsUtils
from ..ui.scenario_dialog import ScenarioItem, ScenarioDialog, ScenarioLanduseDialog

# Graphab utils

#{ 'DIRPATH' : 'TEMPORARY_OUTPUT', 'INPUT' : 'D:/IRSTEA/ERC/tests/BousquetOrbExtended/Source/CorineLandCover/CLC12_BOUSQUET_ORB.tif', 'LANDCODE' : '241', 'NAMEPROJECT' : 'Project1', 'NODATA' : None, 'SIZEPATCHES' : 0 }
# TODO : grapha wrappers in erc_tvb_algs_provider ?
def createGraphabProject(landuse,codes,out_dir,project_name,
        nodata=None,patch_size=0,feedback=None):
    params = {
        'DIRPATH' : out_dir,
        'INPUT' : landuse,
        'LANDCODE' : codes,
        'NAMEPROJECT' : project_name,
        'NODATA' : nodata,
        'SIZEPATCHES' : 0 }
    applyProcessingAlg('erc_tvb','create_graph',params,feedback=feedback)

# Scenario
        
class ScenarioModel(DictModel):

    def __init__(self, pluginModel):
        itemClass = getattr(sys.modules[__name__], ScenarioItem.__name__)
        super().__init__(itemClass,feedback=pluginModel.feedback,
            fields=ScenarioItem.FIELDS,display_fields=ScenarioItem.DISPLAY_FIELDS)
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
                        
    # Returns absolute path of 'item' output layer
    # def getItemSubElement
    def getItemOutBase(self,item,suffix=""):
        sc_name = item.getName()
        out_bname = sc_name + suffix + ".tif"
        out_dir = self.pluginModel.getScenarioDir(sc_name)
        return joinPath(out_dir,out_bname)
    def getItemLanduse(self,item):
        return self.getItemOutBase(item,suffix="_landuse")
    def getItemFriction(self,item):
        return self.getItemOutBase(item,suffix="_friction")
    # def getItemGraphabDir(self,item):
        # return self.getItemOutBase(item,suffix="_landuse")
        
    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled
        
    def applyItemLanduse(self, scItem, spItem,context=None):
        self.feedback.pushDebugInfo("applyItemLanduse")
        name = scItem.getName()
        if scItem.getStatusLanduse():
            msg = self.tr("Landuse layer already computed for scenario ")
            self.feedback.pushWarning(msg + str(name))
            return
        in_path = self.pluginModel.getOrigPath(scItem.getLayer())
        out_path = self.getItemLanduse(scItem)
        out_path = QgsProcessingUtils.generateTempFilename("out.tif")
        out_path2 = QgsProcessingUtils.generateTempFilename("out2.tif")
        out_gpkg = QgsProcessingUtils.generateTempFilename("out.gpkg")
        out_shp = QgsProcessingUtils.generateTempFilename("out.shp")
        if scItem.isLanduseMode():
            # self.pluginModel.paramsModel.normalizeRaster(
                # in_path,out_path=out_path,
                # context=QgsProcessingContext(),
                # feedback=self.feedback)
            # qgsUtils.loadRasterLayer(in_path,loadProject=True)
            # qgsTreatments.applyWarpReproject(in_path,out_path,resolution=10,
                # feedback=self.feedback)
            # qgsUtils.loadRasterLayer(out_path,loadProject=True)
            #
            # { 'EXPRESSION' : 'True', 'INPUT' : 'D:/IRSTEA/ERC/tests/BousquetOrbExtended/Source/Routes/TRONCON_ROUTE_BOUSQUET_ORB.shp', 'METHOD' : 0 }
            input = 'D:/IRSTEA/ERC/tests/BousquetOrbExtended/Source/Routes/TRONCON_ROUTE_BOUSQUET_ORB.shp'
            # qgsUtils.loadVectorLayer(input,loadProject=True)
            # qgsTreatments.selectByExpression(input,'True',feedback=self.feedback)
            # qgsTreatments.extractByExpression(input,'True',out_gpkg,feedback=self.feedback)
            # self.pluginModel.paramsModel.clipByExtent(input,name="test",
                # feedback=self.feedback)
            
            crs, extent, resolution = self.pluginModel.getRasterParams()
            # res = qgsTreatments.clipVectorByExtent(input,extent,out_shp,
                # feedback=self.feedback)
            extent_layer_path = self.pluginModel.paramsModel.getExtentLayer()
            res = qgsTreatments.clipRasterFromVector(in_path,extent_layer_path,out_path,context=context,feedback=self.feedback,resolution=10)
            # qgsTreatments.applyRasterization(input,out_path,extent=extent,resolution=10,feedback=self.feedback)
            # out_layer = qgsUtils.loadRasterLayer(out_path,loadProject=True)
            # qgsTreatments.applyWarpReproject(out_path,out_path2,extent=extent,dst_crs=crs,extent_crs=crs,resolution=resolution,nodata_val=255,feedback=self.feedback)
            assert(False)
        else:
            # Rasterize
            # Reclassify
            # Merge
            self.feedback.pushInfo("About to apply rrm")
            
    def applyItemFriction(self, item):
        self.feedback.pushDebugInfo("applyItemFriction")
        name = item.getName()
        if self.item.getStatusFriction():
            msg = self.tr("Friction layer already computed for scenario ")
            self.feedback.pushWarning(msg + str(name))
        else:
            # GetLanduse
            # Reclassify
            self.feedback.pushInfo("About to apply rm")
            
    #{ 'DIRPATH' : 'TEMPORARY_OUTPUT', 'INPUT' : 'D:/IRSTEA/ERC/tests/BousquetOrbExtended/Source/CorineLandCover/CLC12_BOUSQUET_ORB.tif', 'LANDCODE' : '241', 'NAMEPROJECT' : 'Project1', 'NODATA' : None, 'SIZEPATCHES' : 0 }
    def applyItemGraph(self, item):
        self.feedback.pushDebugInfo("applyItemGraph")
        name = item.getName()


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
        self.dlg.speciesSelection.setModel(self.model.pluginModel.speciesModel)
        self.dlg.scLanduseRun.clicked.connect(self.landuseRun)
        self.dlg.scFrictionRun.clicked.connect(self.frictionRun)
        self.dlg.scGraphRun.clicked.connect(self.graphRun)
        
    def getSelectedScenarios(self):
        indexes = self.view.selectedIndexes()
        if not indexes:
            self.feedback.user_error("No scenario selected")
        rows = list(set([i.row() for i in indexes]))
        res = [self.model.items[i] for i in rows]
        return res
        
    def getSelectedSpecies(self):
        specie = self.dlg.speciesSelection.currentText()
        if not specie:
            self.feedback.user_error("No specie selected")
        speciesItem = self.model.pluginModel.speciesModel.getItemFromName(specie)
        return [speciesItem]
        
    def landuseRun(self):
        scenarios = self.getSelectedScenarios()
        species = self.getSelectedSpecies()
        for sc in scenarios:
            for sp in species:
                self.feedback.pushDebugInfo("TODO : landuse Run "
                    + sc.getName() + " - " + sp.getName())
                self.model.applyItemLanduse(sc,sp,context=self.dlg.context)
    def frictionRun(self):
        scenarios = self.getSelectedScenarios()
        species = self.getSelectedSpecies()
        for sc in scenarios:
            for sp in species:
                self.feedback.pushDebugInfo("TODO : friction Run "
                    + sc.getName() + " - " + sp.getName())
    def graphRun(self):
        scenarios = self.getSelectedScenarios()
        species = self.getSelectedSpecies()
        for sc in scenarios:
            for sp in species:
                self.feedback.pushDebugInfo("TODO : graph Run "
                    + sc.getName() + " - " + sp.getName())
    
    def preDlg(self,item):
        self.feedback.pushDebugInfo("preDlg = " + str(item))
        if item is not None:
            self.pathFieldToAbs(item,ScenarioItem.LAYER)
            if item.isLanduseMode():
                 self.pathFieldToAbs(item,ScenarioItem.BASE)

    def postDlg(self,dlg_item):
        self.feedback.pushDebugInfo("postDlg = " + str(dlg_item))
        if dlg_item is not None:
            self.pathFieldToRel(dlg_item,ScenarioItem.LAYER)
            if dlg_item.isLanduseMode():
                 self.pathFieldToRel(dlg_item,ScenarioItem.BASE)
    
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
            luFlag = False
        else:
            luFlag = item.isLanduseMode()
            # b = item.getBase()
            # if (b is None) or (b == "None"):
                # luFlag = True
            # else:
                # luFlag = False
        if not luFlag:
            self.feedback.pushDebugInfo("k1")
            scenarioNames = self.model.getScenarioNames()
            if not scenarioNames:
                msg = self.tr("No scenario in model : please create base scenario from landuse")
                self.feedback.user_error(msg)
            item_copy = item.__deepcopy__()
            scenarioDlg = ScenarioDialog(self.dlg,item_copy,scenarioModel=self.model,feedback=self.feedback)
            # scenarioDlg = ScenarioDialog(self.dlg,item,scenarioModel=self.model,feedback=self.feedback)
        else:
            self.feedback.pushDebugInfo("k2")
            scenarioDlg = ScenarioLanduseDialog(self.dlg,item,
                feedback=self.feedback)
        return scenarioDlg
                        
    def openDialogLanduseNew(self):
        item_dlg = ScenarioLanduseDialog(self.dlg,None,
            feedback=self.feedback)
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
     

        
