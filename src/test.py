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
    """自動獲取 ChromeDriver 路徑，優先使用本地驅動檔案"""
    # 獲取專案根目錄路徑
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    # 根據作業系統選擇正確的檔案名稱
    system = platform.system().lower()
    if system == "windows":
        driver_filename = "chromedriver.exe"
    else :  # macOS
        driver_filename = "chromedriver"
    
    return os.path.join(project_root, driver_filename)

def load_user_credentials():
    """從 userinfo.txt 讀取用戶帳號密碼"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    userinfo_path = os.path.join(project_root, "userinfo.txt")
    credentials = []
    
    with open(userinfo_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for line_num, line in enumerate(lines):
            if line_num == 0:  # 直接跳過第一行
                continue
            line = line.strip()
            if line and ':' in line:
                username, password = line.split(':', 1)  # 只分割第一個冒號
                credentials.append({
                    'username': username.strip(),
                    'password': password.strip()
                })
    
    print(f"成功讀取 {len(credentials)} 組用戶帳密")
    return credentials

def create_browser(driver_path, port_number):
    """建立瀏覽器並設定位置、大小和依序端口"""
    service = Service(driver_path)  # 創建獨立的 Service 實例避免衝突

    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox") # 禁用沙盒模式，避免在某些環境下的權限問題
    chrome_options.add_argument("--disable-dev-shm-usage")  # 禁用 /dev/shm 使用，解決共享記憶體不足的問題
    chrome_options.add_argument("--disable-gpu")  # 禁用 GPU 硬體加速，提高在虛擬環境或無顯示環境中的穩定性
    chrome_options.add_argument("--disable-extensions")  # 禁用所有瀏覽器擴充功能，減少干擾和提高啟動速度
    chrome_options.add_argument("--disable-plugins")  # 禁用所有插件 (如 Flash)，減少潜在衝突
    chrome_options.add_argument("--disable-images")  # 禁用圖片加載，減少網路流量和記憶體使用，提高頁面載入速度
    chrome_options.add_argument(f"--remote-debugging-port={port_number}")  # 設定遠端調試端口，允許外部工具連接並控制瀏覽器

    driver = webdriver.Chrome(service=service, options=chrome_options)
    # 設置更長的超時時間
    driver.set_page_load_timeout(300)  # 5分鐘超時
    driver.implicitly_wait(30)  # 30秒隱式等待
    return driver

def navigate_to_JFW(driver, browser_number, credentials):
    """讓指定的瀏覽器導向網站並執行登入"""
    if driver is None:
        print(f"瀏覽器 {browser_number} 未成功建立，跳過導向")
        return
    
    # 獲取對應的帳密（browser_number從1開始，list index從0開始）
    if browser_number > len(credentials):
        print(f"瀏覽器 {browser_number} 沒有對應的帳密資料，跳過登入")
        return
    
    user_cred = credentials[browser_number - 1]
    username = user_cred['username']
    password = user_cred['password']
    
    max_retries = 3 # 最大重試次數
    for attempt in range(max_retries):
        try:
            driver.get("https://m.jfw-win.com/#/home/page")
            
            # 使用 WebDriverWait 等待元素出現
            wait = WebDriverWait(driver, 30)  # 最多等待30秒
            
            # 點選用戶資料
            userinfo_xpath = "/html/body/div[2]/div[3]/div/section/div/main/div[1]/div[2]/img"
            userinfo_element = wait.until(EC.element_to_be_clickable((By.XPATH, userinfo_xpath)))
            userinfo_element.click()

            # 開始登入流程
            time.sleep(5)
            
            # 1. 輸入帳號
            username_xpath = "/html/body/div[2]/main/div/div[2]/div/div[3]/div[1]/div/div/div/div/input"
            username_element = wait.until(EC.element_to_be_clickable((By.XPATH, username_xpath)))
            username_element.clear()  # 清空輸入框
            username_element.send_keys(username)
            
            # 2. 輸入密碼
            password_xpath = "/html/body/div[2]/main/div/div[2]/div/div[3]/div[2]/div/div/div/div/input"
            password_element = wait.until(EC.element_to_be_clickable((By.XPATH, password_xpath)))
            password_element.clear()  # 清空輸入框
            password_element.send_keys(password)
            
            time.sleep(1)
            
            # 3. 點擊登入
            login_button_xpath = "/html/body/div[2]/main/div/div[2]/div/div[3]/div[4]/div[1]"
            login_button = wait.until(EC.element_to_be_clickable((By.XPATH, login_button_xpath)))
            login_button.click()
            
            # 4. 等待登入公告
            time.sleep(3)  # 等待5秒讓公告出現
            
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

            # 7. 進入金富翁大廳
            print(f"{username} 進入金富翁大廳完成")
            
            # 9. 點擊開啟所有遊戲運營商
            time.sleep(3)  # 等待2秒讓頁面穩定
            
            try:
                # 點擊遊戲運營商按鈕
                game_provider_xpath = "/html/body/div[2]/div[3]/div/section/div/main/div[3]/div[1]/div/div[2]/img"
                game_provider_button = wait.until(EC.element_to_be_clickable((By.XPATH, game_provider_xpath)))
                game_provider_button.click()

            except Exception as game_provider_error:
                print(f"瀏覽器 {username} 點擊遊戲運營商失敗: {game_provider_error}")
            
            # 10. 尋找並點擊ATG運營商
            time.sleep(3)  # 等待3秒讓運營商列表載入
            
            try:
                # 尋找包含"ATG"文字的運營商                    
                # 使用XPath尋找包含ATG文字的div元素
                atg_xpath = "//div[contains(@class, 'tablabel') and text()='ATG']"
                atg_element = wait.until(EC.element_to_be_clickable((By.XPATH, atg_xpath)))
                atg_container = atg_element.find_element(By.XPATH, "..")  # 獲取父元素（整個inner-item容器）
                atg_container.click()
                
            except Exception as atg_error:
                print(f"瀏覽器 {username} 點擊ATG運營商失敗: {atg_error}")
            
            # 11. 尋找並點擊塞特遊戲選單
            time.sleep(3)  # 等待3秒讓ATG遊戲列表載入
            
            try:
                # 點擊指定的塞特遊戲選單
                sett_game_xpath = "/html/body/div[2]/div[3]/div/section/div/main/div[3]/div[2]/div/div/div[1]/div[2]/div/div[2]/div/img"
                sett_game_element = wait.until(EC.element_to_be_clickable((By.XPATH, sett_game_xpath)))
                sett_game_element.click()

            except Exception as game_menu_error:
                print(f"瀏覽器 {username} 點擊遊戲選單失敗: {game_menu_error}")
            
            # 12. 點擊塞特遊玩按鈕
            time.sleep(3)  # 等待2秒讓遊戲詳情載入
            
            try:
                # 點擊遊玩按鈕
                sett_game_play_button_xpath = "/html/body/div[2]/div[3]/div/section/div/main/div[3]/div[2]/div/div/div[1]/div[2]/div[3]/div[3]"
                sett_game_play_button_element = wait.until(EC.element_to_be_clickable((By.XPATH, sett_game_play_button_xpath)))
                sett_game_play_button_element.click()

            except Exception as play_button_error:
                print(f"瀏覽器 {username} 點擊遊玩按鈕失敗: {play_button_error}")
            
            print(f"瀏覽器 {username} 成功導向賽特")

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
            
            print(f"瀏覽器 {username} 已排版至位置({x_position}, {y_position})，大小({browser_width}x{browser_height})")
            
            return  # 成功後退出函數
        
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"帳號 {username} 第 {attempt + 1} 次嘗試失敗，正在重試...")
                time.sleep(2)  # 等待2秒後重試
            else:
                print(f"帳號 {username} 導向失敗（已重試 {max_retries} 次）: {e}")


def close_browser(browser_number, driver):
    """關閉指定的瀏覽器"""
    if driver is None:
        return
        
    try:
        driver.quit()
        print(f"瀏覽器 {browser_number} 已關閉")
    except Exception as e:
        # 忽略常見的無害關閉錯誤
        error_message = str(e)
        if "Remote end closed connection" in error_message or "chrome not reachable" in error_message.lower():
            pass
        else:
            print(f"關閉瀏覽器 {browser_number} 時發生錯誤: {e}")


if __name__ == "__main__":
    """主程式函數"""
    # 獲取 ChromeDriver 路徑
    driver_path = get_chromedriver_path()

    # 讀取用戶帳密資料
    user_credentials = load_user_credentials()
    if not user_credentials:
        print("無法讀取用戶資料，程式終止")
        exit(1)

    drivers = []
    base_port = 9222  # 起始端口

    # TODO: 依序啟動瀏覽器以避免衝突
    for i in range(12):
        port_number = base_port + i  # 依序端口：9222, 9223, 9224, 9225
        
        print(f"建立瀏覽器 {i+1}: 端口({port_number})")
        
        try:
            driver = create_browser(driver_path ,port_number)
            drivers.append(driver)
            time.sleep(1)  # 添加小延遲避免衝突
        except Exception as e:
            drivers.append(None)  # 即使失敗也要添加佔位符

    # 建立線程列表
    threads = []

    # 為每個瀏覽器建立獨立的線程
    for i, driver in enumerate(drivers):
        thread = threading.Thread(target=navigate_to_JFW, args=(driver, i+1, user_credentials))
        threads.append(thread)
        thread.start()

    # 等待所有線程完成
    for thread in threads:
        thread.join()

    input("按 Enter 鍵關閉所有瀏覽器...")

    # 建立線程列表用於關閉瀏覽器
    close_threads = []

    # 為每個瀏覽器建立獨立的關閉線程
    for i, driver in enumerate(drivers):
        thread = threading.Thread(args=(driver, i+1), target=close_browser)
        close_threads.append(thread)
        thread.start()

    # 等待所有關閉線程完成
    for thread in close_threads:
        thread.join()

    print("所有瀏覽器已關閉")
