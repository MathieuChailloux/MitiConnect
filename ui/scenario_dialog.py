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

import os, sys, copy

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.core import QgsFieldProxyModel 

from ..qgis_lib_mc import utils, abstract_model, qgsUtils, feedbacks, qgsTreatments
from ..steps import friction

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
SC_DIALOG, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'scenario_dialog.ui'))
SC_LANDUSE_DIALOG, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'scenario_landuse_dialog.ui'))
SC_IS_DIALOG, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'scenario_initialState_dialog.ui'))

class ScenarioItem(abstract_model.DictItem):
    
    NAME = 'NAME'
    DESCR = 'DESCR'
    BASE = 'BASE'
    BASE_LAYER = 'BASE_LAYER'
    LAYER = 'LAYER'
    EXTENT_FLAG = 'EXTENT_FLAG'
    # True = Field mode, False = Fixed mode
    MODE = 'MODE'
    RECLASS_FIELD = 'RECLASS_FIELD'
    # MODEL = 'RECLASS_VAL'
    MODEL = 'MODEL'
    BURN_VAL = 'BURN_VAL'
    # DISPLAY_FIELDS = ['NAME','BASE']
    
    LANDUSE_MODE = 0
    VECTOR_FIXED_MODE = 1
    VECTOR_FIELD_MODE = 2
    INITIAL_STATE_MODE = 3
    RASTER_VALUES_MODE = 4
    RASTER_FIXED_MODE = 5
    
    BASE_FIELDS = [ NAME, DESCR, BASE ]
    RECLASS_FIELDS = [ MODE, RECLASS_FIELD, BURN_VAL ]
    FIELDS = BASE_FIELDS + RECLASS_FIELDS
    DISPLAY_FIELDS = BASE_FIELDS
    
    def __init__(self,dict,feedback=None):
        super().__init__(dict,feedback=feedback)
        self.shortMode = False
        self.values = []
    
    @classmethod
    def fromValues(cls, name, descr="", layer=None, base=None,
            baseLayer=None,
            extentFlag=True, mode=0, reclassField=None, burnVal=1,
            feedback=None):
        dict = { cls.NAME : name, cls.DESCR : descr, cls.BASE : base,
            cls.BASE_LAYER : baseLayer, cls.LAYER : layer,
            cls.EXTENT_FLAG : extentFlag, cls.MODE : mode,
            cls.RECLASS_FIELD : reclassField,
            cls.BURN_VAL : burnVal }
        return cls(dict, feedback=feedback)
        
    def __deepcopy__(self):
        item = ScenarioItem(copy.deepcopy(self.dict),feedback=self.feedback)
        return item
        
    def getName(self):
        return self.dict[self.NAME]
    def setName(self,val):
        self.dict[self.NAME] = val
    def getDescr(self):
        return self.dict[self.DESCR]
    def getBase(self):
        return self.dict[self.BASE]
    def setBase(self,val):
        self.dict[self.BASE] = val
    def getBaseLayer(self):
        return self.dict[self.BASE_LAYER]
    def getLayer(self):
        return self.dict[self.LAYER]
    def getExtentFlag(self):
        if self.EXTENT_FLAG not in self.dict:
            self.dict[self.EXTENT_FLAG] = True
        return self.dict[self.EXTENT_FLAG]
    def getMode(self):
        return self.dict[self.MODE]
    def getBurnVal(self):
        return self.dict[self.BURN_VAL]
    def getBurnField(self):
        return self.dict[self.RECLASS_FIELD]
    # Mode checkers
    def isInitialState(self):
        return self.getMode() == self.INITIAL_STATE_MODE
    def isLanduseMode(self):
        return self.getMode() == self.LANDUSE_MODE
    def isVectorFixedMode(self):
        return self.getMode() == self.VECTOR_FIXED_MODE
    def isVectorFieldMode(self):
        return self.getMode() == self.VECTOR_FIELD_MODE
    def isRasterValuesMode(self):
        return self.getMode() == self.RASTER_VALUES_MODE
    def isRasterFixedMode(self):
        return self.getMode() == self.RASTER_FIXED_MODE
    def isFixedMode(self):
        return self.getMode() in [self.VECTOR_FIXED_MODE, self.RASTER_FIXED_MODE]
    def isValueMode(self):
        return self.getMode() in [self.VECTOR_FIELD_MODE, self.RASTER_VALUES_MODE]
    def isStackedMode(self):
        return self.getMode() not in [self.LANDUSE_MODE, self.INITIAL_STATE_MODE]
    def isVectorMode(self):
        return self.getMode() in [self.VECTOR_FIXED_MODE, self.VECTOR_FIELD_MODE]
    def isRasterMode(self):
        return self.getMode() in [self.RASTER_FIXED_MODE, self.RASTER_VALUES_MODE]
        
    def isLeaf(self):
        return self.getBase() == None
    def useExtent(self):
        return self.getExtentFlag()
        
    def isVector(self):
        layerPath = self.getLayer()
        layer = qgsUtils.loadLayer(layerPath)
        if layer:
            return qgsUtils.isVectorLayer(layer)
        else:
            self.feedback.internal_error("Empty layer for scenario {}".format(self))
        
    def sameBurn(self,other):
        mode1, mode2 = self.getMode(), other.getMode()
        if mode1 != mode2:
            return False
        if mode1:
            return self.getBurnVal() == other.getBurnVal()
        else:
            return self.getBurnField() == other.getBurnField()
        
    # def updateFromOther(self,other):
        # for k in other.dict:
            # self.dict[k] = other.dict[k]
    def updateFromDlgItem(self,dlgItem):
        self.updateFromOther(dlgItem)
                
    # Mandatory to redefine it for import links reasons
    @classmethod
    def fromXML(cls,root,feedback=None):
        utils.debug("fromXML " + str(root))
        if cls.DESCR not in root.attrib:
            root.attrib[cls.DESCR] = ""
        o = cls.fromDict(root.attrib,feedback=feedback)
        return o
    
    def computeValues(self,layer=None):
        if not layer:
            layerPath = self.getLayer()
            layer = qgsUtils.loadLayer(layerPath)
        if self.isFixedMode():
            # self.values = [self.getBurnVal()]
            self.values = []
        elif self.isVectorFieldMode():
            fieldname = self.getBurnField()
            self.values = qgsUtils.getLayerFieldUniqueValues(layer,fieldname)
        elif self.isRasterValuesMode():
            self.feedback.setProgressText("Fetching unique values")
            self.values = qgsTreatments.getRasterUniqueVals(layer,self.feedback)
            self.feedback.setProgress(100)
        self.feedback.pushDebugInfo("computeValues {} = {}".format(self,self.values))
        
            
    

class ScenarioDialog(QtWidgets.QDialog, SC_DIALOG):
    def __init__(self, parent, dlgItem, model=None, feedback=None):
        """Constructor."""
        super(ScenarioDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.newFlag = dlgItem is None
        self.reloadFlag = False
        self.feedback = feedback
        if model is None:
            assert(False)
        self.scModel = model.scenarioModel
        self.frictionModel = model.frictionModel
        self.classModel = model.classModel
        self.setupUi(self)
        self.layerComboDlg = qgsUtils.LayerComboDialog(self,
            self.scLayerCombo,self.scLayerButton)
        #self.layerComboDlg.setVectorMode()
        self.connectComponents()
        self.updateUi(dlgItem)
        self.reloadFlag = True
        self.values = []
        self.layer = None
        
    def connectComponents(self):
        self.scLayerCombo.layerChanged.connect(self.changeLayer)
        self.scFieldMode.clicked.connect(self.switchFieldMode)
        self.scFixedMode.clicked.connect(self.switchFixedMode)
        self.scField.setFilters(QgsFieldProxyModel.Numeric)
        self.scField.fieldChanged.connect(self.changeField)
        self.scBase.setModel(self.scModel)
        self.scModel.layoutChanged.emit()
        
    def switchBurnMode(self,fieldMode):
        self.scFixedMode.setChecked(not fieldMode)
        self.scFieldMode.setChecked(fieldMode)
        #self.scPerValue.setEnabled(fieldMode)
        self.scField.setEnabled(fieldMode)
        self.scBurnVal.setEnabled(not fieldMode)
    def switchFieldMode(self):
        self.switchBurnMode(True)
    def switchFixedMode(self):
        self.switchBurnMode(False)
        
    def changeLayer(self,layer):
        self.scField.setLayer(layer)
        # self.layer = layer
    def changeField(self,fieldname):
        layer = self.scLayerCombo.currentLayer()
        if fieldname:
            self.values = qgsUtils.getLayerFieldUniqueValues(layer,fieldname)
            self.feedback.pushDebugInfo("field values = " + str(self.values))
            nb_values = len(self.values)
            if nb_values > 5:
                feedbacks.paramError("Field {} contains {} unique values, is it ok or too much ?".format(fieldname,nb_values))
        else:
            self.values = []
        
    def errorDialog(self,msg):
        feedbacks.launchDialog(None,self.tr('Wrong parameter value'),msg)
        
    def showDialog(self):
        while self.exec_():
            # Name
            name = self.scName.text()
            if not utils.isValidTag(name):
                feedbacks.launchDialog(self,self.tr("Wrong value"),
                    self.tr("Name '{}' contains invalid characters".format(name)))
                continue
            if self.newFlag and self.scModel.scExists(name):
                self.errorDialog(self.tr("Scenario already exists : " + name))
                continue
            if self.newFlag and self.frictionModel.importExists(name):
                self.errorDialog(self.tr("Import already exists : " + name))
                continue
            descr = self.scDescr.text()
            # base scenario
            base = self.scBase.currentText()
            self.feedback.pushDebugInfo("base = " + str(base))
            if base is None:
                self.errorDialog(self.tr("Empty base scenario"))
                continue
            # new layer
            layer = self.scLayerCombo.currentLayer()
            if not layer:
                self.errorDialog(self.tr("Empty layer"))
                continue
            isVectorMode = qgsUtils.isVectorLayer(layer)
            layerPath = qgsUtils.pathOfLayer(layer)
            extentFlag = self.scExtentFlag.isChecked()
            shortMode = self.scShort.isChecked()
            scPerValueMode = self.scPerValue.isChecked()
            fixedMode = self.scFixedMode.isChecked()
            # reclassField = self.scField.currentField()
            self.feedback.pushDebugInfo("fixedMode = " + str(fixedMode))
            if fixedMode:
                mode = ScenarioItem.VECTOR_FIXED_MODE if isVectorMode else ScenarioItem.RASTER_FIXED_MODE
                burnVal = self.scBurnVal.text()
                # burnVal = self.frictionModel.getCodeFromCombo(self.scBurnVal)
                dlgItem = ScenarioItem.fromValues(name,descr=descr,
                    layer=layerPath,base=base,
                    mode=mode,burnVal=burnVal,extentFlag=extentFlag,
                    feedback=self.feedback)
                # self.values = [burnVal]
            else:
                reclassField = ""
                if isVectorMode:
                    mode = ScenarioItem.VECTOR_FIELD_MODE
                    reclassField = self.scField.currentField()
                    if not reclassField:
                        self.errorDialog(self.tr("Empty field"))
                        continue
                    # if not self.values:
                        # self.values = qgsUtils.getLayerFieldUniqueValues(layer,reclassField)
                else:
                    mode = ScenarioItem.RASTER_VALUES_MODE
                    # self.feedback.setProgressText(self.tr("Fetching unique values"))
                    # self.values = qgsTreatments.getRasterUniqueVals(layer,self.feedback)
                    # self.feedback.setProgress(100)
                # Check values count
                # nb_values = len(self.values)
                # if nb_values == 0:
                    # self.errorDialog(self.tr("No values found, please check that layer is not empty"))
                    # continue
                # elif nb_values > 40:
                    # title = "High values count"
                    # msg = "Field {} contains {} unique values, is it ok ?".format(reclassField,nb_values)
                    # reply = feedbacks.launchQuestionDialog(self,title,msg)
                    # self.feedback.pushDebugInfo("reply {}".format(reply))
                    # if reply == QtWidgets.QMessageBox.No:
                        # continue
                dlgItem = ScenarioItem.fromValues(name,descr=descr,
                    layer=layerPath,base=base,
                    mode=mode,reclassField=reclassField,extentFlag=extentFlag,
                    feedback=self.feedback)
            dlgItem.computeValues(layer=layer)
            # Check values count
            if dlgItem.isValueMode():
                nb_values = len(dlgItem.values)
                if nb_values == 0:
                    self.errorDialog(self.tr("No values found, please check that layer is not empty"))
                    continue
                elif nb_values > 40:
                    title = "High values count"
                    msg = "Scenario contains {} unique values to reclass, is it ok ?".format(nb_values)
                    reply = feedbacks.launchQuestionDialog(self,title,msg)
                    self.feedback.pushDebugInfo("reply {}".format(reply))
                    if reply == QtWidgets.QMessageBox.No:
                        continue
            self.values = dlgItem.values
            # dlgItem.values = self.values
            dlgItem.shortMode = shortMode
            return dlgItem
        return None

    def updateUi(self,dlgItem):
        # self.scBase.addItems(self.scenarioList)
        if dlgItem:
            self.feedback.pushDebugInfo("updateUI " + str(dlgItem.dict))
            # self.feedback.pushDebugInfo("updateUI child 1 " + str(dlgItem.reclassModel))
            scName = dlgItem.getName()
            self.scName.setText(scName)
            self.scDescr.setText(dlgItem.getDescr())
            self.scBase.setCurrentText(dlgItem.getBase())
            layer = dlgItem.getLayer()
            if layer and os.path.isfile(layer):
                self.layerComboDlg.setLayerPath(layer)
            self.scExtentFlag.setChecked(dlgItem.getExtentFlag())
            # fieldMode = dlgItem.dict[ScenarioItem.MODE] == ScenarioItem.VECTOR_FIELD_MODE
            # fieldMode = dlgItem.isFieldMode()
            if dlgItem.isValueMode():
                self.switchBurnMode(True)
                # self.feedback.pushDebugInfo("updateUI child 2" + str(dlgItem.reclassModel))
                # copyModel = dlgItem.reclassModel.__copy__()
                # self.reclassModel = dlgItem.reclassModel.__copy__()
                self.scField.setField(dlgItem.getBurnField())
                # load model values
                # initVals = self.frictionModel.getInitVals(origin=scName)
                # newVals = self.frictionModel.getCodesStrComplete(origin=scName)
                # self.reclassModel = dlgItem.reclassModel
                # self.reclassModel = ScenarioReclassModel.fromValues(values=initVals,codes=newVals,feedback=self.feedback)
                # self.feedback.pushDebugInfo("updateUI child 3 " + str(dlgItem.reclassModel))
                # self.feedback.pushDebugInfo("updateUI child 4 " + str(self.reclassModel))
                # self.scDialogView.setModel(copyModel)
                # self.scDialogView.setModel(self.reclassModel)
                # self.reclassModel.layoutChanged.emit()
                burnVal = None
            elif dlgItem.isFixedMode():
                self.switchBurnMode(False)
                # burnVal = str(dlgItem.dict[ScenarioItem.BURN_VAL])
                classItem = self.classModel.getItemFromOrigin(scName)
                burnVal = classItem.getNewVal() if classItem else dlgItem.getBurnVal()
                try:
                    burnVal =  int(burnVal)
                except TypeError:
                    burnVal = self.frictionModel.getFreeVal()
                self.feedback.pushDebugInfo("burnVal = " + str(burnVal))
                self.scBurnVal.setValue(burnVal)
                # self.scBurnVal.setText(burnVal)
                # self.frictionModel.initComboCodes(self.scBurnVal,burnVal)
        else:
            burnVal = self.frictionModel.getFreeVal()
            self.scBurnVal.setValue(burnVal)
        # self.frictionModel.initComboCodes(self.scBurnVal,burnVal)

class ScenarioInitialStateDialog(QtWidgets.QDialog, SC_IS_DIALOG):
    def __init__(self, parent, dlgItem, feedback=None):
        """Constructor."""
        super(ScenarioInitialStateDialog, self).__init__(parent)
        self.feedback = feedback
        self.setupUi(self)
        self.updateUi(dlgItem)
                
    def updateUi(self,dlgItem):
        if dlgItem:
            self.scName.setText(dlgItem.getName())
            self.scDescr.setText(dlgItem.getDescr())
        else:
            assert(False)
        
    def showDialog(self):
        while self.exec_():
            name = self.scName.text()
            if not utils.isValidTag(name):
                feedbacks.launchDialog(self,self.tr("Wrong value"),
                    self.tr("Name '{}' contains invalid characters".format(name)))
                continue
            descr = self.scDescr.text()
            dlgItem = ScenarioItem.fromValues(name=name,descr=descr,
                mode=3,layer=None,feedback=self.feedback)
            return dlgItem
        return None

class ScenarioLanduseDialog(QtWidgets.QDialog, SC_LANDUSE_DIALOG):
    def __init__(self, parent, dlgItem, feedback=None, dataNames=[]):
        """Constructor."""
        super(ScenarioLanduseDialog, self).__init__(parent)
        self.feedback = feedback
        # self.luModel = luModel
        self.dataNames=dataNames
        self.setupUi(self)
        self.connectComponents()
        self.updateUi(dlgItem)
        
    def connectComponents(self):
        self.scLanduseCombo.insertItems(0,self.dataNames)
        # self.scLanduseCombo.setModel(self.luModel)
        # self.layerComboDlg = qgsUtils.LayerComboDialog(self,
            # self.scLayerCombo,self.scLayer)
                
    def updateUi(self,dlgItem):
        if dlgItem:
            self.scName.setText(dlgItem.getName())
            self.scLayer.setFilePath(dlgItem.getLayer())
            self.scLanduseCombo.setCurrentText(dlgItem.getBase())
        
    def errorDialog(self,msg):
        feedbacks.launchDialog(self,self.tr('Wrong parameter value'),msg)
        
    def showDialog(self):
        while self.exec_():
            name = self.scName.text()
            if not utils.isValidTag(name):
                feedbacks.launchDialog(self,self.tr("Wrong value"),
                    self.tr("Name '{}' contains invalid characters".format(name)))
                continue
            base = self.scLanduseCombo.currentText()
            if not base:
                feedbacks.paramError(self.tr("Empty landuse"),parent=self)
                continue
            # layer = self.scLayer.filePath()
            # if not layer:
                # self.errorDialog(self.tr("Empty layer"))
                # continue
            dlgItem = ScenarioItem.fromValues(name=name,base=base,
                layer=None,feedback=self.feedback)
            return dlgItem
        return None
                
                
                
                
