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

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

from ..qgis_lib_mc.abstract_model import DictItem

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'vector_data_dialog.ui'))

class VectorDataItem(DictItem):

    PATH = 'PATH'
    EXPRESSION = 'EXPRESSION'
    BURN_MODE = 'BURN_MODE'
    BURN_VAL = 'BURN_VAL'
    ALL_TOUCH = 'ALL_TOUCH'
    BUFFER_MODE = 'BUFFER_MODE'
    BUFFER_EXPR = 'BUFFER_EXPR'
    ITEM_FIELDS = [ PATH, EXPRESSION, BURN_MODE, BURN_VAL,
            ALL_TOUCH, BUFFER_MODE, BUFFER_EXPR ]

    def __init__(self, parent=None):
        super().__init__(self.ITEM_FIELDS)

class VectorDataDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(VectorDataDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)


    def showDialog(self):
        while self.exec_():
            return None
        
        return None