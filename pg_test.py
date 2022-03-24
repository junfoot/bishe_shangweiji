import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QThread, pyqtSignal
import pyqtgraph as pg
import numpy as np
import test1
import serial
import serial.tools.list_ports
import os

ser = serial.Serial()


class PgUi(QMainWindow):
    global ser

    def __init__(self):
        super().__init__()

        # 定义当前窗口对象
        self.ui = test1.Ui_MainWindow()
        self.ui.setupUi(self)

        # pyqtgraph绘图设置
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')

        # 添加绘图控件
        self.pw1 = pg.PlotWidget(enableAutoRange=True)
        self.pw2 = pg.PlotWidget(enableAutoRange=True)
        self.pw3 = pg.PlotWidget(enableAutoRange=True)
        self.pw4 = pg.PlotWidget(enableAutoRange=True)
        self.ui.imageShow.addWidget(self.pw1)
        self.ui.imageShow.addWidget(self.pw2)
        self.ui.imageShow.addWidget(self.pw3)
        self.ui.imageShow.addWidget(self.pw4)
        self.curve1 = self.pw1.plot(pen='r')
        self.curve2 = self.pw1.plot(pen='g')
        self.curve3 = self.pw1.plot(pen='b')
        self.curve4 = self.pw2.plot(pen='r')
        self.curve5 = self.pw3.plot(pen='b')
        self.curve6 = self.pw4.plot(pen='r')

        # 绑定按键事件
        self.ui.debugButton.clicked.connect(self.debug)
        self.ui.transButton.clicked.connect(self.data_send)
        self.ui.posButton.clicked.connect(self.pos_send)
        self.ui.velButton.clicked.connect(self.vel_send)
        self.ui.torButton.clicked.connect(self.tor_send)
        self.ui.nextButton.clicked.connect(self.next_page)
        self.ui.detectButton.clicked.connect(self.serial_list)
        self.ui.portButton.clicked.connect(self.port_send)

        self.ui.port.editingFinished.connect(self.port_send)

        # 调整LCD
        self.ui.lcdpin.setStyleSheet("border: 2px solid black; color: black; background: silver;")
        self.ui.lcdvin.setStyleSheet("border: 2px solid black; color: black; background: silver;")
        self.ui.lcdtin.setStyleSheet("border: 2px solid black; color: black; background: silver;")
        self.ui.lcdintemp.setStyleSheet("border: 2px solid black; color: black; background: silver;")
        self.ui.lcdtemp.setStyleSheet("border: 2px solid black; color: red; background: silver;")
        self.ui.lcdaux.setStyleSheet("border: 2px solid black; color: black; background: silver;")
        self.ui.lcdmode.setStyleSheet("border: 2px solid black; color: black; background: silver;")
        self.ui.lcdinput.setStyleSheet("border: 2px solid black; color: black; background: silver;")
        self.ui.lcdcontrol.setStyleSheet("border: 2px solid black; color: black; background: silver;")

        # 设置下拉框
        self.ui.inputmode.addItems(['passthrough', 'torque_ramp', 'vel_ramp', 'pos_filter', 'trap_traj'])
        self.ui.inputmode.currentIndexChanged.connect(self.input_mode_select)
        self.ui.controlmode.addItems(['torque', 'velocity', 'position'])
        self.ui.controlmode.currentIndexChanged.connect(self.control_mode_select)
        self.ui.mode.addItems(['menu', 'motor', 'calibration', 'anticogging'])
        self.ui.mode.currentIndexChanged.connect(self.mode_select)

        # 开启线程
        self.work = ThreadOne()
        self.game_work = ThreadTwo()

        self.port = "COM3"
        self.serial_running = False
        # 定义待绘制数据
        # ia ib ic pos vel
        self.data_list = [[] for _ in range(5)]
        self.data_anti = []
        self.oktoshow = False

    def serial_list(self):
        ports_list = list(serial.tools.list_ports.comports())
        if len(ports_list) <= 0:
            # print("无串口设备。")
            self.ui.serialReceive.insertPlainText("无串口设备。\r\n")
        else:
            # print("可用的串口设备如下：")
            self.ui.serialReceive.insertPlainText("可用的串口设备如下：\r\n")
            for comport in ports_list:
                # print(list(comport)[0], list(comport)[1])
                self.ui.serialReceive.insertPlainText(list(comport)[0] + list(comport)[1] + '\r\n')

    # 绘制串口相关图形与数据
    def serial_draw(self, data):
        if data != b'':
            data_split = data.split(b' ')
            if data_split[0] == b'm':
                self.list_add(self.data_list[0], float(data_split[1]))
                self.list_add(self.data_list[1], float(data_split[2]))
                self.list_add(self.data_list[2], float(data_split[3]))
                self.list_add(self.data_list[3], float(data_split[4]))
                self.list_add(self.data_list[4], float(data_split[5]))

                self.curve1.setData(np.arange(len(self.data_list[0])), self.data_list[0])
                self.curve2.setData(np.arange(len(self.data_list[1])), self.data_list[1])
                self.curve3.setData(np.arange(len(self.data_list[2])), self.data_list[2])
                self.curve4.setData(np.arange(len(self.data_list[3])), self.data_list[3])
                self.curve5.setData(np.arange(len(self.data_list[4])), self.data_list[4])

                # lcd显示
                self.ui.lcdintemp.display("{:.2f}".format(float(data_split[6])))
                self.ui.lcdtemp.display("{:.2f}".format(float(data_split[7])))
                self.ui.lcdaux.display("{:.2f}".format(float(data_split[8])))
                self.oktoshow = True
            elif data_split[0] == b'q':
                # lcd显示
                self.ui.lcdmode.display(int(data_split[1]))
                self.ui.lcdinput.display(int(data_split[2]))
                self.ui.lcdcontrol.display(int(data_split[3]))
                self.ui.lcdpin.display("{:.2f}".format(float(data_split[4])))
                self.ui.lcdvin.display("{:.2f}".format(float(data_split[5])))
                self.ui.lcdtin.display("{:.2f}".format(float(data_split[6])))
            elif data_split[0] == b's':
                self.data_anti.append(float(data_split[1]))
                self.curve6.setData(np.arange(len(self.data_anti)), self.data_anti)

            # 显示其他信息
            elif self.oktoshow:
                data_str = data.decode()
                self.ui.serialReceive.insertPlainText(data_str)

        # text_cursor = self.ui.serialReceive.textCursor()
        # text_cursor.movePosition(text_cursor.End)
        # self.ui.serialReceive.setTextCursor(text_cursor)

    def list_add(self, data, new_data):
        length = 300
        data.append(new_data)
        if len(data) > length:
            data.pop(0)

    def port_send(self):
        self.port = self.ui.port.text()
        self.ui.serialReceive.insertPlainText(self.port + '\r\n')
        # print(self.port)

    def debug(self):
        # 打开串口
        if not ser.isOpen():
            self.serial_running = True
            self.ui.debugButton.setText("STOP")

            # 打开串口
            ser.port = self.port
            ser.baudrate = 115200
            ser.timeout = 0.01
            try:
                ser.open()
            except Exception as e:
                self.ui.serialReceive.insertPlainText(repr(e) + '\r\n')
            if ser.isOpen():
                print("COM open successfully")
            else:
                print("COM open failed")

            # 50Hz
            self.work.trigger.connect(self.serial_draw)
            self.work.start()
        # 关闭串口
        else:
            self.serial_running = False
            self.ui.debugButton.setText("START")

    def data_send(self):
        if ser.isOpen():
            input_s = self.ui.serialTransmit.toPlainText()
            if input_s != "":
                # 发送数据
                input_s = input_s.encode('utf-8')
                ser.write(input_s)
        else:
            pass

    def pos_send(self):
        if ser.isOpen():
            input_s = self.ui.pin.text()
            if input_s != "":
                input_s = ('pin ' + input_s).encode('utf-8')
                # 发送数据
                ser.write(input_s)
        else:
            pass

    def vel_send(self):
        if ser.isOpen():
            input_s = self.ui.vin.text()
            if input_s != "":
                input_s = ('vin ' + input_s).encode('utf-8')
                # 发送数据
                ser.write(input_s)
        else:
            pass

    def tor_send(self):
        if ser.isOpen():
            input_s = self.ui.tin.text()
            if input_s != "":
                input_s = ('tin ' + input_s).encode('utf-8')
                # 发送数据
                ser.write(input_s)
        else:
            pass

    def mode_select(self):
        if ser.isOpen():
            text_index = self.ui.mode.currentIndex()
            if text_index == 0:
                ser.write('1'.encode('utf-8'))
            elif text_index == 1:
                ser.write('2'.encode('utf-8'))
            elif text_index == 2:
                ser.write('3'.encode('utf-8'))
            elif text_index == 3:
                ser.write('4'.encode('utf-8'))
        else:
            pass

    def input_mode_select(self):
        if ser.isOpen():
            text_index = self.ui.inputmode.currentIndex()
            if text_index == 0:
                ser.write('a'.encode('utf-8'))
            elif text_index == 1:
                ser.write('s'.encode('utf-8'))
            elif text_index == 2:
                ser.write('d'.encode('utf-8'))
            elif text_index == 3:
                ser.write('f'.encode('utf-8'))
            elif text_index == 4:
                ser.write('g'.encode('utf-8'))
        else:
            pass

    def control_mode_select(self):
        if ser.isOpen():
            text_index = self.ui.controlmode.currentIndex()
            if text_index == 0:
                ser.write('t'.encode('utf-8'))
            elif text_index == 1:
                ser.write('v'.encode('utf-8'))
            elif text_index == 2:
                ser.write('p'.encode('utf-8'))
        else:
            pass

    def next_page(self):
        # 自动关闭串口
        self.serial_running = False
        self.ui.debugButton.setText("START")
        self.game_work.start()


# 串口接收
class ThreadOne(QThread):
    trigger = pyqtSignal(bytes)
    global ser

    def __init__(self):
        super().__init__()

    def run(self):
        while True:
            if not pgui.serial_running:
                break
            if ser.isOpen():
                try:
                    data = ser.readline()
                    self.trigger.emit(data)
                except Exception as e:
                    pgui.ui.serialReceive.insertPlainText('1   ' + repr(e) + '\r\n')
        # 串口停止
        ser.close()
        self.quit()
        pgui.oktoshow = False


# 游戏运行
class ThreadTwo(QThread):
    def __init__(self):
        super(ThreadTwo, self).__init__()

    # pygame运行
    def run(self):
        os.chdir('plane-shooter')
        # os.system('python main.py')
        os.system('main.exe')
        os.chdir(os.path.abspath(os.path.dirname(os.getcwd())))


if __name__ == '__main__':
    # pyqt5程序都需要QApplication对象
    app = QApplication(sys.argv)
    # 实例化
    pgui = PgUi()
    # 显示窗口
    pgui.show()
    # 确保程序完整推出
    sys.exit(app.exec_())
