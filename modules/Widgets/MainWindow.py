import os
from PyQt5.Qt import QIntValidator, QRegExp, QRegExpValidator
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox
from PyQt5.QtCore import pyqtSlot
from modules.Widgets.Ui_mainWindow import Ui_mainWindow
from modules.ProcessHandler import ProcessHandler


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
        # self.spinWidth.setToolTip('此处输入需要的图片宽度（范围：1-10000）')
        # self.spinHeight.setToolTip('此处输入需要的图片高度（范围：1-10000）')
        # self.spinDepth.setToolTip('此处输入照片与背景的浸入深度（范围：1-500）')
        # self.spinRadius.setToolTip('此处输入高斯模糊的模糊半径（范围：1-100）')
        # self.spinThreads.setToolTip('此处输入运行的线程数（范围：1-10）')
        # sizeValidator = QRegExpValidator(QRegExp('^[1-9]\\d{2,3}$'), self)
        # depthValidator = QRegExpValidator(QRegExp('^[0-4]?\\d{1,2}$'), self)
        # radiusValidator = QRegExpValidator(QRegExp('^\\d{1,2}$'), self)
        # threadsValidator = QRegExpValidator(QRegExp('^[1-9]$'), self)
        # self.spinWidth.setValidator(sizeValidator)
        # self.spinHeight.setValidator(sizeValidator)
        # self.spinDepth.setValidator(depthValidator)
        # self.spinRadius.setValidator(radiusValidator)
        # self.spinThreads.setValidator(threadsValidator)

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
