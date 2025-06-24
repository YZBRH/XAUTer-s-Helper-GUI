# -*- coding: utf-8 -*-
# @Time    : 2025/1/26 下午6:38
# @Author  : BR
# @File    : menu_window.py
# @description: 菜单栏的一些窗口
import os
import sys

from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QApplication
from PySide6.QtGui import Qt, QDesktopServices, QPixmap, QIcon

from core import log
from core.tool import set_work_dir


class AboutDialog(QDialog):
    """
    关于窗口
    """
    def __init__(self):
        log.info("关于窗口启动")
        super().__init__()

        # 设置对话框标题
        self.setWindowTitle("关于")
        self.setWindowIcon(QIcon(os.path.join(os.getcwd(), "resources", "images", "logo.ico")))
        self.resize(400, 300)

        # 创建布局
        layout = QVBoxLayout()

        pixmap = QPixmap(os.path.join(os.getcwd(), "resources", "images", "logo.ico"))
        pixmap = pixmap.scaled(100, 100)
        img_label = QLabel()
        img_label.setPixmap(pixmap)
        img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(img_label)

        # 添加信息标签
        message = """
        <h1><b>XAUTer's Helper</b></h1>
        <h2>version: 0.1</h2>
        
        author: BR <br>
        <a href='https://github.com/YZBRH'>github</a> <br>
        <a href='https://blog.yzbrh.top'>BR's blog</a> <br>
        QQ: 1947514592
        """

        about_label = QLabel(message)
        about_label.setTextFormat(Qt.RichText)
        about_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        about_label.linkActivated.connect(self.link_clicked)
        layout.addWidget(about_label)

        # 添加确认按钮
        close_button = QPushButton("确认")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        # 设置对话框的布局
        self.setLayout(layout)

    def link_clicked(self, url: str) -> None:
        """
        url点击跳转
        :param url: url链接
        :return:
        """
        log.debug(f"跳转至url: {url}")
        QDesktopServices.openUrl(QUrl(url))


if __name__ == '__main__':
    set_work_dir()
    app = QApplication(sys.argv)

    window = AboutDialog()
    window.show()

    sys.exit(app.exec())
