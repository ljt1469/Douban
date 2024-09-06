# src/llm.py
import os
from zhipuai import ZhipuAI
from openai import OpenAI
from logger import LOG

class LLM:
    def __init__(self, model, key):
        self.model = model
        if self.model == "openAI":
            self.client = OpenAI(key)
        elif self.model == "智谱清言":
            #"2f5c3c7df9abcb9989a1086817dd87be.HPdNhOkCc3ymILfw"
            print(key)
            self.client = ZhipuAI(api_key=key)
        LOG.add("daily_progress/llm_logs.log", rotation="1 MB", level="DEBUG")
    
    def test_connection(self):
        try:
            if self.model == "openAI":
                self.client.ChatCompletion.create(model="gpt-4o", messages=[{"role": "user", "content": "Hello!"}])
            elif self.model == "智谱清言":
                self.client.chat.completions.create(
                    model="glm-4-flash",  # 填写需要调用的模型编码
                    messages=[{"role": "user", "content": "Hello!"}],
                    tools = [{"type":"web_search","web_search":{"search_result":True}}],
                )
        except Exception as e:
            return 1

    def generate_daily_report(self, markdown_content, favor, dry_run=False):
        # 使用从TXT文件加载的提示信息
        messages = [
            {"role": "system", "content": f'当前正在热映的电影信息如下：\n{markdown_content}\n '},
            {"role": "user", "content": f'我的观影偏好如下：\n{favor}\n 请推荐1-2部电影，并简要说明推荐理由。'},
        ]
        
        if dry_run:
            # 如果启用了dry_run模式，将不会调用模型，而是将提示信息保存到文件中
            LOG.info("Dry run mode enabled. Saving prompt to file.")
            with open("daily_progress/prompt.txt", "w+") as f:
                # 格式化JSON字符串的保存
                json.dump(messages, f, indent=4, ensure_ascii=False)
            LOG.debug("Prompt saved to daily_progress/prompt.txt")
            return "DRY RUN"

        # 日志记录开始生成报告
        LOG.info("Starting report generation using GPT model.")
        
        try:
            # 调用OpenAI GPT模型生成报告
            if self.model == "openAI":
                response = self.client.chat.completions.create(
                    model="gpt-4o",  # 使用配置中的OpenAI模型名称
                    messages=messages
                )
            elif self.model == "智谱清言":
                response = self.client.chat.completions.create(
                    model="glm-4-flash",  # 填写需要调用的模型编码
                    messages=messages,
                    tools = [{"type":"web_search","web_search":{"search_result":True}}],
                )
            LOG.debug("GPT response: {}", response)
            # 返回模型生成的内容
            return response.choices[0].message.content
        except Exception as e:
            # 如果在请求过程中出现异常，记录错误并抛出
            LOG.error("An error occurred while generating the report: {}", e)
            raise
        
if __name__ == "__main__":
    llm = LLM()
    from douban_client import DoubanClient
    douban_client = DoubanClient()
    #raw_file_path = douban_client.export_daily_progress("beijing")
    raw_file_path = "daily_progress\\beijing\\2024-09-05.md"
    with open(raw_file_path, 'r', encoding="utf-8") as file:
        markdown_content = file.read()
    favor = "喜欢的电影类型:科幻、悬疑。\n偏好的电影风格:有深度、剧情紧凑。\n不喜欢的电影类型:动画片、家庭类。\n"
    report = llm.generate_daily_report(markdown_content, favor)
    report_file_path = os.path.splitext(raw_file_path)[0] + "_report.md"
    with open(report_file_path, 'w+', encoding="utf-8") as report_file:
        report_file.write(report)
    print("finish")

