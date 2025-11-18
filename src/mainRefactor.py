"""
金富翁遊戲自動化系統



作者: 凡臻科技
版本: 3.0.0
Python: 3.8+
"""

import logging
import sys
import platform
import socket
import select
import base64
import time
from typing import Optional, List, Dict, Tuple, Any
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from dataclasses import dataclass
import requests
import threading

# Selenium WebDriver 相關
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager


@dataclass
class UserCredential:
    """使用者憑證資料結構。"""
    username: str
    password: str
    proxy: Optional[str] = None


@dataclass
class BetRule:
    """下注規則資料結構。"""
    amount: float
    duration: int  # 分鐘


@dataclass
class ProxyInfo:
    """Proxy 資訊資料結構。"""
    host: str
    port: int
    username: str
    password: str
    
    def to_url(self) -> str:
        """轉換為 Proxy URL 格式。
        
        Returns:
            格式化的 Proxy URL
        """
        return f"http://{self.username}:{self.password}@{self.host}:{self.port}"


class ConfigReader:
    """配置檔案讀取器。
    
    讀取並解析系統所需的各種配置檔案。
    
    Attributes:
        lib_path: 配置檔案所在目錄路徑
        logger: 日誌記錄器
    """
    
    def __init__(self, lib_path: str = None) -> None:
        """初始化配置讀取器。
        
        Args:
            lib_path: 配置檔案目錄路徑,預設為專案的 lib 目錄
        """
        if lib_path is None:
            # 預設使用專案根目錄下的 lib 資料夾
            project_root = Path(__file__).parent.parent
            lib_path = project_root / "lib"
        
        self.lib_path = Path(lib_path)
        self.logger = logging.getLogger("AutoSlotGame")
    
    def read_user_credentials(self, filename: str = "user_credentials.txt") -> List[UserCredential]:
        """讀取使用者憑證檔案。
        
        檔案格式: 帳號,密碼,proxy (首行為標題)
        
        Args:
            filename: 檔案名稱
            
        Returns:
            使用者憑證列表
        """
        file_path = self.lib_path / filename
        credentials = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
                # 跳過標題行
                for line in lines[1:]:
                    line = line.strip()
                    if not line:
                        continue
                    
                    parts = line.split(',')
                    if len(parts) >= 3:
                        credentials.append(UserCredential(
                            username=parts[0].strip(),
                            password=parts[1].strip(),
                            proxy=parts[2].strip()
                        ))
            
            self.logger.info(f"成功讀取 {len(credentials)} 筆使用者憑證")
            return credentials
            
        except FileNotFoundError:
            self.logger.error(f"找不到檔案: {file_path}")
            return []
        except Exception as e:
            self.logger.error(f"讀取使用者憑證失敗: {e}")
            return []
    
    def read_bet_rules(self, filename: str = "user_rules.txt") -> List[BetRule]:
        """讀取下注規則檔案。
        
        檔案格式: 金額:時間(分鐘) (首行為標題)
        
        Args:
            filename: 檔案名稱
            
        Returns:
            下注規則列表
        """
        file_path = self.lib_path / filename
        rules = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
                # 跳過標題行
                for line in lines[1:]:
                    line = line.strip()
                    if not line:
                        continue
                    
                    parts = line.split(':')
                    if len(parts) >= 2:
                        try:
                            amount = float(parts[0].strip())
                            duration = int(parts[1].strip())
                            rules.append(BetRule(amount=amount, duration=duration))
                        except ValueError as e:
                            self.logger.warning(f"無法解析規則行: {line} - {e}")
            
            self.logger.info(f"成功讀取 {len(rules)} 條下注規則")
            return rules
            
        except FileNotFoundError:
            self.logger.error(f"找不到檔案: {file_path}")
            return []
        except Exception as e:
            self.logger.error(f"讀取下注規則失敗: {e}")
            return []
    
    def read_proxies(self, filename: str = "user_proxys.txt") -> List[ProxyInfo]:
        """讀取 Proxy 列表檔案。
        
        檔案格式: host:port:username:password
        
        Args:
            filename: 檔案名稱
            
        Returns:
            Proxy 資訊列表
        """
        file_path = self.lib_path / filename
        proxies = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    parts = line.split(':')
                    if len(parts) >= 4:
                        try:
                            proxies.append(ProxyInfo(
                                host=parts[0].strip(),
                                port=int(parts[1].strip()),
                                username=parts[2].strip(),
                                password=parts[3].strip()
                            ))
                        except ValueError as e:
                            self.logger.warning(f"無法解析 Proxy 行: {line} - {e}")
            
            self.logger.info(f"成功讀取 {len(proxies)} 個 Proxy")
            return proxies
            
        except FileNotFoundError:
            self.logger.error(f"找不到檔案: {file_path}")
            return []
        except Exception as e:
            self.logger.error(f"讀取 Proxy 列表失敗: {e}")
            return []
    
    def read_user_data(self, filename: str = "用戶資料.txt") -> List[Dict[str, str]]:
        """讀取用戶資料檔案(舊格式相容)。
        
        檔案格式: 帳號:密碼:IP:port:user:password (首行為標題)
        
        Args:
            filename: 檔案名稱
            
        Returns:
            用戶資料字典列表
        """
        file_path = self.lib_path / filename
        users = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
                # 跳過標題行
                for line in lines[1:]:
                    line = line.strip()
                    if not line:
                        continue
                    
                    parts = line.split(',')
                    if len(parts) >= 2:
                        # 解析 proxy 部分
                        proxy_parts = parts[1].split(':') if len(parts) > 1 else []
                        
                        user_data = {
                            'username': parts[0].strip(),
                            'password': parts[1].strip() if len(parts) > 1 else '',
                        }
                        
                        # 如果有 proxy 資訊
                        if len(proxy_parts) >= 4:
                            user_data['proxy_host'] = proxy_parts[0].strip()
                            user_data['proxy_port'] = proxy_parts[1].strip()
                            user_data['proxy_user'] = proxy_parts[2].strip()
                            user_data['proxy_pass'] = proxy_parts[3].strip()
                        
                        users.append(user_data)
            
            self.logger.info(f"成功讀取 {len(users)} 筆用戶資料")
            return users
            
        except FileNotFoundError:
            self.logger.error(f"找不到檔案: {file_path}")
            return []
        except Exception as e:
            self.logger.error(f"讀取用戶資料失敗: {e}")
            return []


class ColoredFormatter(logging.Formatter):
    """帶顏色的日誌格式化器。
    
    使用 ANSI 顏色碼為不同等級的日誌訊息添加顏色。
    """
    
    # ANSI 顏色碼
    RESET = "\033[0m"
    INFO = "\033[32m"       # 綠色
    WARNING = "\033[33m"    # 黃色
    ERROR = "\033[31m"      # 紅色
    TIMESTAMP = "\033[90m"  # 灰色
    
    def __init__(self, fmt: Optional[str] = None, datefmt: Optional[str] = None) -> None:
        """初始化顏色格式化器。
        
        Args:
            fmt: 日誌格式字串
            datefmt: 日期格式字串
        """
        super().__init__(fmt, datefmt)
        self.formatters = {
            logging.INFO: logging.Formatter(
                f"{self.TIMESTAMP}%(asctime)s{self.RESET} - "
                f"{self.INFO}%(levelname)-8s{self.RESET} - "
                f"%(message)s"
            ),
            logging.WARNING: logging.Formatter(
                f"{self.TIMESTAMP}%(asctime)s{self.RESET} - "
                f"{self.WARNING}%(levelname)-8s{self.RESET} - "
                f"%(message)s"
            ),
            logging.ERROR: logging.Formatter(
                f"{self.TIMESTAMP}%(asctime)s{self.RESET} - "
                f"{self.ERROR}%(levelname)-8s{self.RESET} - "
                f"%(message)s"
            ),
        }
    
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


def setup_logger() -> logging.Logger:
    """設定並返回配置好的 logger。
    
    建立控制台輸出的日誌系統,輸出帶顏色。
    
    Returns:
        配置完成的 Logger 物件
    """
    logger = logging.getLogger("AutoSlotGame")
    logger.setLevel(logging.INFO)
    
    # 避免重複添加 handler
    if logger.handlers:
        return logger
    
    # 控制台 handler (帶顏色)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(ColoredFormatter())
    
    logger.addHandler(console_handler)
    
    return logger


class ProxyRequestHandler(BaseHTTPRequestHandler):
    """簡易 HTTP Proxy 請求處理器。
    
    處理 HTTP GET/POST 請求並轉發到目標伺服器。
    """
    
    def log_message(self, format: str, *args) -> None:
        """重寫日誌方法以使用自定義 logger。
        
        Args:
            format: 日誌格式字串
            *args: 格式化參數
        """
        logger = logging.getLogger("AutoSlotGame")
        logger.info(f"Proxy: {format % args}")
    
    def do_GET(self) -> None:
        """處理 GET 請求。"""
        self._proxy_request("GET")
    
    def do_POST(self) -> None:
        """處理 POST 請求。"""
        self._proxy_request("POST")
    
    def _proxy_request(self, method: str) -> None:
        """轉發請求到目標伺服器。
        
        Args:
            method: HTTP 方法 (GET/POST)
        """
        try:
            # 解析目標 URL
            url = self.path
            if not url.startswith('http'):
                url = f"http://{self.headers.get('Host', '')}{url}"
            
            # 準備標頭
            headers = {key: val for key, val in self.headers.items() 
                      if key.lower() not in ['host', 'connection']}
            
            # 讀取請求內容
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else None
            
            # 發送請求
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                data=body,
                allow_redirects=False,
                timeout=30
            )
            
            # 返回響應
            self.send_response(response.status_code)
            for key, val in response.headers.items():
                if key.lower() not in ['connection', 'transfer-encoding']:
                    self.send_header(key, val)
            self.end_headers()
            self.wfile.write(response.content)
            
        except Exception as e:
            logger = logging.getLogger("AutoSlotGame")
            logger.error(f"Proxy 請求失敗: {e}")
            self.send_error(500, f"Proxy Error: {str(e)}")


class BrowserManager:
    """瀏覽器管理器。
    
    提供 WebDriver 建立和配置功能,支援自動和手動驅動程式管理。
    """
    
    @staticmethod
    def create_chrome_options(local_proxy_port: Optional[int] = None) -> Options:
        """建立 Chrome 瀏覽器選項。
        
        Args:
            local_proxy_port: 本機 proxy 中繼埠號（可選）
            
        Returns:
            Options: 配置好的 Chrome 選項
        """
        logger = logging.getLogger("AutoSlotGame")
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
        })
        
        return chrome_options
    
    @staticmethod
    def create_webdriver(local_proxy_port: Optional[int] = None) -> WebDriver:
        """建立 WebDriver 實例。
        
        優先使用 WebDriver Manager 自動管理驅動程式，
        若失敗則嘗試使用專案內的驅動程式檔案作為備援。
        
        Args:
            local_proxy_port: 本機 proxy 中繼埠號（可選）
            
        Returns:
            WebDriver: WebDriver 實例
            
        Raises:
            Exception: 當所有方法都失敗時
        """
        logger = logging.getLogger("AutoSlotGame")
        chrome_options = BrowserManager.create_chrome_options(local_proxy_port)
        driver = None
        
        # 方法 1: 使用 WebDriver Manager 自動管理
        try:
            logger.info("正在使用 WebDriver Manager 取得 ChromeDriver...")
            service = Service(ChromeDriverManager().install())
            logger.info("正在啟動 Chrome 瀏覽器...")
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # 取得 Chrome 版本
            try:
                chrome_version = driver.capabilities.get('browserVersion', 'unknown')
                logger.info(f"Chrome 版本: {chrome_version}")
            except Exception:
                pass
            
            logger.info("✓ 瀏覽器實例已建立 (使用 WebDriver Manager)")
            
        except Exception as e:
            logger.warning(f"WebDriver Manager 失敗: {e}")
            logger.info("嘗試使用專案內驅動程式作為備援...")
            
            # 方法 2: 使用專案內的驅動程式檔案
            try:
                driver = BrowserManager._create_webdriver_with_local_driver(
                    chrome_options
                )
                logger.info("✓ 瀏覽器實例已建立 (使用本機驅動程式)")
                
            except Exception as e2:
                logger.error(f"本機驅動程式也失敗: {e2}")
                raise Exception(
                    f"無法建立瀏覽器實例。\n"
                    f"WebDriver Manager 錯誤: {e}\n"
                    f"本機驅動程式錯誤: {e2}"
                )
        
        if driver is None:
            raise Exception("無法建立瀏覽器實例")
        
        # 設定超時（可依需求調整）
        driver.set_page_load_timeout(600)
        driver.set_script_timeout(600)
        driver.implicitly_wait(60)
        
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
            logger.warning(f"網路優化設定失敗: {e}")
        
        logger.info("✓ 瀏覽器設定完成")
        return driver
    
    @staticmethod
    def _create_webdriver_with_local_driver(chrome_options: Options) -> WebDriver:
        """使用專案內的驅動程式檔案建立 WebDriver。
        
        根據作業系統自動選擇正確的驅動程式檔案。
        
        Args:
            chrome_options: Chrome 選項
            
        Returns:
            WebDriver: WebDriver 實例
            
        Raises:
            Exception: 當驅動程式不存在或無法啟動時
        """
        logger = logging.getLogger("AutoSlotGame")
        
        # 取得專案根目錄
        if getattr(sys, 'frozen', False):
            project_root = Path(sys.executable).resolve().parent
        else:
            project_root = Path(__file__).resolve().parent.parent
        
        # 根據作業系統選擇驅動程式
        system = platform.system().lower()
        if system == "windows":
            driver_filename = "chromedriver.exe"
        elif system == "darwin":  # macOS
            driver_filename = "chromedriver"
        else:  # Linux
            driver_filename = "chromedriver"
        
        driver_path = project_root / driver_filename
        
        if not driver_path.exists():
            raise FileNotFoundError(
                f"找不到驅動程式檔案: {driver_path}\n"
                f"請確保 {driver_filename} 存在於專案根目錄"
            )
        
        logger.info(f"使用本機驅動程式: {driver_path}")
        
        # 確保驅動程式有執行權限 (Unix-like 系統)
        if system in ["darwin", "linux"]:
            import os
            os.chmod(driver_path, 0o755)
        
        service = Service(str(driver_path))
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        return driver


class SimpleProxyServer:
    """
    簡易 HTTP Proxy 伺服器 (使用 Python 內建模組)
    將帶認證的遠端 proxy 轉換為本地無需認證的 proxy
    """
    
    def __init__(self, local_port: int, upstream_proxy: str):
        """
        Args:
            local_port: 本地監聽端口
            upstream_proxy: 上游 proxy,格式 "ip:port:username:password"
        """
        self.local_port = local_port
        self.upstream_proxy = self.parse_proxy(upstream_proxy)
        self.running = False
        
    def parse_proxy(self, proxy_string: str) -> dict:
        """解析 proxy 字串"""
        parts = proxy_string.split(':')
        ip = parts[0]
        port = int(parts[1])
        remaining = ':'.join(parts[2:])
        last_colon_index = remaining.rfind(':')
        username = remaining[:last_colon_index]
        password = remaining[last_colon_index + 1:]
        
        return {
            'host': ip,
            'port': port,
            'username': username,
            'password': password,
            'url': f"http://{username}:{password}@{ip}:{port}"
        }
    
    def handle_client(self, client_socket: socket.socket) -> None:
        """處理客戶端連接"""
        try:
            # 接收客戶端請求
            request = client_socket.recv(4096)
            if not request:
                return
            
            # 解析請求
            first_line = request.split(b'\r\n')[0].decode('utf-8', errors='ignore')
            
            # 使用 requests 透過上游 proxy 發送請求
            try:
                # 簡單處理 CONNECT 請求 (HTTPS)
                if first_line.startswith('CONNECT'):
                    # 建立到上游 proxy 的連接
                    upstream_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    upstream_socket.connect((self.upstream_proxy['host'], self.upstream_proxy['port']))
                    
                    # 構建帶認證的 CONNECT 請求
                    auth_string = f"{self.upstream_proxy['username']}:{self.upstream_proxy['password']}"
                    auth_bytes = auth_string.encode('utf-8')
                    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
                    
                    # 修改請求,添加認證頭
                    request_lines = request.split(b'\r\n')
                    auth_header = f"Proxy-Authorization: Basic {auth_b64}\r\n".encode('utf-8')
                    
                    # 重建請求
                    new_request = request_lines[0] + b'\r\n' + auth_header
                    for line in request_lines[1:]:
                        new_request += line + b'\r\n'
                    
                    # 發送帶認證的 CONNECT 請求到上游 proxy
                    upstream_socket.send(new_request)
                    
                    # 等待上游 proxy 回應
                    response = upstream_socket.recv(4096)
                    if b'200' in response:
                        # 告訴客戶端連接成功
                        client_socket.send(b'HTTP/1.1 200 Connection Established\r\n\r\n')
                        
                        # 雙向轉發數據
                        self.forward_data(client_socket, upstream_socket)
                    else:
                        client_socket.send(b'HTTP/1.1 502 Bad Gateway\r\n\r\n')
                        upstream_socket.close()
                    
                else:
                    # 處理普通 HTTP 請求
                    # 添加 Proxy 認證頭
                    auth_string = f"{self.upstream_proxy['username']}:{self.upstream_proxy['password']}"
                    auth_bytes = auth_string.encode('utf-8')
                    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
                    
                    request_lines = request.split(b'\r\n')
                    auth_header = f"Proxy-Authorization: Basic {auth_b64}\r\n".encode('utf-8')
                    
                    # 重建請求
                    new_request = request_lines[0] + b'\r\n' + auth_header
                    for line in request_lines[1:]:
                        new_request += line + b'\r\n'
                    
                    # 透過上游 proxy 發送
                    upstream_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    upstream_socket.connect((self.upstream_proxy['host'], self.upstream_proxy['port']))
                    upstream_socket.send(new_request)
                    
                    # 接收回應並轉發給客戶端
                    response = upstream_socket.recv(4096)
                    while response:
                        client_socket.send(response)
                        response = upstream_socket.recv(4096)
                    
                    upstream_socket.close()
                    
            except Exception:
                try:
                    client_socket.send(b'HTTP/1.1 502 Bad Gateway\r\n\r\n')
                except:
                    pass
                
        except Exception:
            pass
        finally:
            try:
                client_socket.close()
            except:
                pass
    
    def forward_data(self, source: socket.socket, destination: socket.socket) -> None:
        """雙向轉發數據"""
        try:
            while True:
                ready_sockets, _, _ = select.select([source, destination], [], [], 1)
                
                if not ready_sockets:
                    continue
                    
                for sock in ready_sockets:
                    try:
                        data = sock.recv(4096)
                        if not data:
                            return
                        
                        if sock is source:
                            destination.send(data)
                        else:
                            source.send(data)
                    except:
                        return
                        
        except Exception:
            pass  # 靜默處理斷線錯誤
    
    def start(self) -> None:
        """啟動 proxy 伺服器"""
        self.running = True
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            server_socket.bind(('127.0.0.1', self.local_port))
            server_socket.listen(5)
            
            while self.running:
                try:
                    server_socket.settimeout(1.0)
                    client_socket, address = server_socket.accept()
                    
                    # 在新線程中處理客戶端
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket,)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.timeout:
                    continue
                except KeyboardInterrupt:
                    break
                    
        except Exception as e:
            raise Exception(f"伺服器啟動失敗: {e}")
        finally:
            server_socket.close()


class LocalProxyServerManager:
    """本機 Proxy 中繼伺服器管理器。
    
    為每個瀏覽器建立獨立的本機 Proxy 埠,將請求轉發到上游 Proxy。
    """
    
    _proxy_servers: Dict[int, Any] = {}
    _proxy_threads: Dict[int, threading.Thread] = {}
    _next_port: int = 9000
    _lock = threading.Lock()
    
    @staticmethod
    def start_proxy_server(upstream_proxy: str) -> Optional[int]:
        """啟動本機 Proxy 中繼伺服器。
        
        Args:
            upstream_proxy: 上游 Proxy 字串,格式為 "ip:port:user:pass"
            
        Returns:
            本機埠號,失敗返回 None
        """
        logger = logging.getLogger("AutoSlotGame")
        
        with LocalProxyServerManager._lock:
            local_port = LocalProxyServerManager._next_port
            LocalProxyServerManager._next_port += 1
        
        try:
            # 解析上游 Proxy
            parts = upstream_proxy.split(':')
            if len(parts) != 4:
                logger.error(f"Proxy 格式錯誤: {upstream_proxy}")
                return None
            
            proxy_host, proxy_port, proxy_user, proxy_pass = parts
            
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
            
            logger.info(f"啟動本機 Proxy 中繼: 127.0.0.1:{local_port} -> {proxy_host}:{proxy_port}")
            return local_port
            
        except Exception as e:
            logger.error(f"啟動本機 Proxy 伺服器失敗: {e}")
            return None
    
    @staticmethod
    def stop_proxy_server(local_port: int) -> None:
        """停止指定的 proxy 伺服器"""
        if local_port in LocalProxyServerManager._proxy_servers:
            server = LocalProxyServerManager._proxy_servers[local_port]
            server.running = False
            logger = logging.getLogger("AutoSlotGame")
            logger.info(f"已停止本機 Proxy 伺服器: 127.0.0.1:{local_port}")
            del LocalProxyServerManager._proxy_servers[local_port]
            if local_port in LocalProxyServerManager._proxy_threads:
                del LocalProxyServerManager._proxy_threads[local_port]
    
    @staticmethod
    def stop_all_servers() -> None:
        """停止所有 proxy 伺服器"""
        logger = logging.getLogger("AutoSlotGame")
        if LocalProxyServerManager._proxy_servers:
            logger.info(f"清理 {len(LocalProxyServerManager._proxy_servers)} 個 Proxy 中繼伺服器")
            for local_port in list(LocalProxyServerManager._proxy_servers.keys()):
                LocalProxyServerManager.stop_proxy_server(local_port)


def main() -> None:
    """主程式入口。
    
    初始化系統並執行主要邏輯,包含錯誤處理和資源清理。
    """
    logger = setup_logger()
    drivers = []  # 儲存所有瀏覽器實例
    
    logger.info("=== 金富翁遊戲自動化系統啟動 ===")
    
    try:
        # 讀取配置檔案
        config_reader = ConfigReader()
        
        # 讀取使用者憑證
        credentials = config_reader.read_user_credentials()
        logger.info(f"載入 {len(credentials)} 個使用者帳號")
        
        # 讀取下注規則
        rules = config_reader.read_bet_rules()
        logger.info(f"載入 {len(rules)} 條下注規則")
        
        # 讀取 Proxy 列表
        proxies = config_reader.read_proxies()
        if proxies:
            logger.info(f"載入 {len(proxies)} 個 Proxy")
        
        # 詢問使用者要開啟幾個瀏覽器
        logger.info("\n" + "="*50)
        max_browsers = len(credentials)
        
        while True:
            try:
                user_input = input(f"請輸入要開啟的瀏覽器數量 (1-{max_browsers}): ").strip()
                browser_count = int(user_input)
                
                if 1 <= browser_count <= max_browsers:
                    break
                else:
                    logger.warning(f"請輸入 1 到 {max_browsers} 之間的數字")
            except ValueError:
                logger.warning("請輸入有效的數字")
            except (EOFError, KeyboardInterrupt):
                logger.warning("\n使用者取消輸入")
                return
        
        logger.info(f"\n將開啟 {browser_count} 個瀏覽器實例")
        logger.info("="*50 + "\n")
        
        # 建立瀏覽器實例
        for i in range(browser_count):
            try:
                credential = credentials[i]
                logger.info(f"[{i+1}/{browser_count}] 正在建立瀏覽器 (帳號: {credential.username})")
                
                local_proxy_port = None
                
                # 如果使用者有設定 Proxy,則啟動本機 Proxy 中繼
                if credential.proxy:
                    logger.info(f"[{i+1}/{browser_count}] 正在配置 Proxy: {credential.proxy.split(':')[0]}:***")
                    local_proxy_port = LocalProxyServerManager.start_proxy_server(credential.proxy)
                    
                    if local_proxy_port:
                        logger.info(f"[{i+1}/{browser_count}] ✓ Proxy 中繼已啟動於埠 {local_proxy_port}")
                    else:
                        logger.warning(f"[{i+1}/{browser_count}] Proxy 啟動失敗,將不使用 Proxy")
                
                # 建立瀏覽器 (如果有 Proxy 則使用)
                driver = BrowserManager.create_webdriver(local_proxy_port=local_proxy_port)
                
                drivers.append({
                    'driver': driver,
                    'credential': credential,
                    'index': i + 1,
                    'proxy_port': local_proxy_port
                })
                
                proxy_info = f" (使用 Proxy: 埠 {local_proxy_port})" if local_proxy_port else " (無 Proxy)"
                logger.info(f"[{i+1}/{browser_count}] ✓ 瀏覽器建立成功{proxy_info}")
                
            except Exception as e:
                logger.error(f"[{i+1}/{browser_count}] 建立瀏覽器失敗: {e}")
                continue
        
        logger.info(f"\n✓ 成功建立 {len(drivers)} 個瀏覽器實例")
        
        # TODO: 在這裡實作後續的自動化邏輯
        # 例如: 登入、遊戲操作等
        
        # 暫停,讓使用者可以觀察
        input("\n按 Enter 鍵關閉所有瀏覽器...")
        
        # 關閉所有瀏覽器
        logger.info("\n正在關閉所有瀏覽器...")
        for browser_info in drivers:
            try:
                browser_info['driver'].quit()
                logger.info(f"✓ 已關閉瀏覽器 (帳號: {browser_info['credential'].username})")
            except Exception as e:
                logger.warning(f"關閉瀏覽器時發生錯誤: {e}")
        
        logger.info("✓ 所有瀏覽器已關閉")
    except KeyboardInterrupt:
        logger.warning("使用者中斷程式執行")
    except Exception as e:
        logger.error(f"系統發生錯誤: {e}", exc_info=True)
        raise
    finally:
        # 清理資源
        # 清理所有 Proxy 中繼伺服器
        LocalProxyServerManager.stop_all_servers()
        
        logger.info("=== 系統結束 ===")


if __name__ == "__main__":
    main()
