import os
import sys
import threading

from PyQt5.Qt import QIntValidator
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import (QFileDialog, QGridLayout, QHBoxLayout, QLabel,
                             QLineEdit, QListWidget, QMainWindow, QMessageBox,
                             QProgressBar, QPushButton, QVBoxLayout, QWidget)

from modules.MyImage import MyImage
from modules.Widgets.ProgressDialog import ProgressDialog
from modules.Widgets.SwitchButton import SwitchButton


class MainWindow(QMainWindow):
    """主窗口类"""

    def __init__(self):
        super(MainWindow, self).__init__()
        self._init_var()
        self._set_property()
        self._init_widgets()
        self._set_layout()
        self._set_connect()

    def _init_var(self):
        self.fileNames = []
        self.progressing = False

    def _init_widgets(self):
        # 初始化标签部件
        self.widthLabel = QLabel('宽度')
        self.heightLabel = QLabel('高度')
        self.radiusLabel = QLabel('模糊半径')
        # 初始化输入部件
        self.widthEdit = QLineEdit()
        self.heightEdit = QLineEdit()
        self.radiusEdit = QLineEdit()
        self.widthEdit.setText('1920')
        self.heightEdit.setText('1080')
        self.radiusEdit.setText('10')
        self.widthEdit.setValidator(QIntValidator(1, 10000))
        self.heightEdit.setValidator(QIntValidator(1, 10000))
        self.radiusEdit.setValidator(QIntValidator(1, 100))
        # 初始化按键
        self.imgListWidget = QListWidget(self)
        self.imgSelectBtn = QPushButton('选取图像')
        # 初始化进度控制部件
        self.progressBar = QProgressBar(self)
        self.progressBtn = SwitchButton('开始', '取消')
        self.progressBtn.setPosAction(self._start_progress)
        # self.progressBtn.setNegAction()

    def _set_property(self):
        """设置属性"""
        self.setWindowTitle('图片批量加背景工具')
        self.resize(500, 300)

    def _set_layout(self):
        """设置布局"""
        # 设置中心部件
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        # 使用网格布局作为主布局
        self.centralLayout = QGridLayout()
        self.centralWidget.setLayout(self.centralLayout)
        # 参数输入群组使用网格布局
        self.paramLayout = QGridLayout()
        self.centralLayout.addLayout(self.paramLayout, 0, 0, 1, 1)
        self.paramLayout.addWidget(self.widthLabel, 0, 0)
        self.paramLayout.addWidget(self.widthEdit, 0, 1)
        self.paramLayout.addWidget(self.heightLabel, 1, 0)
        self.paramLayout.addWidget(self.heightEdit, 1, 1)
        self.paramLayout.addWidget(self.radiusLabel, 2, 0)
        self.paramLayout.addWidget(self.radiusEdit, 2, 1)
        # 图片选取群组使用纵向布局
        self.imgSelectLayout = QVBoxLayout()
        self.centralLayout.addLayout(self.imgSelectLayout, 0, 1, 1, 1)
        self.imgSelectLayout.addWidget(self.imgListWidget)
        self.imgSelectLayout.addWidget(self.imgSelectBtn)
        # 进度控制群组使用横向布局
        self.progressLayout = QHBoxLayout()
        self.centralLayout.addLayout(self.progressLayout, 1, 0, 1, 2)
        self.progressLayout.addWidget(self.progressBar)
        self.progressLayout.addWidget(self.progressBtn)

    def _set_connect(self):
        """设置信号槽连接"""
        self.imgSelectBtn.clicked.connect(self._open_file_dialog)
        self.progressBtn.setPosAction(self._start_progress)

    @pyqtSlot()
    def _open_file_dialog(self):
        """打开文件选择器"""
        self.fileNames, self.fileTypes = QFileDialog.getOpenFileNames(
            self,
            '请选择需要处理的图片',
            os.path.expandvars('$HOME'),
            "Image Files (*.jpg *.png)"
        )
        self.imgListWidget.clear()
        self.imgListWidget.addItems(self.fileNames)

    @pyqtSlot()
    def _start_progress(self):
        if self.fileNames:
            try:
                width = int(self.widthEdit.text()),
                height = int(self.heightEdit.text()),
                radius = int(self.radiusEdit.text())
            except ValueError as e:
                print(e)
                QMessageBox.information(self, '错误', '请正确输入参数！')
                self.progressBtn.setPos()
                return False
            threading.Thread(target=self._background_progress, args=(
                self.fileNames,
                int(self.widthEdit.text()),
                int(self.heightEdit.text()),
                int(self.radiusEdit.text())
            )).start()
            self.progressBtn.setNeg()
        else:
            self.progressBtn.setPos()

    def _background_progress(self, fileNames, width, height, radius):
        """子线程图片处理"""
        self.progressing = True
        file_num = len(fileNames)
        for index in range(file_num):
            if self.progressBtn.signal:
                break
            else:
                print('processing {}...'.format(index))
                myImage = MyImage(fileNames[index])
                myImage.adjust(width, height, radius)
                del myImage
                self.progressBar.setValue(int((index + 1) / file_num * 100))
        QMessageBox.information(self, '提示', '图片处理完成！')
        self.progressBar.setValue(0)
        self.progressBtn.setPos()
