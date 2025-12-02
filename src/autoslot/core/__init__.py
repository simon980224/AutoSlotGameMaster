"""
核心模組初始化

導出核心資料模型、常數和例外。
"""

from .constants import Constants
from .exceptions import (
    AutoSlotGameError,
    ConfigurationError,
    BrowserCreationError,
    ProxyServerError,
    ImageDetectionError
)
from .models import (
    UserCredential,
    BetRule,
    ProxyInfo,
    BrowserContext,
    OperationResult
)

__all__ = [
    # 常數
    'Constants',
    # 例外
    'AutoSlotGameError',
    'ConfigurationError',
    'BrowserCreationError',
    'ProxyServerError',
    'ImageDetectionError',
    # 資料模型
    'UserCredential',
    'BetRule',
    'ProxyInfo',
    'BrowserContext',
    'OperationResult',
]
