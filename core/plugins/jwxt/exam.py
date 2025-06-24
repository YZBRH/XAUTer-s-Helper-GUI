# -*- coding: utf-8 -*-
# @Time    : 2025/2/6 上午12:17
# @Author  : BR
# @File    : exam.py
# @description: 教务系统考试相关

import requests
from bs4 import BeautifulSoup

from core import log


class jwxtExam:
    """
    教务系统考试相关类
    """
    exam_url = "http://jwgl.xaut.edu.cn/jsxsd/xsks/xsksap_list"

    def __init__(self):
        pass

    def get_exam(self, r_session: requests.Session, term: str = "") -> list[dict]:
        """
        获取考试信息
        :param r_session: 处于登录状态的requests.Session
        :param term: 学年学期
        :return: 考试信息
        """
        post_data = {
            "xqlbmc": "",
            "xnxqid": term  # 学年学期
        }

        try:
            res = r_session.post(self.exam_url, data=post_data)
        except Exception as e:
            log.error(f"获取考试信息失败：{e}")
            return []

        table_data = BeautifulSoup(res.text, "html.parser").find("table", id="dataList")
        if "未查询到数据" in table_data.text:
            return []

        trs = table_data.find_all("tr")

        exam_data = []
        for tr in trs:
            tds = tr.find_all("td")
            if len(tds) == 0:
                continue
            single_exam = {
                "campus": tds[1].text.strip(),  # 校区
                "exam_campus": tds[2].text.strip(),  # 考试校区
                "exam_session": tds[3].text.strip(),  # 考试场次
                "course_id": tds[4].text.strip(),  # 课程编号
                "course_name": tds[5].text.strip(),  # 课程名称
                "teacher": tds[6].text.strip(),  # 授课教师
                "exam_time": tds[7].text.strip(),  # 考试时间
                "exam_room": tds[8].text.strip(),  # 考场
                "seat_number": tds[9].text.strip(),  # 座位号
                "admission_ticket": tds[10].text.strip(),  # 准考证号
                "remark": tds[11].text.strip()  # 备注
            }
            exam_data.append(single_exam)

        return exam_data


if __name__ == "__main__":
    from core.tool import set_work_dir
    from core.plugins.jwxt.user import jwxtUser
    from config import jwxt_account, jwxt_password
    set_work_dir()
    jwxt_user = jwxtUser(jwxt_account, jwxt_password)
    if not jwxt_user.login_jwxt():
        exit(0)

    jwxt_exam = jwxtExam()
    data = jwxt_exam.get_exam(jwxt_user.get_session(), "2024-2025-1")
    print(data)

