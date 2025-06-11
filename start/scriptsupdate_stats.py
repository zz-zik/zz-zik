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

    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        time.sleep(5)

        stats = {}
        selectors = {
            'views': "//span[contains(@class, 'user-profile-statistics-views')]//div[contains(@class, 'user-profile-statistics-num')]",
            'posts': "//div[contains(@class, 'user-profile-statistics-num')][following-sibling::div[contains(text(), '原创')]]",
            'followers': "//div[contains(@class, 'user-profile-statistics-num')][following-sibling::div[contains(text(), '粉丝')]]"
        }

        for key, selector in selectors.items():
            try:
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                stats[key] = int(element.text.replace(',', ''))
            except Exception:
                stats[key] = 0

        return stats

    finally:
        if 'driver' in locals():
            driver.quit()


def update_readme(stats):
    with open('README.md', 'r', encoding='utf-8') as file:
        content = file.read()

    content = re.sub(r'<!--CSDN_VIEWS-->', str(stats['views']), content)
    content = re.sub(r'<!--CSDN_POSTS-->', str(stats['posts']), content)
    content = re.sub(r'<!--CSDN_FOLLOWERS-->', str(stats['followers']), content)

    with open('README.md', 'w', encoding='utf-8') as file:
        file.write(content)


if __name__ == "__main__":
    url = 'https://blog.csdn.net/weixin_62828995?spm=1011.2415.3001.10640'  # 替换为你的CSDN主页URL
    stats = get_csdn_stats(url)
    update_readme(stats)
