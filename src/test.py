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
    自動獲取 ChromeDriver 路徑。
    
    根據作業系統自動判斷並返回 ChromeDriver 的完整路徑。
    Windows 系統返回 .exe 檔案路徑，macOS 或 Linux 系統返回一般執行檔路徑。
    
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
    從 user_credentials.txt 讀取用戶帳號密碼。
    
    讀取並解析 user_credentials.txt 文件中的帳號密碼資訊，跳過標題行，
    每行格式為 "username:password"。同時進行帳號數量限制檢查。
    
    Returns:
        list: 包含用戶帳密字典的列表，格式為 [{'username': str, 'password': str}, ...]
        每個字典包含 'username' 和 'password' 兩個鍵值對
    """
    # 建構 user_credentials.txt 的完整路徑
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    userinfo_path = os.path.join(project_root, "user_credentials.txt")
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
    
    # 檢查帳號數量並進行限制
    total_count = len(credentials)
    if total_count > 20:
        print(f"[系統] 偵測到 {total_count} 個帳號，超過 20 個上限，只取前 20 個帳號")
        credentials = credentials[:20]
    else:
        print(f"[系統] 成功讀取 {total_count} 組用戶帳密")
    
    return credentials


def create_browser(driver_path):
    """
    建立並配置 Chrome 瀏覽器實例。
    
    設定瀏覽器的各項優化選項，包括禁用不必要的功能、設定調試端口、
    配置安全選項等，以提升自動化效能和穩定性。
    
    Args:
        browser_number (int): 瀏覽器編號，從 1 開始計數
        driver_path (str): ChromeDriver 的完整路徑
        
    Returns:
        webdriver.Chrome: 完整配置的 Chrome 瀏覽器實例
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
    # chrome_options.add_argument(f"--remote-debugging-port={port_number}")  # 設定調試端口
    chrome_options.add_experimental_option("prefs", {
        "credentials_enable_service": False,  # 禁用密碼儲存服務
        "profile.password_manager_enabled": False  # 禁用密碼管理器
    })
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])  # 隱藏自動化控制提示
    chrome_options.add_experimental_option('useAutomationExtension', False)  # 禁用自動化擴充

    # 建立瀏覽器實例
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # 設定超時時間
    driver.set_page_load_timeout(300)  # 頁面載入超時：5 分鐘
    driver.implicitly_wait(30)  # 元素查找超時：30 秒
    
    return driver


def navigate_to_JFW(driver, browser_number, credentials):
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
        browser_number (int): 瀏覽器編號，從 1 開始計數
        credentials (list): 包含帳密資訊的用戶憑證列表
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
            print(f"[瀏覽器 {browser_number}] 正在導向登入頁面...")
            driver.get("https://m.jfw-win.com/#/login?redirect=%2Fhome%2Fpage")
            
            # 初始化等待物件
            wait = WebDriverWait(driver, 30)
            time.sleep(3)
            
            # === 步驟 2: 輸入帳號 ===
            print(f"[瀏覽器 {browser_number}] ⏳ 輸入帳號...")
            username_xpath = "/html/body/div[2]/main/div/div[2]/div/div[3]/div[1]/div/div/div/div/input"
            username_element = driver.find_element(By.XPATH, username_xpath)
            username_element.send_keys(username)
            
            # === 步驟 3: 輸入密碼 ===
            print(f"[瀏覽器 {browser_number}] ⏳ 輸入密碼...")
            password_xpath = "/html/body/div[2]/main/div/div[2]/div/div[3]/div[2]/div/div/div/div/input"
            password_element = driver.find_element(By.XPATH, password_xpath)
            password_element.send_keys(password)
            
            # === 步驟 4: 點擊登入按鈕 ===
            print(f"[瀏覽器 {browser_number}] ⏳ 執行登入...")
            login_button_xpath = "/html/body/div[2]/main/div/div[2]/div/div[3]/div[4]/div[1]"
            login_button = driver.find_element(By.XPATH, login_button_xpath)
            login_button.click()
            time.sleep(1)

            # === 檢查是否登入失敗 ===
            try:
                error_message_xpath = "/html/body/div[3]/div[2]/div/div[3]/span"
                error_message_element = driver.find_element(By.XPATH, error_message_xpath)
                if error_message_element.text == "帳號密碼錯誤":
                    print(f"[瀏覽器 {browser_number}] ❌ 登入失敗：帳號密碼錯誤")
                    return  # 直接返回，不繼續執行後續步驟
            except:
                pass  # 如果找不到錯誤訊息，表示登入可能成功，繼續執行
            
            # === 步驟 5: 關閉登入公告 ===
            print(f"[瀏覽器 {browser_number}] 步驟 5: 處理登入公告")
            try:
                # 尋找第一個公告關閉按鈕
                login_announcement_close_xpath = "/html/body/div[2]/main/div/div[2]/div/div[3]/div[6]/div/div[3]/div[2]/div[1]"
                login_announcement_close_button = wait.until(EC.element_to_be_clickable((By.XPATH, login_announcement_close_xpath)))
                login_announcement_close_button.click()

            except Exception as login_announcement_error:
                pass    # 沒有找到公告，繼續下一步

            # === 步驟 6: 等待登入驗證 ===
            print(f"[瀏覽器 {browser_number}] 步驟 6: 等待登入驗證")
            time.sleep(5)  # 等待5秒讓第二個公告出現

            # ----------登入----------登入----------登入----------登入----------登入----------
            
            # 處理大廳公告（可能出現多次）
            lobby_announcement_xpath = "/html/body/div[2]/div[3]/div/section/div/main/div[6]/div[2]/img"
            announcement_count = 0
            max_announcements = 10  # 設定最大處理次數避免無限迴圈
            while announcement_count < max_announcements:
                try:
                    lobby_announcement_button = wait.until(EC.element_to_be_clickable((By.XPATH, lobby_announcement_xpath)))
                    lobby_announcement_button.click()
                    announcement_count += 1
                    time.sleep(1)  # 等待下一個公告可能出現

                except Exception:
                    break   # 沒有找到公告，結束迴圈

            print(f"[瀏覽器 {browser_number}] 成功進入大廳")
            time.sleep(1)
            
            # === 步驟 7: 點擊遊戲運營商選單 ===
            try:
                print(f"[瀏覽器 {browser_number}] ⏳ 開啟遊戲運營商選單...")
                game_provider_xpath = "/html/body/div[2]/div[3]/div/section/div/main/div[3]/div[1]/div/div[2]/img"
                game_provider_button = wait.until(EC.element_to_be_clickable((By.XPATH, game_provider_xpath)))
                game_provider_button.click()
            except Exception as e:
                print(f"[錯誤] 瀏覽器 {browser_number} 無法開啟運營商選單: {e}")
            
            time.sleep(1)
            
            # === 步驟 8: 選擇 ATG 運營商 ===
            try:
                print(f"[瀏覽器 {browser_number}] ⏳ 選擇 ATG 運營商...")
                atg_xpath = "//div[contains(@class, 'tablabel') and text()='ATG']"
                atg_element = wait.until(EC.element_to_be_clickable((By.XPATH, atg_xpath)))
                atg_container = atg_element.find_element(By.XPATH, "..")
                atg_container.click()
            except Exception as e:
                print(f"[錯誤] 瀏覽器 {browser_number} 無法選擇 ATG 運營商: {e}")
            
            time.sleep(1)
            
            # === 步驟 9: 點擊賽特遊戲 ===
            try:
                print(f"[瀏覽器 {browser_number}] ⏳ 選擇賽特遊戲...")
                sett_game_xpath = "/html/body/div[2]/div[3]/div/section/div/main/div[3]/div[2]/div/div/div[1]/div[2]/div/div[2]/div/img"
                sett_game_element = wait.until(EC.element_to_be_clickable((By.XPATH, sett_game_xpath)))
                sett_game_element.click()
            except Exception as e:
                print(f"[錯誤] 瀏覽器 {browser_number} 無法選擇賽特遊戲: {e}")
            
            time.sleep(1)
            
            # === 步驟 10: 點擊遊玩按鈕 ===
            try:
                print(f"[瀏覽器 {browser_number}] ⏳ 啟動遊戲...")
                sett_game_play_button_xpath = "/html/body/div[2]/div[3]/div/section/div/main/div[3]/div[2]/div/div/div[1]/div[2]/div[3]/div[3]"
                sett_game_play_button_element = wait.until(EC.element_to_be_clickable((By.XPATH, sett_game_play_button_xpath)))
                sett_game_play_button_element.click()
            except Exception as e:
                print(f"[錯誤] 瀏覽器 {browser_number} 無法點擊遊玩按鈕: {e}")
            
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

            print(f"[瀏覽器 {browser_number}] ✓ 成功進入賽特遊戲")
            
            return
        
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"[警告] 帳號 {username} 第 {attempt + 1} 次嘗試失敗，1秒後重試...")
                time.sleep(1)
            else:
                print(f"[錯誤] 帳號 {username} 操作失敗（已重試 {max_retries} 次）: {e}")


def operate_sett_game(driver, browser_number):
    """
    操作賽特遊戲的自動化流程。
    
    處理遊戲內的各項操作，包括：
    - 點擊按鈕
    - 處理遊戲內彈窗
    - 執行遊戲特定操作
    
    Args:
        driver (webdriver.Chrome): 已進入遊戲的瀏覽器實例
        browser_number (int): 瀏覽器編號，從 1 開始計數
    """
    return


def close_browser(browser_number, driver):
    """
    安全關閉指定的瀏覽器實例。
    
    處理瀏覽器關閉過程，包括：
    - 檢查瀏覽器實例是否有效
    - 優雅處理關閉過程中的異常
    - 過濾正常關閉時的無害錯誤訊息
    
    Args:
        browser_number (int): 要關閉的瀏覽器編號
        driver (webdriver.Chrome): 要關閉的瀏覽器實例
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


def main():
    pass


if __name__ == "__main__":
    main()