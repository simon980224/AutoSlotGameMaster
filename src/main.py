import cv2
import pytesseract
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, os, pyautogui

# === ✅ 自動匹配 ChromeDriver ===
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--window-size=400,600")
chrome_options.add_argument("--window-position=100,100")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# === 開啟登入頁 ===
driver.get("https://cyf888.com/#/login")
time.sleep(5)  # 等待頁面載入

account = "qq0303"
password = "qq112233"
try:
    captcha_xpath_num = "/html/body/div/div/div[3]/div[3]/form/div[3]/label/div/div[3]/button/i"
    captcha_elem = driver.find_element(By.XPATH, captcha_xpath_num)
    captcha = captcha_elem.text.strip()
    print(f"🔢 抓取到驗證碼：{captcha}")
except Exception as e:
    print("❌ 無法取得驗證碼內容：", e)
    captcha = input("請手動輸入驗證碼：")

# input("請確認視窗已經打開並且登入完畢後按 Enter 繼續...")

# === 登入流程 ===
account_xpath = "/html/body/div/div/div[3]/div[3]/form/div[1]/label/div[1]/input"
driver.find_element(By.XPATH, account_xpath).send_keys(account)

password_xpath = "/html/body/div/div/div[3]/div[3]/form/div[2]/label/div[1]/input"
driver.find_element(By.XPATH, password_xpath).send_keys(password)

captcha_xpath = "/html/body/div/div/div[3]/div[3]/form/div[3]/label/div/div[1]/input"
captcha_elem = driver.find_element(By.XPATH, captcha_xpath)
captcha_elem.send_keys(captcha)

login_button_xpath = "/html/body/div/div/div[3]/div[3]/form/button"
driver.find_element(By.XPATH, login_button_xpath).click()

# === 處理公告遮罩 ===
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

# === 關閉公告視窗 ===
notice_xpath = "/html/body/div/div/div[3]/div[1]/div[1]/div/button[1]"
try:
    driver.find_element(By.XPATH, notice_xpath).click()
    time.sleep(1)
except:
    print("未偵測到公告視窗，略過")

# === 進入遊戲大廳 ===
game1_elem = driver.find_elements(By.CSS_SELECTOR, 'a.relative.row-span-2.col-span-1')
if len(game1_elem) >= 4:
    driver.execute_script("arguments[0].click();", game1_elem[3])
else:
    print("找不到遊戲廠商")
    driver.quit()
time.sleep(10)

# === 切換分頁並點擊進入遊戲 ===
driver.switch_to.window(driver.window_handles[-1])
try:
    atg_xpath = "/html/body/div/div/div[3]/div[2]/div/div[1]/div[2]/button"
    driver.find_element(By.XPATH, atg_xpath).click()
    time.sleep(20)
except Exception as e:
    print("找不到遊戲內容")

# === 找到 Canvas 並點擊 ===
try:
    canvas = driver.find_element(By.ID, "GameCanvas")
except:
    print("未找到 Canvas 元素")

TARGET1_X, TARGET1_Y = 346, 588
time.sleep(2)
pyautogui.click(TARGET1_X, TARGET1_Y)

TARGET2_X, TARGET2_Y = 495, 569
time.sleep(2)
pyautogui.click(TARGET2_X, TARGET2_Y)

TARGET3_X, TARGET3_Y = 562, 561
time.sleep(2)
pyautogui.click(TARGET3_X, TARGET3_Y)

# === 自動按空白鍵 ===
print("🟢 開始自動按空白鍵，每 0.5 秒一次...")
while True:
    pyautogui.keyDown('space')
    time.sleep(0.5)
    pyautogui.keyUp('space')
    time.sleep(0.5)
