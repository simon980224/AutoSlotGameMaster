"""
金富翁遊戲自動化系統

此模組提供完整的自動化流程，包括：
- 多帳號批次登入
- 瀏覽器視窗管理
- 遊戲自動操作
- 執行緒安全的狀態控制
"""

from __future__ import annotations

import logging
import os
import platform
import threading
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# ==================== 常量定義 ====================

class GameCommand(Enum):
    """遊戲控制指令列舉"""
    CONTINUE = 'c'
    PAUSE = 'p'
    QUIT = 'q'
    BUY_FREE = 'b'  # 購買免費遊戲


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


# XPath 常量
class XPath:
    """頁面元素 XPath 定義"""
    USERNAME_INPUT = "/html/body/div[2]/main/div/div[2]/div/div[3]/div[1]/div/div/div/div/input"
    PASSWORD_INPUT = "/html/body/div[2]/main/div/div[2]/div/div[3]/div[2]/div/div/div/div/input"
    LOGIN_BUTTON = "/html/body/div[2]/main/div/div[2]/div/div[3]/div[4]/div[1]"
    ERROR_MESSAGE = "/html/body/div[3]/div[2]/div/div[3]/span"
    ANNOUNCEMENT_CLOSE = "/html/body/div[2]/main/div/div[2]/div/div[3]/div[6]/div/div[3]/div[2]/div[1]"


# URL 常量
class URL:
    """網站 URL 定義"""
    LOGIN_PAGE = "https://m.jfw-win.com/#/login?redirect=%2Fhome%2Fpage"
    GAME_PAGE = "https://m.jfw-win.com/#/home/loding?game_code=egyptian-mythology&factory_code=ATG&state=true&name=%E6%88%B0%E7%A5%9E%E8%B3%BD%E7%89%B9"


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

# Canvas 位置快取（用於 buyfreeGame）
canvas_rect_cache: Dict[WebDriver, Optional[Dict[str, float]]] = {}


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
    - 最多讀取前 20 組帳號
    
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
    # chrome_options.add_experimental_option('useAutomationExtension', False)   # TODO: 註解以免影響canvas點擊
    
    # 偏好設定
    chrome_options.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_settings.popups": 0,
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


def close_announcement_popup(driver: WebDriver, wait: WebDriverWait) -> bool:
    """
    嘗試關閉公告彈窗。
    
    Args:
        driver: WebDriver 實例
        wait: WebDriverWait 實例
        
    Returns:
        bool: 成功關閉返回 True，否則返回 False
    """
    try:
        close_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, XPath.ANNOUNCEMENT_CLOSE))
        )
        close_button.click()
        logger.info("已關閉公告彈窗")
        return True
    except Exception:
        logger.debug("無公告彈窗")
        return False


def check_login_error(driver: WebDriver) -> Optional[str]:
    """
    檢查登入錯誤訊息。
    
    Args:
        driver: WebDriver 實例
        
    Returns:
        Optional[str]: 錯誤訊息，無錯誤時返回 None
    """
    try:
        error_element = driver.find_element(By.XPATH, XPath.ERROR_MESSAGE)
        error_text = error_element.text
        if error_text and "錯誤" in error_text:
            return error_text
    except Exception:
        pass
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
        wait = WebDriverWait(driver, GAME_CONFIG.explicit_wait)
        
        # 輸入帳號密碼
        driver.find_element(By.XPATH, XPath.USERNAME_INPUT).send_keys(username)
        driver.find_element(By.XPATH, XPath.PASSWORD_INPUT).send_keys(password)
        driver.find_element(By.XPATH, XPath.LOGIN_BUTTON).click()
        
        time.sleep(1)
        
        # 檢查登入錯誤
        error_msg = check_login_error(driver)
        if error_msg:
            logger.error(f"[{username}] 登入失敗：{error_msg}")
            return False
        
        # 關閉公告彈窗（如果有）
        close_announcement_popup(driver, wait)
        
        return True
    except Exception as e:
        logger.error(f"[{username}] 登入過程發生錯誤：{e}")
        return False


def navigate_to_game(driver: WebDriver, username: str) -> bool:
    """
    導航到遊戲頁面並設定視窗大小。
    
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
        logger.info(f"[{username}] 成功進入遊戲")
        return True
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

def send_space_key(driver: WebDriver) -> bool:
    """
    使用 Chrome DevTools Protocol 發送空白鍵事件。
    
    Args:
        driver: WebDriver 實例
        
    Returns:
        bool: 成功返回 True，失敗返回 False
    """
    try:
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
        return True
    except Exception as e:
        logger.warning(f"發送空白鍵失敗：{e}")
        return False


def press_space_key_once(driver: WebDriver) -> bool:
    """
    按下一次空白鍵（按下 + 放開），不包含任何等待時間。
    
    此函式專門用於需要自訂間隔時間的場景。
    呼叫者可以在呼叫此函式後自行決定等待時間。
    
    Args:
        driver: WebDriver 實例
        
    Returns:
        bool: 成功返回 True，失敗返回 False
    
    Example:
        >>> press_space_key_once(driver)
        >>> time.sleep(15)  # 自訂間隔時間
        >>> press_space_key_once(driver)
    """
    try:
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
        return True
    except Exception as e:
        logger.warning(f"按空白鍵失敗：{e}")
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


def initialize_canvas(driver: WebDriver) -> bool:
    """
    初始化 Canvas 並儲存位置資訊。
    
    必須在執行 buyfreeGame 之前呼叫此函式。
    
    Args:
        driver: WebDriver 實例
        
    Returns:
        bool: 成功返回 True，失敗返回 False
    """
    try:
        # 切入 iframe
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "gameFrame-0"))
        )
        driver.switch_to.frame(iframe)
        
        # 取得 Canvas 區域
        rect = driver.execute_script("""
            const canvas = document.getElementById('GameCanvas');
            const r = canvas.getBoundingClientRect();
            return {x: r.left, y: r.top, w: r.width, h: r.height};
        """)
        
        # 儲存到快取
        canvas_rect_cache[driver] = rect
        
        # 切回主頁面
        driver.switch_to.default_content()
        
        logger.info(f"Canvas 初始化成功：位置 ({rect['x']:.1f}, {rect['y']:.1f})，大小 {rect['w']:.1f}x{rect['h']:.1f}")
        return True
    except Exception as e:
        logger.error(f"Canvas 初始化失敗：{e}")
        driver.switch_to.default_content()
        return False


def click_canvas_position(driver: WebDriver, rect: Dict[str, float], x_ratio: float, y_ratio: float, description: str = "點擊位置") -> bool:
    """
    在 Canvas 上指定位置點擊。
    
    Args:
        driver: WebDriver 實例
        rect: Canvas 區域資訊
        x_ratio: X 軸比例（0.0-1.0+）
        y_ratio: Y 軸比例（0.0-1.0+）
        description: 點擊位置的描述
        
    Returns:
        bool: 成功返回 True，失敗返回 False
    """
    try:
        click_x = rect["x"] + rect["w"] * x_ratio
        click_y = rect["y"] + rect["h"] * y_ratio
        
        for ev in ["mousePressed", "mouseReleased"]:
            driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
                "type": ev,
                "x": click_x,
                "y": click_y,
                "button": "left",
                "clickCount": 1
            })
        
        logger.info(f"已點擊{description} ({click_x:.1f}, {click_y:.1f})")
        return True
    except Exception as e:
        logger.error(f"點擊{description}失敗：{e}")
        return False


def wait_for_user_completion() -> bool:
    """
    等待使用者輸入 'done' 確認完成。
    
    Returns:
        bool: 使用者確認完成返回 True，中斷返回 False
    """
    logger.info("💡 免費遊戲結束後，請在終端輸入 'done' 並按 Enter 鍵")
    
    while True:
        try:
            user_input = input("👉 請輸入 'done' 確認免費遊戲已完成：").strip().lower()
            if user_input == 'done':
                return True
            logger.warning("請輸入 'done' 以確認完成")
        except (EOFError, KeyboardInterrupt):
            logger.warning("輸入被中斷")
            return False


def auto_press_space_until_done(driver: WebDriver, stop_event: threading.Event, interval: int = 15) -> None:
    """
    持續按空白鍵的執行緒函式。
    
    會持續按空白鍵直到 stop_event 被設定。
    
    Args:
        driver: WebDriver 實例
        stop_event: 停止事件
        interval: 按鍵間隔秒數，預設 15 秒
    """
    try:
        while not stop_event.is_set():
            if not press_space_key_once(driver):
                logger.warning("按空白鍵失敗，停止執行緒")
                break
            time.sleep(interval)
    except Exception as e:
        logger.error(f"空白鍵執行緒發生錯誤：{e}")


def switch_to_game_iframe(driver: WebDriver) -> bool:
    """
    切換到遊戲 iframe。
    
    Args:
        driver: WebDriver 實例
        
    Returns:
        bool: 成功返回 True，失敗返回 False
    """
    try:
        iframe = driver.find_element(By.ID, "gameFrame-0")
        driver.switch_to.frame(iframe)
        return True
    except Exception as e:
        logger.error(f"切換到遊戲 iframe 失敗：{e}")
        return False


def buy_free_game(driver: WebDriver) -> bool:
    """
    自動購買免費遊戲。
    
    執行步驟：
    1. 檢查 Canvas 是否已初始化
    2. 暫停當前自動按鍵
    3. 切換到遊戲 iframe
    4. 點擊免費遊戲區域
    5. 點擊開始按鈕
    6. 持續按空白鍵直到使用者輸入 'done' 確認完成
    7. 切回主頁面並恢復之前的狀態
    
    Args:
        driver: WebDriver 實例
        
    Returns:
        bool: 成功返回 True，失敗返回 False
    """
    # 檢查 Canvas 是否已初始化
    if driver not in canvas_rect_cache or canvas_rect_cache[driver] is None:
        logger.warning("Canvas 尚未初始化，正在嘗試初始化...")
        if not initialize_canvas(driver):
            logger.error("無法執行購買免費遊戲")
            return False
    
    # 暫停當前遊戲並記錄狀態
    was_running = game_state_manager.is_running(driver)
    if was_running:
        pause_game(driver)
        time.sleep(1)
    
    # 建立停止事件
    stop_event = threading.Event()
    space_thread = None
    
    try:
        rect = canvas_rect_cache[driver]
        
        # 切換到遊戲 iframe
        if not switch_to_game_iframe(driver):
            return False
        
        # 點擊免費遊戲區域
        if not click_canvas_position(driver, rect, 0.29, 1.14, "免費遊戲位置"):
            return False
        time.sleep(2)
        
        # 點擊開始按鈕
        if not click_canvas_position(driver, rect, 0.6, 1.25, "開始按鈕"):
            return False
        time.sleep(1)
        
        # 啟動自動按空白鍵執行緒
        space_thread = threading.Thread(
            target=auto_press_space_until_done,
            args=(driver, stop_event, 15),
            daemon=True
        )
        space_thread.start()
        logger.info("⏳ 開始自動按空白鍵...")
        
        # 等待使用者確認完成
        user_confirmed = wait_for_user_completion()
        
        # 停止空白鍵執行緒
        stop_event.set()
        if space_thread and space_thread.is_alive():
            space_thread.join(timeout=2)
        
        if user_confirmed:
            logger.info("✅ 購買免費遊戲完成！")
        else:
            logger.warning("購買免費遊戲被中斷")
        
        return True
        
    except Exception as e:
        logger.error(f"購買免費遊戲失敗：{e}")
        return False
    
    finally:
        # 確保停止執行緒
        stop_event.set()
        if space_thread and space_thread.is_alive():
            space_thread.join(timeout=2)
        
        # 切回主頁面
        try:
            driver.switch_to.default_content()
        except Exception:
            pass
        
        # 恢復之前的狀態
        if was_running:
            time.sleep(1)
            start_game(driver)


def operate_game(driver: WebDriver, command: str) -> bool:
    """
    根據指令操作遊戲。
    
    Args:
        driver: WebDriver 實例
        command: 操作指令 ('c':繼續, 'p':暫停, 'q':退出, 'b':購買免費遊戲)
        
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
    elif command == GameCommand.BUY_FREE.value:
        return buy_free_game(driver)
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
    logger.info(f"可用指令：{GameCommand.CONTINUE.value}(繼續) {GameCommand.PAUSE.value}(暫停) {GameCommand.BUY_FREE.value}(購買免費遊戲) {GameCommand.QUIT.value}(退出)")
    
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
