# https://www.kanken.or.jp/kanken/outline/degree/example.html

import os
import requests
from bs4 import BeautifulSoup
import re

def download_pdf(url, save_path):
    """下载PDF文件"""
    response = requests.get(url)
    with open(save_path, 'wb') as f:
        f.write(response.content)

def main():
    # 创建保存目录
    save_dir = os.path.join('漢検', '2023年度第3回検定')
    os.makedirs(save_dir, exist_ok=True)

    # 直接从网站获取HTML
    url = 'https://www.kanken.or.jp/kanken/outline/degree/example.html'
    response = requests.get(url)
    response.encoding = 'utf-8'  # 设置正确的编码
    html = response.text
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # 查找所有PDF链接
    for row in soup.find_all('tr'):
        # 获取级别
        level = row.find('img', alt=re.compile(r'[0-9準]*級'))
        if not level:
            continue
        level_text = level['alt']
        
        # 获取PDF链接
        links = row.find_all('a', href=re.compile(r'.*\.pdf$'))
        for link in links:
            url = link['href']
            # 判断是问题还是答案
            is_mondai = '検定問題' in link.text
            type_text = '問題' if is_mondai else '解答'
            
            # 构建文件名
            filename = f"{level_text}_{type_text}.pdf"
            save_path = os.path.join(save_dir, filename)
            
            print(f"下载 {filename}...")
            download_pdf(url, save_path)
            print(f"完成: {filename}")

if __name__ == '__main__':
    main()
