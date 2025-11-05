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
    
    try:
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
    
    except:
        print(f"找不到用戶資料文件: {userinfo_path}")
        return []

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

# 獲取螢幕大小
screen_width, screen_height = get_screen_size()
print(f"螢幕大小: {screen_width} x {screen_height}")

# 讀取用戶帳密資料
user_credentials = load_user_credentials()
if not user_credentials:
    print("無法讀取用戶資料，程式終止")
    exit(1)

# 計算每個瀏覽器的寬度（平均分配4個）和高度（螢幕上方1/3）
browser_width = screen_width // 4
browser_height = screen_height // 3  # 改為螢幕高度的1/3

print("正在依序開啟4個瀏覽器...")

# 建立4個瀏覽器實例（依序啟動以避免衝突）
drivers = []
base_port = 9222  # 起始端口

# TODO: 依序啟動瀏覽器以避免衝突
for i in range(4):
    x_position = i * browser_width
    y_position = 0
    port_number = base_port + i  # 依序端口：9222, 9223, 9224, 9225
    
    print(f"建立瀏覽器 {i+1}: 位置({x_position}, {y_position}), 大小({browser_width} x {browser_height}), 端口({port_number})")
    
    try:
        driver = create_browser(x_position, y_position, browser_width, browser_height, port_number)
        drivers.append(driver)
        print(f"瀏覽器 {i+1} 建立完成")
        time.sleep(1)  # 添加小延遲避免衝突
    except Exception as e:
        print(f"瀏覽器 {i+1} 建立失敗: {e}")
        drivers.append(None)  # 即使失敗也要添加佔位符

print("所有瀏覽器已建立完成")

# 讓所有瀏覽器同時導向目標網站
print("正在同時導向目標網站...")

def navigate_to_aws(driver, browser_number, credentials):
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
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"瀏覽器 {browser_number} 嘗試第 {attempt + 1} 次連接...")
            driver.get("https://m.jfw-win.com/#/home/page")
            print(f"瀏覽器 {browser_number} 成功導向目標網站")
            
            # 等待頁面載入完成並尋找目標元素
            try:
                # 使用 WebDriverWait 等待元素出現
                wait = WebDriverWait(driver, 30)  # 最多等待30秒
                
                # 使用 fullxpath 找尋目標元素並點擊
                target_xpath = "/html/body/div[2]/div[3]/div/section/div/main/div[1]/div[2]/img"
                print(f"瀏覽器 {browser_number} 正在等待目標元素出現...")
                
                # 等待元素可點擊
                element = wait.until(EC.element_to_be_clickable((By.XPATH, target_xpath)))
                
                print(f"瀏覽器 {browser_number} 找到目標元素，正在點擊...")
                element.click()
                print(f"瀏覽器 {browser_number} 成功點擊目標元素")
                
                # 等待一下讓頁面載入
                time.sleep(3)
                
                # 開始登入流程
                print(f"瀏覽器 {browser_number} 開始登入流程，使用帳號: {username}")
                
                # 1. 輸入帳號
                username_xpath = "/html/body/div[2]/main/div/div[2]/div/div[3]/div[1]/div/div/div/div/input"
                print(f"瀏覽器 {browser_number} 正在尋找帳號輸入框...")
                username_element = wait.until(EC.element_to_be_clickable((By.XPATH, username_xpath)))
                username_element.clear()  # 清空輸入框
                username_element.send_keys(username)
                print(f"瀏覽器 {browser_number} 已輸入帳號: {username}")
                
                # 2. 輸入密碼
                password_xpath = "/html/body/div[2]/main/div/div[2]/div/div[3]/div[2]/div/div/div/div/input"
                print(f"瀏覽器 {browser_number} 正在尋找密碼輸入框...")
                password_element = wait.until(EC.element_to_be_clickable((By.XPATH, password_xpath)))
                password_element.clear()  # 清空輸入框
                password_element.send_keys(password)
                print(f"瀏覽器 {browser_number} 已輸入密碼")
                
                # 等待一下讓頁面穩定
                time.sleep(2)
                print(f"瀏覽器 {browser_number} 等待頁面穩定...")
                
                # 等待任何覆蓋層消失
                try:
                    print(f"瀏覽器 {browser_number} 等待覆蓋層消失...")
                    overlay_wait = WebDriverWait(driver, 10)
                    # 等待覆蓋層不可見
                    overlay_wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".van-overlay")))
                    print(f"瀏覽器 {browser_number} 覆蓋層已消失")
                except Exception as overlay_error:
                    print(f"瀏覽器 {browser_number} 等待覆蓋層消失時發生錯誤（可能本來就沒有覆蓋層）: {overlay_error}")
                
                # 3. 點擊登入按鈕
                login_button_xpath = "/html/body/div[2]/main/div/div[2]/div/div[3]/div[4]/div[1]"
                print(f"瀏覽器 {browser_number} 正在尋找登入按鈕...")
                
                # 增加額外等待確保按鈕完全可點擊
                login_wait = WebDriverWait(driver, 15)
                login_button = login_wait.until(EC.element_to_be_clickable((By.XPATH, login_button_xpath)))
                
                # 使用JavaScript點擊以避免覆蓋層問題
                try:
                    driver.execute_script("arguments[0].click();", login_button)
                    print(f"瀏覽器 {browser_number} 已點擊登入按鈕（使用JavaScript）")
                except Exception as js_click_error:
                    print(f"瀏覽器 {browser_number} JavaScript點擊失敗，嘗試普通點擊: {js_click_error}")
                    login_button.click()
                    print(f"瀏覽器 {browser_number} 已點擊登入按鈕（普通點擊）")
                
                # 4. 等待第一個公告出現並關閉
                print(f"瀏覽器 {browser_number} 等待第一個公告出現...")
                time.sleep(5)  # 等待5秒讓公告出現
                
                try:
                    # 尋找第一個公告關閉按鈕
                    announcement_close_xpath = "/html/body/div[2]/main/div/div[2]/div/div[3]/div[6]/div/div[3]/div[2]/div[1]"
                    print(f"瀏覽器 {browser_number} 正在尋找第一個公告關閉按鈕...")
                    announcement_close_button = wait.until(EC.element_to_be_clickable((By.XPATH, announcement_close_xpath)))
                    announcement_close_button.click()
                    print(f"瀏覽器 {browser_number} 已關閉第一個公告")
                except Exception as announcement_error:
                    print(f"瀏覽器 {browser_number} 關閉第一個公告失敗（可能公告未出現）: {announcement_error}")
                
                # 5. 等待第二個公告出現並關閉（第一次）
                print(f"瀏覽器 {browser_number} 等待第二個公告出現...")
                time.sleep(5)  # 等待5秒讓第二個公告出現
                
                try:
                    # 尋找第二個公告關閉按鈕（第一次）
                    second_announcement_xpath = "/html/body/div[2]/div[3]/div/section/div/main/div[6]/div[2]/img"
                    print(f"瀏覽器 {browser_number} 正在尋找第二個公告關閉按鈕（第一次）...")
                    second_announcement_button = wait.until(EC.element_to_be_clickable((By.XPATH, second_announcement_xpath)))
                    second_announcement_button.click()
                    print(f"瀏覽器 {browser_number} 已關閉第二個公告（第一次）")
                except Exception as second_announcement_error:
                    print(f"瀏覽器 {browser_number} 關閉第二個公告失敗（第一次，可能公告未出現）: {second_announcement_error}")
                
                # 6. 等待第二個公告再次出現並關閉（第二次）
                print(f"瀏覽器 {browser_number} 等待第二個公告再次出現...")
                time.sleep(3)  # 等待3秒讓第二個公告再次出現
                
                try:
                    # 尋找第二個公告關閉按鈕（第二次）
                    print(f"瀏覽器 {browser_number} 正在尋找第二個公告關閉按鈕（第二次）...")
                    second_announcement_button_2 = wait.until(EC.element_to_be_clickable((By.XPATH, second_announcement_xpath)))
                    second_announcement_button_2.click()
                    print(f"瀏覽器 {browser_number} 已關閉第二個公告（第二次）")
                except Exception as second_announcement_error_2:
                    print(f"瀏覽器 {browser_number} 關閉第二個公告失敗（第二次，可能公告未出現）: {second_announcement_error_2}")
                
                # 7. 等待第二個公告第三次出現並關閉（第三次）
                print(f"瀏覽器 {browser_number} 等待第二個公告第三次出現...")
                time.sleep(3)  # 等待3秒讓第二個公告第三次出現
                
                try:
                    # 尋找第二個公告關閉按鈕（第三次）
                    print(f"瀏覽器 {browser_number} 正在尋找第二個公告關閉按鈕（第三次）...")
                    second_announcement_button_3 = wait.until(EC.element_to_be_clickable((By.XPATH, second_announcement_xpath)))
                    second_announcement_button_3.click()
                    print(f"瀏覽器 {browser_number} 已關閉第二個公告（第三次）")
                except Exception as second_announcement_error_3:
                    print(f"瀏覽器 {browser_number} 關閉第二個公告失敗（第三次，可能公告未出現）: {second_announcement_error_3}")
                
                # 8. 進入金富翁大廳
                print(f"瀏覽器 {browser_number} 進入金富翁大廳完成")
                
                # 9. 點擊開啟所有遊戲運營商
                print(f"瀏覽器 {browser_number} 準備開啟所有遊戲運營商...")
                time.sleep(2)  # 等待2秒讓頁面穩定
                
                try:
                    # 點擊遊戲運營商按鈕
                    game_provider_xpath = "/html/body/div[2]/div[3]/div/section/div/main/div[3]/div[1]/div/div[2]/img"
                    print(f"瀏覽器 {browser_number} 正在尋找遊戲運營商按鈕...")
                    game_provider_button = wait.until(EC.element_to_be_clickable((By.XPATH, game_provider_xpath)))
                    game_provider_button.click()
                    print(f"瀏覽器 {browser_number} 已點擊開啟所有遊戲運營商")
                except Exception as game_provider_error:
                    print(f"瀏覽器 {browser_number} 點擊遊戲運營商失敗: {game_provider_error}")
                
                # 10. 尋找並點擊ATG運營商
                print(f"瀏覽器 {browser_number} 準備尋找ATG運營商...")
                time.sleep(3)  # 等待3秒讓運營商列表載入
                
                try:
                    # 尋找包含"ATG"文字的運營商
                    print(f"瀏覽器 {browser_number} 正在尋找ATG運營商...")
                    
                    # 使用XPath尋找包含ATG文字的div元素
                    atg_xpath = "//div[contains(@class, 'tablabel') and text()='ATG']"
                    atg_element = wait.until(EC.element_to_be_clickable((By.XPATH, atg_xpath)))
                    
                    # 點擊ATG運營商（點擊整個容器）
                    atg_container = atg_element.find_element(By.XPATH, "..")  # 獲取父元素（整個inner-item容器）
                    atg_container.click()
                    print(f"瀏覽器 {browser_number} 已點擊ATG運營商")
                    
                except Exception as atg_error:
                    print(f"瀏覽器 {browser_number} 點擊ATG運營商失敗: {atg_error}")
                    # 如果第一種方法失敗，嘗試直接點擊包含ATG的任何元素
                    try:
                        print(f"瀏覽器 {browser_number} 嘗試備用方法尋找ATG...")
                        atg_alternative = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'ATG')]")))
                        atg_alternative.click()
                        print(f"瀏覽器 {browser_number} 已使用備用方法點擊ATG運營商")
                    except Exception as atg_alternative_error:
                        print(f"瀏覽器 {browser_number} 備用方法也失敗: {atg_alternative_error}")
                
                # 11. 點擊遊戲選單
                print(f"瀏覽器 {browser_number} 準備點擊遊戲選單...")
                time.sleep(3)  # 等待3秒讓ATG遊戲列表載入
                
                try:
                    # 點擊指定的遊戲選單
                    game_menu_xpath = "/html/body/div[2]/div[3]/div/section/div/main/div[3]/div[2]/div/div/div[1]/div[2]/div/div[2]/div/img"
                    print(f"瀏覽器 {browser_number} 正在尋找遊戲選單...")
                    game_menu_element = wait.until(EC.element_to_be_clickable((By.XPATH, game_menu_xpath)))
                    game_menu_element.click()
                    print(f"瀏覽器 {browser_number} 已點擊遊戲選單")
                except Exception as game_menu_error:
                    print(f"瀏覽器 {browser_number} 點擊遊戲選單失敗: {game_menu_error}")
                
                # 12. 點擊遊玩按鈕
                print(f"瀏覽器 {browser_number} 準備點擊遊玩按鈕...")
                time.sleep(2)  # 等待2秒讓遊戲詳情載入
                
                try:
                    # 點擊遊玩按鈕
                    play_button_xpath = "/html/body/div[2]/div[3]/div/section/div/main/div[3]/div[2]/div/div/div[1]/div[2]/div[3]/div[3]"
                    print(f"瀏覽器 {browser_number} 正在尋找遊玩按鈕...")
                    play_button_element = wait.until(EC.element_to_be_clickable((By.XPATH, play_button_xpath)))
                    play_button_element.click()
                    print(f"瀏覽器 {browser_number} 已點擊遊玩按鈕")
                except Exception as play_button_error:
                    print(f"瀏覽器 {browser_number} 點擊遊玩按鈕失敗: {play_button_error}")
                
                print(f"瀏覽器 {browser_number} 登入流程完成")
                
            except Exception as click_error:
                print(f"瀏覽器 {browser_number} 操作失敗: {click_error}")
            
            return  # 成功後退出函數
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"瀏覽器 {browser_number} 第 {attempt + 1} 次嘗試失敗，正在重試...")
                time.sleep(2)  # 等待2秒後重試
            else:
                print(f"瀏覽器 {browser_number} 導向失敗（已重試 {max_retries} 次）: {e}")

# 建立線程列表
threads = []

# 為每個瀏覽器建立獨立的線程
for i, driver in enumerate(drivers):
    thread = threading.Thread(target=navigate_to_aws, args=(driver, i+1, user_credentials))
    threads.append(thread)
    thread.start()

# 等待所有線程完成
for thread in threads:
    thread.join()

print("所有瀏覽器已導向目標網站")
input("按 Enter 鍵關閉所有瀏覽器...")

# 同時關閉所有瀏覽器
def close_browser(driver, browser_number):
    """關閉指定的瀏覽器"""
    if driver is None:
        print(f"瀏覽器 {browser_number} 未成功建立，跳過關閉")
        return
        
    try:
        driver.quit()
        print(f"瀏覽器 {browser_number} 已關閉")
    except Exception as e:
        # 忽略常見的無害關閉錯誤
        error_message = str(e)
        if "Remote end closed connection" in error_message or "chrome not reachable" in error_message.lower():
            print(f"瀏覽器 {browser_number} 已關閉")  # 實際上已經關閉了
        else:
            print(f"關閉瀏覽器 {browser_number} 時發生錯誤: {e}")

# 建立線程列表用於關閉瀏覽器
close_threads = []

# 為每個瀏覽器建立獨立的關閉線程
for i, driver in enumerate(drivers):
    thread = threading.Thread(target=close_browser, args=(driver, i+1))
    close_threads.append(thread)
    thread.start()

# 等待所有關閉線程完成
for thread in close_threads:
    thread.join()

print("所有瀏覽器已關閉")
