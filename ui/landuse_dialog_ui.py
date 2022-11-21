# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/landuse_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_landuseDialog(object):
    def setupUi(self, landuseDialog):
        landuseDialog.setObjectName("landuseDialog")
        landuseDialog.resize(380, 319)
        self.gridLayout = QtWidgets.QGridLayout(landuseDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(landuseDialog)
        self.label.setMinimumSize(QtCore.QSize(0, 0))
        self.label.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)
        self.landuseDialogName = QtWidgets.QLineEdit(landuseDialog)
        self.landuseDialogName.setMinimumSize(QtCore.QSize(0, 20))
        self.landuseDialogName.setObjectName("landuseDialogName")
        self.gridLayout.addWidget(self.landuseDialogName, 0, 2, 1, 3)
        spacerItem = QtWidgets.QSpacerItem(266, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 0, 1, 3)
        self.landuseDialogReload = QtWidgets.QToolButton(landuseDialog)
        self.landuseDialogReload.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/plugins/MitiConnect/icons/mActionRefresh.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.landuseDialogReload.setIcon(icon)
        self.landuseDialogReload.setAutoRaise(True)
        self.landuseDialogReload.setObjectName("landuseDialogReload")
        self.gridLayout.addWidget(self.landuseDialogReload, 1, 3, 1, 1)
        self.landuseDialogRemove = QtWidgets.QToolButton(landuseDialog)
        self.landuseDialogRemove.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/plugins/MitiConnect/icons/mActionDeleteSelected.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.landuseDialogRemove.setIcon(icon1)
        self.landuseDialogRemove.setAutoRaise(True)
        self.landuseDialogRemove.setObjectName("landuseDialogRemove")
        self.gridLayout.addWidget(self.landuseDialogRemove, 1, 4, 1, 1)
        self.landuseDialogUp = QtWidgets.QToolButton(landuseDialog)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("ui/../icons/up-arrow.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.landuseDialogUp.setIcon(icon2)
        self.landuseDialogUp.setAutoRaise(True)
        self.landuseDialogUp.setObjectName("landuseDialogUp")
        self.gridLayout.addWidget(self.landuseDialogUp, 2, 0, 1, 1)
        self.landuseDialogView = QtWidgets.QTableView(landuseDialog)
        self.landuseDialogView.setMinimumSize(QtCore.QSize(300, 200))
        self.landuseDialogView.setObjectName("landuseDialogView")
        self.gridLayout.addWidget(self.landuseDialogView, 2, 1, 2, 3)
        self.landuseDialogDown = QtWidgets.QToolButton(landuseDialog)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("ui/../icons/down-arrow.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.landuseDialogDown.setIcon(icon3)
        self.landuseDialogDown.setAutoRaise(True)
        self.landuseDialogDown.setObjectName("landuseDialogDown")
        self.gridLayout.addWidget(self.landuseDialogDown, 3, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(landuseDialog)
        self.buttonBox.setMaximumSize(QtCore.QSize(16777215, 25))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Save)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 4, 2, 1, 3)

        self.retranslateUi(landuseDialog)
        self.buttonBox.accepted.connect(landuseDialog.accept)
        self.buttonBox.rejected.connect(landuseDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(landuseDialog)

    def retranslateUi(self, landuseDialog):
        _translate = QtCore.QCoreApplication.translate
        landuseDialog.setWindowTitle(_translate("landuseDialog", "Create new land use layer"))
        self.label.setText(_translate("landuseDialog", "Land use name"))
        self.landuseDialogUp.setText(_translate("landuseDialog", "..."))
        self.landuseDialogDown.setText(_translate("landuseDialog", "..."))