# -*- coding: utf-8 -*-
import os
import traceback, sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import re
import queue
from threading import Thread,Semaphore

from adb import fastboot
from adb import usb_exceptions
from fastboot_ui_layout import Ui_MainWindow
#from operator import length_hint

g_queue = queue.Queue(maxsize=1)
g_sem = Semaphore(0)
g_result_list=[]

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        
        self.queue = g_queue

        #init QT ui modules
        self.setupUi(self)

        self.filetype_comboBox.addItem("None")
        self.filetype_comboBox.addItem("kernel")
        self.filetype_comboBox.addItem("rootfs")
        self.filetype_comboBox.addItem("custom")
        self.filetype_comboBox.addItem("Fanvil_z_packet")

        self.detect_btn.pressed.connect(self.detect_device)
        self.Browse_btn.pressed.connect(self.browse_img)
        self.Upgrade_btn.pressed.connect(self.upgrade_img)
        self.cmd_send_btn.pressed.connect(self.send_cmd)
        self.cmd_lineEdit.returnPressed.connect(self.send_cmd)
        self.setWindowTitle("Fastboot Client")
        self.timer = QTimer()
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.cmd_result_update)
        self.timer.start()
        self.show()

    def cmd_result_hdl(self, result):
        if(result.startswith('detect')):
            fields = re.split(r'[=]',result)
            if(int(fields[1]) > 0):
                self.device_label.setStyleSheet("color:blue")
                self.device_label.setText(fields[1]+" device(s) found")
                self.cmd_send_btn.setEnabled(True)
            else:
                self.device_label.setStyleSheet("color:red")
                self.device_label.setText("No device found")
                self.cmd_send_btn.setEnabled(False)
        elif(result.startswith('progress')):
            fields = re.split(r'[=:]',result)
            #if(length_hint(fields) != 3):
            #    return
            if(int(fields[1]) == int(fields[2])):
                self.log_textBrowser.append("<font color=red>"+"Image Download Done, device is writing flash, waiting for a minute!!!")
            self.upgrade_progressBar.setMinimum(0)
            self.upgrade_progressBar.setMaximum(int(fields[2]))
            self.upgrade_progressBar.setValue(int(fields[1]))


    def cmd_result_update(self):
        if(g_sem.acquire(timeout=0.05)):
            for l_item in g_result_list:
                self.log_textBrowser.append("<font color=blue>"+l_item)
                if(l_item.startswith('[RES]')):
                    self.cmd_result_hdl(l_item[5:])
            g_result_list.clear()
            self.update()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message',"Are you sure to quit?",QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self.queue.put("ignore", timeout = 0.2)
            except:
                pass
            try:
                self.queue.put("exit", timeout = 0.3)
                event.accept()
            except queue.Full:
                QMessageBox.warning(self,"Warning","Fastboot command is running, try later")
                event.ignore()
        else:
            event.ignore()

    def check_and_send_cmd(self, cmd):
        try:
            self.queue.put(cmd, timeout = 0.3)
        except queue.Full:
            QMessageBox.warning(self,"Warning","Fastboot command is running, try later")

    def detect_device(self):
        self.check_and_send_cmd("detect")

    def send_cmd(self):
        self.check_and_send_cmd(self.cmd_lineEdit.text())

    def browse_img(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open file",
            "",
            "img files (*.bin);;All files (*.*)",
        )

        if path:
            self.select_file_label.setText(path)
            
            if(os.path.basename(path).find('kernel') >= 0):
                self.filetype_comboBox.setCurrentText("kernel")
            elif(os.path.basename(path).find('rootfs') >= 0):
                self.filetype_comboBox.setCurrentText("rootfs")
            elif(os.path.basename(path).find('custom') >= 0):
                self.filetype_comboBox.setCurrentText("custom")
            elif(os.path.basename(path).endswith('.z')):
                self.filetype_comboBox.setCurrentText("Fanvil_z_packet")
            else:
                self.filetype_comboBox.setCurrentIndex(0)
            self.Upgrade_btn.setEnabled(True)

    def upgrade_img(self):
        self.check_and_send_cmd("upgrade|"+ "kernel1|"+self.select_file_label.text())


class fastboot_client(object):
    def __init__(self, queue = None):
        #init usb modules
        self.queue = queue
        self.usb_dev = fastboot.FastbootCommands()
        self.thread = Thread(target=self.fastboot_cmd_execute)
        self.thread.start()

    def upgrade_progress(self, current, total):
        self.fastboot_cmd_result("progress",str(current)+":"+str(total))

    def fastboot_cmd_result(self, cmd, log):
        g_result_list.append("[RES]"+cmd +"="+log)
        g_sem.release()

    def fastboot_getvar_result(self,msg):
        self.fastboot_cmd_result("getvar",bytes.decode(msg.header)+':'+ bytes.decode(msg.message))

    def fastboot_cmd_execute(self):
        while True:
            item = self.queue.get()
            if(item.startswith("exit")):
                break
            elif(item.startswith("ignore")):
                continue
            try:
                self.usb_dev.ConnectDevice()
                if(item.startswith('detect')):
                    i = 0
                    for device in self.usb_dev.Devices():
                        i = i + 1
                        if(i > 0):
                            self.fastboot_cmd_result("detect", str(i))
                        else:
                            self.fastboot_cmd_result("detect", '0')
                elif(item.startswith('getvar:')):
                    self.usb_dev.Getvar(var = item[7:], info_cb = self.fastboot_getvar_result)
                elif(item.startswith('upgrade')):
                    fields = re.split(r'[|]',item)
                    self.usb_dev.FlashFromFile(partition=fields[1],source_file=fields[2],progress_callback=self.upgrade_progress)
                elif(item.startswith('reboot-bootloader')):
                    self.usb_dev.RebootBootloader()
                elif(item.startswith('reboot')):
                    self.usb_dev.Reboot()
                self.usb_dev.Close()
            except fastboot.FastbootRemoteFailure:
                pass
            except:
                self.fastboot_cmd_result(item,"except error")

if __name__=='__main__':
    app = QApplication([])
    app.setApplicationName("Fastboot")
    fb_client = fastboot_client(queue=g_queue)
    window = MainWindow()
    sys.exit(app.exec_())

