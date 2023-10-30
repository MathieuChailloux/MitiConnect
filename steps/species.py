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

import os, sys

from qgis.PyQt import uic, QtWidgets
from qgis.PyQt.QtCore import Qt

from ..qgis_lib_mc.utils import CustomException
from ..qgis_lib_mc.abstract_model import DictItem, DictModel, TableToDialogConnector
from ..ui.species_dialog import SpeciesItem, SpeciesDialog


# class SpeciesItem(SpeciesDialogItem):

    # FIELDS = [ SpeciesDialogItem.ID, SpeciesDialogItem.FULL_NAME ]

    # def __init__(self, dlg_item, parent=None, feedback=None):
        # self.updateFromDlgItem(dlg_item)
        # dict = dlg_item.dict if dlg_item else {}
        # DictItem.__init__(self,dlg_item.dict,fields=self.FIELDS,feedback=feedback)
        
    # def updateFromDlgItem(self,dlg_item):
        # if dlg_item:
            # self.dict = { k : dlg_item.dict[k] for k in self.FIELDS if k in dlg_item.dict }
            # self.dlg_item = dlg_item
            
    # def getName(self):
        # return self.dict[self.ID]  

class SpeciesModel(DictModel):

    def __init__(self, pluginModel):
        # self.item_fields = [ self.PATH, self.EXPRESSION, self.BURN_MODE, self.BURN_VAL,
            # self.ALL_TOUCH, self.BUFFER_MODE, self.BUFFER_EXPR ]
        itemClass = getattr(sys.modules[__name__], SpeciesItem.__name__)
        super().__init__(itemClass,fields=SpeciesItem.FIELDS,
            display_fields=SpeciesItem.DISPLAY_FIELDS,feedback=pluginModel.feedback)
        self.pluginModel = pluginModel
        
    def addItem(self,item):
        super().addItem(item)
        self.pluginModel.addSpecie(item)
    def removeItems(self,indices):
        names = [self.items[ind.row()].getName() for ind in indices]
        super().removeItems(indices)
        for n in names:
            self.pluginModel.frictionModel.removeColFromName(n)
                        
    # Returns absolute path of 'item' output layer
    def getItemOutPath(self,item):
        out_bname = item.getName() + ".tif"
        out_dir = self.pluginModel.getImportsDir()
        return os.path.join(out_dir,out_bname)
    def getItemLandusePath(self,spItem):
        if spItem is None:
            self.feedback.internal_error("No species named " + str(spName))
        spName =  spItem.getName()
        landuse = spItem.getLanduse()
        if not landuse:
            self.feedback.user_error("No base landuse specified for specie "
                + str(spName))
        return self.pluginModel.getDataOutPathFromName(landuse)
    def getLandusePathFromName(self,spName):
        spItem = self.getItemFromName(spName)
        if spItem is None:
            self.feedback.internal_error("No species named " + str(spName))
        landuse = spItem.getLanduse()
        if not landuse:
            self.feedback.user_error("No base landuse specified for specie "
                + str(spName))
        return self.pluginModel.getDataOutPathFromName(landuse)
    def getItemFromName(self,name):
        for i in self.items:
            if i.getName() == name:
                return i
        return None
    def getNames(self):
        return [i.getName() for i in self.items]
    def getImportNames(self):
        return [i.getBaseName() for i in self.items]
        
    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled
        
    def mkItemFromDict(self,dict,parent=None,feedback=None):
        return SpeciesItem.fromDict(dict)

    def getHeaderString(self,col):
        h = [self.tr('ID'),
            self.tr('Full name'),
            self.tr('Max dispersal'),
            self.tr('Min patch area'),
            self.tr('Land use ID')]
        return h[col]


class SpeciesConnector(TableToDialogConnector):

    def __init__(self,dlg,model):
        self.dlg = dlg
        self.feedback = dlg.feedback
        super().__init__(model,self.dlg.speciesView,
                         self.dlg.speciesAdd,self.dlg.speciesRemove)

    def connectComponents(self):
        super().connectComponents()
    
    def openDialog(self,item): 
        self.feedback.pushDebugInfo("item = " + str(item))
        # dlg_item = item.dlg_item if item else None
        species_dlg = SpeciesDialog(self.dlg,item,
            pluginModel=self.model.pluginModel,
            feedback=self.feedback)
        return species_dlg 
        
    def preDlg(self,item):
        if item:
            if not item.isHabitatCodesMode():
                self.pathFieldToAbs(item,SpeciesItem.HABITAT_VAL)
            
    def postDlg(self,dlg_item):
        if dlg_item:
            if not dlg_item.isHabitatCodesMode():
                self.pathFieldToRel(dlg_item,SpeciesItem.HABITAT_VAL)
        
    
    def updateFromDlgItem(self,item,dlgItem):
        initName, newName = item.getName(), dlgItem.getName()
        diffName = initName != newName
        self.feedback.pushDebugInfo("updateFromDlgItem {} {} = {}".format(initName,newName,diffName))
        if diffName:
            self.model.pluginModel.frictionModel.renameField(initName,newName)
        item.updateFromDlgItem(dlgItem)
        self.model.layoutChanged.emit()
            
    def mkItemFromDlgItem(self,dlgItem): 
        return SpeciesItem(dlgItem,feedback=self.feedback)
     

        
