import cv2
import pytesseract
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, os, pyautogui, threading, platform


# === ✅ 初始化 Chrome Driver ===
def init_driver():
    """初始化 WebDriver 並返回 driver"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    driver_name = "chromedriver.exe" if platform.system() == "Windows" else "chromedriver"
    driver_path = os.path.join(base_dir, "..", driver_name)

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--window-size=500,600")
    chrome_options.add_argument("--window-position=100,100")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(driver_path), options=chrome_options)
    return driver


# === ✅ 登入流程 ===
def login(driver, account, password):
    """自動登入帳號"""
    driver.get("https://m.jfw-win.com/#/login?redirect=%2Fhome%2Fpage")
    time.sleep(5)

    account_xpath = "/html/body/div[2]/main/div/div[2]/div/div[3]/div[1]/div/div/div/div/input"
    password_xpath = "/html/body/div[2]/main/div/div[2]/div/div[3]/div[2]/div/div/div/div/input"
    login_button_xpath = "/html/body/div[2]/main/div/div[2]/div/div[3]/div[4]/div[1]"
    agree_button_xpath = "/html/body/div[2]/main/div/div[2]/div/div[3]/div[6]/div/div[3]/div[2]/div[1]"

    driver.find_element(By.XPATH, account_xpath).send_keys(account)
    driver.find_element(By.XPATH, password_xpath).send_keys(password)
    time.sleep(2)
    driver.find_element(By.XPATH, login_button_xpath).click()
    time.sleep(3)
    driver.find_element(By.XPATH, agree_button_xpath).click()
    time.sleep(10)


# === ✅ 處理公告遮罩 ===
def close_overlay(driver):
    """嘗試關閉公告彈窗或遮罩"""
    try:
        WebDriverWait(driver, 5).until(
            lambda d: d.execute_script("""
                return document.querySelector('div.box, div.close, div.activewrapper') !== null;
            """)
        )
        driver.execute_script("""
            const closeBtn = document.querySelector('div.close');
            if (closeBtn) closeBtn.click();
        """)
        time.sleep(2)
        driver.execute_script("""
            document.querySelectorAll('div.box, div.close, div.activewrapper').forEach(el => el.remove());
        """)
        time.sleep(1)
    except Exception:
        pass


# === ✅ 進入遊戲主頁 ===
def enter_game(driver):
    """點擊進入遊戲"""
    atg_xpath = "/html/body/div[2]/div[3]/div/section/div/main/div[3]/div[1]/div/div[1]/div/div[8]"
    game_xpath = "/html/body/div[2]/div[3]/div/section/div/main/div[3]/div[2]/div/div/div[1]/div[2]/div/div[2]/div"
    start_xpath = "/html/body/div[2]/div[3]/div/section/div/main/div[3]/div[2]/div/div/div[1]/div[2]/div[3]/div[3]"

    input("請確認視窗已經打開並且登入完畢後按 Enter 繼續...")

    for xpath, name in [(atg_xpath, "ATG"), (game_xpath, "Game")]:
        driver.execute_script("""
            const el = document.evaluate(arguments[0], document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
            if (el) {
                el.scrollIntoView({block: 'center'});
                el.click();
                console.log("✅ JS 已點擊元素：" + arguments[1]);
            }
        """, xpath, name)
        time.sleep(1)

    driver.find_element(By.XPATH, start_xpath).click()
    time.sleep(30)
    input("請確認遊戲已經載入完成後按 Enter 繼續...")


# === ✅ Canvas 點擊遊戲 ===
def click_canvas(driver):
    """進入 iframe 並在 Canvas 上點擊開始遊戲與確定按鈕"""
    try:
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "gameFrame-0"))
        )
        driver.switch_to.frame(iframe)

        rect = driver.execute_script("""
            const canvas = document.getElementById('GameCanvas');
            const r = canvas.getBoundingClientRect();
            return {x: r.left, y: r.top, w: r.width, h: r.height};
        """)

        win_x, win_y = rect["x"] + rect["w"] * 0.5, rect["y"] + rect["h"] * 0.93
        confirm_x, confirm_y = rect["x"] + rect["w"] * 0.748, rect["y"] + rect["h"] * 0.92

        for ev in ["mousePressed", "mouseReleased"]:
            driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
                "type": ev, "x": win_x, "y": win_y, "button": "left", "clickCount": 1
            })
        print(f"✅ 已在開始遊戲點擊 ({win_x:.1f}, {win_y:.1f})")

        time.sleep(3)

        for ev in ["mousePressed", "mouseReleased"]:
            driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
                "type": ev, "x": confirm_x, "y": confirm_y, "button": "left", "clickCount": 1
            })
        print(f"✅ 已在確定按鈕區點擊 ({confirm_x:.1f}, {confirm_y:.1f})")

    except Exception as e:
        print("❌ 無法切入或操作 iframe：", e)


# === ✅ 自動空白鍵模組 ===
running = False
stop_program = False

def press_space(driver):
    """在瀏覽器內模擬空白鍵"""
    global running, stop_program
    while not stop_program:
        if running:
            try:
                for t in ["keyDown", "keyUp"]:
                    driver.execute_cdp_cmd("Input.dispatchKeyEvent", {
                        "type": t, "key": " ", "code": "Space",
                        "windowsVirtualKeyCode": 32, "nativeVirtualKeyCode": 32
                    })
                time.sleep(0.5)
            except Exception as e:
                print("⚠️ 模擬空白鍵失敗：", e)
                time.sleep(1)
        else:
            time.sleep(0.1)

def keyboard_control(driver):
    """改進版：終端控制空白鍵模組"""
    global running, stop_program
    print("\n🟢 程式啟動成功！")
    print("輸入指令控制：")
    print("  c = Continue（開始）")
    print("  p = Pause（暫停）")
    print("  q = Quit（結束）")
    print("────────────────────────────")

    # 啟動背景執行緒
    t = threading.Thread(target=press_space, args=(driver,), daemon=True)
    t.start()

    while True:
        try:
            cmd = input("👉 請輸入指令 (c/p/q)：").strip().lower()
            if cmd == "c":
                if not running:
                    running = True
                    print("▶️ 開始自動按空白鍵（僅瀏覽器內）...")
                else:
                    print("⚠️ 已在運作中。")
            elif cmd == "p":
                if running:
                    running = False
                    print("⏸️ 已暫停。")
                else:
                    print("⚠️ 目前已是暫停狀態。")
            elif cmd == "q":
                print("🛑 程式即將結束...")
                running = False
                stop_program = True
                driver.quit()
                time.sleep(0.1)
                driver.close()
                break
            else:
                print("❓ 無效指令，請重新輸入 c / p / q。")

        except EOFError:
            # 終端被關閉或 stdin 無法讀取
            print("⚠️ 無法從終端讀取指令，強制結束。")
            stop_program = True
            break
        except Exception as e:
            print("⚠️ 錯誤：", e)
            stop_program = True
            break

    print("✅ 主程式已安全退出。")

# === ✅ 主流程 ===
def main():
    driver = init_driver()
    login(driver, "g73ac9e", "aaaa1111")
    close_overlay(driver)
    enter_game(driver)
    click_canvas(driver)
    keyboard_control(driver)


if __name__ == "__main__":
    main()
