import cv2
import pytesseract
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
import time
import os, pyautogui
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


# 初始化瀏覽器，指定 chromedriver 路徑並設置視窗大小 800x600
chrome_service = Service("/Users/ayuan/Desktop/helpblack/chromedriver")
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--window-size=400,600")
chrome_options.add_argument("--window-position=100,100")
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

driver.get("https://cyf888.com/#/login")
time.sleep(5)  # 等待頁面載入

account = "qq0303"
password = "qq112233"
captcha = input("請輸入驗證碼：")

account_xpath = "/html/body/div/div/div[3]/div[2]/form/div[1]/label/div[1]/input"
driver.find_element(By.XPATH, account_xpath).send_keys(account)

password_xpath = "/html/body/div/div/div[3]/div[2]/form/div[2]/label/div[1]/input"
driver.find_element(By.XPATH, password_xpath).send_keys(password)

captcha_xpath = "/html/body/div/div/div[3]/div[2]/form/div[3]/label/div/div[1]/input"
driver.find_element(By.XPATH, captcha_xpath).send_keys(captcha)

login_button_xpath = "/html/body/div/div/div[3]/div[2]/form/button"
driver.find_element(By.XPATH, login_button_xpath).click()

# 用 WebDriverWait 最多等 10 秒，若有公告遮罩才執行隱藏
try:
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script("return document.querySelectorAll('div.fixed.top-0.left-0.w-full.h-full.flex').length > 0;")
    )
    driver.execute_script("""
      document.querySelectorAll('div.fixed.top-0.left-0.w-full.h-full.flex')
        .forEach(n => {
          if ((n.className||'').includes('z-[90]')) {
            n.style.setProperty('display','none','important');
            n.style.pointerEvents = 'none';
          }
        });
    """)
    time.sleep(1)
except Exception:
    pass

notice_xpath = "/html/body/div/div/div[3]/div[1]/div[1]/div/button[1]"
driver.find_element(By.XPATH, notice_xpath).click()
time.sleep(1)  # 等待公告視窗關閉動畫

# 進入遊戲大廳
game1_elem = driver.find_elements(By.CSS_SELECTOR, 'a.relative.row-span-2.col-span-1')
if len(game1_elem) >= 4:
    driver.execute_script("arguments[0].click();", game1_elem[3])  # 索引3是第4個
else:
    print("找不到遊戲廠商")
    driver.quit()
time.sleep(10)  # 等待遊戲頁面載入

# 等待第二頁大容器出現（你要換成實際的 XPath）
driver.switch_to.window(driver.window_handles[-1])

try:
    atg_xpath = "/html/body/div/div/div[3]/div[2]/div/div[1]/div[2]/button"
    driver.find_element(By.XPATH, atg_xpath).click()
    time.sleep(20)  # 等待新分頁載入

except Exception as e:
    print("找不到遊戲內容")

# === 找到 canvas ===
canvas = driver.find_element(By.ID, "GameCanvas")

# 你自己量到的螢幕絕對座標
TARGET1_X, TARGET1_Y = 346, 588   # ← 換成你實測的值
time.sleep(2)  # 給你 2 秒把視窗切到遊戲
pyautogui.click(TARGET1_X, TARGET1_Y)

TARGET2_X, TARGET2_Y = 495, 569   # ← 換成你實測的值
time.sleep(2)  # 給你 2 秒把視窗切到遊戲
pyautogui.click(TARGET2_X, TARGET2_Y)

TARGET3_X, TARGET3_Y = 562, 561   # ← 換成你實測的值

time.sleep(2)  # 給你 2 秒把視窗切到遊戲

# 持續按住空白鍵，每 100 秒釋放再重新按住
while True:
    pyautogui.keyDown('space')
    time.sleep(0.5)
    pyautogui.keyUp('space')
    time.sleep(0.5)  # 可微調，避免太快重複

input("請操作完畢後按 Enter 結束...")
driver.quit()

# =============================================================

# count = 0
# while True:
#     # 找到 canvas 元素並截圖
#     canvas = driver.find_element(By.ID, "GameCanvas")
#     canvas.screenshot("canvas.png")

#     # ===== OpenCV 前處理 =====
#     img = cv2.imread("canvas.png")

#     # 假設金額區域在固定位置 (依你的實際畫面修改)
#     x, y, w, h = 400, 500, 200, 50
#     roi = img[y:y+h, x:x+w]

#     # 存檔 (每次截圖一張)
#     roi_filename = f"cash_snapshots/cash_{count}.png"
#     cv2.imwrite(roi_filename, roi)
#     print(f"已存金額截圖：{roi_filename}")

#     # 灰階 + 二值化
#     gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
#     _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

#     # ===== OCR 辨識 =====
#     text = pytesseract.image_to_string(thresh, config="--psm 7 digits")
#     try:
#         cash = int("".join(filter(str.isdigit, text)))
#     except ValueError:
#         cash = 0

#     print(f"辨識到現金：{cash}")

#     # ===== 條件判斷 =====
#     if 100 < cash < 10000:
#         canvas.send_keys(Keys.SPACE)
#         print("動作：空白鍵轉一次")

#     elif cash >= 10000:
#         print("動作：提領")
#         # driver.find_element(By.ID, "withdrawButton").click()

#     elif cash <= 100:
#         can_refill = True  # 依你的邏輯決定
#         if can_refill:
#             print("動作：補錢")
#             # driver.find_element(By.ID, "refillButton").click()
#         else:
#             print("⚠️ 提示用戶：現金不足且無法補錢")

#     # 間隔 3 秒再檢查一次
#     time.sleep(3)
#     count += 1
