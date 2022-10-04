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

from .qgis_lib_mc import utils
#import helps
from PyQt5.QtCore import QUrl, QFile, QIODevice, QTextStream
from PyQt5.QtGui import QTextDocument

class TabItem:

    def __init__(self,helpFile):
        self.descr = "TODO"
        self.helpFile = helpFile
        
    def setDescr(self,descr):
        self.descr = descr

    def getHelpFile(self):
        plugin_dir = os.path.dirname(__file__)
        help_dir = os.path.join(plugin_dir,"help")
        helpFile = os.path.join(help_dir,self.helpFile + "-" + utils.curr_language + ".html")
        return helpFile
        
paramsTabItem = TabItem("paramsHelp")
dataTabItem = TabItem("dataHelp")
spTabItem = TabItem("speciesHelp")
frictionTabItem = TabItem("frictionHelp")
scTabItem = TabItem("scenarioHelp")
launchItem = TabItem("launchHelp")
logTabItem = TabItem("logHelp")
        
class TabConnector:
    
    def __init__(self,dlg):
        self.tabs = [paramsTabItem,
                     dataTabItem,
                     spTabItem,
                     frictionTabItem,
                     scTabItem,
                     launchItem,
                     logTabItem]
        self.dlg = dlg
        self.curr_tab = 0
        
    def initGui(self):
        self.dlg.textShortHelp.setOpenLinks(True)
        self.loadNTab(0)
        
    def loadNTab(self,n):
        utils.debug("[loadNTab] " + str(n))
        nb_tabs = len(self.tabs)
        self.curr_tab = n
        if n >= nb_tabs:
            utils.internal_error("[loadNTab] loading " + str(n) + " tab but nb_tabs = " + str(nb_tabs))
        else:
            self.loadHelpFile()
            #utils.debug("source : " + str(self.dlg.textShortHelp.source()))

    def loadHelpFile(self):
        tabItem = self.tabs[self.curr_tab]
        helpFile = tabItem.getHelpFile()
        utils.debug("Help file = " + str(helpFile))
        utils.checkFileExists(helpFile)
        with open(helpFile) as f:
            msg = f.read()
        self.dlg.textShortHelp.setHtml(msg)
        

            
    def connectComponents(self):
        self.dlg.mTabWidget.currentChanged.connect(self.loadNTab)
            