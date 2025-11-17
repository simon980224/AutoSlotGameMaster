"""
簡易 HTTP Proxy 伺服器 (使用 Python 內建模組)
將帶認證的遠端 proxy 轉換為本地無需認證的 proxy
"""

import socket
import threading
import select
import requests
from urllib.parse import urlparse


class SimpleProxyServer:
    def __init__(self, local_port, upstream_proxy):
        """
        Args:
            local_port: 本地監聽端口
            upstream_proxy: 上游 proxy,格式 "ip:port:username:password"
        """
        self.local_port = local_port
        self.upstream_proxy = self.parse_proxy(upstream_proxy)
        self.running = False
        
    def parse_proxy(self, proxy_string):
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
    
    def handle_client(self, client_socket):
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
                    import base64
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
                        print(f"上游 Proxy 拒絕連接: {response[:100]}")
                        client_socket.send(b'HTTP/1.1 502 Bad Gateway\r\n\r\n')
                        upstream_socket.close()
                    
                else:
                    # 處理普通 HTTP 請求
                    # 添加 Proxy 認證頭
                    import base64
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
                    
            except Exception as e:
                print(f"處理請求錯誤: {e}")
                try:
                    client_socket.send(b'HTTP/1.1 502 Bad Gateway\r\n\r\n')
                except:
                    pass
                
        except Exception as e:
            print(f"客戶端處理錯誤: {e}")
        finally:
            try:
                client_socket.close()
            except:
                pass
    
    def forward_data(self, source, destination):
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
                        
        except Exception as e:
            pass  # 靜默處理斷線錯誤
    
    def start(self):
        """啟動 proxy 伺服器"""
        self.running = True
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            server_socket.bind(('127.0.0.1', self.local_port))
            server_socket.listen(5)
            
            print(f"\n{'='*60}")
            print(f"✓ Proxy 伺服器已啟動")
            print(f"  本地地址: 127.0.0.1:{self.local_port}")
            print(f"  上游 Proxy: {self.upstream_proxy['host']}:{self.upstream_proxy['port']}")
            print(f"  認證用戶: {self.upstream_proxy['username']}")
            print(f"{'='*60}")
            print(f"\n在 Selenium 中使用: 127.0.0.1:{self.local_port}")
            print(f"按 Ctrl+C 停止伺服器\n")
            
            while self.running:
                try:
                    server_socket.settimeout(1.0)
                    client_socket, address = server_socket.accept()
                    print(f"接受連接: {address}")
                    
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
            print(f"❌ 伺服器啟動失敗: {e}")
        finally:
            server_socket.close()
            print("\n伺服器已停止")


def main():
    """主函式"""
    import sys
    
    # 可用的 proxy 列表
    TEST_PROXIES = [
        "212.42.202.2:80:evuxkwoi-residential-TW-1:hsrmr72i08rc",
        "185.191.236.38:80:evuxkwoi-residential-TW-2:hsrmr72i08rc",
        "212.32.244.16:80:evuxkwoi-residential-TW-3:hsrmr72i08rc",
        "143.202.153.58:80:evuxkwoi-residential-TW-4:hsrmr72i08rc",
    ]
    
    print("簡易本地 Proxy 伺服器")
    print("="*60)
    print("\n可用的 Proxy:")
    for i, proxy in enumerate(TEST_PROXIES, 1):
        print(f"  {i}. {proxy.split(':')[0]}:{proxy.split(':')[1]}")
    
    # 選擇 proxy
    if len(sys.argv) > 2:
        proxy_index = int(sys.argv[1]) - 1
        local_port = int(sys.argv[2])
    elif len(sys.argv) > 1:
        proxy_index = int(sys.argv[1]) - 1
        local_port = 8888
    else:
        proxy_index = 0
        local_port = 8888
    
    if proxy_index < 0 or proxy_index >= len(TEST_PROXIES):
        print(f"\n❌ 無效的 proxy 索引: {proxy_index + 1}")
        return
    
    selected_proxy = TEST_PROXIES[proxy_index]
    print(f"\n選擇的 Proxy: #{proxy_index + 1}")
    print(f"本地端口: {local_port}\n")
    
    # 啟動伺服器
    server = SimpleProxyServer(local_port, selected_proxy)
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n\n正在停止伺服器...")
        server.running = False


if __name__ == "__main__":
    main()
