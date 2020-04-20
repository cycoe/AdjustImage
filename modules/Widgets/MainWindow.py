import os

from PyQt5.Qt import QIntValidator, QRegExp, QRegExpValidator
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QMessageBox

from modules.ProcessHandler import ProcessHandler
from modules.Widgets.Ui_mainWindow import Ui_mainWindow


class MainWindow(QMainWindow, Ui_mainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self._initVar()
        self._initWidgets()
        self._setConnect()

    def setupUi(self, window):
        super(MainWindow, self).setupUi(window)
        self.centralWidget().setLayout(self.mainLayout)
        self.setFixedSize(800, 400)

    def _initVar(self):
        self._imagePathes = []
        self._fileDialog = QFileDialog(self)
        self._progressHandler = ProcessHandler()

    def _initWidgets(self):
        self.spinWidth.setValue(1920)
        self.spinHeight.setValue(1080)
        self.spinDepth.setValue(100)
        self.spinRadius.setValue(10)
        self.spinThreads.setValue(4)
        self.progressBar.setValue(0)

    def _setConnect(self):
        self.btnSelect.clicked.connect(self._openFileDialog)
        self.btnRun.clicked.connect(self._run)
        self._progressHandler.finishSignal.connect(self._done)
        self._progressHandler.updateSignal.connect(self.progressBar.setValue)
        self._progressHandler.messageSignal.connect(self.statusbar.showMessage)

    @pyqtSlot()
    def _openFileDialog(self):
        self._imagePathes, self._imageTypes = self._fileDialog.getOpenFileNames(
            self,
            '请选择需要处理的图片',
            os.path.expandvars('$HOME'),
            "Image Files (*.jpg *.png)"
        )
        self.listImages.clear()
        self.listImages.addItems(self._imagePathes)
        self._progressHandler.setImagePath(self._imagePathes)

    @pyqtSlot()
    def _run(self):
        if self._imagePathes:
            try:
                width = int(self.spinWidth.text())
                height = int(self.spinHeight.text())
                depth = int(self.spinDepth.text())
                radius = int(self.spinRadius.text())
                threads = int(self.spinThreads.text())
            except ValueError as e:
                QMessageBox.warning(self, '错误', '请正确输入参数！')
                return False
            self._convertRun()
            self._progressHandler.setParams(
                width, height, depth, radius, threads
            ).start()
        else:
            QMessageBox.warning(self, '警告', '请先选择图片！')

    @pyqtSlot()
    def _done(self):
        self._imagePathes = []
        self.listImages.clear()
        self._progressHandler.setImagePath(self._imagePathes)
        self._convertDone()
        self.statusbar.showMessage('处理完成')

    @pyqtSlot()
    def _convertDone(self):
        self.btnRun.setText('点击开始')
        self.btnRun.setEnabled(True)
        # 切记 disconnect
        self.btnRun.clicked.disconnect(self._convertStop)
        self.btnRun.clicked.connect(self._run)

    @pyqtSlot()
    def _convertRun(self):
        self.btnRun.setText('点击停止')
        self.btnRun.setEnabled(True)
        self.btnRun.clicked.disconnect(self._run)
        self.btnRun.clicked.connect(self._convertStop)

    @pyqtSlot()
    def _convertStop(self):
        self.btnRun.setEnabled(False)
        self._progressHandler.stop()
