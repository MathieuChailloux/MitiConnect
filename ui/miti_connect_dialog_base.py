# -*- coding: utf-8 -*-

from qgis.PyQt.QtWidgets import (
    QDialog, QGridLayout, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSplitter,
    QToolButton, QPushButton, QCheckBox, QTabWidget, QTableView, QTextEdit,
    QTextBrowser, QProgressBar, QComboBox, QSpinBox, QSpacerItem, QSizePolicy,
    QGroupBox, QScrollArea, QWidget, QApplication
)
from qgis.PyQt.QtCore import Qt, QSize
from qgis.PyQt.QtGui import QIcon, QPixmap
from qgis.gui import (
    QgsFileWidget, QgsProjectionSelectionWidget, QgsDoubleSpinBox,
    QgsCheckableComboBox, QgsCollapsibleGroupBox, QgsScrollArea
)

class MitiConnectDialogBase(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("MitiConnect")
        self.setWindowIcon(QIcon(":/plugins/MitiConnect/icons/icon.png"))
        self.resize(1153, 725)

        # --- Layout principal ---
        self.gridLayout_11 = QGridLayout(self)
        self.gridLayout_11.setVerticalSpacing(0)

        # --- Barre de progression (en bas) ---
        self.lblProgress = QLabel()
        self.progressBar = QProgressBar()
        self.gridLayout_11.addWidget(self.lblProgress, 1, 0)
        self.gridLayout_11.addWidget(self.progressBar, 2, 0)

        # --- Frame principal (contenant tout sauf la barre de progression) ---
        self.frame = QFrame()
        self.frame.setMinimumHeight(100)
        self.frame.setFrameShape(QFrame.NoFrame)
        self.frame.setFrameShadow(QFrame.Raised)
        self.gridLayout_3 = QGridLayout(self.frame)
        self.gridLayout_3.setContentsMargins(3, 0, 0, 0)

        # --- Splitter principal (gauche: onglets / droite: aide) ---
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.gridLayout_3.addWidget(self.splitter, 0, 0)

        # --- ScrollArea pour les onglets ---
        self.scrollArea = QgsScrollArea()
        self.scrollArea.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents_2 = QWidget()
        self.scrollAreaWidgetContents_2.setGeometry(0, 0, 917, 637)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents_2)
        self.splitter.addWidget(self.scrollArea)

        # --- Layout des onglets ---
        self.gridLayout_6 = QGridLayout(self.scrollAreaWidgetContents_2)

        # --- Barre d'outils (haut) ---
        self._create_toolbar()

        # --- Onglets principaux ---
        self.mTabWidget = QTabWidget()
        self.mTabWidget.setMinimumSize(850, 520)
        self.mTabWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.gridLayout_6.addWidget(self.mTabWidget, 1, 0, 1, 9)

        # --- Création des onglets ---
        self._create_params_tab()
        self._create_data_tab()
        self._create_species_tab()
        self._create_friction_tab()
        self._create_scenario_tab()
        self._create_launch_tab()
        self._create_log_tab()

        # --- TextBrowser (aide) ---
        self.textShortHelp = QTextBrowser()
        self.textShortHelp.setMinimumWidth(200)
        self.textShortHelp.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.textShortHelp.setHtml("""
        <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
        <html><head><meta name="qrichtext" content="1" /></head>
        <body style="font-family:'Ubuntu'; font-size:10pt;">
            <p style="margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px;">
                <span style="font-family:'MS Shell Dlg 2'; font-size:14pt; font-weight:600;">Nom étape</span>
            </p>
            <p style="margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px;">
                <span style="font-family:'MS Shell Dlg 2'; font-weight:600;">Description générale</span>
            </p>
            <p style="margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px;">
                <span style="font-family:'MS Shell Dlg 2'; font-size:8pt;">Ceci est une description générale</span>
            </p>
        </body></html>
        """)
        self.splitter.addWidget(self.textShortHelp)

        # --- Frame des logos (en bas à droite) ---
        self._create_logos_frame()
        self.gridLayout_11.addWidget(self.frame_10, 1, 1, 2, 1)

        # --- Initialisation des valeurs par défaut ---
        self.projectName.setText("No project loaded")

    # --- Méthodes de création des sections ---
    def _create_toolbar(self):
        """Crée la barre d'outils en haut."""
        # Open Project
        self.openProject = QToolButton()
        self.openProject.setToolTip("Open project")
        self.openProject.setIcon(QIcon(":/plugins/MitiConnect/icons/mActionFileOpen.svg"))
        self.openProject.setAutoRaise(True)
        self.gridLayout_6.addWidget(self.openProject, 0, 0)

        # Initialize Project
        self.initializeProject = QToolButton()
        self.initializeProject.setToolTip("Create new project")
        self.initializeProject.setIcon(QIcon(":/plugins/MitiConnect/icons/mActionAdd.svg"))
        self.initializeProject.setAutoRaise(True)
        self.gridLayout_6.addWidget(self.initializeProject, 0, 1)

        # Save Project
        self.saveProject = QToolButton()
        self.saveProject.setToolTip("Save project")
        self.saveProject.setIcon(QIcon(":/plugins/MitiConnect/icons/mActionFileSave.svg"))
        self.saveProject.setAutoRaise(True)
        self.gridLayout_6.addWidget(self.saveProject, 0, 2)

        # Save Project As
        self.saveProjectAs = QToolButton()
        self.saveProjectAs.setToolTip("Save project as")
        self.saveProjectAs.setIcon(QIcon(":/plugins/MitiConnect/icons/mActionFileSaveAs.svg"))
        self.saveProjectAs.setAutoRaise(True)
        self.gridLayout_6.addWidget(self.saveProjectAs, 0, 3)

        # About
        self.aboutButton = QToolButton()
        self.aboutButton.setEnabled(False)
        self.aboutButton.setToolTip("About")
        self.aboutButton.setIcon(QIcon(":/plugins/MitiConnect/icons/iconHelpConsole.svg"))
        self.aboutButton.setAutoRaise(True)
        self.gridLayout_6.addWidget(self.aboutButton, 0, 4)

        # Project Name
        self.projectName = QLabel("No project loaded")
        self.gridLayout_6.addWidget(self.projectName, 0, 5)

        # Espaceur
        self.horizontalSpacer_7 = QSpacerItem(790, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.gridLayout_6.addItem(self.horizontalSpacer_7, 0, 6)

        # Langues
        self.langEn = QToolButton()
        self.langEn.setToolTip("English")
        self.langEn.setIcon(QIcon(":/plugins/MitiConnect/icons/enFlag.svg"))
        self.langEn.setCheckable(True)
        self.langEn.setAutoRaise(True)
        self.gridLayout_6.addWidget(self.langEn, 0, 7)

        self.langFr = QToolButton()
        self.langFr.setIcon(QIcon(":/plugins/MitiConnect/icons/frFlag.svg"))
        self.langFr.setCheckable(True)
        self.langFr.setAutoRaise(True)
        self.gridLayout_6.addWidget(self.langFr, 0, 8)

    def _create_params_tab(self):
        """Onglet 1 : Parameters."""
        self.paramsTab = QWidget()
        self.gridLayout = QGridLayout(self.paramsTab)

        # Message de bienvenue
        self.frame_14 = QFrame()
        self.frame_14.setMinimumHeight(161)
        self.frame_14.setMaximumHeight(161)
        self.frame_14.setFrameShape(QFrame.NoFrame)
        self.frame_14.setFrameShadow(QFrame.Raised)
        self.gridLayout_5 = QGridLayout(self.frame_14)
        self.label_11 = QLabel()
        self.label_11.setWordWrap(True)
        self.label_11.setText("""
        <html><head/><body>
            <p>Welcome in MitiConnect !</p>
            <p>Homepage: <a href="https://github.com/MathieuChailloux/MitiConnect/blob/main/README.md">
                <span style="text-decoration: underline; color:#0000ff;">https://github.com/MathieuChailloux/MitiConnect/blob/main/README.md</span>
            </a><br/>
            Video tutorials: <a href="https://www.youtube.com/watch?v=uhbXupWRqGk">
                <span style="text-decoration: underline; color:#0000ff;">https://www.youtube.com/watch?v=uhbXupWRqGk</span>
            </a>
            </p>
            <p><span style="font-weight:600;">Configuration should be frequently saved (buttons </span>
                <img src=":/plugins/BioDispersal/icons/mActionFileSaveAs.svg"/>
                <span style="font-weight:600;">, </span>
                <img src=":/plugins/BioDispersal/icons/mActionFileSave.svg"/>
                <span style="font-weight:600;"> in top left corner).</span>
            </p>
        </body></html>
        """)
        self.gridLayout_5.addWidget(self.label_11, 0, 0)
        self.gridLayout.addWidget(self.frame_14, 0, 0, 1, 2)

        # Paramètres
        self.paramlabel = QLabel("Parameters")
        self.paramlabel.setFont(QApplication.font())
        self.paramlabel.setStyleSheet("font-weight: bold;")
        self.gridLayout.addWidget(self.paramlabel, 1, 0)

        # Workspace
        self.label_44 = QLabel("Workspace")
        self.workspace = QgsFileWidget()
        self.gridLayout.addWidget(self.label_44, 2, 0)
        self.gridLayout.addWidget(self.workspace, 2, 1)

        # Extent Layer
        self.label_45 = QLabel("Extent layer")
        self.extentLayer = QgsFileWidget()
        self.gridLayout.addWidget(self.label_45, 3, 0)
        self.gridLayout.addWidget(self.extentLayer, 3, 1)

        # Resolution
        self.label_46 = QLabel("Resolution")
        self.rasterResolution = QgsDoubleSpinBox()
        self.rasterResolution.setMaximum(999999.0)
        self.gridLayout.addWidget(self.label_46, 4, 0)
        self.gridLayout.addWidget(self.rasterResolution, 4, 1)

        # Projection
        self.label_47 = QLabel("Projection")
        self.paramsCrs = QgsProjectionSelectionWidget()
        self.gridLayout.addWidget(self.label_47, 5, 0)
        self.gridLayout.addWidget(self.paramsCrs, 5, 1)

        # TableView
        self.paramsView = QTableView()
        self.paramsView.setMinimumWidth(800)
        self.gridLayout.addWidget(self.paramsView, 6, 0, 1, 2)

        self.mTabWidget.addTab(self.paramsTab, "1 - Parameters")

    def _create_data_tab(self):
        """Onglet 2 : Data."""
        self.dataTab = QWidget()
        self.gridLayout_14 = QGridLayout(self.dataTab)

        # Splitter principal
        self.splitter_4 = QSplitter(Qt.Horizontal)
        self.gridLayout_14.addWidget(self.splitter_4, 0, 0)

        # Frame gauche (Import layers + Merge layers)
        self.frame_5 = QFrame()
        self.frame_5.setMinimumWidth(565)
        self.frame_5.setFrameShape(QFrame.NoFrame)
        self.frame_5.setFrameShadow(QFrame.Raised)
        self.gridLayout_2 = QGridLayout(self.frame_5)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)

        # Splitter vertical (Import / Merge)
        self.splitter_3 = QSplitter(Qt.Vertical)
        self.gridLayout_2.addWidget(self.splitter_3, 0, 0)

        # --- Import Layers ---
        self.selectionViewFrame = QFrame()
        self.selectionViewFrame.setFrameShape(QFrame.NoFrame)
        self.selectionViewFrame.setFrameShadow(QFrame.Raised)
        self.gridLayout_13 = QGridLayout(self.selectionViewFrame)
        self.gridLayout_13.setVerticalSpacing(0)

        # Barre d'outils Import
        self.frame_9 = QFrame()
        self.frame_9.setMaximumHeight(25)
        self.frame_9.setFrameShape(QFrame.NoFrame)
        self.frame_9.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_13 = QHBoxLayout(self.frame_9)
        self.selectionLabel = QLabel("Import layers")
        self.selectionLabel.setFont(QApplication.font())
        self.selectionLabel.setStyleSheet("font-weight: bold;")
        self.horizontalLayout_13.addWidget(self.selectionLabel)
        self.horizontalSpacer_3 = QSpacerItem(263, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_13.addItem(self.horizontalSpacer_3)
        self.importVector = QToolButton()
        self.importVector.setMinimumSize(25, 25)
        self.importVector.setToolTip("Import vector data")
        self.importVector.setIcon(QIcon(":/plugins/MitiConnect/icons/mActionNewVectorLayer.svg"))
        self.importVector.setAutoRaise(True)
        self.horizontalLayout_13.addWidget(self.importVector)
        self.importRaster = QToolButton()
        self.importRaster.setMinimumSize(25, 25)
        self.importRaster.setToolTip("Import raster data")
        self.importRaster.setIcon(QIcon(":/plugins/MitiConnect/icons/mActionAddRasterLayer.svg"))
        self.importRaster.setAutoRaise(True)
        self.horizontalLayout_13.addWidget(self.importRaster)
        self.importDelete = QToolButton()
        self.importDelete.setToolTip("Delete selected lines")
        self.importDelete.setIcon(QIcon(":/plugins/MitiConnect/icons/mActionDeleteSelected.svg"))
        self.importDelete.setAutoRaise(True)
        self.horizontalLayout_13.addWidget(self.importDelete)
        self.gridLayout_13.addWidget(self.frame_9, 0, 0)

        # TableView Import
        self.importView = QTableView()
        self.importView.setAlternatingRowColors(True)
        self.importView.setSelectionBehavior(QTableView.SelectRows)
        self.importView.setSortingEnabled(True)
        self.gridLayout_13.addWidget(self.importView, 1, 0)

        # Boutons Import
        self.frame_7 = QFrame()
        self.frame_7.setMinimumHeight(24)
        self.frame_7.setMaximumHeight(25)
        self.frame_7.setFrameShape(QFrame.NoFrame)
        self.frame_7.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_5 = QHBoxLayout(self.frame_7)
        self.importSelection = QCheckBox("Apply only to selected lines")
        self.horizontalLayout_5.addWidget(self.importSelection)
        self.importRun = QPushButton("Import data")
        self.importRun.setMinimumSize(100, 23)
        self.importRun.setMaximumSize(16777215, 23)
        self.importRun.setIcon(QIcon(":/plugins/MitiConnect/icons/play.svg"))
        self.horizontalLayout_5.addWidget(self.importRun)
        self.gridLayout_13.addWidget(self.frame_7, 2, 0)

        self.splitter_3.addWidget(self.selectionViewFrame)

        # --- Merge Layers ---
        self.frame_29 = QFrame()
        self.frame_29.setFrameShape(QFrame.NoFrame)
        self.frame_29.setFrameShadow(QFrame.Raised)
        self.gridLayout_12 = QGridLayout(self.frame_29)

        # Barre d'outils Merge
        self.frame_16 = QFrame()
        self.frame_16.setMinimumHeight(24)
        self.frame_16.setMaximumHeight(25)
        self.frame_16.setFrameShape(QFrame.NoFrame)
        self.frame_16.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_7 = QHBoxLayout(self.frame_16)
        self.landuseSelection = QCheckBox("Apply only to selected lines")
        self.landuseSelection.setMinimumWidth(150)
        self.horizontalLayout_7.addWidget(self.landuseSelection)
        self.mergeRun = QPushButton("Create")
        self.mergeRun.setMinimumSize(100, 24)
        self.mergeRun.setMaximumSize(16777215, 24)
        self.mergeRun.setIcon(QIcon(":/plugins/MitiConnect/icons/play.svg"))
        self.horizontalLayout_7.addWidget(self.mergeRun)
        self.gridLayout_12.addWidget(self.frame_16, 2, 0, 1, 4)

        # Boutons Merge
        self.label_113 = QLabel("Create landuse layers")
        self.label_113.setFont(QApplication.font())
        self.label_113.setStyleSheet("font-weight: bold;")
        self.gridLayout_12.addWidget(self.label_113, 0, 0)
        self.mergeNew = QToolButton()
        self.mergeNew.setMinimumSize(25, 25)
        self.mergeNew.setToolTip("Add land use layer")
        self.mergeNew.setIcon(QIcon(":/plugins/MitiConnect/icons/symbologyAdd.svg"))
        self.mergeNew.setAutoRaise(True)
        self.gridLayout_12.addWidget(self.mergeNew, 0, 2)
        self.mergeRemove = QToolButton()
        self.mergeRemove.setMinimumSize(25, 25)
        self.mergeRemove.setToolTip("Delete selected groups")
        self.mergeRemove.setIcon(QIcon(":/plugins/MitiConnect/icons/symbologyRemove.svg"))
        self.mergeRemove.setAutoRaise(True)
        self.gridLayout_12.addWidget(self.mergeRemove, 0, 3)
        self.horizontalSpacer_5 = QSpacerItem(321, 15, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.gridLayout_12.addItem(self.horizontalSpacer_5, 0, 1)

        # TableView Merge
        self.mergeView = QTableView()
        self.mergeView.setSortingEnabled(True)
        self.gridLayout_12.addWidget(self.mergeView, 1, 0, 1, 4)

        self.splitter_3.addWidget(self.frame_29)

        # --- Classes ---
        self.groupFrame = QFrame()
        self.groupFrame.setFrameShape(QFrame.NoFrame)
        self.groupFrame.setFrameShadow(QFrame.Raised)
        self.gridLayout_9 = QGridLayout(self.groupFrame)
        self.frame_3 = QFrame()
        self.frame_3.setMinimumHeight(20)
        self.frame_3.setMaximumHeight(20)
        self.frame_3.setFrameShape(QFrame.NoFrame)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_4 = QHBoxLayout(self.frame_3)
        self.label_111 = QLabel("Classes")
        self.label_111.setFont(QApplication.font())
        self.label_111.setStyleSheet("font-weight: bold;")
        self.horizontalLayout_4.addWidget(self.label_111)
        self.horizontalSpacer = QSpacerItem(416, 15, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(self.horizontalSpacer)
        self.gridLayout_9.addWidget(self.frame_3, 0, 0)
        self.classView = QTableView()
        self.classView.setMinimumSize(100, 100)
        self.classView.setSortingEnabled(True)
        self.gridLayout_9.addWidget(self.classView, 1, 0)

        self.splitter_4.addWidget(self.groupFrame)
        self.mTabWidget.addTab(self.dataTab, "2 - Data")

    def _create_species_tab(self):
        """Onglet 3 : Species."""
        self.speciesTab = QWidget()
        self.gridLayout_10 = QGridLayout(self.speciesTab)
        self.splitter_2 = QSplitter(Qt.Vertical)
        self.gridLayout_10.addWidget(self.splitter_2, 0, 0)

        self.frame_28 = QFrame()
        self.frame_28.setMinimumHeight(150)
        self.frame_28.setMaximumHeight(565)
        self.frame_28.setFrameShape(QFrame.NoFrame)
        self.frame_28.setFrameShadow(QFrame.Raised)
        self.gridLayout_8 = QGridLayout(self.frame_28)
        self.gridLayout_8.setContentsMargins(0, 0, 0, 0)

        self.frame_13 = QFrame()
        self.frame_13.setMinimumHeight(25)
        self.frame_13.setFrameShape(QFrame.NoFrame)
        self.frame_13.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_9 = QHBoxLayout(self.frame_13)
        self.label_102 = QLabel("Species")
        self.label_102.setFont(QApplication.font())
        self.label_102.setStyleSheet("font-weight: bold;")
        self.horizontalLayout_9.addWidget(self.label_102)
        self.horizontalSpacer_22 = QSpacerItem(100, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_9.addItem(self.horizontalSpacer_22)
        self.speciesAdd = QToolButton()
        self.speciesAdd.setMinimumSize(25, 25)
        self.speciesAdd.setToolTip("Add new species")
        self.speciesAdd.setIcon(QIcon(":/plugins/MitiConnect/icons/symbologyAdd.svg"))
        self.speciesAdd.setAutoRaise(True)
        self.horizontalLayout_9.addWidget(self.speciesAdd)
        self.speciesRemove = QToolButton()
        self.speciesRemove.setMinimumSize(25, 25)
        self.speciesRemove.setToolTip("Delete selected species")
        self.speciesRemove.setIcon(QIcon(":/plugins/MitiConnect/icons/mActionDeleteSelected.svg"))
        self.speciesRemove.setAutoRaise(True)
        self.horizontalLayout_9.addWidget(self.speciesRemove)
        self.gridLayout_8.addWidget(self.frame_13, 0, 0)
        self.speciesView = QTableView()
        self.speciesView.setMinimumSize(350, 100)
        self.speciesView.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.speciesView.setEditTriggers(QTableView.DoubleClicked | QTableView.SelectedClicked)
        self.speciesView.setSelectionBehavior(QTableView.SelectRows)
        self.speciesView.setSortingEnabled(True)
        self.gridLayout_8.addWidget(self.speciesView, 1, 0)
        self.splitter_2.addWidget(self.frame_28)
        self.mTabWidget.addTab(self.speciesTab, "3 - Species")

    def _create_friction_tab(self):
        """Onglet 4 : Friction."""
        self.frictionTab = QWidget()
        self.verticalLayout_12 = QVBoxLayout(self.frictionTab)
        self.label_26 = QLabel("Friction")
        self.label_26.setMinimumHeight(16)
        self.label_26.setFont(QApplication.font())
        self.label_26.setStyleSheet("font-weight: bold;")
        self.verticalLayout_12.addWidget(self.label_26)

        self.frictionFrame = QFrame()
        self.frictionFrame.setFrameShape(QFrame.NoFrame)
        self.frictionFrame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_11 = QVBoxLayout(self.frictionFrame)

        self.frictionButtonsFrame = QFrame()
        self.frictionButtonsFrame.setMinimumHeight(25)
        self.frictionButtonsFrame.setFrameShape(QFrame.NoFrame)
        self.frictionButtonsFrame.setFrameShadow(QFrame.Raised)
        self.frictionLoadClass = QToolButton()
        self.frictionLoadClass.setMinimumSize(25, 25)
        self.frictionLoadClass.setToolTip("Reload classes")
        self.frictionLoadClass.setIcon(QIcon(":/plugins/MitiConnect/icons/mActionRefresh.svg"))
        self.frictionLoadClass.setAutoRaise(True)
        self.frictionLoad = QToolButton()
        self.frictionLoad.setMinimumSize(25, 25)
        self.frictionLoad.setToolTip("Import friction from CSV file")
        self.frictionLoad.setIcon(QIcon(":/plugins/MitiConnect/icons/mActionFileOpen.svg"))
        self.frictionLoad.setAutoRaise(True)
        self.frictionSave = QToolButton()
        self.frictionSave.setMinimumSize(25, 25)
        self.frictionSave.setToolTip("Save friction as CSV file")
        self.frictionSave.setIcon(QIcon(":/plugins/MitiConnect/icons/mActionFileSaveAs.svg"))
        self.frictionSave.setAutoRaise(True)
        self.verticalLayout_11.addWidget(self.frictionButtonsFrame)
        self.frictionView = QTableView()
        self.frictionView.setMinimumSize(350, 200)
        self.frictionView.setAlternatingRowColors(True)
        self.frictionView.setSortingEnabled(True)
        self.verticalLayout_11.addWidget(self.frictionView)
        self.verticalLayout_12.addWidget(self.frictionFrame)
        self.mTabWidget.addTab(self.frictionTab, "4 - Friction")

    def _create_scenario_tab(self):
        """Onglet 5 : Scenarios."""
        self.scenarioTab = QWidget()
        self.gridLayout_16 = QGridLayout(self.scenarioTab)
        self.frame_11 = QFrame()
        self.frame_11.setFrameShape(QFrame.NoFrame)
        self.frame_11.setFrameShadow(QFrame.Raised)
        self.verticalLayout = QVBoxLayout(self.frame_11)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.label_31 = QLabel("Scenarios")
        self.label_31.setFont(QApplication.font())
        self.label_31.setStyleSheet("font-weight: bold;")
        self.verticalLayout.addWidget(self.label_31)
        self.frame_6 = QFrame()
        self.frame_6.setMinimumHeight(23)
        self.frame_6.setMaximumHeight(23)
        self.frame_6.setFrameShape(QFrame.NoFrame)
        self.frame_6.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame_6)
        self.horizontalSpacer_6 = QSpacerItem(55, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(self.horizontalSpacer_6)
        self.scenarioAdd = QToolButton()
        self.scenarioAdd.setMinimumSize(25, 25)
        self.scenarioAdd.setToolTip("Add scenario")
        self.scenarioAdd.setIcon(QIcon(":/plugins/MitiConnect/icons/mActionAdd.svg"))
        self.scenarioAdd.setAutoRaise(True)
        self.horizontalLayout.addWidget(self.scenarioAdd)
        self.scenarioRemove = QToolButton()
        self.scenarioRemove.setMinimumSize(25, 25)
        self.scenarioRemove.setToolTip("Delete selected scenario")
        self.scenarioRemove.setIcon(QIcon(":/plugins/MitiConnect/icons/mActionDeleteSelected.svg"))
        self.scenarioRemove.setAutoRaise(True)
        self.horizontalLayout.addWidget(self.scenarioRemove)
        self.scenarioUp = QToolButton()
        self.scenarioUp.setMinimumSize(25, 25)
        self.scenarioUp.setToolTip("Upgrade scenario")
        self.scenarioUp.setIcon(QIcon(":/plugins/MitiConnect/icons/up-arrow.png"))
        self.scenarioUp.setAutoRaise(True)
        self.horizontalLayout.addWidget(self.scenarioUp)
        self.scenarioDown = QToolButton()
        self.scenarioDown.setMinimumSize(25, 25)
        self.scenarioDown.setToolTip("Downgrade scenario")
        self.scenarioDown.setIcon(QIcon(":/plugins/MitiConnect/icons/down-arrow.png"))
        self.scenarioDown.setAutoRaise(True)
        self.horizontalLayout.addWidget(self.scenarioDown)
        self.verticalLayout.addWidget(self.frame_6)
        self.scenarioView = QTableView()
        self.scenarioView.setMinimumSize(300, 200)
        self.scenarioView.setEditTriggers(QTableView.NoEditTriggers)
        self.scenarioView.setDragEnabled(True)
        self.scenarioView.setAlternatingRowColors(True)
        self.scenarioView.setSelectionBehavior(QTableView.SelectRows)
        self.scenarioView.setSortingEnabled(True)
        self.verticalLayout.addWidget(self.scenarioView)
        self.gridLayout_16.addWidget(self.frame_11, 1, 0)
        self.mTabWidget.addTab(self.scenarioTab, "5 - Scenarios")

    def _create_launch_tab(self):
        """Onglet 6 : Launches."""
        self.launchTab = QWidget()
        self.gridLayout_4 = QGridLayout(self.launchTab)
        self.frame_12 = QFrame()
        self.frame_12.setFrameShape(QFrame.NoFrame)
        self.frame_12.setFrameShadow(QFrame.Raised)
        self.gridLayout_19 = QGridLayout(self.frame_12)
        self.gridLayout_19.setContentsMargins(0, 0, 0, 0)
        self.splitter_5 = QSplitter(Qt.Vertical)
        self.gridLayout_19.addWidget(self.splitter_5, 0, 0)

        # --- Table des lancements ---
        self.frame_2 = QFrame()
        self.frame_2.setMinimumHeight(150)
        self.frame_2.setFrameShape(QFrame.NoFrame)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.gridLayout_18 = QGridLayout(self.frame_2)
        self.gridLayout_18.setContentsMargins(0, 0, 0, 0)
        self.label_32 = QLabel("Launches")
        self.label_32.setFont(QApplication.font())
        self.label_32.setStyleSheet("font-weight: bold;")
        self.gridLayout_18.addWidget(self.label_32, 0, 0)
        self.frame_8 = QFrame()
        self.frame_8.setMinimumHeight(23)
        self.frame_8.setMaximumHeight(23)
        self.frame_8.setFrameShape(QFrame.NoFrame)
        self.frame_8.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_6 = QHBoxLayout(self.frame_8)
        self.horizontalSpacer_8 = QSpacerItem(55, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(self.horizontalSpacer_8)
        self.reloadButton = QToolButton()
        self.reloadButton.setMinimumSize(25, 25)
        self.reloadButton.setToolTip("Reload scenarios")
        self.reloadButton.setIcon(QIcon(":/plugins/MitiConnect/icons/mActionRefresh.svg"))
        self.reloadButton.setAutoRaise(True)
        self.horizontalLayout_6.addWidget(self.reloadButton)
        self.launchesUp = QToolButton()
        self.launchesUp.setMinimumSize(25, 25)
        self.launchesUp.setToolTip("Upgrade scenario")
        self.launchesUp.setIcon(QIcon(":/plugins/MitiConnect/icons/up-arrow.png"))
        self.launchesUp.setAutoRaise(True)
        self.horizontalLayout_6.addWidget(self.launchesUp)
        self.launchesDown = QToolButton()
        self.launchesDown.setMinimumSize(25, 25)
        self.launchesDown.setToolTip("Downgrade scenario")
        self.launchesDown.setIcon(QIcon(":/plugins/MitiConnect/icons/down-arrow.png"))
        self.launchesDown.setAutoRaise(True)
        self.horizontalLayout_6.addWidget(self.launchesDown)
        self.gridLayout_18.addWidget(self.frame_8, 1, 0)
        self.launchesView = QTableView()
        self.launchesView.setMinimumSize(300, 100)
        self.launchesView.setEditTriggers(QTableView.NoEditTriggers)
        self.launchesView.setDragEnabled(True)
        self.launchesView.setAlternatingRowColors(True)
        self.launchesView.setSelectionBehavior(QTableView.SelectRows)
        self.launchesView.setSortingEnabled(True)
        self.gridLayout_18.addWidget(self.launchesView, 2, 0)
        self.splitter_5.addWidget(self.frame_2)

        # --- Paramètres et boutons de lancement ---
        self.frame_15 = QFrame()
        self.frame_15.setMinimumHeight(227)
        self.frame_15.setFrameShape(QFrame.NoFrame)
        self.frame_15.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_11 = QHBoxLayout(self.frame_15)
        self.horizontalLayout_11.setContentsMargins(0, 0, 0, 0)

        # --- Frame des labels ---
        self.frame_17 = QFrame()
        self.frame_17.setFrameShape(QFrame.NoFrame)
        self.frame_17.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame_17)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.bufferInGroupLabel_18 = QLabel("Select scenarios")
        self.bufferInGroupLabel_18.setFont(QApplication.font())
        self.verticalLayout_2.addWidget(self.bufferInGroupLabel_18)
        self.bufferInGroupLabel_19 = QLabel("Select species")
        self.bufferInGroupLabel_19.setFont(QApplication.font())
        self.verticalLayout_2.addWidget(self.bufferInGroupLabel_19)
        self.bufferInGroupLabel_20 = QLabel("Base layers")
        self.bufferInGroupLabel_20.setFont(QApplication.font())
        self.verticalLayout_2.addWidget(self.bufferInGroupLabel_20)
        self.bufferInGroupLabel_21 = QLabel("Graphab")
        self.bufferInGroupLabel_21.setFont(QApplication.font())
        self.verticalLayout_2.addWidget(self.bufferInGroupLabel_21)
        self.bufferInGroupLabel_22 = QLabel("Analysis")
        self.bufferInGroupLabel_22.setFont(QApplication.font())
        self.verticalLayout_2.addWidget(self.bufferInGroupLabel_22)
        self.horizontalLayout_11.addWidget(self.frame_17)

        # --- Frame des sélecteurs et boutons ---
        self.frame_19 = QFrame()
        self.frame_19.setMinimumWidth(450)
        self.frame_19.setFrameShape(QFrame.NoFrame)
        self.frame_19.setFrameShadow(QFrame.Raised)
        self.gridLayout_17 = QGridLayout(self.frame_19)
        self.gridLayout_17.setContentsMargins(0, 0, 0, 0)
        self.scenariosSelection = QgsCheckableComboBox()
        self.scenariosSelection.setMinimumHeight(23)
        self.gridLayout_17.addWidget(self.scenariosSelection, 0, 0, 1, 3)
        self.speciesSelection = QgsCheckableComboBox()
        self.speciesSelection.setMinimumHeight(23)
        self.gridLayout_17.addWidget(self.speciesSelection, 1, 0, 1, 3)

        # Boutons de lancement
        self.landuseRun = QPushButton("1 - Land Use")
        self.landuseRun.setMinimumSize(145, 23)
        self.landuseRun.setIcon(QIcon(":/plugins/MitiConnect/icons/play.svg"))
        self.gridLayout_17.addWidget(self.landuseRun, 2, 0)
        self.frictionRun = QPushButton("2 - Friction")
        self.frictionRun.setMinimumHeight(23)
        self.frictionRun.setIcon(QIcon(":/plugins/MitiConnect/icons/play.svg"))
        self.gridLayout_17.addWidget(self.frictionRun, 2, 1)
        self.projectRun = QPushButton("3 - Project")
        self.projectRun.setMinimumHeight(23)
        self.projectRun.setIcon(QIcon(":/plugins/MitiConnect/icons/play.svg"))
        self.gridLayout_17.addWidget(self.projectRun, 3, 0)
        self.linksetRun = QPushButton("4 - Linkset")
        self.linksetRun.setMinimumSize(120, 23)
        self.linksetRun.setIcon(QIcon(":/plugins/MitiConnect/icons/play.svg"))
        self.gridLayout_17.addWidget(self.linksetRun, 3, 1)
        self.graphRun = QPushButton("5 - Graph")
        self.graphRun.setMinimumHeight(23)
        self.graphRun.setIcon(QIcon(":/plugins/MitiConnect/icons/play.svg"))
        self.gridLayout_17.addWidget(self.graphRun, 3, 2)
        self.dispersalRun = QPushButton("Dispersal")
        self.dispersalRun.setIcon(QIcon(":/plugins/MitiConnect/icons/play.svg"))
        self.gridLayout_17.addWidget(self.dispersalRun, 4, 0)
        self.localMetricsRun = QPushButton("Local metric")
        self.localMetricsRun.setMinimumHeight(23)
        self.localMetricsRun.setIcon(QIcon(":/plugins/MitiConnect/icons/play.svg"))
        self.gridLayout_17.addWidget(self.localMetricsRun, 4, 1)
        self.compareScenariosRun = QPushButton("Compare scenarios")
        self.compareScenariosRun.setMinimumSize(160, 23)
        self.compareScenariosRun.setIcon(QIcon(":/plugins/MitiConnect/icons/play.svg"))
        self.gridLayout_17.addWidget(self.compareScenariosRun, 4, 2)
        self.horizontalLayout_11.addWidget(self.frame_19)

        # --- Frame des paramètres ---
        self.frame_21 = QFrame()
        self.frame_21.setMinimumSize(10, 227)
        self.frame_21.setFrameShape(QFrame.NoFrame)
        self.frame_21.setFrameShadow(QFrame.Raised)
        self.verticalLayout_4 = QVBoxLayout(self.frame_21)
        self.verticalLayout_4.setSpacing(6)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)

        # Launch parameters
        self.graphabParamsGroup_3 = QgsCollapsibleGroupBox("Launch parameters")
        self.graphabParamsGroup_3.setMinimumHeight(60)
        self.graphabParamsGroup_3.setFont(QApplication.font())
        self.graphabParamsGroup_3.setStyleSheet("font-size: 8pt;")
        self.gridLayout_15 = QGridLayout(self.graphabParamsGroup_3)
        self.gridLayout_15.setVerticalSpacing(0)
        self.gridLayout_15.setContentsMargins(0, 0, 0, 0)
        self.eraseResults = QCheckBox("Erase existing results")
        self.eraseResults.setMinimumHeight(17)
        self.eraseResults.setFont(QApplication.font())
        self.eraseResults.setStyleSheet("font-size: 8pt;")
        self.gridLayout_15.addWidget(self.eraseResults, 0, 0)
        self.loadResults = QCheckBox("Load base layers")
        self.loadResults.setMinimumHeight(17)
        self.loadResults.setFont(QApplication.font())
        self.loadResults.setStyleSheet("font-size: 8pt;")
        self.gridLayout_15.addWidget(self.loadResults, 1, 0)
        self.verticalLayout_4.addWidget(self.graphabParamsGroup_3)

        # Graphab parameters
        self.graphabParamsGroup_2 = QgsCollapsibleGroupBox("Graphab parameters")
        self.graphabParamsGroup_2.setMinimumHeight(90)
        self.graphabParamsGroup_2.setFont(QApplication.font())
        self.gridLayout_20 = QGridLayout(self.graphabParamsGroup_2)
        self.frame_20 = QFrame()
        self.frame_20.setMinimumHeight(17)
        self.frame_20.setFrameShape(QFrame.NoFrame)
        self.frame_20.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_10 = QHBoxLayout(self.frame_20)
        self.horizontalLayout_10.setSpacing(0)
        self.horizontalLayout_10.setContentsMargins(0, 0, 0, 0)
        self.linksetMaxFlag = QCheckBox("Links <=")
        self.horizontalLayout_10.addWidget(self.linksetMaxFlag)
        self.linksetMaxCoeff = QSpinBox()
        self.horizontalLayout_10.addWidget(self.linksetMaxCoeff)
        self.label_2 = QLabel(" * max disp")
        self.horizontalLayout_10.addWidget(self.label_2)
        self.gridLayout_20.addWidget(self.frame_20, 0, 0, 1, 2)
        self.label_54 = QLabel("Local metric")
        self.label_54.setFont(QApplication.font())
        self.label_54.setStyleSheet("font-size: 8pt;")
        self.gridLayout_20.addWidget(self.label_54, 1, 0)
        self.localMetric = QComboBox()
        self.localMetric.setMinimumHeight(18)
        self.localMetric.addItems(["BC", "CF", "F", "IF", "CC", "CCe", "CCor", "Dg", "Ec"])
        self.gridLayout_20.addWidget(self.localMetric, 1, 1)
        self.label_55 = QLabel("Global metric")
        self.label_55.setFont(QApplication.font())
        self.label_55.setStyleSheet("font-size: 8pt;")
        self.gridLayout_20.addWidget(self.label_55, 2, 0)
        self.globalMetric = QComboBox()
        self.globalMetric.setMinimumHeight(18)
        self.globalMetric.addItems(["PC", "EC", "IIC"])
        self.globalMetric.setCurrentIndex(1)
        self.gridLayout_20.addWidget(self.globalMetric, 2, 1)
        self.verticalLayout_4.addWidget(self.graphabParamsGroup_2)

        # Comparaison
        self.cmpInit = QCheckBox("Compare scenarios to initial state")
        self.cmpInit.setMinimumHeight(20)
        self.cmpInit.setFont(QApplication.font())
        self.cmpInit.setStyleSheet("font-size: 8pt;")
        self.cmpInit.setChecked(True)
        self.verticalLayout_4.addWidget(self.cmpInit)
        self.cmpPerc = QCheckBox("Display comparison as percentage")
        self.cmpPerc.setMinimumHeight(20)
        self.cmpPerc.setFont(QApplication.font())
        self.cmpPerc.setStyleSheet("font-size: 8pt;")
        self.cmpPerc.setChecked(True)
        self.verticalLayout_4.addWidget(self.cmpPerc)

        self.horizontalLayout_11.addWidget(self.frame_21)
        self.splitter_5.addWidget(self.frame_15)
        self.gridLayout_4.addWidget(self.frame_12, 0, 0)
        self.mTabWidget.addTab(self.launchTab, "6 - Launches")

    def _create_log_tab(self):
        """Onglet Log."""
        self.logTab = QWidget()
        self.verticalLayout_3 = QVBoxLayout(self.logTab)
        self.verticalLayout_3.setSpacing(2)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.txtLog = QTextEdit()
        self.txtLog.setReadOnly(True)
        self.verticalLayout_3.addWidget(self.txtLog)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)
        self.debugButton = QToolButton()
        self.debugButton.setToolTip("Debug mode")
        self.debugButton.setIcon(QIcon(":/plugins/BioDispersal/icons/debug_icon/mActionAnnotation.svg"))
        self.debugButton.setCheckable(True)
        self.debugButton.setAutoRaise(True)
        self.horizontalLayout_2.addWidget(self.debugButton)
        self.logSaveAs = QToolButton()
        self.logSaveAs.setToolTip("Save log as")
        self.logSaveAs.setIcon(QIcon(":/plugins/BioDispersal/icons/mActionFileSave.svg"))
        self.logSaveAs.setAutoRaise(True)
        self.horizontalLayout_2.addWidget(self.logSaveAs)
        self.logClear = QToolButton()
        self.logClear.setToolTip("Clear log")
        self.logClear.setIcon(QIcon(":/plugins/BioDispersal/icons/iconClearConsole.svg"))
        self.logClear.setAutoRaise(True)
        self.horizontalLayout_2.addWidget(self.logClear)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.mTabWidget.addTab(self.logTab, "Log")

    def _create_logos_frame(self):
        """Frame des logos (en bas à droite)."""
        self.frame_10 = QFrame()
        self.frame_10.setFrameShape(QFrame.NoFrame)
        self.frame_10.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frame_10)
        self.horizontalLayout_3.setSpacing(6)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.label_3 = QLabel()
        self.label_3.setMaximumSize(85, 21)
        self.label_3.setPixmap(QPixmap(":/plugins/BioDispersal/icons/logoINRAE.png"))
        self.label_3.setScaledContents(True)
        self.horizontalLayout_3.addWidget(self.label_3)
        self.label = QLabel()
        self.label.setMinimumSize(122, 61)
        self.label.setMaximumSize(122, 61)
        self.label.setPixmap(QPixmap(":/plugins/MitiConnect/icons/logoCRTVBNew.png"))
        self.label.setScaledContents(True)
        self.horizontalLayout_3.addWidget(self.label)