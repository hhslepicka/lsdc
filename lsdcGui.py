#!/usr/bin/python
import sys
import os
import string
import math
from epics import PV
import daq_utils
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtCore import * 
from PyQt4.QtGui import * 
import db_lib
from QtEpicsMotorEntry import *
from QtEpicsMotorLabel import *
from QtEpicsPVLabel import *
from QtEpicsPVEntry import *
import cv2
from cv2 import *
from testSimpleConsole import *
import functools
from QPeriodicTable import QPeriodicTable
from PyMca.QtBlissGraph import QtBlissGraph
from PyMca.McaAdvancedFit import McaAdvancedFit
import numpy as np
import thread
import lsdcOlog

class snapCommentDialog(QDialog):
    def __init__(self,parent = None):
        QDialog.__init__(self,parent)
        self.setWindowTitle("Snapshot Comment")
        self.setModal(True)
        vBoxColParams1 = QtGui.QVBoxLayout()
        hBoxColParams1 = QtGui.QHBoxLayout()
        self.textEdit = QtGui.QPlainTextEdit()
        vBoxColParams1.addWidget(self.textEdit)
        commentButton = QtGui.QPushButton("Add Comment")        
        commentButton.clicked.connect(self.commentCB)
        cancelButton = QtGui.QPushButton("Cancel")        
        cancelButton.clicked.connect(self.cancelCB)
        hBoxColParams1.addWidget(commentButton)
        hBoxColParams1.addWidget(cancelButton)
        vBoxColParams1.addLayout(hBoxColParams1)
        self.setLayout(vBoxColParams1)

    def cancelCB(self):
      self.comment = ""
      self.reject()

    def commentCB(self):
      self.comment = self.textEdit.toPlainText()
      self.accept()
    
    @staticmethod
    def getComment(parent = None):
        dialog = snapCommentDialog(parent)
        result = dialog.exec_()
        return (dialog.comment, result == QDialog.Accepted)



class screenDefaultsDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.setModal(True)
        vBoxColParams1 = QtGui.QVBoxLayout()
        hBoxColParams1 = QtGui.QHBoxLayout()
        colStartLabel = QtGui.QLabel('Oscillation Start:')
        colStartLabel.setFixedWidth(120)
        colStartLabel.setAlignment(QtCore.Qt.AlignCenter) 
        self.osc_start_ledit = QtGui.QLineEdit()
        self.osc_start_ledit.setFixedWidth(60)
        self.osc_start_ledit.setText(str(daq_utils.getBeamlineConfigParam("screen_default_phist")))
        colEndLabel = QtGui.QLabel('Oscillation End:')
        colEndLabel.setAlignment(QtCore.Qt.AlignCenter) 
        colEndLabel.setFixedWidth(120)
        self.osc_end_ledit = QtGui.QLineEdit()
        self.osc_end_ledit.setFixedWidth(60)
        self.osc_end_ledit.setText(str(daq_utils.getBeamlineConfigParam("screen_default_phi_end")))
        hBoxColParams1.addWidget(colStartLabel)
        hBoxColParams1.addWidget(self.osc_start_ledit)
        hBoxColParams1.addWidget(colEndLabel)
        hBoxColParams1.addWidget(self.osc_end_ledit)
        hBoxColParams2 = QtGui.QHBoxLayout()
        colRangeLabel = QtGui.QLabel('Oscillation Range:')
        colRangeLabel.setFixedWidth(120)
        colRangeLabel.setAlignment(QtCore.Qt.AlignCenter) 
        self.osc_range_ledit = QtGui.QLineEdit()
        self.osc_range_ledit.setFixedWidth(60)
        self.osc_range_ledit.setText(str(daq_utils.getBeamlineConfigParam("screen_default_width")))
        colExptimeLabel = QtGui.QLabel('ExposureTime:')
        colExptimeLabel.setFixedWidth(120)
        colExptimeLabel.setAlignment(QtCore.Qt.AlignCenter) 
        self.exp_time_ledit = QtGui.QLineEdit()
        self.exp_time_ledit.setFixedWidth(60)
        self.exp_time_ledit.setText(str(daq_utils.getBeamlineConfigParam("screen_default_time")))
        hBoxColParams2.addWidget(colRangeLabel)
        hBoxColParams2.addWidget(self.osc_range_ledit)
        hBoxColParams2.addWidget(colExptimeLabel)
        hBoxColParams2.addWidget(self.exp_time_ledit)
        hBoxColParams3 = QtGui.QHBoxLayout()
        colEnergyLabel = QtGui.QLabel('Energy (KeV):')
        colEnergyLabel.setFixedWidth(120)
        colEnergyLabel.setAlignment(QtCore.Qt.AlignCenter) 
        self.energy_ledit = QtGui.QLineEdit()
        self.energy_ledit.setFixedWidth(60)
        self.energy_ledit.setText(str(daq_utils.getBeamlineConfigParam("screen_default_energy")))
        colTransmissionLabel = QtGui.QLabel('Transmission (%):')
        colTransmissionLabel.setAlignment(QtCore.Qt.AlignCenter) 
        colTransmissionLabel.setFixedWidth(120)
        self.transmission_ledit = QtGui.QLineEdit()
        self.transmission_ledit.setFixedWidth(60)
        self.transmission_ledit.setText(str(daq_utils.getBeamlineConfigParam("screen_transmission_percent")))
        hBoxColParams3.addWidget(colTransmissionLabel)
        hBoxColParams3.addWidget(self.transmission_ledit)
        hBoxColParams3.addWidget(colEnergyLabel)
        hBoxColParams3.addWidget(self.energy_ledit)
        hBoxColParams4 = QtGui.QHBoxLayout()
        colBeamWLabel = QtGui.QLabel('Beam Width:')
        colBeamWLabel.setFixedWidth(120)
        colBeamWLabel.setAlignment(QtCore.Qt.AlignCenter) 
        self.beamWidth_ledit = QtGui.QLineEdit()
        self.beamWidth_ledit.setText(str(daq_utils.getBeamlineConfigParam("screen_default_beamWidth")))
        self.beamWidth_ledit.setFixedWidth(60)
        colBeamHLabel = QtGui.QLabel('Beam Height:')
        colBeamHLabel.setFixedWidth(120)
        colBeamHLabel.setAlignment(QtCore.Qt.AlignCenter) 
        self.beamHeight_ledit = QtGui.QLineEdit()
        self.beamHeight_ledit.setText(str(daq_utils.getBeamlineConfigParam("screen_default_beamHeight")))
        self.beamHeight_ledit.setFixedWidth(60)
        hBoxColParams4.addWidget(colBeamWLabel)
        hBoxColParams4.addWidget(self.beamWidth_ledit)
        hBoxColParams4.addWidget(colBeamHLabel)
        hBoxColParams4.addWidget(self.beamHeight_ledit)
        hBoxColParams5 = QtGui.QHBoxLayout()
        colResoLabel = QtGui.QLabel('Resolution:')
        colResoLabel.setFixedWidth(120)
        colResoLabel.setAlignment(QtCore.Qt.AlignCenter) 
        self.resolution_ledit = QtGui.QLineEdit()
        self.resolution_ledit.setFixedWidth(60)
        self.resolution_ledit.setText(str(daq_utils.getBeamlineConfigParam("screen_default_reso")))
        colResoDistLabel = QtGui.QLabel('Detector Distance')
        colResoDistLabel.setFixedWidth(120)
        colResoDistLabel.setAlignment(QtCore.Qt.AlignCenter) 
        self.colResoCalcDistance_ledit = QtGui.QLineEdit()
        self.colResoCalcDistance_ledit.setFixedWidth(60)
        hBoxColParams5.addWidget(colResoLabel)
        hBoxColParams5.addWidget(self.resolution_ledit)
#        hBoxColParams5.addWidget(colResoDistLabel)
#        hBoxColParams5.addWidget(self.colResoCalcDistance_ledit)


        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Apply | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        self.buttons.buttons()[1].clicked.connect(self.screenDefaultsOKCB)
        self.buttons.buttons()[0].clicked.connect(self.screenDefaultsCancelCB)

#        cancelButton = QtGui.QPushButton("Cancel")        
#        cancelButton.clicked.connect(self.screenDefaultsCancelCB)
        vBoxColParams1.addLayout(hBoxColParams1)
        vBoxColParams1.addLayout(hBoxColParams2)
        vBoxColParams1.addLayout(hBoxColParams3)
        vBoxColParams1.addLayout(hBoxColParams4)
        vBoxColParams1.addLayout(hBoxColParams5)
        vBoxColParams1.addWidget(self.buttons)
#        vBoxColParams1.addWidget(cancelButton)
        self.setLayout(vBoxColParams1)

    def screenDefaultsCancelCB(self):
      self.done(QDialog.Rejected)

    def screenDefaultsOKCB(self):
      daq_utils.setBeamlineConfigParams({"screen_default_phist":float(self.osc_start_ledit.text()),"screen_default_phi_end":float(self.osc_end_ledit.text()),"screen_default_width":float(self.osc_range_ledit.text()),"screen_default_time":float(self.exp_time_ledit.text()),"screen_default_reso":float(self.resolution_ledit.text()),"screen_default_energy":float(self.energy_ledit.text()),"screen_transmission_percent":float(self.transmission_ledit.text()),"screen_default_beamWidth":float(self.beamWidth_ledit.text()),"screen_default_beamHeight":float(self.beamHeight_ledit.text())})
      self.done(QDialog.Accepted)
    


class PuckDialog(QtGui.QDialog):
    def __init__(self, parent = None):
        super(PuckDialog, self).__init__(parent)
        self.initData()
        self.initUI()


    def initData(self):
        puckList = db_lib.getAllPucks()
        dewarObj = db_lib.getPrimaryDewar()
        pucksInDewar = dewarObj["item_list"]

        data = []
#if you have to, you could store the puck_id in the item data
        for i in xrange(len(puckList)):
          if (puckList[i]["container_id"] not in pucksInDewar):
            data.append(puckList[i]["containerName"])
        self.model = QtGui.QStandardItemModel()
        labels = QtCore.QStringList(("Name"))
        self.model.setHorizontalHeaderLabels(labels)
        for i in xrange(len(data)):
            name = QtGui.QStandardItem(data[i])
            self.model.appendRow(name)


    def initUI(self):
        self.tv = QtGui.QListView(self)
        self.tv.setModel(self.model)
        QtCore.QObject.connect(self.tv, QtCore.SIGNAL("doubleClicked (QModelIndex)"),self.containerOKCB)
        behavior = QtGui.QAbstractItemView.SelectRows
        self.tv.setSelectionBehavior(behavior)
        
        self.label = QtGui.QLabel(self)
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        self.buttons.buttons()[0].clicked.connect(self.containerOKCB)
        self.buttons.buttons()[1].clicked.connect(self.containerCancelCB)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.tv) 
        layout.addWidget(self.label)
        layout.addWidget(self.buttons)
        self.setLayout(layout)        
        self.tv.clicked.connect(self.onClicked)
            
    def containerOKCB(self):
      selmod = self.tv.selectionModel()
      selection = selmod.selection()
      indexes = selection.indexes()
      if (indexes != []):
        i = 0
        item = self.model.itemFromIndex(indexes[i])
        text = str(item.text())
        self.label.setText(text)      
        self.accept()
        self.puckName = text
      else:
        text = ""
        self.reject()
        self.puckName = text
      

    def containerCancelCB(self):
      text = ""
      self.reject()
      self.puckName = text

        
    def onClicked(self, idx):
      item = self.model.itemFromIndex(idx)        
      text = str(item.text())

    @staticmethod
    def getPuckName(parent = None):
        dialog = PuckDialog(parent)
        result = dialog.exec_()
        return (dialog.puckName, result == QDialog.Accepted)



class DewarDialog(QtGui.QDialog):
    def __init__(self, parent = None):
        super(DewarDialog, self).__init__(parent)
        self.pucksPerDewarSector = 3
        self.dewarSectors = 8

        self.initData()
        self.initUI()

    def initData(self):
      dewarObj = db_lib.getPrimaryDewar()
      puckLocs = dewarObj["item_list"]
      self.data = []
      for i in xrange(len(puckLocs)):
        if (puckLocs[i] != None):
          self.data.append(db_lib.getContainerNameByID(puckLocs[i]))
        else:
          self.data.append("empty")

    def initUI(self):
        layout = QtGui.QVBoxLayout()
        headerLabelLayout = QtGui.QHBoxLayout()
        aLabel = QtGui.QLabel("A")
        aLabel.setFixedWidth(15)
        headerLabelLayout.addWidget(aLabel)
        bLabel = QtGui.QLabel("B")
        bLabel.setFixedWidth(10)
        headerLabelLayout.addWidget(bLabel)
        cLabel = QtGui.QLabel("C")
        cLabel.setFixedWidth(10)
        headerLabelLayout.addWidget(cLabel)
        layout.addLayout(headerLabelLayout)
 
        for i in range (0,self.dewarSectors):
          rowLayout = QtGui.QHBoxLayout()
          numLabel = QtGui.QLabel(str(i+1))
          rowLayout.addWidget(numLabel)
#          numLabel.setFixedWidth(
          buttons = QDialogButtonBox(Qt.Horizontal, self)
#          for j in range (0,self.pucksPerDewarSector):
          for j in range (self.pucksPerDewarSector,0,-1):
            dataIndex = (i*self.pucksPerDewarSector)+j-1
#            print dataIndex
            buttons.addButton(str(self.data[dataIndex]),0)
            buttons.buttons()[self.pucksPerDewarSector-j].clicked.connect(functools.partial(self.on_button,str(dataIndex)))
          rowLayout.addWidget(buttons)
          layout.addLayout(rowLayout)
#        for i in xrange(len(self.data),0,-1): #counting backwards
#          self.buttons.addButton(str(self.data[i-1]),0)
#          self.buttons.buttons()[len(self.data)-i].clicked.connect(functools.partial(self.on_button,str(i)))
        cancelButton = QtGui.QPushButton("Cancel")        
        cancelButton.clicked.connect(self.containerCancelCB)


        layout.addWidget(cancelButton)
        self.setLayout(layout)        
            
    def on_button(self, n):
        self.dewarPos = n
        self.accept()

    def containerCancelCB(self):
      self.dewarPos = 0
      self.reject()

    @staticmethod
    def getDewarPos(parent = None):
        dialog = DewarDialog(parent)
        result = dialog.exec_()
        return (dialog.dewarPos, result == QDialog.Accepted)


class DewarTree(QtGui.QTreeView):
    def __init__(self, parent=None):
        super(DewarTree, self).__init__(parent)
        self.pucksPerDewarSector = 3
        self.dewarSectors = 8
        self.parent=parent
        self.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        self.setAnimated(True)
        self.model = QtGui.QStandardItemModel()
        self.model.itemChanged.connect(self.queueSelectedSample)

    def keyPressEvent(self, event):
      if (event.key() == Qt.Key_Delete or event.key() == Qt.Key_Backspace):
#        print "caught the delete key"
        self.deleteSelectedCB()
      else:
        super(DewarTree,self).keyPressEvent(event)  

    def refreshTree(self):
      self.parent.dewarViewToggleCheckCB()

    def refreshTreeDewarView(self):
        selectedIndex = None
        mountedIndex = None
        selectedSampleIndex = None
        puck = None
        collectionRunning = False
        self.model.clear()
        dewarContents = db_lib.getContainerByName("primaryDewar")["item_list"]
        for i in range (0,len(dewarContents)): #dewar contents is the list of puck IDs
          parentItem = self.model.invisibleRootItem()
          if (dewarContents[i]==None):
            puck = None
            puckName = ""
          else:
            puck = db_lib.getContainerByID(dewarContents[i])
            puckName = puck["containerName"]
#            puckName = db_lib.getContainerNameByID(dewarContents[i])
#          item = QtGui.QStandardItem(QtGui.QIcon(":/trolltech/styles/commonstyle/images/file-16.png"), QtCore.QString(str(i+1) + " " + puckName))
          index_s = "%d%s" % ((i)/self.pucksPerDewarSector+1,chr(((i)%self.pucksPerDewarSector)+ord('A')))
          item = QtGui.QStandardItem(QtGui.QIcon(":/trolltech/styles/commonstyle/images/file-16.png"), QtCore.QString(index_s + " " + puckName))
          parentItem.appendRow(item)
          parentItem = item
          if (puck != None):
            puckContents = puck["item_list"]
#            puckContents = db_lib.getContainerByID(dewarContents[i])["item_list"]
            puckSize = len(puckContents)
            for j in range (0,len(puckContents)):#should be the list of samples
              if (puckContents[j] != None):
                position_s = str(j+1) + "-" + db_lib.getSampleNamebyID(puckContents[j])
                item = QtGui.QStandardItem(QtGui.QIcon(":/trolltech/styles/commonstyle/images/file-16.png"), QtCore.QString(position_s))
                item.setData(-100-puckContents[j]) #not sure what this is (9/19) - it WAS the absolute dewar position, just stuck sampleID there, but negate it to diff from reqID
#                item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsSelectable)
#                item.setCheckState(Qt.Unchecked)
                if (puckContents[j] == self.parent.mountedPin_pv.get()):
                  item.setForeground(QtGui.QColor('red'))       
                  font = QtGui.QFont()
                  font.setItalic(True)
                  font.setOverline(True)
                  font.setUnderline(True)
                  item.setFont(font)
#                  item.setBackground(QtGui.QColor('yellow'))       
                parentItem.appendRow(item)
                if (puckContents[j] == self.parent.mountedPin_pv.get()):
#                if (samplePos == self.parent.mountedPin_pv.get()):
                  mountedIndex = self.model.indexFromItem(item)
                if (puckContents[j] == self.parent.selectedSampleID): #looking for the selected item
#                if ((-100-puckContents[j]) == self.parent.SelectedItemData): #looking for the selected item
                  print "found " + str(self.parent.SelectedItemData)
                  selectedSampleIndex = self.model.indexFromItem(item)
                sampleRequestList = db_lib.getRequestsBySampleID(puckContents[j])
                for k in xrange(len(sampleRequestList)):
                  if not (sampleRequestList[k]["request_obj"].has_key("protocol")):
                    continue
                  col_item = QtGui.QStandardItem(QtGui.QIcon(":/trolltech/styles/commonstyle/images/file-16.png"), QtCore.QString(sampleRequestList[k]["request_obj"]["file_prefix"]+"_"+sampleRequestList[k]["request_obj"]["protocol"]))
                  col_item.setData(sampleRequestList[k]["request_id"])
                  col_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsSelectable)
                  if (sampleRequestList[k]["priority"] == 99999):
                    col_item.setCheckState(Qt.Checked)
                    col_item.setBackground(QtGui.QColor('green'))
                    collectionRunning = True
                    self.parent.refreshCollectionParams(sampleRequestList[k])

                  elif (sampleRequestList[k]["priority"] > 0):
                    col_item.setCheckState(Qt.Checked)
                    col_item.setBackground(QtGui.QColor('white'))
                  elif (sampleRequestList[k]["priority"]< 0):
                    col_item.setCheckState(Qt.Unchecked)
                    col_item.setBackground(QtGui.QColor('cyan'))
                  else:
                    col_item.setCheckState(Qt.Unchecked)
                    col_item.setBackground(QtGui.QColor('white'))
                  item.appendRow(col_item)
                  if (sampleRequestList[k]["request_id"] == self.parent.SelectedItemData): #looking for the selected item
                    selectedIndex = self.model.indexFromItem(col_item)
              else : #this is an empty spot, no sample
                position_s = str(j+1)
                item = QtGui.QStandardItem(QtGui.QIcon(":/trolltech/styles/commonstyle/images/file-16.png"), QtCore.QString(position_s))
                item.setData(-99)
                item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsSelectable)
                item.setCheckState(Qt.Unchecked)
                parentItem.appendRow(item)

        self.setModel(self.model)
        if (selectedSampleIndex != None and collectionRunning == False):
          print "selectedSampleIndex = " + str(selectedSampleIndex)
          self.setCurrentIndex(selectedSampleIndex)
          if (mountedIndex != None):
            self.model.itemFromIndex(mountedIndex).setForeground(QtGui.QColor('red'))       
            font = QtGui.QFont()
            font.setUnderline(True)
            font.setItalic(True)
            font.setOverline(True)
            self.model.itemFromIndex(mountedIndex).setFont(font)
          self.parent.row_clicked(selectedSampleIndex)
        elif (selectedSampleIndex == None and collectionRunning == False):
          if (mountedIndex != None):
            self.setCurrentIndex(mountedIndex)
            self.model.itemFromIndex(mountedIndex).setForeground(QtGui.QColor('red'))       
            font = QtGui.QFont()
            font.setUnderline(True)
            font.setItalic(True)
            font.setOverline(True)
            self.model.itemFromIndex(mountedIndex).setFont(font)
            self.parent.row_clicked(mountedIndex)
        else:
          pass
        if (selectedIndex != None and collectionRunning == False):
          self.setCurrentIndex(selectedIndex)
          self.parent.row_clicked(selectedIndex)
        if (collectionRunning == True):
          self.setCurrentIndex(mountedIndex)
          self.parent.row_clicked(mountedIndex)

        self.expandAll()
        self.scrollTo(self.currentIndex(),QAbstractItemView.PositionAtCenter)


    def refreshTreePriorityView(self): #"item" is a sample, "col_items" are requests which are children of samples.
        collectionRunning = False
        selectedIndex = None
        mountedIndex = None
        selectedSampleIndex = None
        self.model.clear()
        self.orderedRequests = db_lib.getOrderedRequestList()
        dewarContents = db_lib.getContainerByName("primaryDewar")["item_list"]
        maxPucks = len(dewarContents)
        requestedSampleList = []
        for i in xrange(len(self.orderedRequests)): # I need a list of samples for parent nodes
          if (self.orderedRequests[i]["sample_id"] not in requestedSampleList):
            requestedSampleList.append(self.orderedRequests[i]["sample_id"])
        for i in xrange(len(requestedSampleList)):
          parentItem = self.model.invisibleRootItem()
#          (puckPosition,absDewarPos,containerID,samplePositionInContainer) = db_lib.getAbsoluteDewarPosfromSampleID(requestedSampleList[i])
          (puckPosition,samplePositionInContainer,containerID) = db_lib.getCoordsfromSampleID(requestedSampleList[i])
       
          containerName = db_lib.getContainerNameByID(containerID)
          index_s = "%d%s" % ((puckPosition)/self.pucksPerDewarSector+1,chr(((puckPosition)%self.pucksPerDewarSector)+ord('A')))
          nodeString = QtCore.QString(index_s + " " +str(containerName)+ "-" + str(samplePositionInContainer) + "-" + str(db_lib.getSampleNamebyID(requestedSampleList[i])))
#          nodeString = QtCore.QString(str(containerName)+ "-" + str(samplePositionInContainer) + "-" + str(db_lib.getSampleNamebyID(requestedSampleList[i])))
          item = QtGui.QStandardItem(QtGui.QIcon(":/trolltech/styles/commonstyle/images/file-16.png"), nodeString)
          item.setData(-100-requestedSampleList[i]) #the negated sample_id for use in row_click
#          if (absDewarPos == self.parent.mountedPin_pv.get()):
          if (requestedSampleList[i] == self.parent.mountedPin_pv.get()):
            item.setForeground(QtGui.QColor('red'))       
            font = QtGui.QFont()
            font.setItalic(True)
            font.setOverline(True)
            font.setUnderline(True)
            item.setFont(font)

          parentItem.appendRow(item)
#          if (absDewarPos == self.parent.mountedPin_pv.get()):
          if (requestedSampleList[i] == self.parent.mountedPin_pv.get()):
            mountedIndex = self.model.indexFromItem(item)
          if (requestedSampleList[i] == self.parent.selectedSampleID): #looking for the selected item
#          if ((-100-requestedSampleList[i]) == self.parent.SelectedItemData): #looking for the selected item
            selectedSampleIndex = self.model.indexFromItem(item)
          parentItem = item
          for k in xrange(len(self.orderedRequests)):
            if (self.orderedRequests[k]["sample_id"] == requestedSampleList[i]):
              col_item = QtGui.QStandardItem(QtGui.QIcon(":/trolltech/styles/commonstyle/images/file-16.png"), QtCore.QString(self.orderedRequests[k]["request_obj"]["file_prefix"]+"_"+self.orderedRequests[k]["request_obj"]["protocol"]))
#              col_item = QtGui.QStandardItem(QtGui.QIcon(":/trolltech/styles/commonstyle/images/file-16.png"), QtCore.QString(self.orderedRequests[k]["protocol"]))
              col_item.setData(self.orderedRequests[k]["request_id"])
              col_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsSelectable)
              if (self.orderedRequests[k]["priority"] == 99999):
                col_item.setCheckState(Qt.Checked)
                col_item.setBackground(QtGui.QColor('green'))
                collectionRunning = True
                self.parent.refreshCollectionParams(self.orderedRequests[k])

              elif (self.orderedRequests[k]["priority"] > 0):
                col_item.setCheckState(Qt.Checked)
                col_item.setBackground(QtGui.QColor('white'))
              elif (self.orderedRequests[k]["priority"]< 0):
                col_item.setCheckState(Qt.Unchecked)
                col_item.setBackground(QtGui.QColor('cyan'))
              else:
                col_item.setCheckState(Qt.Unchecked)
                col_item.setBackground(QtGui.QColor('white'))
              item.appendRow(col_item)
              if (self.orderedRequests[k]["request_id"] == self.parent.SelectedItemData): #looking for the selected item
                selectedIndex = self.model.indexFromItem(col_item)
        self.setModel(self.model)
        if (selectedSampleIndex != None and collectionRunning == False):
          self.setCurrentIndex(selectedSampleIndex)
          self.parent.row_clicked(selectedSampleIndex)
        elif (selectedSampleIndex == None and collectionRunning == False):
          if (mountedIndex != None):
            self.setCurrentIndex(mountedIndex)
            self.parent.row_clicked(mountedIndex)
        else:
          pass

        if (selectedIndex != None and collectionRunning == False):
          self.setCurrentIndex(selectedIndex)
          self.parent.row_clicked(selectedIndex)
        self.scrollTo(self.currentIndex(),QAbstractItemView.PositionAtCenter)
        self.expandAll()


    def queueSelectedSample(self,item):
        print "queueing selected sample"
        reqID = item.data().toInt()[0]
        checkedSampleRequest = db_lib.getRequest(reqID)      
        if (item.checkState() == Qt.Checked):
          db_lib.updatePriority(reqID,5000)
##          checkedSampleRequest["priority"] = 5000
        else:
          db_lib.updatePriority(reqID,0)
##          checkedSampleRequest["priority"] = 0
        item.setBackground(QtGui.QColor('white'))

##        db_lib.updateRequest(checkedSampleRequest)
        self.parent.treeChanged_pv.put(1) #not sure why I don't just call the update routine, although this allows multiple guis
#        self.refreshTree()        

    def queueAllSelectedCB(self):
      selmod = self.selectionModel()
      selection = selmod.selection()
      indexes = selection.indexes()
      for i in xrange(len(indexes)):
        item = self.model.itemFromIndex(indexes[i])
        itemData = item.data().toInt()[0]
        if (itemData > 0): #then it's a request, not a sample
          selectedSampleRequest = db_lib.getRequest(itemData)
          db_lib.updatePriority(itemData,5000)
##          selectedSampleRequest["priority"] = 5000
##          db_lib.updateRequest(selectedSampleRequest)
#      self.refreshTree()
      self.parent.treeChanged_pv.put(1)



    def deQueueAllSelectedCB(self):
      selmod = self.selectionModel()
      selection = selmod.selection()
      indexes = selection.indexes()
      for i in xrange(len(indexes)):
        item = self.model.itemFromIndex(indexes[i])
        itemData = item.data().toInt()[0]
        if (itemData > 0): #then it's a request, not a sample
          selectedSampleRequest = db_lib.getRequest(itemData)
          db_lib.updatePriority(itemData,0)
##          selectedSampleRequest["priority"] = 0
##          db_lib.updateRequest(selectedSampleRequest)
#        item.setCheckState(Qt.Unchecked)
#      self.refreshTree()
      self.parent.treeChanged_pv.put(1)

    def deleteSelectedCB(self):
      selmod = self.selectionModel()
      selection = selmod.selection()
      indexes = selection.indexes()
      for i in xrange(len(indexes)):
        item = self.model.itemFromIndex(indexes[i])
        itemData = item.data().toInt()[0]
        if (itemData > 0): #then it's a request, not a sample
          selectedSampleRequest = db_lib.getRequest(itemData)
          self.selectedSampleID = selectedSampleRequest["sample_id"]
          db_lib.deleteRequest(selectedSampleRequest)
          if (selectedSampleRequest["request_obj"]["protocol"] == "raster"):
            for i in xrange(len(self.parent.rasterList)):
              if (self.parent.rasterList[i] != None):
                if (self.parent.rasterList[i]["request_id"] == selectedSampleRequest["request_id"]):
                  self.parent.scene.removeItem(self.parent.rasterList[i]["graphicsItem"])
                  self.parent.rasterList[i] = None
#      self.refreshTree()
      self.parent.treeChanged_pv.put(1)
      

    def expandAllCB(self):
      self.expandAll()

    def collapseAllCB(self):
      self.collapseAll()



class DataLocInfo(QtGui.QGroupBox):

    def __init__(self,parent=None):
        QGroupBox.__init__(self,parent)
        self.parent = parent
#        self.dataPathGB = QtGui.QGroupBox()
        self.setTitle("Data Location")
        self.vBoxDPathParams1 = QtGui.QVBoxLayout()
        self.hBoxDPathParams1 = QtGui.QHBoxLayout()
        self.basePathLabel = QtGui.QLabel('Base Path:')
        self.base_path_ledit = QtGui.QLineEdit() #leave editable for now
        self.base_path_ledit.setText(os.getcwd())
        self.base_path_ledit.textChanged[str].connect(self.basePathTextChanged)
        self.browseBasePathButton = QtGui.QPushButton("Browse...") 
        self.browseBasePathButton.clicked.connect(self.parent.popBaseDirectoryDialogCB)
        self.hBoxDPathParams1.addWidget(self.basePathLabel)
        self.hBoxDPathParams1.addWidget(self.base_path_ledit)
        self.hBoxDPathParams1.addWidget(self.browseBasePathButton)
        self.hBoxDPathParams2 = QtGui.QHBoxLayout()
        self.dataPrefixLabel = QtGui.QLabel('Data Prefix:')
        self.prefix_ledit = QtGui.QLineEdit()
        self.hBoxDPathParams2.addWidget(self.dataPrefixLabel)
        self.hBoxDPathParams2.addWidget(self.prefix_ledit)
        self.dataNumstartLabel = QtGui.QLabel('File Number Start:')
        self.file_numstart_ledit = QtGui.QLineEdit()
        self.file_numstart_ledit.setFixedWidth(50)
        self.hBoxDPathParams3 = QtGui.QHBoxLayout()
        self.dataPathLabel = QtGui.QLabel('Data Path:')
        self.dataPath_ledit = QtGui.QLineEdit()
        self.hBoxDPathParams3.addWidget(self.dataPathLabel)
        self.hBoxDPathParams3.addWidget(self.dataPath_ledit)
        self.hBoxDPathParams2.addWidget(self.dataNumstartLabel)
        self.hBoxDPathParams2.addWidget(self.file_numstart_ledit)
        self.vBoxDPathParams1.addLayout(self.hBoxDPathParams1)
        self.vBoxDPathParams1.addLayout(self.hBoxDPathParams2)
        self.vBoxDPathParams1.addLayout(self.hBoxDPathParams3)
#        self.vBoxDPathParams1.addLayout(self.hBoxLastFileLayout1)
        self.setLayout(self.vBoxDPathParams1)


    def basePathTextChanged(self,text):
      prefix = self.prefix_ledit.text()
      self.setDataPath_ledit(text+"/projID/"+prefix+"/1/")


    def setFileNumstart_ledit(self,s):
      self.file_numstart_ledit.setText(s)

    def setFilePrefix_ledit(self,s):
      self.prefix_ledit.setText(s)

    def setBasePath_ledit(self,s):
      self.base_path_ledit.setText(s)

    def setDataPath_ledit(self,s):
      self.dataPath_ledit.setText(s)



class rasterCell(QtGui.QGraphicsRectItem):

    def __init__(self,x,y,w,h,topParent,scene):
      super(rasterCell,self).__init__(x,y,w,h,None,scene)
      self.topParent = topParent

    def mousePressEvent(self, e):
      print "mouse pressed on raster cell"
      if (self.topParent.vidActionRasterExploreRadio.isChecked()):
        if (self.data(0) != None):
          print "found " + str(self.data(0).toInt()[0]) + " spots"
          print "for file " + str(self.data(1).toString())
      else:
        super(rasterCell, self).mousePressEvent(e)



class rasterGroup(QtGui.QGraphicsItemGroup):
    def __init__(self,parent = None):
        super(rasterGroup, self).__init__()
        self.parent=parent
        self.setHandlesChildEvents(False)
#        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True)
#        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)


    def mousePressEvent(self, e):
      super(rasterGroup, self).mousePressEvent(e)
      print "mouse pressed on group"
      for i in xrange(len(self.parent.rasterList)):
        if (self.parent.rasterList[i] != None):
          if (self.parent.rasterList[i]["graphicsItem"].isSelected()):
            print "found selected raster"
            self.parent.SelectedItemData = self.parent.rasterList[i]["request_id"]
            self.parent.treeChanged_pv.put(1)




    def mouseMoveEvent(self, e):

#        if e.buttons() != QtCore.Qt.RightButton:                      
#        QtGui.QWidget.mouseMoveEvent(self, e)   
        if e.buttons() == QtCore.Qt.LeftButton:
          pass
#            print 'left move'
        if e.buttons() == QtCore.Qt.RightButton:
          pass
#            print 'right move'

        super(rasterGroup, self).mouseMoveEvent(e)
        print "pos " + str(self.pos())
#        print "scene pos " + str(self.scenePos()

    def mouseReleaseEvent(self, e):
        super(rasterGroup, self).mouseReleaseEvent(e)
        if e.button() == QtCore.Qt.LeftButton:
          pass
#            print 'left release'
        if e.button() == QtCore.Qt.RightButton:
#            print 'right release'
          pass

#        print "released at " + str(self.pos())
#        print "released at scene pos " + str(self.scenePos())



class controlMain(QtGui.QMainWindow):
    global program_starting
    program_starting = 1
#1/13/15 - are these necessary?, 4/1 - still no idea
    Signal = QtCore.pyqtSignal()
    refreshTreeSignal = QtCore.pyqtSignal()
    serverMessageSignal = QtCore.pyqtSignal()
    programStateSignal = QtCore.pyqtSignal()

    
    def __init__(self):
        super(controlMain, self).__init__()
        self.SelectedItemData = -999 #attempt to know what row is selected
        self.groupName = "skinner"        
        self.vectorStart = None
        self.vectorEnd = None
        self.initUI()
        self.createSampleTab()
        self.initCallbacks()
        self.dewarTree.refreshTreeDewarView()
        self.motPos = {"x":self.sampx_pv.get(),"y":self.sampy_pv.get(),"z":self.sampz_pv.get(),"omega":self.omega_pv.get()}
        if (self.mountedPin_pv.get() == 0):
          mountedPin = db_lib.beamlineInfo('john', 'mountedSample')["sampleID"]
          self.mountedPin_pv.put(mountedPin)


    def initVideo2(self,frequency):
      self.captureZoom=cv2.VideoCapture("http://lob1-h:8080/CZOOM.MJPG.mjpg")
            

    def createSampleTab(self):

        sampleTab= QtGui.QWidget()      
        splitter1 = QtGui.QSplitter(Qt.Horizontal)
        vBoxlayout= QtGui.QVBoxLayout()
        self.dewarTreeFrame = QFrame()
        vBoxDFlayout= QtGui.QVBoxLayout()
        self.selectedSampleRequest = {}
        self.selectedSampleID = -1
        self.dewarTree   = DewarTree(self)
#        self.connect(self.dewarTree.model, QtCore.SIGNAL('dataChanged(QModelIndex,QModelIndex)'), self.tree_changed)
        QtCore.QObject.connect(self.dewarTree, QtCore.SIGNAL("clicked (QModelIndex)"),self.row_clicked)
        treeSelectBehavior = QtGui.QAbstractItemView.SelectItems
        treeSelectMode = QtGui.QAbstractItemView.ExtendedSelection
        self.dewarTree.setSelectionMode(treeSelectMode)
        self.dewarTree.setSelectionBehavior(treeSelectBehavior)
        hBoxRadioLayout1= QtGui.QHBoxLayout()   
        self.viewRadioGroup=QtGui.QButtonGroup()
        self.priorityViewRadio = QtGui.QRadioButton("PriorityView")
        self.priorityViewRadio.setChecked(True)
        self.priorityViewRadio.toggled.connect(functools.partial(self.dewarViewToggledCB,"priorityView"))
        self.viewRadioGroup.addButton(self.priorityViewRadio)
        self.dewarViewRadio = QtGui.QRadioButton("DewarView")
        self.dewarViewRadio.toggled.connect(functools.partial(self.dewarViewToggledCB,"dewarView"))
        hBoxRadioLayout1.addWidget(self.priorityViewRadio)
        hBoxRadioLayout1.addWidget(self.dewarViewRadio)
        self.viewRadioGroup.addButton(self.dewarViewRadio)
        vBoxDFlayout.addLayout(hBoxRadioLayout1)
        vBoxDFlayout.addWidget(self.dewarTree)
        queueSelectedButton = QtGui.QPushButton("Queue All Selected")        
        queueSelectedButton.clicked.connect(self.dewarTree.queueAllSelectedCB)
        deQueueSelectedButton = QtGui.QPushButton("deQueue All Selected")        
        deQueueSelectedButton.clicked.connect(self.dewarTree.deQueueAllSelectedCB)
        runQueueButton = QtGui.QPushButton("Collect Queue")        
        runQueueButton.clicked.connect(self.collectQueueCB)
        stopRunButton = QtGui.QPushButton("Stop Collection")        
        stopRunButton.clicked.connect(self.stopRunCB)
        puckToDewarButton = QtGui.QPushButton("Puck to Dewar...")        
        mountSampleButton = QtGui.QPushButton("Mount Sample")        
        mountSampleButton.clicked.connect(self.mountSampleCB)
        unmountSampleButton = QtGui.QPushButton("Unmount Sample")        
        unmountSampleButton.clicked.connect(self.unmountSampleCB)
        puckToDewarButton.clicked.connect(self.puckToDewarCB)
        removePuckButton = QtGui.QPushButton("Remove Puck...")        
        removePuckButton.clicked.connect(self.removePuckCB)
        expandAllButton = QtGui.QPushButton("Expand All")        
        expandAllButton.clicked.connect(self.dewarTree.expandAllCB)
        collapseAllButton = QtGui.QPushButton("Collapse All")        
        collapseAllButton.clicked.connect(self.dewarTree.collapseAllCB)

###        self.statusLabel = QtEpicsPVLabel(daq_utils.beamline+"_comm:program_state",self,300,highlight_on_change=False)
#        self.statusLabel = QtEpicsPVLabel(daq_utils.beamline+"_comm:program_state",self,300)
###        self.statusLabel.getEntry().setAlignment(QtCore.Qt.AlignCenter) 
        hBoxTreeButtsLayout = QtGui.QHBoxLayout()
        vBoxTreeButtsLayoutLeft = QtGui.QVBoxLayout()
        vBoxTreeButtsLayoutRight = QtGui.QVBoxLayout()
        vBoxTreeButtsLayoutLeft.addWidget(runQueueButton)
        vBoxTreeButtsLayoutLeft.addWidget(stopRunButton)
        vBoxTreeButtsLayoutLeft.addWidget(mountSampleButton)
        vBoxTreeButtsLayoutLeft.addWidget(unmountSampleButton)
        vBoxTreeButtsLayoutLeft.addWidget(expandAllButton)
        vBoxTreeButtsLayoutRight.addWidget(puckToDewarButton)
        vBoxTreeButtsLayoutRight.addWidget(removePuckButton)
        vBoxTreeButtsLayoutRight.addWidget(queueSelectedButton)
        vBoxTreeButtsLayoutRight.addWidget(deQueueSelectedButton)
        vBoxTreeButtsLayoutRight.addWidget(collapseAllButton)
        hBoxTreeButtsLayout.addLayout(vBoxTreeButtsLayoutLeft)
        hBoxTreeButtsLayout.addLayout(vBoxTreeButtsLayoutRight)
        vBoxDFlayout.addLayout(hBoxTreeButtsLayout)
###        vBoxDFlayout.addWidget(self.statusLabel.getEntry())
        self.dewarTreeFrame.setLayout(vBoxDFlayout)
        splitter1.addWidget(self.dewarTreeFrame)
        splitter11 = QtGui.QSplitter(Qt.Horizontal)
        self.mainSetupFrame = QFrame()
        vBoxMainSetup = QtGui.QVBoxLayout()
        self.mainToolBox = QtGui.QToolBox()
#        self.mainToolBox.setFixedWidth(570)
        self.mainToolBox.setMinimumWidth(520)
        self.mainColFrame = QFrame()
        vBoxMainColLayout= QtGui.QVBoxLayout()
        colParamsGB = QtGui.QGroupBox()
        colParamsGB.setTitle("Acquisition")
        vBoxColParams1 = QtGui.QVBoxLayout()
        hBoxColParams1 = QtGui.QHBoxLayout()
        colStartLabel = QtGui.QLabel('Oscillation Start:')
        colStartLabel.setFixedWidth(120)
        colStartLabel.setAlignment(QtCore.Qt.AlignCenter) 
        self.osc_start_ledit = QtGui.QLineEdit()
        self.osc_start_ledit.setFixedWidth(60)
        colEndLabel = QtGui.QLabel('Oscillation End:')
        colEndLabel.setAlignment(QtCore.Qt.AlignCenter) 
        colEndLabel.setFixedWidth(120)
        self.osc_end_ledit = QtGui.QLineEdit()
        self.osc_end_ledit.setFixedWidth(60)
        hBoxColParams1.addWidget(colStartLabel)
        hBoxColParams1.addWidget(self.osc_start_ledit)
        hBoxColParams1.addWidget(colEndLabel)
        hBoxColParams1.addWidget(self.osc_end_ledit)
        hBoxColParams2 = QtGui.QHBoxLayout()
        colRangeLabel = QtGui.QLabel('Oscillation Range:')
        colRangeLabel.setFixedWidth(120)
        colRangeLabel.setAlignment(QtCore.Qt.AlignCenter) 
        self.osc_range_ledit = QtGui.QLineEdit()
        self.osc_range_ledit.setFixedWidth(60)
        colExptimeLabel = QtGui.QLabel('ExposureTime:')
        colExptimeLabel.setFixedWidth(120)
        colExptimeLabel.setAlignment(QtCore.Qt.AlignCenter) 
        self.exp_time_ledit = QtGui.QLineEdit()
        self.exp_time_ledit.setFixedWidth(60)
        hBoxColParams2.addWidget(colRangeLabel)
        hBoxColParams2.addWidget(self.osc_range_ledit)
        hBoxColParams2.addWidget(colExptimeLabel)
        hBoxColParams2.addWidget(self.exp_time_ledit)
        hBoxColParams3 = QtGui.QHBoxLayout()
        colEnergyLabel = QtGui.QLabel('Energy (KeV):')
        colEnergyLabel.setFixedWidth(120)
        colEnergyLabel.setAlignment(QtCore.Qt.AlignCenter) 
        self.energy_ledit = QtGui.QLineEdit()
        self.energy_ledit.setFixedWidth(60)
        self.energy_ledit.textChanged[str].connect(self.energyTextChanged)
        colTransmissionLabel = QtGui.QLabel('Transmission (%):')
        colTransmissionLabel.setAlignment(QtCore.Qt.AlignCenter) 
        colTransmissionLabel.setFixedWidth(120)
        self.transmission_ledit = QtGui.QLineEdit()
        self.transmission_ledit.setFixedWidth(60)
        hBoxColParams3.addWidget(colTransmissionLabel)
        hBoxColParams3.addWidget(self.transmission_ledit)
        hBoxColParams3.addWidget(colEnergyLabel)
        hBoxColParams3.addWidget(self.energy_ledit)
        hBoxColParams4 = QtGui.QHBoxLayout()
        colBeamWLabel = QtGui.QLabel('Beam Width:')
        colBeamWLabel.setFixedWidth(120)
        colBeamWLabel.setAlignment(QtCore.Qt.AlignCenter) 
        self.beamWidth_ledit = QtGui.QLineEdit()
        self.beamWidth_ledit.setFixedWidth(60)
        colBeamHLabel = QtGui.QLabel('Beam Height:')
        colBeamHLabel.setFixedWidth(120)
        colBeamHLabel.setAlignment(QtCore.Qt.AlignCenter) 
        self.beamHeight_ledit = QtGui.QLineEdit()
        self.beamHeight_ledit.setFixedWidth(60)
        hBoxColParams4.addWidget(colBeamWLabel)
        hBoxColParams4.addWidget(self.beamWidth_ledit)
        hBoxColParams4.addWidget(colBeamHLabel)
        hBoxColParams4.addWidget(self.beamHeight_ledit)
        hBoxColParams5 = QtGui.QHBoxLayout()
        colResoLabel = QtGui.QLabel('Resolution:')
        colResoLabel.setFixedWidth(120)
        colResoLabel.setAlignment(QtCore.Qt.AlignCenter) 
        self.resolution_ledit = QtGui.QLineEdit()
        self.resolution_ledit.textChanged[str].connect(self.resoTextChanged)
        self.resolution_ledit.setFixedWidth(60)
        colResoDistLabel = QtGui.QLabel('Detector Distance')
        colResoDistLabel.setFixedWidth(120)
        colResoDistLabel.setAlignment(QtCore.Qt.AlignCenter) 
        self.colResoCalcDistance_ledit = QtGui.QLabel()
#        self.colResoCalcDistance_ledit = QtGui.QLineEdit()
#        self.colResoCalcDistance_ledit.setReadOnly(True)
        self.colResoCalcDistance_ledit.setFixedWidth(60)
        hBoxColParams5.addWidget(colResoLabel)
        hBoxColParams5.addWidget(self.resolution_ledit)
        hBoxColParams5.addWidget(colResoDistLabel)
        hBoxColParams5.addWidget(self.colResoCalcDistance_ledit)
        hBoxColParams6 = QtGui.QHBoxLayout()
        hBoxColParams6.setAlignment(QtCore.Qt.AlignLeft) 
        centeringLabel = QtGui.QLabel('Centering:')
#        centeringOptionList = ["Interactive","AutoRaster","AutoLoop"]
        centeringOptionList = ["Interactive","Automatic"]
        self.centeringComboBox = QtGui.QComboBox(self)
        self.centeringComboBox.addItems(centeringOptionList)
#        self.centeringComboBox.activated[str].connect(self.ComboActivatedCB) 
        protoLabel = QtGui.QLabel('Protocol:')
        protoOptionList = ["standard","screen","raster","vector","characterize"]
        self.protoComboBox = QtGui.QComboBox(self)
        self.protoComboBox.addItems(protoOptionList)
        self.protoComboBox.activated[str].connect(self.protoComboActivatedCB) 
        hBoxColParams6.addWidget(protoLabel)
        hBoxColParams6.addWidget(self.protoComboBox)
#        hBoxColParams6.addWidget(centeringLabel)
#        hBoxColParams6.addWidget(self.centeringComboBox)

        self.processingOptionsFrame = QFrame()
        self.hBoxProcessingLayout1= QtGui.QHBoxLayout()        
        self.hBoxProcessingLayout1.setAlignment(QtCore.Qt.AlignLeft) 
        procOptionLabel = QtGui.QLabel('Processing Options:')
        procOptionLabel.setFixedWidth(200)
        self.fastDPCheckBox = QCheckBox("FastDP")
        self.fastDPCheckBox.setChecked(False)
        self.fastEPCheckBox = QCheckBox("FastEP")
        self.fastEPCheckBox.setChecked(False)
        self.xia2CheckBox = QCheckBox("Xia2")
        self.xia2CheckBox.setChecked(False)
        self.hBoxProcessingLayout1.addWidget(procOptionLabel)
        self.hBoxProcessingLayout1.addWidget(self.fastDPCheckBox)
        self.hBoxProcessingLayout1.addWidget(self.fastEPCheckBox)
        self.hBoxProcessingLayout1.addWidget(self.xia2CheckBox)
        self.processingOptionsFrame.setLayout(self.hBoxProcessingLayout1)

        self.rasterParamsFrame = QFrame()
        self.hBoxRasterLayout1= QtGui.QHBoxLayout()        
        self.hBoxRasterLayout1.setAlignment(QtCore.Qt.AlignLeft) 
        rasterStepLabel = QtGui.QLabel('Raster Step')
        rasterStepLabel.setFixedWidth(100)
        self.rasterStepEdit = QtGui.QLineEdit("30")
        self.rasterStepEdit.setFixedWidth(60)

        self.rasterGrainRadioGroup=QtGui.QButtonGroup()
        self.rasterGrainCoarseRadio = QtGui.QRadioButton("Coarse")
        self.rasterGrainCoarseRadio.setChecked(False)
        self.rasterGrainCoarseRadio.toggled.connect(functools.partial(self.rasterGrainToggledCB,"Coarse"))
        self.rasterGrainRadioGroup.addButton(self.rasterGrainCoarseRadio)
        self.rasterGrainFineRadio = QtGui.QRadioButton("Fine")
        self.rasterGrainFineRadio.setChecked(False)
        self.rasterGrainFineRadio.toggled.connect(functools.partial(self.rasterGrainToggledCB,"Fine"))
        self.rasterGrainRadioGroup.addButton(self.rasterGrainFineRadio)
        self.rasterGrainCustomRadio = QtGui.QRadioButton("Custom")
        self.rasterGrainCustomRadio.setChecked(True)
        self.rasterGrainCustomRadio.toggled.connect(functools.partial(self.rasterGrainToggledCB,"Custom"))
        self.rasterGrainRadioGroup.addButton(self.rasterGrainCustomRadio)

#        self.rasterStepEdit.setAlignment(QtCore.Qt.AlignLeft) 
        self.hBoxRasterLayout1.addWidget(rasterStepLabel)
#        self.hBoxRasterLayout1.addWidget(self.rasterStepEdit.getEntry())
        self.hBoxRasterLayout1.addWidget(self.rasterStepEdit)
        self.hBoxRasterLayout1.addWidget(self.rasterGrainCoarseRadio)
        self.hBoxRasterLayout1.addWidget(self.rasterGrainFineRadio)
        self.hBoxRasterLayout1.addWidget(self.rasterGrainCustomRadio)
        self.rasterParamsFrame.setLayout(self.hBoxRasterLayout1)
        self.characterizeParamsFrame = QFrame()
        vBoxCharacterizeParams1 = QtGui.QVBoxLayout()
        self.hBoxCharacterizeLayout1= QtGui.QHBoxLayout() 
        self.characterizeTargetLabel = QtGui.QLabel('Characterization Targets')       
        characterizeResoLabel = QtGui.QLabel('Resolution')
        characterizeResoLabel.setFixedWidth(120)
        characterizeResoLabel.setAlignment(QtCore.Qt.AlignCenter) 
        self.characterizeResoEdit = QtGui.QLineEdit("3.0")
        self.characterizeResoEdit.setFixedWidth(60)
        characterizeISIGLabel = QtGui.QLabel('I/Sigma')
        characterizeISIGLabel.setFixedWidth(120)
        characterizeISIGLabel.setAlignment(QtCore.Qt.AlignCenter) 
        self.characterizeISIGEdit = QtGui.QLineEdit("2.0")
        self.characterizeISIGEdit.setFixedWidth(60)
        self.hBoxCharacterizeLayout2 = QtGui.QHBoxLayout() 
        characterizeCompletenessLabel = QtGui.QLabel('Completeness')
        characterizeCompletenessLabel.setFixedWidth(120)
        characterizeCompletenessLabel.setAlignment(QtCore.Qt.AlignCenter) 
        self.characterizeCompletenessEdit = QtGui.QLineEdit("0.99")
        self.characterizeCompletenessEdit.setFixedWidth(60)
        characterizeMultiplicityLabel = QtGui.QLabel('Multiplicity')
        characterizeMultiplicityLabel.setFixedWidth(120)
        characterizeMultiplicityLabel.setAlignment(QtCore.Qt.AlignCenter) 
        self.characterizeMultiplicityEdit = QtGui.QLineEdit("auto")
        self.characterizeMultiplicityEdit.setFixedWidth(60)
        self.hBoxCharacterizeLayout1.addWidget(characterizeResoLabel)
        self.hBoxCharacterizeLayout1.addWidget(self.characterizeResoEdit)
        self.hBoxCharacterizeLayout1.addWidget(characterizeISIGLabel)
        self.hBoxCharacterizeLayout1.addWidget(self.characterizeISIGEdit)
        self.hBoxCharacterizeLayout2.addWidget(characterizeCompletenessLabel)
        self.hBoxCharacterizeLayout2.addWidget(self.characterizeCompletenessEdit)
        self.hBoxCharacterizeLayout2.addWidget(characterizeMultiplicityLabel)
        self.hBoxCharacterizeLayout2.addWidget(self.characterizeMultiplicityEdit)
        vBoxCharacterizeParams1.addWidget(self.characterizeTargetLabel)
        vBoxCharacterizeParams1.addLayout(self.hBoxCharacterizeLayout1)
        vBoxCharacterizeParams1.addLayout(self.hBoxCharacterizeLayout2)
        self.characterizeParamsFrame.setLayout(vBoxCharacterizeParams1)
        self.vectorParamsFrame = QFrame()
        hBoxVectorLayout1= QtGui.QHBoxLayout() 
        setVectorStartButton = QtGui.QPushButton("Set Start") 
        setVectorStartButton.clicked.connect(self.setVectorStartCB)
        setVectorEndButton = QtGui.QPushButton("Set End") 
        setVectorEndButton.clicked.connect(self.setVectorEndCB)
        vectorFPPLabel = QtGui.QLabel("Frames Per Point")
        self.vectorFPP_ledit = QtGui.QLineEdit("1")
#        clearVectorButton = QtGui.QPushButton("Clear Vector") 
#        clearVectorButton.clicked.connect(self.clearVectorCB)
        hBoxVectorLayout1.addWidget(setVectorStartButton)
        hBoxVectorLayout1.addWidget(setVectorEndButton)
        hBoxVectorLayout1.addWidget(vectorFPPLabel)
        hBoxVectorLayout1.addWidget(self.vectorFPP_ledit)
#        hBoxVectorLayout1.addWidget(clearVectorButton)
        self.vectorParamsFrame.setLayout(hBoxVectorLayout1)
        vBoxColParams1.addLayout(hBoxColParams1)
        vBoxColParams1.addLayout(hBoxColParams2)
        vBoxColParams1.addLayout(hBoxColParams3)
        vBoxColParams1.addLayout(hBoxColParams4)
        vBoxColParams1.addLayout(hBoxColParams5)
        vBoxColParams1.addLayout(hBoxColParams6)
#        vBoxColParams1.addLayout(self.hBoxRasterLayout1)
        vBoxColParams1.addWidget(self.rasterParamsFrame)
        vBoxColParams1.addWidget(self.vectorParamsFrame)
        vBoxColParams1.addWidget(self.characterizeParamsFrame)
        vBoxColParams1.addWidget(self.processingOptionsFrame)
        self.vectorParamsFrame.hide()
        self.processingOptionsFrame.hide()
        self.rasterParamsFrame.hide()
        self.characterizeParamsFrame.hide()
        colParamsGB.setLayout(vBoxColParams1)
        self.dataPathGB = DataLocInfo(self)
        self.hBoxLastFileLayout1= QtGui.QHBoxLayout()        
#        self.lastFileLabel = QtGui.QLabel('Last File:')
#        self.lastFileLabel.setFixedWidth(70)
#        self.lastFileRBV = QtEpicsPVLabel("XF:AMXFMX:det1:FullFileName_RBV",self,0)
#        self.hBoxLastFileLayout1.addWidget(self.lastFileLabel)
#        self.hBoxLastFileLayout1.addWidget(self.lastFileRBV.getEntry())
        vBoxMainColLayout.addWidget(colParamsGB)
        vBoxMainColLayout.addWidget(self.dataPathGB)
        vBoxMainColLayout.addLayout(self.hBoxLastFileLayout1)
        self.mainColFrame.setLayout(vBoxMainColLayout)
        self.EScanToolFrame = QFrame()
        vBoxEScanTool = QtGui.QVBoxLayout()
        self.periodicTableTool = QPeriodicTable(self.EScanToolFrame,butSize=20)
        self.EScanDataPathGBTool = DataLocInfo(self)
        vBoxEScanTool.addWidget(self.periodicTableTool)
        vBoxEScanTool.addWidget(self.EScanDataPathGBTool)
        self.EScanToolFrame.setLayout(vBoxEScanTool)
        self.mainToolBox.addItem(self.mainColFrame,"Standard Collection")
        self.mainToolBox.addItem(self.EScanToolFrame,"Energy Scan")
        editSampleButton = QtGui.QPushButton("Apply Changes") 
        editSampleButton.clicked.connect(self.editSelectedRequestsCB)
#        editSampleButton.clicked.connect(self.editSampleRequestCB)
        hBoxPriorityLayout1= QtGui.QHBoxLayout()        
        priorityEditLabel = QtGui.QLabel("Priority Edit")
        priorityTopButton =  QtGui.QPushButton("   >>   ")
        priorityUpButton =   QtGui.QPushButton("   >    ")
        priorityDownButton = QtGui.QPushButton("   <    ")
        priorityBottomButton=QtGui.QPushButton("   <<   ")
        priorityTopButton.clicked.connect(self.topPriorityCB)
        priorityBottomButton.clicked.connect(self.bottomPriorityCB)
        priorityUpButton.clicked.connect(self.upPriorityCB)
        priorityDownButton.clicked.connect(self.downPriorityCB)
        hBoxPriorityLayout1.addWidget(priorityEditLabel)
        hBoxPriorityLayout1.addWidget(priorityBottomButton)
        hBoxPriorityLayout1.addWidget(priorityDownButton)
        hBoxPriorityLayout1.addWidget(priorityUpButton)
        hBoxPriorityLayout1.addWidget(priorityTopButton)
        queueSampleButton = QtGui.QPushButton("Add Requests to Queue") 
        queueSampleButton.clicked.connect(self.addRequestsToAllSelectedCB)
#        queueSampleButton.clicked.connect(self.addSampleRequestCB)
        deleteSampleButton = QtGui.QPushButton("Delete Requests") 
#        deleteSampleButton.clicked.connect(self.deleteFromQueueCB)
        deleteSampleButton.clicked.connect(self.dewarTree.deleteSelectedCB)
        editScreenParamsButton = QtGui.QPushButton("Edit Screening Parmams...") 
        editScreenParamsButton.clicked.connect(self.editScreenParamsCB)
        vBoxMainSetup.addWidget(self.mainToolBox)
        vBoxMainSetup.addLayout(hBoxPriorityLayout1)
        vBoxMainSetup.addWidget(editSampleButton)
        vBoxMainSetup.addWidget(queueSampleButton)
        vBoxMainSetup.addWidget(deleteSampleButton)
        vBoxMainSetup.addWidget(editScreenParamsButton)
        self.mainSetupFrame.setLayout(vBoxMainSetup)
        self.VidFrame = QFrame()
        vBoxVidLayout= QtGui.QVBoxLayout()
        if (daq_utils.has_xtalview):
          thread.start_new_thread(self.initVideo2,(.25,))
          self.captureFull=cv2.VideoCapture("http://lob1-h:8080/C1.MJPG.mjpg")
        else:
          self.captureFull = None
          self.captureZoom = None
        time.sleep(1)
        self.capture = self.captureFull
        self.nocapture = self.captureZoom
        if (daq_utils.has_xtalview):
          self.timerId = self.startTimer(0) #allegedly does this when window event loop is done if this = 0, otherwise milliseconds, but seems to suspend anyway is use milliseconds (confirmed)
        self.centeringMarksList = []
        self.rasterList = []
        self.rasterDefList = []
        self.polyPointItems = []
        self.rasterPoly = None
        self.scene = QtGui.QGraphicsScene(0,0,646,482,self)
        self.scene.keyPressEvent = self.sceneKey
        self.view = QtGui.QGraphicsView(self.scene)
        self.pixmap_item = QtGui.QGraphicsPixmapItem(None, self.scene)      
        self.pixmap_item.mousePressEvent = self.pixelSelect
        pen = QtGui.QPen(QtCore.Qt.red)
        brush = QtGui.QBrush(QtCore.Qt.red)
        self.centerMarker = self.scene.addEllipse(daq_utils.screenPixCenterX-3,daq_utils.screenPixCenterY-3,6, 6, pen,brush)      
        self.click_positions = []
        self.vectorStartFlag = 0
#        self.vectorPointsList = []
        vBoxVidLayout.addWidget(self.view)
        hBoxSampleOrientationLayout = QtGui.QHBoxLayout()
        omegaLabel = QtGui.QLabel("Omega")
        omegaRBLabel = QtGui.QLabel("Readback:")
#        self.sampleOmegaRBVLedit = QtEpicsPVEntry(daq_utils.gonioPvPrefix+"Omega.RBV",self,0,"real") #type ignored for now, no validator yet
        self.sampleOmegaRBVLedit = QtEpicsPVLabel(daq_utils.gonioPvPrefix+"Omega.VAL",self,0) #this works better for remote!
#        self.sampleOmegaRBVLedit = QtEpicsMotorLabel(daq_utils.gonioPvPrefix+"Omega",self,70) #type ignored for now, no validator yet
        omegaSPLabel = QtGui.QLabel("SetPoint:")
#        self.sampleOmegaMoveLedit = QtEpicsPVEntry(daq_utils.gonioPvPrefix+"Omega.VAL",self,70,"real")
        self.sampleOmegaMoveLedit = QtEpicsPVEntry(daq_utils.gonioPvPrefix+"Omega.VAL",self,70,2)
        moveOmegaButton = QtGui.QPushButton("Move")
        moveOmegaButton.clicked.connect(self.moveOmegaCB)
        omega90Button = QtGui.QPushButton("+90")
        omega90Button.clicked.connect(self.omega90CB)
        omegaMinus90Button = QtGui.QPushButton("-90")
        omegaMinus90Button.clicked.connect(self.omegaMinus90CB)
        hBoxSampleOrientationLayout.addWidget(omegaLabel)
        hBoxSampleOrientationLayout.addWidget(omegaRBLabel)
        hBoxSampleOrientationLayout.addWidget(self.sampleOmegaRBVLedit.getEntry())
        hBoxSampleOrientationLayout.addWidget(omegaSPLabel)
        hBoxSampleOrientationLayout.addWidget(self.sampleOmegaMoveLedit.getEntry())
        hBoxSampleOrientationLayout.addWidget(moveOmegaButton)
        spacerItem = QtGui.QSpacerItem(50, 1, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        hBoxSampleOrientationLayout.addItem(spacerItem)
        hBoxSampleOrientationLayout.addWidget(omega90Button)
        hBoxSampleOrientationLayout.addWidget(omegaMinus90Button)
        hBoxSampleOrientationLayout.addStretch(1)
        hBoxVidControlLayout = QtGui.QHBoxLayout()
#        lightLevelLabel = QtGui.QLabel("Sample Illumination:")
#        sampleBrighterButton = QtGui.QPushButton("+")
#        sampleBrighterButton.clicked.connect(self.lightUpCB)
#        sampleDimmerButton = QtGui.QPushButton("-")
#        sampleDimmerButton.clicked.connect(self.lightDimCB)
        magLevelLabel = QtGui.QLabel("Video Source:")
        self.cameraRadioGroup=QtGui.QButtonGroup()
        self.lowMagLevelRadio = QtGui.QRadioButton("LowMag")
        self.lowMagLevelRadio.setChecked(True)
        self.lowMagLevelRadio.toggled.connect(self.vidSourceToggledCB)
        self.cameraRadioGroup.addButton(self.lowMagLevelRadio)
        self.highMagLevelRadio = QtGui.QRadioButton("HighMag")
        self.highMagLevelRadio.setChecked(False)
        self.cameraRadioGroup.addButton(self.highMagLevelRadio)
        self.highMagLevelRadio.toggled.connect(self.vidSourceToggledCB)
        self.digiZoomCheckBox = QCheckBox("Zoom")
        self.digiZoomCheckBox.setEnabled(False)
        self.digiZoomCheckBox.stateChanged.connect(self.changeZoomCB)
        snapshotButton = QtGui.QPushButton("Snapshot")
        snapshotButton.clicked.connect(self.saveVidSnapshotButtonCB)
#        zoomInButton = QtGui.QPushButton("+")
#        zoomInButton.clicked.connect(self.zoomInCB)
#        zoomOutButton = QtGui.QPushButton("-")
#        zoomOutButton.clicked.connect(self.zoomOutCB)
#        zoomResetButton = QtGui.QPushButton("Zoom Reset")
#        zoomResetButton.clicked.connect(self.zoomResetCB)
        hBoxVidControlLayout.addWidget(magLevelLabel)
        hBoxVidControlLayout.addWidget(self.lowMagLevelRadio)
        hBoxVidControlLayout.addWidget(self.highMagLevelRadio)
        hBoxVidControlLayout.addWidget(self.digiZoomCheckBox)
        hBoxVidControlLayout.addWidget(snapshotButton)
#        hBoxVidControlLayout.addWidget(lightLevelLabel)
#        hBoxVidControlLayout.addWidget(sampleBrighterButton)
#        hBoxVidControlLayout.addWidget(sampleDimmerButton)
        hBoxSampleAlignLayout = QtGui.QHBoxLayout()
        centerLoopButton = QtGui.QPushButton("Center\nLoop")
        centerLoopButton.clicked.connect(self.autoCenterLoopCB)
        rasterLoopButton = QtGui.QPushButton("Raster\nLoop")
        rasterLoopButton.clicked.connect(self.autoRasterLoopCB)
        loopShapeButton = QtGui.QPushButton("Draw\nRaster")
        loopShapeButton.clicked.connect(self.drawInteractiveRasterCB)
        runRastersButton = QtGui.QPushButton("Run\nRaster")
        runRastersButton.clicked.connect(self.runRastersCB)
        clearGraphicsButton = QtGui.QPushButton("Clear")
        clearGraphicsButton.clicked.connect(self.eraseCB)
        self.click3Button = QtGui.QPushButton("3-Click\nCenter")
        self.click3Button.clicked.connect(self.center3LoopCB)
        self.threeClickCount = 0
        saveCenteringButton = QtGui.QPushButton("Save\nCenter")
        saveCenteringButton.clicked.connect(self.saveCenterCB)
        selectAllCenteringButton = QtGui.QPushButton("Select All\nCenterings")
        selectAllCenteringButton.clicked.connect(self.selectAllCenterCB)
        hBoxSampleAlignLayout.addWidget(centerLoopButton)
        hBoxSampleAlignLayout.addWidget(rasterLoopButton)
        hBoxSampleAlignLayout.addWidget(loopShapeButton)
###        hBoxSampleAlignLayout.addWidget(runRastersButton) #maybe not a good idea to have multiple ways to run a raster. Force the collect button.
        hBoxSampleAlignLayout.addWidget(clearGraphicsButton)
        hBoxSampleAlignLayout.addWidget(self.click3Button)
        hBoxSampleAlignLayout.addWidget(saveCenteringButton)
        hBoxSampleAlignLayout.addWidget(selectAllCenteringButton)
        hBoxRadioLayout100= QtGui.QHBoxLayout()
        self.vidActionRadioGroup=QtGui.QButtonGroup()
        self.vidActionC2CRadio = QtGui.QRadioButton("C2C")
        self.vidActionC2CRadio.setChecked(True)
        self.vidActionC2CRadio.toggled.connect(self.vidActionToggledCB)
        self.vidActionRadioGroup.addButton(self.vidActionC2CRadio)
        self.vidActionRasterExploreRadio = QtGui.QRadioButton("RasterExplore")
        self.vidActionRasterExploreRadio.setChecked(False)
        self.vidActionRasterExploreRadio.toggled.connect(self.vidActionToggledCB)
        self.vidActionRadioGroup.addButton(self.vidActionRasterExploreRadio)
        self.vidActionRasterSelectRadio = QtGui.QRadioButton("RasterSelect")
        self.vidActionRasterSelectRadio.setChecked(False)
        self.vidActionRasterSelectRadio.toggled.connect(self.vidActionToggledCB)
        self.vidActionRadioGroup.addButton(self.vidActionRasterSelectRadio)
        self.vidActionRasterDefRadio = QtGui.QRadioButton("Define Raster Polygon")
        self.vidActionRasterDefRadio.setChecked(False)
        self.vidActionRasterDefRadio.toggled.connect(self.vidActionToggledCB)
        self.vidActionRadioGroup.addButton(self.vidActionRasterDefRadio)
#        self.vidActionRasterMoveRadio = QtGui.QRadioButton("RasterMove")
#        self.vidActionRasterMoveRadio.toggled.connect(self.vidActionToggledCB)
#        self.vidActionRadioGroup.addButton(self.vidActionRasterMoveRadio)
        hBoxRadioLayout100.addWidget(self.vidActionC2CRadio)
        hBoxRadioLayout100.addWidget(self.vidActionRasterExploreRadio)
        hBoxRadioLayout100.addWidget(self.vidActionRasterSelectRadio)
        hBoxRadioLayout100.addWidget(self.vidActionRasterDefRadio)
#        hBoxRadioLayout100.addWidget(self.vidActionPolyRasterDefRadio)
#######        hBoxRadioLayout100.addWidget(self.vidActionRasterMoveRadio)
##        vBoxDFlayout.addLayout(hBoxRadioLayout1)                   
        vBoxVidLayout.addLayout(hBoxSampleOrientationLayout)
        vBoxVidLayout.addLayout(hBoxVidControlLayout)
        vBoxVidLayout.addLayout(hBoxSampleAlignLayout)
        vBoxVidLayout.addLayout(hBoxRadioLayout100)
        self.VidFrame.setLayout(vBoxVidLayout)
        splitter11.addWidget(self.mainSetupFrame)
        self.colTabs= QtGui.QTabWidget()        
        self.energyFrame = QFrame()
        vBoxEScanFull = QtGui.QVBoxLayout()
        hBoxEScan = QtGui.QHBoxLayout()
        vBoxEScan = QtGui.QVBoxLayout()
#        self.periodicFrame = QFrame()
#        self.periodicFrame.setLineWidth(1)
        self.periodicTable = QPeriodicTable(self.energyFrame,butSize=20)
        vBoxEScan.addWidget(self.periodicTable)
#        vBoxEScan.addWidget(self.periodicFrame)
        EScanDataPathGB = DataLocInfo(self)
        vBoxEScan.addWidget(EScanDataPathGB)
        tempPlotButton = QtGui.QPushButton("Plot")        
        tempPlotButton.clicked.connect(self.plotChoochCB)
        vBoxEScan.addWidget(tempPlotButton)
        hBoxEScan.addLayout(vBoxEScan)
        verticalLine = QFrame()
        verticalLine.setFrameStyle(QFrame.VLine)
#        verticalLine.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.EScanGraph = QtBlissGraph(self.energyFrame)
        hBoxEScan.addWidget(verticalLine)
        hBoxEScan.addWidget(self.EScanGraph)
        vBoxEScanFull.addLayout(hBoxEScan)
        self.choochGraph = QtBlissGraph(self.energyFrame)
        vBoxEScanFull.addWidget(self.choochGraph)
#        vBoxEScan.addWidget(self.graph)
        self.energyFrame.setLayout(vBoxEScanFull)
#        self.colTabs.addTab(self.VidFrame,"Sample Control")
        splitter11.addWidget(self.VidFrame)
        self.colTabs.addTab(splitter11,"Sample Control")
        self.colTabs.addTab(self.energyFrame,"Energy Scan")
#        splitter11.addWidget(self.colTabs)
        splitter1.addWidget(self.colTabs)
###        splitter1.addWidget(splitter11)
#        splitterSizes = [300,300,300]
#        splitter1.setSizes(splitterSizes)
        vBoxlayout.addWidget(splitter1)
        self.lastFileLabel2 = QtGui.QLabel('Last File:')
        self.lastFileLabel2.setFixedWidth(70)
        self.lastFileRBV2 = QtEpicsPVLabel("XF:AMXFMX:det1:FullFileName_RBV",self,0)
        fileHBoxLayout = QtGui.QHBoxLayout()
        self.statusLabel = QtEpicsPVLabel(daq_utils.beamline+"_comm:program_state",self,300,highlight_on_change=False)
        fileHBoxLayout.addWidget(self.statusLabel.getEntry())
        fileHBoxLayout.addWidget(self.lastFileLabel2)
        fileHBoxLayout.addWidget(self.lastFileRBV2.getEntry())
        vBoxlayout.addLayout(fileHBoxLayout)
        sampleTab.setLayout(vBoxlayout)   
#        self.dewarTree.refreshTreeDewarView()
        self.XRFTab = QtGui.QFrame()        
        XRFhBox = QtGui.QHBoxLayout()
        self.mcafit = McaAdvancedFit(self.XRFTab)
#        self.mcafit = QFrame() #temp for printer issue!
        XRFhBox.addWidget(self.mcafit)
        self.XRFTab.setLayout(XRFhBox)
        self.tabs.addTab(sampleTab,"Collect")
        self.tabs.addTab(self.XRFTab,"XRF Spectrum")


    def rasterGrainToggledCB(self,identifier):
      if (identifier == "Coarse"):
        if (self.rasterGrainCoarseRadio.isChecked()):
          cellSize = 30
          self.rasterStepEdit.setText(str(cellSize))
          self.beamWidth_ledit.setText(str(cellSize))
      elif (identifier == "Fine"):
        if (self.rasterGrainFineRadio.isChecked()):
          cellSize = 10
          self.rasterStepEdit.setText(str(cellSize))
          self.beamWidth_ledit.setText(str(cellSize))
      else:
        pass



    def vidActionToggledCB(self):
      if (len(self.rasterList) > 0):
   
#        if (self.vidActionRasterMoveRadio.isChecked()):
#          for i in xrange(len(self.rasterList)):
#            self.rasterList[i]["graphicsItem"].setFlag(QtGui.QGraphicsItem.ItemIsMovable, True)
        if (self.vidActionRasterSelectRadio.isChecked()):
          for i in xrange(len(self.rasterList)):
            if (self.rasterList[i] != None):
              self.rasterList[i]["graphicsItem"].setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)            
        else:
          for i in xrange(len(self.rasterList)):
            if (self.rasterList[i] != None):
              self.rasterList[i]["graphicsItem"].setFlag(QtGui.QGraphicsItem.ItemIsMovable, False)
              self.rasterList[i]["graphicsItem"].setFlag(QtGui.QGraphicsItem.ItemIsSelectable, False)            
      if (self.vidActionRasterDefRadio.isChecked()):
        self.click_positions = []
        self.protoComboBox.setCurrentIndex(self.protoComboBox.findText(str("raster")))
        self.showProtParams()




    def adjustGraphics4ZoomChange(self,fov):
      if (self.rasterList != []):
        saveRasterList = self.rasterList
        self.eraseDisplayCB()
#        for i in xrange(len(self.rasterDefList)): #rasterdef b/c the erase got rid of raster graphics.
        for i in xrange(len(saveRasterList)):
          if (saveRasterList[i] == None): 
            self.rasterList.append(None)
          else:
            rasterXPixels = float(saveRasterList[i]["graphicsItem"].x())
            rasterYPixels = float(saveRasterList[i]["graphicsItem"].y())
            self.rasterXmicrons = rasterXPixels * (fov["x"]/daq_utils.screenPixX)
            self.rasterYmicrons = rasterYPixels * (fov["y"]/daq_utils.screenPixY)
#            print saveRasterList[i]
            self.drawPolyRaster(db_lib.getRequest(saveRasterList[i]["request_id"]))

#            self.drawPolyRaster(self.rasterDefList[i])
            self.rasterList[i]["graphicsItem"].setPos(self.screenXmicrons2pixels(self.rasterXmicrons),self.screenYmicrons2pixels(self.rasterYmicrons))
      if (self.vectorStart != None):
        self.processSampMove(self.sampx_pv.get(),"x")
        self.processSampMove(self.sampy_pv.get(),"y")
        self.processSampMove(self.sampz_pv.get(),"z")



    def vidSourceToggledCB(self):
      fov = {}
      if (self.lowMagLevelRadio.isChecked()):
        self.capture = self.captureFull
        self.nocapture = self.captureZoom
        self.digiZoomCheckBox.setEnabled(False)
        fov["x"] = daq_utils.lowMagFOVx
        fov["y"] = daq_utils.lowMagFOVy
      else:
        self.capture = self.captureZoom
        self.nocapture = self.captureFull
        self.digiZoomCheckBox.setEnabled(True)
        if (self.camZoom_pv.get() == "ROI2"):
          fov["x"] = daq_utils.highMagFOVx/2.0
          fov["y"] = daq_utils.highMagFOVy/2.0
        else:
          fov["x"] = daq_utils.highMagFOVx
          fov["y"] = daq_utils.highMagFOVy
      self.adjustGraphics4ZoomChange(fov)


    def saveVidSnapshotButtonCB(self): 
      comment,ok = snapCommentDialog.getComment()
      if (ok):
        self.saveVidSnapshotCB(comment)


    def saveVidSnapshotCB(self,comment=""):
      totalRect = QtCore.QRectF(self.view.frameRect())
      width = 646
      height = 482
      targetrect = QRectF(0, 0, width, height)
      sourcerect = QRectF(0, 0, width, height)
#    view.render(painter, targetrect, sourcerect)
#      pix = QtGui.QPixmap(totalRect.width(), totalRect.height())
      pix = QtGui.QPixmap(width, height)
      painter = QtGui.QPainter(pix)
#      self.scene.render(painter, totalRect)
      self.scene.render(painter, targetrect,sourcerect)
      now = time.time()
      imagePath = os.getcwd()+"/snapshots/capture"+str(int(now))+".jpg"
      pix.save(imagePath, "JPG")
      lsdcOlog.toOlog(imagePath,comment,self.omegaRBV_pv)
      del painter

    def changeZoomCB(self, state):
      fov = {}      
      if state == QtCore.Qt.Checked:
        fov["x"] = daq_utils.highMagFOVx
        fov["y"] = daq_utils.highMagFOVy
        if (self.camZoom_pv.get() != "ROI1"):
          self.camZoom_pv.put("ROI1")
      else:
        fov["x"] = daq_utils.highMagFOVx/2.0
        fov["y"] = daq_utils.highMagFOVy/2.0
        if (self.camZoom_pv.get() != "ROI2"):
          self.camZoom_pv.put("ROI2")
      self.adjustGraphics4ZoomChange(fov)


    def calculateNewYCoordPosOld(self,startYX,startYY):
      startY_pixels = 0
      xMotRBV = self.motPos["x"]
      deltaYX = startYX-xMotRBV
      yMotRBV = self.motPos["y"]
      deltaYY = startYY-yMotRBV
      omegaRad = math.radians(self.motPos["omega"])
      newYX = 0-((float(startY_pixels-(self.screenYmicrons2pixels(deltaYX))))*math.sin(omegaRad))
      newYY = (float(startY_pixels-(self.screenYmicrons2pixels(deltaYY))))*math.cos(omegaRad)
      newY = newYX + newYY
      return newY


    def calculateNewYCoordPos(self,startYX,startYY):
      startY_pixels = 0
      xMotRBV = self.motPos["x"]
      deltaYX = startYX-xMotRBV
      yMotRBV = self.motPos["y"]
      deltaYY = startYY-yMotRBV
      omegaRad = math.radians(self.motPos["omega"])
      newYY = 0-((float(startY_pixels-(self.screenYmicrons2pixels(deltaYY))))*math.sin(omegaRad))
      newYX = (float(startY_pixels-(self.screenYmicrons2pixels(deltaYX))))*math.cos(omegaRad)
      newY = newYX + newYY
      return newY


    def processZoomLevelChange(self,pvVal,userParam):
      if (str(pvVal) == "ROI1"):
        if not (self.digiZoomCheckBox.isChecked()):
           self.digiZoomCheckBox.setChecked(True)
      else:
        if (self.digiZoomCheckBox.isChecked()):
           self.digiZoomCheckBox.setChecked(False)
        

    def processSampMove(self,posRBV,motID):
#      print "new " + motID + " pos=" + str(posRBV)
      self.motPos[motID] = posRBV
      if (len(self.centeringMarksList)>0):
        for i in xrange(len(self.centeringMarksList)):
          if (motID == "z"):
            startX = self.centeringMarksList[i]["sampCoords"]["z"]
            startX_pixels = 0
            delta = startX-posRBV
            newX = float(startX_pixels-(self.screenXmicrons2pixels(delta)))
            self.centeringMarksList[i]["graphicsItem"].setPos(newX,self.centeringMarksList[i]["graphicsItem"].y())
          if (motID == "y" or motID == "x" or motID == "omega"):
            startYY = self.centeringMarksList[i]["sampCoords"]["y"]
            startYX = self.centeringMarksList[i]["sampCoords"]["x"]
            newY = self.calculateNewYCoordPos(startYX,startYY)
            self.centeringMarksList[i]["graphicsItem"].setPos(self.centeringMarksList[i]["graphicsItem"].x(),newY)
      if (len(self.rasterList)>0):
        for i in xrange(len(self.rasterList)):
          if (self.rasterList[i] != None):
            if (motID == "z"):
              startX = self.rasterList[i]["coords"]["z"]
              startX_pixels = 0
              delta = startX-posRBV
              newX = float(startX_pixels-(self.screenXmicrons2pixels(delta)))
              self.rasterList[i]["graphicsItem"].setPos(newX,self.rasterList[i]["graphicsItem"].y())
            if (motID == "y" or motID == "x"):
              startYY = self.rasterList[i]["coords"]["y"]
              startYX = self.rasterList[i]["coords"]["x"]
              newY = self.calculateNewYCoordPos(startYX,startYY)
              self.rasterList[i]["graphicsItem"].setPos(self.rasterList[i]["graphicsItem"].x(),newY)
      if (self.vectorStart != None):
        if (motID == "omega"):
          startYY = self.vectorStart["coords"]["y"]
          startYX = self.vectorStart["coords"]["x"]
          newY = self.calculateNewYCoordPos(startYX,startYY)
          self.vectorStart["graphicsitem"].setPos(self.vectorStart["graphicsitem"].x(),newY)
          if (self.vectorEnd != None):
            startYX = self.vectorEnd["coords"]["x"]
            startYY = self.vectorEnd["coords"]["y"]
            newY = self.calculateNewYCoordPos(startYX,startYY)
            self.vectorEnd["graphicsitem"].setPos(self.vectorEnd["graphicsitem"].x(),newY)
        if (motID == "z"):
          startX = self.vectorStart["coords"]["z"]
          startX_pixels = 0
          delta = startX-posRBV
          newX = float(startX_pixels-(self.screenXmicrons2pixels(delta)))
          self.vectorStart["graphicsitem"].setPos(newX,self.vectorStart["graphicsitem"].y())
          if (self.vectorEnd != None):
            startX = self.vectorEnd["coords"]["z"]
            startX_pixels = 0
            delta = startX-posRBV
            newX = float(startX_pixels-(self.screenXmicrons2pixels(delta)))
            self.vectorEnd["graphicsitem"].setPos(newX,self.vectorEnd["graphicsitem"].y())
        if (motID == "y" or motID == "x"):
          startYX = self.vectorStart["coords"]["x"]
          startYY = self.vectorStart["coords"]["y"]
          newY = self.calculateNewYCoordPos(startYX,startYY)
          self.vectorStart["graphicsitem"].setPos(self.vectorStart["graphicsitem"].x(),newY)
          if (self.vectorEnd != None):
            startYX = self.vectorEnd["coords"]["x"]
            startYY = self.vectorEnd["coords"]["y"]
            newY = self.calculateNewYCoordPos(startYX,startYY)
            self.vectorEnd["graphicsitem"].setPos(self.vectorEnd["graphicsitem"].x(),newY)
        if (self.vectorEnd != None):
            self.vecLine.setLine(daq_utils.screenPixCenterX+self.vectorStart["graphicsitem"].x(),daq_utils.screenPixCenterY+self.vectorStart["graphicsitem"].y(),daq_utils.screenPixCenterX+self.vectorEnd["graphicsitem"].x(),daq_utils.screenPixCenterY+self.vectorEnd["graphicsitem"].y())


    def plotChoochCB(self):
      self.send_to_server("runChooch()")


    def displayXrecRaster(self,xrecRasterFlag):
      self.xrecRasterFlag_pv.put(0)
      if (xrecRasterFlag==100):
        for i in xrange(len(self.rasterList)):
          if (self.rasterList[i] != None):
            self.scene.removeItem(self.rasterList[i]["graphicsItem"])
      else:
        rasterReq = db_lib.getRequest(xrecRasterFlag)
        rasterDef = rasterReq["request_obj"]["rasterDef"]
        if (rasterDef["status"] == 1):
          self.drawPolyRaster(rasterReq)
        elif (rasterDef["status"] == 2):        
          self.fillPolyRaster(rasterReq)
          self.selectedSampleID = rasterReq["sample_id"]
          db_lib.deleteRequest(rasterReq)
          self.treeChanged_pv.put(1) #not sure about this
        else:
          pass


    def processMountedPin(self,mountedPinPos):
      print "in callback mounted pin = " + str(mountedPinPos)
      self.treeChanged_pv.put(1)


    def processChoochResult(self,choochResultFlag):
      eScanOutFile = open("/h/skinner/proto_data4/choochData1.spec","r")
      graph_x = []
      graph_y = []
      for outLine in eScanOutFile.readlines():
        tokens = string.split(outLine)
        graph_x.append(float(tokens[0]))
        graph_y.append(float(tokens[1]))
      eScanOutFile.close()
      self.EScanGraph.setTitle("Chooch PLot")
      self.EScanGraph.newcurve("whatever", graph_x, graph_y)
      self.EScanGraph.replot()

      choochOutFile = open("/h/skinner/proto_data4/choochData1.efs","r")
      chooch_graph_x = []
      chooch_graph_y1 = []
      chooch_graph_y2 = []
      for outLine in choochOutFile.readlines():
        tokens = string.split(outLine)
        chooch_graph_x.append(float(tokens[0]))
        chooch_graph_y1.append(float(tokens[1]))
        chooch_graph_y2.append(float(tokens[2]))
      choochOutFile.close()
      self.choochGraph.setTitle("Chooch PLot")
      self.choochGraph.newcurve("spline", chooch_graph_x, chooch_graph_y1)
      self.choochGraph.newcurve("fp", chooch_graph_x, chooch_graph_y2)
      self.choochGraph.replot()
      self.choochResultFlag_pv.put(0)


    def getMaxPriority(self):
      orderedRequests = db_lib.getOrderedRequestList()      
      priorityMax = 0
      for i in xrange(len(orderedRequests)):
        if (orderedRequests[i]["priority"] > priorityMax):
          priorityMax = orderedRequests[i]["priority"]
      return priorityMax

    def getMinPriority(self):
      orderedRequests = db_lib.getOrderedRequestList()      
      priorityMin = 10000000
      for i in xrange(len(orderedRequests)):
        if (orderedRequests[i]["priority"] < priorityMin):
          priorityMin = orderedRequests[i]["priority"]
      return priorityMin


    def showProtParams(self):
      protocol = str(self.protoComboBox.currentText())
      self.rasterParamsFrame.hide()
      self.vectorParamsFrame.hide()
      self.characterizeParamsFrame.hide()
      self.processingOptionsFrame.hide()

      if (protocol == "raster"):
        self.rasterParamsFrame.show()
#        self.vectorParamsFrame.hide()
#        self.characterizeParamsFrame.hide()
      elif (protocol == "screen"):
#        return #SHORT CIRCUIT #why would I short circuit this?
        self.osc_start_ledit.setText(str(daq_utils.getBeamlineConfigParam("screen_default_phist")))
        self.osc_end_ledit.setText(str(daq_utils.getBeamlineConfigParam("screen_default_phi_end")))
        self.osc_range_ledit.setText(str(daq_utils.getBeamlineConfigParam("screen_default_width")))
        self.exp_time_ledit.setText(str(daq_utils.getBeamlineConfigParam("screen_default_time")))
        self.energy_ledit.setText(str(daq_utils.getBeamlineConfigParam("screen_default_energy")))
        self.transmission_ledit.setText(str(daq_utils.getBeamlineConfigParam("screen_transmission_percent")))
        self.beamWidth_ledit.setText(str(daq_utils.getBeamlineConfigParam("screen_default_beamWidth")))
        self.beamHeight_ledit.setText(str(daq_utils.getBeamlineConfigParam("screen_default_beamHeight")))
        self.resolution_ledit.setText(str(daq_utils.getBeamlineConfigParam("screen_default_reso")))
      elif (protocol == "vector"):
        self.vectorParamsFrame.show()
      elif (protocol == "characterize"):
        self.characterizeParamsFrame.show()
      elif (protocol == "standard"):
        self.processingOptionsFrame.show()
      else:
        pass 



    def resoTextChanged(self,text):
      try:
        dist_s = "%.2f" % (daq_utils.distance_from_reso(daq_utils.det_radius,float(text),daq_utils.wave2energy(float(self.energy_ledit.text())),0))
      except ValueError:
        dist_s = "500.0"
      self.colResoCalcDistance_ledit.setText(dist_s)

    def energyTextChanged(self,text):
      dist_s = "%.2f" % (daq_utils.distance_from_reso(daq_utils.det_radius,float(self.resolution_ledit.text()),float(text),0))
#      dist_s = "%.2f" % (daq_utils.distance_from_reso(daq_utils.det_radius,float(self.resolution_ledit.text()),daq_utils.wave2energy(float(text)),0))
      self.colResoCalcDistance_ledit.setText(dist_s)

    def protoComboActivatedCB(self, text):
#      print "protocol = " + str(text)
      self.showProtParams()
      protocol = str(self.protoComboBox.currentText())
      if (protocol == "raster"):
        self.vidActionRasterDefRadio.setChecked(True)        


    def  popBaseDirectoryDialogCB(self):
      fname = QtGui.QFileDialog.getExistingDirectory(self, 'Choose Directory', '/home')
      self.dataPathGB.setBasePath_ledit(fname)


    def upPriorityCB(self):
      orderedRequests = db_lib.getOrderedRequestList()
      for i in xrange(len(orderedRequests)):
        if (orderedRequests[i]["sample_id"] == self.selectedSampleRequest["sample_id"]):
          if (i<2):
            self.topPriorityCB()
          else:
            self.selectedSampleRequest["priority"] = (orderedRequests[i-2]["priority"] + orderedRequests[i-1]["priority"])/2
            db_lib.updateRequest(self.selectedSampleRequest)     
##      self.parent.treeChanged_pv.put(1)
#      self.dewarTree.refreshTree()
            
      
    def downPriorityCB(self):
      orderedRequests = db_lib.getOrderedRequestList()
      for i in xrange(len(orderedRequests)):
        if (orderedRequests[i]["sample_id"] == self.selectedSampleRequest["sample_id"]):
          if ((len(orderedRequests)-i) < 3):
            self.bottomPriorityCB()
          else:
            self.selectedSampleRequest["priority"] = (orderedRequests[i+1]["priority"] + orderedRequests[i+2]["priority"])/2
            db_lib.updateRequest(self.selectedSampleRequest)     
#      self.dewarTree.refreshTree()
##      self.parent.treeChanged_pv.put(1)


    def topPriorityCB(self):
      priority = int(self.getMaxPriority())
      priority = priority+100
      self.selectedSampleRequest["priority"] = priority
      db_lib.updateRequest(self.selectedSampleRequest)     
      self.treeChanged_pv.put(1)
#      self.dewarTree.refreshTree()


    def bottomPriorityCB(self):
      priority = int(self.getMinPriority())
      priority = priority-100
      self.selectedSampleRequest["priority"] = priority
      db_lib.updateRequest(self.selectedSampleRequest)     
##      self.parent.treeChanged_pv.put(1)
#      self.dewarTree.refreshTree()
      

    def dewarViewToggledCB(self,identifier):
#      self.eraseCB()
      self.selectedSampleRequest = {}
#should probably clear textfields here too
      if (identifier == "dewarView"):
        if (self.dewarViewRadio.isChecked()):
          self.dewarTree.refreshTreeDewarView()
      else:
        if (self.priorityViewRadio.isChecked()):
          self.dewarTree.refreshTreePriorityView()

    def dewarViewToggleCheckCB(self):
      if (self.dewarViewRadio.isChecked()):
        self.dewarTree.refreshTreeDewarView()
      else:
        self.dewarTree.refreshTreePriorityView()

    def moveOmegaCB(self):
      comm_s = "mva(\"Omega\"," + str(self.sampleOmegaMoveLedit.getEntry().text()) + ")"
      self.send_to_server(comm_s)

    def omega90CB(self):
      self.send_to_server("mvr(\"Omega\",90)")

    def omegaMinus90CB(self):
      self.send_to_server("mvr(\"Omega\",-90)")

    def autoCenterLoopCB(self):
      print "auto center loop"
      self.send_to_server("loop_center_xrec()")
      
    def autoRasterLoopCB(self):
      self.selectedSampleID = self.selectedSampleRequest["sample_id"]
      comm_s = "autoRasterLoop(" + str(self.selectedSampleID) + ")"
      self.send_to_server(comm_s)
#      self.send_to_server("autoRasterLoop()")

    def runRastersCB(self):
      comm_s = "snakeRaster(" + str(self.selectedSampleRequest["request_id"]) + ")"
      self.send_to_server(comm_s)
      
    def drawInteractiveRasterCB(self): # any polygon for now, interactive or from xrec
      for i in xrange(len(self.polyPointItems)):
        self.scene.removeItem(self.polyPointItems[i])
      polyPointItems = []
      pen = QtGui.QPen(QtCore.Qt.red)
      brush = QtGui.QBrush(QtCore.Qt.red)
      points = []
      polyPoints = []      
      if (self.click_positions != []): #use the user clicks
        if (len(self.click_positions) == 2):
          polyPoints.append(self.click_positions[0])
          point = QtCore.QPointF(self.click_positions[0].x(),self.click_positions[1].y())
          polyPoints.append(point)
          polyPoints.append(self.click_positions[1])
          point = QtCore.QPointF(self.click_positions[1].x(),self.click_positions[0].y())
          polyPoints.append(point)
          self.rasterPoly = QtGui.QGraphicsPolygonItem(QtGui.QPolygonF(polyPoints))
        else:
          self.rasterPoly = QtGui.QGraphicsPolygonItem(QtGui.QPolygonF(self.click_positions))
###          for point in self.click_positions:
###            newLoopPoint = QtGui.QGraphicsEllipseItem(point.x(),point.y(),3,3)      
###            self.polyPointItems.append(newLoopPoint)
#            self.polyPointItems.append(self.scene.addEllipse(point.x(), point.y(), 2, 2, pen))
      else:
        return
      self.polyBoundingRect = self.rasterPoly.boundingRect()
#      self.polyBoundingRect = self.scene.addRect(self.rasterPoly.boundingRect(),penBlue) #really don't need this
      raster_w = int(self.polyBoundingRect.width())
      raster_h = int(self.polyBoundingRect.height())
      center_x = int(self.polyBoundingRect.center().x())
      center_y = int(self.polyBoundingRect.center().y())
      stepsize = self.screenXmicrons2pixels(float(self.rasterStepEdit.text()))
      self.click_positions = []
      self.definePolyRaster(raster_w,raster_h,stepsize,center_x,center_y)

      
    def center3LoopCB(self):
      print "3-click center loop"
      self.threeClickCount = 1
      self.click3Button.setStyleSheet("background-color: yellow")
      self.send_to_server("mva(\"Omega\",0)")
      

    def fillPolyRaster(self,rasterReq): #at this point I should have a drawn polyRaster
#      (rasterListIndex,rasterDef) = db_lib.getNextDisplayRaster()
      print "filling poly for " + str(rasterReq["request_id"])
      rasterResult = db_lib.getResultsforRequest(rasterReq["request_id"])[0]
      rasterDef = rasterReq["rasterDef"]
      rasterListIndex = 0
      for i in xrange(len(self.rasterList)):
        if (self.rasterList[i] != None):
          if (self.rasterList[i]["request_id"] == rasterReq["request_id"]):
            rasterListIndex = i
      currentRasterGroup = self.rasterList[rasterListIndex]["graphicsItem"]
#      print len(currentRasterGroup.childItems())
      self.currentRasterCellList = currentRasterGroup.childItems()
      cellResults = db_lib.getResultsforRequest(rasterReq["request_id"])[0]["resultObj"]["rasterCellResults"]['resultObj']["data"]["response"]
      numLines = len(cellResults)
      filename_array = ["" for i in xrange(numLines)]
      my_array = np.zeros(numLines)
      spotLineCounter = 0
      cellIndex=0
      rowStartIndex = 0
      for i in xrange(len(rasterDef["rowDefs"])):
        rowStartIndex = spotLineCounter
        numsteps = rasterDef["rowDefs"][i]["numsteps"]
        for j in xrange(numsteps):
          cellResult = cellResults[spotLineCounter]
          spotcount = cellResult["spot_count"]
          filename =  cellResult["image"]
          if (i%2 == 0): 
            cellIndex = spotLineCounter
          else:
            cellIndex = rowStartIndex + ((numsteps-1)-j)          
          my_array[cellIndex] = spotcount
          filename_array[cellIndex] = filename
          spotLineCounter+=1
#  plt.text(int_w+.6,int_h+.5, str(spotcount), size=10,ha="right", va="top", color='r')
      floor = np.amin(my_array)
      ceiling = np.amax(my_array)
      cellCounter = 0     
      for i in xrange(len(rasterDef["rowDefs"])):
        rowCellCount = 0
        for j in xrange(rasterDef["rowDefs"][i]["numsteps"]):
          spotcount = int(my_array[cellCounter])
          filenameArrayIndex = cellCounter
          cellFilename = filename_array[filenameArrayIndex]
          if (ceiling == 0):
            color_id = 255
          else:
            color_id = int(255-(255.0*(float(spotcount-floor)/float(ceiling-floor))))
          self.currentRasterCellList[cellCounter*2].setBrush(QtGui.QBrush(QtGui.QColor(color_id,color_id,color_id,127)))
          self.currentRasterCellList[cellCounter*2].setData(0,spotcount)
          self.currentRasterCellList[cellCounter*2].setData(1,cellFilename)
          cellCounter+=1
      self.saveVidSnapshotCB("Raster Result from sample " + str(rasterReq["file_prefix"]))
      

    def saveCenterCB(self):
      pen = QtGui.QPen(QtCore.Qt.magenta)
      brush = QtGui.QBrush(QtCore.Qt.magenta)
      markWidth = 10
      marker = self.scene.addEllipse(daq_utils.screenPixCenterX-(markWidth/2),daq_utils.screenPixCenterY-(markWidth/2),markWidth,markWidth,pen,brush)
      marker.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)            
      self.centeringMark = {"sampCoords":{"x":self.sampx_pv.get(),"y":self.sampy_pv.get(),"z":self.sampz_pv.get()},"graphicsItem":marker}
      self.centeringMarksList.append(self.centeringMark)
 

    def selectAllCenterCB(self):
      print "select all center"
      for i in xrange(len(self.centeringMarksList)):
        self.centeringMarksList[i]["graphicsItem"].setSelected(True)        


    def lightUpCB(self):
      print "brighter"

    def lightDimCB(self):
      print "dimmer"
      

    def zoomInCB(self): #notused
      print "zoom in"
      self.capture = self.captureZoom

      
    def zoomOutCB(self): #notused
      print "zoom out"
      self.capture = self.captureFull


    def zoomResetCB(self):
      print "zoom reset"

    def eraseCB(self):
      self.click_positions = []
      for i in xrange(len(self.centeringMarksList)):
        self.scene.removeItem(self.centeringMarksList[i]["graphicsItem"])        
      self.centeringMarksList = []
      for i in xrange(len(self.polyPointItems)):
        self.scene.removeItem(self.polyPointItems[i])
      self.polyPointItems = []
      if (self.rasterList != []):
        for i in xrange(len(self.rasterList)):
          if (self.rasterList[i] != None):
            self.scene.removeItem(self.rasterList[i]["graphicsItem"])
        self.rasterList = []
        self.rasterDefList = []
      self.clearVectorCB()
      if (self.rasterPoly != None):      
        self.scene.removeItem(self.rasterPoly)
      self.rasterPoly =  None


    def eraseDisplayCB(self): #use this for things like zoom change. This is not the same as getting rid of all rasters.
      if (self.rasterList != []):
        for i in xrange(len(self.rasterList)):
          if (self.rasterList[i] != None):
            self.scene.removeItem(self.rasterList[i]["graphicsItem"])
        self.rasterList = []
        return   #short circuit
#      if (self.vectorPointsList != []):      
#        for i in xrange(len(self.vectorPointsList)):
#          self.scene.removeItem(self.vectorPointsList[i])
#        self.vectorPointsList = []
#      if (self.polyPointItems != []):      
      if (self.rasterPoly != None):      
        self.scene.removeItem(self.rasterPoly)
#        for i in xrange(len(self.polyPointItems)):
#          self.scene.removeItem(self.polyPointItems[i])
#        self.polyPointItems = []


    def getCurrentFOV(self):
      fov = {"x":0.0,"y":0.0}
      if (self.lowMagLevelRadio.isChecked()):
        fov["x"] = daq_utils.lowMagFOVx
        fov["y"] = daq_utils.lowMagFOVy
      else:
#        if (beamline_support.pvGet(self.camZoom_pv) == "ROI1"):
        if (self.digiZoomCheckBox.isChecked()):
          fov["x"] = daq_utils.highMagFOVx/2
          fov["y"] = daq_utils.highMagFOVy/2
        else:
          fov["x"] = daq_utils.highMagFOVx
          fov["y"] = daq_utils.highMagFOVy
      return fov


    def screenXPixels2microns(self,pixels):
      fov = self.getCurrentFOV()
      fovX = fov["x"]
      return float(pixels)*(fovX/daq_utils.screenPixX)

    def screenYPixels2microns(self,pixels):
      fov = self.getCurrentFOV()
      fovY = fov["y"]
      return float(pixels)*(fovY/daq_utils.screenPixY)

    def screenXmicrons2pixels(self,microns):
      fov = self.getCurrentFOV()
      fovX = fov["x"]
      return int(round(microns*(daq_utils.screenPixX/fovX)))

    def screenYmicrons2pixels(self,microns):
      fov = self.getCurrentFOV()
      fovY = fov["y"]
      return int(round(microns*(daq_utils.screenPixY/fovY)))


    def definePolyRaster(self,raster_w,raster_h,stepsize,point_x,point_y): #all come in as pixels
#raster status - 0=nothing done, 1=run, 2=displayed
      beamWidth = float(self.beamWidth_ledit.text())
      beamHeight = float(self.beamHeight_ledit.text())
      rasterDef = {"rasterType":"normal","beamWidth":beamWidth,"beamHeight":beamHeight,"status":0,"x":self.sampx_pv.get(),"y":self.sampy_pv.get(),"z":self.sampz_pv.get(),"omega":self.omega_pv.get(),"stepsize":float(self.rasterStepEdit.text()),"rowDefs":[]} #just storing step as microns, not using here
      numsteps_h = int(raster_w/stepsize) #raster_w = width,goes to numsteps horizonatl
      numsteps_v = int(raster_h/stepsize)
      if (numsteps_h%2 == 0):
        numsteps_h = numsteps_h + 1
      if (numsteps_v%2 == 0):
        numsteps_v = numsteps_v + 1
      point_offset_x = -(numsteps_h*stepsize)/2
      point_offset_y = -(numsteps_v*stepsize)/2
      newRasterCellList = []
      for i in xrange(numsteps_v):
        rowCellCount = 0
        for j in xrange(numsteps_h):
          newCellX = point_x+(j*stepsize)+point_offset_x
          newCellY = point_y+(i*stepsize)+point_offset_y
          if (self.rasterPoly.contains(QtCore.QPointF(newCellX+(stepsize/2.0),newCellY+(stepsize/2.0)))):
            if (rowCellCount == 0): #start of a new row
              rowStartX = newCellX
              rowStartY = newCellY
            rowCellCount = rowCellCount+1
        if (rowCellCount != 0): #no points in this row of the bounding rect are in the poly?
          newRowDef = {"start":{"x": self.screenXPixels2microns(rowStartX-daq_utils.screenPixCenterX),"y":self.screenYPixels2microns(rowStartY-daq_utils.screenPixCenterY)},"numsteps":rowCellCount}
          rasterDef["rowDefs"].append(newRowDef)
      self.addSampleRequestCB(rasterDef)
      return #short circuit


    def rasterIsDrawn(self,rasterReq):
      for i in xrange(len(self.rasterList)):
        if (self.rasterList[i] != None):
          if (self.rasterList[i]["request_id"] == rasterReq["request_id"]):
            return True
      return False
          


    def drawPolyRaster(self,rasterReq): #rasterDef in microns,offset from center, need to convert to pixels to draw
      rasterDef = rasterReq["request_obj"]["rasterDef"]
      beamSize = self.screenXmicrons2pixels(rasterDef["beamWidth"])
      stepsize = self.screenXmicrons2pixels(rasterDef["stepsize"])
      penBeam = QtGui.QPen(QtCore.Qt.green)
      if (stepsize>20):      
        penBeam = QtGui.QPen(QtCore.Qt.green)
      else:
        penBeam = QtGui.QPen(QtCore.Qt.red)
      pen = QtGui.QPen(QtCore.Qt.green)
      pen.setStyle(QtCore.Qt.NoPen)
      newRasterCellList = []
      for i in xrange(len(rasterDef["rowDefs"])):
        rowCellCount = 0
        for j in xrange(rasterDef["rowDefs"][i]["numsteps"]):
          newCellX = self.screenXmicrons2pixels(rasterDef["rowDefs"][i]["start"]["x"])+(j*stepsize)+daq_utils.screenPixCenterX
          newCellY = self.screenYmicrons2pixels(rasterDef["rowDefs"][i]["start"]["y"])+daq_utils.screenPixCenterY
#          print str(newCellX) + "  " + str(newCellY)
          if (rowCellCount == 0): #start of a new row
            rowStartX = newCellX
            rowStartY = newCellY
          newCell = rasterCell(newCellX,newCellY,stepsize, stepsize, self,self.scene)
          newRasterCellList.append(newCell)
          newCellBeam = QtGui.QGraphicsEllipseItem(newCellX+((stepsize-beamSize)/2.0),newCellY+((stepsize-beamSize)/2.0),beamSize, beamSize, None,self.scene)
          newRasterCellList.append(newCellBeam)
          newCell.setPen(pen)
          newCellBeam.setPen(penBeam)
          rowCellCount = rowCellCount+1 #really just for test of new row
      newItemGroup = rasterGroup(self)
      self.scene.addItem(newItemGroup)
      for i in xrange(len(newRasterCellList)):
        newItemGroup.addToGroup(newRasterCellList[i])
      newRasterGraphicsDesc = {"request_id":rasterReq["request_id"],"coords":{"x":self.sampx_pv.get(),"y":self.sampy_pv.get(),"z":self.sampz_pv.get()},"graphicsItem":newItemGroup}
      self.rasterList.append(newRasterGraphicsDesc)



#    def rasterItemMoveEvent(self, event): #crap?????
##      super(QtGui.QGraphicsRectItem, self).mouseMoveEvent(e)
#      print "caught move"
#      print self.rasterList[0]["graphicsItem"].pos()

#    def rasterItemReleaseEvent(self, event):
#      super(QtGui.QGraphicsRectItem, self).mouseReleaseEvent(e)
#      print "caught release"
#      print self.rasterList[0]["graphicsItem"].pos()


    def timerEvent(self, event):
      retval,self.readframe = self.capture.read()
      crapretval = self.nocapture.grab() #this is a very unfortunate fix for a memory leak.
      if self.readframe is None:
###        print 'Cam not found'
        return #maybe stop the timer also???
      self.currentFrame = cv2.cvtColor(self.readframe,cv2.COLOR_BGR2RGB)
      height,width=self.currentFrame.shape[:2]
      qimage=QtGui.QImage(self.currentFrame,width,height,3*width,QtGui.QImage.Format_RGB888)
#      print "got qimage" 
      frameWidth = qimage.width()
      frameHeight = qimage.height()
      pixmap_orig = QtGui.QPixmap.fromImage(qimage)
      if (frameWidth>1000): #for now, this can be more specific later if needed, but I really never want to scale here!!
        pixmap = pixmap_orig.scaled(frameWidth/2,qimage.height()/2)
        self.pixmap_item.setPixmap(pixmap)
      else:
#      print "got pixmap"
        self.pixmap_item.setPixmap(pixmap_orig)
#      print "done setting picture"


    def sceneKey(self, event):
        if (event.key() == QtCore.Qt.Key_Delete or event.key() == QtCore.Qt.Key_Backspace):
          for i in xrange(len(self.rasterList)):
            if (self.rasterList[i] != None):
              if (self.rasterList[i]["graphicsItem"].isSelected()):
                try:
                  sceneReq = db_lib.getRequest(self.rasterList[i]["request_id"])
                  self.selectedSampleID = sceneReq["sample_id"]
                  db_lib.deleteRequest(sceneReq)
                except AttributeError:
                  pass
                self.scene.removeItem(self.rasterList[i]["graphicsItem"])
                self.rasterList[i] = None
                self.treeChanged_pv.put(1)
          for i in xrange(len(self.centeringMarksList)):
            if (self.centeringMarksList[i] != None):
              if (self.centeringMarksList[i]["graphicsItem"].isSelected()):
                self.scene.removeItem(self.centeringMarksList[i]["graphicsItem"])        
                self.centeringMarksList[i] = None
          

    def pixelSelect(self, event):
        super(QtGui.QGraphicsPixmapItem, self.pixmap_item).mousePressEvent(event)
        x_click = float(event.pos().x())
        y_click = float(event.pos().y())
        penGreen = QtGui.QPen(QtCore.Qt.green)
        penRed = QtGui.QPen(QtCore.Qt.red)
        if (self.vidActionRasterDefRadio.isChecked()):
          self.click_positions.append(event.pos())
          self.polyPointItems.append(self.scene.addEllipse(x_click, y_click, 4, 4, penRed))
          return
        if (self.lowMagLevelRadio.isChecked()):
          maglevel = 0
        else:
          maglevel = 1
        if (self.threeClickCount > 0): #3-click centering
          self.threeClickCount = self.threeClickCount + 1
          comm_s = 'center_on_click(' + str(x_click) + "," + str(y_click) + "," + str(maglevel) + "," + '"screen",90)'
        else:
          comm_s = 'center_on_click(' + str(x_click) + "," + str(y_click) + "," + str(maglevel) + "," + '"screen",0)'
#          comm_s = "center_on_click(" + str(x_click) + "," + str(y_click) + "," + str(maglevel) + ",screen 0)"
        self.send_to_server(comm_s)
        if (self.threeClickCount == 4):
          self.threeClickCount = 0
          self.click3Button.setStyleSheet("background-color: None")          
        return 


    def editScreenParamsCB(self):
      self.screenDefaultsDialog = screenDefaultsDialog()
#       self.w.setGeometry(QRect(100, 100, 400, 200))
      self.screenDefaultsDialog.show()


    def deleteFromQueueCBNOTUSED(self):
#      print "add to queue"
      selmod = self.dewarTree.selectionModel()
      selection = selmod.selection()
      indexes = selection.indexes()
      i = 0
      item = self.dewarTree.model.itemFromIndex(indexes[i])
      db_lib.deleteRequest(self.selectedSampleRequest)
      self.dewarTree.refreshTree()
#      item.setCheckState(Qt.Checked)

    def editSelectedRequestsCB(self):
      selmod = self.dewarTree.selectionModel()
      selection = selmod.selection()
      indexes = selection.indexes()
      singleRequest = 1
      for i in xrange(len(indexes)):
        item = self.dewarTree.model.itemFromIndex(indexes[i])
        itemData = item.data().toInt()[0]
        if not (itemData < -100): #then it's a request
          self.selectedSampleRequest = db_lib.getRequest(itemData)
          self.editSampleRequestCB(singleRequest)
          singleRequest = 0
#            if (len(indexes)>1):
#            self.dataPathGB.setFilePrefix_ledit(str(self.selectedSampleRequest["file_prefix"]))
#          self.addSampleRequestCB(selectedSampleID=self.selectedSampleID)
#      self.refreshTree()
      self.treeChanged_pv.put(1)



    def editSampleRequestCB(self,singleRequest):
      colRequest=self.selectedSampleRequest
      reqObj = colRequest["request_obj"]
      reqObj["sweep_start"] = float(self.osc_start_ledit.text())
      reqObj["sweep_end"] = float(self.osc_end_ledit.text())
      reqObj["img_width"] = float(self.osc_range_ledit.text())
      reqObj["exposure_time"] = float(self.exp_time_ledit.text())
      reqObj["resolution"] = float(self.resolution_ledit.text())
      if (singleRequest == 1): # a touch kludgy, but I want to be able to edit parameters for multiple requests w/o screwing the data loc info
        reqObj["file_prefix"] = str(self.dataPathGB.prefix_ledit.text())
        reqObj["basePath"] = str(self.dataPathGB.base_path_ledit.text())
        reqObj["directory"] = str(self.dataPathGB.dataPath_ledit.text())
        reqObj["file_number_start"] = int(self.dataPathGB.file_numstart_ledit.text())
#      colRequest["gridStep"] = self.rasterStepEdit.text()
      reqObj["attenuation"] = float(self.transmission_ledit.text())
      reqObj["slit_width"] = float(self.beamWidth_ledit.text())
      reqObj["slit_height"] = float(self.beamHeight_ledit.text())
      wave = daq_utils.energy2wave(float(self.energy_ledit.text()))
      reqObj["wavelength"] = wave
      reqObj["fastDP"] =(self.fastDPCheckBox.isChecked() or self.fastEPCheckBox.isChecked())
      reqObj["fastEP"] =self.fastEPCheckBox.isChecked()
      reqObj["xia2"] =self.xia2CheckBox.isChecked()
      reqObj["protocol"] = str(self.protoComboBox.currentText())
      if (reqObj["protocol"] == "vector"):
        reqObj["vectorParams"]["fpp"] = int(self.vectorFPP_ledit.text())
      colRequest["request_obj"] = reqObj
      db_lib.updateRequest(colRequest)
#      self.eraseCB()
      self.treeChanged_pv.put(1)
#      self.dewarTree.refreshTree()



    def addRequestsToAllSelectedCB(self):
      selmod = self.dewarTree.selectionModel()
      selection = selmod.selection()
      indexes = selection.indexes()
      for i in xrange(len(indexes)):
        item = self.dewarTree.model.itemFromIndex(indexes[i])
        itemData = item.data().toInt()[0]
        if (itemData < -100): #then it's a sample
          self.selectedSampleID = (0-(itemData))-100
          self.selectedSampleRequest = daq_utils.createDefaultRequest(self.selectedSampleID) #7/21/15  - not sure what this does, b/c I don't pass it, ahhh probably the commented line for prefix
          if (len(indexes)>1):
            self.dataPathGB.setFilePrefix_ledit(str(self.selectedSampleRequest["request_obj"]["file_prefix"]))
            self.dataPathGB.setDataPath_ledit(str(self.selectedSampleRequest["request_obj"]["directory"]))
          self.addSampleRequestCB(selectedSampleID=self.selectedSampleID)
#      self.refreshTree()
      self.treeChanged_pv.put(1)


    def addSampleRequestCB(self,rasterDef=None,selectedSampleID=None):
#      self.selectedSampleID = self.selectedSampleRequest["sample_id"]

#      centeringOption = str(self.centeringComboBox.currentText())
#      if (centeringOption == "Interactive"):

# I don't like the code duplication, but one case is the mounted sample and selected centerings - so it's in a loop for multiple reqs, the other requires autocenter.
      if ((self.mountedPin_pv.get() == self.selectedSampleID) and (len(self.centeringMarksList) != 0)): 
        selectedCenteringFound = 0
        for i in xrange(len(self.centeringMarksList)):
           if (self.centeringMarksList[i]["graphicsItem"].isSelected()):
             selectedCenteringFound = 1
             colRequest = daq_utils.createDefaultRequest(self.selectedSampleID)
             reqObj = colRequest["request_obj"]
             reqObj["sweep_start"] = float(self.osc_start_ledit.text())
             reqObj["sweep_end"] = float(self.osc_end_ledit.text())
             reqObj["img_width"] = float(self.osc_range_ledit.text())
             reqObj["exposure_time"] = float(self.exp_time_ledit.text())
             reqObj["resolution"] = float(self.resolution_ledit.text())
             reqObj["file_prefix"] = str(self.dataPathGB.prefix_ledit.text()+"_C"+str(i+1))
             reqObj["directory"] = str(self.dataPathGB.dataPath_ledit.text())
             reqObj["basePath"] = str(self.dataPathGB.base_path_ledit.text())
             reqObj["file_number_start"] = int(self.dataPathGB.file_numstart_ledit.text())
#             colRequest["gridStep"] = self.rasterStepEdit.text()
             reqObj["attenuation"] = float(self.transmission_ledit.text())
             reqObj["slit_width"] = float(self.beamWidth_ledit.text())
             reqObj["slit_height"] = float(self.beamHeight_ledit.text())
             wave = daq_utils.energy2wave(float(self.energy_ledit.text()))
             reqObj["wavelength"] = wave
             reqObj["protocol"] = str(self.protoComboBox.currentText())
             reqObj["pos_x"] = float(self.centeringMarksList[i]["sampCoords"]["x"])
             reqObj["pos_y"] = float(self.centeringMarksList[i]["sampCoords"]["y"])
             reqObj["pos_z"] = float(self.centeringMarksList[i]["sampCoords"]["z"])
             reqObj["fastDP"] = (self.fastDPCheckBox.isChecked() or self.fastEPCheckBox.isChecked())
             reqObj["fastEP"] =self.fastEPCheckBox.isChecked()
             reqObj["xia2"] =self.xia2CheckBox.isChecked()
             if (reqObj["protocol"] == "characterize"):
               characterizationParams = {"aimed_completeness":float(self.characterizeCompletenessEdit.text()),"aimed_multiplicity":str(self.characterizeMultiplicityEdit.text()),"aimed_resolution":float(self.characterizeResoEdit.text()),"aimed_ISig":float(self.characterizeISIGEdit.text())}
               reqObj["characterizationParams"] = characterizationParams
             colRequest["request_obj"] = reqObj             
             newSampleRequest = db_lib.addRequesttoSample(self.selectedSampleID,reqObj["protocol"],reqObj,priority=0)
#             db_lib.updateRequest(colRequest)
#             time.sleep(1) #for now only because I use timestamp for sample creation!!!!!
        if (selectedCenteringFound == 0):
          message = QtGui.QErrorMessage(self)
          message.setModal(True)
          message.showMessage("You need to select a centering.")
      else: #autocenter
        colRequest=self.selectedSampleRequest
        reqObj = colRequest["request_obj"]
        reqObj["sweep_start"] = float(self.osc_start_ledit.text())
        reqObj["sweep_end"] = float(self.osc_end_ledit.text())
        reqObj["img_width"] = float(self.osc_range_ledit.text())
        reqObj["exposure_time"] = float(self.exp_time_ledit.text())
        reqObj["resolution"] = float(self.resolution_ledit.text())
        reqObj["directory"] = str(self.dataPathGB.dataPath_ledit.text())
        reqObj["basePath"] = str(self.dataPathGB.base_path_ledit.text())
        reqObj["file_prefix"] = str(self.dataPathGB.prefix_ledit.text())
        reqObj["file_number_start"] = int(self.dataPathGB.file_numstart_ledit.text())
        reqObj["fastDP"] = (self.fastDPCheckBox.isChecked() or self.fastEPCheckBox.isChecked())
        reqObj["fastEP"] =self.fastEPCheckBox.isChecked()
        reqObj["xia2"] =self.xia2CheckBox.isChecked()
#        colRequest["gridStep"] = self.rasterStepEdit.text()
        reqObj["attenuation"] = float(self.transmission_ledit.text())
        reqObj["slit_width"] = float(self.beamWidth_ledit.text())
        reqObj["slit_height"] = float(self.beamHeight_ledit.text())
        wave = daq_utils.energy2wave(float(self.energy_ledit.text()))
        reqObj["wavelength"] = wave
        reqObj["protocol"] = str(self.protoComboBox.currentText())
#        print colRequest
#        if (rasterDef != False):
        if (rasterDef != None):
          reqObj["rasterDef"] = rasterDef
          reqObj["gridStep"] = float(self.rasterStepEdit.text())
        if (reqObj["protocol"] == "characterize"):
          characterizationParams = {"aimed_completeness":float(self.characterizeCompletenessEdit.text()),"aimed_multiplicity":str(self.characterizeMultiplicityEdit.text()),"aimed_resolution":float(self.characterizeResoEdit.text()),"aimed_ISig":float(self.characterizeISIGEdit.text())}
          reqObj["characterizationParams"] = characterizationParams
        if (reqObj["protocol"] == "vector"):
          x_vec_end = self.vectorEnd["coords"]["x"]
          y_vec_end = self.vectorEnd["coords"]["y"]
          z_vec_end = self.vectorEnd["coords"]["z"]
          x_vec_start = self.vectorStart["coords"]["x"]
          y_vec_start = self.vectorStart["coords"]["y"]
          z_vec_start = self.vectorStart["coords"]["z"]
          x_vec = x_vec_end - x_vec_start
          y_vec = y_vec_end - y_vec_start
          z_vec = z_vec_end - z_vec_start
          trans_total = math.sqrt(x_vec**2 + y_vec**2 + z_vec**2)
          print trans_total
          framesPerPoint = int(self.vectorFPP_ledit.text())
          vectorParams={"vecStart":self.vectorStart["coords"],"vecEnd":self.vectorEnd["coords"],"x_vec":x_vec,"y_vec":y_vec,"z_vec":z_vec,"trans_total":trans_total,"fpp":framesPerPoint}
          reqObj["vectorParams"] = vectorParams
        colRequest["request_obj"] = reqObj
        newSampleRequest = db_lib.addRequesttoSample(self.selectedSampleID,reqObj["protocol"],reqObj,priority=0)
#        if (rasterDef != False):
        if (rasterDef != None):
          self.rasterDefList.append(newSampleRequest)
          self.drawPolyRaster(newSampleRequest)
#        db_lib.updateRequest(colRequest)
#      self.eraseCB()
      if (selectedSampleID == None): #this is a temp kludge to see if this is called from addAll
        self.treeChanged_pv.put(1)
#      self.dewarTree.refreshTree()
      

    def collectQueueCB(self):
      print "running queue"
      self.send_to_server("runDCQueue()")


    def removePuckCB(self):
      dewarPos, ok = DewarDialog.getDewarPos()
      ipos = int(dewarPos)
#      ipos = int(dewarPos)-1
#      print ipos
      if (ok):
        db_lib.removePuckFromDewar(ipos)
        self.treeChanged_pv.put(1)
#        self.dewarTree.refreshTree()

    def setVectorStartCB(self): #save sample x,y,z
      print "set vector start"        
      pen = QtGui.QPen(QtCore.Qt.blue)
      brush = QtGui.QBrush(QtCore.Qt.blue)
      vecStartMarker = self.scene.addEllipse(daq_utils.screenPixCenterX-5,daq_utils.screenPixCenterY-5,10, 10, pen,brush)      
      vectorStartcoords = {"x":self.sampx_pv.get(),"y":self.sampy_pv.get(),"z":self.sampz_pv.get()}
      self.vectorStart = {"coords":vectorStartcoords,"graphicsitem":vecStartMarker}
######      self.send_to_server("set_vector_start()")
#      print self.vectorStartcoords
#      self.vectorStartFlag = 1


    def setVectorEndCB(self): #save sample x,y,z
      print "set vector end"        
      pen = QtGui.QPen(QtCore.Qt.blue)
      brush = QtGui.QBrush(QtCore.Qt.blue)
      vecEndMarker = self.scene.addEllipse(daq_utils.screenPixCenterX-5,daq_utils.screenPixCenterY-5,10, 10, pen,brush)      
      vectorEndcoords = {"x":self.sampx_pv.get(),"y":self.sampy_pv.get(),"z":self.sampz_pv.get()}
      self.vectorEnd = {"coords":vectorEndcoords,"graphicsitem":vecEndMarker}
      self.vecLine = self.scene.addLine(daq_utils.screenPixCenterX+self.vectorStart["graphicsitem"].x(),daq_utils.screenPixCenterY+self.vectorStart["graphicsitem"].y(),daq_utils.screenPixCenterX+vecEndMarker.x(),daq_utils.screenPixCenterY+vecEndMarker.y(), pen)
      self.vecLine.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True)
#####      self.send_to_server("set_vector_end()")
#      self.vecLine = self.scene.addLine(self.vecStartMarker.scenePos().x(),self.vecStartMarker.scenePos().y(),self.vecEndMarker.scenePos().x(),self.vecEndMarker.scenePos().y(), pen)

    def clearVectorCB(self):
      if (self.vectorStart != None):
        self.scene.removeItem(self.vectorStart["graphicsitem"])
        self.vectorStart = None
      if (self.vectorEnd != None):
        self.scene.removeItem(self.vectorEnd["graphicsitem"])
        self.scene.removeItem(self.vecLine)
        self.vectorEnd = None

    def puckToDewarCB(self):
       puckName, ok = PuckDialog.getPuckName()
#       print puckName
       if (ok):
         dewarPos, ok = DewarDialog.getDewarPos()
#         print dewarPos
         ipos = int(dewarPos)
#         ipos = int(dewarPos)-1
         if (ok):
           db_lib.insertIntoContainer("primaryDewar",ipos,db_lib.getContainerIDbyName(puckName))
           self.treeChanged_pv.put(1)


    def stopRunCB(self):
      print "stopping collection"
      self.aux_send_to_server("stopDCQueue()")

    def mountSampleCB(self):
      print "mount selected sample"
      self.selectedSampleID = self.selectedSampleRequest["sample_id"]
#      (puckPosition,dewarPos,puckID,position) = db_lib.getAbsoluteDewarPosfromSampleID(self.selectedSampleID)
#      (puckPosition,samplePositionInContainer,containerID) = db_lib.getCoordsfromSampleID(requestedSampleList[i])
#      self.send_to_server("mountSample("+str(dewarPos)+")")
      self.send_to_server("mountSample("+str(self.selectedSampleID)+")")

    def unmountSampleCB(self):
      print "unmount sample"
      self.send_to_server("unmountSample()")

#not used yet
    def tree_changed(self, topLeft, bottomRight):
        sg = self.gen_mystructure_from_tree(self.dewarTree.model)
        print sg 
#        print "tree changed"


    def refreshCollectionParams(self,selectedSampleRequest):
      reqObj = self.selectedSampleRequest["request_obj"]
      self.protoComboBox.setCurrentIndex(self.protoComboBox.findText(str(reqObj["protocol"])))
      self.osc_start_ledit.setText(str(reqObj["sweep_start"]))
      self.osc_end_ledit.setText(str(reqObj["sweep_end"]))
      self.osc_range_ledit.setText(str(reqObj["img_width"]))
      self.exp_time_ledit.setText(str(reqObj["exposure_time"]))
      self.resolution_ledit.setText(str(reqObj["resolution"]))
      self.dataPathGB.setFileNumstart_ledit(str(reqObj["file_number_start"]))
      self.beamWidth_ledit.setText(str(reqObj["slit_width"]))
      self.beamHeight_ledit.setText(str(reqObj["slit_height"]))
      if (reqObj.has_key("fastDP")):
        self.fastDPCheckBox.setChecked((reqObj["fastDP"] or reqObj["fastEP"]))
      if (reqObj.has_key("fastEP")):
        self.fastEPCheckBox.setChecked(reqObj["fastEP"])
      if (reqObj.has_key("xia2")):
        self.xia2CheckBox.setChecked(reqObj["xia2"])
      energy_s = str(daq_utils.wave2energy(reqObj["wavelength"]))
#      energy_s = "%.4f" % (12.3985/selectedSampleRequest["wavelength"])
      self.energy_ledit.setText(str(energy_s))
      self.transmission_ledit.setText(str(reqObj["attenuation"]))
      dist_s = "%.2f" % (daq_utils.distance_from_reso(daq_utils.det_radius,reqObj["resolution"],1.1,0))
      self.colResoCalcDistance_ledit.setText(str(dist_s))
      self.dataPathGB.setFilePrefix_ledit(str(reqObj["file_prefix"]))
      self.dataPathGB.setBasePath_ledit(str(reqObj["basePath"]))
      self.dataPathGB.setDataPath_ledit(str(reqObj["directory"]))
      self.rasterStepEdit.setText(str(reqObj["gridStep"]))
      rasterStep = int(reqObj["gridStep"])
#      self.eraseCB()
      if (str(reqObj["protocol"])== "raster"):
        if (not self.rasterIsDrawn(selectedSampleRequest)):
          self.drawPolyRaster(selectedSampleRequest)
      elif (str(reqObj["protocol"])== "characterize"):
        characterizationParams = reqObj["characterizationParams"]
        self.characterizeCompletenessEdit.setText(str(characterizationParams["aimed_completeness"]))
        self.characterizeISIGEdit.setText(str(characterizationParams["aimed_ISig"]))
        self.characterizeResoEdit.setText(str(characterizationParams["aimed_resolution"]))
        self.characterizeMultiplicityEdit.setText(str(characterizationParams["aimed_multiplicity"]))
      else: #for now, erase the rasters if a non-raster is selected, need to rationalize later
#        self.eraseDisplayCB()
        pass
      self.showProtParams()



    def row_clicked(self,index): # do I really need "index" here? seems like I get it from selmod
      selmod = self.dewarTree.selectionModel()
      selection = selmod.selection()
      indexes = selection.indexes()
#      for i in xrange(len(indexes)):
      i = 0
      item = self.dewarTree.model.itemFromIndex(indexes[i])

#      sample_name = indexes[i].data().toString()
#      print sample_name
      parent = indexes[i].parent()
      puck_name = parent.data().toString()
#      print puck_name
#      sampleRequest = self.dewarTree.sampleRequests[item.data().toInt()[0]]
      itemData = item.data().toInt()[0]
#      print itemData
      self.SelectedItemData = itemData # an attempt to know what is selected and preserve it when refreshing the tree
#      sample_name = getSampleIdFromDewarPos(itemData)

      if (itemData == -99):
        print "nothing there"
        return
      elif (itemData == 0):
        print "I'm a puck"
        return
      elif (itemData< -100):
        self.selectedSampleID = (0-(itemData))-100 #a terrible kludge to differentiate samples from requests, compounded with low id # in mongo
        sample_name = db_lib.getSampleNamebyID(self.selectedSampleID) 
        print "sample in pos " + str(itemData) 
        if (self.osc_start_ledit.text() == ""):
          self.selectedSampleRequest = daq_utils.createDefaultRequest((0-(itemData))-100)
          self.refreshCollectionParams(self.selectedSampleRequest)
          if (self.vidActionRasterDefRadio.isChecked()):
#          self.selectedSampleRequest["protocol"] = "raster"
            self.protoComboBox.setCurrentIndex(self.protoComboBox.findText(str("raster")))
            self.showProtParams()
        elif (str(self.protoComboBox.currentText()) == "screen"):
          self.selectedSampleRequest = daq_utils.createDefaultRequest((0-(itemData))-100)
          self.refreshCollectionParams(self.selectedSampleRequest)

        else:
          self.selectedSampleRequest = daq_utils.createDefaultRequest((0-(itemData))-100)
          reqObj = self.selectedSampleRequest["request_obj"]
          self.dataPathGB.setFilePrefix_ledit(str(reqObj["file_prefix"]))          
          self.dataPathGB.setBasePath_ledit(reqObj["basePath"])
          self.dataPathGB.setDataPath_ledit(reqObj["directory"])
      else: #collection request
        self.selectedSampleRequest = db_lib.getRequest(itemData)
        reqObj = self.selectedSampleRequest["request_obj"]
        self.selectedSampleID = self.selectedSampleRequest["sample_id"]
#        if (self.selectedSampleRequest["protocol"] == "raster"): #might want this, problem is that it requires "rasterSelect", and maybe we don't want that.
#          for i in xrange(len(self.rasterList)):
#            if (self.rasterList[i] != None):
#              if (self.rasterList[i]["request_id"] == self.selectedSampleRequest["request_id"]):
#                self.rasterList[i]["graphicsItem"].setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)            
#                self.rasterList[i]["graphicsItem"].setSelected(True)
#              else:
#                self.rasterList[i]["graphicsItem"].setFlag(QtGui.QGraphicsItem.ItemIsSelectable, False)            
#                self.rasterList[i]["graphicsItem"].setSelected(False)

#####        self.eraseDisplayCB()
        self.refreshCollectionParams(self.selectedSampleRequest)

#      self.dewarTree.refreshTree()
##      numimages = (sampleRequest["sweep_end"] - sampleRequest["sweep_start"])/sampleRequest["img_width"]
##      self.dcFrame.num_images_ledit.setText(str(numimages))


    def processXrecRasterCB(self,value=None, char_value=None, **kw):
      xrecFlag = value
      if (xrecFlag > 0):
        self.emit(QtCore.SIGNAL("xrecRasterSignal"),xrecFlag)

    def processChoochResultsCB(self,value=None, char_value=None, **kw):
      choochFlag = value
      if (choochFlag > 0):
        self.emit(QtCore.SIGNAL("choochResultSignal"),choochFlag)

    def mountedPinChangedCB(self,value=None, char_value=None, **kw):
      mountedPinPos = value
      self.emit(QtCore.SIGNAL("mountedPinSignal"),mountedPinPos)

    def processSampMoveCB(self,value=None, char_value=None, **kw):
      posRBV = value
      motID = kw["motID"]
      self.emit(QtCore.SIGNAL("sampMoveSignal"),posRBV,motID)

    def processZoomLevelChangeCB(self,value=None, char_value=None, **kw):
      zoomVal = value
#      userFlag = user_args[0]
      userFlag = "" #I think I don't use this
      self.emit(QtCore.SIGNAL("zoomLevelSignal"),zoomVal,userFlag)

    def treeChangedCB(self,value=None, char_value=None, **kw):
      self.emit(QtCore.SIGNAL("refreshTreeSignal"))

    def serverMessageCB(self,value=None, char_value=None, **kw):
      serverMessageVar = char_value
      self.emit(QtCore.SIGNAL("serverMessageSignal"),serverMessageVar)

      
    def programStateCB(self, value=None, char_value=None, **kw):
      programStateVar = value
      self.emit(QtCore.SIGNAL("programStateSignal"),programStateVar)

        
    def initUI(self):               
        self.tabs= QtGui.QTabWidget()
        self.text_output = Console(parent=self)
        self.comm_pv = PV(daq_utils.beamline + "_comm:command_s")
        self.immediate_comm_pv = PV(daq_utils.beamline + "_comm:immediate_command_s")
        tab1= QtGui.QWidget()
        vBoxlayout1= QtGui.QVBoxLayout()
        splitter1 = QtGui.QSplitter(QtCore.Qt.Vertical,self)
        splitter1.addWidget(self.tabs)
        self.setCentralWidget(splitter1)
        splitter1.addWidget(self.text_output)
        splitterSizes = [600,100]
        splitter1.setSizes(splitterSizes)
        exitAction = QtGui.QAction(QtGui.QIcon('exit24.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)
        self.statusBar()
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)
        self.setGeometry(300, 300, 300, 970)
        self.setWindowTitle('Main window')    
        self.show()

    def initCallbacks(self):
      self.treeChanged_pv = PV(daq_utils.beamline + "_comm:live_q_change_flag")
      self.connect(self, QtCore.SIGNAL("refreshTreeSignal"),self.dewarTree.refreshTree)
      self.treeChanged_pv.add_callback(self.treeChangedCB)  
      self.mountedPin_pv = PV(daq_utils.beamline + "_comm:mounted_pin")
      self.connect(self, QtCore.SIGNAL("mountedPinSignal"),self.processMountedPin)
      self.mountedPin_pv.add_callback(self.mountedPinChangedCB)  
      self.choochResultFlag_pv = PV(daq_utils.beamline + "_comm:choochResultFlag")
      self.connect(self, QtCore.SIGNAL("choochResultSignal"),self.processChoochResult)
      self.choochResultFlag_pv.add_callback(self.processChoochResultsCB)  
      self.xrecRasterFlag_pv = PV(daq_utils.beamline + "_comm:xrecRasterFlag")
      self.xrecRasterFlag_pv.put(0)
      self.connect(self, QtCore.SIGNAL("xrecRasterSignal"),self.displayXrecRaster)
      self.xrecRasterFlag_pv.add_callback(self.processXrecRasterCB)  
      self.message_string_pv = PV(daq_utils.beamline + "_comm:message_string") 
      self.connect(self, QtCore.SIGNAL("serverMessageSignal"),self.printServerMessage)
      self.message_string_pv.add_callback(self.serverMessageCB)  
      self.program_state_pv = PV(daq_utils.beamline + "_comm:program_state") 
      self.connect(self, QtCore.SIGNAL("programStateSignal"),self.colorProgramState)
      self.program_state_pv.add_callback(self.programStateCB)  
      self.sampx_pv = PV(daq_utils.gonioPvPrefix+"X.VAL")
      self.connect(self, QtCore.SIGNAL("sampMoveSignal"),self.processSampMove)
      self.sampx_pv.add_callback(self.processSampMoveCB,motID="x")
      self.sampy_pv = PV(daq_utils.gonioPvPrefix+"Y.VAL")
      self.connect(self, QtCore.SIGNAL("sampMoveSignal"),self.processSampMove)
      self.sampy_pv.add_callback(self.processSampMoveCB,motID="y")
      self.sampz_pv = PV(daq_utils.gonioPvPrefix+"Z.VAL")
      self.connect(self, QtCore.SIGNAL("sampMoveSignal"),self.processSampMove)
      self.sampz_pv.add_callback(self.processSampMoveCB,motID="z")

      self.omega_pv = PV(daq_utils.gonioPvPrefix+"Omega.VAL")
      self.omegaRBV_pv = PV(daq_utils.gonioPvPrefix+"Omega.RBV")
      self.connect(self, QtCore.SIGNAL("sampMoveSignal"),self.processSampMove)
      self.omega_pv.add_callback(self.processSampMoveCB,motID="omega")

      self.camZoom_pv = PV("FAMX-cam1:MJPGZOOM:NDArrayPort")
      self.connect(self, QtCore.SIGNAL("zoomLevelSignal"),self.processZoomLevelChange)
      self.camZoom_pv.add_callback(self.processZoomLevelChangeCB)
        

    def printServerMessage(self,message_s):
      global program_starting

      if (program_starting):
        program_starting = 0
        return        
#      message_s = beamline_support.pvGet(self.message_string_pv)
      print message_s
      self.text_output.showMessage(message_s)
      self.text_output.scrollContentsBy(0,1000)

    def colorProgramState(self,programState_s):
#      programState_s = beamline_support.pvGet(self.program_state_pv)
      if (string.find(programState_s,"Ready") == -1):
        self.statusLabel.setColor("yellow")
      else:
        self.statusLabel.setColor("green")
#        self.statusLabel.setColor("None")
        self.text_output.newPrompt()

        
    def send_to_server(self,s):
#      if not (control_disabled):
      time.sleep(.01)
      self.comm_pv.put(s)

    def aux_send_to_server(self,s):
#      if not (control_disabled):
      time.sleep(.01)
      self.immediate_comm_pv.put(s)


def main():
    daq_utils.init_environment()    
    app = QtGui.QApplication(sys.argv)
    ex = controlMain()
    sys.exit(app.exec_())


if __name__ == '__main__':
    if '-pc' in sys.argv or '-p' in sys.argv:
        print 'cProfile not working yet :('
        #print 'starting cProfile profiler...'
        #import cProfile, pstats, io
        #pr = cProfile.Profile()
        #pr.enable()

    elif '-py' in sys.argv:
        print 'starting yappi profiler...'
        import yappi
        yappi.start(True)

    try:
        main()    

    finally:
        if '-pc' in sys.argv or '-p' in sys.argv:
            pass
            #pr.disable()
            #s = io.StringIO()
            #sortby = 'cumulative'
            #ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
            #ps.print_stats()  # dies here, expected unicode, got string, need unicode io stream?
            #print(s.getvalue())

        elif '-py' in sys.argv:
            # stop profiler and print results
            yappi.stop()
            yappi.get_func_stats().print_all()
            yappi.get_thread_stats().print_all()
            print 'memory usage: {0}'.format(yappi.get_mem_usage())
