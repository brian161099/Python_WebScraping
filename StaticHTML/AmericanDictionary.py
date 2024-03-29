# %%
'''
匯入套件
'''
# 操作 browser 的 API
from selenium.webdriver.chrome.service import Service
from selenium import webdriver

# 處理逾時例外的工具
from selenium.common.exceptions import TimeoutException

# 面對動態網頁，等待某個元素出現的工具，通常與 exptected_conditions 搭配
from selenium.webdriver.support.ui import WebDriverWait

# 搭配 WebDriverWait 使用，對元素狀態的一種期待條件，若條件發生，則等待結束，往下一行執行
from selenium.webdriver.support import expected_conditions as EC

# 期待元素出現要透過什麼方式指定，通常與 EC、WebDriverWait 一起使用
from selenium.webdriver.common.by import By

# 強制等待 (執行期間休息一下)
from time import sleep

from selenium.webdriver.chrome.service import Service
from selenium import webdriver

# 處理逾時例外的工具
from selenium.common.exceptions import TimeoutException

# 面對動態網頁，等待某個元素出現的工具，通常與 exptected_conditions 搭配
from selenium.webdriver.support.ui import WebDriverWait

# 搭配 WebDriverWait 使用，對元素狀態的一種期待條件，若條件發生，則等待結束，往下一行執行
from selenium.webdriver.support import expected_conditions as EC

# 期待元素出現要透過什麼方式指定，通常與 EC、WebDriverWait 一起使用
from selenium.webdriver.common.by import By

# 強制等待 (執行期間休息一下)
from time import sleep

from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup as bs

from selenium.common.exceptions import TimeoutException, NoSuchElementException

def start_chrome():
    # 啟動瀏覽器工具的選項
    my_options = webdriver.ChromeOptions()
    # my_options.add_argument("--headless")                #不開啟實體瀏覽器背景執行
    my_options.add_argument("--start-maximized")         #最大化視窗
    my_options.add_argument("--incognito")               #開啟無痕模式
    my_options.add_argument("--disable-popup-blocking") #禁用彈出攔截
    my_options.add_argument("--disable-notifications")  #取消 chrome 推播通知
    my_options.add_argument("--lang=zh-TW")  #設定為正體中文
    my_options.binary_location = "/Applications/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"


    # 使用 Chrome 的 WebDriver (Mac ARM64 + Chrome for Testing with version 120.0.6099.109)
    my_service = Service(executable_path="/usr/local/bin/chromedriver",)
    driver = webdriver.Chrome(
        options = my_options,
        service = my_service
    )
    return driver

# # %%
# driver = start_chrome()
# driver.get('https://www.oxfordreference.com/display/10.1093/acref/9780195081374.001.0001/acref-9780195081374')

# # 取得檢視原始碼的內容 (page_source 取得的 html，是動態的、使用者操作過後的結果)
# html = driver.page_source

# # 印出 html (也可以跟 Beautifulsoup 整合)
# # print(html)

# # 指定 lxml 作為解析器
# soup = bs(html, "lxml")

# # 取得 上方選單 元素
# ul = soup.select_one('#searchContent > div:nth-child(1) > h2 > a')

# # 顯示內文
# print(ul.get_text())

# # 休眠幾秒
# sleep(3)

# # 關閉瀏覽器
# driver.quit()
# %%
# driver = start_chrome()
# try:
#     # 最多等 15 秒
#     driver.implicitly_wait(15)
    
#     # 走訪網址
#     driver.get('https://www.oxfordreference.com/display/10.1093/acref/9780195081374.001.0001/acref-9780195081374')
    
#     # 取得元素
#     for idx in range(1, 21):
#         elements = driver.find_elements(By.CSS_SELECTOR, f'#searchContent > div:nth-child({idx}) > h2 > a')

#         # 迴圈遍歷每一個元素
#         for element in elements:
#             # 印出每一個元素的超連結 ( 透過 .get_attribute('屬性') 來取得屬性的值 )
#             print(element.get_attribute('href'))

# except NoSuchElementException:
#     print("找不到元素!")

# finally:
#     # 關閉瀏覽器
#     driver.quit()
# %%
import pandas as pd

driver = start_chrome()

df_result = pd.DataFrame(columns=['title', 'content'])
df_dict = {}

# 最多等 10 秒
driver.implicitly_wait(10)
count = 11
driver.get(f'https://www.oxfordreference.com/display/10.1093/acref/9780195081374.001.0001/acref-9780195081374')
# 走訪網址
for idx in range(1, 70317):
    driver.get(f'https://www.oxfordreference.com/display/10.1093/acref/9780195081374.001.0001/acref-9780195081374-e-{idx}')
    element = driver.find_element(By.CSS_SELECTOR, "#pagetitle > span.oxencycl-headword")
    title = element.get_attribute('innerText')

    content = ""
    for i in range(3):
        try:
            attempt_count  = count + i
            element = driver.find_element(By.CSS_SELECTOR, f"#acref-9780195081374-div1-{attempt_count}")
            found_content = element.get_attribute('innerText')
            if found_content != "":
                content += found_content
                last_success_count = attempt_count
        except NoSuchElementException:
            continue
    count = last_success_count + 1
    df_dict[title]=content

    # current progress
    print(f"current progress: {idx}/70316")

    # temp-save
    if idx % 1000 == 0:
        df_temp_result = pd.DataFrame(list(df_dict.items()), columns=['title', 'content'])
        df_temp_result.to_csv(f'temp_dictionary_1_to_{idx}.csv', index=False)

    # 關閉瀏覽器
driver.quit()
df_result = pd.DataFrame(list(df_dict.items()), columns=['title', 'content'])
df_result.to_csv(f'final_dictionary.csv', index=False)

# %%
