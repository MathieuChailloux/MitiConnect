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

from qgis.PyQt import uic, QtWidgets
from qgis.PyQt.QtCore import Qt

from ..qgis_lib_mc.utils import CustomException
from ..ui.vector_data_dialog import VectorDlgItem, VectorDataDialog
from ..ui.raster_data_dialog import RasterDlgItem, RasterDataDialog
from ..ui.landuse_dialog import LanduseDialog
from ..qgis_lib_mc.abstract_model import (DictItem, DictModel,
    AbstractConnector, TableToDialogConnector,
    DictItemWithChild, DictItemWithChildren)

# RASTER_DLG_CLASS, _ = uic.loadUiType(os.path.join(
    # os.path.dirname(__file__), '../ui/raster_data_dialog.ui'))
# VECTOR_DLG_CLASS, _ = uic.loadUiType(os.path.join(
    # os.path.dirname(__file__), '../ui/vector_data_dialog.ui'))
    
# class ReclassItem(DictItem):
    
    # INPUT = 'INPUT'
    # OUTPUT = 'OUTPUT'
    # FIELDS = [ INPUT, OUTPUT ]

    # def __init__(self, in_val,out_val):
        # d = { self.INPUT : in_val, self.OUTPUT : out_val }
        # super().__init__(d,self.FIELDS)
        
        
# class ReclassModel(DictModel):
    
    # def __init__(self, parent):
        # super().__init__(parent,itemClass=ReclassItem,
            # feedback=parent.feedback)
    
    # def getCodes(self):
        # return [i.dict[ReclassItem.OUTPUT] for i in self.items]


# class RasterDlgItem(DictItem):

    # INPUT = 'INPUT'
    # RECLASS = 'RECLASS'
    # FIELDS = [ INPUT, RECLASS ]

    # def __init__(self, dict, parent=None):
        # super().__init__(dict,self.FIELDS)
    # def getReclassModel(self):
        # return self.dict[self.RECLASS]

# class RasterDataDialog(QtWidgets.QDialog, FORM_CLASS):
    # def __init__(self, raster_data_item, parent,class_model=None):
        # """Constructor."""
        # super(RasterDataDialog, self).__init__(parent)
        # self.feedback=parent.feedback
        # self.data_item = raster_data_item
        # self.class_model = class_model
        # self.reclass_model = ReclassModel(self)
        # self.setupUi(self)
        # self.layerComboDlg = qgsUtils.LayerComboDialog(self,
            # self.rasterDataLayerCombo,self.rasterDataLayerOpen)
        # self.layerComboDlg.setRasterMode()
        # self.connectComponents()

    # def connectComponents(self):
        # self.rasterDataDialogView.setModel(self.reclass_model)
        # self.rasterDataLayerCombo.layerChanged.connect(self.setLayer)
        
    # def setLayer(self,layer):
        # vals = qgsUtils.getRasterValsBis(layer)
        # nb_vals = len(vals)
        # free_vals = self.class_model.getFreeVals(nb_vals)
        # self.reclass_model.items = [ReclassItem(in_val,out_val)
            # for (in_val, out_val) in zip(vals, free_vals)]
        # self.reclass_model.layoutChanged.emit() 
        
    # def showDialog(self):
        # self.feedback.pushDebugInfo("showDialog")
        # while self.exec_():
            # dict = {}
            # layer = self.rasterDataLayerCombo.currentLayer()
            # if not layer:
                # self.feedback.user_error("No layer selected")
            # layer_path = qgsUtils.pathOfLayer(layer)
            # if not layer_path:
                # self.feedback.user_error("Could not load layer " + str(layer_path))
            # dict[RasterDlgItem.INPUT] = layer_path
            # dict[RasterDlgItem.RECLASS] = self.reclass_model
            # self.data_item = RasterDlgItem(dict)
            # return self.data_item
        # return None


class ImportItem(DictItemWithChild):
            
    INPUT = 'INPUT'
    MODE = 'MODE'
    VALUE = 'VALUE'
    STATUS = 'STATUS'
    DISPLAY_FIELDS = [ INPUT, VALUE, STATUS ]
    FIELDS = DISPLAY_FIELDS
    
    INPUT_IDX = 0
    MODE_IDX = 1
    VALUE_IDX = 2
    STATUS_IDX = 3

    # def fromValues(self, dlgItem=None, dict=None, parent=None, feedback=None):
        # print("dict = " +str(dict))
        # self.children = []
        # if dict:
            # self.dict = dict
            # self.recompute()
        # elif dlgItem:
            # self.updateFromDlgItem(dlgItem)
        # else:
            # assert(False)
        # super().__init__(self.dict,feedback=feedback,children=self.children)
    # @classmethod
    # def fromDlgItem(cls,dlgItem,feedback=None):
        # dict = cls.dlgToDict(dlgItem)
        # return cls(dict,feedback=feedback)
    # def recompute(self):
        # self.computed = False
        # self.name = self.getBaseName()     
        
    @staticmethod
    def getItemClass(childTag):
        return getattr(sys.modules[__name__], childTag)              
        
    @staticmethod
    def childToDict(dlgItem):
        is_vector = type(dlgItem) is VectorDlgItem
        if is_vector:
            if dlgItem.getBurnMode():
                val = dlgItem.getBurnField()
            else:
                val = dlgItem.getBurnVal()
        else:
            val = None
        dict = { ImportItem.INPUT : dlgItem.dict[ImportItem.INPUT],
            ImportItem.MODE : is_vector,
            ImportItem.VALUE : val,
            ImportItem.STATUS : False }
        return dict
    # def updateFromDlgItem(self,dlgItem):
        # self.dict = self.dlgToDict(dlgItem)
        # self.children = [dlgItem]
        # self.dlgItem = dlgItem
        
        # self.recompute()        
        
    def updateFromOther(self,other):
        for k in other.dict:
            self.dict[k] = other.dict[k]
        
    def getBaseName(self):
        # print("dict = " +str(self.dict))
        layer_path = self.dict[self.INPUT]
        if not layer_path:
            raise utils.CustomException("No layer specified for vector import")
        base = os.path.basename(layer_path)
        res = os.path.splitext(base)[0]
        # if self.is_vector and self.dlgItem.getBurnMode():
            # res += "_" + str(self.dlgItem.getBurnField())
        return res

    def isVector(self):
        return self.dict[self.MODE]
    # def getDialog(self):
        # if self.children:
            # return self.children[0]
        # else:
            # self.feedback.internal_error("No children for ImportItem")
            
    # Mandatory to redefine it for import links reasons
    # @classmethod
    # def fromXML(cls,root,feedback=None):
        # o = cls.fromDict(root.attrib)
        # for child in root:
            # childTag = child.tag
            # classObj = getattr(sys.modules[__name__], childTag)
            # childObj = classObj.fromXML(child,feedback=feedback)
            # o.setChild(childObj)
        # return o
        

class ImportModel(DictModel):

    def __init__(self, pluginModel):
        # self.item_fields = [ self.INPUT, self.EXPRESSION, self.BURN_MODE, self.BURN_VAL,
            # self.ALL_TOUCH, self.BUFFER_MODE, self.BUFFER_EXPR ]
        itemClass = getattr(sys.modules[__name__], ImportItem.__name__)
        super().__init__(itemClass,feedback=pluginModel.feedback)
        self.feedback.pushInfo("IM OK")
        # self.itemClass = getattr(sys.modules[__name__], itemClassName)
        self.pluginModel = pluginModel
        
    @staticmethod
    def getItemClass(childTag):
        return getattr(sys.modules[__name__], childTag)      
        
    def applyItemWithContext(self,item,context,feedback):
        input_path = item.getLayerPath()
        input = qgsUtils.loadLayer(input_path)
        input_extent = input.extent()
        crs = input.crs().authid()
        resolution = 10
        out_type = Qgis.Int16
        out_nodata = -1
        out_path = self.getItemOutPath(item)
        if item.isVector():
            selected = QgsProcessingUtils.generateTempFilename('selection.gpkg')
            all_touch = item.getAllTouch()
            if item.getBurnMode():
                burn_field = item.getBurnField()
                BioDispersal_algs.applyRasterizationFixAllTouch(
                    selected,out_path,input_extent,resolution,
                    field=burn_field,out_type=out_type,all_touch=all_touch,
                    context=context,feedback=feedback)
            else:
                burn_val = item.getBurnVal()
                BioDispersal_algs.applyRasterizationFixAllTouch(
                    selected,out_path,input_extent,resolution,
                    burn_val=burn_val,out_type=out_type,all_touch=all_touch,
                    context=context,feedback=feedback)
        else:
            reclassified = QgsProcessingUtils.generateTempFilename('reclassified.tif')
            qgsTreatments.applyReclassifyByTable(input,matrix,reclassified,
                out_type = out_type,boundaries_mode=2,nodata_missing=True,
                context=context,feedback=feedback)
            qgsTreatments.applyWarpReproject(reclassified,out_path,dst_crs=crs,
                extent=input_extent,extent_crs=crs,resolution=resolution,
                out_type=out_type,overwrite=True,context=context,feedback=feedback)
                
    # Returns absolute path of 'item' output layer
    def getItemOutPath(self,item):
        out_bname = item.getName() + ".tif"
        out_dir = self.pluginModel.getImportsDir()
        return os.path.join(out_dir,out_bname)
    def getItemFromName(self,name):
        for i in self.items:
            if i.getName() == name:
                return i
        return None
        
    def getImportNames(self):
        return [i.getBaseName() for i in self.items]
        
    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled
        
    # FIELDS = [ INPUT, MODE, VALUE, STATUS ]
    def getHeaderString(self,col):
        h = [self.tr('Input layer'),
            self.tr('Value'),
            self.tr('Status')]
        return h[col] 
        
    # def mkItemFromDict(self,dict,parent=None,feedback=None):
        # item = ImportItem.fromDict(dict=dict,feedback=self.feedback)
        # item.recompute()
        # return item

class ImportConnector(TableToDialogConnector):

    def __init__(self,dlg,model):
        # self.importModel = ImportModel(self)
        self.dlg = dlg
        super().__init__(model,self.dlg.importView,
            removeButton=self.dlg.importDelete,
            runButton=self.dlg.importRun)
        self.feedback.pushInfo("IC OK")
        # self.feedback = dlg.feedback
        self.onlySelection = False

    def connectComponents(self):
        super().connectComponents()
        # self.dlg.importView.doubleClicked.connect(self.openImport)
        self.dlg.importVector.clicked.connect(self.openImportVectorNew)
        self.dlg.importRaster.clicked.connect(self.openImportRasterNew)
    
    # def openImport(self,index):
        # row = index.row()
        # item = self.model.getNItem(row)
        # self.feedback.pushDebugInfo("openImport item = " +str(item))
        # if item.is_vector:
            # dlgItem = self.openImportVector(item.dlgItem)
        # else:
            # dlgItem = self.openImportRaster(item.dlgItem)
        # if dlgItem:
            # item.updateFromDlgItem(dlgItem)
            # self.model.layoutChanged.emit()
            
            
    def openDialog(self,item):
        dlgItem = item.getChild()
        if item.isVector():
            item_dlg = VectorDataDialog(dlgItem,self.dlg)
        else:
            item_dlg = RasterDataDialog(dlgItem,self.dlg,
                class_model=self.model.pluginModel.frictionModel)
        return item_dlg
        # dlgItem = item_dlg.showDialog()
        # return dlgItem
        
    def openImportVectorNew(self,checked):
        item_dlg = VectorDataDialog(None,self.dlg)
        dlgItem = item_dlg.showDialog()
        self.addDlgItem(dlgItem,True)
        
    # def openImportVector(self,dlgItem):
        # vector_data_dlg = VectorDataDialog(dlgItem,self.dlg)
        # dlgItem = vector_data_dlg.showDialog()
        # return dlgItem
        
    def openImportRasterNew(self,checked):
        item_dlg = RasterDataDialog(None,self.dlg,
            class_model=self.model.pluginModel.frictionModel)
        dlgItem = item_dlg.showDialog()
        self.addDlgItem(dlgItem,False)
            
    # def openImportRaster(self,dlgItem):
        # raster_data_dlg = RasterDataDialog(dlgItem,self.dlg,class_model=self.model.frictionModel)
        # dlgItem = raster_data_dlg.showDialog()
        # return dlgItem
        
    def addDlgItem(self,dlgItem,is_vector):
        if dlgItem:
            item = ImportItem.fromChildItem(dlgItem,feedback=self.feedback)
            item.setChild(dlgItem)
            self.model.addItem(item)
            self.model.layoutChanged.emit()
            if not item.isVector():
                codes = dlgItem.getReclassModel().getCodes()
                for code in codes:
                    basename = item.getBaseName()
                    self.model.pluginModel.frictionModel.addRowFromCode(
                        code,descr=basename)
        else:
            self.feedback.pushDebugInfo("No dlgItem given")
        
    def updateItem(self,item,dlgItem): 
        item.updateFromDlgItem(dlgItem)
        

class LanduseItem(DictItem):

    NAME = 'NAME'
    IMPORTS = 'IMPORTS'
    FIELDS = [ NAME, IMPORTS ]
    
    @classmethod
    def fromValues(cls,name=None, imports=None,feedback=None):
        dict = { cls.NAME : name, cls.IMPORTS : imports }
        return cls(dict,feedback=feedback)
        
    def getName(self):
        return self.dict[self.NAME]
    def getImports(self):
        return self.dict[self.IMPORTS]
    def setName(self,name):
        self.dict[self.NAME] = name
    def setImports(self,imports):
        self.dict[self.IMPORTS] = imports
        
    def applyItemWithContext(self,context,feedback,indexes=None):
        names = [i.getName() for n in self.items]
        import_items = [self.pluginModel.importModel.getItemFromName(n) for n in names]
        paths = [i.getItemOutPath() for i in import_items]
        # out_path = 
        qgsTreatments.applyMergeRaster(paths,out_path,
            out_type=Qgis.Int16,context=context,feedback=feedback)
        
class LanduseModel(DictModel):

    def __init__(self, pluginModel):
        itemClass = getattr(sys.modules[__name__], LanduseItem.__name__)
        self.pluginModel = pluginModel
        self.currImportNames = []
        super().__init__(itemClass,feedback=pluginModel.feedback)
                    
    def updateImportName(self):
        pass
        
    def getOutPathOfItem(self,item):
        pass
        
    def getNames(self,item):  
        return [i.getName() for i in self.items]
        
    # def addItem(self,item):
        # super().addItem()
        # self.pluginModel.addLanduse(item)
        
    def applyItemWithContext(self,context,feedback,indexes=None):
        names = [i.getName() for n in self.items]
        import_items = [self.pluginModel.importModel.getItemFromName(n) for n in names]
        paths = [i.getItemOutPath() for i in import_items]
        # out_path = 
        qgsTreatments.applyMergeRaster(paths,out_path,
            out_type=Qgis.Int16,context=context,feedback=feedback)
        
    def mkItemFromDict(self,dict,feedback=None):
        return LanduseItem(dict)
        

class LanduseConnector(AbstractConnector):

    def __init__(self,dlg,landuseModel):
        self.dlg = dlg
        self.feedback = landuseModel.feedback
        super().__init__(landuseModel,self.dlg.landuseView,
                        None,self.dlg.landuseRemove)
    
    def connectComponents(self):
        super().connectComponents()
        self.dlg.landuseView.doubleClicked.connect(self.openLanduse)
        self.dlg.landuseNew.clicked.connect(self.openLanduseNew)
    
    def openLanduseNew(self,checked):
        self.feedback.pushDebugInfo("checked = " + str(checked))
        import_names = self.model.pluginModel.importModel.getImportNames()
        self.feedback.pushDebugInfo("import names = " + str(import_names))
        landuse_dlg = LanduseDialog(self.dlg,self.model.pluginModel,
            string_list=import_names)
        res = landuse_dlg.showDialog()
        if not res:
            return
        (name, imports) = res
        if name:
            item = LanduseItem.fromValues(name=name,imports=imports,feedback=self.feedback)
            self.model.addItem(item)
            self.model.layoutChanged.emit()
        else:
            self.feedback.user_error("No name given to landuse layers ranking")
        
    def openLanduse(self,index):
        row = index.row()
        item = self.model.getNItem(row)
        self.feedback.pushDebugInfo("openImport item = " +str(item))
        landuse_dlg = LanduseDialog(self.dlg,self.model.pluginModel,
            name=item.getName(),string_list=item.getImports())
        res = landuse_dlg.showDialog()
        if not res:
            return
        (name, imports) = res
        self.feedback.pushDebugInfo("name = " +str(name))
        self.feedback.pushDebugInfo("imports = " +str(imports))
        if name:
            item.setName(name)
            item.setImports(imports)
            self.model.layoutChanged.emit()
        else:
            self.feedback.user_error("No name given to landuse layers ranking")
