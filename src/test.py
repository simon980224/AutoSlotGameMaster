from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
# import threading
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
        print("[錯誤] 瀏覽器未成功建立，跳過操作")
        return
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"[帳號 {username}] 正在導向登入頁面...")
            driver.get("https://m.jfw-win.com/#/login?redirect=%2Fhome%2Fpage")
            
            wait = WebDriverWait(driver, 30)
            time.sleep(3)
            
            # === 步驟 2: 輸入帳號 ===
            print(f"[帳號 {username}] ⏳ 輸入帳號...")
            username_xpath = "/html/body/div[2]/main/div/div[2]/div/div[3]/div[1]/div/div/div/div/input"
            username_element = driver.find_element(By.XPATH, username_xpath)
            username_element.send_keys(username)
            
            # === 步驟 3: 輸入密碼 ===
            print(f"[帳號 {username}] ⏳ 輸入密碼...")
            password_xpath = "/html/body/div[2]/main/div/div[2]/div/div[3]/div[2]/div/div/div/div/input"
            password_element = driver.find_element(By.XPATH, password_xpath)
            password_element.send_keys(password)
            
            # === 步驟 4: 點擊登入按鈕 ===
            print(f"[帳號 {username}] ⏳ 執行登入...")
            login_button_xpath = "/html/body/div[2]/main/div/div[2]/div/div[3]/div[4]/div[1]"
            login_button = driver.find_element(By.XPATH, login_button_xpath)
            login_button.click()
            time.sleep(1)

            # === 檢查是否登入失敗 ===
            try:
                error_message_xpath = "/html/body/div[3]/div[2]/div/div[3]/span"
                error_message_element = driver.find_element(By.XPATH, error_message_xpath)
                if error_message_element.text == "帳號密碼錯誤":
                    print(f"[帳號 {username}] ❌ 登入失敗：帳號密碼錯誤")
                    return
            except:
                pass
            
            # === 處理登入公告 ===
            print(f"[帳號 {username}] 處理登入公告...")
            try:
                login_announcement_close_xpath = "/html/body/div[2]/main/div/div[2]/div/div[3]/div[6]/div/div[3]/div[2]/div[1]"
                login_announcement_close_button = wait.until(EC.element_to_be_clickable((By.XPATH, login_announcement_close_xpath)))
                login_announcement_close_button.click()
            except:
                pass

            # === 處理大廳公告 ===
            print(f"[帳號 {username}] 處理大廳公告...")
            lobby_announcement_xpath = "/html/body/div[2]/div[3]/div/section/div/main/div[6]/div[2]/img"
            announcement_count = 0
            while announcement_count < 10:
                try:
                    lobby_announcement_button = wait.until(EC.element_to_be_clickable((By.XPATH, lobby_announcement_xpath)))
                    lobby_announcement_button.click()
                    announcement_count += 1
                    time.sleep(1)
                except:
                    break

            print(f"[帳號 {username}] 成功進入大廳")
            time.sleep(1)
            
            # === 點擊遊戲運營商選單 ===
            try:
                print(f"[帳號 {username}] 開啟遊戲運營商選單...")
                game_provider_xpath = "/html/body/div[2]/div[3]/div/section/div/main/div[3]/div[1]/div/div[2]/img"
                game_provider_button = wait.until(EC.element_to_be_clickable((By.XPATH, game_provider_xpath)))
                game_provider_button.click()
            except Exception as e:
                print(f"[錯誤] 無法開啟運營商選單: {e}")
            
            time.sleep(1)
            
            # === 選擇 ATG 運營商 ===
            try:
                print(f"[帳號 {username}] 選擇 ATG 運營商...")
                atg_xpath = "//div[contains(@class, 'tablabel') and text()='ATG']"
                atg_element = wait.until(EC.element_to_be_clickable((By.XPATH, atg_xpath)))
                atg_element.find_element(By.XPATH, "..").click()
            except Exception as e:
                print(f"[錯誤] 無法選擇 ATG 運營商: {e}")
            
            time.sleep(1)
            
            # === 選擇賽特遊戲 ===
            try:
                print(f"[帳號 {username}] 選擇賽特遊戲...")
                sett_game_xpath = "/html/body/div[2]/div[3]/div/section/div/main/div[3]/div[2]/div/div/div[1]/div[2]/div/div[2]/div/img"
                sett_game_element = wait.until(EC.element_to_be_clickable((By.XPATH, sett_game_xpath)))
                sett_game_element.click()
            except Exception as e:
                print(f"[錯誤] 無法選擇賽特遊戲: {e}")
            
            time.sleep(1)
            
            # === 點擊遊玩按鈕 ===
            try:
                print(f"[帳號 {username}] 啟動遊戲...")
                sett_game_play_button_xpath = "/html/body/div[2]/div[3]/div/section/div/main/div[3]/div[2]/div/div/div[1]/div[2]/div[3]/div[3]"
                sett_game_play_button_element = wait.until(EC.element_to_be_clickable((By.XPATH, sett_game_play_button_xpath)))
                sett_game_play_button_element.click()
            except Exception as e:
                print(f"[錯誤] 無法點擊遊玩按鈕: {e}")
            
            print(f"[帳號 {username}] ✓ 成功進入賽特遊戲")
            return
        
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"[警告] 帳號 {username} 第 {attempt + 1} 次嘗試失敗，1 秒後重試...")
                time.sleep(1)
            else:
                print(f"[錯誤] 帳號 {username} 操作失敗（已重試 {max_retries} 次）: {e}")


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
        print("[錯誤] 瀏覽器實例不存在，無法執行遊戲操作")
        return
    
    print(f"[系統] 收到指令：{command}")
    print("[系統] （指令功能尚未實作）")
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
        # 忽略正常關閉時的無害錯誤訊息
        error_message = str(e)
        if "Remote end closed connection" not in error_message and "chrome not reachable" not in error_message.lower():
            print(f"[警告] 關閉瀏覽器時發生錯誤: {e}")


def main():
    """
    主程式入口：
    1. 由使用者輸入要啟動的瀏覽器數量。
    2. 根據數量依序啟動瀏覽器、登入金富翁網站並進入遊戲。
    3. 等待使用者輸入操作指令。
       - 若輸入 'q' 則關閉所有瀏覽器並結束程式。
    """
    print("=== 金富翁自動化登入與操作系統 ===")
    
    # 讀取帳號資料
    credentials = load_user_credentials()
    if not credentials:
        print("[錯誤] 無法讀取 user_credentials.txt 或內容為空。")
        return
    
    # 讓使用者輸入要開幾個瀏覽器
    while True:
        try:
            browser_count = int(input("請輸入要啟動的瀏覽器數量 (1~20)："))
            if 1 <= browser_count <= min(20, len(credentials)):
                break
            else:
                print(f"[警告] 請輸入介於 1 到 {min(20, len(credentials))} 的整數。")
        except ValueError:
            print("[錯誤] 請輸入有效的整數。")
    
    # 取得 chromedriver 路徑
    driver_path = get_chromedriver_path()
    
    # 建立並啟動瀏覽器
    drivers = []
    for i in range(browser_count):
        username = credentials[i]["username"]
        password = credentials[i]["password"]
        print(f"\n[系統] 啟動第 {i+1} 個瀏覽器（帳號：{username}）...")
        driver = create_browser(driver_path)
        # navigate_to_JFW(driver, username, password) # TODO暫時註解掉測試用
        drivers.append(driver)
        time.sleep(1)
    
    print("\n[系統] 所有瀏覽器已啟動並登入成功。")
    
    # 操作階段
    while True:
        command = input("\n請輸入指令：").strip().lower()
        if command == "q":
            print("[系統] 收到退出指令，開始關閉所有瀏覽器...")
            for driver in drivers:
                close_browser(driver)
            print("[系統] 所有瀏覽器已關閉，程式結束。")
            break

if __name__ == "__main__":
    main()