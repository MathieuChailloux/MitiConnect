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

import os, ast

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
# from qgis.gui import QgsCheckableItemModel

from ..qgis_lib_mc import utils, abstract_model, feedbacks

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'species_dialog.ui'))
    

# class TestModel(QgsCheckableItemModel):

    # def __init__(self,values=[]):
        # super().__init__()
        # if not values:
            # values = range(5)
        # self.values = values
        
    # def columnCount(self):
        # return 1
        
    # def rowCount(self):
        # return len(self.values)
        
    # def data(self,index,role):
        # if not index.isValid():
            # return QVariant()
        # row = index.row()
        # item = self.values[row]
        # if role != Qt.DisplayRole:
            # return QVariant()
        # elif row < self.rowCount():
            # return(QVariant(item))
        # else:
            # return QVariant()
    
class SpeciesItem(abstract_model.DictItem):

    ID = 'ID'
    FULL_NAME = 'FULL_NAME'
    MAX_DISP = 'MAX_DISP'
    DISP_UNIT = 'DISP_UNIT'
    MIN_AREA = 'MIN_AREA'
    LANDUSE = 'LANDUSE'
    HABITAT_MODE = 'HABITAT_MODE'
    HABITAT_VAL = 'CODES'
    PATCH_CONNEXITY = 'PATCH_CONNEXITY'
    FRICTION_MODE = 'FRICTION_MODE'
    FRICTION_LAYER = 'FRICTION_LAYER'
    EXTENT_MODE = 'EXTENT_MODE'
    EXTENT_VAL = 'EXTENT_VAL'
    FIELDS = [ ID, FULL_NAME, MAX_DISP, DISP_UNIT, MIN_AREA, LANDUSE, EXTENT_MODE, EXTENT_VAL ]
    DISPLAY_FIELDS = [ ID, FULL_NAME, MAX_DISP, MIN_AREA, LANDUSE ]
    
    def __init__(self,dict,feedback=None):
        if self.HABITAT_MODE not in dict:
            dict[self.HABITAT_MODE] = True
        super().__init__(dict,feedback=feedback)
    
    @classmethod
    def fromValues(cls,name,full_name,max_disp,disp_unit,min_patch,patch_unit,
                   landuse,habitatMode,habitatVal,patchConnexity,frictionMode,
                   frictionLayer,extent_mode,extent_val,feedback=None):
        dict = { cls.ID : name,
                 cls.FULL_NAME : full_name,
                 cls.MAX_DISP : max_disp,
                 cls.DISP_UNIT : disp_unit,
                 cls.MIN_AREA : min_patch,
                 cls.LANDUSE : landuse,
                 cls.HABITAT_MODE : habitatMode,
                 cls.HABITAT_VAL : habitatVal,
                 cls.PATCH_CONNEXITY : patchConnexity,
                 cls.FRICTION_MODE : frictionMode,
                 cls.FRICTION_LAYER : frictionLayer,
                 cls.EXTENT_MODE : extent_mode,
                 cls.EXTENT_VAL : extent_val }
        return cls(dict,feedback=feedback)
    # def __init__(self,dict=dict,feedback=None):
        # super().__init__(dict=dict,feedback=feedback)
        
    # getters
    def getName(self):
        return self.dict[self.ID]
    def getLanduse(self):
        return self.dict[self.LANDUSE]
    def setLanduse(self,val):
        self.dict[self.LANDUSE] = val
    def getMinArea(self):
        return self.dict[self.MIN_AREA]
    def getMaxDisp(self):
        return self.dict[self.MAX_DISP]
    def dispUnitIsMeters(self):
        if self.DISP_UNIT in self.dict:
            return self.dict[self.DISP_UNIT]
        else:
            return True
    def getHabitatMode(self):
        return self.dict[self.HABITAT_MODE]
    def getHabitatVal(self):
        return self.dict[self.HABITAT_VAL]
    # def getCodesFull(self):
        # return ast.literal_eval(self.dict[self.HABITAT_VAL])
    def getPatchConnexity(self):
        return self.PATCH_CONNEXITY not in self.dict or self.dict[self.PATCH_CONNEXITY]
    def getFrictionMode(self):
        return self.FRICTION_MODE not in self.dict or self.dict[self.FRICTION_MODE]
    def getFrictionLayer(self):
        return self.dict[self.FRICTION_LAYER]
    def getExtentMode(self):
        return self.dict[self.EXTENT_MODE]
    def getExtentVal(self):
        return self.dict[self.EXTENT_VAL]
        
    # getters wrappers
    def isHabitatCodesMode(self):
        return self.getHabitatMode() == True
    def isBufferMode(self):
        return self.getExtentMode() == True
    def isMaxExtentMode(self):
        return False
    def isCustomLayerMode(self):
        return False
    def getCodesVal(self):
        # descrList = self.getCodesFull()
        # codesList = [s.split(" - ")[0] for s in descrList]
        # return codesList
        # return ast.literal_eval(codes)
        codesStr = self.dict[self.HABITAT_VAL]
        if codesStr:
            if isinstance(codesStr,str):
                codes = ast.literal_eval(codesStr)
            elif isinstance(codesStr,list):
                codes = codesStr
            else:
                self.feedback.internal_error("Unexpected type {} for {}".format(type(codesStr),codesStr))
            # Backward compatibility
            if "-" in codesStr:
                newCodes = [int(s.split(" - ")[0]) for s in codes]
                self.dict[self.HABITAT_VAL] = str(newCodes)
                codes = newCodes
            return codes
        else:
            return []
                

class SpeciesDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent, dlg_item, pluginModel=None,feedback=None):
        """Constructor."""
        super(SpeciesDialog, self).__init__(parent)
        self.feedback=feedback
        self.pluginModel = pluginModel
        self.setupUi(self)
        self.updateUi(dlg_item)
        self.connectComponents()
        
    def connectComponents(self):
        # super().connectComponents()
        self.frictionTabOpt.clicked.connect(self.switchFrictionTabMode)
        self.frictionLayerOpt.clicked.connect(self.switchFrictionLayerMode)
        self.habitatCodesMode.clicked.connect(self.switchHabitatCodesMode)
        self.habitatLayerMode.clicked.connect(self.switchHabitatLayerMode)
        self.speciesBufferMode.clicked.connect(self.switchExtentBufferMode)
        self.speciesLayerMode.clicked.connect(self.switchExtentLayerMode)
        # dataNames =  self.pluginModel.getDataNames()
        # self.speciesLanduse.insertItems(0,dataNames)
        # testModel = TestModel()
        self.feedback.pushInfo("LANDUSE MODEL NB ITEMS " + str(len(self.pluginModel.landuseModel.items)))
        # assert(False)
        self.pluginModel.landuseModel.layoutChanged.emit()
        # self.pluginModel.frictionModel.layoutChanged.emit()
        
    # Switch extent mode
    def switchExtentMode(self,buffer_mode):
        self.speciesBufferMode.setChecked(buffer_mode)
        self.speciesLayerMode.setChecked(not buffer_mode)
        self.speciesExtentBuffer.setEnabled(buffer_mode)
        self.speciesExtentLayer.setEnabled(not buffer_mode)
    def switchExtentBufferMode(self):
        self.switchExtentMode(True)
    def switchExtentLayerMode(self):
        self.switchExtentMode(False)
        
    # Switch habitat mode
    def switchHabitatMode(self,extent_mode):
        self.habitatCodesMode.setChecked(extent_mode)
        self.habitatLayerMode.setChecked(not extent_mode)
        self.habitatCodes.setEnabled(extent_mode)
        self.habitatLayer.setEnabled(not extent_mode)
    def switchHabitatCodesMode(self):
        self.switchHabitatMode(True)
    def switchHabitatLayerMode(self):
        self.switchHabitatMode(False)
        
    # Switch connexity mode
    def switchConnexityMode(self,mode):
        self.connexity4.setChecked(mode)
        self.connexity8.setChecked(not mode)
    def switchConnexity4Mode(self):
        self.switchConnexityMode(True)
    def switchConnexity8Mode(self):
        self.switchConnexityMode(False)
    
        
    # Switch Friction mode
    def switchFrictionMode(self,mode):
        self.frictionTabOpt.setChecked(mode)
        self.frictionLayerOpt.setChecked(not mode)
        self.frictionLayer.setEnabled(not mode)
    def switchFrictionTabMode(self):
        self.switchFrictionMode(True)
    def switchFrictionLayerMode(self):
        self.switchFrictionMode(False)
        
    def showDialog(self):
        while self.exec_():
            name = self.speciesID.text()
            if not utils.isValidTag(name):
                feedbacks.launchDialog(self,self.tr("Wrong value"),
                    self.tr("Name '{}' contains invalid characters".format(name)))
                continue
            full_name = self.speciesFullName.text()
            max_disp = self.speciesMaxDisp.value()
            disp_unit = self.speciesDispUnit.currentIndex() == 0
            min_patch = self.speciesMinPatch.value()
            patch_unit = self.speciesPatchUnit.currentIndex()
            # landuse = self.speciesLanduse.currentLayer()
            landuse = self.speciesLanduse.currentText()
            # Habitat
            habitat_mode = self.habitatCodesMode.isChecked()
            if habitat_mode:
                checkedItems = self.habitatCodes.checkedItems()
                codes = [int(s.split(" - ")[0]) for s in checkedItems]
                habitat_val = codes               
            else:
                habitat_val = self.habitatLayer.filePath()
            # Connexity
            patch_connexity = self.connexity4.isChecked()
            # Friction
            friction_mode = self.frictionTabOpt.isChecked()
            friction_layer = self.frictionLayer.filePath()
            # Extent
            buffer_mode = self.speciesBufferMode.isChecked()
            layer_mode = self.speciesLayerMode.isChecked()
            extent_mode = buffer_mode
            buffer_val = self.speciesExtentBuffer.value()
            buffer_layer = self.speciesExtentLayer.filePath()
            extent_val = buffer_val if buffer_mode else buffer_layer
            # Build item
            item = SpeciesItem.fromValues(name,full_name,max_disp,disp_unit,
                min_patch,patch_unit,landuse,
                habitat_mode,habitat_val,patch_connexity,friction_mode,friction_layer,
                extent_mode,extent_val,feedback=self.feedback)
            return item
        return None
        
    def updateUi(self,dlg_item):
        l = self.pluginModel.frictionModel.getCodesStr()
        self.feedback.pushDebugInfo("l = " + str(l))
        self.habitatCodes.insertItems(0,l)
        dataNames =  self.pluginModel.getDataNames()
        self.speciesLanduse.insertItems(0,dataNames)
        # self.habitatCodes.model.layoutChanged.emit()
        if dlg_item:
            self.speciesID.setText(dlg_item.dict[SpeciesItem.ID])
            self.speciesFullName.setText(dlg_item.dict[SpeciesItem.FULL_NAME])
            self.speciesMaxDisp.setValue(dlg_item.getMaxDisp())
            if dlg_item.dispUnitIsMeters():
                self.speciesDispUnit.setCurrentIndex(0)
            else:
                self.speciesDispUnit.setCurrentIndex(1)
            self.speciesMinPatch.setValue(dlg_item.getMinArea())
            self.speciesLanduse.setCurrentText(dlg_item.dict[SpeciesItem.LANDUSE])
            # Habitat
            habitat_mode = dlg_item.getHabitatMode()
            self.switchHabitatMode(habitat_mode)
            if habitat_mode:
                codes = dlg_item.getCodesVal()
                if codes:
                    checkedItems = self.pluginModel.frictionModel.getCodesStr(codes=codes)
                    self.habitatCodes.setCheckedItems(checkedItems)
            else:
                habitatLayer = dlg_item.getHabitatVal()
                if utils.fileExists(habitatLayer):
                    self.habitatLayer.setFilePath(dlg_item.getHabitatVal())
                else:
                    self.feedback.pushWarning("No habitat layer {}".format(habitatLayer))
            # Connexity
            self.switchConnexityMode(dlg_item.getPatchConnexity())
            # Friction
            friction_mode = dlg_item.getFrictionMode()
            self.switchFrictionMode(friction_mode)
            if not friction_mode:
                friction_layer = dlg_item.getFrictionLayer()
                if utils.fileExists(friction_layer):
                    self.frictionLayer.setFilePath(friction_layer)
                else:
                    self.feedback.pushWarning("No friction layer {}".format(friction_layer))
            # Extent
            extent_mode = dlg_item.dict[SpeciesItem.EXTENT_MODE]
            extent_val = dlg_item.dict[SpeciesItem.EXTENT_VAL]
            self.switchExtentMode(extent_mode)
            if extent_mode:
                self.speciesExtentBuffer.setValue(extent_val)
            else:
                self.speciesExtentLayer.setFilePath(extent_val)
            