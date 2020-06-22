import multiprocessing
import os
import sqlite3
import subprocess
import sys
import time
import socket
import threading
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject, QDateTime
from PyQt5.QtGui import QPalette, QBrush, QPixmap, QPainter, QColor, QIcon, QFont
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget, QMainWindow, QPushButton, QGridLayout, QFrame, \
    QAction, qApp, QLabel, QMessageBox, QTextEdit, QLineEdit
from MediaPlayer import Player
from Register import RegisterWindow
from Login import LoginWindow
from Settings import SettingWindow
from WhiteBoard import WhiteBoard
from UserManage import UserManageWindow
from ChatServer import ChatServer
from RoomManage import RoomManageWindow

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

        # 数据库初始化
        self.conn = sqlite3.connect('./mySqlite.db')
        self.cur = self.conn.cursor()

        # 用户信息初始化
        self.users = []
        self.userID = "Null"
        self.userPWD = "Null"
        self.status = "离线"
        self.is_camera_available = False
        self.is_microphone_available = False
        self.is_screen_available = False
        self.frame_rate = -1
        self.resolvtion = ""
        self.roomID = -1
        self.isSetted = False

        # 界面初始化
        self.initUI()
        self.setFixedSize(self.width(), self.height())

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
        self.is_camera_available = False
        self.is_microphone_available = False
        self.is_screen_available = False
        self.frame_rate = -1
        self.resolvtion = ""
        self.roomID = -1
        self.isSetted = False

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
        self.setWindowTitle('直播软件教师端')

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

        self.setAct = QAction('&直播设置', self)
        self.setAct.triggered.connect(self.set)

        self.settingMenu = self.menubar.addMenu('&设置')
        self.settingMenu.addAction(self.setAct)

        self.userManageAct = QAction('&用户管理', self)
        self.userManageAct.triggered.connect(self.user_manage)

        self.manageMenu = self.menubar.addMenu('&管理')
        self.manageMenu.addAction(self.userManageAct)

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

        #设置VLC播放器
        self.frame = QFrame(self)
        self.frame.resize(1000,600)
        self.frame.move(100, 100)
        self.frame.setStyleSheet("background-color: black;")
        self.player = Player()
        self.player.set_window(self.frame.winId())

        #设置主要按钮
        self.btn1 = QPushButton('开始直播', self)
        self.btn1.clicked.connect(self.live_start)
        self.btn1.resize(100,50)
        self.btn1.move(250,720)
        self.btn1.setEnabled(False)

        self.btn2 = QPushButton('结束直播', self)
        self.btn2.clicked.connect(self.live_finish)
        self.btn2.resize(100, 50)
        self.btn2.move(550, 720)
        self.btn2.setEnabled(False)

        self.btn3 = QPushButton('白板', self)
        self.btn3.clicked.connect(self.open_white_board)
        self.btn3.resize(100, 50)
        self.btn3.move(800, 720)
        self.btn3.setEnabled(False)

        self.btn4 = QPushButton('发送消息', self)
        self.btn4.resize(100, 50)
        self.btn4.move(700, 1080)
        self.btn4.clicked.connect(self.send_msg)
        self.btn4.setEnabled(False)

        self.btn5 = QPushButton('直播间管理', self)
        self.btn5.clicked.connect(self.manage_room)
        self.btn5.resize(200, 50)
        self.btn5.move(850, 1080)
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

    def handleDisplay(self, data):
        """
        显示聊天室接收的消息
        :param data:
        :return:
        """
        self.messageText.setText(self.msg_rec)
        self.roomInfoText.setText(self.room_info)

    def user_manage(self):
        """
        管理用户
        :return:
        """
        if self.status == "离线":
            QMessageBox.warning(self,"消息","请先登录！",QMessageBox.Yes)
        else:
            self.user_manage_window = UserManageWindow()
            self.user_manage_window.show()

    def open_white_board(self):
        """
        开启白板
        :return:
        """
        self.white_board = WhiteBoard()
        self.white_board.show()

    def live_start(self):
        """
        直播启动，rtmp推拉流，并在当前窗口显示
        :return:
        """
        if self.status == "登录":
            if self.isSetted:
                if self.socket_is_used(self.roomID):
                    QMessageBox.warning(self, "消息", "房间号已被占用，请重新进行设置！", QMessageBox.Yes)
                    self.set()
                else:
                    screen_size = "2560x1600"
                    framerate = str(self.frame_rate)
                    camera = "Integrated Camera"
                    microphone = "@device_cm_{33D9A762-90C8-11D0-BD43-00A0C911CE86}\wave_{BA4FE0F6-9988-467D-92A4-317C7775E78E}"
                    rtmp_server = "127.0.0.1:1935/myapp/" + str(self.roomID)
                    # 拼接命令
                    cmd = 'ffmpeg -thread_queue_size 128 -f dshow -i audio="{:s}" -f gdigrab -video_size {:s} -framerate {:s} -i desktop -f dshow -i video="{:s}" -framerate {:s}  -filter_complex "[2]scale=iw/2:ih/2[pip];[1][pip]overlay=main_w-overlay_w-10:main_h-overlay_h-10" -g 25 -vcodec libx264  -preset:v ultrafast -pix_fmt yuv420p -tune:v zerolatency -acodec aac -ab 128k -map 0:0 -f flv rtmp:{:s}'.format(
                        microphone, screen_size, framerate, camera, framerate, rtmp_server)

                    # 录频+录像+录音（默认）
                    if self.is_camera_available and self.is_screen_available:
                        pass
                    # 录像+录音
                    elif self.is_camera_available:
                        cmd = 'ffmpeg -thread_queue_size 128 -f dshow -i video="{:s}" -framerate {:s} -f dshow -i audio="{:s}" -pix_fmt yuv420p -f flv rtmp:{:s}'.format(
                            camera, framerate, microphone, rtmp_server)
                    # 录屏+录音
                    elif self.is_screen_available:
                        cmd = 'ffmpeg -thread_queue_size 128 -f gdigrab -video_size {:s} -i desktop -framerate {:s} -f dshow -i audio="{:s}" -pix_fmt yuv420p -f flv rtmp:{:s}'.format(
                            screen_size, framerate, microphone, rtmp_server)

                    # rtmp推流
                    self.live_video = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
                                                       stdout=subprocess.PIPE)
                    # 调用VLC播放器，显示直播结果
                    self.player.play('http://127.0.0.1:8086/live?port=1935&app=myapp&stream=' + str(self.roomID))

                    self.btn1.setEnabled(False)
                    self.btn2.setEnabled(True)
                    self.status = "直播中"
                    self.resetInfo()
                    self.start_chat_server()

                    self.btn4.setEnabled(True)
                    self.btn5.setEnabled(True)

                    s = 'INSERT INTO Lives VALUES ({:d},"{:s}");'.format(int(self.roomID),self.userID)
                    self.cur.execute('INSERT INTO Lives VALUES ({:d},"{:s}");'.format(int(self.roomID),self.userID))

                    self.conn.commit()

            else:
                QMessageBox.warning(self, "消息", "请先进行设置！", QMessageBox.Yes)
                self.set()

        elif self.status == "直播中":
            QMessageBox.warning(self,"消息","直播已开启！",QMessageBox.Yes)

        elif self.status == "离线":
            QMessageBox.warning(self,"消息","请先登录！",QMessageBox.Yes)

    def live_finish(self):
        """
        结束直播
        :return:
        """
        self.live_video.stdin.write('q'.encode("GBK"))
        self.live_video.communicate()
        self.player.stop()
        self.live_video = None
        self.status = "登录"
        self.users = []
        self.btn1.setEnabled(True)
        self.btn2.setEnabled(False)
        self.btn4.setEnabled(False)
        self.btn5.setEnabled(False)
        self.resetInfo()
        self.terminate_chat_server()
        self.cur.execute('delete from Lives where RoomID={:d};'.format(int(self.roomID)))
        self.conn.commit()
        QMessageBox.information(self, "消息", "直播已结束！", QMessageBox.Yes)

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
            s3 = '欢迎您：{:s}老师，直播功能已就绪！'.format(self.userID)
        elif self.status == "直播中":
            s1 = "直播信息：录像：{:s}，录频：{:s}，录音：{:s}，分辨率：{:s}，帧率：{:s}".format("开" if self.is_camera_available else "关", "开" if self.is_screen_available else "关", "开" if self.is_microphone_available else "关", self.resolvtion, str(self.frame_rate))
            s3 = '{:s}老师正在直播！房间号：{:s}' .format(self.userID, str(self.roomID))
        self.label3.setText(s3)

        self.label1.setText(s1)

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
        用户登出
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
        self.btn5.setEnabled(False)

    def set(self):
        """
        直播设置
        :return:
        """
        if self.status == "离线":
            QMessageBox.warning(self,"消息","请先登录！",QMessageBox.Yes)
        elif self.status == "直播中":
            QMessageBox.warning(self,"消息","请先关闭直播！",QMessageBox.Yes)
        else:
            self.setting_window = SettingWindow(self)
            self.setting_window.show()

    def closeDB(self):
        """
        关闭数据库连接
        :return:
        """
        if self.cur is not None:
            self.cur.close()
        if self.conn is not None:
            self.conn.close()

    def start_chat_server(self):
        """
        开启一个聊天室服务器
        :return:
        """
        # 创建一个新进程开启聊天服务器
        self.chat_server = multiprocessing.Process(target=ChatServer, args=(int(self.roomID),))
        self.chat_server.start()

        # 由于这里是异步的，需要进行同步控制，但我懒得用信号量了，直接让主进程暂停1s
        time.sleep(1)
        self.connect_server()

    def terminate_chat_server(self):
        """
        终止聊天室服务器
        :return:
        """
        msg = "老师关闭了直播间"
        message = msg.encode("utf-8")
        self.s.sendto(message, self.addr)
        if self.chat_server.is_alive():
            self.chat_server.terminate()

    def rec_msg(self):
        """
        自旋，接收服务端发送的消息
        :return:
        """
        while 1:
            msg = self.s.recvfrom(1024)[0].decode('utf-8')
            self.msg_rec += msg+'\n'
            if "进入聊天室..." in msg:
                tmp = msg.rstrip("进入聊天室...")
                self.room_info += tmp[:-2] + "(" + tmp[-2:] + ")\n"
                self.users.append(tmp)
            elif msg == "老师关闭了直播间":
                break

    def send_msg(self):
        """
        发送消息
        :return:
        """
        msg = self.userID + "老师:" + self.inputEdit.text()
        message = msg.encode("utf-8")
        self.s.sendto(message, self.addr)
        self.inputEdit.clear()

    def connect_server(self):
        """
        连接聊天服务器
        :return:
        """
        add1 = "127.0.0.1"
        add2 = int(self.roomID)
        self.addr = (add1, add2)
        s = self.userID + "老师"
        self.s.sendto(s.encode('utf-8'), self.addr)
        self.msg_rec += "您已连接到本直播间聊天室：{:s}:{:d}\n".format(add1, add2)
        t = threading.Thread(target=self.rec_msg)
        t.start()

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

    def manage_room(self):
        """
        管理直播间
        :return:
        """
        self.manage_room_window = RoomManageWindow(user_info=self.users, main_window=self)
        self.manage_room_window.show()

    def closeEvent(self, event):
        """
        清理一些 自己需要关闭的东西
        :param event:
        :return:
        """
        self.cur.execute("delete from lives")
        self.conn.commit()
        self.conn.close()
        self.s.close()
        if self.live_video:
            self.live_video.stdin.write('q'.encode("GBK"))
            self.live_video.communicate()
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

