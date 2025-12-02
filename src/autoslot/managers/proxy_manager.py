#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Proxy 管理器模組

提供本機 Proxy 中繼伺服器功能，將帶認證的遠端 Proxy 轉換為本地無需認證的 Proxy。
採用執行緒安全和資源管理最佳實踐。
"""

import base64
import logging
import select
import socket
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import suppress
from typing import Dict, Optional

from ..core.constants import Constants
from ..core.exceptions import ProxyServerError
from ..core.models import ProxyInfo
from ..utils.logger import LoggerFactory


class ProxyConnectionHandler:
    """Proxy 連接處理器"""
    
    def __init__(
        self, 
        upstream_proxy: ProxyInfo,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化連接處理器
        
        Args:
            upstream_proxy: 上游 Proxy 資訊
            logger: 日誌記錄器
        """
        self.upstream_proxy = upstream_proxy
        self.logger = logger or LoggerFactory.get_logger()
    
    def handle_connect_request(
        self, 
        client_socket: socket.socket,
        request: bytes
    ) -> None:
        """
        處理 HTTPS CONNECT 請求
        
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
        """
        處理普通 HTTP 請求
        
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
        """
        雙向轉發數據
        
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
    簡易 HTTP Proxy 伺服器
    
    將帶認證的遠端 proxy 轉換為本地無需認證的 proxy。
    採用執行緒安全和良好的資源管理。
    """
    
    def __init__(
        self, 
        local_port: int, 
        upstream_proxy: ProxyInfo,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化 Proxy 伺服器
        
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
        """
        處理客戶端連接
        
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
        """
        啟動 proxy 伺服器
        
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
    """
    本機 Proxy 中繼伺服器管理器
    
    為每個瀏覽器建立獨立的本機 Proxy 埠，將請求轉發到上游 Proxy。
    採用執行緒安全和良好的資源管理。
    支援上下文管理器（with 語句）。
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
        """
        啟動本機 Proxy 中繼伺服器
        
        Args:
            upstream_proxy: 上游 Proxy 資訊
            
        Returns:
            本機埠號，失敗返回 None
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
                    self.logger.error(f"Proxy 伺服器執行失敗 埠 {local_port}: {e}")
            
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
            self.logger.error(f"啟動本機 Proxy 伺服器失敗: {e}")
            return None
    
    def stop_proxy_server(self, local_port: int) -> None:
        """
        停止指定的 proxy 伺服器
        
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
        """停止所有 proxy 伺服器"""
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
        """上下文管理器退出，自動清理資源"""
        self.stop_all_servers()
        return False
