# code:utf8
import socket
import time
import threading
import sys
import html
import pickle
from PyQt5.QtWidgets import QApplication, QMainWindow, QHeaderView, QAbstractItemView, QTableWidgetItem, QMessageBox
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

    def __init__(self, data, parent=None):
        super(SendThread, self).__init__(parent)
        self.data = data
        self.sendPackets = 0
        self.lossPackets = 0
        self.continuousLoss = 0
        print("sendThread")

    def buildPacket(self, data):
        size = len(data)
        self.update_log_signal.emit(0, "开始数据传送，总大小 " + str(size) + " Bytes")
        self.sendPacket(0, [str(0), str(size)])
        send_id = 1
        packData = [str(send_id)]
        packSize = len(packData)
        buffer = bytearray(b'')
        for i in range(0, size):
            packSize = packSize + len(data[i:i + 1])
            buffer = buffer + data[i:i + 1]
            if (packSize + 47 >= MAX_PACK_SIZE or i == size - 1):
                packData.append(buffer)
                print(packData)
                print("进入发包流程 编号" + str(send_id))
                self.sendPacket(send_id, packData)
                if(self.continuousLoss >= 10):
                    self.update_log_signal.emit(2, "发送失败！网络通讯出现异常，请检查服务端是否在线")
                    break
                send_id = send_id + 1
                print("包编号 " + str(send_id) + " 已确认到达")
                packData = [str(send_id)]
                packSize = len(packData)
                buffer = bytearray(b'')

    def sendPacket(self, send_id, packData):
        global resend
        resend = True
        while (resend and self.continuousLoss < 10):
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            subthread = threading.Thread(target=self.sendProcess, args=(send_id, pickle.dumps(packData), s))
            subthread.start()
            time.sleep(0.2)
            s.close()

    def sendProcess(self, send_id, data, s):
        global resend
        self.sendPackets = self.sendPackets + 1
        packetSize = s.sendto(data, (DEST_IP, DEST_PORT))
        try:
            (rawData, addr) = s.recvfrom(1024)
            if (int(rawData.decode()) == send_id):
                self.continuousLoss = 0
                resend = False
                self.update_table_signal.emit(str(send_id), str(packetSize), '确认到达')
                self.update_log_signal.emit(1, "包编号 " + str(send_id) + " 确认到达")
        except Exception:
            self.lossPackets = self.lossPackets + 1
            self.continuousLoss = self.continuousLoss + 1
            self.update_table_signal.emit(str(send_id), str(packetSize), '丢失，等待重传')
            self.update_log_signal.emit(2, "包编号 " + str(send_id) + " 丢失，正在重传...")
            print("包丢失，即将重传...")

    def run(self):
        print("开工！")
        self.buildPacket(self.data)
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
        self.send.clicked.connect(self.on_send_click)
        self.apply.clicked.connect(self.on_apply_click)
        self.print_log(0, "软件初始化完毕，欢迎使用！")

    @pyqtSlot()
    def on_send_click(self):
        data = self.input.toPlainText()
        if(data):
            self.input.clear()
            self.recentTable.setRowCount(0)
            self.send.setEnabled(False)
            self.send.setText("发送中")
            self.sendThread = SendThread(data.encode())
            self.sendThread.send_over_signal.connect(self.on_send_over)
            self.sendThread.update_table_signal.connect(self.update_table)
            self.sendThread.update_label_signal.connect(self.update_label)
            self.sendThread.update_log_signal.connect(self.print_log)
            self.sendThread.start()
            self.browser.append("<font color=\"#1E90FF\" size=\"2\">" + html.escape("------->>> " + DEST_IP + ":" + str(DEST_PORT)) + "</font>")
            self.browser.append(data)

    @pyqtSlot()
    def on_send_over(self):
        self.browser.append("<font color=\"#66CD00\" size=\"2\">" + "--------------------" + "</font>")
        self.send.setText("发送")
        self.send.setEnabled(True)

    @pyqtSlot(str, str, str)
    def update_table(self, packetID, size, message):
        rowCount = self.recentTable.rowCount()
        self.recentTable.setRowCount(rowCount + 1)
        print(rowCount)
        print(packetID)
        print(size)
        print(message)
        self.recentTable.setItem(rowCount, 0, QTableWidgetItem(packetID))
        self.recentTable.setItem(rowCount, 1, QTableWidgetItem(size))
        self.recentTable.setItem(rowCount, 2, QTableWidgetItem(message))
        self.recentTable.scrollToBottom()
        for index in range(self.recentTable.columnCount()):
            self.recentTable.item(rowCount, index).setTextAlignment(Qt.AlignCenter)

    @pyqtSlot(int, int)
    def update_label(self, sendPackets, lossPackets):
        self.recentAnal.setText("本次传送 " + str(sendPackets) + " 个包，重传 " + str(lossPackets) + " 个包")
        self.allSendPackets = self.allSendPackets + sendPackets
        self.allLossPackets = self.allLossPackets + lossPackets
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
        nowTime = "<font color=\"#000000\" size=\"3\">" + html.escape("[" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "] ")
        if(level == 0):
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