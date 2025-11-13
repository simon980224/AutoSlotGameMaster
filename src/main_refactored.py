"""
金富翁遊戲自動化系統 - 專業重構版本

這是一個高度專業化的自動化系統，提供以下核心功能：
- 多帳號並行登入與管理
- 智慧型瀏覽器視窗排列
- 基於規則的自動遊戲執行
- 圖像識別與金額調整
- Proxy 支援與網路優化
- 執行緒安全的狀態管理

作者: simon980224
版本: 2.0.0 (重構版)
Python: 3.8+
"""

from __future__ import annotations

import io
import logging
import platform
import tempfile
import threading
import time
import zipfile
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Callable
from contextlib import contextmanager

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
from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
    NoSuchElementException,
)


# ==================== 自定義異常類別 ====================


class GameAutomationError(Exception):
    """遊戲自動化基礎異常類別"""
    pass


class ConfigurationError(GameAutomationError):
    """配置錯誤異常"""
    pass


class BrowserError(GameAutomationError):
    """瀏覽器操作錯誤異常"""
    pass


class LoginError(GameAutomationError):
    """登入錯誤異常"""
    pass


class ImageDetectionError(GameAutomationError):
    """圖片檢測錯誤異常"""
    pass


class GameControlError(GameAutomationError):
    """遊戲控制錯誤異常"""
    pass


# ==================== 日誌配置 ====================


class LogFormatter(logging.Formatter):
    """自定義日誌格式化器，支援顏色輸出"""

    # ANSI 顏色碼
    COLORS = {
        'DEBUG': '\033[36m',    # 青色
        'INFO': '\033[32m',     # 綠色
        'WARNING': '\033[33m',  # 黃色
        'ERROR': '\033[31m',    # 紅色
        'CRITICAL': '\033[35m', # 紫色
    }
    RESET = '\033[0m'

    def format(self, record: logging.LogRecord) -> str:
        """格式化日誌記錄"""
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname:8s}{self.RESET}"
        return super().format(record)


def setup_logger(name: str = __name__, level: int = logging.INFO) -> logging.Logger:
    """
    設定並返回配置好的日誌記錄器
    
    Args:
        name: 日誌記錄器名稱
        level: 日誌級別
        
    Returns:
        logging.Logger: 配置好的日誌記錄器
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 避免重複添加處理器
    if logger.handlers:
        return logger
    
    # 控制台處理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # 使用自定義格式化器
    formatter = LogFormatter(
        '[%(levelname)s] [%(asctime)s] [%(funcName)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    return logger


# 全域日誌記錄器
logger = setup_logger()


# ==================== 配置管理 ====================


class GameCommand(Enum):
    """遊戲控制指令列舉"""
    CONTINUE = 'c'      # 繼續遊戲
    PAUSE = 'p'         # 暫停遊戲
    QUIT = 'q'          # 退出程式
    BET_SIZE = 'b'      # 調整下注金額
    SCREENSHOT = 's'    # 截取螢幕
    PEEK = 'p'          # 檢測指定金額圖片
    HELP = 'h'          # 顯示幫助


@dataclass(frozen=True)
class WindowConfig:
    """視窗配置（不可變）"""
    width: int = 600
    height: int = 400
    columns: int = 4
    rows: int = 3
    
    def __post_init__(self) -> None:
        """驗證配置有效性"""
        if self.width <= 0 or self.height <= 0:
            raise ConfigurationError(f"視窗尺寸必須為正數: width={self.width}, height={self.height}")
        if self.columns <= 0 or self.rows <= 0:
            raise ConfigurationError(f"網格配置必須為正數: columns={self.columns}, rows={self.rows}")


@dataclass(frozen=True)
class GameConfig:
    """遊戲配置（不可變）"""
    max_accounts: int = 12
    key_interval: int = 15
    page_load_timeout: int = 600
    script_timeout: int = 600
    implicit_wait: int = 60
    explicit_wait: int = 10
    image_detect_timeout: int = 180
    image_detect_interval: float = 0.5
    image_match_threshold: float = 0.95
    max_retries: int = 3
    retry_delay: int = 2
    
    def __post_init__(self) -> None:
        """驗證配置有效性"""
        if self.max_accounts <= 0:
            raise ConfigurationError(f"最大帳號數必須為正數: {self.max_accounts}")
        if self.key_interval <= 0:
            raise ConfigurationError(f"按鍵間隔必須為正數: {self.key_interval}")
        if not 0.0 < self.image_match_threshold <= 1.0:
            raise ConfigurationError(f"圖片匹配閾值必須在 (0, 1] 範圍內: {self.image_match_threshold}")


@dataclass(frozen=True)
class ElementSelector:
    """頁面元素選擇器定義（不可變）"""
    USERNAME_INPUT: str = "//input[@placeholder='請輸入帳號']"
    PASSWORD_INPUT: str = "//input[@placeholder='請輸入密碼']"
    LOGIN_BUTTON: str = "//div[contains(@class, 'login-btn')]//span[text()='立即登入']/.."
    GAME_IFRAME: str = "gameFrame-0"
    GAME_CANVAS: str = "GameCanvas"


@dataclass(frozen=True)
class KeyboardKey:
    """鍵盤按鍵屬性定義（不可變）"""
    SPACE: Dict[str, Any] = field(default_factory=lambda: {
        "key": " ",
        "code": "Space",
        "windowsVirtualKeyCode": 32,
        "nativeVirtualKeyCode": 32
    })
    
    ARROW_LEFT: Dict[str, Any] = field(default_factory=lambda: {
        "key": "ArrowLeft",
        "code": "ArrowLeft",
        "windowsVirtualKeyCode": 37,
        "nativeVirtualKeyCode": 37
    })
    
    ARROW_RIGHT: Dict[str, Any] = field(default_factory=lambda: {
        "key": "ArrowRight",
        "code": "ArrowRight",
        "windowsVirtualKeyCode": 39,
        "nativeVirtualKeyCode": 39
    })


@dataclass(frozen=True)
class ClickCoordinate:
    """遊戲中需要點擊的座標位置（不可變）"""
    # Canvas 動態計算比例
    START_GAME_X_RATIO: float = 0.55
    START_GAME_Y_RATIO: float = 1.2
    MACHINE_CONFIRM_X_RATIO: float = 0.78
    MACHINE_CONFIRM_Y_RATIO: float = 1.15
    FREE_GAME_X_RATIO: float = 0.25
    FREE_GAME_Y_RATIO: float = 0.5
    
    # Betsize 顯示區域（絕對座標）
    BETSIZE_DISPLAY_LEFT: int = 750
    BETSIZE_DISPLAY_TOP: int = 554
    BETSIZE_DISPLAY_RIGHT: int = 850
    BETSIZE_DISPLAY_BOTTOM: int = 600


@dataclass(frozen=True)
class URLConfig:
    """網站 URL 定義（不可變）"""
    LOGIN_PAGE: str = "https://m.jfw-win.com/#/login?redirect=%2Fhome%2Fpage"
    GAME_PAGE: str = "https://m.jfw-win.com/#/home/loding?game_code=egyptian-mythology&factory_code=ATG&state=true&name=%E6%88%B0%E7%A5%9E%E8%B3%BD%E7%89%B9"


# 遊戲可用金額列表（常量）
GAME_BETSIZE: Tuple[float, ...] = (
    0.4, 0.8, 1, 1.2, 1.6, 2, 2.4, 2.8, 3, 3.2, 3.6, 4, 5, 6, 7, 8, 9, 10,
    12, 14, 16, 18, 20, 24, 28, 32, 36, 40, 48, 56, 60, 64, 72, 80, 100,
    120, 140, 160, 180, 200, 240, 280, 300, 320, 360, 400, 420, 480, 500,
    540, 560, 600, 640, 700, 720, 800, 840, 900, 960, 980, 1000, 1080,
    1120, 1200, 1260, 1280, 1400, 1440, 1600, 1800, 2000
)

# 全域配置實例
WINDOW_CONFIG = WindowConfig()
GAME_CONFIG = GameConfig()
ELEMENT_SELECTOR = ElementSelector()
KEYBOARD_KEY = KeyboardKey()
CLICK_COORD = ClickCoordinate()
URL_CONFIG = URLConfig()


# ==================== 路徑管理器 ====================


class PathManager:
    """統一的路徑管理器"""
    
    def __init__(self):
        """初始化路徑管理器"""
        self._project_root = Path(__file__).resolve().parent.parent
        logger.debug(f"專案根目錄: {self._project_root}")
    
    @property
    def project_root(self) -> Path:
        """取得專案根目錄"""
        return self._project_root
    
    @property
    def lib_dir(self) -> Path:
        """取得 lib 目錄"""
        return self._project_root / "lib"
    
    @property
    def img_dir(self) -> Path:
        """取得 img 目錄"""
        return self._project_root / "img"
    
    @property
    def bet_size_dir(self) -> Path:
        """取得 bet_size 圖片目錄"""
        return self.img_dir / "bet_size"
    
    def get_image_path(self, filename: str) -> Path:
        """
        取得圖片完整路徑
        
        Args:
            filename: 圖片檔名
            
        Returns:
            Path: 圖片完整路徑
        """
        return self.img_dir / filename
    
    @property
    def lobby_login_image(self) -> Path:
        """取得大廳登入圖片路徑"""
        return self.get_image_path("lobby_login.png")
    
    @property
    def lobby_confirm_image(self) -> Path:
        """取得大廳確認圖片路徑"""
        return self.get_image_path("lobby_confirm.png")
    
    @property
    def credentials_file(self) -> Path:
        """取得帳號密碼檔案路徑"""
        return self.lib_dir / "user_credentials.txt"
    
    @property
    def rules_file(self) -> Path:
        """取得遊戲規則檔案路徑"""
        return self.lib_dir / "user_rules.txt"
    
    @property
    def chromedriver_path(self) -> Path:
        """
        取得 ChromeDriver 路徑
        
        Returns:
            Path: ChromeDriver 路徑
            
        Raises:
            FileNotFoundError: 當檔案不存在時
        """
        system = platform.system().lower()
        driver_filename = "chromedriver.exe" if system == "windows" else "chromedriver"
        driver_path = self._project_root / driver_filename
        
        if not driver_path.exists():
            raise FileNotFoundError(f"找不到 ChromeDriver: {driver_path}")
        
        return driver_path


# 全域路徑管理器實例
path_manager = PathManager()


# ==================== 數據模型 ====================


@dataclass
class UserCredential:
    """使用者憑證數據模型"""
    username: str
    password: str
    proxy: Optional[str] = None
    
    def __post_init__(self) -> None:
        """驗證數據有效性"""
        if not self.username or not self.password:
            raise ConfigurationError("帳號和密碼不能為空")
        
        # 驗證 proxy 格式（如果有）
        if self.proxy:
            parts = self.proxy.split(':')
            if len(parts) != 4:
                raise ConfigurationError(f"Proxy 格式錯誤，應為 ip:port:username:password: {self.proxy}")
    
    @property
    def proxy_config(self) -> Optional[Tuple[str, str, str, str]]:
        """
        取得 Proxy 配置
        
        Returns:
            Optional[Tuple[str, str, str, str]]: (ip, port, username, password) 或 None
        """
        if not self.proxy:
            return None
        parts = self.proxy.split(':')
        return (parts[0], parts[1], parts[2], parts[3])
    
    def __repr__(self) -> str:
        """字符串表示（隱藏密碼）"""
        return f"UserCredential(username='{self.username}', has_proxy={self.proxy is not None})"


@dataclass
class GameRule:
    """遊戲規則數據模型"""
    betsize: float
    duration_minutes: int
    
    def __post_init__(self) -> None:
        """驗證數據有效性"""
        if self.betsize not in GAME_BETSIZE:
            raise ConfigurationError(f"金額 {self.betsize} 不在可用金額列表中")
        if self.duration_minutes <= 0:
            raise ConfigurationError(f"持續時間必須為正數: {self.duration_minutes}")
    
    @property
    def duration_seconds(self) -> int:
        """取得持續時間（秒）"""
        return self.duration_minutes * 60


@dataclass
class GameState:
    """遊戲狀態數據模型"""
    running: bool = False
    thread: Optional[threading.Thread] = None
    rules: Optional[List[GameRule]] = None


# ==================== Proxy 擴充功能管理器 ====================


class ProxyExtensionManager:
    """Proxy Chrome Extension 管理器"""
    
    @staticmethod
    def create_extension(proxy_host: str, proxy_port: str, 
                        proxy_user: str, proxy_pass: str) -> str:
        """
        創建 Chrome Proxy Extension
        
        完全在記憶體中操作，返回臨時檔案路徑。
        
        Args:
            proxy_host: Proxy 主機 IP
            proxy_port: Proxy 埠號
            proxy_user: Proxy 使用者名稱
            proxy_pass: Proxy 密碼
            
        Returns:
            str: Extension 壓縮檔的完整路徑（臨時檔案）
            
        Raises:
            BrowserError: 當創建失敗時
        """
        try:
            manifest_json = """
            {
                "version": "1.0.0",
                "manifest_version": 2,
                "name": "Chrome Proxy Auth",
                "permissions": [
                    "proxy",
                    "tabs",
                    "unlimitedStorage",
                    "storage",
                    "<all_urls>",
                    "webRequest",
                    "webRequestBlocking"
                ],
                "background": {
                    "scripts": ["background.js"]
                },
                "minimum_chrome_version":"22.0.0"
            }
            """

            background_js = f"""
            var config = {{
                    mode: "fixed_servers",
                    rules: {{
                      singleProxy: {{
                        scheme: "http",
                        host: "{proxy_host}",
                        port: parseInt({proxy_port})
                      }},
                      bypassList: ["localhost"]
                    }}
                  }};

            chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});

            function callbackFn(details) {{
                return {{
                    authCredentials: {{
                        username: "{proxy_user}",
                        password: "{proxy_pass}"
                    }}
                }};
            }}

            chrome.webRequest.onAuthRequired.addListener(
                        callbackFn,
                        {{urls: ["<all_urls>"]}},
                        ['blocking']
            );
            """

            # 創建臨時 zip 檔案
            temp_file = tempfile.NamedTemporaryFile(
                mode='w+b', 
                suffix='.zip', 
                delete=False
            )
            
            with zipfile.ZipFile(temp_file, 'w') as zp:
                zp.writestr("manifest.json", manifest_json)
                zp.writestr("background.js", background_js)
            
            temp_file.close()
            
            logger.debug(f"已創建 Proxy Extension: {temp_file.name}")
            return temp_file.name
            
        except Exception as e:
            raise BrowserError(f"創建 Proxy Extension 失敗: {e}") from e


# ==================== 配置載入器 ====================


class ConfigLoader:
    """配置檔案載入器"""
    
    @staticmethod
    def load_credentials() -> List[UserCredential]:
        """
        從檔案讀取使用者憑證
        
        Returns:
            List[UserCredential]: 憑證列表
            
        Raises:
            ConfigurationError: 當檔案不存在或格式錯誤時
        """
        credentials_path = path_manager.credentials_file
        
        if not credentials_path.exists():
            raise ConfigurationError(f"找不到帳號檔案: {credentials_path}")
        
        credentials = []
        
        try:
            with open(credentials_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for idx, line in enumerate(lines):
                # 跳過標題行和空行
                if idx == 0 or not line.strip():
                    continue
                
                if ',' not in line:
                    logger.warning(f"第 {idx + 1} 行格式錯誤，已跳過: {line.strip()}")
                    continue
                
                parts = [p.strip() for p in line.split(',')]
                if len(parts) < 2:
                    logger.warning(f"第 {idx + 1} 行資料不足，已跳過: {line.strip()}")
                    continue
                
                try:
                    credential = UserCredential(
                        username=parts[0],
                        password=parts[1],
                        proxy=parts[2] if len(parts) >= 3 and parts[2] else None
                    )
                    credentials.append(credential)
                except ConfigurationError as e:
                    logger.warning(f"第 {idx + 1} 行數據驗證失敗: {e}")
                    continue
            
            if not credentials:
                raise ConfigurationError("帳號檔案內容為空或格式錯誤")
            
            # 限制最大數量
            total_count = len(credentials)
            if total_count > GAME_CONFIG.max_accounts:
                logger.info(f"偵測到 {total_count} 組帳號，僅保留前 {GAME_CONFIG.max_accounts} 組")
                credentials = credentials[:GAME_CONFIG.max_accounts]
            else:
                logger.info(f"已載入 {total_count} 組帳號資料")
            
            return credentials
            
        except Exception as e:
            if isinstance(e, ConfigurationError):
                raise
            raise ConfigurationError(f"讀取帳號檔案失敗: {e}") from e
    
    @staticmethod
    def load_game_rules() -> List[GameRule]:
        """
        從檔案讀取遊戲規則
        
        Returns:
            List[GameRule]: 規則列表
            
        Raises:
            ConfigurationError: 當檔案不存在或格式錯誤時
        """
        rules_path = path_manager.rules_file
        
        if not rules_path.exists():
            raise ConfigurationError(f"找不到規則檔案: {rules_path}")
        
        rules = []
        
        try:
            with open(rules_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for idx, line in enumerate(lines):
                # 跳過標題行和空行
                if idx == 0 or not line.strip():
                    continue
                
                if ':' not in line:
                    logger.warning(f"第 {idx + 1} 行格式錯誤，已跳過: {line.strip()}")
                    continue
                
                try:
                    betsize_str, duration_str = line.split(':', 1)
                    rule = GameRule(
                        betsize=float(betsize_str.strip()),
                        duration_minutes=int(duration_str.strip())
                    )
                    rules.append(rule)
                except (ValueError, ConfigurationError) as e:
                    logger.warning(f"第 {idx + 1} 行解析失敗: {e}，已跳過")
                    continue
            
            if not rules:
                raise ConfigurationError("規則檔案內容為空或格式錯誤")
            
            logger.info(f"已載入 {len(rules)} 條遊戲規則")
            for idx, rule in enumerate(rules, 1):
                logger.info(f"  規則 {idx}: 金額 {rule.betsize} 執行 {rule.duration_minutes} 分鐘")
            
            return rules
            
        except Exception as e:
            if isinstance(e, ConfigurationError):
                raise
            raise ConfigurationError(f"讀取規則檔案失敗: {e}") from e


# ==================== 遊戲狀態管理器 ====================


class GameStateManager:
    """執行緒安全的遊戲狀態管理器"""
    
    def __init__(self):
        """初始化狀態管理器"""
        self._states: Dict[WebDriver, GameState] = {}
        self._lock = threading.RLock()  # 使用可重入鎖
        logger.debug("遊戲狀態管理器已初始化")
    
    @contextmanager
    def _get_lock(self):
        """上下文管理器用於鎖定"""
        self._lock.acquire()
        try:
            yield
        finally:
            self._lock.release()
    
    def _ensure_state(self, driver: WebDriver) -> GameState:
        """確保驅動器有對應的狀態"""
        if driver not in self._states:
            self._states[driver] = GameState()
        return self._states[driver]
    
    def set_running(self, driver: WebDriver, running: bool) -> None:
        """
        設定執行狀態
        
        Args:
            driver: WebDriver 實例
            running: 是否正在執行
        """
        with self._get_lock():
            state = self._ensure_state(driver)
            state.running = running
            logger.debug(f"設定遊戲執行狀態: {running}")
    
    def is_running(self, driver: WebDriver) -> bool:
        """
        檢查是否正在執行
        
        Args:
            driver: WebDriver 實例
            
        Returns:
            bool: 是否正在執行
        """
        with self._get_lock():
            return driver in self._states and self._states[driver].running
    
    def set_thread(self, driver: WebDriver, thread: Optional[threading.Thread]) -> None:
        """
        設定執行緒
        
        Args:
            driver: WebDriver 實例
            thread: 執行緒實例
        """
        with self._get_lock():
            state = self._ensure_state(driver)
            state.thread = thread
    
    def get_thread(self, driver: WebDriver) -> Optional[threading.Thread]:
        """
        取得執行緒
        
        Args:
            driver: WebDriver 實例
            
        Returns:
            Optional[threading.Thread]: 執行緒實例
        """
        with self._get_lock():
            if driver in self._states:
                return self._states[driver].thread
            return None
    
    def set_rules(self, driver: WebDriver, rules: Optional[List[GameRule]]) -> None:
        """
        設定遊戲規則
        
        Args:
            driver: WebDriver 實例
            rules: 規則列表
        """
        with self._get_lock():
            state = self._ensure_state(driver)
            state.rules = rules
            logger.debug(f"已設定 {len(rules) if rules else 0} 條遊戲規則")
    
    def get_rules(self, driver: WebDriver) -> Optional[List[GameRule]]:
        """
        取得遊戲規則
        
        Args:
            driver: WebDriver 實例
            
        Returns:
            Optional[List[GameRule]]: 規則列表
        """
        with self._get_lock():
            if driver in self._states:
                return self._states[driver].rules
            return None
    
    def remove(self, driver: WebDriver) -> None:
        """
        移除狀態
        
        Args:
            driver: WebDriver 實例
        """
        with self._get_lock():
            if driver in self._states:
                del self._states[driver]
                logger.debug("已移除遊戲狀態")
    
    def cleanup_all(self) -> None:
        """清理所有狀態"""
        with self._get_lock():
            count = len(self._states)
            self._states.clear()
            logger.info(f"已清理 {count} 個遊戲狀態")


# 全域狀態管理器實例
game_state_manager = GameStateManager()


# ==================== 圖片處理工具 ====================


class ImageProcessor:
    """圖片處理工具類"""
    
    @staticmethod
    def screenshot_to_array(screenshot_png: bytes) -> np.ndarray:
        """
        將PNG截圖轉換為NumPy陣列
        
        Args:
            screenshot_png: PNG格式的截圖數據
            
        Returns:
            np.ndarray: RGB格式的NumPy陣列
        """
        return np.array(Image.open(io.BytesIO(screenshot_png)))
    
    @staticmethod
    def to_grayscale(image: np.ndarray) -> np.ndarray:
        """
        將圖片轉換為灰階
        
        Args:
            image: RGB格式的圖片
            
        Returns:
            np.ndarray: 灰階圖片
        """
        return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    
    @staticmethod
    def match_template(screenshot_gray: np.ndarray, template_path: Path, 
                      threshold: float = 0.8) -> Tuple[bool, float, Tuple[int, int]]:
        """
        模板匹配
        
        Args:
            screenshot_gray: 截圖（灰階）
            template_path: 模板圖片路徑
            threshold: 匹配閾值
            
        Returns:
            Tuple[bool, float, Tuple[int, int]]: (是否匹配, 相似度, 位置)
            
        Raises:
            ImageDetectionError: 當處理失敗時
        """
        try:
            if not template_path.exists():
                raise ImageDetectionError(f"模板圖片不存在: {template_path}")
            
            template = cv2.imread(str(template_path), cv2.IMREAD_GRAYSCALE)
            if template is None:
                raise ImageDetectionError(f"無法讀取模板圖片: {template_path}")
            
            # 檢查尺寸
            if (screenshot_gray.shape[0] < template.shape[0] or 
                screenshot_gray.shape[1] < template.shape[1]):
                return False, 0.0, (0, 0)
            
            # 執行模板匹配
            result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            matched = max_val >= threshold
            return matched, max_val, max_loc
            
        except Exception as e:
            if isinstance(e, ImageDetectionError):
                raise
            raise ImageDetectionError(f"模板匹配失敗: {e}") from e


# ==================== 瀏覽器管理器 ====================


class BrowserManager:
    """瀏覽器管理器"""
    
    @staticmethod
    def create_chrome_options(proxy: Optional[str] = None) -> Options:
        """
        創建Chrome瀏覽器選項
        
        Args:
            proxy: Proxy字串（格式：ip:port:username:password）
            
        Returns:
            Options: 配置好的Chrome選項
            
        Raises:
            BrowserError: 當配置失敗時
        """
        try:
            chrome_options = Options()
            
            # Proxy設定
            if proxy:
                parts = proxy.split(':')
                if len(parts) >= 4:
                    extension_path = ProxyExtensionManager.create_extension(
                        parts[0], parts[1], parts[2], parts[3]
                    )
                    chrome_options.add_extension(extension_path)
                    logger.info(f"已設定 Proxy: {parts[0]}:{parts[1]} (使用者: {parts[2]})")
            
            # 基本設定
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-popup-blocking")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--no-sandbox")
            
            # 網路優化
            chrome_options.add_argument("--disable-features=NetworkTimeServiceQuerying")
            chrome_options.add_argument("--dns-prefetch-disable")
            chrome_options.add_argument("--disable-background-networking")
            chrome_options.add_argument("--disable-sync")
            chrome_options.add_argument("--metrics-recording-only")
            chrome_options.add_argument("--disable-default-apps")
            chrome_options.add_argument("--no-first-run")
            chrome_options.add_argument("--disable-extensions")
            
            # 移除自動化痕跡
            chrome_options.add_experimental_option(
                "excludeSwitches", 
                ["enable-automation", "enable-logging"]
            )
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # 偏好設定
            chrome_options.add_experimental_option("prefs", {
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_settings.popups": 0,
                "profile.default_content_setting_values.media_stream_mic": 2,
                "profile.default_content_setting_values.media_stream_camera": 2,
                "profile.default_content_setting_values.sound": 2,
                "profile.default_content_setting_values.automatic_downloads": 2,
                "download.prompt_for_download": False,
                "download_restrictions": 3,
            })
            
            return chrome_options
            
        except Exception as e:
            raise BrowserError(f"創建Chrome選項失敗: {e}") from e
    
    @staticmethod
    def create_webdriver(proxy: Optional[str] = None) -> WebDriver:
        """
        創建WebDriver實例
        
        Args:
            proxy: Proxy字串（可選）
            
        Returns:
            WebDriver: WebDriver實例
            
        Raises:
            BrowserError: 當創建失敗時
        """
        try:
            service = Service(str(path_manager.chromedriver_path))
            chrome_options = BrowserManager.create_chrome_options(proxy)
            
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # 設定超時
            driver.set_page_load_timeout(GAME_CONFIG.page_load_timeout)
            driver.set_script_timeout(GAME_CONFIG.script_timeout)
            driver.implicitly_wait(GAME_CONFIG.implicit_wait)
            
            # 網路優化
            driver.execute_cdp_cmd("Network.enable", {})
            driver.execute_cdp_cmd("Network.emulateNetworkConditions", {
                "offline": False,
                "downloadThroughput": -1,
                "uploadThroughput": -1,
                "latency": 0
            })
            
            logger.info("已創建瀏覽器實例並優化網路設定")
            return driver
            
        except Exception as e:
            raise BrowserError(f"創建瀏覽器失敗: {e}") from e


# ==================== 繼續下一部分 ====================
# 由於程式碼過長，我將在下一個回應中繼續...
