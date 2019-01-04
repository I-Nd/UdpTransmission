# code:utf8
import socket
import time
import threading
import sys
import html
import pickle
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QHeaderView, QAbstractItemView, QTableWidgetItem, QMessageBox, QFileDialog
from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal, Qt
from PyQt5.QtGui import QIcon
from client_ui import *

global DEST_IP, DEST_PORT, MAX_PACK_SIZE
DEST_IP = '127.0.0.1'
DEST_PORT = 6666
MAX_PACK_SIZE = 100


class SendThread(QThread):
    send_over_signal = pyqtSignal()
    update_table_signal = pyqtSignal(str, str, str)
    update_label_signal = pyqtSignal(int, int)
    update_log_signal = pyqtSignal(int, str)

    def __init__(self, data, file_name, parent=None):
        super(SendThread, self).__init__(parent)
        self.data = data
        self.fileName = file_name
        self.sendPackets = 0
        self.lossPackets = 0
        self.continuousLoss = 0
        print("sendThread")

    def build_message_packet(self, data):
        size = len(data)
        self.update_log_signal.emit(0, "开始数据传送，数据类型【消息】，总大小 " + str(size) + " Bytes")
        self.send_packet(0, [str(0), str(size), self.fileName])
        send_id = 1
        pack_data = [str(send_id)]
        pack_size = len(pack_data)
        buffer = bytearray(b'')
        for i in range(0, size):
            pack_size = pack_size + len(data[i:i + 1])
            buffer = buffer + data[i:i + 1]
            if pack_size + 47 >= MAX_PACK_SIZE or i == size - 1:
                pack_data.append(buffer)
                print(pack_data)
                print("进入发包流程 编号" + str(send_id))
                self.send_packet(send_id, pack_data)
                if self.continuousLoss >= 10:
                    self.update_log_signal.emit(2, "发送失败！网络通讯出现异常，请检查服务端是否在线")
                    break
                send_id = send_id + 1
                print("包编号 " + str(send_id) + " 已确认到达")
                pack_data = [str(send_id)]
                pack_size = len(pack_data)
                buffer = bytearray(b'')

    def build_file_packet(self, file):
        size = os.path.getsize(file)
        self.update_log_signal.emit(0, "开始数据传送，数据类型【文件】，总大小 " + str(size) + " Bytes")
        self.send_packet(0, [str(0), str(size), self.fileName])
        send_id = 1
        pack_data = [str(send_id)]
        pack_size = len(pack_data)
        buffer = bytearray(b'')
        with open(file, 'rb') as f:
            for i in range(0, size):
                pack_size = pack_size + 1
                buffer = buffer + f.read(1)
                if pack_size + 47 >= MAX_PACK_SIZE or i == size - 1:
                    pack_data.append(buffer)
                    print(pack_data)
                    print("进入发包流程 编号" + str(send_id))
                    self.send_packet(send_id, pack_data)
                    if self.continuousLoss >= 10:
                        self.update_log_signal.emit(2, "发送失败！网络通讯出现异常，请检查服务端是否在线")
                        break
                    send_id = send_id + 1
                    print("包编号 " + str(send_id) + " 已确认到达")
                    pack_data = [str(send_id)]
                    pack_size = len(pack_data)
                    buffer = bytearray(b'')
        f.close()

    def send_packet(self, send_id, pack_data):
        global resend
        resend = True
        while resend and self.continuousLoss < 10:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            subthread = threading.Thread(target=self.send_process, args=(send_id, pickle.dumps(pack_data), s))
            subthread.start()
            time.sleep(0.2)
            s.close()

    def send_process(self, send_id, data, s):
        global resend
        self.sendPackets = self.sendPackets + 1
        packet_size = s.sendto(data, (DEST_IP, DEST_PORT))
        try:
            (rawData, addr) = s.recvfrom(1024)
            if int(rawData.decode()) == send_id:
                self.continuousLoss = 0
                resend = False
                self.update_table_signal.emit(str(send_id), str(packet_size), '确认到达')
                self.update_log_signal.emit(1, "包编号 " + str(send_id) + " 确认到达")
        except Exception as e:
            self.lossPackets = self.lossPackets + 1
            self.continuousLoss = self.continuousLoss + 1
            self.update_table_signal.emit(str(send_id), str(packet_size), '丢失，等待重传')
            self.update_log_signal.emit(2, "包编号 " + str(send_id) + " 丢失，正在重传...")
            print("包丢失，即将重传...")
            print(e)

    def run(self):
        print("开工！")
        if self.fileName:
            print("文件传送开始")
            self.build_file_packet(self.data)
        else:
            print("消息传送开始")
            self.build_message_packet(self.data)
        self.update_label_signal.emit(self.sendPackets, self.lossPackets)
        self.update_log_signal.emit(0, "数据传送完毕！")
        self.send_over_signal.emit()


class ClientWindow(QMainWindow, Ui_udpClient):
    def __init__(self, parent=None):
        super(ClientWindow, self).__init__(parent)
        self.setupUi(self)
        self.setWindowIcon(QIcon('./udp.png'))
        self.serverIP.setText(DEST_IP)
        self.serverPort.setText(str(DEST_PORT))
        self.packetLimit.setText(str(MAX_PACK_SIZE))
        self.recentTable.setColumnWidth(0, 60)
        self.recentTable.setColumnWidth(1, 60)
        self.recentTable.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.recentTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.recentTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.allSendPackets = 0
        self.allLossPackets = 0
        self.selectedFile = ""
        self.send.clicked.connect(self.on_send_click)
        self.apply.clicked.connect(self.on_apply_click)
        self.chooseFile.clicked.connect(self.openfile)
        self.print_log(0, "软件初始化完毕，欢迎使用！")

    @pyqtSlot()
    def on_send_click(self):
        data = self.input.toPlainText()
        if data:
            self.recentTable.setRowCount(0)
            self.send.setEnabled(False)
            self.send.setText("发送中")
            self.sendThread = SendThread(data.encode(), "")
            self.sendThread.send_over_signal.connect(self.on_send_over)
            self.sendThread.update_table_signal.connect(self.update_table)
            self.sendThread.update_label_signal.connect(self.update_label)
            self.sendThread.update_log_signal.connect(self.print_log)
            self.sendThread.start()
            self.browser.append("<font color=\"#1E90FF\" size=\"2\">" + html.escape("------->>> " + DEST_IP + ":" + str(DEST_PORT)) + "</font>")
            self.browser.append(data)
            self.input.clear()
            self.file.setText("未选择文件...")
            self.selectedFile = ""
        elif self.selectedFile:
            self.recentTable.setRowCount(0)
            self.send.setEnabled(False)
            self.send.setText("发送中")
            self.sendThread = SendThread(self.selectedFile, self.selectedFile.split('/')[-1])
            self.sendThread.send_over_signal.connect(self.on_send_over)
            self.sendThread.update_table_signal.connect(self.update_table)
            self.sendThread.update_label_signal.connect(self.update_label)
            self.sendThread.update_log_signal.connect(self.print_log)
            self.sendThread.start()
            self.browser.append("<font color=\"#1E90FF\" size=\"2\">" + html.escape("------->>> " + DEST_IP + ":" + str(DEST_PORT)) + "</font>")
            self.browser.append("正在发送文件：" + self.selectedFile)
            self.input.clear()
            self.file.setText("未选择文件...")
            self.selectedFile = ""

    @pyqtSlot()
    def on_send_over(self):
        self.browser.append("<font color=\"#66CD00\" size=\"2\">" + "--------------------" + "</font>")
        self.send.setText("发送")
        self.send.setEnabled(True)

    @pyqtSlot()
    def openfile(self):
        file_name = QFileDialog.getOpenFileName(self, '选择文件', '', '')
        print(file_name)
        if file_name:
            self.selectedFile = file_name[0]
            self.file.setText(file_name[0].split('/')[-1])

    @pyqtSlot(str, str, str)
    def update_table(self, packet_id, size, message):
        row_count = self.recentTable.rowCount()
        self.recentTable.setRowCount(row_count + 1)
        print(row_count)
        print(packet_id)
        print(size)
        print(message)
        self.recentTable.setItem(row_count, 0, QTableWidgetItem(packet_id))
        self.recentTable.setItem(row_count, 1, QTableWidgetItem(size))
        self.recentTable.setItem(row_count, 2, QTableWidgetItem(message))
        self.recentTable.scrollToBottom()
        for index in range(self.recentTable.columnCount()):
            self.recentTable.item(row_count, index).setTextAlignment(Qt.AlignCenter)

    @pyqtSlot(int, int)
    def update_label(self, send_packets, loss_packets):
        self.recentAnal.setText("本次传送 " + str(send_packets) + " 个包，重传 " + str(loss_packets) + " 个包")
        self.allSendPackets = self.allSendPackets + send_packets
        self.allLossPackets = self.allLossPackets + loss_packets
        self.allAnal.setText("累计传送 " + str(self.allSendPackets) + " 个包，重传 " + str(self.allLossPackets) + " 个包")

    @pyqtSlot()
    def on_apply_click(self):
        global DEST_IP, DEST_PORT, MAX_PACK_SIZE
        DEST_IP = self.serverIP.text()
        DEST_PORT = int(self.serverPort.text())
        MAX_PACK_SIZE = int(self.packetLimit.text())
        QMessageBox.information(self, "设置更新", "连接设置已更新！\t\n\n服务器IP: " + DEST_IP + "\t\n端口号: " + str(DEST_PORT) + "\n包大小限制: " + str(MAX_PACK_SIZE), QMessageBox.Yes)

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
    sys.exit(app.exec_())
