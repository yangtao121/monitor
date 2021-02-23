import sys
import threading
import time

import pyqtgraph as pg
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QWidget, QGridLayout, QTabWidget, QPushButton
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.Qt import Qt
from PyQt5.QtCore import pyqtSlot
from virtual_rod import ControlButton

from pymavlink import mavutil
import airsim

import numpy as np
import quaternion

from UI.monitorV2 import Ui_MainWindow


def data_expand(data):
    temp = data
    data = np.empty(data.shape[0] * 2)
    data[:temp.shape[0]] = temp
    return data


class UI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.mod = 0
        self.run_flag = True

        # 记录无人机在x-y平面的位置
        self.x_y = [0, 0]

        # 鼠标参数press
        self.is_move = False

        # control btn flag
        self.take_off_flag = False
        self.land_flag = False

        # control_mod设置，0直接控制螺旋桨转速控制模式
        # 1使用虚拟摇杆控制
        self.control_mod = 0
        self.vmotor1 = 0
        self.vmotor2 = 0
        self.vmotor3 = 0
        self.vmotor4 = 0

        self.ptr = 0
        self.data_roll = np.empty(31)
        self.data_pitch = np.empty(31)
        self.data_yaw = np.empty(31)
        self.data_speed_roll = np.empty(31)
        self.data_speed_pitch = np.empty(31)
        self.data_speed_yaw = np.empty(31)
        self.data_x_ = np.empty(31)
        self.data_y = np.empty(31)
        self.data_z = np.empty(31)
        self.data_vx = np.empty(31)
        self.data_vy = np.empty(31)
        self.data_vz = np.empty(31)
        self.data_x = []

        self.InitUI()

    def InitUI(self):
        ui = Ui_MainWindow()
        ui.setupUi(self)

        # 摇杆按钮
        self.control_button = ControlButton()
        # print(self.control_button.size())
        self.control_widget = self.findChild(QTabWidget, 'control_widget')
        self.take_off_btn = self.findChild(QPushButton, 'take_off')
        self.land_btn = self.findChild(QPushButton, 'land')

        # pyqtgraph全局参数
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        pg.setConfigOptions(useOpenGL=True)

        # 添加画图控件
        self.pw_omega_roll = pg.PlotWidget()
        self.pw_omega_roll.setRange(xRange=[-300, 0])
        self.curve_omega_roll = self.pw_omega_roll.plot(pen=(0, 0, 0))

        self.pw_omega_pitch = pg.PlotWidget()
        self.pw_omega_pitch.setRange(xRange=[-300, 0])
        self.curve_omega_pitch = self.pw_omega_pitch.plot(pen=(0, 0, 0))

        self.pw_omega_yaw = pg.PlotWidget()
        self.pw_omega_yaw.setRange(xRange=[-300, 0])
        self.curve_omega_yaw = self.pw_omega_yaw.plot(pen=(0, 0, 0))

        self.pw_roll = pg.PlotWidget()
        self.pw_roll.setRange(xRange=[-300, 0])
        self.curve_roll = self.pw_roll.plot(pen=(0, 0, 0))

        self.pw_pitch = pg.PlotWidget()
        self.pw_pitch.setRange(xRange=[-300, 0])
        self.curve_pitch = self.pw_pitch.plot(pen=(0, 0, 0))

        self.pw_yaw = pg.PlotWidget()
        self.pw_yaw.setRange(xRange=[-300, 0])
        self.curve_yaw = self.pw_yaw.plot(pen=(0, 0, 0))

        self.pw_vx = pg.PlotWidget()
        self.pw_vx.setRange(xRange=[-300, 0])
        self.curve_vx = self.pw_vx.plot(pen=(0, 0, 0))

        self.pw_vy = pg.PlotWidget()
        self.pw_vy.setRange(xRange=[-300, 0])
        self.curve_vy = self.pw_vy.plot(pen=(0, 0, 0))

        self.pw_vz = pg.PlotWidget()
        self.pw_vz.setRange(xRange=[-300, 0])
        self.curve_vz = self.pw_vz.plot(pen=(0, 0, 0))

        self.pw_x = pg.PlotWidget()
        self.pw_x.setRange(xRange=[-300, 0])
        self.curve_x = self.pw_x.plot(pen=(0, 0, 0))

        self.pw_y = pg.PlotWidget()
        self.pw_y.setRange(xRange=[-300, 0])
        self.curve_y = self.pw_y.plot(pen=(0, 0, 0))

        self.pw_z = pg.PlotWidget()
        self.pw_z.setRange(xRange=[-300, 0])
        self.curve_z = self.pw_z.plot(pen=(0, 0, 0))

        plot_display = self.findChild(QVBoxLayout, 'speed_x')
        plot_display.addWidget(self.pw_vx)
        plot_display = self.findChild(QVBoxLayout, 'speed_y')
        plot_display.addWidget(self.pw_vy)
        plot_display = self.findChild(QVBoxLayout, 'speed_z')
        plot_display.addWidget(self.pw_vz)
        plot_display = self.findChild(QVBoxLayout, 'p_x')
        plot_display.addWidget(self.pw_x)
        plot_display = self.findChild(QVBoxLayout, 'p_y')
        plot_display.addWidget(self.pw_y)
        plot_display = self.findChild(QVBoxLayout, 'p_z')
        plot_display.addWidget(self.pw_z)

        plot_display = self.findChild(QVBoxLayout, 'omega_roll')
        plot_display.addWidget(self.pw_omega_roll)
        plot_display = self.findChild(QVBoxLayout, 'omega_pitch')
        plot_display.addWidget(self.pw_omega_pitch)
        plot_display = self.findChild(QVBoxLayout, 'omega_yaw')
        plot_display.addWidget(self.pw_omega_yaw)
        plot_display = self.findChild(QVBoxLayout, 'roll')
        plot_display.addWidget(self.pw_roll)
        plot_display = self.findChild(QVBoxLayout, 'pitch')
        plot_display.addWidget(self.pw_pitch)
        plot_display = self.findChild(QVBoxLayout, 'yaw')
        plot_display.addWidget(self.pw_yaw)
        control_button = self.findChild(QGridLayout, 'rod')
        control_button.addWidget(self.control_button)

        self.statusBar().show()
        ############################################################
        self.log_display = self.findChild(QWidget, 'log_display')
        self.mod_switch = self.findChild(QWidget, 'mod_switch')
        self.mod_switch.activated[str].connect(self.mod_selector)

        self.checkM1 = self.findChild(QWidget, 'checkM1')
        self.checkM2 = self.findChild(QWidget, 'checkM2')
        self.checkM3 = self.findChild(QWidget, 'checkM3')
        self.checkM4 = self.findChild(QWidget, 'checkM4')

        self.motor1 = self.findChild(QWidget, 'motor1')
        self.motor1.valueChanged.connect(self.control)
        self.motor2 = self.findChild(QWidget, 'motor2')
        self.motor2.valueChanged.connect(self.control)
        self.motor3 = self.findChild(QWidget, 'motor3')
        self.motor3.valueChanged.connect(self.control)
        self.motor4 = self.findChild(QWidget, 'motor4')
        self.motor4.valueChanged.connect(self.control)

        self.motor_all = self.findChild(QWidget, 'motor_all')
        self.motor_all.valueChanged.connect(self.control_all)

        self.control_widget.tabBarClicked.connect(self.control_widget_change)

        self.take_off_btn.clicked.connect(self.take_off_trigger)
        self.land_btn.clicked.connect(self.land_trigger)

        self.control_button.view.MousePress.connect(self.do_mousePressEvent)
        self.control_button.view.MouseRelease.connect(self.do_mouseReleaseEvent)
        self.control_button.view.MouseMove.connect(self.do_mouseMoveEvent)

        self.InitLink()
        self.control_widget_change(0)

        # 等待任务接入
        t1 = threading.Thread(target=self.run_mod, name='air_run')
        t1.start()
        t2 = threading.Thread(target=self.controller, name='controller')
        t2.start()
        # t_collect_data = threading.Thread(target=self.collect_virtual_data, name='collect_data')
        # t_collect_data.start()

        self.show()

    def run_mod(self):
        while self.run_flag:
            if self.mod != 0:
                while self.mod == 1 and self.virtual_connect:
                    self.update_virtual()
                    time.sleep(1)
                while self.mod == 2 and self.real_connect:
                    self.update_test()
                    time.sleep(1)
            time.sleep(1)

    def mod_selector(self, text):
        if text == '选择模式':
            self.mod = 0
        elif text == '仿真模式':
            self.mod = 1
            self.log_display.append("当前模式：仿真模式")
            self.log_display.moveCursor(QTextCursor.End)
            self.statusBar().showMessage("仿真模式")
        else:
            self.mod = 2
            self.mod = 1
            self.log_display.append("当前模式：测试模式")
            self.log_display.moveCursor(QTextCursor.End)
            self.statusBar().showMessage("测试模式")

    def closeEvent(self, event):
        self.run_flag = False

    def update_virtual(self):
        # position, linear_velocity, angular_velocity, linear_acceleration, angular_acceleration, angle = self.get_virtual_data()
        self.data_x.append(10 * self.ptr)
        self.data_roll[self.ptr] = self.angle[0]
        self.data_pitch[self.ptr] = self.angle[1]
        self.data_yaw[self.ptr] = self.angle[2]
        self.data_speed_roll[self.ptr] = self.angular_acceleration[0]
        self.data_speed_pitch[self.ptr] = self.angular_acceleration[1]
        self.data_speed_yaw[self.ptr] = self.angular_acceleration[2]
        self.data_vx[self.ptr] = self.linear_velocity[0]
        self.data_vy[self.ptr] = self.linear_velocity[1]
        self.data_vz[self.ptr] = self.linear_velocity[2]
        self.data_x_[self.ptr] = self.position[0]
        self.data_y[self.ptr] = self.position[1]
        self.data_z[self.ptr] = self.position[2]
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
            self.data_vx = data_expand(self.data_vx)
            self.data_vy = data_expand(self.data_vy)
            self.data_vz = data_expand(self.data_vz)
            self.data_x_ = data_expand(self.data_x_)
            self.data_y = data_expand(self.data_y)
            self.data_z = data_expand(self.data_z)

        # self.curve_vx.setData(self.data_x[:self.ptr], self.data_vx[:self.ptr])
        # self.curve_vx.setPos(-10 * self.ptr, 0)
        self.draw(self.curve_roll, self.data_roll)
        self.draw(self.curve_pitch, self.data_pitch)
        self.draw(self.curve_yaw, self.data_yaw)
        self.draw(self.curve_omega_roll, self.data_speed_roll)
        self.draw(self.curve_omega_pitch, self.data_speed_pitch)
        self.draw(self.curve_omega_yaw, self.data_speed_yaw)
        self.draw(self.curve_vx, self.data_vx)
        self.draw(self.curve_vy, self.data_vy)
        self.draw(self.curve_vz, self.data_vz)
        self.draw(self.curve_x, self.data_x_)
        self.draw(self.curve_y, self.data_y)
        self.draw(self.curve_z, self.data_z)

    def update_test(self):
        msg = self.real_client.recv_match(type='ATTITUDE', blocking=True)
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
        self.draw(self.curve_omega_roll, self.data_speed_roll)
        self.draw(self.curve_omega_pitch, self.data_speed_pitch)
        self.draw(self.curve_omega_yaw, self.data_speed_yaw)

    def control_widget_change(self, index):
        # 更改控制模式
        self.control_mod = index

    def InitLink(self):
        try:
            self.real_client = mavutil.mavlink_connection("com3", baud=57600)
            self.log_display.append("真实无人机链接成功！")
            self.log_display.moveCursor(QTextCursor.End)
            self.real_connect = True

        except:
            self.log_display.append("真实无人机链接失败请检查设备")
            self.log_display.moveCursor(QTextCursor.End)
            self.real_connect = False

        try:
            self.virtual_client = airsim.MultirotorClient()
            self.virtual_client.confirmConnection()
            self.log_display.append("仿真无人机链接成功！")
            self.log_display.moveCursor(QTextCursor.End)
            self.virtual_connect = True
        except:
            self.log_display.append("仿真无人机链接失败！")
            self.log_display.moveCursor(QTextCursor.End)
            self.virtual_connect = False

    def control(self):
        if self.virtual_connect:
            self.vmotor1 = (self.motor1.value() + 1) / 100
            self.vmotor2 = (self.motor2.value() + 1) / 100
            self.vmotor3 = (self.motor3.value() + 1) / 100
            self.vmotor4 = (self.motor4.value() + 1) / 100
        else:
            self.log_display.append("无法控制！")
            self.log_display.moveCursor(QTextCursor.End)

    def control_all(self):
        if self.virtual_connect:
            V = self.motor_all.value()
            value = (self.motor_all.value() + 1) / 100
            if self.checkM1.isChecked():
                self.vmotor1 = value
                self.motor1.setValue(V)

            if self.checkM2.isChecked():
                self.vmotor2 = value
                self.motor2.setValue(V)

            if self.checkM3.isChecked():
                self.vmotor3 = value
                self.motor3.setValue(V)

            if self.checkM4.isChecked():
                self.vmotor4 = value
                self.motor4.setValue(V)
            # print(value)

        else:
            self.log_display.append("无法控制！")
            self.log_display.moveCursor(QTextCursor.End)

    def controller(self):
        while self.virtual_connect and self.run_flag:
            self.virtual_client.enableApiControl(True)
            self.virtual_client.armDisarm(True)
            while self.run_flag and self.control_mod == 0 and self.run_flag:
                self.virtual_client.moveByMotorPWMsAsync(self.vmotor1, self.vmotor2, self.vmotor3, self.vmotor4, 0.05)
                self.position, self.linear_velocity, self.angular_velocity, self.linear_acceleration, self.angular_acceleration, self.angle = self.get_virtual_data()
                time.sleep(0.05)
            while self.run_flag and self.control_mod == 1 and self.run_flag:
                # print("摇杆控制模式")
                self.position, self.linear_velocity, self.angular_velocity, self.linear_acceleration, self.angular_acceleration, self.angle = self.get_virtual_data()

                if self.take_off_flag:
                    self.virtual_client.takeoffAsync().join()
                if self.land_flag:
                    self.virtual_client.landAsync().join()
                if self.is_move:
                    # self.virtual_client.moveByVelocityAsync(0,0,-8,0.2).join()
                    # print('move')
                    # print(self.x_y)
                    self.virtual_client.moveByVelocityAsync(self.x_y[0], self.x_y[1], 0, 0.2)
                time.sleep(0.05)
                # self.virtual_client.moveByMotorPWMsAsync(1, 1, 1, 1, 0.05)
                # print("run")

    def get_virtual_data(self):
        position = self.virtual_client.getMultirotorState().kinematics_estimated.position.to_numpy_array()
        linear_velocity = self.virtual_client.getMultirotorState().kinematics_estimated.linear_velocity.to_numpy_array()
        angular_velocity = self.virtual_client.getMultirotorState().kinematics_estimated.angular_velocity.to_numpy_array()
        linear_acceleration = self.virtual_client.getMultirotorState().kinematics_estimated.linear_acceleration.to_numpy_array()
        angular_acceleration = self.virtual_client.getMultirotorState().kinematics_estimated.angular_acceleration.to_numpy_array()

        orientation = self.virtual_client.getMultirotorState().kinematics_estimated.orientation
        std_orientation = np.quaternion(orientation.x_val, orientation.y_val, orientation.z_val, orientation.w_val)
        angle = quaternion.as_euler_angles(std_orientation)
        # print(position)

        return position, linear_velocity, angular_velocity, linear_acceleration, angular_acceleration, angle

    def draw(self, pen, data):
        pen.setData(self.data_x[:self.ptr], data[:self.ptr])
        pen.setPos(-10 * self.ptr, 0)

    def take_off_trigger(self):
        self.take_off_flag = True
        time.sleep(0.1)
        self.take_off_flag = False

    def land_trigger(self):
        self.land_flag = True
        time.sleep(0.1)
        self.land_btn = False

    # 重载virtual rod部分代码
    @pyqtSlot(QtCore.QPoint, name="do_mouseMoveEvent")
    def do_mouseMoveEvent(self, point):
        if self.is_move:
            pt = self.control_button.view.mapToScene(point)
            x = pt.x()
            y = pt.y()

            max_ = self.control_button.W_H / 3 + self.control_button.W_H / 6 / 2
            min_ = self.control_button.W_H / 10
            if abs(x) >= max_:
                x = max_ * x / abs(x)
            if abs(y) >= max_:
                y = max_ * y / abs(y)

            out = '(' + str(x) + ',' + str(y) + ')'
            print(out)
            self.x_y = [x / 10., -y / 10.]

            self.control_button.button.setPos(x, y)

    def do_mousePressEvent(self):
        self.is_move = True

    def do_mouseReleaseEvent(self):
        # print('false')
        self.control_button.End_Action.emit()
        self.is_move = False
        self.control_button.button.setPos(0, 0)
        brush_1 = QtGui.QBrush(Qt.white)
        self.control_button.right.setBrush(brush_1)
        self.control_button.left.setBrush(brush_1)
        self.control_button.up.setBrush(brush_1)
        self.control_button.down.setBrush(brush_1)


app = QApplication(sys.argv)
monitor_ui = UI()
sys.exit(app.exec_())
