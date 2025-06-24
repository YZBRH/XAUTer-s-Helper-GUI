# -*- coding: utf-8 -*-
# @Time    : 2025/1/29 下午9:26
# @Author  : BR
# @File    : tab_window.py
# @description: 标签界面
import copy
import sys
import os
from PySide6.QtGui import QPalette, QColor, QStandardItemModel, Qt, QStandardItem
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QGroupBox, QSizePolicy, QLabel, QTextEdit, \
    QApplication, QTabWidget, QMainWindow, QComboBox, QRadioButton, QCheckBox, QTableView, QHeaderView, QFileDialog, \
    QLineEdit, QTableWidget, QTableWidgetItem

from core.plugins.jwxt.score import jwxtScore
from core.plugins.jwxt.schedule import jwxtSchedule
from core.plugins.jwxt.course_selection import jwxtCourseSelection
from ui.common_window import error_dialog, information_dialog, warning_dialog, fileDialog, ReadOnlyModel, ClearableQPushButton
from ui.function_window import loginWindow
from core import log
from core.tool import getUrlConnectByThread, set_work_dir, get_default_term


class baseTab:
    """
    基础选项卡
    """
    tab = None

    def __init__(self):
        self.tab = QWidget()

    def get_tab(self) -> QWidget:
        """
        获取标签对象
        :return:
        """
        return self.tab


class personInformationTab(baseTab):
    """
    个人信息选项卡
    """
    check_thread = None
    jwxt_user = None

    def __init__(self, parent=None):
        log.debug("个人信息选项卡初始化")
        self.parent = parent
        super().__init__()

        # 主布局
        main_layout = QVBoxLayout()

        # 个人信息主布局
        person_information_layout = QVBoxLayout()
        # 提示信息布局
        person_information_tip_layout = QHBoxLayout()
        person_information_layout.addLayout(person_information_tip_layout)
        # 操作选项布局
        person_information_btn_layout = QHBoxLayout()
        person_information_layout.addLayout(person_information_btn_layout)

        # 操作选项
        self.login_btn = QPushButton("登录")
        self.logout_btn = QPushButton("注销")
        self.permission_btn = QPushButton("检测权限")
        self.internet_btn = QPushButton("检测网络连接")

        person_information_btn_layout.addWidget(self.login_btn)
        person_information_btn_layout.addWidget(self.logout_btn)
        person_information_btn_layout.addWidget(self.permission_btn)
        person_information_btn_layout.addWidget(self.internet_btn)

        # 个人信息组框
        person_information_groupbox = QGroupBox("个人信息")
        person_information_groupbox.setLayout(person_information_layout)
        person_information_groupbox.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        # 个人信息-姓名布局
        self.name_label = QLabel("姓名：未登录")
        person_information_tip_layout.addWidget(self.name_label)

        # 个人信息-班级布局
        self.class_layout = QLabel("班级：未登录")
        person_information_tip_layout.addWidget(self.class_layout)

        # 个人信息-学号布局
        self.id_label = QLabel("学号：未登录")
        person_information_tip_layout.addWidget(self.id_label)

        # 个人信息-权限布局
        permission_label = QLabel("权限：普通用户")
        person_information_tip_layout.addWidget(permission_label)

        # 个人信息-网络链接布局
        self.internet_label = QLabel("网络状态：未知")
        person_information_tip_layout.addWidget(self.internet_label)

        # 添加到主布局
        main_layout.addWidget(person_information_groupbox)
        # 临时占位
        tmp_widget = QTextEdit("")
        tmp_widget.setReadOnly(True)
        main_layout.addWidget(tmp_widget)

        self.tab.setLayout(main_layout)

        self.bind()

    def bind(self):
        """
        绑定按钮事件
        :return:
        """
        self.login_btn.clicked.connect(self.login_btn_clicked)
        self.logout_btn.clicked.connect(self.logout_btn_clicked)
        self.permission_btn.clicked.connect(self.permission_btn_clicked)
        self.internet_btn.clicked.connect(self.check_internet_connect)

    def login_btn_clicked(self):
        """
        登录按钮点击事件
        :return:
        """
        log.debug("登录按钮被点击")
        if self.name_label.text().strip() != "姓名：未登录" or self.jwxt_user.get_login_status():
            log.info("已存在登录账户，请先退出该账户！")
            information_dialog("已存在登录账户，请先退出该账户！")
            return

        login_window = loginWindow()
        login_window.exec()

        if login_window.account_lineedit.text() != "" and login_window.get_login_status():
            log.debug("更新登录信息")
            self.jwxt_user = login_window.get_jwxt_user()
            self.update_person_information(self.jwxt_user.get_username(), self.jwxt_user.get_class(),
                                           self.jwxt_user.get_id())

    def logout_btn_clicked(self):
        """
        注销按钮点击事件
        :return:
        """
        log.debug("注销按钮被点击")

        if self.name_label.text().strip() == "姓名：未登录":
            log.info("未登录，无需注销！")
            information_dialog("未登录，无需注销！")
            return

        if not warning_dialog("确定注销登录吗？"):
            return

        self.jwxt_user.logout()
        self.update_person_information(self.jwxt_user.get_username(), self.jwxt_user.get_class(),
                                       self.jwxt_user.get_id())

    def update_person_information(self, username: str, class_: str, id_: str):
        """
        更新个人信息
        :return:
        """
        self.name_label.setText("姓名：" + username)
        self.class_layout.setText("班级：" + class_)
        self.id_label.setText("学号：" + id_)

    def permission_btn_clicked(self):
        """
        权限按钮点击事件
        :return:
        """
        log.debug("权限检测按钮被点击")
        information_dialog("功能开发中！")

    def check_internet_connect(self):
        """
        检测网络连接状态
        :return:
        """
        log.debug("网络检测按钮被点击")
        if self.check_thread is None or not self.check_thread.isRunning():
            log.info("正在测试网络连接状态！")

            palette = QPalette()
            self.internet_label.setText("网络状态：尝试连接")
            palette.setColor(QPalette.WindowText, QColor("yellow"))
            self.internet_label.setPalette(palette)

            self.check_thread = getUrlConnectByThread("http://jwgl.xaut.edu.cn/")
            #  self.check_thread = getUrlConnectByThread("https://baidu.com")
            self.check_thread.result.connect(self.update_internet_status)
            self.check_thread.start()

    def update_internet_status(self, status: bool, result: object) -> None:
        """
        更新网络连接状态
        :param status:是否成功建立连接
        :param result:返回结果
        :return:
        """
        log.debug("测试完成！更新网络连接状态！")
        self.check_thread.quit()
        palette = QPalette()
        try:
            if status:
                self.internet_label.setText("网络状态：连接正常")
                palette.setColor(QPalette.WindowText, QColor("green"))
            else:
                self.internet_label.setText("网络状态：连接超时")
                palette.setColor(QPalette.WindowText, QColor("red"))

            self.internet_label.setPalette(palette)
            self.check_thread = None

            if status:
                log.info("网络连接正常！")
            else:
                error_dialog("网络连接超时！可能是你的网络炸了或者教务系统寄了！\n请过一会再重试一下！")

        except Exception as e:
            log.error(f"网络测试失败，原因：{e}")



class scoreTab(baseTab):
    """
    成绩选项卡
    """
    jwxt_score = jwxtScore()
    score_data_show = []  # 展示表格数据

    def __init__(self, parent=None):
        log.debug("成绩选项卡初始化")
        self.parent = parent
        super().__init__()

        # 主布局
        main_layout = QVBoxLayout()

        # 提示栏主布局
        # 开课时间下拉框
        term_layout = QHBoxLayout()
        term_label = QLabel("开课时间：")
        self.term_combox = QComboBox()
        self.term_combox.addItems(["全部", "2027-2028-2", "2027-2028-1",
                                   "2026-2027-2", "2026-2027-1", "2025-2026-2", "2025-2026-1",
                                   "2024-2025-2", "2024-2025-1", "2023-2024-2", "2023-2024-1",
                                   "2022-2023-2", "2022-2023-1", "2021-2022-2", "2021-2022-1",
                                   "2020-2021-2", "2020-2021-1", "2019-2020-2", "2019-2020-1"])
        self.term_combox.setCurrentText(get_default_term())
        term_layout.addWidget(term_label)
        term_layout.addWidget(self.term_combox)

        # 课程属性下拉框
        attribute_layout = QHBoxLayout()
        attribute_label = QLabel("课程属性：")
        self.attribute_combox = QComboBox()
        self.attribute_combox.addItems(["全部", "公共基础课", "专业基础课", "专业课", "选修课", "其他"])
        attribute_layout.addWidget(attribute_label)
        attribute_layout.addWidget(self.attribute_combox)

        # 课程性质下拉框
        type_layout = QHBoxLayout()
        type_label = QLabel("课程性质：")
        self.type_combox = QComboBox()
        self.type_combox.addItems(["全部", "必修课", "院级选修课", "校级选修课", "其他"])
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_combox)

        # 是否替换"未评教"为实际分数
        self.replace_unevaluated = QCheckBox("干掉'请评教'")
        self.replace_unevaluated.setCheckState(Qt.Checked)

        # 是否显示不及格成绩
        self.failed_score = QCheckBox("是否统计不及格成绩")
        self.failed_score.setCheckState(Qt.Checked)

        # 刷新按钮
        self.refresh_btn = QPushButton("刷新成绩")

        # 查询按钮
        self.query_btn = QPushButton("筛选查询")

        # 导出按钮
        self.export_btn = QPushButton("导出该成绩")

        # 不及格科目数
        self.failed_score_num_label = QLabel("不及格科目数：0")

        # 当前学期平均绩点
        self.current_GPA_label = QLabel("当前绩点：-1")

        # 选择栏组框
        # 第一行
        layout_tmp_1 = QHBoxLayout()
        layout_tmp_1.addLayout(term_layout)
        layout_tmp_1.addStretch(1)
        layout_tmp_1.addLayout(attribute_layout)
        layout_tmp_1.addStretch(1)
        layout_tmp_1.addLayout(type_layout)
        layout_tmp_1.addStretch(1)
        layout_tmp_1.addWidget(self.refresh_btn)
        layout_tmp_1.addStretch(1)
        layout_tmp_1.addWidget(self.query_btn)
        layout_tmp_1.addStretch(1)
        layout_tmp_1.addWidget(self.export_btn)

        # 第二行
        layout_tmp_2 = QHBoxLayout()
        layout_tmp_2.addWidget(self.replace_unevaluated)
        layout_tmp_2.addStretch(1)
        layout_tmp_2.addWidget(self.failed_score)
        layout_tmp_2.addStretch(1)
        layout_tmp_2.addWidget(self.failed_score_num_label)
        layout_tmp_2.addStretch(1)
        layout_tmp_2.addWidget(self.current_GPA_label)
        layout_tmp_2.addStretch(1)

        # 一二行组合
        layout_tmp_main = QVBoxLayout()
        layout_tmp_main.addLayout(layout_tmp_1)
        layout_tmp_main.addLayout(layout_tmp_2)

        query_groupbox = QGroupBox("课程成绩查询")
        query_groupbox.setLayout(layout_tmp_main)
        query_groupbox.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        main_layout.addWidget(query_groupbox)

        # 表格
        self.table = ReadOnlyModel(0, 9)

        self.table.setHorizontalHeaderLabels(
            ["课程名称", "课程编号", "学分", "成绩", "绩点", "成绩标识", "补重学期", "课程属性", "课程性质"])

        table_view = QTableView()
        table_view.setModel(self.table)

        # 设置水平表头最后一列随窗口大小拉伸
        table_view.horizontalHeader().setStretchLastSection(True)

        # 设置所有列宽随窗口大小调整/允许用户自由拉伸/根据内容自动调整列宽
        # table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        # table_view.horizontalHeader().setStretchLastSection(True)
        table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        main_layout.addWidget(table_view)

        self.tab.setLayout(main_layout)

        self.bind()

    def bind(self):
        self.refresh_btn.clicked.connect(self.refresh_btn_clicked)
        self.query_btn.clicked.connect(self.query_btn_clicked)
        self.export_btn.clicked.connect(self.export_btn_clicked)

    def refresh_btn_clicked(self):
        """
        刷新成绩
        :return:
        """
        log.debug("刷新事件触发")
        if not self.parent.person_information_tab.jwxt_user.get_login_status():
            error_dialog("登录状态异常，请重新登录后再试！")
            return

        self.jwxt_score.refresh_score_data(self.parent.person_information_tab.jwxt_user.get_session())
        log.info("刷新完成")

    def query_btn_clicked(self):
        """
        成绩查询
        :return:
        """
        log.debug("查询事件触发")
        term = self.term_combox.currentText()
        if term == "全部":
            term = ""

        course_attribute = self.attribute_combox.currentText()
        if course_attribute == "全部":
            course_attribute = ""

        course_type = self.type_combox.currentText()
        if course_type == "全部":
            course_type = ""

        replace_unevaluated = self.replace_unevaluated.isChecked()
        failed_score = self.failed_score.isChecked()

        # 如果未刷新过数据，则主动刷新一次数据
        if self.jwxt_score.get_score_data_all() == [] or self.jwxt_score.get_score_data() == []:
            log.info("首次查询，自动刷新一次")
            jwxt_user = self.parent.person_information_tab.jwxt_user

            if not jwxt_user.get_login_status():
                jwxt_user.logout()
                error_dialog("请先登录！")
                return

            self.refresh_btn_clicked()

        # 获取基础展示列表
        score_data_show = self.jwxt_score.get_score_data_all()
        if score_data_show == []:
            log.warning("未从 成绩查询接口 成功获取基准数据，将使用 已修课程接口 数据作为基准")
            score_data_show = self.jwxt_score.get_score_data()

        # 替换"请评教"数据
        if replace_unevaluated:
            log.debug("替换'请评教'")
            score_data_show = self.jwxt_score.replace_unevaluated(score_data_show)

        # 筛选获得最终显示数据
        self.score_data_show = self.jwxt_score.data_filter(score_data_show, term, course_attribute, course_type,
                                                           failed_score)

        # 绩点计算
        self.current_GPA_label.setText(
            "当前绩点：" + str(self.jwxt_score.get_average_GPA(self.score_data_show, failed_score)))

        # 不及格科目数
        self.failed_score_num_label.setText(
            "不及格科目数：" + str(self.jwxt_score.get_failed_score_num(self.score_data_show)))

        # 填充数据
        self.full_table(self.score_data_show)

    def export_btn_clicked(self):
        log.debug("导出事件触发")
        log.debug(f"尝试导出数据为：{self.score_data_show}")

        if not self.score_data_show:
            error_dialog("无数据可以导出！")
            return
        file_path, _ = fileDialog().file_save(os.path.join(os.getcwd(), "output", "成绩单"), "Excel Files (*.xlsx)")

        if not file_path:
            log.info("导出操作取消")
            return

        self.jwxt_score.export_to_execl(self.score_data_show, file_path)
        information_dialog("导出成功！")

    def full_table(self, score_data: list[dict]):
        """
        填充表格数据
        :param score_data: 成绩字典列表
        :return:
        """
        self.clear_table()
        if score_data is None or len(score_data) == 0:
            error_dialog("未查询到数据！")
            return

        for index, x in enumerate(score_data):
            course_name = QStandardItem(x["course_name"])
            course_number = QStandardItem(x["course_number"])
            credit = QStandardItem(x["credit"])
            score = QStandardItem(x["score"])
            GPA = QStandardItem(x["GPA"])
            score_flag = QStandardItem(x["score_flag"])
            reschedule_term = QStandardItem(x["reschedule_term"])
            course_attribute = QStandardItem(x["course_attribute"])
            course_type = QStandardItem(x["course_type"])

            self.table.insertRow(index, [course_name, course_number, credit, score, GPA, score_flag, reschedule_term, course_attribute, course_type])

    def clear_table(self):
        """
        清空表格数据
        :return:
        """
        self.table.removeRows(0, self.table.rowCount())


class scheduleTab(baseTab):
    """
    课程选项卡
    """
    jwxt_schedule = jwxtSchedule()
    schedule_data = []

    def __init__(self, parent=None):
        log.debug("课程选项卡初始化")
        self.parent = parent
        super().__init__()

        # 主布局
        main_layout = QVBoxLayout()

        # 提示栏主布局
        # 学年学期下拉框
        term_layout = QHBoxLayout()
        term_label = QLabel("学年学期：")
        self.term_combox = QComboBox()
        self.term_combox.addItems(["", "2027-2028-2", "2027-2028-1",
                                   "2026-2027-2", "2026-2027-1", "2025-2026-2", "2025-2026-1",
                                   "2024-2025-2", "2024-2025-1", "2023-2024-2", "2023-2024-1",
                                   "2022-2023-2", "2022-2023-1", "2021-2022-2", "2021-2022-1",
                                   "2020-2021-2", "2020-2021-1", "2019-2020-2", "2019-2020-1"])
        self.term_combox.setCurrentText(get_default_term())
        term_layout.addWidget(term_label)
        term_layout.addWidget(self.term_combox)

        # 周次下拉框
        week_layout = QHBoxLayout()
        week_label = QLabel("周次：")
        self.week_combox = QComboBox()

        week_list = ["全部"]
        for i in range(1, 30):
            week_list.append("第" + str(i) + "周")

        self.week_combox.addItems(week_list)
        week_layout.addWidget(week_label)
        week_layout.addWidget(self.week_combox)

        # 极简显示
        self.simple_display = QCheckBox("极简显示")
        self.simple_display.setChecked(True)

        # 刷新按钮
        self.refresh_btn = QPushButton("刷新课表")

        # 早八与午二统计
        self.statistics_label = QLabel("共有 0 个早八，0 个午二")

        # 选择栏组框
        layout_tmp_1 = QHBoxLayout()
        layout_tmp_1.addLayout(term_layout)
        layout_tmp_1.addStretch(1)
        layout_tmp_1.addLayout(week_layout)
        layout_tmp_1.addStretch(1)
        layout_tmp_1.addWidget(self.simple_display)
        layout_tmp_1.addStretch(1)
        layout_tmp_1.addWidget(self.refresh_btn)

        layout_tmp_main = QVBoxLayout()
        layout_tmp_main.addLayout(layout_tmp_1)
        layout_tmp_main.addWidget(self.statistics_label)

        query_groupbox = QGroupBox("课程时间表")
        query_groupbox.setLayout(layout_tmp_main)
        query_groupbox.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        main_layout.addWidget(query_groupbox)

        # 表格
        self.table = ReadOnlyModel(6, 7)
        self.set_table_hander()

        table_view = QTableView()
        table_view.setModel(self.table)

        # 设置水平表头最后一列随窗口大小拉伸
        table_view.horizontalHeader().setStretchLastSection(True)

        # 设置所有列宽随窗口大小调整/允许用户自由拉伸/根据内容自动调整列宽
        table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table_view.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        # table_view.horizontalHeader().setStretchLastSection(True)

        #table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        main_layout.addWidget(table_view)

        self.tab.setLayout(main_layout)

        self.bind()

    def set_table_hander(self):
        self.table.setHorizontalHeaderLabels(
            ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期天"])
        self.table.setVerticalHeaderLabels(
            ["第一大节 \n(01,02小节)\n08:00-09:50", "第二大节\n(03,04小节)\n10:10-12:00",
             "第三大节\n(05,06小节)\n12:10-14:00",
             "第四大节\n(07,08小节)\n14:10-16:00", "第五大节\n(09,10小节)\n16:10-18:00",
             "第六大节\n(11,12,13小节)\n19:00-21:50"]
        )

    def bind(self):
        self.refresh_btn.clicked.connect(self.refresh_btn_clicked)

    def full_statistics_label(self):
        """
        刷新统计栏
        :return:
        """
        am_8, pm_2 = self.jwxt_schedule.count_8_am_and_2_pm(self.schedule_data)
        text = f"共有 {am_8} 个早八，{pm_2} 个午二"
        if am_8 == 0 and pm_2 == 0:
            text += "，没有早八，也没有午二，这才是应该有的大学生活嘛！！！"
        elif am_8 >= 5:
            text += "，哦吼全是早八，悲~~"
        elif am_8 == 0:
            text += "，没有早八，爽！"
        elif am_8 >= 3:
            text += "，一半多都是早八？"
        else:
            text += "，也还不错啦~"
        self.statistics_label.setText(text)

    def refresh_btn_clicked(self):
        term = self.term_combox.currentText()
        week = self.week_combox.currentText()
        if week == "全部":
            week = ""
        else:
            week = week.split("第")[1].split("周")[0]

        if not self.parent.person_information_tab.jwxt_user.get_login_status():
            error_dialog("登录状态异常，请重新登录后再试！")
            return

        self.schedule_data = self.jwxt_schedule.get_course(self.parent.person_information_tab.jwxt_user.get_session(),
                                                           term, week)
        self.full_table(self.schedule_data, self.simple_display.isChecked())
        self.full_statistics_label()

    def full_table(self, schedule_data: list[dict], simple: bool = True):
        self.clear_table()
        if schedule_data is None or len(schedule_data) == 0:
            error_dialog("未查询到数据！")
            return

        for course in schedule_data:
            if simple:
                show_text = (f'{course["course_name"]}\n'
                             f'{course["week_session"]}\n'
                             f'{course["classroom"]}')
            else:
                show_text = (f'课程名称：{course["course_name"]}\n'
                             f'授课教师：{course["teacher"]}\n'
                             f'课程周次：{course["week_session"]}\n'
                             f'授课教室：{course["classroom"]}\n'
                             f'授课课时：{course["teaching_hours"]}\n'
                             f'授课班级：{course["class"]}\n'
                             f'通知书编号：{course["course_id"]}')

                if course["group_number"] != "":
                    show_text += f'\n群号：{course["group_number"]}'
                if course["link"] != "":
                    show_text += f'\n链接：{course["link"]}'''
                if course["remark"] != "":
                    show_text += f'\n备注：{course["remark"]}'

            item = QStandardItem(show_text)
            item.setToolTip(show_text)
            self.table.setItem(int(course["period"]) - 1, int(course["day"]) - 1, item)
            self.set_table_hander()

    def clear_table(self):
        self.table.removeRows(0, self.table.rowCount())


class examsAndTextbooksTab(baseTab):
    """
    考试及教材选项卡
    """

    def __init__(self, parent=None):
        log.debug("考试及教材初始化")
        self.parent = parent
        super().__init__()

        # 主布局
        main_layout = QVBoxLayout()

        # 提示栏主布局
        # 开课时间下拉框
        term_layout = QHBoxLayout()
        term_label = QLabel("学年学期：")
        self.term_combox = QComboBox()
        self.term_combox.addItems(["全部", "2027-2028-2", "2027-2028-1",
                                   "2026-2027-2", "2026-2027-1", "2025-2026-2", "2025-2026-1",
                                   "2024-2025-2", "2024-2025-1", "2023-2024-2", "2023-2024-1",
                                   "2022-2023-2", "2022-2023-1", "2021-2022-2", "2021-2022-1",
                                   "2020-2021-2", "2020-2021-1", "2019-2020-2", "2019-2020-1"])
        self.term_combox.setCurrentText(get_default_term())
        term_layout.addWidget(term_label)
        term_layout.addWidget(self.term_combox)

        # 考试查询按钮
        self.exam_query = QPushButton("考试查询")

        # 教材查询按钮
        self.textbook_query = QPushButton("教材查询")

        # 查询栏组框
        layout_tmp_main = QHBoxLayout()
        layout_tmp_main.addLayout(term_layout)
        layout_tmp_main.addStretch(1)
        layout_tmp_main.addWidget(self.exam_query)
        layout_tmp_main.addWidget(self.textbook_query)
        query_groupbox = QGroupBox("考试与教材")
        query_groupbox.setLayout(layout_tmp_main)

        main_layout.addWidget(query_groupbox)

        # 表格
        table_view = self.set_exam_table()

        main_layout.addWidget(table_view)

        self.tab.setLayout(main_layout)

    def set_base_tableview(self) -> QTableView:
        table_view = QTableView()
        table_view.setModel(self.table)

        # 设置水平表头最后一列随窗口大小拉伸
        table_view.horizontalHeader().setStretchLastSection(True)
        # 设置所有列宽随窗口大小调整/允许用户自由拉伸/根据内容自动调整列宽
        table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table_view.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        return table_view

    def set_exam_table(self) -> QTableView:
        self.table = ReadOnlyModel(0, 11)
        self.table.setHorizontalHeaderLabels(["校区", "考试校区", "考试场次", "课程编号",
                                              "课程名称", "授课教室", "考试时间", "考场",
                                              "座位号", "准考证号", "备注"])
        table_view = self.set_base_tableview()
        return table_view

    def set_textbook_table(self) -> QTableView:
        self.table = ReadOnlyModel(0, 10)
        self.table.setHorizontalHeaderLabels(["课程编号", "课程名称", "ISBN书号", "教材名称",
                                              "定价", "版次", "出版社", "上课教师",
                                              "上课院系", "征订状态"])
        table_view = self.set_base_tableview()
        return table_view


class courseSelectionTab(baseTab):
    """
    选课选项卡
    """
    jwxt_course_selection = jwxtCourseSelection()
    # 表格按钮存贮
    table_btn = {}
    # 查询到的数据暂存
    search_data = []

    def __init__(self, parent=None):
        log.debug("选课选项卡初始化")
        self.parent = parent
        super().__init__()

        # 主布局
        main_layout = QVBoxLayout()

        # 提示框布局
        # 开课时间下拉框
        term_layout = QHBoxLayout()
        term_label = QLabel("开课学年学期：")
        self.term_combox = QComboBox()
        self.term_combox.addItems(["全部", "2027-2028-2", "2027-2028-1",
                                   "2026-2027-2", "2026-2027-1", "2025-2026-2", "2025-2026-1",
                                   "2024-2025-2", "2024-2025-1", "2023-2024-2", "2023-2024-1",
                                   "2022-2023-2", "2022-2023-1", "2021-2022-2", "2021-2022-1",
                                   "2020-2021-2", "2020-2021-1", "2019-2020-2", "2019-2020-1"])
        self.term_combox.setCurrentText(get_default_term())
        term_layout.addWidget(term_label)
        term_layout.addWidget(self.term_combox)

        # 课程名称/编号输入框
        course_layout = QHBoxLayout()
        course_label = QLabel("课程名称/编号：")
        self.course_name_lineedit = QLineEdit()
        course_layout.addWidget(course_label)
        course_layout.addWidget(self.course_name_lineedit)

        # 授课教师输入框
        teacher_layout = QHBoxLayout()
        teacher_label = QLabel("授课教师：")
        self.teacher_lineedit = QLineEdit()
        teacher_layout.addWidget(teacher_label)
        teacher_layout.addWidget(self.teacher_lineedit)

        # 校区选择
        campus_layout = QHBoxLayout()
        campus_label = QLabel("校区：")
        self.campus_combox = QComboBox()
        self.campus_combox.addItems(["全部", "金花校区", "曲江校区", "莲湖校区", "曲江校区(西区)"])
        campus_layout.addWidget(campus_label)
        campus_layout.addWidget(self.campus_combox)

        # 查询课程按钮
        self.course_query_btn = ClearableQPushButton("查询并添加课程")

        # 获取当前已选择预选课按钮
        self.current_course_btn = ClearableQPushButton("查询当前已预定课程")

        # 当前选定轮次
        self.round = QLabel("当前选定轮次：N/A")
        self.set_round_information(self.jwxt_course_selection.get_current_round().get("name", None))

        # 选择选课轮次按钮
        self.round_select_btn = ClearableQPushButton("查询并选择轮次")

        # 开始选课按钮
        self.start_btn = ClearableQPushButton("开始选课")

        # 第一行组框
        layout_tmp_1 = QHBoxLayout()
        layout_tmp_1.addLayout(term_layout)
        layout_tmp_1.addStretch(1)
        layout_tmp_1.addLayout(course_layout)
        layout_tmp_1.addStretch(1)
        layout_tmp_1.addLayout(teacher_layout)
        layout_tmp_1.addStretch(1)
        layout_tmp_1.addLayout(campus_layout)
        layout_tmp_1.addStretch(1)
        layout_tmp_1.addWidget(self.course_query_btn)

        # 第二行组框
        layout_tmp_2 = QHBoxLayout()
        layout_tmp_2.addWidget(self.round)
        layout_tmp_2.addStretch(1)
        layout_tmp_2.addWidget(self.round_select_btn)
        layout_tmp_2.addStretch(1)
        layout_tmp_2.addWidget(self.current_course_btn)
        layout_tmp_2.addStretch(1)
        layout_tmp_2.addWidget(self.start_btn)

        # 一二行组框组合
        layout_tmp_main = QVBoxLayout()
        layout_tmp_main.addLayout(layout_tmp_1)
        layout_tmp_main.addLayout(layout_tmp_2)

        course_selection_groupbox = QGroupBox("选课")
        course_selection_groupbox.setLayout(layout_tmp_main)
        course_selection_groupbox.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        main_layout.addWidget(course_selection_groupbox)

        # 表格
        self.table = self.use_course_table()

        self.table_view = QTableView()
        self.table_view.setModel(self.table)
        # 设置水平表头最后一列随窗口大小拉伸
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        main_layout.addWidget(self.table_view)

        self.tab.setLayout(main_layout)

        self.bind()

    def bind(self):
        self.course_query_btn.clicked.connect(self.course_query)
        self.current_course_btn.clicked.connect(self.get_current_course)
        self.round_select_btn.clicked.connect(self.round_query)

    def course_query(self):
        """
        课程查询
        :return:
        """
        log.info("课程查询按钮触发")
        log.info("开始查询课程")
        term = self.term_combox.currentText()
        if term == "全部":
            term = ""

        name = self.course_name_lineedit.text()
        teacher = self.teacher_lineedit.text()

        campus = self.campus_combox.currentText()
        if campus == "金花校区":
            campus = "1"
        elif campus == "曲江校区":
            campus = "2"
        elif campus == "莲湖校区":
            campus = "3"
        elif campus == "曲江校区(西区)":
            campus = "4"
        else:
            campus = ""

        if not self.parent.person_information_tab.jwxt_user.get_login_status():
            error_dialog("登录状态异常，请重新登录后再试！")
            return

        self.search_data = self.jwxt_course_selection.get_course(self.parent.person_information_tab.jwxt_user.get_session(), term, name, teacher, campus)
        self.full_course_table(self.search_data)
        self.full_course_table_btn(len(self.search_data), 9)

        if len(self.search_data) == 0:
            error_dialog("未查询到任何符合要求的课程！")

    def get_current_course(self):
        """
        查询当前已选择课程事件
        :return:
        """
        log.info("查询已选择课程事件触发")
        self.search_data = copy.deepcopy(self.jwxt_course_selection.get_current_course())
        self.full_course_table(self.search_data)
        self.full_course_table_btn(len(self.search_data), 9)

        if len(self.search_data) == 0:
            error_dialog("当前无已选择的课程")

    def use_course_table(self):
        table = ReadOnlyModel(0, 10)
        table.setHorizontalHeaderLabels(["课程名称", "教师", "上课班级", "课程编号", "学分", "学时", "上课时间", "上课地点", "备注", "操作"])
        return table

    def full_course_table(self, course_data: list[dict]):
        """
        填充课程表格
        :param course_data: 课程数据
        :return:
        """
        log.info("表格数据填充")
        self.clear_table()
        self.table = self.use_course_table()
        self.table_view.setModel(self.table)
        for index, x in enumerate(course_data):
            course_name = QStandardItem(x["course_name"])
            course_teacher = QStandardItem(x["teacher_name"])
            course_class = QStandardItem(x["class"])
            course_id = QStandardItem(x["course_id"])
            course_credit = QStandardItem(x["credit"])
            course_hours = QStandardItem(x["total_hours"])

            course_time_text = x["class_time"].replace(";", "\n").strip()
            course_time = QStandardItem(course_time_text)
            course_time.setToolTip(course_time_text)

            course_location = QStandardItem(x["class_location"])
            remark = QStandardItem(x["remark"])

            self.table.insertRow(index, [course_name, course_teacher, course_class, course_id, course_credit, course_hours, course_time, course_location, remark])

    def full_course_table_btn(self, total_row: int, column: int):
        """
        添加课程表格按钮
        :param total_row: 总行数
        :param column: 指定列
        :return:
        """
        log.info("添加表格按钮")
        self.table_btn = {}
        for i in range(total_row):
            if self.jwxt_course_selection.course_exist(self.search_data[i]["notice_id"]):
                btn = ClearableQPushButton("删除")
                btn.connect_signal(btn.clicked, lambda _, r=i: self.remove_course(r))
            else:
                btn = ClearableQPushButton("添加")
                btn.connect_signal(btn.clicked, lambda _, r=i: self.add_course(r))

            self.table_btn[i] = btn
            self.table_view.setIndexWidget(self.table_view.model().index(i, column), btn)

    def add_course(self, row: int):
        """
        按钮点击添加课程事件
        :param row: 目标行
        :return:
        """
        if not warning_dialog("确定添加该课程吗？"):
            return
        log.info(f"第{row+1}列被点击，添加至课程列表")

        self.table_btn[row].setText("删除")
        self.table_btn[row].disconnect_all_slots()
        self.table_btn[row].connect_signal(self.table_btn[row].clicked, lambda _, r=row: self.remove_course(r))

        self.jwxt_course_selection.add_course(self.search_data[row])
        self.jwxt_course_selection.save_course_to_file()

    def remove_course(self, row: int):
        """
        按钮删除课程事件
        :param row:
        :return:
        """
        if not warning_dialog("确定删除该课程吗？"):
            return
        log.info(f"第{row+1}列被点击，从课程列表删除")

        self.table_btn[row].setText("添加")
        self.table_btn[row].disconnect_all_slots()
        self.table_btn[row].connect_signal(self.table_btn[row].clicked, lambda _, r=row: self.add_course(r))

        self.jwxt_course_selection.remove_course(self.search_data[row]["notice_id"])
        self.jwxt_course_selection.save_course_to_file()

    def clear_table(self):
        """
        清空表格
        :return:
        """
        self.table.removeRows(0, self.table.rowCount())

    def use_round_table(self):
        table = ReadOnlyModel(0, 5)
        table.setHorizontalHeaderLabels(["学期学年", "选课名称", "选课时间", "选课编号", "操作"])
        return table

    def set_round_information(self, message: str = None):
        if message is None or message == "":
            text = "N/A"
        else:
            text = message
        log.info(f"当前选定轮次设置为：{text}")
        self.round.setText(f"当前选定轮次：{text}")

    def round_query(self):
        log.info("轮次查询按钮触发")
        self.search_data = self.jwxt_course_selection.get_course_selection_rounds(self.parent.person_information_tab.jwxt_user.get_session())
        self.full_round_table(self.search_data)
        self.full_round_table_btn(len(self.search_data), 4)

        if len(self.search_data) == 0:
            error_dialog("未查询到任何符合要求的轮次！")

    def full_round_table(self, round_data: list[dict]):
        """
        填充轮次表格
        :param round_data: 轮次数据
        :return:
        """
        log.info("轮次数据添加")
        self.clear_table()
        self.table = self.use_round_table()
        self.table_view.setModel(self.table)
        for index, x in enumerate(round_data):
            self.table.insertRow(index, [QStandardItem(x["term"]), QStandardItem(x["name"]), QStandardItem(x["time"]), QStandardItem(x["round_id"])])

    def full_round_table_btn(self, total_row: int, column: int):
        """
        添加轮次表格按钮
        :param total_row: 总行数
        :param column: 指定列
        :return:
        """
        log.info("添加表格按钮")
        self.table_btn = {}
        current_select = -1
        for i in range(total_row):
            if self.search_data[i]["round_id"] == self.jwxt_course_selection.get_current_round().get("round_id", ""):
                btn = ClearableQPushButton("已选")
                current_select = i
                btn.setEnabled(False)
            else:
                btn = ClearableQPushButton("选择")
                btn.connect_signal(btn.clicked, lambda _, r=i, c=current_select: self.select_round(r, c))

            self.table_btn[i] = btn
            self.table_view.setIndexWidget(self.table_view.model().index(i, column), btn)

    def select_round(self, row: int, curent_select: int):
        """
        按钮点击选择轮次事件
        :param row: 目标行
        :param curent_select: 当前已选择的轮次
        :return:
        """
        if not warning_dialog("确定选择该轮次吗？"):
            return
        log.info(f"第{row + 1}列被点击，选择为目标轮次")
        self.table_btn[row].setEnabled(False)
        self.table_btn[row].setText("已选")
        self.jwxt_course_selection.set_round(self.search_data[row])
        self.set_round_information(self.jwxt_course_selection.get_current_round().get("name", None))

        if curent_select != -1:
            self.table_btn[curent_select].setEnabled(True)
            self.table_btn[curent_select].disconnect_all_slots()
            self.table_btn[curent_select].clicked.connect(lambda _, r=curent_select, c=row: self.select_round(r, c))
            self.table_btn[curent_select].setText("选择")


class otherTab(baseTab):
    """
    其他选项卡
    """

    def __init__(self):
        log.debug("其他选项卡初始化")
        super().__init__()


if __name__ == '__main__':
    set_work_dir()
    app = QApplication(sys.argv)

    window = QMainWindow()

    tab = QTabWidget()
    tab.setTabPosition(QTabWidget.North)

    test_tab = courseSelectionTab()
    tab.addTab(test_tab.tab, "测试选项卡")

    window.setCentralWidget(tab)

    window.show()

    sys.exit(app.exec())
