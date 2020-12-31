# -*- coding: utf-8 -*-

import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from fastboot_ui_layout import Ui_MainWindow

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.Browse_btn.pressed.connect(self.browse_img)
        self.show()

    def browse_img(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open file",
            "",
            "img files (*.bin);;All files (*.*)",
        )

        if path:
            self.select_file_label.setText(path)
            self.Upgrade_btn.setEnabled(True)

if __name__=='__main__':
    app = QApplication([])
    app.setApplicationName("Fastboot")

    window = MainWindow()
    app.exec_()

