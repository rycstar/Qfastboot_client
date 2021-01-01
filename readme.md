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
        pip install adb

####Arch Preview

    1. UI designer
        a)  find and open qt designer. For exampe:
            <Python-path>\Scripts\pyqt5-tools.exe designer
        b) Use qt designer to layout UI widgets
        c) Use pyuic5 to translate the .ui file. for example:
            <Python-path>\Scripts\pyuic5.exe .\QUI\fastboot.ui -o .\QUI\fastboot_ui_layout.py

####Issues

    1. error in adb install:
        a) Error Info: 'error: Microsoft Visual C++ 14.0 is required. 
            Get it with "Build Tools for Visual Studio":
            https://visualstudio.microsoft.com/downloads/'
        b) Analysis: in package 'M2Crypto' installing , it need to compile   the source code and build package. But in python3.9, Microsoft Visual C++ 14.0 is required for python package compile
        c) Fix method: 
            Install 'Microsoft Visual C++ Build Tools 2015' to fix this issue
            or install the 'whl' package directly.
            Refer to Link[3][4] to get more information

    /*******************************Notice**********************************/
    M2crypto is a Crypto library for python, we can use other library instead of it.
    If you want use RSA or pycryptodome, you should download the adb source code, change the setup.py as below and recompile it.
            # Figure out if the system already has a supported Crypto library
            # rsa_signer_library = 'M2Crypto>=0.21.1,<=0.26.4'
            rsa_signer_library = 'rsa'
    Then, use command "python setup.py build" and "python.exe setup.py bdist_wheel" to generate a new adb-1.3.0-py3-none-any.whl under "dist" directory.
    At last, run 'pip install adb-1.3.0-py3-none-any.whl' to add it into python package.


####Links
1. https://blog.csdn.net/u013541325/article/details/107742835
2. https://github.com/google/python-adb
3. https://blog.csdn.net/weixin_40547993/article/details/89399825
4. https://github.com/iOSForensics/pymobiledevice/issues/25
5. https://github.com/cperezabo/m2crypto-wheels
