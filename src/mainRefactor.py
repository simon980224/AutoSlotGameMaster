"""
金富翁遊戲自動化系統



作者: 凡臻科技
版本: 3.0.0
Python: 3.8+
"""

import logging
import sys
from typing import Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
import threading


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


class SimpleProxyServer:
    """簡易 Proxy 伺服器類別。
    
    提供基本的 HTTP Proxy 功能,可在背景執行緒中運行。
    
    Attributes:
        host: 伺服器監聽的主機位址
        port: 伺服器監聽的埠號
        server: HTTPServer 實例
        thread: 執行伺服器的執行緒
        logger: 日誌記錄器
    """
    
    def __init__(self, host: str = "127.0.0.1", port: int = 8888) -> None:
        """初始化 Proxy 伺服器。
        
        Args:
            host: 監聽的主機位址,預設為 127.0.0.1
            port: 監聽的埠號,預設為 8888
        """
        self.host = host
        self.port = port
        self.server: Optional[HTTPServer] = None
        self.thread: Optional[threading.Thread] = None
        self.logger = logging.getLogger("AutoSlotGame")
        self._running = False
    
    def start(self) -> bool:
        """啟動 Proxy 伺服器。
        
        在背景執行緒中啟動伺服器。
        
        Returns:
            True 表示啟動成功,False 表示啟動失敗
        """
        try:
            self.server = HTTPServer((self.host, self.port), ProxyRequestHandler)
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
            self._running = True
            self.logger.info(f"Proxy 伺服器已啟動於 {self.host}:{self.port}")
            return True
        except Exception as e:
            self.logger.error(f"Proxy 伺服器啟動失敗: {e}")
            return False
    
    def stop(self) -> None:
        """停止 Proxy 伺服器。"""
        if self.server and self._running:
            self.logger.info("正在停止 Proxy 伺服器...")
            self.server.shutdown()
            self.server.server_close()
            if self.thread:
                self.thread.join(timeout=5)
            self._running = False
            self.logger.info("Proxy 伺服器已停止")
    
    def is_running(self) -> bool:
        """檢查伺服器是否正在執行。
        
        Returns:
            True 表示伺服器正在執行,False 表示已停止
        """
        return self._running
    
    def get_proxy_url(self) -> str:
        """取得 Proxy 伺服器的 URL。
        
        Returns:
            Proxy 伺服器的完整 URL
        """
        return f"http://{self.host}:{self.port}"


def main() -> None:
    """主程式入口。
    
    初始化系統並執行主要邏輯,包含錯誤處理和資源清理。
    """
    logger = setup_logger()
    proxy_server = None
    
    logger.info("=== 金富翁遊戲自動化系統啟動 ===")
    
    try:
        # 示範:啟動 Proxy 伺服器
        proxy_server = SimpleProxyServer(host="127.0.0.1", port=8888)
        if proxy_server.start():
            logger.info(f"可使用 Proxy: {proxy_server.get_proxy_url()}")
        
        # TODO: 主程式邏輯將在這裡實作
        pass
    except KeyboardInterrupt:
        logger.warning("使用者中斷程式執行")
    except Exception as e:
        logger.error(f"系統發生錯誤: {e}", exc_info=True)
        raise
    finally:
        # 清理資源
        if proxy_server and proxy_server.is_running():
            proxy_server.stop()
        logger.info("=== 系統結束 ===")


if __name__ == "__main__":
    main()
