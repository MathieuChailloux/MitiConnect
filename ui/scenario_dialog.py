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

import os, sys, copy

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.core import QgsFieldProxyModel 

from ..qgis_lib_mc import utils, abstract_model, qgsUtils, feedbacks

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
SC_DIALOG, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'scenario_dialog.ui'))
SC_LANDUSE_DIALOG, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'scenario_landuse_dialog.ui'))

class ScenarioReclassItem(abstract_model.DictItem):

    VAL = 'VAL'
    CLASS = 'CLASS'
    FIELDS = [ VAL, CLASS ]
    
    @classmethod
    def fromValues(cls, val, reclass=None,feedback=None):
        dict = { cls.VAL : val, cls.CLASS : reclass }
        return cls(dict,feedback=feedback)
        # self.feedback=feedback
    def getValue(self):
        return self.dict[self.VAL]
    def getClass(self):
        return self.dict[self.CLASS]
        
    def __deepcopy__(self):
        return ScenarioReclassItem(copy.deepcopy(self.dict),feedback=self.feedback)
        
class ScenarioReclassModel(abstract_model.DictModel):

    def __init__(self,feedback=None):
        # itemClass = getattr(sys.modules[__name__], ScenarioReclassItem.__name__)
        itemClass = ScenarioReclassItem
        super().__init__(itemClass=itemClass,fields=ScenarioReclassItem.FIELDS,feedback=feedback)

    @classmethod
    def fromValues(cls,values=[],codes=[],feedback=None):
        utils.debug("values = " +str(values))
        assert(feedback is not None)
        feedback.pushInfo("values = " +str(values))
        res = cls(feedback=feedback)
        # self.feedback=feedback
        res.loadValues(values,codes=codes)
        return res
            
    def loadValues(self,values,codes=[]):
        self.items=[]
        if codes:
            assert(len(codes) == len(values))
            for v, c in zip(values,codes):
                i = ScenarioReclassItem.fromValues(v,reclass=c,
                    feedback=self.feedback)
                self.addItem(i)
        else:
            assert(False)
            # for v in zip(values):
                # i = ScenarioReclassItem.fromValues(v,reclass=c,
                    # feedback=self.feedback)
                # self.addItem(i)
        self.layoutChanged.emit()
        
    def getValuesAndClasses(self):
        values = [i.getValue() for i in self.items]
        classes = [i.getClass() for i in self.items]
        return values, classes
        
    def getReclassTable(self):
        res = []
        for i in self.items:
            init = i.getValue()
            res += [ init, init, i.getClass() ]
        return res
        
    def __deepcopy__(self):
        model = ScenarioReclassModel(feedback=self.feedback)
        for i in self.items:
            model.addItem(i.__deepcopy__())
        return model
    # def __str__(self):
        # return "ReclassModel"
        

# class ScenarioItem(abstract_model.DictItemWithChildren):
class ScenarioItem(abstract_model.DictItemWithChild):
    
    NAME = 'NAME'
    BASE = 'BASE'
    BASE_LAYER = 'BASE_LAYER'
    LAYER = 'LAYER'
    # True = Field mode, False = Fixed mode
    MODE = 'MODE'
    RECLASS_FIELD = 'RECLASS_FIELD'
    # MODEL = 'RECLASS_VAL'
    MODEL = 'MODEL'
    BURN_VAL = 'BURN_VAL'
    # DISPLAY_FIELDS = ['NAME','BASE']
    STATUS_LANDUSE = 'LANDUSE'
    STATUS_FRICTION = 'FRICTION'
    STATUS_GRAPH = 'GRAPH'
    
    LANDUSE_MODE = 0
    
    BASE_FIELDS = [ NAME, BASE ]
    RECLASS_FIELDS = [ MODE, RECLASS_FIELD, BURN_VAL ]
    STATUS_FIELDS = [ STATUS_LANDUSE, STATUS_FRICTION, STATUS_GRAPH ]
    FIELDS = BASE_FIELDS + RECLASS_FIELDS + STATUS_FIELDS
    DISPLAY_FIELDS = BASE_FIELDS + STATUS_FIELDS
    
    def __init__(self,dict,feedback=None):
        super().__init__(dict,feedback=feedback,child=None)
        reclassModel = ScenarioReclassModel(feedback=feedback)
        self.setReclassModel(reclassModel)
        # self.reclassModel = se lf.child
        # self.setReclassModel(ScenarioReclassModel(feedback=self.feedback))
    
    @classmethod
    def fromValues(cls, name, layer=None, base=None,baseLayer=None,
            mode=0, reclassField=None, burnVal=1,
            statusLanduse=False,statusFrict=False,statusGraph=False,
            feedback=None):
        dict = { cls.NAME : name, cls.BASE : base, cls.BASE_LAYER : baseLayer,
            cls.LAYER : layer, cls.MODE : mode, cls.RECLASS_FIELD : reclassField,
            cls.BURN_VAL : burnVal, cls.STATUS_LANDUSE : statusLanduse,
            cls.STATUS_FRICTION : statusFrict, cls.STATUS_GRAPH : statusGraph }
        return cls(dict, feedback=feedback)
        
    def __deepcopy__(self):
        item = ScenarioItem(copy.deepcopy(self.dict),feedback=self.feedback)
        self.feedback.pushDebugInfo("deepcpy1 " + str(self.reclassModel))
        item.setReclassModel(self.reclassModel.__deepcopy__())
        self.feedback.pushDebugInfo("deepcpy2 " + str(item.reclassModel))
        return item
        
    def getName(self):
        return self.dict[self.NAME]
    def getBase(self):
        return self.dict[self.BASE]
    def getBaseLayer(self):
        return self.dict[self.BASE_LAYER]
    def getLayer(self):
        return self.dict[self.LAYER]
    def getMode(self):
        return self.dict[self.MODE]
    def getBurnVal(self):
        return self.dict[self.BURN_VAL]
    def getBurnField(self):
        return self.dict[self.RECLASS_FIELD]
    def getStatusLanduse(self):
        return bool(self.dict[self.STATUS_LANDUSE])
    def getStatusFriction(self):
        return bool(self.dict[self.STATUS_FRICTION])
    def getStatusGraph(self):
        return bool(self.dict[self.STATUS_GRAPH])
    def isInitialState(self):
        return self.getMode() == 3
    def isLanduseMode(self):
        return self.getMode() == 0
    def isFixedMode(self):
        return self.getMode() == 1
    def isFieldMode(self):
        return self.getMode() == 2
    def isStackedMode(self):
        return self.isFixedMode() or self.isFieldMode()
    def isLeaf(self):
        return self.getBase() == None
    def useExtent(self):
        return True
        
    def getReclassTable(self):
        return self.reclassModel.getReclassTable()
        
    def setReclassModel(self,model):
        super().setChild(model)
        self.reclassModel = model
        # self.children = [model]
        
    # def updateFromOther(self,other):
        # for k in other.dict:
            # self.dict[k] = other.dict[k]
    def updateFromDlgItem(self,dlgItem):
        self.updateFromOther(dlgItem)
        self.setReclassModel(dlgItem.reclassModel)
    # def childToDict(self,child):
        # return child.dict
            
    # @staticmethod
    # def childToDict(dlgItem):
        # is_vector = type(dlgItem) is VectorDlgItem
        # if is_vector:
            # if dlgItem.getBurnMode():
                # val = dlgItem.getBurnField()
            # else:
                # val = dlgItem.getBurnVal()
        # else:
            # val = None
        # dict = { ImportItem.INPUT : dlgItem.dict[ImportItem.INPUT],
            # ImportItem.MODE : is_vector,
            # ImportItem.VALUE : val,
            # ImportItem.STATUS : False }
                
    # Mandatory to redefine it for import links reasons
    @classmethod
    def fromXML(cls,root,feedback=None):
        utils.debug("fromXML " + str(root))
        o = cls.fromDict(root.attrib,feedback=feedback)
        for child in root:
            # childObj = ScenarioReclassModel(feedback=feedback)
            childTag = child.tag
            utils.debug("childTag str = " + str(childTag))
            # classObj = getattr(sys.modules[__name__], childTag)
            classObj = ScenarioReclassModel
            childObj = classObj.fromXML(child,feedback=feedback)
            # childTag = child.tag
            # classObj = getattr(sys.modules[__name__], childTag)
            # childObj = classObj.fromXML(child,feedback=feedback)
            utils.debug("child str = " + str(child))
            # o.child = (childObj)
            o.setReclassModel(childObj)
            utils.debug("child str = " + str(child))
            utils.debug("reclassModel = " + str(o.reclassModel))
            utils.debug("reclassModel type = " + str(o.reclassModel.__class__.__name__))
            # o.reclassModel = childObj
        return o
    
    

class ScenarioDialog(QtWidgets.QDialog, SC_DIALOG):
    def __init__(self, parent, dlgItem, model=None, feedback=None):
        """Constructor."""
        super(ScenarioDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.newFlag = dlgItem is None
        self.reclassModel = ScenarioReclassModel(feedback=feedback) if self.newFlag else dlgItem.reclassModel.__deepcopy__()
        self.reloadFlag = False
        # self.reclassModel = ScenarioReclassModel(feedback=feedback)
        self.feedback = feedback
        # self.reclassModel.feedback = feedback
        # self.feedback.pushDebugInfo("TESTES")
        # self.reclassModel.feedback.pushDebugInfo("TESTTTT")
        if model is None:
            assert(False)
        self.scModel = model.scenarioModel
        self.frictionModel = model.frictionModel
        # self.scModel = scenarioModel
        # self.scenarioList = scenarioList
        self.setupUi(self)
        self.layerComboDlg = qgsUtils.LayerComboDialog(self,
            self.scLayerCombo,self.scLayerButton)
        self.layerComboDlg.setVectorMode()
        self.connectComponents()
        self.updateUi(dlgItem)
        self.reloadFlag = True
        # self.updateUi(dlgItem)
        # self.feedback.pushDebugInfo("TESTES")
        # self.reclassModel.feedback.pushDebugInfo("TESTTTT")
        
    def connectComponents(self):
        self.scLayerCombo.layerChanged.connect(self.changeLayer)
        self.scFieldMode.clicked.connect(self.switchFieldMode)
        self.scFixedMode.clicked.connect(self.switchFixedMode)
        self.scField.setFilters(QgsFieldProxyModel.Numeric)
        self.scField.fieldChanged.connect(self.changeField)
        self.scBase.setModel(self.scModel)
        self.scDialogView.setModel(self.reclassModel)
        self.scModel.layoutChanged.emit()
        
    def switchBurnMode(self,fieldMode):
        self.scFixedMode.setChecked(not fieldMode)
        self.scFieldMode.setChecked(fieldMode)
        self.scPerValue.setEnabled(fieldMode)
        self.scField.setEnabled(fieldMode)
        self.scDialogView.setEnabled(fieldMode)
        self.scBurnVal.setEnabled(not fieldMode)
    def switchFieldMode(self):
        self.switchBurnMode(True)
    def switchFixedMode(self):
        self.switchBurnMode(False)
        
    def changeLayer(self,layer):
        self.scField.setLayer(layer)
        # self.layer = layer
    def changeField(self,fieldname):
        values = qgsUtils.getLayerFieldUniqueValues(self.scLayerCombo.currentLayer(),fieldname)
        self.feedback.pushDebugInfo("field values = " + str(values))
        self.feedback.pushDebugInfo("reload flag = " + str(self.reloadFlag))
        if self.reloadFlag:
            nbVals = len(values)
            freeCodes = self.frictionModel.getFreeVals(nbVals)
            self.reclassModel.loadValues(values,freeCodes)
            self.reclassModel.layoutChanged.emit()
        
    def errorDialog(self,msg):
        feedbacks.launchDialog(None,self.tr('Wrong parameter value'),msg)
        
    def showDialog(self):
        while self.exec_():
            name = self.scName.text()
            if not name.isalnum():
                self.feedback.user_error("Name '" + str(name) + "' is not alphanumeric")
                continue
            if self.newFlag and self.scModel.scExists(name):
                self.errorDialog(self.tr("Scenario already exists : " + name))
                continue
            if self.newFlag and self.frictionModel.importExists(name):
                self.errorDialog(self.tr("Import already exists : " + name))
                continue
            base = self.scBase.currentText()
            self.feedback.pushDebugInfo("base = " + str(base))
            if base is None:
                self.errorDialog(self.tr("Empty base scenario"))
                continue
            layer = self.scLayerCombo.currentLayer()
            if not layer:
                self.errorDialog(self.tr("Empty layer"))
                continue
            layerPath = qgsUtils.pathOfLayer(layer)
            shortMode = self.scShort.isChecked()
            scPerValueMode = self.scPerValue.isChecked()
            fixedMode = self.scFixedMode.isChecked()
            reclassField = self.scField.currentField()
            self.feedback.pushDebugInfo("fixedMode = " + str(fixedMode))
            if fixedMode:
                burnVal = self.scBurnVal.text()
                dlgItem = ScenarioItem.fromValues(name,layer=layerPath,base=base,
                    mode=1,burnVal=burnVal,feedback=self.feedback)
            else:
                if not reclassField:
                    self.errorDialog(self.tr("Empty field"))
                    continue
                dlgItem = ScenarioItem.fromValues(name,layer=layerPath,base=base,
                    mode=2,reclassField=reclassField,feedback=self.feedback)
                dlgItem.setReclassModel(self.reclassModel)
                # if not self.model.items:
                    # self.errorDialog(self.tr("Empty model"))
                    # continue
            self.feedback.pushDebugInfo("reclassModel = " + str(dlgItem.reclassModel))
            return dlgItem
        return None

    def updateUi(self,dlgItem):
        # self.scBase.addItems(self.scenarioList)
        if dlgItem:
            self.feedback.pushDebugInfo("updateUI " + str(dlgItem.dict))
            self.feedback.pushDebugInfo("updateUI child 1 " + str(dlgItem.reclassModel))
            self.scName.setText(dlgItem.dict[ScenarioItem.NAME])
            self.scBase.setCurrentText(dlgItem.dict[ScenarioItem.BASE])
            layer = dlgItem.getLayer()
            if layer:
                self.layerComboDlg.setLayerPath(dlgItem.dict[ScenarioItem.LAYER])
            fieldMode = dlgItem.dict[ScenarioItem.MODE] == 2
            self.switchBurnMode(fieldMode)
            if fieldMode:
                self.feedback.pushDebugInfo("updateUI child 2" + str(dlgItem.reclassModel))
                # copyModel = dlgItem.reclassModel.__copy__()
                # self.reclassModel = dlgItem.reclassModel.__copy__()
                self.scField.setField(dlgItem.dict[ScenarioItem.RECLASS_FIELD])
                self.reclassModel = dlgItem.reclassModel
                self.feedback.pushDebugInfo("updateUI child 3 " + str(dlgItem.reclassModel))
                # self.feedback.pushDebugInfo("updateUI child 4 " + str(self.reclassModel))
                # self.scDialogView.setModel(copyModel)
                self.scDialogView.setModel(self.reclassModel)
                self.reclassModel.layoutChanged.emit()
            else:
                burnVal = str(dlgItem.dict[ScenarioItem.BURN_VAL])
                self.feedback.pushDebugInfo("burnVal = " + str(burnVal))
                self.scBurnVal.setText(burnVal)
        else:
            burnVal = str(self.frictionModel.getFreeVals(1)[0])
            self.scBurnVal.setText(burnVal)

class ScenarioLanduseDialog(QtWidgets.QDialog, SC_LANDUSE_DIALOG):
    def __init__(self, parent, dlgItem, feedback=None, dataNames=[]):
        """Constructor."""
        super(ScenarioLanduseDialog, self).__init__(parent)
        self.feedback = feedback
        # self.luModel = luModel
        self.dataNames=dataNames
        self.setupUi(self)
        self.connectComponents()
        self.updateUi(dlgItem)
        
    def connectComponents(self):
        self.scLanduseCombo.insertItems(0,self.dataNames)
        # self.scLanduseCombo.setModel(self.luModel)
        # self.layerComboDlg = qgsUtils.LayerComboDialog(self,
            # self.scLayerCombo,self.scLayer)
                
    def updateUi(self,dlgItem):
        if dlgItem:
            self.scName.setText(dlgItem.getName())
            self.scLayer.setFilePath(dlgItem.getLayer())
            self.scLanduseCombo.setCurrentText(dlgItem.getBase())
        
    def errorDialog(self,msg):
        feedbacks.launchDialog(self,self.tr('Wrong parameter value'),msg)
        
    def showDialog(self):
        while self.exec_():
            name = self.scName.text()
            if not name.isalnum():
                feedbacks.paramError("Name '" + str(name) + "' is not alphanumeric",parent=self)
                continue
            base = self.scLanduseCombo.currentText()
            if not base:
                feedbacks.paramError(self.tr("Empty landuse"),parent=self)
                continue
            # layer = self.scLayer.filePath()
            # if not layer:
                # self.errorDialog(self.tr("Empty layer"))
                # continue
            dlgItem = ScenarioItem.fromValues(name=name,base=base,
                layer=None,feedback=self.feedback)
            return dlgItem
        return None
                
                
                
                