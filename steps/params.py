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

import os.path
import pathlib

from qgis.core import (QgsCoordinateReferenceSystem, QgsRectangle, QgsProject,
                       QgsCoordinateTransform, QgsProcessingUtils)
from qgis.gui import QgsFileWidget
from PyQt5.QtCore import QVariant, QAbstractTableModel, QModelIndex, Qt, QCoreApplication
from PyQt5.QtWidgets import QAbstractItemView, QFileDialog, QHeaderView

from ..qgis_lib_mc import utils, qgsUtils, qgsTreatments, abstract_model

# BioDispersal global parameters

# ParamsModel from which parameters are retrieved
paramsModel = None

# Default CRS is set to epsg:2154 (France area, metric system)
defaultCrs = QgsCoordinateReferenceSystem("EPSG:2154")
        
#class ParamsModel(abstract_model.AbstractGroupModel):
class ParamsModel(abstract_model.NormalizingParamsModel):

    def __init__(self,parentModel):
        self.parser_name = "ParamsModel"
        self.is_runnable = False
        # self.workspace = None
        # self.extentLayer = None
        # self.resolution = 0.0
        # self.projectFile = ""
        # self.crs = defaultCrs
        # fields = ["workspace","extentLayer","resolution","projectFile","crs"]
        abstract_model.NormalizingParamsModel.__init__(self,feedback=parentModel.feedback)
        
    # def setWorkspace(self,workspace,name):
        # super().setWorkspace(workspace)
    
    def toXML(self,indent=""):
        xmlStr = indent + "<" + self.parser_name
        if self.workspace:
            xmlStr += " workspace=\"" + str(self.workspace) + "\""
        if self.resolution:
            xmlStr += " resolution=\"" + str(self.resolution) + "\""
        if self.extentLayer:
            xmlStr += " extentLayer=\"" + str(self.extentLayer) + "\""
        xmlStr += "/>"
        return xmlStr
        

class ParamsConnector:

    def __init__(self,dlg,paramsModel):
        self.dlg = dlg
        self.model = paramsModel
        
    def initGui(self):
        self.dlg.paramsView.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.dlg.paramsCrs.setCrs(defaultCrs)
        
    def connectComponents(self):
        self.dlg.paramsView.setModel(self.model)
        self.dlg.rasterResolution.valueChanged.connect(self.model.setResolution)
        self.dlg.extentLayer.setStorageMode(QgsFileWidget.GetFile)
        self.dlg.extentLayer.fileChanged.connect(self.model.setExtentLayer)
        self.dlg.workspace.setStorageMode(QgsFileWidget.GetDirectory)
        self.dlg.workspace.fileChanged.connect(self.model.setWorkspace)
        self.dlg.paramsCrs.crsChanged.connect(self.model.setCrs)
        header = self.dlg.paramsView.horizontalHeader()     
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        self.model.layoutChanged.emit()
        
    def tr(self, message):
        return QCoreApplication.translate('ERC-TVB', message)
        
    def refreshProjectName(self):
        fname = self.model.projectFile
        basename = os.path.basename(fname)
        if basename:
            self.dlg.projectName.setText(self.tr("Projet ERC-TVB : ") + basename)
        else:
            self.dlg.projectName.setText(self.tr("Pas de projet ERC-TVB"))
        
    def setProjectFile(self,fname):
        self.model.projectFile = fname
        self.refreshProjectName()
        # basename = os.path.basename(fname)
        # if basename:
            # self.dlg.projectName.setText(self.tr("Current project : ") + basename)
