"""
資料模型定義

定義系統中使用的資料結構。
"""

import time
from dataclasses import dataclass, field
from typing import Optional, Any
from selenium.webdriver.chrome.webdriver import WebDriver


@dataclass(frozen=True)
class UserCredential:
    """使用者憑證資料結構（不可變）"""
    username: str
    password: str
    proxy: Optional[str] = None
    
    def __post_init__(self) -> None:
        """驗證資料完整性"""
        if not self.username or not self.password:
            raise ValueError("使用者名稱和密碼不能為空")


@dataclass(frozen=True)
class BetRule:
    """下注規則資料結構（不可變）
    
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
            pass
        
        else:
            raise ValueError(f"無效的規則類型: {self.rule_type}，必須是 'a'、's' 或 'f'")


@dataclass(frozen=True)
class ProxyInfo:
    """Proxy 資訊資料結構（不可變）"""
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
        """轉換為 Proxy URL 格式"""
        return f"http://{self.username}:{self.password}@{self.host}:{self.port}"
    
    def to_connection_string(self) -> str:
        """轉換為連接字串格式"""
        return f"{self.host}:{self.port}:{self.username}:{self.password}"
    
    def __str__(self) -> str:
        """字串表示（隱藏敏感資訊）"""
        return f"ProxyInfo({self.host}:{self.port}, user={self.username[:3]}***)"
    
    @staticmethod
    def from_connection_string(connection_string: str) -> 'ProxyInfo':
        """從連接字串建立 ProxyInfo 實例"""
        parts = connection_string.split(':')
        if len(parts) < 4:
            raise ValueError(f"Proxy 連接字串格式不正確: {connection_string}")
        
        return ProxyInfo(
            host=parts[0],
            port=int(parts[1]),
            username=parts[2],
            password=':'.join(parts[3:])
        )


@dataclass
class BrowserContext:
    """瀏覽器上下文資訊"""
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
