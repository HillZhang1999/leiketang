import sys
import sqlite3
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtWidgets import QWidget, QApplication, QDesktopWidget, QLineEdit, QPushButton, QLabel, qApp, QMessageBox


class RegisterWindow(QWidget):
    """
    注册窗口
    """

    def __init__(self, main_window=None):
        super(RegisterWindow,self).__init__()
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
        self.resize(600, 600)
        self.center()
        self.setWindowTitle('用户注册')

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

        self.pwd2Label = QLabel(self)
        self.pwd2Label.setText("重复密码:")
        self.pwd2Label.move(0,310)
        self.pwd2Edit = QLineEdit(self)
        self.pwd2Edit.setEchoMode(QLineEdit.Password)
        self.pwd2Edit.setClearButtonEnabled(True)
        self.pwd2Edit.setPlaceholderText("请再次输入密码")
        self.pwd2Edit.resize(400,50)
        self.pwd2Edit.move(130,300)

        self.btn1 = QPushButton(self)
        self.btn1.setText('注册')
        self.btn1.move(100, 400)
        self.btn1.clicked.connect(self.register)

        self.btn2 = QPushButton(self)
        self.btn2.setText('取消')
        self.btn2.move(300, 400)
        self.btn2.clicked.connect(self.close)

    def close(self):
        """
        关闭窗口
        :return:
        """
        reply = QMessageBox.question(self,
                                        "消息",
                                        "确定要取消注册吗？",
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

    def register(self):
        """
        返回注册信息给主窗口
        :return:
        """
        if not(self.pwdEdit.text()) or not(self.pwdEdit.text()) or not(self.pwd2Edit.text()):
            QMessageBox.warning(self,"消息","请不要留空！",QMessageBox.Yes)
            return

        if self.pwdEdit.text() != self.pwd2Edit.text():
            QMessageBox.warning(self,"消息","请确保两次输入的密码一致！",QMessageBox.Yes)
            return

        #利用构造函数传入的主窗口指针，修改主窗口类的变量
        self.cur.execute('select * from Users')
        if self.unEdit.text() in [x[0] for x in self.cur.fetchall()]:
            QMessageBox.information(self, "消息", "用户名已存在！", QMessageBox.Yes)
        else:
            QMessageBox.information(self, "消息", "注册成功！", QMessageBox.Yes)
            self.cur.execute('INSERT INTO Users VALUES ("{:s}","{:s}","教师");'.format(self.unEdit.text(),self.pwdEdit.text()))

        #self.mw.users.append([self.unEdit.text(),self.pwdEdit.text()])
        self.conn.commit()
        self.closeDB()
        self.destroy()

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
    window = RegisterWindow()
    window.show()
    sys.exit(app.exec_())