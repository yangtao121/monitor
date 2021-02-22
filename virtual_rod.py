# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.Qt import Qt
from PyQt5.QtCore import pyqtSignal, pyqtSlot


class CustomButtonView(QtWidgets.QGraphicsView):
    MousePress = pyqtSignal()
    MouseMove = pyqtSignal(QtCore.QPoint)
    MouseRelease = pyqtSignal()

    # ==========================利用信号传递事件==========================
    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.LeftButton:
            self.MousePress.emit()
        super(CustomButtonView, self).mousePressEvent(QMouseEvent)

    def mouseReleaseEvent(self, QMouseEvent):
        self.MouseRelease.emit()
        super(CustomButtonView, self).mouseReleaseEvent(QMouseEvent)

    def mouseMoveEvent(self, QMouseEvent):
        self.MouseMove.emit(QMouseEvent.pos())
        # print(QMouseEvent.pos())
        super(CustomButtonView, self).mouseMoveEvent(QMouseEvent)


class ControlButton(QtWidgets.QWidget):
    Go_Direction = pyqtSignal(str)
    End_Action = pyqtSignal()

    def __init__(self, parent=None):
        super(ControlButton, self).__init__(parent, flags=Qt.Widget)

        self.is_move = False
        self.NoPen = QtGui.QPen(Qt.NoPen)
        self.W_H = 300
        self.brush_1 = QtGui.QBrush(Qt.white)
        self.brush_2 = QtGui.QBrush(QtGui.QColor(52, 160, 220))

        self.__initView()
        self.__initButton()
        self.__initSignal()

    # ==========================初始化==========================
    def __initView(self):
        # 初始化视图
        self.view = CustomButtonView(self)
        self.view.resize(self.W_H, self.W_H)
        # self.setCentralWidget(self.view)
        self.view.setAlignment(Qt.AlignCenter)
        self.view.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform)
        self.view.setMouseTracking(True)
        self.scene = QtWidgets.QGraphicsScene(QtCore.QRectF(-self.W_H / 2, -self.W_H / 2, self.W_H, self.W_H))
        self.view.setScene(self.scene)

    def __initButton(self):
        # 最外围的圆
        ___ = QtWidgets.QGraphicsEllipseItem(-self.W_H / 2, -self.W_H / 2, self.W_H, self.W_H)
        ___.setPen(self.NoPen)
        brush = QtGui.QLinearGradient(0, -self.W_H / 2, 0, self.W_H / 2)
        brush.setColorAt(0, QtGui.QColor(74, 68, 68))
        brush.setColorAt(1, QtGui.QColor(158, 156, 156))
        ___.setBrush(brush)
        self.scene.addItem(___)
        # 第二个大圆
        ___ = QtWidgets.QGraphicsEllipseItem(-self.W_H / 2 + 5, -self.W_H / 2 + 5, self.W_H - 10, self.W_H - 10)
        ___.setPen(self.NoPen)
        brush = QtGui.QRadialGradient(0, 0, self.W_H / 2 - 5, 0, 0)
        brush.setColorAt(0, QtGui.QColor(110, 110, 110))
        brush.setColorAt(0.8, QtGui.QColor(35, 35, 35))
        brush.setColorAt(1, QtGui.QColor(14, 14, 14))
        ___.setBrush(brush)
        self.scene.addItem(___)
        # 最里面的圆
        ___ = QtWidgets.QGraphicsEllipseItem(-(self.W_H / 6 + 5), -(self.W_H / 6 + 5), self.W_H / 3 + 10,
                                             self.W_H / 3 + 10)
        ___.setPen(self.NoPen)
        brush = QtGui.QRadialGradient(0, 0, self.W_H / 6 + 5, 0, 0)
        brush.setColorAt(0, QtGui.QColor(95, 95, 95))
        brush.setColorAt(1, QtGui.QColor(45, 45, 45))
        ___.setBrush(brush)
        self.scene.addItem(___)
        # 四条线
        # pen_1 = QtGui.QPen()
        # pen_1.setWidth(5)
        # pen_1.setCapStyle(Qt.RoundCap)
        # pen_1.setColor(QtGui.QColor(52, 160, 220))
        #
        # pen_2 = QtGui.QPen()
        # pen_2.setWidth(5)
        # pen_2.setColor(QtGui.QColor(10, 10, 10))
        # angle = 45
        # for i in range(4):
        #     ___ = QtWidgets.QGraphicsLineItem(self.W_H / 6 + 5, 0, self.W_H / 2 - 10, 0)
        #     ___.setPen(pen_1)
        #     ___.setRotation(angle)
        #     self.scene.addItem(___)
        #     ___ = QtWidgets.QGraphicsLineItem(self.W_H / 2 - 10, 0, self.W_H / 2 - 5, 0)
        #     ___.setPen(pen_2)
        #     ___.setRotation(angle)
        #     self.scene.addItem(___)
        #     angle += 90

        # 上下左右
        x = self.W_H / 3
        x_ = x + self.W_H / 15
        y = self.W_H / 30
        self.right = QtWidgets.QGraphicsPolygonItem()
        self.right.setPolygon(QtGui.QPolygonF([QtCore.QPoint(x, -y), QtCore.QPoint(x, y), QtCore.QPoint(x_, 0)]))
        self.right.setPen(self.NoPen)
        self.right.setBrush(self.brush_1)
        self.scene.addItem(self.right)

        self.down = QtWidgets.QGraphicsPolygonItem()
        self.down.setPolygon(QtGui.QPolygonF([QtCore.QPoint(x, -y), QtCore.QPoint(x, y), QtCore.QPoint(x_, 0)]))
        self.down.setPen(self.NoPen)
        self.down.setBrush(self.brush_1)
        self.down.setRotation(90)
        self.scene.addItem(self.down)

        self.left = QtWidgets.QGraphicsPolygonItem()
        self.left.setPolygon(QtGui.QPolygonF([QtCore.QPoint(x, -y), QtCore.QPoint(x, y), QtCore.QPoint(x_, 0)]))
        self.left.setPen(self.NoPen)
        self.left.setBrush(self.brush_1)
        self.left.setRotation(180)
        self.scene.addItem(self.left)

        self.up = QtWidgets.QGraphicsPolygonItem()
        self.up.setPolygon(QtGui.QPolygonF([QtCore.QPoint(x, -y), QtCore.QPoint(x, y), QtCore.QPoint(x_, 0)]))
        self.up.setPen(self.NoPen)
        self.up.setBrush(self.brush_1)
        self.up.setRotation(-90)
        self.scene.addItem(self.up)

        # 中心的可拖拽按钮
        self.button = QtWidgets.QGraphicsEllipseItem(-self.W_H / 6, -self.W_H / 6, self.W_H / 3, self.W_H / 3)
        self.button.setPen(self.NoPen)
        brush = QtGui.QRadialGradient(0, 0, self.W_H / 6, 0, 0)
        brush.setColorAt(0, QtGui.QColor(80, 80, 80))
        brush.setColorAt(0.5, QtGui.QColor(40, 40, 40))
        brush.setColorAt(1, QtGui.QColor(15, 15, 15))
        self.button.setBrush(brush)
        self.scene.addItem(self.button)

    def __initSignal(self):
        # 初始化信号槽
        self.view.MouseRelease.connect(self.do_mouseReleaseEvent)
        self.view.MousePress.connect(self.do_mousePressEvent)
        self.view.MouseMove.connect(self.do_mouseMoveEvent)

    # ==========================事件处理==========================
    def do_mouseReleaseEvent(self):
        self.End_Action.emit()
        self.is_move = False
        self.button.setPos(0, 0)
        brush_1 = QtGui.QBrush(Qt.white)
        self.right.setBrush(brush_1)
        self.left.setBrush(brush_1)
        self.up.setBrush(brush_1)
        self.down.setBrush(brush_1)

    def do_mousePressEvent(self):
        self.is_move = True
        # print(self.is_move)

    @pyqtSlot(QtCore.QPoint, name="do_mouseMoveEvent")
    def do_mouseMoveEvent(self, point):
        if self.is_move:
            pt = self.view.mapToScene(point)
            x = pt.x()
            y = pt.y()

            max_ = self.W_H / 3 + self.W_H / 6 / 2
            min_ = self.W_H / 10
            # if abs(x) > abs(y):
            #     y = 0
            # else:
            #     x = 0
            if abs(x) >= max_:
                x = max_ * x / abs(x)
            if abs(y) >= max_:
                y = max_ * y / abs(y)

            out = '(' + str(x) + ',' + str(y) + ')'
            print(point)
            if x > min_:
                self.right.setBrush(self.brush_2)
                self.left.setBrush(self.brush_1)
                self.up.setBrush(self.brush_1)
                self.down.setBrush(self.brush_1)
                self.Go_Direction.emit("right")
            elif x < -min_:
                self.right.setBrush(self.brush_1)
                self.left.setBrush(self.brush_2)
                self.up.setBrush(self.brush_1)
                self.down.setBrush(self.brush_1)
                self.Go_Direction.emit("left")
            elif y > min_:
                self.right.setBrush(self.brush_1)
                self.left.setBrush(self.brush_1)
                self.up.setBrush(self.brush_1)
                self.down.setBrush(self.brush_2)
                self.Go_Direction.emit("down")
            elif y < -min_:
                self.right.setBrush(self.brush_1)
                self.left.setBrush(self.brush_1)
                self.up.setBrush(self.brush_2)
                self.down.setBrush(self.brush_1)
                self.Go_Direction.emit("up")
            else:
                self.right.setBrush(self.brush_1)
                self.left.setBrush(self.brush_1)
                self.up.setBrush(self.brush_1)
                self.down.setBrush(self.brush_1)


            # print(x)
            # print(y)

            self.button.setPos(x, y)

    def resizeEvent(self, event):
        # 自适配界面
        if self.width() > self.height():
            self.W_H = self.height() - 50
        else:
            self.W_H = self.width() - 50
        self.view.resize(self.width(), self.height())
        self.scene.setSceneRect(QtCore.QRectF(-self.W_H / 2, -self.W_H / 2, self.W_H, self.W_H))
        self.scene.clear()
        self.__initButton()


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    button = ControlButton()
    button.show()
    sys.exit(app.exec_())