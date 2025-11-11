from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import os
import platform
import threading

# 全域狀態管理：追蹤每個瀏覽器的執行狀態與執行緒
# 格式：{driver: {"running": bool, "thread": Thread or None}}
game_states = {}
game_states_lock = threading.Lock()


def get_chromedriver_path():
    """
    功能：自動取得 ChromeDriver 的完整路徑。

    說明：根據作業系統（Windows / macOS / Linux）回傳相對應的執行檔名稱。

    回傳:
        str: ChromeDriver 的完整路徑
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)

    system = platform.system().lower()
    driver_filename = "chromedriver.exe" if system == "windows" else "chromedriver"

    return os.path.join(project_root, driver_filename)


def load_user_credentials():
    """
    功能：從 `user_credentials.txt` 讀取帳號與密碼。

    說明：跳過檔案的第一行（標題），每行格式為 `username:password`。
    最多回傳前 20 組帳號，若少於 20 則回傳全部。

    回傳:
        list: 每項為 {'username': str, 'password': str}
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    userinfo_path = os.path.join(project_root, "user_credentials.txt")
    credentials = []

    try:
        with open(userinfo_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print("[系統] 找不到 user_credentials.txt，請確認檔案存在於專案根目錄。")
        return []

    for idx, line in enumerate(lines):
        if idx == 0:
            continue
        raw = line.strip()
        if not raw:
            continue
        if ':' in raw:
            username, password = raw.split(':', 1)
            credentials.append({
                'username': username.strip(),
                'password': password.strip()
            })

    total_count = len(credentials)
    if total_count == 0:
        print("[系統] user_credentials.txt 內容為空或格式錯誤。")
        return []

    if total_count > 20:
        print(f"[系統] 偵測到 {total_count} 組帳號，僅保留前 20 組。")
        credentials = credentials[:20]
    else:
        print(f"[系統] 已載入 {total_count} 組帳號資料。")

    return credentials


def navigate_to_JFW(driver_path, username, password):
    """
    建立瀏覽器並導向金富翁網站執行完整的自動登入流程。
    
    執行從建立瀏覽器到進入遊戲的完整流程，包括：
    1. 建立並配置 Chrome 瀏覽器實例
    2. 開啟登入頁面
    3. 輸入帳號密碼
    4. 處理登入後的各種彈窗
    5. 選擇遊戲運營商和遊戲
    
    Args:
        driver_path (str): ChromeDriver 的完整路徑
        username (str): 登入帳號
        password (str): 登入密碼
        
    Returns:
        webdriver.Chrome: 已登入並進入遊戲的瀏覽器實例，失敗時返回 None
    """
    # 建立 ChromeDriver Service
    service = Service(driver_path)

    # 配置 Chrome 選項 - 模擬正常瀏覽器行為
    chrome_options = Options()
    
    # 基本設定
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # 移除自動化控制標記
    chrome_options.add_argument("--disable-popup-blocking")  # 禁用彈窗攔截
    
    # 模擬正常使用者環境
    # chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    # chrome_options.add_argument("--lang=zh-TW")  # 設定語言為繁體中文
    # chrome_options.add_argument("--disable-web-security")  # 禁用網頁安全檢查
    # chrome_options.add_argument("--allow-running-insecure-content")  # 允許執行不安全內容
    
    # 效能優化
    chrome_options.add_argument("--disable-dev-shm-usage")  # 解決資源限制問題
    chrome_options.add_argument("--no-sandbox")  # 沙箱模式（視安全需求決定）
    
    # 時間同步設定 - 避免時間對不上導致無法聯網
    chrome_options.add_argument("--disable-features=NetworkTimeServiceQuerying")  # 禁用網路時間服務查詢
    
    # 移除自動化痕跡
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # 偏好設定
    chrome_options.add_experimental_option("prefs", {
        "credentials_enable_service": False,  # 禁用密碼管理服務
        "profile.password_manager_enabled": False,  # 禁用密碼管理器
        "profile.default_content_setting_values.notifications": 2,  # 禁用通知
        "profile.default_content_settings.popups": 0,  # 允許彈出視窗
    })

    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(300)
        driver.implicitly_wait(30)
    except Exception as e:
        print(f"[錯誤] [{username}] 建立瀏覽器失敗：{e}")
        return None

    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"[帳號:{username}] 開始登入流程（嘗試 {attempt+1}/{max_retries}）")
            driver.get("https://m.jfw-win.com/#/login?redirect=%2Fhome%2Fpage")

            wait = WebDriverWait(driver, 5)
            time.sleep(2)

            # 步驟 1：輸入帳號與密碼並送出
            username_xpath = "/html/body/div[2]/main/div/div[2]/div/div[3]/div[1]/div/div/div/div/input"
            password_xpath = "/html/body/div[2]/main/div/div[2]/div/div[3]/div[2]/div/div/div/div/input"
            login_button_xpath = "/html/body/div[2]/main/div/div[2]/div/div[3]/div[4]/div[1]"

            driver.find_element(By.XPATH, username_xpath).send_keys(username)
            driver.find_element(By.XPATH, password_xpath).send_keys(password)
            driver.find_element(By.XPATH, login_button_xpath).click()
            time.sleep(1)

            # 檢查登入失敗訊息
            try:
                error_message_xpath = "/html/body/div[3]/div[2]/div/div[3]/span"
                err_el = driver.find_element(By.XPATH, error_message_xpath)
                if err_el.text and "錯誤" in err_el.text:
                    print(f"[帳號:{username}] 登入失敗：{err_el.text}")
                    return
            except Exception:
                pass

            # 嘗試關閉可能的公告彈窗（若有）
            try:
                login_announcement_close_xpath = "/html/body/div[2]/main/div/div[2]/div/div[3]/div[6]/div/div[3]/div[2]/div[1]"
                wait.until(EC.element_to_be_clickable((By.XPATH, login_announcement_close_xpath))).click()
                print(f"[帳號:{username}] 已關閉公告彈窗")
            except Exception:
                print(f"[帳號:{username}] 無公告彈窗，繼續流程")
                pass

            # 等待進入大廳
            time.sleep(2)

            # 進入賽特遊戲頁面
            print(f"[帳號:{username}] 正在進入賽特遊戲...")
            driver.get("https://m.jfw-win.com/#/home/loding?game_code=egyptian-mythology&factory_code=ATG&state=true&name=%E6%88%B0%E7%A5%9E%E8%B3%BD%E7%89%B9")
            
            # 等待遊戲頁面載入
            time.sleep(3)

            # 設定瀏覽器視窗大小為 600x400
            driver.set_window_size(600, 400)
            print(f"[帳號:{username}] 成功進入賽特遊戲，視窗大小已設定為 600x400")
            return driver

        except Exception as e:
            if attempt < max_retries - 1:
                print(f"[警告] [{username}] 第 {attempt+1} 次嘗試失敗，稍後重試。")
                time.sleep(1)
                continue
            print(f"[錯誤] [{username}] 登入流程失敗（重試 {max_retries} 次）：{e}")
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass
            return None


def continue_game(driver):
    """
    繼續遊戲：控制瀏覽器按空白鍵並等待 15 秒後再按空白鍵，循環往復。
    
    此函式會在獨立執行緒中持續運行，直到被 pause_game 停止。
    使用全域狀態字典來控制執行/暫停。
    使用 Chrome DevTools Protocol 發送按鍵事件。
    
    Args:
        driver (webdriver.Chrome): 瀏覽器實例
    """
    try:
        # 切換到遊戲 iframe（如果有的話）
        try:
            driver.switch_to.default_content()
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            if iframes:
                driver.switch_to.frame(iframes[0])
                print("[系統] 已切換到遊戲 iframe")
        except Exception:
            pass
        
        while True:
            # 檢查是否應該繼續執行
            with game_states_lock:
                if driver not in game_states or not game_states[driver]["running"]:
                    print("[系統] 遊戲已暫停")
                    break
            
            # 按下空白鍵（使用 CDP 協議）
            try:
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
                print("[遊戲] 按下空白鍵")
            except Exception as e:
                print(f"[警告] 按空白鍵失敗：{e}")
                break
            
            # 等待 15 秒（分段檢查以便快速回應暫停指令）
            for _ in range(15):
                time.sleep(1)
                with game_states_lock:
                    if driver not in game_states or not game_states[driver]["running"]:
                        print("[系統] 偵測到暫停指令，停止執行")
                        return
            
            # 再按一次空白鍵（使用 CDP 協議）
            try:
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
                print("[遊戲] 按下空白鍵")
            except Exception as e:
                print(f"[警告] 按空白鍵失敗：{e}")
                break
                
    except Exception as e:
        print(f"[錯誤] 遊戲執行發生錯誤：{e}")
    finally:
        # 清理狀態
        with game_states_lock:
            if driver in game_states:
                game_states[driver]["running"] = False
                game_states[driver]["thread"] = None


def pause_game(driver):
    """
    暫停遊戲：停止瀏覽器按下空白鍵的行為。
    
    透過修改全域狀態來通知 continue_game 執行緒停止運行。
    
    Args:
        driver (webdriver.Chrome): 瀏覽器實例
    """
    with game_states_lock:
        if driver in game_states and game_states[driver]["running"]:
            game_states[driver]["running"] = False
            print("[系統] 已發送暫停信號")
            
            # 等待執行緒結束
            thread = game_states[driver].get("thread")
            if thread and thread.is_alive():
                # 在鎖外等待執行緒
                pass
        else:
            print("[系統] 遊戲未在執行中")
    
    # 在鎖外等待執行緒結束
    with game_states_lock:
        if driver in game_states:
            thread = game_states[driver].get("thread")
    
    if thread and thread.is_alive():
        thread.join(timeout=3)
        print("[系統] 遊戲已暫停")


def operate_sett_game(driver, command):
    """
    操作賽特遊戲的自動化流程。
    
    根據使用者輸入的指令執行對應的遊戲操作：
    - 'c': 繼續遊戲（自動按空白鍵）
    - 'p': 暫停遊戲（停止按空白鍵）
    - 'q': 關閉瀏覽器

    Args:
        driver (webdriver.Chrome): 已進入遊戲的瀏覽器實例
        command (str): 使用者輸入的操作指令
    """
    if driver is None:
        print("[系統] 瀏覽器實例不存在，無法執行遊戲操作")
        return

    if command in ("c", "C"):
        # 繼續遊戲
        with game_states_lock:
            if driver not in game_states:
                game_states[driver] = {"running": False, "thread": None}
            
            if game_states[driver]["running"]:
                print("[系統] 遊戲已在執行中")
                return
            
            # 啟動遊戲執行緒
            game_states[driver]["running"] = True
            game_thread = threading.Thread(target=continue_game, args=(driver,), daemon=True)
            game_states[driver]["thread"] = game_thread
            game_thread.start()
            print("[系統] 遊戲已開始執行")
    
    elif command in ("p", "P"):
        # 暫停遊戲
        pause_game(driver)
    
    elif command in ("Q", "q"):
        # 關閉瀏覽器
        # 先暫停遊戲
        pause_game(driver)
        
        try:
            driver.quit()
            print("[系統] 瀏覽器已關閉")
            
            # 清理狀態
            with game_states_lock:
                if driver in game_states:
                    del game_states[driver]
        except Exception as e:
            err = str(e)
            if "Remote end closed connection" not in err and "chrome not reachable" not in err.lower():
                print(f"[警告] 關閉瀏覽器時發生錯誤：{e}")
    
    else:
        print("[警告] 未識別的指令。可用指令：c(繼續)、p(暫停)、q(退出)")
    
    return


def arrange_browser_windows(drivers):
    """
    排列瀏覽器視窗：每個螢幕寬度放 5 個瀏覽器，高度放 4 個瀏覽器。
    
    Args:
        drivers (list): 瀏覽器實例列表
    """
    window_width = 600
    window_height = 400
    columns = 5  # 每行 5 個
    rows = 4     # 每列 4 個
    
    valid_drivers = [d for d in drivers if d is not None]
    if not valid_drivers:
        return
    
    print(f"[系統] 開始排列 {len(valid_drivers)} 個瀏覽器視窗...")
    
    for index, driver in enumerate(valid_drivers):
        try:
            # 計算視窗位置
            col = index % columns  # 第幾列
            row = (index // columns) % rows  # 第幾行
            
            x_position = col * window_width
            y_position = row * window_height
            
            # 設定視窗位置和大小
            driver.set_window_position(x_position, y_position)
            driver.set_window_size(window_width, window_height)
            
            print(f"[系統] 瀏覽器 #{index+1} 已移動到位置 ({x_position}, {y_position})")
        except Exception as e:
            print(f"[警告] 無法排列瀏覽器 #{index+1}：{e}")
    
    print("[系統] 瀏覽器視窗排列完成")


def main():
    """
    主程式入口：中央控管系統
    1. 載入帳號資料
    2. 取得使用者輸入的瀏覽器數量
    3. 同步啟動多個瀏覽器並登入
    4. 排列瀏覽器視窗
    5. 進入指令控制模式
    6. 清理資源並結束
    """
    print("[系統] 金富翁自動化登入與操作系統")

    # ===== 階段 1: 載入帳號資料 =====
    credentials = load_user_credentials()
    if not credentials:
        print("[系統] 無法載入帳號資料，程式結束")
        return

    # ===== 階段 2: 取得使用者輸入 =====
    max_allowed = min(20, len(credentials))
    while True:
        try:
            browser_count = int(input(f"請輸入要啟動的瀏覽器數量 (1~{max_allowed})："))
            if 1 <= browser_count <= max_allowed:
                break
            print(f"[系統] 請輸入介於 1 到 {max_allowed} 的整數。")
        except ValueError:
            print("[系統] 請輸入有效的整數。")

    # ===== 階段 3: 同步啟動所有瀏覽器 =====
    driver_path = get_chromedriver_path()
    drivers = [None] * browser_count
    threads = []
    
    # 定義執行緒工作函式（使用閉包捕獲索引）
    def launch_worker(index):
        username = credentials[index]["username"]
        password = credentials[index]["password"]
        driver = navigate_to_JFW(driver_path, username, password)
        drivers[index] = driver  # 將結果儲存到共用串列
    
    print(f"[系統] 開始啟動 {browser_count} 個瀏覽器...")
    for i in range(browser_count):
        print(f"[系統] 啟動第 {i+1} 個瀏覽器（帳號:{credentials[i]['username']}）")
        thread = threading.Thread(target=launch_worker, args=(i,))
        threads.append(thread)
        thread.start()

    print("[系統] 等待所有瀏覽器啟動完成...")
    for thread in threads:
        thread.join()
    
    # 統計成功數量
    success_count = sum(1 for d in drivers if d is not None)
    print(f"[系統] 完成！成功啟動 {success_count}/{browser_count} 個瀏覽器")

    # ===== 階段 4: 排列瀏覽器視窗 =====
    if success_count > 0:
        arrange_browser_windows(drivers)

    # ===== 階段 5: 進入指令控制模式 =====
    print("[系統] 已進入指令模式。")
    print("[系統] 可用指令：c(繼續) p(暫停) q(退出)")
    
    try:
        while True:
            command = input("請輸入指令：").strip()
            
            # 檢查是否為退出指令
            if command.lower() == 'q':
                # 先暫停所有遊戲
                print("[系統] 正在停止所有遊戲...")
                for driver in drivers:
                    if driver is not None:
                        pause_game(driver)
                
                # 關閉所有瀏覽器
                print("[系統] 正在關閉所有瀏覽器...")
                for driver in drivers:
                    if driver is not None:
                        try:
                            driver.quit()
                        except Exception:
                            pass
                break
            
            # 對所有瀏覽器執行指令（不使用執行緒，直接執行）
            for driver in drivers:
                if driver is not None:
                    operate_sett_game(driver, command)
                
    except KeyboardInterrupt:
        print("\n[系統] 偵測到中斷訊號 (Ctrl+C)")
        # 清理所有瀏覽器
        for driver in drivers:
            if driver is not None:
                try:
                    pause_game(driver)
                    driver.quit()
                except Exception:
                    pass


if __name__ == "__main__":
    main()