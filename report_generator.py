import os
from datetime import date, timedelta
from logger import LOG

class ReportGenerator:
    def __init__(self, llm):
        self.llm = llm

    def generate_daily_report(self, markdown_file_path, favor):
        with open(markdown_file_path, 'r', encoding="utf-8") as file:
            markdown_content = file.read()

        report = self.llm.generate_daily_report(markdown_content, favor)

        report_file_path = os.path.splitext(markdown_file_path)[0] + "_report.md"
        with open(report_file_path, 'w+', encoding="utf-8") as report_file:
            report_file.write(report)

        LOG.info(f"Generated report saved to {report_file_path}")
        
        return report, report_file_path
