from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import threading
import pyautogui

# 設定 ChromeDriver 路徑
driver_path = "/Users/chenyaoxuan/Desktop/chromedriver"
service = Service(driver_path)

def get_screen_size():
    """使用 pyautogui 獲取螢幕大小"""
    screen_width, screen_height = pyautogui.size()
    return screen_width, screen_height

def create_browser(x_position, y_position, width, height, port_number):
    """建立瀏覽器並設定位置、大小和依序端口"""
    chrome_options = Options()
    chrome_options.add_argument(f"--window-position={x_position},{y_position}")
    chrome_options.add_argument(f"--window-size={width},{height}")
    # 添加穩定性選項
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument(f"--remote-debugging-port={port_number}")  # 使用依序端口
    
    driver = webdriver.Chrome(service=service, options=chrome_options)
    # 設置更長的超時時間
    driver.set_page_load_timeout(300)  # 5分鐘超時
    driver.implicitly_wait(30)  # 30秒隱式等待
    return driver

# 獲取螢幕大小
screen_width, screen_height = get_screen_size()
print(f"螢幕大小: {screen_width} x {screen_height}")

# 計算每個瀏覽器的寬度（平均分配4個）和高度（螢幕上方1/3）
browser_width = screen_width // 4
browser_height = screen_height // 3  # 改為螢幕高度的1/3

print("正在同時開啟4個瀏覽器...")

def create_browser_thread(browser_number, x_position, y_position, width, height, port_number, drivers_list):
    """建立瀏覽器的線程函數"""
    print(f"建立瀏覽器 {browser_number}: 位置({x_position}, {y_position}), 大小({width} x {height}), 端口({port_number})")
    driver = create_browser(x_position, y_position, width, height, port_number)
    drivers_list.append((browser_number - 1, driver))  # 儲存索引和driver
    print(f"瀏覽器 {browser_number} 建立完成")

# 建立4個瀏覽器實例（同時啟動）
drivers = [None] * 4  # 預先建立固定大小的列表
drivers_list = []
browser_threads = []
base_port = 9222  # 起始端口

for i in range(4):
    x_position = i * browser_width
    y_position = 0
    port_number = base_port + i  # 依序端口：9222, 9223, 9224, 9225
    
    thread = threading.Thread(target=create_browser_thread, args=(i+1, x_position, y_position, browser_width, browser_height, port_number, drivers_list))
    browser_threads.append(thread)
    thread.start()

# 等待所有瀏覽器建立完成
for thread in browser_threads:
    thread.join()

# 將driver按順序放入drivers列表
for index, driver in drivers_list:
    drivers[index] = driver

print("所有瀏覽器已同時建立完成")

print("初始化完畢")
input("按任意鍵後所有瀏覽器將導向 AWS 網站...")

# 讓所有瀏覽器同時導向 AWS 網站
print("正在同時導向 AWS 網站...")

def navigate_to_aws(driver, browser_number):
    """讓指定的瀏覽器導向 AWS 網站"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"瀏覽器 {browser_number} 嘗試第 {attempt + 1} 次連接...")
            driver.get("https://aws.amazon.com/tw/")
            print(f"瀏覽器 {browser_number} 成功導向 AWS")
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
    thread = threading.Thread(target=navigate_to_aws, args=(driver, i+1))
    threads.append(thread)
    thread.start()

# 等待所有線程完成
for thread in threads:
    thread.join()

print("所有瀏覽器已導向 AWS 網站")
input("按 Enter 鍵關閉所有瀏覽器...")

# 同時關閉所有瀏覽器
def close_browser(driver, browser_number):
    """關閉指定的瀏覽器"""
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
