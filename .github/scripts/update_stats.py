# -*- coding: utf-8 -*-
"""
@Project : zz-zik
@FileName: scriptsupdate_stats.py
@Time    : 2025/6/11 下午9:26
@Author  : ZhouFei
@Email   : zhoufei21@s.nuit.edu.cn
@Desc    :
@Usage   :
"""
import os
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time


def get_csdn_stats(url):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument('--disable-notifications')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    chrome_options.page_load_strategy = 'eager'  # 使用急切加载策略

    max_retries = 5  # 增加重试次数
    for attempt in range(max_retries):
        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(60)  # 增加超时时间

            print(f"Attempt {attempt + 1}: Accessing {url}")

            # 先访问一个简单的页面
            driver.get("https://www.csdn.net")
            time.sleep(5)

            # 然后再访问目标页面
            driver.get(url)

            # 使用显式等待替代 sleep
            wait = WebDriverWait(driver, 30)

            stats = {}
            selectors = {
                'views': "//div[contains(@class, 'user-profile-statistics-num')]",
                'posts': "//div[contains(@class, 'user-profile-statistics-num')][following-sibling::div[contains(text(), '原创')]]",
                'followers': "//div[contains(@class, 'user-profile-statistics-num')][following-sibling::div[contains(text(), '粉丝')]]"
            }

            # 等待任意一个元素出现
            first_element = wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'user-profile-statistics-num')]"))
            )

            # 确保页面完全加载
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, 0);")

            for key, selector in selectors.items():
                try:
                    element = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                    # 尝试多种方法获取文本
                    text = element.text
                    if not text:
                        text = driver.execute_script("return arguments[0].textContent;", element)
                    if not text:
                        text = element.get_attribute('textContent')

                    print(f"Raw {key} text: '{text}'")  # 调试信息

                    # 清理并转换文本
                    cleaned_text = ''.join(filter(str.isdigit, text))
                    stats[key] = int(cleaned_text) if cleaned_text else 0
                    print(f"Processed {key}: {stats[key]}")  # 调试信息

                except Exception as e:
                    print(f"Error retrieving {key}: {e}")
                    stats[key] = 0

            # 如果至少有一个非零值，认为是成功的
            if any(stats.values()):
                print("Successfully retrieved stats:", stats)
                return stats

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(10)  # 增加重试间隔
                continue
        finally:
            try:
                if 'driver' in locals():
                    driver.quit()
            except Exception as e:
                print(f"Error closing driver: {e}")

    print("All attempts failed, returning zeros")
    return {'views': 0, 'posts': 0, 'followers': 0}


def update_readme(stats):
    with open('README.md', 'r', encoding='utf-8') as file:
        content = file.read()

    # 定义替换模式和对应的完整URL格式
    replacements = {
        'views': (
            r'badge/My%20Blog%20Views-\d+-blue\?style=social',
            f'badge/My%20Blog%20Views-{stats["views"]}-blue?style=social'
        ),
        'posts': (
            r'badge/Posts-\d+-green\?style=social',
            f'badge/Posts-{stats["posts"]}-green?style=social'
        ),
        'followers': (
            r'badge/Followers-\d+-orange\?style=social',
            f'badge/Followers-{stats["followers"]}-orange?style=social'
        )
    }

    # 执行替换
    for key, (pattern, replacement) in replacements.items():
        content = re.sub(pattern, replacement, content)

    with open('README.md', 'w', encoding='utf-8') as file:
        file.write(content)


if __name__ == "__main__":
    url = 'https://blog.csdn.net/weixin_62828995?spm=1011.2415.3001.10640'
    stats = get_csdn_stats(url)
    print(f"访问量: {stats['views']}")
    print(f"文章数: {stats['posts']}")
    print(f"粉丝数: {stats['followers']}")
    update_readme(stats)