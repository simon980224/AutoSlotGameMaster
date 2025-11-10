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
from threading import Lock


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


def create_browser(driver_path):
    """
    建立並配置 Chrome 瀏覽器實例。
    
    設定瀏覽器的各項優化選項，包括禁用不必要的功能、設定調試端口、
    配置安全選項等，以提升自動化效能和穩定性。
    
    Args:
        driver_path (str): ChromeDriver 的完整路徑
        
    Returns:
        webdriver.Chrome: 完整配置的 Chrome 瀏覽器實例
    """
    # 建立 ChromeDriver Service
    service = Service(driver_path)

    # 配置 Chrome 選項
    chrome_options = Options()
    # chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--disable-dev-shm-usage")
    # chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--disable-extensions")
    # chrome_options.add_argument("--disable-plugins")
    # chrome_options.add_argument("--disable-images")
    # chrome_options.add_experimental_option("prefs", {
    #     "credentials_enable_service": False,
    #     "profile.password_manager_enabled": False
    # })
    # chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # chrome_options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(300)
    driver.implicitly_wait(30)

    return driver


def navigate_to_JFW(driver, username, password):
    """
    導向金富翁網站並執行完整的自動登入流程。
    
    執行從登入到進入遊戲的完整流程，包括：
    1. 開啟登入頁面
    2. 輸入帳號密碼
    3. 處理登入後的各種彈窗
    4. 選擇遊戲運營商和遊戲
    5. 調整瀏覽器視窗位置和大小
    
    Args:
        driver (webdriver.Chrome): 已配置的瀏覽器實例
        username (str): 登入帳號
        password (str): 登入密碼
    """
    if driver is None:
        print(f"[系統] [{username}] 瀏覽器未建立，跳過。")
        return

    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"[帳號:{username}] 開始登入流程（嘗試 {attempt+1}/{max_retries}）")
            driver.get("https://m.jfw-win.com/#/login?redirect=%2Fhome%2Fpage")

            wait = WebDriverWait(driver, 30)
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
                pass

            # 進入賽特遊戲頁面
            try:
                driver.get("https://m.jfw-win.com/#/home/loding?game_code=egyptian-mythology&factory_code=ATG&state=true&name=%E6%88%B0%E7%A5%9E%E8%B3%BD%E7%89%B9")
            except Exception:
                pass

            print(f"[帳號:{username}] 成功進入賽特遊戲")
            return

        except Exception as e:
            if attempt < max_retries - 1:
                print(f"[警告] [{username}] 第 {attempt+1} 次嘗試失敗，稍後重試。")
                time.sleep(1)
                continue
            print(f"[錯誤] [{username}] 登入流程失敗（重試 {max_retries} 次）：{e}")
            return


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
    # if command == "start":
    #     # 執行開始遊戲動作
    # elif command == "pause":
    #     # 執行暫停遊戲動作
    # elif command == "auto":
    #     # 啟動自動模式
    # else:
    #     print("[警告] 未識別的指令")
    return


def close_browser(driver):
    """
    安全關閉指定的瀏覽器實例。

    處理關閉過程中的異常並給出友善的日誌訊息。

    Args:
        driver (webdriver.Chrome): 要關閉的瀏覽器實例
    """
    if driver is None:
        return

    try:
        driver.quit()
        print("[系統] 瀏覽器已關閉")
    except Exception as e:
        err = str(e)
        if "Remote end closed connection" not in err and "chrome not reachable" not in err.lower():
            print(f"[警告] 關閉瀏覽器時發生錯誤：{e}")


def main():
    """
    主程式入口：
    1. 由使用者輸入要啟動的瀏覽器數量。
    2. 使用 threading 同步啟動多個瀏覽器、登入金富翁網站並進入遊戲。
    3. 等待使用者輸入操作指令。
       - 若輸入 'q' 則關閉所有瀏覽器並結束程式。
    """
    print("[系統] 金富翁自動化登入與操作系統")

    credentials = load_user_credentials()
    if not credentials:
        return

    max_allowed = 20
    while True:
        try:
            browser_count = int(input(f"請輸入要啟動的瀏覽器數量 (1~{max_allowed})："))
            if 1 <= browser_count <= max_allowed:
                break
            print(f"[系統] 請輸入介於 1 到 {max_allowed} 的整數。")
        except ValueError:
            print("[系統] 請輸入有效的整數。")

    driver_path = get_chromedriver_path()

    drivers = [None] * browser_count
    drivers_lock = Lock()
    threads = []

    def init_browser_thread(index, username, password):
        """
        線程函式：建立瀏覽器並執行登入流程
        
        Args:
            index (int): 瀏覽器索引
            username (str): 登入帳號
            password (str): 登入密碼
        """
        try:
            print(f"[系統] 啟動第 {index+1} 個瀏覽器（帳號:{username}）")
            driver = create_browser(driver_path)
            navigate_to_JFW(driver, username, password)
            
            with drivers_lock:
                drivers[index] = driver
        except Exception as e:
            print(f"[錯誤] 第 {index+1} 個瀏覽器啟動失敗：{e}")

    # 建立並啟動所有線程
    for i in range(browser_count):
        username = credentials[i]["username"]
        password = credentials[i]["password"]
        thread = threading.Thread(
            target=init_browser_thread,
            args=(i, username, password)
        )
        threads.append(thread)
        thread.start()
        time.sleep(0.5)  # 稍微錯開啟動時間，避免資源競爭

    # 等待所有線程完成
    print("[系統] 等待所有瀏覽器啟動完成...")
    for thread in threads:
        thread.join()

    print("[系統] 已啟動所有瀏覽器。輸入 'q' 可關閉並離開。")

    while True:
        command = input("請輸入指令：").strip().lower()
        if command == "q":
            print("[系統] 開始關閉所有瀏覽器...")
            
            # 使用線程同步關閉所有瀏覽器
            close_threads = []
            for i, driver in enumerate(drivers):
                if driver is not None:
                    thread = threading.Thread(
                        target=close_browser,
                        args=(driver,)
                    )
                    close_threads.append(thread)
                    thread.start()
            
            # 等待所有關閉線程完成
            for thread in close_threads:
                thread.join()
            
            print("[系統] 已全部關閉，程式結束。")
            break
        else:
            # 使用線程同步執行遊戲操作
            operation_threads = []
            for driver in drivers:
                if driver is not None:
                    thread = threading.Thread(
                        target=operate_sett_game,
                        args=(driver, command)
                    )
                    operation_threads.append(thread)
                    thread.start()
            
            # 等待所有操作線程完成
            for thread in operation_threads:
                thread.join()

if __name__ == "__main__":
    main()