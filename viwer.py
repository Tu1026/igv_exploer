#!/usr/bin/python3
# -*- coding: utf-8 -*-

from fileinput import filename
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt5 import QtCore
from PyQt5.QtGui import QImage, QPixmap, QPalette, QPainter
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5.QtWidgets import QLabel, QSizePolicy, QScrollArea, QMessageBox, QMainWindow, QMenu, QAction, \
    qApp, QFileDialog
import csv
import os 
import threading
import queue


# class ProcessThread(threading.Thread):
#     def __init__(self, in_queue, out_queue):
#         threading.Thread.__init__(self)
#         self.in_queue = in_queue
#         self.out_queue = out_queue

#     def run(self):
#         while True:
#             path = self.in_queue.get()
#             result = self.process(path)
#             self.out_queue.put(result)
#             self.in_queue.task_done()

#     def process(self, path):
#         pass
    
# class PrintThread(threading.Thread):
#     def __init__(self, queue):
#         threading.Thread.__init__(self)
#         self.queue = queue

#     def run(self):
#         while True:
#             result = self.queue.get()
#             self.printfiles(result)
#             self.queue.task_done()

class ImageThread(QThread):
    igvScreenShot = pyqtSignal(QPixmap)
    
    def __init__(self, path, parent=None):
        QThread.__init__(self, parent)
        self.path = path
            
    def run(self):
        image = QImage(self.path)
        pixmapImage = QPixmap.fromImage(image)
        self.igvScreenShot.emit(pixmapImage)


class WriteToFileThread(QThread):
    
    def __init__(self, action, file, data, parent=None):
        QThread.__init__(self, parent)
        self.action = action
        self.file = file
        self.data = data
            
    def run(self):
        if self.action == "Blacklist":
            csv.writer(self.file).writerow(self.data)
            self.file.flush()
        print("I got here")




class QImageViewer(QMainWindow):
    keyPressed = pyqtSignal(int)
    fileAction = pyqtSignal(str)
    def __init__(self, blacklist, checklist):
        super().__init__()
        self.counter = 0
        self.printer = QPrinter()
        self.scaleFactor = 0.0
        
        self.inputQueue = queue.Queue()
        self.
        
        self.imageLabel = QLabel()
        self.imageLabel.setBackgroundRole(QPalette.Base)
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)

        self.scrollArea = QScrollArea()
        self.scrollArea.setBackgroundRole(QPalette.Dark)
        self.scrollArea.setWidget(self.imageLabel)
        self.scrollArea.setVisible(False)

        self.setCentralWidget(self.scrollArea)
        self.createActions()
        self.createMenus()
        self.blacklist = blacklist
        # self.blacklist_writer = csv.writer(self.blacklist, delimiter="\t")
        self.checklist = checklist
        self.setWindowTitle("IGV Image Viewer - no folder selected yet")
        # self.resize(800, 600)
        self.showMaximized()
        

    # def open(self):
    #     options = QFileDialog.Options()
    #     # fileName = QFileDialog.getOpenFileName(self, "Open File", QDir.currentPath())
    #     fileName, _ = QFileDialog.getOpenFileName(self, 'QFileDialog.getOpenFileName()', '',
    #                                               'Images (*.png *.jpeg *.jpg *.bmp *.gif)', options=options)
    #     if fileName:
    #         image = QImage(fileName)
    #         if image.isNull():
    #             QMessageBox.information(self, "Image Viewer", "Cannot load %s." % fileName)
    #             return

    #         self.imageLabel.setPixmap(QPixmap.fromImage(image))
    #         self.scaleFactor = 1.0

    #         self.scrollArea.setVisible(True)
    #         self.printAct.setEnabled(True)
    #         self.fitToWindowAct.setEnabled(True)
    #         self.updateActions()

    #         if not self.fitToWindowAct.isChecked():
    #             self.imageLabel.adjustSize()
    
    def keyPressEvent(self, event):
        super(QImageViewer, self).keyPressEvent(event)
        self.keyPressed.emit(event.key()) 
        
    def on_key(self, key):
        # test for a specific key
        if key == QtCore.Qt.Key_B:
            self.counter -= 1
            self.openImage(os.path.join(self.folder, self.files[self.counter]))
        else:
            self.counter += 1
            if key == QtCore.Qt.Key_Q:
                print('Pressed Q')
                writeImageThread = WriteToFileThread("Blacklist", self.blacklist, ["123", "123", "123"])
                writeImageThread.start()
                self.openImage(os.path.join(self.folder, self.files[self.counter]))
            elif key == QtCore.Qt.Key_E:
                print("Pressed E")
                self.openImage(os.path.join(self.folder, self.files[self.counter]))
            elif key == QtCore.Qt.Key_W:
                print("Pressed W")
            
    def fileAction(self, action):
        if action == "Blacklist":
            # self.blacklist_writer.writerow(["123", "123", "123"])
            self.blacklist.write("123123")
            self.blacklist.flush()
        # elif action == "Checklist":
            
        # elif action == "Move Back"
            
    def loadImage(self, pixmap):
        self.imageLabel.setPixmap(pixmap)
        self.scaleFactor = 1.0

        self.scrollArea.setVisible(True)
        
        self.fitToWindowAct.setChecked(True)
        self.scrollArea.setWidgetResizable(True)
        self.updateActions()
        self.imageLabel.adjustSize()
    
    def openImage(self, fileName):
        imgTd = ImageThread(fileName, self)
        imgTd.igvScreenShot.connect(self.loadImage)
        imgTd.start()

                
    def select_folder(self):
        self.folder = QFileDialog.getExistingDirectory(self, 'Select folder of screenshots', options=QFileDialog.ShowDirsOnly)
        self.keyPressed.connect(self.on_key)
        self.files = [img for img in os.listdir(self.folder) if img.endswith((".png", ".jpeg", "jpg"))]
        print(os.path.join(self.folder, self.files[0]))
        self.openImage(os.path.join(self.folder, self.files[0]))
        self.setWindowTitle(f"IGV Image Viewer - {self.folder}")
        
    def select_tsv(self):
        options = QFileDialog.Options()
        self.tsv_path = QFileDialog.getOpenFileName(self, 'Select betastasis TSV', '',
                                  'TSV (*.tsv)', options=options)

    def zoomIn(self):
        self.scaleImage(1.25)

    def zoomOut(self):
        self.scaleImage(0.8)

    def normalSize(self):
        self.imageLabel.adjustSize()
        self.scaleFactor = 1.0

    def fitToWindow(self):
        fitToWindow = self.fitToWindowAct.isChecked()
        self.scrollArea.setWidgetResizable(fitToWindow)
        if not fitToWindow:
            self.normalSize()
        self.updateActions()

    def about(self):
        QMessageBox.about(self, "About Image Viewer",
                          "<p>The <b>Image Viewer</b> example shows how to combine "
                          "QLabel and QScrollArea to display an image. QLabel is "
                          "typically used for displaying text, but it can also display "
                          "an image. QScrollArea provides a scrolling view around "
                          "another widget. If the child widget exceeds the size of the "
                          "frame, QScrollArea automatically provides scroll bars.</p>"
                          "<p>The example demonstrates how QLabel's ability to scale "
                          "its contents (QLabel.scaledContents), and QScrollArea's "
                          "ability to automatically resize its contents "
                          "(QScrollArea.widgetResizable), can be used to implement "
                          "zooming and scaling features.</p>"
                          "<p>In addition the example shows how to use QPainter to "
                          "print an image.</p>")

    def createActions(self):
        self.openAct = QAction("&Select screenshot foler", self, shortcut="Ctrl+O", triggered=self.select_folder)
        self.select_tsv_act = QAction("&Select betastasis TSV", self, shortcut="Ctrl++", triggered=self.select_tsv)
        # self.printAct = QAction("&Print...", self, shortcut="Ctrl+P", enabled=False, triggered=self.print_)
        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q", triggered=self.close)
        # self.openImage = QAction("&TestIamge", self, shortcut="Ctrl+O", triggered=self.openImage)
        self.zoomInAct = QAction("Zoom &In (25%)", self, shortcut="Ctrl++", enabled=False, triggered=self.zoomIn)
        self.zoomOutAct = QAction("Zoom &Out (25%)", self, shortcut="Ctrl+-", enabled=False, triggered=self.zoomOut)
        self.normalSizeAct = QAction("&Normal Size", self, shortcut="Ctrl+S", enabled=False, triggered=self.normalSize)
        self.fitToWindowAct = QAction("&Fit to Window", self, enabled=False, checkable=True, shortcut="Ctrl+F",
                                      triggered=self.fitToWindow)
        self.aboutAct = QAction("&About", self, triggered=self.about)
        self.aboutQtAct = QAction("About &Qt", self, triggered=qApp.aboutQt)

    def createMenus(self):
        self.folderMenu = QMenu("&Folder", self)
        self.folderMenu.addAction(self.openAct)
        # self.folderMenu.addAction(self.printAct)
        self.folderMenu.addSeparator()
        self.folderMenu.addAction(self.exitAct)
        
        self.fileMenu = QMenu("&File", self)
        self.fileMenu.addAction(self.select_tsv_act)
        # self.fileMenu.addAction(self.openImage)
    
        
        self.viewMenu = QMenu("&View", self)
        self.viewMenu.addAction(self.zoomInAct)
        self.viewMenu.addAction(self.zoomOutAct)
        self.viewMenu.addAction(self.normalSizeAct)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.fitToWindowAct)
        


        self.helpMenu = QMenu("&Help", self)
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

        self.menuBar().addMenu(self.folderMenu)
        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.viewMenu)
        self.menuBar().addMenu(self.helpMenu)

    def updateActions(self):
        self.zoomInAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.zoomOutAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.normalSizeAct.setEnabled(not self.fitToWindowAct.isChecked())

    def scaleImage(self, factor):
        self.scaleFactor *= factor
        self.imageLabel.resize(self.scaleFactor * self.imageLabel.pixmap().size())

        self.adjustScrollBar(self.scrollArea.horizontalScrollBar(), factor)
        self.adjustScrollBar(self.scrollArea.verticalScrollBar(), factor)

        self.zoomInAct.setEnabled(self.scaleFactor < 3.0)
        self.zoomOutAct.setEnabled(self.scaleFactor > 0.333)

    def adjustScrollBar(self, scrollBar, factor):
        scrollBar.setValue(int(factor * scrollBar.value()
                               + ((factor - 1) * scrollBar.pageStep() / 2)))


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    with open("Blacklist.tsv", "w+") as blacklist, open("DoubleChecklist.tsv", "w+") as checklist: 
        pass
    
    with open("Blacklist.tsv", "r+") as blacklist, open("DoubleChecklist.tsv", "r+") as checklist: 
        app = QApplication(sys.argv)
        imageViewer = QImageViewer(blacklist, checklist)
        imageViewer.show()
        sys.exit(app.exec_())
    # TODO QScrollArea support mouse
    # base on https://github.com/baoboa/pyqt5/blob/master/examples/widgets/imageviewer.py
    #
    # if you need Two Image Synchronous Scrolling in the window by PyQt5 and Python 3
    # please visit https://gist.github.com/acbetter/e7d0c600fdc0865f4b0ee05a17b858f2