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

from ..qgis_lib_mc import abstract_model, feedbacks, utils

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'landuse_dialog.ui'))
        
class LanduseDialogItem(abstract_model.DictItem):

    NAME = 'NAME'
    FIELDS = [ NAME ]
    
    def __init__(self, name, parent=None):
        dict = { self.NAME : name }
        super().__init__(dict, self.FIELDS)
        
    def getName(self):
        return self.dict[self.NAME]
        
class LanduseDialogModel(abstract_model.DictModel):

    NAME = 'NAME'
    LIST = 'LIST'
    FIELDS = [ NAME ]
    
    def __init__(self, name, string_list,pluginModel):
        #itemClass = utils.getModuleRelativePath(__name__,LanduseDialogItem.__name__)
        itemClass = getattr(sys.modules[__name__], LanduseDialogItem.__name__)
        super().__init__(itemClass=itemClass,feedback = pluginModel.feedback)
        self.pluginModel = pluginModel
        # self.feedback = pluginModel.feedback
        self.name = name
        self.setItemsFromList(string_list)
        
    def setItemsFromList(self,string_list):
        self.feedback.pushDebugInfo("string_list = " + str(string_list))
        self.items = []
        for s in string_list:
            self.feedback.pushDebugInfo("s = " + str(s))
            string_item = LanduseDialogItem(s)
            self.addItem(string_item)
            
    def reloadNames(self):
        self.setItemsFromList(self.pluginModel.importModel.getImportNames())
        self.layoutChanged.emit()
        
    def getName(self):
        return self.name
    def setName(self,name):
        self.name = name
        

class LanduseDialogConnector(abstract_model.AbstractConnector):

    def __init__(self,dlg,landuseDialogModel):
        self.dlg = dlg
        self.feedback = landuseDialogModel.feedback
        super().__init__(landuseDialogModel,self.dlg.landuseDialogView,
                        None,self.dlg.landuseDialogRemove)
                        
    def connectComponents(self):
        super().connectComponents()
        self.dlg.landuseDialogReload.clicked.connect(self.model.reloadNames)
        self.dlg.landuseDialogUp.clicked.connect(self.upgradeItem)
        self.dlg.landuseDialogDown.clicked.connect(self.downgradeItem)
        self.dlg.landuseDialogName.textChanged.connect(self.model.setName)

class LanduseItem(abstract_model.DictItem):

    NAME = 'NAME'
    IMPORTS = 'IMPORTS'
    FIELDS = [ NAME, IMPORTS ]
    
    @classmethod
    def fromValues(cls,name=None, imports=None,feedback=None):
        dict = { cls.NAME : name, cls.IMPORTS : imports }
        return cls(dict,feedback=feedback)
        
    def getName(self):
        return self.dict[self.NAME]
    def getImports(self):
        return self.dict[self.IMPORTS]
    def getImportsAsList(self):
        return self.getImports().split(",")
    def setName(self,name):
        self.dict[self.NAME] = name
    def renameImport(self,oldName,newName):
        imports = self.getImportsAsList()
        imports = [newName if i == oldName else i for i in imports]
        self.dict[self.IMPORTS]= ",".join(imports)
    def setImports(self,imports):
        self.dict[self.IMPORTS] = imports

class LanduseDialog(QtWidgets.QDialog, FORM_CLASS):#, abstract_model.AbstractConnector):
    def __init__(self, parent, pluginModel, name = "", string_list = []):
        """Constructor."""
        super(LanduseDialog, self).__init__(parent)
        self.setupUi(self)
        # super().__init__(parent)
        self.feedback=parent.feedback
        self.feedback.pushDebugInfo("string_list = " + str(string_list))
        self.model = LanduseDialogModel(name,string_list,pluginModel)
        self.connector = LanduseDialogConnector(self,self.model)
        self.connector.connectComponents()
        self.updateUi()
        
    def updateUi(self):
        self.landuseDialogName.setText(self.model.getName())
        self.model.layoutChanged.emit()
        
    def showDialog(self):
        self.feedback.pushDebugInfo("showDialog")
        while self.exec_():
            name = self.landuseDialogName.text()
            if not name.isalnum():
                feedbacks.paramError("Name '" + str(name) + "' is not alphanumeric",parent=self)
                continue
            imports = [ i.getName() for i in self.model.items ]
            imports_str = ",".join(imports)
            item = LanduseItem.fromValues(name=name,imports=imports_str,feedback=self.feedback)
            return item
        return None
            
            
