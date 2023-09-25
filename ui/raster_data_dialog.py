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

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
# from qgis.core import QgsMapLayerProxyModel

from ..qgis_lib_mc import utils, qgsUtils, abstract_model, feedbacks, qgsTreatments

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'raster_data_dialog.ui'))

class ReclassItem(abstract_model.DictItem):
    
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    FIELDS = [ INPUT, OUTPUT ]

    @classmethod
    def fromValues(cls, in_val,out_val,feedback=None):
        d = { cls.INPUT : in_val, cls.OUTPUT : out_val }
        return cls(d,feedback=feedback)
        
    def getInVal(self):
        return self.dict[self.INPUT]
    def getOutVal(self):
        return self.dict[self.OUTPUT]
        
        
class ReclassModel(abstract_model.DictModel):
    
    def __init__(self, feedback=None):
        # itemClass = getattr(sys.modules[__name__], ReclassItem.__name__)
        # super().__init__(parent,itemClass=itemClass,feedback=parent.feedback)
        super().__init__(itemClass=ReclassItem,feedback=feedback)
    
    def getValues(self):
        return [i.dict[ReclassItem.INPUT] for i in self.items]
    def getCodes(self):
        return [i.dict[ReclassItem.OUTPUT] for i in self.items]
        
    def getReclassTable(self):
        table = []
        for i in self.items:
            inVal = i.getInVal()
            line = [inVal, inVal, i.getOutVal()]
            table.append(line)
        return table


class RasterDlgItem(abstract_model.DictItem):

    NAME = 'NAME'
    INPUT = 'INPUT'
    KEEP_VALUES = 'KEEP_VALUES'
    # RECLASS = 'RECLASS'
    FIELDS = [ INPUT ]

    def __init__(self, dict, feedback=None):
        if self.KEEP_VALUES not in dict:
            dict[self.KEEP_VALUES] = False
        super().__init__(dict,feedback=feedback)
        self.values = []
    def getName(self):
        return self.dict[self.NAME]
    def getLayerPath(self):
        return self.dict[self.INPUT]
    # def getReclassModel(self):
        # return self.getChild()
    def getValues(self):
        return self.values
        
    def getValue(self):
        return self.dict[self.KEEP_VALUES]
        
    @staticmethod
    def getItemClass(childTag):
        return ReclassModel
        # print("sys.modules " + str(sys.modules))
        # print("__name__ " + str(__name__))
        # print("ReclassModel.__name__ " + str(ReclassModel.__name__))
        # print("sys.modules[__name__] " + str(sys.modules[__name__]))
        # return getattr(sys.modules[__name__], ReclassModel.__name__)

class RasterDataDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, raster_data_item, parent,class_model=None):
        """Constructor."""
        super(RasterDataDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.feedback=parent.feedback
        self.data_item = raster_data_item
        # self.class_model = class_model
        self.setupUi(self)
        self.initGui()
        self.connectComponents()
        self.updateUi()
        # self.connectComponents()
        
    def initGui(self):
        self.layerComboDlg = qgsUtils.LayerComboDialog(self,
            self.rasterDataLayerCombo,self.rasterDataLayerOpen)
        self.layerComboDlg.setRasterMode()
        # if self.data_item:
            # self.reclass_model = self.data_item.child
        # else:
            # self.reclass_model = ReclassModel(feedback=self.feedback)
        #self.rasterDataLayerOpen.setFilter(qgsUtils.getRasterFilters())

    def connectComponents(self):
        # self.rasterDataDialogView.setModel(self.reclass_model)
        self.rasterDataLayerCombo.layerChanged.connect(self.setLayer)
        # self.reclass_model.layoutChanged.emit()
        
    def setLayer(self,layer):
        if layer:
            vals = qgsTreatments.getRasterUniqueVals(layer,
                feedback=self.feedback)
            self.values = vals
            # nb_vals = len(vals)
            # free_vals = self.class_model.getFreeVals(nb_vals)
            # self.reclass_model.items = [ReclassItem.fromValues(in_val,out_val,feedback=self.feedback)
                # for (in_val, out_val) in zip(vals, free_vals)]
            # self.reclass_model.layoutChanged.emit() 
    
    def updateUi(self):
        if self.data_item:
            name = self.data_item.getName()
            self.nameValue.setText(name)
            layer = self.data_item.getLayerPath()
            utils.checkFileExists(layer)
            self.layerComboDlg.setLayerPath(layer)
            self.keepValues.setChecked(self.data_item.getValue())
            # model = self.data_item.child
            # if model:
                # self.rasterDataDialogView.setModel(model)
                # model.layoutChanged.emit()
        
    def showDialog(self):
        self.feedback.pushDebugInfo("showDialog")
        while self.exec_():
            dict = {}
            name = self.nameValue.text()
            dict[RasterDlgItem.NAME] = name
            if not name.isalnum():
                feedbacks.paramError("Name '" + str(name) + "' is not alphanumeric",parent=self)
                continue
            layer = self.rasterDataLayerCombo.currentLayer()
            if not layer:
                feedbacks.paramError("No layer selected",parent=self)
                continue
            layer_path = qgsUtils.pathOfLayer(layer)
            if not layer_path:
                feedbacks.paramError("Could not load layer " + str(layer_path),parent=self)
                continue
            dict[RasterDlgItem.INPUT] = layer_path
            dict[RasterDlgItem.KEEP_VALUES] = self.keepValues.isChecked()
            # dict[RasterDlgItem.RECLASS] = self.reclass_model
            self.data_item = RasterDlgItem(dict,feedback=self.feedback)
            # self.data_item.setChild(self.rasterDataDialogView.model())
            self.data_item.values = self.values
            # self.data_item.isScenario = self.isScenario.isChecked()
            # self.data_item.setChild(self.reclass_model)
            return self.data_item
        return None
        
    # def getReclassTable(self):
        # return self.reclass_model.getReclassTable()
    def getValues(self):
        return self.values
        # return self.reclass_model.getValues()
