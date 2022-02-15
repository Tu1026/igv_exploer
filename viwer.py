#!/usr/bin/python3
# -*- coding: utf-8 -*-
import pandas as pd
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt5 import QtCore
from PyQt5.QtGui import QImage, QPixmap, QPalette, QPainter
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5.QtWidgets import QLabel, QSizePolicy, QScrollArea, QMessageBox, QMainWindow, QMenu, QAction, \
    qApp, QFileDialog
import os 
from pathlib import Path
import platform
from PyQt5 import QtGui
import sys

if platform.system():
    try:
        from ctypes import windll  # Only exists on Windows.
        myappid = 'mycompany.myproduct.subproduct.version'
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except ImportError:
        pass
working_dir = Path(__file__).parent


bundle_dir = os.path.dirname(sys.argv[0])


mutex = QtCore.QMutex()
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
    errorMessage = pyqtSignal(str, str)
    
    def __init__(self, action, dataName, parent=None):
        QThread.__init__(self, parent)
        self.action = action
        self.dataName = dataName
        self.chrom, self.pos, self.gene, self.patient, _ = self.dataName.split(".")

    
    def run(self):
        mutex.lock()
        betastasis_df = contextPerserver.betastasis_df
        row = betastasis_df[(betastasis_df["CHROM"] == "chr" + str(self.chrom)) & (
            (betastasis_df["POSITION"])==int(self.pos))&
            (betastasis_df["GENE"]==self.gene)]
        # print(f"This is row {row}")
        # print(f"This is chr chr{str(self.chrom)}")
        # print(f"Position: {self.pos}")
        # print(f"This is Gene {self.gene}")
        if not len(row):
            self.errorMessage.emit("Could not find related entry for the screenshot in the betastasis TSV",
                                "You might want to double check the betastasis TSV you downloaded, maybe you forgot to show silent and blacklisted genes? "
                                "This gene will be skipped for record keeping now")
        try:
            ref = row["REF"].iloc[0]
            alt = row["ALT"].iloc[0]
        except:
            self.errorMessage.emit("Could not find related entry for the screenshot in the betastasis TSV",
                                "You might want to double check the betastasis TSV you downloaded, maybe you forgot to show silent and blacklisted genes? "
                                "This gene will be skipped for record keeping now")
        if self.action == "Blacklisted":
            with open(os.path.join(contextPerserver.resultDir, contextPerserver.black_list_name), "a") as file:
                file.write(f"chr{self.chrom}\t{self.pos}\t{ref}\t{alt}\n")
                file.flush()
        elif self.action == "Needs Double Check":
            with open(os.path.join(contextPerserver.resultDir, contextPerserver.checklist_name), "a") as file:
                file.write(f"{self.dataName} needs double checking \n")
                file.flush()
        with open(os.path.join(contextPerserver.resultDir, contextPerserver.curatelist_name), "a") as file:
            file.write(f"chr{self.chrom}\t{self.pos}\t{ref}\t{alt}\t{self.gene}\t{self.action}\t{self.dataName}\n")
            file.flush()
        mutex.unlock()


class ReloadProgressThread(QThread):
    fileName = pyqtSignal(str)
    errorMessage = pyqtSignal(str, str)
    # def __init__(self, parent=None):
    #     QThread.__init__(self, parent)
    
    def peek_line(self, file):
        file.seek(0, os.SEEK_END)

        # This code means the following code skips the very last character in the file -
        # i.e. in the case the last line is null we delete the last line
        # and the penultimate one
        pos = file.tell() - 1

        # Read each character in the file one at a time from the penultimate
        # character going backwards, searching for a newline character
        # If we find a new line, exit the search
        while pos > 0 and file.read(1) != "\n":
            pos -= 1
            file.seek(pos, os.SEEK_SET)

        # So long as we're not at the start of the file, delete all the characters ahead
        # of this position
        # if pos > 0:
        #     file.seek(pos, os.SEEK_SET)
        line = file.readline()
        file.seek(pos)
        return line

    def run(self):
        mutex.lock()
        if os.getsize(os.path.join(contextPerserver.resultDir, contextPerserver.curatelist_name)):
            with open(os.path.join(contextPerserver.resultDir, contextPerserver.curatelist_name), "r+") as curateFile:
                last_line = self.peek_line(curateFile)
                self.fileName.emit(last_line.split("\t")[-1])
                
        else:
            self.errorMessage.emit("The progress reload folder you selected doesn't seem to be correct", "The curated file has nothing in it causing the program to fail. Are you sure you have already curated stuff for this project?")
        mutex.unlock()


class DeleteLineThread(QThread):
    
    def __init__(self, parent=None):
        QThread.__init__(self, parent)
    
    def delete_last_line(self,file):

    # Move the pointer (similar to a cursor in a text editor) to the end of the file
        file.seek(0, os.SEEK_END)

        # This code means the following code skips the very last character in the file -
        # i.e. in the case the last line is null we delete the last line
        # and the penultimate one
        pos = file.tell() - 1

        # Read each character in the file one at a time from the penultimate
        # character going backwards, searching for a newline character
        # If we find a new line, exit the search
        while pos > 0 and file.read(1) != "\n":
            pos -= 1
            file.seek(pos, os.SEEK_SET)

        # So long as we're not at the start of the file, delete all the characters ahead
        # of this position
        if pos > 0:
            file.seek(pos, os.SEEK_SET)
            file.truncate()
        file.write("\n")
    
    def peek_line(self, file):
        file.seek(0, os.SEEK_END)

        # This code means the following code skips the very last character in the file -
        # i.e. in the case the last line is null we delete the last line
        # and the penultimate one
        pos = file.tell() - 1

        # Read each character in the file one at a time from the penultimate
        # character going backwards, searching for a newline character
        # If we find a new line, exit the search
        while pos > 0 and file.read(1) != "\n":
            pos -= 1
            file.seek(pos, os.SEEK_SET)

        # So long as we're not at the start of the file, delete all the characters ahead
        # of this position
        # if pos > 0:
        #     file.seek(pos, os.SEEK_SET)
        line = file.readline()
        file.seek(pos)
        return line
        
    def run(self):
        mutex.lock()
        with open(os.path.join(contextPerserver.resultDir, contextPerserver.curatelist_name), "r+") as curateFile:
            curateFile.seek(0, os.SEEK_END)
            curate_line = self.peek_line(curateFile)
            print("This is curate_line", curate_line)
            action = curate_line.split("\t")[-1]
            print("This is action", action)
            if "Blacklisted" in action:
                with open(os.path.join(contextPerserver.resultDir, contextPerserver.black_list_name), "r+") as blackList:
                    blackList.seek(0, os.SEEK_END)
                    print(action, "should be blacklist")
                    self.delete_last_line(blackList)
                    print("Delete from blacklist")
                    blackList.flush()
            elif "Needs Double Check" in action:
                with open(os.path.join(contextPerserver.resultDir, contextPerserver.black_list_name), "r+") as checkList:
                    checkList.seek(0, os.SEEK_END)
                    print(action, "should be needs double chec ")
                    self.delete_last_line(checkList)
                    checkList.flush()
            self.delete_last_line(curateFile)
            curateFile.flush()
        mutex.unlock()

class QImageViewer(QMainWindow):
    keyPressed = pyqtSignal(int)
    fileAction = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.counter = 0
        self.scaleFactor = 0.0
        
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
        
        self.setWindowTitle("IGV Image Viewer - no folder selected yet")
        # self.resize(800, 600)
        self.showMaximized()
        

    def keyPressEvent(self, event):
        super(QImageViewer, self).keyPressEvent(event)
        self.keyPressed.emit(event.key()) 
        
    def on_key(self, key):
        betastasis_df = contextPerserver.betastasis_df
        if betastasis_df is None:
            self.pop_up_alert("You need to select the exported full TSV before you can start", 
                              "Download the TSV from betastasis (include the silent and blacklisted) and select the tsv from file option").exec_()
            return
        # test for a specific key
        if key == QtCore.Qt.Key_B:
            if self.counter == 0:
                return
            self.counter -= 1
            # self.openImage(os.path.join(self.folder, self.files[self.counter]))
            self.deleteLineThread = DeleteLineThread()
            self.deleteLineThread.start()
        elif key == QtCore.Qt.Key_Q or key == QtCore.Qt.Key_E or key == QtCore.Qt.Key_W:
            self.counter += 1
            if key == QtCore.Qt.Key_Q:
                action = "Blacklisted"
                print('Pressed Q')
                # self.openImage(os.path.join(self.folder, self.files[self.counter]))
            elif key == QtCore.Qt.Key_E:
                action = "Curated"
                print("Pressed E")
                # self.openImage(os.path.join(self.folder, self.files[self.counter]))
            elif key == QtCore.Qt.Key_W:
                print("Pressed W")
                action = "Needs Double Check"
            
            self.writeImageThread = WriteToFileThread(action,self.files[self.counter])
            self.writeImageThread.errorMessage.connect(self.pop_up_alert)
            self.writeImageThread.start()
        self.openImage(os.path.join(self.folder, self.files[self.counter]))
    
    def pop_up_alert(self, shortText, longText):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(shortText)
        msg.setInformativeText(longText)
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        return msg
    

            
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
        if self.folder:
            self.keyPressed.connect(self.on_key)
            self.files = [img for img in os.listdir(self.folder) if img.endswith((".png", ".jpeg", "jpg"))]
            print(os.path.join(self.folder, self.files[0]))
            self.setWindowTitle(f"IGV Image Viewer - {self.folder}")
            folderName = os.path.basename(self.folder)
            resultsFolder = os.path.join(bundle_dir, "results_"+folderName)
            Path(resultsFolder).mkdir(parents=True, exist_ok=True)
            contextPerserver.resultDir = resultsFolder
            print(os.path.join(contextPerserver.resultDir, contextPerserver.black_list_name))
            qm = QMessageBox()
            qm.setIcon(QMessageBox.information)
            ret = qm.question(self,'', "Do you want to load progress from previously creted folder?", qm.Yes | qm.No)
            if ret == qm.Yes:
                work_dir = QFileDialog.getExistingDirectory(self, 'Select folder where previous results are located', options=QFileDialog.ShowDirsOnly)
                if work_dir:
                    #@TODO connect the threads
                    contextPerserver.resultDir = work_dir
            else:
                self.openImage(os.path.join(self.folder, self.files[0]))
                with open(os.path.join(contextPerserver.resultDir, contextPerserver.black_list_name), "a+") as blacklist, open(os.path.join(contextPerserver.resultDir, contextPerserver.checklist_name), "a+") as checklist, open(os.path.join(contextPerserver.resultDir, contextPerserver.curatelist_name), "a+") as curatelist: 
                    pass
            
            
    def select_tsv(self):
        options = QFileDialog.Options()
        self.tsv_path = QFileDialog.getOpenFileName(self, 'Select betastasis TSV', '',
                                'TSV (*.tsv)', options=options)
        print(self.tsv_path)
        if self.tsv_path[0]:
            contextPerserver.betastasis_df = pd.read_csv(self.tsv_path[0], sep="\t", index_col=False)

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

class contextPerserver():
    resultDir = None
    betastasis_df = None
    black_list_name = "BlackList.tsv"
    checklist_name = "DoubleCheckList.tsv"
    curatelist_name = "CuratedList.tsv"

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    
    app = QApplication(sys.argv)
    imageViewer = QImageViewer()
    imageViewer.show()
    sys.exit(app.exec_())
    # TODO QScrollArea support mouse
    # base on https://github.com/baoboa/pyqt5/blob/master/examples/widgets/imageviewer.py
    #
    # if you need Two Image Synchronous Scrolling in the window by PyQt5 and Python 3
    # please visit https://gist.github.com/acbetter/e7d0c600fdc0865f4b0ee05a17b858f2
    
    
