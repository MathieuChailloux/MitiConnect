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

from ..qgis_lib_mc.utils import CustomException
from ..qgis_lib_mc.abstract_model import DictItem, DictModel, TableToDialogConnector
from ..ui.scenario_dialog import ScenarioItem, ScenarioDialog, ScenarioLanduseDialog


# class ScenarioItem(ScenarioDialogItem):

    # NAME = 'NAME'
    # STATUS_OS = 'OS'
    # STATUS_FRICTION = 'FRICTION'
    # STATUS_GRAPH = 'GRAPH'
    # STATUS_FIELDS = [ STATUS_OS, STATUS_FRICTION, STATUS_GRAPH ]
    # FIELDS = ScenarioDialogItem.FIELDS + STATUS_FIELDS
    # DISPLAY_FIELDS = [ ScenarioDialogItem.NAME, ScenarioDialogItem.BASE ] + STATUS_FIELDS
    
    # @classmethod
    # def fromDlgItem(cls, dlg_item, parent=None, feedback=None):
        # dict = self.getDictFromDlgItem(dlg_item)
        # i = cls(dict,fields=self.FIELDS,feedback=feedback)
        # i.dlg_item = dlg_item
        # return i
        
    # def getDictFromDlgItem(self,dlg_item):
        # statusChanged = True
        # dict = { self.NAME : dlg_item.getName(),
            # self.BASE : dlg_item.getBase(),
            # self.STATUS_OS : not statusChanged,
            # self.STATUS_FRICTION : not statusChanged,
            # self.STATUS_GRAPH : not statusChanged }
        # return dict
        
    # def updateFromDlgItem(self,dlg_item):
        # dict = self.getDictFromDlgItem(dlg_item)
        # self.dict = dict
        
    # def getName(self):
        # return self.dict[self.NAME]
    # def getBase(self):
        # return self.dict[self.BASE]
    # def getLayer(self):
        # return self.dict[self.LAYER]
        
class ScenarioModel(DictModel):

    def __init__(self, parentModel):
        itemClass = getattr(sys.modules[__name__], ScenarioItem.__name__)
        super().__init__(self,itemClass,feedback=parentModel.feedback)
        # super().__init__(self,itemClass,feedback=parentModel.feedback,
            # display_fields=ScenarioItem.DISPLAY_FIELDS)
        self.parentModel = parentModel
        
    def getScenarioNames(self):
        return [i.getName() for i in self.items]
    def getItemFromName(self,name):
        for i in self.items:
            if i.getName() == name:
                return i
        return None
                        
    # Returns absolute path of 'item' output layer
    # def getItemOutBase(self,item):
        # out_bname = item.getName() + ".tif"
        # out_dir = self.parentModel.getScenarioDir()
        # return os.path.join(out_dir,out_bname)
        
        
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
        if not item or item.getBase() is not None:
            scenarioNames = self.model.getScenarioNames()
            if not scenarioNames:
                msg = self.tr("No scenario in model : please create base scenario from landuse")
                self.feedback.user_error(msg)
            scenarioDlg = ScenarioDialog(self.dlg,item,scenarioModel=self.model,feedback=self.feedback)
        else:
            scenarioDlg = ScenarioLanduseDialog(self.dlg,item)
        return scenarioDlg
        
    def openDialogLanduseNew(self):
        item_dlg = ScenarioLanduseDialog(self.dlg,None)
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
     

        
