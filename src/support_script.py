import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "https://www.fin88.app/"
GAME_PATTERN = "ATG-egyptian-mythology"              # 賽特一
# GAME_PATTERN = "feb91c659e820a0405aabc1520c24d12"    # 賽特二

options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 30)


def go_home():
    print("🏠 回到首頁...")
    driver.get(BASE_URL)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    time.sleep(2)


def enter_game():
    """用背景圖片找遊戲卡片並點擊進入"""
    print(f"🎮 尋找遊戲: {GAME_PATTERN}")
    selector = f"//div[contains(@class, 'game-img') and contains(@style, '{GAME_PATTERN}')]"
    
    try:
        game = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, selector))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", game)
        time.sleep(0.3)
        driver.execute_script("arguments[0].click();", game)
        print("✅ 已點擊遊戲")
    except:
        print("⚠️ 找不到遊戲，請手動點擊後按 Enter")
        input()

    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe.iframe-item")))
    print("✅ 遊戲載入完成")


# ================= 主流程 =================

go_home()

print("👉 請手動登入後按 Enter")
input()

time.sleep(3)
enter_game()

# 🔁 重啟循環
while True:
    cmd = input("\n輸入 r 重新進入遊戲，q 離開：").strip().lower()

    if cmd == "q":
        break
    if cmd == "r":
        go_home()
        time.sleep(3)
        enter_game()

print("👋 結束程式")
driver.quit()
