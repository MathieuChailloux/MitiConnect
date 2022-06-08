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

from qgis.PyQt import uic, QtWidgets
from qgis.PyQt.QtCore import Qt

from ..qgis_lib_mc.utils import CustomException, getIntValues
from ..qgis_lib_mc.abstract_model import DictItem, ExtensiveTableModel, AbstractConnector


class FrictionModel(ExtensiveTableModel):

    def __init__(self,parentModel):
        self.parser_name = "FrictionModel"
        ExtensiveTableModel.__init__(self,parentModel)
        self.feedback.pushInfo("FM1 " + str(self.__class__.__name__))
        self.feedback.pushInfo("FM2 " + str(self.itemClass.__class__.__name__))
        
    def reload(self):
        colNames = self.parentModel.speciesModel.getNames()
        
    def getFreeVals(self,nbVals):
        codes = [ i.dict[self.ROW_CODE] for i in self.items ]
        freeVals = getIntValues(nbVals)
        return freeVals
        
    def getHeaderStr(self,col):
        if col < 2:
            h = [self.tr('Value'),self.tr('Description')]
            return h
        return None
        
        
          
class FrictionConnector(AbstractConnector):
    
    def __init__(self,dlg,frictionModel):
        self.dlg = dlg
        self.feedback = frictionModel.feedback
        super().__init__(frictionModel,self.dlg.frictionView)
                         #selectionCheckbox=self.dlg.frictRunOnlySelection)
        
    def initGui(self):
        pass
            
    def connectComponents(self):
        super().connectComponents()
        # self.dlg.frictionLoadClass.clicked.connect(self.model.reload)
        # self.dlg.frictionRun.clicked.connect(self.applyItems)
        self.dlg.frictionSave.clicked.connect(self.saveCSVAction)
        self.dlg.frictionLoad.clicked.connect(self.loadCSVAction)
        
    # Return indexes currently selected in friction view
    def getSelectedIndexes(self):
        if self.onlySelection:
            indexes = list(set([i.column() for i in self.view.selectedIndexes()]))
        else:
            indexes = range(3,len(self.model.fields))
        nb_indexes = len(indexes)
        if nb_indexes == 0:
            self.feedback.user_error("No species selected for friction step")
        nbCols = len(self.model.getExtFields())
        self.feedback.pushDebugInfo("nbCols = " + str(nbCols))
        for idx in indexes:
            st_idx = idx - 3
            if st_idx < 0 or st_idx >= nbCols:
                self.feedback.user_error("Column " + str(idx) + " selected is not a specie")
        return indexes
        
    # Updates model with items loaded from file 'fname'
    def loadCSV(self,fname):
        utils.checkFileExists(fname)
        self.model.fromCSVUpdate(fname)
        self.feedback.pushInfo("Friction loaded from '" + str(fname))
        
    # Opens file dialog and loads model from selected CSV file.
    def loadCSVAction(self):
        self.feedback.pushDebugInfo("loadCSVAction " + str(self))
        fname = qgsUtils.openFileDialog(parent=self.dlg,
                                      msg=self.tr("Open CSV file"),
                                      filter="*.csv")
        if fname:
            self.loadCSV(fname)
            
    def saveCSV(self,fname):
        self.model.saveCSV(fname)
     
    def saveCSVAction(self):
        self.feedback.pushDebugInfo("saveCSVAction")
        fname = qgsUtils.saveFileDialog(parent=self.dlg,
                                      msg="Save friction as CSV file",
                                      filter="*.csv")
        if fname:
            self.saveCSV(fname)
        
