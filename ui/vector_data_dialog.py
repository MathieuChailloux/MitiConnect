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

import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.core import QgsFieldProxyModel
# from qgis.core import QgsMapLayerProxyModel

from ..qgis_lib_mc import utils, qgsUtils, abstract_model, feedbacks, qgsTreatments
from ..ui.raster_data_dialog import ReclassItem, ReclassModel

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'vector_data_dialog.ui'))

class VectorDlgItem(abstract_model.DictItem):

    NAME = 'NAME'
    INPUT = 'INPUT'
    EXPRESSION = 'EXPRESSION'
    BURN_MODE = 'BURN_MODE'
    BURN_FIELD = 'BURN_FIELD'
    KEEP_VAL = 'KEEP_VALUES'
    BURN_VAL = 'BURN_VAL'
    ALL_TOUCH = 'ALL_TOUCH'
    BUFFER_MODE = 'BUFFER_MODE'
    BUFFER_EXPR = 'BUFFER_EXPR'
    FIELDS = [ NAME, INPUT, EXPRESSION, BURN_MODE, BURN_FIELD, KEEP_VAL, BURN_VAL,
            ALL_TOUCH, BUFFER_MODE, BUFFER_EXPR ]

    def __init__(self, dict, feedback=None):
        super().__init__(dict, self.FIELDS)
        
    def getName(self):
        return self.dict[self.NAME]
    def getLayerPath(self):
        return self.dict[self.INPUT]
    def getExpression(self):
        return self.dict[self.EXPRESSION]
    def getBurnMode(self):
        return self.dict[self.BURN_MODE]
    def isBurnFieldMode(self):
        return self.getBurnMode()
    def getBurnField(self):
        return self.dict[self.BURN_FIELD]
    def keepValues(self):
        if self.KEEP_VAL in self.dict:
            return self.dict[self.KEEP_VAL]
        else:
            return False
    def getBurnVal(self):
        return self.dict[self.BURN_VAL]
    def getAllTouch(self):
        return self.dict[self.ALL_TOUCH]
    def isBufferMode(self):
        return self.dict[self.BUFFER_MODE]
    def getBufferExpr(self):
        return self.dict[self.BUFFER_EXPR]
        
    def getValue(self):
        if self.isBurnFieldMode():
            val = self.getBurnField()
        else:
            val = self.getBurnVal()
        return val
        
    def setBurnVal(self,burnVal):
        self.dict[self.BURN_VAL] = burnVal
        
    # def getValues(self):
        # if self.isBurnFieldMode():
            # layer = self.getLayerPath()
            # fieldname = self.getBurnField()
            # values = qgsUtils.getLayerFieldUniqueValues(layer,fieldname)
        # else:
            # values = [self.getBurnVal()]
        # return values


# def initComboCodes(frModel,combo,val=None):
    # itemsStr = frModel.getCodesStrComplete()
    # combo.insertItems(0,itemsStr)
    # if val is None or val == "":
        # combo.setCurrentIndex(0)
    # else:
        # codes = frModel.getCodes()
        # idx = codes.index(val)
        # combo.setCurrentIndex(idx+1)
        
# def getCodeFromCombo(frModel,combo):
    # idx = combo.currentIndex()
    # if idx == 0:
        # code = frModel.getFreeVals(1)[0]
    # else:
        # codes = frModel.getCodes()
        # code = codes[idx-1]
    # return code
    

# TODO : idée : génération automatique XML depuis QDialog 
# en fonction des widgets ??
class VectorDataDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, vector_data_item, parent, frictionModel):
        """Constructor."""
        super(VectorDataDialog, self).__init__(parent)
        self.feedback=parent.feedback
        self.data_item = vector_data_item
        self.frictionModel = frictionModel
        self.setupUi(self)
        self.initGui()
        self.connectComponents()
        self.updateUi()

    # def mkItem(self):
        # layer = self.vectorLayerFile.fileInfo()

    def initGui(self):
        self.layerComboDlg = qgsUtils.LayerComboDialog(self,
            self.vectorLayerCombo,self.vectorLayerFile)
        self.layerComboDlg.setVectorMode()
        #self.vectorLayerFile.setFilter(qgsUtils.getVectorFilters())
        
    def connectComponents(self):
        self.vectorLayerCombo.layerChanged.connect(self.setLayer)
        self.vectorDefaultSetting.currentIndexChanged.connect(
            self.setDefaultSetting)
        self.vectorFieldMode.clicked.connect(self.setFieldMode)
        self.vectorFieldCombo.fieldChanged.connect(self.setField)
        self.keepValues.clicked.connect(self.setKeepValMode)
        self.vectorFixedMode.clicked.connect(self.setFixedMode)
        self.vectorBufferMode.clicked.connect(self.setBufferMode)
        
    def updateUi(self):
        # print("update")
        if self.data_item:
            # print("lets go")
            self.nameValue.setText(self.data_item.getName())
            self.vectorLayerCombo.setLayer(None)
            layerPath = self.data_item.getLayerPath()
            if utils.fileExists(layerPath):
                self.layerComboDlg.setLayerPath(layerPath)
            self.vectorSelectionExpression.setExpression(self.data_item.getExpression())
            burnMode = self.data_item.getBurnMode()
            self.setBurnMode(burnMode)
            self.vectorFieldCombo.setField(self.data_item.getBurnField())
            self.keepValues.setChecked(self.data_item.keepValues())
            burnVal = self.frictionModel.getFreeVal() if burnMode else self.data_item.getBurnVal() 
            self.vectorFixedValue.setValue(burnVal)
            # self.frictionModel.initComboCodes(self.vectorFixedCombo,burnVal)
            self.vectorAllTouch.setChecked(self.data_item.getAllTouch())
            bm = self.data_item.isBufferMode()
            self.vectorBufferMode.setChecked(bm)
            self.vectorBufferValue.setEnabled(bm)
            self.vectorBufferValue.setValue(self.data_item.getBufferExpr())
        else:
            self.vectorFixedValue.setValue(self.frictionModel.getFreeVal())
            
        
    def setLayer(self,layer):
        self.vectorSelectionExpression.setLayer(layer)
        self.vectorFieldCombo.setLayer(layer)
        
    def setDefaultSetting(self,idx):
        if idx == 0:
            pass
        else:
            pass

    def setBurnMode(self,is_field_mode):
        self.vectorFieldMode.setChecked(is_field_mode)
        self.vectorFieldCombo.setEnabled(is_field_mode)
        self.keepValues.setEnabled(is_field_mode)
        self.vectorFixedMode.setChecked(not is_field_mode)
        self.vectorFixedValue.setEnabled(not is_field_mode)
        # self.vectorFixedCombo.setEnabled(not is_field_mode)
        
    def setFieldMode(self,checked):
        self.setBurnMode(checked)
        
    def setKeepValMode(self,checked):
        if checked:
            self.vectorFieldCombo.setFilters(QgsFieldProxyModel.Numeric)
        else:
            self.vectorFieldCombo.setFilters(QgsFieldProxyModel.AllTypes)
        
    # Useless function now : to delete (with calls)
    def setField(self,fieldname):
        pass
        
    def setFixedMode(self,checked):
        self.setBurnMode(not checked)
        # self.values = [self.vectorFixedValue.value()]
        
    def setBufferMode(self,checked):
        self.vectorBufferValue.setEnabled(checked)

    def showDialog(self):
        self.feedback.pushDebugInfo("showDialog")
        while self.exec_():
            dict = {}
            name = self.nameValue.text()
            if not utils.isValidTag(name):
                feedbacks.launchDialog(self,self.tr("Wrong value"),
                    self.tr("Name '{}' contains invalid characters".format(name)))
                continue
            dict[VectorDlgItem.NAME] = name
            layer = self.vectorLayerCombo.currentLayer()
            if not layer:
                feedbacks.paramError("No layer selected",parent=self)
                continue
            layer_path = qgsUtils.pathOfLayer(layer)
            if not layer_path:
                feedbacks.paramError("Could not load layer " + str(layer_path))
                continue
            dict[VectorDlgItem.INPUT] = layer_path
            # Expression
            expression = self.vectorSelectionExpression.currentText()
            self.feedback.pushDebugInfo("showDialog expression = {}".format(expression))
            dict[VectorDlgItem.EXPRESSION] = expression
            # Burn
            burn_field_mode = self.vectorFieldMode.isChecked()
            dict[VectorDlgItem.BURN_MODE] = burn_field_mode
            fieldname = self.vectorFieldCombo.currentField()
            dict[VectorDlgItem.BURN_FIELD] = fieldname
            dict[VectorDlgItem.KEEP_VAL] = self.keepValues.isChecked()
            if burn_field_mode:
                # Field mode
                if not fieldname:
                    feedbacks.paramError("No field selected")
                    continue
                # Check values count
                values = qgsTreatments.getVectorUniqueVals(layer,fieldname,feedback=self.feedback)
                nb_values = len(values)
                if nb_values > 40:
                    title = "High values count"
                    msg = "Field {} contains {} unique values, is it ok ?".format(fieldname,nb_values)
                    reply = feedbacks.launchQuestionDialog(self,title,msg)
                    self.feedback.pushDebugInfo("reply {}".format(reply))
                    if reply == QtWidgets.QMessageBox.No:
                        continue
                dict[VectorDlgItem.BURN_VAL] = ""
            else:
                # Fixed mode
                dict[VectorDlgItem.BURN_VAL] = self.vectorFixedValue.value()
            dict[VectorDlgItem.ALL_TOUCH] = self.vectorAllTouch.isChecked()
            # Buffer
            dict[VectorDlgItem.BUFFER_MODE] = self.vectorBufferMode.isChecked()
            dict[VectorDlgItem.BUFFER_EXPR] = self.vectorBufferValue.value()
            self.data_item = VectorDlgItem(dict)
            self.feedback.pushDebugInfo("dict = " + str(dict))
            return self.data_item
        return None
