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
import os.path, sys

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from qgis.core import QgsApplication
# from qgis.utils import qgis_excepthook

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .qgis_lib_mc import utils
from .miti_connect_dialog import MitiConnectDialog

from .algs.miti_connect_provider import MitiConnectProvider
from .graphab4qgis.GraphabPlugin import GraphabPlugin
from .graphab4qgis.GraphabStyle import GraphabStyle
from .graphab4qgis.graph_symbology_dialog import GraphSymbologyDialog
from .graphab4qgis.create_graph_dialog import CreateGraphDialog
from .graphab4qgis.create_linkset_dialog import CreateLinksetDialog
from .graphab4qgis.calculate_metrics_dialog import CalculateMetricDialog
from .graphab4qgis.corridor_dialog import CorridorDialog
from .graphab4qgis.OsRaster.OsRaster import OsRaster

# backup_modules = None

class GraphabPluginOverride(GraphabPlugin):

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            '{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        
        # all available styles for Graph circles
        self.stylesTabUnabled = ["Red","Blue"]
        
        # csv prefix that is important to know because it's in imported fieldnames
        self.prefix = '_'

        self.UNITS = [self.translate('py', 'Meter'), self.translate('py', 'Cost')]

        # All necessary objects
        self.GraphabStyle = GraphabStyle(self)
        self.GraphSymbologyDialog = GraphSymbologyDialog(self)
        self.CreateGraphDialog = CreateGraphDialog(self)
        self.CreateLinksetDialog = CreateLinksetDialog(self)
        self.CalculateMetricDialogGlobal = CalculateMetricDialog(self.GMETRICS, 0, self)
        self.CalculateMetricDialogLocal = CalculateMetricDialog(self.LMETRICS, 1, self)
        self.CorridorDialog = CorridorDialog(self)

        # Initialization of OsRaster
        self.OsRaster = OsRaster(self)

        self.actions = []
        # self.graphabProvider = GraphabProvider(self)
        # QgsApplication.processingRegistry().addProvider(self.graphabProvider)

        # def loadProject(self, filename):
            # print("loadPRoj 1 " + str(filename))
            # d = {filename : None}
            # print("loadPRoj dict " + str(d))
            # normFname = utils.normPath(filename)
            # print("loadPRoj 2 " + str(normFname))
            # super().loadProject(normFname)
            
    def getProject(self, projectName):
        print("projectName = " + str(projectName))
        print("projects = " + str(self.projects))
        for project in self.projects.values():
            print("project.project.name = " + str(project.project.name))
            if project.project.name == projectName:
                print("lets go")
                return project

        return None

    # def checkJavaInstalled(self):
        # javaExec = self.provider.getJavaCommand()
        # try:
            # ret = subprocess.run([javaExec, '-version'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            # self.java = ret.returncode == 0
        # except:
            # self.java = False

        # if not self.java:
            # QgsMessageLog.logMessage("Java not found for Graphab plugin.\n" + javaExec + "\n", 'Extensions', Qgis.Warning)

class MitiConnect:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'MitiConnect_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.pluginName = self.tr(u'&MitiConnect')
        self.menu = self.pluginName

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None
        
        # global sys.modules
        # if backup_modules is None:
            # sys.modules = backup_modules
        
        self.graphabPlugin = GraphabPluginOverride(self.iface)
        self.provider = MitiConnectProvider(self)
        self.graphabProvider = self.provider
        self.graphabPlugin.graphabProvider = self.provider 
        # self.provider.unload()
        # self.provider.loadAlgorithms()

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('MitiConnect', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/MitiConnect/icons/icon.png'
        self.add_action(
            icon_path,
            text=self.pluginName,
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True
        # Add provider
        QgsApplication.processingRegistry().addProvider(self.provider)
        # Connect components
        #self.dlg.connectComponents()


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        # self.provider.unload()
        # print("unload")
        # print("unload 1 modules " + str(sys.modules))
        for action in self.actions:
            self.iface.removePluginMenu(
                self.pluginName,
                action)
            self.iface.removeToolBarIcon(action)
        if self.provider:
            self.provider.unload()
            QgsApplication.processingRegistry().removeProvider(self.provider)
        # print("unload 2 modules " + str(sys.modules))
        # global backup_modules
        # backup_modules = sys.modules


    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        # if self.first_start == True:
            # self.first_start = False
        self.provider.checkJavaInstalled()
        from .miti_connect_dialog import MitiConnectDialog
        self.dlg = MitiConnectDialog(self.graphabPlugin)
        # print("reload modules = " + str(sys.modules))
        
        self.dlg.initTabs()
        self.dlg.connectComponents()
        # show the dialog
        self.dlg.show()
        # Debug java paths
        
        print("java homes = " + str(self.provider.getJavaHomesWin()))
        self.dlg.feedback.pushInfo("java homes = " + str(self.provider.getJavaHomesWin()))
        self.dlg.feedback.pushInfo("PATH = " + str(self.provider.getenv_system("PATH").split(os.pathsep)))
        self.dlg.feedback.pushInfo("java = " + str(self.provider.getJavaWin('javaw.exe')))
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
