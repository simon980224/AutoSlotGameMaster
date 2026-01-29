import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "https://www.fin88.app/"   # 如果你真的是 fin888.com 就改這裡
GAME_CODE = "egyptian-mythology"      # 你的目標遊戲代碼

options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 30)


def go_home():
    print("🏠 回到首頁...")
    driver.get(BASE_URL)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    time.sleep(3)


def wait_for_lobby_loaded():
    print("⏳ 等待大廳載入完成...")
    time.sleep(5)  # 大廳通常是 SPA，給它點時間


def enter_game():
    print("🎮 自動尋找並點擊遊戲:", GAME_CODE)

    # 嘗試用多種方式找遊戲卡片（不同站 DOM 不同）
    game = wait.until(EC.presence_of_element_located((
        By.XPATH,
        f"//*[contains(@style, '{GAME_CODE}') or contains(text(), '{GAME_CODE}') or contains(@src, '{GAME_CODE}')]"
    )))

    driver.execute_script("arguments[0].click();", game)

    print("⏳ 等待遊戲 iframe 出現...")
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe.iframe-item")))
    print("✅ 遊戲已成功進入")


# ================= 主流程 =================

go_home()

print("👉 請手動登入，登入完成後按 Enter")
input()

wait_for_lobby_loaded()
enter_game()

# 🔁 重啟循環
while True:
    cmd = input("\n輸入 restart 重新進入遊戲，或 q 離開：").strip().lower()

    if cmd == "q":
        break

    if cmd == "restart":
        go_home()
        wait_for_lobby_loaded()
        enter_game()

print("👋 結束程式")
driver.quit()
