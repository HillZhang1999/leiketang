import sys
import sqlite3
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtWidgets import QWidget, QApplication, QDesktopWidget, QLineEdit, QPushButton, QLabel, qApp, QMessageBox, \
    QComboBox


class UserManageWindow(QWidget):
    """
    注册窗口
    """

    def __init__(self, main_window=None):
        super(UserManageWindow,self).__init__()
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
        self.setWindowTitle('用户管理')

        self.usersInfo = self.cur.execute('select * from Users').fetchall()

        self.label1 = QLabel(self)
        self.label1.setText("选择用户:")
        self.label1.move(0,30)
        self.users = QComboBox(self)
        self.users.move(130, 30)
        self.users.addItems([x[0] for x in self.usersInfo])
        self.users.currentIndexChanged.connect(self.resetInfo)

        self.unLabel = QLabel(self)
        self.unLabel.setText("用户名:")
        self.unLabel.move(0,110)
        self.unEdit = QLineEdit(self)
        self.unEdit.setPlaceholderText("请输入用户名")
        self.unEdit.setClearButtonEnabled(True)
        self.unEdit.resize(400,50)
        self.unEdit.move(130,100)
        self.unEdit.setEnabled(False)

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

        self.label2 = QLabel(self)
        self.label2.setText("身份:")
        self.label2.move(0,410)

        self.identity = QComboBox(self)
        self.identity.addItems(["教师","学生"])
        self.identity.move(130, 400)

        self.btn1 = QPushButton(self)
        self.btn1.setText('确认修改')
        self.btn1.move(50, 500)
        self.btn1.clicked.connect(self.register)

        self.btn2 = QPushButton(self)
        self.btn2.setText('删除用户')
        self.btn2.move(230, 500)
        self.btn2.clicked.connect(self.delete)

        self.btn3 = QPushButton(self)
        self.btn3.setText('返回')
        self.btn3.move(400, 500)
        self.btn3.clicked.connect(self.close)

        self.resetInfo()

    def delete(self):
        """
        删除用户
        :return:
        """
        sql = 'delete from Users where UserName="{:s}";'.format(self.users.currentText())
        reply = QMessageBox.question(self,
                                     "消息",
                                     "确定要删除用户{:s}吗？".format(self.users.currentText()),
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == 16384:
            self.cur.execute(sql)
            self.conn.commit()
            self.usersInfo = self.cur.execute('select * from Users').fetchall()
            self.users.clear()
            self.users.addItems([x[0] for x in self.usersInfo])
            self.resetInfo()
            QMessageBox.information(self, "消息", "删除成功！", QMessageBox.Yes)
        else:
            return

    def resetInfo(self):
        """
        重置信息
        :return:
        """
        sql = 'select * from Users where UserName="{:s}";'.format(self.users.currentText())
        res = self.cur.execute(sql).fetchall()
        if len(res)>0:
            self.unEdit.setText(res[0][0])
            self.pwdEdit.setText(res[0][1])
            self.pwd2Edit.setText(res[0][1])
            if res[0][2] == "教师":
                self.identity.setCurrentIndex(0)
            else:
                self.identity.setCurrentIndex(1)
        else:
            self.unEdit.clear()
            self.pwdEdit.clear()
            self.pwd2Edit.clear()
            self.identity.setCurrentIndex(0)

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
        sql = 'Update Users Set PassWord = "{:s}", Role = "{:s}" where UserName = "{:s}"'.format(self.pwdEdit.text(), self.identity.currentText(), self.users.currentText())
        self.cur.execute(sql)
        QMessageBox.information(self, "消息", "修改成功！", QMessageBox.Yes)

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
    window = UserManageWindow()
    window.show()
    sys.exit(app.exec_())