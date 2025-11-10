import base64
from io import BytesIO
import cv2
import pytesseract
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, os, pyautogui, threading, platform
from PIL import Image
import numpy as np


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
    game_xpath = "/html/body/div[2]/div[3]/div/section/div/main/div[3]/div[2]/div/div/div[2]/div[2]/div/div[2]/div/img"
    start_xpath = "/html/body/div[2]/div[3]/div/section/div/main/div[3]/div[2]/div/div/div[2]/div[2]/div[3]/div[3]"

    time.sleep(1)

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

    # 調整視窗大小
    time.sleep(1)
    driver.set_window_size(600, 400)
    
    time.sleep(30)
    
    input("請確認遊戲已經載入完成按 Enter 繼續...")


# === ✅ Canvas 點擊遊戲 ===
def click_canvas(driver):
    """在 Canvas 上點擊開始遊戲與確定按鈕，並以 CDP clip 擷取點擊區域"""
    try:
        # === 切入 iframe ===
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "gameFrame-0"))
        )
        driver.switch_to.frame(iframe)

        # === 取得 Canvas 區域 ===
        rect = driver.execute_script("""
            const canvas = document.getElementById('GameCanvas');
            const r = canvas.getBoundingClientRect();
            return {x: r.left, y: r.top, w: r.width, h: r.height};
        """)

        global last_canvas_rect
        last_canvas_rect = rect

        # === 計算點擊座標 ===
        win_x = rect["x"] + rect["w"] * 0.5
        win_y = rect["y"] + rect["h"] * 1.3
        confirm_x = rect["x"] + rect["w"] * 0.74
        confirm_y = rect["y"] + rect["h"] * 1.24

        # === 點擊「開始遊戲」 ===
        for ev in ["mousePressed", "mouseReleased"]:
            driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
                "type": ev,
                "x": win_x,
                "y": win_y,
                "button": "left",
                "clickCount": 1
            })
        print(f"✅ 已在開始遊戲點擊 ({win_x:.1f}, {win_y:.1f})")

        # === 等待確認後點擊「確定」 ===
        time.sleep(3)
        for ev in ["mousePressed", "mouseReleased"]:
            driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
                "type": ev,
                "x": confirm_x,
                "y": confirm_y,
                "button": "left",
                "clickCount": 1
            })
        print(f"✅ 已在確定按鈕區點擊 ({confirm_x:.1f}, {confirm_y:.1f})")
        input("請確認遊戲已經開始按 Enter 繼續...")

    except Exception as e:
        print("❌ 無法切入或操作 iframe：", e)

# === ✅ 自動購買免費遊戲模組（OpenCV 版） ===
def buyfreeGame(driver):
    """
    在 Canvas 上點擊兩個指定位置（freegame 區域與中心點），
    並使用 OpenCV 在「瀏覽器畫面」中截取該位置區域。
    """
    try:
        global last_canvas_rect
        rect = last_canvas_rect  # click_canvas 儲存的 Canvas 範圍

        # === 第一次點擊（freegame 區域） ===
        freegame_x = rect["x"] + rect["w"] * 0.29
        freegame_y = rect["y"] + rect["h"] * 1.14

        for ev in ["mousePressed", "mouseReleased"]:
            driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
                "type": ev,
                "x": freegame_x,
                "y": freegame_y,
                "button": "left",
                "clickCount": 1
            })
        print(f"🟢 已在 Canvas 點擊 FreeGame 位置 ({freegame_x:.1f}, {freegame_y:.1f})")
        time.sleep(2)
        # === 第二次點擊（Canvas ） ===
        start_x = rect["x"] + rect["w"] * 0.6
        start_y = rect["y"] + rect["h"] * 1.25

        for ev in ["mousePressed", "mouseReleased"]:
            driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
                "type": ev,
                "x": start_x,
                "y": start_y,
                "button": "left",
                "clickCount": 1
            })
        print(f"🟢 已在 Canvas 開始點擊 ({start_x:.1f}, {start_y:.1f})")

            # === 延遲 1 秒後開始空白鍵回圈 ===
        time.sleep(1)
        print("🔁 開始自動按空白鍵迴圈（每15秒一次，共20次）")

        for i in range(20):
            # 模擬空白鍵按下與放開
            driver.execute_cdp_cmd("Input.dispatchKeyEvent", {
                "type": "keyDown",
                "key": " ",
                "code": "Space",
                "windowsVirtualKeyCode": 32,
                "nativeVirtualKeyCode": 32
            })
            driver.execute_cdp_cmd("Input.dispatchKeyEvent", {
                "type": "keyUp",
                "key": " ",
                "code": "Space",
                "windowsVirtualKeyCode": 32,
                "nativeVirtualKeyCode": 32
            })
            print(f"✅ 第 {i+1}/20 次空白鍵已按下")
            if i < 19:
                time.sleep(15)  # 每15秒按一次

        print("🏁 空白鍵迴圈已完成！")

    except Exception as e:
        print("❌ buyfreeGame 執行錯誤：", e)

    except Exception as e:
        print("❌ buyfreeGame 執行錯誤：", e)

    finally:
        try:
            driver.switch_to.default_content()
        except Exception:
            pass

# === ✅ 自動空白鍵模組 ===
running = False
stop_program = False

def press_space(driver):
    """在瀏覽器內模擬空白鍵，按下與放開的背景執行緒"""
    global running, stop_program
    while not stop_program:
        if running:
            try:
                for t in ["keyDown", "keyUp"]:
                    driver.execute_cdp_cmd("Input.dispatchKeyEvent", {
                        "type": t, "key": " ", "code": "Space",
                        "windowsVirtualKeyCode": 32, "nativeVirtualKeyCode": 32
                    })
                time.sleep(15)
            except Exception as e:
                print("⚠️ 模擬空白鍵失敗：", e)
                time.sleep(1)
        else:
            time.sleep(0.1)

def keyboard_control(driver):
    """終端互動控制：選單僅 c / p / q；按 p 時才詢問是否執行 b。
       做用全域變數 running 控制空白鍵模組啟停。
       在 p 分支中呼叫 run_buyfree_safe() 執行 buyfreeGame。"""
    global running, stop_program

    print("\n🟢 程式啟動成功！")
    print("指令：")
    print("  c = Continue（開始/恢復自動按空白鍵）")
    print("  p = Pause / 狀態（並可選擇是否執行買免費遊戲 b）")
    print("  q = Quit（結束）")
    print("────────────────────────────")

    # 背景執行緒（空白鍵）
    t = threading.Thread(target=press_space, args=(driver,), daemon=True)
    t.start()

    while True:
        try:
            cmd = input("👉 請輸入指令 (c/p/q)：").strip().lower()

            if cmd == "c":
                if not running:
                    running = True
                    print("▶️ 已開始自動按空白鍵。")
                else:
                    print("⚠️ 目前已在自動按空白鍵中。")

            elif cmd == "p":
                # 顯示狀態
                if running:
                    print("⏸️ 目前狀態：自動按空白鍵中（將暫停）")
                else:
                    print("⏸️ 目前狀態：暫停中")

                # 先暫停
                was_running = running
                running = False

                # 在「p」情境下才問是否執行 b
                choice = input("是否執行買免費遊戲？按 'b' 執行，直接 Enter 跳過：").strip().lower()
                if choice == "b":
                    run_buyfree_safe(driver)
                else:
                    print("↩️ 已略過 buyfreeGame。")

                # 若原本在跑，自動恢復
                if was_running:
                    running = True
                    print("▶️ 已恢復自動按空白鍵。")

            elif cmd == "q":
                print("🛑 程式即將結束...")
                running = False
                stop_program = True
                try:
                    driver.quit()  # quit 會關閉所有視窗；無需再 close()
                except Exception:
                    pass
                break

            else:
                print("❓ 無效指令，請輸入 c / p / q。")

        except EOFError:
            print("⚠️ 無法從終端讀取指令，強制結束。")
            stop_program = True
            break
        except Exception as e:
            print("⚠️ 錯誤：", e)
            stop_program = True
            break

    print("✅ 主程式已安全退出。")


def run_buyfree_safe(driver):
    """只在 keyboard_control 的 p 分支中被呼叫；會暫停空白鍵、檢查狀態、執行後自動恢復。"""
    global running, last_canvas_rect

    if 'last_canvas_rect' not in globals() or last_canvas_rect is None:
        print("⚠️ 尚未完成 Canvas 初始化，請先執行 click_canvas()。")
        return

    prev = running
    running = False  # 暫停空白鍵避免衝突
    print("🛒 執行 buyfreeGame 中...")
    try:
        buyfreeGame(driver)
        print("✅ buyfreeGame 完成。")
    except Exception as e:
        print("❌ buyfreeGame 發生錯誤：", e)
    finally:
        running = prev
        print("🔄 已恢復先前狀態。")

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
