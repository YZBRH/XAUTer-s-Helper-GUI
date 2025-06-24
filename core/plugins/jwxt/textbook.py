# -*- coding: utf-8 -*-
# @Time    : 2025/2/6 上午12:20
# @Author  : BR
# @File    : textbook.py
# @description: 教材相关


import requests


class jwxtTextbook:
    def __init__(self):
        pass

    def get_textbook(self, r_session: requests.Session, term: str = "") -> list[dict]:
        pass


if __name__ == "__main__":
    from core.tool import set_work_dir
    from core.plugins.jwxt.user import jwxtUser
    from config import jwxt_account, jwxt_password

    set_work_dir()
    jwxt_user = jwxtUser(jwxt_account, jwxt_password)
    if not jwxt_user.login_jwxt():
        exit(0)

    jwxt_textbook = jwxtTextbook()
    data = jwxt_textbook.get_textbook(jwxt_user.get_session(), "2024-2025-1")
    print(data)
