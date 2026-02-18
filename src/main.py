"""戰神賽特自動化系統。

此模組提供完整的遊戲自動化功能，採用模組化架構設計，
支援多視窗同步操作、智慧圖片識別、網路代理中繼等核心功能。

功能特點:
    - 多視窗同步管理：支援同時操控多個遊戲視窗
    - 智慧圖片識別：基於 OpenCV 的畫面自動辨識
    - 網路代理支援：可設定獨立的網路出口
    - 互動式控制面板：便捷的命令列操作介面
    - 異常監控與自動恢復：掉線偵測、錯誤自動處理

系統需求:
    - Python 3.8+
    - Selenium 4.25+
    - OpenCV (opencv-python)
    - Pillow
    - webdriver-manager

使用方式:
    直接執行此檔案即可啟動系統::

        $ python main_refactor.py

版本資訊:
    版本: 2.0.6
    作者: 凡臻科技
    授權: MIT License

"""

# =============================================================================
# 標準庫
# =============================================================================
import base64
import io
import logging
import os
import select
import socket
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager, suppress
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Protocol, Set, Tuple, Union

# =============================================================================
# 全域輸出緩衝設置 - 避免多執行緒環境下的輸出阻塞
# =============================================================================
os.environ['PYTHONUNBUFFERED'] = '1'

# 強制設置 stdout/stderr 為行緩衝模式（如果支援的話）
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
if hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(line_buffering=True)
    except Exception:
        pass

# =============================================================================
# 第三方庫 - 圖片處理
# =============================================================================
import cv2
import numpy as np
from PIL import Image

# =============================================================================
# 第三方庫 - Selenium WebDriver
# =============================================================================
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


# =============================================================================
# 常量定義
# =============================================================================


class Constants:
    """系統常量配置。

    集中管理所有魔法數字和配置值，避免硬編碼。
    所有常量按功能分組，並提供詳細的註解說明。

    常量分類:
        版本資訊: 系統版本與名稱
        配置檔案: 檔案路徑與名稱
        代理伺服器: Proxy 相關設定
        超時配置: 各類操作超時時間
        網路容錯: 重試次數與間隔
        視窗配置: 瀏覽器視窗尺寸與排列
        圖片檢測: 模板匹配相關參數
        遊戲金額: 可用下注金額列表
    """
    
    # =========================================================================
    # 版本資訊
    # =========================================================================
    VERSION: str = "2.0.6"
    SYSTEM_NAME: str = "戰神賽特自動化系統"
    
    # =========================================================================
    # 日誌格式配置
    # =========================================================================
    LOG_SEPARATOR: str = "=" * 60     # 日誌分隔線（主要分隔）
    LOG_SEPARATOR_LIGHT: str = "-" * 60  # 日誌分隔線（次要分隔）
    LOG_INDENT: str = "       "       # 日誌縮排前綴（7 個空格）
    LOG_BULLET: str = "  •"           # 日誌項目符號
    
    # =========================================================================
    # 配置檔案路徑
    # =========================================================================
    DEFAULT_LIB_PATH: str = "lib"
    DEFAULT_CREDENTIALS_FILE: str = "用戶資料.txt"
    DEFAULT_RULES_FILE: str = "用戶規則.txt"
    
    # =========================================================================
    # 代理伺服器配置
    # =========================================================================
    DEFAULT_PROXY_START_PORT: int = 9000
    PROXY_SERVER_BIND_HOST: str = "127.0.0.1"
    PROXY_BUFFER_SIZE: int = 4096
    PROXY_SELECT_TIMEOUT: float = 1.0
    PROXY_SERVER_START_WAIT: float = 1.0
    
    # =========================================================================
    # 超時配置（單位：秒）
    # =========================================================================
    DEFAULT_TIMEOUT_SECONDS: int = 30
    DEFAULT_PAGE_LOAD_TIMEOUT: int = 600
    DEFAULT_SCRIPT_TIMEOUT: int = 600
    DEFAULT_IMPLICIT_WAIT: int = 60
    SERVER_SOCKET_TIMEOUT: float = 1.0
    CLEANUP_PROCESS_TIMEOUT: int = 10
    QUIT_WAIT_TIME: float = 10.0  # 關閉前等待時間
    
    # 自動啟動配置
    AUTO_START_DELAY: float = 60.0  # 自動啟動延遲時間（秒）= 1 分鐘
    AUTO_START_COMMAND: str = "r 4"  # 自動啟動命令（執行 4 小時規則）
    
    # =========================================================================
    # 網路容錯配置
    # =========================================================================
    # 元素等待超時（網路慢時需要更長時間）
    ELEMENT_WAIT_TIMEOUT: int = 30
    ELEMENT_WAIT_TIMEOUT_LONG: int = 60
    # 操作重試次數
    MAX_RETRY_ATTEMPTS: int = 5
    # 重試間隔（秒）
    RETRY_INTERVAL: float = 3.0
    # 頁面載入等待時間（網路慢時需要更長）
    PAGE_LOAD_WAIT: float = 5.0
    PAGE_LOAD_WAIT_LONG: float = 10.0
    # Loading 遮罩最大等待時間
    LOADING_MAX_WAIT: int = 30
    # 登入流程超時
    LOGIN_TASK_TIMEOUT: int = 120
    # 導航到遊戲超時
    GAME_NAVIGATION_TIMEOUT: int = 120
    
    # =========================================================================
    # 執行緒與瀏覽器配置
    # =========================================================================
    MAX_THREAD_WORKERS: int = 10
    MAX_BROWSER_COUNT: int = 16
    
    # =========================================================================
    # 視窗配置
    # =========================================================================
    DEFAULT_WINDOW_WIDTH: int = 600
    DEFAULT_WINDOW_HEIGHT: int = 400
    DEFAULT_WINDOW_COLUMNS: int = 4
    
    # =========================================================================
    # 代理商配置
    # =========================================================================
    # TODO: 更新為正式代理商網址
    LOGIN_PAGE: str = "https://www.fin88.app/"
    # LOGIN_PAGE: str = "https://richpanda.vip"  # --- IGNORE ---

    # =========================================================================
    # 遊戲配置
    # =========================================================================
    # TODO: 遊戲種類選擇：True = 賽特一, False = 賽特二
    IS_SETTE_1: bool = True
    # IS_SETTE_1: bool = False  # --- IGNORE ---
    
    # 遊戲識別碼（根據版本自動設定）
    GAME_PATTERN_SETTE_1: str = "ATG-egyptian-mythology"
    GAME_PATTERN_SETTE_2_FIN88: str = "feb91c659e820a0405aabc1520c24d12"
    GAME_PATTERN_SETTE_2_RICHPANDA: str = "af48d779dc07d08d07a526d0076db801"
    
    @classmethod
    def get_game_pattern(cls) -> str:
        """取得當前遊戲種類的識別碼。"""
        if cls.IS_SETTE_1:
            return cls.GAME_PATTERN_SETTE_1
        else:
            # 根據 LOGIN_PAGE 決定 sett2 的識別碼
            if "richpanda" in cls.LOGIN_PAGE.lower():
                return cls.GAME_PATTERN_SETTE_2_RICHPANDA
            return cls.GAME_PATTERN_SETTE_2_FIN88
    
    # =========================================================================
    # 登入相關 XPath
    # =========================================================================
    INITIAL_LOGIN_BUTTON: str = (
        "//button[contains(@class, 'btn') and contains(@class, 'login') "
        "and contains(@class, 'pc') and text()='登入']"
    )
    USERNAME_INPUT: str = "//input[@placeholder='請輸入帳號/手機號']"
    PASSWORD_INPUT: str = "//input[@placeholder='請輸入您的登入密碼']"
    LOGIN_BUTTON: str = (
        "//button[contains(@class, 'custom-button') and @type='submit' "
        "and (text()='登入遊戲' or .//span[text()='登入遊戲'])]"
    )
    
    # =========================================================================
    # 遊戲頁面相關 XPath
    # =========================================================================
    GAME_IFRAME: str = "//iframe[contains(@class, 'iframe-item')]"
    GAME_CANVAS: str = "GameCanvas"
    
    # =========================================================================
    # 圖片檢測配置
    # =========================================================================
    IMAGE_DIR: str = "img"
    GAME_LOGIN: str = "遊戲登入.png"
    GAME_CONFIRM: str = "遊戲開始.png"
    MATCH_THRESHOLD: float = 0.8
    DETECTION_INTERVAL: float = 1.0
    MAX_DETECTION_ATTEMPTS: int = 60
    DETECTION_PROGRESS_INTERVAL: int = 20
    RECOVERY_DETECTION_ATTEMPTS: int = 30  # 恢復流程檢測最大次數
    
    # =========================================================================
    # Canvas 點擊座標比例
    # =========================================================================
    GAME_LOGIN_BUTTON_X_RATIO: float = 0.5
    GAME_LOGIN_BUTTON_Y_RATIO: float = 0.9
    GAME_CONFIRM_BUTTON_X_RATIO: float = 0.74
    GAME_CONFIRM_BUTTON_Y_RATIO: float = 0.85
    
    # 自動跳過點擊座標比例（關閉按鈕）
    AUTO_SKIP_CLICK_X_RATIO: float = 0.5
    AUTO_SKIP_CLICK_Y_RATIO: float = 0.38
    
    # 自動關閉點擊座標比例
    AUTO_CLOSE_CLICK_X_RATIO: float = 0.5
    AUTO_CLOSE_CLICK_Y_RATIO: float = 0.72

    # =========================================================================
    # 自動旋轉按鈕座標比例
    # =========================================================================
    AUTO_SPIN_BUTTON_X_RATIO: float = 0.8     # 自動轉按鈕 X 座標比例
    AUTO_SPIN_BUTTON_Y_RATIO: float = 0.77    # 自動轉按鈕 Y 座標比例
    AUTO_SPIN_10_X_RATIO: float = 0.4         # 10 次按鈕 X 座標比例
    AUTO_SPIN_10_Y_RATIO: float = 0.5         # 10 次按鈕 Y 座標比例
    AUTO_SPIN_50_X_RATIO: float = 0.5         # 50 次按鈕 X 座標比例
    AUTO_SPIN_50_Y_RATIO: float = 0.5         # 50 次按鈕 Y 座標比例
    AUTO_SPIN_100_X_RATIO: float = 0.57       # 100 次按鈕 X 座標比例
    AUTO_SPIN_100_Y_RATIO: float = 0.5        # 100 次按鈕 Y 座標比例
    AUTO_SPIN_MENU_WAIT: float = 1.0          # 自動旋轉選單等待時間（秒）
    AUTO_SPIN_VALID_COUNTS: Tuple[int, ...] = (10, 50, 100)  # 有效的自動旋轉次數
    
    # =========================================================================
    # 購買免費遊戲按鈕座標比例
    # =========================================================================
    # 賽特一專用：只有一個免費遊戲按鈕
    BUY_FREE_GAME_BUTTON_X_RATIO: float = 0.15    # 免費遊戲區域按鈕 X 座標比例
    BUY_FREE_GAME_BUTTON_Y_RATIO: float = 0.75    # 免費遊戲區域按鈕 Y 座標比例
    BUY_FREE_GAME_CONFIRM_X_RATIO: float = 0.65   # 免費遊戲確認按鈕 X 座標比例（賽特一）
    BUY_FREE_GAME_CONFIRM_Y_RATIO: float = 0.9    # 免費遊戲確認按鈕 Y 座標比例（賽特一）
    
    # 賽特二專用：免費遊戲類別座標 - only_freegame (類別 1)
    BUY_FREE_GAME_ONLY_FREEGAME_X_RATIO: float = 0.3    # 免費遊戲確認按鈕 X 座標比例
    BUY_FREE_GAME_ONLY_FREEGAME_Y_RATIO: float = 0.85   # 免費遊戲確認按鈕 Y 座標比例
    
    # 賽特二專用：免費遊戲類別座標 - awake_power (類別 2)
    BUY_FREE_GAME_AWAKE_POWER_X_RATIO: float = 0.5      # 覺醒之力確認按鈕 X 座標比例
    BUY_FREE_GAME_AWAKE_POWER_Y_RATIO: float = 0.95     # 覺醒之力確認按鈕 Y 座標比例
    
    # 賽特二專用：免費遊戲類別座標 - immortal_awake (類別 3)
    BUY_FREE_GAME_IMMORTAL_AWAKE_X_RATIO: float = 0.7   # 不朽覺醒確認按鈕 X 座標比例
    BUY_FREE_GAME_IMMORTAL_AWAKE_Y_RATIO: float = 0.85  # 不朽覺醒確認按鈕 Y 座標比例
    FREE_GAME_VALID_TYPES: Tuple[int, ...] = (1, 2, 3)  # 有效的免費遊戲類別
    
    # 購買後等待與結算配置
    BUY_FREE_GAME_WAIT_SECONDS: int = 10              # 購買後等待秒數
    FREE_GAME_CLICK_WAIT: float = 2.0                 # 免費遊戲點擊間隔
    FREE_GAME_SETTLE_INITIAL_WAIT: float = 3.0        # 免費遊戲結算初始等待
    FREE_GAME_SETTLE_CLICK_INTERVAL: float = 3.0      # 免費遊戲結算點擊間隔
    FREE_GAME_SETTLE_CLICK_COUNT: int = 5             # 免費遊戲結算點擊次數
    
    # =========================================================================
    # 控制面板配置
    # =========================================================================
    AUTO_CLICK_INTERVAL: int = 30
    ERROR_MONITOR_INTERVAL: float = 3.0  # 錯誤訊息監控間隔（秒）
    BLACKSCREEN_CONSECUTIVE_THRESHOLD: int = 5  # 黑屏連續檢測次數閾值（達到後導航到登入頁）
    
    # =========================================================================
    # 規則執行配置
    # =========================================================================
    RULE_SWITCH_WAIT: float = 1.0              # 規則切換等待時間（秒）
    RULE_PROGRESS_INTERVAL: int = 60           # 規則進度顯示間隔（秒）
    AUTO_PRESS_THREAD_JOIN_TIMEOUT: float = 2.0  # 自動按鍵執行緒結束等待時間
    
    # -------------------------------------------------------------------------
    # 金額模板配置
    # -------------------------------------------------------------------------
    BETSIZE_DISPLAY_X: float = 0.72
    BETSIZE_DISPLAY_Y: float = 0.89
    BETSIZE_CROP_MARGIN_X: int = 40
    BETSIZE_CROP_MARGIN_Y: int = 10
    
    # =========================================================================
    # 黑屏檢測模板配置
    # =========================================================================
    BLACK_SCREEN: str = "黑屏提示.png"
    BLACKSCREEN_CENTER_X: float = 0.5
    BLACKSCREEN_CENTER_Y: float = 0.5
    BLACKSCREEN_CROP_MARGIN_X: int = 100
    BLACKSCREEN_CROP_MARGIN_Y: int = 50
    
    # =========================================================================
    # 錯誤提醒模板配置
    # =========================================================================
    ERROR_REMIND: str = "錯誤訊息.png"
    ERROR_REMIND_CENTER_X: float = 0.5
    ERROR_REMIND_CENTER_Y: float = 0.55
    ERROR_REMIND_CROP_MARGIN_X: int = 50
    ERROR_REMIND_CROP_MARGIN_Y: int = 10
    
    # 錯誤訊息確認按鈕座標比例
    ERROR_CONFIRM_BUTTON_X_RATIO: float = 0.5
    ERROR_CONFIRM_BUTTON_Y_RATIO: float = 0.53
    
    # =========================================================================
    # 大廳返回模板配置
    # =========================================================================
    LOBBY_RETURN: str = "返回大廳.png"
    
    # =========================================================================
    # 模板顯示名稱對應表
    # =========================================================================
    TEMPLATE_DISPLAY_NAMES: Dict[str, str] = {
        "遊戲登入.png": "遊戲登入",
        "遊戲開始.png": "遊戲開始",
        "黑屏提示.png": "黑屏提示",
        "錯誤訊息.png": "錯誤訊息",
        "返回大廳.png": "返回大廳",
    }
    
    # =========================================================================
    # 短等待時間配置（單位：秒）
    # =========================================================================
    SHORT_WAIT: float = 0.5                    # 短暫等待（元素操作間隔）
    NORMAL_WAIT: float = 1.0                   # 一般等待（DOM 更新）
    SCREEN_SWITCH_WAIT: float = 2.0            # 畫面切換等待
    CANVAS_RETRY_WAIT: float = 1.0             # Canvas 重試等待
    CANVAS_RETRY_COUNT: int = 5                # Canvas 取得最大重試次數
    
    # =========================================================================
    # 金額調整按鈕配置
    # =========================================================================
    BETSIZE_INCREASE_BUTTON_X: float = 0.8     # 增加金額按鈕 X 座標比例
    BETSIZE_INCREASE_BUTTON_Y: float = 0.89    # 增加金額按鈕 Y 座標比例
    BETSIZE_DECREASE_BUTTON_X: float = 0.63    # 減少金額按鈕 X 座標比例
    BETSIZE_DECREASE_BUTTON_Y: float = 0.89    # 減少金額按鈕 Y 座標比例
    BETSIZE_MATCH_THRESHOLD: float = 0.85      # 金額識別匹配閾值
    BETSIZE_ADJUST_STEP_WAIT: float = 1.0      # 調整金額每步等待時間
    BETSIZE_ADJUST_RETRY_WAIT: float = 1.0     # 調整金額重試等待時間
    BETSIZE_READ_RETRY_WAIT: float = 0.5       # 讀取金額重試等待時間
    BETSIZE_READ_MAX_RETRIES: int = 2          # 讀取金額最大重試次數
    
    # =========================================================================
    # 網路錯誤關鍵字（用於判斷是否可重試）
    # =========================================================================
    NETWORK_ERROR_KEYWORDS: Tuple[str, ...] = (
        'timeout', 'timed out', 'connection', 'network', 'err_',
        'loading', 'stale'
    )
    
    # -------------------------------------------------------------------------
    # 遊戲金額配置（tuple 支援 in 檢查和索引計算）
    # -------------------------------------------------------------------------
    GAME_BETSIZE: Tuple[int, ...] = (
        2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 24, 28, 32, 36, 40,
        48, 56, 60, 64, 72, 80, 96, 100, 120, 140, 160, 180, 200,
        240, 280, 300, 320, 360, 400, 420, 480, 500, 540, 560, 600,
        640, 700, 720, 800, 840, 900, 960, 980, 1000, 1080, 1120,
        1200, 1260, 1280, 1400, 1440, 1500, 1600, 1800, 2000, 2100,
        2400, 2700, 3000
    )


# =============================================================================
# 例外類別
# =============================================================================

class AutoSlotGameError(Exception):
    """自動化遊戲系統基礎例外類別。

    所有自定義例外皆繼承自此類別，便於統一捕獲和處理。

    範例:
        >>> try:
        ...     raise AutoSlotGameError("發生錯誤")
        ... except AutoSlotGameError as e:
        ...     print(f"捕獲到錯誤: {e}")
    """


class ConfigurationError(AutoSlotGameError):
    """配置相關錯誤。

    當配置檔案不存在、格式錯誤或讀取失敗時拋出。

    範例:
        >>> raise ConfigurationError("找不到配置檔案: config.txt")
    """


class BrowserCreationError(AutoSlotGameError):
    """瀏覽器建立錯誤。

    當 WebDriver 初始化失敗或瀏覽器無法啟動時拋出。

    範例:
        >>> raise BrowserCreationError("ChromeDriver 版本不相容")
    """


class ProxyServerError(AutoSlotGameError):
    """代理伺服器錯誤。

    當代理伺服器啟動失敗或連線異常時拋出。

    範例:
        >>> raise ProxyServerError("無法綁定到埠號 9000")
    """


class ImageDetectionError(AutoSlotGameError):
    """圖片檢測錯誤。

    當截圖失敗、模板不存在或圖片比對異常時拋出。

    範例:
        >>> raise ImageDetectionError("模板圖片不存在: login.png")
    """


# =============================================================================
# 資料類別
# =============================================================================

@dataclass(frozen=True)
class UserCredential:
    """使用者憑證資料結構（不可變）。

    屬性:
        username: 使用者帳號。
        password: 登入密碼。
        proxy: 代理連接字串，格式為 ``host:port:username:password``。

    異常:
        ValueError: 當帳號或密碼為空時。

    範例:
        >>> cred = UserCredential(
        ...     username="test_user",
        ...     password="test_pass",
        ...     proxy="proxy.example.com:8080:user:pass"
        ... )
    """
    username: str
    password: str
    proxy: Optional[str] = None

    def __post_init__(self) -> None:
        """驗證資料完整性。"""
        if not self.username or not self.password:
            raise ValueError("使用者名稱和密碼不能為空")


@dataclass(frozen=True)
class BetRule:
    """下注規則資料結構（不可變）。

    支援三種規則類型:
        - ``'a'`` (自動旋轉): 指定金額和旋轉次數
        - ``'s'`` (標準規則): 指定金額、持續時間、最小/最大間隔
        - ``'f'`` (購買免費遊戲): 指定金額和類別

    前綴說明:
        - 帶 ``'-'`` 前綴（如 ``-a:2:10``）: 只執行一次
        - 不帶前綴（如 ``a:2:10``）: 循環執行
        - 帶 ``'#'`` 前綴: 略過此規則（註釋）

    屬性:
        rule_type: 規則類型，可為 ``'a'``、``'s'`` 或 ``'f'``。
        amount: 下注金額。
        spin_count: 自動旋轉次數，僅 ``'a'`` 類型使用。
        duration: 持續時間（分鐘），僅 ``'s'`` 類型使用。
        min_seconds: 最小間隔秒數，僅 ``'s'`` 類型使用。
        max_seconds: 最大間隔秒數，僅 ``'s'`` 類型使用。
        free_game_type: 免費遊戲類別，僅 ``'f'`` 類型使用。
            1=免費遊戲, 2=覺醒之力, 3=不朽覺醒（賽特二專用）
        once_only: 是否只執行一次（帶 ``'-'`` 前綴的規則）。

    異常:
        ValueError: 當規則參數無效時。

    範例:
        >>> rule = BetRule(rule_type='a', amount=10, spin_count=50)
        >>> rule = BetRule(rule_type='s', amount=20, duration=30,
        ...                min_seconds=1.0, max_seconds=3.0)
        >>> rule = BetRule(rule_type='f', amount=8, free_game_type=1)
    """
    rule_type: str
    amount: float
    spin_count: Optional[int] = None
    duration: Optional[int] = None
    min_seconds: Optional[float] = None
    max_seconds: Optional[float] = None
    free_game_type: Optional[int] = None
    once_only: bool = False

    def __post_init__(self) -> None:
        """驗證資料完整性。"""
        if self.amount <= 0:
            raise ValueError(f"下注金額必須大於 0: {self.amount}")

        if self.rule_type == 'a':
            if self.spin_count is None:
                raise ValueError("自動旋轉規則必須指定次數")
            if self.spin_count not in Constants.AUTO_SPIN_VALID_COUNTS:
                valid_counts = ", ".join(str(c) for c in Constants.AUTO_SPIN_VALID_COUNTS)
                raise ValueError(f"自動旋轉次數必須是 {valid_counts}: {self.spin_count}")

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
            # 購買免費遊戲規則驗證
            # 賽特一不需要類別，賽特二需要類別（1=免費遊戲, 2=覺醒之力, 3=不朽覺醒）
            if self.free_game_type is not None and self.free_game_type not in Constants.FREE_GAME_VALID_TYPES:
                valid_types = ", ".join(str(t) for t in Constants.FREE_GAME_VALID_TYPES)
                raise ValueError(
                    f"免費遊戲類別必須是 {valid_types}: {self.free_game_type}"
                )

        else:
            raise ValueError(f"無效的規則類型: {self.rule_type}，必須是 'a'、's' 或 'f'")


@dataclass(frozen=True)
class ProxyInfo:
    """代理伺服器資訊資料結構（不可變）。

    屬性:
        host: 代理主機位址。
        port: 代理埠號（1-65535）。
        username: 認證使用者名稱。
        password: 認證密碼。

    異常:
        ValueError: 當參數無效時。

    範例:
        >>> proxy = ProxyInfo.from_connection_string("proxy.com:8080:user:pass")
        >>> print(proxy.to_url())
        http://user:pass@proxy.com:8080
    """
    host: str
    port: int
    username: str
    password: str

    def __post_init__(self) -> None:
        """驗證資料完整性。"""
        if not self.host:
            raise ValueError("代理主機不能為空")
        if not (0 < self.port < 65536):
            raise ValueError(f"代理埠號無效: {self.port}")
        if not self.username:
            raise ValueError("代理使用者名稱不能為空")

    def to_url(self) -> str:
        """轉換為代理 URL 格式。

        回傳:
            格式為 ``http://username:password@host:port`` 的 URL 字串。
        """
        return f"http://{self.username}:{self.password}@{self.host}:{self.port}"

    def to_connection_string(self) -> str:
        """轉換為連接字串格式。

        回傳:
            格式為 ``host:port:username:password`` 的連接字串。
        """
        return f"{self.host}:{self.port}:{self.username}:{self.password}"

    def __str__(self) -> str:
        """字串表示（隱藏敏感資訊）。"""
        return f"ProxyInfo({self.host}:{self.port}, user={self.username[:3]}***)"
    
    @staticmethod
    def from_connection_string(connection_string: str) -> 'ProxyInfo':
        """從連接字串建立 ProxyInfo 實例。

        參數:
            connection_string: 格式為 ``host:port:username:password`` 的字串。

        回傳:
            解析後的 ProxyInfo 實例。

        異常:
            ValueError: 當連接字串格式不正確時。

        範例:
            >>> proxy = ProxyInfo.from_connection_string("proxy.com:8080:user:pass")
        """
        parts = connection_string.split(':')
        if len(parts) < 4:
            raise ValueError(f"代理連接字串格式不正確: {connection_string}")

        return ProxyInfo(
            host=parts[0],
            port=int(parts[1]),
            username=parts[2],
            password=':'.join(parts[3:])  # 密碼可能包含冒號
        )


@dataclass
class BrowserContext:
    """瀏覽器上下文資訊。

    儲存單一瀏覽器實例的相關資訊，包含驅動程式、憑證和狀態。
    此類別為可變的，因為需要在執行時更新狀態。

    屬性:
        driver: WebDriver 實例。
        credential: 使用者憑證。
        index: 瀏覽器索引（從 1 開始）。
        proxy_port: 代理埠號（無代理時為 None）。
        created_at: 建立時間戳（秒）。

    範例:
        >>> context = BrowserContext(
        ...     driver=driver,
        ...     credential=credential,
        ...     index=1
        ... )
        >>> print(f"瀏覽器已運行 {context.age_in_seconds} 秒")
    """
    driver: WebDriver
    credential: UserCredential
    index: int
    proxy_port: Optional[int] = None
    created_at: Optional[float] = None

    def __post_init__(self) -> None:
        """初始化後設定預設值。"""
        if self.created_at is None:
            self.created_at = time.time()

    @property
    def age_in_seconds(self) -> float:
        """取得瀏覽器實例的存活時間（秒）。"""
        return time.time() - (self.created_at or time.time())


class BrowserThread(threading.Thread):
    """瀏覽器控制器。

    每個瀏覽器視窗都有自己的專屬控制器，負責處理該視窗的所有操作，
    包括建立、導航、登入和遊戲控制等。

    屬性:
        index: 瀏覽器編號（從 1 開始）。
        credential: 使用者憑證。
        proxy_port: 代理埠號（無代理時為 None）。
        browser_manager: 瀏覽器管理器實例。
        context: 瀏覽器上下文（建立後填充）。
        driver: WebDriver 實例。

    範例:
        >>> thread = BrowserThread(
        ...     index=1,
        ...     credential=credential,
        ...     browser_manager=browser_manager
        ... )
        >>> thread.start()
        >>> thread.wait_until_ready(timeout=30)
        >>> result = thread.execute_task(lambda ctx: ctx.driver.current_url)
    """

    def __init__(
        self,
        index: int,
        credential: UserCredential,
        browser_manager: 'BrowserManager',
        proxy_port: Optional[int] = None,
        logger: Optional[logging.Logger] = None
    ) -> None:
        """初始化瀏覽器控制器。

        參數:
            index: 瀏覽器編號（從 1 開始）。
            credential: 使用者憑證。
            browser_manager: 瀏覽器管理器實例。
            proxy_port: 代理埠號（可選）。
            logger: 日誌記錄器（可選）。
        """
        super().__init__(name=f"BrowserThread-{index}", daemon=True)
        self.index = index
        self.credential = credential
        self.proxy_port = proxy_port
        self.browser_manager = browser_manager
        self.logger = logger or LoggerFactory.get_logger()

        # 瀏覽器上下文（在啟動後建立）
        self.context: Optional[BrowserContext] = None
        self.driver: Optional[WebDriver] = None

        # 內部狀態控制
        self._stop_event = threading.Event()
        self._ready_event = threading.Event()  # 瀏覽器就緒事件
        self._creation_error: Optional[Exception] = None

        # 任務佇列
        self._task_queue: List[Tuple[Callable, tuple, dict]] = []
        self._task_lock = threading.Lock()
        self._task_event = threading.Event()  # 新任務通知
        self._task_result: Any = None
        self._task_done_event = threading.Event()  # 任務完成事件

    def run(self) -> None:
        """控制器主迴圈。

        流程：
        1. 建立瀏覽器
        2. 通知瀏覽器已就緒
        3. 等待任務或停止信號
        4. 清理資源
        """
        try:
            # 1. 建立瀏覽器
            self._create_browser()

            if self.driver is None:
                return

            # 2. 通知瀏覽器已就緒
            self._ready_event.set()

            # 3. 等待任務或停止信號
            while not self._stop_event.is_set():
                # 每秒檢查一次
                if self._task_event.wait(timeout=1.0):
                    self._task_event.clear()
                    self._process_tasks()

        except Exception as e:
            self.logger.error(f"瀏覽器 {self.index} 發生異常: {e}")
        finally:
            # 4. 清理資源
            self._cleanup()

    def _create_browser(self) -> None:
        """建立瀏覽器實例。

        建立 WebDriver 實例並初始化 BrowserContext。
        若建立失敗，將錯誤儲存到 _creation_error。
        """
        try:
            self.driver = self.browser_manager.create_webdriver(
                local_proxy_port=self.proxy_port
            )

            self.context = BrowserContext(
                driver=self.driver,
                credential=self.credential,
                index=self.index,
                proxy_port=self.proxy_port
            )

        except Exception as e:
            self._creation_error = e
            self._ready_event.set()

    def _process_tasks(self) -> None:
        """處理任務佇列中的所有任務。

        依序執行佇列中的任務，並將結果儲存到 _task_result。
        """
        while True:
            with self._task_lock:
                if not self._task_queue:
                    break
                func, args, kwargs = self._task_queue.pop(0)

            try:
                # 將 context 注入到任務中
                self._task_result = func(self.context, *args, **kwargs)
            except Exception as e:
                self._task_result = e
            finally:
                self._task_done_event.set()

    def _cleanup(self) -> None:
        """清理瀏覽器資源。"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            finally:
                self.driver = None
                self.context = None

    def wait_until_ready(self, timeout: Optional[float] = None) -> bool:
        """等待瀏覽器就緒。

        參數:
            timeout: 超時時間（秒），None 表示無限等待。

        回傳:
            瀏覽器是否成功建立。
        """
        self._ready_event.wait(timeout=timeout)
        return self.context is not None and self._creation_error is None

    def get_creation_error(self) -> Optional[Exception]:
        """取得建立瀏覽器時的錯誤。

        回傳:
            建立時發生的例外，若成功則為 None。
        """
        return self._creation_error

    def execute_task(
        self,
        func: Callable[[BrowserContext], Any],
        *args: Any,
        timeout: Optional[float] = None,
        **kwargs: Any
    ) -> Any:
        """在瀏覽器中執行任務。

        參數:
            func: 要執行的函數，第一個參數會是 BrowserContext。
            *args: 額外的位置參數。
            timeout: 超時時間（秒）。
            **kwargs: 額外的關鍵字參數。

        回傳:
            任務執行的結果。

        異常:
            RuntimeError: 當瀏覽器已關閉時。
            TimeoutError: 當任務執行超時時。
        """
        if not self.is_alive() or self._stop_event.is_set():
            raise RuntimeError(f"瀏覽器 {self.index} 已關閉")

        # 重置任務完成事件
        self._task_done_event.clear()
        self._task_result = None

        # 加入任務佇列
        with self._task_lock:
            self._task_queue.append((func, args, kwargs))
        
        # 通知有新任務
        self._task_event.set()
        
        # 等待任務完成
        if self._task_done_event.wait(timeout=timeout):
            result = self._task_result
            if isinstance(result, Exception):
                raise result
            return result
        else:
            raise TimeoutError(f"瀏覽器 {self.index} 任務執行超時")
    
    def stop(self) -> None:
        """停止瀏覽器並釋放資源。"""
        self._stop_event.set()
        self._task_event.set()

    def is_browser_alive(self) -> bool:
        """檢查瀏覽器是否仍然有效。

        回傳:
            瀏覽器是否仍可操作。
        """
        if self.driver is None:
            return False
        try:
            _ = self.driver.current_url
            return True
        except Exception:
            return False


class OperationResult:
    """操作結果封裝類別。

    統一封裝操作的執行結果，支援布林轉換和字串表示。
    此類別用於統一各種操作的回傳格式。

    屬性:
        success: 操作是否成功。
        data: 操作返回的資料。
        error: 發生的例外（如果有）。
        message: 額外的訊息說明。

    範例:
        >>> result = OperationResult(success=True, data={"count": 5})
        >>> if result:
        ...     print(result.data)
        {'count': 5}
    """

    def __init__(
        self,
        success: bool,
        data: Any = None,
        error: Optional[Exception] = None,
        message: str = ""
    ) -> None:
        """初始化操作結果。

        參數:
            success: 操作是否成功。
            data: 操作返回的資料。
            error: 發生的例外（如果有）。
            message: 額外的訊息說明。
        """
        self.success = success
        self.data = data
        self.error = error
        self.message = message

    def __bool__(self) -> bool:
        """支援布林轉換。"""
        return self.success

    def __repr__(self) -> str:
        """字串表示。"""
        status = "成功" if self.success else "失敗"
        return f"OperationResult({status}, {self.message})"


# =============================================================================
# 日誌系統
# =============================================================================

class LogLevel(Enum):
    """日誌等級列舉。

    提供與 logging 模組相容的日誌等級定義。

    等級:
        DEBUG: 除錯等級，用於開發時的詳細資訊。
        INFO: 資訊等級，用於一般運行狀態。
        WARNING: 警告等級，用於潛在問題。
        ERROR: 錯誤等級，用於錯誤狀況。
        CRITICAL: 嚴重等級，用於致命錯誤。
    """
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class ColoredFormatter(logging.Formatter):
    """帶顏色的日誌格式化器。

    根據日誌等級為輸出添加不同的 ANSI 顏色代碼，
    提升終端機輸出的可讀性。

    屬性:
        COLORS: 顏色代碼對應表。
        formatters: 各日誌等級的格式化器。

    註意:
        此格式化器僅在支援 ANSI 顏色代碼的終端機中有效。
    """

    COLORS: Dict[str, str] = {
        'RESET': "\033[0m",
        'INFO': "\033[32m",       # 綠色
        'WARNING': "\033[33m",    # 黃色
        'ERROR': "\033[31m",      # 紅色
        'CRITICAL': "\033[35m",   # 紫色
        'DEBUG': "\033[36m",      # 青色
        'TIMESTAMP': "\033[90m",  # 灰色
    }

    def __init__(self, fmt: Optional[str] = None, datefmt: Optional[str] = None) -> None:
        """初始化格式化器。

        參數:
            fmt: 日誌格式字串（可選）。
            datefmt: 日期格式字串（可選）。
        """
        super().__init__(fmt, datefmt)
        self.formatters: Dict[int, logging.Formatter] = {
            logging.DEBUG: self._create_formatter(self.COLORS['DEBUG'], 'DEBUG'),
            logging.INFO: self._create_formatter(self.COLORS['INFO'], 'INFO'),
            logging.WARNING: self._create_formatter(self.COLORS['WARNING'], 'WARNING'),
            logging.ERROR: self._create_formatter(self.COLORS['ERROR'], 'ERROR'),
            logging.CRITICAL: self._create_formatter(self.COLORS['CRITICAL'], 'CRITICAL'),
        }

    def _create_formatter(self, color: str, level_name: str) -> logging.Formatter:
        """建立指定顏色的格式化器。

        參數:
            color: ANSI 顏色代碼。
            level_name: 日誌等級名稱。

        回傳:
            配置好的 Formatter 實例。
        """
        return logging.Formatter(
            f"{self.COLORS['TIMESTAMP']}%(asctime)s{self.COLORS['RESET']} - "
            f"{color}%(levelname)-8s{self.COLORS['RESET']} - "
            f"%(message)s"
        )

    def format(self, record: logging.LogRecord) -> str:
        """格式化日誌記錄。

        參數:
            record: 日誌記錄。

        回傳:
            格式化後的字串。
        """
        formatter = self.formatters.get(record.levelno)
        if formatter:
            return formatter.format(record)
        return super().format(record)


class FlushingStreamHandler(logging.StreamHandler):
    """自動刷新的 StreamHandler。

    確保日誌訊息能即時顯示在終端機上，
    每次輸出後立即刷新緩衝區。
    在輸出前清除當前行，避免與輸入提示混在一起。
    輸出後重新顯示提示符。
    """
    
    # 類別變數：控制是否顯示提示符
    show_prompt: bool = False
    # 類別變數：控制是否啟用清除行功能（某些終端可能不支援）
    enable_line_clear: bool = True
    
    def emit(self, record: logging.LogRecord) -> None:
        """輸出日誌記錄並強制刷新緩衝區。

        參數:
            record: 日誌記錄。
        """
        try:
            # 清除當前行（避免與 >>> 提示混在一起）
            if FlushingStreamHandler.enable_line_clear and FlushingStreamHandler.show_prompt:
                # 使用 \r 回到行首，然後用空格覆蓋提示符
                self.stream.write('\r    \r')
            super().emit(record)
            # 如果需要顯示提示符，重新輸出
            if FlushingStreamHandler.show_prompt:
                self.stream.write('>>> ')
            self.flush()
        except Exception:
            self.handleError(record)


class LoggerFactory:
    """日誌記錄器工廠類別。

    使用單例模式管理 logger 實例。
    所有模組應透過此工廠取得 logger，以保持一致的格式和行為。

    屬性:
        _loggers: logger 實例緩存。
        _lock: 鎖定機制。
        _formatter: 共享的格式化器實例。

    範例:
        >>> logger = LoggerFactory.get_logger()
        >>> logger.info("程式啟動")
    """

    _loggers: Dict[str, logging.Logger] = {}
    _lock: threading.RLock = threading.RLock()
    _formatter: Optional[ColoredFormatter] = None

    @classmethod
    def get_logger(
        cls,
        name: str = "AutoSlotGame",
        level: LogLevel = LogLevel.INFO
    ) -> logging.Logger:
        """取得或建立 logger 實例。

        參數:
            name: logger 名稱。
            level: 日誌等級。

        回傳:
            配置完成的 logger 實例。

        範例:
            >>> logger = LoggerFactory.get_logger(level=LogLevel.DEBUG)
        """
        if name in cls._loggers:
            return cls._loggers[name]

        with cls._lock:
            if name in cls._loggers:
                return cls._loggers[name]

            logger = logging.getLogger(name)
            logger.setLevel(level.value)
            logger.propagate = False

            if not logger.handlers:
                if cls._formatter is None:
                    cls._formatter = ColoredFormatter()

                console_handler = FlushingStreamHandler(sys.stdout)
                console_handler.setLevel(level.value)
                console_handler.setFormatter(cls._formatter)
                logger.addHandler(console_handler)

            cls._loggers[name] = logger
            return logger


# =============================================================================
# 輔助函式
# =============================================================================

def get_resource_path(relative_path: str = "") -> Path:
    """取得資源檔案的絕對路徑。

    根據執行環境自動判斷基礎路徑：
    - 開發環境：返回專案根目錄
    - 打包環境：返回可執行檔所在目錄

    參數:
        relative_path: 相對路徑（可選）。

    回傳:
        完整的絕對路徑。

    範例:
        >>> path = get_resource_path("img/template.png")
        >>> print(path)
        /path/to/project/img/template.png
    """
    if getattr(sys, 'frozen', False):
        base_path = Path(sys.executable).resolve().parent
    else:
        base_path = Path(__file__).resolve().parent.parent
    
    if relative_path:
        return base_path / relative_path
    return base_path


def is_network_error(error: Exception) -> bool:
    """判斷是否為網路相關錯誤（可重試）。

    檢查錯誤訊息中是否包含網路相關關鍵字，用於決定是否應該重試操作。

    參數:
        error: 發生的例外。

    回傳:
        如果是網路相關錯誤則返回 True。

    範例:
        >>> try:
        ...     do_something()
        ... except Exception as e:
        ...     if is_network_error(e):
        ...         retry()
    """
    error_msg = str(error).lower()
    return any(kw in error_msg for kw in Constants.NETWORK_ERROR_KEYWORDS)


def cv2_imread_unicode(file_path: Union[str, Path], flags: int = cv2.IMREAD_COLOR) -> Optional[np.ndarray]:
    """安全讀取圖片（支援 Unicode 路徑）。

    OpenCV 的 cv2.imread() 無法處理包含中文或其他非 ASCII 字元的路徑。
    此函式使用 numpy 和 PIL 作為替代方案。

    參數:
        file_path: 圖片檔案路徑（支援中文路徑）。
        flags: OpenCV 讀取標誌，支援 cv2.IMREAD_COLOR、cv2.IMREAD_GRAYSCALE 等。

    回傳:
        圖片的 numpy 陣列，失敗返回 None。

    範例:
        >>> img = cv2_imread_unicode("圖片/模板.png")
        >>> if img is not None:
        ...     print(f"圖片尺寸: {img.shape}")
    """
    try:
        # 轉換為 Path 物件
        path = Path(file_path)

        # 使用 PIL 讀取圖片（PIL 支援 Unicode 路徑）
        pil_image = Image.open(path)

        # 轉換為 numpy 陣列
        img_array = np.array(pil_image)

        # 根據讀取標誌處理圖片
        if flags == cv2.IMREAD_GRAYSCALE:
            # 轉換為灰階
            if len(img_array.shape) == 3:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        elif flags == cv2.IMREAD_COLOR:
            # 確保是彩色圖片
            if len(img_array.shape) == 2:
                # 灰階轉彩色
                img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2RGB)
            elif img_array.shape[2] == 4:
                # RGBA 轉 RGB
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
            # PIL 使用 RGB，OpenCV 使用 BGR，需要轉換
            if len(img_array.shape) == 3 and img_array.shape[2] == 3:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

        return img_array

    except Exception:
        # 返回 None 保持與 cv2.imread() 相同的行為
        return None


# =============================================================================
# 配置讀取器
# =============================================================================

class ConfigReaderProtocol(Protocol):
    """配置讀取器協議。

    定義配置讀取器必須實現的方法介面。
    使用 Protocol 實現結構化子類型（鴨子類型）。
    """

    def read_user_credentials(self, filename: str) -> List[UserCredential]:
        """讀取使用者憑證檔案。"""
        ...

    def read_bet_rules(self, filename: str) -> List[BetRule]:
        """讀取下注規則檔案。"""
        ...


class ConfigReader:
    """配置檔案讀取器。

    讀取並解析系統所需的各種配置檔案，包含:
        - 用戶資料.txt: 使用者憑證
        - 用戶規則.txt: 下注規則

    屬性:
        lib_path: 配置檔案目錄路徑。
        logger: 日誌記錄器。

    異常:
        ConfigurationError: 當配置目錄不存在時。

    範例:
        >>> reader = ConfigReader()
        >>> credentials = reader.read_user_credentials()
        >>> rules = reader.read_bet_rules()
    """

    def __init__(
        self,
        lib_path: Optional[Path] = None,
        logger: Optional[logging.Logger] = None
    ) -> None:
        """初始化配置讀取器。

        參數:
            lib_path: 配置檔案目錄路徑（可選，預設為 lib/）。
            logger: 日誌記錄器（可選）。
        """
        if lib_path is None:
            lib_path = get_resource_path(Constants.DEFAULT_LIB_PATH)

        self.lib_path = Path(lib_path)
        self.logger = logger or LoggerFactory.get_logger()

        if not self.lib_path.exists():
            raise ConfigurationError(f"配置目錄不存在: {self.lib_path}")

    def _read_file_lines(self, filename: str, skip_header: bool = True) -> List[str]:
        """讀取檔案並返回有效行列表。

        參數:
            filename: 檔案名稱。
            skip_header: 是否跳過首行（標題列）。

        回傳:
            有效行列表（已去除空白和註釋行）。
        """
        file_path = self.lib_path / filename

        if not file_path.exists():
            raise ConfigurationError(f"找不到配置檔案: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8', buffering=8192) as f:
                lines = f.readlines()

            start_index = 1 if skip_header and lines else 0
            
            valid_lines = [
                line.strip() 
                for line in lines[start_index:] 
                if (stripped := line.strip()) and not stripped.startswith('#')
            ]
            
            return valid_lines
            
        except (IOError, OSError) as e:
            raise ConfigurationError(f"讀取檔案失敗 {filename}: {e}") from e
        except Exception as e:
            raise ConfigurationError(f"解析檔案失敗 {filename}: {e}") from e
    
    def read_user_credentials(
        self, 
        filename: str = Constants.DEFAULT_CREDENTIALS_FILE
    ) -> List[UserCredential]:
        """讀取使用者憑證檔案。
        
        檔案格式: 帳號,密碼,出口IP (首行為標題)
        """
        credentials = []
        lines = self._read_file_lines(filename, skip_header=True)
        
        for line_number, line in enumerate(lines, start=2):
            try:
                parts = [p.strip() for p in line.split(',')]
                
                if len(parts) < 2:
                    self.logger.warning(f"第 {line_number} 行格式不完整，已跳過: {line}")
                    continue
                
                username = parts[0]
                password = parts[1]
                proxy = parts[2] if len(parts) >= 3 and parts[2].strip() else None
                
                credentials.append(UserCredential(
                    username=username,
                    password=password,
                    proxy=proxy
                ))  
                
            except ValueError as e:
                self.logger.warning(f"第 {line_number} 行資料無效: {e}")
                continue
        
        return credentials
    
    def read_bet_rules(
        self, 
        filename: str = Constants.DEFAULT_RULES_FILE
    ) -> List[BetRule]:
        """讀取下注規則檔案。
        
        執行模式前綴:
            - (無前綴): 循環執行
            - ``-``: 執行一次後跳過
            - ``#``: 略過此規則（註釋）
        
        支援三種規則格式:
            - ``s:金額:最小間隔,最大間隔:時間(分鐘)`` (定時旋轉)
            - ``a:金額:次數`` (自動旋轉)
            - ``f:金額`` 或 ``f:金額:類別`` (購買免費遊戲)
              類別: 1=免費遊戲, 2=覺醒之力, 3=不朽覺醒
        
        回傳:
            有效的規則列表
        """
        rules = []
        lines = self._read_file_lines(filename, skip_header=False)
        
        for line_number, line in enumerate(lines, start=1):
            try:
                # 跳過空行和註釋行（# 開頭）
                stripped_line = line.strip()
                if not stripped_line or stripped_line.startswith('#'):
                    continue
                
                # 解析執行模式前綴
                once_only = False
                if stripped_line.startswith('-'):
                    once_only = True
                    stripped_line = stripped_line[1:]  # 移除前綴
                
                # 再次檢查是否為空
                if not stripped_line:
                    continue
                
                parts = stripped_line.split(':')
                
                if len(parts) < 2:
                    self.logger.warning(f"第 {line_number} 行格式不完整: {line}")
                    continue
                
                rule_type = parts[0].strip().lower()
                
                if rule_type == 'a':
                    # 自動旋轉規則: a:金額:次數
                    if len(parts) < 3:
                        self.logger.warning(f"第 {line_number} 行格式不完整: {line}")
                        continue
                    
                    amount = float(parts[1].strip())
                    spin_count = int(parts[2].strip())
                    
                    rules.append(BetRule(
                        rule_type='a',
                        amount=amount,
                        spin_count=spin_count,
                        once_only=once_only
                    ))
                    
                elif rule_type == 's':
                    # 定時旋轉規則: s:金額:最小間隔,最大間隔:時間(分鐘)
                    if len(parts) < 4:
                        self.logger.warning(f"第 {line_number} 行格式不完整: {line}")
                        continue
                    
                    amount = float(parts[1].strip())
                    
                    # 解析間隔時間（格式: 最小,最大）
                    interval_str = parts[2].strip()
                    if ',' in interval_str:
                        interval_parts = interval_str.split(',')
                        min_seconds = float(interval_parts[0].strip())
                        max_seconds = float(interval_parts[1].strip())
                    else:
                        # 如果沒有逗號，視為舊格式（duration:min:max）
                        # 嘗試解析為舊格式: s:金額:時間:最小:最大
                        if len(parts) >= 5:
                            duration = int(parts[2].strip())
                            min_seconds = float(parts[3].strip())
                            max_seconds = float(parts[4].strip())
                            
                            rules.append(BetRule(
                                rule_type='s',
                                amount=amount,
                                duration=duration,
                                min_seconds=min_seconds,
                                max_seconds=max_seconds,
                                once_only=once_only
                            ))
                            continue
                        else:
                            self.logger.warning(f"第 {line_number} 行間隔格式錯誤: {line}")
                            continue
                    
                    duration = int(parts[3].strip())
                    
                    rules.append(BetRule(
                        rule_type='s',
                        amount=amount,
                        duration=duration,
                        min_seconds=min_seconds,
                        max_seconds=max_seconds,
                        once_only=once_only
                    ))
                    
                elif rule_type == 'f':
                    # 購買免費遊戲規則: f:金額 或 f:金額:類別
                    amount = float(parts[1].strip())
                    
                    # 解析類別（可選）
                    free_game_type = None
                    if len(parts) >= 3:
                        free_game_type = int(parts[2].strip())
                    
                    rules.append(BetRule(
                        rule_type='f',
                        amount=amount,
                        free_game_type=free_game_type,
                        once_only=once_only
                    ))
                    
                else:
                    self.logger.warning(f"第 {line_number} 行無效的規則類型 '{rule_type}'")
                    continue
                
            except (ValueError, IndexError) as e:
                self.logger.warning(f"第 {line_number} 行無法解析: {e}")
                continue
        
        return rules


# =============================================================================
# 代理伺服器
# =============================================================================

class ProxyConnectionHandler:
    """代理連接處理器。

    處理 HTTP/HTTPS 請求並轉發到上游代理伺服器。
    自動添加代理認證標頭（Proxy-Authorization）。

    此類別實現了 HTTP 代理協議的核心功能:
        - CONNECT 方法: 用於 HTTPS 連接的隧道建立
        - 普通 HTTP 方法: GET、POST 等請求的轉發

    屬性:
        upstream_proxy: 上游代理伺服器資訊。
        logger: 日誌記錄器。

    範例:
        >>> handler = ProxyConnectionHandler(proxy_info)
        >>> handler.handle_connect_request(client_socket, request)
    """

    def __init__(
        self,
        upstream_proxy: ProxyInfo,
        logger: Optional[logging.Logger] = None
    ) -> None:
        """初始化代理連接處理器。

        參數:
            upstream_proxy: 上游代理伺服器資訊。
            logger: 日誌記錄器（可選）。
        """
        self.upstream_proxy = upstream_proxy
        self.logger = logger or LoggerFactory.get_logger()

    def handle_connect_request(
        self,
        client_socket: socket.socket,
        request: bytes
    ) -> None:
        """處理 HTTPS CONNECT 請求。

        建立到上游代理的隧道，並雙向轉發數據。

        參數:
            client_socket: 客戶端 socket。
            request: 原始請求數據。
        """
        upstream_socket = None
        try:
            upstream_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            upstream_socket.settimeout(Constants.DEFAULT_TIMEOUT_SECONDS)
            upstream_socket.connect((self.upstream_proxy.host, self.upstream_proxy.port))

            auth_string = f"{self.upstream_proxy.username}:{self.upstream_proxy.password}"
            auth_b64 = base64.b64encode(auth_string.encode('utf-8')).decode('ascii')

            request_lines = request.split(b'\r\n')
            auth_header = f"Proxy-Authorization: Basic {auth_b64}\r\n".encode('utf-8')

            new_request = request_lines[0] + b'\r\n' + auth_header
            for line in request_lines[1:]:
                new_request += line + b'\r\n'

            upstream_socket.sendall(new_request)

            response = upstream_socket.recv(Constants.PROXY_BUFFER_SIZE)

            if b'200' in response:
                client_socket.sendall(b'HTTP/1.1 200 Connection Established\r\n\r\n')
                self._forward_data(client_socket, upstream_socket)
            else:
                client_socket.sendall(b'HTTP/1.1 502 Bad Gateway\r\n\r\n')
                
        except socket.timeout:
            self.logger.warning("上游代理連接逾時")
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
        """處理普通 HTTP 請求。"""
        upstream_socket = None
        try:
            auth_string = f"{self.upstream_proxy.username}:{self.upstream_proxy.password}"
            auth_b64 = base64.b64encode(auth_string.encode('utf-8')).decode('ascii')
            
            request_lines = request.split(b'\r\n')
            auth_header = f"Proxy-Authorization: Basic {auth_b64}\r\n".encode('utf-8')
            
            new_request = request_lines[0] + b'\r\n' + auth_header
            for line in request_lines[1:]:
                new_request += line + b'\r\n'
            
            upstream_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            upstream_socket.settimeout(Constants.DEFAULT_TIMEOUT_SECONDS)
            upstream_socket.connect((self.upstream_proxy.host, self.upstream_proxy.port))
            upstream_socket.sendall(new_request)
            
            while True:
                response = upstream_socket.recv(Constants.PROXY_BUFFER_SIZE)
                if not response:
                    break
                client_socket.sendall(response)
                
        except socket.timeout:
            self.logger.warning("上游代理回應逾時")
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
        """雙向轉發數據。"""
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
    """簡易 HTTP 代理伺服器。

    將帶認證的遠端代理轉換為本地無需認證的代理。
    每個客戶端連接都在獨立的執行緒中處理。

    屬性:
        local_port: 本地監聽埠號。
        upstream_proxy: 上游代理伺服器資訊。
        running: 伺服器是否運行中。
        server_socket: 伺服器 socket。
        handler: 連接處理器實例。
    """
    
    def __init__(
        self, 
        local_port: int, 
        upstream_proxy: ProxyInfo,
        logger: Optional[logging.Logger] = None
    ):
        self.local_port = local_port
        self.upstream_proxy = upstream_proxy
        self.logger = logger or LoggerFactory.get_logger()
        self.running = False
        self.server_socket: Optional[socket.socket] = None
        self.handler = ProxyConnectionHandler(upstream_proxy, self.logger)
    
    def handle_client(self, client_socket: socket.socket) -> None:
        """處理客戶端連接。"""
        try:
            client_socket.settimeout(Constants.DEFAULT_TIMEOUT_SECONDS)
            
            request = client_socket.recv(Constants.PROXY_BUFFER_SIZE)
            if not request:
                return
            
            first_line = request.split(b'\r\n')[0].decode('utf-8', errors='ignore')
            
            if first_line.startswith('CONNECT'):
                self.handler.handle_connect_request(client_socket, request)
            else:
                self.handler.handle_http_request(client_socket, request)
                
        except socket.timeout:
            self.logger.debug("客戶端連接逾時")
        except Exception as e:
            self.logger.debug(f"處理客戶端連接時發生錯誤: {e}")
        finally:
            with suppress(Exception):
                client_socket.close()
    
    def start(self) -> None:
        """啟動代理伺服器。"""
        self.running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.server_socket.bind((Constants.PROXY_SERVER_BIND_HOST, self.local_port))
            self.server_socket.listen(5)
            
            while self.running:
                try:
                    self.server_socket.settimeout(Constants.SERVER_SOCKET_TIMEOUT)
                    client_socket, address = self.server_socket.accept()
                    
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
                        self.logger.error(f"接受連接時發生錯誤: {e}")
                    
        except Exception as e:
            raise ProxyServerError(f"代理伺服器啟動失敗: {e}") from e
        finally:
            self.stop()
    
    def stop(self) -> None:
        """停止代理伺服器。"""
        self.running = False
        if self.server_socket:
            with suppress(Exception):
                self.server_socket.close()
            self.server_socket = None


class LocalProxyServerManager:
    """本機代理中繼伺服器管理器。

    為每個瀏覽器建立獨立的本機代理埠，支援上下文管理器協議。

    屬性:
        _proxy_servers: 代理伺服器實例字典 (埠號 -> 伺服器)。
        _proxy_threads: 代理執行緒字典 (埠號 -> 執行緒)。
        _next_port: 下一個可用埠號。
        _lock: 執行緒鎖。

    範例:
        >>> with LocalProxyServerManager() as manager:
        ...     port = manager.start_proxy_server(proxy_info)
        ...     # 使用代理...
        # 自動清理所有代理伺服器
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or LoggerFactory.get_logger()
        self._proxy_servers: Dict[int, SimpleProxyServer] = {}
        self._proxy_threads: Dict[int, threading.Thread] = {}
        self._next_port: int = Constants.DEFAULT_PROXY_START_PORT
        self._lock = threading.Lock()
    
    def start_proxy_server(
        self, 
        upstream_proxy: ProxyInfo
    ) -> Optional[int]:
        """啟動本機代理中繼伺服器。
        
        回傳:
            本機埠號，失敗返回 None
        """
        with self._lock:
            local_port = self._next_port
            self._next_port += 1
        
        try:
            server = SimpleProxyServer(local_port, upstream_proxy, self.logger)
            
            def run_server() -> None:
                try:
                    server.start()
                except Exception as e:
                    self.logger.error(f"代理伺服器執行失敗 (埠 {local_port}): {e}")
            
            server_thread = threading.Thread(target=run_server, daemon=True)
            server_thread.start()
            
            with self._lock:
                self._proxy_servers[local_port] = server
                self._proxy_threads[local_port] = server_thread
            
            time.sleep(Constants.PROXY_SERVER_START_WAIT)
            
            return local_port
            
        except Exception as e:
            self.logger.error(f"啟動本機代理伺服器失敗: {e}")
            return None
    
    def stop_proxy_server(self, local_port: int) -> None:
        """停止指定的代理伺服器。"""
        server = None
        
        with self._lock:
            server = self._proxy_servers.pop(local_port, None)
            self._proxy_threads.pop(local_port, None)
        
        if server:
            try:
                server.stop()
            except Exception as e:
                self.logger.debug(f"停止代理伺服器時發生錯誤 (埠 {local_port}): {e}")
    
    def stop_all_servers(self) -> None:
        """停止所有代理伺服器"""
        with self._lock:
            ports = list(self._proxy_servers.keys())
        
        if ports:
            with ThreadPoolExecutor(max_workers=min(len(ports), Constants.MAX_THREAD_WORKERS)) as executor:
                executor.map(self.stop_proxy_server, ports)
    
    def __enter__(self) -> 'LocalProxyServerManager':
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self.stop_all_servers()
        return False


# =============================================================================
# 瀏覽器輔助工具
# =============================================================================

class BrowserHelper:
    """瀏覽器操作輔助類別。
    
    提供常用的瀏覽器操作方法，主要包含：
    - CDP 按鍵模擬
    - 點擊座標計算
    - Canvas 區域取得
    - 彈窗關閉
    
    所有方法皆為靜態方法，無需實例化。
    """
    
    # JavaScript 程式碼常數（避免重複定義）
    JS_CLOSE_POPUPS: str = """
        const popups = document.querySelectorAll('.popup-container, .popup-wrap, .popup-account-container, .ads-pop-container');
        popups.forEach(popup => {
            popup.style.display = 'none';
            popup.style.visibility = 'hidden';
            popup.remove();
        });
        const overlays = document.querySelectorAll('[class*="overlay"], [class*="mask"]');
        overlays.forEach(overlay => overlay.remove());
    """
    
    JS_GET_CANVAS_RECT: str = """
        const canvas = document.getElementById('%s');
        if (canvas) {
            const r = canvas.getBoundingClientRect();
            return {x: r.left, y: r.top, w: r.width, h: r.height};
        }
        return null;
    """
    
    @staticmethod
    def close_popups(driver: WebDriver) -> None:
        """使用 JavaScript 關閉所有彈窗和遮罩層。
        
        參數:
            driver: WebDriver 實例
        """
        driver.execute_script(BrowserHelper.JS_CLOSE_POPUPS)
    
    @staticmethod
    def get_canvas_rect(
        driver: WebDriver,
        canvas_id: str = Constants.GAME_CANVAS,
        max_retries: int = Constants.CANVAS_RETRY_COUNT
    ) -> Optional[Dict[str, float]]:
        """取得 Canvas 元素的位置和大小。
        
        參數:
            driver: WebDriver 實例
            canvas_id: Canvas 元素 ID
            max_retries: 最大重試次數
        
        回傳:
            Canvas 區域資訊 {"x", "y", "w", "h"}，失敗時回傳 None
        """
        for _ in range(max_retries):
            rect = driver.execute_script(
                BrowserHelper.JS_GET_CANVAS_RECT % canvas_id
            )
            if rect:
                return rect
            time.sleep(Constants.CANVAS_RETRY_WAIT)
        return None
    
    @staticmethod
    def execute_cdp_space_key(driver: WebDriver) -> None:
        """使用 Chrome DevTools Protocol 按下空白鍵。
        
        參數:
            driver: WebDriver 實例
        """
        # 按下空白鍵
        driver.execute_cdp_cmd("Input.dispatchKeyEvent", {
            "type": "keyDown",
            "key": " ",
            "code": "Space",
            "windowsVirtualKeyCode": 32,
            "nativeVirtualKeyCode": 32
        })
        # 釋放空白鍵
        driver.execute_cdp_cmd("Input.dispatchKeyEvent", {
            "type": "keyUp",
            "key": " ",
            "code": "Space",
            "windowsVirtualKeyCode": 32,
            "nativeVirtualKeyCode": 32
        })
    
    @staticmethod
    def click_canvas_position(
        driver: WebDriver,
        canvas_rect: Dict[str, float],
        x_ratio: float,
        y_ratio: float
    ) -> Tuple[float, float]:
        """根據 Canvas 區域和比例計算座標並執行 CDP 點擊。
        
        此方法合併了座標計算和點擊執行，簡化呼叫流程。
        
        參數:
            driver: WebDriver 實例
            canvas_rect: Canvas 區域資訊 {"x", "y", "w", "h"}
            x_ratio: X 座標比例
            y_ratio: Y 座標比例
            
        回傳:
            (x, y) 實際點擊座標
        """
        # 計算點擊座標
        x = canvas_rect["x"] + canvas_rect["w"] * x_ratio
        y = canvas_rect["y"] + canvas_rect["h"] * y_ratio
        
        # 執行 CDP 點擊
        for event_type in ["mousePressed", "mouseReleased"]:
            driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
                "type": event_type,
                "x": x,
                "y": y,
                "button": "left",
                "clickCount": 1
            })
        
        return x, y
    
    @staticmethod
    def execute_cdp_click(driver: WebDriver, x: float, y: float) -> None:
        """使用 Chrome DevTools Protocol 執行滑鼠點擊。
        
        參數:
            driver: WebDriver 實例
            x: 點擊 X 座標
            y: 點擊 Y 座標
        """
        for event_type in ["mousePressed", "mouseReleased"]:
            driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
                "type": event_type,
                "x": x,
                "y": y,
                "button": "left",
                "clickCount": 1
            })


# =============================================================================
# 圖片檢測器
# =============================================================================

class ImageDetector:
    """圖片檢測器。

    提供螢幕截圖、圖片比對和座標定位功能。
    使用 OpenCV 的 TM_CCOEFF_NORMED 方法進行模板匹配。

    此類別是圖片識別功能的核心，支援:
        - 瀏覽器截圖
        - 模板匹配
        - 各種模板的截取和儲存

    屬性:
        logger: 日誌記錄器。
        project_root: 專案根目錄路徑。
        image_dir: 圖片目錄路徑。

    範例:
        >>> detector = ImageDetector()
        >>> result = detector.detect_in_browser(driver, "遊戲登入.png")
        >>> if result:
        ...     x, y, confidence = result
        ...     print(f"找到圖片於 ({x}, {y}), 信心度: {confidence:.2f}")
    """

    def __init__(self, logger: Optional[logging.Logger] = None) -> None:
        """初始化圖片檢測器。

        參數:
            logger: 日誌記錄器（可選）。
        """
        self.logger = logger or LoggerFactory.get_logger()

        # 使用輔助函式取得專案根目錄和圖片目錄
        self.project_root: Path = get_resource_path()
        self.image_dir: Path = get_resource_path(Constants.IMAGE_DIR)

        # 確保圖片目錄存在
        self.image_dir.mkdir(parents=True, exist_ok=True)

    def get_template_path(self, template_name: str) -> Path:
        """取得模板圖片路徑。

        參數:
            template_name: 模板圖片檔名。

        回傳:
            模板圖片完整路徑。
        """
        return self.image_dir / template_name

    def template_exists(self, template_name: str) -> bool:
        """檢查模板圖片是否存在。

        參數:
            template_name: 模板圖片檔名。

        回傳:
            是否存在。
        """
        return self.get_template_path(template_name).exists()

    def capture_canvas_screenshot(
        self, 
        driver: WebDriver, 
        save_path: Optional[Path] = None
    ) -> Optional[np.ndarray]:
        """只截取 Canvas 區域的畫面。

        參數:
            driver: WebDriver 實例。
            save_path: 儲存路徑（可選）
            
        回傳:
            OpenCV 格式的圖片陣列 (BGR)，失敗時回傳 None
        """
        try:
            # 取得 Canvas 區域
            rect = BrowserHelper.get_canvas_rect(driver)
            if not rect:
                self.logger.warning("無法取得 Canvas 區域")
                return None
            
            # 取得完整截圖
            full_screenshot = self.capture_screenshot(driver)
            
            # 裁切 Canvas 區域
            x = int(rect['x'])
            y = int(rect['y'])
            w = int(rect['w'])
            h = int(rect['h'])
            
            # 確保座標有效
            height, width = full_screenshot.shape[:2]
            x = max(0, min(x, width))
            y = max(0, min(y, height))
            w = min(w, width - x)
            h = min(h, height - y)
            
            canvas_screenshot = full_screenshot[y:y+h, x:x+w]
            
            # 如果指定了儲存路徑，則儲存圖片
            if save_path:
                save_path.parent.mkdir(parents=True, exist_ok=True)
                
                # 使用支援 Unicode 路徑的方式儲存圖片
                is_success, buffer = cv2.imencode('.png', canvas_screenshot)
                if is_success:
                    with open(save_path, 'wb') as f:
                        f.write(buffer.tobytes())
                    self.logger.info(f"截圖已儲存 {save_path}")
                else:
                    self.logger.error("圖片編碼失敗")
                    return None
            
            return canvas_screenshot
            
        except Exception as e:
            self.logger.error(f"Canvas 截圖失敗: {e}")
            return None

    def capture_screenshot(self, driver: WebDriver, save_path: Optional[Path] = None) -> np.ndarray:
        """截取瀏覽器畫面。

        參數:
            driver: WebDriver 實例。
            save_path: 儲存路徑（可選）
            
        回傳:
            OpenCV 格式的圖片陣列 (BGR)
            
        異常:
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
                
                # 使用支援 Unicode 路徑的方式儲存圖片
                is_success, buffer = cv2.imencode('.png', image_cv)
                if is_success:
                    with open(save_path, 'wb') as f:
                        f.write(buffer.tobytes())
                    self.logger.info(f"截圖已儲存 {save_path}")
                else:
                    raise ImageDetectionError(f"圖片編碼失敗")
            
            return image_cv
            
        except Exception as e:
            raise ImageDetectionError(f"截圖失敗: {e}") from e
    
    def match_template(
        self, 
        screenshot: np.ndarray, 
        template_path: Path, 
        threshold: float = Constants.MATCH_THRESHOLD
    ) -> Optional[Tuple[int, int, float]]:
        """在截圖中尋找模板圖片。
        
        參數:
            screenshot: 截圖（OpenCV 格式）
            template_path: 模板圖片路徑
            threshold: 匹配閾值（0-1）
            
        回傳:
            如果找到: (x, y, confidence) - 中心座標和信心度
            如果未找到: None
            
        異常:
            ImageDetectionError: 檢測失敗
        """
        try:
            if not template_path.exists():
                raise FileNotFoundError(f"模板圖片不存在: {template_path}")
            
            # 讀取模板圖片（使用支援 Unicode 路徑的函式）
            template = cv2_imread_unicode(template_path, cv2.IMREAD_COLOR)
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
    
    def detect_in_browser(
        self, 
        driver: WebDriver, 
        template_name: str, 
        threshold: float = Constants.MATCH_THRESHOLD
    ) -> Optional[Tuple[int, int, float]]:
        """在瀏覽器中檢測模板圖片。
        
        參數:
            driver: WebDriver 實例
            template_name: 模板圖片檔名
            threshold: 匹配閾值
            
        回傳:
            如果找到: (x, y, confidence)
            如果未找到: None
        """
        try:
            # 檢查瀏覽器是否仍然有效
            try:
                _ = driver.current_url
            except Exception:
                self.logger.warning("瀏覽器已關閉，無法進行圖片檢測")
                return None
            
            screenshot = self.capture_screenshot(driver)
            template_path = self.get_template_path(template_name)
            return self.match_template(screenshot, template_path, threshold)
        except Exception as e:
            self.logger.error(f"瀏覽器圖片檢測失敗: {e}")
            return None
    
    def _capture_cropped_template(
        self,
        driver: WebDriver,
        center_x_ratio: float,
        center_y_ratio: float,
        margin_x: int,
        margin_y: int,
        filename: str,
        output_dir: Optional[Path] = None
    ) -> bool:
        """通用的裁切模板截取方法。
        
        參數:
            driver: WebDriver 實例
            center_x_ratio: 中心點 X 座標比例 (0-1)
            center_y_ratio: 中心點 Y 座標比例 (0-1)
            margin_x: 水平裁切邊距（像素）
            margin_y: 垂直裁切邊距（像素）
            filename: 輸出檔名
            output_dir: 輸出目錄（預設為 img/）
            
        回傳:
            截取成功返回 True
        """
        try:
            # 截取整個瀏覽器畫面
            screenshot = driver.get_screenshot_as_png()
            screenshot_img = Image.open(io.BytesIO(screenshot))
            
            # 獲取實際截圖尺寸
            image_width, image_height = screenshot_img.size
            
            # 使用比例計算實際中心座標
            center_x = int(image_width * center_x_ratio)
            center_y = int(image_height * center_y_ratio)
            
            # 計算裁切範圍
            crop_left = max(0, center_x - margin_x)
            crop_top = max(0, center_y - margin_y)
            crop_right = min(image_width, center_x + margin_x)
            crop_bottom = min(image_height, center_y + margin_y)
            
            # 裁切圖片
            cropped_img = screenshot_img.crop((crop_left, crop_top, crop_right, crop_bottom))
            
            # 決定輸出目錄
            if output_dir is None:
                output_dir = get_resource_path("img")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 儲存圖片
            output_path = output_dir / filename
            cropped_img.save(output_path)
            
            # 取得顯示名稱
            display_name = Constants.TEMPLATE_DISPLAY_NAMES.get(filename, filename)
            self.logger.info(f"模板已儲存: {display_name}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"截取模板失敗: {e}")
            return False
    
    def capture_betsize_template(self, driver: WebDriver, amount: float) -> bool:
        """截取下注金額模板。
        
        參數:
            driver: WebDriver 實例
            amount: 下注金額
            
        回傳:
            截取成功返回 True
        """
        try:
            # 使用常數定義：金額顯示位置比例和裁切邊距
            center_x_ratio = Constants.BETSIZE_DISPLAY_X
            center_y_ratio = Constants.BETSIZE_DISPLAY_Y
            margin_x = Constants.BETSIZE_CROP_MARGIN_X
            margin_y = Constants.BETSIZE_CROP_MARGIN_Y
            
            # 截取整個瀏覽器畫面
            screenshot = driver.get_screenshot_as_png()
            screenshot_img = Image.open(io.BytesIO(screenshot))
            
            # 獲取實際截圖尺寸
            image_width, image_height = screenshot_img.size
            
            # 使用比例計算實際中心座標
            center_x = int(image_width * center_x_ratio)
            center_y = int(image_height * center_y_ratio)
            
            # 計算裁切範圍
            crop_left = max(0, center_x - margin_x)
            crop_top = max(0, center_y - margin_y)
            crop_right = min(image_width, center_x + margin_x)
            crop_bottom = min(image_height, center_y + margin_y)
            
            # 裁切圖片
            cropped_img = screenshot_img.crop((crop_left, crop_top, crop_right, crop_bottom))
            
            # 使用輔助函式取得專案根目錄
            bet_size_dir = get_resource_path("img") / "bet_size"
            bet_size_dir.mkdir(parents=True, exist_ok=True)
            
            # 檔名使用金額（整數去掉 .0，小數保留）
            if amount == int(amount):
                filename = f"{int(amount)}.png"
            else:
                filename = f"{amount}.png"
            
            output_path = bet_size_dir / filename
            cropped_img.save(output_path)
            
            self.logger.info(f"模板已儲存: {filename}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"截取金額模板失敗: {e}")
            return False

    def capture_blackscreen_template(self, driver: WebDriver) -> bool:
        """截取黑屏區域模板。
        
        使用 Constants 定義的座標和裁切範圍。
        
        參數:
            driver: WebDriver 實例
            
        回傳:
            截取成功返回 True
        """
        return self._capture_cropped_template(
            driver=driver,
            center_x_ratio=Constants.BLACKSCREEN_CENTER_X,
            center_y_ratio=Constants.BLACKSCREEN_CENTER_Y,
            margin_x=Constants.BLACKSCREEN_CROP_MARGIN_X,
            margin_y=Constants.BLACKSCREEN_CROP_MARGIN_Y,
            filename=Constants.BLACK_SCREEN
        )

    def capture_error_remind_template(self, driver: WebDriver) -> bool:
        """截取錯誤提醒區域模板。
        
        使用 Constants 定義的座標和裁切範圍。
        
        參數:
            driver: WebDriver 實例
            
        回傳:
            截取成功返回 True
        """
        return self._capture_cropped_template(
            driver=driver,
            center_x_ratio=Constants.ERROR_REMIND_CENTER_X,
            center_y_ratio=Constants.ERROR_REMIND_CENTER_Y,
            margin_x=Constants.ERROR_REMIND_CROP_MARGIN_X,
            margin_y=Constants.ERROR_REMIND_CROP_MARGIN_Y,
            filename=Constants.ERROR_REMIND
        )

    def capture_lobby_return_template(self, driver: WebDriver) -> bool:
        """截取大廳返回提示模板。
        
        截取整個瀏覽器畫面（不裁切）。
        
        參數:
            driver: WebDriver 實例
            
        回傳:
            截取成功返回 True
        """
        try:
            # 使用輔助函式取得專案根目錄
            img_dir = get_resource_path("img")
            img_dir.mkdir(parents=True, exist_ok=True)
            
            # 使用常數定義的檔名
            filename = Constants.LOBBY_RETURN
            display_name = Constants.TEMPLATE_DISPLAY_NAMES.get(filename, filename)
            output_path = img_dir / filename
            
            # 截取整個瀏覽器畫面（與 lobby_login 相同方式）
            screenshot = driver.get_screenshot_as_png()
            screenshot_img = Image.open(io.BytesIO(screenshot))
            
            # 直接儲存完整截圖（不裁切）
            screenshot_img.save(output_path)
            
            self.logger.info(f"模板已儲存: {display_name}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"截取大廳返回提示模板失敗: {e}")
            return False

    # -------------------------------------------------------------------------
    # 金額識別相關方法
    # -------------------------------------------------------------------------

    def get_current_betsize(
        self,
        driver: WebDriver,
        retry_count: Optional[int] = None,
        silent: bool = False
    ) -> Optional[float]:
        """取得當前下注金額。
        
        使用圖片比對方式識別目前遊戲畫面中顯示的金額。
        
        參數:
            driver: WebDriver 實例
            retry_count: 重試次數（預設使用常數）
            silent: 是否靜默模式（不輸出詳細日誌）
            
        回傳:
            當前金額，失敗返回 None
        """
        if retry_count is None:
            retry_count = Constants.BETSIZE_READ_MAX_RETRIES
        
        for attempt in range(retry_count):
            try:
                if attempt > 0:
                    time.sleep(Constants.BETSIZE_READ_RETRY_WAIT)
                
                # 截取整個瀏覽器截圖
                screenshot = driver.get_screenshot_as_png()
                screenshot_np = np.array(Image.open(io.BytesIO(screenshot)))
                screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)
                
                # 與資料夾中的圖片進行比對
                matched_amount, confidence = self._compare_betsize_images(screenshot_gray)
                
                if matched_amount:
                    try:
                        amount_value = float(matched_amount)
                        # 使用 Constants.GAME_BETSIZE 進行驗證
                        if amount_value in Constants.GAME_BETSIZE:
                            if not silent:
                                self.logger.info(f"目前金額: {amount_value}")
                            return amount_value
                    except ValueError:
                        pass
                
            except Exception as e:
                if not silent:
                    self.logger.error(f"查詢下注金額時發生錯誤: {e}")
        
        return None

    def _compare_betsize_images(
        self,
        screenshot_gray: np.ndarray
    ) -> Tuple[Optional[str], float]:
        """使用 bet_size 資料夾中的圖片比對。
        
        參數:
            screenshot_gray: 截圖（灰階）
            
        回傳:
            (匹配的金額, 信心度)
        """
        try:
            bet_size_dir = get_resource_path("img") / "bet_size"
            
            if not bet_size_dir.exists():
                self.logger.warning(f"bet_size 資料夾不存在: {bet_size_dir}")
                try:
                    bet_size_dir.mkdir(parents=True, exist_ok=True)
                    self.logger.info(f"已建立 bet_size 資料夾: {bet_size_dir}")
                except Exception as e:
                    self.logger.error(f"無法建立 bet_size 資料夾: {e}")
                    return None, 0.0
            
            # 取得所有 png 圖片
            image_files = sorted(bet_size_dir.glob("*.png"))
            if not image_files:
                self.logger.warning("bet_size 資料夾中沒有圖片")
                return None, 0.0
            
            # 儲存所有匹配結果
            match_results = []
            
            for image_file in image_files:
                # 讀取模板圖片（使用支援 Unicode 路徑的函式）
                template = cv2_imread_unicode(image_file, cv2.IMREAD_GRAYSCALE)
                if template is None:
                    continue
                
                # 檢查尺寸
                if (screenshot_gray.shape[0] < template.shape[0] or 
                    screenshot_gray.shape[1] < template.shape[1]):
                    continue
                
                # 執行模板匹配
                result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, _ = cv2.minMaxLoc(result)
                
                match_results.append((image_file.stem, max_val))
            
            if not match_results:
                return None, 0.0
            
            # 按信心度排序
            match_results.sort(key=lambda x: x[1], reverse=True)
            best_match_amount, best_match_score = match_results[0]
            
            # 使用常數定義的閾值
            if best_match_score >= Constants.BETSIZE_MATCH_THRESHOLD:
                return best_match_amount, best_match_score
            else:
                return None, best_match_score
                
        except Exception as e:
            self.logger.error(f"比對圖片時發生錯誤: {e}")
            return None, 0.0

    def click_betsize_button(self, driver: WebDriver, x_ratio: float, y_ratio: float) -> None:
        """點擊下注金額調整按鈕。"""
        # 取得畫面尺寸
        screenshot = driver.get_screenshot_as_png()
        w, h = Image.open(io.BytesIO(screenshot)).size
        x, y = int(w * x_ratio), int(h * y_ratio)
        
        # 使用標準 CDP 點擊
        BrowserHelper.execute_cdp_click(driver, x, y)

    def adjust_betsize(
        self,
        driver: WebDriver,
        target_amount: float,
        stop_event: Optional[threading.Event] = None
    ) -> bool:
        """調整下注金額到目標值（無限等待版）。"""
        # 決定調整方向的按鈕座標
        target_index = Constants.GAME_BETSIZE.index(target_amount)
        increase_btn = (Constants.BETSIZE_INCREASE_BUTTON_X, Constants.BETSIZE_INCREASE_BUTTON_Y)
        decrease_btn = (Constants.BETSIZE_DECREASE_BUTTON_X, Constants.BETSIZE_DECREASE_BUTTON_Y)
        
        attempt = 0
        while True:
            # 檢查停止事件
            if stop_event and stop_event.is_set():
                self.logger.info("金額調整已被停止")
                return False
            
            attempt += 1
            current = self.get_current_betsize(driver, silent=True)
            
            # 無法識別金額，繼續等待
            if current is None:
                if attempt == 1 or attempt % 20 == 0:
                    self.logger.warning(f"無法識別金額，持續等待中... (嘗試 {attempt} 次)")
                time.sleep(Constants.BETSIZE_ADJUST_RETRY_WAIT)
                continue
            
            # 已達目標
            if current == target_amount:
                return True
            
            # 點擊調整按鈕
            current_index = Constants.GAME_BETSIZE.index(current)
            btn = increase_btn if target_index > current_index else decrease_btn
            self.click_betsize_button(driver, btn[0], btn[1])
            time.sleep(Constants.BETSIZE_ADJUST_STEP_WAIT)


# =============================================================================
# 瀏覽器管理器
# =============================================================================

class BrowserManager:
    """瀏覽器管理器。

    提供 WebDriver 建立和配置功能，包含:
        - Chrome 選項配置
        - 代理伺服器設定
        - 效能優化參數

    屬性:
        logger: 日誌記錄器。
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or LoggerFactory.get_logger()
    
    @staticmethod
    def create_chrome_options(local_proxy_port: Optional[int] = None) -> Options:
        """建立 Chrome 瀏覽器選項。"""
        chrome_options = Options()
        
        # 本機代理設定
        if local_proxy_port:
            proxy_address = f"http://{Constants.PROXY_SERVER_BIND_HOST}:{local_proxy_port}"
            chrome_options.add_argument(f"--proxy-server={proxy_address}")
        
        # 基本設定
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        
        # 背景執行優化設定
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_argument("--disable-background-timer-throttling")
        
        # 啟用網路加速功能
        chrome_options.add_argument("--enable-features=NetworkService,NetworkServiceInProcess")
        chrome_options.add_argument("--enable-quic")
        chrome_options.add_argument("--enable-tcp-fast-open")
        
        # 其他優化設定
        chrome_options.add_argument("--disable-sync")
        chrome_options.add_argument("--metrics-recording-only")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--disable-extensions")
        
        # 記憶體與渲染優化
        chrome_options.add_argument("--disk-cache-size=209715200")
        chrome_options.add_argument("--media-cache-size=209715200")
        
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
            "profile.content_settings.exceptions.sound": {
                "*": {"setting": 2}
            }
        })
        
        return chrome_options
    
    def create_webdriver(
        self, 
        local_proxy_port: Optional[int] = None
    ) -> WebDriver:
        """建立 WebDriver 實例。
        
        優先使用 WebDriver Manager，若失敗則使用本機驅動程式。
        """
        chrome_options = self.create_chrome_options(local_proxy_port)
        driver = None
        errors = []
        
        # 方法 1: 優先使用 WebDriver Manager
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
        except Exception as e:
            errors.append(f"WebDriver Manager: {e}")
            self.logger.warning("WebDriver Manager 失敗，嘗試使用本機驅動程式")
            
            # 方法 2: 使用本機驅動程式
            try:
                driver = self._create_webdriver_with_local_driver(chrome_options)
            except Exception as e2:
                errors.append(f"本機驅動程式: {e2}")
                self.logger.error(f"本機驅動程式也失敗: {e2}")
        
        if driver is None:
            error_message = "無法建立瀏覽器實例。\n" + "\n".join(f"- {error}" for error in errors)
            raise BrowserCreationError(error_message)
        
        self._configure_webdriver(driver)
        return driver
    
    def _configure_webdriver(self, driver: WebDriver) -> None:
        """配置 WebDriver 超時和優化設定。"""
        with suppress(Exception):
            driver.set_page_load_timeout(Constants.DEFAULT_PAGE_LOAD_TIMEOUT)
            driver.set_script_timeout(Constants.DEFAULT_SCRIPT_TIMEOUT)
            driver.implicitly_wait(Constants.DEFAULT_IMPLICIT_WAIT)
        
        with suppress(Exception):
            driver.execute_cdp_cmd("Network.enable", {})
            driver.execute_cdp_cmd("Network.emulateNetworkConditions", {
                "offline": False,
                "downloadThroughput": -1,
                "uploadThroughput": -1,
                "latency": 0
            })
    
    def _create_webdriver_with_local_driver(self, chrome_options: Options) -> WebDriver:
        """使用本機驅動程式建立 WebDriver。"""
        project_root = get_resource_path()
        driver_path = project_root / "chromedriver.exe"
        
        if not driver_path.exists():
            raise FileNotFoundError(
                f"找不到驅動程式檔案\n"
                f"請確保 chromedriver.exe 存在於專案根目錄"
            )
        
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
        """建立瀏覽器上下文管理器。"""
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


# =============================================================================
# 遊戲控制面板
# =============================================================================

class GameControlCenter:
    """遊戲控制面板。

    提供互動式命令列介面來控制多個瀏覽器，功能包括:
        - 自動按鍵: 每個瀏覽器獨立執行緒
        - 暫停/繼續操作
        - 調整下注金額
        - 購買免費遊戲
        - 截取各種模板圖片
        - 錯誤監控與自動恢復

    屬性:
        browser_threads: 瀏覽器執行緒列表。
        bet_rules: 下注規則列表。
        canvas_rect: Canvas 區域資訊。
        running: 控制面板是否運行中。
        auto_press_running: 自動按鍵是否運行中。
        error_monitor_running: 錯誤監控是否運行中。

    範例:
        >>> center = GameControlCenter(browser_threads, rules)
        >>> center.start()  # 阻塞式運行，直到使用者退出
    """

    def __init__(
        self,
        browser_threads: List['BrowserThread'],
        bet_rules: List[BetRule],
        canvas_rect: Optional[Dict[str, float]] = None,
        logger: Optional[logging.Logger] = None
    ) -> None:
        """初始化控制面板。

        參數:
            browser_threads: 瀏覽器執行緒列表。
            bet_rules: 下注規則列表。
            canvas_rect: Canvas 區域資訊（可選）。
            logger: 日誌記錄器（可選）。
        """
        self.logger = logger or LoggerFactory.get_logger()
        self.browser_threads = browser_threads
        self.bet_rules = bet_rules
        self.canvas_rect = canvas_rect

        # 控制狀態
        self.running: bool = False
        self.auto_press_running: bool = False
        self.error_monitor_running: bool = False
        self.rule_running: bool = False

        # 執行緒控制
        self._stop_event = threading.Event()
        self._error_monitor_stop_event = threading.Event()
        self.auto_press_threads: Dict[int, threading.Thread] = {}
        self._error_monitor_thread: Optional[threading.Thread] = None
        self._rule_thread: Optional[threading.Thread] = None

        # 正在恢復中的瀏覽器（避免重複觸發恢復）
        self._recovering_browsers: Set[int] = set()
        self._recovering_lock = threading.Lock()

        # 圖片檢測器
        self._image_detector = ImageDetector(self.logger)

        # 自動按鍵間隔時間
        self.min_interval: float = 1.0
        self.max_interval: float = 2.0
        
        # 規則執行時間控制
        self._rule_execution_start_time: Optional[float] = None
        self._rule_execution_max_hours: Optional[float] = None
        self._time_monitor_thread: Optional[threading.Thread] = None
        
        # 自動啟動控制
        self._auto_start_timer: Optional[threading.Timer] = None
        self._user_has_input: bool = False

    # -------------------------------------------------------------------------
    # 通用輔助方法
    # -------------------------------------------------------------------------

    def _execute_on_active_browsers(
        self,
        task_func: Callable[['BrowserContext'], Any],
        operation_name: str = "操作",
        show_result: bool = True
    ) -> Dict[int, Any]:
        """對所有活躍瀏覽器並行執行任務（DRY 統一方法）。
        
        此方法封裝了重複的 ThreadPoolExecutor 並行執行模式，
        統一處理瀏覽器過濾、結果收集和日誌輸出。
        
        參數:
            task_func: 任務函數，接收 BrowserContext 作為參數
            operation_name: 操作名稱（用於日誌輸出）
            show_result: 是否顯示執行結果統計
            
        回傳:
            字典，key 為瀏覽器索引，value 為執行結果（True/False 或具體值）
        """
        active_browsers = [
            bt for bt in self._get_active_browsers()
            if bt.is_browser_alive() and bt.context
        ]
        
        if not active_browsers:
            self.logger.warning(f"沒有可用的瀏覽器執行{operation_name}")
            return {}
        
        results: Dict[int, Any] = {}
        
        with ThreadPoolExecutor(max_workers=len(active_browsers)) as executor:
            futures = {
                executor.submit(bt.execute_task, task_func): bt
                for bt in active_browsers
            }
            
            for future in futures:
                bt = futures[future]
                try:
                    results[bt.index] = future.result()
                except Exception as e:
                    username = bt.context.credential.username if bt.context else "Unknown"
                    self.logger.error(f"瀏覽器 {bt.index} ({username}) {operation_name}失敗: {e}")
                    results[bt.index] = False
        
        # 顯示結果統計
        if show_result:
            success_count = sum(1 for v in results.values() if v)
            total = len(active_browsers)
            
            if success_count == total:
                self.logger.info(f"{operation_name}完成: 全部 {success_count} 個瀏覽器成功")
            else:
                self.logger.warning(f"{operation_name}部分完成: {success_count}/{total} 個瀏覽器成功")
        
        return results

    def _get_active_browsers(self) -> List['BrowserThread']:
        """取得所有活躍的瀏覽器執行緒。

        回傳:
            活躍的瀏覽器執行緒列表。
        """
        return [bt for bt in self.browser_threads if bt.is_browser_alive()]

    # -------------------------------------------------------------------------
    # 錯誤訊息監控功能
    # -------------------------------------------------------------------------

    def _error_monitor_loop(self) -> None:
        """錯誤訊息、黑屏監控與自動跳過點擊循環。
        
        在背景持續運行，每隔固定時間同步檢測所有瀏覽器：
        - 黑屏（BLACK_SCREEN）: 連續檢測到 BLACKSCREEN_CONSECUTIVE_THRESHOLD 次 → 導航到 LOGIN_PAGE
        - 錯誤訊息（ERROR_REMIND）: 檢測到 1 次 → 點擊 ERROR_CONFIRM 按鈕
        - 自動跳過點擊：每隔 AUTO_CLICK_INTERVAL 秒，對所有瀏覽器執行跳過點擊
        
        檢測流程同步並行，恢復操作在獨立執行緒中非同步執行（不阻塞監控）。
        """
        self.logger.info("錯誤訊息、黑屏監控與自動跳過點擊已啟動")
        
        # 自動跳過點擊計時器
        last_skip_click_time = time.time()
        skip_click_count = 0
        
        # 黑屏連續檢測計數器（每個瀏覽器獨立計數）
        blackscreen_counts: Dict[int, int] = {}
        
        # 檢查模板是否存在
        blackscreen_template_exists = self._image_detector.template_exists(Constants.BLACK_SCREEN)
        error_template_exists = self._image_detector.template_exists(Constants.ERROR_REMIND)
        
        if not blackscreen_template_exists:
            self.logger.warning(f"黑屏模板 '{Constants.BLACK_SCREEN}' 不存在")
            self.logger.info("請使用 'd' 命令截取黑屏模板")
        
        if not error_template_exists:
            self.logger.warning(f"錯誤訊息模板 '{Constants.ERROR_REMIND}' 不存在")
            self.logger.info("請使用 'e' 命令截取錯誤訊息模板")
        
        while not self._error_monitor_stop_event.is_set():
            try:
                # 取得所有活躍的瀏覽器（排除正在恢復中的）
                with self._recovering_lock:
                    active_browsers = [
                        bt for bt in self._get_active_browsers()
                        if bt.index not in self._recovering_browsers
                    ]
                
                if not active_browsers:
                    self._error_monitor_stop_event.wait(timeout=Constants.ERROR_MONITOR_INTERVAL)
                    continue
                
                # 每次循環更新模板存在狀態（支援動態建立模板）
                blackscreen_template_exists = self._image_detector.template_exists(Constants.BLACK_SCREEN)
                error_template_exists = self._image_detector.template_exists(Constants.ERROR_REMIND)
                
                # 如果兩個模板都不存在，等待後繼續
                if not blackscreen_template_exists and not error_template_exists:
                    self._error_monitor_stop_event.wait(timeout=Constants.ERROR_MONITOR_INTERVAL)
                    continue
                
                # ===== 同時檢測所有瀏覽器的黑屏和錯誤訊息 =====
                blackscreen_detected: Dict[int, bool] = {}
                error_detected: Dict[int, bool] = {}
                
                def detect_for_browser(bt: 'BrowserThread') -> Tuple[int, bool, bool]:
                    """同時檢測單個瀏覽器的黑屏和錯誤訊息。
                    
                    回傳: (browser_index, 是否黑屏, 是否錯誤訊息)
                    """
                    if not bt.is_browser_alive() or not bt.context:
                        return (bt.index, False, False)
                    try:
                        def task(context: BrowserContext) -> Tuple[bool, bool]:
                            is_blackscreen = False
                            is_error = False
                            
                            # 檢測黑屏
                            if blackscreen_template_exists:
                                result = self._image_detector.detect_in_browser(
                                    context.driver, Constants.BLACK_SCREEN
                                )
                                is_blackscreen = result is not None
                            
                            # 檢測錯誤訊息
                            if error_template_exists:
                                result = self._image_detector.detect_in_browser(
                                    context.driver, Constants.ERROR_REMIND
                                )
                                is_error = result is not None
                            
                            return (is_blackscreen, is_error)
                        
                        is_blackscreen, is_error = bt.execute_task(task)
                        return (bt.index, is_blackscreen, is_error)
                    except Exception:
                        return (bt.index, False, False)
                
                # 並行檢測所有瀏覽器
                with ThreadPoolExecutor(max_workers=len(active_browsers)) as executor:
                    futures = [executor.submit(detect_for_browser, bt) for bt in active_browsers]
                    for future in futures:
                        try:
                            browser_index, is_blackscreen, is_error = future.result(timeout=10)
                            blackscreen_detected[browser_index] = is_blackscreen
                            error_detected[browser_index] = is_error
                        except Exception:
                            pass
                
                # ===== 處理檢測結果，啟動非同步恢復執行緒 =====
                for bt in active_browsers:
                    if self._error_monitor_stop_event.is_set():
                        break
                    
                    browser_index = bt.index
                    username = bt.context.credential.username if bt.context else "Unknown"
                    
                    # 處理黑屏
                    if blackscreen_detected.get(browser_index, False):
                        current_count = blackscreen_counts.get(browser_index, 0) + 1
                        blackscreen_counts[browser_index] = current_count
                        
                        self.logger.debug(
                            f"瀏覽器 {browser_index} ({username}) "
                            f"黑屏檢測 {current_count}/{Constants.BLACKSCREEN_CONSECUTIVE_THRESHOLD}"
                        )
                        
                        if current_count >= Constants.BLACKSCREEN_CONSECUTIVE_THRESHOLD:
                            self.logger.warning(
                                f"瀏覽器 {browser_index} ({username}) "
                                f"連續 {current_count} 次黑屏，啟動恢復執行緒..."
                            )
                            blackscreen_counts[browser_index] = 0
                            # 非同步啟動恢復執行緒
                            self._start_recovery_thread(bt, "blackscreen")
                    else:
                        blackscreen_counts[browser_index] = 0
                    
                    # 處理錯誤訊息
                    if error_detected.get(browser_index, False):
                        self.logger.warning(
                            f"瀏覽器 {browser_index} ({username}) 偵測到錯誤訊息，處理中..."
                        )
                        # 非同步啟動點擊執行緒
                        self._start_recovery_thread(bt, "error")
                
                # ===== 自動跳過點擊（每隔 AUTO_CLICK_INTERVAL 秒執行一次）=====
                current_time = time.time()
                if current_time - last_skip_click_time >= Constants.AUTO_CLICK_INTERVAL:
                    last_skip_click_time = current_time
                    skip_click_count += 1
                    
                    # 對所有活躍瀏覽器執行點擊關閉按鈕（排除正在恢復中的）
                    for bt in active_browsers:
                        if self._error_monitor_stop_event.is_set():
                            break
                        try:
                            if not bt.is_browser_alive() or not bt.context:
                                continue
                            
                            def skip_click_task(context: BrowserContext) -> bool:
                                """執行點擊關閉按鈕。"""
                                driver = context.driver
                                rect = BrowserHelper.get_canvas_rect(driver)
                                if not rect:
                                    return False
                                
                                # 點擊跳過按鈕座標
                                BrowserHelper.click_canvas_position(
                                    driver, rect,
                                    Constants.AUTO_SKIP_CLICK_X_RATIO,
                                    Constants.AUTO_SKIP_CLICK_Y_RATIO
                                )
                                # 點擊自動關閉座標
                                BrowserHelper.click_canvas_position(
                                    driver, rect,
                                    Constants.AUTO_CLOSE_CLICK_X_RATIO,
                                    Constants.AUTO_CLOSE_CLICK_Y_RATIO
                                )
                                return True
                            
                            bt.execute_task(skip_click_task, timeout=5)
                        except Exception:
                            # 靜默處理錯誤，避免日誌過多
                            pass
                    
                    # 每 10 次顯示一次統計
                    if skip_click_count % 10 == 0:
                        self.logger.debug(f"自動跳過已執行 {skip_click_count} 次")
                
                # 等待下一次檢測
                self._error_monitor_stop_event.wait(timeout=Constants.ERROR_MONITOR_INTERVAL)
                
            except Exception as e:
                self.logger.error(f"監控循環發生錯誤: {e}")
                self._error_monitor_stop_event.wait(timeout=Constants.ERROR_MONITOR_INTERVAL)
        
        self.logger.info(f"錯誤訊息、黑屏監控與自動跳過點擊已停止（共執行 {skip_click_count} 次跳過點擊）")
    
    def _start_recovery_thread(self, bt: 'BrowserThread', recovery_type: str) -> None:
        """啟動非同步恢復執行緒。
        
        參數:
            bt: 需要恢復的 BrowserThread 實例
            recovery_type: 恢復類型 ("blackscreen" 或 "error")
        """
        browser_index = bt.index
        
        # 標記為恢復中
        with self._recovering_lock:
            if browser_index in self._recovering_browsers:
                self.logger.debug(f"瀏覽器 {browser_index} 已在恢復中，跳過")
                return
            self._recovering_browsers.add(browser_index)
        
        def recovery_task() -> None:
            try:
                if recovery_type == "blackscreen":
                    self._handle_blackscreen_recovery(bt)
                elif recovery_type == "error":
                    self._handle_error_click_confirm(bt)
            finally:
                # 恢復完成，移除標記
                with self._recovering_lock:
                    self._recovering_browsers.discard(browser_index)
        
        # 啟動獨立執行緒執行恢復
        thread = threading.Thread(
            target=recovery_task,
            daemon=True,
            name=f"Recovery-{browser_index}-{recovery_type}"
        )
        thread.start()
    
    def _handle_error_click_confirm(self, bt: 'BrowserThread') -> None:
        """處理錯誤訊息：點擊確認按鈕。
        
        當偵測到「錯誤訊息.png」時，切換到 iframe 並點擊確認按鈕座標。
        包含網路容錯機制，失敗時自動重試。
        
        參數:
            bt: 發生錯誤的 BrowserThread 實例
        """
        username = bt.context.credential.username if bt.context else "Unknown"
        
        # 最多重試 MAX_RETRY_ATTEMPTS 次
        for attempt in range(Constants.MAX_RETRY_ATTEMPTS):
            try:
                if attempt > 0:
                    self.logger.debug(f"瀏覽器 {bt.index} 恢復流程重試第 {attempt + 1} 次...")
                    time.sleep(Constants.RETRY_INTERVAL)
                
                def click_error_confirm_task(context: BrowserContext) -> bool:
                    """點擊錯誤訊息確認按鈕。"""
                    driver = context.driver
                    
                    # 切換到 iframe（Canvas 在 iframe 內），使用較長超時
                    driver.switch_to.default_content()
                    iframe = WebDriverWait(driver, Constants.ELEMENT_WAIT_TIMEOUT).until(
                        EC.presence_of_element_located((By.XPATH, Constants.GAME_IFRAME))
                    )
                    driver.switch_to.frame(iframe)
                    time.sleep(Constants.NORMAL_WAIT)
                    
                    # 取得 Canvas 區域
                    rect = BrowserHelper.get_canvas_rect(driver)
                    if not rect:
                        return False
                    
                    time.sleep(Constants.SHORT_WAIT)
                    
                    # 計算座標並點擊確認按鈕
                    BrowserHelper.click_canvas_position(
                        driver, rect,
                        Constants.ERROR_CONFIRM_BUTTON_X_RATIO,
                        Constants.ERROR_CONFIRM_BUTTON_Y_RATIO
                    )
                    return True
                
                result = bt.execute_task(click_error_confirm_task)
                
                if result:
                    self.logger.info(
                        f"瀏覽器 {bt.index} ({username}) 已點擊錯誤訊息確認按鈕"
                    )
                    return  # 成功，退出重試循環
                else:
                    self.logger.warning(f"瀏覽器 {bt.index} ({username}) 無法找到 Canvas 元素")
                    
            except Exception as e:
                if attempt < Constants.MAX_RETRY_ATTEMPTS - 1 and is_network_error(e):
                    self.logger.warning(f"瀏覽器 {bt.index} ({username}) 點擊確認流程超時，準備重試...")
                    continue
                else:
                    self.logger.error(f"瀏覽器 {bt.index} ({username}) 點擊確認流程失敗: {e}")
                    return
    
    def _handle_blackscreen_recovery(self, bt: 'BrowserThread') -> None:
        """處理黑屏恢復：完整的重新連線流程。
        
        當連續偵測到黑屏達到閾值時，執行完整恢復流程：
        1. 導航到 LOGIN_PAGE
        2. 進入遊戲
        3. 執行圖片檢測流程，檢測 game_login 和 error_remind
        
        包含網路容錯機制，失敗時自動重試。
        
        參數:
            bt: 發生黑屏的 BrowserThread 實例
        """
        username = bt.context.credential.username if bt.context else "Unknown"
        browser_index = bt.index
        
        self.logger.info(f"瀏覽器 {browser_index} ({username}) 開始執行黑屏恢復流程...")
        
        try:
            # ===== 步驟 1: 導航到登入頁面 =====
            self.logger.info(f"瀏覽器 {browser_index} 步驟 1/3: 導航到登入頁面")
            if not self._recovery_navigate_to_login(bt):
                self.logger.error(f"瀏覽器 {browser_index} ({username}) 導航到登入頁面失敗")
                return
            
            # ===== 步驟 2: 進入遊戲 =====
            self.logger.info(f"瀏覽器 {browser_index} 步驟 2/3: 進入遊戲")
            if not self._recovery_navigate_to_game(bt):
                self.logger.error(f"瀏覽器 {browser_index} ({username}) 進入遊戲失敗")
                return
            
            # ===== 步驟 3: 執行圖片檢測流程 =====
            self.logger.info(f"瀏覽器 {browser_index} 步驟 3/3: 執行圖片檢測流程")
            if not self._recovery_image_detection_flow(bt):
                self.logger.error(f"瀏覽器 {browser_index} ({username}) 圖片檢測流程失敗")
                return
            
            self.logger.info(f"瀏覽器 {browser_index} ({username}) 黑屏恢復完成")
            
        except Exception as e:
            self.logger.error(f"瀏覽器 {browser_index} ({username}) 黑屏恢復發生異常: {e}")
    
    def _recovery_navigate_to_login(self, bt: 'BrowserThread') -> bool:
        """恢復流程：導航到登入頁面。"""
        for attempt in range(Constants.MAX_RETRY_ATTEMPTS):
            try:
                if attempt > 0:
                    time.sleep(Constants.RETRY_INTERVAL)
                
                def task(context: BrowserContext) -> bool:
                    driver = context.driver
                    driver.switch_to.default_content()
                    driver.get(Constants.LOGIN_PAGE)
                    WebDriverWait(driver, Constants.ELEMENT_WAIT_TIMEOUT_LONG).until(
                        lambda d: d.execute_script("return document.readyState") == "complete"
                    )
                    time.sleep(Constants.PAGE_LOAD_WAIT)
                    return True
                
                if bt.execute_task(task):
                    return True
                    
            except Exception as e:
                if attempt == Constants.MAX_RETRY_ATTEMPTS - 1:
                    self.logger.debug(f"導航失敗: {e}")
        return False    

    def _recovery_navigate_to_game(self, bt: 'BrowserThread') -> bool:
        """恢復流程：搜尋遊戲並進入（參考 navigate_to_game）。"""
        for attempt in range(Constants.MAX_RETRY_ATTEMPTS):
            try:
                if attempt > 0:
                    time.sleep(Constants.RETRY_INTERVAL)
                
                def task(context: BrowserContext) -> bool:
                    driver = context.driver
                    
                    # 1. 關閉可能出現的公告彈窗
                    try:
                        BrowserHelper.close_popups(driver)
                        time.sleep(Constants.NORMAL_WAIT)
                    except Exception:
                        pass
                    
                    # 2. 用背景圖片找遊戲卡片並點擊
                    game_pattern = Constants.get_game_pattern()
                    game_selector = f"//div[contains(@class, 'game-img') and contains(@style, '{game_pattern}')]"
                    game_element = WebDriverWait(driver, Constants.ELEMENT_WAIT_TIMEOUT).until(
                        EC.presence_of_element_located((By.XPATH, game_selector))
                    )
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", game_element)
                    time.sleep(Constants.NORMAL_WAIT)
                    driver.execute_script("arguments[0].click();", game_element)
                    time.sleep(Constants.PAGE_LOAD_WAIT_LONG)
                    
                    # 3. 切換到 iframe
                    time.sleep(Constants.PAGE_LOAD_WAIT)
                    iframe = WebDriverWait(driver, Constants.ELEMENT_WAIT_TIMEOUT_LONG).until(
                        EC.presence_of_element_located((By.XPATH, Constants.GAME_IFRAME))
                    )
                    driver.switch_to.frame(iframe)
                    
                    # 4. 驗證 Canvas 存在
                    WebDriverWait(driver, Constants.ELEMENT_WAIT_TIMEOUT).until(
                        lambda d: d.execute_script(f"return document.getElementById('{Constants.GAME_CANVAS}') !== null;")
                    )
                    
                    return True
                
                if bt.execute_task(task):
                    return True
                    
            except Exception as e:
                if attempt == Constants.MAX_RETRY_ATTEMPTS - 1:
                    self.logger.debug(f"進入遊戲失敗: {e}")
        return False
    
    def _recovery_image_detection_flow(self, bt: 'BrowserThread') -> bool:
        """恢復流程：執行圖片檢測流程（參照登入流程）。
        
        流程：
        1. 檢測 game_login → 點擊
        2. 檢測 game_confirm 或 error_remind → 點擊對應按鈕
        """
        username = bt.context.credential.username if bt.context else "Unknown"
        browser_index = bt.index
        
        # ===== 階段 1: 檢測並點擊 game_login =====
        self.logger.info(f"瀏覽器 {browser_index} 【階段 1】檢測 遊戲登入...")
        if not self._recovery_detect_and_click(
            bt, 
            Constants.GAME_LOGIN, 
            Constants.GAME_LOGIN_BUTTON_X_RATIO,
            Constants.GAME_LOGIN_BUTTON_Y_RATIO
        ):
            self.logger.warning(f"瀏覽器 {browser_index} 未檢測到 遊戲登入 或點擊失敗")
            # 即使 game_login 失敗也繼續嘗試下一步
        
        time.sleep(Constants.SCREEN_SWITCH_WAIT)  # 等待畫面切換
        
        # ===== 階段 2: 優先檢測 game_confirm，若無則檢測 error_remind =====
        self.logger.info(f"瀏覽器 {browser_index} 【階段 2】檢測 遊戲開始 或 錯誤訊息...")
        
        # 先嘗試檢測 game_confirm（正常流程）
        game_confirm_exists = self._image_detector.template_exists(Constants.GAME_CONFIRM)
        error_remind_exists = self._image_detector.template_exists(Constants.ERROR_REMIND)
        
        if not game_confirm_exists and not error_remind_exists:
            self.logger.warning(f"瀏覽器 {browser_index} 無可用模板，跳過階段 2")
            return True
        
        # 使用改進的檢測邏輯：同時檢查兩個模板，哪個先出現就處理哪個
        detected_template = None
        attempt = 0
        max_attempts = Constants.RECOVERY_DETECTION_ATTEMPTS
        
        while detected_template is None and attempt < max_attempts:
            attempt += 1
            
            try:
                def detect_both_task(context: BrowserContext) -> Optional[str]:
                    """同時檢測 game_confirm 和 error_remind，返回先檢測到的模板名稱。"""
                    # 優先檢測 game_confirm（正常流程）
                    if game_confirm_exists:
                        result = self._image_detector.detect_in_browser(
                            context.driver, Constants.GAME_CONFIRM
                        )
                        if result is not None:
                            return Constants.GAME_CONFIRM
                    
                    # 再檢測 error_remind
                    if error_remind_exists:
                        result = self._image_detector.detect_in_browser(
                            context.driver, Constants.ERROR_REMIND
                        )
                        if result is not None:
                            return Constants.ERROR_REMIND
                    
                    return None
                
                detected_template = bt.execute_task(detect_both_task, timeout=10)
                
            except Exception as e:
                self.logger.debug(f"瀏覽器 {browser_index} 檢測時發生錯誤: {e}")
            
            if detected_template is None:
                # 每 10 次檢測顯示一次進度
                if attempt % Constants.DETECTION_PROGRESS_INTERVAL == 0:
                    self.logger.info(f"瀏覽器 {browser_index} 等待畫面... (已嘗試 {attempt} 次)")
                
                time.sleep(Constants.DETECTION_INTERVAL)
        
        # 根據檢測結果處理
        if detected_template == Constants.GAME_CONFIRM:
            display_name = Constants.TEMPLATE_DISPLAY_NAMES.get(Constants.GAME_CONFIRM, Constants.GAME_CONFIRM)
            self.logger.info(f"瀏覽器 {browser_index} ({username}) 檢測到 {display_name}")
            
            # 等待一下再點擊
            time.sleep(Constants.NORMAL_WAIT)
            self._recovery_click_button(
                bt,
                Constants.GAME_CONFIRM_BUTTON_X_RATIO,
                Constants.GAME_CONFIRM_BUTTON_Y_RATIO,
                display_name
            )
            
        elif detected_template == Constants.ERROR_REMIND:
            display_name = Constants.TEMPLATE_DISPLAY_NAMES.get(Constants.ERROR_REMIND, Constants.ERROR_REMIND)
            self.logger.info(f"瀏覽器 {browser_index} ({username}) 檢測到 {display_name}，點擊確認...")
            
            # 等待一下再點擊
            time.sleep(Constants.NORMAL_WAIT)
            self._recovery_click_error_confirm(bt)
            
        else:
            self.logger.warning(f"瀏覽器 {browser_index} 等待畫面超時（未檢測到 遊戲開始 或 錯誤訊息）")
        
        self.logger.info(f"瀏覽器 {browser_index} ({username}) 圖片檢測流程完成")
        return True
    
    def _recovery_click_button(
        self,
        bt: 'BrowserThread',
        x_ratio: float,
        y_ratio: float,
        display_name: str
    ) -> bool:
        """恢復流程：點擊指定座標的按鈕。"""
        browser_index = bt.index
        username = bt.context.credential.username if bt.context else "Unknown"
        
        for click_attempt in range(Constants.MAX_RETRY_ATTEMPTS):
            try:
                if click_attempt > 0:
                    time.sleep(Constants.RETRY_INTERVAL)
                
                def click_task(context: BrowserContext) -> bool:
                    driver = context.driver
                    
                    # 取得 Canvas 區域
                    rect = BrowserHelper.get_canvas_rect(driver)
                    if not rect:
                        return False
                    
                    BrowserHelper.click_canvas_position(driver, rect, x_ratio, y_ratio)
                    return True
                
                if bt.execute_task(click_task, timeout=10):
                    self.logger.info(f"瀏覽器 {browser_index} ({username}) 已點擊 {display_name}")
                    return True
                    
            except Exception as e:
                if click_attempt < Constants.MAX_RETRY_ATTEMPTS - 1:
                    self.logger.warning(f"瀏覽器 {browser_index} 點擊超時，準備重試...")
                else:
                    self.logger.error(f"瀏覽器 {browser_index} 點擊 {display_name} 失敗: {e}")
        
        return False
    
    def _recovery_detect_and_click(
        self,
        bt: 'BrowserThread',
        template_name: str,
        x_ratio: float,
        y_ratio: float
    ) -> bool:
        """恢復流程：檢測圖片並點擊（參照登入流程）。
        
        持續檢測直到找到圖片，然後點擊指定座標。
        使用與登入流程相同的檢測邏輯，確保穩定性。
        """
        browser_index = bt.index
        username = bt.context.credential.username if bt.context else "Unknown"
        display_name = Constants.TEMPLATE_DISPLAY_NAMES.get(template_name, template_name)
        
        # 檢查模板是否存在
        if not self._image_detector.template_exists(template_name):
            self.logger.warning(f"模板 {template_name} 不存在，跳過檢測")
            return False
        
        self.logger.info(f"瀏覽器 {browser_index} 開始檢測 {display_name}...")
        
        # 持續檢測直到找到（無限循環，參照登入流程）
        attempt = 0
        detected = False
        
        while not detected:
            attempt += 1
            
            try:
                def detect_task(context: BrowserContext) -> Optional[Tuple[int, int, float]]:
                    """檢測任務：返回檢測結果而非布林值，提供更多資訊。"""
                    return self._image_detector.detect_in_browser(
                        context.driver, template_name
                    )
                
                result = bt.execute_task(detect_task, timeout=10)
                
                if result is not None:
                    self.logger.info(
                        f"瀏覽器 {browser_index} ({username}) 檢測到 {display_name}"
                    )
                    detected = True
                    break
                    
            except Exception as e:
                self.logger.debug(f"瀏覽器 {browser_index} 檢測時發生錯誤: {e}")
            
            # 每 10 次檢測顯示一次進度（參照登入流程）
            if attempt % Constants.DETECTION_PROGRESS_INTERVAL == 0:
                self.logger.info(f"瀏覽器 {browser_index} 等待 {display_name}... (已嘗試 {attempt} 次)")
            
            # 設置最大嘗試次數，避免無限循環
            if attempt >= Constants.MAX_DETECTION_ATTEMPTS:
                self.logger.warning(f"瀏覽器 {browser_index} 等待 {display_name} 超時")
                return False
            
            time.sleep(Constants.DETECTION_INTERVAL)
        
        # 檢測成功後等待一下再點擊（參照登入流程）
        time.sleep(Constants.NORMAL_WAIT)
        
        # 點擊（包含重試機制，參照登入流程）
        for click_attempt in range(Constants.MAX_RETRY_ATTEMPTS):
            try:
                if click_attempt > 0:
                    time.sleep(Constants.RETRY_INTERVAL)
                
                def click_task(context: BrowserContext) -> bool:
                    driver = context.driver
                    
                    # 取得 Canvas 區域
                    rect = BrowserHelper.get_canvas_rect(driver)
                    if not rect:
                        return False
                    
                    # 計算座標並點擊
                    click_x, click_y = BrowserHelper.click_canvas_position(
                        driver, rect, x_ratio, y_ratio
                    )
                    self.logger.debug(
                        f"瀏覽器 {context.index} 已點擊 {display_name} "
                        f"(座標: {click_x:.0f}, {click_y:.0f})"
                    )
                    return True
                
                if bt.execute_task(click_task, timeout=10):
                    self.logger.info(f"瀏覽器 {browser_index} ({username}) 已點擊 {display_name}")
                    return True
                    
            except Exception as e:
                if click_attempt < Constants.MAX_RETRY_ATTEMPTS - 1 and is_network_error(e):
                    self.logger.warning(f"瀏覽器 {browser_index} 點擊超時，準備重試...")
                    continue
                else:
                    self.logger.error(f"瀏覽器 {browser_index} 點擊 {display_name} 失敗: {e}")
        
        return False
    
    def _recovery_click_error_confirm(self, bt: 'BrowserThread') -> bool:
        """恢復流程：點擊錯誤訊息確認按鈕。"""
        try:
            def task(context: BrowserContext) -> bool:
                driver = context.driver
                
                rect = BrowserHelper.get_canvas_rect(driver)
                if not rect:
                    return False
                
                BrowserHelper.click_canvas_position(
                    driver, rect,
                    Constants.ERROR_CONFIRM_BUTTON_X_RATIO,
                    Constants.ERROR_CONFIRM_BUTTON_Y_RATIO
                )
                return True
            
            return bt.execute_task(task)
        except Exception as e:
            self.logger.debug(f"點擊錯誤確認按鈕失敗: {e}")
            return False
    
    def _start_error_monitor(self) -> None:
        """啟動錯誤監控功能。"""
        if self.error_monitor_running:
            self.logger.warning("錯誤監控已在運行中")
            return
        
        self._error_monitor_stop_event.clear()
        self._error_monitor_thread = threading.Thread(
            target=self._error_monitor_loop,
            daemon=True,
            name="ErrorMonitorThread"
        )
        self._error_monitor_thread.start()
        self.error_monitor_running = True
    
    def _stop_error_monitor(self) -> None:
        """停止錯誤監控功能。"""
        if not self.error_monitor_running:
            return
        
        self._error_monitor_stop_event.set()
        
        if self._error_monitor_thread and self._error_monitor_thread.is_alive():
            self._error_monitor_thread.join(timeout=2.0)
            
            if self._error_monitor_thread.is_alive():
                self.logger.warning("錯誤監控功能停止時發生延遲")
        
        self._error_monitor_thread = None
        self.error_monitor_running = False
    
    def show_help(self) -> None:
        """顯示指令說明。"""
        help_text = """
==========================================================
                    【遊戲控制面板 - 指令說明】
==========================================================

【自動操作】
  s <最小>,<最大>     開始自動按鍵（設定隨機間隔秒數）
                      範例: s 1,2 → 每 1~2 秒自動下注一次

  r <小時數>          執行規則檔案中的規則
                      r 0      → 無限執行所有規則
                      r 0.5    → 執行 30 分鐘後自動停止
                      r 2      → 執行 2 小時後自動停止

                      規則格式說明（用戶規則.txt）:
                      - s:金額:最小,最大:時間  定時旋轉
                      - a:金額:次數            自動旋轉
                      - f:金額 或 f:金額:類別  購買免費遊戲
                      
                      前綴說明:
                      - (無前綴) 循環執行
                      - -        執行一次
                      - #        略過（註釋）
                   
  p                   暫停所有目前運行的自動操作

【金額與遊戲】  
  b <金額>            調整下注金額
                      範例: b 2, b 4, b 10, b 100
  
  a <次數>            設定自動旋轉
                      a 10     → 自動旋轉 10 次
                      a 50     → 自動旋轉 50 次
                      a 100    → 自動旋轉 100 次
  
  f <編號>            購買免費遊戲
                      f 0      → 所有瀏覽器
                      f 1      → 第 1 個瀏覽器
                      f 1,2,3  → 第 1、2、3 個瀏覽器
                      【賽特一】自動購買免費遊戲
                      【賽特二】1=免費遊戲, 2=覺醒之力, 3=不朽覺醒

【截圖工具】
  t                   截取金額模板（進入互動模式）
  d                   截取黑屏提示模板
  e                   截取錯誤訊息模板
  l                   截取返回大廳模板

【系統指令】
  h                   顯示此幫助信息

  q <編號>             關閉指定瀏覽器
                      q 0      → 關閉所有瀏覽器並退出程式
                      q 1      → 關閉第 1 個瀏覽器

==========================================================
"""
        self.logger.info(help_text)
    
    def _auto_press_loop_single(self, bt: 'BrowserThread', browser_index: int) -> None:
        """單個瀏覽器的自動按鍵循環。
        
        參數:
            bt: BrowserThread 實例
            browser_index: 瀏覽器索引（1-based）
        """
        import random
        
        press_count = 0
        username = bt.context.credential.username if bt.context else "Unknown"
        
        while not self._stop_event.is_set():
            try:
                # 檢查瀏覽器是否仍然有效
                if not bt.is_browser_alive():
                    self.logger.warning(f"瀏覽器 {browser_index} ({username}) 已離線，自動停止")
                    break
                
                press_count += 1
                
                # 執行按空白鍵
                def press_space_task(context: BrowserContext) -> bool:
                    BrowserHelper.execute_cdp_space_key(context.driver)
                    return True
                
                bt.execute_task(press_space_task)
                
                # 每個瀏覽器使用獨立的隨機間隔
                interval = random.uniform(self.min_interval, self.max_interval)
                
                # 使用 wait 而非 sleep，這樣可以立即響應停止信號
                if self._stop_event.wait(timeout=interval):
                    break
                    
            except Exception as e:
                self.logger.error(f"瀏覽器 {browser_index} ({username}) 操作失敗: {e}")
                self._stop_event.wait(timeout=1.0)
        
        self.logger.info(f"瀏覽器 {browser_index} ({username}) 已停止，共執行 {press_count} 次")
    
    def _start_auto_press(self) -> None:
        """為每個瀏覽器啟動獨立的自動按鍵功能。"""
        if self.auto_press_running:
            self.logger.warning("自動按鍵已在運行中")
            return
        
        # 檢查是否已設定間隔時間
        if not hasattr(self, 'min_interval') or not hasattr(self, 'max_interval'):
            self.logger.warning("請先使用 's <最小>,<最大>' 命令設定間隔時間")
            return
        
        # 清除停止事件
        self._stop_event.clear()
        self.auto_press_threads.clear()
        
        # 取得活躍的瀏覽器
        active_browsers = self._get_active_browsers()
        
        # 為每個瀏覽器啟動獨立執行緒
        for i, bt in enumerate(active_browsers, 1):
            thread = threading.Thread(
                target=self._auto_press_loop_single,
                args=(bt, i),
                daemon=True,
                name=f"AutoPressThread-{i}"
            )
            self.auto_press_threads[i] = thread
            thread.start()
        
        self.auto_press_running = True
        
        self.logger.info(f"已啟動 {len(active_browsers)} 個瀏覽器的自動按鍵")
    
    def _stop_auto_press(self) -> None:
        """停止所有瀏覽器的自動按鍵功能。"""
        if not self.auto_press_running:
            self.logger.warning("自動按鍵未在運行")
            return
        
        # 設置停止事件
        self._stop_event.set()
        
        # 等待所有執行緒結束
        stopped_count = 0
        for browser_index, thread in self.auto_press_threads.items():
            if thread and thread.is_alive():
                thread.join(timeout=1.0)
                
                if not thread.is_alive():
                    stopped_count += 1
                else:
                    self.logger.warning(f"瀏覽器 {browser_index} 停止時發生延遲")
            else:
                stopped_count += 1
        
        self.logger.info(f"已停止 {stopped_count}/{len(self.auto_press_threads)} 個瀏覽器")
        
        self.auto_press_threads.clear()
        self.auto_press_running = False

    # -------------------------------------------------------------------------
    # 規則執行功能
    # -------------------------------------------------------------------------

    def _start_rule_execution(self, max_hours: Optional[float] = None) -> None:
        """啟動規則執行。
        
        執行邏輯:
        1. 先執行所有帶 '-' 前綴的規則（once_only=True）
        2. 然後循環執行所有不帶 '-' 前綴的規則（once_only=False）
        
        參數:
            max_hours: 最大執行時間（小時），None 表示無限制
        """
        if self.rule_running:
            self.logger.warning("規則執行已在運行中")
            return
        
        if self.auto_press_running:
            self.logger.warning("自動按鍵正在運行，請先使用 'p' 暫停")
            return
        
        # 檢查是否有規則
        if not self.bet_rules:
            self.logger.error("沒有可執行的規則，請檢查 用戶規則.txt")
            return
        
        # 設定時間控制
        self._rule_execution_start_time = time.time()
        self._rule_execution_max_hours = max_hours
        
        # 顯示規則列表
        self.logger.info("")
        self.logger.info(Constants.LOG_SEPARATOR)
        self.logger.info("【載入的規則】")
        self.logger.info(Constants.LOG_SEPARATOR)
        
        for i, rule in enumerate(self.bet_rules, 1):
            prefix = "[單次]" if rule.once_only else "[循環]"
            if rule.rule_type == 'a':
                self.logger.info(
                    f"  {i}. {prefix} 自動旋轉 | 金額 {rule.amount}, 次數 {rule.spin_count}"
                )
            elif rule.rule_type == 's':
                self.logger.info(
                    f"  {i}. {prefix} 定時旋轉 | 金額 {rule.amount}, "
                    f"間隔 {rule.min_seconds}~{rule.max_seconds} 秒, "
                    f"持續 {rule.duration} 分鐘"
                )
            elif rule.rule_type == 'f':
                type_name = self._get_free_game_type_name(rule.free_game_type)
                self.logger.info(
                    f"  {i}. {prefix} 免費遊戲 | 金額 {rule.amount}, 類別: {type_name}"
                )
        
        self.logger.info("")
        
        # 清除停止事件
        self._stop_event.clear()
        
        # 顯示啟動訊息
        if max_hours is not None:
            self.logger.info(f"規則執行已啟動（將在 {max_hours} 小時後自動停止，按 'p' 可暫停）")
        else:
            self.logger.info("規則執行已啟動（按 'p' 可暫停）")
        self.logger.info("")
        
        # 啟動規則執行執行緒
        self._rule_thread = threading.Thread(
            target=self._rule_execution_loop,
            daemon=True,
            name="RuleExecutionThread"
        )
        self._rule_thread.start()
        self.rule_running = True
        
        # 如果設置了時間限制，啟動時間監控線程
        if max_hours is not None:
            self._time_monitor_thread = threading.Thread(
                target=self._time_limit_monitor_loop,
                daemon=True,
                name="TimeLimitMonitorThread"
            )
            self._time_monitor_thread.start()

    def _stop_rule_execution(self) -> None:
        """停止規則執行。"""
        if not self.rule_running:
            self.logger.warning("規則執行未在運行")
            return
        
        self.logger.info("正在停止規則執行...")
        
        # 設置停止事件
        self._stop_event.set()
        
        # 停止所有自動按鍵執行緒
        if self.auto_press_threads:
            self.logger.info("停止自動按鍵執行緒...")
            stopped_count = 0
            for browser_index, thread in self.auto_press_threads.items():
                if thread and thread.is_alive():
                    thread.join(timeout=Constants.AUTO_PRESS_THREAD_JOIN_TIMEOUT)
                    if not thread.is_alive():
                        stopped_count += 1
                else:
                    stopped_count += 1
            
            self.logger.info(f"已停止 {stopped_count}/{len(self.auto_press_threads)} 個瀏覽器的自動按鍵")
            self.auto_press_threads.clear()
            self.auto_press_running = False
        
        # 等待規則執行緒結束
        if self._rule_thread and self._rule_thread.is_alive():
            self._rule_thread.join(timeout=5.0)
            
            if self._rule_thread.is_alive():
                self.logger.warning("規則執行執行緒未能正常結束")
        
        self.rule_running = False
        self._rule_thread = None
        
        # 停止時間監控線程
        if self._time_monitor_thread and self._time_monitor_thread.is_alive():
            self._time_monitor_thread.join(timeout=2.0)
        self._time_monitor_thread = None
        
        # 清理時間控制狀態
        self._rule_execution_start_time = None
        self._rule_execution_max_hours = None
        
        # 重置停止事件，確保後續手動指令可以正常執行
        self._stop_event.clear()
        
        self.logger.info("規則執行已停止")

    def _rule_execution_loop(self) -> None:
        """規則執行主循環（在獨立執行緒中運行）。
        
        執行邏輯:
        1. 先執行所有帶 '-' 前綴的規則（once_only=True）
        2. 然後循環執行所有不帶 '-' 前綴的規則（once_only=False）
        """
        if not self.bet_rules:
            self.logger.error("沒有可執行的規則")
            return
        
        self.logger.info(f"開始執行規則，共 {len(self.bet_rules)} 條")
        
        # 分離只執行一次的規則和需要循環的規則
        once_rules = [r for r in self.bet_rules if r.once_only]
        loop_rules = [r for r in self.bet_rules if not r.once_only]
        
        # === 第一階段: 執行所有帶 '-' 前綴的規則（只執行一次）===
        if once_rules:
            self.logger.info(f"[階段 1] 執行 {len(once_rules)} 條單次規則...")
            
            for rule_index, rule in enumerate(once_rules):
                if self._stop_event.is_set():
                    self.logger.info("收到停止信號")
                    break
                
                # 檢查時間限制
                if self._check_time_limit():
                    break
                
                try:
                    self._execute_single_rule(rule, rule_index + 1, len(once_rules))
                except Exception as e:
                    self.logger.error(f"執行單次規則時發生錯誤: {e}")
                    continue
                
                # 規則之間短暫暫停
                if rule_index < len(once_rules) - 1:
                    time.sleep(Constants.RULE_SWITCH_WAIT)
            
            self.logger.info("[階段 1 完成] 所有單次規則已執行")
            time.sleep(Constants.RULE_SWITCH_WAIT)
        
        # === 第二階段: 循環執行不帶 '-' 前綴的規則 ===
        if not loop_rules:
            self.logger.warning("沒有循環規則，規則執行結束")
            self.rule_running = False
            return
        
        self.logger.info(f"[階段 2] 開始循環執行 {len(loop_rules)} 條規則...")
        
        rule_index = 0
        while not self._stop_event.is_set() and self.rule_running:
            # 檢查時間限制
            if self._check_time_limit():
                break
            
            try:
                current_rule = loop_rules[rule_index]
                
                self._execute_single_rule(current_rule, rule_index + 1, len(loop_rules))
                
                # 檢查是否被停止
                if self._stop_event.is_set():
                    self.logger.info("收到停止信號")
                    break
                
                # 顯示完成訊息
                self.logger.info(f"規則 {rule_index + 1} 執行完成")
                
                # 移動到下一條規則（循環）
                rule_index = (rule_index + 1) % len(loop_rules)
                
                # 顯示下一步提示
                if rule_index == 0:
                    self.logger.info("所有規則執行完畢，回到第一條規則...")
                else:
                    self.logger.info("準備執行下一條規則...")
                
                # 規則之間短暫暫停
                time.sleep(Constants.RULE_SWITCH_WAIT)
                
            except Exception as e:
                self.logger.error(f"執行規則時發生錯誤: {e}")
                # 確保清理自動按鍵執行緒
                self.auto_press_threads.clear()
                self.auto_press_running = False
                if self._stop_event.wait(timeout=5.0):
                    break
        
        # 最終清理
        if self.auto_press_running:
            for browser_index, thread in self.auto_press_threads.items():
                if thread and thread.is_alive():
                    thread.join(timeout=Constants.AUTO_PRESS_THREAD_JOIN_TIMEOUT)
        
        self.auto_press_threads.clear()
        self.auto_press_running = False
        
        self.logger.info("")
        self.logger.info("規則執行已停止")
        self.rule_running = False
        
        # 停止時間監控線程
        if self._time_monitor_thread and self._time_monitor_thread.is_alive():
            self._time_monitor_thread.join(timeout=2.0)
        self._time_monitor_thread = None
        
        # 清理時間控制狀態
        self._rule_execution_start_time = None
        self._rule_execution_max_hours = None

    def _check_time_limit(self) -> bool:
        """檢查是否超過時間限制。
        
        回傳:
            True 表示已超過時間限制，應該停止執行
        """
        if self._rule_execution_max_hours is None:
            return False
        
        if self._rule_execution_start_time is None:
            return False
        
        elapsed_hours = (time.time() - self._rule_execution_start_time) / 3600
        
        if elapsed_hours >= self._rule_execution_max_hours:
            self.logger.info(f"已達到執行時間上限 ({self._rule_execution_max_hours} 小時)，停止執行")
            # 設置停止事件，讓所有正在執行的操作（如金額調整、自動按鍵）立即停止
            self._stop_event.set()
            return True
        
        return False

    def _time_limit_monitor_loop(self) -> None:
        """時間限制監控循環（在獨立執行緒中運行）。
        
        定期檢查時間限制，確保即使在長時間等待中（如金額調整）
        也能在時間到達時立即停止。
        """
        while self.rule_running and not self._stop_event.is_set():
            # 檢查時間限制（會自動設置 _stop_event）
            if self._check_time_limit():
                break
            # 每秒檢查一次
            time.sleep(1.0)

    def _get_free_game_type_name(self, free_game_type: Optional[int]) -> str:
        """取得免費遊戲類別名稱。"""
        if free_game_type is None:
            return "預設"
        elif free_game_type == 1:
            return "免費遊戲"
        elif free_game_type == 2:
            return "覺醒之力"
        elif free_game_type == 3:
            return "不朽覺醒"
        else:
            return f"未知({free_game_type})"

    def _execute_single_rule(self, rule: BetRule, rule_num: int, total_rules: int) -> None:
        """執行單條規則。
        
        根據規則類型分派到對應的執行方法。
        
        參數:
            rule: 規則物件
            rule_num: 規則編號（顯示用）
            total_rules: 總規則數（顯示用）
        """
        if rule.rule_type == 'a':
            self._execute_auto_spin_rule(rule, rule_num, total_rules)
        elif rule.rule_type == 's':
            self._execute_standard_rule(rule, rule_num, total_rules)
        elif rule.rule_type == 'f':
            self._execute_free_game_rule(rule, rule_num, total_rules)

    def _execute_auto_spin_rule(self, rule: BetRule, rule_num: int, total_rules: int) -> None:
        """執行自動旋轉規則 ('a' 類型)。
        
        參數:
            rule: 自動旋轉規則
            rule_num: 規則編號（顯示用）
            total_rules: 總規則數（顯示用）
        """
        prefix = "[單次]" if rule.once_only else "[循環]"
        
        self.logger.info("")
        self.logger.info(Constants.LOG_SEPARATOR)
        self.logger.info(
            f"【自動旋轉規則 {rule_num}/{total_rules}】{prefix} "
            f"金額 {rule.amount}, 次數 {rule.spin_count}"
        )
        self.logger.info(Constants.LOG_SEPARATOR)
        self.logger.info("")
        
        # 檢查停止信號或時間限制
        if self._stop_event.is_set() or self._check_time_limit():
            self.logger.info("[中斷] 收到停止信號，跳過當前規則")
            return
        
        # 步驟 1: 調整金額
        self.logger.info(f"[步驟 1/2] 調整金額到 {rule.amount}...")
        if not self._adjust_all_browsers_betsize(rule.amount):
            return
        
        # 檢查停止信號或時間限制
        if self._stop_event.is_set() or self._check_time_limit():
            self.logger.info("[中斷] 收到停止信號")
            return
        
        # 步驟 2: 設定自動旋轉（使用內建的 'a' 命令邏輯）
        self.logger.info(f"[步驟 2/2] 設定自動旋轉 {rule.spin_count} 次...")
        self._execute_auto_spin_for_all(rule.spin_count)

    def _execute_standard_rule(self, rule: BetRule, rule_num: int, total_rules: int) -> None:
        """執行標準規則 ('s' 類型，定時旋轉）。
        
        參數:
            rule: 標準規則
            rule_num: 規則編號（顯示用）
            total_rules: 總規則數（顯示用）
        """
        prefix = "[單次]" if rule.once_only else "[循環]"
        
        # === 步驟 1: 確保自動按鍵已完全停止 ===
        if self.auto_press_running:
            self.logger.info("停止自動按鍵...")
            self._stop_event.set()
            
            for browser_index, thread in list(self.auto_press_threads.items()):
                if thread and thread.is_alive():
                    thread.join(timeout=Constants.AUTO_PRESS_THREAD_JOIN_TIMEOUT)
            
            self.auto_press_threads.clear()
            self.auto_press_running = False
            time.sleep(Constants.RULE_SWITCH_WAIT)
            self.logger.info("自動按鍵已停止")
            self._stop_event.clear()
        
        # 顯示規則資訊
        self.logger.info("")
        self.logger.info(Constants.LOG_SEPARATOR)
        self.logger.info(
            f"【定時旋轉規則 {rule_num}/{total_rules}】{prefix} "
            f"金額 {rule.amount}, 持續 {rule.duration} 分鐘, "
            f"間隔 {rule.min_seconds}~{rule.max_seconds} 秒"
        )
        self.logger.info(Constants.LOG_SEPARATOR)
        self.logger.info("")
        
        # 檢查停止信號或時間限制
        if self._stop_event.is_set() or self._check_time_limit():
            self.logger.info("[中斷] 收到停止信號，跳過當前規則")
            return
        
        # === 步驟 2: 調整所有瀏覽器的下注金額 ===
        self.logger.info(f"[步驟 1/2] 調整金額到 {rule.amount}...")
        if not self._adjust_all_browsers_betsize(rule.amount):
            return
        
        # 檢查停止信號或時間限制
        if self._stop_event.is_set() or self._check_time_limit():
            self.logger.info("[中斷] 收到停止信號")
            return
        
        # === 步驟 3: 啟動自動按鍵 ===
        self.logger.info(
            f"[步驟 2/2] 啟動自動按鍵 (持續 {rule.duration} 分鐘, "
            f"間隔 {rule.min_seconds}~{rule.max_seconds} 秒)"
        )
        
        # 設置每個瀏覽器的隨機間隔
        self.min_interval = rule.min_seconds
        self.max_interval = rule.max_seconds
        
        # 清除停止事件（確保自動按鍵可以運行）
        self._stop_event.clear()
        
        # 取得活躍的瀏覽器
        active_browsers = self._get_active_browsers()
        
        # 為每個瀏覽器啟動自動按鍵執行緒
        for i, bt in enumerate(active_browsers, 1):
            thread = threading.Thread(
                target=self._auto_press_loop_single,
                args=(bt, i),
                daemon=True,
                name=f"RuleAutoPress-{i}"
            )
            self.auto_press_threads[i] = thread
            thread.start()
        
        self.auto_press_running = True
        
        # === 步驟 4: 等待指定時間 ===
        wait_seconds = rule.duration * 60
        elapsed_time = 0
        check_interval = 1.0
        
        while elapsed_time < wait_seconds and not self._stop_event.is_set():
            if self._stop_event.wait(timeout=check_interval):
                break
            elapsed_time += check_interval
            
            # 檢查時間限制（會自動設置 _stop_event）
            if self._check_time_limit():
                break
            
            # 每 60 秒顯示一次剩餘時間
            if int(elapsed_time) % Constants.RULE_PROGRESS_INTERVAL == 0 and elapsed_time > 0:
                remaining_minutes = int((wait_seconds - elapsed_time) / 60)
                if remaining_minutes > 0:
                    self.logger.info(f"剩餘 {remaining_minutes} 分鐘...")

    def _execute_free_game_rule(self, rule: BetRule, rule_num: int, total_rules: int) -> None:
        """執行購買免費遊戲規則 ('f' 類型)。
        
        參數:
            rule: 免費遊戲規則
            rule_num: 規則編號（顯示用）
            total_rules: 總規則數（顯示用）
        """
        prefix = "[單次]" if rule.once_only else "[循環]"
        
        # === 步驟 1: 確保自動按鍵已完全停止 ===
        if self.auto_press_running:
            self.logger.info("停止自動按鍵...")
            self._stop_event.set()
            
            for browser_index, thread in list(self.auto_press_threads.items()):
                if thread and thread.is_alive():
                    thread.join(timeout=Constants.AUTO_PRESS_THREAD_JOIN_TIMEOUT)
            
            self.auto_press_threads.clear()
            self.auto_press_running = False
            time.sleep(Constants.RULE_SWITCH_WAIT)
            self.logger.info("自動按鍵已停止")
            self._stop_event.clear()
        
        # 顯示規則資訊
        type_name = self._get_free_game_type_name(rule.free_game_type)
        
        self.logger.info("")
        self.logger.info(Constants.LOG_SEPARATOR)
        self.logger.info(
            f"【免費遊戲規則 {rule_num}/{total_rules}】{prefix} "
            f"金額 {rule.amount} | 類別: {type_name}"
        )
        self.logger.info(Constants.LOG_SEPARATOR)
        self.logger.info("")
        
        # 檢查停止信號或時間限制
        if self._stop_event.is_set() or self._check_time_limit():
            self.logger.info("[中斷] 收到停止信號，跳過當前規則")
            return
        
        # === 步驟 2: 調整所有瀏覽器的下注金額 ===
        self.logger.info(f"[步驟 1/2] 調整金額到 {rule.amount}...")
        if not self._adjust_all_browsers_betsize(rule.amount):
            return
        
        # 檢查停止信號或時間限制
        if self._stop_event.is_set() or self._check_time_limit():
            self.logger.info("[中斷] 收到停止信號")
            return
        
        # === 步驟 3: 購買免費遊戲 ===
        self.logger.info("[步驟 2/2] 開始購買免費遊戲...")
        self._execute_buy_free_game_for_all(rule.free_game_type)
        
        self.logger.info("免費遊戲進行中，自動跳過功能會處理結算畫面")

    def _adjust_all_browsers_betsize(self, target_amount: float) -> bool:
        """調整所有瀏覽器的下注金額。
        
        參數:
            target_amount: 目標金額
            
        回傳:
            是否全部成功
        """
        # 提前驗證金額是否有效
        if target_amount not in Constants.GAME_BETSIZE:
            self.logger.error(f"目標金額 {target_amount} 不在可用金額列表中")
            return False
        
        active_browsers = [bt for bt in self._get_active_browsers() 
                          if bt.is_browser_alive() and bt.context]
        if not active_browsers:
            self.logger.error("沒有可用的瀏覽器")
            return False
        
        # 使用 ThreadPoolExecutor 同步並行調整所有瀏覽器
        results = {}
        with ThreadPoolExecutor(max_workers=len(active_browsers)) as executor:
            futures = {
                executor.submit(
                    self._image_detector.adjust_betsize,
                    bt.context.driver,
                    target_amount,
                    self._stop_event  # 傳入停止事件
                ): bt for bt in active_browsers
            }
            
            for future in futures:
                bt = futures[future]
                try:
                    results[bt.index] = future.result()
                except Exception as e:
                    self.logger.error(f"瀏覽器 {bt.index} 調整金額失敗: {e}")
                    results[bt.index] = False
        
        # 統計結果
        success_count = sum(1 for v in results.values() if v)
        total = len(active_browsers)
        
        if success_count == total:
            self.logger.info(f"金額調整完成: 全部 {success_count} 個瀏覽器成功")
            return True
        else:
            self.logger.error(f"金額調整失敗: 僅 {success_count}/{total} 個瀏覽器成功，必須全部成功才能繼續")
            return False

    def _execute_auto_spin_for_all(self, spin_count: int) -> None:
        """對所有瀏覽器執行自動旋轉設定。
        
        參數:
            spin_count: 旋轉次數（必須在 AUTO_SPIN_VALID_COUNTS 中）
        """
        # 根據次數選擇對應的座標比例
        count_ratio_map = {
            10: (Constants.AUTO_SPIN_10_X_RATIO, Constants.AUTO_SPIN_10_Y_RATIO),
            50: (Constants.AUTO_SPIN_50_X_RATIO, Constants.AUTO_SPIN_50_Y_RATIO),
            100: (Constants.AUTO_SPIN_100_X_RATIO, Constants.AUTO_SPIN_100_Y_RATIO)
        }
        count_x_ratio, count_y_ratio = count_ratio_map.get(spin_count, (0.5, 0.5))
        
        def auto_spin_task(context: BrowserContext) -> bool:
            """在單個瀏覽器中執行自動旋轉設定。"""
            driver = context.driver
            
            rect = BrowserHelper.get_canvas_rect(driver)
            if not rect:
                return False
            
            # 第一次點擊：自動旋轉按鈕
            BrowserHelper.click_canvas_position(
                driver, rect,
                Constants.AUTO_SPIN_BUTTON_X_RATIO,
                Constants.AUTO_SPIN_BUTTON_Y_RATIO
            )
            
            time.sleep(Constants.AUTO_SPIN_MENU_WAIT)
            
            # 第二次點擊：選擇次數
            BrowserHelper.click_canvas_position(
                driver, rect,
                count_x_ratio,
                count_y_ratio
            )
            
            return True
        
        # 使用統一的並行執行方法
        self._execute_on_active_browsers(auto_spin_task, "自動旋轉設定")

    def _create_buy_free_game_task(
        self, 
        free_game_type: Optional[int]
    ) -> Callable[[BrowserContext], bool]:
        """建立購買免費遊戲的任務函數（DRY 抽取）。
        
        此方法將重複的購買免費遊戲邏輯抽取為可重用的任務函數，
        供 _execute_buy_free_game_for_all 和 _handle_free_game_command 使用。
        
        參數:
            free_game_type: 免費遊戲類別
            
        回傳:
            任務函數
        """
        is_sette_1 = Constants.IS_SETTE_1
        
        def buy_free_game_task(context: BrowserContext) -> bool:
            """在單個瀏覽器中購買免費遊戲。"""
            driver = context.driver
            
            rect = BrowserHelper.get_canvas_rect(driver)
            if not rect:
                return False
            
            # 第一次點擊：免費遊戲區域按鈕
            BrowserHelper.click_canvas_position(
                driver, rect,
                Constants.BUY_FREE_GAME_BUTTON_X_RATIO,
                Constants.BUY_FREE_GAME_BUTTON_Y_RATIO
            )
            time.sleep(Constants.FREE_GAME_CLICK_WAIT)
            
            # 第二次點擊：確認按鈕（根據遊戲類型選擇座標）
            confirm_x_ratio, confirm_y_ratio = self._get_free_game_confirm_coords(
                is_sette_1, free_game_type
            )
            
            BrowserHelper.click_canvas_position(
                driver, rect,
                confirm_x_ratio,
                confirm_y_ratio
            )
            
            # 購買完成後等待並按空白鍵開始
            time.sleep(Constants.BUY_FREE_GAME_WAIT_SECONDS)
            BrowserHelper.execute_cdp_space_key(driver)
            
            return True
        
        return buy_free_game_task

    def _get_free_game_confirm_coords(
        self, 
        is_sette_1: bool, 
        free_game_type: Optional[int]
    ) -> Tuple[float, float]:
        """取得免費遊戲確認按鈕座標（DRY 抽取）。
        
        參數:
            is_sette_1: 是否為賽特一
            free_game_type: 免費遊戲類別
            
        回傳:
            (x_ratio, y_ratio) 座標比例
        """
        if is_sette_1:
            return (Constants.BUY_FREE_GAME_CONFIRM_X_RATIO, 
                    Constants.BUY_FREE_GAME_CONFIRM_Y_RATIO)
        
        # 賽特二：根據類別選擇座標
        if free_game_type == 3:
            return (Constants.BUY_FREE_GAME_IMMORTAL_AWAKE_X_RATIO,
                    Constants.BUY_FREE_GAME_IMMORTAL_AWAKE_Y_RATIO)
        elif free_game_type == 2:
            return (Constants.BUY_FREE_GAME_AWAKE_POWER_X_RATIO,
                    Constants.BUY_FREE_GAME_AWAKE_POWER_Y_RATIO)
        else:
            return (Constants.BUY_FREE_GAME_ONLY_FREEGAME_X_RATIO,
                    Constants.BUY_FREE_GAME_ONLY_FREEGAME_Y_RATIO)

    def _execute_buy_free_game_for_all(self, free_game_type: Optional[int]) -> None:
        """對所有瀏覽器執行購買免費遊戲。
        
        參數:
            free_game_type: 免費遊戲類別（1=免費遊戲, 2=覺醒之力, 3=不朽覺醒, None=賽特一預設）
        """
        # 建立任務函數
        buy_free_game_task = self._create_buy_free_game_task(free_game_type)
        
        # 使用統一的並行執行方法
        self._execute_on_active_browsers(buy_free_game_task, "免費遊戲購買")
    
    def process_command(self, command: str) -> bool:
        """處理用戶指令。
        
        參數:
            command: 用戶輸入的指令
            
        回傳:
            是否繼續運行（False 表示退出）
        """
        command = command.strip().lower()
        
        if not command:
            return True
        
        # 解析指令和參數
        parts = command.split(maxsplit=1)
        cmd = parts[0] if parts else ""
        command_arguments = parts[1] if len(parts) > 1 else ""
        
        try:
            if cmd == 'q':
                # 關閉瀏覽器指令
                return self._handle_quit_command(command_arguments)
            
            elif cmd == 'h':
                self.show_help()
            
            elif cmd == 's':
                # 開始自動按鍵
                return self._handle_start_command(command_arguments)
            
            elif cmd == 'p':
                # 暫停指令 - 可暫停自動按鍵或規則執行
                if self.rule_running:
                    self._stop_rule_execution()
                    self.logger.info("")
                    self.logger.info("已暫停規則執行")
                    self.logger.info("")
                    self.show_help()
                elif self.auto_press_running:
                    self._stop_auto_press()
                    self.logger.info("")
                    self.logger.info("已暫停自動按鍵")
                    self.logger.info("")
                    self.show_help()
                else:
                    self.logger.warning("目前沒有運行中的自動操作")
                    self.logger.info("       提示: 使用 's 1,2' 啟動自動按鍵，或使用 'r 0' 啟動規則執行")
            
            elif cmd == 'r':
                # 執行規則
                self._handle_rule_command(command_arguments)
            
            elif cmd == 'b':
                # 調整金額
                self._handle_betsize_command(command_arguments)
            
            elif cmd == 'a':
                # 自動旋轉
                self._handle_auto_spin_command(command_arguments)
            
            elif cmd == 'f':
                # 購買免費遊戲
                self._handle_free_game_command(command_arguments)
            
            elif cmd == 't':
                # 截取金額模板 (template)
                self._handle_capture_betsize_command()
            
            elif cmd == 'd':
                # 截取黑屏模板 (dark)
                self._handle_capture_blackscreen_command()
            
            elif cmd == 'e':
                # 截取錯誤提醒模板 (error)
                self._handle_capture_error_remind_command()
            
            elif cmd == 'l':
                # 截取大廳返回提示模板 (lobby)
                self._handle_capture_lobby_return_command()
            
            else:
                self.logger.warning(f"未知指令: {cmd}")
                self.logger.info("   輸入 'h' 查看指令說明")
                
        except Exception as e:
            self.logger.error(f"處理指令時發生錯誤: {e}")
        
        return True

    def _handle_rule_command(self, arguments: str) -> None:
        """處理規則執行指令。
        
        參數:
            arguments: 指令參數（執行時間，0 表示無限執行）
        """
        if self.rule_running:
            self.logger.warning("規則執行已在運行中，請先使用 'p' 暫停")
            return
        
        if self.auto_press_running:
            self.logger.warning("自動按鍵正在運行，請先使用 'p' 暫停")
            return
        
        # 檢查是否提供參數
        if not arguments:
            self.logger.warning("指令格式錯誤，請使用: r <小時數>")
            self.logger.info("       r 0      → 無限執行所有規則")
            self.logger.info("       r 0.5    → 執行 30 分鐘後自動停止")
            self.logger.info("       r 2      → 執行 2 小時後自動停止")
            return
        
        # 解析小時參數
        try:
            hours = float(arguments)
            if hours < 0:
                self.logger.warning(f"執行時間不能小於 0: {hours}")
                return
            
            # hours == 0 代表無限執行
            max_hours = None if hours == 0 else hours
            
            if max_hours is None:
                self.logger.info("設定規則執行模式: 無限執行")
            else:
                self.logger.info(f"設定規則執行時間: {max_hours} 小時")
                
        except ValueError:
            self.logger.warning(f"無效的小時數: {arguments}，請輸入數字")
            return
        
        self._start_rule_execution(max_hours=max_hours)
    
    def _handle_quit_command(self, arguments: str) -> bool:
        """處理關閉瀏覽器指令。
        
        關閉前會先導航到登入頁面並等待 10 秒，確保伺服器端正確處理登出。
        
        參數:
            arguments: 指令參數
            
        回傳:
            是否繼續運行
        """
        if not arguments:
            self.logger.warning("指令格式錯誤，請使用: q <編號>")
            self.logger.info("       q 0 - 關閉所有瀏覽器並退出")
            self.logger.info("       q 1 - 關閉第 1 個瀏覽器")
            self.logger.info("       q 1,2,3 - 關閉第 1、2、3 個瀏覽器")
            return True
        
        try:
            active_browsers = self._get_active_browsers()
            target_browsers: List['BrowserThread'] = []
            
            # 解析參數
            if ',' in arguments:
                # 多個編號：q 1,2,3
                indices = [int(x.strip()) for x in arguments.split(',')]
                for idx in indices:
                    for bt in active_browsers:
                        if bt.index == idx:
                            target_browsers.append(bt)
                            break
            else:
                # 單一編號
                index = int(arguments)
                if index == 0:
                    # 0 表示所有瀏覽器
                    target_browsers = active_browsers.copy()
                else:
                    for bt in active_browsers:
                        if bt.index == index:
                            target_browsers.append(bt)
                            break
                    if not target_browsers:
                        self.logger.warning(f"瀏覽器 {index} 不存在或已關閉")
                        return True
            
            if not target_browsers:
                self.logger.warning("沒有有效的瀏覽器可關閉")
                return True
            
            # 顯示執行資訊
            if len(target_browsers) == len(active_browsers):
                self.logger.info(f"開始關閉所有 {len(target_browsers)} 個瀏覽器...")
            else:
                browser_list = ", ".join([str(bt.index) for bt in target_browsers])
                self.logger.info(f"開始關閉瀏覽器 ({browser_list})...")
            
            # 在關閉前，先導航到登入頁面並等待 10 秒
            self.logger.info("正在導航到登入頁面...")
            for bt in target_browsers:
                try:
                    if not bt.is_browser_alive() or not bt.context:
                        continue
                    
                    def navigate_to_login_task(context: BrowserContext) -> bool:
                        """導航到登入頁面。"""
                        driver = context.driver
                        driver.switch_to.default_content()
                        driver.get(Constants.LOGIN_PAGE)
                        return True
                    
                    bt.execute_task(navigate_to_login_task, timeout=30)
                except Exception as e:
                    username = bt.context.credential.username if bt.context else "Unknown"
                    self.logger.warning(f"瀏覽器 {bt.index} ({username}) 導航失敗: {e}")
            
            self.logger.info(f"等待 {int(Constants.QUIT_WAIT_TIME)} 秒後關閉...")
            time.sleep(Constants.QUIT_WAIT_TIME)
            
            # 關閉瀏覽器
            closed_count = 0
            for bt in target_browsers:
                try:
                    username = bt.context.credential.username if bt.context else "Unknown"
                    bt.stop()
                    self.logger.info(f"已關閉瀏覽器 {bt.index} ({username})")
                    closed_count += 1
                except Exception as e:
                    self.logger.error(f"關閉瀏覽器 {bt.index} 失敗: {e}")
            
            # 統計結果
            if closed_count == len(target_browsers):
                self.logger.info(f"關閉完成: 全部 {closed_count} 個瀏覽器已關閉")
            else:
                self.logger.warning(f"部分完成: {closed_count}/{len(target_browsers)} 個瀏覽器已關閉")
            
            # 檢查是否還有瀏覽器在運行
            remaining = len(self._get_active_browsers())
            if remaining == 0:
                self.logger.info("所有瀏覽器已關閉，退出控制面板")
                return False
            else:
                self.logger.info(f"剩餘 {remaining} 個瀏覽器仍在運行")
        
        except ValueError:
            self.logger.warning(f"無效的編號: {arguments}，請輸入數字")
        
        return True
    
    def _handle_auto_spin_command(self, arguments: str) -> None:
        """處理自動旋轉指令。
        
        設定所有瀏覽器的自動旋轉功能，使用統一的執行方法遵循 DRY 原則。
        
        參數:
            arguments: 指令參數（旋轉次數）
        """
        if not arguments:
            valid_counts = ", ".join(str(c) for c in Constants.AUTO_SPIN_VALID_COUNTS)
            self.logger.warning("指令格式錯誤")
            self.logger.info("       正確格式: a <次數>")
            self.logger.info(f"       可選次數: {valid_counts}")
            return
        
        # 解析次數參數
        try:
            spin_count = int(arguments.strip())
        except ValueError:
            valid_counts = ", ".join(str(c) for c in Constants.AUTO_SPIN_VALID_COUNTS)
            self.logger.warning("次數格式錯誤，請輸入有效的數字")
            self.logger.info(f"       可選次數: {valid_counts}")
            return
        
        # 驗證次數是否有效
        if spin_count not in Constants.AUTO_SPIN_VALID_COUNTS:
            valid_counts = ", ".join(str(c) for c in Constants.AUTO_SPIN_VALID_COUNTS)
            self.logger.warning("無效的次數")
            self.logger.info(f"       您輸入的: {spin_count}")
            self.logger.info(f"       可選次數: {valid_counts}")
            return
        
        self.logger.info("")
        self.logger.info(f"設定自動旋轉 {spin_count} 次...")
        
        # 使用統一的執行方法（DRY 原則）
        self._execute_auto_spin_for_all(spin_count)
        
        self.logger.info("")
    
    def _handle_free_game_command(self, arguments: str) -> None:
        """處理購買免費遊戲指令。
        
        根據 GAME_PATTERN 自動判斷遊戲種類：
        - 賽特一：直接購買免費遊戲
        - 賽特二：需要選擇類別（1=免費遊戲, 2=覺醒之力, 3=不朽覺醒）
        
        參數:
            arguments: 指令參數（瀏覽器編號）
        """
        if not arguments:
            self.logger.warning("指令格式錯誤")
            self.logger.info("       正確格式: f <編號>")
            self.logger.info("       f 0      → 所有瀏覽器")
            self.logger.info("       f 1      → 第 1 個瀏覽器")
            self.logger.info("       f 1,2,3  → 第 1、2、3 個瀏覽器")
            return
        
        # 取得所有活躍的瀏覽器
        all_browsers = [bt for bt in self._get_active_browsers() 
                       if bt.is_browser_alive() and bt.context]
        if not all_browsers:
            self.logger.error("沒有可用的瀏覽器")
            return
        
        # 解析目標瀏覽器編號
        target_browsers: List[BrowserThread] = []
        
        try:
            if ',' in arguments:
                # 多個編號：f 1,2,3
                indices = [int(x.strip()) for x in arguments.split(',')]
                for idx in indices:
                    found = False
                    for bt in all_browsers:
                        if bt.index == idx:
                            target_browsers.append(bt)
                            found = True
                            break
                    if not found:
                        self.logger.warning(f"瀏覽器 {idx} 不存在或已關閉，跳過")
            else:
                # 單一編號
                idx = int(arguments.strip())
                if idx == 0:
                    # 0 表示所有瀏覽器
                    target_browsers = all_browsers.copy()
                else:
                    for bt in all_browsers:
                        if bt.index == idx:
                            target_browsers.append(bt)
                            break
                    if not target_browsers:
                        self.logger.warning(f"瀏覽器 {idx} 不存在或已關閉")
                        return
        except ValueError:
            self.logger.warning("編號格式錯誤，請輸入數字")
            self.logger.info("       範例: f 0 或 f 1 或 f 1,2,3")
            return
        
        if not target_browsers:
            self.logger.warning("沒有有效的瀏覽器可執行操作")
            return
        
        # 判斷遊戲種類
        is_sette_1 = Constants.IS_SETTE_1
        
        # 賽特二需要選擇免費遊戲類別
        free_game_type: Optional[int] = None
        if not is_sette_1:
            self.logger.info("")
            self.logger.info("請選擇免費遊戲類別:")
            self.logger.info("       1 - 免費遊戲")
            self.logger.info("       2 - 覺醒之力")
            self.logger.info("       3 - 不朽覺醒")
            self.logger.info("       q - 取消")
            self.logger.info("")
            
            try:
                print("請輸入類別 > ", end="", flush=True)
                sys.stdout.flush()
                type_input = input().strip().lower()
                
                if type_input == 'q':
                    self.logger.info("已取消操作")
                    return
                elif type_input in ('1', '2', '3'):
                    free_game_type = int(type_input)
                else:
                    valid_types = ", ".join(str(t) for t in Constants.FREE_GAME_VALID_TYPES)
                    self.logger.warning(f"無效的類別: {type_input}")
                    self.logger.info(f"       請輸入 {valid_types}")
                    return
                    
            except (EOFError, KeyboardInterrupt):
                self.logger.info("")
                self.logger.info("已取消操作")
                return
        
        # 顯示執行資訊
        self.logger.info("")
        if len(target_browsers) == len(all_browsers):
            self.logger.info(f"開始購買免費遊戲 (全部 {len(target_browsers)} 個瀏覽器)")
        else:
            browser_list = ", ".join([str(bt.index) for bt in target_browsers])
            self.logger.info(f"開始購買免費遊戲 (瀏覽器 {browser_list})")
        
        if is_sette_1:
            self.logger.info("       遊戲種類: 賽特一")
        else:
            type_name = self._get_free_game_type_name(free_game_type)
            self.logger.info(f"       遊戲種類: 賽特二")
            self.logger.info(f"       購買類別: {type_name}")
        
        # 使用統一的任務函數（DRY 原則）
        buy_free_game_task = self._create_buy_free_game_task(free_game_type)
        
        # 使用 ThreadPoolExecutor 並行執行
        results = {}
        with ThreadPoolExecutor(max_workers=len(target_browsers)) as executor:
            futures = {
                executor.submit(bt.execute_task, buy_free_game_task): bt 
                for bt in target_browsers
            }
            
            for future in futures:
                bt = futures[future]
                try:
                    results[bt.index] = future.result()
                except Exception as e:
                    username = bt.context.credential.username if bt.context else "Unknown"
                    self.logger.error(f"瀏覽器 {bt.index} ({username}) 購買失敗: {e}")
                    results[bt.index] = False
        
        # 統計結果
        success_count = sum(1 for v in results.values() if v)
        total = len(target_browsers)
        successful_browsers = [bt for bt in target_browsers if results.get(bt.index, False)]
        
        self.logger.info("")
        if success_count == total:
            self.logger.info("免費遊戲購買完成")
            self.logger.info(f"       成功數量: {success_count} 個")
        else:
            self.logger.warning("免費遊戲部分購買完成")
            self.logger.info(f"       成功數量: {success_count}/{total} 個")
            for bt in target_browsers:
                if not results.get(bt.index, False):
                    username = bt.context.credential.username if bt.context else "Unknown"
                    self.logger.error(f"       失敗: 瀏覽器 {bt.index} ({username})")
        
        # 等待用戶確認免費遊戲結束
        if success_count > 0:
            self.logger.info("")
            self.logger.info("免費遊戲已啟動，請手動遊玩")
            self.logger.info("結束後請按 Enter 繼續（系統將自動結算）")
            
            try:
                print("按 Enter 繼續 > ", end="", flush=True)
                sys.stdout.flush()
                input()
                
                # 對成功購買的瀏覽器執行結算
                self.logger.info("正在等待結算...")
                
                def settle_free_game_task(context: BrowserContext) -> bool:
                    """執行免費遊戲結算。"""
                    driver = context.driver
                    
                    # 按空白鍵
                    BrowserHelper.execute_cdp_space_key(driver)
                    
                    # 取得 Canvas 區域
                    rect = BrowserHelper.get_canvas_rect(driver)
                    if not rect:
                        return False
                    
                    # 等待後連續點擊跳過結算畫面
                    time.sleep(Constants.FREE_GAME_SETTLE_INITIAL_WAIT)
                    for i in range(Constants.FREE_GAME_SETTLE_CLICK_COUNT):
                        BrowserHelper.click_canvas_position(
                            driver, rect,
                            Constants.GAME_LOGIN_BUTTON_X_RATIO,
                            Constants.GAME_LOGIN_BUTTON_Y_RATIO
                        )
                        if i < Constants.FREE_GAME_SETTLE_CLICK_COUNT - 1:
                            time.sleep(Constants.FREE_GAME_SETTLE_CLICK_INTERVAL)
                    
                    return True
                
                # 對成功購買的瀏覽器執行結算
                settle_results = {}
                with ThreadPoolExecutor(max_workers=len(successful_browsers)) as executor:
                    futures = {
                        executor.submit(bt.execute_task, settle_free_game_task): bt 
                        for bt in successful_browsers
                    }
                    
                    for future in futures:
                        bt = futures[future]
                        try:
                            settle_results[bt.index] = future.result()
                        except Exception:
                            settle_results[bt.index] = False
                
                settle_success = sum(1 for v in settle_results.values() if v)
                self.logger.info(f"結算完成: {settle_success} 個瀏覽器")
                
            except (EOFError, KeyboardInterrupt):
                self.logger.info("")
                self.logger.info("已取消結算操作")
        
        self.logger.info("")

    def _handle_betsize_command(self, arguments: str) -> None:
        """處理調整金額指令。
        
        使用 _adjust_all_browsers_betsize 方法，遵循 DRY 原則。
        
        參數:
            arguments: 指令參數（目標金額）
        """
        if not arguments:
            self.logger.warning("指令格式錯誤，請使用: b <金額>")
            self.logger.info("       範例: b 2, b 10, b 100")
            return
        
        try:
            target_amount = float(arguments)
        except ValueError:
            self.logger.warning(f"無效的金額: {arguments}，請輸入數字")
            return
        
        # 提前驗證金額是否有效
        if target_amount not in Constants.GAME_BETSIZE:
            self.logger.warning(f"目標金額 {target_amount} 不在可用金額列表中")
            return
        
        self.logger.info(f"開始調整金額到 {target_amount}...")
        
        # 使用統一的調整方法（DRY 原則）
        self._adjust_all_browsers_betsize(target_amount)

    def _handle_start_command(self, arguments: str) -> bool:
        """處理開始自動按鍵指令。
        
        參數:
            arguments: 指令參數
            
        回傳:
            是否繼續運行
        """
        if not arguments:
            self.logger.warning("指令格式錯誤")
            self.logger.info("       正確格式: s <最小>,<最大>")
            self.logger.info("       範例: s 1,2 → 每 1~2 秒自動執行一次")
            return True
        
        # 解析用戶輸入的間隔時間
        try:
            interval_parts = arguments.split(',')
            if len(interval_parts) != 2:
                self.logger.warning("間隔格式錯誤，需要兩個數字")
                self.logger.info("       範例: s 1,2 或 s 1.5,3")
                return True
            
            min_interval = float(interval_parts[0].strip())
            max_interval = float(interval_parts[1].strip())
            
            if min_interval <= 0 or max_interval <= 0:
                self.logger.warning("間隔時間必須大於 0")
                return True
            
            if min_interval > max_interval:
                self.logger.warning("最小間隔不能大於最大間隔")
                self.logger.info(f"       您輸入的: 最小={min_interval}, 最大={max_interval}")
                return True
                
        except ValueError:
            self.logger.warning("間隔格式錯誤，請輸入有效的數字")
            self.logger.info("       範例: s 1,2 或 s 1.5,3")
            return True
        
        # 檢查是否已在運行
        if self.auto_press_running:
            self.logger.warning("自動按鍵已在運行中")
            self.logger.info(f"       目前設定: {self.min_interval}~{self.max_interval} 秒")
            self.logger.info("       請先使用 'p' 暫停後再重新設定")
            return True
        
        # 設置間隔時間
        self.min_interval = min_interval
        self.max_interval = max_interval
        
        active_count = len(self._get_active_browsers())
        
        self.logger.info("")
        self.logger.info("自動按鍵已啟動")
        self.logger.info(f"       間隔時間: {min_interval}~{max_interval} 秒")
        self.logger.info(f"       瀏覽器數: {active_count} 個")
        self.logger.info("       暫停指令: p")
        self.logger.info("")
        
        # 啟動自動按鍵
        self._start_auto_press()
        
        return True
    
    def _select_browser_for_capture(self, display_name: str) -> Optional['BrowserThread']:
        """統一的瀏覽器選擇邏輯（參照 _prompt_capture_template 風格）。
        
        參數:
            display_name: 顯示名稱（用於提示訊息）
            
        回傳:
            選中的 BrowserThread，取消則返回 None
        """
        self.logger.info("")
        self.logger.info(Constants.LOG_SEPARATOR)
        self.logger.info(f"【截取模板】{display_name}")
        self.logger.info(Constants.LOG_SEPARATOR)
        self.logger.info("")
        self.logger.info(f"需要擷取 {display_name} 的參考圖片")
        self.logger.info("       請確保目標遊戲視窗已顯示正確的畫面內容")
        self.logger.info("")
        
        # 取得可用的瀏覽器
        active_browsers = self._get_active_browsers()
        
        if not active_browsers:
            self.logger.error("沒有可用的遊戲視窗")
            return None
        
        # 顯示可選擇的瀏覽器列表
        self.logger.info("請選擇要擷取的遊戲視窗:")
        for bt in active_browsers:
            if bt.context:
                username = bt.context.credential.username
                self.logger.info(f"  {bt.index}  - 視窗 {bt.index} ({username})")
        
        self.logger.info("  q  - 取消")
        self.logger.info("")
        
        try:
            print("請輸入編號: ", end="", flush=True)
            sys.stdout.flush()
            user_input = input().strip().lower()
            
            # 檢查是否要取消
            if user_input == 'q':
                self.logger.info("使用者取消擷取")
                return None
            
            # 解析瀏覽器編號
            try:
                browser_index = int(user_input)
                
                # 尋找對應的瀏覽器
                for bt in active_browsers:
                    if bt.index == browser_index:
                        if bt.is_browser_alive() and bt.context:
                            return bt
                        else:
                            self.logger.warning(f"瀏覽器 {browser_index} 已關閉")
                            return None
                
                self.logger.warning(f"無效的瀏覽器編號: {browser_index}")
                return None
                
            except ValueError:
                self.logger.warning(f"無效的輸入: {user_input}")
                return None
                
        except (EOFError, KeyboardInterrupt):
            self.logger.info("")
            self.logger.info("使用者取消擷取")
            return None
    
    def _handle_capture_betsize_command(self) -> None:
        """處理截取金額模板指令。"""
        # 1. 先選擇瀏覽器
        selected_browser = self._select_browser_for_capture("金額模板")
        
        if selected_browser is None:
            return
        
        # 2. 進入金額輸入模式
        self.logger.info("")
        self.logger.info("請輸入目前遊戲顯示的金額（例: 2, 10, 100）")
        self.logger.info("   輸入 q 退出")
        self.logger.info("")
        
        while True:
            try:
                print("金額: ", end="", flush=True)
                amount_input = input().strip().lower()
                
                # 輸入 q 則退出
                if amount_input == 'q':
                    self.logger.info("退出金額模板工具")
                    break
                
                # 空白輸入則提示
                if not amount_input:
                    self.logger.warning("請輸入金額或輸入 q 退出")
                    continue
                
                amount = float(amount_input)
                
                # 使用 Constants.GAME_BETSIZE 驗證金額
                if amount not in Constants.GAME_BETSIZE:
                    self.logger.warning(f"金額 {amount} 不在標準列表中，但仍會建立模板")
                
                # 檢查瀏覽器是否仍然有效
                if not selected_browser.is_browser_alive():
                    self.logger.error("選中的瀏覽器已關閉")
                    break
                
                # 擷取模板（使用 self._image_detector）
                if self._image_detector.capture_betsize_template(selected_browser.context.driver, amount):
                    self.logger.info("")
                else:
                    self.logger.error("模板截取失敗")
                    
            except ValueError:
                self.logger.warning("金額格式錯誤，請輸入有效數字（例如: 2, 10, 100）")
            except (EOFError, KeyboardInterrupt):
                self.logger.info("")
                self.logger.info("退出金額模板工具")
                break
            except Exception as e:
                self.logger.error(f"截取失敗: {e}")
    
    def _handle_capture_template_command(
        self, 
        template_constant: str,
        capture_method_name: str
    ) -> None:
        """通用的模板截取命令處理。
        
        參數:
            template_constant: 模板常數名稱（如 Constants.BLACK_SCREEN）
            capture_method_name: ImageDetector 中的截取方法名稱
        """
        # 取得顯示名稱
        display_name = Constants.TEMPLATE_DISPLAY_NAMES.get(template_constant, template_constant)
        
        # 選擇瀏覽器
        selected_browser = self._select_browser_for_capture(display_name)
        if selected_browser is None:
            return
        
        # 擷取模板
        try:
            capture_method = getattr(self._image_detector, capture_method_name)
            if capture_method(selected_browser.context.driver):
                self.logger.info("")
            else:
                self.logger.error("模板截取失敗")
        except Exception as e:
            self.logger.error(f"截取失敗: {e}")
    
    def _handle_capture_blackscreen_command(self) -> None:
        """處理截取黑屏模板指令。"""
        self._handle_capture_template_command(
            Constants.BLACK_SCREEN,
            "capture_blackscreen_template"
        )
    
    def _handle_capture_error_remind_command(self) -> None:
        """處理截取錯誤提醒模板指令。"""
        self._handle_capture_template_command(
            Constants.ERROR_REMIND,
            "capture_error_remind_template"
        )
    
    def _handle_capture_lobby_return_command(self) -> None:
        """處理截取大廳返回提示模板指令。"""
        self._handle_capture_template_command(
            Constants.LOBBY_RETURN,
            "capture_lobby_return_template"
        )
    
    def start(self) -> None:
        """啟動控制面板。"""
        self.running = True
        self.logger.info("")
        self.logger.info(Constants.LOG_SEPARATOR)
        self.logger.info("           【遊戲控制面板】已啟動")
        self.logger.info(Constants.LOG_SEPARATOR)
        self.logger.info("")
        
        active_count = len(self._get_active_browsers())
        self.logger.info(f"已連接 {active_count} 個遊戲視窗")
        self.logger.info("")
        
        # 啟動錯誤訊息監控
        self._start_error_monitor()
        
        # 自動顯示幫助訊息
        self.show_help()
        
        # 啟動自動執行計時器
        delay_minutes = int(Constants.AUTO_START_DELAY / 60)
        self.logger.info("")
        self.logger.info(f"⏰ 將在 {delay_minutes} 分鐘後自動執行 '{Constants.AUTO_START_COMMAND}' 命令")
        self.logger.info("   如需取消，請輸入任意命令")
        self.logger.info("")
        
        def auto_execute_command() -> None:
            """自動執行預設命令。"""
            if not self._user_has_input and self.running:
                self.logger.info("")
                self.logger.info(f"⏰ {delay_minutes} 分鐘已到，自動執行 '{Constants.AUTO_START_COMMAND}' 命令...")
                self.logger.info("")
                self.process_command(Constants.AUTO_START_COMMAND)
        
        self._auto_start_timer = threading.Timer(Constants.AUTO_START_DELAY, auto_execute_command)
        self._auto_start_timer.daemon = True
        self._auto_start_timer.start()
        
        try:
            while self.running:
                try:
                    print(">>> ", end="", flush=True)
                    FlushingStreamHandler.show_prompt = True
                    command = input().strip()
                    FlushingStreamHandler.show_prompt = False
                    
                    # 記錄用戶已經輸入過命令，取消自動執行
                    if not self._user_has_input:
                        self._user_has_input = True
                        if self._auto_start_timer and self._auto_start_timer.is_alive():
                            self._auto_start_timer.cancel()
                            self.logger.info(f"[提示] 已取消自動執行 '{Constants.AUTO_START_COMMAND}' 命令")
                    
                    if command:
                        if not self.process_command(command):
                            break
                    else:
                        self.logger.warning("請輸入指令（輸入 'h' 查看幫助）")
                        
                except EOFError:
                    FlushingStreamHandler.show_prompt = False
                    self.logger.info("\n輸入結束，退出控制面板")
                    break
                except KeyboardInterrupt:
                    FlushingStreamHandler.show_prompt = False
                    self.logger.info("\n使用者中斷，退出控制面板")
                    break
        finally:
            FlushingStreamHandler.show_prompt = False
            
            # 取消自動執行計時器
            if self._auto_start_timer and self._auto_start_timer.is_alive():
                self._auto_start_timer.cancel()
            
            # 確保停止所有自動操作
            if self.auto_press_running:
                self._stop_auto_press()
            
            # 停止錯誤訊息監控
            self._stop_error_monitor()
            
            self.running = False
            self.logger.info("控制面板已關閉")
    
    def stop(self) -> None:
        """停止控制面板。"""
        self.running = False
        
        # 確保停止自動按鍵
        if self.auto_press_running:
            self._stop_auto_press()
        
        # 停止錯誤訊息監控
        self._stop_error_monitor()


# =============================================================================
# 應用程式啟動器
# =============================================================================

class AutoSlotGameAppStarter:
    """應用程式啟動器。

    統一管理應用程式的初始化與啟動流程，包含:
        - 載入配置檔案
        - 啟動代理中繼伺服器
        - 建立瀏覽器實例（每個瀏覽器使用專屬執行緒）
        - 執行登入與導航流程
        - 圖片檢測與點擊
        - 啟動控制面板

    屬性:
        browser_threads: 瀏覽器執行緒列表。
        credentials: 使用者憑證列表。
        rules: 下注規則列表。
        proxy_manager: 代理伺服器管理器。
        browser_manager: 瀏覽器管理器。

    範例:
        >>> starter = AutoSlotGameAppStarter()
        >>> if starter.initialize():
        ...     starter.navigate_to_login_page()
        ...     starter.perform_login()
        ...     starter.start_control_center()
        >>> starter.cleanup()
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or LoggerFactory.get_logger()
        self.config_reader: Optional[ConfigReader] = None
        self.proxy_manager: Optional[LocalProxyServerManager] = None
        self.browser_manager: Optional[BrowserManager] = None
        
        # 瀏覽器執行緒列表（取代原本的 browser_contexts）
        self.browser_threads: List[BrowserThread] = []
        
        self.credentials: List[UserCredential] = []
        self.rules: List[BetRule] = []
    
    def initialize(self) -> bool:
        """執行完整的初始化流程。
        
        流程:
        1. 載入配置檔案
        2. 啟動瀏覽器
        3. 啟動代理中繼伺服器
        4. 建立瀏覽器實例
        
        回傳:
            初始化是否成功
        """
        try:
            # 步驟 1: 載入配置檔案
            self._step_load_config()
            
            # 步驟 2: 啟動瀏覽器
            browser_count = self._step_determine_browser_count()
            
            if browser_count == 0:
                self.logger.error("沒有可用的用戶帳號，無法繼續")
                return False
            
            # 步驟 3: 啟動代理中繼伺服器
            proxy_ports = self._step_start_proxy_servers(browser_count)
            
            # 步驟 4: 建立瀏覽器實例
            self._step_create_browsers(browser_count, proxy_ports)
            
            return True
            
        except Exception as e:
            self.logger.error(f"初始化失敗: {e}")
            return False
    
    def _step_load_config(self) -> None:
        """步驟 1: 載入配置檔案。
        
        從 lib/用戶資料.txt 讀取用戶帳號密碼，
        從 lib/用戶規則.txt 讀取下注規則。
        
        異常:
            ConfigurationError: 配置檔案格式錯誤時拋出。
        """
        self.logger.info(Constants.LOG_SEPARATOR)
        self.logger.info("【步驟 1】載入配置檔案")
        self.logger.info(Constants.LOG_SEPARATOR)
        
        self.config_reader = ConfigReader(logger=self.logger)
        
        # 讀取用戶資料
        self.credentials = self.config_reader.read_user_credentials()
        self.logger.info(f"讀取到 {len(self.credentials)} 個用戶帳號")
        
        # 讀取用戶規則
        self.rules = self.config_reader.read_bet_rules()
        self.logger.info(f"讀取到 {len(self.rules)} 條規則")
        
        self.logger.info("")
    
    def _step_determine_browser_count(self) -> int:
        """步驟 2: 啟動瀏覽器
        
        回傳:
            瀏覽器數量
        """
        self.logger.info(Constants.LOG_SEPARATOR)
        self.logger.info("【步驟 2】啟動瀏覽器")
        self.logger.info(Constants.LOG_SEPARATOR)
        
        # 根據用戶數量決定瀏覽器數量，最多 MAX_BROWSER_COUNT 個
        browser_count = min(len(self.credentials), Constants.MAX_BROWSER_COUNT)
        
        self.logger.info(f"將開啟 {browser_count} 個瀏覽器")
        self.logger.info("")
        
        return browser_count
    
    def _step_start_proxy_servers(self, browser_count: int) -> List[Optional[int]]:
        """步驟 3: 啟動代理中繼伺服器
        
        參數:
            browser_count: 瀏覽器數量
            
        回傳:
            每個瀏覽器對應的本機代理埠號列表
        """
        self.logger.info(Constants.LOG_SEPARATOR)
        self.logger.info("【步驟 3】啟動代理中繼伺服器")
        self.logger.info(Constants.LOG_SEPARATOR)
        
        self.proxy_manager = LocalProxyServerManager(logger=self.logger)
        proxy_ports: List[Optional[int]] = []
        success_count = 0
        no_proxy_count = 0
        
        for i in range(browser_count):
            credential = self.credentials[i]
            
            if credential.proxy:
                # 有代理配置，啟動中繼伺服器
                try:
                    proxy_info = ProxyInfo.from_connection_string(credential.proxy)
                    port = self.proxy_manager.start_proxy_server(proxy_info)
                    proxy_ports.append(port)
                    if port:
                        success_count += 1
                except Exception as e:
                    self.logger.warning(f"瀏覽器 {i+1}: 無法解析代理配置 - {e}")
                    proxy_ports.append(None)
            else:
                # 沒有代理配置
                proxy_ports.append(None)
                no_proxy_count += 1
        
        # 統一輸出結果
        if success_count > 0:
            self.logger.info(f"已啟動 {success_count} 個代理中繼伺服器")
        if no_proxy_count > 0:
            self.logger.info(f"{no_proxy_count} 個瀏覽器無代理配置，使用直連網路")
        
        self.logger.info("")
        return proxy_ports
    
    def _step_create_browsers(
        self, 
        browser_count: int, 
        proxy_ports: List[Optional[int]]
    ) -> None:
        """步驟 4: 建立瀏覽器實例（使用專屬執行緒）
        
        每個瀏覽器都會啟動自己的專屬執行緒，從建立到關閉的所有操作
        都在同一個執行緒中執行。
        
        參數:
            browser_count: 瀏覽器數量
            proxy_ports: 代理埠號列表
        """
        self.logger.info(Constants.LOG_SEPARATOR)
        self.logger.info("【步驟 4】建立瀏覽器實例")
        self.logger.info(Constants.LOG_SEPARATOR)
        
        self.browser_manager = BrowserManager(logger=self.logger)
        self.logger.info(f"正在開啟 {browser_count} 個遊戲視窗...")
        
        # 1. 建立並啟動所有瀏覽器執行緒
        for i in range(browser_count):
            credential = self.credentials[i]
            proxy_port = proxy_ports[i]
            
            thread = BrowserThread(
                index=i + 1,
                credential=credential,
                browser_manager=self.browser_manager,
                proxy_port=proxy_port,
                logger=self.logger
            )
            thread.start()
            self.browser_threads.append(thread)
        
        # 2. 等待所有瀏覽器就緒
        success_count = 0
        failed_indices = []
        
        for thread in self.browser_threads:
            if thread.wait_until_ready(timeout=Constants.DEFAULT_TIMEOUT_SECONDS):
                success_count += 1
            else:
                error = thread.get_creation_error()
                failed_indices.append((thread.index, str(error) if error else "未知錯誤"))
        
        # 3. 移除失敗的執行緒
        if failed_indices:
            self.browser_threads = [
                t for t in self.browser_threads if t.context is not None
            ]
        
        # 輸出結果
        if success_count == browser_count:
            self.logger.info(f"全部 {browser_count} 個瀏覽器已建立")
        else:
            self.logger.info(f"成功建立 {success_count}/{browser_count} 個瀏覽器")
            for idx, err in failed_indices:
                self.logger.error(f"瀏覽器 {idx}: {err}")
        
        self.logger.info("")
    
    def cleanup(self) -> None:
        """清理所有資源。
        
        執行以下清理步驟：
        1. 停止所有瀏覽器執行緒（會自動關閉瀏覽器）
        2. 等待所有執行緒結束（最多 5 秒）
        3. 清空執行緒列表
        4. 停止所有代理伺服器
        
        此方法應在程式結束時呼叫，確保資源正確釋放。
        """
        self.logger.info(Constants.LOG_SEPARATOR)
        self.logger.info("【清理資源】")
        self.logger.info(Constants.LOG_SEPARATOR)
        
        browser_count = len(self.browser_threads)
        
        # 停止所有瀏覽器執行緒（會自動關閉瀏覽器）
        for thread in self.browser_threads:
            thread.stop()
        
        # 等待所有執行緒結束
        for thread in self.browser_threads:
            thread.join(timeout=5.0)
        
        self.browser_threads.clear()
        
        if browser_count > 0:
            self.logger.info(f"已關閉 {browser_count} 個瀏覽器")
        
        # 停止所有代理伺服器
        if self.proxy_manager:
            self.proxy_manager.stop_all_servers()
            self.logger.info("已停止所有代理伺服器")
        
        self.logger.info("")
    
    def get_browser_threads(self) -> List[BrowserThread]:
        """取得所有瀏覽器執行緒。
        
        回傳:
            瀏覽器執行緒列表，每個執行緒包含一個獨立的瀏覽器實例。
        
        範例:
            >>> threads = starter.get_browser_threads()
            >>> for thread in threads:
            ...     print(f"瀏覽器 {thread.index}: {thread.is_browser_alive()}")
        """
        return self.browser_threads
    
    def get_browser_contexts(self) -> List[BrowserContext]:
        """取得所有瀏覽器上下文。
        
        此方法提供向後相容性，從執行緒中提取 BrowserContext 物件。
        僅返回已成功建立的瀏覽器上下文（排除 None）。
        
        回傳:
            瀏覽器上下文列表。
        
        範例:
            >>> contexts = starter.get_browser_contexts()
            >>> for ctx in contexts:
            ...     print(f"用戶: {ctx.credential.username}")
        """
        return [t.context for t in self.browser_threads if t.context is not None]
    
    def execute_on_all_browsers(
        self, 
        func: Callable[[BrowserContext], Any],
        timeout: Optional[float] = None
    ) -> List[Tuple[int, Any, Optional[Exception]]]:
        """在所有瀏覽器上並行執行任務。
        
        每個任務都會在對應瀏覽器的專屬執行緒中執行，所有任務同時啟動。
        已關閉的瀏覽器會自動跳過並返回錯誤結果。
        
        參數:
            func: 要執行的函數，接收 BrowserContext 作為參數。
            timeout: 每個任務的超時時間（秒），None 表示無限等待。
            
        回傳:
            結果列表，每個元素為 (index, result, error) 元組：
            - index: 瀏覽器編號
            - result: 任務執行結果，失敗時為 None
            - error: 例外物件，成功時為 None
        
        範例:
            >>> def print_url(ctx: BrowserContext) -> str:
            ...     return ctx.driver.current_url
            >>> results = starter.execute_on_all_browsers(print_url, timeout=10.0)
            >>> for idx, url, err in results:
            ...     if err is None:
            ...         print(f"瀏覽器 {idx}: {url}")
        """
        results: List[Tuple[int, Any, Optional[Exception]]] = []
        pending_threads: List[BrowserThread] = []
        
        # 1. 先將任務分發給所有執行緒
        for thread in self.browser_threads:
            if not thread.is_browser_alive():
                results.append((thread.index, None, RuntimeError("瀏覽器已關閉")))
                continue
            
            # 重置任務完成事件
            thread._task_done_event.clear()
            thread._task_result = None
            
            # 加入任務佇列
            with thread._task_lock:
                thread._task_queue.append((func, (), {}))
            
            # 通知執行緒有新任務
            thread._task_event.set()
            pending_threads.append(thread)
        
        # 2. 等待所有任務完成
        for thread in pending_threads:
            try:
                if thread._task_done_event.wait(timeout=timeout):
                    result = thread._task_result
                    if isinstance(result, Exception):
                        results.append((thread.index, None, result))
                    else:
                        results.append((thread.index, result, None))
                else:
                    results.append((thread.index, None, TimeoutError(f"瀏覽器 {thread.index} 任務執行超時")))
            except Exception as e:
                results.append((thread.index, None, e))
        
        # 3. 按索引排序
        results.sort(key=lambda x: x[0])
        
        return results
    
    def get_credentials(self) -> List[UserCredential]:
        """取得所有用戶憑證。
        
        回傳:
            用戶憑證列表，從配置檔案讀取。
        """
        return self.credentials
    
    def get_rules(self) -> List[BetRule]:
        """取得所有下注規則。
        
        回傳:
            下注規則列表，從配置檔案讀取。
        """
        return self.rules
    
    # ========================================================================
    # 導航與登入相關方法
    # ========================================================================
    
    def navigate_to_login_page(self) -> None:
        """步驟 5: 導航到登入頁面
        
        包含網路容錯機制：
        - 頁面載入失敗時自動重試
        - 驗證頁面是否正確載入
        """
        self.logger.info(Constants.LOG_SEPARATOR)
        self.logger.info("【步驟 5】導航到登入頁面")
        self.logger.info(Constants.LOG_SEPARATOR)
        
        def navigate_task(context: BrowserContext) -> bool:
            driver = context.driver
            
            # 最多重試 MAX_RETRY_ATTEMPTS 次
            for attempt in range(Constants.MAX_RETRY_ATTEMPTS):
                try:
                    if attempt > 0:
                        self.logger.info(f"瀏覽器 {context.index} 導航第 {attempt + 1} 次嘗試...")
                        time.sleep(Constants.RETRY_INTERVAL)
                    
                    # 導航到登入頁面
                    driver.get(Constants.LOGIN_PAGE)
                    
                    # 等待頁面載入（檢查是否有關鍵元素）
                    WebDriverWait(driver, Constants.ELEMENT_WAIT_TIMEOUT_LONG).until(
                        lambda d: d.execute_script("return document.readyState") == "complete"
                    )
                    
                    # 額外等待讓頁面元素完全渲染
                    time.sleep(Constants.PAGE_LOAD_WAIT)
                    
                    return True
                    
                except Exception as e:
                    if attempt < Constants.MAX_RETRY_ATTEMPTS - 1 and is_network_error(e):
                        self.logger.warning(f"瀏覽器 {context.index} 頁面載入超時，準備重試...")
                        continue
                    else:
                        self.logger.warning(f"瀏覽器 {context.index} 導航失敗: {e}")
                        return False
            
            return False
        
        results = self.execute_on_all_browsers(navigate_task, timeout=Constants.ELEMENT_WAIT_TIMEOUT_LONG * 2)
        success_count = sum(1 for _, result, error in results if error is None and result)
        
        self.logger.info(f"{success_count}/{len(self.browser_threads)} 個瀏覽器已導航到登入頁面")
        self.logger.info("")
    
    def perform_login(self) -> None:
        """步驟 6: 執行登入操作
        
        包含網路容錯機制：
        - 延長元素等待超時時間
        - Loading 遮罩等待時間增加
        - 關鍵步驟失敗時自動重試
        """
        self.logger.info(Constants.LOG_SEPARATOR)
        self.logger.info("【步驟 6】執行登入操作")
        self.logger.info(Constants.LOG_SEPARATOR)
        
        def login_task(context: BrowserContext) -> bool:
            driver = context.driver
            credential = context.credential
            
            # 最多重試 MAX_RETRY_ATTEMPTS 次
            for attempt in range(Constants.MAX_RETRY_ATTEMPTS):
                try:
                    if attempt > 0:
                        self.logger.info(f"瀏覽器 {context.index} 登入第 {attempt + 1} 次嘗試...")
                        time.sleep(Constants.RETRY_INTERVAL)
                    
                    # 1. 等待 loading 遮罩層消失（使用 JavaScript 檢測，避免多次 WebDriver 調用）
                    WebDriverWait(driver, Constants.ELEMENT_WAIT_TIMEOUT).until(
                        lambda d: d.execute_script("""
                            const loading = document.querySelector('.loading-container');
                            return !loading || loading.style.display === 'none' || 
                                   getComputedStyle(loading).display === 'none' ||
                                   getComputedStyle(loading).visibility === 'hidden';
                        """)
                    )

                    # 2. 點擊初始登入按鈕
                    initial_login_btn = WebDriverWait(driver, Constants.ELEMENT_WAIT_TIMEOUT).until(
                        EC.element_to_be_clickable((By.XPATH, Constants.INITIAL_LOGIN_BUTTON))
                    )
                    driver.execute_script("arguments[0].click();", initial_login_btn)
                    time.sleep(Constants.PAGE_LOAD_WAIT)  # 等待彈窗動畫
                    
                    # 3. 等待登入表單顯示（使用較長超時）
                    WebDriverWait(driver, Constants.ELEMENT_WAIT_TIMEOUT).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, ".popup-wrap, .popup-account-container"))
                    )
                    
                    # 4. 輸入帳號（使用較長超時）
                    username_input = WebDriverWait(driver, Constants.ELEMENT_WAIT_TIMEOUT).until(
                        EC.element_to_be_clickable((By.XPATH, Constants.USERNAME_INPUT))
                    )
                    username_input.clear()
                    time.sleep(Constants.SHORT_WAIT)
                    username_input.send_keys(credential.username)
                    
                    # 5. 輸入密碼
                    password_input = WebDriverWait(driver, Constants.ELEMENT_WAIT_TIMEOUT).until(
                        EC.element_to_be_clickable((By.XPATH, Constants.PASSWORD_INPUT))
                    )
                    password_input.clear()
                    time.sleep(Constants.NORMAL_WAIT)
                    password_input.send_keys(credential.password)
                    
                    # 6. 點擊登入按鈕
                    login_button = WebDriverWait(driver, Constants.ELEMENT_WAIT_TIMEOUT).until(
                        EC.element_to_be_clickable((By.XPATH, Constants.LOGIN_BUTTON))
                    )
                    driver.execute_script("arguments[0].click();", login_button)
                    time.sleep(Constants.PAGE_LOAD_WAIT)  # 等待登入完成
                    
                    # 7. 關閉所有彈窗
                    BrowserHelper.close_popups(driver)
                    
                    return True
                    
                except Exception as e:
                    if attempt < Constants.MAX_RETRY_ATTEMPTS - 1 and is_network_error(e):
                        self.logger.warning(f"瀏覽器 {context.index} 登入超時，準備重試...")
                        continue
                    else:
                        self.logger.warning(f"瀏覽器 {context.index} 登入失敗: {e}")
                        return False
            
            return False
        
        results = self.execute_on_all_browsers(login_task, timeout=Constants.LOGIN_TASK_TIMEOUT)
        success_count = sum(1 for _, result, error in results if error is None and result)
        
        self.logger.info(f"{success_count}/{len(self.browser_threads)} 個瀏覽器已完成登入")
        self.logger.info("")
    
    def navigate_to_game(self) -> None:
        """步驟 7: 導航到遊戲頁面
        
        包含網路容錯機制：
        - 使用 WebDriverWait 取代 find_element
        - 延長搜尋結果載入時間
        - 關鍵步驟失敗時自動重試
        """
        self.logger.info(Constants.LOG_SEPARATOR)
        self.logger.info("【步驟 7】導航到遊戲頁面")
        self.logger.info(Constants.LOG_SEPARATOR)
        
        def game_task(context: BrowserContext) -> bool:
            driver = context.driver
            
            # 最多重試 MAX_RETRY_ATTEMPTS 次
            for attempt in range(Constants.MAX_RETRY_ATTEMPTS):
                try:
                    if attempt > 0:
                        self.logger.info(f"瀏覽器 {context.index} 進入遊戲第 {attempt + 1} 次嘗試...")
                        # 重試前刷新頁面
                        driver.refresh()
                        time.sleep(Constants.PAGE_LOAD_WAIT_LONG)
                    
                    # 1. 關閉可能出現的公告彈窗
                    try:
                        BrowserHelper.close_popups(driver)
                        time.sleep(Constants.NORMAL_WAIT)
                    except Exception:
                        pass  # 沒有彈窗也沒關係
                    
                    # 2. 用背景圖片找遊戲卡片並點擊
                    game_pattern = Constants.get_game_pattern()
                    game_selector = f"//div[contains(@class, 'game-img') and contains(@style, '{game_pattern}')]"
                    game_element = WebDriverWait(driver, Constants.ELEMENT_WAIT_TIMEOUT).until(
                        EC.presence_of_element_located((By.XPATH, game_selector))
                    )
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", game_element)
                    time.sleep(Constants.NORMAL_WAIT)
                    driver.execute_script("arguments[0].click();", game_element)
                    time.sleep(Constants.PAGE_LOAD_WAIT_LONG)  # 等待遊戲載入
                    
                    # 3. 切換到 iframe（使用較長超時等待 iframe 載入）
                    time.sleep(Constants.PAGE_LOAD_WAIT)  # 額外等待 iframe 載入
                    iframe = WebDriverWait(driver, Constants.ELEMENT_WAIT_TIMEOUT_LONG).until(
                        EC.presence_of_element_located((By.XPATH, Constants.GAME_IFRAME))
                    )
                    driver.switch_to.frame(iframe)
                    
                    # 4. 驗證是否成功進入遊戲（檢查 Canvas 是否存在）
                    WebDriverWait(driver, Constants.ELEMENT_WAIT_TIMEOUT).until(
                        lambda d: d.execute_script(f"return document.getElementById('{Constants.GAME_CANVAS}') !== null;")
                    )
                    
                    return True
                    
                except Exception as e:
                    if attempt < Constants.MAX_RETRY_ATTEMPTS - 1 and is_network_error(e):
                        self.logger.warning(f"瀏覽器 {context.index} 進入遊戲超時，準備重試...")
                        continue
                    else:
                        self.logger.warning(f"瀏覽器 {context.index} 進入遊戲失敗: {e}")
                        return False
            
            return False
        
        results = self.execute_on_all_browsers(game_task, timeout=Constants.GAME_NAVIGATION_TIMEOUT)
        success_count = sum(1 for _, result, error in results if error is None and result)
        
        self.logger.info(f"{success_count}/{len(self.browser_threads)} 個瀏覽器已進入遊戲")
        self.logger.info("")
    
    def arrange_windows(self) -> None:
        """步驟 8: 調整視窗排列"""
        self.logger.info(Constants.LOG_SEPARATOR)
        self.logger.info("【步驟 8】調整視窗排列")
        self.logger.info(Constants.LOG_SEPARATOR)
        
        width = Constants.DEFAULT_WINDOW_WIDTH
        height = Constants.DEFAULT_WINDOW_HEIGHT
        columns = Constants.DEFAULT_WINDOW_COLUMNS
        
        def arrange_task(context: BrowserContext) -> bool:
            index = context.index
            row = (index - 1) // columns
            col = (index - 1) % columns
            
            x = col * width
            y = row * height
            
            context.driver.set_window_size(width, height)
            context.driver.set_window_position(x, y)
            return True
        
        results = self.execute_on_all_browsers(arrange_task)
        success_count = sum(1 for _, result, error in results if error is None and result)
        
        self.logger.info(f"{success_count}/{len(self.browser_threads)} 個視窗已排列完成 ({columns} 列, {width}x{height})")
        self.logger.info("")
    
    def execute_image_detection_flow(self) -> None:
        """步驟 9: 執行圖片檢測流程
        
        包含 game_login 和 game_confirm 的檢測與處理。
        流程:
        1. 檢測 game_login → 點擊
        2. 檢測 game_confirm → 點擊
        """
        self.logger.info(Constants.LOG_SEPARATOR)
        self.logger.info("【步驟 9】執行圖片檢測流程")
        self.logger.info(Constants.LOG_SEPARATOR)
        
        if not self.browser_threads:
            self.logger.error("沒有可用的瀏覽器實例")
            return
        
        # 初始化圖片檢測器
        image_detector = ImageDetector(logger=self.logger)
        
        # 階段 1: 處理 遊戲登入
        self.logger.info("")
        self.logger.info("【階段 1】檢測 遊戲登入 畫面")
        self._handle_image_detection_and_click(
            image_detector=image_detector,
            template_name=Constants.GAME_LOGIN,
            x_ratio=Constants.GAME_LOGIN_BUTTON_X_RATIO,
            y_ratio=Constants.GAME_LOGIN_BUTTON_Y_RATIO
        )
        
        # 階段 2: 處理 遊戲開始
        self.logger.info("")
        self.logger.info("【階段 2】檢測 遊戲開始 畫面")
        self._handle_image_detection_and_click(
            image_detector=image_detector,
            template_name=Constants.GAME_CONFIRM,
            x_ratio=Constants.GAME_CONFIRM_BUTTON_X_RATIO,
            y_ratio=Constants.GAME_CONFIRM_BUTTON_Y_RATIO,
            post_click_wait=3.0,
            post_click_message="所有瀏覽器已準備就緒"
        )
        
        self.logger.info("")
        self.logger.info("圖片檢測與初始化完成")
        self.logger.info("")
    
    def _handle_image_detection_and_click(
        self,
        image_detector: ImageDetector,
        template_name: str,
        x_ratio: float,
        y_ratio: float,
        post_click_wait: float = 0.0,
        post_click_message: Optional[str] = None
    ) -> None:
        """通用的圖片檢測與點擊處理流程。
        
        此方法整合了以下步驟：
        1. 檢查模板是否存在，若不存在則引導用戶擷取
        2. 持續檢測直到所有瀏覽器都找到圖片
        3. 使用 Canvas 比例計算座標並點擊
        4. 等待圖片消失
        
        參數:
            image_detector: 圖片檢測器實例
            template_name: 模板圖片檔名
            x_ratio: 點擊座標 X 比例
            y_ratio: 點擊座標 Y 比例
            post_click_wait: 點擊後額外等待時間（秒）
            post_click_message: 點擊後顯示的訊息（可選）
        """
        display_name = Constants.TEMPLATE_DISPLAY_NAMES.get(template_name, template_name)
        
        # 1. 檢查模板是否存在，若不存在則引導用戶擷取
        if not image_detector.template_exists(template_name):
            self._prompt_capture_template(image_detector, template_name, display_name)
        
        # 2. 持續檢測直到所有瀏覽器都找到圖片
        self._continuous_detect_until_found(image_detector, template_name, display_name)
        
        # 3. 等待一下後點擊
        time.sleep(Constants.NORMAL_WAIT)
        
        # 4. 使用 Canvas 比例計算座標並點擊（包含重試機制）
        def click_canvas_button(context: BrowserContext) -> bool:
            # 最多重試 MAX_RETRY_ATTEMPTS 次
            for attempt in range(Constants.MAX_RETRY_ATTEMPTS):
                try:
                    if attempt > 0:
                        time.sleep(Constants.RETRY_INTERVAL)
                    
                    driver = context.driver
                    
                    # 取得 Canvas 區域
                    rect = BrowserHelper.get_canvas_rect(driver)
                    if not rect:
                        if attempt < Constants.MAX_RETRY_ATTEMPTS - 1:
                            continue
                        return False
                    
                    # 計算座標並點擊
                    click_x, click_y = BrowserHelper.click_canvas_position(
                        driver, rect, x_ratio, y_ratio
                    )
                    self.logger.debug(
                        f"瀏覽器 {context.index} 已點擊 {display_name} "
                        f"(座標: {click_x:.0f}, {click_y:.0f})"
                    )
                    return True
                    
                except Exception as e:
                    if attempt < Constants.MAX_RETRY_ATTEMPTS - 1 and is_network_error(e):
                        continue
                    else:
                        self.logger.error(f"瀏覽器 {context.index} 點擊 {display_name} 失敗: {e}")
                        return False
            
            return False
        
        results = self.execute_on_all_browsers(click_canvas_button)
        success_count = sum(1 for _, result, error in results if error is None and result)
        self.logger.info(f"{success_count}/{len(self.browser_threads)} 個瀏覽器已點擊 {display_name}")
        
        # 5. 等待圖片消失
        self._wait_for_image_disappear(image_detector, template_name)
        
        # 6. 可選的額外等待和訊息
        if post_click_wait > 0:
            time.sleep(post_click_wait)
        if post_click_message:
            self.logger.info(post_click_message)
    
    def _continuous_detect_until_found(
        self, 
        image_detector: ImageDetector, 
        template_name: str, 
        display_name: str
    ) -> List[Optional[Tuple[int, int, float]]]:
        """持續檢測直到在所有瀏覽器中找到圖片。
        
        參數:
            image_detector: 圖片檢測器實例
            template_name: 模板圖片檔名
            display_name: 顯示名稱
            
        回傳:
            檢測結果列表
        """
        attempt = 0
        total_browsers = len(self.browser_threads)
        
        self.logger.info(f"開始檢測 {display_name}...")
        
        while True:
            attempt += 1
            
            # 在所有瀏覽器中檢測
            detection_results: List[Optional[Tuple[int, int, float]]] = []
            
            def detect_task(context: BrowserContext) -> Optional[Tuple[int, int, float]]:
                return image_detector.detect_in_browser(context.driver, template_name)
            
            results = self.execute_on_all_browsers(detect_task)
            detection_results = [result for _, result, error in results if error is None]
            
            found_count = sum(1 for result in detection_results if result is not None)
            
            # 當所有瀏覽器都找到圖片時返回
            if found_count == total_browsers:
                self.logger.info(f"所有瀏覽器都已檢測到 {display_name}")
                return detection_results
            
            # 每 10 次檢測顯示一次進度
            if attempt % Constants.DETECTION_PROGRESS_INTERVAL == 0:
                self.logger.info(f"   檢測進度: {found_count}/{total_browsers} 個瀏覽器已就緒")
                sys.stdout.flush()  # 確保緩衝區刷新
            
            time.sleep(Constants.DETECTION_INTERVAL)
    
    def _prompt_capture_template(
        self, 
        image_detector: ImageDetector, 
        template_name: str, 
        display_name: str
    ) -> None:
        """提示用戶擷取模板圖片。
        
        當模板圖片不存在時，引導用戶選擇瀏覽器並擷取畫面作為模板。
        
        參數:
            image_detector: 圖片檢測器實例
            template_name: 模板檔名
            display_name: 顯示名稱
        """
        self.logger.info("")
        self.logger.info(Constants.LOG_SEPARATOR)
        self.logger.info(f"模板圖片不存在: {template_name}")
        self.logger.info(Constants.LOG_SEPARATOR)
        self.logger.info("")
        self.logger.info(f"需要擷取 {display_name} 的參考圖片")
        self.logger.info("   請確保目標瀏覽器的遊戲畫面已顯示目標內容")
        self.logger.info("")
        
        # 檢查是否有可用的瀏覽器
        if not self.browser_threads:
            self.logger.error("沒有可用的瀏覽器實例")
            raise RuntimeError("沒有可用的瀏覽器實例")
        
        # 顯示可選擇的瀏覽器列表
        self.logger.info("請選擇要擷取的瀏覽器:")
        available_browsers = []
        for thread in self.browser_threads:
            if thread.context and thread.is_browser_alive():
                username = thread.context.credential.username
                self.logger.info(f"  {thread.index}  - 瀏覽器 {thread.index} ({username})")
                available_browsers.append(thread)
        
        if not available_browsers:
            self.logger.error("沒有可用的瀏覽器")
            raise RuntimeError("沒有可用的瀏覽器")
        
        self.logger.info("  q  - 取消")
        self.logger.info("")
        
        try:
            print("請輸入編號: ", end="", flush=True)
            sys.stdout.flush()  # 確保緩衝區刷新
            user_input = input().strip().lower()
            
            # 檢查是否要取消
            if user_input == 'q':
                self.logger.warning("使用者取消擷取")
                raise KeyboardInterrupt("使用者取消")
            
            # 解析瀏覽器編號
            try:
                browser_index = int(user_input)
                
                # 尋找對應的瀏覽器
                selected_thread = None
                for thread in available_browsers:
                    if thread.index == browser_index:
                        selected_thread = thread
                        break
                
                if selected_thread is None:
                    self.logger.warning(f"無效的瀏覽器編號: {browser_index}")
                    # 遞迴重試
                    self._prompt_capture_template(image_detector, template_name, display_name)
                    return
                
                # 擷取並儲存模板（只截取 Canvas 區域）
                template_path = image_detector.get_template_path(template_name)
                result = image_detector.capture_canvas_screenshot(
                    selected_thread.context.driver, 
                    template_path
                )
                
                if result is not None:
                    self.logger.info("")
                    self.logger.info(f"模板圖片已建立（Canvas 區域）: {template_path}")
                    self.logger.info("")
                else:
                    self.logger.error("模板截取失敗，無法取得 Canvas 區域")
                
            except ValueError:
                self.logger.warning(f"無效的輸入: {user_input}")
                # 遞迴重試
                self._prompt_capture_template(image_detector, template_name, display_name)
                return
            
        except (EOFError, KeyboardInterrupt):
            self.logger.warning("")
            self.logger.warning("使用者取消擷取")
            raise
    
    def _wait_for_image_disappear(self, image_detector: ImageDetector, template_name: str) -> None:
        """持續等待圖片在所有瀏覽器中消失。
        
        參數:
            image_detector: 圖片檢測器實例
            template_name: 模板圖片檔名
        """
        attempt = 0
        total_browsers = len(self.browser_threads)
        
        while True:
            attempt += 1
            
            # 檢測所有瀏覽器中仍存在圖片的數量
            still_present_count = 0
            
            def detect_task(context: BrowserContext) -> bool:
                """返回 True 表示圖片仍存在"""
                result = image_detector.detect_in_browser(context.driver, template_name)
                return result is not None
            
            results = self.execute_on_all_browsers(detect_task)
            still_present_count = sum(1 for _, result, error in results if error is None and result)
            
            disappeared_count = total_browsers - still_present_count
            
            # 如果所有瀏覽器都沒有找到圖片，則返回
            if still_present_count == 0:
                self.logger.info(f"圖片已消失")
                return
            
            # 每 10 次檢測顯示一次進度
            if attempt % 10 == 0:
                self.logger.info(f"   等待中... ({disappeared_count}/{total_browsers} 已消失)")
                sys.stdout.flush()  # 確保緩衝區刷新
            
            time.sleep(Constants.DETECTION_INTERVAL)
    
    def start_control_center(self) -> None:
        """步驟 10: 啟動遊戲控制面板
        
        建立並啟動 GameControlCenter 實例，提供互動式命令列介面。
        ClickLobbyConfirm --> StartControlCenter[啟動遊戲控制面板]
        """
        self.logger.info(Constants.LOG_SEPARATOR)
        self.logger.info("【步驟 10】啟動遊戲控制面板")
        self.logger.info(Constants.LOG_SEPARATOR)
        
        if not self.browser_threads:
            self.logger.error("沒有可用的瀏覽器實例")
            return
        
        # 嘗試取得 Canvas 區域資訊（用於點擊座標計算）
        canvas_rect = None
        for bt in self.browser_threads:
            if bt.context and bt.is_browser_alive():
                try:
                    def get_canvas_rect_task(context: BrowserContext) -> Optional[Dict[str, float]]:
                        return BrowserHelper.get_canvas_rect(context.driver)
                    
                    result = bt.execute_task(get_canvas_rect_task)
                    if result:
                        canvas_rect = result
                        break
                except Exception:
                    pass
        
        # 建立控制面板實例
        control_center = GameControlCenter(
            browser_threads=self.browser_threads,
            bet_rules=self.rules,
            canvas_rect=canvas_rect,
            logger=self.logger
        )
        
        # 啟動控制面板（阻塞式，直到使用者退出）
        control_center.start()


# =============================================================================
# 主程式入口
# =============================================================================

def main() -> None:
    """主程式入口點。
    
    執行應用程式的完整流程：
    1. 初始化（載入配置、啟動代理、建立瀏覽器）
    2. 導航到登入頁面
    3. 執行登入操作
    4. 導航到遊戲頁面
    5. 調整視窗排列
    6. 執行圖片檢測流程
    7. 啟動遊戲控制面板
    
    程式結束時自動清理所有資源。
    """
    # 建立日誌記錄器
    logger = LoggerFactory.get_logger()
    # TODO: 發佈前改回 INFO
    # logger = LoggerFactory.get_logger(level=LogLevel.DEBUG)
    
    logger.info("")
    logger.info(Constants.LOG_SEPARATOR)
    logger.info(f"【{Constants.SYSTEM_NAME}】")
    logger.info(f"  版本: {Constants.VERSION}")
    logger.info(Constants.LOG_SEPARATOR)
    logger.info("")
    
    # 建立啟動器
    starter = AutoSlotGameAppStarter(logger=logger)
    
    try:
        # 執行初始化流程（步驟 1-4）
        if starter.initialize():
            browser_threads = starter.get_browser_threads()
            
            logger.info(Constants.LOG_SEPARATOR)
            logger.info("【初始化完成】")
            logger.info(Constants.LOG_SEPARATOR)
            logger.info(f"瀏覽器: {len(browser_threads)} | 用戶: {len(starter.get_credentials())} | 規則: {len(starter.get_rules())}")
            logger.info("")
            
            # 步驟 5: 導航到登入頁面
            starter.navigate_to_login_page()
            
            # 步驟 6: 執行登入操作
            starter.perform_login()
            
            # 步驟 7: 導航到遊戲頁面
            starter.navigate_to_game()
            
            # 步驟 8: 調整視窗排列
            starter.arrange_windows()
            
            # 步驟 9: 執行圖片檢測流程
            starter.execute_image_detection_flow()
            
            logger.info(Constants.LOG_SEPARATOR)
            logger.info("【啟動完成】")
            logger.info(Constants.LOG_SEPARATOR)
            logger.info("所有瀏覽器已就緒")
            logger.info("")
            
            # 步驟 10: 啟動遊戲控制面板（阻塞式，直到使用者退出）
            starter.start_control_center()
            
        else:
            logger.error("初始化失敗，程式退出")
            
    except KeyboardInterrupt:
        logger.info("")
        logger.info("收到中斷信號，正在清理...")
    except Exception as e:
        logger.error(f"程式執行時發生錯誤: {e}")
    finally:
        # 清理資源
        starter.cleanup()
        logger.info("程式已結束")


if __name__ == "__main__":
    main()
