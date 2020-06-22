import multiprocessing
import os
import sqlite3
import sys
import time
import socket
import threading
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject, QDateTime
from PyQt5.QtGui import QPalette, QBrush, QPixmap, QPainter, QColor, QIcon, QFont
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget, QMainWindow, QPushButton, QGridLayout, QFrame, \
    QAction, qApp, QLabel, QMessageBox, QTextEdit, QLineEdit, QComboBox
from MediaPlayer import Player
from Register import RegisterWindow
from Login import LoginWindow

class MainWindow(QMainWindow):
    """
    主窗口
    """
    def __init__(self, parent=None):
        """
        构造函数
        :param parent:
        """
        super(MainWindow, self).__init__(parent)

        # socket初始化（基于UDP，无连接）
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.msg_send = ''
        self.msg_rec = ''
        self.room_info = ''
        self.addr = None
        self.chat_server = None
        self.t = None

        # 数据库初始化
        self.conn = sqlite3.connect('./mySqlite.db')
        self.cur = self.conn.cursor()

        # 用户信息初始化
        self.users = []
        self.userID = "Null"
        self.userPWD = "Null"
        self.status = "离线"
        self.roomID = -1
        self.teacherName = ""

        # 界面初始化
        self.initUI()
        self.setFixedSize(self.width(), self.height())

        # 聊天室初始化
        # 创建一个线程，调用自定义的BackendThread类，自旋监听服务端传来的消息，并实时更新窗口
        self.backend = BackendThread()
        self.backend.update_date.connect(self.handleDisplay)
        self.thread = QThread()  # 创建进程
        self.backend.moveToThread(self.thread)
        self.thread.started.connect(self.backend.run)
        self.thread.start()

    def reset_user_info(self):
        """
        重置用户信息
        :return:
        """
        self.userID = "Null"
        self.userPWD = "Null"
        self.status = "离线"
        self.roomID = -1
        self.teacherName = ""

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
        初始化UI
        :return:
        """
        self.resize(1200, 1200)
        self.center()
        self.setWindowTitle('直播软件学生端')

        # 设置状态栏
        self.statusbar = self.statusBar()
        self.label1 = QLabel('状态：离线')
        self.label2 = QLabel('用户名：Null')

        self.statusbar.addPermanentWidget(self.label1, stretch=3)
        self.statusbar.addPermanentWidget(self.label2, stretch=1)

        #设置菜单栏
        self.RegisterAct = QAction('&注册', self)
        self.RegisterAct.triggered.connect(self.register)
        self.loginAct = QAction('&登录', self)
        self.loginAct.triggered.connect(self.login)
        self.logOutAct = QAction('&登出', self)
        self.logOutAct.triggered.connect(self.logout)
        self.exitAct = QAction('&退出软件', self)
        self.exitAct.triggered.connect(qApp.quit)

        self.menubar = self.menuBar()
        self.userMenu = self.menubar.addMenu('&用户')
        self.userMenu.addAction(self.RegisterAct)
        self.userMenu.addAction(self.loginAct)
        self.userMenu.addAction(self.logOutAct)
        self.userMenu.addAction(self.exitAct)

        #设置标签
        self.label3 = QLabel(self)
        self.label3.setFont(QFont("Microsoft YaHei"))
        self.label3.setText("请先登录！")
        self.label3.resize(600,50)
        self.label3.setAlignment(Qt.AlignCenter)
        self.label3.move(300,50)

        self.label4 = QLabel(self)
        self.label4.setFont(QFont("Microsoft YaHei"))
        self.label4.setText("聊天室")
        self.label4.move(400, 780)

        self.label5 = QLabel(self)
        self.label5.setFont(QFont("Microsoft YaHei"))
        self.label5.setText("直播间")
        self.label5.move(900, 780)

        self.label6 = QLabel(self)
        self.label6.setFont(QFont("Microsoft YaHei"))
        self.label6.setText("直播间列表：")
        self.label6.resize(200,50)
        self.label6.move(50, 720)

        #设置VLC播放器
        self.frame = QFrame(self)
        self.frame.resize(1000,600)
        self.frame.move(100, 100)
        self.frame.setStyleSheet("background-color: black;")
        self.player = Player()
        self.player.set_window(self.frame.winId())

        #设置主要按钮
        self.btn1 = QPushButton('进入直播', self)
        self.btn1.clicked.connect(self.live_start)
        self.btn1.resize(100,50)
        self.btn1.move(870,720)
        self.btn1.setEnabled(False)

        self.btn2 = QPushButton('退出直播', self)
        self.btn2.clicked.connect(self.live_finish)
        self.btn2.resize(100, 50)
        self.btn2.move(1000, 720)

        self.btn2.setEnabled(False)

        self.rooms = QComboBox(self)
        self.rooms.resize(500,50)
        self.rooms.move(200, 720)

        self.btn3 = QPushButton('刷新', self)
        self.btn3.clicked.connect(self.get_rooms)
        self.btn3.resize(100, 50)
        self.btn3.move(730, 720)
        self.btn3.setEnabled(False)

        self.btn4 = QPushButton('发送消息', self)
        self.btn4.resize(100, 50)
        self.btn4.move(700, 1080)
        self.btn4.clicked.connect(self.send_msg)
        self.btn4.setEnabled(False)

        self.btn5 = QPushButton('举手', self)
        self.btn5.resize(200, 50)
        self.btn5.move(850, 1080)
        self.btn5.clicked.connect(self.raise_hand)
        self.btn5.setEnabled(False)

        # 设置文本框
        self.messageText = QTextEdit(self)
        self.messageText.resize(700,250)
        self.messageText.move(100,820)
        self.messageText.setReadOnly(True)

        self.roomInfoText = QTextEdit(self)
        self.roomInfoText.resize(200, 250)
        self.roomInfoText.move(850, 820)
        self.roomInfoText.setReadOnly(True)

        self.inputEdit = QLineEdit(self)
        self.inputEdit.resize(580, 50)
        self.inputEdit.move(100, 1080)
        self.inputEdit.setPlaceholderText("请输入消息")

        self.show()

    def get_rooms(self):
        """
        获取当前可以进入的直播间
        :return:
        """
        res = self.cur.execute("select * from Lives").fetchall()
        if len(res)>0:
            self.rooms.clear()
            self.rooms.addItems(["直播间ID：{:d}，老师：{:s}".format(x[0], x[1]) for x in res])
            self.btn1.setEnabled(True)
        else:
            self.rooms.clear()
            self.rooms.addItem("暂无")
            self.btn1.setEnabled(False)

    def handleDisplay(self, data):
        """
        显示聊天室接收的消息
        :param data:
        :return:
        """
        self.messageText.setText(self.msg_rec)
        self.roomInfoText.setText(self.room_info)

    def live_start(self):
        """
        直播启动，rtmp推拉流，并在当前窗口显示
        :return:
        """
        if self.status == "登录":
            # 调用VLC播放器，显示直播结果
            self.roomID = int(self.rooms.currentText().split("，")[0].split("：")[1])
            self.teacherName = self.rooms.currentText().split("，")[1].split("：")[1]
            self.player.play('http://127.0.0.1:8086/live?port=1935&app=myapp&stream=' + str(self.roomID))
            self.btn1.setEnabled(False)
            self.btn2.setEnabled(True)
            self.status = "直播中"
            self.resetInfo()
            self.connect_server()
            self.btn4.setEnabled(True)
            self.btn5.setEnabled(True)

        elif self.status == "直播中":
            QMessageBox.warning(self,"消息","直播已开启！",QMessageBox.Yes)

        elif self.status == "离线":
            QMessageBox.warning(self,"消息","请先登录！",QMessageBox.Yes)

    def live_finish(self):
        """
        结束直播
        :return:
        """
        self.player.stop()
        self.status = "登录"
        self.btn1.setEnabled(False)
        self.btn2.setEnabled(False)
        self.resetInfo()
        self.s.sendto("EXIT".encode('utf-8'), self.addr)
        QMessageBox.information(self, "消息", "直播已结束！", QMessageBox.Yes)

    def live_finish2(self):
        """
        结束直播
        :return:
        """
        self.player.stop()
        self.status = "登录"
        self.btn1.setEnabled(False)
        self.btn2.setEnabled(False)
        self.resetInfo()
        self.s.sendto("EXIT".encode('utf-8'), self.addr)

    def resetInfo(self):
        """
        重置窗口信息
        :return:
        """
        s1 = '状态:{:s}'.format(self.status)
        s2 = '用户名:{:s}'.format(self.userID)
        self.label2.setText(s2)

        s3 = ""
        if self.status == "离线":
            s3 = '请先登录！'
        elif self.status == "登录":
            s3 = '欢迎您：{:s}同学，请进入直播间！'.format(self.userID)
        elif self.status == "直播中":
            s1 = "收看直播中"
            s3 = '{:s}老师正在直播！房间号：{:s}' .format(self.teacherName, str(self.roomID))
        self.label3.setText(s3)

        self.label1.setText(s1)

        self.btn4.setEnabled(False)
        self.btn5.setEnabled(False)

        self.msg_rec = ""
        self.msg_send = ""
        self.room_info = ""

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
        用户注册
        :return:
        """
        self.register_window = RegisterWindow(self)
        self.register_window.show()

    def login(self):
        """
        用户登录
        :return:
        """
        if self.status == "离线":
            self.login_window = LoginWindow(self)
            self.login_window.show()
        else:
            QMessageBox.warning(self, "消息", "您已登录！", QMessageBox.Yes)

    def logout(self):
        """
        用户登录
        :return:
        """
        if self.status == "离线":
            QMessageBox.warning(self,"消息","请先登录！",QMessageBox.Yes)
        elif self.status == "直播中":
            QMessageBox.warning(self,"消息","请先关闭直播！",QMessageBox.Yes)
        else:
            self.reset_user_info()
            QMessageBox.information(self, "消息", "成功登出！", QMessageBox.Yes)
            self.resetInfo()
            self.btn1.setEnabled(False)
            self.btn2.setEnabled(False)
            self.btn3.setEnabled(False)
            self.btn4.setEnabled(False)

    def closeDB(self):
        """
        关闭数据库连接
        :return:
        """
        if self.cur is not None:
            self.cur.close()
        if self.conn is not None:
            self.conn.close()

    def raise_hand(self):
        """
        举手功能
        :return:
        """
        msg = self.userID + "同学举手了！"
        message = msg.encode("utf-8")
        self.s.sendto(message, self.addr)

    def rec_msg(self):
        """
        自旋，接收服务端发送的消息
        :return:
        """
        while 1:
            msg = self.s.recvfrom(1024)[0].decode('utf-8')
            if "进入聊天室..." in msg:
                tmp = msg.rstrip("进入聊天室...")
                self.room_info += tmp[:-2] + "(" + tmp[-2:] + ")\n"
                self.users.append(tmp)
            elif "直播间成员：" in msg:
                tmp = msg.lstrip("直播间成员：").split(",")
                self.room_info = ""
                for user in tmp:
                    self.users.append(user)
                    self.room_info += user[:-2] + "(" + user[-2:] + ")\n"
            elif msg == "老师关闭了直播间":
                self.live_finish2()
                self.msg_rec = msg
                break
            elif "已被禁言" in msg:
                self.btn4.setEnabled(False)
                self.btn5.setEnabled(False)
            elif "已被踢出直播间" in msg:
                self.live_finish2()
                self.msg_rec = "您被老师踢出了直播间！"
                break
            self.msg_rec += msg + '\n'

    def send_msg(self):
        """
        发送消息
        :return:
        """
        msg = self.userID + "同学:" + self.inputEdit.text()
        message = msg.encode("utf-8")
        self.s.sendto(message, self.addr)
        self.inputEdit.clear()

    def connect_server(self):
        """
        连接聊天服务器
        :return:
        """
        time.sleep(1)
        add1 = "127.0.0.1"
        add2 = int(self.roomID)
        self.addr = (add1, add2)
        s = self.userID + "同学"
        self.s.sendto(s.encode('utf-8'), self.addr)
        self.msg_rec += "您已连接到本直播间聊天室：{:s}:{:d}\n".format(add1, add2)
        self.t = threading.Thread(target=self.rec_msg)
        self.t.start()

    def socket_is_used(self, port, ip='127.0.0.1'):
        """
        判断套接字是否可用，不可用说明房间号已经存在
        :param port:
        :param ip:
        :return:
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((ip, port))
            s.shutdown(2)
            return True
        except:
            return False

    def closeEvent(self, event):
        """
        重写退出方法
        :param event:
        :return:
        """
        self.cur.execute("delete from lives")
        self.conn.commit()
        self.conn.close()
        self.s.close()
        event.accept()  # 界面的关闭   但是会有一些时候退出不完全    需要调用 os 的_exit 完全退出
        try:
            os._exit(5)
        except Exception as e:
            print(e)

class BackendThread(QObject):   # 用来实时更新显示收到的消息
    # 通过类成员对象定义信号
    update_date = pyqtSignal(str)

    def run(self):
        """
        重写QObject的run方法进行多线程
        :return:
        """
        while True:
            data = QDateTime.currentDateTime()
            currTime = data.toString("yyyy-MM-dd hh:mm:ss")
            self.update_date.emit(str(currTime))
            time.sleep(1)

if __name__ == '__main__':

    app = QApplication(sys.argv)
    win = MainWindow()
    sys.exit(app.exec_())

