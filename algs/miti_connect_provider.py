# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MitiConnect
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

from PyQt5.QtGui import QIcon
from qgis.core import QgsApplication, QgsProcessingProvider, QgsMessageLog, Qgis
from processing.core.ProcessingConfig import Setting, ProcessingConfig


from ..graphab4qgis.processing.CreateProject import CreateProject
from ..graphab4qgis.processing.CreateLinkset import CreateLinkset
from ..graphab4qgis.processing.CalculateCorridor import CalculateCorridor
from ..graphab4qgis.processing.CreateGraph import CreateGraph
from ..graphab4qgis.processing.CalculateLocalMetric import CalculateLocalMetric
from ..graphab4qgis.processing.CalculateGlobalMetric import CalculateGlobalMetric
from ..graphab4qgis.processing.GraphabProvider import GraphabProvider


class MitiConnectProvider(GraphabProvider):

    def __init__(self,plugin):
        super().__init__(plugin.graphabPlugin)
        self.alglist = [
            CreateLinkset(self.plugin),
            CreateProject(self.plugin),
            CalculateCorridor(self.plugin),
            CreateGraph(self.plugin),
            CalculateLocalMetric(self.plugin),
            CalculateGlobalMetric(self.plugin)]
        # for a in self.alglist:
            # self.addAlgorithm(a)
                
    def id(self):
        return "mitiConnect"
        
    def name(self):
        return "MitiConnect"
        
    def longName(self):
        return self.name()
        
    def icon(self):
        icon_path = os.path.join(os.path.dirname(__file__), "..", "icons", "icon.png")
        #icon_path = ':/plugins/FragScape/icons/icon.svg'
        # print("icon_path = " + str(icon_path))
        return QIcon(icon_path)
        
    def load(self):
        """In this method we add settings needed to configure our
        provider.
        """
        print("load")
        # ProcessingConfig.readSettings()
        ProcessingConfig.settingIcons[self.name()] = self.icon()

        ProcessingConfig.addSetting(Setting(self.name(), 'ACTIVATE_GRAPHAB',
                                            self.plugin.translate('py', 'Activate'), True))
        ProcessingConfig.addSetting(Setting(self.name(), 'GRAPHAB_VERSION',
                                            self.plugin.translate('py', 'Graphab version'), self.DEFAULT_VERSION))
        ProcessingConfig.addSetting(Setting(self.name(), 'MEMORY_GRAPHAB',
                                            self.plugin.translate('py', 'Max memory for Java in Gb'), 0))
        ProcessingConfig.addSetting(Setting(self.name(), 'PROC_GRAPHAB',
                                            self.plugin.translate('py', 'Processors/Cores used'), 0))
        javacmd = self.getJavaCommand(False)
        ProcessingConfig.addSetting(Setting(self.name(), 'JAVA_GRAPHAB',
                                            self.plugin.translate('py', 'Java path executable'), javacmd))
        # self.loadAlgorithms()
        self.refreshAlgorithms()
        return True

    def unload(self):
        """Setting should be removed here, so they do not appear anymore
        when the plugin is unloaded.
        """
        print("unload GP")
        if ProcessingConfig.getSetting('ACTIVATE_GRAPHAB'):
            ProcessingConfig.removeSetting('ACTIVATE_GRAPHAB')
        if ProcessingConfig.getSetting('GRAPHAB_VERSION'):
            ProcessingConfig.removeSetting('GRAPHAB_VERSION')
        if ProcessingConfig.getSetting('MEMORY_GRAPHAB'):
            ProcessingConfig.removeSetting('MEMORY_GRAPHAB')
        if ProcessingConfig.getSetting('PROC_GRAPHAB'):
            ProcessingConfig.removeSetting('PROC_GRAPHAB')
        if ProcessingConfig.getSetting('JAVA_GRAPHAB'):
            ProcessingConfig.removeSetting('JAVA_GRAPHAB')
        # print("unload 2 sys.modules = " + str(sys.modules))
        
    def getJavaCommand(self, useConfig = True):
        cmd = super().getJavaCommand(useConfig=False)
        print("getJavaCmd " + str(cmd))
        return cmd
        
    def getJavaPath(self):
        path = super().getJavaPath()
        print("getJavaPath " + str(path))
        return path
        
    def loadAlgorithms(self):
        # super().load()
        print("loadAlgorithms")
        # print("loadAlgorithms modules " + str(sys.modules))
        for a in self.alglist:
            self.addAlgorithm(a)
            
    def checkJavaInstalled(self):
        javaExec = self.getJavaCommand()
        try:
            ret = subprocess.run([javaExec, '-version'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.java = ret.returncode == 0
        except:
            self.java = False

        if not self.java:
            QgsMessageLog.logMessage("Java not found for Graphab plugin.\n" + javaExec + "\n", 'Extensions', Qgis.Warning)