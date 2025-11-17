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
import random
import sys
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
from webdriver_manager.chrome import ChromeDriverManager


# ==================== 全域變數 ====================

# 儲存最後一次取得的 Canvas 範圍，供 buy_free_game 使用
last_canvas_rect = None

# 截圖流程控制（確保只有一個瀏覽器執行截圖）
_template_capture_lock = threading.Lock()
_template_capturing = {}


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
    
    # 使用自定義格式化器（用戶友好模式）
    formatter = LogFormatter(
        '[%(levelname)s] %(message)s',
        datefmt='%H:%M:%S'
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
    BET_SIZE = 'bet'    # 調整下注金額
    BUY_FREE_GAME = 'b' # 購買免費遊戲
    SCREENSHOT = 's'    # 截取螢幕
    CAPTURE_AMOUNT = 'cap'  # 截取金額模板
    REPEAT_SPACE = 'r'  # 重複按空白鍵
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
    key_interval_min: int = 10
    key_interval_max: int = 15
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
        if self.key_interval_min <= 0 or self.key_interval_max <= 0:
            raise ConfigurationError(f"按鍵間隔必須為正數: min={self.key_interval_min}, max={self.key_interval_max}")
        if self.key_interval_min > self.key_interval_max:
            raise ConfigurationError(f"最小按鍵間隔不能大於最大間隔: min={self.key_interval_min}, max={self.key_interval_max}")
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
        # 支援 PyInstaller 打包後的路徑
        if getattr(sys, 'frozen', False):
            # 如果是打包後的 EXE
            self._project_root = Path(sys.executable).resolve().parent
        else:
            # 如果是原始 Python 腳本
            self._project_root = Path(__file__).resolve().parent.parent
    
    @property
    def project_root(self) -> Path:
        """取得專案根目錄"""
        return self._project_root
    
    @property
    def lib_dir(self) -> Path:
        """取得 lib 目錄"""
        lib_path = self._project_root / "lib"
        # 檢查目錄是否存在
        if not lib_path.exists():
            logger.warning(f"lib 目錄不存在: {lib_path}")
            logger.info(f"當前工作目錄: {Path.cwd()}")
            logger.info(f"專案根目錄: {self._project_root}")
        return lib_path
    
    @property
    def img_dir(self) -> Path:
        """取得 img 目錄"""
        img_path = self._project_root / "img"
        # 確保目錄存在
        if not img_path.exists():
            try:
                img_path.mkdir(parents=True, exist_ok=True)
                logger.debug(f"已建立 img 目錄: {img_path}")
            except Exception as e:
                logger.warning(f"無法建立 img 目錄: {e}")
        return img_path
    
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
    def proxys_file(self) -> Path:
        """取得 Proxy 列表檔案路徑"""
        return self.lib_dir / "user_proxys.txt"
    
    @property
    def chromedriver_path(self) -> Path:
        """
        取得 ChromeDriver 路徑 (已棄用 - 現在使用 WebDriver Manager)
        
        此方法保留用於向後相容，但不再使用。
        WebDriver Manager 會自動管理 ChromeDriver。
        
        Returns:
            Path: ChromeDriver 路徑
        """
        logger.warning("chromedriver_path 已棄用，現在使用 WebDriver Manager 自動管理驅動程式")
        system = platform.system().lower()
        driver_filename = "chromedriver.exe" if system == "windows" else "chromedriver"
        driver_path = self._project_root / driver_filename
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
    username: Optional[str] = None


# ==================== Proxy 擴充功能管理器 ====================


class LocalProxyServerManager:
    """本機 Proxy 中繼伺服器管理器
    
    使用 simple_proxy_server.py 建立本機 HTTP proxy 伺服器,
    每個瀏覽器實例使用獨立的本機 proxy port,
    本機 proxy 再轉發到上游的認證 proxy。
    """
    
    # 儲存所有執行中的 proxy 伺服器實例和執行緒
    _proxy_servers: Dict[int, Any] = {}
    _proxy_threads: Dict[int, threading.Thread] = {}
    
    @staticmethod
    def start_proxy_server(local_port: int, upstream_proxy: str) -> bool:
        """
        啟動本機 proxy 中繼伺服器
        
        Args:
            local_port: 本機監聽埠號（例如 9000）
            upstream_proxy: 上游 proxy 字串，格式為 "ip:port:user:pass"
            
        Returns:
            bool: 啟動成功返回 True
            
        Raises:
            BrowserError: 當啟動失敗時
        """
        try:
            # 動態匯入 SimpleProxyServer
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from simple_proxy_server import SimpleProxyServer
            
            # 建立 proxy 伺服器實例
            server = SimpleProxyServer(local_port, upstream_proxy)
            
            # 在新執行緒中啟動伺服器
            def run_server():
                server.start()
            
            server_thread = threading.Thread(target=run_server, daemon=True)
            server_thread.start()
            
            # 儲存實例和執行緒參考
            LocalProxyServerManager._proxy_servers[local_port] = server
            LocalProxyServerManager._proxy_threads[local_port] = server_thread
            
            # 等待伺服器啟動
            time.sleep(0.5)
            
            proxy_parts = upstream_proxy.split(':')
            logger.info(f"本機 Proxy 伺服器已啟動: 127.0.0.1:{local_port} -> {proxy_parts[0]}:{proxy_parts[1]}")
            return True
            
        except Exception as e:
            raise BrowserError(f"啟動本機 Proxy 伺服器失敗 (port={local_port}): {e}") from e
    
    @staticmethod
    def stop_proxy_server(local_port: int) -> None:
        """停止指定的 proxy 伺服器"""
        if local_port in LocalProxyServerManager._proxy_servers:
            server = LocalProxyServerManager._proxy_servers[local_port]
            server.running = False
            logger.info(f"已停止本機 Proxy 伺服器: 127.0.0.1:{local_port}")
            del LocalProxyServerManager._proxy_servers[local_port]
            if local_port in LocalProxyServerManager._proxy_threads:
                del LocalProxyServerManager._proxy_threads[local_port]
    
    @staticmethod
    def stop_all_servers() -> None:
        """停止所有 proxy 伺服器"""
        for local_port in list(LocalProxyServerManager._proxy_servers.keys()):
            LocalProxyServerManager.stop_proxy_server(local_port)


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
    
    @staticmethod
    def load_proxys() -> List[str]:
        """
        從檔案讀取 Proxy 列表
        
        Returns:
            List[str]: Proxy 列表
            
        Raises:
            ConfigurationError: 當檔案不存在或格式錯誤時
        """
        proxys_path = path_manager.proxys_file
        
        if not proxys_path.exists():
            raise ConfigurationError(f"找不到 Proxy 檔案: {proxys_path}")
        
        proxys = []
        
        try:
            with open(proxys_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for idx, line in enumerate(lines):
                line = line.strip()
                # 跳過空行
                if not line:
                    continue
                
                # 驗證格式: ip:port:username:password
                parts = line.split(':')
                if len(parts) != 4:
                    logger.warning(f"第 {idx + 1} 行格式錯誤,已跳過: {line}")
                    continue
                
                proxys.append(line)
            
            if not proxys:
                raise ConfigurationError("Proxy 檔案內容為空或格式錯誤")
            
            logger.info(f"已載入 {len(proxys)} 組 Proxy 資料")
            return proxys
            
        except Exception as e:
            if isinstance(e, ConfigurationError):
                raise
            raise ConfigurationError(f"讀取 Proxy 檔案失敗: {e}") from e


# ==================== 遊戲狀態管理器 ====================


class GameStateManager:
    """執行緒安全的遊戲狀態管理器"""
    
    def __init__(self):
        """初始化狀態管理器"""
        self._states: Dict[WebDriver, GameState] = {}
        self._lock = threading.RLock()  # 使用可重入鎖
    
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
    
    def set_username(self, driver: WebDriver, username: str) -> None:
        """
        設定使用者名稱
        
        Args:
            driver: WebDriver 實例
            username: 使用者名稱
        """
        with self._get_lock():
            state = self._ensure_state(driver)
            state.username = username
    
    def get_username(self, driver: WebDriver) -> Optional[str]:
        """
        取得使用者名稱
        
        Args:
            driver: WebDriver 實例
            
        Returns:
            Optional[str]: 使用者名稱
        """
        with self._get_lock():
            if driver in self._states:
                return self._states[driver].username
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
    
    def cleanup_all(self) -> None:
        """清理所有狀態"""
        with self._get_lock():
            count = len(self._states)
            self._states.clear()
            if count > 0:
                logger.info(f"已清理所有遊戲狀態")


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
    def create_chrome_options(local_proxy_port: Optional[int] = None) -> Options:
        """
        創建Chrome瀏覽器選項（使用本機 Proxy 中繼）
        
        Args:
            local_proxy_port: 本機 proxy 中繼埠號（例如 9000），設定後將使用 127.0.0.1:port
            
        Returns:
            Options: 配置好的Chrome選項
            
        Raises:
            BrowserError: 當配置失敗時
        """
        try:
            chrome_options = Options()
            
            # 本機 Proxy 設定
            if local_proxy_port:
                proxy_address = f"http://127.0.0.1:{local_proxy_port}"
                chrome_options.add_argument(f"--proxy-server={proxy_address}")
                logger.info(f"已設定本機 Proxy 中繼: {proxy_address}")
            
            # 基本設定
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-popup-blocking")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--no-sandbox")
            
            # Chrome 131+ 優化設定
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
    def create_webdriver(local_proxy_port: Optional[int] = None) -> WebDriver:
        """
        創建WebDriver實例（使用 WebDriver Manager 自動管理，配合本機 Proxy 中繼）
        
        Args:
            local_proxy_port: 本機 proxy 中繼埠號（可選）
            
        Returns:
            WebDriver: WebDriver實例
            
        Raises:
            BrowserError: 當創建失敗時
        """
        try:
            # 使用 WebDriver Manager 自動下載並管理 ChromeDriver
            logger.info("正在使用 WebDriver Manager 取得 ChromeDriver...")
            service = Service(ChromeDriverManager().install())
            
            chrome_options = BrowserManager.create_chrome_options(local_proxy_port)
            
            logger.info("正在啟動 Chrome 瀏覽器...")
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # 取得 Chrome 版本
            try:
                chrome_version = driver.capabilities.get('browserVersion', 'unknown')
                logger.info(f"Chrome 版本: {chrome_version}")
            except Exception:
                pass
            
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
            
            logger.info("✓ 瀏覽器實例已創建並完成設定")
            return driver
            
        except Exception as e:
            raise BrowserError(f"創建瀏覽器失敗: {e}") from e


# ==================== 繼續下一部分 ====================
# 由於程式碼過長，我將在下一個回應中繼續...
"""
這是 main_refactored.py 的第二部分
包含：登入管理器、遊戲控制器、視窗管理器、主程式邏輯
"""

# ==================== 登入管理器 ====================


class LoginManager:
    """登入流程管理器"""
    
    def __init__(self, driver: WebDriver, credential: UserCredential):
        """
        初始化登入管理器
        
        Args:
            driver: WebDriver實例
            credential: 使用者憑證
        """
        self.driver = driver
        self.credential = credential
        self.username = credential.username
    
    def perform_login(self) -> bool:
        """
        執行登入操作
        
        Returns:
            bool: 登入成功返回True
            
        Raises:
            LoginError: 當登入失敗時
        """
        try:
            logger.info(f"[{self.username}] 開始登入...")
            
            # 輸入帳號
            username_input = self.driver.find_element(By.XPATH, ELEMENT_SELECTOR.USERNAME_INPUT)
            username_input.clear()
            username_input.send_keys(self.credential.username)
            
            # 輸入密碼
            password_input = self.driver.find_element(By.XPATH, ELEMENT_SELECTOR.PASSWORD_INPUT)
            password_input.clear()
            password_input.send_keys(self.credential.password)
            
            # 點擊登入按鈕
            login_button = self.driver.find_element(By.XPATH, ELEMENT_SELECTOR.LOGIN_BUTTON)
            login_button.click()
            
            time.sleep(5)
            
            logger.info(f"[{self.username}] 登入成功")
            return True
            
        except NoSuchElementException as e:
            raise LoginError(f"[{self.username}] 找不到登入元素: {e}") from e
        except Exception as e:
            raise LoginError(f"[{self.username}] 登入過程發生錯誤: {e}") from e
    
    def wait_for_image(self, template_path: Path, timeout: int = 60) -> bool:
        """
        等待圖片出現
        
        Args:
            template_path: 模板圖片路徑
            timeout: 超時時間（秒）
            
        Returns:
            bool: 在超時前找到返回True
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                screenshot = self.driver.get_screenshot_as_png()
                screenshot_np = ImageProcessor.screenshot_to_array(screenshot)
                screenshot_gray = ImageProcessor.to_grayscale(screenshot_np)
                
                matched, similarity, position = ImageProcessor.match_template(
                    screenshot_gray, 
                    template_path, 
                    GAME_CONFIG.image_match_threshold
                )
                
                if matched:
                    return True
                    
            except ImageDetectionError as e:
                logger.warning(f"[{self.username}] 圖片檢測錯誤: {e}")
            
            time.sleep(GAME_CONFIG.image_detect_interval)
        
        logger.warning(f"[{self.username}] 等待圖片超時 ({timeout}秒)")
        return False
    
    def wait_for_image_disappear(self, template_path: Path, timeout: int = 60) -> bool:
        """
        等待圖片消失
        
        Args:
            template_path: 模板圖片路徑
            timeout: 超時時間（秒）
            
        Returns:
            bool: 在超時前消失返回True
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                screenshot = self.driver.get_screenshot_as_png()
                screenshot_np = ImageProcessor.screenshot_to_array(screenshot)
                screenshot_gray = ImageProcessor.to_grayscale(screenshot_np)
                
                matched, _, _ = ImageProcessor.match_template(
                    screenshot_gray, 
                    template_path, 
                    GAME_CONFIG.image_match_threshold
                )
                
                if not matched:
                    return True
                    
            except ImageDetectionError as e:
                logger.warning(f"[{self.username}] 圖片檢測錯誤: {e}")
            
            time.sleep(GAME_CONFIG.image_detect_interval)
        
        logger.warning(f"[{self.username}] 等待圖片消失超時 ({timeout}秒)")
        return False
    
    def navigate_to_game(self) -> bool:
        """
        導航到遊戲頁面
        
        Returns:
            bool: 成功返回True
            
        Raises:
            LoginError: 當導航失敗時
        """
        try:
            logger.info(f"[{self.username}] 正在進入遊戲...")
            self.driver.get(URL_CONFIG.GAME_PAGE)
            time.sleep(3)
            
            # 設定視窗大小
            self.driver.set_window_size(WINDOW_CONFIG.width, WINDOW_CONFIG.height)
            
            # === 步驟 1: 檢查 lobby_login.png 是否存在 ===
            lobby_login_path = path_manager.lobby_login_image
            
            if not lobby_login_path.exists():
                # 使用鎖確保只有一個瀏覽器執行截圖
                with _template_capture_lock:
                    # 再次檢查（可能已被其他執行緒建立）
                    if not lobby_login_path.exists():
                        logger.warning(f"[{self.username}] ⚠️  未找到 lobby_login.png 模板圖片")
                        logger.info(f"[{self.username}] 這似乎是第一次登入，需要建立模板圖片")
                        logger.info(f"[{self.username}] 請確保遊戲已載入到大廳登入畫面")
                        
                        # 標記正在截圖
                        _template_capturing['lobby_login'] = True
                        
                        # 互動式截圖流程
                        if not self._capture_lobby_login_template():
                            _template_capturing['lobby_login'] = False
                            raise LoginError(f"[{self.username}] 無法建立 lobby_login.png 模板")
                        
                        _template_capturing['lobby_login'] = False
                        logger.info(f"[{self.username}] ✓ 模板圖片已成功建立")
                    else:
                        logger.info(f"[{self.username}] 模板已由其他瀏覽器建立，繼續執行...")
            
            # 等待並檢測圖片
            logger.info(f"[{self.username}] 步驟 1: 正在檢測 lobby_login.png...")
            if not self.wait_for_image(
                lobby_login_path, 
                GAME_CONFIG.image_detect_timeout
            ):
                raise LoginError(f"[{self.username}] 步驟 1 失敗：未檢測到 lobby_login.png")
            
            logger.info(f"[{self.username}] 步驟 1 完成：已確認 lobby_login.png 存在")
            
            # === 切入 iframe ===
            logger.info(f"[{self.username}] 正在切換到遊戲 iframe...")
            iframe = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, ELEMENT_SELECTOR.GAME_IFRAME))
            )
            self.driver.switch_to.frame(iframe)
            logger.info(f"[{self.username}] 已成功切換到 iframe")
            
            # === 取得 Canvas 區域 ===
            logger.info(f"[{self.username}] 正在取得 Canvas 座標...")
            rect = self.driver.execute_script(f"""
                const canvas = document.getElementById('{ELEMENT_SELECTOR.GAME_CANVAS}');
                const r = canvas.getBoundingClientRect();
                return {{x: r.left, y: r.top, w: r.width, h: r.height}};
            """)
            logger.info(f"[{self.username}] Canvas 區域: x={rect['x']}, y={rect['y']}, w={rect['w']}, h={rect['h']}")
            
            # 儲存到全域變數供 buy_free_game 使用
            global last_canvas_rect
            last_canvas_rect = rect
            
            # === 計算點擊座標 ===
            start_x = rect["x"] + rect["w"] * CLICK_COORD.START_GAME_X_RATIO
            start_y = rect["y"] + rect["h"] * CLICK_COORD.START_GAME_Y_RATIO
            confirm_x = rect["x"] + rect["w"] * CLICK_COORD.MACHINE_CONFIRM_X_RATIO
            confirm_y = rect["y"] + rect["h"] * CLICK_COORD.MACHINE_CONFIRM_Y_RATIO
            
            logger.info(f"[{self.username}] 開始遊戲按鈕座標: ({start_x:.1f}, {start_y:.1f})")
            logger.info(f"[{self.username}] 確認按鈕座標: ({confirm_x:.1f}, {confirm_y:.1f})")
            
            # === 步驟 2: 點擊開始遊戲按鈕 ===
            time.sleep(1)
            logger.info(f"[{self.username}] 步驟 2: 點擊開始遊戲按鈕...")
            self._click_coordinate(start_x, start_y)
            
            logger.info(f"[{self.username}] 步驟 2: 等待 lobby_login.png 消失...")
            if not self.wait_for_image_disappear(path_manager.lobby_login_image, 30):
                raise LoginError(f"[{self.username}] 步驟 2 失敗：lobby_login.png 未消失")
            
            logger.info(f"[{self.username}] 步驟 2 完成：lobby_login.png 已消失")
            
            # === 步驟 3: 檢查 lobby_confirm.png 是否存在 ===
            lobby_confirm_path = path_manager.lobby_confirm_image
            
            if not lobby_confirm_path.exists():
                # 使用鎖確保只有一個瀏覽器執行截圖
                with _template_capture_lock:
                    # 再次檢查（可能已被其他執行緒建立）
                    if not lobby_confirm_path.exists():
                        logger.info(f"[{self.username}] 正在建立 lobby_confirm.png 模板...")
                        
                        # 標記正在截圖
                        _template_capturing['lobby_confirm'] = True
                        
                        # 使用確認按鈕座標截取模板
                        try:
                            screenshot = self.driver.get_screenshot_as_png()
                            screenshot_img = Image.open(io.BytesIO(screenshot))
                            
                            # 獲取實際截圖尺寸
                            img_width, img_height = screenshot_img.size
                            
                            # 使用已計算好的確認按鈕座標
                            center_x = int(confirm_x)
                            center_y = int(confirm_y)
                            
                            # 固定像素偏移：上下左右各20px
                            crop_left = max(0, center_x - 20)
                            crop_top = max(0, center_y - 20)
                            crop_right = min(img_width, center_x + 20)
                            crop_bottom = min(img_height, center_y + 20)
                            
                            logger.info(f"[{self.username}] 截圖尺寸: {img_width}x{img_height}, 確認按鈕座標: ({center_x}, {center_y})")
                            
                            cropped_img = screenshot_img.crop((crop_left, crop_top, crop_right, crop_bottom))
                            
                            # 儲存圖片
                            lobby_confirm_path.parent.mkdir(parents=True, exist_ok=True)
                            cropped_img.save(lobby_confirm_path)
                            
                            logger.info(f"[{self.username}] ✓ lobby_confirm.png 已建立")
                        except Exception as e:
                            _template_capturing['lobby_confirm'] = False
                            raise LoginError(f"[{self.username}] 建立 lobby_confirm.png 失敗: {e}")
                        
                        _template_capturing['lobby_confirm'] = False
                    else:
                        logger.info(f"[{self.username}] 模板已由其他瀏覽器建立，繼續執行...")
            
            # 等待並檢測圖片
            logger.info(f"[{self.username}] 步驟 3: 正在檢測 lobby_confirm.png...")
            if not self.wait_for_image(lobby_confirm_path, 30):
                raise LoginError(f"[{self.username}] 步驟 3 失敗：未檢測到 lobby_confirm.png")
            
            logger.info(f"[{self.username}] 步驟 3 完成：已確認 lobby_confirm.png 存在")
            
            # === 步驟 4: 點擊確認按鈕 ===
            time.sleep(1)
            logger.info(f"[{self.username}] 步驟 4: 點擊確認按鈕...")
            self._click_coordinate(confirm_x, confirm_y)
            
            logger.info(f"[{self.username}] 步驟 4: 等待 lobby_confirm.png 消失...")
            if not self.wait_for_image_disappear(path_manager.lobby_confirm_image, 30):
                raise LoginError(f"[{self.username}] 步驟 4 失敗：lobby_confirm.png 未消失")
            
            logger.info(f"[{self.username}] 步驟 4 完成：lobby_confirm.png 已消失")
            
            # === 步驟 5: 成功進入遊戲 ===
            logger.info(f"[{self.username}] 步驟 5: 已成功進入遊戲控制模式")
            time.sleep(2)
            return True
            
        except TimeoutException as e:
            raise LoginError(f"[{self.username}] 頁面載入超時: {e}") from e
        except Exception as e:
            if isinstance(e, LoginError):
                raise
            raise LoginError(f"[{self.username}] 導航到遊戲失敗: {e}") from e
    
    def _click_coordinate(self, x: float, y: float) -> None:
        """
        點擊指定座標
        
        Args:
            x: X座標
            y: Y座標
        """
        for event in ["mousePressed", "mouseReleased"]:
            self.driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
                "type": event,
                "x": x,
                "y": y,
                "button": "left",
                "clickCount": 1
            })
    
    def _capture_lobby_login_template(self) -> bool:
        """
        互動式截取 lobby_login.png 模板
        
        Returns:
            bool: 成功返回True
        """
        logger.info(f"[{self.username}] ")
        logger.info(f"[{self.username}] ╔═══════════════════════════════════════════════╗")
        logger.info(f"[{self.username}] ║     需要建立 lobby_login.png 模板圖片        ║")
        logger.info(f"[{self.username}] ╠═══════════════════════════════════════════════╣")
        logger.info(f"[{self.username}] ║  請確保：                                    ║")
        logger.info(f"[{self.username}] ║  1. 遊戲已載入到大廳登入畫面                 ║")
        logger.info(f"[{self.username}] ║  2. 可以看到「開始遊戲」按鈕                 ║")
        logger.info(f"[{self.username}] ║  3. 畫面穩定，沒有動畫或載入中               ║")
        logger.info(f"[{self.username}] ╠═══════════════════════════════════════════════╣")
        logger.info(f"[{self.username}] ║  指令：                                      ║")
        logger.info(f"[{self.username}] ║    's' - 截取當前畫面作為模板               ║")
        logger.info(f"[{self.username}] ║    'q' - 取消並退出                         ║")
        logger.info(f"[{self.username}] ╚═══════════════════════════════════════════════╝")
        logger.info(f"[{self.username}] ")
        
        max_attempts = 5
        for attempt in range(1, max_attempts + 1):
            try:
                user_input = input(f"[{self.username}] 請輸入指令 (嘗試 {attempt}/{max_attempts}): ").strip().lower()
                
                if user_input == 'q':
                    logger.info(f"[{self.username}] 用戶取消截圖操作")
                    return False
                
                elif user_input == 's':
                    logger.info(f"[{self.username}] 正在截取畫面...")
                    
                    # 截取畫面
                    screenshot = self.driver.get_screenshot_as_png()
                    lobby_login_path = path_manager.lobby_login_image
                    
                    # 確保目錄存在
                    lobby_login_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # 儲存圖片
                    with open(lobby_login_path, 'wb') as f:
                        f.write(screenshot)
                    
                    logger.info(f"[{self.username}] ✓ 圖片已儲存至: {lobby_login_path}")
                    
                    # 自動驗證
                    logger.info(f"[{self.username}] 正在驗證模板圖片...")
                    time.sleep(1)
                    
                    # 重新截圖進行比對
                    verify_screenshot = self.driver.get_screenshot_as_png()
                    verify_np = ImageProcessor.screenshot_to_array(verify_screenshot)
                    verify_gray = ImageProcessor.to_grayscale(verify_np)
                    
                    # 使用新建立的模板進行匹配
                    matched, similarity, position = ImageProcessor.match_template(
                        verify_gray,
                        lobby_login_path,
                        GAME_CONFIG.image_match_threshold
                    )
                    
                    if matched:
                        logger.info(f"[{self.username}] ✓ 驗證成功！相似度: {similarity:.3f}")
                        logger.info(f"[{self.username}] ✓ 模板圖片可以正常使用")
                        return True
                    else:
                        logger.warning(f"[{self.username}] ✗ 驗證失敗（相似度: {similarity:.3f}）")
                        logger.warning(f"[{self.username}] 可能原因：畫面不穩定或有動畫")
                        logger.info(f"[{self.username}] 請等待畫面穩定後重試")
                        
                        # 刪除無效的模板
                        if lobby_login_path.exists():
                            lobby_login_path.unlink()
                            logger.info(f"[{self.username}] 已刪除無效的模板圖片")
                        
                        if attempt < max_attempts:
                            continue
                        else:
                            return False
                
                else:
                    logger.warning(f"[{self.username}] 無效的指令，請輸入 's' 或 'q'")
                    
            except (EOFError, KeyboardInterrupt):
                logger.info(f"\n[{self.username}] 操作已中斷")
                return False
            except Exception as e:
                logger.error(f"[{self.username}] 截圖過程發生錯誤: {e}")
                if attempt < max_attempts:
                    continue
                else:
                    return False
        
        logger.error(f"[{self.username}] 已達最大嘗試次數，無法建立有效的模板")
        return False
    
    @staticmethod
    def login_with_retry(driver: WebDriver, credential: UserCredential, 
                        max_retries: int = 3) -> bool:
        """
        帶重試的完整登入流程
        
        Args:
            driver: WebDriver實例
            credential: 使用者憑證
            max_retries: 最大重試次數
            
        Returns:
            bool: 登入成功返回True
        """
        manager = LoginManager(driver, credential)
        
        for attempt in range(max_retries):
            try:
                logger.info(f"[{credential.username}] 開始登入流程（嘗試 {attempt + 1}/{max_retries}）")
                
                # 第一次嘗試：開啟登入頁面並登入
                if attempt == 0:
                    driver.get(URL_CONFIG.LOGIN_PAGE)
                    time.sleep(2)
                    
                    # 執行登入
                    manager.perform_login()
                    time.sleep(2)
                else:
                    # 重試時直接導向遊戲頁面
                    logger.info(f"[{credential.username}] 重試中，直接導向遊戲頁面")
                
                # 導航到遊戲
                manager.navigate_to_game()
                
                logger.info(f"[{credential.username}] 登入流程成功完成")
                return True
                
            except LoginError as e:
                logger.error(f"[{credential.username}] 登入失敗（嘗試 {attempt + 1}/{max_retries}）: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"[{credential.username}] 準備重試...")
                    time.sleep(GAME_CONFIG.retry_delay)
                    continue
                logger.error(f"[{credential.username}] 已達最大重試次數，登入失敗")
                return False
            except Exception as e:
                logger.error(f"[{credential.username}] 未預期的錯誤: {e}")
                if attempt < max_retries - 1:
                    time.sleep(GAME_CONFIG.retry_delay)
                    continue
                return False
        
        return False


# ==================== 遊戲控制器 ====================


class GameController:
    """遊戲控制器"""
    
    def __init__(self, driver: WebDriver):
        """
        初始化遊戲控制器
        
        Args:
            driver: WebDriver實例
        """
        self.driver = driver
        self.username = game_state_manager.get_username(driver) or "未知"
    
    def send_key(self, key_config: Dict[str, Any]) -> bool:
        """
        發送鍵盤事件
        
        Args:
            key_config: 按鍵配置
            
        Returns:
            bool: 成功返回True
        """
        try:
            for event_type in ["keyDown", "keyUp"]:
                self.driver.execute_cdp_cmd("Input.dispatchKeyEvent", {
                    "type": event_type,
                    "key": key_config["key"],
                    "code": key_config["code"],
                    "windowsVirtualKeyCode": key_config["windowsVirtualKeyCode"],
                    "nativeVirtualKeyCode": key_config["nativeVirtualKeyCode"]
                })
            return True
        except Exception as e:
            logger.warning(f"發送按鍵失敗: {e}")
            return False
    
    def send_space(self) -> bool:
        """發送空白鍵"""
        return self.send_key(KEYBOARD_KEY.SPACE)
    
    def send_arrow_left(self) -> bool:
        """發送左方向鍵"""
        return self.send_key(KEYBOARD_KEY.ARROW_LEFT)
    
    def send_arrow_right(self) -> bool:
        """發送右方向鍵"""
        return self.send_key(KEYBOARD_KEY.ARROW_RIGHT)
    
    def switch_to_game_frame(self) -> bool:
        """切換到遊戲iframe"""
        try:
            self.driver.switch_to.default_content()
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            if iframes:
                self.driver.switch_to.frame(iframes[0])
                logger.info("已切換到遊戲 iframe")
                return True
        except Exception as e:
            logger.debug(f"切換 iframe 失敗: {e}")
        return False
    
    def get_current_betsize(self) -> Optional[float]:
        """
        取得當前下注金額
        
        Returns:
            Optional[float]: 當前金額，失敗返回None
        """
        try:
            logger.info(f"[{self.username}] 開始查詢當前下注金額...")
            
            # 截取整個瀏覽器截圖
            screenshot = self.driver.get_screenshot_as_png()
            screenshot_np = ImageProcessor.screenshot_to_array(screenshot)
            screenshot_gray = ImageProcessor.to_grayscale(screenshot_np)
            
            # 與資料夾中的圖片進行比對
            matched_amount = self._compare_betsize_images(screenshot_gray)
            
            if matched_amount:
                try:
                    amount_value = float(matched_amount)
                    if amount_value in GAME_BETSIZE:
                        logger.info(f"[{self.username}] 當前下注金額: {amount_value}")
                        return amount_value
                    else:
                        logger.warning(f"金額 {matched_amount} 不在 GAME_BETSIZE 列表中")
                except ValueError:
                    logger.error(f"無法將 {matched_amount} 轉換為數字")
            else:
                logger.warning("無法識別當前下注金額")
            
            return None
            
        except Exception as e:
            logger.error(f"查詢下注金額時發生錯誤: {e}")
            return None
    
    def _compare_betsize_images(self, screenshot_gray: np.ndarray) -> Optional[str]:
        """
        使用 bet_size 資料夾中的圖片比對
        
        Args:
            screenshot_gray: 截圖（灰階）
            
        Returns:
            Optional[str]: 匹配的金額
        """
        try:
            bet_size_dir = path_manager.bet_size_dir
            if not bet_size_dir.exists():
                logger.warning(f"bet_size 資料夾不存在: {bet_size_dir}，嘗試建立...")
                try:
                    bet_size_dir.mkdir(parents=True, exist_ok=True)
                    logger.info(f"已建立 bet_size 資料夾: {bet_size_dir}")
                except Exception as e:
                    logger.error(f"無法建立 bet_size 資料夾: {e}")
                    return None
            
            # 取得所有 png 圖片
            image_files = sorted(bet_size_dir.glob("*.png"))
            if not image_files:
                logger.warning(f"bet_size 資料夾中沒有圖片")
                return None
            
            logger.info(f"[{self.username}] 開始比對 {len(image_files)} 張圖片...")
            
            best_match_score = 0.0
            best_match_amount = None
            
            for image_file in image_files:
                matched, similarity, _ = ImageProcessor.match_template(
                    screenshot_gray,
                    image_file,
                    GAME_CONFIG.image_match_threshold
                )
                
                if similarity > best_match_score:
                    best_match_score = similarity
                    best_match_amount = image_file.stem
            
            if best_match_score >= GAME_CONFIG.image_match_threshold:
                logger.info(f"[{self.username}] 找到匹配金額：{best_match_amount} (相似度：{best_match_score:.3f})")
                return best_match_amount
            else:
                logger.warning(f"未找到匹配圖片 (最高相似度：{best_match_score:.3f})")
                return None
                
        except Exception as e:
            logger.error(f"比對圖片時發生錯誤: {e}")
            return None
    
    def _click_betsize_button(self, x: float, y: float) -> None:
        """
        點擊下注金額調整按鈕
        
        Args:
            x: X 座標 (基於 600x400 視窗)
            y: Y 座標 (基於 600x400 視窗)
        """
        import io
        from PIL import Image
        
        screenshot = self.driver.get_screenshot_as_png()
        screenshot_img = Image.open(io.BytesIO(screenshot))
        
        # 獲取實際截圖尺寸
        img_width, img_height = screenshot_img.size
        
        # 計算相對座標比例（基於 600x400）
        x_ratio = x / 600
        y_ratio = y / 400
        
        # 應用到實際截圖尺寸
        actual_x = int(img_width * x_ratio)
        actual_y = int(img_height * y_ratio)
        
        # 使用轉換後的實際座標進行點擊
        for ev in ["mousePressed", "mouseReleased"]:
            self.driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
                "type": ev,
                "x": actual_x,
                "y": actual_y,
                "button": "left",
                "clickCount": 1
            })
    
    def adjust_betsize(self, target_amount: float, max_attempts: int = 200) -> bool:
        """
        調整下注金額到目標值
        
        Args:
            target_amount: 目標金額
            max_attempts: 最大嘗試次數
            
        Returns:
            bool: 調整成功返回True
            
        Raises:
            GameControlError: 當調整失敗時
        """
        try:
            # 檢查目標金額
            if target_amount not in GAME_BETSIZE:
                raise GameControlError(f"目標金額 {target_amount} 不在可用金額列表中")
            
            logger.info(f"目標金額: {target_amount}")
            
            # 取得當前金額
            current_amount = self.get_current_betsize()
            if current_amount is None:
                raise GameControlError("無法識別當前金額")
            
            logger.info(f"當前金額: {current_amount}")
            
            # 檢查是否已是目標金額
            if current_amount == target_amount:
                logger.info("當前金額已是目標金額，無需調整")
                return True
            
            # 計算需要調整的次數和方向
            current_index = GAME_BETSIZE.index(current_amount)
            target_index = GAME_BETSIZE.index(target_amount)
            diff = target_index - current_index
            
            # 設定點擊座標（基於 600x400 視窗）
            if diff > 0:
                # 增加金額
                click_x = 440
                click_y = 370
                direction = "增加"
                estimated_steps = diff
            else:
                # 減少金額
                click_x = 360
                click_y = 370
                direction = "減少"
                estimated_steps = abs(diff)
            
            logger.info(f"預估需要點擊{direction}按鈕約 {estimated_steps} 次")
            
            # 開始調整
            for i in range(estimated_steps):
                self._click_betsize_button(click_x, click_y)
                logger.info(f"已點擊 {direction} 按鈕 ({i + 1}/{estimated_steps})")
                time.sleep(0.3)
            
            time.sleep(1)
            
            # 驗證並微調
            logger.info("開始驗證調整結果...")
            for attempt in range(max_attempts):
                current_amount = self.get_current_betsize()
                
                if current_amount is None:
                    logger.warning(f"驗證失敗：無法識別金額 (嘗試 {attempt + 1}/{max_attempts})")
                    time.sleep(0.5)
                    continue
                
                if current_amount == target_amount:
                    logger.info(f"[{self.username}] ✓ 調整成功! 當前金額: {current_amount}")
                    return True
                
                logger.info(f"[{self.username}] 當前金額 {current_amount}，目標 {target_amount}，繼續調整...")
                
                # 根據當前金額決定點擊哪個按鈕
                if current_amount < target_amount:
                    self._click_betsize_button(440, 370)  # 增加
                else:
                    self._click_betsize_button(360, 370)  # 減少
                
                time.sleep(0.5)
            
            raise GameControlError(f"調整失敗，已達最大嘗試次數 ({max_attempts})")
            
        except Exception as e:
            if isinstance(e, GameControlError):
                raise
            raise GameControlError(f"調整金額時發生錯誤: {e}") from e
    
    def take_screenshot(self) -> bool:
        """
        截取螢幕並保存到桌面
        
        Returns:
            bool: 成功返回True
        """
        try:
            from datetime import datetime
            
            desktop_path = Path.home() / "Desktop"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            filepath = desktop_path / filename
            
            screenshot = self.driver.get_screenshot_as_png()
            
            with open(filepath, 'wb') as f:
                f.write(screenshot)
            
            logger.info(f"✓ 截圖已儲存至：{filepath}")
            return True
            
        except Exception as e:
            logger.error(f"截圖失敗：{e}")
            return False
    
    def buy_free_game(self) -> bool:
        """
        購買免費遊戲
        
        Returns:
            bool: 成功返回True
        """
        try:
            global last_canvas_rect
            
            if last_canvas_rect is None:
                logger.error("Canvas 範圍未初始化，請先進入遊戲")
                return False
            
            rect = last_canvas_rect
            
            # === 第一次點擊（freegame 區域） ===
            freegame_x = rect["x"] + rect["w"] * 0.23
            freegame_y = rect["y"] + rect["h"] * 1.05
            
            logger.info("點擊免費遊戲區域...")
            for ev in ["mousePressed", "mouseReleased"]:
                self.driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
                    "type": ev,
                    "x": freegame_x,
                    "y": freegame_y,
                    "button": "left",
                    "clickCount": 1
                })
            time.sleep(2)
            
            # === 第二次點擊（Canvas 確認按鈕） ===
            start_x = rect["x"] + rect["w"] * 0.65
            start_y = rect["y"] + rect["h"] * 1.2
            
            logger.info("點擊確認按鈕...")
            for ev in ["mousePressed", "mouseReleased"]:
                self.driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
                    "type": ev,
                    "x": start_x,
                    "y": start_y,
                    "button": "left",
                    "clickCount": 1
                })
            
            # === 購買完成後自動按一次空白鍵 ===
            logger.info("購買完成，等待 10 秒後開始遊戲...")
            time.sleep(10)
            logger.info("按下空白鍵開始遊戲...")
            self.send_key(KEYBOARD_KEY.SPACE)
            
            logger.info("免費遊戲購買完成！")
            logger.info("您現在可以手動操作遊戲")
            
            # === 等待用戶按 'o' 返回指令選單 ===
            while True:
                user_input = input("輸入 'o' 返回指令選單：").strip().lower()
                if user_input == "o":
                    logger.info("返回指令選單...")
                    break
            
            return True
            
        except Exception as e:
            logger.error(f"購買免費遊戲失敗：{e}")
            return False
        finally:
            try:
                self.driver.switch_to.default_content()
            except Exception:
                pass


# ==================== 遊戲執行器 ====================


class GameExecutor:
    """遊戲執行器"""
    
    def __init__(self, driver: WebDriver):
        """
        初始化遊戲執行器
        
        Args:
            driver: WebDriver實例
        """
        self.driver = driver
        self.controller = GameController(driver)
    
    def execute_with_rules(self) -> None:
        """按規則執行遊戲"""
        try:
            # 切換到遊戲 iframe
            self.controller.switch_to_game_frame()
            
            # 取得規則列表
            rules = game_state_manager.get_rules(self.driver)
            
            if not rules:
                logger.warning("沒有可用的遊戲規則，使用預設模式")
                self._execute_default_mode()
                return
            
            # 按規則執行
            for rule_idx, rule in enumerate(rules, 1):
                if not game_state_manager.is_running(self.driver):
                    logger.info("遊戲已暫停")
                    break
                
                logger.info(f"開始執行規則 {rule_idx}/{len(rules)}: 金額 {rule.betsize}, 持續 {rule.duration_minutes} 分鐘")
                
                # 調整金額
                try:
                    if not self.controller.adjust_betsize(rule.betsize):
                        logger.error(f"調整金額失敗，跳過規則 {rule_idx}")
                        continue
                except GameControlError as e:
                    logger.error(f"調整金額錯誤：{e}，跳過規則 {rule_idx}")
                    continue
                
                logger.info(f"金額已調整為 {rule.betsize}，開始執行 {rule.duration_minutes} 分鐘")
                
                # 計算結束時間
                end_time = time.time() + rule.duration_seconds
                press_count = 0
                
                # 在指定時間內持續按空白鍵
                while time.time() < end_time:
                    if not game_state_manager.is_running(self.driver):
                        logger.info("遊戲已暫停")
                        return
                    
                    self.controller.send_space()
                    press_count += 1
                    
                    remaining_seconds = int(end_time - time.time())
                    logger.info(f"規則 {rule_idx}: 已按 {press_count} 次，剩餘 {remaining_seconds} 秒")
                    
                    # 使用隨機間隔
                    wait_seconds = random.randint(GAME_CONFIG.key_interval_min, GAME_CONFIG.key_interval_max)
                    for _ in range(wait_seconds):
                        if not game_state_manager.is_running(self.driver):
                            logger.info("遊戲已暫停")
                            return
                        if time.time() >= end_time:
                            break
                        time.sleep(1)
                
                logger.info(f"規則 {rule_idx} 執行完成（共按 {press_count} 次空白鍵）")
            
            logger.info("所有規則執行完畢，遊戲停止")
            game_state_manager.set_running(self.driver, False)
            
        except Exception as e:
            logger.error(f"遊戲執行發生錯誤：{e}")
        finally:
            game_state_manager.set_running(self.driver, False)
            game_state_manager.set_thread(self.driver, None)
    
    def _execute_default_mode(self) -> None:
        """執行預設模式（每10~15秒隨機按一次空白鍵）"""
        logger.info("使用預設模式執行遊戲")
        
        while True:
            if not game_state_manager.is_running(self.driver):
                break
            
            self.controller.send_space()
            
            # 使用隨機間隔
            wait_seconds = random.randint(GAME_CONFIG.key_interval_min, GAME_CONFIG.key_interval_max)
            for _ in range(wait_seconds):
                if not game_state_manager.is_running(self.driver):
                    break
                time.sleep(1)


# ==================== 視窗管理器 ====================


class WindowManager:
    """視窗管理器"""
    
    @staticmethod
    def arrange_windows(drivers: List[Optional[WebDriver]]) -> int:
        """
        按網格模式排列視窗
        
        Args:
            drivers: WebDriver實例列表
            
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


# ==================== 主程式控制器 ====================


class MainController:
    """主程式控制器"""
    
    def __init__(self):
        """初始化主程式控制器"""
        self.drivers: List[Optional[WebDriver]] = []
        self.credentials: List[UserCredential] = []
        self.repeat_space_running = False
        self.repeat_space_thread: Optional[threading.Thread] = None
    
    def _check_environment(self) -> None:
        """檢查執行環境"""
        logger.info("檢查執行環境...")
        
        # 顯示路徑資訊
        logger.info(f"專案根目錄: {path_manager.project_root}")
        logger.info(f"當前工作目錄: {Path.cwd()}")
        
        # 檢查是否為打包後的 EXE
        if getattr(sys, 'frozen', False):
            logger.info("執行模式: EXE (打包版本)")
            logger.info(f"執行檔路徑: {sys.executable}")
        else:
            logger.info("執行模式: Python 腳本")
        
        # 檢查必要目錄
        lib_dir = path_manager.lib_dir
        img_dir = path_manager.img_dir
        
        if not lib_dir.exists():
            logger.error(f"✗ 缺少 lib 目錄: {lib_dir}")
            logger.error("請確保 lib 目錄與執行檔在同一層級")
            raise ConfigurationError("找不到 lib 目錄")
        else:
            logger.info(f"✓ lib 目錄: {lib_dir}")
        
        if not img_dir.exists():
            logger.warning(f"⚠ img 目錄不存在，將自動建立: {img_dir}")
            try:
                img_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"✓ 已建立 img 目錄")
            except Exception as e:
                logger.warning(f"無法建立 img 目錄: {e}")
        else:
            logger.info(f"✓ img 目錄: {img_dir}")
        
        # 檢查必要檔案
        credentials_file = path_manager.credentials_file
        if not credentials_file.exists():
            logger.error(f"✗ 缺少帳號檔案: {credentials_file}")
            raise ConfigurationError("找不到 user_credentials.txt")
        else:
            logger.info(f"✓ 帳號檔案: {credentials_file}")
        
        logger.info("環境檢查完成\n")
    
    def load_configurations(self) -> bool:
        """
        載入配置
        
        Returns:
            bool: 成功返回True
        """
        try:
            self.credentials = ConfigLoader.load_credentials()
            return True
        except ConfigurationError as e:
            logger.error(f"載入配置失敗: {e}")
            return False
    
    def get_browser_count(self) -> Optional[int]:
        """
        取得使用者輸入的瀏覽器數量
        
        Returns:
            Optional[int]: 瀏覽器數量，取消返回None
        """
        max_allowed = min(GAME_CONFIG.max_accounts, len(self.credentials))
        
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
                return None
    
    def launch_browsers(self, count: int) -> int:
        """
        並行啟動多個瀏覽器 (使用本地 proxy 中繼)
        
        Args:
            count: 要啟動的數量
            
        Returns:
            int: 成功啟動的數量
        """
        # 載入 proxy 列表
        try:
            proxys = ConfigLoader.load_proxys()
        except ConfigurationError as e:
            logger.error(f"載入 Proxy 失敗: {e}")
            return 0
        
        self.drivers = [None] * count
        threads = []
        
        BASE_LOCAL_PORT = 9000  # 本地 proxy 起始端口
        
        def launch_worker(index: int) -> None:
            """執行緒工作函式"""
            credential = self.credentials[index]
            local_proxy_port = None
            
            try:
                # 取得對應的 upstream proxy
                upstream_proxy = proxys[index % len(proxys)]
                
                # 計算本地 proxy 端口
                local_proxy_port = BASE_LOCAL_PORT + index
                
                # 啟動本地 proxy 中繼伺服器
                logger.info(f"[{credential.username}] 正在啟動本地 Proxy 伺服器...")
                logger.info(f"  本地端口: {local_proxy_port}")
                logger.info(f"  上游 Proxy: {upstream_proxy.split(':')[0]}:{upstream_proxy.split(':')[1]}")
                
                if not LocalProxyServerManager.start_proxy_server(local_proxy_port, upstream_proxy):
                    logger.error(f"[{credential.username}] Proxy 伺服器啟動失敗")
                    return
                
                # 創建瀏覽器(使用本地 proxy)
                driver = BrowserManager.create_webdriver(local_proxy_port)
                
                # 登入
                if LoginManager.login_with_retry(driver, credential):
                    self.drivers[index] = driver
                    game_state_manager.set_username(driver, credential.username)
                else:
                    if driver:
                        driver.quit()
            except Exception as e:
                logger.error(f"[{credential.username}] 啟動失敗: {e}")
                import traceback
                traceback.print_exc()
        
        logger.info(f"開始啟動 {count} 個瀏覽器...")
        logger.info(f"將使用 {len(proxys)} 組 Proxy (循環使用)")
        
        for i in range(count):
            logger.info(f"\n啟動第 {i + 1} 個瀏覽器（帳號：{self.credentials[i].username}）")
            thread = threading.Thread(target=launch_worker, args=(i,), daemon=True)
            threads.append(thread)
            thread.start()
            time.sleep(1)  # 錯開啟動時間
        
        logger.info("\n等待所有瀏覽器啟動完成...")
        for thread in threads:
            thread.join()
        
        success_count = sum(1 for d in self.drivers if d is not None)
        logger.info(f"\n完成！成功啟動 {success_count}/{count} 個瀏覽器")
        
        return success_count
    
    def start_game(self, driver: WebDriver) -> bool:
        """
        開始遊戲
        
        Args:
            driver: WebDriver實例
            
        Returns:
            bool: 成功返回True
        """
        if game_state_manager.is_running(driver):
            logger.info("遊戲已在執行中")
            return False
        
        # 載入遊戲規則
        try:
            rules = ConfigLoader.load_game_rules()
            game_state_manager.set_rules(driver, rules)
            
            if rules:
                logger.info(f"已載入 {len(rules)} 條遊戲規則")
                
                # 檢查並調整到第一條規則的金額
                controller = GameController(driver)
                controller.switch_to_game_frame()
                
                first_rule_betsize = rules[0].betsize
                logger.info(f"檢查當前金額是否符合第一條規則的金額 {first_rule_betsize}...")
                
                current_amount = controller.get_current_betsize()
                if current_amount:
                    logger.info(f"當前金額: {current_amount}")
                    
                    if current_amount != first_rule_betsize:
                        logger.info(f"當前金額 {current_amount} 不符合規則金額 {first_rule_betsize}，開始調整...")
                        try:
                            if not controller.adjust_betsize(first_rule_betsize):
                                logger.error("調整金額失敗，無法開始遊戲")
                                return False
                            logger.info(f"✓ 金額已調整為 {first_rule_betsize}")
                        except GameControlError as e:
                            logger.error(f"調整金額錯誤：{e}，無法開始遊戲")
                            return False
                    else:
                        logger.info("✓ 當前金額已符合規則要求")
                else:
                    logger.warning("無法識別當前金額，將嘗試調整到目標金額")
                    try:
                        if not controller.adjust_betsize(first_rule_betsize):
                            logger.error("調整金額失敗，無法開始遊戲")
                            return False
                    except GameControlError as e:
                        logger.error(f"調整金額錯誤：{e}，無法開始遊戲")
                        return False
        except ConfigurationError as e:
            logger.error(f"載入規則失敗：{e}，將使用預設模式")
            game_state_manager.set_rules(driver, None)
        
        # 啟動遊戲執行緒
        game_state_manager.set_running(driver, True)
        executor = GameExecutor(driver)
        game_thread = threading.Thread(target=executor.execute_with_rules, daemon=True)
        game_state_manager.set_thread(driver, game_thread)
        game_thread.start()
        
        logger.info("遊戲已開始執行")
        return True
    
    def pause_game(self, driver: WebDriver) -> bool:
        """
        暫停遊戲
        
        Args:
            driver: WebDriver實例
            
        Returns:
            bool: 成功返回True
        """
        if not game_state_manager.is_running(driver):
            logger.info("遊戲未在執行中")
            return False
        
        game_state_manager.set_running(driver, False)
        logger.info("已發送暫停信號")
        
        thread = game_state_manager.get_thread(driver)
        if thread and thread.is_alive():
            thread.join(timeout=3)
        
        logger.info("遊戲已暫停")
        return True
    
    def quit_browser(self, driver: WebDriver) -> bool:
        """
        關閉瀏覽器
        
        Args:
            driver: WebDriver實例
            
        Returns:
            bool: 成功返回True
        """
        try:
            self.pause_game(driver)
            driver.quit()
            logger.info("瀏覽器已關閉")
            game_state_manager.remove(driver)
            return True
        except Exception as e:
            err_msg = str(e)
            if "Remote end closed connection" not in err_msg and "chrome not reachable" not in err_msg.lower():
                logger.warning(f"關閉瀏覽器時發生錯誤：{e}")
            return False
    
    def cleanup_all(self) -> None:
        """清理所有資源"""
        # 先停止重複按鍵功能
        self.stop_repeat_space()
        
        logger.info("正在停止所有遊戲...")
        for driver in self.drivers:
            if driver is not None:
                self.pause_game(driver)
        
        logger.info("正在關閉所有瀏覽器...")
        for driver in self.drivers:
            if driver is not None:
                try:
                    driver.quit()
                except Exception:
                    pass
        
        # 停止所有 proxy 伺服器
        logger.info("正在停止所有 Proxy 伺服器...")
        LocalProxyServerManager.stop_all_servers()
        
        game_state_manager.cleanup_all()
        logger.info("清理完成")
    
    def _capture_betsize_template(self, driver: WebDriver, amount: float) -> None:
        """
        截取下注金額模板
        
        Args:
            driver: WebDriver實例
            amount: 下注金額
        """
        try:
            import io
            from PIL import Image
            
            # 固定座標：金額顯示位置 (基於 600x400 視窗)
            target_x = 400
            target_y = 380
            
            # 截取整個瀏覽器畫面
            screenshot = driver.get_screenshot_as_png()
            screenshot_img = Image.open(io.BytesIO(screenshot))
            
            # 獲取實際截圖尺寸
            img_width, img_height = screenshot_img.size
            
            # 計算相對座標比例（基於 600x400）
            x_ratio = target_x / 600
            y_ratio = target_y / 400
            
            # 應用到實際截圖尺寸
            actual_x = int(img_width * x_ratio)
            actual_y = int(img_height * y_ratio)
            
            # 裁切範圍：上下20px, 左右50px
            crop_left = max(0, actual_x - 50)
            crop_top = max(0, actual_y - 20)
            crop_right = min(img_width, actual_x + 50)
            crop_bottom = min(img_height, actual_y + 20)
            
            # 裁切圖片
            cropped_img = screenshot_img.crop((crop_left, crop_top, crop_right, crop_bottom))
            
            # 儲存到 img/bet_size 目錄
            betsize_dir = path_manager.img_dir / "bet_size"
            betsize_dir.mkdir(parents=True, exist_ok=True)
            
            # 檔名使用金額（整數去掉 .0，小數保留）
            if amount == int(amount):
                filename = f"{int(amount)}.png"
            else:
                filename = f"{amount}.png"
            
            output_path = betsize_dir / filename
            cropped_img.save(output_path)
            
            logger.info(f"✓ 金額模板已儲存: {output_path}")
            logger.info(f"  - 金額: {amount}")
            logger.info(f"  - 尺寸: {cropped_img.size[0]}x{cropped_img.size[1]}")
            
        except Exception as e:
            logger.error(f"截取金額模板失敗: {e}")
            raise
    
    def _capture_amount_template(self, driver: WebDriver, target_x: int, target_y: int) -> None:
        """
        截取金額模板
        
        Args:
            driver: WebDriver實例
            target_x: 目標 X 座標 (基於 600x400 視窗)
            target_y: 目標 Y 座標 (基於 600x400 視窗)
        """
        try:
            import io
            from PIL import Image
            
            # 截取整個瀏覽器畫面
            screenshot = driver.get_screenshot_as_png()
            screenshot_img = Image.open(io.BytesIO(screenshot))
            
            # 獲取實際截圖尺寸
            img_width, img_height = screenshot_img.size
            logger.info(f"截圖尺寸: {img_width}x{img_height}")
            
            # 計算相對座標比例（基於 600x400）
            x_ratio = target_x / 600
            y_ratio = target_y / 400
            
            # 應用到實際截圖尺寸
            actual_x = int(img_width * x_ratio)
            actual_y = int(img_height * y_ratio)
            
            logger.info(f"目標位置 ({target_x}, {target_y}) -> 實際座標 ({actual_x}, {actual_y})")
            
            # 裁切範圍：上下20px, 左右50px
            crop_left = max(0, actual_x - 50)
            crop_top = max(0, actual_y - 20)
            crop_right = min(img_width, actual_x + 50)
            crop_bottom = min(img_height, actual_y + 20)
            
            logger.info(f"裁切範圍: left={crop_left}, top={crop_top}, right={crop_right}, bottom={crop_bottom}")
            
            # 裁切圖片
            cropped_img = screenshot_img.crop((crop_left, crop_top, crop_right, crop_bottom))
            
            # 儲存到 img 目錄
            output_path = path_manager.img_dir / f"amount_template_{target_x}_{target_y}.png"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            cropped_img.save(output_path)
            
            logger.info(f"✓ 模板已儲存: {output_path}")
            logger.info(f"  - 尺寸: {cropped_img.size[0]}x{cropped_img.size[1]}")
            logger.info(f"  - 相對比例: X={x_ratio:.4f} ({x_ratio*100:.2f}%), Y={y_ratio:.4f} ({y_ratio*100:.2f}%)")
            
        except Exception as e:
            logger.error(f"截取模板失敗: {e}")
            raise
    
    def start_repeat_space(self, min_interval: float, max_interval: float) -> bool:
        """
        開始重複按空白鍵功能（控制所有瀏覽器）
        這個函式會阻塞當前執行緒，直到使用者輸入 'p' 為止
        
        Args:
            min_interval: 最小間隔（秒）
            max_interval: 最大間隔（秒）
            
        Returns:
            bool: 成功返回True
        """
        if self.repeat_space_running:
            logger.info("重複按鍵功能已在執行中")
            return False
        
        if not self.drivers or all(d is None for d in self.drivers):
            logger.error("沒有可用的瀏覽器")
            return False
        
        if min_interval <= 0 or max_interval <= 0 or min_interval > max_interval:
            logger.error(f"間隔時間設定錯誤: {min_interval}~{max_interval} 秒")
            return False
        
        # Windows 系統使用 msvcrt 進行非阻塞輸入檢查
        import sys
        if sys.platform == 'win32':
            import msvcrt
        
        logger.info(f"開始重複按空白鍵（間隔 {min_interval}~{max_interval} 秒）")
        logger.info("輸入 'p' + Enter 可暫停並返回指令選單")
        logger.info("輸入其他內容會繼續運行")
        
        self.repeat_space_running = True
        press_count = 0
        input_buffer = ""
        
        try:
            while self.repeat_space_running:
                # 對所有瀏覽器按空白鍵
                for driver in self.drivers:
                    if driver is not None and self.repeat_space_running:
                        try:
                            controller = GameController(driver)
                            controller.send_space()
                            username = game_state_manager.get_username(driver) or "未知"
                            logger.debug(f"[{username}] 已按空白鍵")
                        except Exception as e:
                            username = game_state_manager.get_username(driver) or "未知"
                            logger.warning(f"[{username}] 按空白鍵失敗: {e}")
                
                press_count += 1
                logger.info(f"已完成第 {press_count} 次按鍵")
                
                # 計算隨機間隔
                wait_time = random.uniform(min_interval, max_interval)
                logger.info(f"等待 {wait_time:.1f} 秒後再次按鍵...")
                
                # 每 0.1 秒檢查一次輸入
                sleep_step = 0.1
                total_slept = 0
                while total_slept < wait_time and self.repeat_space_running:
                    # Windows 系統檢查鍵盤輸入
                    if sys.platform == 'win32' and msvcrt.kbhit():
                        char = msvcrt.getch().decode('utf-8', errors='ignore').lower()
                        if char == '\r' or char == '\n':
                            # Enter 鍵：處理緩衝區的內容
                            if input_buffer.strip() == 'p':
                                logger.info("收到 'p' 輸入，停止重複按鍵")
                                self.repeat_space_running = False
                                input_buffer = ""
                                break
                            elif input_buffer.strip():
                                logger.info(f"收到 '{input_buffer.strip()}' 輸入，繼續轉動")
                            input_buffer = ""
                        else:
                            # 累積字元到緩衝區
                            input_buffer += char
                    
                    time.sleep(sleep_step)
                    total_slept += sleep_step
        
        except KeyboardInterrupt:
            logger.info("\n偵測到中斷訊號，停止重複按鍵")
        finally:
            self.repeat_space_running = False
            logger.info("重複按鍵功能已停止，返回指令選單")
        
        return True
    
    def stop_repeat_space(self) -> bool:
        """
        停止重複按空白鍵功能
        
        Returns:
            bool: 成功返回True
        """
        if not self.repeat_space_running:
            logger.info("重複按鍵功能未在執行中")
            return False
        
        logger.info("正在停止重複按鍵功能...")
        self.repeat_space_running = False
        
        if self.repeat_space_thread and self.repeat_space_thread.is_alive():
            self.repeat_space_thread.join(timeout=3)
        
        logger.info("重複按鍵功能已停止")
        return True
    
    def process_command(self, command: str) -> bool:
        """
        處理使用者指令
        
        Args:
            command: 指令字串
            
        Returns:
            bool: 是否應該退出程式
        """
        command = command.lower().strip()
        
        if command == GameCommand.QUIT.value:
            self.cleanup_all()
            return True
        
        if command == GameCommand.PAUSE.value:
            # 暫停重複按鍵功能
            self.stop_repeat_space()
            # 也暫停原本的遊戲
            for driver in self.drivers:
                if driver is not None:
                    self.pause_game(driver)
        
        elif command == GameCommand.CONTINUE.value:
            for driver in self.drivers:
                if driver is not None:
                    self.start_game(driver)
        
        elif command == GameCommand.SCREENSHOT.value:
            for driver in self.drivers:
                if driver is not None:
                    GameController(driver).take_screenshot()
        
        elif command == GameCommand.CAPTURE_AMOUNT.value:
            logger.info("=== 截取金額模板工具 ===")
            logger.info("請輸入目前遊戲顯示的金額（例如: 0.4, 2.4, 10）")
            logger.info("按 Enter 鍵退出")
            
            while True:
                try:
                    amount_input = input("\n金額: ").strip()
                    
                    # 空白輸入則退出
                    if not amount_input:
                        logger.info("退出金額模板工具")
                        break
                    
                    amount = float(amount_input)
                    
                    # 驗證金額是否在有效列表中
                    if amount not in GAME_BETSIZE:
                        logger.warning(f"⚠ 金額 {amount} 不在標準列表中，但仍會建立模板")
                    
                    logger.info(f"目標金額: {amount}")
                    
                    # 使用第一個瀏覽器截取
                    if self.drivers and self.drivers[0] is not None:
                        self._capture_betsize_template(self.drivers[0], amount)
                    else:
                        logger.error("沒有可用的瀏覽器")
                        break
                        
                except ValueError:
                    logger.error("金額格式錯誤，請輸入有效數字（例如: 0.4）")
                except EOFError:
                    logger.info("退出金額模板工具")
                    break
                except Exception as e:
                    logger.error(f"截取失敗: {e}")
                    break
        
        elif command == GameCommand.BUY_FREE_GAME.value:
            logger.info("開始購買免費遊戲流程...")
            
            # 使用執行緒同步執行所有瀏覽器的購買操作
            threads = []
            for driver in self.drivers:
                if driver is not None:
                    def buy_worker(d):
                        try:
                            controller = GameController(d)
                            username = game_state_manager.get_username(d) or "未知"
                            
                            # 執行購買操作（不包含等待用戶輸入）
                            global last_canvas_rect
                            if last_canvas_rect is None:
                                logger.error(f"[{username}] Canvas 範圍未初始化，請先進入遊戲")
                                return
                            
                            rect = last_canvas_rect
                            
                            # 第一次點擊（freegame 區域）
                            freegame_x = rect["x"] + rect["w"] * 0.23
                            freegame_y = rect["y"] + rect["h"] * 1.05
                            
                            logger.info(f"[{username}] 點擊免費遊戲區域...")
                            for ev in ["mousePressed", "mouseReleased"]:
                                d.execute_cdp_cmd("Input.dispatchMouseEvent", {
                                    "type": ev,
                                    "x": freegame_x,
                                    "y": freegame_y,
                                    "button": "left",
                                    "clickCount": 1
                                })
                            time.sleep(2)
                            
                            # 第二次點擊（Canvas 確認按鈕）
                            start_x = rect["x"] + rect["w"] * 0.65
                            start_y = rect["y"] + rect["h"] * 1.2
                            
                            logger.info(f"[{username}] 點擊確認按鈕...")
                            for ev in ["mousePressed", "mouseReleased"]:
                                d.execute_cdp_cmd("Input.dispatchMouseEvent", {
                                    "type": ev,
                                    "x": start_x,
                                    "y": start_y,
                                    "button": "left",
                                    "clickCount": 1
                                })
                            
                            # 購買完成後自動按一次空白鍵
                            logger.info(f"[{username}] 購買完成，等待 10 秒後開始遊戲...")
                            time.sleep(10)
                            logger.info(f"[{username}] 按下空白鍵開始遊戲...")
                            controller.send_key(KEYBOARD_KEY.SPACE)
                            
                            logger.info(f"[{username}] 免費遊戲購買完成！")
                            
                        except Exception as e:
                            username = game_state_manager.get_username(d) or "未知"
                            logger.error(f"[{username}] 購買免費遊戲失敗: {e}")
                    
                    thread = threading.Thread(target=buy_worker, args=(driver,), daemon=True)
                    threads.append(thread)
                    thread.start()
            
            # 等待所有執行緒完成
            for thread in threads:
                thread.join()
            
            logger.info("所有瀏覽器購買操作完成")
            logger.info("您現在可以手動操作遊戲")
            
            # 等待用戶按 'o' 返回指令選單（只需按一次）
            while True:
                user_input = input("輸入 'o' 返回指令選單：").strip().lower()
                if user_input == "o":
                    logger.info("免費遊戲結束，對所有瀏覽器按下空白鍵...")
                    # 對所有瀏覽器統一再按一次空白鍵
                    for driver in self.drivers:
                        if driver is not None:
                            try:
                                controller = GameController(driver)
                                controller.send_key(KEYBOARD_KEY.SPACE)
                                username = game_state_manager.get_username(driver) or "未知"
                                logger.info(f"[{username}] 已按下空白鍵")
                            except Exception as e:
                                username = game_state_manager.get_username(driver) or "未知"
                                logger.error(f"[{username}] 按空白鍵失敗: {e}")
                    logger.info("返回指令選單...")
                    break
        
        elif command.startswith(GameCommand.BET_SIZE.value):
            parts = command.split()
            if len(parts) < 2:
                logger.warning("請輸入目標金額，格式: b <金額>")
                logger.info(f"可用金額: {GAME_BETSIZE}")
            else:
                try:
                    target_amount = float(parts[1])
                    for driver in self.drivers:
                        if driver is not None:
                            try:
                                GameController(driver).adjust_betsize(target_amount)
                            except GameControlError as e:
                                logger.error(f"調整金額失敗：{e}")
                except ValueError:
                    logger.error(f"無效的金額: {parts[1]}")
        
        elif command.startswith(GameCommand.REPEAT_SPACE.value):
            # 處理 r 指令：r min,max
            parts = command.split()
            if len(parts) < 2:
                logger.warning("請輸入間隔時間，格式: r <最小秒數>,<最大秒數>")
                logger.info("範例: r 1,2 代表每次間隔 1~2 秒")
            else:
                try:
                    intervals = parts[1].split(',')
                    if len(intervals) != 2:
                        logger.error("格式錯誤，請使用逗號分隔兩個數字，例如: r 1,2")
                    else:
                        min_interval = float(intervals[0].strip())
                        max_interval = float(intervals[1].strip())
                        # 注意：這個函式會阻塞直到使用者按 p 停止
                        self.start_repeat_space(min_interval, max_interval)
                except ValueError:
                    logger.error(f"無效的間隔時間: {parts[1]}")
        
        elif command == GameCommand.HELP.value or command == '?':
            self._show_help()
        
        else:
            logger.warning(f"未識別的指令：{command}")
            logger.info("輸入 'h' 或 '?' 查看幫助")
        
        return False
    
    def _show_help(self) -> None:
        """顯示幫助信息"""
        help_text = """
╔════════════════════════════════════════════════════════════════╗
║                      遊戲控制指令說明                             ║
╠════════════════════════════════════════════════════════════════╣
║  c            - 開始遊戲（自動執行規則）                           ║
║  p            - 暫停遊戲／暫停重複按鍵                             ║
║  r <秒,秒>    - 重複按空白鍵（例如: r 1,2）                        ║
║                 所有瀏覽器同時操作，間隔 1~2 秒                    ║
║  b            - 購買免費遊戲                                      ║
║  bet <金額>   - 調整下注金額（例如: bet 2.4）                      ║
║  s            - 截取螢幕畫面                                     ║
║  cap          - 截取金額模板（輸入當前金額）                        ║
║  q            - 退出程式                                        ║
║  h 或 ?       - 顯示此說明                                       ║
╠════════════════════════════════════════════════════════════════╣
║                      可用金額列表                                ║
╠════════════════════════════════════════════════════════════════╣
║  0.4, 0.8, 1, 1.2, 1.6, 2, 2.4, 2.8, 3, 3.2, 3.6, 4,           ║
║  5, 6, 7, 8, 9, 10, 12, 14, 16, 18, 20, 24, 28, 32, 36, 40,    ║
║  48, 56, 60, 64, 72, 80, 100, 120, 140, 160, 180, 200,         ║
║  240, 280, 300, 320, 360, 400, 420, 480, 500, 540, 560,        ║
║  600, 640, 700, 720, 800, 840, 900, 960, 980, 1000,            ║
║  1080, 1120, 1200, 1260, 1280, 1400, 1440, 1600, 1800, 2000    ║
╚════════════════════════════════════════════════════════════════╝
        """
        print(help_text)
    
    def run_command_loop(self) -> None:
        """執行指令控制迴圈"""
        logger.info("已進入指令模式")
        self._show_help()
        
        try:
            while True:
                try:
                    command = input("\n請輸入指令：").strip()
                except EOFError:
                    logger.info("接收到 EOF，程式結束")
                    break
                
                if not command:
                    logger.warning("指令不能為空白，請重新輸入")
                    continue
                
                if self.process_command(command):
                    break
        
        except KeyboardInterrupt:
            logger.info("\n偵測到中斷訊號 (Ctrl+C)")
            self.cleanup_all()
    
    def run(self) -> None:
        """執行主程式"""
        logger.info("=== 金富翁遊戲自動化系統 ===")
        
        try:
            # 階段 0：環境檢查
            self._check_environment()
            
            # 階段 1：載入配置
            if not self.load_configurations():
                return
            
            # 階段 2：取得使用者輸入
            browser_count = self.get_browser_count()
            if browser_count is None:
                return
            
            # 階段 3：啟動瀏覽器
            success_count = self.launch_browsers(browser_count)
            if success_count == 0:
                logger.error("沒有成功啟動任何瀏覽器，程式結束")
                return
            
            # 階段 4：排列視窗
            WindowManager.arrange_windows(self.drivers)
            
            # 階段 5：指令控制
            self.run_command_loop()
            
        except KeyboardInterrupt:
            logger.info("\n程式已中斷")
        except Exception as e:
            logger.error(f"程式執行錯誤：{e}", exc_info=True)
        finally:
            logger.info("程式結束")


# ==================== 程式入口 ====================


def main() -> None:
    """主程式入口"""
    controller = MainController()
    controller.run()


if __name__ == "__main__":
    main()
