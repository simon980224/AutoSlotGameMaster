"""
AutoSlot 核心模組

提供系統核心功能，包括：
- 常數定義 (Constants)
- 例外類別 (Exceptions)
- 資料模型 (Data Models)
"""

from .constants import Constants
from .exceptions import (
    AutoSlotGameError,
    ConfigurationError,
    BrowserCreationError,
    ProxyServerError,
    ImageDetectionError,
)
from .models import (
    UserCredential,
    BetRule,
    ProxyInfo,
    BrowserContext,
    OperationResult,
)

__all__ = [
    # 常數
    "Constants",
    # 例外
    "AutoSlotGameError",
    "ConfigurationError",
    "BrowserCreationError",
    "ProxyServerError",
    "ImageDetectionError",
    # 資料模型
    "UserCredential",
    "BetRule",
    "ProxyInfo",
    "BrowserContext",
    "OperationResult",
]
