# -*- coding: utf-8 -*-
# @Time    : 2025/2/5 下午8:19
# @Author  : BR
# @File    : schedule.py
# @description: 教务系统课程相关
import copy

import requests
import bs4
from bs4 import BeautifulSoup

from core import log


def add_data(course_data: dict, key: str, value: str) -> dict:
    """
    字典数据追加
    :param course_data:
    :param key:
    :param value:
    :return:
    """
    if course_data[key] == "":
        course_data[key] = value
    elif value not in course_data[key].split('~'):
        course_data[key] += "~" + value
    return course_data


class jwxtSchedule:
    """
    教务系统课程相关类
    """
    # 学期理论课表接口
    schedule_url = "http://jwgl.xaut.edu.cn/jsxsd/xskb/xskb_list.do"

    def __init__(self):
        pass

    def get_course(self, r_session: requests.Session, term: str, week: str = "", mode: str = "47A852EDE04746E8913E2D79DBCEBB7F") -> list[dict]:
        """
        获取课程信息
        :param r_session: 处于登录状态的requests.Session
        :param term: 指定学年学期
        :param week: 指定周次，默认为全部
        :param mode: 课程查询模式，默认为默认节次模式
        :return: 获取到的课程信息
        """
        post_data = {
            "cj0701id": "",
            "zc": week,  # 周次，空-全部，1-第一周
            "demo": "",  # 某种demo模式？？？
            "xnxq01id": term,  # 学年学期
            "xstzd": "",  # 是否显示通知单编号, 空-不显示，1-显示
            "sfFD": "1",  # 是否放大，空-不放大，1-放大
            "wkbkc": "1",  # 是否显示无课表课程，空-不显示，1-显示
            "xswk": "",  # 是否显示课程群号及链接，空-不显示，1-显示
            "kbjcmsid": mode  # 课程基础模式id，47A852EDE04746E8913E2D79DBCEBB7F-默认节次模式
        }
        try:
            res = r_session.post(self.schedule_url, data=post_data)
        except Exception as e:
            log.error(f"请求学期理论课表接口失败，原因：{e}")
            return []

        table_data = BeautifulSoup(res.text, "html.parser").find("table", id="timetable")

        trs = table_data.find_all("tr")
        course_data = []
        for period, tr in enumerate(trs[1:]):
            # 由左至右，由上至下
            tds = tr.find_all("td")
            for day, td in enumerate(tds):
                single_course = {
                    "day": str(day + 1),  # 周几
                    "period": str(period + 1),  # 第几节课
                    "course_name": "",  # 课程名称
                    "teacher": "",  # 授课教师
                    "week_session": "",  # 课程周数
                    "course_id": "",  # 通知书编号
                    "classroom": "",  # 授课教室
                    "teaching_hours": "",  # 授课课时
                    "group_number": "",  # 群号
                    "link": "",  # 链接
                    "class": "",  # 班级
                    "remark": "",  # 备注
                }

                div = td.find_all("div")
                # 数量小于5，可认为没有课程
                if len(div) <= 5:
                    continue

                # 查找有效数据
                res_data = []
                for div_data in div[1:]:
                    res_data = div_data.find_all("font")
                    if res_data:
                        break

                # 数据处理放入字典
                single_course = self.format_course_data(single_course, res_data)
                course_data.append(single_course)

        return course_data

    def format_course_data(self, single_course_ori: dict, res_data: bs4.element.ResultSet) -> dict:
        """
        格式化处理课程数据
        :param single_course_ori: 源模板字典
        :param res_data: 数据参数
        :return: 处理后的字典
        """
        course_data = copy.deepcopy(single_course_ori)

        for font in res_data:
            if not font:
                continue

            name_data = font.get("name")
            title_data = font.get("title")
            text_data = font.text.strip()

            # 课程名称
            if not name_data and not title_data:
                add_data(course_data, "course_name", text_data)
            # 授课教室
            elif title_data == "教室":
                add_data(course_data, "classroom", text_data)
            # 授课教室
            elif title_data == "教师":
                add_data(course_data, "teacher", text_data)
            # 课程周次
            elif title_data == "周次(节次)":
                add_data(course_data, "week_session", text_data)
            # 通知单编号
            elif name_data == "tzdbh":
                add_data(course_data, "course_id", text_data[6:])
            # 群号和链接
            elif name_data == "wkxx":
                group_and_link = text_data.split("群号：")[1].split("链接：")
                add_data(course_data, "group_number", group_and_link[0])
                add_data(course_data, "link", group_and_link[1])
            # 班级
            elif name_data == "ktmcstr":
                add_data(course_data, "class", text_data[3:])
            # 备注
            elif name_data == "bzstr":
                add_data(course_data, "remark", text_data[3:])
            # 授课课时
            elif name_data == "xsks":
                # 针对单格数据中出现多个课程的情况
                text_data = text_data.replace('(', '').replace(')', '').split(",")
                for i in text_data:
                    if i in course_data["teaching_hours"]:
                        continue
                    add_data(course_data, "teaching_hours", i)
        log.debug("查询到的课程数据" + str(course_data))
        return course_data

    def count_8_am_and_2_pm(self, data_list: list[dict]) -> (int, int):
        """
        早八和午二计数
        :param data_list: 需统计的列表数据
        :return: 数量
        """
        i = 0
        j = 0
        for data in data_list:
            if data["period"] == "1":
                i += 1
            if data["period"] == "4":
                j += 1
        return i, j


if __name__ == "__main__":
    from core.plugins.jwxt.user import jwxtUser
    from config import jwxt_account, jwxt_password
    from core.tool import set_work_dir

    set_work_dir()

    jwxt_user = jwxtUser(jwxt_account, jwxt_password)
    if jwxt_user.login_jwxt():
        r_session = jwxt_user.get_session()
    else:
        exit(0)

    jwxt_course = jwxtSchedule()
    data = jwxt_course.get_course(jwxt_user.get_session(), "2025-2026-1")
    print(data)


