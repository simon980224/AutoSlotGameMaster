"""
賽特二遊戲自動化系統

核心特性:
- 完整型別提示與協議 (Protocol)
- 上下文管理器與資源自動清理
- 依賴注入與工廠模式
- 執行緒池並行處理
- 本地 Proxy 中繼伺服器
- 圖片識別與自動化操作
- 多瀏覽器實例管理
- 彩色日誌系統
- 完善的錯誤處理與重試機制

作者: 凡臻科技
版本: 1.1.2
Python: 3.8+

版本歷史:
- v1.1.2: 瀏覽器建立時即固定視窗大小
  * create_browser_context 自動啟動 WindowSizeLocker 監控
  * 瀏覽器關閉時自動停止視窗監控執行緒
- v1.1.1: 優化視窗管理機制
  * WindowSizeLocker 自動監控視窗大小（預設 1280x720）
  * 移除視窗排列功能，簡化為單純的大小控制
  * resize_and_position 改為自動啟動視窗大小鎖定器
  * 視窗大小改變時顯示重置通知（🔄 圖示）
- v1.1.0: 優化座標系統與視窗管理
  * 視窗大小從 600x400 升級至 1280x720
  * 所有按鈕座標改為基於 Canvas 的動態比例計算
  * 新增 WindowSizeLocker 類別，持續鎖定視窗大小
  * BETSIZE 按鈕座標改為相對於 Canvas 的比例座標
  * 新增 BrowserHelper.check_and_fix_window_size() 方法
- v1.0.0: 賽特二初始版本發布
"""

import logging
import sys
import platform
import socket
import select
import base64
import time
import subprocess
from typing import Optional, List, Dict, Tuple, Any, Callable, Protocol, Union
from pathlib import Path
from dataclasses import dataclass, field
from contextlib import contextmanager, suppress
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
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


# 導出的公共 API
__all__ = [
    # 常量
    'Constants',
    # 資料類別
    'UserCredential',
    'BetRule',
    'ProxyInfo',
    'BrowserContext',
    'OperationResult',
    # 例外類別
    'AutoSlotGameError',
    'ConfigurationError',
    'BrowserCreationError',
    'ProxyServerError',
    'ImageDetectionError',
    # 日誌類別
    'LogLevel',
    'LoggerFactory',
    # 輔助類別
    'BrowserHelper',
    'WindowSizeLocker',
    # 主要類別
    'ConfigReader',
    'BrowserManager',
    'LocalProxyServerManager',
    'SyncBrowserOperator',
    'ImageDetector',
    'BrowserRecoveryManager',
    'GameControlCenter',
    'AutoSlotGameApp',
]


# ============================================================================
# 輔助函式
# ============================================================================

def cleanup_chromedriver_processes() -> None:
    """清除所有緩存的 chromedriver 程序。
    
    在程式啟動前執行，確保沒有殘留的 chromedriver 程序佔用資源。
    支援 Windows、macOS 和 Linux 作業系統。
    """
    logger = LoggerFactory.get_logger()
    system = platform.system().lower()
    
    try:
        if system == "windows":
            # Windows: 使用 taskkill 命令
            result = subprocess.run(
                ["taskkill", "/F", "/IM", "chromedriver.exe"],
                capture_output=True,
                text=True,
                timeout=Constants.CLEANUP_PROCESS_TIMEOUT
            )
            
            # 檢查結果
            if result.returncode == 0:
                logger.info("✓ 已清除 Windows 上的 chromedriver 程序")
            elif "找不到" in result.stdout or "not found" in result.stdout.lower():
                logger.debug("沒有執行中的 chromedriver 程序")
            else:
                logger.debug(f"taskkill 執行結果: {result.stdout.strip()}")
                
        elif system in ["darwin", "linux"]:
            # macOS/Linux: 使用 killall 命令
            result = subprocess.run(
                ["killall", "-9", "chromedriver"],
                capture_output=True,
                text=True,
                timeout=Constants.CLEANUP_PROCESS_TIMEOUT
            )
            
            # killall 在沒有找到程序時會返回非 0，這是正常的
            if result.returncode == 0:
                logger.info(f"✓ 已清除 {system.upper()} 上的 chromedriver 程序")
            else:
                logger.debug("沒有執行中的 chromedriver 程序")
        else:
            logger.warning(f"不支援的作業系統: {system}，跳過清除 chromedriver")
            
    except subprocess.TimeoutExpired:
        logger.warning("清除 chromedriver 程序逾時")
    except FileNotFoundError:
        logger.debug(f"系統找不到清除命令（{system}），可能沒有執行中的 chromedriver")
    except Exception as e:
        logger.warning(f"清除 chromedriver 程序時發生錯誤: {e}")


def get_resource_path(relative_path: str = "") -> Path:
    """取得資源檔案的絕對路徑。
    
    在開發環境中，返回專案根目錄的路徑。
    在打包後的環境中，返回 exe 所在目錄的路徑（而非臨時目錄）。
    
    Args:
        relative_path: 相對於根目錄的路徑
        
    Returns:
        資源檔案的絕對路徑
    """
    if getattr(sys, 'frozen', False):
        # 打包後：使用 exe 所在目錄（不是 _MEIPASS 臨時目錄）
        # 因為 lib 和 img 應該放在 exe 旁邊，方便使用者編輯
        base_path = Path(sys.executable).resolve().parent
    else:
        # 開發環境：使用 main.py 的父目錄的父目錄
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
        
    except Exception as e:
        # 返回 None 保持與 cv2.imread() 相同的行為
        return None


# ============================================================================
# 常量定義
# ============================================================================

class Constants:
    """系統常量"""
    DEFAULT_LIB_PATH = "lib"
    DEFAULT_CREDENTIALS_FILE = "用戶資料.txt"
    DEFAULT_RULES_FILE = "用戶規則.txt"
    
    DEFAULT_PROXY_START_PORT = 9000
    DEFAULT_TIMEOUT_SECONDS = 30
    DEFAULT_PAGE_LOAD_TIMEOUT = 600
    DEFAULT_SCRIPT_TIMEOUT = 600
    DEFAULT_IMPLICIT_WAIT = 60
    
    MAX_THREAD_WORKERS = 10
    PROXY_SERVER_BIND_HOST = "127.0.0.1"
    PROXY_BUFFER_SIZE = 4096
    PROXY_SELECT_TIMEOUT = 1.0
    
    # URL 配置
    LOGIN_PAGE = "https://www.welove999.com/login?id=login"
    
    # 頁面元素選擇器
    USERNAME_INPUT = "//input[@placeholder='請輸入會員帳號']"
    PASSWORD_INPUT = "//input[@placeholder='請輸入密碼']"
    LOGIN_BUTTON = "/html/body/div[1]/div/div[1]/div/div/div[2]/div[4]/div[2]"
    
    # 遊戲導航選擇器
    GAME_CATEGORY_URL = "https://www.welove999.com/game?type=slot&code=BNG&id=all"
    GAME_PROVIDER_BUTTON = "/html/body/div/div/div[2]/div/div/div[1]/div[8]/div[1]"
    START_GAME_BUTTON = "//*[@id='gameList']/div[2]/div[2]/button"
    
    GAME_CANVAS = "GameCanvas"
    
    # 圖片檢測配置
    IMAGE_DIR = "img"
    LOBBY_LOGIN = "lobby_login.png"
    LOBBY_CONFIRM = "lobby_confirm.png"
    ERROR_MESSAGE = "error_message.png"
    MATCH_THRESHOLD = 0.8  # 圖片匹配閾值
    BETSIZE_MATCH_THRESHOLD = 0.85  # 金額識別匹配閾值
    DETECTION_INTERVAL = 1.0  # 檢測間隔（秒）
    MAX_DETECTION_ATTEMPTS = 60  # 最大檢測次數
    
    # Canvas 動態計算比例（用於點擊座標）
    # lobby_login 按鈕座標比例
    LOBBY_LOGIN_BUTTON_X_RATIO = 0.50  # lobby_login 開始遊戲按鈕 X 座標比例
    LOBBY_LOGIN_BUTTON_Y_RATIO = 0.90  # lobby_login 開始遊戲按鈕 Y 座標比例
    
    # lobby_confirm 按鈕座標比例
    LOBBY_CONFIRM_BUTTON_X_RATIO = 0.75  # lobby_confirm 確認按鈕 X 座標比例
    LOBBY_CONFIRM_BUTTON_Y_RATIO = 0.86  # lobby_confirm 確認按鈕 Y 座標比例
    
    # 購買免費遊戲按鈕座標比例
    BUY_FREE_GAME_BUTTON_X_RATIO = 0.14025  # 免費遊戲區域按鈕 X 座標比例
    BUY_FREE_GAME_BUTTON_Y_RATIO = 0.75  # 免費遊戲區域按鈕 Y 座標比例
    BUY_FREE_GAME_CONFIRM_X_RATIO = 0.597  # 免費遊戲確認按鈕 X 座標比例
    BUY_FREE_GAME_CONFIRM_Y_RATIO = 0.89   # 免費遊戲確認按鈕 Y 座標比例
    BUY_FREE_GAME_WAIT_SECONDS = 10  # 購買後等待秒數
    
    # 自動旋轉按鈕座標比例
    AUTO_SPIN_BUTTON_X_RATIO = 0.78  # 自動轉按鈕 X 座標比例
    AUTO_SPIN_BUTTON_Y_RATIO = 0.75   # 自動轉按鈕 Y 座標比例
    AUTO_SPIN_10_X_RATIO = 0.421875   # 10次按鈕 X 座標比例
    AUTO_SPIN_10_Y_RATIO = 0.5        # 10次按鈕 Y 座標比例
    AUTO_SPIN_50_X_RATIO = 0.5        # 50次按鈕 X 座標比例
    AUTO_SPIN_50_Y_RATIO = 0.5        # 50次按鈕 Y 座標比例
    AUTO_SPIN_100_X_RATIO = 0.578125  # 100次按鈕 X 座標比例
    AUTO_SPIN_100_Y_RATIO = 0.5       # 100次按鈕 Y 座標比例
    
    # 操作相關常量
    DEFAULT_WAIT_SECONDS = 3  # 預設等待時間（秒）
    DETECTION_PROGRESS_INTERVAL = 20  # 檢測進度顯示間隔
    
    # 操作等待時間（秒）
    LOGIN_WAIT_TIME = 5          # 登入後等待時間
    POPUP_WAIT_TIME = 5          # 等待彈窗出現時間
    GAME_NAVIGATION_WAIT = 3     # 遊戲導航等待時間
    TAB_SWITCH_WAIT = 3          # 分頁切換等待時間
    BETSIZE_ADJUST_STEP_WAIT = 0.3  # 調整金額每步等待時間
    BETSIZE_ADJUST_VERIFY_WAIT = 1.0  # 調整金額驗證前等待時間
    BETSIZE_ADJUST_RETRY_WAIT = 0.5  # 調整金額重試等待時間
    BETSIZE_READ_RETRY_WAIT = 0.5    # 讀取金額重試等待時間
    FREE_GAME_CLICK_WAIT = 2     # 免費遊戲點擊間隔
    FREE_GAME_SETTLE_INITIAL_WAIT = 3  # 免費遊戲結算初始等待
    FREE_GAME_SETTLE_CLICK_INTERVAL = 3  # 免費遊戲結算點擊間隔
    AUTO_SPIN_MENU_WAIT = 0.5    # 自動旋轉選單等待時間
    PROXY_SERVER_START_WAIT = 1  # Proxy 伺服器啟動等待時間
    TEMPLATE_CAPTURE_WAIT = 1    # 模板截取後等待時間
    DETECTION_COMPLETE_WAIT = 2  # 檢測完成後等待時間
    RULE_SWITCH_WAIT = 1.0       # 規則切換等待時間
    AUTO_PRESS_THREAD_JOIN_TIMEOUT = 2.0  # 自動按鍵執行緒結束等待時間
    AUTO_PRESS_STOP_TIMEOUT = 5.0  # 自動按鍵停止等待超時時間
    STOP_EVENT_WAIT_TIMEOUT = 5.0  # 停止事件等待超時時間
    STOP_EVENT_ERROR_WAIT = 1.0    # 停止事件錯誤等待時間
    SERVER_SOCKET_TIMEOUT = 1.0    # 伺服器 Socket 超時時間
    CLEANUP_PROCESS_TIMEOUT = 10   # 清除程序超時時間（秒）
    
    # 重試與循環配置
    BETSIZE_ADJUST_MAX_ATTEMPTS = 200  # 調整金額最大嘗試次數
    BETSIZE_READ_MAX_RETRIES = 2       # 讀取金額最大重試次數
    FREE_GAME_SETTLE_CLICK_COUNT = 5   # 免費遊戲結算點擊次數
    DETECTION_WAIT_MAX_ATTEMPTS = 20   # 檢測等待最大嘗試次數
    LOBBY_CONFIRM_CHECK_ATTEMPTS = 3   # lobby_confirm 檢測嘗試次數（之後檢查錯誤）
    
    # 視窗排列配置
    DEFAULT_WINDOW_WIDTH = 1280
    DEFAULT_WINDOW_HEIGHT = 720
    DEFAULT_WINDOW_COLUMNS = 4
    
    # 下注金額調整按鈕座標比例（基於 Canvas 區域）
    BETSIZE_INCREASE_BUTTON_X_RATIO = 0.796   # 增加金額按鈕 X 座標比例
    BETSIZE_INCREASE_BUTTON_Y_RATIO = 0.89    # 增加金額按鈕 Y 座標比例
    BETSIZE_DECREASE_BUTTON_X_RATIO = 0.6325  # 減少金額按鈕 X 座標比例
    BETSIZE_DECREASE_BUTTON_Y_RATIO = 0.89    # 減少金額按鈕 Y 座標比例
    BETSIZE_DISPLAY_X_RATIO = 0.71          # 金額顯示位置 X 座標比例
    BETSIZE_DISPLAY_Y_RATIO = 0.89            # 金額顯示位置 Y 座標比例

    # 錯誤訊息圖片識別座標（基於預設視窗大小）
    ERROR_MESSAGE_LEFT_X = 240  # 左側錯誤訊息區域 X 座標
    ERROR_MESSAGE_LEFT_Y = 190  # 左側錯誤訊息區域 Y 座標
    ERROR_MESSAGE_RIGHT_X = 360  # 右側錯誤訊息區域 X 座標
    ERROR_MESSAGE_RIGHT_Y = 190   # 右側錯誤訊息區域 Y 座標
    ERROR_MESSAGE_PERSIST_SECONDS = 1  # 錯誤訊息持續秒數閾值

    # 截圖裁切範圍（像素，Retina 顯示器會自動 2 倍縮放）
    BETSIZE_CROP_MARGIN_X = 150   # 金額模板水平裁切邊距（實際 300px）
    BETSIZE_CROP_MARGIN_Y = 40   # 金額模板垂直裁切邊距（實際 600px）
    TEMPLATE_CROP_MARGIN = 20    # 通用模板裁切邊距
    
    # 遊戲金額配置（使用 frozenset 提升查詢效率）
    GAME_BETSIZE = frozenset((
        2, 4, 6, 8, 10, 12, 14, 16, 18, 20,
        24, 30, 32, 36, 40, 42, 48, 54, 56, 60,
        64, 72, 80, 96, 100, 112, 120, 128, 140, 144,
        160, 180, 200, 240, 280, 300, 320, 360, 400, 420,
        480, 500, 540, 560, 600, 640, 700, 720, 800, 840,
        900, 960, 980, 1000, 1080, 1120, 1200, 1260, 1280, 1400,
        1440, 1600, 1800, 2000
    ))
    
    # 遊戲金額列表（用於索引計算）
    GAME_BETSIZE_TUPLE = (
        2, 4, 6, 8, 10, 12, 14, 16, 18, 20,
        24, 30, 32, 36, 40, 42, 48, 54, 56, 60,
        64, 72, 80, 96, 100, 112, 120, 128, 140, 144,
        160, 180, 200, 240, 280, 300, 320, 360, 400, 420,
        480, 500, 540, 560, 600, 640, 700, 720, 800, 840,
        900, 960, 980, 1000, 1080, 1120, 1200, 1260, 1280, 1400,
        1440, 1600, 1800, 2000
    )


# ============================================================================
# 資料類別
# ============================================================================

@dataclass(frozen=True)
class UserCredential:
    """使用者憑證資料結構（不可變）。"""
    username: str
    password: str
    proxy: Optional[str] = None
    
    def __post_init__(self) -> None:
        """驗證資料完整性"""
        if not self.username or not self.password:
            raise ValueError("使用者名稱和密碼不能為空")


@dataclass(frozen=True)
class BetRule:
    """下注規則資料結構（不可變）。"""
    amount: float
    duration: int  # 分鐘
    min_seconds: float  # 最小間隔秒數
    max_seconds: float  # 最大間隔秒數
    
    def __post_init__(self) -> None:
        """驗證資料完整性"""
        if self.amount <= 0:
            raise ValueError(f"下注金額必須大於 0: {self.amount}")
        if self.duration <= 0:
            raise ValueError(f"持續時間必須大於 0: {self.duration}")
        if self.min_seconds <= 0:
            raise ValueError(f"最小間隔秒數必須大於 0: {self.min_seconds}")
        if self.max_seconds <= 0:
            raise ValueError(f"最大間隔秒數必須大於 0: {self.max_seconds}")
        if self.min_seconds > self.max_seconds:
            raise ValueError(f"最小間隔不能大於最大間隔: {self.min_seconds} > {self.max_seconds}")


@dataclass(frozen=True)
class ProxyInfo:
    """Proxy 資訊資料結構（不可變）。"""
    host: str
    port: int
    username: str
    password: str
    
    def __post_init__(self) -> None:
        """驗證資料完整性"""
        if not self.host:
            raise ValueError("Proxy 主機不能為空")
        if not (0 < self.port < 65536):
            raise ValueError(f"Proxy 埠號無效: {self.port}")
        if not self.username:
            raise ValueError("Proxy 使用者名稱不能為空")
    
    def to_url(self) -> str:
        """轉換為 Proxy URL 格式。
        
        Returns:
            格式化的 Proxy URL
        """
        # 使用字串拼接而非 f-string 在大量呼叫時更高效
        return f"http://{self.username}:{self.password}@{self.host}:{self.port}"
    
    def to_connection_string(self) -> str:
        """轉換為連接字串格式（快取結果）。
        
        Returns:
            格式化的連接字串 "host:port:username:password"
        """
        return f"{self.host}:{self.port}:{self.username}:{self.password}"
    
    def __str__(self) -> str:
        """字串表示（隱藏敏感資訊）"""
        return f"ProxyInfo({self.host}:{self.port}, user={self.username[:3]}***)"
    
    @staticmethod
    def from_connection_string(connection_string: str) -> 'ProxyInfo':
        """從連接字串建立 ProxyInfo 實例。
        
        Args:
            connection_string: 格式為 "host:port:username:password"
            
        Returns:
            ProxyInfo 實例
            
        Raises:
            ValueError: 格式不正確時
        """
        parts = connection_string.split(':')
        if len(parts) < 4:
            raise ValueError(f"Proxy 連接字串格式不正確: {connection_string}")
        
        return ProxyInfo(
            host=parts[0],
            port=int(parts[1]),
            username=parts[2],
            password=':'.join(parts[3:])  # 密碼可能包含冒號
        )


@dataclass
class BrowserContext:
    """瀏覽器上下文資訊。
    
    封裝瀏覽器實例及其相關資訊，提供便捷的存取介面。
    
    Attributes:
        driver: WebDriver 實例
        credential: 使用者憑證
        index: 瀏覽器索引（從 1 開始）
        proxy_port: Proxy 埠號（可選）
        created_at: 建立時間戳
    """
    driver: WebDriver
    credential: UserCredential
    index: int
    proxy_port: Optional[int] = None
    created_at: float = field(default_factory=time.time)
    
    @property
    def age_in_seconds(self) -> float:
        """取得瀏覽器實例的存活時間（秒）"""
        return time.time() - self.created_at


class OperationResult:
    """操作結果封裝。
    
    用於封裝操作的執行結果，包含成功狀態、資料、錯誤和訊息。
    
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
    """Proxy 伺服器錯誤"""
    pass


class ImageDetectionError(AutoSlotGameError):
    """圖片檢測錯誤"""
    pass


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
    """帶顏色的日誌格式化器。
    
    使用 ANSI 顏色碼為不同等級的日誌訊息添加顏色。
    """
    
    # ANSI 顏色碼
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
        """初始化顏色格式化器。
        
        Args:
            fmt: 日誌格式字串
            datefmt: 日期格式字串
        """
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
        """格式化日誌記錄。
        
        Args:
            record: 日誌記錄物件
            
        Returns:
            格式化後的日誌字串
        """
        formatter = self.formatters.get(record.levelno)
        if formatter:
            return formatter.format(record)
        return super().format(record)


class LoggerFactory:
    """Logger 工廠類別 - 使用單例模式優化效能"""
    
    _loggers: Dict[str, logging.Logger] = {}
    _lock = threading.RLock()  # 使用 RLock 避免死鎖
    _formatter: Optional[ColoredFormatter] = None  # 共用 formatter 實例
    
    @classmethod
    def get_logger(
        cls, 
        name: str = "AutoSlotGame",
        level: LogLevel = LogLevel.INFO
    ) -> logging.Logger:
        """取得或建立 logger 實例（執行緒安全）。
        
        Args:
            name: Logger 名稱
            level: 日誌等級
            
        Returns:
            配置完成的 Logger 物件
        """
        # 快速路徑：無鎖檢查（大多數情況下避免加鎖）
        if name in cls._loggers:
            return cls._loggers[name]
        
        with cls._lock:
            # 雙重檢查避免重複建立
            if name in cls._loggers:
                return cls._loggers[name]
            
            logger = logging.getLogger(name)
            logger.setLevel(level.value)
            logger.propagate = False
            
            # 避免重複添加 handler
            if not logger.handlers:
                # 共用 formatter 實例以節省記憶體
                if cls._formatter is None:
                    cls._formatter = ColoredFormatter()
                
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setLevel(level.value)
                console_handler.setFormatter(cls._formatter)
                logger.addHandler(console_handler)
            
            cls._loggers[name] = logger
            return logger


# ============================================================================
# 配置讀取器 (使用 Protocol 和依賴注入)
# ============================================================================

class ConfigReaderProtocol(Protocol):
    """配置讀取器協議"""
    
    def read_user_credentials(self, filename: str) -> List[UserCredential]:
        """讀取使用者憑證"""
        ...
    
    def read_bet_rules(self, filename: str) -> List[BetRule]:
        """讀取下注規則"""
        ...


class ConfigReader:
    """配置檔案讀取器。
    
    讀取並解析系統所需的各種配置檔案。
    採用上下文管理器和更好的錯誤處理。
    
    Attributes:
        lib_path: 配置檔案所在目錄路徑
        logger: 日誌記錄器
    """
    
    def __init__(
        self, 
        lib_path: Optional[Path] = None,
        logger: Optional[logging.Logger] = None
    ) -> None:
        """初始化配置讀取器。
        
        Args:
            lib_path: 配置檔案目錄路徑,預設為專案的 lib 目錄
            logger: 日誌記錄器
        """
        if lib_path is None:
            # 使用輔助函式取得專案根目錄
            lib_path = get_resource_path(Constants.DEFAULT_LIB_PATH)
        
        self.lib_path = Path(lib_path)
        self.logger = logger or LoggerFactory.get_logger()
        
        # 驗證目錄存在
        if not self.lib_path.exists():
            raise ConfigurationError(f"配置目錄不存在: {self.lib_path}")
    
    def _read_file_lines(self, filename: str, skip_header: bool = True) -> List[str]:
        """讀取檔案並返回有效行列表（優化版）。
        
        Args:
            filename: 檔案名稱
            skip_header: 是否跳過首行標題
            
        Returns:
            有效行列表（去除空行和註釋）
            
        Raises:
            ConfigurationError: 檔案讀取失敗
        """
        file_path = self.lib_path / filename
        
        if not file_path.exists():
            raise ConfigurationError(f"找不到配置檔案: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8', buffering=8192) as f:
                lines = f.readlines()
            
            # 跳過標題行
            start_index = 1 if skip_header and lines else 0
            
            # 使用列表推導式（更高效）
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
        
        檔案格式: 帳號,密碼,IP:port:user:password (首行為標題)
        第三欄為 proxy 資訊，格式為 host:port:username:password
        
        Args:
            filename: 檔案名稱
            
        Returns:
            使用者憑證列表
            
        Raises:
            ConfigurationError: 讀取或解析失敗
        """
        credentials = []
        lines = self._read_file_lines(filename, skip_header=True)
        
        for line_number, line in enumerate(lines, start=2):  # +2 因為跳過標題
            try:
                parts = [p.strip() for p in line.split(',')]
                
                if len(parts) < 2:
                    self.logger.warning(f"第 {line_number} 行格式不完整 已跳過 {line}")
                    continue
                
                username = parts[0]
                password = parts[1]
                # 第三欄是 proxy 資訊，格式為 host:port:username:password
                # 如果第三欄不存在或為空字串，則 proxy 為 None（不使用 proxy）
                proxy = parts[2] if len(parts) >= 3 and parts[2].strip() else None
                
                credentials.append(UserCredential(
                    username=username,
                    password=password,
                    proxy=proxy
                ))  
                
            except ValueError as e:
                self.logger.warning(f"第 {line_number} 行資料無效 {e}")
                continue
        
        return credentials
    
    def read_bet_rules(
        self, 
        filename: str = Constants.DEFAULT_RULES_FILE
    ) -> List[BetRule]:
        """讀取下注規則檔案。
        
        檔案格式: 金額:時間(分鐘):最小(秒數):最大(秒數) (首行為標題)
        
        Args:
            filename: 檔案名稱
            
        Returns:
            下注規則列表
            
        Raises:
            ConfigurationError: 讀取或解析失敗
        """
        rules = []
        lines = self._read_file_lines(filename, skip_header=True)
        
        for line_number, line in enumerate(lines, start=2):
            try:
                parts = line.split(':')
                
                if len(parts) < 4:
                    self.logger.warning(f"第 {line_number} 行格式不完整 已跳過 {line}")
                    continue
                
                amount = float(parts[0].strip())
                duration = int(parts[1].strip())
                min_seconds = float(parts[2].strip())
                max_seconds = float(parts[3].strip())
                
                rules.append(BetRule(
                    amount=amount, 
                    duration=duration,
                    min_seconds=min_seconds,
                    max_seconds=max_seconds
                ))
                
            except (ValueError, IndexError) as e:
                self.logger.warning(f"第 {line_number} 行無法解析 {e}")
                continue
        
        return rules


# ============================================================================
# Proxy 伺服器 (改進資源管理和執行緒安全)
# ============================================================================

class ProxyConnectionHandler:
    """Proxy 連接處理器"""
    
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
        """處理 HTTPS CONNECT 請求。
        
        Args:
            client_socket: 客戶端 socket
            request: 請求資料
        """
        upstream_socket = None
        try:
            # 建立到上游 proxy 的連接
            upstream_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            upstream_socket.settimeout(Constants.DEFAULT_TIMEOUT_SECONDS)
            upstream_socket.connect((self.upstream_proxy.host, self.upstream_proxy.port))
            
            # 構建帶認證的 CONNECT 請求
            auth_string = f"{self.upstream_proxy.username}:{self.upstream_proxy.password}"
            auth_b64 = base64.b64encode(auth_string.encode('utf-8')).decode('ascii')
            
            # 修改請求,添加認證頭
            request_lines = request.split(b'\r\n')
            auth_header = f"Proxy-Authorization: Basic {auth_b64}\r\n".encode('utf-8')
            
            # 重建請求
            new_request = request_lines[0] + b'\r\n' + auth_header
            for line in request_lines[1:]:
                new_request += line + b'\r\n'
            
            # 發送到上游 proxy
            upstream_socket.sendall(new_request)
            
            # 接收上游回應
            response = upstream_socket.recv(Constants.PROXY_BUFFER_SIZE)
            
            if b'200' in response:
                # 告訴客戶端連接成功
                client_socket.sendall(b'HTTP/1.1 200 Connection Established\r\n\r\n')
                
                # 雙向轉發數據
                self._forward_data(client_socket, upstream_socket)
            else:
                client_socket.sendall(b'HTTP/1.1 502 Bad Gateway\r\n\r\n')
                
        except socket.timeout:
            self.logger.warning("上游 Proxy 連接逾時")
            with suppress(Exception):
                client_socket.sendall(b'HTTP/1.1 504 Gateway Timeout\r\n\r\n')
        except Exception as e:
            self.logger.debug(f"CONNECT 請求處理失敗: {e}")
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
        """處理普通 HTTP 請求。
        
        Args:
            client_socket: 客戶端 socket
            request: 請求資料
        """
        upstream_socket = None
        try:
            # 添加認證頭
            auth_string = f"{self.upstream_proxy.username}:{self.upstream_proxy.password}"
            auth_b64 = base64.b64encode(auth_string.encode('utf-8')).decode('ascii')
            
            request_lines = request.split(b'\r\n')
            auth_header = f"Proxy-Authorization: Basic {auth_b64}\r\n".encode('utf-8')
            
            # 重建請求
            new_request = request_lines[0] + b'\r\n' + auth_header
            for line in request_lines[1:]:
                new_request += line + b'\r\n'
            
            # 連接上游 proxy
            upstream_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            upstream_socket.settimeout(Constants.DEFAULT_TIMEOUT_SECONDS)
            upstream_socket.connect((self.upstream_proxy.host, self.upstream_proxy.port))
            upstream_socket.sendall(new_request)
            
            # 接收並轉發回應
            while True:
                response = upstream_socket.recv(Constants.PROXY_BUFFER_SIZE)
                if not response:
                    break
                client_socket.sendall(response)
                
        except socket.timeout:
            self.logger.warning("上游 Proxy 回應逾時")
            with suppress(Exception):
                client_socket.sendall(b'HTTP/1.1 504 Gateway Timeout\r\n\r\n')
        except Exception as e:
            self.logger.debug(f"HTTP 請求處理失敗: {e}")
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
        """雙向轉發數據。
        
        Args:
            source: 來源 socket
            destination: 目標 socket
        """
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
    """
    簡易 HTTP Proxy 伺服器 (使用 Python 內建模組)
    將帶認證的遠端 proxy 轉換為本地無需認證的 proxy
    採用更好的資源管理和執行緒安全
    """
    
    def __init__(
        self, 
        local_port: int, 
        upstream_proxy: ProxyInfo,
        logger: Optional[logging.Logger] = None
    ):
        """
        Args:
            local_port: 本地監聽埠號
            upstream_proxy: 上游 proxy 資訊
            logger: 日誌記錄器
        """
        self.local_port = local_port
        self.upstream_proxy = upstream_proxy
        self.logger = logger or LoggerFactory.get_logger()
        self.running = False
        self.server_socket: Optional[socket.socket] = None
        self.handler = ProxyConnectionHandler(upstream_proxy, self.logger)
    
    def handle_client(self, client_socket: socket.socket) -> None:
        """處理客戶端連接。
        
        Args:
            client_socket: 客戶端 socket
        """
        try:
            # 設定逾時
            client_socket.settimeout(Constants.DEFAULT_TIMEOUT_SECONDS)
            
            # 接收客戶端請求
            request = client_socket.recv(Constants.PROXY_BUFFER_SIZE)
            if not request:
                return
            
            # 解析請求類型
            first_line = request.split(b'\r\n')[0].decode('utf-8', errors='ignore')
            
            if first_line.startswith('CONNECT'):
                # HTTPS 請求
                self.handler.handle_connect_request(client_socket, request)
            else:
                # HTTP 請求
                self.handler.handle_http_request(client_socket, request)
                
        except socket.timeout:
            self.logger.debug("客戶端連接逾時")
        except Exception as e:
            self.logger.debug(f"處理客戶端連接時發生錯誤: {e}")
        finally:
            with suppress(Exception):
                client_socket.close()
    
    def start(self) -> None:
        """啟動 proxy 伺服器。
        
        Raises:
            ProxyServerError: 伺服器啟動失敗
        """
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
                    
                    # 在新執行緒中處理客戶端
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
                        self.logger.error(f"接受連接時發生錯誤 {e}")
                    
        except Exception as e:
            raise ProxyServerError(f"Proxy 伺服器啟動失敗: {e}") from e
        finally:
            self.stop()
    
    def stop(self) -> None:
        """停止 proxy 伺服器"""
        self.running = False
        if self.server_socket:
            with suppress(Exception):
                self.server_socket.close()
            self.server_socket = None


class LocalProxyServerManager:
    """本機 Proxy 中繼伺服器管理器。
    
    為每個瀏覽器建立獨立的本機 Proxy 埠,將請求轉發到上游 Proxy。
    採用執行緒安全和更好的資源管理。
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """初始化管理器"""
        self.logger = logger or LoggerFactory.get_logger()
        self._proxy_servers: Dict[int, SimpleProxyServer] = {}
        self._proxy_threads: Dict[int, threading.Thread] = {}
        self._next_port: int = Constants.DEFAULT_PROXY_START_PORT
        self._lock = threading.Lock()
    
    def start_proxy_server(
        self, 
        upstream_proxy: ProxyInfo
    ) -> Optional[int]:
        """啟動本機 Proxy 中繼伺服器。
        
        Args:
            upstream_proxy: 上游 Proxy 資訊
            
        Returns:
            本機埠號,失敗返回 None
        """
        with self._lock:
            local_port = self._next_port
            self._next_port += 1
        
        try:
            # 建立 proxy 伺服器實例
            server = SimpleProxyServer(local_port, upstream_proxy, self.logger)
            
            # 在新執行緒中啟動伺服器
            def run_server():
                try:
                    server.start()
                except Exception as e:
                    self.logger.error(f"Proxy 伺服器執行失敗 埠 {local_port} {e}")
            
            server_thread = threading.Thread(target=run_server, daemon=True)
            server_thread.start()
            
            # 儲存實例和執行緒參考
            with self._lock:
                self._proxy_servers[local_port] = server
                self._proxy_threads[local_port] = server_thread
            
            # 等待伺服器啟動
            time.sleep(Constants.PROXY_SERVER_START_WAIT)
            
            self.logger.info(f"✓ Proxy 中繼已啟動 (埠: {local_port})")
            return local_port
            
        except Exception as e:
            self.logger.error(f"啟動本機 Proxy 伺服器失敗 {e}")
            return None
    
    def stop_proxy_server(self, local_port: int) -> None:
        """停止指定的 proxy 伺服器（優化版）。
        
        Args:
            local_port: 本機埠號
        """
        server = None
        
        # 原子性取出 server
        with self._lock:
            server = self._proxy_servers.pop(local_port, None)
            self._proxy_threads.pop(local_port, None)
        
        # 在鎖外執行耗時操作
        if server:
            try:
                server.stop()
            except Exception as e:
                self.logger.debug(f"停止 Proxy 伺服器時發生錯誤 ({local_port}): {e}")
    
    def stop_all_servers(self) -> None:
        """停止所有 proxy 伺服器（優化版）"""
        # 一次性取出所有埠號
        with self._lock:
            ports = list(self._proxy_servers.keys())
        
        # 並行停止所有伺服器（提升效率）
        if ports:
            with ThreadPoolExecutor(max_workers=min(len(ports), Constants.MAX_THREAD_WORKERS)) as executor:
                executor.map(self.stop_proxy_server, ports)
    
    def __enter__(self):
        """上下文管理器進入"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出,自動清理資源"""
        self.stop_all_servers()
        return False


# ============================================================================
# 瀏覽器管理器 (改進錯誤處理和資源管理)
# ============================================================================

class BrowserManager:
    """瀏覽器管理器。
    
    提供 WebDriver 建立和配置功能,支援自動和手動驅動程式管理。
    採用更好的錯誤處理和資源清理。
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """初始化瀏覽器管理器"""
        self.logger = logger or LoggerFactory.get_logger()
    
    @staticmethod
    def create_chrome_options(local_proxy_port: Optional[int] = None) -> Options:
        """建立 Chrome 瀏覽器選項。
        
        Args:
            local_proxy_port: 本機 proxy 中繼埠號（可選）
            
        Returns:
            Options: 配置好的 Chrome 選項
        """
        logger = LoggerFactory.get_logger()
        chrome_options = Options()
        
        # 本機 Proxy 設定
        if local_proxy_port:
            proxy_address = f"http://{Constants.PROXY_SERVER_BIND_HOST}:{local_proxy_port}"
            chrome_options.add_argument(f"--proxy-server={proxy_address}")
        
        # 基本設定
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        
        # 視窗大小設定（固定 1280x720）
        chrome_options.add_argument(f"--window-size={Constants.DEFAULT_WINDOW_WIDTH},{Constants.DEFAULT_WINDOW_HEIGHT}")
        
        # 背景執行優化設定
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_argument("--disable-background-timer-throttling")
        # 移除: --disable-ipc-flooding-protection (可能導致通訊過載)
        
        # 網路效能優化設定
        # 移除: --dns-prefetch-disable (會降低 DNS 解析速度)
        # 移除: --disable-background-networking (會影響連線池管理)
        # 移除: --disable-features=NetworkTimeServiceQuerying (影響時間同步)
        
        # 啟用網路加速功能
        chrome_options.add_argument("--enable-features=NetworkService,NetworkServiceInProcess")
        chrome_options.add_argument("--enable-quic")  # 啟用 QUIC 協定加速
        chrome_options.add_argument("--enable-tcp-fast-open")  # TCP 快速開啟
        
        # 其他優化設定
        chrome_options.add_argument("--disable-sync")
        chrome_options.add_argument("--metrics-recording-only")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--disable-extensions")
        
        # 記憶體與渲染優化
        chrome_options.add_argument("--disk-cache-size=209715200")  # 200MB 磁碟快取
        chrome_options.add_argument("--media-cache-size=209715200")  # 200MB 媒體快取
        
        # 移除自動化痕跡
        chrome_options.add_experimental_option(
            "excludeSwitches", 
            ["enable-automation", "enable-logging"]
        )
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 偏好設定
        chrome_options.add_experimental_option("prefs", {
            # 完全停用密碼管理功能
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.password_manager_leak_detection": False,
            "password_manager_enabled": False,
            # 停用自動填入
            "autofill.profile_enabled": False,
            "autofill.credit_card_enabled": False,
            # 停用通知和彈窗
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_settings.popups": 0,
            # 靜音設定（2 = 靜音，1 = 允許聲音）
            "profile.content_settings.exceptions.sound": {
                "*": {
                    "setting": 2
                }
            }
        })
        
        return chrome_options
    
    def create_webdriver(
        self, 
        local_proxy_port: Optional[int] = None
    ) -> WebDriver:
        """建立 WebDriver 實例（優化版）。
        
        優先使用專案內的驅動程式檔案，
        若失敗則嘗試使用 WebDriver Manager 自動管理作為備援。
        
        Args:
            local_proxy_port: 本機 proxy 中繼埠號（可選）
            
        Returns:
            WebDriver: WebDriver 實例
            
        Raises:
            BrowserCreationError: 當所有方法都失敗時
        """
        chrome_options = self.create_chrome_options(local_proxy_port)
        driver = None
        errors = []
        
        # 方法 1: 優先使用專案內的驅動程式檔案
        try:
            driver = self._create_webdriver_with_local_driver(chrome_options)
            
        except FileNotFoundError as e:
            errors.append(f"本機驅動程式: {e}")
            self.logger.warning(f"本機驅動程式不存在，嘗試使用 WebDriver Manager")
            
            # 方法 2: 使用 WebDriver Manager 自動管理
            try:
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
                
            except Exception as e2:
                errors.append(f"WebDriver Manager: {e2}")
                self.logger.error(f"WebDriver Manager 也失敗: {e2}")
        
        except Exception as e:
            errors.append(f"本機驅動程式: {e}")
            self.logger.warning(f"本機驅動程式失敗，嘗試備援方案: {e}")
        
        if driver is None:
            error_message = "無法建立瀏覽器實例。\n" + "\n".join(f"- {error}" for error in errors)
            raise BrowserCreationError(error_message)
        
        # 配置超時和優化
        self._configure_webdriver(driver)
        return driver
    
    def _configure_webdriver(self, driver: WebDriver) -> None:
        """配置 WebDriver 超時和優化設定。
        
        Args:
            driver: WebDriver 實例
        """
        # 設定超時
        with suppress(Exception):
            driver.set_page_load_timeout(Constants.DEFAULT_PAGE_LOAD_TIMEOUT)
            driver.set_script_timeout(Constants.DEFAULT_SCRIPT_TIMEOUT)
            driver.implicitly_wait(Constants.DEFAULT_IMPLICIT_WAIT)
        
        # 視窗大小設定（確保為 1280x720）
        with suppress(Exception):
            driver.set_window_size(Constants.DEFAULT_WINDOW_WIDTH, Constants.DEFAULT_WINDOW_HEIGHT)
        
        # 網路優化
        with suppress(Exception):
            driver.execute_cdp_cmd("Network.enable", {})
            driver.execute_cdp_cmd("Network.emulateNetworkConditions", {
                "offline": False,
                "downloadThroughput": -1,
                "uploadThroughput": -1,
                "latency": 0
            })
    
    def _create_webdriver_with_local_driver(self, chrome_options: Options) -> WebDriver:
        """使用專案內的驅動程式檔案建立 WebDriver。
        
        根據作業系統自動選擇正確的驅動程式檔案。
        
        Args:
            chrome_options: Chrome 選項
            
        Returns:
            WebDriver: WebDriver 實例
            
        Raises:
            FileNotFoundError: 驅動程式不存在
            BrowserCreationError: 無法啟動驅動程式
        """
        # 使用輔助函式取得專案根目錄
        project_root = get_resource_path()
        
        # 根據作業系統選擇驅動程式
        system = platform.system().lower()
        driver_filename = "chromedriver.exe" if system == "windows" else "chromedriver"
        
        driver_path = project_root / driver_filename
        
        if not driver_path.exists():
            raise FileNotFoundError(
                f"找不到驅動程式檔案\n"
                f"請確保 {driver_filename} 存在於專案根目錄"
            )
        
        # 確保驅動程式有執行權限 (Unix-like 系統)
        if system in ["darwin", "linux"]:
            import os
            with suppress(Exception):
                os.chmod(driver_path, 0o755)
        
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
        """建立瀏覽器上下文管理器。
        
        Args:
            credential: 使用者憑證
            index: 瀏覽器索引
            proxy_port: Proxy 埠號
            
        Yields:
            BrowserContext: 瀏覽器上下文
            
        Raises:
            BrowserCreationError: 建立失敗
        """
        driver = None
        size_locker = None
        try:
            driver = self.create_webdriver(local_proxy_port=proxy_port)
            
            # 立即啟動視窗大小鎖定器
            size_locker = WindowSizeLocker(
                driver, 
                Constants.DEFAULT_WINDOW_WIDTH, 
                Constants.DEFAULT_WINDOW_HEIGHT
            )
            size_locker.start()
            
            context = BrowserContext(
                driver=driver,
                credential=credential,
                index=index,
                proxy_port=proxy_port
            )
            # 將 size_locker 附加到 context，供後續使用
            context.size_locker = size_locker
            
            yield context
        finally:
            # 先停止視窗監控
            if size_locker:
                with suppress(Exception):
                    size_locker.stop()
            # 再關閉瀏覽器
            if driver:
                with suppress(Exception):
                    driver.quit()
                self.logger.debug(f"瀏覽器 #{index} 已關閉")


# ============================================================================
# 同步瀏覽器操作器 (改進執行緒池和錯誤處理)
# ============================================================================

class SyncBrowserOperator:
    """同步瀏覽器操作器。
    
    對多個瀏覽器實例同步執行相同的操作。
    使用執行緒池提升效能和資源管理。
    """
    
    def __init__(
        self,
        max_workers: Optional[int] = None,
        logger: Optional[logging.Logger] = None
    ):
        """初始化操作器。
        
        Args:
            max_workers: 最大工作執行緒數
            logger: 日誌記錄器
        """
        self.max_workers = max_workers or Constants.MAX_THREAD_WORKERS
        self.logger = logger or LoggerFactory.get_logger()
        self.last_canvas_rect: Optional[Dict[str, float]] = None  # Canvas 區域資訊
    
    def execute_sync(
        self,
        browser_contexts: List[BrowserContext],
        operation_func: Callable[[BrowserContext, int, int], Any],
        operation_name: str,
        timeout: Optional[float] = None
    ) -> List[OperationResult]:
        """同步執行操作到所有瀏覽器（優化版）。
        
        Args:
            browser_contexts: 瀏覽器上下文列表
            operation_func: 操作函式,接受參數 (context, index, total)
            operation_name: 操作名稱(用於日誌)
            timeout: 超時時間（秒）
            
        Returns:
            所有操作的結果列表
        """
        total = len(browser_contexts)
        results: List[OperationResult] = [OperationResult(False)] * total
        
        def execute_operation(index: int, context: BrowserContext) -> Tuple[int, OperationResult]:
            """在執行緒中執行操作"""
            try:
                result_data = operation_func(context, index + 1, total)
                return index, OperationResult(
                    success=True,
                    data=result_data,
                    message=f"{operation_name} 成功"
                )
            except Exception as e:
                self.logger.error(f"瀏覽器 {index+1}/{total} {operation_name} 失敗: {e}")
                return index, OperationResult(
                    success=False,
                    error=e,
                    message=str(e)
                )
        
        # 使用執行緒池執行
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任務
            futures = [
                executor.submit(execute_operation, i, context)
                for i, context in enumerate(browser_contexts)
            ]
            
            # 收集結果
            try:
                for future in as_completed(futures, timeout=timeout):
                    index, result = future.result()
                    results[index] = result
            except TimeoutError:
                self.logger.error(f"{operation_name} 執行超時")
        
        success_count = sum(1 for r in results if r.success)
        if success_count < total:
            self.logger.warning(f"⚠ 部分操作未成功: {success_count}/{total}")
        
        return results
    
    def navigate_all(
        self,
        browser_contexts: List[BrowserContext],
        url: str,
        timeout: Optional[float] = None
    ) -> List[OperationResult]:
        """同步導航所有瀏覽器到指定 URL。
        
        Args:
            browser_contexts: 瀏覽器上下文列表
            url: 目標 URL
            timeout: 超時時間
            
        Returns:
            操作結果列表
        """
        def navigate_operation(context: BrowserContext, index: int, total: int) -> str:
            context.driver.get(url)
            return context.driver.current_url
        
        return self.execute_sync(
            browser_contexts,
            navigate_operation,
            f"導航到 {url}",
            timeout=timeout
        )
    
    def navigate_to_login_page(
        self,
        browser_contexts: List[BrowserContext],
        timeout: Optional[float] = None
    ) -> List[OperationResult]:
        """同步導航所有瀏覽器到登入頁面。
        
        Args:
            browser_contexts: 瀏覽器上下文列表
            timeout: 超時時間
            
        Returns:
            操作結果列表
        """
        return self.navigate_all(browser_contexts, Constants.LOGIN_PAGE, timeout)
    
    def perform_login_all(
        self,
        browser_contexts: List[BrowserContext],
        timeout: Optional[float] = None
    ) -> List[OperationResult]:
        """同步執行所有瀏覽器的登入操作。
        
        Args:
            browser_contexts: 瀏覽器上下文列表
            timeout: 超時時間
            
        Returns:
            操作結果列表
        """
        def login_operation(context: BrowserContext, index: int, total: int) -> bool:
            driver = context.driver
            credential = context.credential
            
            # 輸入帳號
            username_input = driver.find_element(By.XPATH, Constants.USERNAME_INPUT)
            username_input.clear()
            username_input.send_keys(credential.username)
            
            # 輸入密碼
            password_input = driver.find_element(By.XPATH, Constants.PASSWORD_INPUT)
            password_input.clear()
            password_input.send_keys(credential.password)
            
            # 點擊登入按鈕
            login_button = driver.find_element(By.XPATH, Constants.LOGIN_BUTTON)
            login_button.click()
            
            time.sleep(Constants.LOGIN_WAIT_TIME)  # 等待登入完成
            return True
        
        return self.execute_sync(
            browser_contexts,
            login_operation,
            "登入操作",
            timeout=timeout
        )
    
    def remove_popup_all(
        self,
        browser_contexts: List[BrowserContext],
        timeout: Optional[float] = None
    ) -> List[OperationResult]:
        """同步移除所有瀏覽器的維護公告彈窗。
        
        Args:
            browser_contexts: 瀏覽器上下文列表
            timeout: 超時時間
            
        Returns:
            操作結果列表
        """
        def remove_popup_operation(context: BrowserContext, index: int, total: int) -> bool:
            BrowserHelper.remove_maintenance_popup(context.driver)
            return True
        
        return self.execute_sync(
            browser_contexts,
            remove_popup_operation,
            "移除維護公告彈窗",
            timeout=timeout
        )
    
    def navigate_to_game_category(
        self,
        browser_contexts: List[BrowserContext],
        timeout: Optional[float] = None
    ) -> List[OperationResult]:
        """同步導航所有瀏覽器到遊戲分類頁面。
        
        Args:
            browser_contexts: 瀏覽器上下文列表
            timeout: 超時時間
            
        Returns:
            操作結果列表
        """
        return self.navigate_all(browser_contexts, Constants.GAME_CATEGORY_URL, timeout)
    
    def click_game_provider_all(
        self,
        browser_contexts: List[BrowserContext],
        timeout: Optional[float] = None
    ) -> List[OperationResult]:
        """同步點擊所有瀏覽器的遊戲供應商按鈕。
        
        Args:
            browser_contexts: 瀏覽器上下文列表
            timeout: 超時時間
            
        Returns:
            操作結果列表
        """
        def click_provider_operation(context: BrowserContext, index: int, total: int) -> bool:
            driver = context.driver
            wait = WebDriverWait(driver, 15)
            provider_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, Constants.GAME_PROVIDER_BUTTON))
            )
            provider_button.click()
            return True
        
        return self.execute_sync(
            browser_contexts,
            click_provider_operation,
            "點擊遊戲供應商",
            timeout=timeout
        )
    
    def switch_to_new_tab_all(
        self,
        browser_contexts: List[BrowserContext],
        timeout: Optional[float] = None
    ) -> List[OperationResult]:
        """同步切換所有瀏覽器到新分頁。
        
        Args:
            browser_contexts: 瀏覽器上下文列表
            timeout: 超時時間
            
        Returns:
            操作結果列表
        """
        def switch_tab_operation(context: BrowserContext, index: int, total: int) -> bool:
            driver = context.driver
            driver.switch_to.window(driver.window_handles[-1])
            return True
        
        return self.execute_sync(
            browser_contexts,
            switch_tab_operation,
            "切換到新分頁",
            timeout=timeout
        )
    
    def click_start_game_all(
        self,
        browser_contexts: List[BrowserContext],
        timeout: Optional[float] = None
    ) -> List[OperationResult]:
        """同步點擊所有瀏覽器的開始遊戲按鈕。
        
        使用 JavaScript 點擊以處理隱藏元素。
        
        Args:
            browser_contexts: 瀏覽器上下文列表
            timeout: 超時時間
            
        Returns:
            操作結果列表
        """
        def click_start_operation(context: BrowserContext, index: int, total: int) -> bool:
            driver = context.driver
            wait = WebDriverWait(driver, 15)
            
            try:
                # 等待元素存在
                start_button = wait.until(
                    EC.presence_of_element_located((By.XPATH, Constants.START_GAME_BUTTON))
                )
                # 使用 JavaScript 點擊隱藏元素
                driver.execute_script("arguments[0].click();", start_button)
                return True
            except Exception as e:
                self.logger.error(f"找不到開始遊戲按鈕: {e}")
                return False
        
        return self.execute_sync(
            browser_contexts,
            click_start_operation,
            "點擊開始遊戲",
            timeout=timeout
        )
    
    def press_space_all(
        self,
        browser_contexts: List[BrowserContext],
        timeout: Optional[float] = None
    ) -> List[OperationResult]:
        """同步在所有瀏覽器中按下空白鍵。
        
        Args:
            browser_contexts: 瀏覽器上下文列表
            timeout: 超時時間
            
        Returns:
            操作結果列表
        """
        def press_space_operation(context: BrowserContext, index: int, total: int) -> bool:
            BrowserHelper.execute_cdp_space_key(context.driver)
            return True
        
        return self.execute_sync(
            browser_contexts,
            press_space_operation,
            "按下空白鍵",
            timeout=timeout
        )
    
    def buy_free_game_single(
        self,
        context: BrowserContext,
        canvas_rect: Dict[str, float]
    ) -> bool:
        """在單個瀏覽器中購買免費遊戲。
        
        Args:
            context: 瀏覽器上下文
            canvas_rect: Canvas 區域資訊 {"x", "y", "w", "h"}
            
        Returns:
            是否成功
        """
        try:
            username = context.credential.username
            driver = context.driver
            
            # === 第一次點擊（免費遊戲區域） ===
            freegame_x, freegame_y = BrowserHelper.calculate_click_position(
                canvas_rect,
                Constants.BUY_FREE_GAME_BUTTON_X_RATIO,
                Constants.BUY_FREE_GAME_BUTTON_Y_RATIO
            )
            
            self.logger.info(f"[{username}] 點擊免費遊戲區域 ({freegame_x:.1f}, {freegame_y:.1f})...")
            BrowserHelper.execute_cdp_click(driver, freegame_x, freegame_y)
            time.sleep(Constants.FREE_GAME_CLICK_WAIT)
            
            # === 第二次點擊（確認按鈕） ===
            confirm_x, confirm_y = BrowserHelper.calculate_click_position(
                canvas_rect,
                Constants.BUY_FREE_GAME_CONFIRM_X_RATIO,
                Constants.BUY_FREE_GAME_CONFIRM_Y_RATIO
            )
            
            self.logger.info(f"[{username}] 點擊確認按鈕 ({confirm_x:.1f}, {confirm_y:.1f})...")
            BrowserHelper.execute_cdp_click(driver, confirm_x, confirm_y)
            
            # === 購買完成後等待並自動按空白鍵 ===
            self.logger.info(f"[{username}] 購買完成，等待 {Constants.BUY_FREE_GAME_WAIT_SECONDS} 秒後開始遊戲...")
            time.sleep(Constants.BUY_FREE_GAME_WAIT_SECONDS)
            
            self.logger.info(f"[{username}] 按下空白鍵開始遊戲...")
            BrowserHelper.execute_cdp_space_key(driver)
            
            self.logger.info(f"[{username}] 免費遊戲購買流程完成！")
            return True
            
        except Exception as e:
            self.logger.error(f"[{username}] 購買免費遊戲失敗：{e}")
            return False
    
    def buy_free_game_all(
        self,
        browser_contexts: List[BrowserContext],
        canvas_rect: Dict[str, float],
        timeout: Optional[float] = None
    ) -> List[OperationResult]:
        """同步在所有瀏覽器中購買免費遊戲。
        
        Args:
            browser_contexts: 瀏覽器上下文列表
            canvas_rect: Canvas 區域資訊
            timeout: 超時時間
            
        Returns:
            操作結果列表
        """
        def buy_operation(context: BrowserContext, index: int, total: int) -> bool:
            """購買免費遊戲操作"""
            username = context.credential.username
            driver = context.driver
            
            try:
                # === 第一次點擊（免費遊戲區域） ===
                freegame_x, freegame_y = BrowserHelper.calculate_click_position(
                    canvas_rect,
                    Constants.BUY_FREE_GAME_BUTTON_X_RATIO,
                    Constants.BUY_FREE_GAME_BUTTON_Y_RATIO
                )
                
                BrowserHelper.execute_cdp_click(driver, freegame_x, freegame_y)
                time.sleep(Constants.FREE_GAME_CLICK_WAIT)
                
                # === 第二次點擊（確認按鈕） ===
                confirm_x, confirm_y = BrowserHelper.calculate_click_position(
                    canvas_rect,
                    Constants.BUY_FREE_GAME_CONFIRM_X_RATIO,
                    Constants.BUY_FREE_GAME_CONFIRM_Y_RATIO
                )
                
                BrowserHelper.execute_cdp_click(driver, confirm_x, confirm_y)
                
                # === 購買完成後等待並自動按空白鍵 ===
                time.sleep(Constants.BUY_FREE_GAME_WAIT_SECONDS)
                BrowserHelper.execute_cdp_space_key(driver)
                
                return True
                
            except Exception as e:
                self.logger.error(f"[{username}] 購買失敗: {e}")
                return False
        
        return self.execute_sync(
            browser_contexts,
            buy_operation,
            "購買免費遊戲",
            timeout
        )
    
    def resize_and_arrange_all(
        self,
        browser_contexts: List[BrowserContext],
        width: int = Constants.DEFAULT_WINDOW_WIDTH,
        height: int = Constants.DEFAULT_WINDOW_HEIGHT,
        columns: int = Constants.DEFAULT_WINDOW_COLUMNS,
        timeout: Optional[float] = None
    ) -> List[OperationResult]:
        """調整所有瀏覽器視窗大小（預設 1280x720）。
        
        Args:
            browser_contexts: 瀏覽器上下文列表
            width: 視窗寬度（預設 1280）
            height: 視窗高度（預設 720）
            columns: 已棄用，保留參數以維持相容性
            timeout: 超時時間
            
        Returns:
            操作結果列表
        """
        def resize_operation(context: BrowserContext, index: int, total: int) -> bool:
            # 只調整視窗大小，不再排列位置
            context.driver.set_window_size(width, height)
            
            # 啟動視窗大小鎖定器
            if not hasattr(context, 'size_locker'):
                context.size_locker = WindowSizeLocker(context.driver, width, height)
                context.size_locker.start()
            
            return True
        
        return self.execute_sync(
            browser_contexts,
            resize_operation,
            f"調整視窗大小為 {width}x{height}",
            timeout=timeout
        )
    
    def close_all(
        self,
        browser_contexts: List[BrowserContext],
        timeout: Optional[float] = None
    ) -> List[OperationResult]:
        """同步關閉所有瀏覽器。
        
        Args:
            browser_contexts: 瀏覽器上下文列表
            timeout: 超時時間
            
        Returns:
            操作結果列表
        """
        def close_operation(context: BrowserContext, index: int, total: int) -> bool:
            context.driver.quit()
            return True
        
        return self.execute_sync(
            browser_contexts,
            close_operation,
            "關閉瀏覽器",
            timeout=timeout
        )
    
    def adjust_betsize_all(
        self,
        browser_contexts: List[BrowserContext],
        target_amount: float,
        timeout: Optional[float] = None
    ) -> List[OperationResult]:
        """同步調整所有瀏覽器的下注金額。
        
        Args:
            browser_contexts: 瀏覽器上下文列表
            target_amount: 目標金額
            timeout: 超時時間
            
        Returns:
            操作結果列表
        """
        def adjust_operation(context: BrowserContext, index: int, total: int) -> bool:
            return self.adjust_betsize(context.driver, target_amount)
        
        return self.execute_sync(
            browser_contexts,
            adjust_operation,
            f"調整下注金額到 {target_amount}",
            timeout=timeout
        )
    
    def get_current_betsize(self, driver: WebDriver, retry_count: int = None) -> Optional[float]:
        """取得當前下注金額（優化版）。
        
        Args:
            driver: WebDriver 實例
            retry_count: 重試次數（預設使用常數）
            
        Returns:
            Optional[float]: 當前金額，失敗返回None
        """
        if retry_count is None:
            retry_count = Constants.BETSIZE_READ_MAX_RETRIES
        
        for attempt in range(retry_count):
            try:
                if attempt > 0:
                    time.sleep(Constants.BETSIZE_READ_RETRY_WAIT)  # 等待畫面穩定
                
                # 截取整個瀏覽器截圖
                screenshot = driver.get_screenshot_as_png()
                screenshot_np = np.array(Image.open(io.BytesIO(screenshot)))
                screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)
                
                # 與資料夾中的圖片進行比對
                matched_amount, confidence = self._compare_betsize_images(screenshot_gray)
                
                if matched_amount:
                    try:
                        amount_value = float(matched_amount)
                        # 使用 Constants.GAME_BETSIZE 進行驗證
                        if amount_value in Constants.GAME_BETSIZE:
                            self.logger.info(f"✓ 目前金額: {amount_value}")
                            return amount_value
                    except ValueError:
                        pass
                
            except Exception as e:
                self.logger.error(f"查詢下注金額時發生錯誤: {e}")
        
        return None
    
    def _compare_betsize_images(self, screenshot_gray: np.ndarray) -> Tuple[Optional[str], float]:
        """使用 bet_size 資料夾中的圖片比對（優化版）。
        
        Args:
            screenshot_gray: 截圖（灰階）
            
        Returns:
            Tuple[Optional[str], float]: (匹配的金額, 信心度)
        """
        try:
            # 使用輔助函式取得專案根目錄
            bet_size_dir = get_resource_path("img") / "bet_size"
            
            if not bet_size_dir.exists():
                self.logger.warning(f"bet_size 資料夾不存在: {bet_size_dir}")
                try:
                    bet_size_dir.mkdir(parents=True, exist_ok=True)
                    self.logger.info(f"已建立 bet_size 資料夾: {bet_size_dir}")
                except Exception as e:
                    self.logger.error(f"無法建立 bet_size 資料夾: {e}")
                    return None, 0.0
            
            # 取得所有 png 圖片
            image_files = sorted(bet_size_dir.glob("*.png"))
            if not image_files:
                self.logger.warning("bet_size 資料夾中沒有圖片")
                return None, 0.0
            
            # 儲存所有匹配結果
            match_results = []
            
            for image_file in image_files:
                # 讀取模板圖片（使用支援 Unicode 路徑的函式）
                template = cv2_imread_unicode(image_file, cv2.IMREAD_GRAYSCALE)
                if template is None:
                    continue
                
                # 檢查尺寸
                if (screenshot_gray.shape[0] < template.shape[0] or 
                    screenshot_gray.shape[1] < template.shape[1]):
                    continue
                
                # 執行模板匹配
                result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, _ = cv2.minMaxLoc(result)
                
                match_results.append((image_file.stem, max_val))
            
            if not match_results:
                return None, 0.0
            
            # 按信心度排序
            match_results.sort(key=lambda x: x[1], reverse=True)
            best_match_amount, best_match_score = match_results[0]
            
            # 使用常數定義的閾值
            if best_match_score >= Constants.BETSIZE_MATCH_THRESHOLD:
                return best_match_amount, best_match_score
            else:
                return None, best_match_score
                
        except Exception as e:
            self.logger.error(f"比對圖片時發生錯誤: {e}")
            return None, 0.0
    
    def _click_betsize_button(self, driver: WebDriver, x_ratio: float, y_ratio: float) -> None:
        """點擊下注金額調整按鈕（使用 Canvas 座標比例）。
        
        Args:
            driver: WebDriver 實例
            x_ratio: X 座標比例（相對於 Canvas）
            y_ratio: Y 座標比例（相對於 Canvas）
        """
        # 取得 Canvas 區域
        try:
            rect = driver.execute_script(f"""
                const canvas = document.getElementById('{Constants.GAME_CANVAS}');
                if (!canvas) {{
                    return {{error: 'Canvas not found'}};
                }}
                const r = canvas.getBoundingClientRect();
                return {{x: r.left, y: r.top, w: r.width, h: r.height}};
            """)
            
            if 'error' in rect:
                self.logger.error(f"找不到 Canvas 元素 (ID: {Constants.GAME_CANVAS})")
                return
            
            # 直接計算實際點擊座標（避免重複計算）
            actual_x = rect["x"] + rect["w"] * x_ratio
            actual_y = rect["y"] + rect["h"] * y_ratio
            
            # 除錯資訊
            self.logger.debug(f"Canvas rect: {rect}, 點擊座標: ({actual_x}, {actual_y}), 比例: ({x_ratio}, {y_ratio})")
            
            # 執行點擊
            BrowserHelper.execute_cdp_click(driver, actual_x, actual_y)
        except Exception as e:
            self.logger.error(f"點擊 BETSIZE 按鈕失敗: {e}")
    
    def adjust_betsize(self, driver: WebDriver, target_amount: float, max_attempts: int = None) -> bool:
        """調整下注金額到目標值（優化版）。
        
        Args:
            driver: WebDriver 實例
            target_amount: 目標金額
            max_attempts: 最大嘗試次數（預設使用常數）
            
        Returns:
            bool: 調整成功返回True
        """
        if max_attempts is None:
            max_attempts = Constants.BETSIZE_ADJUST_MAX_ATTEMPTS
        
        try:
            # 檢查目標金額
            if target_amount not in Constants.GAME_BETSIZE:
                self.logger.error(f"目標金額 {target_amount} 不在可用金額列表中")
                return False
            
            # 取得當前金額
            current_amount = self.get_current_betsize(driver)
            if current_amount is None:
                self.logger.error("✗ 無法識別目前金額")
                return False
            
            # 檢查是否已是目標金額
            if current_amount == target_amount:
                self.logger.info("✓ 金額已符合目標")
                return True
            
            # 計算需要調整的次數和方向
            current_index = Constants.GAME_BETSIZE_TUPLE.index(current_amount)
            target_index = Constants.GAME_BETSIZE_TUPLE.index(target_amount)
            diff = target_index - current_index
            
            # 設定點擊座標比例（基於 Canvas）
            if diff > 0:
                # 增加金額
                click_x_ratio = Constants.BETSIZE_INCREASE_BUTTON_X_RATIO
                click_y_ratio = Constants.BETSIZE_INCREASE_BUTTON_Y_RATIO
                estimated_steps = diff
            else:
                # 減少金額
                click_x_ratio = Constants.BETSIZE_DECREASE_BUTTON_X_RATIO
                click_y_ratio = Constants.BETSIZE_DECREASE_BUTTON_Y_RATIO
                estimated_steps = abs(diff)
            
            # 開始調整
            for i in range(estimated_steps):
                self._click_betsize_button(driver, click_x_ratio, click_y_ratio)
                time.sleep(Constants.BETSIZE_ADJUST_STEP_WAIT)
            
            time.sleep(Constants.BETSIZE_ADJUST_VERIFY_WAIT)
            
            # 驗證並微調
            for attempt in range(max_attempts):
                current_amount = self.get_current_betsize(driver)
                
                if current_amount is None:
                    time.sleep(Constants.BETSIZE_ADJUST_RETRY_WAIT)
                    continue
                
                if current_amount == target_amount:
                    self.logger.info(f"✓ 金額調整完成: {current_amount}")
                    return True
                
                # 根據當前金額決定點擊哪個按鈕
                if current_amount < target_amount:
                    self._click_betsize_button(driver, Constants.BETSIZE_INCREASE_BUTTON_X_RATIO, Constants.BETSIZE_INCREASE_BUTTON_Y_RATIO)  # 增加
                else:
                    self._click_betsize_button(driver, Constants.BETSIZE_DECREASE_BUTTON_X_RATIO, Constants.BETSIZE_DECREASE_BUTTON_Y_RATIO)  # 減少
                
                time.sleep(Constants.BETSIZE_ADJUST_RETRY_WAIT)
            
            self.logger.error("✗ 金額調整失敗")
            return False
            
        except Exception as e:
            self.logger.error(f"✗ 調整過程發生錯誤: {e}")
            return False
    
    def capture_betsize_template(self, driver: WebDriver, amount: float) -> bool:
        """截取下注金額模板（使用 Canvas 座標比例）。
        
        Args:
            driver: WebDriver 實例
            amount: 下注金額
            
        Returns:
            bool: 截取成功返回True
        """
        try:
            # 取得 Canvas 區域
            rect = driver.execute_script(f"""
                const canvas = document.getElementById('{Constants.GAME_CANVAS}');
                if (!canvas) {{
                    return {{error: 'Canvas not found'}};
                }}
                const r = canvas.getBoundingClientRect();
                return {{x: r.left, y: r.top, w: r.width, h: r.height}};
            """)
            
            if 'error' in rect:
                self.logger.error(f"找不到 Canvas 元素 (ID: {Constants.GAME_CANVAS})")
                return False
            
            # 直接計算金額顯示位置（避免重複計算）
            display_x = rect["x"] + rect["w"] * Constants.BETSIZE_DISPLAY_X_RATIO
            display_y = rect["y"] + rect["h"] * Constants.BETSIZE_DISPLAY_Y_RATIO
            
            # # 除錯資訊：顯示計算結果
            # self.logger.info(f"📍 Canvas: x={rect['x']:.1f}, y={rect['y']:.1f}, w={rect['w']:.1f}, h={rect['h']:.1f}")
            # self.logger.info(f"📍 計算公式: x = {rect['x']:.1f} + {rect['w']:.1f} × {Constants.BETSIZE_DISPLAY_X_RATIO} = {display_x:.1f}")
            # self.logger.info(f"📍 計算公式: y = {rect['y']:.1f} + {rect['h']:.1f} × {Constants.BETSIZE_DISPLAY_Y_RATIO} = {display_y:.1f}")
            
            # 截取整個瀏覽器畫面
            screenshot = driver.get_screenshot_as_png()
            screenshot_img = Image.open(io.BytesIO(screenshot))
            
            # 獲取實際截圖尺寸
            image_width, image_height = screenshot_img.size
            
            # 計算縮放比例（Retina 顯示器會是 2 倍）
            scale_x = image_width / rect["w"] if rect["w"] > 0 else 1
            scale_y = image_height / rect["h"] if rect["h"] > 0 else 1
            
            # 轉換為截圖中的實際座標（乘以縮放比例）
            actual_x = int(display_x * scale_x)
            actual_y = int(display_y * scale_y)
            
            self.logger.info(f"📍 截圖尺寸: {image_width}x{image_height}, 縮放比例: {scale_x:.2f}x, {scale_y:.2f}x")
            self.logger.info(f"📍 截圖座標: ({actual_x}, {actual_y})")
            
            # 裁切範圍（使用常數定義）
            crop_left = max(0, actual_x - Constants.BETSIZE_CROP_MARGIN_X)
            crop_top = max(0, actual_y - Constants.BETSIZE_CROP_MARGIN_Y)
            crop_right = min(image_width, actual_x + Constants.BETSIZE_CROP_MARGIN_X)
            crop_bottom = min(image_height, actual_y + Constants.BETSIZE_CROP_MARGIN_Y)
            
            # 裁切圖片
            cropped_img = screenshot_img.crop((crop_left, crop_top, crop_right, crop_bottom))
            
            # 使用輔助函式取得專案根目錄
            bet_size_dir = get_resource_path("img") / "bet_size"
            bet_size_dir.mkdir(parents=True, exist_ok=True)
            
            # 檔名使用金額（整數去掉 .0，小數保留）
            if amount == int(amount):
                filename = f"{int(amount)}.png"
            else:
                filename = f"{amount}.png"
            
            output_path = bet_size_dir / filename
            cropped_img.save(output_path)
            
            self.logger.info(f"✓ 模板已儲存: {filename}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"截取金額模板失敗: {e}")
            return False


# ============================================================================
# 瀏覽器操作輔助類
# ============================================================================

class WindowSizeLocker:
    """視窗大小鎖定器。
    
    持續監控並鎖定瀏覽器視窗大小，防止使用者或系統改變視窗尺寸。
    使用背景執行緒定期檢查視窗大小，如果不符合目標則自動調整。
    
    Attributes:
        driver: WebDriver 實例
        target_width: 目標視窗寬度
        target_height: 目標視窗高度
        interval: 檢查間隔（秒）
        running: 是否正在執行
        thread: 背景執行緒
    """
    
    def __init__(
        self, 
        driver: WebDriver, 
        target_width: int = Constants.DEFAULT_WINDOW_WIDTH, 
        target_height: int = Constants.DEFAULT_WINDOW_HEIGHT, 
        interval: float = 0.5
    ):
        """初始化視窗大小鎖定器。
        
        Args:
            driver: WebDriver 實例
            target_width: 目標視窗寬度（預設 1280）
            target_height: 目標視窗高度（預設 720）
            interval: 檢查間隔秒數（預設 0.5）
        """
        self.driver = driver
        self.target_width = target_width
        self.target_height = target_height
        self.interval = interval
        self.running = False
        self.thread: Optional[threading.Thread] = None
    
    def _monitor(self) -> None:
        """監控視窗大小並自動修正（背景執行緒）"""
        while self.running:
            try:
                current_size = self.driver.get_window_size()
                if (current_size['width'] != self.target_width or 
                    current_size['height'] != self.target_height):
                    self.driver.set_window_size(self.target_width, self.target_height)
                    print(f"🔄 視窗大小已重置為 {self.target_width}x{self.target_height}")
            except:
                # 忽略錯誤，可能是瀏覽器已關閉
                pass
            time.sleep(self.interval)
    
    def start(self) -> None:
        """啟動視窗大小監控"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._monitor, daemon=True)
            self.thread.start()
    
    def stop(self) -> None:
        """停止視窗大小監控"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)


class BrowserHelper:
    """瀏覽器操作輔助類別。
    
    提供常用的瀏覽器操作方法，避免程式碼重複。
    包括 CDP 點擊、座標計算、按鍵模擬等。
    """
    
    @staticmethod
    def execute_cdp_click(driver: WebDriver, x: float, y: float) -> None:
        """使用 Chrome DevTools Protocol 執行點擊操作。
        
        Args:
            driver: WebDriver 實例
            x: X 座標
            y: Y 座標
        """
        for event_type in ["mousePressed", "mouseReleased"]:
            driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
                "type": event_type,
                "x": x,
                "y": y,
                "button": "left",
                "clickCount": 1
            })
    
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
    
    @staticmethod
    def calculate_scaled_position(
        base_x: float,
        base_y: float,
        screenshot_width: int,
        screenshot_height: int,
        base_width: int = Constants.DEFAULT_WINDOW_WIDTH,
        base_height: int = Constants.DEFAULT_WINDOW_HEIGHT
    ) -> Tuple[int, int]:
        """根據視窗大小計算縮放後的座標。
        
        Args:
            base_x: 基準 X 座標（基於預設視窗大小）
            base_y: 基準 Y 座標（基於預設視窗大小）
            screenshot_width: 實際截圖寬度
            screenshot_height: 實際截圖高度
            base_width: 基準視窗寬度
            base_height: 基準視窗高度
            
        Returns:
            (actual_x, actual_y) 實際座標
        """
        x_ratio = base_x / base_width
        y_ratio = base_y / base_height
        actual_x = int(screenshot_width * x_ratio)
        actual_y = int(screenshot_height * y_ratio)
        return actual_x, actual_y
    
    @staticmethod
    def check_and_fix_window_size(
        driver: WebDriver,
        target_width: int = Constants.DEFAULT_WINDOW_WIDTH,
        target_height: int = Constants.DEFAULT_WINDOW_HEIGHT,
        logger: Optional[logging.Logger] = None
    ) -> bool:
        """檢查並修正視窗大小。
        
        如果視窗大小不符合目標，則自動調整。
        
        Args:
            driver: WebDriver 實例
            target_width: 目標視窗寬度
            target_height: 目標視窗高度
            logger: 日誌記錄器（選填）
            
        Returns:
            是否進行了調整
        """
        current_size = driver.get_window_size()
        current_width = current_size['width']
        current_height = current_size['height']
        
        if current_width != target_width or current_height != target_height:
            if logger:
                logger.info(f"視窗大小不符 ({current_width}x{current_height})，調整為 {target_width}x{target_height}")
            driver.set_window_size(target_width, target_height)
            return True
        return False
    
    @staticmethod
    def remove_maintenance_popup(driver: WebDriver) -> None:
        """移除維護公告彈窗和其他干擾性彈窗。
        
        使用 JavaScript 移除所有彈窗元素，包括：
        - 維護公告彈窗（data-v-0ef3d734）
        - Google 密碼管理工具彈窗
        - 其他遮罩層
        
        Args:
            driver: WebDriver 實例
        """
        js_script = """
        // 刪掉所有 data-v-0ef3d734（彈窗所有 scope 元件）
        document.querySelectorAll("div[data-v-0ef3d734]").forEach(el => el.remove());
        
        // 刪掉 Google 密碼管理工具彈窗
        document.querySelectorAll("div[jsname], div[jsaction]").forEach(el => {
            const text = el.textContent || "";
            if (text.includes("變更你的密碼") || text.includes("密碼管理工具") || text.includes("資料侵害")) {
                el.remove();
            }
        });
        
        // 刪掉外層黑色遮罩 (bg-opacity 60%)
        document.querySelectorAll("div[class*='bg-opacity'], div[class*='z-20'], div[class*='fixed']").forEach(el => {
            if (el.clientHeight > 400 && el.clientWidth > 400) {
                el.remove();
            }
        });
        """
        driver.execute_script(js_script)


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
                # cv2.imwrite 無法處理中文路徑，改用 imencode + 檔案寫入
                is_success, buffer = cv2.imencode('.png', image_cv)
                if is_success:
                    with open(save_path, 'wb') as f:
                        f.write(buffer.tobytes())
                    self.logger.info(f"截圖已儲存 {save_path}")
                else:
                    raise ImageDetectionError(f"圖片編碼失敗")
            
            return image_cv
            
        except Exception as e:
            raise ImageDetectionError(f"截圖失敗: {e}") from e
    
    def match_template(self, screenshot: np.ndarray, template_path: Path, threshold: float = Constants.MATCH_THRESHOLD) -> Optional[Tuple[int, int, float]]:
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
            
            # 讀取模板圖片（使用支援 Unicode 路徑的函式，解決中文路徑問題）
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
    
    def detect_in_browser(self, driver: WebDriver, template_name: str, threshold: float = Constants.MATCH_THRESHOLD) -> Optional[Tuple[int, int, float]]:
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
            screenshot = self.capture_screenshot(driver)
            template_path = self.get_template_path(template_name)
            return self.match_template(screenshot, template_path, threshold)
        except Exception as e:
            self.logger.error(f"瀏覽器圖片檢測失敗 {e}")
            return None
    
    def detect_error_message_in_region(
        self, 
        driver: WebDriver, 
        x: int, 
        y: int, 
        margin: int = Constants.TEMPLATE_CROP_MARGIN,
        threshold: float = Constants.MATCH_THRESHOLD
    ) -> bool:
        """檢測指定區域是否包含錯誤訊息。
        
        Args:
            driver: WebDriver 實例
            x: 區域中心 X 座標
            y: 區域中心 Y 座標
            margin: 裁切邊距
            threshold: 匹配閾值
            
        Returns:
            是否檢測到錯誤訊息
        """
        try:
            # 截取全螢幕
            screenshot = self.capture_screenshot(driver)
            if screenshot is None:
                return False
            
            # 獲取截圖尺寸
            height, width = screenshot.shape[:2]
            
            # 計算裁切範圍
            crop_left = max(0, x - margin)
            crop_top = max(0, y - margin)
            crop_right = min(width, x + margin)
            crop_bottom = min(height, y + margin)
            
            # 裁切區域
            cropped = screenshot[crop_top:crop_bottom, crop_left:crop_right]
            
            # 讀取錯誤訊息模板
            template_path = self.get_template_path(Constants.ERROR_MESSAGE)
            if not template_path.exists():
                self.logger.debug(f"錯誤訊息模板不存在: {template_path}")
                return False
            
            template = cv2_imread_unicode(template_path)
            if template is None:
                self.logger.debug("無法讀取錯誤訊息模板")
                return False
            
            # 轉換為灰階
            cropped_gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            
            # 模板匹配
            result = cv2.matchTemplate(cropped_gray, template_gray, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(result)
            
            return max_val >= threshold
            
        except Exception as e:
            self.logger.debug(f"錯誤訊息檢測失敗: {e}")
            return False


# ============================================================================
# 瀏覽器恢復管理器
# ============================================================================

class BrowserRecoveryManager:
    """瀏覽器恢復管理器。
    
    負責處理瀏覽器錯誤檢測、自動重啟等恢復操作。
    提供模組化的錯誤處理流程。
    """
    
    def __init__(
        self,
        image_detector: 'ImageDetector',
        browser_operator: 'SyncBrowserOperator',
        logger: Optional[logging.Logger] = None
    ):
        """初始化恢復管理器。
        
        Args:
            image_detector: 圖片檢測器
            browser_operator: 瀏覽器操作器
            logger: 日誌記錄器
        """
        self.image_detector = image_detector
        self.browser_operator = browser_operator
        self.logger = logger or LoggerFactory.get_logger()
    
    def detect_error_message(self, driver: WebDriver) -> bool:
        """檢測瀏覽器中是否出現錯誤訊息（雙區域檢測）。
        
        Args:
            driver: WebDriver 實例
            
        Returns:
            是否檢測到錯誤訊息
        """
        # 檢測左側區域
        left_error = self.image_detector.detect_error_message_in_region(
            driver,
            Constants.ERROR_MESSAGE_LEFT_X,
            Constants.ERROR_MESSAGE_LEFT_Y,
            Constants.TEMPLATE_CROP_MARGIN
        )
        
        # 檢測右側區域
        right_error = self.image_detector.detect_error_message_in_region(
            driver,
            Constants.ERROR_MESSAGE_RIGHT_X,
            Constants.ERROR_MESSAGE_RIGHT_Y,
            Constants.TEMPLATE_CROP_MARGIN
        )
        
        # 兩個區域都檢測到才算有錯誤
        return left_error and right_error
    
    def refresh_browser(self, context: BrowserContext) -> bool:
        """重新整理單個瀏覽器。
        
        Args:
            context: 瀏覽器上下文
            
        Returns:
            是否成功
        """
        try:
            context.driver.refresh()
            time.sleep(Constants.DEFAULT_WAIT_SECONDS)
            return True
        except Exception as e:
            self.logger.error(f"瀏覽器 {context.index} 重新整理失敗: {e}")
            return False
    
    def wait_for_template(
        self,
        contexts: List[BrowserContext],
        template_name: str,
        max_attempts: int = Constants.MAX_DETECTION_ATTEMPTS
    ) -> bool:
        """等待所有瀏覽器顯示指定模板。
        
        Args:
            contexts: 瀏覽器上下文列表
            template_name: 模板名稱
            max_attempts: 最大嘗試次數
            
        Returns:
            是否所有瀏覽器都找到
        """
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            all_found = True
            
            for context in contexts:
                try:
                    result = self.image_detector.detect_in_browser(
                        context.driver,
                        template_name
                    )
                    if not result:
                        all_found = False
                        break
                except Exception:
                    all_found = False
                    break
            
            if all_found:
                return True
            
            # 顯示進度
            if attempt % Constants.DETECTION_PROGRESS_INTERVAL == 0:
                found_count = sum(
                    1 for context in contexts
                    if self.image_detector.detect_in_browser(
                        context.driver,
                        template_name
                    ) is not None
                )
                self.logger.info(f"檢測中... ({found_count}/{len(contexts)})")
            
            time.sleep(Constants.DETECTION_INTERVAL)
        
        return False
    
    def restart_and_recover(
        self,
        contexts: List[BrowserContext],
        canvas_rect: Dict[str, float]
    ) -> bool:
        """重啟瀏覽器並恢復到可用狀態。
        
        Args:
            contexts: 需要重啟的瀏覽器上下文列表
            canvas_rect: Canvas 區域資訊
            
        Returns:
            是否成功
        """
        if not contexts:
            return True
        
        # 1. 重新整理所有瀏覽器
        for context in contexts:
            self.refresh_browser(context)
        
        # 2. 等待 lobby_login 出現
        if not self.wait_for_template(contexts, Constants.LOBBY_LOGIN):
            self.logger.error("等待 lobby_login 超時")
            return False
        
        # 3. 計算並點擊開始遊戲按鈕
        start_x, start_y = BrowserHelper.calculate_click_position(
            canvas_rect,
            Constants.LOBBY_LOGIN_BUTTON_X_RATIO,
            Constants.LOBBY_LOGIN_BUTTON_Y_RATIO
        )
        
        time.sleep(Constants.TEMPLATE_CAPTURE_WAIT)
        
        # 同步點擊所有瀏覽器
        for context in contexts:
            try:
                BrowserHelper.execute_cdp_click(context.driver, start_x, start_y)
            except Exception as e:
                self.logger.error(f"瀏覽器 {context.index} 點擊失敗: {e}")
        
        # 4. 等待 lobby_login 消失
        time.sleep(Constants.DEFAULT_WAIT_SECONDS)
        
        return True


# ============================================================================
# 遊戲控制中心
# ============================================================================

class GameControlCenter:
    """遊戲控制中心。
    
    提供互動式命令行介面，用於控制多個瀏覽器的遊戲操作。
    支援啟動、暫停遊戲等基本控制功能。
    
    Attributes:
        browser_contexts: 瀏覽器上下文列表
        browser_operator: 瀏覽器操作器
        logger: 日誌記錄器
        running: 控制中心運行狀態
        game_running: 遊戲運行狀態
    """
    
    def __init__(
        self,
        browser_contexts: List[BrowserContext],
        browser_operator: SyncBrowserOperator,
        bet_rules: List[BetRule],
        logger: Optional[logging.Logger] = None
    ):
        """初始化控制中心。
        
        Args:
            browser_contexts: 瀏覽器上下文列表
            browser_operator: 瀏覽器操作器
            bet_rules: 下注規則列表
            logger: 日誌記錄器
        """
        self.browser_contexts = browser_contexts
        self.browser_operator = browser_operator
        self.bet_rules = bet_rules  # 在初始化時就設定規則
        self.logger = logger or LoggerFactory.get_logger()
        self.running = False
        self.game_running = False  # 遊戲運行狀態
        self.auto_press_running = False  # 自動按鍵運行狀態
        self.min_interval = 1.0  # 最小間隔時間
        self.max_interval = 1.0  # 最大間隔時間
        self.auto_press_threads: Dict[int, threading.Thread] = {}  # 每個瀏覽器的執行緒
        self._stop_event = threading.Event()  # 停止事件
        
        # 規則執行相關
        self.rule_running = False  # 規則執行狀態
        self.rule_thread: Optional[threading.Thread] = None  # 規則執行執行緒
    
    def show_help(self) -> None:
        """顯示幫助信息"""
        help_text = """
╔══════════════════════════════════════════════════════════╗
║            遊戲控制中心 - 指令說明                       ║
╚══════════════════════════════════════════════════════════╝

【遊戲控制】
  s <min>,<max>    開始自動按鍵（設定隨機間隔）
                   範例: s 1,2  (間隔 1~2 秒)
                   
  r                開始執行規則（依照用戶規則.txt自動切換金額）
                   格式: 金額:時間(分鐘):最小(秒數):最大(秒數)
                   範例: 4:10:1:1 表示金額4，持續10分鐘，間隔1~1秒
                   
  p                暫停自動按鍵/規則執行
  
  b <金額>         調整所有瀏覽器的下注金額
                   範例: b 0.4, b 2.4, b 10
  
  f <編號>         購買免費遊戲
                   f 0      - 所有瀏覽器都購買
                   f 1      - 第 1 個瀏覽器購買
                   f 1,2,3  - 第 1、2、3 個瀏覽器購買
  
  a <次數>         設定自動旋轉
                   a 10     - 自動旋轉 10 次
                   a 50     - 自動旋轉 50 次
                   a 100    - 自動旋轉 100 次
                   
  c                截取金額模板（用於金額識別）

【系統控制】
  h                顯示此幫助信息
  
  q <編號>         關閉指定瀏覽器
                   q 0      - 關閉所有瀏覽器並退出
                   q 1      - 關閉第 1 個瀏覽器
                   q 1,2,3  - 關閉第 1、2、3 個瀏覽器

提示：所有指令都區分大小寫，請使用小寫字母
"""
        self.logger.info(help_text)
    
    def _auto_press_loop_single(self, context: BrowserContext, browser_index: int) -> None:
        """單個瀏覽器的自動按鍵循環（優化版）。
        
        Args:
            context: 瀏覽器上下文
            browser_index: 瀏覽器索引
        """
        import random
        
        press_count = 0
        username = context.credential.username
        driver = context.driver
        
        while not self._stop_event.is_set():
            try:
                press_count += 1
                
                # 執行按空白鍵
                try:
                    BrowserHelper.execute_cdp_space_key(driver)
                except Exception as e:
                    self.logger.error(f"瀏覽器 {browser_index} ({username}) 按鍵失敗: {e}")
                
                # 每個瀏覽器使用獨立的隨機間隔
                interval = random.uniform(self.min_interval, self.max_interval)
                
                # 使用 wait 而非 sleep，這樣可以立即響應停止信號
                if self._stop_event.wait(timeout=interval):
                    break
                    
            except Exception as e:
                self.logger.error(f"瀏覽器 {browser_index} ({username}) 執行錯誤: {e}")
                self._stop_event.wait(timeout=Constants.STOP_EVENT_ERROR_WAIT)
        
        self.logger.info(f"瀏覽器 {browser_index} ({username}) 已停止，共執行 {press_count} 次")
    
    def _start_auto_press(self) -> None:
        """為每個瀏覽器啟動獨立的自動按鍵執行緒。"""
        if self.auto_press_running:
            self.logger.warning("自動按鍵已在運行中")
            return
        
        # 清除停止事件
        self._stop_event.clear()
        self.auto_press_threads.clear()
        
        # 為每個瀏覽器啟動獨立執行緒
        for i, context in enumerate(self.browser_contexts, 1):
            thread = threading.Thread(
                target=self._auto_press_loop_single,
                args=(context, i),
                daemon=True,
                name=f"AutoPressThread-{i}"
            )
            self.auto_press_threads[i] = thread
            thread.start()
        
        self.auto_press_running = True
        self.game_running = True
        
        self.logger.info(f"✓ 已啟動 {len(self.browser_contexts)} 個瀏覽器的自動按鍵")
    
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
                thread.join(timeout=Constants.AUTO_PRESS_STOP_TIMEOUT)
                
                if not thread.is_alive():
                    stopped_count += 1
                else:
                    self.logger.warning(f"瀏覽器 {browser_index} 的執行緒未能正常結束")
            else:
                stopped_count += 1
        
        self.logger.info(f"✓ 已停止 {stopped_count}/{len(self.auto_press_threads)} 個瀏覽器")
        
        self.auto_press_threads.clear()
        self.auto_press_running = False
        self.game_running = False
    
    def _rule_execution_loop(self) -> None:
        """規則執行主循環（在獨立執行緒中運行）。"""
        if not self.bet_rules:
            self.logger.error("沒有可執行的規則")
            return
        
        self.logger.info(f"開始執行規則，共 {len(self.bet_rules)} 條")
        
        rule_index = 0
        while not self._stop_event.is_set() and self.rule_running:
            try:
                # 取得當前規則
                current_rule = self.bet_rules[rule_index]
                
                # === 步驟 1: 確保自動按鍵已完全停止 ===
                if self.auto_press_running:
                    self.logger.info("停止自動按鍵...")
                    
                    # 設置停止事件
                    self._stop_event.set()
                    
                    # 等待所有執行緒完全停止
                    for browser_index, thread in list(self.auto_press_threads.items()):
                        if thread and thread.is_alive():
                            thread.join(timeout=Constants.AUTO_PRESS_THREAD_JOIN_TIMEOUT)
                            if thread.is_alive():
                                self.logger.warning(f"瀏覽器 {browser_index} 執行緒未能及時停止")
                    
                    self.auto_press_threads.clear()
                    self.auto_press_running = False
                    
                    # 等待畫面穩定
                    time.sleep(Constants.RULE_SWITCH_WAIT)
                    self.logger.info("✓ 自動按鍵已停止")
                
                # 顯示規則資訊
                self.logger.info("")
                self.logger.info("─" * 60)
                self.logger.info(
                    f"規則 {rule_index + 1}/{len(self.bet_rules)}: "
                    f"金額 {current_rule.amount}, 持續 {current_rule.duration} 分鐘, "
                    f"間隔 {current_rule.min_seconds}~{current_rule.max_seconds} 秒"
                )
                
                # === 步驟 2: 調整所有瀏覽器的下注金額 ===
                self.logger.info(f"調整金額到 {current_rule.amount}...")
                results = self.browser_operator.adjust_betsize_all(
                    self.browser_contexts,
                    current_rule.amount
                )
                
                # 統計結果
                success_count = sum(1 for r in results if r.success)
                if success_count == len(self.browser_contexts):
                    self.logger.info(f"✓ 全部 {success_count} 個瀏覽器金額調整完成")
                else:
                    self.logger.warning(
                        f"⚠ {success_count}/{len(self.browser_contexts)} 個瀏覽器金額調整完成"
                    )
                    # 如果有失敗的，記錄詳情
                    for i, result in enumerate(results, 1):
                        if not result.success:
                            username = self.browser_contexts[i-1].credential.username
                            self.logger.error(f"  [{username}] 調整失敗")
                
                # === 步驟 3: 啟動自動按鍵 ===
                self.logger.info(
                    f"啟動自動按鍵 (持續 {current_rule.duration} 分鐘, "
                    f"間隔 {current_rule.min_seconds}~{current_rule.max_seconds} 秒)"
                )
                
                # 設置每個瀏覽器的隨機間隔
                self.min_interval = current_rule.min_seconds
                self.max_interval = current_rule.max_seconds
                
                # 清除停止事件（確保自動按鍵可以運行）
                self._stop_event.clear()
                
                # 為每個瀏覽器啟動自動按鍵執行緒
                for i, context in enumerate(self.browser_contexts, 1):
                    thread = threading.Thread(
                        target=self._auto_press_loop_single,
                        args=(context, i),
                        daemon=True,
                        name=f"RuleAutoPress-{i}"
                    )
                    self.auto_press_threads[i] = thread
                    thread.start()
                
                self.auto_press_running = True
                
                # === 步驟 4: 等待指定時間 ===
                wait_seconds = current_rule.duration * 60
                elapsed_time = 0
                check_interval = 1.0  # 每秒檢查一次
                
                # 只在第一次顯示進度提示
                progress_shown = False
                
                while elapsed_time < wait_seconds and not self._stop_event.is_set():
                    if self._stop_event.wait(timeout=check_interval):
                        break
                    elapsed_time += check_interval
                    
                    # 每 60 秒顯示一次剩餘時間
                    if int(elapsed_time) % 60 == 0 and elapsed_time > 0:
                        remaining_minutes = int((wait_seconds - elapsed_time) / 60)
                        if remaining_minutes > 0:
                            if not progress_shown:
                                progress_shown = True
                            self.logger.info(f"剩餘 {remaining_minutes} 分鐘...")
                
                # 檢查是否被停止
                if self._stop_event.is_set():
                    self.logger.info("收到停止信號")
                    break
                
                # 顯示完成訊息
                self.logger.info(f"✓ 規則 {rule_index + 1} 執行完成")
                
                # 移動到下一條規則（循環）
                rule_index = (rule_index + 1) % len(self.bet_rules)
                
                # 顯示下一步提示
                if rule_index == 0:
                    self.logger.info("所有規則執行完畢，回到第一條規則...")
                else:
                    self.logger.info("準備執行下一條規則...")
                
                # 規則之間短暫暫停（讓畫面穩定）
                time.sleep(Constants.RULE_SWITCH_WAIT)
                
            except Exception as e:
                self.logger.error(f"執行規則時發生錯誤: {e}")
                # 確保清理自動按鍵執行緒
                self.auto_press_threads.clear()
                self.auto_press_running = False
                if self._stop_event.wait(timeout=Constants.STOP_EVENT_WAIT_TIMEOUT):
                    break
        
        # 最終清理
        if self.auto_press_running:
            for browser_index, thread in self.auto_press_threads.items():
                if thread and thread.is_alive():
                    thread.join(timeout=Constants.AUTO_PRESS_THREAD_JOIN_TIMEOUT)
        
        self.auto_press_threads.clear()
        self.auto_press_running = False
        self.logger.info("")
        self.logger.info("規則執行已停止")
        self.rule_running = False
    
    def _start_rule_execution(self) -> None:
        """啟動規則執行。"""
        if self.rule_running:
            self.logger.warning("規則執行已在運行中")
            return
        
        if self.auto_press_running:
            self.logger.warning("自動按鍵正在運行，請先使用 'p' 暫停")
            return
        
        # 檢查是否有規則
        if not self.bet_rules:
            self.logger.error("沒有可執行的規則，請檢查 用戶規則.txt")
            return
        
        # 顯示規則列表
        self.logger.info("載入的規則:")
        for i, rule in enumerate(self.bet_rules, 1):
            self.logger.info(
                f"  {i}. 金額 {rule.amount}, 持續 {rule.duration} 分鐘, "
                f"間隔 {rule.min_seconds}~{rule.max_seconds} 秒"
            )
        
        # 清除停止事件
        self._stop_event.clear()
        
        # 啟動規則執行執行緒
        self.rule_thread = threading.Thread(
            target=self._rule_execution_loop,
            daemon=True,
            name="RuleExecutionThread"
        )
        self.rule_thread.start()
        self.rule_running = True
        self.game_running = True
        
        self.logger.info("✓ 規則執行已啟動 (按 'p' 可暫停)")
        self.logger.info("")
    
    def _stop_rule_execution(self) -> None:
        """停止規則執行。"""
        if not self.rule_running:
            self.logger.warning("規則執行未在運行")
            return
        
        self.logger.info("正在停止規則執行...")
        
        # 設置停止事件
        self._stop_event.set()
        
        # 停止所有自動按鍵執行緒
        if self.auto_press_threads:
            self.logger.info("停止自動按鍵執行緒...")
            stopped_count = 0
            for browser_index, thread in self.auto_press_threads.items():
                if thread and thread.is_alive():
                    thread.join(timeout=Constants.AUTO_PRESS_THREAD_JOIN_TIMEOUT)
                    if not thread.is_alive():
                        stopped_count += 1
                else:
                    stopped_count += 1
            
            self.logger.info(f"✓ 已停止 {stopped_count}/{len(self.auto_press_threads)} 個瀏覽器的自動按鍵")
            self.auto_press_threads.clear()
            self.auto_press_running = False
        
        # 等待規則執行緒結束
        if self.rule_thread and self.rule_thread.is_alive():
            self.rule_thread.join(timeout=Constants.AUTO_PRESS_STOP_TIMEOUT)
            
            if not self.rule_thread.is_alive():
                self.logger.info("✓ 規則執行已停止")
            else:
                self.logger.warning("規則執行執行緒未能正常結束")
        
        self.rule_running = False
        self.game_running = False
        self.rule_thread = None
    
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
                if not command_arguments:
                    self.logger.error("指令格式錯誤，請使用: q <編號>")
                    self.logger.info("  q 0      - 關閉所有瀏覽器並退出")
                    self.logger.info("  q 1      - 關閉第 1 個瀏覽器")
                    self.logger.info("  q 1,2,3  - 關閉第 1、2、3 個瀏覽器")
                    return True
                
                try:
                    # 解析參數
                    target_indices = []
                    
                    # 處理逗號分隔的多個編號
                    if ',' in command_arguments:
                        try:
                            indices = [int(x.strip()) for x in command_arguments.split(',')]
                            for browser_index in indices:
                                if browser_index < 1 or browser_index > len(self.browser_contexts):
                                    self.logger.error(
                                        f"瀏覽器編號 {browser_index} 無效，請輸入 1-{len(self.browser_contexts)} 之間的數字"
                                    )
                                    return True
                            target_indices = indices
                        except ValueError:
                            self.logger.error(f"無效的編號格式: {command_arguments}，請使用數字和逗號 (例如: q 1,2,3)")
                            return True
                    else:
                        # 單一數字
                        try:
                            index = int(command_arguments)
                            if index == 0:
                                # 0 表示所有瀏覽器
                                target_indices = list(range(1, len(self.browser_contexts) + 1))
                            elif index < 1 or index > len(self.browser_contexts):
                                self.logger.error(
                                    f"瀏覽器編號無效，請輸入 0 (全部) 或 1-{len(self.browser_contexts)} 之間的數字"
                                )
                                return True
                            else:
                                target_indices = [index]
                        except ValueError:
                            self.logger.error(f"無效的編號: {command_arguments}，請輸入數字 (例如: q 1 或 q 1,2)")
                            return True
                    
                    # 顯示執行信息
                    if len(target_indices) == len(self.browser_contexts):
                        self.logger.info(f"開始關閉瀏覽器 (全部 {len(target_indices)} 個)")
                    elif len(target_indices) == 1:
                        username = self.browser_contexts[target_indices[0] - 1].credential.username
                        self.logger.info(f"開始關閉瀏覽器 (瀏覽器 {target_indices[0]}: {username})")
                    else:
                        self.logger.info(f"開始關閉瀏覽器 ({len(target_indices)} 個)")
                    
                    # 關閉指定的瀏覽器
                    closed_count = 0
                    failed_browsers = []
                    
                    # 從後往前遍歷，避免索引問題
                    for browser_index in sorted(target_indices, reverse=True):
                        try:
                            context = self.browser_contexts[browser_index - 1]
                            username = context.credential.username
                            
                            # 關閉瀏覽器
                            context.driver.quit()
                            
                            # 從列表中移除
                            self.browser_contexts.pop(browser_index - 1)
                            
                            self.logger.info(f"✓ 已關閉瀏覽器 {browser_index} ({username})")
                            closed_count += 1
                            
                        except Exception as e:
                            username = self.browser_contexts[browser_index - 1].credential.username
                            self.logger.error(f"關閉瀏覽器 {browser_index} ({username}) 失敗: {e}")
                            failed_browsers.append((browser_index, username))
                    
                    # 顯示總結
                    if closed_count == len(target_indices):
                        self.logger.info(f"✓ 關閉完成: 全部 {closed_count} 個瀏覽器已關閉")
                    else:
                        self.logger.warning(
                            f"⚠ 部分完成: {closed_count}/{len(target_indices)} 個瀏覽器已關閉"
                        )
                        if failed_browsers:
                            for browser_index, username in failed_browsers:
                                self.logger.error(f"  瀏覽器 {browser_index} ({username}) 失敗")
                    
                    # 如果所有瀏覽器都關閉了，退出控制中心
                    if len(self.browser_contexts) == 0:
                        self.logger.info("所有瀏覽器已關閉，退出控制中心")
                        return False
                    else:
                        self.logger.info(f"剩餘 {len(self.browser_contexts)} 個瀏覽器仍在運行")
                    
                except Exception as e:
                    self.logger.error(f"關閉瀏覽器時發生錯誤: {e}")
            
            elif cmd == 'h':
                self.show_help()
            
            elif cmd == 's':
                # 解析 's' 指令參數
                if not command_arguments:
                    self.logger.error("指令格式錯誤，請使用: s min,max (例如: s 1,2)")
                    return True
                
                # 解析用戶輸入的間隔時間
                try:
                    interval_parts = command_arguments.split(',')
                    if len(interval_parts) != 2:
                        self.logger.error(
                            "間隔時間格式錯誤，請使用: s min,max (例如: s 1,2)"
                        )
                        return True
                    
                    min_interval = float(interval_parts[0].strip())
                    max_interval = float(interval_parts[1].strip())
                    
                    if min_interval <= 0 or max_interval <= 0:
                        self.logger.error("間隔時間必須大於 0")
                        return True
                    
                    if min_interval > max_interval:
                        self.logger.error("最小間隔不能大於最大間隔")
                        return True
                        
                except ValueError:
                    self.logger.error(
                        "間隔時間格式錯誤，請輸入數字 (例如: s 1,2)"
                    )
                    return True
                
                # 檢查是否已在運行
                if self.auto_press_running:
                    self.logger.warning(
                        f"自動按鍵已在運行中 (間隔: {self.min_interval}~{self.max_interval}秒)\n"
                        f"請先使用 'p' 暫停，再重新啟動"
                    )
                    return True
                
                # 設置間隔時間
                self.min_interval = min_interval
                self.max_interval = max_interval
                
                self.logger.info(
                    f"✓ 啟動自動運行\n"
                    f"  間隔: {min_interval}~{max_interval} 秒\n"
                    f"  瀏覽器: {len(self.browser_contexts)} 個\n"
                    f"  按 'p' 可暫停"
                )
                
                # 啟動自動按鍵
                self._start_auto_press()
            
            elif cmd == 'p':
                # 暫停指令 - 可暫停自動按鍵或規則執行
                if self.auto_press_running:
                    self._stop_auto_press()
                    self.logger.info("✓ 已暫停自動按鍵")
                elif self.rule_running:
                    self._stop_rule_execution()
                    self.logger.info("✓ 已暫停規則執行")
                else:
                    self.logger.warning("目前沒有運行中的自動操作")
            
            elif cmd == 'r':
                # 開始執行規則
                if self.rule_running:
                    self.logger.warning("規則執行已在運行中，請先使用 'p' 暫停")
                    return True
                
                if self.auto_press_running:
                    self.logger.warning("自動按鍵正在運行，請先使用 'p' 暫停")
                    return True
                
                self._start_rule_execution()
            
            elif cmd == 'b':
                # 解析 b 指令參數
                if not command_arguments:
                    self.logger.error("指令格式錯誤，請使用: b amount (例如: b 0.4)")
                    return True
                
                try:
                    target_amount = float(command_arguments)
                    
                    self.logger.info(f"開始調整金額到 {target_amount}...")
                    
                    # 使用同步方法調整所有瀏覽器的金額
                    results = self.browser_operator.adjust_betsize_all(
                        self.browser_contexts,
                        target_amount
                    )
                    
                    # 統計結果
                    success_count = sum(1 for r in results if r.success)
                    
                    if success_count == len(self.browser_contexts):
                        self.logger.info(f"✓ 金額調整完成: 全部 {success_count} 個瀏覽器成功")
                    else:
                        self.logger.warning(
                            f"⚠ 部分完成: {success_count}/{len(self.browser_contexts)} 個瀏覽器成功"
                        )
                        # 顯示失敗的瀏覽器
                        for i, result in enumerate(results, 1):
                            if not result.success:
                                username = self.browser_contexts[i-1].credential.username
                                self.logger.error(f"  瀏覽器 {i} ({username}) 失敗")
                    
                except ValueError:
                    self.logger.error(f"無效的金額: {command_arguments}，請輸入數字")
            
            elif cmd == 'f':
                # 購買免費遊戲指令
                if not command_arguments:
                    self.logger.error("指令格式錯誤，請使用: f <編號>")
                    self.logger.info("  f 0      - 所有瀏覽器")
                    self.logger.info("  f 1      - 第 1 個瀏覽器")
                    self.logger.info("  f 1,2,3  - 第 1、2、3 個瀏覽器")
                    return True
                
                try:
                    # 檢查 Canvas 區域資訊
                    if not hasattr(self.browser_operator, 'last_canvas_rect') or \
                       self.browser_operator.last_canvas_rect is None:
                        self.logger.error("Canvas 區域未初始化，請確保已完成登入流程")
                        return True
                    
                    # 解析參數
                    target_indices = []
                    
                    # 處理逗號分隔的多個編號
                    if ',' in command_arguments:
                        try:
                            indices = [int(x.strip()) for x in command_arguments.split(',')]
                            for browser_index in indices:
                                if browser_index < 1 or browser_index > len(self.browser_contexts):
                                    self.logger.error(
                                        f"瀏覽器編號 {browser_index} 無效，請輸入 1-{len(self.browser_contexts)} 之間的數字"
                                    )
                                    return True
                            target_indices = indices
                        except ValueError:
                            self.logger.error(f"無效的編號格式: {command_arguments}，請使用數字和逗號 (例如: f 1,2,3)")
                            return True
                    else:
                        # 單一數字
                        try:
                            index = int(command_arguments)
                            if index == 0:
                                # 0 表示所有瀏覽器
                                target_indices = list(range(1, len(self.browser_contexts) + 1))
                            elif index < 1 or index > len(self.browser_contexts):
                                self.logger.error(
                                    f"瀏覽器編號無效，請輸入 0 (全部) 或 1-{len(self.browser_contexts)} 之間的數字"
                                )
                                return True
                            else:
                                target_indices = [index]
                        except ValueError:
                            self.logger.error(f"無效的編號: {command_arguments}，請輸入數字 (例如: f 1 或 f 1,2)")
                            return True
                    
                    # 顯示執行信息
                    if len(target_indices) == len(self.browser_contexts):
                        self.logger.info(f"開始購買免費遊戲 (全部 {len(target_indices)} 個瀏覽器)")
                    elif len(target_indices) == 1:
                        username = self.browser_contexts[target_indices[0] - 1].credential.username
                        self.logger.info(f"開始購買免費遊戲 (瀏覽器 {target_indices[0]}: {username})")
                    else:
                        self.logger.info(f"開始購買免費遊戲 ({len(target_indices)} 個瀏覽器)")
                    
                    # 準備目標瀏覽器上下文列表
                    target_contexts = [self.browser_contexts[browser_index - 1] for browser_index in target_indices]
                    
                    # 使用同步方式執行購買
                    results = self.browser_operator.buy_free_game_all(
                        target_contexts,
                        self.browser_operator.last_canvas_rect
                    )
                    
                    # 統計結果
                    success_count = sum(1 for r in results if r.success)
                    failed_browsers = [
                        (target_indices[i], target_contexts[i].credential.username)
                        for i, r in enumerate(results)
                        if not r.success
                    ]
                    
                    # 顯示總結
                    if success_count == len(target_indices):
                        self.logger.info(f"✓ 購買完成: 全部 {success_count} 個瀏覽器成功")
                    else:
                        self.logger.warning(
                            f"⚠ 部分完成: {success_count}/{len(target_indices)} 個瀏覽器成功"
                        )
                        if failed_browsers:
                            for browser_index, username in failed_browsers:
                                self.logger.error(f"  瀏覽器 {browser_index} ({username}) 失敗")
                    
                    # 等待用戶確認免費遊戲流程結束
                    if success_count > 0:
                        self.logger.info("免費遊戲已啟動，請手動遊玩")
                        self.logger.info("結束後請按 Enter 繼續（系統將自動結算）")
                        
                        try:
                            print("按 Enter 繼續 > ", end="", flush=True)
                            input()
                            
                            # 對成功購買的瀏覽器執行空白鍵
                            
                            # 只對成功的瀏覽器執行
                            successful_contexts = [
                                target_contexts[i]
                                for i, r in enumerate(results)
                                if r.success
                            ]
                            
                            if successful_contexts:
                                press_results = self.browser_operator.press_space_all(successful_contexts)
                                press_success = sum(1 for r in press_results if r.success)
                                
                                self.logger.info(f"✓ 已對 {press_success} 個瀏覽器執行結算")
                                
                                # 點擊 LOBBY_LOGIN_BUTTON 座標（連續 5 次，間隔 1 秒）- 快速跳過結算畫面
                                self.logger.info("正在跳過結算畫面...")
                                rect = self.browser_operator.last_canvas_rect
                                lobby_x, lobby_y = BrowserHelper.calculate_click_position(
                                    rect,
                                    Constants.LOBBY_LOGIN_BUTTON_X_RATIO,
                                    Constants.LOBBY_LOGIN_BUTTON_Y_RATIO
                                )
                                
                                def click_lobby_button(context: BrowserContext, index: int, total: int) -> bool:
                                    """跳過結算畫面"""
                                    driver = context.driver
                                    try:
                                        time.sleep(Constants.FREE_GAME_SETTLE_INITIAL_WAIT)  # 等待後開始點擊
                                        for click_num in range(1, Constants.FREE_GAME_SETTLE_CLICK_COUNT + 1):  # 連續點擊跳過結算
                                            BrowserHelper.execute_cdp_click(driver, lobby_x, lobby_y)
                                            if click_num < Constants.FREE_GAME_SETTLE_CLICK_COUNT:  # 最後一次不需要等待
                                                time.sleep(Constants.FREE_GAME_SETTLE_CLICK_INTERVAL)  # 點擊間隔
                                        return True
                                    except Exception as e:
                                        self.logger.error(f"瀏覽器 {index} 點擊失敗: {e}")
                                        return False
                                
                                click_results = self.browser_operator.execute_sync(
                                    successful_contexts,
                                    click_lobby_button,
                                    "跳過結算畫面"
                                )
                                click_success = sum(1 for r in click_results if r.success)
                                
                                self.logger.info(f"✓ 已對 {click_success} 個瀏覽器跳過結算畫面")
                                self.logger.info("免費遊戲流程完成")
                            
                        except (EOFError, KeyboardInterrupt):
                            self.logger.info("\n已取消等待")
                        except Exception as e:
                            self.logger.error(f"執行空白鍵時發生錯誤: {e}")
                    
                    self.logger.info("")
                    
                except Exception as e:
                    self.logger.error(f"購買過程發生錯誤: {e}")
            
            elif cmd == 'a':
                # 自動旋轉指令
                if not command_arguments:
                    self.logger.error("指令格式錯誤，請使用: a <次數>")
                    self.logger.info("  a 10   - 自動旋轉 10 次")
                    self.logger.info("  a 50   - 自動旋轉 50 次")
                    self.logger.info("  a 100  - 自動旋轉 100 次")
                    return True
                
                try:
                    # 檢查 Canvas 區域資訊
                    if not hasattr(self.browser_operator, 'last_canvas_rect') or \
                       self.browser_operator.last_canvas_rect is None:
                        self.logger.error("Canvas 區域未初始化，請確保已完成登入流程")
                        return True
                    
                    # 解析次數參數
                    spin_count = int(command_arguments.strip())
                    
                    # 驗證次數是否有效
                    if spin_count not in [10, 50, 100]:
                        self.logger.error(f"無效的次數: {spin_count}，請輸入 10、50 或 100")
                        return True
                    
                    self.logger.info(f"開始設定自動旋轉 {spin_count} 次...")
                    
                    # 取得 Canvas 區域
                    rect = self.browser_operator.last_canvas_rect
                    
                    # 計算第一次點擊座標（自動轉按鈕）
                    auto_x, auto_y = BrowserHelper.calculate_click_position(
                        rect,
                        Constants.AUTO_SPIN_BUTTON_X_RATIO,
                        Constants.AUTO_SPIN_BUTTON_Y_RATIO
                    )
                    
                    # 根據次數選擇第二次點擊座標
                    count_ratio_map = {
                        10: (Constants.AUTO_SPIN_10_X_RATIO, Constants.AUTO_SPIN_10_Y_RATIO),
                        50: (Constants.AUTO_SPIN_50_X_RATIO, Constants.AUTO_SPIN_50_Y_RATIO),
                        100: (Constants.AUTO_SPIN_100_X_RATIO, Constants.AUTO_SPIN_100_Y_RATIO)
                    }
                    x_ratio, y_ratio = count_ratio_map[spin_count]
                    count_x, count_y = BrowserHelper.calculate_click_position(rect, x_ratio, y_ratio)
                    
                    # 使用同步方式對所有瀏覽器執行點擊
                    def auto_spin_operation(context: BrowserContext, index: int, total: int) -> bool:
                        """執行自動旋轉設定"""
                        username = context.credential.username
                        driver = context.driver
                        
                        try:
                            # 第一次點擊（自動轉按鈕）
                            BrowserHelper.execute_cdp_click(driver, auto_x, auto_y)
                            time.sleep(Constants.AUTO_SPIN_MENU_WAIT)  # 等待選單出現
                            
                            # 第二次點擊（選擇次數）
                            BrowserHelper.execute_cdp_click(driver, count_x, count_y)
                            
                            return True
                            
                        except Exception as e:
                            self.logger.error(f"[{username}] 設定自動旋轉失敗: {e}")
                            return False
                    
                    results = self.browser_operator.execute_sync(
                        self.browser_contexts,
                        auto_spin_operation,
                        f"設定自動旋轉 {spin_count} 次"
                    )
                    
                    # 統計結果
                    success_count = sum(1 for r in results if r.success)
                    
                    if success_count == len(self.browser_contexts):
                        self.logger.info(f"✓ 自動旋轉設定完成: 全部 {success_count} 個瀏覽器成功")
                    else:
                        self.logger.warning(
                            f"⚠ 部分完成: {success_count}/{len(self.browser_contexts)} 個瀏覽器成功"
                        )
                        # 顯示失敗的瀏覽器
                        for i, result in enumerate(results, 1):
                            if not result.success:
                                username = self.browser_contexts[i-1].credential.username
                                self.logger.error(f"  瀏覽器 {i} ({username}) 失敗")
                    
                except ValueError:
                    self.logger.error(f"無效的次數: {command_arguments}，請輸入 10、50 或 100")
                except Exception as e:
                    self.logger.error(f"設定自動旋轉時發生錯誤: {e}")
            
            elif cmd == 'c':
                self.logger.info("")
                self.logger.info("=== 截取金額模板工具 ===")
                self.logger.info("請輸入目前遊戲顯示的金額（例: 0.4, 2.4, 10）")
                self.logger.info("按 Enter 鍵退出")
                
                while True:
                    try:
                        print("\n金額: ", end="", flush=True)
                        amount_input = input().strip()
                        
                        # 空白輸入則退出
                        if not amount_input:
                            self.logger.info("退出金額模板工具")
                            break
                        
                        amount = float(amount_input)
                        
                        # 使用 Constants.GAME_BETSIZE 驗證金額
                        if amount not in Constants.GAME_BETSIZE:
                            self.logger.warning(f"⚠ 金額 {amount} 不在標準列表中，但仍會建立模板")
                        
                        # 使用第一個瀏覽器截取
                        if self.browser_contexts:
                            first_context = self.browser_contexts[0]
                            if self.browser_operator.capture_betsize_template(first_context.driver, amount):
                                self.logger.info("✓ 模板截取成功")
                            else:
                                self.logger.error("✗ 模板截取失敗")
                        else:
                            self.logger.error("沒有可用的瀏覽器")
                            break
                            
                    except ValueError:
                        self.logger.error("金額格式錯誤，請輸入有效數字（例如: 0.4）")
                    except EOFError:
                        self.logger.info("退出金額模板工具")
                        break
                    except KeyboardInterrupt:
                        self.logger.info("\n退出金額模板工具")
                        break
                    except Exception as e:
                        self.logger.error(f"截取失敗: {e}")
            
            else:
                self.logger.warning(f"未知指令 {command}")
                self.logger.info("輸入 'h' 查看可用指令")
        
        except Exception as e:
            self.logger.error(f"執行指令時發生錯誤 {e}")
        
        return True
    
    def start(self) -> None:
        """啟動控制中心"""
        self.running = True
        self.logger.info("")
        self.logger.info("━" * 60)
        self.logger.info("遊戲控制中心")
        self.logger.info("━" * 60)
        self.show_help()
        
        try:
            while self.running:
                try:
                    print("\n請輸入指令 > ", end="", flush=True)
                    command = input().strip()
                    if not self.process_command(command):
                        break
                except EOFError:
                    self.logger.info("檢測到 EOF 退出控制中心")
                    break
                except KeyboardInterrupt:
                    self.logger.info("用戶中斷 退出控制中心")
                    break
        finally:
            # 確保停止自動按鍵
            if self.auto_press_running:
                self._stop_auto_press()
            
            self.running = False
            self.logger.info("✓ 控制中心已關閉")
    
    def stop(self) -> None:
        """停止控制中心"""
        self.running = False
        
        # 確保停止自動按鍵
        if self.auto_press_running:
            self._stop_auto_press()


# ============================================================================
# 應用程式類別
# ============================================================================

class AutoSlotGameApp:
    """金富翁遊戲自動化應用程式主類別。
    
    整合所有元件,提供統一的介面。
    """
    
    def __init__(
        self,
        config_reader: Optional[ConfigReader] = None,
        browser_manager: Optional[BrowserManager] = None,
        proxy_manager: Optional[LocalProxyServerManager] = None,
        browser_operator: Optional[SyncBrowserOperator] = None,
        logger: Optional[logging.Logger] = None
    ):
        """初始化應用程式。
        
        Args:
            config_reader: 配置讀取器
            browser_manager: 瀏覽器管理器
            proxy_manager: Proxy 管理器
            browser_operator: 瀏覽器操作器
            logger: 日誌記錄器
        """
        self.logger = logger or LoggerFactory.get_logger()
        self.config_reader = config_reader or ConfigReader(logger=self.logger)
        self.browser_manager = browser_manager or BrowserManager(logger=self.logger)
        self.proxy_manager = proxy_manager or LocalProxyServerManager(logger=self.logger)
        self.browser_operator = browser_operator or SyncBrowserOperator(logger=self.logger)
        
        self.credentials: List[UserCredential] = []
        self.rules: List[BetRule] = []
        self.browser_contexts: List[BrowserContext] = []
        self.image_detector = ImageDetector(logger=self.logger)
        self.recovery_manager: Optional[BrowserRecoveryManager] = None  # 延遲初始化
        self.last_canvas_rect = None  # 儲存 Canvas 區域資訊
    
    def _ensure_recovery_manager(self) -> None:
        """確保 recovery_manager 已初始化。"""
        if self.recovery_manager is None:
            self.recovery_manager = BrowserRecoveryManager(
                self.image_detector,
                self.browser_operator,
                self.logger
            )
    
    def _print_step(self, step: Union[int, str], title: str) -> None:
        """輸出步驟標題。
        
        Args:
            step: 步驟編號（整數或字串）
            title: 步驟標題
        """
        self.logger.info("")
        self.logger.info(f"步驟 {step} {title}")
        self.logger.info("")
    
    def load_configurations(self) -> None:
        """載入所有配置檔案。
        
        Raises:
            ConfigurationError: 配置載入失敗
        """
        self.logger.info("")
        self.logger.info("━" * 60)
        self.logger.info("金富翁遊戲自動化系統 v1.8.0")
        self.logger.info("━" * 60)
        self.logger.info("")
        
        # 讀取使用者憑證（包含 proxy 資訊）
        self.credentials = self.config_reader.read_user_credentials()
        
        # 讀取下注規則
        self.rules = self.config_reader.read_bet_rules()
        
        self.logger.info(
            f"✓ 配置載入完成: {len(self.credentials)} 個帳號, "
            f"{len(self.rules)} 條規則"
        )
    
    def prompt_browser_count(self) -> int:
        """提示使用者輸入要開啟的瀏覽器數量。
        
        Returns:
            瀏覽器數量
        """
        max_browsers = len(self.credentials)
        
        if max_browsers == 0:
            raise ConfigurationError("沒有可用的使用者憑證")
        
        while True:
            try:
                self.logger.info("")
                print(f"\n請輸入要開啟的瀏覽器數量 (1-{max_browsers}): ", end="", flush=True)
                user_input = input().strip()
                browser_count = int(user_input)
                
                if 1 <= browser_count <= max_browsers:
                    self.logger.info(f"將開啟 {browser_count} 個瀏覽器")
                    return browser_count
                else:
                    self.logger.warning(f"請輸入 1 到 {max_browsers} 之間的數字")
                    
            except ValueError:
                self.logger.warning("請輸入有效的數字")
            except (EOFError, KeyboardInterrupt):
                self.logger.warning("使用者取消輸入")
                raise KeyboardInterrupt()
    
    def setup_proxy_servers(self, browser_count: int) -> List[Optional[int]]:
        """設定 Proxy 中繼伺服器（同步啟動）。
        
        Args:
            browser_count: 瀏覽器數量
            
        Returns:
            Proxy 埠號列表
        """
        self._print_step(1, "啟動 Proxy 中繼伺服器")
        proxy_ports: List[Optional[int]] = [None] * browser_count
        
        def start_single_proxy_server(
            index: int,
            credential: UserCredential
        ) -> Tuple[int, Optional[int]]:
            """在執行緒中啟動單個 Proxy 伺服器"""
            local_proxy_port = None
            
            if credential.proxy:
                try:
                    # 解析 proxy 字串
                    parts = credential.proxy.split(':')
                    if len(parts) >= 4:
                        proxy_info = ProxyInfo(
                            host=parts[0],
                            port=int(parts[1]),
                            username=parts[2],
                            password=':'.join(parts[3:])
                        )
                        
                        local_proxy_port = self.proxy_manager.start_proxy_server(proxy_info)
                        
                        if local_proxy_port:
                            pass  # 成功，但不輸出詳細資訊
                        else:
                            self.logger.warning(
                                f"瀏覽器 {index+1}: Proxy 啟動失敗，將直連網路"
                            )
                    else:
                        self.logger.warning(f"瀏覽器 {index+1}: Proxy 格式錯誤")
                        
                except Exception as e:
                    self.logger.error(f"瀏覽器 {index+1}: Proxy 設定失敗 - {e}")
            else:
                # 沒有設定 proxy，將使用直連
                pass  # 不顯示直連訊息
            
            return index, local_proxy_port
        
        # 使用執行緒池同步啟動所有 Proxy 伺服器
        with ThreadPoolExecutor(max_workers=Constants.MAX_THREAD_WORKERS) as executor:
            futures = []
            for i in range(browser_count):
                future = executor.submit(
                    start_single_proxy_server,
                    i,
                    self.credentials[i]
                )
                futures.append(future)
            
            # 收集結果
            for future in as_completed(futures):
                index, local_proxy_port = future.result()
                proxy_ports[index] = local_proxy_port
        
        active_count = sum(1 for p in proxy_ports if p is not None)
        self.logger.info(f"✓ Proxy 伺服器完成: {active_count} 個使用 Proxy, {len(proxy_ports) - active_count} 個直連")
        return proxy_ports
    
    def create_browser_instances(
        self,
        browser_count: int,
        proxy_ports: List[Optional[int]]
    ) -> List[BrowserContext]:
        """建立瀏覽器實例（優化版）。
        
        Args:
            browser_count: 瀏覽器數量
            proxy_ports: Proxy 埠號列表
            
        Returns:
            瀏覽器上下文列表
        """
        self._print_step(2, "建立瀏覽器實例")
        
        browser_results: List[Optional[BrowserContext]] = [None] * browser_count
        
        def create_browser_instance(
            index: int,
            credential: UserCredential,
            proxy_port: Optional[int]
        ) -> Tuple[int, Optional[BrowserContext]]:
            """在執行緒中建立瀏覽器實例"""
            try:
                driver = self.browser_manager.create_webdriver(local_proxy_port=proxy_port)
                
                context = BrowserContext(
                    driver=driver,
                    credential=credential,
                    index=index + 1,
                    proxy_port=proxy_port
                )
                
                return index, context
                
            except Exception as e:
                self.logger.error(f"瀏覽器 {index+1}/{browser_count} 建立失敗: {e}")
                return index, None
        
        # 使用執行緒池建立瀏覽器
        with ThreadPoolExecutor(max_workers=Constants.MAX_THREAD_WORKERS) as executor:
            futures = [
                executor.submit(create_browser_instance, i, self.credentials[i], proxy_ports[i])
                for i in range(browser_count)
            ]
            
            # 收集結果
            for future in as_completed(futures):
                index, context = future.result()
                browser_results[index] = context
        
        # 過濾成功建立的瀏覽器
        contexts = [context for context in browser_results if context is not None]
        
        if len(contexts) == browser_count:
            self.logger.info(f"✓ 瀏覽器建立完成: {len(contexts)} 個")
        else:
            self.logger.warning(f"⚠ 部分失敗: {len(contexts)}/{browser_count} 個成功")
        return contexts
    
    def run(self) -> None:
        """執行主程式流程。
        
        Raises:
            Exception: 執行過程中的錯誤
        """
        try:
            # 載入配置
            self.load_configurations()
            
            # 詢問瀏覽器數量
            browser_count = self.prompt_browser_count()
            
            # 設定 Proxy 伺服器
            proxy_ports = self.setup_proxy_servers(browser_count)
            
            # 建立瀏覽器實例
            self.browser_contexts = self.create_browser_instances(browser_count, proxy_ports)
            
            if not self.browser_contexts:
                raise BrowserCreationError("沒有成功建立任何瀏覽器實例")
            
            # 步驟 3: 導航到登入頁面
            self._print_step(3, "導航到登入頁面")
            login_results = self.browser_operator.navigate_to_login_page(
                self.browser_contexts
            )
            
            time.sleep(Constants.DEFAULT_WAIT_SECONDS)  # 等待頁面載入
            
            # 步驟 4: 執行登入操作（同步）
            self._print_step(4, "執行登入操作")
            login_results = self.browser_operator.perform_login_all(
                self.browser_contexts
            )
            
            # 等待維護公告彈窗出現
            time.sleep(Constants.POPUP_WAIT_TIME)
            
            # 步驟 5: 移除維護公告彈窗
            self._print_step(5, "移除維護公告彈窗")
            self.browser_operator.remove_popup_all(self.browser_contexts)
            
            # 步驟 6: 導航到遊戲分類頁面
            self._print_step(6, "導航到遊戲分類頁面")
            self.browser_operator.navigate_to_game_category(self.browser_contexts)
            time.sleep(Constants.GAME_NAVIGATION_WAIT)
            
            # 步驟 7: 點擊遊戲供應商
            self._print_step(7, "點擊遊戲供應商")
            self.browser_operator.click_game_provider_all(self.browser_contexts)
            time.sleep(Constants.DEFAULT_WAIT_SECONDS)
            
            # 步驟 8: 切換到新分頁
            self._print_step(8, "切換到新分頁")
            self.browser_operator.switch_to_new_tab_all(self.browser_contexts)
            time.sleep(Constants.TAB_SWITCH_WAIT)
            
            # 步驟 9: 點擊開始遊戲
            self._print_step(9, "點擊開始遊戲")
            self.browser_operator.click_start_game_all(self.browser_contexts)
            time.sleep(Constants.DEFAULT_WAIT_SECONDS)
            
            # 步驟 10: 設定視窗大小並啟動監控
            self._print_step(10, f"設定視窗大小 ({Constants.DEFAULT_WINDOW_WIDTH}x{Constants.DEFAULT_WINDOW_HEIGHT})")
            resize_results = self.browser_operator.resize_and_arrange_all(
                self.browser_contexts,
                width=Constants.DEFAULT_WINDOW_WIDTH,
                height=Constants.DEFAULT_WINDOW_HEIGHT
            )
            
            time.sleep(Constants.DEFAULT_WAIT_SECONDS)  # 等待視窗調整完成
            
            # 步驟 11: 圖片檢測與遊戲流程
            self._print_step(11, "圖片檢測與遊戲流程")
            self._execute_image_detection_flow()
            
            # 步驟 12: 啟動遊戲控制中心
            self._print_step(12, "啟動遊戲控制中心")
            control_center = GameControlCenter(
                browser_contexts=self.browser_contexts,
                browser_operator=self.browser_operator,
                bet_rules=self.rules,
                logger=self.logger
            )
            control_center.start()
            
        except KeyboardInterrupt:
            self.logger.warning("使用者中斷程式執行")
        except Exception as e:
            self.logger.error(f"系統發生錯誤 {e}", exc_info=True)
            raise
        finally:
            self.cleanup()
    
    def _execute_image_detection_flow(self) -> None:
        """執行圖片檢測流程。
        
        包含 lobby_login 和 lobby_confirm 的檢測與處理。
        """
        if not self.browser_contexts:
            self.logger.error("沒有可用的瀏覽器實例")
            return
        
        # 使用第一個瀏覽器作為參考
        reference_browser = self.browser_contexts[0]
        
        # 階段 1: 處理 lobby_login
        self.logger.info("檢測 lobby_login...")
        self._handle_lobby_login(reference_browser)
        
        # 階段 2: 處理 lobby_confirm
        self.logger.info("檢測 lobby_confirm...")
        self._handle_lobby_confirm(reference_browser)
        
        self.logger.info("✓ 圖片檢測完成")
    
    def _handle_lobby_image(
        self, 
        reference_browser: BrowserContext, 
        template_name: str, 
        display_name: str
    ) -> None:
        """處理 lobby 圖片的檢測與點擊（通用方法）。
        
        Args:
            reference_browser: 參考瀏覽器
            template_name: 模板檔名
            display_name: 顯示名稱
        """
        # 1. 檢查模板是否存在
        if not self.image_detector.template_exists(template_name):
            self.logger.warning(f"模板圖片 {template_name} 不存在")
            self._prompt_capture_template(reference_browser, template_name, display_name)
        else:
            self.logger.info(f"找到模板圖片 {template_name}")
        
        # 2. 持續檢測直到找到圖片
        self.logger.info(f"正在檢測 {display_name}")
        detection_results = self._continuous_detect_until_found(template_name, display_name)
        
        # 3. 自動執行點擊
        self._auto_click(display_name, detection_results)
        
        # 4. 等待圖片消失
        self._wait_for_image_disappear(template_name)
        self.logger.info(f"{display_name} 已消失")
    
    def _handle_lobby_login(self, reference_browser: BrowserContext) -> None:
        """處理 lobby_login 的檢測與點擊。
        
        Args:
            reference_browser: 參考瀏覽器
        """
        # 1. 檢查模板是否存在
        template_name = Constants.LOBBY_LOGIN
        display_name = "lobby_login"
        
        if not self.image_detector.template_exists(template_name):
            self.logger.warning(f"模板圖片 {template_name} 不存在")
            self._prompt_capture_template(reference_browser, template_name, display_name)
        
        # 2. 持續檢測直到所有瀏覽器都找到圖片
        detection_results = self._continuous_detect_until_found(template_name, display_name)
        
        # 3. 取得 Canvas 區域（使用第一個瀏覽器作為參考）
        try:
            rect = reference_browser.driver.execute_script(f"""
                const canvas = document.getElementById('{Constants.GAME_CANVAS}');
                const r = canvas.getBoundingClientRect();
                return {{x: r.left, y: r.top, w: r.width, h: r.height}};
            """)
            
            # 儲存到實例變數供後續使用
            self.last_canvas_rect = rect
            # 同時儲存到 browser_operator 供 GameControlCenter 使用
            self.browser_operator.last_canvas_rect = rect
        except Exception as e:
            self.logger.error(f"取得 Canvas 座標失敗: {e}")
            raise
        
        # 4. 計算點擊座標（開始遊戲按鈕）
        start_x, start_y = BrowserHelper.calculate_click_position(
            rect,
            Constants.LOBBY_LOGIN_BUTTON_X_RATIO,
            Constants.LOBBY_LOGIN_BUTTON_Y_RATIO
        )
        
        # 5. 在所有瀏覽器中同步執行點擊
        time.sleep(Constants.TEMPLATE_CAPTURE_WAIT)
        def click_start_button_operation(context: BrowserContext, index: int, total: int) -> bool:
            """點擊開始遊戲按鈕"""
            try:
                self._click_coordinate(context.driver, start_x, start_y)
                return True
            except Exception as e:
                self.logger.error(f"點擊失敗: {e}")
                return False
        
        click_results = self.browser_operator.execute_sync(
            self.browser_contexts,
            click_start_button_operation,
            "點擊開始遊戲按鈕"
        )
        
        # 6. 等待所有瀏覽器中的圖片消失
        self._wait_for_image_disappear(template_name)
    
    def _handle_lobby_confirm(self, reference_browser: BrowserContext) -> None:
        """處理 lobby_confirm 的檢測與點擊，包含錯誤訊息檢測和自動重啟。
        
        Args:
            reference_browser: 參考瀏覽器
        """
        # 1. 檢查模板是否存在
        template_name = Constants.LOBBY_CONFIRM
        display_name = "lobby_confirm"
        
        if not self.image_detector.template_exists(template_name):
            # 如果沒有模板，嘗試使用確認按鈕座標自動建立
            if hasattr(self, 'last_canvas_rect') and self.last_canvas_rect:
                self._auto_capture_lobby_confirm(reference_browser)
            else:
                self._prompt_capture_template(reference_browser, template_name, display_name)
        
        # 2. 持續檢測直到所有瀏覽器都找到圖片（包含錯誤處理）
        self._wait_for_lobby_confirm_with_error_handling()
        
        # 3. 計算點擊座標（確認按鈕）
        if hasattr(self, 'last_canvas_rect') and self.last_canvas_rect:
            rect = self.last_canvas_rect
            confirm_x, confirm_y = BrowserHelper.calculate_click_position(
                rect,
                Constants.LOBBY_CONFIRM_BUTTON_X_RATIO,
                Constants.LOBBY_CONFIRM_BUTTON_Y_RATIO
            )
            
            # 4. 在所有瀏覽器中同步執行點擊
            time.sleep(Constants.TEMPLATE_CAPTURE_WAIT)
            def click_confirm_button_operation(context: BrowserContext, index: int, total: int) -> bool:
                """點擊確認按鈕"""
                try:
                    self._click_coordinate(context.driver, confirm_x, confirm_y)
                    return True
                except Exception as e:
                    self.logger.error(f"點擊失敗: {e}")
                    return False
            
            click_results = self.browser_operator.execute_sync(
                self.browser_contexts,
                click_confirm_button_operation,
                "點擊確認按鈕"
            )
        else:
            self.logger.warning("未找到 Canvas 座標，跳過自動點擊")
        
        # 5. 所有瀏覽器都成功進入遊戲
        self.logger.info("✓ 所有瀏覽器已準備就緒")
        time.sleep(Constants.DETECTION_COMPLETE_WAIT)
    
    def _wait_for_lobby_confirm_with_error_handling(self) -> None:
        """等待 lobby_confirm 出現，包含錯誤訊息檢測和自動重啟邏輯（同步版本）。
        
        流程：
        1. 同步檢測所有瀏覽器的 lobby_confirm（前 3 次）
        2. 如果未找到，同步檢測錯誤訊息
        3. 如果檢測到錯誤且持續超過設定秒數，同步重啟所有錯誤的瀏覽器
        4. 重複直到所有瀏覽器都顯示 lobby_confirm
        """
        self._ensure_recovery_manager()  # 確保 recovery_manager 已初始化
        
        template_name = Constants.LOBBY_CONFIRM
        total_browsers = len(self.browser_contexts)
        browser_states = {}  # 記錄每個瀏覽器的狀態
        
        # 初始化瀏覽器狀態
        for i in range(1, total_browsers + 1):
            browser_states[i] = {
                'found_confirm': False,
                'error_start_time': None,
                'lobby_confirm_attempts': 0
            }
        
        self.logger.info("開始檢測 lobby_confirm（包含錯誤訊息監控）")
        last_progress = -1
        
        while True:
            # 同步檢測所有待處理的瀏覽器
            pending_browsers = [
                i for i in range(1, total_browsers + 1)
                if not browser_states[i]['found_confirm']
            ]
            
            if not pending_browsers:
                self.logger.info("✓ 所有瀏覽器都已檢測到 lobby_confirm")
                break
            
            # 檢測 lobby_confirm 和錯誤訊息
            current_time = time.time()
            errors_to_restart = []
            new_errors = []
            
            for i in pending_browsers:
                context = self.browser_contexts[i - 1]
                browser_states[i]['lobby_confirm_attempts'] += 1
                
                try:
                    # 檢測 lobby_confirm
                    result = self.image_detector.detect_in_browser(
                        context.driver,
                        template_name
                    )
                    
                    if result:
                        # 找到 lobby_confirm
                        browser_states[i]['found_confirm'] = True
                        browser_states[i]['error_start_time'] = None
                        continue
                    
                    # 前幾次不檢查錯誤訊息
                    if browser_states[i]['lobby_confirm_attempts'] <= Constants.LOBBY_CONFIRM_CHECK_ATTEMPTS:
                        continue
                    
                    # 檢測錯誤訊息
                    has_error = self.recovery_manager.detect_error_message(context.driver)
                    
                    if has_error:
                        if browser_states[i]['error_start_time'] is None:
                            # 第一次檢測到錯誤
                            browser_states[i]['error_start_time'] = current_time
                            new_errors.append(i)
                        else:
                            # 持續檢測到錯誤
                            elapsed = current_time - browser_states[i]['error_start_time']
                            if elapsed >= Constants.ERROR_MESSAGE_PERSIST_SECONDS:
                                errors_to_restart.append(i)
                    else:
                        # 未檢測到錯誤，重置計時
                        if browser_states[i]['error_start_time'] is not None:
                            browser_states[i]['error_start_time'] = None
                
                except Exception as e:
                    self.logger.error(f"瀏覽器 {i} 檢測過程發生錯誤: {e}")
            
            # 輸出新檢測到的錯誤
            if new_errors:
                self.logger.warning(f"檢測到錯誤訊息: 瀏覽器 {', '.join(map(str, new_errors))}")
            
            # 同步重啟所有需要重啟的瀏覽器
            if errors_to_restart:
                self.logger.error(f"執行重啟: 瀏覽器 {', '.join(map(str, errors_to_restart))}")
                self._restart_browsers_simple(errors_to_restart, browser_states)
            
            # 顯示進度（只在變化時輸出）
            found_count = sum(1 for state in browser_states.values() if state['found_confirm'])
            if found_count != last_progress:
                if found_count > 0:
                    self.logger.info(f"進度: {found_count}/{total_browsers} 個瀏覽器已就緒")
                last_progress = found_count
            
            time.sleep(Constants.DETECTION_INTERVAL)
    
    def _restart_browsers_simple(
        self,
        browser_indices: List[int],
        browser_states: dict
    ) -> None:
        """簡化的瀏覽器重啟流程。
        
        Args:
            browser_indices: 需要重啟的瀏覽器索引列表
            browser_states: 瀏覽器狀態字典
        """
        if not browser_indices or not self.last_canvas_rect:
            return
        
        self._ensure_recovery_manager()
        
        # 準備需要重啟的瀏覽器上下文
        contexts_to_restart = [
            self.browser_contexts[i - 1]
            for i in browser_indices
        ]
        
        # 使用 recovery_manager 執行重啟和恢復
        success = self.recovery_manager.restart_and_recover(
            contexts_to_restart,
            self.last_canvas_rect
        )
        
        if success:
            # 重置狀態
            for i in browser_indices:
                browser_states[i]['error_start_time'] = None
                browser_states[i]['lobby_confirm_attempts'] = 0
            
            browser_list = ', '.join(map(str, browser_indices))
            self.logger.info(f"✓ 瀏覽器 {browser_list} 已重啟並等待 lobby_confirm")
        else:
            self.logger.error("瀏覽器重啟失敗")
    
    def _click_coordinate(self, driver: WebDriver, x: float, y: float) -> None:
        """點擊指定座標。
        
        Args:
            driver: WebDriver 實例
            x: X座標
            y: Y座標
        """
        BrowserHelper.execute_cdp_click(driver, x, y)
    
    def _auto_capture_lobby_confirm(self, reference_browser: BrowserContext) -> None:
        """自動截取 lobby_confirm 模板圖片。
        
        使用已知的確認按鈕座標自動截取模板。
        
        Args:
            reference_browser: 參考瀏覽器
        """
        try:
            # 取得確認按鈕座標
            rect = self.last_canvas_rect
            confirm_x = rect["x"] + rect["w"] * Constants.LOBBY_CONFIRM_BUTTON_X_RATIO
            confirm_y = rect["y"] + rect["h"] * Constants.LOBBY_CONFIRM_BUTTON_Y_RATIO
            
            # 截取畫面
            screenshot = reference_browser.driver.get_screenshot_as_png()
            screenshot_img = Image.open(io.BytesIO(screenshot))
            
            # 獲取實際截圖尺寸
            image_width, image_height = screenshot_img.size
            
            center_x = int(confirm_x)
            center_y = int(confirm_y)
            
            # 固定像素偏移（使用常數定義）
            crop_left = max(0, center_x - Constants.TEMPLATE_CROP_MARGIN)
            crop_top = max(0, center_y - Constants.TEMPLATE_CROP_MARGIN)
            crop_right = min(image_width, center_x + Constants.TEMPLATE_CROP_MARGIN)
            crop_bottom = min(image_height, center_y + Constants.TEMPLATE_CROP_MARGIN)
            
            cropped_img = screenshot_img.crop((crop_left, crop_top, crop_right, crop_bottom))
            
            # 儲存圖片
            template_path = self.image_detector.get_template_path(Constants.LOBBY_CONFIRM)
            template_path.parent.mkdir(parents=True, exist_ok=True)
            cropped_img.save(template_path)
            
            self.logger.info("✓ 模板建立成功")
            
        except Exception as e:
            self.logger.error(f"自動建立 lobby_confirm.png 失敗: {e}")
            raise
    
    def _prompt_capture_template(self, reference_browser: BrowserContext, template_name: str, display_name: str) -> None:
        """提示用戶截取模板圖片。
        
        Args:
            reference_browser: 參考瀏覽器
            template_name: 模板檔名
            display_name: 顯示名稱
        """
        self.logger.info(f"請準備截取 {display_name} 的參考圖片")
        print(f"按 Enter 鍵截取第一個瀏覽器的畫面作為 {display_name} 模板", end="", flush=True)
        
        try:
            input()
            
            # 截取並儲存模板
            template_path = self.image_detector.get_template_path(template_name)
            self.image_detector.capture_screenshot(reference_browser.driver, template_path)
            self.logger.info(f"模板圖片已建立 路徑 {template_path}")
            
        except (EOFError, KeyboardInterrupt):
            self.logger.warning("用戶取消截圖")
            raise
    
    def _handle_image_not_found(self, reference_browser: BrowserContext, template_name: str, display_name: str) -> None:
        """處理圖片未檢測到的情況，提供選項讓用戶重新截圖或跳過。
        
        Args:
            reference_browser: 參考瀏覽器
            template_name: 模板檔名
            display_name: 顯示名稱
        """
        self.logger.info("當前模板圖片可能與實際畫面不符")
        self.logger.info("選項")
        self.logger.info(f"  1 重新截取 {display_name} 模板圖片")
        self.logger.info("  2 等待並重新檢測")
        self.logger.info("  3 跳過此階段")
        
        while True:
            try:
                print(f"\n請選擇 (1/2/3): ", end="", flush=True)
                choice = input().strip()
                
                if choice == "1":
                    # 重新截取模板
                    self.logger.info(f"準備重新截取 {display_name} 模板")
                    self._prompt_capture_template(reference_browser, template_name, display_name)
                    
                    # 重新檢測
                    self.logger.info("使用新模板重新檢測")
                    detection_results = self._detect_in_all_browsers(template_name)
                    found_count = sum(1 for result in detection_results if result is not None)
                    
                    if found_count > 0:
                        self.logger.info(f"檢測到 {found_count}/{len(self.browser_contexts)} 個瀏覽器中有 {display_name}")
                        self._prompt_user_click(display_name, detection_results)
                        self.logger.info(f"等待 {display_name} 消失")
                        self._wait_for_image_disappear(template_name)
                        self.logger.info(f"{display_name} 已消失")
                        return
                    else:
                        self.logger.warning(f"仍未檢測到 {display_name} 請重新選擇")
                        continue
                
                elif choice == "2":
                    # 等待並重新檢測
                    self.logger.info(f"等待 {display_name} 出現")
                    self.logger.info("持續檢測中 每3秒檢測一次 按 Ctrl+C 可中斷")
                    
                    try:
                        for attempt in range(Constants.DETECTION_WAIT_MAX_ATTEMPTS):
                            time.sleep(Constants.DEFAULT_WAIT_SECONDS)
                            detection_results = self._detect_in_all_browsers(template_name)
                            found_count = sum(1 for result in detection_results if result is not None)
                            
                            if found_count > 0:
                                self.logger.info(f"檢測到 {found_count}/{len(self.browser_contexts)} 個瀏覽器中有 {display_name}")
                                self._prompt_user_click(display_name, detection_results)
                                self.logger.info(f"等待 {display_name} 消失")
                                self._wait_for_image_disappear(template_name)
                                self.logger.info(f"{display_name} 已消失")
                                return
                            
                            if (attempt + 1) % 5 == 0:
                                self.logger.info(f"檢測進度 {attempt + 1}/{Constants.DETECTION_WAIT_MAX_ATTEMPTS} 次 仍未找到")
                        
                        self.logger.warning(f"等待超時 未檢測到 {display_name}")
                        continue
                        
                    except KeyboardInterrupt:
                        self.logger.info("用戶中斷等待")
                        continue
                
                elif choice == "3":
                    # 跳過此階段
                    self.logger.info("已跳過該階段")
                    return
                
                else:
                    self.logger.warning("無效的選擇 請輸入 1 2 或 3")
                    continue
                    
            except (EOFError, KeyboardInterrupt):
                self.logger.warning("用戶中斷操作")
                raise
    
    def _continuous_detect_until_found(self, template_name: str, display_name: str) -> List[Optional[Tuple[int, int, float]]]:
        """持續檢測直到在所有瀏覽器中找到圖片。
        
        Args:
            template_name: 模板圖片檔名
            display_name: 顯示名稱
            
        Returns:
            檢測結果列表 (每個元素為 None 或 (x, y, confidence))
        """
        attempt = 0
        total_browsers = len(self.browser_contexts)
        
        while True:
            attempt += 1
            detection_results = self._detect_in_all_browsers(template_name, silent=True)
            found_count = sum(1 for result in detection_results if result is not None)
            
            # 只有當所有瀏覽器都找到圖片時才返回
            if found_count == total_browsers:
                # 顯示最終找到的座標
                self.logger.info(f"✓ 所有瀏覽器都已檢測到 {display_name}")
                return detection_results
            
            # 每 N 次檢測顯示一次進度
            if attempt % Constants.DETECTION_PROGRESS_INTERVAL == 0:
                self.logger.info(f"檢測中... ({found_count}/{total_browsers})")
            
            time.sleep(Constants.DETECTION_INTERVAL)
    
    def _detect_in_all_browsers(self, template_name: str, silent: bool = False) -> List[Optional[Tuple[int, int, float]]]:
        """在所有瀏覽器中檢測模板圖片。
        
        Args:
            template_name: 模板圖片檔名
            silent: 是否靜默模式(不輸出log)
            
        Returns:
            檢測結果列表 (每個元素為 None 或 (x, y, confidence))
        """
        results: List[Optional[Tuple[int, int, float]]] = []
        
        for i, context in enumerate(self.browser_contexts, 1):
            try:
                result = self.image_detector.detect_in_browser(
                    context.driver,
                    template_name
                )
                
                if result and not silent:
                    x, y, confidence = result
                    self.logger.info(f"瀏覽器 {i}/{len(self.browser_contexts)} 找到圖片 座標 {x} {y} 信心度 {confidence:.2f}")
                
                results.append(result)
                
            except ImageDetectionError as e:
                if not silent:
                    self.logger.error(f"瀏覽器 {i}/{len(self.browser_contexts)} 圖片檢測錯誤: {e}")
                results.append(None)
            except Exception as e:
                if not silent:
                    self.logger.error(f"瀏覽器 {i}/{len(self.browser_contexts)} 未預期錯誤: {e}")
                results.append(None)
        
        return results
    
    def _auto_click(self, display_name: str, detection_results: List[Optional[Tuple[int, int, float]]]) -> None:
        """自動執行點擊操作。
        
        Args:
            display_name: 顯示名稱
            detection_results: 檢測結果列表
        """
        self.logger.info(f"找到 {display_name}，自動執行點擊操作")
        
        def click_operation(context: BrowserContext, index: int, total: int) -> bool:
            """在單個瀏覽器中執行點擊操作"""
            result = detection_results[index - 1]
            if result is None:
                return False
            
            x, y, confidence = result
            
            try:
                BrowserHelper.execute_cdp_click(context.driver, x, y)
                self.logger.debug(f"瀏覽器 {index} 在座標 ({x}, {y}) 執行點擊成功")
                return True
            except Exception as e:
                self.logger.error(f"瀏覽器 {index} 點擊失敗: {e}")
                return False
        
        # 同步執行所有點擊
        self.browser_operator.execute_sync(
            self.browser_contexts,
            click_operation,
            f"點擊 {display_name}"
        )
    
    def _wait_for_image_disappear(self, template_name: str) -> None:
        """持續等待圖片在所有瀏覽器中消失。
        
        Args:
            template_name: 模板圖片檔名
        """
        attempt = 0
        total_browsers = len(self.browser_contexts)
        
        while True:
            attempt += 1
            
            # 檢測所有瀏覽器
            still_present = []
            for i, context in enumerate(self.browser_contexts, 1):
                try:
                    result = self.image_detector.detect_in_browser(
                        context.driver,
                        template_name
                    )
                    if result:
                        still_present.append(i)
                except Exception as e:
                    self.logger.debug(f"瀏覽器 {i} 檢測失敗 {e}")
            
            disappeared_count = total_browsers - len(still_present)
            
            # 如果所有瀏覽器都沒有找到圖片，則返回
            if not still_present:
                self.logger.info(f"✓ 圖片已消失")
                return
            
            # 每 10 次檢測顯示一次進度
            if attempt % 10 == 0:
                self.logger.info(f"等待中... ({disappeared_count}/{total_browsers} 已消失)")
            
            # 等待後再次檢測
            time.sleep(Constants.DETECTION_INTERVAL)
    
    def cleanup(self) -> None:
        """清理所有資源（優化版）"""
        self.logger.info("正在清理資源...")
        
        # 1. 關閉所有瀏覽器
        if self.browser_contexts:
            try:
                self.browser_operator.close_all(self.browser_contexts)
            except Exception as e:
                self.logger.error(f"關閉瀏覽器時發生錯誤: {e}")
            finally:
                self.browser_contexts.clear()
        
        # 2. 停止所有 Proxy 伺服器
        try:
            self.proxy_manager.stop_all_servers()
        except Exception as e:
            self.logger.error(f"停止 Proxy 伺服器時發生錯誤: {e}")
        
        self.logger.info("✓ 清理完成")


# ============================================================================
# 主程式入口
# ============================================================================

def main() -> None:
    """主程式入口函式。
    
    初始化並執行應用程式。
    """
    logger = LoggerFactory.get_logger()
    
    # 在程式啟動前清除所有緩存的 chromedriver 程序
    cleanup_chromedriver_processes()
    
    try:
        app = AutoSlotGameApp()
        app.run()
    except KeyboardInterrupt:
        logger.warning("使用者中斷程式執行")
        sys.exit(0)
    except ConfigurationError as e:
        logger.critical(f"配置錯誤: {e}")
        sys.exit(1)
    except BrowserCreationError as e:
        logger.critical(f"瀏覽器建立失敗: {e}")
        sys.exit(1)
    except ProxyServerError as e:
        logger.critical(f"Proxy 伺服器錯誤: {e}")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"應用程式執行失敗: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
