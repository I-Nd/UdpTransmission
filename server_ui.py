# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'server_ui.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_udpServer(object):
    def setupUi(self, udpServer):
        udpServer.setObjectName("udpServer")
        udpServer.resize(800, 600)
        udpServer.setMinimumSize(QtCore.QSize(800, 600))
        udpServer.setMaximumSize(QtCore.QSize(800, 600))
        self.centralwidget = QtWidgets.QWidget(udpServer)
        self.centralwidget.setObjectName("centralwidget")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(10, 10, 781, 291))
        self.groupBox.setObjectName("groupBox")
        self.browser = QtWidgets.QTextBrowser(self.groupBox)
        self.browser.setGeometry(QtCore.QRect(10, 20, 761, 261))
        self.browser.setObjectName("browser")
        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_2.setGeometry(QtCore.QRect(10, 310, 541, 261))
        self.groupBox_2.setObjectName("groupBox_2")
        self.log = QtWidgets.QTextBrowser(self.groupBox_2)
        self.log.setGeometry(QtCore.QRect(10, 20, 521, 231))
        self.log.setObjectName("log")
        self.groupBox_3 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_3.setGeometry(QtCore.QRect(560, 310, 231, 111))
        self.groupBox_3.setObjectName("groupBox_3")
        self.label = QtWidgets.QLabel(self.groupBox_3)
        self.label.setGeometry(QtCore.QRect(10, 20, 50, 20))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.groupBox_3)
        self.label_2.setGeometry(QtCore.QRect(10, 50, 50, 20))
        self.label_2.setObjectName("label_2")
        self.serverIP = QtWidgets.QLineEdit(self.groupBox_3)
        self.serverIP.setGeometry(QtCore.QRect(50, 20, 111, 20))
        self.serverIP.setObjectName("serverIP")
        self.serverPort = QtWidgets.QLineEdit(self.groupBox_3)
        self.serverPort.setGeometry(QtCore.QRect(60, 50, 101, 20))
        self.serverPort.setObjectName("serverPort")
        self.modButton = QtWidgets.QPushButton(self.groupBox_3)
        self.modButton.setGeometry(QtCore.QRect(170, 20, 51, 51))
        self.modButton.setObjectName("modButton")
        self.optButton = QtWidgets.QPushButton(self.groupBox_3)
        self.optButton.setGeometry(QtCore.QRect(10, 80, 211, 23))
        self.optButton.setObjectName("optButton")
        self.groupBox_4 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_4.setGeometry(QtCore.QRect(560, 430, 231, 61))
        self.groupBox_4.setObjectName("groupBox_4")
        self.label_3 = QtWidgets.QLabel(self.groupBox_4)
        self.label_3.setGeometry(QtCore.QRect(10, 20, 41, 20))
        self.label_3.setObjectName("label_3")
        self.dropNow = QtWidgets.QPushButton(self.groupBox_4)
        self.dropNow.setGeometry(QtCore.QRect(170, 10, 51, 41))
        self.dropNow.setObjectName("dropNow")
        self.dropRate = QtWidgets.QDoubleSpinBox(self.groupBox_4)
        self.dropRate.setGeometry(QtCore.QRect(60, 20, 101, 22))
        self.dropRate.setObjectName("dropRate")
        udpServer.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(udpServer)
        self.statusbar.setObjectName("statusbar")
        udpServer.setStatusBar(self.statusbar)

        self.retranslateUi(udpServer)
        QtCore.QMetaObject.connectSlotsByName(udpServer)

    def retranslateUi(self, udpServer):
        _translate = QtCore.QCoreApplication.translate
        udpServer.setWindowTitle(_translate("udpServer", "UDP网络通信服务端 v0.3d"))
        self.groupBox.setTitle(_translate("udpServer", "网络通信"))
        self.groupBox_2.setTitle(_translate("udpServer", "运行日志"))
        self.groupBox_3.setTitle(_translate("udpServer", "连接设置"))
        self.label.setText(_translate("udpServer", "服务IP"))
        self.label_2.setText(_translate("udpServer", "服务端口"))
        self.modButton.setText(_translate("udpServer", "修改"))
        self.optButton.setText(_translate("udpServer", "启动服务"))
        self.groupBox_4.setTitle(_translate("udpServer", "模拟丢包"))
        self.label_3.setText(_translate("udpServer", "丢包率"))
        self.dropNow.setText(_translate("udpServer", "丢!"))

