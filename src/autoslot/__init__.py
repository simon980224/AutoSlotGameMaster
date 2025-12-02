"""
AutoSlotGame 套件初始化

金富翁遊戲自動化系統 - 模組化架構

版本: 2.0.0
"""

# 核心模組
from .core import (
    Constants,
    AutoSlotGameError,
    ConfigurationError,
    BrowserCreationError,
    ProxyServerError,
    ImageDetectionError,
    UserCredential,
    BetRule,
    ProxyInfo,
    BrowserContext,
    OperationResult,
)

# 工具模組
from .utils import (
    LogLevel,
    LoggerFactory,
    cleanup_chromedriver_processes,
    get_resource_path,
    cv2_imread_unicode,
)

# 配置模組
from .config import ConfigReader

# 管理器模組
from .managers import (
    BrowserHelper,
    BrowserManager,
    LocalProxyServerManager,
    ProxyConnectionHandler,
    SimpleProxyServer,
)

__version__ = "2.0.0"

__all__ = [
    # 版本
    '__version__',
    # 核心 - 常數
    'Constants',
    # 核心 - 例外
    'AutoSlotGameError',
    'ConfigurationError',
    'BrowserCreationError',
    'ProxyServerError',
    'ImageDetectionError',
    # 核心 - 資料模型
    'UserCredential',
    'BetRule',
    'ProxyInfo',
    'BrowserContext',
    'OperationResult',
    # 工具
    'LogLevel',
    'LoggerFactory',
    'cleanup_chromedriver_processes',
    'get_resource_path',
    'cv2_imread_unicode',
    # 配置
    'ConfigReader',
    # 管理器
    'BrowserHelper',
    'BrowserManager',
    'LocalProxyServerManager',
    'ProxyConnectionHandler',
    'SimpleProxyServer',
]
