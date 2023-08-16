import os
import re
import glob
from datetime import datetime

# 获取当前目录下所有的.md文件
md_files = glob.glob('*.md')

articles = []

for md_file in md_files:
    with open(md_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            # 使用正则表达式匹配日期
            match = re.search(r'date: "(.*?)"', line)
            if match:
                date_str = match.group(1)
                # 将日期字符串转换为日期对象
                date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                # 将日期对象和文件名添加到列表中
                articles.append((date, os.path.splitext(md_file)[0]))
                break

# 按日期排序
articles.sort(reverse=True)

# 打印结果
for i, (date, md_file) in enumerate(articles, 1):
    print(f'{i}. {date.strftime("%Y年%m月%d日")} - {md_file}')