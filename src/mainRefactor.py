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
from typing import Optional, List, Dict, Tuple, Any, Callable, Protocol
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


@dataclass
class BrowserContext:
    """瀏覽器上下文資訊"""
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
    """操作結果封裝"""
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
        with self._lock:
            if local_port in self._proxy_servers:
                server = self._proxy_servers[local_port]
                server.stop()
                self.logger.debug(f"已停止 Proxy 伺服器: 埠 {local_port}")
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
        width: int = 600,
        height: int = 400,
        columns: int = 4,
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


# ============================================================================
# 圖片檢測器
# ============================================================================

class ImageDetector:
    """圖片檢測器。
    
    提供螢幕截圖、圖片比對和座標定位功能。
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
    """遊戲控制中心（基礎版本）。
    
    提供基本的指令接收框架，具體功能待實現。
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
    
    def show_help(self) -> None:
        """顯示幫助信息"""
        help_text = """
遊戲控制中心 指令說明

遊戲控制
  s         開始遊戲 按空白鍵
  p         暫停遊戲

系統控制
  h         顯示此幫助信息
  q         退出控制中心
"""
        self.logger.info(help_text)
    
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
        
        try:
            if command == 'q':
                self.logger.info("正在退出控制中心")
                return False
            
            elif command == 'h':
                self.show_help()
            
            elif command == 's':
                if self.game_running:
                    self.logger.warning("遊戲已經在運行中")
                else:
                    self.logger.info("執行指令 開始遊戲 按空白鍵")
                    results = self.browser_operator.press_space_all(self.browser_contexts)
                    success_count = sum(1 for r in results if r.success)
                    if success_count > 0:
                        self.game_running = True
                        self.logger.info(f"遊戲已開始 {success_count}/{len(results)} 個瀏覽器")
                    else:
                        self.logger.error("開始遊戲失敗")
            
            elif command == 'p':
                if not self.game_running:
                    self.logger.warning("遊戲尚未開始")
                else:
                    self.game_running = False
                    self.logger.info("遊戲已暫停")
            
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
            self.running = False
            self.logger.info("控制中心已停止")
    
    def stop(self) -> None:
        """停止控制中心"""
        self.running = False


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
    
    def _print_step(self, step: Any, title: str) -> None:
        """輸出步驟標題。
        
        Args:
            step: 步驟編號
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
            
            time.sleep(3)  # 等待頁面載入
            
            # 步驟 4: 執行登入操作（同步）
            self._print_step(4, "執行登入操作")
            login_results = self.browser_operator.perform_login_all(
                self.browser_contexts
            )
            
            time.sleep(3)  # 等待登入後的頁面跳轉
            
            # 步驟 5: 導航到遊戲頁面
            self._print_step(5, "導航到遊戲頁面")
            game_results = self.browser_operator.navigate_to_game_page(
                self.browser_contexts
            )
            
            time.sleep(3)  # 等待遊戲頁面載入
            
            # 調整視窗
            self._print_step("5+", "調整視窗排列 (600x400)")
            resize_results = self.browser_operator.resize_and_arrange_all(
                self.browser_contexts,
                width=600,
                height=400,
                columns=4
            )
            
            time.sleep(3)  # 等待視窗調整完成
            
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
    
    def _handle_lobby_login(self, reference_browser: BrowserContext) -> None:
        """處理 lobby_login 的檢測與點擊。
        
        Args:
            reference_browser: 參考瀏覽器
        """
        template_name = Constants.LOBBY_LOGIN
        
        # 1. 檢查模板是否存在
        if not self.image_detector.template_exists(template_name):
            self.logger.warning(f"模板圖片 {template_name} 不存在")
            self._prompt_capture_template(reference_browser, template_name, "lobby_login")
        else:
            self.logger.info(f"找到模板圖片 {template_name}")
        
        # 2. 持續檢測直到找到圖片
        self.logger.info("正在檢測 lobby_login 靜默檢測中")
        detection_results = self._continuous_detect_until_found(template_name, "lobby_login")
        
        # 3. 自動執行點擊
        self._auto_click("lobby_login", detection_results)
        
        # 4. 等待 lobby_login 消失
        self._wait_for_image_disappear(template_name)
        self.logger.info("lobby_login 已消失")
    
    def _handle_lobby_confirm(self, reference_browser: BrowserContext) -> None:
        """處理 lobby_confirm 的檢測與點擊。
        
        Args:
            reference_browser: 參考瀏覽器
        """
        template_name = Constants.LOBBY_CONFIRM
        
        # 1. 檢查模板是否存在
        if not self.image_detector.template_exists(template_name):
            self.logger.warning(f"模板圖片 {template_name} 不存在")
            self._prompt_capture_template(reference_browser, template_name, "lobby_confirm")
        else:
            self.logger.info(f"找到模板圖片 {template_name}")
        
        # 2. 持續檢測直到找到圖片
        self.logger.info("正在檢測 lobby_confirm 靜默檢測中")
        detection_results = self._continuous_detect_until_found(template_name, "lobby_confirm")
        
        # 3. 自動執行點擊
        self._auto_click("lobby_confirm", detection_results)
        
        # 4. 等待 lobby_confirm 消失
        self._wait_for_image_disappear(template_name)
        self.logger.info("lobby_confirm 已消失")
    
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
        
        while True:
            attempt += 1
            detection_results = self._detect_in_all_browsers(template_name, silent=True)
            found_count = sum(1 for result in detection_results if result is not None)
            
            if found_count > 0:
                # 顯示最終找到的座標
                for i, result in enumerate(detection_results, 1):
                    if result:
                        x, y, confidence = result
                        self.logger.info(f"瀏覽器 {i}/{len(self.browser_contexts)} 找到圖片 座標 {x} {y} 信心度 {confidence:.2f}")
                return detection_results
            
            # 每 20 次檢測顯示一次進度
            if attempt % 20 == 0:
                self.logger.info(f"持續檢測中 第 {attempt} 次 loading 中請稍候")
            
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
                
            except Exception as e:
                if not silent:
                    self.logger.error(f"瀏覽器 {i}/{len(self.browser_contexts)} 檢測失敗 {e}")
                results.append(None)
        
        return results
    
    def _auto_click(self, display_name: str, detection_results: List[Optional[Tuple[int, int, float]]]) -> None:
        """自動執行點擊操作。
        
        Args:
            display_name: 顯示名稱
            detection_results: 檢測結果列表
        """
        self.logger.info(f"找到 {display_name} 自動執行點擊操作")
        
        # TODO: 在所有瀏覽器中執行點擊
        # 這裡需要實現在 Canvas 中的實際點擊邏輯
        # 暫時只記錄座標
        click_count = sum(1 for result in detection_results if result is not None)
        self.logger.info(f"TODO 將在 {click_count} 個瀏覽器中執行點擊 實際點擊功能待實現")
    
    def _wait_for_image_disappear(self, template_name: str) -> None:
        """持續等待圖片在所有瀏覽器中消失。
        
        Args:
            template_name: 模板圖片檔名
        """
        attempt = 0
        
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
            
            # 如果所有瀏覽器都沒有找到圖片，則返回
            if not still_present:
                return
            
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
    try:
        app = AutoSlotGameApp()
        app.run()
    except Exception as e:
        logger = LoggerFactory.get_logger()
        logger.critical(f"應用程式執行失敗 {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
