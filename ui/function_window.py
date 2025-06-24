# -*- coding: utf-8 -*-
# @Time    : 2025/1/29 下午11:29
# @Author  : BR
# @File    : function_window.py
# @description: 一些功能性小窗口
import copy
import os
import sys

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QApplication, QFormLayout, QLineEdit, QPushButton, QDialog, QLabel

from ui.common_window import error_dialog
from core.tool import set_work_dir, clickableLabel
from core import log
from core.plugins.jwxt.user import jwxtUser


class loginWindow(QDialog):
    jwxt_user = jwxtUser("", "")

    def __init__(self):
        super().__init__()

        # 基础设置
        self.setWindowTitle("登录")
        self.setFixedSize(350, 150)

        # 主布局
        main_layout = QFormLayout()

        self.account_lineedit = QLineEdit()
        self.password_lineedit = QLineEdit()
        self.password_lineedit.setEchoMode(QLineEdit.Password)
        self.code_lineedit = QLineEdit("")
        self.code_label = clickableLabel()
        self.refresh_verification_code()

        login_btn = QPushButton("登录")

        login_btn.clicked.connect(self.login)
        self.code_label.clicked.connect(self.refresh_verification_code)

        main_layout.addRow("用户名", self.account_lineedit)
        main_layout.addRow("密码", self.password_lineedit)
        main_layout.addRow(self.code_label, self.code_lineedit)
        main_layout.addRow(login_btn)

        self.setLayout(main_layout)

    def login(self):
        """
        登录按钮按下
        :return:
        """

        log.info("尝试登录教务系统ing...")
        account = self.account_lineedit.text()
        password = self.password_lineedit.text()
        code = self.code_lineedit.text()

        if account == "" or password == "":
            log.error("登陆的用户名或密码为空")
            error_dialog("用户名或密码不能为空！！")
            return False

        log.debug(f"使用用户：{account}，密码：{password}，验证码：{code}尝试登录")

        self.jwxt_user.set_account_and_passwd(account, password)
        if self.jwxt_user.login_jwxt(code):
            self.jwxt_user.login_status = True
            self.close()
        else:
            self.refresh_verification_code()
            error_dialog("登录失败！请检查账号密码及验证码是否正确或网络连接是否通畅！")

    def refresh_verification_code(self):
        """
        刷新验证码
        :return:
        """
        self.jwxt_user.get_verification_code()
        code_img = QPixmap(os.path.join(os.getcwd(), "resources", "verification_code", "jwxt_verification.jpg"))
        self.code_label.setPixmap(code_img)
        # 设置高度相同
        self.code_lineedit.setFixedHeight(self.code_label.sizeHint().height())

    def get_jwxt_user(self) -> jwxtUser:
        """
        获取登录的教务系统用户类
        :return:
        """
        return self.jwxt_user

    def get_login_status(self) -> bool:
        """
        获取登录状态
        :return:
        """
        return self.jwxt_user.login_status


if __name__ == '__main__':
    set_work_dir()
    app = QApplication(sys.argv)

    window = loginWindow()
    window.show()

    sys.exit(app.exec())