"""
金富翁遊戲自動化系統

此模組提供完整的自動化流程，包括：
- 多帳號批次登入
- 瀏覽器視窗管理
- 遊戲自動操作
- 執行緒安全的狀態控制
"""

from __future__ import annotations

import io
import logging
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
from selenium.webdriver.common.by import By


# ==================== 常量定義 ====================

class GameCommand(Enum):
    """遊戲控制指令列舉"""
    CONTINUE = 'c'
    PAUSE = 'p'
    QUIT = 'q'


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
    page_load_timeout: int = 300
    implicit_wait: int = 30
    explicit_wait: int = 5
    image_detect_timeout: int = 120  # 圖片檢測超時秒數
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
    START_GAME_Y = 600
    MACHINE_CONFIRM_X = 850
    MACHINE_CONFIRM_Y = 550
    FREE_GAME_X = 250
    FREE_GAME_Y = 500


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
    
    # 時間同步設定
    chrome_options.add_argument("--disable-features=NetworkTimeServiceQuerying")
    
    # 移除自動化痕跡
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
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
        driver.set_page_load_timeout(GAME_CONFIG.page_load_timeout)
        driver.implicitly_wait(GAME_CONFIG.implicit_wait)
        
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


def navigate_to_game(driver: WebDriver, username: str) -> bool:
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
            logger.info(f"[{username}] 成功進入遊戲（已確認 lobby_login.png）")
            return True
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
    logger.info(f"可用指令：{GameCommand.CONTINUE.value}(繼續) {GameCommand.PAUSE.value}(暫停) {GameCommand.QUIT.value}(退出)")
    
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
