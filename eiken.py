# https://www.eiken.or.jp/eiken/exam/grade_1/
# https://www.eiken.or.jp/eiken/exam/grade_p1/
# https://www.eiken.or.jp/eiken/exam/grade_2/
# https://www.eiken.or.jp/eiken/exam/grade_p2/
# https://www.eiken.or.jp/eiken/exam/grade_3/
# https://www.eiken.or.jp/eiken/exam/grade_4/
# https://www.eiken.or.jp/eiken/exam/grade_5/

import os
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import time

def get_grade_from_url(url):
    """从URL中提取级别信息"""
    grade_map = {
        'grade_1': '1級',
        'grade_p1': '準1級',
        'grade_2': '2級',
        'grade_p2': '準2級',
        'grade_3': '3級',
        'grade_4': '4級',
        'grade_5': '5級'
    }
    
    for key, value in grade_map.items():
        if key in url:
            return value
    return None

def download_file(url, save_path, file_type):
    """下载文件（PDF或MP3）"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # 确保目录存在
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # 如果文件已存在且大小相同，则跳过
        if os.path.exists(save_path):
            if os.path.getsize(save_path) == int(response.headers.get('content-length', 0)):
                print(f"文件已存在，跳过: {save_path}")
                return True
        
        # 下载文件
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return True
    except Exception as e:
        print(f"下载失败 {url}: {str(e)}")
        return False

def process_page(url):
    """处理单个页面"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 获取级别
        grade = get_grade_from_url(url)
        if not grade:
            print(f"无法识别级别: {url}")
            return
            
        base_dir = os.path.join('英検', grade)
        os.makedirs(base_dir, exist_ok=True)
        
        # 查找所有PDF和MP3链接
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if not href:
                continue
                
            full_url = urljoin(url, href)
            
            # 处理PDF文件
            if href.endswith('.pdf'):
                filename = os.path.basename(href)
                save_path = os.path.join(base_dir, filename)
                print(f"下载PDF: {filename}")
                download_file(full_url, save_path, 'pdf')
                
            # 处理MP3文件
            elif 'audio' in href or href.endswith('.mp3'):
                filename = os.path.basename(href)
                if not filename.endswith('.mp3'):
                    filename += '.mp3'
                save_path = os.path.join(base_dir, 'audio', filename)
                print(f"下载MP3: {filename}")
                download_file(full_url, save_path, 'mp3')
                
            time.sleep(0.5)  # 添加延迟避免请求过快
            
    except Exception as e:
        print(f"处理页面失败 {url}: {str(e)}")

def main():
    # 英検各级别的URL列表
    urls = [
        'https://www.eiken.or.jp/eiken/exam/grade_1/',
        'https://www.eiken.or.jp/eiken/exam/grade_p1/',
        'https://www.eiken.or.jp/eiken/exam/grade_2/',
        'https://www.eiken.or.jp/eiken/exam/grade_p2/',
        'https://www.eiken.or.jp/eiken/exam/grade_3/',
        'https://www.eiken.or.jp/eiken/exam/grade_4/',
        'https://www.eiken.or.jp/eiken/exam/grade_5/'
    ]
    
    for url in urls:
        print(f"\n处理级别: {get_grade_from_url(url)}")
        process_page(url)

if __name__ == '__main__':
    main()