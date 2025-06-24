# -*- coding: utf-8 -*-
# @Time    : 2025/1/26 下午6:37
# @Author  : BR
# @File    : common_window.py
# @description: 常用到的通用型窗口
import os
import sys
import time
from PySide6.QtCore import QPoint, QSize, QTimer, Signal
from PySide6.QtGui import QIcon, QMovie, Qt, QPainter, QStandardItemModel
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QMessageBox, QDialog, QLabel, QVBoxLayout, \
    QBoxLayout, QHBoxLayout, QWidget, QFileDialog
from core.tool import set_work_dir
from core import log


def information_dialog(message: str = "BR真帅"):
    """
    消息框
    :param message: 需要显示的提示文字
    :return:
    """
    log.debug(f"显示确认框，提示信息：{message}")
    msg_box = QMessageBox()
    msg_box.setWindowTitle("提示！")
    msg_box.setText(message)
    msg_box.setIcon(QMessageBox.Icon.Information)
    msg_box.setWindowIcon(QIcon(os.path.join(os.getcwd(), "resources", "images", "information.png")))
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

    msg_box.exec()


def warning_dialog(message: str = "该操作有风险，是否确认继续？") -> bool:
    """
    警告框
    :param message: 需要显示的提示文字
    :return:
    """
    log.debug(f"显示警告框，提示信息：{message}")
    msg_box = QMessageBox()
    msg_box.setWindowTitle("警告！")
    msg_box.setText(message)
    msg_box.setIcon(QMessageBox.Icon.Warning)
    msg_box.setWindowIcon(QIcon(os.path.join(os.getcwd(), "resources", "images", "warning.png")))
    msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

    res = msg_box.exec()

    if res == QMessageBox.StandardButton.Yes:
        log.debug("确认操作")
        return True
    else:
        log.debug("取消操作")
        return False


def error_dialog(message: str = "出现未知错误！"):
    """
    错误弹窗
    :param message: 需要显示的提示文字
    :return:
    """
    log.debug(f"显示错误框，提示信息：{message}")
    msg_box = QMessageBox()
    msg_box.setWindowTitle("哦不，出错了！")
    msg_box.setText(message)
    msg_box.setIcon(QMessageBox.Icon.Critical)
    msg_box.setWindowIcon(QIcon(os.path.join(os.getcwd(), "resources", "images", "error.png")))
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

    msg_box.exec()


class fileDialog(QWidget):
    """
    文件相关窗体
    """
    def file_save(self, base_path: str = "", base_filter: str = "All Files (*)") -> (str, str):
        """
        选择文件保存路径
        :param base_path: 基础展示的文件路径（默认为程序根路径）
        :param base_filter: 待选的文件格式
        :return: 获取到的用户选择的路径和文件格式
        """
        if base_path == "":
            base_path = os.getcwd()
        file_path, file_filter = QFileDialog.getSaveFileName(self, '保存文件', base_path, base_filter)

        log.debug(f"保存文件路径：{file_path}，选择的文件格式：{file_filter}")
        return file_path, file_filter


class ReadOnlyModel(QStandardItemModel):
    """
    只读表格
    """
    def flags(self, index):
        """重写 flags 方法以禁用编辑"""
        if index.isValid():
            return super().flags(index) & ~Qt.ItemIsEditable
        return super().flags(index)


class ClearableQPushButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super(ClearableQPushButton, self).__init__(*args, **kwargs)
        self._connections = []

    def connect_signal(self, signal, slot):
        """封装信号连接以记录连接"""
        connection = signal.connect(slot)
        self._connections.append((signal, slot, connection))
        return connection

    def disconnect_all_slots(self):
        """断开所有已连接的槽"""
        for signal, slot, connection in self._connections:
            signal.disconnect(connection)
        self._connections.clear()


class gifLabel(QLabel):
    """
    针对GIF类优化重写的QLabel
    """

    def __init__(self):
        super().__init__()
        self.movie_obj = None  # type: QMovie
        self.setScaledContents(True)
        self.setAlignment(Qt.AlignCenter)

    def setGif(self, gif_path):
        self.movie_obj = QMovie(gif_path)
        self.setMovie(self.movie_obj)
        self.movie_obj.start()

    def stop(self):
        self.movie_obj.stop()

    def paintEvent(self, event):
        # 重写动画的绘制事件，使用自带的会导致动画模糊有锯齿
        if self.movie_obj and self.movie_obj.isValid():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            curr_pix = self.movie_obj.currentPixmap()
            if self.hasScaledContents():
                pix = curr_pix.scaled(self.size(), Qt.AspectRatioMode.IgnoreAspectRatio,
                                      Qt.TransformationMode.SmoothTransformation)
                painter.drawPixmap(QPoint(0, 0), pix)
            else:
                painter.drawPixmap(QPoint(0, 0), curr_pix)
        else:
            super().paintEvent(event)


class loading_dialog(QDialog):
    """
    加载框
    """
    def __init__(self, message: str = "正在努力加载中..."):
        log.debug(f"显示加载框，提示信息：{message}")
        super().__init__()
        self.setWindowTitle("加载中...")
        self.setFixedSize(120, 120)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")

        self.gif_label = gifLabel()
        self.gif_label.setGif(os.path.join(os.getcwd(), "resources", "images", "loading.gif"))

        msg_label = QLabel(message)
        msg_label.setAlignment(Qt.AlignCenter)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.gif_label)
        main_layout.addWidget(msg_label)

        self.setLayout(main_layout)

    def closeEvent(self, event):
        self.gif_label.stop()
        event.accept()
        self.close()


class testWindow(QMainWindow):
    def __init__(self):
        log.debug("测试窗口创建")
        super().__init__()
        self.setWindowTitle("测试窗口")
        self.setGeometry(100, 100, 400, 300)

        test_button = QPushButton("测试按钮", self)

        test_button.clicked.connect(self.btn_clicked)

    def btn_clicked(self):
        self.a = loading_dialog()
        self.a.exec()


if __name__ == '__main__':
    set_work_dir()
    app = QApplication(sys.argv)

    window = testWindow()
    window.show()

    sys.exit(app.exec())
