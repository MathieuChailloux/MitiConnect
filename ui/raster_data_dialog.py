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

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
# from qgis.core import QgsMapLayerProxyModel

from ..qgis_lib_mc import qgsUtils, abstract_model

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'raster_data_dialog.ui'))

class ReclassItem(abstract_model.DictItem):
    
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    FIELDS = [ INPUT, OUTPUT ]

    def __init__(self, in_val,out_val):
        d = { self.INPUT : in_val, self.OUTPUT : out_val }
        super().__init__(d,self.FIELDS)
        
        
class ReclassModel(abstract_model.DictModel):
    
    def __init__(self, parent):
        # itemClass = getattr(sys.modules[__name__], ReclassItem.__name__)
        # super().__init__(parent,itemClass=itemClass,feedback=parent.feedback)
        super().__init__(parent,itemClass=ReclassItem,
            feedback=parent.feedback)
    
    def getCodes(self):
        return [i.dict[ReclassItem.OUTPUT] for i in self.items]


class RasterDlgItem(abstract_model.DictItem):

    INPUT = 'INPUT'
    RECLASS = 'RECLASS'
    FIELDS = [ INPUT, RECLASS ]

    def __init__(self, dict, parent=None):
        super().__init__(dict,self.FIELDS)
    def getReclassModel(self):
        return self.dict[self.RECLASS]

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
        self.class_model = class_model
        self.reclass_model = ReclassModel(self)
        self.setupUi(self)
        self.layerComboDlg = qgsUtils.LayerComboDialog(self,
            self.rasterDataLayerCombo,self.rasterDataLayerOpen)
        self.layerComboDlg.setRasterMode()
        self.connectComponents()

    def connectComponents(self):
        self.rasterDataDialogView.setModel(self.reclass_model)
        self.rasterDataLayerCombo.layerChanged.connect(self.setLayer)
        
    def setLayer(self,layer):
        vals = qgsUtils.getRasterValsBis(layer)
        nb_vals = len(vals)
        free_vals = self.class_model.getFreeVals(nb_vals)
        self.reclass_model.items = [ReclassItem(in_val,out_val)
            for (in_val, out_val) in zip(vals, free_vals)]
        self.reclass_model.layoutChanged.emit() 
        
    def showDialog(self):
        self.feedback.pushDebugInfo("showDialog")
        while self.exec_():
            dict = {}
            layer = self.rasterDataLayerCombo.currentLayer()
            if not layer:
                self.feedback.user_error("No layer selected")
            layer_path = qgsUtils.pathOfLayer(layer)
            if not layer_path:
                self.feedback.user_error("Could not load layer " + str(layer_path))
            dict[RasterDlgItem.INPUT] = layer_path
            dict[RasterDlgItem.RECLASS] = self.reclass_model
            self.data_item = RasterDlgItem(dict)
            return self.data_item
        return None
