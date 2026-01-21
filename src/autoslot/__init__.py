"""
AutoSlotGameMaster - 金富翁遊戲自動化系統

版本: 2.0.0

核心特性:
- 模組化架構設計
- 完整型別提示與協議 (Protocol)
- 上下文管理器與資源自動清理
- 依賴注入與工廠模式
- 執行緒池並行處理
- 本地 Proxy 中繼伺服器
- 圖片識別與自動化操作
- 多瀏覽器實例管理
- 彩色日誌系統
- 完善的錯誤處理與重試機制

模組結構:
    core/           # 核心模組（常數、例外、資料模型）
    utils/          # 工具模組（日誌、輔助函式）
    config/         # 配置模組（配置讀取）
    managers/       # 管理器模組（瀏覽器、Proxy、輔助工具）
    operators/      # 操作器模組（待遷移）
    detectors/      # 檢測器模組（待遷移）
    app/            # 應用程式模組（待遷移）

使用方式:
    from autoslot import (
        Constants,              # 核心常數
        LoggerFactory,         # 日誌工廠
        ConfigReader,          # 配置讀取
        UserCredential,        # 使用者憑證
        BetRule,              # 下注規則
        ProxyInfo,            # Proxy 資訊
        BrowserContext,       # 瀏覽器上下文
        OperationResult,      # 操作結果
    )

作者: 凡臻科技
Python: 3.8+

版本歷史:
- v2.0.0: 模組化重構（將單一檔案拆分為多個模組，提升可維護性和可擴展性）
- v1.27.0: 優化 Proxy 配置管理
- v1.26.1: 簡化登入後公告處理邏輯
- v1.26.0: 移除錯誤訊息自動檢測功能
- v1.25.0: 優化登入彈窗檢測邏輯
- v1.24.1: 優化登入流程穩定性
- v1.24.0: 新增登入失敗自動重試機制
- v1.23.0: 優化登入流程與修復緩衝阻塞問題
- v1.22.1: 優化等待時間與自動跳過間隔
- v1.22.0: 優化登入與恢復流程
- v1.21.1: 優化黑屏恢復流程
- v1.21.0: 優化規則執行結束流程
- v1.20.0: 新增 lobby_return 檢測與自動恢復功能
"""

__version__ = "2.0.0"
__author__ = "凡臻科技"

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
    ColoredFormatter,
    FlushingStreamHandler,
    LoggerFactory,
    cleanup_chromedriver_processes,
    get_resource_path,
    cv2_imread_unicode,
)

# 配置模組
from .config import (
    ConfigReader,
    ConfigReaderProtocol,
)

# 管理器模組（暫時為空，後續版本會遷移）
# from .managers import ...

# 操作器模組（暫時為空，後續版本會遷移）
# from .operators import ...

# 檢測器模組（暫時為空，後續版本會遷移）
# from .detectors import ...

# 應用程式模組（暫時為空，後續版本會遷移）
# from .app import ...

__all__ = [
    # 版本資訊
    "__version__",
    "__author__",
    
    # 核心常數
    "Constants",
    
    # 例外類別
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
    
    # 日誌系統
    "LogLevel",
    "ColoredFormatter",
    "FlushingStreamHandler",
    "LoggerFactory",
    
    # 輔助函式
    "cleanup_chromedriver_processes",
    "get_resource_path",
    "cv2_imread_unicode",
    
    # 配置讀取
    "ConfigReader",
    "ConfigReaderProtocol",
]
