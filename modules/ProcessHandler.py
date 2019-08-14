from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject
from modules.MyImage import MyImage
import pdb


class ProcessHandler(QObject):

    finishSignal = pyqtSignal()
    updateSignal = pyqtSignal(int)
    messageSignal = pyqtSignal(str)

    def __init__(self):
        super(ProcessHandler, self).__init__()

    def setImagePath(self, imagePathes):
        self._imagePathes = imagePathes
        self._imageLists = [MyImage(imagePath) for imagePath in self._imagePathes]
        # 已完成的进程数
        self._finishedCount = 0
        # 已开始运行的进程数
        self._pointer = 0
        # 正在运行的进程数
        self._currentCount = 0
        # 需要运行的总进程数
        self._taskCount = len(self._imagePathes)
        # 停止标记
        self._stopFlag = False

    def setParams(self, width, height, depth, radius, threads=4):
        self._threads = threads
        for image in self._imageLists:
            image.setParams(width, height, depth, radius)
            image.messageSignal.connect(self.messageSignal.emit)
        return self

    def start(self):
        self.updateSignal.emit(0)
        firstCount = min(self._taskCount, self._threads)
        for image in self._imageLists[:firstCount]:
            image.finishSignal.connect(self._update)
            image.start()
            self._currentCount += 1
            self._pointer += 1

    def _update(self):
        self._finishedCount += 1
        self._currentCount -= 1
        self.updateSignal.emit(int(self._finishedCount / self._taskCount * 100))

        if self._currentCount == 0:
            self.finishSignal.emit()
            return

        if self._stopFlag and self._currentCount != 0:
            print('Wait Other threads to stop...')
            return

        try:
            self._imageLists[self._pointer].finishSignal.connect(self._update)
            self._imageLists[self._pointer].start()
            self._pointer += 1
            self._currentCount += 1
        except IndexError as e:
            print(e)

    @pyqtSlot()
    def stop(self):
        self._stopFlag = True
