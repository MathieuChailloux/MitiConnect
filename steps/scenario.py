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
                                
    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled


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
        
     

        
