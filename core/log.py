# -*- coding: utf-8 -*-
# @Time    : 2025/1/25 下午11:28
# @Author  : BR
# @File    : log.py
# @description: 日志模块

import time
import os
import json
from config import debug_status, log_status


def json_format(message):
    """
    待完成
    :param message:
    :return:
    """
    try:
        return json.dumps(message, indent=4, ensure_ascii=False)
    except Exception as e:
        return message


def get_now_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def save_log_to_file(message: str):
    if not log_status:
        return
    try:
        with open(os.path.join(os.getcwd(), "log", "log.txt"), "a", encoding="utf-8") as fp:
            fp.write(message+"\n")
    except Exception as e:
        pass


def info(message: str):
    message = f"[{get_now_time()}][INFO] {message}"
    print("\033[32m" + message + "\033[0m")
    save_log_to_file(message)


def warning(message: str):
    message = f"[{get_now_time()}][WARNING] {message}"
    print("\033[33m" + message + "\033[0m")
    save_log_to_file(message)


def error(message: str):
    message = f"[{get_now_time()}][ERROR] {message}"
    print("\033[31m" + message + "\033[0m")
    save_log_to_file(message)


def debug(message: str):
    if debug_status:
        message = f"[{get_now_time()}][DEBUG] {message}"
        print("\033[34m" + message + "\033[0m")
        save_log_to_file(message)


if __name__ == "__main__":
    a = ["1",3,43,5]
    info(json_format(a))
