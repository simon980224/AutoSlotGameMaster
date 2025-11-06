from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import threading
import pyautogui
import os
import platform

def get_chromedriver_path():
    """
    自動獲取 ChromeDriver 路徑
    
    Returns:
        str: ChromeDriver 的完整路徑
    """
    # 取得專案根目錄路徑
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    # 根據作業系統決定驅動程式檔名
    system = platform.system().lower()
    if system == "windows":
        driver_filename = "chromedriver.exe"
    else:  # macOS 或 Linux
        driver_filename = "chromedriver"
    
    return os.path.join(project_root, driver_filename)

def load_user_credentials():
    """
    從 userinfo.txt 讀取用戶帳號密碼
    
    Returns:
        list: 包含用戶帳密字典的列表 [{'username': str, 'password': str}, ...]
    """
    # 建構 userinfo.txt 的完整路徑
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    userinfo_path = os.path.join(project_root, "userinfo.txt")
    credentials = []
    
    # 讀取並解析帳密資料
    with open(userinfo_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for line_num, line in enumerate(lines):
            if line_num == 0:  # 跳過標題行
                continue
            line = line.strip()
            if line and ':' in line:
                username, password = line.split(':', 1)  # 以第一個冒號分割
                credentials.append({
                    'username': username.strip(),
                    'password': password.strip()
                })
    
    print(f"[系統] 成功讀取 {len(credentials)} 組用戶帳密")
    return credentials

def create_browser(driver_path, port_number):
    """
    建立瀏覽器實例並配置選項
    
    Args:
        driver_path (str): ChromeDriver 的路徑
        port_number (int): 遠端調試端口號
        
    Returns:
        webdriver.Chrome: 配置完成的 Chrome 瀏覽器實例
    """
    # 建立 ChromeDriver Service
    service = Service(driver_path)

    # 配置 Chrome 選項以優化效能
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")  # 禁用沙盒模式
    chrome_options.add_argument("--disable-dev-shm-usage")  # 解決共享記憶體不足問題
    chrome_options.add_argument("--disable-gpu")  # 禁用 GPU 加速
    chrome_options.add_argument("--disable-extensions")  # 禁用擴充功能
    chrome_options.add_argument("--disable-plugins")  # 禁用插件
    chrome_options.add_argument("--disable-images")  # 禁用圖片載入以加速
    chrome_options.add_argument(f"--remote-debugging-port={port_number}")  # 設定調試端口

    # 建立瀏覽器實例
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # 設定超時時間
    driver.set_page_load_timeout(300)  # 頁面載入超時：5 分鐘
    driver.implicitly_wait(30)  # 元素查找超時：30 秒
    
    return driver

def navigate_to_JFW(driver, browser_number, credentials):
    """
    導向金富翁網站並執行自動登入流程
    
    Args:
        driver (webdriver.Chrome): 瀏覽器實例
        browser_number (int): 瀏覽器編號（從 1 開始）
        credentials (list): 用戶帳密列表
    """
    # 驗證瀏覽器實例
    if driver is None:
        print(f"[錯誤] 瀏覽器 {browser_number} 未成功建立，跳過操作")
        return
    
    # 驗證帳密資料是否存在
    if browser_number > len(credentials):
        print(f"[錯誤] 瀏覽器 {browser_number} 沒有對應的帳密資料")
        return
    
    # 取得對應的用戶帳密
    user_cred = credentials[browser_number - 1]
    username = user_cred['username']
    password = user_cred['password']
    
    # 設定重試機制
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"[瀏覽器 {browser_number}] 正在導向網站...")
            driver.get("https://m.jfw-win.com/#/home/page")
            
            # 初始化等待物件
            wait = WebDriverWait(driver, 30)
            
            # === 步驟 1: 點擊用戶資料按鈕 ===
            print(f"[瀏覽器 {browser_number}] 步驟 1: 點擊用戶資料")
            userinfo_xpath = "/html/body/div[2]/div[3]/div/section/div/main/div[1]/div[2]/img"
            userinfo_element = wait.until(EC.element_to_be_clickable((By.XPATH, userinfo_xpath)))
            userinfo_element.click()
            time.sleep(5)
            
            # === 步驟 2: 輸入帳號 ===
            print(f"[瀏覽器 {browser_number}] 步驟 2: 輸入帳號")
            username_xpath = "/html/body/div[2]/main/div/div[2]/div/div[3]/div[1]/div/div/div/div/input"
            username_element = wait.until(EC.element_to_be_clickable((By.XPATH, username_xpath)))
            username_element.clear()
            username_element.send_keys(username)
            
            # === 步驟 3: 輸入密碼 ===
            print(f"[瀏覽器 {browser_number}] 步驟 3: 輸入密碼")
            password_xpath = "/html/body/div[2]/main/div/div[2]/div/div[3]/div[2]/div/div/div/div/input"
            password_element = wait.until(EC.element_to_be_clickable((By.XPATH, password_xpath)))
            password_element.clear()
            password_element.send_keys(password)
            time.sleep(1)
            
            # === 步驟 4: 點擊登入按鈕 ===
            print(f"[瀏覽器 {browser_number}] 步驟 4: 點擊登入")
            login_button_xpath = "/html/body/div[2]/main/div/div[2]/div/div[3]/div[4]/div[1]"
            login_button = wait.until(EC.element_to_be_clickable((By.XPATH, login_button_xpath)))
            login_button.click()
            time.sleep(3)
            
            try:
                # 尋找第一個公告關閉按鈕
                login_announcement_close_xpath = "/html/body/div[2]/main/div/div[2]/div/div[3]/div[6]/div/div[3]/div[2]/div[1]"
                login_announcement_close_button = wait.until(EC.element_to_be_clickable((By.XPATH, login_announcement_close_xpath)))
                login_announcement_close_button.click()

            except Exception as login_announcement_error:
                pass    # 沒有找到公告，繼續下一步

            # 5. 等待登入驗證
            time.sleep(5)  # 等待5秒讓第二個公告出現

            # ----------登入----------登入----------登入----------登入----------登入----------
            
            # 6. 處理大廳公告（可能出現多次）
            lobby_announcement_xpath = "/html/body/div[2]/div[3]/div/section/div/main/div[6]/div[2]/img"
            announcement_count = 0
            max_announcements = 10  # 設定最大處理次數避免無限迴圈
            while announcement_count < max_announcements:
                try:
                    # 設定較短的等待時間來檢查公告是否存在
                    short_wait = WebDriverWait(driver, 5)
                    lobby_announcement_button = short_wait.until(EC.element_to_be_clickable((By.XPATH, lobby_announcement_xpath)))
                    lobby_announcement_button.click()
                    announcement_count += 1
                    time.sleep(3)  # 等待下一個公告可能出現

                except Exception:
                    break   # 沒有找到公告，結束迴圈

            print(f"[瀏覽器 {browser_number}] 成功進入大廳")
            time.sleep(3)
            
            # === 步驟 7: 點擊遊戲運營商選單 ===
            try:
                print(f"[瀏覽器 {browser_number}] 步驟 7: 開啟遊戲運營商選單")
                game_provider_xpath = "/html/body/div[2]/div[3]/div/section/div/main/div[3]/div[1]/div/div[2]/img"
                game_provider_button = wait.until(EC.element_to_be_clickable((By.XPATH, game_provider_xpath)))
                game_provider_button.click()
            except Exception as e:
                print(f"[錯誤] 瀏覽器 {browser_number} 無法開啟運營商選單: {e}")
            
            time.sleep(3)
            
            # === 步驟 8: 選擇 ATG 運營商 ===
            try:
                print(f"[瀏覽器 {browser_number}] 步驟 8: 選擇 ATG 運營商")
                atg_xpath = "//div[contains(@class, 'tablabel') and text()='ATG']"
                atg_element = wait.until(EC.element_to_be_clickable((By.XPATH, atg_xpath)))
                atg_container = atg_element.find_element(By.XPATH, "..")
                atg_container.click()
            except Exception as e:
                print(f"[錯誤] 瀏覽器 {browser_number} 無法選擇 ATG 運營商: {e}")
            
            time.sleep(3)
            
            # === 步驟 9: 點擊賽特遊戲 ===
            try:
                print(f"[瀏覽器 {browser_number}] 步驟 9: 選擇賽特遊戲")
                sett_game_xpath = "/html/body/div[2]/div[3]/div/section/div/main/div[3]/div[2]/div/div/div[1]/div[2]/div/div[2]/div/img"
                sett_game_element = wait.until(EC.element_to_be_clickable((By.XPATH, sett_game_xpath)))
                sett_game_element.click()
            except Exception as e:
                print(f"[錯誤] 瀏覽器 {browser_number} 無法選擇賽特遊戲: {e}")
            
            time.sleep(3)
            
            # === 步驟 10: 點擊遊玩按鈕 ===
            try:
                print(f"[瀏覽器 {browser_number}] 步驟 10: 點擊遊玩按鈕")
                sett_game_play_button_xpath = "/html/body/div[2]/div[3]/div/section/div/main/div[3]/div[2]/div/div/div[1]/div[2]/div[3]/div[3]"
                sett_game_play_button_element = wait.until(EC.element_to_be_clickable((By.XPATH, sett_game_play_button_xpath)))
                sett_game_play_button_element.click()
            except Exception as e:
                print(f"[錯誤] 瀏覽器 {browser_number} 無法點擊遊玩按鈕: {e}")
            
            print(f"[瀏覽器 {browser_number}] ✓ 成功進入賽特遊戲")

            # 更新瀏覽器大小並進行排版
            # 獲取螢幕大小
            screen_width, screen_height = pyautogui.size()
            
            # 計算每個瀏覽器的寬度和高度（5列4行）
            browser_width = screen_width // 5
            browser_height = screen_height // 4
            
            # 計算當前瀏覽器的位置（browser_number從1開始）
            # 位置計算：第1個在(0,0)，第2個在(1,0)...第6個在(0,1)
            col = (browser_number - 1) % 5  # 列位置 (0-4)
            row = (browser_number - 1) // 5  # 行位置 (0-3)
            
            x_position = col * browser_width
            y_position = row * browser_height
            
            # 設置瀏覽器窗口位置和大小
            driver.set_window_position(x_position, y_position)
            driver.set_window_size(browser_width, browser_height)
            
            print(f"[瀏覽器 {browser_number}] ✓ 視窗排版完成 - 位置({x_position}, {y_position}) 大小({browser_width}x{browser_height})")
            
            return
        
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"[警告] 帳號 {username} 第 {attempt + 1} 次嘗試失敗，2秒後重試...")
                time.sleep(2)
            else:
                print(f"[錯誤] 帳號 {username} 操作失敗（已重試 {max_retries} 次）: {e}")


def close_browser(browser_number, driver):
    """
    關閉指定的瀏覽器實例
    
    Args:
        browser_number (int): 瀏覽器編號
        driver (webdriver.Chrome): 瀏覽器實例
    """
    if driver is None:
        return
        
    try:
        driver.quit()
        print(f"[系統] 瀏覽器 {browser_number} 已關閉")
    except Exception as e:
        # 忽略正常關閉時的無害錯誤訊息
        error_message = str(e)
        if "Remote end closed connection" not in error_message and "chrome not reachable" not in error_message.lower():
            print(f"[警告] 關閉瀏覽器 {browser_number} 時發生錯誤: {e}")


if __name__ == "__main__":
    """
    主程式進入點
    功能：批量啟動瀏覽器並自動登入金富翁遊戲
    """
    print("=" * 60)
    print("自動賽特遊戲大師 - 批量登入系統")
    print("=" * 60)
    
    # ===== 初始化階段 =====
    print("\n[階段 1] 系統初始化")
    driver_path = get_chromedriver_path()
    print(f"[系統] ChromeDriver 路徑: {driver_path}")

    user_credentials = load_user_credentials()
    if not user_credentials:
        print("[錯誤] 無法讀取用戶資料，程式終止")
        exit(1)

    # ===== 建立瀏覽器階段 =====
    print(f"\n[階段 2] 建立瀏覽器實例")
    drivers = []
    base_port = 9222
    browser_count = 2   # TODO: 修改此數值以設定瀏覽器數量

    for i in range(browser_count):
        port_number = base_port + i
        print(f"[系統] 正在建立瀏覽器 {i+1}/{browser_count} (端口: {port_number})")
        
        try:
            driver = create_browser(driver_path, port_number)
            drivers.append(driver)
            time.sleep(1)
        except Exception as e:
            print(f"[錯誤] 瀏覽器 {i+1} 建立失敗: {e}")
            drivers.append(None)

    # ===== 多線程登入階段 =====
    print(f"\n[階段 3] 執行多線程自動登入")
    threads = []

    for i, driver in enumerate(drivers):
        thread = threading.Thread(target=navigate_to_JFW, args=(driver, i+1, user_credentials))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print("\n" + "=" * 60)
    print("[系統] 所有瀏覽器登入流程已完成")
    print("=" * 60)
    input("\n按 Enter 鍵關閉所有瀏覽器...")

    # ===== 關閉瀏覽器階段 =====
    print("\n[階段 4] 關閉所有瀏覽器")
    close_threads = []

    for i, driver in enumerate(drivers):
        thread = threading.Thread(target=close_browser, args=(i+1, driver))
        close_threads.append(thread)
        thread.start()

    for thread in close_threads:
        thread.join()

    print("\n" + "=" * 60)
    print("[系統] 程式執行完畢，所有瀏覽器已關閉")
    print("=" * 60)
