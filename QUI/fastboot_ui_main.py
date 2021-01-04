# -*- coding: utf-8 -*-

import traceback, sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from adb import fastboot
from adb import usb_exceptions
from fastboot_ui_layout import Ui_MainWindow

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        #init usb modules
        self.usb_dev = fastboot.FastbootCommands()
        #init QT ui modules
        self.setupUi(self)

        self.filetype_comboBox.addItem("Fanvil_z_packet")
        self.filetype_comboBox.addItem("kernel")
        self.filetype_comboBox.addItem("rootfs")
        self.filetype_comboBox.addItem("custom")

        self.detect_btn.pressed.connect(self.detect_device)
        self.Browse_btn.pressed.connect(self.browse_img)
        self.Upgrade_btn.pressed.connect(self.upgrade_img)
        self.cmd_send_btn.pressed.connect(self.send_cmd)
        self.show()

    def device_not_found(self, err_msg):
        self.device_label.setStyleSheet("color:red")
        self.device_label.setText("No device found.")
        self.cmd_send_btn.setEnabled(False)
        self.log_textBrowser.append(err_msg)

    def detect_device(self):
        dev_list = self.usb_dev.Devices()
        i = 0
        for device in fastboot.FastbootCommands.Devices():
            #print('%s\tdevice' % device.serial_number)
            i = i + 1

        if(i > 0):
            self.device_label.setStyleSheet("color:blue")
            self.device_label.setText(str(i)+" device(s) found.")
            self.cmd_send_btn.setEnabled(True)
        else:
            self.device_not_found()

    def send_cmd(self):
        try:
            self.usb_dev.ConnectDevice()
            if(self.cmd_lineEdit.text().startswith('getvar:')):
                self.usb_dev.Getvar(var=self.cmd_lineEdit.text()[7:], info_cb = self.update_fb_msg)
            elif(self.cmd_lineEdit.text().startswith('reboot')):
                self.usb_dev.Reboot()
            self.usb_dev.Close()
        except fastboot.FastbootRemoteFailure:
            pass
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.device_not_found(str(repr(traceback.format_exception(exc_type, exc_value, exc_traceback))))

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

    def upgrade_img(self):
        try:
            self.usb_dev.ConnectDevice()
            self.usb_dev.FlashFromFile(partition='kernel1',source_file=self.select_file_label.text(),progress_callback=self.upgrade_progress)
            self.usb_dev.Close()
        except:
            self.device_not_found(None)

    def upgrade_progress(self, current, total):
        if(total == current):
            self.log_textBrowser.setStyleSheet("color:red")
            self.log_textBrowser.append("Image Download Done, device is writing flash, waiting for a minute!!!")

        self.upgrade_progressBar.setMinimum(0)
        self.upgrade_progressBar.setMaximum(total)
        self.upgrade_progressBar.setValue(current)

    def update_fb_msg(self, log):
        self.log_textBrowser.setStyleSheet("color:blue")
        self.log_textBrowser.append(bytes.decode(log.header)+':'+ bytes.decode(log.message))


if __name__=='__main__':
    app = QApplication([])
    app.setApplicationName("Fastboot")

    window = MainWindow()
    app.exec_()

