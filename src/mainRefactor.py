"""
金富翁遊戲自動化系統 - 重構版本

採用最佳實踐重構:
- 完整型別提示
- 上下文管理器
- 依賴注入
- 錯誤處理
- 資源管理
- 執行緒安全
- 可測試性

作者: 凡臻科技
版本: 4.0.0
Python: 3.8+
"""

import logging
import sys
import platform
import socket
import select
import base64
import time
import random
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
    # 主要類別
    'ConfigReader',
    'BrowserManager',
    'LocalProxyServerManager',
    'SyncBrowserOperator',
    'ImageDetector',
    'GameControlCenter',
    'AutoSlotGameApp',
]


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
    LOGIN_PAGE = "https://m.jfw-win.com/#/login?redirect=%2Fhome%2Fpage"
    GAME_PAGE = "https://m.jfw-win.com/#/home/loding?game_code=egyptian-mythology&factory_code=ATG&state=true&name=%E6%88%B0%E7%A5%9E%E8%B3%BD%E7%89%B9"
    
    # 頁面元素選擇器
    USERNAME_INPUT = "//input[@placeholder='請輸入帳號']"
    PASSWORD_INPUT = "//input[@placeholder='請輸入密碼']"
    LOGIN_BUTTON = "//div[contains(@class, 'login-btn')]//span[text()='立即登入']/.."
    GAME_IFRAME = "gameFrame-0"
    GAME_CANVAS = "GameCanvas"
    
    # 圖片檢測配置
    IMAGE_DIR = "img"
    LOBBY_LOGIN = "lobby_login.png"
    LOBBY_CONFIRM = "lobby_confirm.png"
    MATCH_THRESHOLD = 0.8  # 圖片匹配閾值
    DETECTION_INTERVAL = 1.0  # 檢測間隔（秒）
    MAX_DETECTION_ATTEMPTS = 60  # 最大檢測次數
    
    # Canvas 動態計算比例（用於點擊座標）
    START_GAME_X_RATIO = 0.55  # 開始遊戲按鈕 X 座標比例
    START_GAME_Y_RATIO = 1.2   # 開始遊戲按鈕 Y 座標比例
    MACHINE_CONFIRM_X_RATIO = 0.78  # 確認按鈕 X 座標比例
    MACHINE_CONFIRM_Y_RATIO = 1.15  # 確認按鈕 Y 座標比例
    FREE_GAME_X_RATIO = 0.25  # 免費遊戲按鈕 X 座標比例
    FREE_GAME_Y_RATIO = 0.5   # 免費遊戲按鈕 Y 座標比例
    
    # 操作相關常量
    DEFAULT_WAIT_SECONDS = 3  # 預設等待時間（秒）
    MAX_WAIT_ATTEMPTS = 20  # 最大等待嘗試次數
    DETECTION_PROGRESS_INTERVAL = 20  # 檢測進度顯示間隔
    
    # 視窗排列配置
    DEFAULT_WINDOW_WIDTH = 600
    DEFAULT_WINDOW_HEIGHT = 400
    DEFAULT_WINDOW_COLUMNS = 4


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
    
    def __post_init__(self) -> None:
        """驗證資料完整性"""
        if self.amount <= 0:
            raise ValueError(f"下注金額必須大於 0: {self.amount}")
        if self.duration <= 0:
            raise ValueError(f"持續時間必須大於 0: {self.duration}")


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
        return f"http://{self.username}:{self.password}@{self.host}:{self.port}"
    
    def to_connection_string(self) -> str:
        """轉換為連接字串格式。
        
        Returns:
            格式化的連接字串 "host:port:username:password"
        """
        return f"{self.host}:{self.port}:{self.username}:{self.password}"
    
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
    def age_seconds(self) -> float:
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
    """Logger 工廠類別"""
    
    _loggers: Dict[str, logging.Logger] = {}
    _lock = threading.Lock()
    
    @classmethod
    def get_logger(
        cls, 
        name: str = "AutoSlotGame",
        level: LogLevel = LogLevel.INFO
    ) -> logging.Logger:
        """取得或建立 logger 實例。
        
        Args:
            name: Logger 名稱
            level: 日誌等級
            
        Returns:
            配置完成的 Logger 物件
        """
        with cls._lock:
            if name in cls._loggers:
                return cls._loggers[name]
            
            logger = logging.getLogger(name)
            logger.setLevel(level.value)
            logger.propagate = False
            
            # 避免重複添加 handler
            if not logger.handlers:
                # 控制台 handler (帶顏色)
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setLevel(level.value)
                console_handler.setFormatter(ColoredFormatter())
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
            # 預設使用專案根目錄下的 lib 資料夾
            project_root = Path(__file__).parent.parent
            lib_path = project_root / Constants.DEFAULT_LIB_PATH
        
        self.lib_path = Path(lib_path)
        self.logger = logger or LoggerFactory.get_logger()
        
        # 驗證目錄存在
        if not self.lib_path.exists():
            raise ConfigurationError(f"配置目錄不存在: {self.lib_path}")
    
    def _read_file_lines(self, filename: str, skip_header: bool = True) -> List[str]:
        """讀取檔案並返回有效行列表。
        
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
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 跳過標題行
            start_index = 1 if skip_header and lines else 0
            
            # 過濾空行和註釋
            valid_lines = []
            for line in lines[start_index:]:
                line = line.strip()
                if line and not line.startswith('#'):
                    valid_lines.append(line)
            
            return valid_lines
            
        except Exception as e:
            raise ConfigurationError(f"讀取檔案失敗 {filename}: {e}") from e
    
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
        
        for line_num, line in enumerate(lines, start=2):  # +2 因為跳過標題
            try:
                parts = [p.strip() for p in line.split(',')]
                
                if len(parts) < 2:
                    self.logger.warning(f"第 {line_num} 行格式不完整 已跳過 {line}")
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
                self.logger.warning(f"第 {line_num} 行資料無效 {e}")
                continue
        
        self.logger.info(f"成功讀取 {len(credentials)} 筆使用者憑證")
        return credentials
    
    def read_bet_rules(
        self, 
        filename: str = Constants.DEFAULT_RULES_FILE
    ) -> List[BetRule]:
        """讀取下注規則檔案。
        
        檔案格式: 金額:時間(分鐘) (首行為標題)
        
        Args:
            filename: 檔案名稱
            
        Returns:
            下注規則列表
            
        Raises:
            ConfigurationError: 讀取或解析失敗
        """
        rules = []
        lines = self._read_file_lines(filename, skip_header=True)
        
        for line_num, line in enumerate(lines, start=2):
            try:
                parts = line.split(':')
                
                if len(parts) < 2:
                    self.logger.warning(f"第 {line_num} 行格式不完整 已跳過 {line}")
                    continue
                
                amount = float(parts[0].strip())
                duration = int(parts[1].strip())
                
                rules.append(BetRule(amount=amount, duration=duration))
                
            except (ValueError, IndexError) as e:
                self.logger.warning(f"第 {line_num} 行無法解析 {e}")
                continue
        
        self.logger.info(f"成功讀取 {len(rules)} 條下注規則")
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
        self.upstream = upstream_proxy
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
            upstream_socket.connect((self.upstream.host, self.upstream.port))
            
            # 構建帶認證的 CONNECT 請求
            auth_string = f"{self.upstream.username}:{self.upstream.password}"
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
            auth_string = f"{self.upstream.username}:{self.upstream.password}"
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
            upstream_socket.connect((self.upstream.host, self.upstream.port))
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
            self.logger.debug(f"Proxy 伺服器監聽於 {Constants.PROXY_SERVER_BIND_HOST}:{self.local_port}")
            
            while self.running:
                try:
                    self.server_socket.settimeout(1.0)
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
            time.sleep(1)
            
            self.logger.info(
                f"啟動本機 Proxy 中繼: {Constants.PROXY_SERVER_BIND_HOST}:{local_port} "
                f"-> {upstream_proxy.host}:{upstream_proxy.port}"
            )
            return local_port
            
        except Exception as e:
            self.logger.error(f"啟動本機 Proxy 伺服器失敗 {e}")
            return None
    
    def stop_proxy_server(self, local_port: int) -> None:
        """停止指定的 proxy 伺服器。
        
        Args:
            local_port: 本機埠號
        """
        # 先從字典中取出 server
        with self._lock:
            server = self._proxy_servers.get(local_port)
        
        # 在鎖外執行耗時操作
        if server:
            server.stop()
            self.logger.debug(f"已停止 Proxy 伺服器: 埠 {local_port}")
            
            # 再次加鎖從字典中刪除
            with self._lock:
                if local_port in self._proxy_servers:
                    del self._proxy_servers[local_port]
                if local_port in self._proxy_threads:
                    del self._proxy_threads[local_port]
    
    def stop_all_servers(self) -> None:
        """停止所有 proxy 伺服器"""
        ports = []
        with self._lock:
            if self._proxy_servers:
                # 複製鍵列表以避免在迭代時修改字典
                ports = list(self._proxy_servers.keys())
        
        # 在鎖外停止伺服器
        for local_port in ports:
            self.stop_proxy_server(local_port)
    
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
            logger.info(f"已設定本機 Proxy 中繼 {proxy_address}")
        
        # 基本設定
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        
        # 背景執行優化設定
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-ipc-flooding-protection")
        
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
        })
        
        return chrome_options
    
    def create_webdriver(
        self, 
        local_proxy_port: Optional[int] = None
    ) -> WebDriver:
        """建立 WebDriver 實例。
        
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
            self.logger.info("正在使用專案內驅動程式")
            driver = self._create_webdriver_with_local_driver(chrome_options)
            
            # 取得 Chrome 版本
            with suppress(Exception):
                chrome_version = driver.capabilities.get('browserVersion', 'unknown')
                self.logger.info(f"Chrome 版本 {chrome_version}")
            
            self.logger.info("瀏覽器實例已建立 使用本機驅動程式")
            
        except Exception as e:
            errors.append(f"本機驅動程式: {e}")
            self.logger.warning(f"本機驅動程式失敗 {e}")
            self.logger.info("嘗試使用 WebDriver Manager 作為備援")
            
            # 方法 2: 使用 WebDriver Manager 自動管理
            try:
                self.logger.info("正在使用 WebDriver Manager 取得 ChromeDriver")
                service = Service(ChromeDriverManager().install())
                self.logger.info("正在啟動 Chrome 瀏覽器")
                driver = webdriver.Chrome(service=service, options=chrome_options)
                
                # 取得 Chrome 版本
                with suppress(Exception):
                    chrome_version = driver.capabilities.get('browserVersion', 'unknown')
                    self.logger.info(f"Chrome 版本 {chrome_version}")
                
                self.logger.info("瀏覽器實例已建立 使用 WebDriver Manager")
                
            except Exception as e2:
                errors.append(f"WebDriver Manager: {e2}")
                self.logger.error(f"WebDriver Manager 也失敗 {e2}")
        
        if driver is None:
            error_msg = "無法建立瀏覽器實例。\n" + "\n".join(f"- {err}" for err in errors)
            raise BrowserCreationError(error_msg)
        
        # 設定超時
        try:
            driver.set_page_load_timeout(Constants.DEFAULT_PAGE_LOAD_TIMEOUT)
            driver.set_script_timeout(Constants.DEFAULT_SCRIPT_TIMEOUT)
            driver.implicitly_wait(Constants.DEFAULT_IMPLICIT_WAIT)
        except Exception as e:
            self.logger.warning(f"設定超時參數失敗 {e}")
        
        # 網路優化
        try:
            driver.execute_cdp_cmd("Network.enable", {})
            driver.execute_cdp_cmd("Network.emulateNetworkConditions", {
                "offline": False,
                "downloadThroughput": -1,
                "uploadThroughput": -1,
                "latency": 0
            })
        except Exception as e:
            self.logger.warning(f"網路優化設定失敗 {e}")
        
        self.logger.info("瀏覽器設定完成")
        return driver
    
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
        # 取得專案根目錄
        if getattr(sys, 'frozen', False):
            project_root = Path(sys.executable).resolve().parent
        else:
            project_root = Path(__file__).resolve().parent.parent
        
        # 根據作業系統選擇驅動程式
        system = platform.system().lower()
        driver_filename = "chromedriver.exe" if system == "windows" else "chromedriver"
        
        driver_path = project_root / driver_filename
        
        if not driver_path.exists():
            raise FileNotFoundError(
                f"找不到驅動程式檔案: {driver_path}\n"
                f"請確保 {driver_filename} 存在於專案根目錄"
            )
        
        self.logger.info(f"使用本機驅動程式 {driver_path}")
        
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
    
    def execute_sync(
        self,
        browser_contexts: List[BrowserContext],
        operation_func: Callable[[BrowserContext, int, int], Any],
        operation_name: str,
        timeout: Optional[float] = None
    ) -> List[OperationResult]:
        """同步執行操作到所有瀏覽器。
        
        Args:
            browser_contexts: 瀏覽器上下文列表
            operation_func: 操作函式,接受參數 (context, index, total)
            operation_name: 操作名稱(用於日誌)
            timeout: 超時時間（秒）
            
        Returns:
            所有操作的結果列表
        """
        # 不在這裡輸出標題,由調用方決定是否需要
        
        total = len(browser_contexts)
        results: List[OperationResult] = [OperationResult(False)] * total
        
        def execute_operation(index: int, context: BrowserContext) -> Tuple[int, OperationResult]:
            """在執行緒中執行操作"""
            try:
                self.logger.info(
                    f"瀏覽器 {index+1}/{total} 開始 {operation_name} "
                    f"帳號 {context.credential.username}"
                )
                
                result_data = operation_func(context, index + 1, total)
                result = OperationResult(
                    success=True,
                    data=result_data,
                    message=f"{operation_name} 成功"
                )
                
                self.logger.info(f"瀏覽器 {index+1}/{total} {operation_name} 完成")
                return index, result
                
            except Exception as e:
                self.logger.error(f"瀏覽器 {index+1}/{total} {operation_name} 失敗 {e}")
                result = OperationResult(
                    success=False,
                    error=e,
                    message=str(e)
                )
                return index, result
        
        # 使用執行緒池執行
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任務
            futures: Dict[Future, int] = {}
            for i, context in enumerate(browser_contexts):
                future = executor.submit(execute_operation, i, context)
                futures[future] = i
            
            # 收集結果
            try:
                for future in as_completed(futures, timeout=timeout):
                    index, result = future.result()
                    results[index] = result
            except TimeoutError:
                self.logger.error(f"{operation_name} 執行超時")
        
        success_count = sum(1 for r in results if r.success)
        if success_count == total:
            self.logger.info(f"{operation_name} 完成 {success_count}/{total}")
        else:
            self.logger.warning(f"{operation_name} 部分完成 {success_count}/{total}")
        
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
    
    def navigate_to_game_page(
        self,
        browser_contexts: List[BrowserContext],
        timeout: Optional[float] = None
    ) -> List[OperationResult]:
        """同步導航所有瀏覽器到遊戲頁面。
        
        Args:
            browser_contexts: 瀏覽器上下文列表
            timeout: 超時時間
            
        Returns:
            操作結果列表
        """
        return self.navigate_all(browser_contexts, Constants.GAME_PAGE, timeout)
    
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
            
            time.sleep(5)  # 等待登入完成
            return True
        
        return self.execute_sync(
            browser_contexts,
            login_operation,
            "登入操作",
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
            # 按下空白鍵
            context.driver.execute_cdp_cmd("Input.dispatchKeyEvent", {
                "type": "keyDown",
                "key": " ",
                "code": "Space",
                "windowsVirtualKeyCode": 32,
                "nativeVirtualKeyCode": 32
            })
            # 釋放空白鍵
            context.driver.execute_cdp_cmd("Input.dispatchKeyEvent", {
                "type": "keyUp",
                "key": " ",
                "code": "Space",
                "windowsVirtualKeyCode": 32,
                "nativeVirtualKeyCode": 32
            })
            return True
        
        return self.execute_sync(
            browser_contexts,
            press_space_operation,
            "按下空白鍵",
            timeout=timeout
        )
    
    def resize_and_arrange_all(
        self,
        browser_contexts: List[BrowserContext],
        width: int = Constants.DEFAULT_WINDOW_WIDTH,
        height: int = Constants.DEFAULT_WINDOW_HEIGHT,
        columns: int = Constants.DEFAULT_WINDOW_COLUMNS,
        timeout: Optional[float] = None
    ) -> List[OperationResult]:
        """調整所有瀏覽器視窗大小並進行排列。
        
        Args:
            browser_contexts: 瀏覽器上下文列表
            width: 視窗寬度
            height: 視窗高度
            columns: 每行視窗數量（預設4列）
            timeout: 超時時間
            
        Returns:
            操作結果列表
        """
        def resize_and_position_operation(context: BrowserContext, index: int, total: int) -> bool:
            # 計算視窗位置 (4x3 排列)
            row = (index - 1) // columns
            col = (index - 1) % columns
            
            x = col * width
            y = row * height
            
            # 調整視窗大小和位置
            context.driver.set_window_size(width, height)
            context.driver.set_window_position(x, y)
            return True
        
        return self.execute_sync(
            browser_contexts,
            resize_and_position_operation,
            f"調整視窗大小為 {width}x{height} 並進行 {columns}列排列",
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
    
    def get_current_betsize(self, driver: WebDriver, retry_count: int = 2) -> Optional[float]:
        """取得當前下注金額。
        
        Args:
            driver: WebDriver 實例
            retry_count: 重試次數（預設2次）
            
        Returns:
            Optional[float]: 當前金額，失敗返回None
        """
        # 定義可用金額列表
        GAME_BETSIZE = (
            0.4, 0.8, 1, 1.2, 1.6, 2, 2.4, 2.8, 3, 3.2, 3.6, 4, 5, 6, 7, 8, 9, 10,
            12, 14, 16, 18, 20, 24, 28, 32, 36, 40, 48, 56, 60, 64, 72, 80, 100,
            120, 140, 160, 180, 200, 240, 280, 300, 320, 360, 400, 420, 480, 500,
            540, 560, 600, 640, 700, 720, 800, 840, 900, 960, 980, 1000, 1080,
            1120, 1200, 1260, 1280, 1400, 1440, 1600, 1800, 2000
        )
        
        for attempt in range(retry_count):
            try:
                if attempt > 0:
                    self.logger.info(f"重試識別金額... (第 {attempt + 1} 次)")
                    time.sleep(0.5)  # 等待畫面穩定
                else:
                    self.logger.info("開始查詢當前下注金額...")
                
                # 截取整個瀏覽器截圖
                screenshot = driver.get_screenshot_as_png()
                screenshot_np = np.array(Image.open(io.BytesIO(screenshot)))
                screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)
                
                # 與資料夾中的圖片進行比對
                matched_amount, confidence = self._compare_betsize_images(screenshot_gray)
                
                if matched_amount:
                    try:
                        amount_value = float(matched_amount)
                        if amount_value in GAME_BETSIZE:
                            self.logger.info(f"當前下注金額: {amount_value} (信心度: {confidence:.3f})")
                            return amount_value
                        else:
                            self.logger.warning(f"金額 {matched_amount} 不在 GAME_BETSIZE 列表中")
                    except ValueError:
                        self.logger.error(f"無法將 {matched_amount} 轉換為數字")
                else:
                    self.logger.warning(f"無法識別當前下注金額 (最高信心度: {confidence:.3f})")
                
            except Exception as e:
                self.logger.error(f"查詢下注金額時發生錯誤: {e}")
        
        return None
    
    def _compare_betsize_images(self, screenshot_gray: np.ndarray) -> Tuple[Optional[str], float]:
        """使用 bet_size 資料夾中的圖片比對。
        
        Args:
            screenshot_gray: 截圖（灰階）
            
        Returns:
            Tuple[Optional[str], float]: (匹配的金額, 信心度)
        """
        try:
            # 取得專案根目錄
            if getattr(sys, 'frozen', False):
                project_root = Path(sys.executable).resolve().parent
            else:
                project_root = Path(__file__).resolve().parent.parent
            
            bet_size_dir = project_root / "img" / "bet_size"
            
            if not bet_size_dir.exists():
                self.logger.warning(f"bet_size 資料夾不存在: {bet_size_dir}，嘗試建立...")
                try:
                    bet_size_dir.mkdir(parents=True, exist_ok=True)
                    self.logger.info(f"已建立 bet_size 資料夾: {bet_size_dir}")
                except Exception as e:
                    self.logger.error(f"無法建立 bet_size 資料夾: {e}")
                    return None, 0.0
            
            # 取得所有 png 圖片
            image_files = sorted(bet_size_dir.glob("*.png"))
            if not image_files:
                self.logger.warning(f"bet_size 資料夾中沒有圖片")
                return None, 0.0
            
            self.logger.debug(f"開始比對 {len(image_files)} 張圖片...")
            
            # 儲存所有匹配結果（用於除錯）
            match_results = []
            
            for image_file in image_files:
                # 讀取模板圖片
                template = cv2.imread(str(image_file), cv2.IMREAD_GRAYSCALE)
                if template is None:
                    continue
                
                # 檢查尺寸
                if (screenshot_gray.shape[0] < template.shape[0] or 
                    screenshot_gray.shape[1] < template.shape[1]):
                    continue
                
                # 執行模板匹配
                result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                
                match_results.append((image_file.stem, max_val))
            
            # 按信心度排序
            match_results.sort(key=lambda x: x[1], reverse=True)
            
            # 顯示前 5 名候選（除錯用）
            if match_results:
                self.logger.debug("前 5 名匹配候選:")
                for i, (amount, score) in enumerate(match_results[:5]):
                    self.logger.debug(f"  {i+1}. {amount}: {score:.4f}")
            
            if not match_results:
                return None, 0.0
            
            best_match_amount, best_match_score = match_results[0]
            
            # 調整閾值：0.90 為可接受，0.85-0.90 為警告，< 0.85 為失敗
            if best_match_score >= 0.90:
                self.logger.info(f"找到匹配金額：{best_match_amount} (信心度：{best_match_score:.4f})")
                return best_match_amount, best_match_score
            elif best_match_score >= 0.85:
                self.logger.warning(f"找到可能匹配：{best_match_amount} (信心度較低：{best_match_score:.4f})")
                return best_match_amount, best_match_score
            else:
                self.logger.warning(f"未找到可靠匹配 (最高信心度：{best_match_score:.4f}, 金額：{best_match_amount})")
                return None, best_match_score
                
        except Exception as e:
            self.logger.error(f"比對圖片時發生錯誤: {e}")
            return None, 0.0
    
    def _click_betsize_button(self, driver: WebDriver, x: float, y: float) -> None:
        """點擊下注金額調整按鈕。
        
        Args:
            driver: WebDriver 實例
            x: X 座標 (基於 600x400 視窗)
            y: Y 座標 (基於 600x400 視窗)
        """
        screenshot = driver.get_screenshot_as_png()
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
            driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
                "type": ev,
                "x": actual_x,
                "y": actual_y,
                "button": "left",
                "clickCount": 1
            })
    
    def adjust_betsize(self, driver: WebDriver, target_amount: float, max_attempts: int = 200) -> bool:
        """調整下注金額到目標值。
        
        Args:
            driver: WebDriver 實例
            target_amount: 目標金額
            max_attempts: 最大嘗試次數
            
        Returns:
            bool: 調整成功返回True
        """
        try:
            # 定義可用金額列表
            GAME_BETSIZE = (
                0.4, 0.8, 1, 1.2, 1.6, 2, 2.4, 2.8, 3, 3.2, 3.6, 4, 5, 6, 7, 8, 9, 10,
                12, 14, 16, 18, 20, 24, 28, 32, 36, 40, 48, 56, 60, 64, 72, 80, 100,
                120, 140, 160, 180, 200, 240, 280, 300, 320, 360, 400, 420, 480, 500,
                540, 560, 600, 640, 700, 720, 800, 840, 900, 960, 980, 1000, 1080,
                1120, 1200, 1260, 1280, 1400, 1440, 1600, 1800, 2000
            )
            
            # 檢查目標金額
            if target_amount not in GAME_BETSIZE:
                self.logger.error(f"目標金額 {target_amount} 不在可用金額列表中")
                return False
            
            self.logger.info(f"目標金額: {target_amount}")
            
            # 取得當前金額
            current_amount = self.get_current_betsize(driver)
            if current_amount is None:
                self.logger.error("無法識別當前金額")
                return False
            
            self.logger.info(f"當前金額: {current_amount}")
            
            # 檢查是否已是目標金額
            if current_amount == target_amount:
                self.logger.info("當前金額已是目標金額，無需調整")
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
            
            self.logger.info(f"預估需要點擊{direction}按鈕約 {estimated_steps} 次")
            
            # 開始調整
            for i in range(estimated_steps):
                self._click_betsize_button(driver, click_x, click_y)
                self.logger.info(f"已點擊 {direction} 按鈕 ({i + 1}/{estimated_steps})")
                time.sleep(0.3)
            
            time.sleep(1)
            
            # 驗證並微調
            self.logger.info("開始驗證調整結果...")
            for attempt in range(max_attempts):
                current_amount = self.get_current_betsize(driver)
                
                if current_amount is None:
                    self.logger.warning(f"驗證失敗：無法識別金額 (嘗試 {attempt + 1}/{max_attempts})")
                    time.sleep(0.5)
                    continue
                
                if current_amount == target_amount:
                    self.logger.info(f"✓ 調整成功! 當前金額: {current_amount}")
                    return True
                
                self.logger.info(f"當前金額 {current_amount}，目標 {target_amount}，繼續調整...")
                
                # 根據當前金額決定點擊哪個按鈕
                if current_amount < target_amount:
                    self._click_betsize_button(driver, 440, 370)  # 增加
                else:
                    self._click_betsize_button(driver, 360, 370)  # 減少
                
                time.sleep(0.5)
            
            self.logger.error(f"調整失敗，已達最大嘗試次數 ({max_attempts})")
            return False
            
        except Exception as e:
            self.logger.error(f"調整金額時發生錯誤: {e}")
            return False
    
    def capture_betsize_template(self, driver: WebDriver, amount: float) -> bool:
        """截取下注金額模板。
        
        Args:
            driver: WebDriver 實例
            amount: 下注金額
            
        Returns:
            bool: 截取成功返回True
        """
        try:
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
            
            # 取得專案根目錄
            if getattr(sys, 'frozen', False):
                project_root = Path(sys.executable).resolve().parent
            else:
                project_root = Path(__file__).resolve().parent.parent
            
            # 儲存到 img/bet_size 目錄
            betsize_dir = project_root / "img" / "bet_size"
            betsize_dir.mkdir(parents=True, exist_ok=True)
            
            # 檔名使用金額（整數去掉 .0，小數保留）
            if amount == int(amount):
                filename = f"{int(amount)}.png"
            else:
                filename = f"{amount}.png"
            
            output_path = betsize_dir / filename
            cropped_img.save(output_path)
            
            self.logger.info(f"✓ 金額模板已儲存: {output_path}")
            self.logger.info(f"  - 金額: {amount}")
            self.logger.info(f"  - 尺寸: {cropped_img.size[0]}x{cropped_img.size[1]}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"截取金額模板失敗: {e}")
            return False


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
        
        # 取得專案根目錄
        if getattr(sys, 'frozen', False):
            self.project_root = Path(sys.executable).resolve().parent
        else:
            self.project_root = Path(__file__).resolve().parent.parent
        
        self.image_dir = self.project_root / Constants.IMAGE_DIR
        
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
                cv2.imwrite(str(save_path), image_cv)
                self.logger.info(f"截圖已儲存 {save_path}")
            
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
            
            # 讀取模板圖片
            template = cv2.imread(str(template_path))
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
        logger: Optional[logging.Logger] = None
    ):
        """初始化控制中心。
        
        Args:
            browser_contexts: 瀏覽器上下文列表
            browser_operator: 瀏覽器操作器
            logger: 日誌記錄器
        """
        self.browser_contexts = browser_contexts
        self.browser_operator = browser_operator
        self.logger = logger or LoggerFactory.get_logger()
        self.running = False
        self.game_running = False  # 遊戲運行狀態
        self.auto_press_running = False  # 自動按鍵運行狀態
        self.min_interval = 1.0  # 最小間隔時間
        self.max_interval = 1.0  # 最大間隔時間
        self.auto_press_threads: Dict[int, threading.Thread] = {}  # 每個瀏覽器的執行緒
        self._stop_event = threading.Event()  # 停止事件
    
    def show_help(self) -> None:
        """顯示幫助信息"""
        help_text = """
╔══════════════════════════════════════════════════════════╗
║            遊戲控制中心 - 指令說明                       ║
╚══════════════════════════════════════════════════════════╝

【遊戲控制】
  s <min>,<max>    開始自動按鍵（設定隨機間隔）
                   範例: s 1,2  (間隔 1~2 秒)
                   
  p                暫停自動按鍵
  
  b <金額>         調整所有瀏覽器的下注金額
                   範例: b 0.4, b 2.4, b 10
                   
  c                截取金額模板（用於金額識別）

【系統控制】
  h                顯示此幫助信息
  q                退出控制中心

提示：所有指令都區分大小寫，請使用小寫字母
"""
        self.logger.info(help_text)
    
    def _auto_press_loop_single(self, context: BrowserContext, browser_index: int) -> None:
        """單個瀏覽器的自動按鍵循環。
        
        Args:
            context: 瀏覽器上下文
            browser_index: 瀏覽器索引
        """
        import random
        
        press_count = 0
        username = context.credential.username
        
        self.logger.info(f"瀏覽器 {browser_index} ({username}) 自動按鍵已啟動")
        
        while not self._stop_event.is_set():
            try:
                press_count += 1
                
                # 執行按空白鍵
                try:
                    context.driver.execute_cdp_cmd("Input.dispatchKeyEvent", {
                        "type": "keyDown",
                        "key": " ",
                        "code": "Space",
                        "windowsVirtualKeyCode": 32,
                        "nativeVirtualKeyCode": 32
                    })
                    context.driver.execute_cdp_cmd("Input.dispatchKeyEvent", {
                        "type": "keyUp",
                        "key": " ",
                        "code": "Space",
                        "windowsVirtualKeyCode": 32,
                        "nativeVirtualKeyCode": 32
                    })
                    
                    self.logger.debug(
                        f"瀏覽器 {browser_index} ({username}) 第 {press_count} 次按鍵成功"
                    )
                    
                except Exception as e:
                    self.logger.error(
                        f"瀏覽器 {browser_index} ({username}) 按鍵失敗: {e}"
                    )
                
                # 每個瀏覽器使用獨立的隨機間隔
                interval = random.uniform(self.min_interval, self.max_interval)
                self.logger.debug(
                    f"瀏覽器 {browser_index} ({username}) 等待 {interval:.2f} 秒"
                )
                
                # 使用 wait 而非 sleep，這樣可以立即響應停止信號
                if self._stop_event.wait(timeout=interval):
                    break
                    
            except Exception as e:
                self.logger.error(
                    f"瀏覽器 {browser_index} ({username}) 執行錯誤: {e}"
                )
                self._stop_event.wait(timeout=1.0)
        
        self.logger.info(
            f"瀏覽器 {browser_index} ({username}) 自動按鍵已停止，共執行 {press_count} 次"
        )
    
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
        
        self.logger.info(
            f"已為 {len(self.browser_contexts)} 個瀏覽器啟動獨立的自動按鍵執行緒"
        )
    
    def _stop_auto_press(self) -> None:
        """停止所有自動按鍵執行緒。"""
        if not self.auto_press_running:
            self.logger.warning("自動按鍵未在運行")
            return
        
        self.logger.info(f"正在停止 {len(self.auto_press_threads)} 個瀏覽器的自動按鍵...")
        
        # 設置停止事件
        self._stop_event.set()
        
        # 等待所有執行緒結束
        stopped_count = 0
        for browser_index, thread in self.auto_press_threads.items():
            if thread and thread.is_alive():
                thread.join(timeout=5.0)
                
                if not thread.is_alive():
                    stopped_count += 1
                else:
                    self.logger.warning(f"瀏覽器 {browser_index} 的執行緒未能正常結束")
            else:
                stopped_count += 1
        
        self.logger.info(f"自動按鍵已停止: {stopped_count}/{len(self.auto_press_threads)} 個執行緒成功停止")
        
        self.auto_press_threads.clear()
        self.auto_press_running = False
        self.game_running = False
    
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
        args = parts[1] if len(parts) > 1 else ""
        
        try:
            if cmd == 'q':
                self.logger.info("正在退出控制中心")
                return False
            
            elif cmd == 'h':
                self.show_help()
            
            elif cmd == 's':
                # 解析 's' 指令參數
                if not args:
                    self.logger.error("指令格式錯誤，請使用: s min,max (例如: s 1,2)")
                    return True
                
                # 解析用戶輸入的間隔時間
                try:
                    interval_parts = args.split(',')
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
                    f"啟動自動按鍵循環\n"
                    f"  間隔時間: {min_interval}~{max_interval} 秒\n"
                    f"  瀏覽器數量: {len(self.browser_contexts)}\n"
                    f"  使用 'p' 指令可暫停"
                )
                
                # 啟動自動按鍵
                self._start_auto_press()
            
            elif cmd == 'p':
                if not self.auto_press_running:
                    self.logger.warning("自動按鍵未在運行")
                else:
                    self._stop_auto_press()
                    self.logger.info("遊戲已暫停")
            
            elif cmd == 'b':
                # 解析 b 指令參數
                if not args:
                    self.logger.error("指令格式錯誤，請使用: b amount (例如: b 0.4)")
                    return True
                
                try:
                    target_amount = float(args)
                    
                    self.logger.info("")
                    self.logger.info(f"開始同步調整所有瀏覽器的下注金額到 {target_amount}...")
                    self.logger.info(f"瀏覽器數量: {len(self.browser_contexts)}")
                    self.logger.info("")
                    
                    # 使用同步方法調整所有瀏覽器的金額
                    results = self.browser_operator.adjust_betsize_all(
                        self.browser_contexts,
                        target_amount
                    )
                    
                    # 統計結果
                    success_count = sum(1 for r in results if r.success)
                    
                    self.logger.info("")
                    self.logger.info("=" * 60)
                    if success_count == len(self.browser_contexts):
                        self.logger.info(f"✓ 金額調整完成: 全部 {success_count} 個瀏覽器調整成功")
                    else:
                        self.logger.warning(
                            f"⚠ 金額調整部分完成: {success_count}/{len(self.browser_contexts)} 個瀏覽器成功"
                        )
                        # 顯示失敗的瀏覽器
                        for i, result in enumerate(results, 1):
                            if not result.success:
                                username = self.browser_contexts[i-1].credential.username
                                self.logger.error(f"  瀏覽器 {i} ({username}) 失敗: {result.message}")
                    self.logger.info("=" * 60)
                    self.logger.info("")
                    
                except ValueError:
                    self.logger.error(f"無效的金額: {args}，請輸入數字")
            
            elif cmd == 'c':
                # 定義可用金額列表
                GAME_BETSIZE = (
                    0.4, 0.8, 1, 1.2, 1.6, 2, 2.4, 2.8, 3, 3.2, 3.6, 4, 5, 6, 7, 8, 9, 10,
                    12, 14, 16, 18, 20, 24, 28, 32, 36, 40, 48, 56, 60, 64, 72, 80, 100,
                    120, 140, 160, 180, 200, 240, 280, 300, 320, 360, 400, 420, 480, 500,
                    540, 560, 600, 640, 700, 720, 800, 840, 900, 960, 980, 1000, 1080,
                    1120, 1200, 1260, 1280, 1400, 1440, 1600, 1800, 2000
                )
                
                self.logger.info("")
                self.logger.info("=== 截取金額模板工具 ===")
                self.logger.info("請輸入目前遊戲顯示的金額（例如: 0.4, 2.4, 10）")
                self.logger.info("按 Enter 鍵退出")
                self.logger.info("")
                
                while True:
                    try:
                        print("\n金額: ", end="", flush=True)
                        amount_input = input().strip()
                        
                        # 空白輸入則退出
                        if not amount_input:
                            self.logger.info("退出金額模板工具")
                            break
                        
                        amount = float(amount_input)
                        
                        # 驗證金額是否在有效列表中
                        if amount not in GAME_BETSIZE:
                            self.logger.warning(f"⚠ 金額 {amount} 不在標準列表中，但仍會建立模板")
                        
                        self.logger.info(f"目標金額: {amount}")
                        
                        # 使用第一個瀏覽器截取
                        if self.browser_contexts:
                            first_context = self.browser_contexts[0]
                            if self.browser_operator.capture_betsize_template(first_context.driver, amount):
                                self.logger.info("✓ 模板截取成功，可繼續輸入下一個金額或按 Enter 退出")
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
        self.logger.info("遊戲控制中心已啟動")
        self.logger.info("")
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
            self.logger.info("控制中心已停止")
    
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
        self.last_canvas_rect = None  # 儲存 Canvas 區域資訊
    
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
        self.logger.info("金富翁遊戲自動化系統 v4.0")
        self.logger.info("")
        self.logger.info("")
        self.logger.info("正在載入配置")
        
        # 讀取使用者憑證（包含 proxy 資訊）
        self.credentials = self.config_reader.read_user_credentials()
        
        # 讀取下注規則
        self.rules = self.config_reader.read_bet_rules()
        
        self.logger.info(
            f"配置載入完成 {len(self.credentials)} 個帳號 "
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
                            self.logger.info(
                                f"瀏覽器 {index+1}/{browser_count} Proxy 中繼已啟動 {proxy_info.host}:{proxy_info.port} 本機埠 {local_proxy_port}"
                            )
                        else:
                            self.logger.warning(
                                f"瀏覽器 {index+1}/{browser_count} Proxy 啟動失敗 將直連網路"
                            )
                    else:
                        self.logger.warning(f"瀏覽器 {index+1}/{browser_count} Proxy 格式錯誤 {credential.proxy}")
                        
                except Exception as e:
                    self.logger.error(f"瀏覽器 {index+1}/{browser_count} Proxy 設定失敗 {e}")
            else:
                # 沒有設定 proxy，將使用直連
                self.logger.info(f"瀏覽器 {index+1}/{browser_count} 使用直連網路 未設定 Proxy")
            
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
        self.logger.info(f"Proxy 伺服器啟動完成 {active_count}/{len(proxy_ports)}")
        return proxy_ports
    
    def create_browser_instances(
        self,
        browser_count: int,
        proxy_ports: List[Optional[int]]
    ) -> List[BrowserContext]:
        """建立瀏覽器實例。
        
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
                self.logger.info(
                    f"瀏覽器 {index+1}/{browser_count} 正在建立瀏覽器 "
                    f"帳號 {credential.username}"
                )
                
                driver = self.browser_manager.create_webdriver(local_proxy_port=proxy_port)
                
                context = BrowserContext(
                    driver=driver,
                    credential=credential,
                    index=index + 1,
                    proxy_port=proxy_port
                )
                
                proxy_info = f" Proxy 埠 {proxy_port}" if proxy_port else " 直連"
                self.logger.info(f"瀏覽器 {index+1}/{browser_count} 瀏覽器建立成功{proxy_info}")
                
                return index, context
                
            except Exception as e:
                self.logger.error(f"瀏覽器 {index+1}/{browser_count} 建立瀏覽器失敗 {e}")
                return index, None
        
        # 使用執行緒池建立瀏覽器
        with ThreadPoolExecutor(max_workers=Constants.MAX_THREAD_WORKERS) as executor:
            futures = []
            for i in range(browser_count):
                future = executor.submit(
                    create_browser_instance,
                    i,
                    self.credentials[i],
                    proxy_ports[i]
                )
                futures.append(future)
            
            # 收集結果
            for future in as_completed(futures):
                index, context = future.result()
                browser_results[index] = context
        
        # 過濾成功建立的瀏覽器
        contexts = [ctx for ctx in browser_results if ctx is not None]
        
        if len(contexts) == browser_count:
            self.logger.info(f"瀏覽器建立完成 {len(contexts)}/{browser_count}")
        else:
            self.logger.warning(f"部分瀏覽器建立失敗 {len(contexts)}/{browser_count}")
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
            
            time.sleep(Constants.DEFAULT_WAIT_SECONDS)  # 等待登入後的頁面跳轉
            
            # 步驟 5: 導航到遊戲頁面
            self._print_step(5, "導航到遊戲頁面")
            game_results = self.browser_operator.navigate_to_game_page(
                self.browser_contexts
            )
            
            time.sleep(Constants.DEFAULT_WAIT_SECONDS)  # 等待遊戲頁面載入
            
            # 調整視窗
            self._print_step("5+", "調整視窗排列 (600x400)")
            resize_results = self.browser_operator.resize_and_arrange_all(
                self.browser_contexts,
                width=600,
                height=400,
                columns=4
            )
            
            time.sleep(Constants.DEFAULT_WAIT_SECONDS)  # 等待視窗調整完成
            
            # 步驟 6: 圖片檢測與遊戲流程
            self._print_step(6, "圖片檢測與遊戲流程")
            self._execute_image_detection_flow()
            
            # 步驟 7: 啟動遊戲控制中心
            self._print_step(7, "啟動遊戲控制中心")
            control_center = GameControlCenter(
                browser_contexts=self.browser_contexts,
                browser_operator=self.browser_operator,
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
        self.logger.info("")
        self.logger.info("階段 1 檢測 lobby_login")
        self.logger.info("")
        
        self._handle_lobby_login(reference_browser)
        
        # 階段 2: 處理 lobby_confirm
        self.logger.info("")
        self.logger.info("階段 2 檢測 lobby_confirm")
        self.logger.info("")
        
        self._handle_lobby_confirm(reference_browser)
        
        self.logger.info("")
        self.logger.info("圖片檢測流程完成 準備進入遊戲控制中心")
        self.logger.info("")
    
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
        else:
            self.logger.info(f"找到模板圖片 {template_name}")
        
        # 2. 持續檢測直到所有瀏覽器都找到圖片
        self.logger.info(f"正在檢測 {display_name}，等待所有瀏覽器準備就緒...")
        detection_results = self._continuous_detect_until_found(template_name, display_name)
        
        # 3. 切換到 iframe 並取得 Canvas 座標
        self.logger.info("正在切換到遊戲 iframe...")
        for i, context in enumerate(self.browser_contexts, 1):
            try:
                # 切換到 iframe
                iframe = WebDriverWait(context.driver, 10).until(
                    EC.presence_of_element_located((By.ID, Constants.GAME_IFRAME))
                )
                context.driver.switch_to.frame(iframe)
                self.logger.info(f"  瀏覽器 {i} ({context.credential.username}) 已切換到 iframe")
            except Exception as e:
                self.logger.error(f"  瀏覽器 {i} ({context.credential.username}) 切換 iframe 失敗: {e}")
        
        # 取得 Canvas 區域（使用第一個瀏覽器作為參考）
        try:
            rect = reference_browser.driver.execute_script(f"""
                const canvas = document.getElementById('{Constants.GAME_CANVAS}');
                const r = canvas.getBoundingClientRect();
                return {{x: r.left, y: r.top, w: r.width, h: r.height}};
            """)
            self.logger.info(f"Canvas 區域: x={rect['x']}, y={rect['y']}, w={rect['w']}, h={rect['h']}")
            
            # 儲存到實例變數供後續使用
            self.last_canvas_rect = rect
        except Exception as e:
            self.logger.error(f"取得 Canvas 座標失敗: {e}")
            raise
        
        # 4. 計算點擊座標（開始遊戲按鈕）
        start_x = rect["x"] + rect["w"] * Constants.START_GAME_X_RATIO
        start_y = rect["y"] + rect["h"] * Constants.START_GAME_Y_RATIO
        self.logger.info(f"開始遊戲按鈕座標: ({start_x:.1f}, {start_y:.1f})")
        
        # 5. 在所有瀏覽器中執行點擊
        time.sleep(1)
        self.logger.info("步驟 2: 在所有瀏覽器中點擊開始遊戲按鈕...")
        for i, context in enumerate(self.browser_contexts, 1):
            self._click_coordinate(context.driver, start_x, start_y)
            self.logger.debug(f"  瀏覽器 {i} 已執行點擊")
        
        # 6. 等待所有瀏覽器中的圖片消失
        self.logger.info("步驟 2: 等待所有瀏覽器的 lobby_login.png 消失...")
        self._wait_for_image_disappear(template_name)
        self.logger.info(f"步驟 2 完成：所有瀏覽器的 {display_name} 都已消失")
    
    def _handle_lobby_confirm(self, reference_browser: BrowserContext) -> None:
        """處理 lobby_confirm 的檢測與點擊。
        
        Args:
            reference_browser: 參考瀏覽器
        """
        # 1. 檢查模板是否存在
        template_name = Constants.LOBBY_CONFIRM
        display_name = "lobby_confirm"
        
        if not self.image_detector.template_exists(template_name):
            self.logger.warning(f"模板圖片 {template_name} 不存在")
            # 如果沒有模板，嘗試使用確認按鈕座標自動建立
            if hasattr(self, 'last_canvas_rect') and self.last_canvas_rect:
                self._auto_capture_lobby_confirm(reference_browser)
            else:
                self._prompt_capture_template(reference_browser, template_name, display_name)
        else:
            self.logger.info(f"找到模板圖片 {template_name}")
        
        # 2. 持續檢測直到所有瀏覽器都找到圖片
        self.logger.info(f"正在檢測 {display_name}，等待所有瀏覽器準備就緒...")
        detection_results = self._continuous_detect_until_found(template_name, display_name)
        
        # 3. 計算點擊座標（確認按鈕）
        if hasattr(self, 'last_canvas_rect') and self.last_canvas_rect:
            rect = self.last_canvas_rect
            confirm_x = rect["x"] + rect["w"] * Constants.MACHINE_CONFIRM_X_RATIO
            confirm_y = rect["y"] + rect["h"] * Constants.MACHINE_CONFIRM_Y_RATIO
            self.logger.info(f"確認按鈕座標: ({confirm_x:.1f}, {confirm_y:.1f})")
            
            # 4. 在所有瀏覽器中執行點擊
            time.sleep(1)
            self.logger.info("步驟 4: 在所有瀏覽器中點擊確認按鈕...")
            for i, context in enumerate(self.browser_contexts, 1):
                self._click_coordinate(context.driver, confirm_x, confirm_y)
                self.logger.debug(f"  瀏覽器 {i} 已執行點擊")
        else:
            self.logger.warning("未找到 Canvas 座標，跳過自動點擊")
        
        # 5. 等待所有瀏覽器中的圖片消失
        self.logger.info("步驟 4: 等待所有瀏覽器的 lobby_confirm.png 消失...")
        self._wait_for_image_disappear(template_name)
        self.logger.info(f"步驟 4 完成：所有瀏覽器的 {display_name} 都已消失")
        
        # 6. 所有瀏覽器都成功進入遊戲
        self.logger.info("")
        self.logger.info("=" * 60)
        self.logger.info("步驟 5: 所有瀏覽器都已成功進入遊戲控制模式")
        self.logger.info("=" * 60)
        self.logger.info("")
        time.sleep(2)
    
    def _click_coordinate(self, driver: WebDriver, x: float, y: float) -> None:
        """點擊指定座標。
        
        Args:
            driver: WebDriver 實例
            x: X座標
            y: Y座標
        """
        for event in ["mousePressed", "mouseReleased"]:
            driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
                "type": event,
                "x": x,
                "y": y,
                "button": "left",
                "clickCount": 1
            })
    
    def _auto_capture_lobby_confirm(self, reference_browser: BrowserContext) -> None:
        """自動截取 lobby_confirm 模板圖片。
        
        使用已知的確認按鈕座標自動截取模板。
        
        Args:
            reference_browser: 參考瀏覽器
        """
        try:
            self.logger.info("正在自動建立 lobby_confirm.png 模板...")
            
            # 取得確認按鈕座標
            rect = self.last_canvas_rect
            confirm_x = rect["x"] + rect["w"] * Constants.MACHINE_CONFIRM_X_RATIO
            confirm_y = rect["y"] + rect["h"] * Constants.MACHINE_CONFIRM_Y_RATIO
            
            # 截取畫面
            screenshot = reference_browser.driver.get_screenshot_as_png()
            screenshot_img = Image.open(io.BytesIO(screenshot))
            
            # 獲取實際截圖尺寸
            img_width, img_height = screenshot_img.size
            
            center_x = int(confirm_x)
            center_y = int(confirm_y)
            
            # 固定像素偏移：上下左右各20px
            crop_left = max(0, center_x - 20)
            crop_top = max(0, center_y - 20)
            crop_right = min(img_width, center_x + 20)
            crop_bottom = min(img_height, center_y + 20)
            
            self.logger.info(f"截圖尺寸: {img_width}x{img_height}, 確認按鈕座標: ({center_x}, {center_y})")
            
            cropped_img = screenshot_img.crop((crop_left, crop_top, crop_right, crop_bottom))
            
            # 儲存圖片
            template_path = self.image_detector.get_template_path(Constants.LOBBY_CONFIRM)
            template_path.parent.mkdir(parents=True, exist_ok=True)
            cropped_img.save(template_path)
            
            self.logger.info(f"✓ lobby_confirm.png 已自動建立")
            
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
                        max_wait_attempts = 20  # 最多等待 60 秒
                        for attempt in range(max_wait_attempts):
                            time.sleep(3)
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
                                self.logger.info(f"檢測進度 {attempt + 1}/{max_wait_attempts} 次 仍未找到")
                        
                        self.logger.warning(f"等待超時 未檢測到 {display_name}")
                        continue
                        
                    except KeyboardInterrupt:
                        self.logger.info("用戶中斷等待")
                        continue
                
                elif choice == "3":
                    # 跳過此階段
                    self.logger.info(f"跳過 {display_name} 檢測階段")
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
                self.logger.info(f"所有瀏覽器 ({found_count}/{total_browsers}) 都已檢測到 {display_name}")
                for i, result in enumerate(detection_results, 1):
                    if result:
                        x, y, confidence = result
                        self.logger.info(f"  瀏覽器 {i} 座標 ({x}, {y}) 信心度 {confidence:.2f}")
                return detection_results
            
            # 每 N 次檢測顯示一次進度
            if attempt % Constants.DETECTION_PROGRESS_INTERVAL == 0:
                self.logger.info(f"持續檢測中，第 {attempt} 次，已找到 {found_count}/{total_browsers} 個瀏覽器")
            
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
        
        # 使用同步操作器執行點擊
        def click_operation(context: BrowserContext, index: int, total: int) -> bool:
            """在單個瀏覽器中執行點擊操作"""
            result = detection_results[index - 1]
            if result is None:
                return False
            
            x, y, confidence = result
            driver = context.driver
            
            try:
                # 使用 CDP (Chrome DevTools Protocol) 執行點擊
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
                self.logger.info(f"所有瀏覽器 ({total_browsers}/{total_browsers}) 中的圖片都已消失")
                return
            
            # 每 10 次檢測顯示一次進度
            if attempt % 10 == 0:
                self.logger.info(f"等待圖片消失中，已消失 {disappeared_count}/{total_browsers} 個瀏覽器")
            
            # 等待後再次檢測
            time.sleep(Constants.DETECTION_INTERVAL)
    
    def cleanup(self) -> None:
        """清理所有資源"""
        self.logger.info("")
        self.logger.info("正在清理資源")
        
        # 關閉所有瀏覽器
        if self.browser_contexts:
            self.browser_operator.close_all(self.browser_contexts)
            self.browser_contexts.clear()
        
        # 停止所有 Proxy 伺服器
        self.proxy_manager.stop_all_servers()
        
        self.logger.info("清理完成")
        self.logger.info("")


# ============================================================================
# 主程式入口
# ============================================================================

def main() -> None:
    """主程式入口函式。
    
    初始化並執行應用程式。
    """
    logger = LoggerFactory.get_logger()
    
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
