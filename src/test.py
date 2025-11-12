"""
金富翁遊戲自動化系統

此模組提供完整的自動化流程，包括：
- 多帳號批次登入
- 瀏覽器視窗管理
- 遊戲自動操作
- 執行緒安全的狀態控制
"""

from __future__ import annotations

import base64
import io
import logging
import os
import platform
import threading
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By



# ==================== 常量定義 ====================

class GameCommand(Enum):
    """遊戲控制指令列舉"""
    CONTINUE = 'c'
    PAUSE = 'p'
    QUIT = 'q'
    BET_SIZE = 'b'  # 調整下注金額
    BUY_FREE_GAME = 'f'  # 購買免費遊戲


@dataclass
class WindowConfig:
    """視窗配置"""
    width: int = 600
    height: int = 400
    columns: int = 4  # 每行視窗數
    rows: int = 3     # 每列視窗數


@dataclass
class GameConfig:
    """遊戲配置"""
    max_accounts: int = 12
    key_interval: int = 15  # 按鍵間隔秒數
    page_load_timeout: int = 600  # 頁面載入超時（秒）- 提高到 10 分鐘
    script_timeout: int = 600  # 腳本執行超時（秒）- 10 分鐘
    implicit_wait: int = 60  # 隱式等待（秒）- 提高到 60 秒
    explicit_wait: int = 10  # 顯式等待（秒）- 提高到 10 秒
    image_detect_timeout: int = 180  # 圖片檢測超時秒數 - 提高到 3 分鐘
    image_detect_interval: float = 0.5  # 圖片檢測間隔秒數
    image_match_threshold: float = 0.8  # 圖片匹配閾值


# 元素選擇器常量
class ElementSelector:
    """頁面元素選擇器定義"""
    USERNAME_INPUT = "//input[@placeholder='請輸入帳號']"
    PASSWORD_INPUT = "//input[@placeholder='請輸入密碼']"
    LOGIN_BUTTON = "//div[contains(@class, 'login-btn')]//span[text()='立即登入']/.."


# 鍵盤按鍵常量
class KeyboardKey:
    """鍵盤按鍵屬性定義"""
    # 空白鍵
    SPACE = {
        "key": " ",
        "code": "Space",
        "windowsVirtualKeyCode": 32,
        "nativeVirtualKeyCode": 32
    }
    
    # 左方向鍵（減少金額）
    ARROW_LEFT = {
        "key": "ArrowLeft",
        "code": "ArrowLeft",
        "windowsVirtualKeyCode": 37,
        "nativeVirtualKeyCode": 37
    }
    
    # 右方向鍵（增加金額）
    ARROW_RIGHT = {
        "key": "ArrowRight",
        "code": "ArrowRight",
        "windowsVirtualKeyCode": 39,
        "nativeVirtualKeyCode": 39
    }


# 點擊座標常量
class ClickCoordinate:
    """遊戲中需要點擊的座標位置"""
    START_GAME_X = 600
    START_GAME_Y = 620
    MACHINE_CONFIRM_X = 850
    MACHINE_CONFIRM_Y = 550
    FREE_GAME_X = 250
    FREE_GAME_Y = 500
    
    # Betsize 顯示區域
    BETSIZE_DISPLAY_LEFT = 750
    BETSIZE_DISPLAY_TOP = 554
    BETSIZE_DISPLAY_RIGHT = 850
    BETSIZE_DISPLAY_BOTTOM = 600


# URL 常量
class URL:
    """網站 URL 定義"""
    LOGIN_PAGE = "https://m.jfw-win.com/#/login?redirect=%2Fhome%2Fpage"
    GAME_PAGE = "https://m.jfw-win.com/#/home/loding?game_code=egyptian-mythology&factory_code=ATG&state=true&name=%E6%88%B0%E7%A5%9E%E8%B3%BD%E7%89%B9"


# 圖片路徑常量
class ImagePath:
    """圖片路徑定義"""
    @staticmethod
    def get_image_path(filename: str) -> str:
        """取得圖片完整路徑"""
        current_dir = Path(__file__).resolve().parent
        project_root = current_dir.parent
        return str(project_root / "img" / filename)
    
    @staticmethod
    def lobby_login() -> str:
        """大廳登入圖片"""
        return ImagePath.get_image_path("lobby_login.png")
    
    @staticmethod
    def lobby_confirm() -> str:
        """大廳確認圖片"""
        return ImagePath.get_image_path("lobby_confirm.png")
    
    @staticmethod
    def bet_size_dir() -> str:
        """bet_size 資料夾路徑"""
        current_dir = Path(__file__).resolve().parent
        project_root = current_dir.parent
        return str(project_root / "img" / "bet_size")


# 遊戲倍率常量
GAME_BETSIZE = [ 0.4, 0.8, 1, 1.2, 1.6, 2, 2.4, 2.8, 3, 3.2, 3.6, 4, 5, 6, 7, 8, 9, 10, 12, 14, 16, 18, 20, 24, 28, 32, 36, 40, 48, 56, 60, 64, 72, 80, 100, 120, 140, 160, 180, 200, 240, 280, 300, 320, 360, 400, 420, 480, 500, 540, 560, 600, 640, 700, 720, 800, 840, 900, 960, 980, 1000, 1080, 1120, 1200, 1260, 1280, 1400, 1440, 1600, 1800, 2000]


# 全域配置實例
WINDOW_CONFIG = WindowConfig()
GAME_CONFIG = GameConfig()


# ==================== 日誌配置 ====================

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] [%(asctime)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


# ==================== 全域狀態管理 ====================

@dataclass
class GameState:
    """遊戲狀態資料類別"""
    running: bool = False
    thread: Optional[threading.Thread] = None


class GameStateManager:
    """執行緒安全的遊戲狀態管理器"""
    
    def __init__(self):
        self._states: Dict[WebDriver, GameState] = {}
        self._lock = threading.Lock()
    
    def set_running(self, driver: WebDriver, running: bool) -> None:
        """設定執行狀態"""
        with self._lock:
            if driver not in self._states:
                self._states[driver] = GameState()
            self._states[driver].running = running
    
    def set_thread(self, driver: WebDriver, thread: Optional[threading.Thread]) -> None:
        """設定執行緒"""
        with self._lock:
            if driver not in self._states:
                self._states[driver] = GameState()
            self._states[driver].thread = thread
    
    def is_running(self, driver: WebDriver) -> bool:
        """檢查是否正在執行"""
        with self._lock:
            return driver in self._states and self._states[driver].running
    
    def get_thread(self, driver: WebDriver) -> Optional[threading.Thread]:
        """取得執行緒"""
        with self._lock:
            if driver in self._states:
                return self._states[driver].thread
            return None
    
    def remove(self, driver: WebDriver) -> None:
        """移除狀態"""
        with self._lock:
            if driver in self._states:
                del self._states[driver]
    
    def cleanup_all(self) -> None:
        """清理所有狀態"""
        with self._lock:
            self._states.clear()


# 全域狀態管理器實例
game_state_manager = GameStateManager()


# ==================== 工具函式 ====================

def get_chromedriver_path() -> str:
    """
    取得 ChromeDriver 執行檔的完整路徑。
    
    根據作業系統自動選擇對應的執行檔名稱：
    - Windows: chromedriver.exe
    - macOS/Linux: chromedriver
    
    Returns:
        str: ChromeDriver 的完整路徑
    
    Raises:
        FileNotFoundError: 當 ChromeDriver 檔案不存在時
    """
    current_dir = Path(__file__).resolve().parent
    project_root = current_dir.parent
    
    system = platform.system().lower()
    driver_filename = "chromedriver.exe" if system == "windows" else "chromedriver"
    driver_path = project_root / driver_filename
    
    if not driver_path.exists():
        raise FileNotFoundError(f"找不到 ChromeDriver：{driver_path}")
    
    return str(driver_path)


def load_user_credentials() -> List[Dict[str, str]]:
    """
    從檔案讀取使用者帳號密碼資料。
    
    檔案格式：
    - 第一行為標題（會被跳過）
    - 每行格式：username:password
    - 最多讀取前 12 組帳號
    
    Returns:
        List[Dict[str, str]]: 帳號密碼列表，每項包含 'username' 和 'password' 鍵值
        
    Raises:
        FileNotFoundError: 當檔案不存在時
    """
    current_dir = Path(__file__).resolve().parent
    project_root = current_dir.parent
    credentials_path = project_root / "lib" / "user_credentials.txt"
    
    if not credentials_path.exists():
        raise FileNotFoundError(f"找不到帳號檔案：{credentials_path}")
    
    credentials = []
    
    with open(credentials_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for idx, line in enumerate(lines):
        # 跳過標題行
        if idx == 0:
            continue
        
        line = line.strip()
        if not line or ':' not in line:
            continue
        
        username, password = line.split(':', 1)
        credentials.append({
            'username': username.strip(),
            'password': password.strip()
        })
    
    total_count = len(credentials)
    
    if total_count == 0:
        logger.warning("帳號檔案內容為空或格式錯誤")
        return []
    
    # 限制最多 12 組帳號
    if total_count > GAME_CONFIG.max_accounts:
        logger.info(f"偵測到 {total_count} 組帳號，僅保留前 {GAME_CONFIG.max_accounts} 組")
        credentials = credentials[:GAME_CONFIG.max_accounts]
    else:
        logger.info(f"已載入 {total_count} 組帳號資料")
    
    return credentials


def create_chrome_options() -> Options:
    """
    建立並配置 Chrome 瀏覽器選項。
    
    配置項目包括：
    - 移除自動化控制標記
    - 禁用彈窗攔截
    - 禁用通知
    - 禁用密碼管理
    - 效能優化設定
    - 網路連線優化設定
    
    Returns:
        Options: 配置好的 Chrome 選項物件
    """
    chrome_options = Options()
    
    # 基本設定
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-popup-blocking")
    
    # 效能優化
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    
    # # 網路連線優化
    chrome_options.add_argument("--disable-features=NetworkTimeServiceQuerying")
    chrome_options.add_argument("--dns-prefetch-disable")  # 禁用 DNS 預取以減少網路請求
    chrome_options.add_argument("--disable-background-networking")  # 禁用背景網路活動
    chrome_options.add_argument("--disable-sync")  # 禁用同步
    chrome_options.add_argument("--metrics-recording-only")  # 僅記錄指標
    chrome_options.add_argument("--disable-default-apps")  # 禁用預設應用程式
    chrome_options.add_argument("--no-first-run")  # 跳過首次執行
    chrome_options.add_argument("--disable-extensions")  # 禁用擴充功能
    
    # 提高網路效能
    # chrome_options.add_argument("--disable-web-security")  # 禁用網路安全檢查（提高速度）
    # chrome_options.add_argument("--disk-cache-size=0")  # 禁用磁碟快取
    # chrome_options.add_argument("--aggressive-cache-discard")  # 積極丟棄快取
    # chrome_options.add_argument("--disable-application-cache")  # 禁用應用程式快取
    
    # 移除自動化痕跡
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # 偏好設定
    chrome_options.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_settings.popups": 0,
        "profile.default_content_setting_values.media_stream_mic": 2,
        "profile.default_content_setting_values.media_stream_camera": 2,
        "profile.default_content_setting_values.sound": 2,  # 靜音所有網站
        # 網路優化設定
        "profile.default_content_setting_values.automatic_downloads": 2,
        "download.prompt_for_download": False,
        "download_restrictions": 3,
    })
    
    return chrome_options


def create_webdriver(driver_path: str) -> Optional[WebDriver]:
    """
    建立 Chrome WebDriver 實例。
    
    Args:
        driver_path: ChromeDriver 執行檔路徑
        
    Returns:
        Optional[WebDriver]: WebDriver 實例，失敗時返回 None
    """
    try:
        service = Service(driver_path)
        chrome_options = create_chrome_options()
        
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 設定超時時間（使用更長的時間避免逾時）
        driver.set_page_load_timeout(GAME_CONFIG.page_load_timeout)
        driver.set_script_timeout(GAME_CONFIG.script_timeout)
        driver.implicitly_wait(GAME_CONFIG.implicit_wait)
        
        # 設定網路條件（移除頻寬限制）
        driver.execute_cdp_cmd("Network.enable", {})
        driver.execute_cdp_cmd("Network.emulateNetworkConditions", {
            "offline": False,
            "downloadThroughput": -1,  # 無限下載速度
            "uploadThroughput": -1,    # 無限上傳速度
            "latency": 0               # 零延遲
        })
        
        logger.info("已建立瀏覽器實例並優化網路設定")
        return driver
    except Exception as e:
        logger.error(f"建立瀏覽器失敗：{e}")
        return None


# ==================== 登入流程 ====================

def perform_login(driver: WebDriver, username: str, password: str) -> bool:
    """
    執行登入操作。
    
    Args:
        driver: WebDriver 實例
        username: 帳號
        password: 密碼
        
    Returns:
        bool: 登入成功返回 True，失敗返回 False
    """
    try:
        # 輸入帳號密碼
        driver.find_element(By.XPATH, ElementSelector.USERNAME_INPUT).send_keys(username)
        driver.find_element(By.XPATH, ElementSelector.PASSWORD_INPUT).send_keys(password)
        driver.find_element(By.XPATH, ElementSelector.LOGIN_BUTTON).click()
        
        time.sleep(5)
        
        return True
    except Exception as e:
        logger.error(f"[{username}] 登入過程發生錯誤：{e}")
        return False


def detect_image_on_screen(driver: WebDriver, template_path: str, threshold: float = 0.8) -> bool:
    """
    檢測瀏覽器視窗中是否出現指定圖片。
    
    使用模板匹配技術在螢幕截圖中尋找目標圖片。
    
    Args:
        driver: WebDriver 實例
        template_path: 模板圖片的完整路徑
        threshold: 匹配閾值 (0-1)，越接近 1 表示要求越精確
        
    Returns:
        bool: 找到圖片返回 True，否則返回 False
    """
    try:
        # 檢查模板圖片是否存在
        if not Path(template_path).exists():
            logger.error(f"模板圖片不存在：{template_path}")
            return False
        
        # 擷取瀏覽器視窗截圖
        screenshot = driver.get_screenshot_as_png()
        screenshot_np = np.array(Image.open(io.BytesIO(screenshot)))
        screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)
        
        # 讀取模板圖片
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        if template is None:
            logger.error(f"無法讀取模板圖片：{template_path}")
            return False
        
        # 執行模板匹配
        result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        # 判斷是否匹配成功
        if max_val >= threshold:
            logger.debug(f"找到圖片匹配 (相似度: {max_val:.2f}, 位置: {max_loc})")
            return True
        else:
            logger.debug(f"圖片不匹配 (相似度: {max_val:.2f})")
            return False
            
    except Exception as e:
        logger.warning(f"圖片檢測失敗：{e}")
        return False


def wait_for_image(driver: WebDriver, template_path: str, timeout: int = 60, 
                   interval: float = 0.5, threshold: float = 0.8) -> bool:
    """
    等待指定圖片出現在瀏覽器視窗中。
    
    持續檢測直到圖片出現或超時。
    
    Args:
        driver: WebDriver 實例
        template_path: 模板圖片路徑
        timeout: 超時時間（秒）
        interval: 檢測間隔（秒）
        threshold: 匹配閾值 (0-1)
        
    Returns:
        bool: 在超時前找到圖片返回 True，超時返回 False
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if detect_image_on_screen(driver, template_path, threshold):
            return True
        time.sleep(interval)
    
    logger.warning(f"等待圖片超時（{timeout} 秒）")
    return False


def navigate_to_game(driver: WebDriver, username: str, crop_size = 50) -> bool:
    """
    導航到遊戲頁面並確認成功進入。
    
    會持續檢測 lobby_login.png 圖片，確認真正進入遊戲。
    
    Args:
        driver: WebDriver 實例
        username: 帳號（用於日誌）
        
    Returns:
        bool: 成功返回 True，失敗返回 False
    """
    try:
        logger.info(f"[{username}] 正在進入遊戲...")
        driver.get(URL.GAME_PAGE)
        time.sleep(3)
        
        # 設定視窗大小
        driver.set_window_size(WINDOW_CONFIG.width, WINDOW_CONFIG.height)
        
        # 檢測 lobby_login.png 圖片確認進入遊戲
        logger.info(f"[{username}] 正在檢測遊戲載入狀態...")
        lobby_image_path = ImagePath.lobby_login()
        
        if wait_for_image(
            driver, 
            lobby_image_path, 
            timeout=GAME_CONFIG.image_detect_timeout,
            interval=GAME_CONFIG.image_detect_interval,
            threshold=GAME_CONFIG.image_match_threshold
        ):
            logger.info(f"[{username}] 成功進入遊戲大廳（已確認 lobby_login.png）")
            
            try:
                # === 切入 iframe ===
                iframe = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "gameFrame-0"))
                )
                driver.switch_to.frame(iframe)

                # === 取得 Canvas 區域 ===
                rect = driver.execute_script("""
                    const canvas = document.getElementById('GameCanvas');
                    const r = canvas.getBoundingClientRect();
                    return {x: r.left, y: r.top, w: r.width, h: r.height};
                """)

                global last_canvas_rect
                last_canvas_rect = rect

                # === 計算點擊座標 ===
                start_x = rect["x"] + rect["w"] * 0.55
                start_y = rect["y"] + rect["h"] * 1.2
                confirm_x = rect["x"] + rect["w"] * 0.78
                confirm_y = rect["y"] + rect["h"] * 1.15

                time.sleep(1)
                # === 點擊「開始遊戲」 ===
                for ev in ["mousePressed", "mouseReleased"]:
                    driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
                        "type": ev,
                        "x": start_x,
                        "y": start_y,
                        "button": "left",
                        "clickCount": 1
                    })
                time.sleep(3)

                # === 等待確認後點擊「確定」 ===
                input("請確認遊戲已經載入完成按 Enter 繼續...")
                for ev in ["mousePressed", "mouseReleased"]:
                    driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
                        "type": ev,
                        "x": confirm_x,
                        "y": confirm_y,
                        "button": "left",
                        "clickCount": 1
                    })

            except Exception as e:
                print("❌ 無法切入或操作 iframe：", e)

        else:
            logger.error(f"[{username}] 進入遊戲失敗：未檢測到 lobby_login.png")
            return False
            
    except Exception as e:
        logger.error(f"[{username}] 進入遊戲失敗：{e}")
        return False


def navigate_to_jfw(driver_path: str, username: str, password: str, max_retries: int = 3) -> Optional[WebDriver]:
    """
    建立瀏覽器並完成完整登入流程。
    
    執行步驟：
    1. 建立瀏覽器實例
    2. 開啟登入頁面
    3. 輸入帳號密碼並登入
    4. 處理公告彈窗
    5. 進入遊戲頁面
    6. 設定視窗大小
    
    Args:
        driver_path: ChromeDriver 路徑
        username: 登入帳號
        password: 登入密碼
        max_retries: 最大重試次數
        
    Returns:
        Optional[WebDriver]: 成功返回 WebDriver 實例，失敗返回 None
    """
    driver = None
    
    for attempt in range(max_retries):
        try:
            logger.info(f"[{username}] 開始登入流程（嘗試 {attempt + 1}/{max_retries}）")
            
            # 建立瀏覽器（第一次嘗試或需要重建）
            if driver is None:
                driver = create_webdriver(driver_path)
                if driver is None:
                    if attempt < max_retries - 1:
                        time.sleep(1)
                        continue
                    return None
            
            # 開啟登入頁面
            driver.get(URL.LOGIN_PAGE)
            time.sleep(2)
            
            # 執行登入
            if not perform_login(driver, username, password):
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                driver.quit()
                return None
            
            # 等待進入大廳
            time.sleep(2)
            
            # 導航到遊戲
            if not navigate_to_game(driver, username):
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                driver.quit()
                return None
            
            return driver
            
        except Exception as e:
            logger.error(f"[{username}] 登入流程異常：{e}")
            if attempt < max_retries - 1:
                logger.info(f"[{username}] 準備進行第 {attempt + 2} 次嘗試")
                time.sleep(1)
                continue
            
            # 最後一次嘗試失敗，清理資源
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass
            return None
    
    return None




# ==================== 遊戲控制 ====================

def send_key(driver: WebDriver, key_config: Dict[str, any]) -> bool:
    """
    使用 Chrome DevTools Protocol 發送鍵盤事件。
    
    按下並放開指定按鍵一次，不包含任何等待時間。
    呼叫者可以在呼叫此函式後自行決定等待時間。
    
    Args:
        driver: WebDriver 實例
        key_config: 按鍵配置字典，包含 key、code、windowsVirtualKeyCode、nativeVirtualKeyCode
        
    Returns:
        bool: 成功返回 True，失敗返回 False
        
    Example:
        >>> send_key(driver, KeyboardKey.SPACE)
        >>> time.sleep(15)  # 自訂間隔時間
        >>> send_key(driver, KeyboardKey.ARROW_LEFT)
    """
    try:
        driver.execute_cdp_cmd("Input.dispatchKeyEvent", {
            "type": "keyDown",
            "key": key_config["key"],
            "code": key_config["code"],
            "windowsVirtualKeyCode": key_config["windowsVirtualKeyCode"],
            "nativeVirtualKeyCode": key_config["nativeVirtualKeyCode"]
        })
        driver.execute_cdp_cmd("Input.dispatchKeyEvent", {
            "type": "keyUp",
            "key": key_config["key"],
            "code": key_config["code"],
            "windowsVirtualKeyCode": key_config["windowsVirtualKeyCode"],
            "nativeVirtualKeyCode": key_config["nativeVirtualKeyCode"]
        })
        return True
    except Exception as e:
        logger.warning(f"發送按鍵失敗：{e}")
        return False


def send_space_key(driver: WebDriver) -> bool:
    """
    發送空白鍵。
    
    Args:
        driver: WebDriver 實例
        
    Returns:
        bool: 成功返回 True，失敗返回 False
    """
    return send_key(driver, KeyboardKey.SPACE)


def send_arrow_left(driver: WebDriver) -> bool:
    """
    發送左方向鍵（減少金額）。
    
    Args:
        driver: WebDriver 實例
        
    Returns:
        bool: 成功返回 True，失敗返回 False
    """
    return send_key(driver, KeyboardKey.ARROW_LEFT)


def send_arrow_right(driver: WebDriver) -> bool:
    """
    發送右方向鍵（增加金額）。
    
    Args:
        driver: WebDriver 實例
        
    Returns:
        bool: 成功返回 True，失敗返回 False
    """
    return send_key(driver, KeyboardKey.ARROW_RIGHT)


def click_coordinate(driver: WebDriver, x: int, y: int) -> bool:
    """
    點擊指定座標位置。
    
    Args:
        driver: WebDriver 實例
        x: X 座標
        y: Y 座標
        
    Returns:
        bool: 成功返回 True，失敗返回 False
    """
    try:
        driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
            "type": "mousePressed",
            "x": x,
            "y": y,
            "button": "left",
            "clickCount": 1
        })
        driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
            "type": "mouseReleased",
            "x": x,
            "y": y,
            "button": "left",
            "clickCount": 1
        })
        logger.debug(f"已點擊座標 ({x}, {y})")
        return True
    except Exception as e:
        logger.warning(f"點擊座標 ({x}, {y}) 失敗：{e}")
        return False


def switch_to_game_frame(driver: WebDriver) -> bool:
    """
    切換到遊戲 iframe（如果存在）。
    
    Args:
        driver: WebDriver 實例
        
    Returns:
        bool: 成功切換返回 True，無需切換或失敗返回 False
    """
    try:
        driver.switch_to.default_content()
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        if iframes:
            driver.switch_to.frame(iframes[0])
            logger.info("已切換到遊戲 iframe")
            return True
    except Exception as e:
        logger.debug(f"切換 iframe 失敗：{e}")
    return False


def continue_game(driver: WebDriver) -> None:
    """
    持續執行遊戲操作的執行緒函式。
    
    循環執行：
    1. 按下空白鍵
    2. 等待指定秒數
    3. 再按一次空白鍵
    4. 重複循環
    
    會定期檢查執行狀態，當狀態變為非執行時立即停止。
    
    Args:
        driver: WebDriver 實例
    """
    try:
        # 嘗試切換到遊戲 iframe
        switch_to_game_frame(driver)
        
        while True:
            # 檢查是否應該繼續執行
            if not game_state_manager.is_running(driver):
                logger.info("遊戲已暫停")
                break
            
            # 第一次按空白鍵
            if not send_space_key(driver):
                break
            logger.debug("按下空白鍵（第一次）")
            
            # 分段等待，以便快速響應暫停指令
            for _ in range(GAME_CONFIG.key_interval):
                time.sleep(1)
                if not game_state_manager.is_running(driver):
                    logger.info("偵測到暫停指令")
                    return
            
            # 第二次按空白鍵
            if not send_space_key(driver):
                break
            logger.debug("按下空白鍵（第二次）")
                
    except Exception as e:
        logger.error(f"遊戲執行發生錯誤：{e}")
    finally:
        # 清理狀態
        game_state_manager.set_running(driver, False)
        game_state_manager.set_thread(driver, None)


def start_game(driver: WebDriver) -> bool:
    """
    開始遊戲執行。
    
    Args:
        driver: WebDriver 實例
        
    Returns:
        bool: 成功開始返回 True，已在執行中返回 False
    """
    if game_state_manager.is_running(driver):
        logger.info("遊戲已在執行中")
        return False
    
    # 啟動遊戲執行緒
    game_state_manager.set_running(driver, True)
    game_thread = threading.Thread(target=continue_game, args=(driver,), daemon=True)
    game_state_manager.set_thread(driver, game_thread)
    game_thread.start()
    
    logger.info("遊戲已開始執行")
    return True


def pause_game(driver: WebDriver) -> bool:
    """
    暫停遊戲執行。
    
    停止自動按鍵操作，並等待執行緒結束。
    
    Args:
        driver: WebDriver 實例
        
    Returns:
        bool: 成功暫停返回 True，未在執行返回 False
    """
    if not game_state_manager.is_running(driver):
        logger.info("遊戲未在執行中")
        return False
    
    # 發送暫停信號
    game_state_manager.set_running(driver, False)
    logger.info("已發送暫停信號")
    
    # 等待執行緒結束
    thread = game_state_manager.get_thread(driver)
    if thread and thread.is_alive():
        thread.join(timeout=3)
    
    logger.info("遊戲已暫停")
    return True


def quit_browser(driver: WebDriver) -> bool:
    """
    關閉瀏覽器並清理資源。
    
    Args:
        driver: WebDriver 實例
        
    Returns:
        bool: 成功關閉返回 True，失敗返回 False
    """
    try:
        # 先暫停遊戲
        pause_game(driver)
        
        # 關閉瀏覽器
        driver.quit()
        logger.info("瀏覽器已關閉")
        
        # 清理狀態
        game_state_manager.remove(driver)
        return True
    except Exception as e:
        # 忽略常見的關閉錯誤
        err_msg = str(e)
        if "Remote end closed connection" not in err_msg and "chrome not reachable" not in err_msg.lower():
            logger.warning(f"關閉瀏覽器時發生錯誤：{e}")
        return False


def capture_betsize_region(driver: WebDriver) -> Optional[np.ndarray]:
    """
    截取 betsize 顯示區域的圖片。
    
    Args:
        driver: WebDriver 實例
        
    Returns:
        Optional[np.ndarray]: 截取的區域圖片 (灰階)，失敗時返回 None
    """
    try:
        # 擷取整個瀏覽器截圖
        screenshot = driver.get_screenshot_as_png()
        screenshot_np = np.array(Image.open(io.BytesIO(screenshot)))
        
        # 裁剪 betsize 顯示區域
        betsize_region = screenshot_np[
            ClickCoordinate.BETSIZE_DISPLAY_TOP:ClickCoordinate.BETSIZE_DISPLAY_BOTTOM,
            ClickCoordinate.BETSIZE_DISPLAY_LEFT:ClickCoordinate.BETSIZE_DISPLAY_RIGHT
        ]
        
        # 轉換為灰階
        betsize_gray = cv2.cvtColor(betsize_region, cv2.COLOR_RGB2GRAY)
        
        logger.debug(f"已截取 betsize 區域 ({ClickCoordinate.BETSIZE_DISPLAY_LEFT},{ClickCoordinate.BETSIZE_DISPLAY_TOP}) - ({ClickCoordinate.BETSIZE_DISPLAY_RIGHT},{ClickCoordinate.BETSIZE_DISPLAY_BOTTOM})")
        return betsize_gray
        
    except Exception as e:
        logger.error(f"截取 betsize 區域失敗：{e}")
        return None


def compare_betsize_images(current_image: np.ndarray, bet_size_dir: str, threshold: float = 0.8) -> Optional[str]:
    """
    將當前 betsize 圖片與資料夾中所有圖片進行對比。
    
    Args:
        current_image: 當前截取的 betsize 圖片 (灰階)
        bet_size_dir: bet_size 圖片資料夾路徑
        threshold: 匹配閾值 (0-1)
        
    Returns:
        Optional[str]: 匹配的金額(檔名不含副檔名)，無匹配時返回 None
    """
    try:
        bet_size_path = Path(bet_size_dir)
        if not bet_size_path.exists():
            logger.error(f"bet_size 資料夾不存在：{bet_size_dir}")
            return None
        
        # 取得所有 png 圖片
        image_files = sorted(bet_size_path.glob("*.png"))
        if not image_files:
            logger.warning(f"bet_size 資料夾中沒有圖片：{bet_size_dir}")
            return None
        
        logger.info(f"開始比對 {len(image_files)} 張圖片...")
        
        best_match_score = 0.0
        best_match_amount = None
        
        # 對每張圖片進行匹配
        for image_file in image_files:
            # 讀取模板圖片
            template = cv2.imread(str(image_file), cv2.IMREAD_GRAYSCALE)
            if template is None:
                logger.warning(f"無法讀取圖片：{image_file}")
                continue
            
            # 確保模板大小不超過當前圖片
            if template.shape[0] > current_image.shape[0] or template.shape[1] > current_image.shape[1]:
                logger.debug(f"模板圖片 {image_file.name} 尺寸過大，跳過")
                continue
            
            # 執行模板匹配
            result = cv2.matchTemplate(current_image, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            logger.debug(f"圖片 {image_file.name} 匹配度：{max_val:.3f}")
            
            # 更新最佳匹配
            if max_val > best_match_score:
                best_match_score = max_val
                best_match_amount = image_file.stem  # 檔名不含副檔名
        
        # 檢查是否達到閾值
        if best_match_score >= threshold:
            logger.info(f"找到匹配金額：{best_match_amount} (相似度：{best_match_score:.3f})")
            return best_match_amount
        else:
            logger.warning(f"未找到匹配圖片 (最高相似度：{best_match_score:.3f})")
            return None
            
    except Exception as e:
        logger.error(f"比對圖片時發生錯誤：{e}")
        return None


def get_current_betsize_index(driver: WebDriver) -> Optional[int]:
    """
    取得當前下注金額在 GAME_BETSIZE 列表中的索引。
    
    Args:
        driver: WebDriver 實例
        
    Returns:
        Optional[int]: 當前金額的索引，查詢失敗時返回 None
    """
    try:
        logger.info("開始查詢當前下注金額...")
        
        # 截取 betsize 區域
        betsize_image = capture_betsize_region(driver)
        if betsize_image is None:
            logger.error("截取 betsize 區域失敗")
            return None
        
        # 與資料夾中的圖片進行比對
        bet_size_dir = ImagePath.bet_size_dir()
        matched_amount = compare_betsize_images(betsize_image, bet_size_dir, threshold=GAME_CONFIG.image_match_threshold)
        
        if matched_amount:
            # 將字串轉換為數字並在 GAME_BETSIZE 中找到對應索引
            try:
                amount_value = float(matched_amount)
                if amount_value in GAME_BETSIZE:
                    index = GAME_BETSIZE.index(amount_value)
                    logger.info(f"當前下注金額: {matched_amount} (索引: {index})")
                    return index
                else:
                    logger.warning(f"金額 {matched_amount} 不在 GAME_BETSIZE 列表中")
                    return None
            except ValueError:
                logger.error(f"無法將 {matched_amount} 轉換為數字")
                return None
        else:
            logger.warning("無法識別當前下注金額")
            return None
            
    except Exception as e:
        logger.error(f"查詢下注金額時發生錯誤: {e}")
        return None


def adjust_betsize(driver: WebDriver, target_amount: float, max_attempts: int = 200) -> bool:
    """
    調整下注金額到目標值。
    
    Args:
        driver: WebDriver 實例
        target_amount: 目標金額
        max_attempts: 最大嘗試次數
        
    Returns:
        bool: 調整成功返回 True，失敗返回 False
    """
    try:
        # 檢查目標金額是否在列表中
        if target_amount not in GAME_BETSIZE:
            logger.error(f"目標金額 {target_amount} 不在 GAME_BETSIZE 列表中")
            logger.info(f"可用金額: {GAME_BETSIZE}")
            return False
        
        target_index = GAME_BETSIZE.index(target_amount)
        logger.info(f"目標金額: {target_amount} (索引: {target_index})")
        
        # 取得當前金額索引
        current_index = get_current_betsize_index(driver)
        if current_index is None:
            logger.error("無法取得當前金額，調整失敗")
            return False
        
        # 計算需要按的次數和方向
        diff = target_index - current_index
        
        if diff == 0:
            logger.info("當前金額已經是目標金額，無需調整")
            return True
        
        # 決定按哪個鍵
        if diff > 0:
            # 需要增加，按右鍵
            key = KeyboardKey.ARROW_RIGHT
            direction = "增加"
            steps = diff
        else:
            # 需要減少，按左鍵
            key = KeyboardKey.ARROW_LEFT
            direction = "減少"
            steps = abs(diff)
        
        logger.info(f"需要{direction} {steps} 次才能到達目標金額")
        
        # 開始調整
        for i in range(steps):
            send_key(driver, key)
            logger.info(f"已按 {direction} 鍵 ({i + 1}/{steps})")
            time.sleep(0.3)  # 每次按鍵後短暫等待
        
        # 等待畫面更新
        time.sleep(1)
        
        # 驗證是否調整成功
        logger.info("開始驗證調整結果...")
        for attempt in range(max_attempts):
            final_index = get_current_betsize_index(driver)
            
            if final_index is None:
                logger.warning(f"驗證失敗 (嘗試 {attempt + 1}/{max_attempts})，重試中...")
                time.sleep(0.5)
                continue
            
            if final_index == target_index:
                logger.info(f"✓ 調整成功! 當前金額: {GAME_BETSIZE[final_index]}")
                return True
            else:
                # 如果不正確，繼續調整
                diff = target_index - final_index
                logger.warning(f"當前金額 {GAME_BETSIZE[final_index]} 未達目標，繼續調整 (差距: {diff})")
                
                if diff > 0:
                    send_key(driver, KeyboardKey.ARROW_RIGHT)
                else:
                    send_key(driver, KeyboardKey.ARROW_LEFT)
                
                time.sleep(0.5)
        
        logger.error(f"調整失敗，已達最大嘗試次數 ({max_attempts})")
        return False
        
    except Exception as e:
        logger.error(f"調整金額時發生錯誤: {e}")
        return False


def buy_free_game(driver: WebDriver, crop_size = 50) -> bool:   
    """
    嘗試購買免費遊戲。
    
    Args:
        driver: WebDriver 實例
        
    Returns:
        bool: 成功返回 True，失敗返回 False
    """
    try:
        global last_canvas_rect
        rect = last_canvas_rect  # click_canvas 儲存的 Canvas 範圍

        # === 第一次點擊（freegame 區域） ===
        freegame_x = rect["x"] + rect["w"] * 0.23
        freegame_y = rect["y"] + rect["h"] * 1.05

        for ev in ["mousePressed", "mouseReleased"]:
            driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
                "type": ev,
                "x": freegame_x,
                "y": freegame_y,
                "button": "left",
                "clickCount": 1
            })
        time.sleep(2)

        # === 第二次點擊（Canvas ） ===
        start_x = rect["x"] + rect["w"] * 0.65
        start_y = rect["y"] + rect["h"] * 1.2

        for ev in ["mousePressed", "mouseReleased"]:
            driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
                "type": ev,
                "x": start_x,
                "y": start_y,
                "button": "left",
                "clickCount": 1
            })
        input("請確認遊戲已經開始後按 Enter 繼續...")
            # === 延遲 1 秒後開始空白鍵回圈 ===
        time.sleep(1)
        stop_flag = threading.Event()

        # 開啟一個執行緒監聽終端輸入
        def listen_input():
            while True:
                user_input = input("🕹️ 輸入 'over' 結束空白鍵迴圈：").strip().lower()
                if user_input == "over":
                    stop_flag.set()
                    print("🛑 收到 'over' 指令，準備停止自動按空白鍵。")
                    break

        threading.Thread(target=listen_input, daemon=True).start()

        print("🔁 開始自動按空白鍵迴圈（每15秒一次，直到輸入 'over'）")

        counter = 0
        while not stop_flag.is_set():
            # 模擬空白鍵按下與放開
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
            counter += 1
            print(f"✅ 第 {counter} 次空白鍵已按下")

            # 每15秒按一次（可提前輸入 over 停止）
            for _ in range(15):
                if stop_flag.is_set():
                    break
                time.sleep(1)

        print("🏁 空白鍵自動按鍵已結束。")

    except Exception as e:
        print("❌ buyfreeGame 執行錯誤：", e)

    except Exception as e:
        print("❌ buyfreeGame 執行錯誤：", e)

    finally:
        try:
            driver.switch_to.default_content()
        except Exception:
            pass


def operate_game(driver: WebDriver, command: str) -> bool:
    """
    根據指令操作遊戲。
    
    Args:
        driver: WebDriver 實例
        command: 操作指令 ('c':繼續, 'p':暫停, 'q':退出)
        
    Returns:
        bool: 操作成功返回 True，無效指令或失敗返回 False
    """
    if driver is None:
        logger.error("瀏覽器實例不存在")
        return False
    
    command = command.lower()
    
    if command == GameCommand.CONTINUE.value:
        return start_game(driver)
    elif command == GameCommand.PAUSE.value:
        return pause_game(driver)
    elif command == GameCommand.QUIT.value:
        return quit_browser(driver)
    elif command == GameCommand.BUY_FREE_GAME.value:
        return buy_free_game(driver)
    elif command.startswith(GameCommand.BET_SIZE.value):
        # 處理調整金額指令: b <金額>
        parts = command.split()
        if len(parts) < 2:
            logger.warning("請輸入目標金額，格式: b <金額>")
            logger.info(f"可用金額: {GAME_BETSIZE}")
            return False
        
        try:
            target_amount = float(parts[1])
            return adjust_betsize(driver, target_amount)
        except ValueError:
            logger.error(f"無效的金額: {parts[1]}")
            return False
    else:
        logger.warning(f"未識別的指令：{command}")
        return False



# ==================== 視窗管理 ====================

def arrange_browser_windows(drivers: List[Optional[WebDriver]]) -> int:
    """
    按網格模式排列瀏覽器視窗。
    
    根據配置將視窗排列成網格：
    - 每行放置指定數量的視窗
    - 每列放置指定數量的視窗
    - 自動計算視窗位置
    
    Args:
        drivers: WebDriver 實例列表
        
    Returns:
        int: 成功排列的視窗數量
    """
    valid_drivers = [d for d in drivers if d is not None]
    if not valid_drivers:
        logger.warning("沒有有效的瀏覽器實例需要排列")
        return 0
    
    logger.info(f"開始排列 {len(valid_drivers)} 個瀏覽器視窗...")
    success_count = 0
    
    for index, driver in enumerate(valid_drivers):
        try:
            # 計算視窗位置
            col = index % WINDOW_CONFIG.columns
            row = (index // WINDOW_CONFIG.columns) % WINDOW_CONFIG.rows
            
            x_position = col * WINDOW_CONFIG.width
            y_position = row * WINDOW_CONFIG.height
            
            # 設定視窗位置和大小
            driver.set_window_position(x_position, y_position)
            driver.set_window_size(WINDOW_CONFIG.width, WINDOW_CONFIG.height)
            
            logger.info(f"瀏覽器 #{index + 1} 已移動到位置 ({x_position}, {y_position})")
            success_count += 1
        except Exception as e:
            logger.warning(f"無法排列瀏覽器 #{index + 1}：{e}")
    
    logger.info(f"瀏覽器視窗排列完成（成功：{success_count}/{len(valid_drivers)}）")
    return success_count



# ==================== 主程式 ====================

def get_browser_count(max_allowed: int) -> int:
    """
    取得使用者輸入的瀏覽器數量。
    
    Args:
        max_allowed: 允許的最大數量
        
    Returns:
        int: 使用者輸入的數量
    """
    while True:
        try:
            count = int(input(f"請輸入要啟動的瀏覽器數量 (1~{max_allowed})："))
            if 1 <= count <= max_allowed:
                return count
            logger.warning(f"請輸入介於 1 到 {max_allowed} 的整數")
        except ValueError:
            logger.warning("請輸入有效的整數")
        except (EOFError, KeyboardInterrupt):
            logger.info("\n程式已中止")
            raise


def launch_browsers_parallel(
    driver_path: str,
    credentials: List[Dict[str, str]],
    count: int
) -> Tuple[List[Optional[WebDriver]], int]:
    """
    並行啟動多個瀏覽器。
    
    Args:
        driver_path: ChromeDriver 路徑
        credentials: 帳號密碼列表
        count: 要啟動的數量
        
    Returns:
        Tuple[List[Optional[WebDriver]], int]: (瀏覽器實例列表, 成功數量)
    """
    drivers = [None] * count
    threads = []
    
    def launch_worker(index: int) -> None:
        """執行緒工作函式"""
        username = credentials[index]["username"]
        password = credentials[index]["password"]
        driver = navigate_to_jfw(driver_path, username, password)
        drivers[index] = driver
    
    logger.info(f"開始啟動 {count} 個瀏覽器...")
    
    for i in range(count):
        logger.info(f"啟動第 {i + 1} 個瀏覽器（帳號：{credentials[i]['username']}）")
        thread = threading.Thread(target=launch_worker, args=(i,), daemon=True)
        threads.append(thread)
        thread.start()
    
    logger.info("等待所有瀏覽器啟動完成...")
    for thread in threads:
        thread.join()
    
    success_count = sum(1 for d in drivers if d is not None)
    logger.info(f"完成！成功啟動 {success_count}/{count} 個瀏覽器")
    
    return drivers, success_count


def cleanup_all_browsers(drivers: List[Optional[WebDriver]]) -> None:
    """
    清理所有瀏覽器資源。
    
    Args:
        drivers: 瀏覽器實例列表
    """
    logger.info("正在停止所有遊戲...")
    for driver in drivers:
        if driver is not None:
            pause_game(driver)
    
    logger.info("正在關閉所有瀏覽器...")
    for driver in drivers:
        if driver is not None:
            try:
                driver.quit()
            except Exception:
                pass
    
    game_state_manager.cleanup_all()
    logger.info("清理完成")


def run_command_loop(drivers: List[Optional[WebDriver]]) -> None:
    """
    執行指令控制迴圈。
    
    Args:
        drivers: 瀏覽器實例列表
    """
    logger.info("已進入指令模式")
    logger.info(f"可用指令：{GameCommand.CONTINUE.value}(繼續) {GameCommand.PAUSE.value}(暫停) {GameCommand.BET_SIZE.value} <金額>(調整金額) {GameCommand.QUIT.value}(退出)")
    logger.info(f"可用金額列表: {GAME_BETSIZE}")
    
    try:
        while True:
            try:
                command = input("請輸入指令：").strip()
            except EOFError:
                logger.info("接收到 EOF，程式結束")
                break
            
            if not command:
                continue
            
            # 檢查退出指令
            if command.lower() == GameCommand.QUIT.value:
                cleanup_all_browsers(drivers)
                break
            
            # 對所有瀏覽器執行指令
            for driver in drivers:
                if driver is not None:
                    operate_game(driver, command)
    
    except KeyboardInterrupt:
        logger.info("\n偵測到中斷訊號 (Ctrl+C)")
        cleanup_all_browsers(drivers)


def main() -> None:
    """
    主程式入口。
    
    執行流程：
    1. 載入帳號資料
    2. 取得使用者輸入的瀏覽器數量
    3. 並行啟動多個瀏覽器
    4. 排列瀏覽器視窗
    5. 進入指令控制模式
    6. 清理資源並結束
    """
    logger.info("=== 金富翁遊戲自動化系統 ===")
    
    try:
        # 階段 1：載入帳號資料
        credentials = load_user_credentials()
        if not credentials:
            logger.error("無法載入帳號資料，程式結束")
            return
        
        # 階段 2：取得使用者輸入
        max_allowed = min(GAME_CONFIG.max_accounts, len(credentials))
        browser_count = get_browser_count(max_allowed)
        
        # 階段 3：啟動瀏覽器
        driver_path = get_chromedriver_path()
        drivers, success_count = launch_browsers_parallel(
            driver_path, credentials, browser_count
        )
        
        if success_count == 0:
            logger.error("沒有成功啟動任何瀏覽器，程式結束")
            return
        
        # 階段 4：排列視窗
        arrange_browser_windows(drivers)
        
        # 階段 5：指令控制
        run_command_loop(drivers)
        
    except KeyboardInterrupt:
        logger.info("\n程式已中斷")
    except Exception as e:
        logger.error(f"程式執行錯誤：{e}", exc_info=True)
    finally:
        logger.info("程式結束")


# ==================== 程式入口 ====================

if __name__ == "__main__":
    main()
