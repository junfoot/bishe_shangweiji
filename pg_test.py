import sys
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
import pyqtgraph as pg
import numpy as np
import test1
import test2
import serial
import pygame_test
import pygame
import random

ser = serial.Serial()


class PgUi(QMainWindow):
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
        self.ui.imageShow.addWidget(self.pw1)
        self.ui.imageShow.addWidget(self.pw2)
        self.ui.imageShow.addWidget(self.pw3)
        self.curve1 = self.pw1.plot(pen='r')
        self.curve2 = self.pw1.plot(pen='g')
        self.curve3 = self.pw1.plot(pen='b')
        self.curve4 = self.pw2.plot(pen='r')
        self.curve5 = self.pw3.plot(pen='b')

        # 绑定按键事件
        self.ui.debugButton.clicked.connect(self.debug_start)
        self.ui.stopButton.clicked.connect(self.debug_stop)
        self.ui.transButton.clicked.connect(self.data_send)
        self.ui.posButton.clicked.connect(self.pos_send)
        self.ui.velButton.clicked.connect(self.vel_send)
        self.ui.torButton.clicked.connect(self.tor_send)
        self.ui.nextButton.clicked.connect(self.next_page)

        # 调整LCD
        self.ui.lcdpin.setStyleSheet("border: 2px solid black; color: black; background: silver;")
        self.ui.lcdvin.setStyleSheet("border: 2px solid black; color: black; background: silver;")
        self.ui.lcdtin.setStyleSheet("border: 2px solid black; color: black; background: silver;")
        self.ui.lcdintemp.setStyleSheet("border: 2px solid black; color: black; background: silver;")
        self.ui.lcdtemp.setStyleSheet("border: 2px solid black; color: red; background: silver;")
        self.ui.lcdaux.setStyleSheet("border: 2px solid black; color: black; background: silver;")

        # 设置下拉框
        self.ui.inputmode.addItems(['passthrough', 'torque_ramp', 'vel_ramp', 'pos_filter', 'trap_traj'])
        self.ui.inputmode.currentIndexChanged.connect(self.input_mode_select)
        self.ui.controlmode.addItems(['torque', 'velocity', 'position'])
        self.ui.controlmode.currentIndexChanged.connect(self.control_mode_select)

        # 开启线程
        self.work = ThreadOne()

    # 绘制串口相关图形与数据
    def serial_draw(self, data_list, data_split, data, flag):
        if flag:
            self.curve1.setData(np.arange(len(data_list[0])), data_list[0])
            self.curve2.setData(np.arange(len(data_list[1])), data_list[1])
            self.curve3.setData(np.arange(len(data_list[2])), data_list[2])
            self.curve4.setData(np.arange(len(data_list[3])), data_list[3])
            self.curve5.setData(np.arange(len(data_list[4])), data_list[4])

            self.ui.lcdpin.display("{:.2f}".format(float(data_split[6])))
            self.ui.lcdvin.display("{:.2f}".format(float(data_split[7])))
            self.ui.lcdtin.display("{:.2f}".format(float(data_split[8])))
            self.ui.lcdintemp.display("{:.2f}".format(float(data_split[9])))
            self.ui.lcdtemp.display("{:.2f}".format(float(data_split[10])))
            self.ui.lcdaux.display("{:.2f}".format(float(data_split[11])))

        else:
            self.ui.serialReceive.insertPlainText(data)

        textCursor = self.ui.serialReceive.textCursor()
        textCursor.movePosition(textCursor.End)
        self.ui.serialReceive.setTextCursor(textCursor)

    def debug_start(self):
        # 打开串口
        self.work.serial_open()
        # 50Hz
        self.work.timer_serial.start(20)
        self.work.trigger.connect(self.serial_draw)
        self.work.start()

    def data_send(self):
        if ser.isOpen():
            input_s = self.ui.serialTransmit.toPlainText()
            if input_s != "":
                # 发送数据
                input_s = input_s.encode('utf-8')
                ser.write(input_s)
        else:
            pass

    def debug_stop(self):
        self.work.timer_serial.stop()
        ser.close()

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
                ser.write('p'.encode('utf-8'))
            elif text_index == 1:
                ser.write('v'.encode('utf-8'))
            elif text_index == 2:
                ser.write('t'.encode('utf-8'))
        else:
            pass

    def next_page(self):
        self.debug_stop()
        self.hide()
        gameui.show()


class GameUi(QMainWindow):
    def __init__(self):
        super(GameUi, self).__init__()

        # 定义当前窗口对象
        self.ui = test2.Ui_Form()
        self.ui.setupUi(self)

        # 绑定按键事件
        self.ui.pushButton.clicked.connect(self.front_page)

        self.game_work = ThreadTwo()
        self.game_work.trigger.connect(self.pygame_draw)
        self.game_work.start()

    def pygame_draw(self, surface):
        # 将pygame绘制到界面上
        mygame = pygame_test.ImageWidget(surface)

        # 删除布局中之前的画面
        item_list = list(range(self.ui.verticalLayout.count()))
        item_list.reverse()  # 倒序删除，避免影响布局顺序
        for i in item_list:
            item = self.ui.verticalLayout.itemAt(i)
            self.ui.verticalLayout.removeItem(item)
            if item.widget():
                item.widget().deleteLater()

        # 添加当前画面
        self.ui.verticalLayout.addWidget(mygame)

    def front_page(self):
        self.hide()
        pgui.show()


class ThreadOne(QThread):
    trigger = pyqtSignal(list, list, str, int)

    def __init__(self):
        super().__init__()

        # 添加定时器
        self.timer_serial = QTimer()
        self.timer_serial.timeout.connect(self.run)

        # 定义待绘制数据
        # ia ib ic pos vel
        self.data_list = [[] for _ in range(5)]

    def serial_open(self):
        ser.port = "COM3"
        ser.baudrate = 115200
        ser.bytesize = 8
        ser.stopbits = 1
        ser.parity = "N"
        ser.open()
        if ser.isOpen:
            print("COM open successfully")
        else:
            print("COM open failed")

    def run(self):
        flag = 0
        data = ""
        data_split = []
        try:
            data = str(ser.readline(), encoding="utf-8")
        except UnicodeDecodeError:
            pass
        if data != "":
            data_split = data.split()
            if data_split[0] == 'mute':
                flag = 1
                self.list_add(self.data_list[0], float(data_split[1]))
                self.list_add(self.data_list[1], float(data_split[2]))
                self.list_add(self.data_list[2], float(data_split[3]))
                self.list_add(self.data_list[3], float(data_split[4]))
                self.list_add(self.data_list[4], float(data_split[5]))

        self.trigger.emit(self.data_list, data_split, data, flag)

    def list_add(self, data, new_data):
        length = 300
        data.append(new_data)
        if len(data) > length:
            data.pop(0)


class ThreadTwo(QThread):
    trigger = pyqtSignal(object)

    def __init__(self):
        super(ThreadTwo, self).__init__()

        # pygame初始化
        self.running = True
        self.clock = pygame.time.Clock()

        # self.s = pygame.display.set_mode((600, 400))
        self.s = pygame.Surface((600, 400))

    # pygame运行
    def run(self):
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load("斗♂地主.mp3")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        while self.running:
            # FPS
            self.clock.tick(60)
            # Process input (events)
            for event in pygame.event.get():
                # check for closing window
                if event.type == pygame.QUIT:
                    self.running = False

            # 开始游戏
            self.s.fill((255, 0, 0))

            pos1 = random.randint(50, 150)
            pos2 = random.randint(50, 150)
            pygame.draw.circle(self.s, (255, 255, 255), (pos1, pos2), 10)

            self.trigger.emit(self.s)
            # pygame.display.flip()

        pygame.quit()


if __name__ == '__main__':
    # pyqt5程序都需要QApplication对象
    app = QApplication(sys.argv)
    # 实例化
    pgui = PgUi()
    gameui = GameUi()
    # 显示窗口
    pgui.show()
    # 确保程序完整推出
    sys.exit(app.exec_())
