# -*- coding: utf-8 -*-
# @Time    : 2025/2/6 上午12:23
# @Author  : BR
# @File    : course_selection.py
# @description: 选课相关
import json
import os

import requests
from bs4 import BeautifulSoup

from core import log


class jwxtCourseSelection:
    # 可选择课程查询接口
    course_query_url = "http://jwgl.xaut.edu.cn/jsxsd/jskb/qxzkbQuery.do?type=1"
    # 选课轮次接口
    course_selection_rounds_list_url = "http://jwgl.xaut.edu.cn/jsxsd/xsxk/xklc_list"
    # 选课主界面接口（选课前置）
    course_selection_main_url = "http://jwgl.xaut.edu.cn/jsxsd/xsxk/newXsxkzx?jx0502zbid={*jx0502zbid*}"
    # 选课按钮接口（选课前置）
    course_selection_button_url = "http://jwgl.xaut.edu.cn/jsxsd/xsxk/selectBottom?jx0502zbid={*jx0502zbid*}&sfylxkstr="
    # 课程选择接口
    course_selection_curriculum_url = "http://jwgl.xaut.edu.cn/jsxsd/xsxkkc/bxxkOper?kcid={*kcid*}&cfbs=null&jx0404id={*jx0404id*}&xkzy=&trjf="

    def __init__(self):
        # 已选择的课程信息
        self.course_data = []
        # 已选择轮次
        self.current_round = {}

        self.read_course_from_file()
        self.read_round_from_file()

    def get_course(self, r_session: requests.Session, term: str, name: str, teacher: str, campus: str, page_index: int = 1, index_limit: int = 5) -> list[dict]:
        """
        根据筛选条件获取课程
        :param r_session: 处于登录状态的requests.Session
        :param term: 学年学期
        :param name: 课程名称或编号
        :param teacher: 授课教师
        :param campus: 校区
        :param page_index: 当前查询的页面索引值（递归递增）
        :param index_limit: 允许最大的递归次数（默认为5）
        :return: 查询到的符合条件的课程
        """
        post_data = {
            "xnxq01id": term,  # 学年学期
            "kbjcmsid": "47A852EDE04746E8913E2D79DBCEBB7F",  # 时间模式，默认为默认节次模式
            "xq": campus,  # 校区, 空-全选,1-金花校区,2-曲江校区,3-莲湖校区,4-曲江校区(西区)
            "kkyx": "",  # 开课院系, 空-全选,01-材料科学与工程学院,02-机械与精密仪器工程学院,03-印刷包装与数字媒体学院,
                         # 04-自动化与信息工程学院,05-经济与管理学院,06-水利水电学院,07-人文与外国语学院,08-理学院,09-计算机科学与工程学院,
                         # 10-体育教学部,11-马克思主义学院,12-工程训练中心,13-曲江校区,14-艺术与设计学院,15-现代分析测试中心,16-土木建筑工程学院,
                         # 17-电气工程学院,22-国际工学院,30-云课堂平台,31-学生处,803-西北旱区生态水利国重室,99-临时单位
            "skyx": "",  # 上课院系, 空-全选,01-材料科学与工程学院,02-机械与精密仪器工程学院,03-印刷包装与数字媒体学院,
                         # 04-自动化与信息工程学院,05-经济与管理学院,06-水利水电学院,07-人文与外国语学院,08-理学院,09-计算机科学与工程学院,
                         # 10-体育教学部,11-马克思主义学院,12-工程训练中心,13-曲江校区,14-艺术与设计学院,15-现代分析测试中心,16-土木建筑工程学院,
                         # 17-电气工程学院,22-国际工学院
            "sknj": "",  # 上课年级, 例2025,空-全部
            "skzy": "",  # 上课专业, 空-全部
            "kc": name,  # 课程名称或编号
            "kclb": "",  # 课程类别, 空-全部, 01-理论课(不含实践),02-理论课(含实践),03-实验课,04-集中性实践环节
            "kcsx": "",  # 课程属性, 空-全部, 1-必修课,4-校级选修课,9-其他,2-院级选修
            "zc1": "",  # 周次开始, 空-全部
            "zc2": "",  # 周次结束, 空-全部
            "jc1": "",  # 节次开始, 空-全部
            "jc2": "",  # 节次结束, 空-全部
            "txklb": "",    # 通选课类别, 空-全部, 1-人文社科(A)类,2-自然科学(B)类,3-公共艺术(C)类,4-创新创业(D)类,9-其他
            "skxq1": "",  # 星期开始, 空-全部
            "skxq2": "",  # 星期结束, 空-全部
            "skls": teacher,  # 授课教师
            "pageIndex": str(page_index)  # 第几页
        }

        try:
            res = r_session.post(self.course_query_url, data=post_data)
        except Exception as e:
            log.error(f"获取课程失败，原因: {str(e)}")
            return []

        if "未查询到数据" in res.text:
            log.info(f"未查询到课程信息")
            return []

        soup = BeautifulSoup(res.text, "html.parser")

        script = None
        for s in soup.find_all("script"):
            if not s:
                break
            if "pageNum" in s.text:
                script = s

        # 当前页数
        current_index = script.text.split("current: ")[1].split(",")[0]
        # 最大页数
        max_index = script.text.split("pageNum: ")[1].split(",")[0]

        table = soup.find("table", class_="layui-table")
        trs = table.find_all("tr")

        course_data = []
        for tr in trs[1:]:
            tds = tr.find_all("td")
            single_course_data = {
                "select_id": tds[1].text.strip(),  # 选课课号
                "notice_id": tds[2].text.strip(),  # 通知单编号
                "campus": tds[3].text.strip(),  # 校区
                "open_department": tds[4].text.strip(),  # 开课院系
                "teacher_id": tds[5].text.strip(),  # 教师职工号
                "teacher_name": tds[6].text.strip(),  # 教师姓名
                "job_title": tds[7].text.strip(),  # 职称
                "course_id": tds[8].text.strip(),  # 课程编号
                "course_name": tds[9].text.strip(),  # 课程名称
                "course_tag": tds[10].text.strip(),  # 课程标签
                "course_type": tds[11].text.strip(),  # 课程类别
                "study_department": tds[12].text.strip(),  # 上课院系
                "class": tds[13].text.strip(),  # 上课班级
                "total_people": tds[14].text.strip(),  # 人数
                "current_people": tds[15].text.strip(),  # 已选人数
                "weekly_hours": tds[16].text.strip(),  # 周学时
                "s2e_weeks": tds[17].text.strip(),  # 起止周
                "credit": tds[18].text.strip(),  # 学分
                "scheduled_hours": tds[19].text.strip(),  # 已排学时
                "total_hours": tds[20].text.strip(),  # 总学时
                "lecture_hours": tds[21].text.strip(),  # 讲课学时
                "computer_hours": tds[22].text.strip(),  # 上机学时
                "extracurricular_hours": tds[23].text.strip(),  # 课外学时
                "experimental_hours": tds[24].text.strip(),  # 实验学时
                "assessment_method": tds[25].text.strip(),  # 考核方式
                "course_categories": tds[26].text.strip(),  # 课程大类
                "course_nature": tds[27].text.strip(),  # 课程性质
                "course_attribute": tds[28].text.strip(),  # 课程属性
                "class_time": tds[29].text.strip(),  # 上课时间
                "class_location": tds[30].text.strip(),  # 上课地点
                "remark": tds[31].text.strip(),  # 备注
                "General_course_category": tds[32].text.strip(),  # 通选课类别
                "group_number": tds[33].text.strip(),  # 网课群号
                "link": tds[34].text.strip(),  # 链接
            }
            course_data.append(single_course_data)
        log.info(f"正在获取课程信息，筛选条件为：学年学期：{term}，课程名称或编号：{name}，授课教师：{teacher}，校区id：{campus}， 当前页数：{current_index}，最大页数：{max_index}，允许的最大页数：{index_limit}")
        log.info(f"查询到数据：{course_data}")
        if int(current_index) < int(max_index) and int(current_index) < index_limit:
            course_data.extend(self.get_course(r_session, term, name, campus, teacher, page_index + 1))

        return course_data

    def get_course_selection_rounds(self, r_session: requests.Session) -> list[dict]:
        """
        获取选课轮次信息
        输出格式示例：
        [{
        '学期学年': '2024-2025-2',
        '选课名称': '2024-2025-2第一轮选课',
        '选课时间': '2025-01-02 08:30~2025-01-03 17:00',
        'jx0502zbid': '63BD32E2E3B24FA58A9D16219D1545D5'
        }]
        :param r_session: 处于登录状态的requests.Session
        :return: 获取到的选课轮次信息
        """
        log.info("正在获取选课轮次")

        try:
            res = r_session.get(self.course_selection_rounds_list_url)
        except Exception as e:
            log.error(f"获取选课轮次失败，原因: {str(e)}")
            return []

        # 数据处理提取
        soup = BeautifulSoup(res.text, "html.parser")
        trs = soup.find_all("tr")

        data = []
        for tr in trs:
            tds = tr.find_all("td")
            if tds:
                if len(tds) < 4:  # 跳过显然不符合条件的数据
                    continue
                new_data = {
                    "term": tds[0].text,  # 学期学年
                    "name": tds[1].text,  # 选课名称
                    "time": tds[2].text,  # 选课时间
                    "round_id": tds[3].find('span', attrs={'onclick': True})['onclick'][10:-6:]  # 选课编号
                }
                data.append(new_data)

        log.info(f"获取到数据为: {data}")
        return data

    def course_selection_first(self, r_session: requests.Session, jx0502zbid: str) -> bool:
        """
        自动选课前置

        :param r_session:
        :param jx0502zbid: 选课轮次id
        :return: 是否成功
        """
        log.info("正在执行选课前置")

        goal_url_main = (self.course_selection_main_url
                         .replace("{*jx0502zbid*}", jx0502zbid))
        goal_url_button = (self.course_selection_button_url
                           .replace("{*jx0502zbid*}", jx0502zbid))

        try:
            res = r_session.get(goal_url_main)
            if "未开放选课" in res.text or "不在选课时间范围" in res.text:
                log.error("选课前置失败，选课未开放")
                return False
            else:
                r_session.get(goal_url_button)
                return True
        except Exception as e:
            log.error(f"选课前置失败，原因: {str(e)}")
            return False

    def select_curriculum(self, r_session: requests.Session, curriculum_data: dict[str, str]) -> bool:
        """
        尝试选择目标课程
        输入格式示例:
        {
        "curriculum_name": "体育2",
        "curriculum_teacher": "高天悦",
        "kcid": "10100060",
        "jx0404id": "202420252001766"
        }

        :param r_session: 处于登录状态的requests.Session
        :param curriculum_data: 课程数据
        :return:
        """
        # 不同类别选课请求url虽不同，但似乎可通用，故以下暂时注释掉不使用
        """if data["type"] == "必修课":
            select_url = url + f"xsxkkc/bxxkOper?kcid={data['kcid']}&cfbs=null&jx0404id={data['jx0404id']}&xkzy=&trjf="
        elif data["type"] == "院选修":
            select_url = url + ""
        elif data["type"] == "校选修":
            select_url = url + f"xsxkkc/ggxxkxkOper?kcid={data['kcid']}&cfbs=null&jx0404id={data['jx0404id']}&xkzy=&trjf="
        elif data["type"] == "跨专业/年级选课":
            select_url = url + ""
        elif data["type"] == "体育选课":
            select_url = url + ""
        elif data["type"] == "实验选课":
            select_url = url + f"xsxkkc/SyxkOper?kcid={data['kcid']}&cfbs=null&jx0404id={data['jx0404id']}&xkzy=&trjf="
        else:
            print("选课数据有误，请检查数据格式后重试！")
        """
        goal_url = (self.course_selection_curriculum_url
                    .replace("{*jx0404id*}", curriculum_data["jx0404id"])
                    .replace("{*kcid*}", curriculum_data["kcid"]))

        res = r_session.get(goal_url, timeout=3600)
        log.debug("选课回显数据包：" + res.text)

        curriculum_information = f"【{curriculum_data['curriculum_name']}-{curriculum_data['curriculum_teacher']}】"

        # 各种情况处理
        if "true" in res.text:
            log.info(f"{curriculum_information}选课成功!")
            return True

        if "false" in res.text:
            msg = json.loads(res.text)
            if msg["message"]:
                log.error(f"{curriculum_information}选课失败，原因: {msg['message']}")
                if "已选" in msg["message"]:  # 已选课程
                    log.info(f"{curriculum_information}已选过！后续将不再选择！")
                    return True
                return False

            log.error(f"{curriculum_information}未获得有效回显，如持续出现请检查预选课配置信息！")
            return False

        log.error("未从服务器中获取有效响应！")
        return False

    def save_course_to_file(self):
        log.info("开始课程文件保存")
        try:
            with open(os.path.join(os.getcwd(), "data", "course.json"), "w", encoding="utf-8") as fp:
                json.dump(self.course_data, fp, ensure_ascii=False, indent=4)
            log.info("课程文件保存完成")
        except Exception as e:
            log.error(f"课程文件保存失败，原因：{e}")

    def read_course_from_file(self):
        log.info("开始课程文件读取")
        try:
            with open(os.path.join(os.getcwd(), "data", "course.json"), "r", encoding="utf-8") as fp:
                self.course_data = json.load(fp)
                log.info(f"课程文件读取完成，读取数据为：{self.course_data}")
        except Exception as e:
            log.error(f"课程文件读取失败，原因：{e}")

    def get_current_course(self) -> list[dict]:
        """
        获取当前课程
        :return:
        """
        return self.course_data

    def add_course(self, course: dict):
        """
        添加课程
        :param course: 要添加的课程信息
        :return:
        """
        self.course_data.append(course)

    def remove_course(self, notice_id: str):
        """
        根据通知书编号删除课程
        :param notice_id:
        :return:
        """
        for i in self.course_data:
            if i["notice_id"] == notice_id:
                self.course_data.remove(i)
                log.info(f"删除课程成功，删除课程为：{i}")
                return
        log.info(f"删除课程失败，未找到课程：{notice_id}")

    def course_exist(self, notice_id: str) -> bool:
        """
        根据通知书编号判断课程是否已存在
        :param notice_id: 通知书编号
        :return: 是否存在
        """
        try:
            for i in self.course_data:
                if i["notice_id"] == notice_id:
                    return True
        except Exception as e:
            log.error(f"判断课程是否存在失败，原因：{e}")
        return False

    def save_round_to_file(self):
        log.info("开始轮次文件保存")
        try:
            with open(os.path.join(os.getcwd(), "data", "round.json"), "w", encoding="utf-8") as fp:
                json.dump(self.current_round, fp, ensure_ascii=False, indent=4)
            log.info("轮次文件保存完成")
        except Exception as e:
            log.error(f"轮次文件保存失败，原因：{e}")

    def read_round_from_file(self):
        log.info("开始选课轮次读取")
        try:
            with open(os.path.join(os.getcwd(), "data", "round.json"), "r", encoding="utf-8") as fp:
                self.current_round = json.load(fp)
                log.info(f"轮次文件读取完成，读取数据为：{self.current_round}")
        except Exception as e:
            log.error(f"轮次文件读取失败，原因：{e}")

    def set_round(self, round_data: dict):
        self.current_round = round_data
        self.save_round_to_file()

    def get_current_round(self) -> dict:
        return self.current_round


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

    cs = jwxtCourseSelection()
    data = cs.get_course_selection_rounds(jwxt_user.get_session())

    print(data)

        
    