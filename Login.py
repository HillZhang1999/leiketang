import sqlite3
import sys

from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtWidgets import QWidget, QApplication, QDesktopWidget, QLineEdit, QPushButton, QLabel, qApp, QMessageBox


class LoginWindow(QWidget):
    """
    登录窗口
    """

    def __init__(self, main_window=None):
        super(LoginWindow,self).__init__()
        self.mw = main_window
        self.conn = sqlite3.connect('./mySqlite.db')
        self.cur = self.conn.cursor()
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
        self.resize(600, 400)
        self.center()
        self.setWindowTitle('用户登录')

        self.unLabel = QLabel(self)
        self.unLabel.setText("用户名:")
        self.unLabel.move(0,110)
        self.unEdit = QLineEdit(self)
        self.unEdit.setPlaceholderText("请输入用户名")
        self.unEdit.setClearButtonEnabled(True)
        self.unEdit.resize(400,50)
        self.unEdit.move(130,100)

        self.pwdLabel = QLabel(self)
        self.pwdLabel.setText("密码:")
        self.pwdLabel.move(0,210)
        self.pwdEdit = QLineEdit(self)
        self.pwdEdit.setEchoMode(QLineEdit.Password)
        self.pwdEdit.setClearButtonEnabled(True)
        self.pwdEdit.setPlaceholderText("请输入密码")
        self.pwdEdit.resize(400,50)
        self.pwdEdit.move(130,200)

        self.btn1 = QPushButton(self)
        self.btn1.setText('登录')
        self.btn1.move(100, 300)
        self.btn1.clicked.connect(self.login)

        self.btn2 = QPushButton(self)
        self.btn2.setText('取消')
        self.btn2.move(300, 300)
        self.btn2.clicked.connect(self.close)

    def close(self):
        """
        关闭窗口
        :return:
        """
        reply = QMessageBox.question(self,
                                        "消息",
                                        "确定要取消登录吗？",
                                        QMessageBox.Yes | QMessageBox.No)
        if reply == 16384:
            self.destroy()
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

    def login(self):
        """
        登录功能
        :return:
        """
        if not(self.pwdEdit.text()) or not(self.pwdEdit.text()):
            QMessageBox.warning(self,"消息","请不要留空！",QMessageBox.Yes)
            return

        sql = 'select * from Users where UserName="{:s}" and PassWord="{:s}"'.format(self.unEdit.text(), self.pwdEdit.text())
        if len(self.conn.execute(sql).fetchall())>0:
            QMessageBox.information(self, "消息", "登录成功！", QMessageBox.Yes)
            self.mw.userID = self.unEdit.text()
            self.mw.userPWD = self.pwdEdit.text()
            self.mw.status = "登录"
            self.mw.btn1.setEnabled(True)
            self.mw.btn3.setEnabled(True)
            self.mw.resetInfo()
            self.destroy()
        else:
            QMessageBox.warning(self, "消息", "用户名或密码错误", QMessageBox.Yes)
            return



    def closeDB(self):
        """
        关闭数据库连接
        :return:
        """
        if self.cur is not None:
            self.cur.close()
        if self.conn is not None:
            self.conn.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())