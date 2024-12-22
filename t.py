# https://www.kyoiku.metro.tokyo.lg.jp/admission/high_school/ability_test/problem_and_answer/release20230221_09.html
# https://www.kyoiku.metro.tokyo.lg.jp/admission/high_school/ability_test/problem_and_answer/release20220221_05.html
# https://www.kyoiku.metro.tokyo.lg.jp/admission/high_school/ability_test/problem_and_answer/release20210221_01.html
# https://www.kyoiku.metro.tokyo.lg.jp/admission/high_school/ability_test/problem_and_answer/release20200221_01.html
# https://www.kyoiku.metro.tokyo.lg.jp/admission/high_school/ability_test/problem_and_answer/release20190222_01.html
import os
import requests
from bs4 import BeautifulSoup
import re

def create_directory(path):
    """创建目录"""
    if not os.path.exists(path):
        os.makedirs(path)

def download_file(url, local_path):
    """下载文件"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"Successfully downloaded: {local_path}")
        return True
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")
        return False

def process_url(base_url, target_url):
    """处理单个URL的下载"""
    # 获取网页内容
    response = requests.get(target_url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 从title获取年度信息
    title = soup.find('title').text if soup.find('title') else ''
    if not title:
        title = soup.find('h1').text if soup.find('h1') else '未知年度'
    year_str = title[:5]  # 取前5个字符作为年度
    
    # 创建基础目录
    base_dir = os.path.join("都立高等学校入学者選抜学力検査問題", year_str)
    create_directory(base_dir)
    
    print(f"\n处理年度: {year_str}")
    print(f"URL: {target_url}")
    
    # 查找所有h2标题和对应的ul列表
    h2_tags = soup.find_all('h2')
    
    for h2 in h2_tags:
        # 获取科目名称
        subject = h2.text
        # 跳过"お問い合わせ"等非科目标题
        if subject in ["お問い合わせ"]:
            continue
            
        # 为每个科目创建子目录
        subject_dir = os.path.join(base_dir, subject)
        create_directory(subject_dir)
        
        # 获取该h2标题后面的ul元素
        ul = h2.find_next('ul')
        if ul:
            # 查找ul中的所有PDF链接
            pdf_links = ul.find_all('a', href=re.compile(r'\.pdf$'))
            
            # 下载该科目的所有PDF文件
            for link in pdf_links:
                # 获取PDF URL
                pdf_url = base_url + link.get('href')
                
                # 获取文件名
                filename = os.path.basename(link.get('href'))
                
                # 构建保存路径
                save_path = os.path.join(subject_dir, filename)
                
                # 下载文件
                print(f"Downloading {year_str}/{subject}/{filename}...")
                download_file(pdf_url, save_path)

def main():
    # 基础URL
    base_url = "https://www.kyoiku.metro.tokyo.lg.jp"
    
    # 所有要处理的URL
    urls = [
        "/admission/high_school/ability_test/problem_and_answer/release20240221_09.html",  # 令和6年度
        "/admission/high_school/ability_test/problem_and_answer/release20230221_09.html",  # 令和5年度
        "/admission/high_school/ability_test/problem_and_answer/release20220221_05.html",  # 令和4年度
        "/admission/high_school/ability_test/problem_and_answer/release20210221_01.html",  # 令和3年度
        "/admission/high_school/ability_test/problem_and_answer/release20200221_01.html",  # 令和2年度
        "/admission/high_school/ability_test/problem_and_answer/release20190222_01.html",  # 平成31年度
    ]
    
    # 处理每个URL
    for url in urls:
        target_url = base_url + url
        try:
            process_url(base_url, target_url)
        except Exception as e:
            print(f"Error processing {target_url}: {str(e)}")
            continue

if __name__ == "__main__":
    main()

