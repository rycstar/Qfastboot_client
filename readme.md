####Project introduction
    This project aim to implement a Fastboot client to upgrade images to Android/embedded devices
    For better user experiense, pyqt5 is a good choise.

####Development environment

    1. Install Python3.0+
        Too many documents and instructions, find it on Google.
    2. Install PyQt5
        pip install pyqt5
        pip install pyqt5-tools   (for QT designer and pyuic5)
    3. Install python ADB
        download the latest version (v1.3.0) package from https://github.com/google/python-adb

####Arch Preview

    1. UI designer
        a)  find and open qt designer. For exampe:
            <Python-path>\Scripts\pyqt5-tools.exe designer
        b) Use qt designer to layout UI widgets
        c) Use pyuic5 to translate the .ui file. for example:
            <Python-path>\Scripts\pyuic5.exe .\QUI\fastboot.ui -o .\QUI\fastboot_ui_layout.py

####Issues


####Links
1. https://blog.csdn.net/u013541325/article/details/107742835
2. https://github.com/google/python-adb
