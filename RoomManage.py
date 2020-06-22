import sys
import sqlite3
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtWidgets import QWidget, QApplication, QDesktopWidget, QLineEdit, QPushButton, QLabel, qApp, QMessageBox, \
    QComboBox


class RoomManageWindow(QWidget):
    """
    注册窗口
    """

    def __init__(self, user_info, main_window=None):
        super(RoomManageWindow,self).__init__()
        self.mw = main_window
        self.user_info = user_info
        self.initUI()
        self.setFixedSize(self.width(), self.height())

    def paintEvent(self, event):
        """
        设置窗口背景
        :param event:
        :return:
        """
        painter = QPainter(self)
        pixmap = QPixmap("./bg.jpg")
        painter.drawPixmap(self.rect(), pixmap)

    def initUI(self):
        """
        UI设置
        :return:
        """
        self.resize(600, 200)
        self.center()
        self.setWindowTitle('用户管理')


        self.label1 = QLabel(self)
        self.label1.setText("选择观众:")
        self.label1.move(100,30)
        self.users = QComboBox(self)
        self.users.move(230, 30)
        self.users.addItems([x for x in self.user_info])

        self.btn1 = QPushButton(self)
        self.btn1.setText('禁言')
        self.btn1.move(50, 100)
        self.btn1.clicked.connect(self.shut_up)

        self.btn2 = QPushButton(self)
        self.btn2.setText('踢出直播间')
        self.btn2.move(230, 100)
        self.btn2.clicked.connect(self.ban)

        self.btn3 = QPushButton(self)
        self.btn3.setText('返回')
        self.btn3.move(400, 100)
        self.btn3.clicked.connect(self.close)

    def shut_up(self):
        if self.users.currentText():
            msg = "*"*6 + self.users.currentText() + "已被禁言" + "*"*6
            message = msg.encode("utf-8")
            self.mw.s.sendto(message, self.mw.addr)
            self.destroy()

    def ban(self):
        if self.users.currentText():
            msg = "*"*6 + self.users.currentText() + "已被踢出直播间" + "*"*6
            message = msg.encode("utf-8")
            self.mw.s.sendto(message, self.mw.addr)
            self.mw.users.remove(self.users.currentText())
            self.destroy()

    def close(self):
        """
        关闭窗口
        :return:
        """
        reply = QMessageBox.question(self,
                                        "消息",
                                        "确定要取消修改吗？",
                                        QMessageBox.Yes | QMessageBox.No)
        if reply == 16384:
            self.destroy()
            self.closeDB()
        else:
            return

    def center(self):
        """
        移动窗口到屏幕中心
        :return:
        """
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    from TeacherClient import MainWindow
    mw = MainWindow()
    window = RoomManageWindow(user_info = [],main_window= mw)
    window.show()
    sys.exit(app.exec_())