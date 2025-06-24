# -*- coding: utf-8 -*-
# @Time    : 2025/1/25 下午11:28
# @Author  : BR
# @File    : main.py
# @description: 程序入口

from ui import main_window
from config import debug_status
from core.tool import set_work_dir
from core import log

if __name__ == "__main__":
    set_work_dir()
    log.info("程序启动")

    if debug_status:
        log.info("正在以DEBUG模式运行")

    log.info("程序开始初始化")
    main_window.start()

