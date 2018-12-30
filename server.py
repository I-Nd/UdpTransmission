# code:utf8
import socket
import time
import threading
import sys
import html
import random
import pickle
from PyQt5.QtWidgets import QApplication, QMainWindow, QHeaderView, QAbstractItemView, QTableWidgetItem, QMessageBox
from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal, Qt
from PyQt5.QtGui import QIcon
from server_ui import *

global DEST_IP, DEST_PORT, run, dropRate
DEST_IP = '0.0.0.0'
DEST_PORT = 6666
run = False
dropRate = 0.0

class ReceiveThread(QThread):
    update_message_signal = pyqtSignal(str)
    update_log_signal = pyqtSignal(int, str)

    def __init__(self, skt, parent=None):
        super(ReceiveThread, self).__init__(parent)
        self.skt = skt

    def receivePacket(self):
        try:
            skt = self.skt
            (rawData, addr) = skt.recvfrom(1024)
            data = pickle.loads(rawData)
            skt.sendto(data[0].encode(), addr)
            print(addr)
            send_id = int(data[0])
            if(send_id == 0):
                size = int(data[1])
                self.update_log_signal.emit(0, "开始数据接收，总大小 " + str(size) + " Bytes")
                self.update_message_signal.emit("<font color=\"#1E90FF\" size=\"2\">" + html.escape("-------<<< " + str(addr[0]) + ":" + str(addr[1])) + "</font>")
                self.receiveMessage(size, skt)
        except Exception as e:
            print(e)
            self.update_log_signal.emit(2, "服务已停止！")

    def receiveMessage(self, size, skt):
        try:
            received_id = 0
            receivedData = b''
            while (len(receivedData) < size):
                (rawData, addr) = skt.recvfrom(1024)
                data = pickle.loads(rawData)
                if(random.uniform(0, 100) > dropRate):
                    skt.sendto(data[0].encode(), addr)
                send_id = int(data[0])
                self.update_log_signal.emit(1, "包编号 " + str(send_id) + " 收到,已发送确认包")
                if (send_id == received_id + 1):
                    received_id = received_id + 1
                    receivedData = receivedData + data[1]
            self.update_log_signal.emit(0, "数据接收完毕！")
            self.update_message_signal.emit(receivedData.decode())
            self.update_message_signal.emit("<font color=\"#66CD00\" size=\"2\">" + "--------------------" + "</font>")
            print(receivedData.decode())
        except Exception as e:
            print(e)
            self.update_log_signal.emit(2, "服务已中断！")

    def run(self):
        while(run):
            print("开工！")
            self.receivePacket()


class ClientWindow(QMainWindow, Ui_udpServer):
    def __init__(self, parent=None):
        super(ClientWindow, self).__init__(parent)
        self.setupUi(self)
        self.setWindowIcon(QIcon('./udp.png'))
        self.serverIP.setText(DEST_IP)
        self.serverPort.setText(str(DEST_PORT))
        self.optButton.clicked.connect(self.serverControl)
        self.modButton.clicked.connect(self.serverMod)
        self.dropNow.clicked.connect(self.dropMod)
        self.print_log(0, "软件初始化完毕，欢迎使用！")

    @pyqtSlot()
    def serverControl(self):
        global run
        if(not run):
            run = True
            self.skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.skt.bind((DEST_IP, DEST_PORT))
            self.receiveThread = ReceiveThread(self.skt)
            self.receiveThread.update_log_signal.connect(self.print_log)
            self.receiveThread.update_message_signal.connect(self.print_message)
            self.receiveThread.start()
            self.print_log(1, "服务已启动！监听IP：" + DEST_IP + " 监听端口：" + str(DEST_PORT))
            self.optButton.setText("停止服务")
        else:
            run = False
            self.skt.close()
            self.optButton.setText("启动服务")

    @pyqtSlot()
    def serverMod(self):
        global DEST_IP, DEST_PORT
        DEST_IP = self.serverIP.text()
        DEST_PORT = int(self.serverPort.text())
        if(run):
            self.serverControl()
        QMessageBox.information(self, "设置更新", "服务设置已更新！\t\n\n服务IP: " + DEST_IP + "\t\n服务端口: " + str(DEST_PORT) + "\n请重新启动服务！", QMessageBox.Yes)

    @pyqtSlot()
    def dropMod(self):
        try:
            global dropRate
            dropRate = float(self.dropRate.text())
            QMessageBox.information(self, "模拟丢包", "模拟丢包已启用！\t\n\n丢包率: " + str(dropRate), QMessageBox.Yes)
        except Exception as e:
            print(e)

    @pyqtSlot(str)
    def print_message(self, message):
        self.browser.append(message)

    @pyqtSlot(int, str)
    def print_log(self, level, message):
        nowTime = "<font color=\"#000000\" size=\"3\">" + html.escape("[" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "] ")
        if (level == 0):
            self.log.append(nowTime + "<font color=\"#1E90FF\" size=\"3\">" + html.escape(message) + "</font>")
        elif (level == 1):
            self.log.append(nowTime + "<font color=\"#66CD00\" size=\"3\">" + html.escape(message) + "</font>")
        elif (level == 2):
            self.log.append(nowTime + "<font color=\"#FF2D2D\" size=\"3\">" + html.escape(message) + "</font>")
        elif (level == 3):
            self.log.append(nowTime + "<font color=\"#000000\" size=\"3\">" + html.escape(message) + "</font>")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    clientWindow = ClientWindow()
    clientWindow.show()
    sys.exit(app.exec_())