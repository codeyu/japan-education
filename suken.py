import os
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import time

def download_pdf(url, save_path):
    """下载PDF文件"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # 确保目录存在
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # 保存文件
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return True
    except Exception as e:
        print(f"下载失败 {url}: {str(e)}")
        return False

def main():
    # 基础URL和保存目录
    base_url = 'https://www.su-gaku.net/suken/support/past_questions/'
    save_dir = os.path.join('数検', '検定過去問題')
    
    # 获取网页内容
    response = requests.get(base_url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 查找所有PDF链接
    for box in soup.find_all('div', class_='box'):
        # 获取级别标题
        title = box.find('h4')
        if not title:
            continue
        level = title.text.strip()
        
        # 创建级别目录
        level_dir = os.path.join(save_dir, level)
        os.makedirs(level_dir, exist_ok=True)
        
        # 查找所有PDF链接
        for link in box.find_all('a', href=re.compile(r'.*\.pdf')):
            url = urljoin(base_url, link.get('href'))
            filename = link.text.strip() + '.pdf'
            save_path = os.path.join(level_dir, filename)
            
            print(f"下载 {level} - {filename}...")
            if download_pdf(url, save_path):
                print(f"完成: {filename}")
                # 添加短暂延迟，避免请求过快
                time.sleep(1)
            else:
                print(f"跳过: {filename}")

if __name__ == '__main__':
    main()
