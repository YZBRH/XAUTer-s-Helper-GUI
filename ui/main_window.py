# -*- coding: utf-8 -*-
# @Time    : 2025/1/26 下午6:37
# @Author  : BR
# @File    : main_window.py
# @description: 主要窗口

import os
import sys

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget
from PySide6.QtGui import QIcon
from qt_material import apply_stylesheet

from core.plugins.jwxt.user import jwxtUser
from ui.menu_window import AboutDialog
from ui.tab_window import personInformationTab, scoreTab, scheduleTab, examsAndTextbooksTab, courseSelectionTab, \
    otherTab
from core import log
from core.tool import set_work_dir
from config import auto_login, jwxt_account, jwxt_password


class mainWindow(QMainWindow):
    """
    主窗口类
    """

    def __init__(self, *args, **kwargs):
        log.info("主窗口初始化")
        super().__init__(*args, **kwargs)

        self.set_base_settings()
        self.set_mune_bar()
        self.set_ui()

    def set_base_settings(self) -> None:
        """
        基础设置
        :return:
        """
        log.debug("进行基础设置")
        self.setWindowTitle("XUATer's Helper")
        self.setWindowIcon(QIcon(os.path.join(os.getcwd(), "resources", "images", "logo.ico")))
        self.resize(800, 600)

    def set_mune_bar(self) -> None:
        """
        菜单栏设置
        :return:
        """
        log.debug("进行菜单栏设置")

        menu_bar = self.menuBar()

        # "帮助"菜单栏
        help_menu = menu_bar.addMenu("帮助")
        # "关于"动作
        about_action = help_menu.addAction("关于")
        about_action.setStatusTip("关于此应用程序")
        about_action.triggered.connect(self.show_about_dialog)

        # "检查更新"动作
        updates_action = help_menu.addAction("检查更新")
        updates_action.setStatusTip("检查更新最新版本")
        updates_action.triggered.connect(self.check_for_updates)

        help_menu.addAction(about_action)

        self.statusBar()

    def set_ui(self) -> None:
        """
        基础ui布局设置
        :return:
        """
        log.debug("进行页面布局设置")

        log.info("选项卡初始化")
        self.tabwidget = QTabWidget()
        self.tabwidget.setTabPosition(QTabWidget.North)

        self.person_information_tab = personInformationTab(self)
        self.tabwidget.addTab(self.person_information_tab.get_tab(), "个人信息")

        self.score_tab = scoreTab(self)
        self.tabwidget.addTab(self.score_tab.get_tab(), "成绩")

        self.schedule_tab = scheduleTab(self)
        self.tabwidget.addTab(self.schedule_tab.get_tab(), "课程")

        self.exams_and_text_books_tab = examsAndTextbooksTab(self)
        self.tabwidget.addTab(self.exams_and_text_books_tab.get_tab(), "考试与教程")

        self.course_selection_tab = courseSelectionTab(self)
        self.tabwidget.addTab(self.course_selection_tab.get_tab(), "选课")

        self.other_tab = otherTab()
        self.tabwidget.addTab(self.other_tab.get_tab(), "其他")

        self.setCentralWidget(self.tabwidget)

    def show_about_dialog(self) -> None:
        """
        创建并显示关于对话框
        :return:
        """
        log.debug("'关于'按钮触发")
        about_dialog = AboutDialog()
        about_dialog.exec()

    def check_for_updates(self) -> None:
        """
        检查更新
        :return:
        """
        log.debug("'检查更新'按钮触发")
        pass


class initThread(QThread):
    """
    多线程初始化（提升用户体验）
    """

    def __init__(self, window: mainWindow):
        super().__init__()
        self.window = window

    def run(self):
        # 尝试自动登录
        if auto_login:
            tab = self.window.person_information_tab
            tab.jwxt_user = jwxtUser(jwxt_account, jwxt_password)
            tab.jwxt_user.login_jwxt()
            if tab.jwxt_user.get_login_status():
                tab.update_person_information(
                    tab.jwxt_user.get_username(),
                    tab.jwxt_user.get_class(),
                    tab.jwxt_user.get_id())


def start():
    app = QApplication(sys.argv)  # 创建APP，将运行脚本时（可能的）的其他参数传给Qt以初始化
    # apply_stylesheet(app, theme='dark_blue.xml')

    window = mainWindow()

    log.info("数据初始化")
    # 测试网络连接
    window.person_information_tab.check_internet_connect()
    # 多线程初始化
    init_thread = initThread(window)
    init_thread.start()

    window.show()

    sys.exit(app.exec())  # 正常退出APP：app.exec()关闭app，sys.exit()退出进程


if __name__ == "__main__":
    set_work_dir()
    start()
