from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QPushButton

import threading

class SwitchButton(QPushButton):

    def __init__(self, parent=None, posText=None, negText=None):
        super(SwitchButton, self).__init__(posText, parent)
        # 当前状态
        self.status = True
        # 切换信号
        self.signal = True
        # 正向状态文字
        self.posText = posText
        # 反向状态文字
        self.negText = negText
        # 正向到反向过渡文字
        self.pos2NegText = '...'
        # 反向到正向过渡文字
        self.neg2PosText = '...'
        # 正向按键点击事件
        self.posAction = lambda: None
        # 反向按键点击事件
        self.negAction = lambda: None

        # 按键状态检查周期
        self.period = 0.1
        # 初始化按键状态为正向
        self.setStatus(True)
        # 绑定点击事件
        self.clicked.connect(self._clicked)

    def setPosText(self, text):
        """设置正向状态文字"""
        self.posText = text

    def setNegText(self, text):
        """设置反向状态文字"""
        self.negText = text

    def setPos2NegText(self, text):
        """设置正向到反向过渡状态文字"""
        self.pos2NegText = text

    def setNeg2PosText(self, text):
        """设置反向到正向过渡状态文字"""
        self.neg2PosText = text

    def setPosAction(self, action):
        self.posAction = action

    def setNegAction(self, action):
        self.negAction = action

    def setCheckPeriod(self, period):
        self.period = period

    @pyqtSlot()
    def setStatus(self, status):
        if status:
            self.setText(self.posText)
        else:
            self.setText(self.negText)
        self.signal = status
        self.setEnabled(status)

    @pyqtSlot()
    def _clicked(self):
        if self.signal:
            self.signal = False
            self.setEnabled(False)
            self.setText(self.pos2NegText)
            self.posAction()
            # threading.Thread(target=self.posAction).start()
            # self.setNeg()
        else:
            self.signal = True
            self.setEnabled(False)
            self.setText(self.neg2PosText)
            self.negAction()
            # threading.Thread(target=self.negAction).start()
            # self.setPos()
