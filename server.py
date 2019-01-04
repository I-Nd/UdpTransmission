# code:utf8
import socket
import time
import os
import sys
import html
import random
import pickle
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal
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

    def receive_packet(self):
        try:
            skt = self.skt
            (rawData, addr) = skt.recvfrom(1024)
            data = pickle.loads(rawData)
            skt.sendto(data[0].encode(), addr)
            print(addr)
            send_id = int(data[0])
            if send_id == 0:
                if data[2]:
                    size = int(data[1])
                    file_name = data[2]
                    self.update_log_signal.emit(0, "开始数据接收，数据类型【文件】，总大小 " + str(size) + " Bytes")
                    self.update_log_signal.emit(1, "包编号 " + str(send_id) + " 收到,已发送确认包")
                    self.update_message_signal.emit("<font color=\"#1E90FF\" size=\"2\">" + html.escape("-------<<< " + str(addr[0]) + ":" + str(addr[1])) + "</font>")
                    self.receive_file(size, file_name, skt)
                else:
                    size = int(data[1])
                    self.update_log_signal.emit(0, "开始数据接收，数据类型【消息】，总大小 " + str(size) + " Bytes")
                    self.update_log_signal.emit(1, "包编号 " + str(send_id) + " 收到,已发送确认包")
                    self.update_message_signal.emit("<font color=\"#1E90FF\" size=\"2\">" + html.escape("-------<<< " + str(addr[0]) + ":" + str(addr[1])) + "</font>")
                    self.receive_message(size, skt)
        except Exception as e:
            print(e)
            self.update_log_signal.emit(2, "服务已停止！")

    def receive_message(self, size, skt):
        try:
            received_id = 0
            received_data = b''
            while len(received_data) < size:
                (rawData, addr) = skt.recvfrom(1024)
                data = pickle.loads(rawData)
                if random.uniform(0, 100) > dropRate:
                    skt.sendto(data[0].encode(), addr)
                send_id = int(data[0])
                self.update_log_signal.emit(1, "包编号 " + str(send_id) + " 收到,已发送确认包")
                if send_id == received_id + 1:
                    received_id = received_id + 1
                    received_data = received_data + data[1]
            self.update_log_signal.emit(0, "数据接收完毕！")
            self.update_message_signal.emit(received_data.decode())
            self.update_message_signal.emit("<font color=\"#66CD00\" size=\"2\">" + "--------------------" + "</font>")
            print(received_data.decode())
        except Exception as e:
            print(e)
            self.update_log_signal.emit(2, "服务已中断！")

    def receive_file(self, size, file_name, skt):
        try:
            received_id = 0
            received_size = 0
            self.update_message_signal.emit("开始接收文件：" + file_name)
            with open(file_name, 'wb') as f:
                while received_size < size:
                    (rawData, addr) = skt.recvfrom(1024)
                    data = pickle.loads(rawData)
                    if random.uniform(0, 100) > dropRate:
                        skt.sendto(data[0].encode(), addr)
                    send_id = int(data[0])
                    self.update_log_signal.emit(1, "包编号 " + str(send_id) + " 收到,已发送确认包")
                    if send_id == received_id + 1:
                        received_id = received_id + 1
                        f.write(data[1])
                        received_size = received_size + len(data[1])
                self.update_log_signal.emit(0, "数据接收完毕！")
                self.update_message_signal.emit("文件接收完毕！保存至：" + os.getcwd())
                self.update_message_signal.emit("<font color=\"#66CD00\" size=\"2\">" + "--------------------" + "</font>")
        except Exception as e:
            print(e)
            self.update_log_signal.emit(2, "服务已中断！")

    def run(self):
        while(run):
            print("开工！")
            self.receive_packet()


class ClientWindow(QMainWindow, Ui_udpServer):
    def __init__(self, parent=None):
        super(ClientWindow, self).__init__(parent)
        self.setupUi(self)
        self.setWindowIcon(QIcon('./udp.png'))
        self.serverIP.setText(DEST_IP)
        self.serverPort.setText(str(DEST_PORT))
        self.optButton.clicked.connect(self.server_control)
        self.modButton.clicked.connect(self.server_mod)
        self.dropNow.clicked.connect(self.drop_mod)
        self.print_log(0, "软件初始化完毕，欢迎使用！")

    @pyqtSlot()
    def server_control(self):
        global run
        if not run:
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
    def server_mod(self):
        global DEST_IP, DEST_PORT
        DEST_IP = self.serverIP.text()
        DEST_PORT = int(self.serverPort.text())
        if run:
            self.server_control()
        QMessageBox.information(self, "设置更新", "服务设置已更新！\t\n\n服务IP: " + DEST_IP + "\t\n服务端口: " + str(DEST_PORT) + "\n请重新启动服务！", QMessageBox.Yes)

    @pyqtSlot()
    def drop_mod(self):
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
        now_time = "<font color=\"#ffffff\" size=\"3\">" + html.escape("[" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "] ")
        if level == 0:
            self.log.append(now_time + "<font color=\"#1E90FF\" size=\"3\">" + html.escape(message) + "</font>")
        elif level == 1:
            self.log.append(now_time + "<font color=\"#66CD00\" size=\"3\">" + html.escape(message) + "</font>")
        elif level == 2:
            self.log.append(now_time + "<font color=\"#FF2D2D\" size=\"3\">" + html.escape(message) + "</font>")
        elif level == 3:
            self.log.append(now_time + "<font color=\"#000000\" size=\"3\">" + html.escape(message) + "</font>")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    clientWindow = ClientWindow()
    with open('qmc2-black.qss', 'r') as q:
        clientWindow.setStyleSheet(q.read())
    clientWindow.show()
    clientWindow.show()
    sys.exit(app.exec_())
