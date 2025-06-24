# -*- coding: utf-8 -*-
# @Time    : 2025/1/30 下午4:59
# @Author  : BR
# @File    : user.py
# @description: 教务系统用户相关

import requests
import os
from bs4 import BeautifulSoup

from core import log
from core.tool import str_to_base64, identify_verification_code
from ui.common_window import error_dialog


class jwxtUser:
    """
    教务系统用户类
    """
    # 登录接口
    login_url = "http://jwgl.xaut.edu.cn/jsxsd/xk/LoginToXk"
    # 验证码下载接口
    verification_url = "http://jwgl.xaut.edu.cn/jsxsd/verifycode.servlet"
    # 主页
    main_url = "http://jwgl.xaut.edu.cn/jsxsd/framework/xsMain_10700.htmlx"
    # 个人信息
    person_url = "http://jwgl.xaut.edu.cn/jsxsd/framework/xsdPerson_10700.htmlx"
    # 注销登录
    logout_url = "http://jwgl.xaut.edu.cn/jsxsd/xk/LoginToXk?method=exit"

    def __init__(self, account: str, password: str):
        # 姓名
        self.username = "未登录"
        # 班级
        self.class_ = "未登录"
        # 学号
        self.id = "未登录"
        # 生源地
        self.place_of_origin = ""
        # 学院
        self.academy = ""
        # 专业
        self.major = ""
        # 性别
        self.gender = ""

        self.r_session_jwxt = requests.session()
        self.user_jwxt = account
        self.password_jwxt = password
        self.login_status = False

    def get_verification_code(self, img_path: str = "") -> bytes:
        if img_path == "":
            img_path = os.path.join(os.getcwd(), "resources", "verification_code", "jwxt_verification.jpg")
        try:
            img_data = self.r_session_jwxt.get(self.verification_url).content
            open(img_path, "wb").write(img_data)
            return img_data
        except Exception as e:
            log.error(f"下载验证码失败，原因：{e}")
            return b""

    def ddddocr_identify(self, img_path: str = "") -> str:
        """
        ddddocr识别验证码
        :param img_path: 验证码图片位置
        :return:
        """
        if img_path == "":
            img_path = os.path.join(os.getcwd(), "resources", "verification_code", "jwxt_verification.jpg")
        verification_code = ""
        try:
            while len(verification_code) != 4:
                # 下载验证码并识别验证码
                self.get_verification_code()
                verification_code = identify_verification_code(img_path)
            return verification_code
        except Exception as e:
            log.error(f"识别验证码失败，原因：{e}")
            return ""

    def login_jwxt(self, verification_code: str = "", max_retry: int = 5) -> bool:
        """
        教务系统登录

        :param verification_code: 验证码(不填写则使用ddddocr自动识别)
        :param max_retry: 最大重试次数
        :return: 是否登录成功
        """
        log.info("开始登录教务系统...")

        i = 1
        while True:
            if verification_code != "":
                i = max_retry + 1
                code = verification_code
            else:
                code = self.ddddocr_identify()

            post_data = {
                "userAccount": self.user_jwxt,
                "userPassword": self.password_jwxt,
                "RANDOMCODE": code.strip(),
                "encoded": str_to_base64(self.user_jwxt, ) + "%%%" + str_to_base64(self.password_jwxt)

            }

            try:
                self.r_session_jwxt.post(self.login_url, data=post_data)
            except Exception as e:
                log.error(f"请求登录失败，原因：{e}")
                i += 1
                break

            # log.debug(res.text)

            if self.check_login_status():
                log.info("教务系统登录成功!")
                self.get_user_information_from_jwxt()
                self.login_status = True
                return True
            else:
                # 允许一定次数的重试
                if i > max_retry:
                    log.error("教务系统登录失败次数过多，请检查账号密码是否正确！")
                    return False
                log.debug(f"进行第{i}次重试...")
                i += 1

    def check_login_status(self) -> bool:
        """
        检查登录状态
        :return: 是否处于登录状态
        """
        self.login_status = False

        try:
            res = self.r_session_jwxt.get(self.main_url)
            if res.status_code != 200:
                log.debug(f"尝试使用的教务系统账户 {self.user_jwxt} 处于非登录状态！请求状态码为：{res.status_code}")
                return False

            if res.url != self.main_url:
                log.debug(f"尝试使用的教务系统账户 {self.user_jwxt} 处于非登录状态！访问url为：{res.url}")
                return False

            if "教学一体化服务平台" not in res.text:
                log.debug(f"尝试使用的教务系统账户 {self.user_jwxt} 处于非登录状态！访问主页信息结果为：{res.text}")
                return False

            res = self.r_session_jwxt.get(self.person_url)
            if self.user_jwxt not in res.text:
                log.debug(f"尝试使用的教务系统账户 {self.user_jwxt} 处于非登录状态！访问个人信息结果为：{res.text}")
                return False

            log.debug(f"尝试使用的教务系统账户 {self.user_jwxt} 处于登录状态！")
            self.login_status = True
            return True
        except Exception as e:
            log.error(f"获取登录状态失败，原因：{e}")
            return False

    def get_user_information_from_jwxt(self):
        """
        尝试获取教务系统用户基础信息
        """

        try:
            res = self.r_session_jwxt.get(self.person_url)
            user_info = BeautifulSoup(res.text, "html.parser").find("div", class_="myInfo-main-detail")
            self.username = user_info.find_all("h4")[0].text.split("-")[0]
            self.id = user_info.find_all("h4")[0].text.split("-")[1]
            self.gender = user_info.find_all("span", class_="female")[0].text
            self.place_of_origin = user_info.find_all("li")[0].text.split("：")[-1]
            self.academy = user_info.find_all("li")[1].text.split("：")[-1]
            self.major = user_info.find_all("li")[2].text.split("：")[-1]
            self.class_ = user_info.find_all("li")[3].text.split("：")[-1]

            log.info(f"获取登录用户为：{self.username}，学号为：{self.id}，性别为：{self.gender}，生源地为：{self.place_of_origin}，学院为：{self.academy}，专业为：{self.major}，班级为：{self.class_}")
        except Exception as e:
            log.error(f"获取用户信息失败！错误信息为：{e}")

    def logout(self):
        """
        主动注销账户
        :return:
        """
        try:
            self.r_session_jwxt.get(self.logout_url)
        except Exception as e:
            self.r_session_jwxt = requests.session()
            log.error(f"主动注销失败，原因：{e}")
            error_dialog("啊哦，似乎出现了些问题，可能没有成功注销！")
        self.username = "未登录"
        self.id = "未登录"
        self.class_ = "未登录"
        self.user_jwxt = ""
        self.password_jwxt = ""
        self.login_status = False

    def get_session(self) -> requests.session:
        """
        获取教务系统会话
        """
        return self.r_session_jwxt

    def set_account_and_passwd(self, account: str, password: str):
        self.user_jwxt = account
        self.password_jwxt = password

    def get_username(self) -> str:
        """
        获取用户名
        """
        return self.username

    def get_id(self) -> str:
        """
        获取学号
        """
        return self.id

    def get_class(self) -> str:
        """
        获取班级
        """
        return self.class_

    def get_login_status(self) -> bool:
        """
        获取登录状态
        """
        self.check_login_status()
        return self.login_status

    def get_academy(self) -> str:
        """
        获取学院
        """
        return self.academy

    def get_major(self) -> str:
        """
        获取专业
        """
        return self.major

    def get_place_of_origin(self) -> str:
        """
        获取生源地
        """
        return self.place_of_origin

    def get_gender(self) -> str:
        """
        获取性别
        """
        return self.gender


if __name__ == "__main__":
    from core.tool import set_work_dir
    from config import jwxt_account, jwxt_password

    set_work_dir()
    print(os.path.join(os.getcwd(), "resources", "verification_code", "jwxt_verification.jpg"))
    jwxt_user = jwxtUser(jwxt_account, jwxt_password)
    jwxt_user.login_jwxt()
