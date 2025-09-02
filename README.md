## 前言

​	本项目是[YZBRH/XAUTer-s-UEAS_helper](https://github.com/YZBRH/XAUTer-s-UEAS_helper)的GUI版本，目前处于demo状态，正在极其缓慢开发中。



​	目前已实现功能：

- 自动登录及验证码识别

- 成绩查询

- 绩点计算

- 课程表查询

  

​	即将实现功能：

- 考试信息查询
- 教程信息查询
- 自动选课
- 通过VPN登录教务系统



## 环境要求

​	推荐运行环境：

- windows10及以上系统
- python 3.10.4及更新版本



## 使用指南

​	首次使用，你需要将config-example.py修改为config.py，并且完成其中包括账号密码在内的配置信息。

​	执行

```bash
python main.py
```

​	等待启动即可

## 项目结构说明

│
├─core				     核心逻辑部分，包含各种功能函数
│  └─plugins 
│		└─jwxt
├─data					  持久化保存的系统配置
├─log						程序运行日志
├─output				 程序输出结果
├─resources			资源文件
│  ├─images
│  └─verification_code
└─ui						  ui相关配置代码



## 已知部分问题及解决方法



## 更新记录

- V0.1.1 [2025/09/02]    

  - 修复在课表单格出现多个课程时，查询失败的问题

  

- V0.1.0 [2025/09/02]	

  - demo概念版

  

