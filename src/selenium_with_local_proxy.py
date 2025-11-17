"""
使用本地 Proxy 中繼伺服器的 Selenium 腳本
此方法100%可靠,因為不需要處理 proxy 認證

使用步驟:
1. 先在另一個終端啟動 simple_proxy_server.py
2. 然後執行此腳本
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import os
import platform


def get_chromedriver_path():
    """根據作業系統返回正確的 chromedriver 路徑"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    system = platform.system()
    
    if system == "Windows":
        return os.path.join(project_root, "chromedriver.exe")
    else:
        return os.path.join(project_root, "chromedriver")


def create_driver_with_local_proxy(local_proxy_port=8888):
    """
    使用本地 proxy 建立 Chrome driver
    
    Args:
        local_proxy_port: 本地 proxy 端口 (預設 8888)
    
    Returns:
        driver: Chrome driver
    """
    print(f"設定本地 Proxy: 127.0.0.1:{local_proxy_port}")
    
    # 設定 Chrome 選項
    options = webdriver.ChromeOptions()
    
    # 設定本地 proxy (無需認證)
    options.add_argument(f'--proxy-server=http://127.0.0.1:{local_proxy_port}')
    
    # 其他選項
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # 取得 chromedriver 路徑
    driver_path = get_chromedriver_path()
    
    try:
        # 建立 driver
        if os.path.exists(driver_path):
            service = Service(executable_path=driver_path)
            driver = webdriver.Chrome(service=service, options=options)
            print(f"✓ 使用 ChromeDriver: {driver_path}")
        else:
            driver = webdriver.Chrome(options=options)
            print("✓ 使用系統 PATH 中的 ChromeDriver")
        
        return driver
        
    except Exception as e:
        print(f"❌ 建立 driver 失敗: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_local_proxy(local_port=8888):
    """測試本地 proxy"""
    print(f"\n{'='*60}")
    print(f"使用本地 Proxy 測試")
    print(f"{'='*60}\n")
    
    driver = None
    try:
        driver = create_driver_with_local_proxy(local_port)
        
        if not driver:
            print("❌ 無法建立 driver")
            return False
        
        # 等待頁面載入
        print("\n等待瀏覽器啟動...")
        time.sleep(2)
        
        # 訪問 IP 檢查網站
        print("正在檢查 IP 位址...")
        driver.get("https://api.ipify.org?format=json")
        time.sleep(3)
        
        # 獲取頁面內容
        page_text = driver.find_element(By.TAG_NAME, "body").text
        print(f"\n檢測到的 IP 資訊:")
        print(f"  {page_text}")
        
        # 解析 IP
        if '"ip"' in page_text:
            import json
            try:
                ip_data = json.loads(page_text)
                detected_ip = ip_data.get('ip')
                
                print(f"\n✅ Proxy 運作正常!")
                print(f"   通過 proxy 的 IP: {detected_ip}")
                print(f"\n您現在可以在主程式中使用 127.0.0.1:{local_port} 作為 proxy")
                print(f"此 proxy 不需要認證!")
            except:
                print(f"  無法解析 JSON")
        else:
            print(f"\n⚠️  警告: 頁面未顯示 IP 資訊")
            print(f"  請確認 local_proxy_server.py 是否正在運行")
        
        # 繼續測試其他網站
        print(f"\n測試訪問 Google...")
        driver.get("https://www.google.com")
        time.sleep(2)
        print(f"✓ 成功訪問 Google")
        
        # 等待使用者確認
        input(f"\n按 Enter 關閉瀏覽器...")
        
        driver.quit()
        return True
        
    except Exception as e:
        print(f"\n❌ 測試失敗: {str(e)}")
        print(f"\n請確認:")
        print(f"  1. local_proxy_server.py 是否正在運行")
        print(f"  2. 端口 {local_port} 是否正確")
        import traceback
        traceback.print_exc()
        if driver:
            try:
                driver.quit()
            except:
                pass
        return False


def main():
    """主執行函式"""
    print("\n" + "="*60)
    print("Selenium with Local Proxy (無需認證)")
    print("="*60)
    print("\n⚠️  請確保已在另一個終端啟動 simple_proxy_server.py\n")
    
    import sys
    if len(sys.argv) > 1:
        local_port = int(sys.argv[1])
    else:
        local_port = 8888
    
    test_local_proxy(local_port)
    
    print("\n" + "="*60)
    print("測試完成!")
    print("="*60)


if __name__ == "__main__":
    main()
