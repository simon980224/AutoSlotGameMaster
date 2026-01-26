"""
賽特遊戲自動化系統 - 重構版

此版本完全獨立運行，不依賴 main.py

功能範圍（對應 main_flow_explanation.md 第 76~92 行）:
- 清除殘留 chromedriver 程序
- 載入配置檔案（用戶資料.txt、用戶規則.txt）
- 自動決定瀏覽器數量
- 啟動代理中繼伺服器（為每個瀏覽器建立本地代理）
- 建立瀏覽器實例（為每個用戶建立 WebDriver）

作者: 凡臻科技
版本: 1.0.0
Python: 3.8+
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
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import Enum
import threading

# Selenium WebDriver 相關
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager

# 圖片處理相關
import cv2
import numpy as np
from PIL import Image


# ============================================================================
# 常量定義
# ============================================================================

class Constants:
    """系統常量"""
    # 版本資訊
    VERSION = "1.0.0"
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


def cleanup_chromedriver_processes() -> None:
    """清除所有殘留的 chromedriver 程序。
    
    在程式啟動前執行，確保沒有殘留的 chromedriver 程序佔用資源。
    支援 Windows、macOS 和 Linux 作業系統。
    """
    logger = LoggerFactory.get_logger()
    system = platform.system().lower()
    
    logger.info("=" * 60)
    logger.info("【系統初始化】清理殘留程序")
    logger.info("=" * 60)
    
    try:
        if system == "windows":
            result = subprocess.run(
                ["taskkill", "/F", "/IM", "chromedriver.exe"],
                capture_output=True,
                text=True,
                timeout=Constants.CLEANUP_PROCESS_TIMEOUT
            )
            
            if result.returncode == 0:
                logger.info("[成功] 已清除 Windows 上的 chromedriver 程序")
            elif "找不到" in result.stdout or "not found" in result.stdout.lower():
                logger.info("[成功] 沒有殘留的 chromedriver 程序")
            else:
                logger.debug(f"taskkill 執行結果: {result.stdout.strip()}")
                
        elif system in ["darwin", "linux"]:
            result = subprocess.run(
                ["killall", "-9", "chromedriver"],
                capture_output=True,
                text=True,
                timeout=Constants.CLEANUP_PROCESS_TIMEOUT
            )
            
            if result.returncode == 0:
                logger.info(f"[成功] 已清除 {system.upper()} 上的 chromedriver 程序")
            else:
                logger.info("[成功] 沒有殘留的 chromedriver 程序")
        else:
            logger.warning(f"[警告] 不支援的作業系統: {system}，跳過清除 chromedriver")
            
    except subprocess.TimeoutExpired:
        logger.warning("[警告] 清除 chromedriver 程序逾時")
    except FileNotFoundError:
        logger.info("[成功] 沒有殘留的 chromedriver 程序")
    except Exception as e:
        logger.warning(f"[警告] 清除程序時發生錯誤: {e}")
    
    logger.info("")


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
                    self.logger.warning(f"第 {line_number} 行格式不完整 已跳過 {line}")
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
                self.logger.warning(f"第 {line_number} 行資料無效 {e}")
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
                    self.logger.warning(f"第 {line_number} 行格式不完整 已跳過 {line}")
                    continue
                
                rule_type = parts[0].strip().lower()
                
                if rule_type == 'a':
                    if len(parts) < 3:
                        self.logger.warning(f"第 {line_number} 行格式不完整 已跳過 {line}")
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
                        self.logger.warning(f"第 {line_number} 行格式不完整 已跳過 {line}")
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
                    self.logger.warning(f"第 {line_number} 行無效的規則類型 '{rule_type}' 已跳過")
                    continue
                
            except (ValueError, IndexError) as e:
                self.logger.warning(f"第 {line_number} 行無法解析 {e}")
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
            self.logger.warning("上游代理連接逾時")
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
            self.logger.warning("上游代理回應逾時")
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
            self.logger.debug("客戶端連接逾時")
        except Exception as e:
            self.logger.debug(f"處理客戶端連接時發生錯誤: {e}")
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
                        self.logger.error(f"接受連接時發生錯誤 {e}")
                    
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
                    self.logger.error(f"代理伺服器執行失敗 埠 {local_port} {e}")
            
            server_thread = threading.Thread(target=run_server, daemon=True)
            server_thread.start()
            
            with self._lock:
                self._proxy_servers[local_port] = server
                self._proxy_threads[local_port] = server_thread
            
            time.sleep(Constants.PROXY_SERVER_START_WAIT)
            
            self.logger.info(f"[成功] 代理中繼已啟動 (埠: {local_port})")
            return local_port
            
        except Exception as e:
            self.logger.error(f"啟動本機代理伺服器失敗 {e}")
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
                self.logger.debug(f"停止代理伺服器時發生錯誤 ({local_port}): {e}")
    
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
            self.logger.warning(f"WebDriver Manager 失敗，嘗試使用本機驅動程式")
            
            # 方法 2: 使用本機驅動程式
            try:
                driver = self._create_webdriver_with_local_driver(chrome_options)
            except Exception as e2:
                errors.append(f"本機驅動程式: {e2}")
                self.logger.error(f"本機驅動程式也失敗: {e2}")
        
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
        import os
        
        project_root = get_resource_path()
        
        system = platform.system().lower()
        driver_filename = "chromedriver.exe" if system == "windows" else "chromedriver"
        
        driver_path = project_root / driver_filename
        
        if not driver_path.exists():
            raise FileNotFoundError(
                f"找不到驅動程式檔案\n"
                f"請確保 {driver_filename} 存在於專案根目錄"
            )
        
        if system in ["darwin", "linux"]:
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
                self.logger.debug(f"瀏覽器 #{index} 已關閉")


# ============================================================================
# 應用程式啟動器
# ============================================================================

class AutoSlotGameAppStarter:
    """應用程式啟動器。
    
    實現 main_flow_explanation.md 第 76~92 行描述的流程：
    - 清除殘留 chromedriver 程序
    - 載入配置檔案
    - 自動決定瀏覽器數量
    - 啟動代理中繼伺服器
    - 建立瀏覽器實例
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or LoggerFactory.get_logger()
        self.config_reader: Optional[ConfigReader] = None
        self.proxy_manager: Optional[LocalProxyServerManager] = None
        self.browser_manager: Optional[BrowserManager] = None
        self.browser_contexts: List[BrowserContext] = []
        self.credentials: List[UserCredential] = []
        self.rules: List[BetRule] = []
    
    def initialize(self) -> bool:
        """執行完整的初始化流程。
        
        流程:
        1. 清除殘留 chromedriver 程序
        2. 載入配置檔案
        3. 自動決定瀏覽器數量
        4. 啟動代理中繼伺服器
        5. 建立瀏覽器實例
        
        Returns:
            初始化是否成功
        """
        try:
            # 步驟 1: 清除殘留 chromedriver 程序
            self._step_cleanup_chromedriver()
            
            # 步驟 2: 載入配置檔案
            self._step_load_config()
            
            # 步驟 3: 自動決定瀏覽器數量
            browser_count = self._step_determine_browser_count()
            
            if browser_count == 0:
                self.logger.error("沒有可用的用戶帳號，無法繼續")
                return False
            
            # 步驟 4: 啟動代理中繼伺服器
            proxy_ports = self._step_start_proxy_servers(browser_count)
            
            # 步驟 5: 建立瀏覽器實例
            self._step_create_browsers(browser_count, proxy_ports)
            
            return True
            
        except Exception as e:
            self.logger.error(f"初始化失敗: {e}")
            return False
    
    def _step_cleanup_chromedriver(self) -> None:
        """步驟 1: 清除殘留 chromedriver 程序"""
        cleanup_chromedriver_processes()
    
    def _step_load_config(self) -> None:
        """步驟 2: 載入配置檔案"""
        self.logger.info("=" * 60)
        self.logger.info("【步驟 2】載入配置檔案")
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
        """步驟 3: 自動決定瀏覽器數量
        
        Returns:
            瀏覽器數量
        """
        self.logger.info("=" * 60)
        self.logger.info("【步驟 3】自動決定瀏覽器數量")
        self.logger.info("=" * 60)
        
        # 根據用戶數量決定瀏覽器數量，最多 MAX_BROWSER_COUNT 個
        browser_count = min(len(self.credentials), Constants.MAX_BROWSER_COUNT)
        
        self.logger.info(f"[成功] 將開啟 {browser_count} 個瀏覽器")
        self.logger.info("")
        
        return browser_count
    
    def _step_start_proxy_servers(self, browser_count: int) -> List[Optional[int]]:
        """步驟 4: 啟動代理中繼伺服器
        
        Args:
            browser_count: 瀏覽器數量
            
        Returns:
            每個瀏覽器對應的本機代理埠號列表
        """
        self.logger.info("=" * 60)
        self.logger.info("【步驟 4】啟動代理中繼伺服器")
        self.logger.info("=" * 60)
        
        self.proxy_manager = LocalProxyServerManager(logger=self.logger)
        proxy_ports: List[Optional[int]] = []
        
        for i in range(browser_count):
            credential = self.credentials[i]
            
            if credential.proxy:
                # 有代理配置，啟動中繼伺服器
                try:
                    proxy_info = ProxyInfo.from_connection_string(credential.proxy)
                    port = self.proxy_manager.start_proxy_server(proxy_info)
                    proxy_ports.append(port)
                    self.logger.info(f"  瀏覽器 {i+1}: 代理中繼埠 {port}")
                except Exception as e:
                    self.logger.warning(f"  瀏覽器 {i+1}: 無法解析代理配置 - {e}")
                    proxy_ports.append(None)
            else:
                # 沒有代理配置
                proxy_ports.append(None)
                self.logger.info(f"  瀏覽器 {i+1}: 無代理配置")
        
        self.logger.info("")
        return proxy_ports
    
    def _step_create_browsers(
        self, 
        browser_count: int, 
        proxy_ports: List[Optional[int]]
    ) -> None:
        """步驟 5: 建立瀏覽器實例
        
        Args:
            browser_count: 瀏覽器數量
            proxy_ports: 代理埠號列表
        """
        self.logger.info("=" * 60)
        self.logger.info("【步驟 5】建立瀏覽器實例")
        self.logger.info("=" * 60)
        
        self.browser_manager = BrowserManager(logger=self.logger)
        
        def create_browser(index: int) -> Optional[BrowserContext]:
            """建立單個瀏覽器"""
            credential = self.credentials[index]
            proxy_port = proxy_ports[index]
            
            try:
                driver = self.browser_manager.create_webdriver(
                    local_proxy_port=proxy_port
                )
                
                context = BrowserContext(
                    driver=driver,
                    credential=credential,
                    index=index + 1,
                    proxy_port=proxy_port
                )
                
                self.logger.info(f"[成功] 瀏覽器 {index+1}/{browser_count} 已建立")
                return context
                
            except Exception as e:
                self.logger.error(f"[失敗] 瀏覽器 {index+1}/{browser_count} 建立失敗: {e}")
                return None
        
        # 並行建立瀏覽器
        with ThreadPoolExecutor(max_workers=Constants.MAX_THREAD_WORKERS) as executor:
            futures = [
                executor.submit(create_browser, i) 
                for i in range(browser_count)
            ]
            
            for future in as_completed(futures):
                context = future.result()
                if context:
                    self.browser_contexts.append(context)
        
        # 按索引排序
        self.browser_contexts.sort(key=lambda c: c.index)
        
        self.logger.info("")
        self.logger.info(f"[完成] 成功建立 {len(self.browser_contexts)}/{browser_count} 個瀏覽器")
        self.logger.info("")
    
    def cleanup(self) -> None:
        """清理所有資源"""
        self.logger.info("=" * 60)
        self.logger.info("【清理資源】")
        self.logger.info("=" * 60)
        
        # 關閉所有瀏覽器
        for context in self.browser_contexts:
            try:
                context.driver.quit()
                self.logger.info(f"[成功] 已關閉瀏覽器 {context.index}")
            except Exception as e:
                self.logger.warning(f"[警告] 關閉瀏覽器 {context.index} 時發生錯誤: {e}")
        
        self.browser_contexts.clear()
        
        # 停止所有代理伺服器
        if self.proxy_manager:
            self.proxy_manager.stop_all_servers()
            self.logger.info("[成功] 已停止所有代理伺服器")
        
        self.logger.info("")
    
    def get_browser_contexts(self) -> List[BrowserContext]:
        """取得所有瀏覽器上下文"""
        return self.browser_contexts
    
    def get_credentials(self) -> List[UserCredential]:
        """取得所有用戶憑證"""
        return self.credentials
    
    def get_rules(self) -> List[BetRule]:
        """取得所有下注規則"""
        return self.rules


# ============================================================================
# 主程式入口
# ============================================================================

def main():
    """主程式入口點"""
    logger = LoggerFactory.get_logger()
    
    logger.info("")
    logger.info("*" * 60)
    logger.info(f"  {Constants.SYSTEM_NAME}")
    logger.info(f"  版本: {Constants.VERSION}")
    logger.info("*" * 60)
    logger.info("")
    
    # 建立啟動器
    starter = AutoSlotGameAppStarter(logger=logger)
    
    try:
        # 執行初始化流程
        if starter.initialize():
            logger.info("=" * 60)
            logger.info("【初始化完成】")
            logger.info("=" * 60)
            logger.info(f"  - 瀏覽器數量: {len(starter.get_browser_contexts())}")
            logger.info(f"  - 用戶數量: {len(starter.get_credentials())}")
            logger.info(f"  - 規則數量: {len(starter.get_rules())}")
            logger.info("")
            
            # 在這裡可以繼續執行後續流程...
            # 例如: 導航到登入頁面、執行登入、導航到遊戲頁面等
            
            # 暫時保持程式運行，讓使用者可以看到瀏覽器
            logger.info("按 Enter 鍵結束程式...")
            input()
            
        else:
            logger.error("初始化失敗，程式退出")
            
    except KeyboardInterrupt:
        logger.info("\n收到中斷信號，正在清理...")
    except Exception as e:
        logger.error(f"程式執行時發生錯誤: {e}")
    finally:
        # 清理資源
        starter.cleanup()
        logger.info("程式已結束")


if __name__ == "__main__":
    main()
