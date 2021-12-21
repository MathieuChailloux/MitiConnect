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
import traceback
from io import StringIO

from .qgis_lib_mc import feedbacks, log, utils, abstract_model
from .steps import (params, data, species, friction, scenario)#, species, friction, scenarios)

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
PLUGIN_DIR = os.path.dirname(__file__)
UI_DIR = os.path.join(PLUGIN_DIR,'ui')
STEPS_DIR = os.path.join(PLUGIN_DIR,'steps')
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    UI_DIR, 'erc_tvb_plugin_dialog_base.ui'))


class PluginModel(abstract_model.MainModel):

    def __init__(self,feedback):
        self.parser_name = "ERC-TVB"
        self.context = None
        self.feedback = feedback
        self.feedback.pushDebugInfo("feedback bd = " + str(feedback))
        self.paramsModel = params.ParamsModel(self)
        self.importModel = data.ImportModel(self)
        self.landuseModel = data.LanduseModel(self)
        self.speciesModel = species.SpeciesModel(self)
        self.frictionModel = friction.FrictionModel(self)
        self.scenarioModel = scenario.ScenarioModel(self)
        self.models = [ self.paramsModel, self.importModel,
            self.landuseModel, self.speciesModel, self.frictionModel,
            self.scenarioModel ]
            
    def addImport(self,import_item):
        self.frictionModel.addRowItem(import_item)
    def addSpecies(self,species_item):
        item_name = species_item.getName()
        self.frictionModel.addCol(item_name)
        # self.landuseModel.addItem()
        # self.frictionModel.addImport(import_item)
    def removeImport(import_item):
        #self.landuseModel.
        # self.frictionModel.removeImport(import_item)
        pass
        
    def getImportsDir(self):
        return utils.createSubDir(self.paramsModel.workspace,"Imports")
    def getScenarioDir(self,sc_name):
        return utils.createSubDir(self.paramsModel.workspace,sc_name)
        
    def checkWorkspaceInit(self):
        self.paramsModel.checkWorkspaceInit()
    def normalizePath(self,path):
        return self.paramsModel.normalizePath(path)
    def getOrigPath(self,path):
        return self.paramsModel.getOrigPath(path)
    def mkOutputFile(self,name):
        return self.paramsModel.mkOutputFile(name)
    def getRasterParams(self):
        crs = self.paramsModel.crs
        extent = self.paramsModel.getExtentString()
        resolution = self.paramsModel.getResolution()
        return (crs, extent, resolution)
        

    

class ErcTvbPluginDialog(abstract_model.MainDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(ErcTvbPluginDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.pluginName = 'ERC-TVB'
            
    def initTabs(self):
        self.feedback =  feedbacks.ProgressFeedback(self)
        self.pluginModel = PluginModel(self.feedback)
        self.importConnector = data.ImportConnector(self,self.pluginModel.importModel)
        self.landuseConnector = data.LanduseConnector(self,self.pluginModel.landuseModel)
        self.speciesConnector = species.SpeciesConnector(self,self.pluginModel.speciesModel)
        self.frictionConnector = friction.FrictionConnector(self,self.pluginModel.frictionModel)
        self.scenarioConnector = scenario.ScenarioConnector(self,self.pluginModel.scenarioModel)
        self.connectors = [ self.feedback, self.importConnector,
            self.landuseConnector, self.speciesConnector,
            self.frictionConnector, self.scenarioConnector ]
        
    # Exception hook, i.e. function called when exception raised.
    # Displays traceback and error message in log tab.
    # Ignores CustomException : exception raised from erc_tvb and already displayed.
    def exceptionHook(self,excType, excValue, tracebackobj):
        self.feedback.pushDebugInfo("exceptionHook")
        if excType == utils.CustomException:
            self.feedback.pushDebugInfo("Ignoring custom exception : " + str(excValue))
        else:
            tbinfofile = StringIO()
            traceback.print_tb(tracebackobj, None, tbinfofile)
            tbinfofile.seek(0)
            tbinfo = tbinfofile.read()
            errmsg = str(excType.__name__) + " : " + str(excValue)
            separator = '-' * 80
            msg = separator + "\n" + errmsg + "\n" + separator
            self.feedback.pushDebugInfo(str(msg))
            self.feedback.pushWarning("Traceback : " + tbinfo)
            self.feedback.error_msg(msg,prefix="Unexpected error")
        self.mTabWidget.setCurrentWidget(self.logTab)
        
        