# -*- coding: utf-8 -*-
# @Time    : 2025/1/25 下午11:28
# @Author  : BR
# @File    : tool.py
# @description: 包含常用工具函数的模块

import os
import sys
import requests
import base64
import time
import ddddocr
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QLabel

from core import log


class clickableLabel(QLabel):
    """
    重写可被点击的QLabel
    """
    clicked = Signal()

    def __init__(self):
        super().__init__()
        # 设置标签为可点击的
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        # 发射点击信号
        self.clicked.emit()
        super().mousePressEvent(event)


def identify_verification_code(path: str) -> str:
    """
    识别图片验证码

    :param path: 图片路径
    :return: 识别结果
    """
    try:
        with open(path, 'rb') as f:
            img_data = f.read()
        code = ddddocr.DdddOcr(show_ad=False).classification(img_data)
        log.info(f"识别验证码为: {code}")
        return code
    except Exception as e:
        log.error(f"识别验证码失败，原因：{str(e)}")
        return ""


def str_to_base64(message: str) -> str:
    """
    字符串base64编码

    :param message: 待编码字符串
    :return: 编码后字符串(编码失败则返回传入值)
    """
    try:
        encoded = base64.b64encode(message.encode('utf-8')).decode("utf-8")
    except Exception as e:
        log.error(f"字符转化base64失败，原因：{str(e)}")
        encoded = message
    return encoded


def set_work_dir(work_dir: str = None) -> None:
    """
    设置工作目录，默认为项目根路径
    :param work_dir: 工作路径
    :return:
    """
    if work_dir:
        root_dir = work_dir
    else:
        # 获取当前目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # 获取根目录
        root_dir = os.path.dirname(script_dir)
    # 设置工作目录和项目目录
    log.debug(f"设置工作根目录为：{root_dir}")
    sys.path.append(root_dir)
    os.chdir(root_dir)


def get_default_term() -> str:
    """
    获取当前时间所处学年学期
    :return: 计算得到的学年学期
    """
    date = time.localtime()
    year = date.tm_year
    month = date.tm_mon
    if month >= 9:
        return f"{year}-{year+1}-1"
    elif month <= 2:
        return f"{year-1}-{year}-1"
    else:
        return f"{year-1}-{year}-2"


class getUrlConnectByThread(QThread):
    """
    多线程网络请求
    """
    result = Signal(bool, object)

    def __init__(self, url: str):
        super().__init__()
        self.url = url

    def run(self):
        try:
            res = requests.get(self.url, timeout=5)
            log.debug(f"与{self.url}成功连接,状态码为{res.status_code}")
            self.result.emit(True, res)
        except Exception as e:
            log.error(f"与{self.url}连接失败，原因：{e}")
            self.result.emit(False, None)


if __name__ == "__main__":
    set_work_dir()
    print(os.getcwd())
    print(get_default_term())
