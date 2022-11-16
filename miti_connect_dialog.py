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
from builtins import IOError, OSError

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.gui import QgsFileWidget
from qgis.core import Qgis, QgsProcessingContext, QgsProcessingException
import traceback
from io import StringIO

from .qgis_lib_mc import feedbacks, log, utils, abstract_model, qgsTreatments
from .steps import (params, data, species, friction, scenario, launches)#, species, friction, scenarios)
from . import tabs

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
PLUGIN_DIR = os.path.dirname(__file__)
UI_DIR = os.path.join(PLUGIN_DIR,'ui')
STEPS_DIR = os.path.join(PLUGIN_DIR,'steps')
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    UI_DIR, 'miti_connect_dialog_base.ui'))
CREATE_PROJECT_CLASS, _ = uic.loadUiType(os.path.join(
    UI_DIR, 'new_project.ui'))


class MitiConnectModel(abstract_model.MainModel):

    def __init__(self,graphabPlugin,feedback):
        self.parser_name = "ERC-TVB"
        self.feedback = feedback
        self.feedback.pushDebugInfo("feedback bd = " + str(feedback))
        self.graphabPlugin = graphabPlugin
        self.paramsModel = params.ParamsModel(self)
        self.importModel = data.ImportModel(self)
        self.importModel.feedback.pushInfo("PM OK")
        self.landuseModel = data.LanduseModel(self)
        self.speciesModel = species.SpeciesModel(self)
        self.frictionModel = friction.FrictionModel(self)
        self.scenarioModel = scenario.ScenarioModel(self)
        self.launchModel = launches.LaunchModel(self)
        self.models = [ self.paramsModel, self.importModel,
            self.landuseModel, self.speciesModel, self.frictionModel,
            self.scenarioModel, self.launchModel ]
        self.baseType = Qgis.UInt16
        self.nodataVal = 65535
            
    def getLanduseNames(self):
        return self.landuseModel.getNames()
            
    def addImport(self,import_item):
        self.frictionModel.addRowItem(import_item)
    def addSpecie(self,specie_item):
        item_name = specie_item.getName()
        self.frictionModel.addCol(item_name)
        # self.scenarioModel.speciesSelection.addItems(item_name)
        # self.landuseModel.addItem()
        # self.frictionModel.addImport(import_item)
    def removeImports(self,importNames):
        self.frictionModel.removeImports(importNames)
    def removeSpecies(self,speciesName):
        #TODO ; friction
        # self.scenarioModel.speciesSelection.removeItem(idx)
        pass
    def reloadFriction(self):
        import_names = [i.getName() for i in self.importModel.items]
        self.frictionModel.reloadFriction(imports=import_names)
        
    def getSubDir(self,name,baseDir=None):
        if baseDir is None:
            baseDir = self.paramsModel.workspace
        return utils.createSubdir(baseDir,name)
    def getImportsDir(self):
        return self.getSubDir("Imports")
    # def getScenarioDir(self,sc_name):
        # return utils.createSubdir(self.paramsModel.workspace,sc_name)
        
    def getImportOutLayerFromName(self,name):
        layer = self.getOutLayerFromName(name,self.importModel)
        return layer
    def getLanduseOutLayerFromName(self,name):
        layer = self.getOutLayerFromName(name,self.landuseModel)
        return layer
    def getScenarioOutLayerFromName(self,name):
        layer = self.getOutLayerFromName(name,self.landuseModel)
        return layer
        
    # def applyRename(self,oldName,newName,model):
        # for item in model.items:
            # if item.getName() == oldName:
                # item.setName(newName)
        # model.layoutChanged.emit()
    def renameClassImports(self,oldName,newName):
        self.frictionModel.renameImport(oldName,newName)
    def renameData(self,oldName,newName):
        for item in self.speciesModel.items:
            if item.getLanduse() == oldName:
                item.setLanduse(newName)
        self.speciesModel.layoutChanged.emit()
    def renameImport(self,oldName,newName):
        self.renameData(oldName,newName)
        self.renameClassImports(oldName,newName)
        for li in self.landuseModel.items:
            li.renameImport(oldName,newName)
        self.landuseModel.layoutChanged.emit()
        
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

    def getImportNames(self):
        return [i.getName() for i in self.importModel.items]
    def getDataNames(self):
        dataItems = self.importModel.items + self.landuseModel.items
        return [i.getName() for i in dataItems]
    def getDataOutPathFromName(self,name):
        importItem = self.importModel.getItemFromName(name)
        if importItem:
            return self.importModel.getItemOutPath(importItem)
        else:
            landuseItem = self.landuseModel.getItemFromName(name)
            if landuseItem:
                return self.landuseModel.getItemOutPath(landuseItem)
            else:
                self.feedback.pushDebugInfo("No data item named '"
                    + str(name) + "'")
        
    def loadProject(self, filename,retFlag=False):
        self.graphabPlugin.loadProject(filename)
        if retFlag:
            assert(False)
            project = self.graphabPlugin.getProject(filename)
            print("retFlag True")
            print("filename " + str(filename))
            print("project = " + str(project))
            print("projects = " + str(self.graphabPlugin.projects))
            return project

class CreateProjectDialog(QtWidgets.QDialog,CREATE_PROJECT_CLASS):

    def __init__(self, parent=None):
        super(CreateProjectDialog, self).__init__(parent)
        self.setupUi(self)
        self.workspaceDir.setStorageMode(QgsFileWidget.GetDirectory)
        
    def showDialog(self):
        while self.exec_():
            d = self.workspaceDir.filePath()
            n = self.projectName.text()
            if not n.isalnum():
                feedbacks.launchDialog(self,self.tr("Wrong value"),
                    self.tr("Project name '") + str(n) + str("' must be an alphanumeric string"))
                continue
            joined = utils.joinPath(d,n)
            if utils.fileExists(joined):
                feedbacks.launchDialog(self,self.tr("Wrong value"),
                    self.tr("Directory '") + str(joined) + str("' already exists"))
                continue
            return (d,n,joined)
        return None
            

class MitiConnectDialog(abstract_model.MainDialog, FORM_CLASS):
    def __init__(self, graphabPlugin,parent=None):
        """Constructor."""
        super(MitiConnectDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.pluginName = 'MitiConnect'
        self.graphabPlugin = graphabPlugin
            
    def initTabs(self):
        self.feedback =  feedbacks.ProgressFeedback(self)
        # self.feedback.pushInfo("ERC1 OK")
        utils.print_func = self.feedback.print_func
        qgsTreatments.nodata_val = 0
        self.context = QgsProcessingContext()
        self.context.setFeedback(self.feedback)
        # self.feedback.switchDebugMode()
        # self.feedback.pushInfo("hey")
        self.pluginModel = MitiConnectModel(self.graphabPlugin,self.feedback)
        # self.pluginModel.feedback.pushInfo("ERC2 OK")
        self.paramsConnector = params.ParamsConnector(self,self.pluginModel.paramsModel)
        self.importConnector = data.ImportConnector(self,self.pluginModel.importModel)
        # self.importConnector.feedback.pushInfo("ERC3 OK")
        self.landuseConnector = data.LanduseConnector(self,self.pluginModel.landuseModel)
        self.speciesConnector = species.SpeciesConnector(self,self.pluginModel.speciesModel)
        self.frictionConnector = friction.FrictionConnector(self,self.pluginModel.frictionModel)
        self.scenarioConnector = scenario.ScenarioConnector(self,self.pluginModel.scenarioModel)
        self.launchConnector = launches.LaunchConnector(self,self.pluginModel.launchModel)
        self.tabConnector = tabs.TabConnector(self)
        self.tabConnector.loadHelpFile()
        self.connectors = [ self.feedback,
            self.paramsConnector, self.importConnector,
            self.landuseConnector, self.speciesConnector,
            self.frictionConnector, self.scenarioConnector,
            self.launchConnector, self.tabConnector ]
            
    def connectComponents(self):
        super().connectComponents(saveAsFlag=True)
        self.initializeProject.clicked.connect(self.createNewProject)
        
    def createNewProject(self):
        dlgObj = CreateProjectDialog(parent=self)
        createDlg = dlgObj.showDialog()
        if createDlg:
            d, n, workspace = createDlg
            if workspace:
                self.initializeWorkspace(workspace,n)
        
    # def getScenariosDir(self):
        # self.scDir = utils.joinPath(workspace,"Scenarios")
        # return 
    # def getScenarioDir(self,scDir):
        # return utils.joinPath(self.scDir,scDir)
    def initializeWorkspace(self,workspace,name):
        utils.mkDir(workspace)
        self.pluginModel.paramsModel.setWorkspace(workspace)
        self.workspace.setFilePath(workspace)
        # self.scDir = utils.joinPath(workspace,"Scenarios")
        # utils.mkDir(self.scDir)
        projectFile = utils.joinPath(workspace, name + ".xml")
        self.saveModelAs(projectFile)
                
    # Exception hook, i.e. function called when exception raised.
    # Displays traceback and error message in log tab.
    # Ignores CustomException : exception raised from MitiConnect and already displayed.
    def pluginExcHook(self,excType, excValue, tracebackobj):
        self.feedback.pushDebugInfo("exceptionHook")
        self.feedback.pushDebugInfo(str(excType))
        self.feedback.pushDebugInfo(str(excType.__name__))
        tbinfofile = StringIO()
        traceback.print_tb(tracebackobj, None, tbinfofile)
        tbinfofile.seek(0)
        tbinfo = tbinfofile.read()
        errmsg = str(excType.__name__) + " : " + str(excValue)
        separator = '-' * 80
        msg = separator + "\n" + errmsg + "\n" + separator
        self.feedback.pushDebugInfo("Traceback : " + tbinfo)
        if excType == utils.CustomException:
            self.feedback.pushDebugInfo("Ignoring custom exception : " + str(excValue))
        elif excType == utils.UserError:
            self.feedback.user_error(str(excValue))
        elif excType == utils.InternalError:
            self.feedback.internal_error(str(excValue))
        elif excType == utils.TodoError:
            self.feedback.todo_error(str(excValue))
        elif excType == QgsProcessingException:
            self.feedback.pushDebugInfo("Graphab catched")
            try:
                msg1 = str(excValue).split("Exception:")[1]
                msg2 = msg1.split("at org")[0]
                self.feedback.pushDebugInfo(msg)
                self.feedback.error_msg(msg2,prefix="Graphab error")
            except Exception as e:
                raise e
                self.feedback.error_msg(msg,prefix="Unexpected error")
        else:
            self.feedback.error_msg(msg,prefix="Unexpected error")
        self.mTabWidget.setCurrentWidget(self.logTab)
        self.feedback.focusLogTab()
        
        
