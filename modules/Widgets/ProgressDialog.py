from PyQt5.QtWidgets import QProgressDialog
from PyQt5.QtCore import Qt


class ProgressDialog(QProgressDialog):

    def __init__(self, parent, file_num):
        super(ProgressDialog, self).__init__(parent)
        self.file_num = file_num
        self._set_var()

    def _set_var(self):
        self.setWindowTitle('正在处理图片')
        self.setCancelButtonText('取消')
        self.setRange(0, 100)
        self.setWindowModality(Qt.WindowModal)
        self.update(0)

    def update(self, current_index):
        self.setLabelText('正在处理第{}张图片...'.format(current_index + 1))
        self.setValue(int((current_index + 1) / self.file_num * 100))
