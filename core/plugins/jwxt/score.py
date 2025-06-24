# -*- coding: utf-8 -*-
# @Time    : 2025/2/1 上午11:00
# @Author  : BR
# @File    : score.py
# @description: 教务系统成绩相关

import copy
from bs4 import BeautifulSoup
import requests
import pandas as pd

from core import log


class jwxtScore:
    # 成绩查询接口
    score_search_url = "http://jwgl.xaut.edu.cn/jsxsd/kscj/cjcx_list"
    # 已修课程接口
    taken_courses_url = "http://jwgl.xaut.edu.cn/jsxsd/yxszzy/yxkc_list"
    # 从已修课程接口获取到的数据
    score_data = []
    # 从成绩查询接口获取到的数据
    score_data_all = []

    def __init__(self):
        pass

    def get_score_from_score_search(self, r_session: requests.Session,
                                    term: str = "", course_type: str = "", course_attribute: str = "",
                                    course_name: str = "", display_method: str = "max",
                                    overweight_grade: bool = False, failed_grade: bool = False,
                                    micro_specialization: bool = False
                                    ) -> list[dict]:
        """
        从成绩查询接口获取成绩（更新score_data_all）
        :param r_session: 处于登录状态的requests.Session
        :param term: 开课时间，无-全部
        :param course_type: 课程性质，无-全部，1-必修课，2-院级选修课，4-校级选修课，9-其他
        :param course_attribute: 课程属性，无-全部，02-公共基础课，03-专业基础课，04-专业课，11-其他，12-选修课
        :param course_name: 课程名称
        :param display_method: 显示方式，max-显示最好成绩，all-显示全部成绩
        :param overweight_grade: 是否显示补重成绩
        :param failed_grade: 是否只显示不及格成绩
        :param micro_specialization: 是否显示微专业
        :return: 查询到的字典列表数据
        """
        log.info("开始从 成绩查询接口 获取成绩获取成绩数据...")

        overweight_grade = "1" if overweight_grade else ""
        failed_grade = "1" if failed_grade else ""
        micro_specialization = "1" if micro_specialization else ""

        post_data = {
            "kksj": term,  # 开课时间，无-全部
            "kcsx": course_type,  # 课程性质，无-全部，1-必修课，2-院级选修课，4-校级选修课，9-其他
            "kcxz": course_attribute,  # 课程属性，无-全部，02-公共基础课，03-专业基础课，04-专业课，11-其他，12-选修课
            "kcmc": course_name,  # 课程名称
            "xsfs": display_method,  # 显示方式，max-显示最好成绩，all-显示全部成绩
            "sfxsbcxq": overweight_grade,  # 是否显示补重成绩，1-显示，无-不显示
            "zxsbjg": failed_grade,  # 是否只显示不及格成绩，1-显示，无-不显示
            "fxkcmc": micro_specialization,  # 是否显示微专业，1-显示，无-不显示
            "mold": ""
        }

        try:
            res = r_session.post(self.score_search_url, data=post_data)
        except Exception as e:
            log.error(f"访问数据接口失败，原因：{e}")
            return []

        # 数据处理
        datatable = BeautifulSoup(res.text, "html.parser").find("table", id="dataList")

        if not datatable or "未查询到数据" in datatable:
            log.info("未查询到成绩数据!")
            return []

        trs = datatable.find_all("tr")

        try:
            score_data = []
            for i in range(1, len(trs)):
                flag = True  # 标记是否跳过该条数据,若该条数据为空，则跳过不添加
                # 单科信息
                single_score = {
                    "term": "",  # 开课学期
                    "course_number": "",  # 课程编号
                    "course_name": "",  # 课程名称
                    "score": "",  # 成绩
                    "score_flag": "",  # 成绩标识
                    "credit": "",  # 学分
                    "period": "",  # 学时
                    "GPA": "",  # 绩点
                    "reschedule_term": "",  # 补重学期
                    "assessment_method": "",  # 考核方式
                    "exam_status": "",  # 考试性质
                    "course_type": "",  # 课程性质
                    "course_attribute": "",  # 课程属性
                    "general_course_type": ""  # 通选课类别
                }
                origin_data = trs[i]
                tds = origin_data.find_all("td")

                # 处理并放置数据
                for j in range(1, len(tds)):
                    flag = False
                    single_score[list(single_score.keys())[j - 1]] = tds[j].text.strip()

                # 特殊处理部分补考后的数据，将重复的进行合并
                for index, x in enumerate(score_data):
                    if single_score["course_number"] == x["course_number"]:
                        # 取成绩最高的
                        if single_score["score"] >= x["score"]:
                            score_data[index]["score"] = single_score["score"]
                            score_data[index]["GPA"] = single_score["GPA"]
                        # 补考学期与成绩标识合并
                        score_data[index]["reschedule_term"] += single_score["reschedule_term"]
                        score_data[index]["score_flag"] += single_score["score_flag"]
                        flag = True
                        break

                # 处理完后添加到列表中
                if not flag:
                    score_data.append(single_score)

        except Exception as e:
            log.error(f"数据处理失败，原因：{e}")
            return []

        log.debug(f"查询到数据为：{score_data}")
        return score_data

    def get_score_from_taken_courses(self, r_session: requests.Session) -> list[dict]:
        """
        从已修课程接口获取成绩（更新score_data）
        :param r_session: 处于登录状态的requests.session
        :return: 查询到的字典列表数据
        """

        log.info("开始从 已修课程接口 获取成绩获取成绩数据...")

        try:
            res = r_session.get(self.taken_courses_url)
        except Exception as e:
            log.error(f"访问数据接口失败，原因：{e}")
            return []

        # 数据处理
        datatable = BeautifulSoup(res.text, "html.parser").find("table", class_="layui-table")

        if not datatable or "未查询到数据" in datatable:
            log.info("未查询到成绩数据!")
            return []

        trs = datatable.find_all("tr")

        try:
            score_data = []
            for i in range(1, len(trs) - 2):
                flag = True  # 标记是否跳过该条数据,若该条数据为空，则跳过不添加
                # 单科信息
                single_score = {
                    "term": "",  # 开课学期
                    "course_number": "",  # 课程编号
                    "course_name": "",  # 课程名称
                    "course_attribute": "",  # 课程属性
                    "credit": "",  # 学分
                    "period": "",  # 学时
                    "score": "",  # 成绩
                    "exam_status": ""  # 考试性质
                }

                # 额外的，非直接查询数据
                extra_score_data = {
                    "score_flag": "unknown",  # 成绩标识
                    "GPA": "unknown",  # 绩点
                    "assessment_method": "unknown",  # 考核方式
                    "course_type": "unknown",  # 课程性质
                    "general_course_type": "unknown",  # 通选课类别
                    "reschedule_term": "unknown"  # 补重学期
                }

                single_score.update(extra_score_data)

                origin_data = trs[i]
                tds = origin_data.find_all("td")

                for j in range(1, len(tds)):
                    flag = False
                    single_score[list(single_score.keys())[j - 1]] = tds[j].text.strip()

                if not flag:
                    single_score["GPA"] = str(self.score_to_GPA(single_score["score"]))
                    score_data.append(single_score)
        except Exception as e:
            log.error(f"数据处理失败，原因：{e}")
            return []

        log.debug(f"查询到数据为：{score_data}")
        return score_data

    def data_filter(self, score_data: list[dict], term: str = "", course_attribute: str = "", course_type: str = "",
                    failed_score: bool = False):
        """
        筛选得到指定数据
        :param score_data: 需要筛选的数据
        :param term: 指定的开课时间
        :param course_attribute: 指定的课程属性
        :param course_type: 指定的课程性质
        :param failed_score: 是否统计不及格成绩
        :return: 筛选后的字典列表数据
        """
        log.debug(f"原始数据: {score_data}")
        new_score_data = []
        log.debug(f"筛选数据，指定学期为：{term}，课程属性为：{course_attribute}，课程性质为：{course_type}")
        try:
            for score in score_data:
                # 挨个筛选
                if term != "" and score["term"] != term.strip():
                    continue
                if course_attribute != "" and score["course_attribute"] != course_attribute.strip():
                    continue
                if course_type != "" and score["course_type"] != course_type.strip():
                    continue

                try:
                    if (float(score["score"]) < 60 or score["score"] == "不及格") and not failed_score:
                        continue
                except Exception as e:
                    pass

                new_score_data.append(score)
        except Exception as e:
            log.error(f"数据筛选失败，原因：{e}")
            return score_data

        log.debug(f"筛选后的数据为：{new_score_data}")
        return new_score_data

    def get_score_data_by_course_number(self, score_data: list[dict], course_number: str) -> dict | None:
        """
        通过课程编号获取指定课程成绩
        :param score_data: 需要替换的数据
        :param course_number: 指定课程编号
        :return:
        """
        for score in score_data:
            if score["course_number"] == course_number.strip():
                return score
        log.error(f"通过课程编号{course_number} 未检索到指定数据！")
        return None

    def replace_unevaluated(self, score_data: list[dict]) -> list[dict]:
        """
        将"未评教"数据替换成实际得分
        :param score_data: 需要替换的数据
        :return:
        """
        score_data_all = self.get_score_data()
        new_score_data = []
        for score in copy.deepcopy(score_data):
            tmp_data = score
            # 如果存在"请评教"就替换
            if tmp_data["score"] == "请评教":
                data = self.get_score_data_by_course_number(score_data_all, tmp_data["course_number"])
                if data is None:
                    log.error("未检索到数据，替换失败！")
                else:
                    tmp_data["score"] = data["score"]
                    tmp_data["GPA"] = str(self.score_to_GPA(float(tmp_data["score"])))
            new_score_data.append(tmp_data)
        return new_score_data

    def export_to_execl(self, score_data: list[dict], file_path: str = "成绩.xlsx"):
        df = pd.DataFrame(score_data)
        df = df.rename(columns={"term": "开课学期", "course_number": "课程编号", "course_name": "课程名称",
                                "score": "成绩", "score_flag": "成绩标识", "credit": "学分",
                                "period": "学时", "GPA": "绩点", "reschedule_term": "补重学期",
                                "assessment_method": "考核方式", "exam_status": "考试性质", "course_type": "课程性质",
                                "course_attribute": "课程属性", "general_course_type": "通选课类别"})
        df.index += 1
        df.to_excel(file_path, index=True)

    def get_failed_score_num(self, score_data: list[dict]) -> int:
        num = 0
        for score in score_data:
            if score["score"] == "请评教":
                continue

            try:
                if float(score["score"]) < 60:
                    num += 1
            except ValueError as e:
                if score["score"] == "不合格":
                    num += 1
        return num

    def get_score_data_all(self):
        """
        获取成绩信息
        :return:
        """
        return self.score_data_all

    def get_score_data(self):
        """
        获取成绩信息
        :return:
        """
        return self.score_data

    def refresh_score_data(self, r_session: requests.Session) -> bool:
        """
        刷新成绩信息
        :param r_session: 已登录的Session
        :return: 是否刷新成功
        """
        try:
            self.score_data_all = self.get_score_from_score_search(r_session, display_method="all",
                                                                   overweight_grade=True)
            self.score_data = self.get_score_from_taken_courses(r_session)
            log.info("成绩成功刷新")
            log.debug(f"score_data_all={self.score_data_all}")
            log.debug(f"score_data={self.score_data}")
        except Exception as e:
            log.error(f"成绩刷新失败，原因：{e}")
            return False
        return True

    def get_average_GPA(self, score_data: list[dict], failed_course: bool = False) -> float:
        """
        计算平均绩点
        :param score_data: 成绩字典列表
        :param failed_course: 是否统计不及格科目
        :return: 计算后的平均分数
        """
        total_score = 0
        total_credit = 0
        result = -1
        try:
            for score in score_data:
                # 跳过不及格科目
                if float(score["GPA"]) < 0.1 and not failed_course:
                    continue
                total_score += float(score["GPA"]) * float(score["credit"])
                total_credit += float(score["credit"])
            result = total_score / total_credit
        except Exception as e:
            log.warning(f"计算平均得分失败，原因：{e}")
            return -1
        return result

    def grade_to_GPA(self, score: str | float) -> float:
        """
        如果是等级成绩转化绩点
        :param score: 等级
        :return: 转化后的绩点
        """
        if isinstance(score, float):
            return score

        score = score.strip()
        if score == "优":
            return 4.5
        elif score == "良":
            return 3.5
        elif score == "中":
            return 2.5
        elif score == "及格":
            return 1.5
        elif score == "不及格":
            return 0.0
        else:
            log.error(f"绩点转化失败！非预期的 {score} ！")
            return 0.0

    def score_to_GPA(self, score: (float, str)) -> float:
        """
        成绩得分转化绩点
        :param score: 成绩得分
        :return: 转化后的绩点
        """
        try:
            score = float(score)

            if score < 0 or score > 100:
                log.warning("成绩得分不在0-100范围内")
                return 0.0

            if score < 60:
                return 0.0
            elif score >= 95:
                return 5.0
            else:
                return 1.5 + (score - 60) / 10
        except Exception as e:
            log.warning(f"成绩转化绩点失败，原因：{e}")
            return 0.0


if __name__ == '__main__':
    from core.plugins.jwxt.user import jwxtUser
    from core.tool import set_work_dir
    from config import jwxt_account, jwxt_password

    set_work_dir()
    jwxt_user = jwxtUser(jwxt_account, jwxt_password)
    jwxt_user.login_jwxt()
    if jwxt_user.check_login_status():
        log.info("登录成功")
    else:
        log.error("登录失败")

    jwxt_score = jwxtScore()
    jwxt_score.refresh_score_data(jwxt_user.get_session())
    data = jwxt_score.get_score_data()
    print(jwxt_score.score_to_GPA(jwxt_score.get_average_GPA(data)))
