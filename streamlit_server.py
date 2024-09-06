import streamlit as st
import os
from config import Config
from douban_client import DoubanClient
from report_generator import ReportGenerator
from llm import LLM
from subscription_manager import SubscriptionManager
from logger import LOG

# 初始化配置和客户端
config = Config()
douban_client = DoubanClient()
subscription_manager = SubscriptionManager(config.subscriptions_file)

# 定义主要处理函数
def export_daily_progress(city, favor, model, key):
    if not key:
        st.error("请输入API Key")
        return None, None
    if not model:
        st.error("请选择模型")
        return None, None
    if not city:
        st.error("请选择城市")
        return None, None
    if not favor:
        st.error("请输入你的观影偏好")
        return None, None
    llm = LLM(model, key)
    print(llm.test_connection())
    if llm.test_connection() == 1: 
        st.error("请输入正确的key")
        return None, None
    report_generator = ReportGenerator(llm)
    city_arr = subscription_manager.list_subscriptions()
    for item in city_arr:
        if list(item.keys())[0] == city:
            city = item[city]
            break
    raw_file_path = douban_client.export_daily_progress(city)
    report, report_file_path = report_generator.generate_daily_report(raw_file_path, favor)

    return report, report_file_path

# 创建 Streamlit 表单
st.title("电影推荐小助手")

# 动态加载城市选项
city_arr = [list(item.keys())[0] for item in subscription_manager.list_subscriptions()]
city = st.selectbox("选择你的城市", city_arr)

# 输入观影偏好
favor = st.text_input("你的观影偏好", placeholder="请输入你的观影偏好")

# 模型选择
model = st.selectbox("选择模型", ["OpenAI", "智谱清言"])

# 输入API Key
key = st.text_input("输入您的 API Key", type="password")

# 提交按钮
if st.button("生成报告"):
    report, report_file_path = export_daily_progress(city, favor, model, key)
    if report:
        st.markdown(report)
        # 提供下载链接
        with open(report_file_path, "rb") as file:
            btn = st.download_button(label="下载报告", data=file, file_name="daily_report.md", mime="text/markdown")