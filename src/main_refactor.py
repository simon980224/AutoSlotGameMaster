"""
賽特遊戲自動化系統 - 重構版

此版本完全獨立運行，不依賴 main.py

功能範圍（對應 main_flow_explanation.md 第 76~97 行）:
- 載入配置檔案（用戶資料.txt、用戶規則.txt）
- 自動決定瀏覽器數量
- 啟動代理中繼伺服器（為每個瀏覽器建立本地代理）
- 建立瀏覽器實例（為每個用戶建立 WebDriver）
- 導航到登入頁面
- 執行登入操作
- 導航到遊戲頁面
- 調整視窗排列

作者: 凡臻科技
版本: 2.0.0
Python: 3.8+
"""

import logging
import sys
import socket
import select
import base64
import time
import subprocess
from typing import Optional, List, Dict, Tuple, Any, Callable, Protocol, Union
from pathlib import Path
from dataclasses import dataclass, field
from contextlib import contextmanager, suppress
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import Enum
import threading

# Selenium WebDriver 相關
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# 圖片處理相關
import cv2
import numpy as np
from PIL import Image
import io


# ============================================================================
# 常量定義
# ============================================================================

class Constants:
    """系統常量"""
    # 版本資訊
    VERSION = "2.0.0"
    SYSTEM_NAME = "賽特遊戲自動化系統 - 重構版"
    
    # 配置檔案路徑
    DEFAULT_LIB_PATH = "lib"
    DEFAULT_CREDENTIALS_FILE = "用戶資料.txt"
    DEFAULT_RULES_FILE = "用戶規則.txt"
    
    # 代理伺服器配置
    DEFAULT_PROXY_START_PORT = 9000
    PROXY_SERVER_BIND_HOST = "127.0.0.1"
    PROXY_BUFFER_SIZE = 4096
    PROXY_SELECT_TIMEOUT = 1.0
    PROXY_SERVER_START_WAIT = 1  # 代理伺服器啟動等待時間
    
    # 超時配置
    DEFAULT_TIMEOUT_SECONDS = 30
    DEFAULT_PAGE_LOAD_TIMEOUT = 600
    DEFAULT_SCRIPT_TIMEOUT = 600
    DEFAULT_IMPLICIT_WAIT = 60
    SERVER_SOCKET_TIMEOUT = 1.0
    CLEANUP_PROCESS_TIMEOUT = 10
    
    # 執行緒配置
    MAX_THREAD_WORKERS = 10
    MAX_BROWSER_COUNT = 12  # 最大瀏覽器數量
    
    # 視窗配置
    DEFAULT_WINDOW_WIDTH = 600
    DEFAULT_WINDOW_HEIGHT = 400
    DEFAULT_WINDOW_COLUMNS = 4
    
    # URL 配置
    LOGIN_PAGE = "https://www.fin88.app/"
    GAME_PAGE = "https://www.fin88.app/"
    
    # 登入相關 XPath
    INITIAL_LOGIN_BUTTON = "//button[contains(@class, 'btn') and contains(@class, 'login') and contains(@class, 'pc') and text()='登入']"
    USERNAME_INPUT = "//input[@placeholder='請輸入帳號/手機號']"
    PASSWORD_INPUT = "//input[@placeholder='請輸入您的登入密碼']"
    LOGIN_BUTTON = "//button[contains(@class, 'custom-button') and @type='submit' and text()='登入遊戲']"
    
    # 遊戲頁面相關 XPath
    SEARCH_BUTTON = "//button[contains(@class, 'search-btn')]"
    SEARCH_INPUT = "//input[@placeholder='按換行鍵搜索']"
    GAME_XPATH = "//div[contains(@class, 'game-card-container') and .//div[contains(@style, 'ATG-egyptian-mythology.png')]]"
    GAME_IFRAME = "//iframe[contains(@class, 'iframe-item')]"
    GAME_CANVAS = "GameCanvas"  # 遊戲 Canvas 元素 ID
    
    # 圖片檢測配置
    IMAGE_DIR = "img"
    GAME_LOGIN = "game_login.png"
    GAME_CONFIRM = "game_confirm.png"
    MATCH_THRESHOLD = 0.8  # 圖片匹配閾值
    DETECTION_INTERVAL = 1.0  # 檢測間隔（秒）
    MAX_DETECTION_ATTEMPTS = 60  # 最大檢測次數
    DETECTION_PROGRESS_INTERVAL = 20  # 檢測進度顯示間隔
    
    # Canvas 動態計算比例（用於點擊座標）
    GAME_LOGIN_BUTTON_X_RATIO = 0.5   # game_login 開始遊戲按鈕 X 座標比例
    GAME_LOGIN_BUTTON_Y_RATIO = 0.9   # game_login 開始遊戲按鈕 Y 座標比例
    GAME_CONFIRM_BUTTON_X_RATIO = 0.74  # game_confirm 確認按鈕 X 座標比例
    GAME_CONFIRM_BUTTON_Y_RATIO = 0.85  # game_confirm 確認按鈕 Y 座標比例
    
    # 控制中心配置
    AUTO_SKIP_CLICK_INTERVAL = 30  # 自動跳過點擊間隔（秒）


# ============================================================================
# 例外類別
# ============================================================================

class AutoSlotGameError(Exception):
    """基礎例外類別"""
    pass


class ConfigurationError(AutoSlotGameError):
    """配置相關錯誤"""
    pass


class BrowserCreationError(AutoSlotGameError):
    """瀏覽器建立錯誤"""
    pass


class ProxyServerError(AutoSlotGameError):
    """代理伺服器錯誤"""
    pass


class ImageDetectionError(AutoSlotGameError):
    """圖片檢測錯誤"""
    pass


# ============================================================================
# 資料類別
# ============================================================================

@dataclass(frozen=True)
class UserCredential:
    """使用者憑證資料結構（不可變）。
    
    Attributes:
        username: 使用者名稱
        password: 密碼
        proxy: 代理出口 IP（可選）
    """
    username: str
    password: str
    proxy: Optional[str] = None
    
    def __post_init__(self) -> None:
        """驗證資料完整性"""
        if not self.username or not self.password:
            raise ValueError("使用者名稱和密碼不能為空")


@dataclass(frozen=True)
class BetRule:
    """下注規則資料結構（不可變）。
    
    支援三種類型:
    - 'a' (自動旋轉): amount, spin_count
    - 's' (標準規則): amount, duration, min_seconds, max_seconds
    - 'f' (購買免費遊戲): amount
    """
    rule_type: str  # 'a'、's' 或 'f'
    amount: float
    spin_count: Optional[int] = None  # 'a' 類型使用
    duration: Optional[int] = None  # 's' 類型使用（分鐘）
    min_seconds: Optional[float] = None  # 's' 類型使用
    max_seconds: Optional[float] = None  # 's' 類型使用
    
    def __post_init__(self) -> None:
        """驗證資料完整性"""
        if self.amount <= 0:
            raise ValueError(f"下注金額必須大於 0: {self.amount}")
        
        if self.rule_type == 'a':
            if self.spin_count is None:
                raise ValueError("自動旋轉規則必須指定次數")
            if self.spin_count not in [10, 50, 100]:
                raise ValueError(f"自動旋轉次數必須是 10、50 或 100: {self.spin_count}")
        
        elif self.rule_type == 's':
            if self.duration is None or self.duration <= 0:
                raise ValueError(f"持續時間必須大於 0: {self.duration}")
            if self.min_seconds is None or self.min_seconds <= 0:
                raise ValueError(f"最小間隔秒數必須大於 0: {self.min_seconds}")
            if self.max_seconds is None or self.max_seconds <= 0:
                raise ValueError(f"最大間隔秒數必須大於 0: {self.max_seconds}")
            if self.min_seconds > self.max_seconds:
                raise ValueError(f"最小間隔不能大於最大間隔: {self.min_seconds} > {self.max_seconds}")
        
        elif self.rule_type == 'f':
            # 購買免費遊戲規則驗證（只需要金額）
            pass
        
        else:
            raise ValueError(f"無效的規則類型: {self.rule_type}，必須是 'a'、's' 或 'f'")


@dataclass(frozen=True)
class ProxyInfo:
    """代理伺服器資訊資料結構（不可變）。
    
    Attributes:
        host: 代理主機
        port: 代理埠號
        username: 認證使用者名稱
        password: 認證密碼
    """
    host: str
    port: int
    username: str
    password: str
    
    def __post_init__(self) -> None:
        """驗證資料完整性"""
        if not self.host:
            raise ValueError("代理主機不能為空")
        if not (0 < self.port < 65536):
            raise ValueError(f"代理埠號無效: {self.port}")
        if not self.username:
            raise ValueError("代理使用者名稱不能為空")
    
    def to_url(self) -> str:
        """轉換為代理 URL 格式。"""
        return f"http://{self.username}:{self.password}@{self.host}:{self.port}"
    
    def to_connection_string(self) -> str:
        """轉換為連接字串格式。"""
        return f"{self.host}:{self.port}:{self.username}:{self.password}"
    
    def __str__(self) -> str:
        """字串表示（隱藏敏感資訊）"""
        return f"ProxyInfo({self.host}:{self.port}, user={self.username[:3]}***)"
    
    @staticmethod
    def from_connection_string(connection_string: str) -> 'ProxyInfo':
        """從連接字串建立 ProxyInfo 實例。
        
        Args:
            connection_string: 格式為 "host:port:username:password"
        """
        parts = connection_string.split(':')
        if len(parts) < 4:
            raise ValueError(f"代理連接字串格式不正確: {connection_string}")
        
        return ProxyInfo(
            host=parts[0],
            port=int(parts[1]),
            username=parts[2],
            password=':'.join(parts[3:])  # 密碼可能包含冒號
        )


@dataclass
class BrowserContext:
    """瀏覽器上下文資訊。
    
    Attributes:
        driver: WebDriver 實例
        credential: 使用者憑證
        index: 瀏覽器索引（從 1 開始）
        proxy_port: 代理埠號（可選）
        created_at: 建立時間戳
    """
    driver: WebDriver
    credential: UserCredential
    index: int
    proxy_port: Optional[int] = None  # 代理埠號（可選）
    created_at: float = field(default_factory=time.time)
    
    @property
    def age_in_seconds(self) -> float:
        """取得瀏覽器實例的存活時間（秒）"""
        return time.time() - self.created_at


class BrowserThread(threading.Thread):
    """瀏覽器專屬執行緒。
    
    每個瀏覽器實例都有自己的專屬執行緒，從建立到關閉的所有操作
    都在同一個執行緒中執行，確保執行緒安全性。
    
    Attributes:
        index: 瀏覽器索引（從 1 開始）
        credential: 使用者憑證
        proxy_port: 代理埠號（可選）
        browser_manager: 瀏覽器管理器
        context: 瀏覽器上下文（建立後填充）
    """
    
    def __init__(
        self,
        index: int,
        credential: UserCredential,
        browser_manager: 'BrowserManager',
        proxy_port: Optional[int] = None,
        logger: Optional[logging.Logger] = None
    ):
        super().__init__(name=f"BrowserThread-{index}", daemon=True)
        self.index = index
        self.credential = credential
        self.proxy_port = proxy_port
        self.browser_manager = browser_manager
        self.logger = logger or LoggerFactory.get_logger()
        
        # 瀏覽器上下文（在執行緒中建立）
        self.context: Optional[BrowserContext] = None
        self.driver: Optional[WebDriver] = None
        
        # 執行緒控制
        self._stop_event = threading.Event()
        self._ready_event = threading.Event()  # 瀏覽器就緒事件
        self._creation_error: Optional[Exception] = None
        
        # 任務佇列
        self._task_queue: List[Tuple[Callable, tuple, dict]] = []
        self._task_lock = threading.Lock()
        self._task_event = threading.Event()  # 有新任務時通知
        self._task_result: Any = None
        self._task_done_event = threading.Event()  # 任務完成事件
    
    def run(self) -> None:
        """執行緒主迴圈。"""
        try:
            # 1. 建立瀏覽器
            self._create_browser()
            
            if self.driver is None:
                return
            
            # 2. 通知瀏覽器已就緒
            self._ready_event.set()
            
            # 3. 主迴圈：等待任務或停止信號
            while not self._stop_event.is_set():
                # 等待任務或停止信號（每秒檢查一次）
                if self._task_event.wait(timeout=1.0):
                    self._task_event.clear()
                    self._process_tasks()
            
        except Exception as e:
            self.logger.error(f"[錯誤] 瀏覽器 {self.index} 執行緒異常: {e}")
        finally:
            # 4. 清理資源
            self._cleanup()
    
    def _create_browser(self) -> None:
        """在執行緒中建立瀏覽器。"""
        try:
            self.driver = self.browser_manager.create_webdriver(
                local_proxy_port=self.proxy_port
            )
            
            self.context = BrowserContext(
                driver=self.driver,
                credential=self.credential,
                index=self.index,
                proxy_port=self.proxy_port
            )
            
        except Exception as e:
            self._creation_error = e
            self._ready_event.set()  # 即使失敗也要通知
    
    def _process_tasks(self) -> None:
        """處理任務佇列中的所有任務。"""
        while True:
            with self._task_lock:
                if not self._task_queue:
                    break
                func, args, kwargs = self._task_queue.pop(0)
            
            try:
                # 將 context 注入到任務中
                self._task_result = func(self.context, *args, **kwargs)
            except Exception as e:
                self._task_result = e
            finally:
                self._task_done_event.set()
    
    def _cleanup(self) -> None:
        """清理瀏覽器資源。"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            finally:
                self.driver = None
                self.context = None
    
    def wait_until_ready(self, timeout: Optional[float] = None) -> bool:
        """等待瀏覽器就緒。
        
        Args:
            timeout: 超時時間（秒），None 表示無限等待
            
        Returns:
            瀏覽器是否成功建立
        """
        self._ready_event.wait(timeout=timeout)
        return self.context is not None and self._creation_error is None
    
    def get_creation_error(self) -> Optional[Exception]:
        """取得建立瀏覽器時的錯誤。"""
        return self._creation_error
    
    def execute_task(
        self, 
        func: Callable[[BrowserContext], Any],
        *args,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Any:
        """在瀏覽器執行緒中執行任務。
        
        Args:
            func: 要執行的函數，第一個參數會是 BrowserContext
            *args: 額外的位置參數
            timeout: 超時時間（秒）
            **kwargs: 額外的關鍵字參數
            
        Returns:
            任務執行的結果
        """
        if not self.is_alive() or self._stop_event.is_set():
            raise RuntimeError(f"瀏覽器 {self.index} 執行緒已停止")
        
        # 重置任務完成事件
        self._task_done_event.clear()
        self._task_result = None
        
        # 加入任務佇列
        with self._task_lock:
            self._task_queue.append((func, args, kwargs))
        
        # 通知執行緒有新任務
        self._task_event.set()
        
        # 等待任務完成
        if self._task_done_event.wait(timeout=timeout):
            result = self._task_result
            if isinstance(result, Exception):
                raise result
            return result
        else:
            raise TimeoutError(f"瀏覽器 {self.index} 任務執行超時")
    
    def stop(self) -> None:
        """停止執行緒。"""
        self._stop_event.set()
        self._task_event.set()  # 喚醒等待中的執行緒
    
    def is_browser_alive(self) -> bool:
        """檢查瀏覽器是否仍然有效。"""
        if self.driver is None:
            return False
        try:
            _ = self.driver.current_url
            return True
        except Exception:
            return False


class OperationResult:
    """操作結果封裝。
    
    Attributes:
        success: 操作是否成功
        data: 操作返回的資料
        error: 發生的例外（如果有）
        message: 額外的訊息
    """
    def __init__(
        self, 
        success: bool, 
        data: Any = None, 
        error: Optional[Exception] = None,
        message: str = ""
    ):
        self.success = success
        self.data = data
        self.error = error
        self.message = message
    
    def __bool__(self) -> bool:
        return self.success
    
    def __repr__(self) -> str:
        status = "成功" if self.success else "失敗"
        return f"OperationResult({status}, {self.message})"


# ============================================================================
# 日誌系統
# ============================================================================

class LogLevel(Enum):
    """日誌等級"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class ColoredFormatter(logging.Formatter):
    """帶顏色的日誌格式化器。"""
    
    COLORS = {
        'RESET': "\033[0m",
        'INFO': "\033[32m",       # 綠色
        'WARNING': "\033[33m",    # 黃色
        'ERROR': "\033[31m",      # 紅色
        'CRITICAL': "\033[35m",   # 紫色
        'DEBUG': "\033[36m",      # 青色
        'TIMESTAMP': "\033[90m",  # 灰色
    }
    
    def __init__(self, fmt: Optional[str] = None, datefmt: Optional[str] = None) -> None:
        super().__init__(fmt, datefmt)
        self.formatters = {
            logging.DEBUG: self._create_formatter(self.COLORS['DEBUG'], 'DEBUG'),
            logging.INFO: self._create_formatter(self.COLORS['INFO'], 'INFO'),
            logging.WARNING: self._create_formatter(self.COLORS['WARNING'], 'WARNING'),
            logging.ERROR: self._create_formatter(self.COLORS['ERROR'], 'ERROR'),
            logging.CRITICAL: self._create_formatter(self.COLORS['CRITICAL'], 'CRITICAL'),
        }
    
    def _create_formatter(self, color: str, level_name: str) -> logging.Formatter:
        """建立指定顏色的格式化器"""
        return logging.Formatter(
            f"{self.COLORS['TIMESTAMP']}%(asctime)s{self.COLORS['RESET']} - "
            f"{color}%(levelname)-8s{self.COLORS['RESET']} - "
            f"%(message)s"
        )
    
    def format(self, record: logging.LogRecord) -> str:
        formatter = self.formatters.get(record.levelno)
        if formatter:
            return formatter.format(record)
        return super().format(record)


class FlushingStreamHandler(logging.StreamHandler):
    """自動刷新的 StreamHandler，解決多執行緒環境下的緩衝阻塞問題。"""
    
    def emit(self, record: logging.LogRecord) -> None:
        try:
            super().emit(record)
            self.flush()
        except Exception:
            self.handleError(record)


class LoggerFactory:
    """Logger 工廠類別 - 使用單例模式"""
    
    _loggers: Dict[str, logging.Logger] = {}
    _lock = threading.RLock()
    _formatter: Optional[ColoredFormatter] = None
    
    @classmethod
    def get_logger(
        cls, 
        name: str = "AutoSlotGame",
        level: LogLevel = LogLevel.INFO
    ) -> logging.Logger:
        """取得或建立 logger 實例（執行緒安全）。"""
        if name in cls._loggers:
            return cls._loggers[name]
        
        with cls._lock:
            if name in cls._loggers:
                return cls._loggers[name]
            
            logger = logging.getLogger(name)
            logger.setLevel(level.value)
            logger.propagate = False
            
            if not logger.handlers:
                if cls._formatter is None:
                    cls._formatter = ColoredFormatter()
                
                console_handler = FlushingStreamHandler(sys.stdout)
                console_handler.setLevel(level.value)
                console_handler.setFormatter(cls._formatter)
                logger.addHandler(console_handler)
            
            cls._loggers[name] = logger
            return logger


# ============================================================================
# 輔助函式
# ============================================================================

def get_resource_path(relative_path: str = "") -> Path:
    """取得資源檔案的絕對路徑。
    
    在開發環境中，返回專案根目錄的路徑。
    在打包後的環境中，返回 exe 所在目錄的路徑。
    """
    if getattr(sys, 'frozen', False):
        base_path = Path(sys.executable).resolve().parent
    else:
        base_path = Path(__file__).resolve().parent.parent
    
    if relative_path:
        return base_path / relative_path
    return base_path


def cv2_imread_unicode(file_path: Union[str, Path], flags: int = cv2.IMREAD_COLOR) -> Optional[np.ndarray]:
    """安全讀取圖片（支援 Unicode 路徑）。
    
    OpenCV 的 cv2.imread() 無法處理包含中文或其他非 ASCII 字元的路徑。
    此函式使用 numpy 和 PIL 作為替代方案。
    
    Args:
        file_path: 圖片檔案路徑（支援中文路徑）
        flags: OpenCV 讀取標誌（cv2.IMREAD_COLOR, cv2.IMREAD_GRAYSCALE 等）
        
    Returns:
        圖片的 numpy 陣列，失敗返回 None
    """
    try:
        # 轉換為 Path 物件
        path = Path(file_path)
        
        # 使用 PIL 讀取圖片（PIL 支援 Unicode 路徑）
        pil_image = Image.open(path)
        
        # 轉換為 numpy 陣列
        img_array = np.array(pil_image)
        
        # 根據讀取標誌處理圖片
        if flags == cv2.IMREAD_GRAYSCALE:
            # 轉換為灰階
            if len(img_array.shape) == 3:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        elif flags == cv2.IMREAD_COLOR:
            # 確保是彩色圖片
            if len(img_array.shape) == 2:
                # 灰階轉彩色
                img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2RGB)
            elif img_array.shape[2] == 4:
                # RGBA 轉 RGB
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
            # PIL 使用 RGB，OpenCV 使用 BGR，需要轉換
            if len(img_array.shape) == 3 and img_array.shape[2] == 3:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        return img_array
        
    except Exception:
        # 返回 None 保持與 cv2.imread() 相同的行為
        return None


# ============================================================================
# 配置讀取器
# ============================================================================

class ConfigReaderProtocol(Protocol):
    """配置讀取器協議"""
    
    def read_user_credentials(self, filename: str) -> List[UserCredential]:
        ...
    
    def read_bet_rules(self, filename: str) -> List[BetRule]:
        ...


class ConfigReader:
    """配置檔案讀取器。
    
    讀取並解析系統所需的各種配置檔案。
    """
    
    def __init__(
        self, 
        lib_path: Optional[Path] = None,
        logger: Optional[logging.Logger] = None
    ) -> None:
        if lib_path is None:
            lib_path = get_resource_path(Constants.DEFAULT_LIB_PATH)
        
        self.lib_path = Path(lib_path)
        self.logger = logger or LoggerFactory.get_logger()
        
        if not self.lib_path.exists():
            raise ConfigurationError(f"配置目錄不存在: {self.lib_path}")
    
    def _read_file_lines(self, filename: str, skip_header: bool = True) -> List[str]:
        """讀取檔案並返回有效行列表。"""
        file_path = self.lib_path / filename
        
        if not file_path.exists():
            raise ConfigurationError(f"找不到配置檔案: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8', buffering=8192) as f:
                lines = f.readlines()
            
            start_index = 1 if skip_header and lines else 0
            
            valid_lines = [
                line.strip() 
                for line in lines[start_index:] 
                if (stripped := line.strip()) and not stripped.startswith('#')
            ]
            
            return valid_lines
            
        except (IOError, OSError) as e:
            raise ConfigurationError(f"讀取檔案失敗 {filename}: {e}") from e
        except Exception as e:
            raise ConfigurationError(f"解析檔案失敗 {filename}: {e}") from e
    
    def read_user_credentials(
        self, 
        filename: str = Constants.DEFAULT_CREDENTIALS_FILE
    ) -> List[UserCredential]:
        """讀取使用者憑證檔案。
        
        檔案格式: 帳號,密碼,出口IP (首行為標題)
        """
        credentials = []
        lines = self._read_file_lines(filename, skip_header=True)
        
        for line_number, line in enumerate(lines, start=2):
            try:
                parts = [p.strip() for p in line.split(',')]
                
                if len(parts) < 2:
                    self.logger.warning(f"[警告] 第 {line_number} 行格式不完整，已跳過: {line}")
                    continue
                
                username = parts[0]
                password = parts[1]
                proxy = parts[2] if len(parts) >= 3 and parts[2].strip() else None
                
                credentials.append(UserCredential(
                    username=username,
                    password=password,
                    proxy=proxy
                ))  
                
            except ValueError as e:
                self.logger.warning(f"[警告] 第 {line_number} 行資料無效: {e}")
                continue
        
        return credentials
    
    def read_bet_rules(
        self, 
        filename: str = Constants.DEFAULT_RULES_FILE
    ) -> List[BetRule]:
        """讀取下注規則檔案。
        
        支援三種格式:
        - a:金額:次數 (自動旋轉規則)
        - s:金額:時間(分鐘):最小(秒數):最大(秒數) (標準規則)
        - f:金額 (購買免費遊戲)
        """
        rules = []
        lines = self._read_file_lines(filename, skip_header=True)
        
        for line_number, line in enumerate(lines, start=2):
            try:
                parts = line.split(':')
                
                if len(parts) < 2:
                    self.logger.warning(f"[警告] 第 {line_number} 行格式不完整，已跳過: {line}")
                    continue
                
                rule_type = parts[0].strip().lower()
                
                if rule_type == 'a':
                    if len(parts) < 3:
                        self.logger.warning(f"[警告] 第 {line_number} 行格式不完整，已跳過: {line}")
                        continue
                    
                    amount = float(parts[1].strip())
                    spin_count = int(parts[2].strip())
                    
                    rules.append(BetRule(
                        rule_type='a',
                        amount=amount,
                        spin_count=spin_count
                    ))
                    
                elif rule_type == 's':
                    if len(parts) < 5:
                        self.logger.warning(f"[警告] 第 {line_number} 行格式不完整，已跳過: {line}")
                        continue
                    
                    amount = float(parts[1].strip())
                    duration = int(parts[2].strip())
                    min_seconds = float(parts[3].strip())
                    max_seconds = float(parts[4].strip())
                    
                    rules.append(BetRule(
                        rule_type='s',
                        amount=amount,
                        duration=duration,
                        min_seconds=min_seconds,
                        max_seconds=max_seconds
                    ))
                    
                elif rule_type == 'f':
                    amount = float(parts[1].strip())
                    
                    rules.append(BetRule(
                        rule_type='f',
                        amount=amount
                    ))
                    
                else:
                    self.logger.warning(f"[警告] 第 {line_number} 行無效的規則類型 '{rule_type}'，已跳過")
                    continue
                
            except (ValueError, IndexError) as e:
                self.logger.warning(f"[警告] 第 {line_number} 行無法解析: {e}")
                continue
        
        return rules


# ============================================================================
# 代理伺服器
# ============================================================================

class ProxyConnectionHandler:
    """代理連接處理器"""
    
    def __init__(
        self, 
        upstream_proxy: ProxyInfo,
        logger: Optional[logging.Logger] = None
    ):
        self.upstream_proxy = upstream_proxy
        self.logger = logger or LoggerFactory.get_logger()
    
    def handle_connect_request(
        self, 
        client_socket: socket.socket,
        request: bytes
    ) -> None:
        """處理 HTTPS CONNECT 請求。"""
        upstream_socket = None
        try:
            upstream_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            upstream_socket.settimeout(Constants.DEFAULT_TIMEOUT_SECONDS)
            upstream_socket.connect((self.upstream_proxy.host, self.upstream_proxy.port))
            
            auth_string = f"{self.upstream_proxy.username}:{self.upstream_proxy.password}"
            auth_b64 = base64.b64encode(auth_string.encode('utf-8')).decode('ascii')
            
            request_lines = request.split(b'\r\n')
            auth_header = f"Proxy-Authorization: Basic {auth_b64}\r\n".encode('utf-8')
            
            new_request = request_lines[0] + b'\r\n' + auth_header
            for line in request_lines[1:]:
                new_request += line + b'\r\n'
            
            upstream_socket.sendall(new_request)
            
            response = upstream_socket.recv(Constants.PROXY_BUFFER_SIZE)
            
            if b'200' in response:
                client_socket.sendall(b'HTTP/1.1 200 Connection Established\r\n\r\n')
                self._forward_data(client_socket, upstream_socket)
            else:
                client_socket.sendall(b'HTTP/1.1 502 Bad Gateway\r\n\r\n')
                
        except socket.timeout:
            self.logger.warning("[警告] 上游代理連接逾時")
            with suppress(Exception):
                client_socket.sendall(b'HTTP/1.1 504 Gateway Timeout\r\n\r\n')
        except Exception as e:
            self.logger.debug(f"[除錯] CONNECT 請求處理失敗: {e}")
            with suppress(Exception):
                client_socket.sendall(b'HTTP/1.1 502 Bad Gateway\r\n\r\n')
        finally:
            if upstream_socket:
                with suppress(Exception):
                    upstream_socket.close()
    
    def handle_http_request(
        self,
        client_socket: socket.socket,
        request: bytes
    ) -> None:
        """處理普通 HTTP 請求。"""
        upstream_socket = None
        try:
            auth_string = f"{self.upstream_proxy.username}:{self.upstream_proxy.password}"
            auth_b64 = base64.b64encode(auth_string.encode('utf-8')).decode('ascii')
            
            request_lines = request.split(b'\r\n')
            auth_header = f"Proxy-Authorization: Basic {auth_b64}\r\n".encode('utf-8')
            
            new_request = request_lines[0] + b'\r\n' + auth_header
            for line in request_lines[1:]:
                new_request += line + b'\r\n'
            
            upstream_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            upstream_socket.settimeout(Constants.DEFAULT_TIMEOUT_SECONDS)
            upstream_socket.connect((self.upstream_proxy.host, self.upstream_proxy.port))
            upstream_socket.sendall(new_request)
            
            while True:
                response = upstream_socket.recv(Constants.PROXY_BUFFER_SIZE)
                if not response:
                    break
                client_socket.sendall(response)
                
        except socket.timeout:
            self.logger.warning("[警告] 上游代理回應逾時")
            with suppress(Exception):
                client_socket.sendall(b'HTTP/1.1 504 Gateway Timeout\r\n\r\n')
        except Exception as e:
            self.logger.debug(f"[除錯] HTTP 請求處理失敗: {e}")
            with suppress(Exception):
                client_socket.sendall(b'HTTP/1.1 502 Bad Gateway\r\n\r\n')
        finally:
            if upstream_socket:
                with suppress(Exception):
                    upstream_socket.close()
    
    def _forward_data(
        self, 
        source: socket.socket, 
        destination: socket.socket
    ) -> None:
        """雙向轉發數據。"""
        try:
            while True:
                ready_sockets, _, _ = select.select(
                    [source, destination], 
                    [], 
                    [], 
                    Constants.PROXY_SELECT_TIMEOUT
                )
                
                if not ready_sockets:
                    continue
                
                for sock in ready_sockets:
                    try:
                        data = sock.recv(Constants.PROXY_BUFFER_SIZE)
                        if not data:
                            return
                        
                        target = destination if sock is source else source
                        target.sendall(data)
                    except Exception:
                        return
                        
        except Exception:
            pass


class SimpleProxyServer:
    """簡易 HTTP 代理伺服器。
    
    將帶認證的遠端代理轉換為本地無需認證的代理。
    """
    
    def __init__(
        self, 
        local_port: int, 
        upstream_proxy: ProxyInfo,
        logger: Optional[logging.Logger] = None
    ):
        self.local_port = local_port
        self.upstream_proxy = upstream_proxy
        self.logger = logger or LoggerFactory.get_logger()
        self.running = False
        self.server_socket: Optional[socket.socket] = None
        self.handler = ProxyConnectionHandler(upstream_proxy, self.logger)
    
    def handle_client(self, client_socket: socket.socket) -> None:
        """處理客戶端連接。"""
        try:
            client_socket.settimeout(Constants.DEFAULT_TIMEOUT_SECONDS)
            
            request = client_socket.recv(Constants.PROXY_BUFFER_SIZE)
            if not request:
                return
            
            first_line = request.split(b'\r\n')[0].decode('utf-8', errors='ignore')
            
            if first_line.startswith('CONNECT'):
                self.handler.handle_connect_request(client_socket, request)
            else:
                self.handler.handle_http_request(client_socket, request)
                
        except socket.timeout:
            self.logger.debug("[除錯] 客戶端連接逾時")
        except Exception as e:
            self.logger.debug(f"[除錯] 處理客戶端連接時發生錯誤: {e}")
        finally:
            with suppress(Exception):
                client_socket.close()
    
    def start(self) -> None:
        """啟動代理伺服器。"""
        self.running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.server_socket.bind((Constants.PROXY_SERVER_BIND_HOST, self.local_port))
            self.server_socket.listen(5)
            
            while self.running:
                try:
                    self.server_socket.settimeout(Constants.SERVER_SOCKET_TIMEOUT)
                    client_socket, address = self.server_socket.accept()
                    
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket,),
                        daemon=True
                    )
                    client_thread.start()
                    
                except socket.timeout:
                    continue
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    if self.running:
                        self.logger.error(f"[錯誤] 接受連接時發生錯誤: {e}")
                    
        except Exception as e:
            raise ProxyServerError(f"代理伺服器啟動失敗: {e}") from e
        finally:
            self.stop()
    
    def stop(self) -> None:
        """停止代理伺服器"""
        self.running = False
        if self.server_socket:
            with suppress(Exception):
                self.server_socket.close()
            self.server_socket = None


class LocalProxyServerManager:
    """本機代理中繼伺服器管理器。
    
    為每個瀏覽器建立獨立的本機代理埠。
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or LoggerFactory.get_logger()
        self._proxy_servers: Dict[int, SimpleProxyServer] = {}
        self._proxy_threads: Dict[int, threading.Thread] = {}
        self._next_port: int = Constants.DEFAULT_PROXY_START_PORT
        self._lock = threading.Lock()
    
    def start_proxy_server(
        self, 
        upstream_proxy: ProxyInfo
    ) -> Optional[int]:
        """啟動本機代理中繼伺服器。
        
        Returns:
            本機埠號，失敗返回 None
        """
        with self._lock:
            local_port = self._next_port
            self._next_port += 1
        
        try:
            server = SimpleProxyServer(local_port, upstream_proxy, self.logger)
            
            def run_server():
                try:
                    server.start()
                except Exception as e:
                    self.logger.error(f"[錯誤] 代理伺服器執行失敗 (埠 {local_port}): {e}")
            
            server_thread = threading.Thread(target=run_server, daemon=True)
            server_thread.start()
            
            with self._lock:
                self._proxy_servers[local_port] = server
                self._proxy_threads[local_port] = server_thread
            
            time.sleep(Constants.PROXY_SERVER_START_WAIT)
            
            return local_port
            
        except Exception as e:
            self.logger.error(f"[錯誤] 啟動本機代理伺服器失敗: {e}")
            return None
    
    def stop_proxy_server(self, local_port: int) -> None:
        """停止指定的代理伺服器。"""
        server = None
        
        with self._lock:
            server = self._proxy_servers.pop(local_port, None)
            self._proxy_threads.pop(local_port, None)
        
        if server:
            try:
                server.stop()
            except Exception as e:
                self.logger.debug(f"[除錯] 停止代理伺服器時發生錯誤 (埠 {local_port}): {e}")
    
    def stop_all_servers(self) -> None:
        """停止所有代理伺服器"""
        with self._lock:
            ports = list(self._proxy_servers.keys())
        
        if ports:
            with ThreadPoolExecutor(max_workers=min(len(ports), Constants.MAX_THREAD_WORKERS)) as executor:
                executor.map(self.stop_proxy_server, ports)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_all_servers()
        return False


# ============================================================================
# 瀏覽器輔助工具
# ============================================================================

class BrowserHelper:
    """瀏覽器操作輔助類別。
    
    提供常用的瀏覽器操作方法，避免程式碼重複。
    包括座標計算、按鍵模擬等。
    """
    
    @staticmethod
    def execute_cdp_space_key(driver: WebDriver) -> None:
        """使用 Chrome DevTools Protocol 按下空白鍵。
        
        Args:
            driver: WebDriver 實例
        """
        # 按下空白鍵
        driver.execute_cdp_cmd("Input.dispatchKeyEvent", {
            "type": "keyDown",
            "key": " ",
            "code": "Space",
            "windowsVirtualKeyCode": 32,
            "nativeVirtualKeyCode": 32
        })
        # 釋放空白鍵
        driver.execute_cdp_cmd("Input.dispatchKeyEvent", {
            "type": "keyUp",
            "key": " ",
            "code": "Space",
            "windowsVirtualKeyCode": 32,
            "nativeVirtualKeyCode": 32
        })
    
    @staticmethod
    def calculate_click_position(
        canvas_rect: Dict[str, float],
        x_ratio: float,
        y_ratio: float
    ) -> Tuple[float, float]:
        """根據 Canvas 區域和比例計算點擊座標。
        
        Args:
            canvas_rect: Canvas 區域資訊 {"x", "y", "w", "h"}
            x_ratio: X 座標比例
            y_ratio: Y 座標比例
            
        Returns:
            (x, y) 實際座標
        """
        x = canvas_rect["x"] + canvas_rect["w"] * x_ratio
        y = canvas_rect["y"] + canvas_rect["h"] * y_ratio
        return x, y


# ============================================================================
# 圖片檢測器
# ============================================================================

class ImageDetector:
    """圖片檢測器。
    
    提供螢幕截圖、圖片比對和座標定位功能。
    使用 OpenCV 進行模板匹配，支援多種圖片格式。
    
    Attributes:
        logger: 日誌記錄器
        project_root: 專案根目錄
        image_dir: 圖片目錄
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """初始化圖片檢測器"""
        self.logger = logger or LoggerFactory.get_logger()
        
        # 使用輔助函式取得專案根目錄和圖片目錄
        self.project_root = get_resource_path()
        self.image_dir = get_resource_path(Constants.IMAGE_DIR)
        
        # 確保圖片目錄存在
        self.image_dir.mkdir(parents=True, exist_ok=True)
    
    def get_template_path(self, template_name: str) -> Path:
        """取得模板圖片路徑。
        
        Args:
            template_name: 模板圖片檔名
            
        Returns:
            模板圖片完整路徑
        """
        return self.image_dir / template_name
    
    def template_exists(self, template_name: str) -> bool:
        """檢查模板圖片是否存在。
        
        Args:
            template_name: 模板圖片檔名
            
        Returns:
            是否存在
        """
        return self.get_template_path(template_name).exists()
    
    def capture_screenshot(self, driver: WebDriver, save_path: Optional[Path] = None) -> np.ndarray:
        """截取瀏覽器畫面。
        
        Args:
            driver: WebDriver 實例
            save_path: 儲存路徑（可選）
            
        Returns:
            OpenCV 格式的圖片陣列 (BGR)
            
        Raises:
            ImageDetectionError: 截圖失敗
        """
        try:
            # 取得截圖（base64 格式）
            screenshot_base64 = driver.get_screenshot_as_base64()
            
            # 解碼並轉換為 OpenCV 格式
            screenshot_bytes = base64.b64decode(screenshot_base64)
            image = Image.open(io.BytesIO(screenshot_bytes))
            image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # 如果指定了儲存路徑，則儲存圖片
            if save_path:
                save_path.parent.mkdir(parents=True, exist_ok=True)
                
                # 使用支援 Unicode 路徑的方式儲存圖片
                is_success, buffer = cv2.imencode('.png', image_cv)
                if is_success:
                    with open(save_path, 'wb') as f:
                        f.write(buffer.tobytes())
                    self.logger.info(f"[資訊] 截圖已儲存 {save_path}")
                else:
                    raise ImageDetectionError(f"圖片編碼失敗")
            
            return image_cv
            
        except Exception as e:
            raise ImageDetectionError(f"截圖失敗: {e}") from e
    
    def match_template(
        self, 
        screenshot: np.ndarray, 
        template_path: Path, 
        threshold: float = Constants.MATCH_THRESHOLD
    ) -> Optional[Tuple[int, int, float]]:
        """在截圖中尋找模板圖片。
        
        Args:
            screenshot: 截圖（OpenCV 格式）
            template_path: 模板圖片路徑
            threshold: 匹配閾值（0-1）
            
        Returns:
            如果找到: (x, y, confidence) - 中心座標和信心度
            如果未找到: None
            
        Raises:
            ImageDetectionError: 檢測失敗
        """
        try:
            if not template_path.exists():
                raise FileNotFoundError(f"模板圖片不存在: {template_path}")
            
            # 讀取模板圖片（使用支援 Unicode 路徑的函式）
            template = cv2_imread_unicode(template_path, cv2.IMREAD_COLOR)
            if template is None:
                raise ImageDetectionError(f"無法讀取模板圖片: {template_path}")
            
            # 取得模板尺寸
            template_h, template_w = template.shape[:2]
            
            # 執行模板匹配
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # 檢查是否超過閾值
            if max_val >= threshold:
                # 計算中心座標
                center_x = max_loc[0] + template_w // 2
                center_y = max_loc[1] + template_h // 2
                return (center_x, center_y, max_val)
            
            return None
            
        except FileNotFoundError:
            raise
        except Exception as e:
            raise ImageDetectionError(f"圖片匹配失敗: {e}") from e
    
    def detect_in_browser(
        self, 
        driver: WebDriver, 
        template_name: str, 
        threshold: float = Constants.MATCH_THRESHOLD
    ) -> Optional[Tuple[int, int, float]]:
        """在瀏覽器中檢測模板圖片。
        
        Args:
            driver: WebDriver 實例
            template_name: 模板圖片檔名
            threshold: 匹配閾值
            
        Returns:
            如果找到: (x, y, confidence)
            如果未找到: None
        """
        try:
            # 檢查瀏覽器是否仍然有效
            try:
                _ = driver.current_url
            except Exception:
                self.logger.warning(f"[警告] 瀏覽器已關閉，無法進行圖片檢測")
                return None
            
            screenshot = self.capture_screenshot(driver)
            template_path = self.get_template_path(template_name)
            return self.match_template(screenshot, template_path, threshold)
        except Exception as e:
            self.logger.error(f"[錯誤] 瀏覽器圖片檢測失敗: {e}")
            return None


# ============================================================================
# 瀏覽器管理器
# ============================================================================

class BrowserManager:
    """瀏覽器管理器。
    
    提供 WebDriver 建立和配置功能。
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or LoggerFactory.get_logger()
    
    @staticmethod
    def create_chrome_options(local_proxy_port: Optional[int] = None) -> Options:
        """建立 Chrome 瀏覽器選項。"""
        chrome_options = Options()
        
        # 本機代理設定
        if local_proxy_port:
            proxy_address = f"http://{Constants.PROXY_SERVER_BIND_HOST}:{local_proxy_port}"
            chrome_options.add_argument(f"--proxy-server={proxy_address}")
        
        # 基本設定
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        
        # 背景執行優化設定
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_argument("--disable-background-timer-throttling")
        
        # 啟用網路加速功能
        chrome_options.add_argument("--enable-features=NetworkService,NetworkServiceInProcess")
        chrome_options.add_argument("--enable-quic")
        chrome_options.add_argument("--enable-tcp-fast-open")
        
        # 其他優化設定
        chrome_options.add_argument("--disable-sync")
        chrome_options.add_argument("--metrics-recording-only")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--disable-extensions")
        
        # 記憶體與渲染優化
        chrome_options.add_argument("--disk-cache-size=209715200")
        chrome_options.add_argument("--media-cache-size=209715200")
        
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
            "profile.content_settings.exceptions.sound": {
                "*": {"setting": 2}
            }
        })
        
        return chrome_options
    
    def create_webdriver(
        self, 
        local_proxy_port: Optional[int] = None
    ) -> WebDriver:
        """建立 WebDriver 實例。
        
        優先使用 WebDriver Manager，若失敗則使用本機驅動程式。
        """
        chrome_options = self.create_chrome_options(local_proxy_port)
        driver = None
        errors = []
        
        # 方法 1: 優先使用 WebDriver Manager
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
        except Exception as e:
            errors.append(f"WebDriver Manager: {e}")
            self.logger.warning(f"[警告] WebDriver Manager 失敗，嘗試使用本機驅動程式")
            
            # 方法 2: 使用本機驅動程式
            try:
                driver = self._create_webdriver_with_local_driver(chrome_options)
            except Exception as e2:
                errors.append(f"本機驅動程式: {e2}")
                self.logger.error(f"[錯誤] 本機驅動程式也失敗: {e2}")
        
        if driver is None:
            error_message = "無法建立瀏覽器實例。\n" + "\n".join(f"- {error}" for error in errors)
            raise BrowserCreationError(error_message)
        
        self._configure_webdriver(driver)
        return driver
    
    def _configure_webdriver(self, driver: WebDriver) -> None:
        """配置 WebDriver 超時和優化設定。"""
        with suppress(Exception):
            driver.set_page_load_timeout(Constants.DEFAULT_PAGE_LOAD_TIMEOUT)
            driver.set_script_timeout(Constants.DEFAULT_SCRIPT_TIMEOUT)
            driver.implicitly_wait(Constants.DEFAULT_IMPLICIT_WAIT)
        
        with suppress(Exception):
            driver.execute_cdp_cmd("Network.enable", {})
            driver.execute_cdp_cmd("Network.emulateNetworkConditions", {
                "offline": False,
                "downloadThroughput": -1,
                "uploadThroughput": -1,
                "latency": 0
            })
    
    def _create_webdriver_with_local_driver(self, chrome_options: Options) -> WebDriver:
        """使用本機驅動程式建立 WebDriver。"""
        project_root = get_resource_path()
        driver_path = project_root / "chromedriver.exe"
        
        if not driver_path.exists():
            raise FileNotFoundError(
                f"找不到驅動程式檔案\n"
                f"請確保 chromedriver.exe 存在於專案根目錄"
            )
        
        try:
            service = Service(str(driver_path))
            driver = webdriver.Chrome(service=service, options=chrome_options)
            return driver
        except Exception as e:
            raise BrowserCreationError(f"啟動本機驅動程式失敗: {e}") from e
    
    @contextmanager
    def create_browser_context(
        self,
        credential: UserCredential,
        index: int,
        proxy_port: Optional[int] = None
    ):
        """建立瀏覽器上下文管理器。"""
        driver = None
        try:
            driver = self.create_webdriver(local_proxy_port=proxy_port)
            context = BrowserContext(
                driver=driver,
                credential=credential,
                index=index,
                proxy_port=proxy_port
            )
            yield context
        finally:
            if driver:
                with suppress(Exception):
                    driver.quit()
                self.logger.debug(f"[除錯] 瀏覽器 #{index} 已關閉")


# ============================================================================
# 遊戲控制中心
# ============================================================================

class GameControlCenter:
    """遊戲控制中心。
    
    提供互動式命令列介面來控制多個瀏覽器，功能包括：
    - 自動按鍵（每個瀏覽器獨立執行緒）
    - 暫停/繼續操作
    - 調整下注金額
    - 購買免費遊戲
    - 關閉瀏覽器
    
    """
    
    def __init__(
        self,
        browser_threads: List['BrowserThread'],
        bet_rules: List[BetRule],
        canvas_rect: Optional[Dict[str, float]] = None,
        logger: Optional[logging.Logger] = None
    ):
        """初始化控制中心。
        
        Args:
            browser_threads: 瀏覽器執行緒列表
            bet_rules: 下注規則列表
            canvas_rect: Canvas 區域資訊（可選）
            logger: 日誌記錄器
        """
        self.logger = logger or LoggerFactory.get_logger()
        self.browser_threads = browser_threads
        self.bet_rules = bet_rules
        self.canvas_rect = canvas_rect
        
        # 控制狀態
        self.running = False
        self.auto_press_running = False
        
        # 執行緒控制
        self._stop_event = threading.Event()
        self.auto_press_threads: Dict[int, threading.Thread] = {}
    
    def _get_active_browsers(self) -> List['BrowserThread']:
        """取得所有活躍的瀏覽器執行緒。
        
        Returns:
            活躍的瀏覽器執行緒列表
        """
        return [bt for bt in self.browser_threads if bt.is_browser_alive()]
    
    def _is_browser_alive(self, driver: WebDriver) -> bool:
        """檢查瀏覽器是否仍然有效。
        
        Args:
            driver: WebDriver 實例
            
        Returns:
            bool: True 表示瀏覽器有效，False 表示已關閉
        """
        try:
            _ = driver.current_url
            return True
        except Exception:
            return False
    
    def show_help(self) -> None:
        """顯示指令說明。"""
        help_text = """
==========================================================
                    【遊戲控制中心 - 指令說明】
==========================================================

【自動操作】
  s <最小>,<最大>     開始自動按鍵（設定隨機間隔秒數）
                      範例: s 1,2  → 每次間隔 1~2 秒按空白鍵
                   
  p                   暫停目前運行的自動操作

【金額與遊戲】  
  b <金額>            調整所有瀏覽器的下注金額
                      範例: b 2, b 4, b 10, b 100
  
  f <編號>            購買免費遊戲
                      f 0      → 所有瀏覽器
                      f 1      → 第 1 個瀏覽器

【系統指令】
  h                   顯示此幫助信息

  q <編號>            關閉指定瀏覽器
                      q 0      → 關閉所有瀏覽器並退出程式
                      q 1      → 關閉第 1 個瀏覽器

==========================================================
"""
        self.logger.info(help_text)
    
    def _auto_press_loop_single(self, bt: 'BrowserThread', browser_index: int) -> None:
        """單個瀏覽器的自動按鍵循環。
        
        Args:
            bt: BrowserThread 實例
            browser_index: 瀏覽器索引（1-based）
        """
        import random
        
        press_count = 0
        username = bt.context.credential.username if bt.context else "Unknown"
        
        while not self._stop_event.is_set():
            try:
                # 檢查瀏覽器是否仍然有效
                if not bt.is_browser_alive():
                    self.logger.warning(f"瀏覽器 {browser_index} ({username}) 已關閉，停止自動按鍵")
                    break
                
                press_count += 1
                
                # 執行按空白鍵
                def press_space_task(context: BrowserContext) -> bool:
                    BrowserHelper.execute_cdp_space_key(context.driver)
                    return True
                
                bt.execute_task(press_space_task)
                
                # 每個瀏覽器使用獨立的隨機間隔
                interval = random.uniform(self.min_interval, self.max_interval)
                
                # 使用 wait 而非 sleep，這樣可以立即響應停止信號
                if self._stop_event.wait(timeout=interval):
                    break
                    
            except Exception as e:
                self.logger.error(f"瀏覽器 {browser_index} ({username}) 執行錯誤: {e}")
                self._stop_event.wait(timeout=1.0)
        
        self.logger.info(f"瀏覽器 {browser_index} ({username}) 已停止，共執行 {press_count} 次")
    
    def _start_auto_press(self) -> None:
        """為每個瀏覽器啟動獨立的自動按鍵執行緒。"""
        if self.auto_press_running:
            self.logger.warning("自動按鍵已在運行中")
            return
        
        # 檢查是否已設定間隔時間
        if not hasattr(self, 'min_interval') or not hasattr(self, 'max_interval'):
            self.logger.warning("請先使用 's <最小>,<最大>' 命令設定間隔時間")
            return
        
        # 清除停止事件
        self._stop_event.clear()
        self.auto_press_threads.clear()
        
        # 取得活躍的瀏覽器
        active_browsers = self._get_active_browsers()
        
        # 為每個瀏覽器啟動獨立執行緒
        for i, bt in enumerate(active_browsers, 1):
            thread = threading.Thread(
                target=self._auto_press_loop_single,
                args=(bt, i),
                daemon=True,
                name=f"AutoPressThread-{i}"
            )
            self.auto_press_threads[i] = thread
            thread.start()
        
        self.auto_press_running = True
        
        self.logger.info(f"[成功] 已啟動 {len(active_browsers)} 個瀏覽器的自動按鍵")
    
    def _stop_auto_press(self) -> None:
        """停止所有自動按鍵執行緒。"""
        if not self.auto_press_running:
            self.logger.warning("自動按鍵未在運行")
            return
        
        # 設置停止事件
        self._stop_event.set()
        
        # 等待所有執行緒結束
        stopped_count = 0
        for browser_index, thread in self.auto_press_threads.items():
            if thread and thread.is_alive():
                thread.join(timeout=1.0)
                
                if not thread.is_alive():
                    stopped_count += 1
                else:
                    self.logger.warning(f"瀏覽器 {browser_index} 的執行緒未能正常結束")
            else:
                stopped_count += 1
        
        self.logger.info(f"[成功] 已停止 {stopped_count}/{len(self.auto_press_threads)} 個瀏覽器")
        
        self.auto_press_threads.clear()
        self.auto_press_running = False
    
    def process_command(self, command: str) -> bool:
        """處理用戶指令。
        
        Args:
            command: 用戶輸入的指令
            
        Returns:
            是否繼續運行（False 表示退出）
        """
        command = command.strip().lower()
        
        if not command:
            return True
        
        # 解析指令和參數
        parts = command.split(maxsplit=1)
        cmd = parts[0] if parts else ""
        command_arguments = parts[1] if len(parts) > 1 else ""
        
        try:
            if cmd == 'q':
                # 關閉瀏覽器指令
                return self._handle_quit_command(command_arguments)
            
            elif cmd == 'h':
                self.show_help()
            
            elif cmd == 's':
                # 開始自動按鍵
                return self._handle_start_command(command_arguments)
            
            elif cmd == 'p':
                # 暫停指令
                if self.auto_press_running:
                    self._stop_auto_press()
                    self.logger.info("")
                    self.logger.info("[成功] 已暫停自動按鍵")
                    self.logger.info("")
                    self.show_help()
                else:
                    self.logger.warning("[警告] 目前沒有運行中的自動操作")
            
            elif cmd == 'b':
                # 調整金額（簡化版 - 尚未實作完整邏輯）
                self.logger.info("[提示] 金額調整功能尚未完整實作")
            
            elif cmd == 'f':
                # 購買免費遊戲（簡化版 - 尚未實作完整邏輯）
                self.logger.info("[提示] 購買免費遊戲功能尚未完整實作")
            
            else:
                self.logger.warning(f"[警告] 未知指令: {cmd}")
                self.logger.info("   輸入 'h' 查看指令說明")
                
        except Exception as e:
            self.logger.error(f"[錯誤] 處理指令時發生錯誤: {e}")
        
        return True
    
    def _handle_quit_command(self, arguments: str) -> bool:
        """處理關閉瀏覽器指令。
        
        Args:
            arguments: 指令參數
            
        Returns:
            是否繼續運行
        """
        if not arguments:
            self.logger.error("指令格式錯誤，請使用: q <編號>")
            self.logger.info("  q 0      - 關閉所有瀏覽器並退出")
            self.logger.info("  q 1      - 關閉第 1 個瀏覽器")
            return True
        
        try:
            index = int(arguments)
            active_browsers = self._get_active_browsers()
            
            if index == 0:
                # 關閉所有瀏覽器
                self.logger.info(f"開始關閉所有 {len(active_browsers)} 個瀏覽器...")
                
                for i, bt in enumerate(active_browsers, 1):
                    try:
                        bt.stop()
                        username = bt.context.credential.username if bt.context else "Unknown"
                        self.logger.info(f"[成功] 已關閉瀏覽器 {i} ({username})")
                    except Exception as e:
                        self.logger.error(f"關閉瀏覽器 {i} 失敗: {e}")
                
                self.logger.info("所有瀏覽器已關閉，退出控制中心")
                return False
            
            elif 1 <= index <= len(active_browsers):
                # 關閉指定瀏覽器
                bt = active_browsers[index - 1]
                username = bt.context.credential.username if bt.context else "Unknown"
                
                try:
                    bt.stop()
                    self.logger.info(f"[成功] 已關閉瀏覽器 {index} ({username})")
                except Exception as e:
                    self.logger.error(f"關閉瀏覽器 {index} 失敗: {e}")
                
                # 檢查是否還有瀏覽器在運行
                remaining = len(self._get_active_browsers())
                if remaining == 0:
                    self.logger.info("所有瀏覽器已關閉，退出控制中心")
                    return False
                else:
                    self.logger.info(f"剩餘 {remaining} 個瀏覽器仍在運行")
            else:
                self.logger.error(f"瀏覽器編號無效，請輸入 0 (全部) 或 1-{len(active_browsers)} 之間的數字")
        
        except ValueError:
            self.logger.error(f"無效的編號: {arguments}，請輸入數字")
        
        return True
    
    def _handle_start_command(self, arguments: str) -> bool:
        """處理開始自動按鍵指令。
        
        Args:
            arguments: 指令參數
            
        Returns:
            是否繼續運行
        """
        if not arguments:
            self.logger.error("[錯誤] 指令格式錯誤")
            self.logger.info("   正確格式: s <最小>,<最大>")
            self.logger.info("   範例: s 1,2  → 間隔 1~2 秒按空白鍵")
            return True
        
        # 解析用戶輸入的間隔時間
        try:
            interval_parts = arguments.split(',')
            if len(interval_parts) != 2:
                self.logger.error("[錯誤] 間隔格式錯誤，需要兩個數字")
                self.logger.info("   範例: s 1,2 或 s 1.5,3")
                return True
            
            min_interval = float(interval_parts[0].strip())
            max_interval = float(interval_parts[1].strip())
            
            if min_interval <= 0 or max_interval <= 0:
                self.logger.error("[錯誤] 間隔時間必須大於 0")
                return True
            
            if min_interval > max_interval:
                self.logger.error("[錯誤] 最小間隔不能大於最大間隔")
                self.logger.info(f"   您輸入的: 最小={min_interval}, 最大={max_interval}")
                return True
                
        except ValueError:
            self.logger.error("[錯誤] 間隔格式錯誤，請輸入有效的數字")
            self.logger.info("   範例: s 1,2 或 s 1.5,3")
            return True
        
        # 檢查是否已在運行
        if self.auto_press_running:
            self.logger.warning("[警告] 自動按鍵已在運行中")
            self.logger.info(f"   目前設定: {self.min_interval}~{self.max_interval} 秒")
            self.logger.info("   提示: 請先使用 'p' 暫停，再重新啟動")
            return True
        
        # 設置間隔時間
        self.min_interval = min_interval
        self.max_interval = max_interval
        
        active_count = len(self._get_active_browsers())
        
        self.logger.info("")
        self.logger.info("[成功] 自動按鍵已啟動")
        self.logger.info(f"  > 間隔時間: {min_interval}~{max_interval} 秒")
        self.logger.info(f"  > 瀏覽器數: {active_count} 個")
        self.logger.info("  > 暫停指令: p")
        self.logger.info("")
        
        # 啟動自動按鍵
        self._start_auto_press()
        
        return True
    
    def start(self) -> None:
        """啟動控制中心。"""
        self.running = True
        self.logger.info("")
        self.logger.info("=" * 60)
        self.logger.info("           【遊戲控制中心】已啟動")
        self.logger.info("=" * 60)
        self.logger.info("")
        
        active_count = len(self._get_active_browsers())
        self.logger.info(f"[成功] 已連接 {active_count} 個瀏覽器")
        self.logger.info("")
        
        # 自動顯示幫助訊息
        self.show_help()
        
        try:
            while self.running:
                try:
                    print(">>> ", end="", flush=True)
                    command = input().strip()
                    
                    if command:
                        if not self.process_command(command):
                            break
                    else:
                        self.logger.warning("[警告] 請輸入指令（輸入 'h' 查看幫助）")
                        
                except EOFError:
                    self.logger.info("\n[警告] 檢測到 EOF，退出控制中心")
                    break
                except KeyboardInterrupt:
                    self.logger.info("\n[警告] 使用者中斷，退出控制中心")
                    break
        finally:
            # 確保停止所有自動操作
            if self.auto_press_running:
                self._stop_auto_press()
            
            self.running = False
            self.logger.info("[成功] 控制中心已關閉")
    
    def stop(self) -> None:
        """停止控制中心。"""
        self.running = False
        
        # 確保停止自動按鍵
        if self.auto_press_running:
            self._stop_auto_press()


# ============================================================================
# 應用程式啟動器
# ============================================================================

class AutoSlotGameAppStarter:
    """應用程式啟動器。
    
    實現 main_flow_explanation.md 第 76~92 行描述的流程：
    - 清除殘留 chromedriver 程序
    - 載入配置檔案
    - 啟動瀏覽器
    - 啟動代理中繼伺服器
    - 建立瀏覽器實例（每個瀏覽器使用專屬執行緒）
    
    架構特點：
    - 每個瀏覽器都有自己的專屬執行緒 (BrowserThread)
    - 從建立到關閉的所有操作都在同一執行緒中執行
    - 透過 execute_task() 方法在瀏覽器執行緒中執行任務
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or LoggerFactory.get_logger()
        self.config_reader: Optional[ConfigReader] = None
        self.proxy_manager: Optional[LocalProxyServerManager] = None
        self.browser_manager: Optional[BrowserManager] = None
        
        # 瀏覽器執行緒列表（取代原本的 browser_contexts）
        self.browser_threads: List[BrowserThread] = []
        
        self.credentials: List[UserCredential] = []
        self.rules: List[BetRule] = []
    
    def initialize(self) -> bool:
        """執行完整的初始化流程。
        
        流程:
        1. 載入配置檔案
        2. 啟動瀏覽器
        3. 啟動代理中繼伺服器
        4. 建立瀏覽器實例
        
        Returns:
            初始化是否成功
        """
        try:
            # 步驟 1: 載入配置檔案
            self._step_load_config()
            
            # 步驟 2: 啟動瀏覽器
            browser_count = self._step_determine_browser_count()
            
            if browser_count == 0:
                self.logger.error("[錯誤] 沒有可用的用戶帳號，無法繼續")
                return False
            
            # 步驟 3: 啟動代理中繼伺服器
            proxy_ports = self._step_start_proxy_servers(browser_count)
            
            # 步驟 4: 建立瀏覽器實例
            self._step_create_browsers(browser_count, proxy_ports)
            
            return True
            
        except Exception as e:
            self.logger.error(f"[錯誤] 初始化失敗: {e}")
            return False
    
    def _step_load_config(self) -> None:
        """步驟 1: 載入配置檔案"""
        self.logger.info("=" * 60)
        self.logger.info("【步驟 1】載入配置檔案")
        self.logger.info("=" * 60)
        
        self.config_reader = ConfigReader(logger=self.logger)
        
        # 讀取用戶資料
        self.credentials = self.config_reader.read_user_credentials()
        self.logger.info(f"[成功] 讀取到 {len(self.credentials)} 個用戶帳號")
        
        # 讀取用戶規則
        self.rules = self.config_reader.read_bet_rules()
        self.logger.info(f"[成功] 讀取到 {len(self.rules)} 條規則")
        
        self.logger.info("")
    
    def _step_determine_browser_count(self) -> int:
        """步驟 2: 啟動瀏覽器
        
        Returns:
            瀏覽器數量
        """
        self.logger.info("=" * 60)
        self.logger.info("【步驟 2】啟動瀏覽器")
        self.logger.info("=" * 60)
        
        # 根據用戶數量決定瀏覽器數量，最多 MAX_BROWSER_COUNT 個
        browser_count = min(len(self.credentials), Constants.MAX_BROWSER_COUNT)
        
        self.logger.info(f"[成功] 將開啟 {browser_count} 個瀏覽器")
        self.logger.info("")
        
        return browser_count
    
    def _step_start_proxy_servers(self, browser_count: int) -> List[Optional[int]]:
        """步驟 3: 啟動代理中繼伺服器
        
        Args:
            browser_count: 瀏覽器數量
            
        Returns:
            每個瀏覽器對應的本機代理埠號列表
        """
        self.logger.info("=" * 60)
        self.logger.info("【步驟 3】啟動代理中繼伺服器")
        self.logger.info("=" * 60)
        
        self.proxy_manager = LocalProxyServerManager(logger=self.logger)
        proxy_ports: List[Optional[int]] = []
        success_count = 0
        no_proxy_count = 0
        
        for i in range(browser_count):
            credential = self.credentials[i]
            
            if credential.proxy:
                # 有代理配置，啟動中繼伺服器
                try:
                    proxy_info = ProxyInfo.from_connection_string(credential.proxy)
                    port = self.proxy_manager.start_proxy_server(proxy_info)
                    proxy_ports.append(port)
                    if port:
                        success_count += 1
                except Exception as e:
                    self.logger.warning(f"[警告] 瀏覽器 {i+1}: 無法解析代理配置 - {e}")
                    proxy_ports.append(None)
            else:
                # 沒有代理配置
                proxy_ports.append(None)
                no_proxy_count += 1
        
        # 統一輸出結果
        if success_count > 0:
            self.logger.info(f"[成功] 已啟動 {success_count} 個代理中繼伺服器")
        if no_proxy_count > 0:
            self.logger.info(f"[資訊] {no_proxy_count} 個瀏覽器無代理配置，將使用本機網路")
        
        self.logger.info("")
        return proxy_ports
    
    def _step_create_browsers(
        self, 
        browser_count: int, 
        proxy_ports: List[Optional[int]]
    ) -> None:
        """步驟 4: 建立瀏覽器實例（使用專屬執行緒）
        
        每個瀏覽器都會啟動自己的專屬執行緒，從建立到關閉的所有操作
        都在同一個執行緒中執行。
        
        Args:
            browser_count: 瀏覽器數量
            proxy_ports: 代理埠號列表
        """
        self.logger.info("=" * 60)
        self.logger.info("【步驟 4】建立瀏覽器實例")
        self.logger.info("=" * 60)
        
        self.browser_manager = BrowserManager(logger=self.logger)
        self.logger.info(f"[資訊] 正在建立 {browser_count} 個瀏覽器執行緒...")
        
        # 1. 建立並啟動所有瀏覽器執行緒
        for i in range(browser_count):
            credential = self.credentials[i]
            proxy_port = proxy_ports[i]
            
            thread = BrowserThread(
                index=i + 1,
                credential=credential,
                browser_manager=self.browser_manager,
                proxy_port=proxy_port,
                logger=self.logger
            )
            thread.start()
            self.browser_threads.append(thread)
        
        # 2. 等待所有瀏覽器就緒
        success_count = 0
        failed_indices = []
        
        for thread in self.browser_threads:
            if thread.wait_until_ready(timeout=Constants.DEFAULT_TIMEOUT_SECONDS):
                success_count += 1
            else:
                error = thread.get_creation_error()
                failed_indices.append((thread.index, str(error) if error else "未知錯誤"))
        
        # 3. 移除失敗的執行緒
        if failed_indices:
            self.browser_threads = [
                t for t in self.browser_threads if t.context is not None
            ]
        
        # 輸出結果
        if success_count == browser_count:
            self.logger.info(f"[成功] 全部 {browser_count} 個瀏覽器已建立")
        else:
            self.logger.info(f"[完成] 成功建立 {success_count}/{browser_count} 個瀏覽器")
            for idx, err in failed_indices:
                self.logger.error(f"[錯誤] 瀏覽器 {idx}: {err}")
        
        self.logger.info("")
    
    def cleanup(self) -> None:
        """清理所有資源"""
        self.logger.info("=" * 60)
        self.logger.info("【清理資源】")
        self.logger.info("=" * 60)
        
        browser_count = len(self.browser_threads)
        
        # 停止所有瀏覽器執行緒（會自動關閉瀏覽器）
        for thread in self.browser_threads:
            thread.stop()
        
        # 等待所有執行緒結束
        for thread in self.browser_threads:
            thread.join(timeout=5.0)
        
        self.browser_threads.clear()
        
        if browser_count > 0:
            self.logger.info(f"[成功] 已關閉 {browser_count} 個瀏覽器")
        
        # 停止所有代理伺服器
        if self.proxy_manager:
            self.proxy_manager.stop_all_servers()
            self.logger.info("[成功] 已停止所有代理伺服器")
        
        self.logger.info("")
    
    def get_browser_threads(self) -> List[BrowserThread]:
        """取得所有瀏覽器執行緒"""
        return self.browser_threads
    
    def get_browser_contexts(self) -> List[BrowserContext]:
        """取得所有瀏覽器上下文（向後相容）"""
        return [t.context for t in self.browser_threads if t.context is not None]
    
    def execute_on_all_browsers(
        self, 
        func: Callable[[BrowserContext], Any],
        timeout: Optional[float] = None
    ) -> List[Tuple[int, Any, Optional[Exception]]]:
        """在所有瀏覽器上並行執行任務。
        
        每個任務都會在對應瀏覽器的專屬執行緒中執行，所有任務同時啟動。
        
        Args:
            func: 要執行的函數，接收 BrowserContext 作為參數
            timeout: 每個任務的超時時間
            
        Returns:
            結果列表，每個元素為 (index, result, error)
        """
        results: List[Tuple[int, Any, Optional[Exception]]] = []
        pending_threads: List[BrowserThread] = []
        
        # 1. 先將任務分發給所有執行緒
        for thread in self.browser_threads:
            if not thread.is_browser_alive():
                results.append((thread.index, None, RuntimeError("瀏覽器已關閉")))
                continue
            
            # 重置任務完成事件
            thread._task_done_event.clear()
            thread._task_result = None
            
            # 加入任務佇列
            with thread._task_lock:
                thread._task_queue.append((func, (), {}))
            
            # 通知執行緒有新任務
            thread._task_event.set()
            pending_threads.append(thread)
        
        # 2. 等待所有任務完成
        for thread in pending_threads:
            try:
                if thread._task_done_event.wait(timeout=timeout):
                    result = thread._task_result
                    if isinstance(result, Exception):
                        results.append((thread.index, None, result))
                    else:
                        results.append((thread.index, result, None))
                else:
                    results.append((thread.index, None, TimeoutError(f"瀏覽器 {thread.index} 任務執行超時")))
            except Exception as e:
                results.append((thread.index, None, e))
        
        # 3. 按索引排序
        results.sort(key=lambda x: x[0])
        
        return results
    
    def get_credentials(self) -> List[UserCredential]:
        """取得所有用戶憑證"""
        return self.credentials
    
    def get_rules(self) -> List[BetRule]:
        """取得所有下注規則"""
        return self.rules
    
    # ========================================================================
    # 導航與登入相關方法
    # ========================================================================
    
    def navigate_to_login_page(self) -> None:
        """步驟 5: 導航到登入頁面"""
        self.logger.info("=" * 60)
        self.logger.info("【步驟 5】導航到登入頁面")
        self.logger.info("=" * 60)
        
        def navigate_task(context: BrowserContext) -> bool:
            context.driver.get(Constants.LOGIN_PAGE)
            return True
        
        results = self.execute_on_all_browsers(navigate_task)
        success_count = sum(1 for _, result, error in results if error is None and result)
        
        self.logger.info(f"[成功] {success_count}/{len(self.browser_threads)} 個瀏覽器已導航到登入頁面")
        self.logger.info("")
    
    def perform_login(self) -> None:
        """步驟 6: 執行登入操作"""
        self.logger.info("=" * 60)
        self.logger.info("【步驟 6】執行登入操作")
        self.logger.info("=" * 60)
        
        def login_task(context: BrowserContext) -> bool:
            driver = context.driver
            credential = context.credential
            
            try:
                # 1. 等待 loading 遮罩層消失（每 1 秒檢查一次，最多等 10 秒）
                for _ in range(10):
                    loading_elements = driver.find_elements(By.CSS_SELECTOR, ".loading-container")
                    if not loading_elements or not loading_elements[0].is_displayed():
                        break
                    time.sleep(1)
                
                # 2. 點擊初始登入按鈕
                initial_login_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, Constants.INITIAL_LOGIN_BUTTON))
                )
                driver.execute_script("arguments[0].click();", initial_login_btn)
                time.sleep(3)  # 等待彈窗動畫
                
                # 3. 等待登入表單顯示
                WebDriverWait(driver, 8).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, ".popup-wrap, .popup-account-container"))
                )
                
                # 4. 輸入帳號
                username_input = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, Constants.USERNAME_INPUT))
                )
                username_input.clear()
                time.sleep(1)
                username_input.send_keys(credential.username)
                
                # 5. 輸入密碼
                password_input = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, Constants.PASSWORD_INPUT))
                )
                password_input.clear()
                time.sleep(1)
                password_input.send_keys(credential.password)
                
                # 6. 點擊登入按鈕
                login_button = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, Constants.LOGIN_BUTTON))
                )
                driver.execute_script("arguments[0].click();", login_button)        
                time.sleep(3)  # 等待登入完成
                
                # 7. 關閉所有彈窗
                driver.execute_script("""
                    const popups = document.querySelectorAll('.popup-container, .popup-wrap, .popup-account-container');
                    popups.forEach(popup => {
                        popup.style.display = 'none';
                        popup.style.visibility = 'hidden';
                        popup.remove();
                    });
                    const overlays = document.querySelectorAll('[class*="overlay"], [class*="mask"]');
                    overlays.forEach(overlay => overlay.remove());
                """)
                
                return True
                
            except Exception as e:
                self.logger.warning(f"[警告] 瀏覽器 {context.index} 登入失敗: {e}")
                return False
        
        results = self.execute_on_all_browsers(login_task, timeout=60)
        success_count = sum(1 for _, result, error in results if error is None and result)
        
        self.logger.info(f"[成功] {success_count}/{len(self.browser_threads)} 個瀏覽器已完成登入")
        self.logger.info("")
    
    def navigate_to_game(self) -> None:
        """步驟 7: 導航到遊戲頁面"""
        self.logger.info("=" * 60)
        self.logger.info("【步驟 7】導航到遊戲頁面")
        self.logger.info("=" * 60)
        
        def game_task(context: BrowserContext) -> bool:
            driver = context.driver
            
            try:
                # 1. 關閉可能出現的公告彈窗
                try:
                    driver.execute_script("""
                        // 隱藏所有彈窗容器
                        const popups = document.querySelectorAll('.popup-container, .popup-wrap, .popup-account-container');
                        popups.forEach(popup => {
                            popup.style.display = 'none';
                            popup.style.visibility = 'hidden';
                            popup.remove();
                        });
                        
                        // 移除遮罩層
                        const overlays = document.querySelectorAll('[class*="overlay"], [class*="mask"]');
                        overlays.forEach(overlay => overlay.remove());
                    """)
                    time.sleep(0.5)
                except Exception:
                    pass  # 沒有彈窗也沒關係
                
                # 2. 點擊搜尋按鈕
                search_btn = driver.find_element(By.XPATH, Constants.SEARCH_BUTTON)
                search_btn.click()
                time.sleep(3)  # 等待搜尋輸入框顯示
                
                # 3. 輸入「戰神」
                search_input = driver.find_element(By.XPATH, Constants.SEARCH_INPUT)
                search_input.clear()
                search_input.send_keys('戰神')
                search_input.send_keys('\n')
                time.sleep(5)  # 等待搜尋結果載入
                
                # 4. 點擊遊戲
                game_element = driver.find_element(By.XPATH, Constants.GAME_XPATH)
                game_element.click()
                time.sleep(5)  # 等待遊戲載入
                
                # 5. 切換到 iframe
                time.sleep(3)  # 等待 iframe 載入
                iframe = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, Constants.GAME_IFRAME))
                )
                driver.switch_to.frame(iframe)
                
                return True
                
            except Exception as e:
                self.logger.warning(f"[警告] 瀏覽器 {context.index} 進入遊戲失敗: {e}")
                return False
        
        results = self.execute_on_all_browsers(game_task, timeout=60)
        success_count = sum(1 for _, result, error in results if error is None and result)
        
        self.logger.info(f"[成功] {success_count}/{len(self.browser_threads)} 個瀏覽器已進入遊戲")
        self.logger.info("")
    
    def arrange_windows(self) -> None:
        """步驟 8: 調整視窗排列"""
        self.logger.info("=" * 60)
        self.logger.info("【步驟 8】調整視窗排列")
        self.logger.info("=" * 60)
        
        width = Constants.DEFAULT_WINDOW_WIDTH
        height = Constants.DEFAULT_WINDOW_HEIGHT
        columns = Constants.DEFAULT_WINDOW_COLUMNS
        
        def arrange_task(context: BrowserContext) -> bool:
            index = context.index
            row = (index - 1) // columns
            col = (index - 1) % columns
            
            x = col * width
            y = row * height
            
            context.driver.set_window_size(width, height)
            context.driver.set_window_position(x, y)
            return True
        
        results = self.execute_on_all_browsers(arrange_task)
        success_count = sum(1 for _, result, error in results if error is None and result)
        
        self.logger.info(f"[成功] {success_count}/{len(self.browser_threads)} 個視窗已排列完成 ({columns} 列, {width}x{height})")
        self.logger.info("")
    
    def execute_image_detection_flow(self) -> None:
        """步驟 9: 執行圖片檢測流程
        
        包含 game_login 和 game_confirm 的檢測與處理。
        流程:
        1. 檢測 game_login → 點擊
        2. 檢測 game_confirm → 點擊
        """
        self.logger.info("=" * 60)
        self.logger.info("【步驟 9】執行圖片檢測流程")
        self.logger.info("=" * 60)
        
        if not self.browser_threads:
            self.logger.error("[錯誤] 沒有可用的瀏覽器實例")
            return
        
        # 初始化圖片檢測器
        image_detector = ImageDetector(logger=self.logger)
        
        # 階段 1: 處理 game_login
        self.logger.info("")
        self.logger.info("【階段 1】檢測 game_login 畫面")
        self._handle_game_login(image_detector)
        
        # 階段 2: 處理 game_confirm
        self.logger.info("")
        self.logger.info("【階段 2】檢測 game_confirm 畫面")
        self._handle_game_confirm(image_detector)
        
        self.logger.info("")
        self.logger.info("[成功] 圖片檢測與初始化完成")
        self.logger.info("")
    
    def _handle_game_login(self, image_detector: ImageDetector) -> None:
        """處理 game_login 的檢測與點擊。
        
        Args:
            image_detector: 圖片檢測器實例
        """
        template_name = Constants.GAME_LOGIN
        display_name = "game_login"
        
        # 1. 檢查模板是否存在，若不存在則引導用戶擷取
        if not image_detector.template_exists(template_name):
            self._prompt_capture_template(image_detector, template_name, display_name)
        
        # 2. 持續檢測直到所有瀏覽器都找到圖片
        self._continuous_detect_until_found(image_detector, template_name, display_name)
        
        # 3. 等待一下後點擊
        time.sleep(1)
        
        # 4. 使用 Canvas 比例計算座標並點擊
        def click_game_login(context: BrowserContext) -> bool:
            try:
                driver = context.driver
                
                # 取得 Canvas 區域
                rect = driver.execute_script(f"""
                    const canvas = document.getElementById('{Constants.GAME_CANVAS}');
                    const r = canvas.getBoundingClientRect();
                    return {{x: r.left, y: r.top, w: r.width, h: r.height}};
                """)
                
                # 使用 calculate_click_position 計算點擊座標
                click_x, click_y = BrowserHelper.calculate_click_position(
                    rect,
                    Constants.GAME_LOGIN_BUTTON_X_RATIO,
                    Constants.GAME_LOGIN_BUTTON_Y_RATIO
                )
                
                # 執行 CDP 點擊
                for event_type in ["mousePressed", "mouseReleased"]:
                    driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
                        "type": event_type,
                        "x": click_x,
                        "y": click_y,
                        "button": "left",
                        "clickCount": 1
                    })
                self.logger.debug(f"[除錯] 瀏覽器 {context.index} 已點擊 {display_name} (座標: {click_x:.0f}, {click_y:.0f})")
                return True
                
            except Exception as e:
                self.logger.error(f"[錯誤] 瀏覽器 {context.index} 點擊 {display_name} 失敗: {e}")
                return False
        
        results = self.execute_on_all_browsers(click_game_login)
        success_count = sum(1 for _, result, error in results if error is None and result)
        self.logger.info(f"[成功] {success_count}/{len(self.browser_threads)} 個瀏覽器已點擊 {display_name}")
        
        # 5. 等待圖片消失
        self._wait_for_image_disappear(image_detector, template_name)
    
    def _handle_game_confirm(self, image_detector: ImageDetector) -> None:
        """處理 game_confirm 的檢測與點擊。
        
        Args:
            image_detector: 圖片檢測器實例
        """
        template_name = Constants.GAME_CONFIRM
        display_name = "game_confirm"
        
        # 1. 檢查模板是否存在，若不存在則引導用戶擷取
        if not image_detector.template_exists(template_name):
            self._prompt_capture_template(image_detector, template_name, display_name)
        
        # 2. 持續檢測直到所有瀏覽器都找到圖片
        self._continuous_detect_until_found(image_detector, template_name, display_name)
        
        # 3. 等待一下後點擊
        time.sleep(1)
        
        # 4. 使用 Canvas 比例計算座標並點擊
        def click_game_confirm(context: BrowserContext) -> bool:
            try:
                driver = context.driver
                
                # 取得 Canvas 區域
                rect = driver.execute_script(f"""
                    const canvas = document.getElementById('{Constants.GAME_CANVAS}');
                    const r = canvas.getBoundingClientRect();
                    return {{x: r.left, y: r.top, w: r.width, h: r.height}};
                """)
                
                # 使用 calculate_click_position 計算點擊座標
                click_x, click_y = BrowserHelper.calculate_click_position(
                    rect,
                    Constants.GAME_CONFIRM_BUTTON_X_RATIO,
                    Constants.GAME_CONFIRM_BUTTON_Y_RATIO
                )
                
                # 執行 CDP 點擊
                for event_type in ["mousePressed", "mouseReleased"]:
                    driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
                        "type": event_type,
                        "x": click_x,
                        "y": click_y,
                        "button": "left",
                        "clickCount": 1
                    })
                self.logger.debug(f"[除錯] 瀏覽器 {context.index} 已點擊 {display_name} (座標: {click_x:.0f}, {click_y:.0f})")
                return True
                
            except Exception as e:
                self.logger.error(f"[錯誤] 瀏覽器 {context.index} 點擊 {display_name} 失敗: {e}")
                return False
        
        results = self.execute_on_all_browsers(click_game_confirm)
        success_count = sum(1 for _, result, error in results if error is None and result)
        self.logger.info(f"[成功] {success_count}/{len(self.browser_threads)} 個瀏覽器已點擊 {display_name}")
        
        # 5. 等待圖片消失
        self._wait_for_image_disappear(image_detector, template_name)
        
        # 6. 等待遊戲完全載入
        time.sleep(3)
        self.logger.info("[成功] 所有瀏覽器已準備就緒")
    
    def _continuous_detect_until_found(
        self, 
        image_detector: ImageDetector, 
        template_name: str, 
        display_name: str
    ) -> List[Optional[Tuple[int, int, float]]]:
        """持續檢測直到在所有瀏覽器中找到圖片。
        
        Args:
            image_detector: 圖片檢測器實例
            template_name: 模板圖片檔名
            display_name: 顯示名稱
            
        Returns:
            檢測結果列表
        """
        attempt = 0
        total_browsers = len(self.browser_threads)
        
        self.logger.info(f"[資訊] 開始檢測 {display_name}...")
        
        while True:
            attempt += 1
            
            # 在所有瀏覽器中檢測
            detection_results: List[Optional[Tuple[int, int, float]]] = []
            
            def detect_task(context: BrowserContext) -> Optional[Tuple[int, int, float]]:
                return image_detector.detect_in_browser(context.driver, template_name)
            
            results = self.execute_on_all_browsers(detect_task)
            detection_results = [result for _, result, error in results if error is None]
            
            found_count = sum(1 for result in detection_results if result is not None)
            
            # 當所有瀏覽器都找到圖片時返回
            if found_count == total_browsers:
                self.logger.info(f"[成功] 所有瀏覽器都已檢測到 {display_name}")
                return detection_results
            
            # 每 10 次檢測顯示一次進度
            if attempt % Constants.DETECTION_PROGRESS_INTERVAL == 0:
                self.logger.info(f"   檢測進度: {found_count}/{total_browsers} 個瀏覽器已就緒")
                sys.stdout.flush()  # 確保緩衝區刷新
            
            time.sleep(Constants.DETECTION_INTERVAL)
    
    def _prompt_capture_template(
        self, 
        image_detector: ImageDetector, 
        template_name: str, 
        display_name: str
    ) -> None:
        """提示用戶擷取模板圖片。
        
        當模板圖片不存在時，引導用戶選擇瀏覽器並擷取畫面作為模板。
        
        Args:
            image_detector: 圖片檢測器實例
            template_name: 模板檔名
            display_name: 顯示名稱
        """
        self.logger.info("")
        self.logger.info("=" * 60)
        self.logger.info(f"[警告] 模板圖片不存在: {template_name}")
        self.logger.info("=" * 60)
        self.logger.info("")
        self.logger.info(f"[提示] 需要擷取 {display_name} 的參考圖片")
        self.logger.info("   請確保目標瀏覽器的遊戲畫面已顯示目標內容")
        self.logger.info("")
        
        # 檢查是否有可用的瀏覽器
        if not self.browser_threads:
            self.logger.error("[錯誤] 沒有可用的瀏覽器實例")
            raise RuntimeError("沒有可用的瀏覽器實例")
        
        # 顯示可選擇的瀏覽器列表
        self.logger.info("請選擇要擷取的瀏覽器:")
        available_browsers = []
        for thread in self.browser_threads:
            if thread.context and thread.is_browser_alive():
                username = thread.context.credential.username
                self.logger.info(f"  {thread.index}  - 瀏覽器 {thread.index} ({username})")
                available_browsers.append(thread)
        
        if not available_browsers:
            self.logger.error("[錯誤] 沒有可用的瀏覽器")
            raise RuntimeError("沒有可用的瀏覽器")
        
        self.logger.info("  q  - 取消")
        self.logger.info("")
        
        try:
            print("請輸入編號: ", end="", flush=True)
            sys.stdout.flush()  # 確保緩衝區刷新
            user_input = input().strip().lower()
            
            # 檢查是否要取消
            if user_input == 'q':
                self.logger.warning("[警告] 使用者取消擷取")
                raise KeyboardInterrupt("使用者取消")
            
            # 解析瀏覽器編號
            try:
                browser_index = int(user_input)
                
                # 尋找對應的瀏覽器
                selected_thread = None
                for thread in available_browsers:
                    if thread.index == browser_index:
                        selected_thread = thread
                        break
                
                if selected_thread is None:
                    self.logger.error(f"[錯誤] 無效的瀏覽器編號: {browser_index}")
                    # 遞迴重試
                    self._prompt_capture_template(image_detector, template_name, display_name)
                    return
                
                # 擷取並儲存模板
                template_path = image_detector.get_template_path(template_name)
                image_detector.capture_screenshot(selected_thread.context.driver, template_path)
                
                self.logger.info("")
                self.logger.info(f"[成功] 模板圖片已建立: {template_path}")
                self.logger.info("")
                
            except ValueError:
                self.logger.error(f"[錯誤] 無效的輸入: {user_input}")
                # 遞迴重試
                self._prompt_capture_template(image_detector, template_name, display_name)
                return
            
        except (EOFError, KeyboardInterrupt):
            self.logger.warning("")
            self.logger.warning("[警告] 使用者取消擷取")
            raise
    
    def _wait_for_image_disappear(self, image_detector: ImageDetector, template_name: str) -> None:
        """持續等待圖片在所有瀏覽器中消失。
        
        Args:
            image_detector: 圖片檢測器實例
            template_name: 模板圖片檔名
        """
        attempt = 0
        total_browsers = len(self.browser_threads)
        
        while True:
            attempt += 1
            
            # 檢測所有瀏覽器中仍存在圖片的數量
            still_present_count = 0
            
            def detect_task(context: BrowserContext) -> bool:
                """返回 True 表示圖片仍存在"""
                result = image_detector.detect_in_browser(context.driver, template_name)
                return result is not None
            
            results = self.execute_on_all_browsers(detect_task)
            still_present_count = sum(1 for _, result, error in results if error is None and result)
            
            disappeared_count = total_browsers - still_present_count
            
            # 如果所有瀏覽器都沒有找到圖片，則返回
            if still_present_count == 0:
                self.logger.info(f"[成功] 圖片已消失")
                return
            
            # 每 10 次檢測顯示一次進度
            if attempt % 10 == 0:
                self.logger.info(f"   等待中... ({disappeared_count}/{total_browsers} 已消失)")
                sys.stdout.flush()  # 確保緩衝區刷新
            
            time.sleep(Constants.DETECTION_INTERVAL)
    
    def start_control_center(self) -> None:
        """步驟 10: 啟動遊戲控制中心
        
        建立並啟動 GameControlCenter 實例，提供互動式命令列介面。
        對應 main_flow_explanation.md 第 105 行:
        ClickLobbyConfirm --> StartControlCenter[啟動遊戲控制中心]
        """
        self.logger.info("=" * 60)
        self.logger.info("【步驟 10】啟動遊戲控制中心")
        self.logger.info("=" * 60)
        
        if not self.browser_threads:
            self.logger.error("[錯誤] 沒有可用的瀏覽器實例")
            return
        
        # 嘗試取得 Canvas 區域資訊（用於點擊座標計算）
        canvas_rect = None
        for bt in self.browser_threads:
            if bt.context and bt.is_browser_alive():
                try:
                    def get_canvas_rect(context: BrowserContext) -> Optional[Dict[str, float]]:
                        return context.driver.execute_script(f"""
                            const canvas = document.getElementById('{Constants.GAME_CANVAS}');
                            if (!canvas) return null;
                            const r = canvas.getBoundingClientRect();
                            return {{x: r.left, y: r.top, w: r.width, h: r.height}};
                        """)
                    
                    result = bt.execute_task(get_canvas_rect)
                    if result:
                        canvas_rect = result
                        break
                except Exception:
                    pass
        
        # 建立控制中心實例
        control_center = GameControlCenter(
            browser_threads=self.browser_threads,
            bet_rules=self.rules,
            canvas_rect=canvas_rect,
            logger=self.logger
        )
        
        # 啟動控制中心（阻塞式，直到使用者退出）
        control_center.start()


# ============================================================================
# 主程式入口
# ============================================================================

def main():
    """主程式入口點"""
    logger = LoggerFactory.get_logger()
    
    logger.info("")
    logger.info("=" * 60)
    logger.info(f"【{Constants.SYSTEM_NAME}】")
    logger.info(f"  版本: {Constants.VERSION}")
    logger.info("=" * 60)
    logger.info("")
    
    # 建立啟動器
    starter = AutoSlotGameAppStarter(logger=logger)
    
    try:
        # 執行初始化流程（步驟 1-4）
        if starter.initialize():
            browser_threads = starter.get_browser_threads()
            
            logger.info("=" * 60)
            logger.info("【初始化完成】")
            logger.info("=" * 60)
            logger.info(f"[成功] 瀏覽器: {len(browser_threads)} | 用戶: {len(starter.get_credentials())} | 規則: {len(starter.get_rules())}")
            logger.info("")
            
            # 步驟 5: 導航到登入頁面
            starter.navigate_to_login_page()
            
            # 步驟 6: 執行登入操作
            starter.perform_login()
            
            # 步驟 7: 導航到遊戲頁面
            starter.navigate_to_game()
            
            # 步驟 8: 調整視窗排列
            starter.arrange_windows()
            
            # 步驟 9: 執行圖片檢測流程
            starter.execute_image_detection_flow()
            
            logger.info("=" * 60)
            logger.info("【啟動完成】")
            logger.info("=" * 60)
            logger.info("[成功] 所有瀏覽器已就緒")
            logger.info("")
            
            # 步驟 10: 啟動遊戲控制中心（阻塞式，直到使用者退出）
            starter.start_control_center()
            
        else:
            logger.error("[錯誤] 初始化失敗，程式退出")
            
    except KeyboardInterrupt:
        logger.info("")
        logger.info("[資訊] 收到中斷信號，正在清理...")
    except Exception as e:
        logger.error(f"[錯誤] 程式執行時發生錯誤: {e}")
    finally:
        # 清理資源
        starter.cleanup()
        logger.info("[資訊] 程式已結束")


if __name__ == "__main__":
    main()
