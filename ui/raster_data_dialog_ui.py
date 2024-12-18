# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/raster_data_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_rasterDataDialog(object):
    def setupUi(self, rasterDataDialog):
        rasterDataDialog.setObjectName("rasterDataDialog")
        rasterDataDialog.resize(271, 127)
        self.gridLayout = QtWidgets.QGridLayout(rasterDataDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.frame = QtWidgets.QFrame(rasterDataDialog)
        self.frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.fileLabel = QtWidgets.QLabel(self.frame)
        self.fileLabel.setMinimumSize(QtCore.QSize(0, 16))
        self.fileLabel.setMaximumSize(QtCore.QSize(16777215, 20))
        self.fileLabel.setScaledContents(True)
        self.fileLabel.setObjectName("fileLabel")
        self.horizontalLayout_2.addWidget(self.fileLabel)
        self.rasterDataLayerCombo = gui.QgsMapLayerComboBox(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.rasterDataLayerCombo.sizePolicy().hasHeightForWidth())
        self.rasterDataLayerCombo.setSizePolicy(sizePolicy)
        self.rasterDataLayerCombo.setMinimumSize(QtCore.QSize(0, 20))
        self.rasterDataLayerCombo.setMaximumSize(QtCore.QSize(16777215, 20))
        self.rasterDataLayerCombo.setObjectName("rasterDataLayerCombo")
        self.horizontalLayout_2.addWidget(self.rasterDataLayerCombo)
        self.rasterDataLayerOpen = QtWidgets.QToolButton(self.frame)
        self.rasterDataLayerOpen.setObjectName("rasterDataLayerOpen")
        self.horizontalLayout_2.addWidget(self.rasterDataLayerOpen)
        self.gridLayout.addWidget(self.frame, 1, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(rasterDataDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 1)
        self.frame_3 = QtWidgets.QFrame(rasterDataDialog)
        self.frame_3.setEnabled(True)
        self.frame_3.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.frame_3.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.frame_3)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.keepValues = QtWidgets.QCheckBox(self.frame_3)
        self.keepValues.setEnabled(True)
        self.keepValues.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.keepValues.setObjectName("keepValues")
        self.horizontalLayout_3.addWidget(self.keepValues)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.gridLayout.addWidget(self.frame_3, 2, 0, 1, 1)
        self.frame_2 = QtWidgets.QFrame(rasterDataDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame_2)
        self.horizontalLayout.setContentsMargins(3, 3, 3, 3)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.frame_2)
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.nameValue = QtWidgets.QLineEdit(self.frame_2)
        self.nameValue.setMinimumSize(QtCore.QSize(0, 20))
        self.nameValue.setMaximumSize(QtCore.QSize(16777215, 20))
        self.nameValue.setObjectName("nameValue")
        self.horizontalLayout.addWidget(self.nameValue)
        self.gridLayout.addWidget(self.frame_2, 0, 0, 1, 1)

        self.retranslateUi(rasterDataDialog)
        self.buttonBox.accepted.connect(rasterDataDialog.accept) # type: ignore
        self.buttonBox.rejected.connect(rasterDataDialog.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(rasterDataDialog)

    def retranslateUi(self, rasterDataDialog):
        _translate = QtCore.QCoreApplication.translate
        rasterDataDialog.setWindowTitle(_translate("rasterDataDialog", "Import raster data"))
        self.fileLabel.setText(_translate("rasterDataDialog", "Select raster layer"))
        self.rasterDataLayerOpen.setText(_translate("rasterDataDialog", "..."))
        self.keepValues.setText(_translate("rasterDataDialog", "Keep initial values"))
        self.label.setText(_translate("rasterDataDialog", "Name"))
from qgis import gui
