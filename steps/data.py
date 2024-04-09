
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

from qgis.PyQt import uic, QtWidgets
from qgis.PyQt.QtCore import Qt
from qgis.core import Qgis, QgsProcessingUtils

from ..qgis_lib_mc import qgsUtils, qgsTreatments, utils, feedbacks
from ..qgis_lib_mc.utils import CustomException
from ..ui.vector_data_dialog import VectorDlgItem, VectorDataDialog
from ..ui.raster_data_dialog import RasterDlgItem, RasterDataDialog
from ..ui.landuse_dialog import LanduseItem, LanduseDialog
from ..qgis_lib_mc.abstract_model import (DictItem, DictModel,
    AbstractConnector, TableToDialogConnector,
    DictItemWithChild, DictItemWithChildren)


class ImportItem(DictItemWithChild):
            
    NAME = 'NAME'
    INPUT = 'INPUT'
    MODE = 'MODE'
    VALUE = 'VALUE'
    DISPLAY_FIELDS = [ NAME, INPUT, VALUE ]
    FIELDS = DISPLAY_FIELDS
        
    @staticmethod
    def getItemClass(childTag):
        return getattr(sys.modules[__name__], childTag)              
        
    @staticmethod
    def childToDict(dlgItem):
        is_vector = type(dlgItem) is VectorDlgItem
        # if is_vector:
            # val = dlgItem.getValue()
        # else:
            # val = None
        dict = { ImportItem.NAME : dlgItem.getName(),
            ImportItem.INPUT : dlgItem.dict[ImportItem.INPUT],
            ImportItem.MODE : is_vector,
            ImportItem.VALUE : dlgItem.getValue() }
        return dict 
        
    def getName(self):
        return self.dict[ImportItem.NAME]
    def getInput(self):
        return self.dict[ImportItem.INPUT]
    def getValue(self):
        return self.dict[ImportItem.VALUE]
    def keepValues(self):
        return self.child.keepValues()
    def isVector(self):
        return self.dict[self.MODE]
        
    def getValues(self):
        return self.child.getValues()
        
    def equals(self,other):
        return self.getName() == other.getName()
        
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
        return res

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
                          
    def getReclassTableFromUniqueAssoc(assoc_path,inField,outField):
        layer = qgsUtils.loadVectorLayer(assoc_path)
        table = []
        for f in layer.getFeatures():
            inVal = f[inField]
            table.append([inVal,inVal,f[outField]])
        return table
        
    def addItem(self,item,addValues=False):
        name = item.getName()
        super().addItem(item)
        if addValues:
            self.addClassItems(item)
        
    # def addClassFromValues(self,origin,values):
        # freeVals = self.pluginModel.frictionModel.getFreeVals(len(values))
        # for initVal, newVal in zip(values,freeVals):
            # self.pluginModel.classModel.addRow(origin,initVal,newVal)
    def addClassItems(self,item):
        # values = self.getItemValues(item)
        name = item.getName()
        classModel = self.pluginModel.classModel
        classModel.removeItemsWithOrigin(name)
        if item.isVector():
            if item.child.isBurnFieldMode():
                layer_path = self.pluginModel.getOrigPath(item.getInput())
                # Apply selection if needed
                childItem = item.getChild()
                expr = childItem.getExpression()
                if expr:
                    selected = qgsUtils.mkTmpPath(childItem.getName() + '_selection.gpkg')
                    qgsTreatments.extractByExpression(layer_path,expr,selected,feedback=self.feedback)
                    self.feedback.setProgress(100)
                    layer_path = selected
                layer = qgsUtils.loadVectorLayer(layer_path)
                # Fetch unique values
                fieldname = item.child.getBurnField()
                values = qgsTreatments.getVectorUniqueVals(layer,fieldname,
                    feedback=self.feedback)
                if item.keepValues():
                    for v in values:
                        classModel.addRow(name,v,v)
                else:
                    classModel.addRowFromValues(name,values)
            else:
                newVal = item.child.getBurnVal()
                classModel.addRow(name,"",newVal)
                # classModel.layoutChanged.emit()
        else:
            values = item.getValues()
            # Raster value = keep values mode
            if item.keepValues():
                for v in values:
                    classModel.addRow(name,v,v)
            else:
                classModel.addRowFromValues(name,values)
        # self.pluginModel.frictionModel.updateFromImports()
            
    # def updateItem(self,item,dlgItem):
        # diff_layer = item.getInput() != dlgItem.getLayerPath()
        # diff_field = item.getValue() != .getLayerPath()
        # if item.getInput() != dlgItem.getLayerPath():
            # importName = item.getName()
            # self.model.frictionModel.removeImports([importName])
            # super().updateItem(item,dlgItem)
            # self.addValues(item)
        # assert(False)
        
    def updateFromClassItem(self,classItem):
        for i in self.items:
            if i.isVector() and (not i.child.isBurnFieldMode()) and (i.getName() == classItem.getOrigin()):
                i.dict[ImportItem.VALUE] = classItem.getNewVal()
                self.layoutChanged.emit()
                return
        
        
    def applyItemWithContext(self,item,context,feedback):
        # Retrieve parameters
        name = item.getName()
        self.feedback.pushDebugInfo("apply Import {} ".format(name))
        self.pluginModel.paramsModel.checkInit()
        input_rel_path = item.getInput()
        input_path = self.pluginModel.getOrigPath(input_rel_path)
        inputLayer = qgsUtils.loadLayer(input_path)
        # out_type = Qgis.Byte
        reclassified = qgsUtils.mkTmpPath('reclassified.tif')
        to_norm_path = None
        out_path = self.getItemOutPath(item)
        qgsUtils.removeLayerFromPath(out_path)
        qgsUtils.removeRaster(out_path)
        crs, extent, resolution = self.pluginModel.getRasterParams()
        min_type, nodata_val = self.pluginModel.baseType, self.pluginModel.nodataVal
        nodata_val_rasterization = 65535
        # Main
        reclassified = qgsUtils.mkTmpPath('reclassified.tif')
        if item.isVector():
            childItem = item.getChild()
            # Reprojection
            reprojected = qgsUtils.mkTmpPath('reprojected.gpkg')
            qgsTreatments.applyReprojectLayer(inputLayer,crs,reprojected,
                context=context,feedback=feedback)
            # Feature selection
            expr = childItem.getExpression()
            if expr:
                selected = qgsUtils.mkTmpPath(name + '_selection.gpkg')
                qgsTreatments.extractByExpression(reprojected,expr,selected,
                    context=context,feedback=feedback)
                selected_layer = qgsUtils.loadVectorLayer(selected)
                if selected_layer.featureCount() == 0:
                    self.feedback.user_error("Empty selection for import {}, please verify expression".format(name))
            else:
                selected = reprojected
            # Bufferization
            if childItem.isBufferMode():
                buffered = qgsUtils.mkTmpPath(name + '_buffered.gpkg')
                bufferExpr = childItem.getBufferExpr()
                qgsTreatments.applyBufferFromExpr(selected,bufferExpr,
                    buffered,context=context,feedback=feedback)
            else:
                buffered = selected
            # Rasterization
            all_touch = childItem.getAllTouch()
            raster_path = qgsUtils.mkTmpPath(name + '_raster.tif')
            if childItem.isBurnFieldMode():
                # Burn by field mode
                burnField = childItem.getBurnField()
                name = item.getName()
                if childItem.keepValues():
                    self.feedback.pushDebugInfo("min_type = {}".format(min_type))
                    qgsTreatments.applyRasterization(buffered,raster_path,
                        extent,resolution,field=burnField,out_type=min_type,
                        nodata_val=nodata_val_rasterization,all_touch=all_touch,
                        context=context,feedback=feedback)
                    to_norm_path = raster_path
                else:
                    # Rasterize
                    unique_path = qgsUtils.mkTmpPath(name + '_unique.gpkg')
                    assoc_path = qgsUtils.mkTmpPath(name + '_assoc.gpkg')
                    outField = 'NUM_FIELD'
                    qgsTreatments.addUniqueValue(buffered,burnField,outField,
                        unique_path,assoc_path,context=context,feedback=feedback)
                    qgsTreatments.applyRasterization(unique_path,raster_path,
                        extent,resolution,field=outField,out_type=min_type,
                        nodata_val=nodata_val_rasterization,all_touch=all_touch,
                        context=context,feedback=feedback)                    
                    # Reclassify
                    assoc_layer = qgsUtils.loadVectorLayer(assoc_path)
                    reclassDict = self.pluginModel.classModel.getReclassDict(name)
                    self.feedback.pushDebugInfo("reclassDict = " + str(reclassDict))
                    reclassTable = []
                    for f in assoc_layer.getFeatures():
                        initVal = str(f[burnField])
                        self.feedback.pushDebugInfo("initVal = " + str(initVal))
                        self.feedback.pushDebugInfo("initVal type = " + str(initVal.__class__.__name__))
                        if len(reclassDict) > 0:
                            self.feedback.pushDebugInfo("reclassDict type = "
                                + str(list(reclassDict)[0].__class__.__name__))
                        tmpVal = f[outField]
                        if initVal not in reclassDict:
                            self.feedback.internal_error("No matching found for {} in {}".format(initVal,self.pluginModel.classModel.items))
                        outVal = reclassDict[initVal]
                        row = [tmpVal,tmpVal,outVal]
                        reclassTable += row
                    qgsTreatments.applyReclassifyByTable(raster_path,reclassTable,
                        reclassified,out_type=min_type,nodata_val=nodata_val,
                        boundaries_mode=2,context=context,feedback=feedback)
                    to_norm_path = reclassified
            else:
                # Burn by fixed value mode
                classItem = self.pluginModel.classModel.getItemFromOrigin(name)
                if not classItem:
                    self.feedback.internal_error("No class item found for item {}".format(item))
                burnVal = self.pluginModel.classModel.getItemReclassVal(classItem)
                # min_type, nodata_val = Qgis.UInt16, 0
                qgsTreatments.applyRasterization(buffered,raster_path,
                    extent,resolution,burn_val=burnVal,out_type=min_type,nodata_val=nodata_val_rasterization,
                    all_touch=all_touch,context=context,feedback=feedback)
                to_norm_path = raster_path
        else:
            # Raster mode
            keepValues = item.keepValues()
            if keepValues:
                to_norm_path = input_path
            else:           
                table = self.pluginModel.classModel.getReclassTable(name)
                # min_type, nodata_val = Qgis.UInt16, 0
                qgsTreatments.applyReclassifyByTable(input_path,table,
                    reclassified,out_type=min_type,nodata_val=nodata_val_rasterization,
                    boundaries_mode=2,nodata_missing=True,
                    context=context,feedback=feedback)
                to_norm_path = reclassified
        if to_norm_path:
            self.pluginModel.paramsModel.normalizeRaster(
                to_norm_path,out_path=out_path,
                context=context,
                feedback=feedback)
        qgsUtils.loadRasterLayer(out_path,loadProject=True)
                
    # Returns absolute path of 'item' output layer
    def getItemOutPath(self,item):
        out_bname = item.getName() + ".tif"
        out_dir = self.pluginModel.getImportsDir()
        return utils.joinPath(out_dir,out_bname)
    # def getItemFromName(self,name):
        # for i in self.items:
            # if i.getName() == name:
                # return i
        # return None
        
    def getImportNames(self):
        return [i.getName() for i in self.items]
        # return [i.getBaseName() for i in self.items]
    def getImportNamesAsStr(self):
        return ",".join(self.getImportNames())
        
    def removeItems(self,indexes):
        names = [self.items[ind.row()].getName() for ind in indexes]
        super().removeItems(indexes)
        self.pluginModel.removeImports(names)
    def removeFromName(self,name):
        self.items = [i for i in self.items if i.getName() != name]
        self.layoutChanged.emit()
        self.pluginModel.removeImports(name)
        
    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled
        
    # FIELDS = [ INPUT, MODE, VALUE, STATUS ]
    def getHeaderString(self,col):
        h = [self.tr('Name'),
            self.tr('Input layer'),
            self.tr('Value')]
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
            runButton=self.dlg.importRun,
            selectionCheckbox=self.dlg.importSelection)
        self.feedback.pushInfo("IC OK")
        # self.feedback = dlg.feedback
        self.onlySelection = False

    def connectComponents(self):
        super().connectComponents()
        # self.dlg.importView.doubleClicked.connect(self.openImport)
        self.dlg.importVector.clicked.connect(self.openImportVectorNew)
        self.dlg.importRaster.clicked.connect(self.openImportRasterNew)
        
    def applyItems(self):
        self.feedback.beginSection("Computing imports")
        super().applyItems()
        self.feedback.endSection()
    
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
            
    def preDlg(self,item):
        if item:
            dlg_item = item.getChild()
            self.pathFieldToAbs(dlg_item,VectorDlgItem.INPUT)

    def postDlg(self,dlg_item):
        self.feedback.pushDebugInfo("postDlg %s"%(str(dlg_item)))
        if isinstance(dlg_item,ImportItem):
            dlg_item = dlg_item.child
        self.pathFieldToRel(dlg_item,VectorDlgItem.INPUT)
      
    def openDialog(self,item):
        self.feedback.pushDebugInfo("openDialog " + str(item))
        dlgItem = item.getChild()
        self.feedback.pushDebugInfo("dlgItem " + str(dlgItem))
        # self.pathFieldToAbs(item,VectorDlgItem.INPUT)
        if item.isVector():
            if not item.child.isBurnFieldMode():
                classItem = self.model.pluginModel.classModel.getItemFromOrigin(item.getName())
                if not classItem:
                    self.feedback.internal_error("No class item found for item {}".format(item))
                burnVal = self.model.pluginModel.classModel.getItemReclassVal(classItem)
                dlgItem.setBurnVal(burnVal)
            item_dlg = VectorDataDialog(dlgItem,self.dlg,self.model.pluginModel.frictionModel)
        else:
            item_dlg = RasterDataDialog(dlgItem,self.dlg,
                class_model=self.model.pluginModel.frictionModel)
        return item_dlg
        # dlgItem = item_dlg.showDialog()
        # return dlgItem
        
    def openImportVectorNew(self,checked):
        item_dlg = VectorDataDialog(None,self.dlg,self.model.pluginModel.frictionModel)
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
            self.pathFieldToRel(dlgItem,VectorDlgItem.INPUT)
            item = ImportItem.fromChildItem(dlgItem,feedback=self.feedback)
            item.setChild(dlgItem)
            self.model.addItem(item,addValues=True)
            self.model.layoutChanged.emit()
            # frictionModel = self.model.pluginModel.frictionModel
            # self.feedback.pushDebugInfo("values = " + str(dlgItem.values))
            # frictionModel.addRowFromImport(dlgItem.values,item.getName())
            # if not item.isVector():
                # codes = dlgItem.getReclassModel().getCodes()
                # for code in codes:
                    # basename = item.getBaseName()
                    # self.model.pluginModel.frictionModel.addRowFromCode(
                        # code,descr=basename)
                    
        else:
            self.feedback.pushDebugInfo("No dlgItem given")
        
    def updateFromDlgItem(self,item,dlgItem):
        # Check name
        oldName, newName = item.getName(), dlgItem.getName()
        diffName = oldName != newName
        self.feedback.pushDebugInfo("diffName {} {} = {}".format(oldName,newName,diffName))
        # Check value
        oldValue, newValue = item.getValue(), dlgItem.getValue()
        diffValue = oldValue != newValue
        self.feedback.pushDebugInfo("diffValue {} {} = {}".format(oldValue,newValue,diffValue))
        # Keep values
        oldKeepValues, newKeepValues = item.keepValues(), dlgItem.keepValues()
        diffKeepValues = oldKeepValues != newKeepValues
        self.feedback.pushDebugInfo("diffKeepValues {} {} = {}".format(oldKeepValues,newKeepValues,diffKeepValues))
        # Check input
        self.pathFieldToRel(dlgItem,VectorDlgItem.INPUT)
        oldInput, newInput = item.getInput(), dlgItem.getLayerPath()
        diffInput = oldInput != newInput
        self.feedback.pushDebugInfo("diffInput {} {} = {}".format(oldInput,newInput,diffInput))
        isVector = item.isVector()
        # Check expression
        if item.isVector():
            oldExpr, newExpr = item.getChild().getExpression(), dlgItem.getExpression()
            diffExpr = oldExpr != newExpr
            self.feedback.pushDebugInfo("diffExpr {} {} = {}".format(oldExpr,newExpr,diffExpr))
        else:
            diffExpr = False
        if diffInput or diffValue or diffKeepValues or diffExpr:
            # DELETE then create NEW
            self.model.removeFromName(oldName)
            self.addDlgItem(dlgItem,isVector)
        elif diffName:
            # Update name 
            item.updateFromDlgItem(dlgItem)
            self.model.pluginModel.renameImport(oldName,newName)
        
        
class LanduseModel(DictModel):

    def __init__(self, pluginModel):
        itemClass = getattr(sys.modules[__name__], LanduseItem.__name__)
        super().__init__(itemClass,feedback=pluginModel.feedback)
        self.pluginModel = pluginModel
        self.currImportNames = []
                    
    def updateImportName(self):
        pass
        
    def getItemOutPath(self,item):
        out_bname = item.getName() + ".tif"
        out_dir = self.pluginModel.getImportsDir()
        return utils.joinPath(out_dir,out_bname)
        
    def getNames(self,item):
        return [i.getName() for i in self.items]
                                    
    def applyItemWithContext(self,item,context,feedback,indexes=None):
        names = item.getImportsAsList()
        names.reverse()
        feedback.pushDebugInfo("names = " + str(names))
        importModel = self.pluginModel.importModel
        all_names = [i.getName() for i in importModel.items]
        feedback.pushDebugInfo("all names = " + str(all_names))
        import_items = [importModel.getItemFromName(n) for n in names]
        paths = [importModel.getItemOutPath(i) for i in import_items]
        for p in paths:
            if not utils.fileExists(p):
                feedback.user_error("Please launch imports first, file '"
                    + str(p) + " does not exist")
        out_path = self.getItemOutPath(item)
        qgsUtils.removeLayerFromPath(out_path)
        qgsUtils.removeRaster(out_path)
        min_type, nodata_val = self.pluginModel.baseType, self.pluginModel.nodataVal
        qgsTreatments.applyMergeRaster(paths,out_path,out_type=min_type,
            nodata_val=nodata_val,context=context,feedback=feedback)
        qgsUtils.loadRasterLayer(out_path,loadProject=True)
        
    def mkItemFromDict(self,dict,feedback=None):
        return LanduseItem(dict)
        
    def getHeaderString(self,col):
        h = [self.tr('Name'),
            self.tr('Imports')]
        return h[col]

class LanduseConnector(TableToDialogConnector):

    def __init__(self,dlg,landuseModel):
        self.dlg = dlg
        self.feedback = landuseModel.feedback
        super().__init__(landuseModel,self.dlg.mergeView,
                        addButton=self.dlg.mergeNew,
                        removeButton=self.dlg.mergeRemove,#,
                        runButton=self.dlg.mergeRun,
                        selectionCheckbox=self.dlg.landuseSelection)
        self.onlySelection = False
    
    # def connectComponents(self):
        # super().connectComponents()
        # self.dlg.mergeView.doubleClicked.connect(self.openLanduse)
        # self.dlg.mergeNew.clicked.connect(self.openLanduseNew)
        
    def applyItems(self):
        self.feedback.beginSection("Computing merge")
        super().applyItems()
        self.feedback.endSection()
        
    def openDialog(self,item):
        self.feedback.pushDebugInfo("openDialog item = " +str(item))
        if item:
            imports_str = item.getImportsAsList()
            landuse_dlg = LanduseDialog(self.dlg,self.model.pluginModel,
                name=item.getName(),string_list=imports_str)
        else:
            import_names = self.model.pluginModel.importModel.getImportNames()
            self.feedback.pushDebugInfo("import names = " + str(import_names))
            landuse_dlg = LanduseDialog(self.dlg,self.model.pluginModel,
                string_list=import_names)
        return landuse_dlg
        
    def postDlgNew(self,item):
        self.model.addItem(item)
        self.model.layoutChanged.emit()
    
    # def openLanduseNew(self,checked):
        # self.feedback.pushDebugInfo("checked = " + str(checked))
        # import_names = self.model.pluginModel.importModel.getImportNames()
        # self.feedback.pushDebugInfo("import names = " + str(import_names))
        # landuse_dlg = LanduseDialog(self.dlg,self.model.pluginModel,
            # string_list=import_names)
        # res = landuse_dlg.showDialog()
        # if not res:
            # return
        # (name, imports) = res
        # imports2 = ",".join(imports)
        # if name:
            # item = LanduseItem.fromValues(name=name,imports=imports2,feedback=self.feedback)
            # self.model.addItem(item)
            # self.model.layoutChanged.emit()
        # else:
            # self.feedback.user_error("No name given to landuse layers ranking")
        
    # def openLanduse(self,index):
        # row = index.row()
        # item = self.model.getNItem(row)
        # self.feedback.pushDebugInfo("openLanduse item = " +str(item))
        # landuse_dlg = LanduseDialog(self.dlg,self.model.pluginModel,
            # name=item.getName(),string_list=item.getImportsAsList())
        # res = landuse_dlg.showDialog()
        # if not res:
            # return
        # (name, imports) = res
        # self.feedback.pushDebugInfo("name = " +str(name))
        # self.feedback.pushDebugInfo("imports = " +str(imports))
        # imports2 = ",".join(imports)
        # self.feedback.pushDebugInfo("imports2 = " +str(imports2))
        # if name:
            # item.setName(name)
            # item.setImports(imports2)
            # self.model.layoutChanged.emit()
        # else:
            # self.feedback.user_error("No name given to landuse layers ranking")
            
    def updateFromDlgItem(self,item,dlgItem):
        initName, newName = item.getName(), dlgItem.getName()
        self.feedback.pushDebugInfo("updateFromDlgItem {} {}".format(initName,newName))
        item.updateFromDlgItem(dlgItem)
        if initName != newName:
            self.model.pluginModel.renameData(initName,newName)
