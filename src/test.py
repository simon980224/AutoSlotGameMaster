from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import platform
import threading


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
            except Exception:
                print(f"[帳號:{username}] 無公告彈窗，繼續流程")
                pass

            # # 處理大廳公告（可能出現多次）
            # lobby_announcement_xpath = "/html/body/div[2]/div[3]/div/section/div/main/div[6]/div[2]/img"
            # announcement_count = 0
            # max_announcements = 10  # 設定最大處理次數避免無限迴圈
            # while announcement_count < max_announcements:
            #     try:
            #         lobby_announcement_button = wait.until(EC.element_to_be_clickable((By.XPATH, lobby_announcement_xpath)))
            #         lobby_announcement_button.click()
            #         announcement_count += 1
            #         time.sleep(1)  # 等待下一個公告可能出現

            #     except Exception:
            #         break   # 沒有找到公告，結束迴圈

            # print(f"[帳號:{username}] 成功進入大廳")

            # 進入賽特遊戲頁面
            try:
                driver.get("https://m.jfw-win.com/#/home/loding?game_code=egyptian-mythology&factory_code=ATG&state=true&name=%E6%88%B0%E7%A5%9E%E8%B3%BD%E7%89%B9")
            except Exception:
                print(f"[帳號:{username}] 進入賽特遊戲頁面失敗，重試中...")
                pass

            print(f"[帳號:{username}] 成功進入賽特遊戲")
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


def operate_sett_game(driver, command):
    """
    操作賽特遊戲的自動化流程。
    
    根據使用者輸入的指令執行對應的遊戲操作。
    目前指令內容暫緩實作，僅做為結構預留。

    Args:
        driver (webdriver.Chrome): 已進入遊戲的瀏覽器實例
        command (str): 使用者輸入的操作指令
    """
    if driver is None:
        print("[系統] 瀏覽器實例不存在，無法執行遊戲操作")
        return

    print(f"[系統] 已收到指令：{command}（功能未實作）")
    # === 以下區塊將於未來實作各項遊戲操作指令 ===
    if command in ("Q","q"):
        try:
            driver.quit()
            print("[系統] 瀏覽器已關閉")
        except Exception as e:
            err = str(e)
            if "Remote end closed connection" not in err and "chrome not reachable" not in err.lower():
                print(f"[警告] 關閉瀏覽器時發生錯誤：{e}")
    else:
        print("[警告] 未識別的指令")
    return


def main():
    """
    主程式入口：中央控管系統
    1. 載入帳號資料
    2. 取得使用者輸入的瀏覽器數量
    3. 同步啟動多個瀏覽器並登入
    4. 進入指令控制模式
    5. 清理資源並結束
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

    # ===== 階段 4: 進入指令控制模式 =====
    print("[系統] 已進入指令模式。輸入 'q' 可關閉所有瀏覽器並離開。")
    
    try:
        while True:
            command = input("請輸入指令：").strip()
            
            # 檢查是否為退出指令
            if command.lower() == 'q':
                break
            
            # 對所有瀏覽器執行指令
            operation_threads = []
            for driver in drivers:
                if driver is not None:
                    thread = threading.Thread(
                        target=operate_sett_game,
                        args=(driver, command)
                    )
                    operation_threads.append(thread)
                    thread.start()
            
            # 等待所有操作完成
            for thread in operation_threads:
                thread.join()
                
    except KeyboardInterrupt:
        print("\n[系統] 偵測到中斷訊號 (Ctrl+C)")


if __name__ == "__main__":
    main()