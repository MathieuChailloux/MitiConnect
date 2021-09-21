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

from .landuse_dialog import ImportConnector, ImportModel
from ..qgis_lib_mc import feedbacks, log, utils

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'erc_tvb_plugin_dialog_base.ui'))


class ErcTvbPluginDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(ErcTvbPluginDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        
        self.feedback =  feedbacks.TabProgressFeedback(self)
        self.importConnector = ImportConnector(self,ImportModel(self.feedback))
        self.connectors = [ self.feedback, self.importConnector ]
        
    def connectComponents(self):
        for tab in self.connectors:
            tab.connectComponents()
        sys.excepthook = self.exceptionHook
        
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
        
        