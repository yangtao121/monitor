from UI.monitor_ui import Ui_Monitor
from PyQt5.QtWidgets import QMainWindow, QApplication, QAction, QMessageBox, QVBoxLayout
from PyQt5.QtGui import QIcon
from pymavlink import mavutil
from PyQt5.QtCore import QTimer
import pyqtgraph as pg
import sys
import numpy as np


def data_expand(data):
    temp = data
    data = np.empty(data.shape[0] * 2)
    data[:temp.shape[0]] = temp
    return data


class control(QMainWindow):
    def __init__(self):
        super(control, self).__init__()
        self.timer = QTimer()
        self.ptr = 0
        self.data_roll = np.empty(31)
        self.data_pitch = np.empty(31)
        self.data_yaw = np.empty(31)
        self.data_speed_roll = np.empty(31)
        self.data_speed_pitch = np.empty(31)
        self.data_speed_yaw = np.empty(31)
        self.data_x = []
        self.InitUI()

    def InitUI(self):
        ui = Ui_Monitor()
        ui.setupUi(self)
        self.statusBar().showMessage("欢迎使用")
        pg.setConfigOptions(leftButtonPan=False)
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        connect = QAction(QIcon("src/link.png"), ' ', self)
        draw = QAction(QIcon("src/data-view.png"), ' ', self)
        connect.triggered.connect(self.link_UVA)
        draw.triggered.connect(self.draw_switch)
        ##############################################################
        self.roll = pg.PlotWidget()
        self.roll.setRange(xRange=[-300, 0])
        self.curve_roll = self.roll.plot()
        self.pitch = pg.PlotWidget()
        self.pitch.setRange(xRange=[-300, 0])
        self.curve_pitch = self.pitch.plot()
        self.yaw = pg.PlotWidget()
        self.yaw.setRange(xRange=[-300, 0])
        self.curve_yaw = self.yaw.plot()
        self.speed_roll = pg.PlotWidget()
        self.speed_roll.setRange(xRange=[-300, 0])
        self.curve_speed_roll = self.speed_roll.plot()
        self.speed_pitch = pg.PlotWidget()
        self.speed_pitch.setRange(xRange=[-300, 0])
        self.curve_speed_pitch = self.speed_pitch.plot()
        self.speed_yaw = pg.PlotWidget()
        self.speed_yaw.setRange(xRange=[-300, 0])
        self.curve_speed_yaw= self.speed_yaw.plot()
        ########################添加控件#########################
        plot_display = self.findChild(QVBoxLayout, 'roll')
        plot_display.addWidget(self.roll)
        plot_display = self.findChild(QVBoxLayout, 'pitch')
        plot_display.addWidget(self.pitch)
        plot_display = self.findChild(QVBoxLayout, 'yaw')
        plot_display.addWidget(self.yaw)
        plot_display = self.findChild(QVBoxLayout, 'rollspeed')
        plot_display.addWidget(self.speed_roll)
        plot_display = self.findChild(QVBoxLayout, 'pitchspeed')
        plot_display.addWidget(self.speed_pitch)
        plot_display = self.findChild(QVBoxLayout, 'yawspeed')
        plot_display.addWidget(self.speed_yaw)
        ######################################################
        self.menuBar().addAction(connect)
        self.menuBar().addAction(draw)
        self.show()

    def link_UVA(self):
        try:
            self.UVA = mavutil.mavlink_connection("/dev/ttyUSB0", baud=57600)
            reply = QMessageBox.question(self, '通知', '连接成功', QMessageBox.Yes)
            self.statusBar().showMessage("连接成功")
            # if reply == QMessageBox.Yes:
            #     self.draw_flag == 1

        except:
            reply = QMessageBox.question(self, "警告", "连接失败", QMessageBox.Yes)
            self.statusBar().showMessage("连接失败")
            # if reply == QMessageBox.Yes:
            #     self.draw_flag == 0

    def update(self):
        msg = self.UVA.recv_match(type='ATTITUDE', blocking=True)
        self.data_x.append(10 * self.ptr)
        self.data_roll[self.ptr] = msg.roll
        self.data_pitch[self.ptr] = msg.pitch
        self.data_yaw[self.ptr] = msg.yaw
        self.data_speed_roll[self.ptr] = msg.rollspeed
        self.data_speed_pitch[self.ptr] = msg.pitchspeed
        self.data_speed_yaw[self.ptr] = msg.yawspeed
        self.ptr += 1
        if self.ptr >= self.data_roll.shape[0]:
            # temp = self.data_vx
            # self.data_vx = np.empty(self.data_vx.shape[0] * 2)
            # self.data_vx[:temp.shape[0]] = temp
            self.data_roll = data_expand(self.data_roll)
            self.data_pitch = data_expand(self.data_pitch)
            self.data_yaw = data_expand(self.data_yaw)
            self.data_speed_roll = data_expand(self.data_speed_roll)
            self.data_speed_pitch = data_expand(self.data_speed_pitch)
            self.data_speed_yaw = data_expand(self.data_speed_yaw)

        # self.curve_vx.setData(self.data_x[:self.ptr], self.data_vx[:self.ptr])
        # self.curve_vx.setPos(-10 * self.ptr, 0)
        self.draw(self.curve_roll, self.data_roll)
        self.draw(self.curve_pitch, self.data_pitch)
        self.draw(self.curve_yaw, self.data_yaw)
        self.draw(self.curve_speed_roll, self.data_speed_roll)
        self.draw(self.curve_speed_pitch, self.data_speed_pitch)
        self.draw(self.curve_speed_yaw, self.data_speed_yaw)

    def draw(self, pen, data):
        pen.setData(self.data_x[:self.ptr], data[:self.ptr])
        pen.setPos(-10 * self.ptr, 0)

    def draw_switch(self):
        self.timer.timeout.connect(self.update)
        self.timer.start(200)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = control()
    sys.exit(app.exec_())
