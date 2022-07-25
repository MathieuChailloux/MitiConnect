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

import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
# from qgis.core import QgsMapLayerProxyModel

from ..qgis_lib_mc import utils, qgsUtils, abstract_model

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'vector_data_dialog.ui'))

class VectorDlgItem(abstract_model.DictItem):

    NAME = 'NAME'
    INPUT = 'INPUT'
    EXPRESSION = 'EXPRESSION'
    BURN_MODE = 'BURN_MODE'
    BURN_FIELD = 'BURN_FIELD'
    BURN_VAL = 'BURN_VAL'
    ALL_TOUCH = 'ALL_TOUCH'
    BUFFER_MODE = 'BUFFER_MODE'
    BUFFER_EXPR = 'BUFFER_EXPR'
    FIELDS = [ NAME, INPUT, EXPRESSION, BURN_MODE, BURN_FIELD, BURN_VAL,
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
    def getBurnField(self):
        return self.dict[self.BURN_FIELD]
    def getBurnVal(self):
        return self.dict[self.BURN_VAL]
    def getAllTouch(self):
        return self.dict[self.ALL_TOUCH]
    def getBufferMode(self):
        return self.dict[self.BUFFER_MODE]
    def getBufferExpr(self):
        return self.dict[self.BUFFER_EXPR]


# TODO : idée : génération automatique XML depuis QDialog 
# en fonction des widgets ??
class VectorDataDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, vector_data_item, parent):
        """Constructor."""
        super(VectorDataDialog, self).__init__(parent)
        self.feedback=parent.feedback
        self.data_item = vector_data_item
        self.setupUi(self)
        self.layerComboDlg = qgsUtils.LayerComboDialog(self,
            self.vectorLayerCombo,self.vectorLayerFile)
        self.layerComboDlg.setVectorMode()
        self.connectComponents()
        self.updateUi()

    # def mkItem(self):
        # layer = self.vectorLayerFile.fileInfo()
        
        
    def connectComponents(self):
        self.vectorLayerCombo.layerChanged.connect(self.setLayer)
        self.vectorDefaultSetting.currentIndexChanged.connect(
            self.setDefaultSetting)
        self.vectorFieldMode.clicked.connect(self.setFieldMode)
        self.vectorFixedMode.clicked.connect(self.setFixedMode)
        self.vectorBufferMode.clicked.connect(self.setBufferMode)
        
    def updateUi(self):
        # print("update")
        if self.data_item:
            # print("lets go")
            self.nameValue.setText(self.data_item.getName())
            self.vectorLayerCombo.setLayer(None)
            self.layerComboDlg.setLayerPath(self.data_item.getLayerPath())
            self.vectorSelectionExpression.setExpression(self.data_item.getExpression())
            self.setBurnMode(self.data_item.getBurnMode())
            self.vectorFieldCombo.setField(self.data_item.getBurnField())
            self.vectorFixedValue.setValue(self.data_item.getBurnVal())
            self.vectorAllTouch.setChecked(self.data_item.getAllTouch())
            bm = self.data_item.getBufferMode()
            self.vectorBufferMode.setChecked(bm)
            self.vectorBufferValue.setEnabled(bm)
            self.vectorBufferValue.setValue(self.data_item.getBufferExpr())
        
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
        self.vectorFixedMode.setChecked(not is_field_mode)
        self.vectorFixedValue.setEnabled(not is_field_mode)
        
    def setFieldMode(self,checked):
        self.setBurnMode(checked)
        
    def setFixedMode(self,checked):
        self.setBurnMode(not checked)
        
    def setBufferMode(self,checked):
        self.vectorBufferValue.setEnabled(checked)

    def showDialog(self):
        self.feedback.pushDebugInfo("showDialog")
        while self.exec_():
            dict = {}
            name = self.nameValue.text()
            if not name:
                self.feedback.user_error("Empty name")
            dict[VectorDlgItem.NAME] = name
            layer = self.vectorLayerCombo.currentLayer()
            if not layer:
                self.feedback.user_error("No layer selected")
            layer_path = qgsUtils.pathOfLayer(layer)
            if not layer_path:
                self.feedback.user_error("Could not load layer " + str(layer_path))
            dict[VectorDlgItem.INPUT] = layer_path
            dict[VectorDlgItem.EXPRESSION] = self.vectorSelectionExpression.currentText()
            burn_field_mode = self.vectorFieldMode.isChecked()
            dict[VectorDlgItem.BURN_MODE] = burn_field_mode
            dict[VectorDlgItem.BURN_FIELD] = self.vectorFieldCombo.currentField()
            dict[VectorDlgItem.BURN_VAL] = self.vectorFixedValue.value()
            dict[VectorDlgItem.ALL_TOUCH] = self.vectorAllTouch.isChecked()
            dict[VectorDlgItem.BUFFER_MODE] = self.vectorBufferMode.isChecked()
            dict[VectorDlgItem.BUFFER_EXPR] = self.vectorBufferValue.value()
            self.data_item = VectorDlgItem(dict)
            self.feedback.pushDebugInfo("dict = " + str(dict))
            return self.data_item
        return None