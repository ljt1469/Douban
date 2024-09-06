import requests
from datetime import datetime, date, timedelta
import os
from logger import LOG
import random
from lxml import etree

class DoubanClient:
    def __init__(self):
        self.headers = self.header_x()
    def header_x(self):
        # 随机获取一个headers
        user_agents = ['Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
                       'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
                       'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2',
                       'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
                       'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER',
                       'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 SE 2.X MetaSr 1.0'
                       ]

        headers = {
            "User-Agent": random.choice(user_agents)
        }
        return headers
    
    def fetch_updates(self, city):
        url = f'https://movie.douban.com/cinema/nowplaying/{city}/'
        headers = self.header_x()
        resp = requests.get(url, headers=headers)
        html = etree.HTML(resp.text)
        movie_list = []
        #movies = html.xpath(".//div[@id='nowplaying']/div[@class='mod-bd']/ul/li[@class='stitle']/a/text()")
        movies = html.xpath(".//div[@id='nowplaying']/div[@class='mod-bd']/ul/li")
        for item in movies:
            m_url = item.xpath(".//li[@class='poster']/a/@href")[0]
            headers = self.header_x()
            resp = requests.get(m_url, headers=headers)
            html = etree.HTML(resp.text)
            title = html.xpath(".//div[@id='content']/h1/span[@property='v:itemreviewed']/text()")[0]
            rating = html.xpath(".//div[@class='rating_self clearfix']/strong/text()")[0] if html.xpath(".//div[@class='rating_self clearfix']/strong/text()") else '暂无评分'
            type = html.xpath(".//div[@id='info']/span[@property='v:genre']/text()")[0] if html.xpath(".//div[@id='info']/span[@property='v:genre']/text()") else '暂无类型'
            print(title,rating,type)
            movie_list.append ({
                'title': title,
                'rating': rating,
                'type': type
            })
        return movie_list
      
    def export_daily_progress(self, city):
        today = datetime.now().date().isoformat()
        updates = self.fetch_updates(city)
        
        repo_dir = os.path.join('daily_progress', city)
        os.makedirs(repo_dir, exist_ok=True)
        
        file_path = os.path.join(repo_dir, f'{today}.md')
        with open(file_path, 'w', encoding="utf-8") as file:
            file.write(f"# 正在热映的电影 ({today})\n\n")
            headers = ['电影名称', '评分', '类型']
            rows = [[movie['title'], movie['rating'], movie['type']] for movie in updates]
            markdown_table = self.create_markdown_table(headers, rows)
            file.write(markdown_table)
        LOG.info(f"Exported daily progress to {file_path}")
        return file_path
      
    def create_markdown_table(self, headers, rows):
        # 创建表头
        header_row = "| " + " | ".join(headers) + " |"
        separator_row = "| " + " | ".join(["---"] * len(headers)) + " |"

        # 创建数据行
        data_rows = []
        for row in rows:
            data_row = "| " + " | ".join(map(str, row)) + " |"
            data_rows.append(data_row)

        # 合并成完整的表格
        table = "\n".join([header_row, separator_row] + data_rows)
        return table
      
if __name__ == "__main__":
    douban_client = DoubanClient()
    report = douban_client.export_daily_progress("beijing")