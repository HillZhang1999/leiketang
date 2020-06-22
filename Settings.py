import sys

from PyQt5.QtGui import QPainter, QPixmap, QValidator, QIntValidator
from PyQt5.QtWidgets import QWidget, QApplication, QDesktopWidget, QLineEdit, QPushButton, QLabel, qApp, QMessageBox, \
    QCheckBox, QComboBox


class SettingWindow(QWidget):
    """
    设置窗口
    """

    def __init__(self, main_window=None):
        super(SettingWindow,self).__init__()
        self.mw = main_window
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
        self.setWindowTitle('直播设置')

        self.roomLabel = QLabel(self)
        self.roomLabel.setText("房间号:")
        self.roomLabel.move(0, 110)
        self.roomEdit = QLineEdit(self)
        self.roomEdit.setPlaceholderText("请输入房间号（0-9999）")
        self.roomEdit.setClearButtonEnabled(True)
        intValidator = QIntValidator(self)
        intValidator.setRange(0, 9999)
        self.roomEdit.setValidator(intValidator)
        self.roomEdit.resize(400, 50)
        self.roomEdit.move(130, 100)

        self.label1 = QLabel(self)
        self.label1.setText("屏幕:")
        self.label1.move(0, 210)
        self.checkBox1 = QCheckBox('录制', self)
        self.checkBox1.move(70,210)

        self.label2 = QLabel(self)
        self.label2.setText("摄像头:")
        self.label2.move(180, 210)
        self.checkBox2 = QCheckBox('录制', self)
        self.checkBox2.move(270,210)

        self.label3 = QLabel(self)
        self.label3.setText("麦克风:")
        self.label3.move(400, 210)
        self.checkBox3 = QCheckBox('录制', self)
        self.checkBox3.move(490,210)

        self.label4 = QLabel(self)
        self.label4.setText("设置帧率:")
        self.label4.move(0, 310)
        self.frameRateEdit = QLineEdit(self)
        self.frameRateEdit.setPlaceholderText("请输入帧率（24-60）")
        self.frameRateEdit.setClearButtonEnabled(True)
        intValidator2 = QIntValidator(self)
        intValidator2.setRange(24, 60)
        self.frameRateEdit.setValidator(intValidator2)
        self.frameRateEdit.resize(400, 50)
        self.frameRateEdit.move(130, 300)

        self.label5 = QLabel(self)
        self.label5.setText("设置分辨率:")
        self.label5.move(0, 410)
        self.resolvtion = QComboBox(self)
        self.resolvtion.addItem("2560x1600")
        self.resolvtion.addItem("1920×1080")
        self.resolvtion.addItem("1440×900")
        self.resolvtion.addItem("1280×800")
        self.resolvtion.move(130,410)

        self.btn1 = QPushButton(self)
        self.btn1.setText('确认')
        self.btn1.move(100, 500)
        self.btn1.clicked.connect(self.set)

        self.btn2 = QPushButton(self)
        self.btn2.setText('取消')
        self.btn2.move(300, 500)
        self.btn2.clicked.connect(self.close)

        self.btn3 = QPushButton(self)
        self.btn3.setText('使用默认设置')
        self.btn3.move(200, 20)
        self.btn3.clicked.connect(self.default)

    def default(self):
        """
        默认设置
        :return:
        """
        self.checkBox1.setChecked(True)
        self.checkBox2.setChecked(True)
        self.checkBox3.setChecked(True)
        self.frameRateEdit.setText("30")
        self.resolvtion.setCurrentIndex(0)
        self.roomEdit.setText("1234")

    def set(self):
        """
        返回设置信息
        :return:
        """
        if not(self.roomEdit.text()):
            QMessageBox.warning(self, "消息", "请填写房间号！", QMessageBox.Yes)
        elif not(self.frameRateEdit.text()):
            QMessageBox.warning(self, "消息", "请填写帧率！", QMessageBox.Yes)
        elif not(self.checkBox1.isChecked()) and not(self.checkBox2.isChecked()) and not(self.checkBox3.isChecked()):
            QMessageBox.warning(self, "消息", "请至少选取一个数据源！", QMessageBox.Yes)
        elif not(24<=int(self.frameRateEdit.text())<=60):
            QMessageBox.warning(self, "消息", "请设置正确的帧率！", QMessageBox.Yes)
        else:
            self.mw.is_screen_available = self.checkBox1.isChecked()
            self.mw.is_camera_available = self.checkBox2.isChecked()
            self.mw.is_microphone_available = self.checkBox3.isChecked()
            self.mw.frame_rate = self.frameRateEdit.text()
            self.mw.resolvtion = self.resolvtion.currentText()
            self.mw.roomID = self.roomEdit.text()
            self.mw.isSetted = True
            QMessageBox.information(self, "消息", "设置已保存！", QMessageBox.Yes)
            self.destroy()

    def close(self):
        """
        关闭窗口
        :return:
        """
        reply = QMessageBox.question(self,
                                        "消息",
                                        "确定要取消设置吗？",
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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SettingWindow()
    window.show()
    sys.exit(app.exec_())