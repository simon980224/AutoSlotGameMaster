import cv2
import pytesseract
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, os, pyautogui, threading

# === ✅ 自動匹配 ChromeDriver ===
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--window-size=500,600")
chrome_options.add_argument("--window-position=100,100")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# === 開啟登入頁 ===
driver.get("https://m.jfw-win.com/#/login?redirect=%2Fhome%2Fpage")
# input("請確認視窗已經打開並且登入完畢後按 Enter 繼續...")
time.sleep(5)  # 等待頁面載入

account = "xxpp12"
password = "aaaa1111"

# === 登入流程 ===
account_xpath = "/html/body/div[2]/main/div/div[2]/div/div[3]/div[1]/div/div/div/div/input"
driver.find_element(By.XPATH, account_xpath).send_keys(account)

password_xpath = "/html/body/div[2]/main/div/div[2]/div/div[3]/div[2]/div/div/div/div/input"
driver.find_element(By.XPATH, password_xpath).send_keys(password)
time.sleep(2)

login_button_xpath = "/html/body/div[2]/main/div/div[2]/div/div[3]/div[4]/div[1]"
driver.find_element(By.XPATH, login_button_xpath).click()
time.sleep(3)

agree_button_xpath = "/html/body/div[2]/main/div/div[2]/div/div[3]/div[6]/div/div[3]/div[2]/div[1]"
driver.find_element(By.XPATH, agree_button_xpath).click()
time.sleep(10)

# === 處理公告遮罩 ===
try:
    # 等待任何遮罩出現（最多 10 秒）
    WebDriverWait(driver, 5).until(
        lambda d: d.execute_script("""
            return document.querySelector('div.box, div.close, div.activewrapper') !== null;
        """)
    )
    # print("🟡 偵測到公告或遮罩，嘗試處理中...")

    # 嘗試點擊關閉按鈕
    driver.execute_script("""
        const closeBtn = document.querySelector('div.close');
        if (closeBtn) {
            closeBtn.click();
            console.log("✅ 已點擊公告關閉按鈕");
        }
    """)

    # 等待動畫關閉
    time.sleep(2)

    # 再確認是否仍存在，若有就直接移除所有干擾元素
    driver.execute_script("""
        document.querySelectorAll('div.box, div.close, div.activewrapper').forEach(el => {
            el.remove();
        });
        console.log("✅ 已強制移除公告與遮罩");
    """)

    # 再延遲確保畫面刷新
    time.sleep(1)

except Exception as e:
    pass

time.sleep(3)

atg_xpath = "/html/body/div[2]/div[3]/div/section/div/main/div[3]/div[1]/div/div[1]/div/div[8]"
# 用 JavaScript 執行 click()
input("請確認視窗已經打開並且登入完畢後按 Enter 繼續...")
driver.execute_script("""
    const el = document.evaluate(arguments[0], document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
    if (el) {
        el.scrollIntoView({block: 'center'});
        el.click();
        console.log("✅ JS 已點擊 stickyElement 元素");
    } else {
        console.log("⚠️ 找不到 stickyElement 元素");
    }
""", atg_xpath)
time.sleep(1)

game_xpath = "/html/body/div[2]/div[3]/div/section/div/main/div[3]/div[2]/div/div/div[1]/div[2]/div/div[2]/div"
driver.execute_script("""
    const el = document.evaluate(arguments[0], document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
    if (el) {
        el.scrollIntoView({block: 'center'});  // 滾到畫面中央
        el.click();  // 用 JS 直接觸發 click，不受前景元素遮擋影響
        console.log("✅ JS 已成功點擊 game 元素");
    } else {
        console.log("⚠️ 找不到 game 元素");
    }
""", game_xpath)
time.sleep(1)

start_xpath = "/html/body/div[2]/div[3]/div/section/div/main/div[3]/div[2]/div/div/div[1]/div[2]/div[3]/div[3]"
driver.find_element(By.XPATH, start_xpath).click()
time.sleep(30)

# === 在 Canvas 中點擊遊戲畫面 ===
# === 列出所有帶 id 的元素（確認 GameCanvas 是否動態載入）===
try:
    # 直接切入 iframe
    iframe = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "gameFrame-0"))
    )
    driver.switch_to.frame(iframe)

    # 取得 Canvas 實際位置與大小
    rect = driver.execute_script("""
        const canvas = document.getElementById('GameCanvas');
        const r = canvas.getBoundingClientRect();
        return {x: r.left, y: r.top, w: r.width, h: r.height};
    """)
    # === 1️⃣ 點擊贏分區 ===
    win_x = rect["x"] + rect["w"] * 0.5
    win_y = rect["y"] + rect["h"] * 0.93

    for ev in ["mousePressed", "mouseReleased"]:
        driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
            "type": ev,
            "x": win_x,
            "y": win_y,
            "button": "left",
            "clickCount": 1
        })
    print(f"✅ 已在贏分區點擊 ({win_x:.1f}, {win_y:.1f})")

    # 暫停 1 秒等待動畫或彈窗出現
    time.sleep(3)
    # === 2️⃣ 點擊確定按鈕區 ===
    confirm_x = rect["x"] + rect["w"] * 0.748
    confirm_y = rect["y"] + rect["h"] * 0.92

    for ev in ["mousePressed", "mouseReleased"]:
        driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
            "type": ev,
            "x": confirm_x,
            "y": confirm_y,
            "button": "left",
            "clickCount": 1
        })
    print(f"✅ 已在確定按鈕區點擊 ({confirm_x:.1f}, {confirm_y:.1f})")

except Exception as e:
    print("❌ 無法切入或操作 iframe：", e)

time.sleep(1)

# === 自動按空白鍵 ===
running = False  # 控制是否執行
stop_program = False  # 結束程式用

def press_space():
    """持續自動按空白鍵的執行緒"""
    global running, stop_program
    while not stop_program:
        if running:
            pyautogui.press('space')
            time.sleep(0.5)
        else:
            time.sleep(0.1)

def main():
    global running, stop_program
    print("🟢 程式啟動成功！")
    print("輸入指令控制：")
    print("  c = Continue（開始）")
    print("  p = Pause（暫停）")
    print("  q = Quit（結束）")
    print("────────────────────────────")

    # 啟動自動按鍵的背景執行緒
    t = threading.Thread(target=press_space)
    t.daemon = True
    t.start()

    # 主迴圈：等待使用者輸入
    try:
        while True:
            cmd = input("👉 請輸入指令 (c/p/q)：").strip().lower()
            if cmd == 'c':
                if not running:
                    running = True
                    print("▶️ 開始自動按空白鍵...")
                else:
                    print("⚠️ 已在運作中。")
            elif cmd == 'p':
                if running:
                    running = False
                    print("⏸️ 已暫停。")
                else:
                    print("⚠️ 目前已經是暫停狀態。")
            elif cmd == 'q':
                stop_program = True
                running = False
                print("🛑 程式即將結束...")
                break
            else:
                print("❓ 無效指令，請輸入 c/p/q。")
    except KeyboardInterrupt:
        stop_program = True
        print("\n⚠️ 使用者中斷程式。")

if __name__ == "__main__":
    main()
