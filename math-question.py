# https://www.kumamoto-kmm.ed.jp/sugakubraindumps/

import os
import time
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import requests

def download_pdfs(pdf_list, default_dir):
    """批量下载PDF文件"""
    try:
        # 设置 Chrome 选项
        options = uc.ChromeOptions()
        # 启用无头模式
        options.add_argument('--headless')
        
        # 设置下载路径
        prefs = {
            "download.default_directory": os.path.abspath(default_dir),
            "download.prompt_for_download": False,
            "plugins.always_open_pdf_externally": True  # 直接下载PDF而不是在浏览器中打开
        }
        options.add_experimental_option("prefs", prefs)
        
        # 创建浏览器实例
        driver = uc.Chrome(options=options)
        
        try:
            for pdf_url, save_path in pdf_list: 
                print(f"下载: {os.path.basename(save_path)}")
                
                # 访问PDF链接
                driver.get(pdf_url)
                time.sleep(2)  # 等待下载开始
                
                # 获取临时文件名
                temp_file = os.path.join(os.path.dirname(save_path), os.path.basename(pdf_url))
                
                # 等待下载完成
                max_wait = 30
                while max_wait > 0:
                    if os.path.exists(temp_file):
                        # 如果文件存在，重命名为期望的文件名
                        if os.path.exists(save_path):
                            os.remove(save_path)
                        os.rename(temp_file, save_path)
                        print(f"完成: {os.path.basename(save_path)}")
                        break
                    time.sleep(1)
                    max_wait -= 1
                
                if max_wait <= 0:
                    print(f"下载超时: {os.path.basename(save_path)}")
                
                time.sleep(1)  # 添加短暂延迟
                
        finally:
            driver.quit()
            
    except Exception as e:
        print(f"下载过程出错: {str(e)}")
        return False

def get_new_filename(grade, chapter, original_filename):
    """生成新的文件名"""
    # 替换所有空格（包括全角空格）
    grade = grade.strip().replace(' ', '').replace('　', '')
    chapter = chapter.strip().replace(' ', '').replace('　', '')
    
    # 获取原文件名的最后部分（question或answer）
    last_part = original_filename.split('_')[-1]
    
    # 构建新文件名
    new_filename = f"{grade}_{chapter}_{last_part}"
    return new_filename

def main():
    # 基础URL和保存目录
    base_url = 'https://www.kumamoto-kmm.ed.jp/sugakubraindumps/'
    save_dir = '中学数学問題集'
    os.makedirs(save_dir, exist_ok=True)
    
    # 从本地文件读取HTML
    with open('math.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 收集所有需要下载的PDF信息
    pdf_list = []
    
    # 遍历所有表格
    for table in soup.find_all('table'):
        current_grade = None
        
        # 遍历表格行
        for tr in table.find_all('tr'):
            # 获取年级（在th中）
            th = tr.find('th')
            if th and 'width' in th.attrs and th['width'] == '290px':
                current_grade = th.text.strip()
                continue
            
            # 获取章节名（在td class="tangen"中）
            tangen = tr.find('td', class_='tangen')
            if not tangen:
                continue
            
            chapter = tangen.text.strip()
            
            # 获取PDF链接
            for a in tr.find_all('a', href=re.compile(r'.*\.pdf$')):
                pdf_url = urljoin(base_url, a['href'])
                original_filename = os.path.basename(pdf_url)
                
                # 生成新文件名
                new_filename = get_new_filename(current_grade, chapter, original_filename)
                save_path = os.path.join(save_dir, new_filename)
                
                # 如果文件已存在，跳过
                if os.path.exists(save_path):
                    print(f"文件已存在，跳过: {new_filename}")
                    continue
                
                pdf_list.append((pdf_url, save_path))
    
    # 批量下载PDF
    if pdf_list:
        download_pdfs(pdf_list, save_dir)
    else:
        print("没有需要下载的文件")

if __name__ == '__main__':
    main()