"""
賽特遊戲自動化系統

核心特性:
- 完整型別提示與協議 (Protocol)
- 上下文管理器與資源自動清理
- 依賴注入與工廠模式
- 執行緒池並行處理
- 本地 Proxy 中繼伺服器
- 圖片識別與自動化操作
- 多瀏覽器實例管理
- 彩色日誌系統
- 完善的錯誤處理與重試機制

作者: 凡臻科技
版本: 1.32.0
Python: 3.8+

版本歷史:
- v1.32.0: 新增免費遊戲類別 3（不朽覺醒 immortal_awake）並更新座標配置（類別 1 座標更新為 0.3,0.85；類別 2 座標更新為 0.5,0.95；新增類別 3 座標為 0.7,0.85；'f' 命令和規則解析支援三種類別選擇）
- v1.31.0: 新增 richpanda 網站廣告彈窗處理功能（自動檢測 ads-container 和 close-btn-container 元素，登入後自動點擊關閉按鈕；更新 richpanda 網站的 GAME_XPATH 選擇器配置）
- v1.30.1: 修正規則執行中按 'p' 暫停後金額調整卡住的問題（adjust_betsize 方法新增 stop_event 參數支援，規則執行中的金額調整操作現在可以立即響應停止信號，避免無限等待導致程式無法正常暫停）
- v1.30.0: 新增規則前綴控制功能（帶 '-' 前綴的規則只執行一次，如 -a:2:10；不帶前綴的規則循環執行；'a' 類型規則現在也支援循環執行；規則執行邏輯重構為先執行所有單次規則，再循環執行剩餘規則）
- v1.29.0: 新增賽特二免費遊戲類別選擇功能（支援兩種類別：1=免費遊戲、2=覺醒之力；'f' 命令和規則執行時提示用戶選擇類別；規則格式更新為 f:金額:類別；自動偵測遊戲版本決定是否需要選擇類別）
- v1.28.0: 優化金額調整機制（改為無限等待模式，移除最大嘗試次數限制和關閉瀏覽器邏輯；所有瀏覽器會持續嘗試調整金額直到成功，確保全部完成後才進入下一個動作；避免因暫時性識別失敗導致瀏覽器被關閉）
- v1.27.0: 優化 Proxy 配置管理（將 Brightdata proxy 共同配置提取到 Constants，包含 PROXY_HOST、PROXY_PORT、PROXY_USERNAME_BASE、PROXY_PASSWORD；用戶資料檔案簡化為僅存儲出口 IP，程式自動組合完整 proxy 連接字串；提升配置安全性和可維護性，完全隱藏供應商資訊）
- v1.26.1: 簡化登入後公告處理邏輯（移除複雜的彈窗類型判斷和循環檢測機制，改為登入後直接使用 JavaScript 強制關閉所有彈窗；等待時間從可能超過 30 秒優化為固定 7 秒；避免卡在彈窗檢測循環，提升登入流程穩定性和響應速度）
- v1.26.0: 移除錯誤訊息自動檢測功能（移除所有 error_message 相關邏輯、常數定義、檢測方法和背景監控執行緒；保留黑屏和 game_return 檢測功能；簡化監控流程，提升系統效能）
- v1.25.0: 優化登入彈窗檢測邏輯（透過檢查 span 內容和輸入框判斷彈窗類型，區分登入表單與公告彈窗；公告彈窗自動關閉不重試，登入表單才執行重試邏輯；支援多種公告關鍵字識別，避免誤判提升登入成功率）
- v1.24.1: 優化登入流程穩定性（新增登入表單確認機制，確保表單完全載入後才輸入帳號密碼；登入表單打開失敗時自動重試最多 3 次；登入後自動檢測並關閉公告彈窗，避免誤判登入狀態；調整登入重試檢查時間從 10 秒改為 5 秒，加快重試響應速度）
- v1.24.0: 新增登入失敗自動重試機制（點擊登入按鈕後等待 10 秒檢查登入彈窗是否還存在，若存在則自動重新輸入帳號密碼並重試，最多重試 3 次，有效提升登入成功率）
- v1.23.0: 優化登入流程與修復緩衝阻塞問題（登入表單等待改用 element_to_be_clickable 確保元素可互動；創建 FlushingStreamHandler 實現全域自動刷新機制，解決多執行緒環境下日誌輸出阻塞問題；黑屏恢復時自動關閉公告彈窗）
- v1.22.1: 優化等待時間與自動跳過間隔（將搜尋「戰神」後的等待時間從 10 秒優化為 5 秒，統一遊戲載入等待時間為 5 秒；調整自動跳過點擊間隔從 10 秒改為 60 秒，減少不必要的操作頻率）
- v1.22.0: 優化登入與恢復流程（修正等待 lobby_login 超時問題：在等待過程中同時檢測 game_return，若直接出現則視為登入成功；延長搜尋「戰神」後的等待時間從 3 秒改為 10 秒，確保搜尋結果完全載入）
- v1.21.1: 優化黑屏恢復流程（將視窗放大方式從 2 倍改為全螢幕，確保 DOM 元素完全展開，提升自動導航成功率）
- v1.21.0: 優化規則執行結束流程（關閉前回到登入頁面並等待 10 秒，確保伺服器端正確處理登出）
- v1.20.0: 新增 lobby_return 檢測與自動恢復功能（點擊 game_return 後自動檢測 lobby_return，若出現則執行完整登入流程：回到 LOGIN_PAGE → 放大視窗 → 搜尋戰神 → 點擊遊戲 → 完成登入）
- v1.19.0: 優化 game_return 點擊功能（調整 iframe 檢測順序為先檢查外層頁面，增加重試機制與詳細日誌，提升首次點擊成功率）
- v1.18.0: 新增 game_return 圖片檢測功能（自動檢測並點擊返回遊戲提示，優化錯誤恢復流程為完整登入流程）
- v1.17.1: 修正自動跳過點擊功能的時間戳錯誤（將 AUTO_SKIP_CLICK_INTERVAL 從極大值改為 86400 秒，避免 timestamp too large 錯誤）
- v1.17.0: 優化調整金額功能（每次調整間隔改為3秒，超過最大嘗試次數自動關閉該瀏覽器）
- v1.16.1: 修正規則執行時間控制功能（優化時間到達後的自動退出機制，使用 os._exit() 強制退出；短時間執行時更頻繁顯示剩餘時間）
- v1.16.0: 新增規則執行時間控制功能（'r' 命令支援可選的小時參數，時間到後自動關閉所有瀏覽器並退出）
- v1.15.0: 新增錯誤訊息自動監控與重整功能（每 10 秒檢測，雙區域模板匹配，'e' 命令截取模板）
- v1.14.3: 修正按下 'p' 後規則仍繼續執行的問題（在規則執行的關鍵步驟之間加入停止檢查）
- v1.14.2: 修正規則執行循環問題（'f' 規則執行後正確清除停止事件，確保循環繼續）
- v1.14.1: 修正規則執行中 'f' 規則 AttributeError 問題（改用 browser_operator.last_canvas_rect）
- v1.14.0: 擴展規則執行功能，支援 'f' 類型規則（購買免費遊戲），規則格式: f:金額
- v1.13.0: 擴展規則執行功能，支援自動旋轉規則（'a' 類型）和標準規則（'s' 類型）混合執行
- v1.12.1: 修正規則執行中關閉瀏覽器導致程序停頓的問題（添加瀏覽器狀態檢測）
- v1.12.0: 移除視窗大小鎖定功能，允許用戶自由調整視窗大小（初始仍為 600x400）
- v1.11.0: 新增自動跳過點擊功能，每 30 秒自動點擊跳過區域（背景執行，持續運行）
- v1.10.0: 新增視窗大小鎖定功能，自動監控並恢復視窗大小（位置可自由移動）
- v1.9.0: 優化系統啟動流程（自動顯示完整指令列表，移除 emoji 符號，統一日誌格式）
- v1.8.0: 優化關閉瀏覽器功能（'q' 指令），支援選擇性關閉指定瀏覽器
- v1.7.1: 修正金額識別問題（統一使用 Constants 定義，移除重複定義和硬編碼數值）
- v1.7.0: 新增規則執行功能（'r' 指令），支援自動切換金額並按空白鍵，規則循環執行
- v1.6.2: 調整遊戲金額配置（GAME_BETSIZE 和 GAME_BETSIZE_TUPLE），從 73 種金額優化為 64 種金額
- v1.6.1: 調整金額顯示和裁切參數（BETSIZE_DISPLAY_Y: 380→370, CROP_MARGIN_X: 50→40, CROP_MARGIN_Y: 20→10）
- v1.6.0: 優化登入流程（新增錯誤訊息檢測與自動重啟機制）
- v1.5.0: 統一管理所有魔法數字（視窗尺寸、座標、等待時間、重試次數等）
- v1.4.3: 優化瀏覽器網路設定（啟用 QUIC、TCP Fast Open、NetworkService）
- v1.4.2: 修正 Windows 中文路徑截圖儲存失敗問題
- v1.4.1: 新增瀏覽器靜音功能，自動將所有瀏覽器設為靜音
- v1.4.0: 優化免費遊戲結算流程（3秒後開始點擊，間隔3秒，共5次）
- v1.3.0: 新增自動旋轉功能（支援 10、50、100 次）
- v1.2.0: 新增專案啟動前自動清除 chromedriver 快取功能
- v1.1.0: 修正 OpenCV 無法讀取中文路徑圖片的問題
- v1.0.0: 初始版本發布
"""

import datetime
import logging
import sys
import platform
import socket
import select
import base64
import time
import subprocess
from typing import Optional, List, Dict, Tuple, Any, Callable, Protocol, Union
from pathlib import Path
from dataclasses import dataclass, field
from contextlib import contextmanager, suppress
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
from enum import Enum
import threading

# Selenium WebDriver 相關
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# 圖片處理相關
import cv2
import numpy as np
from PIL import Image
import io


# 導出的公共 API
__all__ = [
    # 常量
    'Constants',
    # 資料類別
    'UserCredential',
    'BetRule',
    'ProxyInfo',
    'BrowserContext',
    'OperationResult',
    # 例外類別
    'AutoSlotGameError',
    'ConfigurationError',
    'BrowserCreationError',
    'ProxyServerError',
    'ImageDetectionError',
    # 日誌類別
    'LogLevel',
    'LoggerFactory',
    # 輔助類別
    'BrowserHelper',
    # 主要類別
    'ConfigReader',
    'BrowserManager',
    'LocalProxyServerManager',
    'SyncBrowserOperator',
    'ImageDetector',
    'BrowserRecoveryManager',
    'GameControlCenter',
    'AutoSlotGameApp',
]


# ============================================================================
# 常量定義
# ============================================================================

class Constants:
    """系統常量"""
    # 版本資訊
    VERSION = "1.30.1"
    SYSTEM_NAME = "賽特遊戲自動化系統"
    
    DEFAULT_LIB_PATH = "lib"
    DEFAULT_CREDENTIALS_FILE = "用戶資料.txt"
    DEFAULT_RULES_FILE = "用戶規則.txt"
    
    DEFAULT_PROXY_START_PORT = 9000
    DEFAULT_TIMEOUT_SECONDS = 30
    DEFAULT_PAGE_LOAD_TIMEOUT = 600
    DEFAULT_SCRIPT_TIMEOUT = 600
    DEFAULT_IMPLICIT_WAIT = 60
    
    MAX_THREAD_WORKERS = 10
    PROXY_SERVER_BIND_HOST = "127.0.0.1"
    PROXY_BUFFER_SIZE = 4096
    PROXY_SELECT_TIMEOUT = 1.0
    
    # URL 配置
    # LOGIN_PAGE = "https://m.jfw-win.com/#/login?redirect=%2Fhome%2Fpage"
    # GAME_PAGE = "https://www.sf-16888.com/#/home/loding?game_code=golden-seth&factory_code=ATG&state=true&name=戰神賽特2%20覺醒之力"
    
    # FIN
    LOGIN_PAGE = "https://www.fin88.app"
    GAME_PAGE = "https://www.fin88.app"
    # GAME_XPATH = "//div[contains(@class, 'game-card-container') and .//div[contains(@style, 'ATG-egyptian-mythology.png')]]" # 賽特1（第二個大卡片-戰神埃及神話）
    GAME_XPATH = "//div[contains(@class, 'game-card-container') and contains(@class, 'big')]" # 賽特2（第一個大卡片）勿刪除

    # FPD 勿刪除
    # LOGIN_PAGE = "https://richpanda.vip"
    # GAME_PAGE = "https://richpanda.vip"
    # GAME_XPATH = "//div[contains(@class, 'game-card-container') and .//div[contains(@class, 'game-img') and contains(@style, 'ATG-egyptian-mythology.png')]]"  # 賽特1
    # GAME_XPATH = "//div[contains(@class, 'game-card-container') and contains(@class, 'big')]"  # 賽特2 勿刪除

    # 頁面元素選擇器
    INITIAL_LOGIN_BUTTON = "//button[contains(@class, 'btn') and contains(@class, 'login') and contains(@class, 'pc') and text()='登入']"
    USERNAME_INPUT = "//input[@placeholder='請輸入帳號/手機號']"
    PASSWORD_INPUT = "//input[@placeholder='請輸入您的登入密碼']"
    LOGIN_BUTTON = "//button[contains(@class, 'custom-button') and @type='submit' and contains(., '登入遊戲')]"
    POPUP_CLOSE_BUTTON = "//button[contains(@class, 'btn-close')]"
    SEARCH_BUTTON = "//button[contains(@class, 'search-btn')]"
    SEARCH_INPUT = "//input[@placeholder='按換行鍵搜索']"
    GAME_IFRAME = "//iframe[contains(@class, 'iframe-item')]"
    GAME_CANVAS = "GameCanvas"
    
    # 圖片檢測配置
    IMAGE_DIR = "img"
    LOBBY_LOGIN = "lobby_login.png"
    LOBBY_CONFIRM = "lobby_confirm.png"
    LOBBY_RETURN = "lobby_return.png"  # 大廳返回模板
    GAME_RETURN = "game_return.png"  # 遊戲返回模板
    BLACK_SCREEN = "black_screen.png"  # 黑屏模板
    MATCH_THRESHOLD = 0.8  # 圖片匹配閾值
    BETSIZE_MATCH_THRESHOLD = 0.85  # 金額識別匹配閾值
    DETECTION_INTERVAL = 1.0  # 檢測間隔（秒）
    MAX_DETECTION_ATTEMPTS = 60  # 最大檢測次數
    
    # Canvas 動態計算比例（用於點擊座標）
    # lobby_login 按鈕座標比例
    LOBBY_LOGIN_BUTTON_X_RATIO = 0.5  # lobby_login 開始遊戲按鈕 X 座標比例
    LOBBY_LOGIN_BUTTON_Y_RATIO = 0.9   # lobby_login 開始遊戲按鈕 Y 座標比例
    
    # lobby_confirm 按鈕座標比例
    LOBBY_CONFIRM_BUTTON_X_RATIO = 0.74  # lobby_confirm 確認按鈕 X 座標比例
    LOBBY_CONFIRM_BUTTON_Y_RATIO = 0.85  # lobby_confirm 確認按鈕 Y 座標比例
    
    # 購買免費遊戲按鈕座標比例
    BUY_FREE_GAME_BUTTON_X_RATIO = 0.15  # 免費遊戲區域按鈕 X 座標比例
    BUY_FREE_GAME_BUTTON_Y_RATIO = 0.75  # 免費遊戲區域按鈕 Y 座標比例
    BUY_FREE_GAME_CONFIRM_X_RATIO = 0.65  # 免費遊戲確認按鈕 X 座標比例（預設）
    BUY_FREE_GAME_CONFIRM_Y_RATIO = 0.9   # 免費遊戲確認按鈕 Y 座標比例（預設）
    # 免費遊戲類別座標 - only_freegame (類別 1)
    BUY_FREE_GAME_ONLY_FREEGAME_X_RATIO = 0.3   # only_freegame 確認按鈕 X 座標比例
    BUY_FREE_GAME_ONLY_FREEGAME_Y_RATIO = 0.85  # only_freegame 確認按鈕 Y 座標比例
    # 免費遊戲類別座標 - awake_power (類別 2)
    BUY_FREE_GAME_AWAKE_POWER_X_RATIO = 0.5     # awake_power 確認按鈕 X 座標比例
    BUY_FREE_GAME_AWAKE_POWER_Y_RATIO = 0.95    # awake_power 確認按鈕 Y 座標比例
    # 免費遊戲類別座標 - immortal_awake (類別 3)
    BUY_FREE_GAME_IMMORTAL_AWAKE_X_RATIO = 0.7  # immortal_awake 確認按鈕 X 座標比例
    BUY_FREE_GAME_IMMORTAL_AWAKE_Y_RATIO = 0.85 # immortal_awake 確認按鈕 Y 座標比例
    BUY_FREE_GAME_WAIT_SECONDS = 10  # 購買後等待秒數
    
    # game_return 返回確認按鈕座標比例
    GAME_CONFIRM_BUTTON_X_RATIO = 0.5  # game_return 確認按鈕 X 座標比例
    GAME_CONFIRM_BUTTON_Y_RATIO = 0.55  # game_return 確認按鈕 Y 座標比例
    
    # 自動旋轉按鈕座標比例
    AUTO_SPIN_BUTTON_X_RATIO = 0.8  # 自動轉按鈕 X 座標比例
    AUTO_SPIN_BUTTON_Y_RATIO = 0.77   # 自動轉按鈕 Y 座標比例
    AUTO_SPIN_10_X_RATIO = 0.4        # 10次按鈕 X 座標比例
    AUTO_SPIN_10_Y_RATIO = 0.5       # 10次按鈕 Y 座標比例
    AUTO_SPIN_50_X_RATIO = 0.5       # 50次按鈕 X 座標比例
    AUTO_SPIN_50_Y_RATIO = 0.5       # 50次按鈕 Y 座標比例
    AUTO_SPIN_100_X_RATIO = 0.57      # 100次按鈕 X 座標比例
    AUTO_SPIN_100_Y_RATIO = 0.5      # 100次按鈕 Y 座標比例
    
    # 操作相關常量
    DEFAULT_WAIT_SECONDS = 3  # 預設等待時間（秒）
    DETECTION_PROGRESS_INTERVAL = 20  # 檢測進度顯示間隔
    
    # 操作等待時間（秒）
    LOGIN_WAIT_TIME = 5          # 登入後等待時間
    BETSIZE_ADJUST_STEP_WAIT = 3.0  # 調整金額每步等待時間
    BETSIZE_ADJUST_VERIFY_WAIT = 2.0  # 調整金額驗證前等待時間
    BETSIZE_ADJUST_RETRY_WAIT = 1.0  # 調整金額重試等待時間
    BETSIZE_READ_RETRY_WAIT = 0.5    # 讀取金額重試等待時間
    FREE_GAME_CLICK_WAIT = 2     # 免費遊戲點擊間隔
    FREE_GAME_SETTLE_INITIAL_WAIT = 3  # 免費遊戲結算初始等待
    FREE_GAME_SETTLE_CLICK_INTERVAL = 3  # 免費遊戲結算點擊間隔
    AUTO_SPIN_MENU_WAIT = 0.5    # 自動旋轉選單等待時間
    PROXY_SERVER_START_WAIT = 1  # Proxy 伺服器啟動等待時間
    TEMPLATE_CAPTURE_WAIT = 1    # 模板截取後等待時間
    DETECTION_COMPLETE_WAIT = 2  # 檢測完成後等待時間
    RULE_SWITCH_WAIT = 1.0       # 規則切換等待時間
    AUTO_PRESS_THREAD_JOIN_TIMEOUT = 2.0  # 自動按鍵執行緒結束等待時間
    AUTO_PRESS_STOP_TIMEOUT = 5.0  # 自動按鍵停止等待超時時間
    STOP_EVENT_WAIT_TIMEOUT = 5.0  # 停止事件等待超時時間
    STOP_EVENT_ERROR_WAIT = 1.0    # 停止事件錯誤等待時間
    SERVER_SOCKET_TIMEOUT = 1.0    # 伺服器 Socket 超時時間
    CLEANUP_PROCESS_TIMEOUT = 10   # 清除程序超時時間（秒）
    AUTO_SKIP_CLICK_INTERVAL = 60  # 自動跳過點擊間隔時間（秒）# 設為 86400表示不啟用
    RULE_EXECUTION_TIME_CHECK_INTERVAL = 10  # 規則執行時間檢查間隔（秒）
    
    # 重試與循環配置
    BETSIZE_ADJUST_MAX_ATTEMPTS = 400  # 調整金額最大嘗試次數
    BETSIZE_READ_MAX_RETRIES = 2       # 讀取金額最大重試次數
    FREE_GAME_SETTLE_CLICK_COUNT = 5   # 免費遊戲結算點擊次數
    DETECTION_WAIT_MAX_ATTEMPTS = 20   # 檢測等待最大嘗試次數
    LOBBY_CONFIRM_CHECK_ATTEMPTS = 3   # lobby_confirm 檢測嘗試次數（之後檢查錯誤）
    
    # 視窗排列配置
    DEFAULT_WINDOW_WIDTH = 600
    DEFAULT_WINDOW_HEIGHT = 400
    DEFAULT_WINDOW_COLUMNS = 4
    ENLARGED_WINDOW_WIDTH = 1200   # 恢復連線時放大視窗寬度（避免 maximize_window 多瀏覽器衝突）
    ENLARGED_WINDOW_HEIGHT = 800   # 恢復連線時放大視窗高度
    
    # 下注金額調整按鈕座標
    BETSIZE_INCREASE_BUTTON_X = 0.8     # 增加金額按鈕 X 座標
    BETSIZE_INCREASE_BUTTON_Y = 0.89    # 增加金額按鈕 Y 座標
    BETSIZE_DECREASE_BUTTON_X =  0.63   # 減少金額按鈕 X 座標
    BETSIZE_DECREASE_BUTTON_Y =  0.89   # 減少金額按鈕 Y 座標
    BETSIZE_DISPLAY_X = 0.72            # 金額顯示位置 X 座標
    BETSIZE_DISPLAY_Y = 0.89            # 金額顯示位置 Y 座標

    # 黑屏截圖座標（基於預設視窗大小）
    BLACKSCREEN_CENTER_X = 300  # 黑屏區域中心 X 座標
    BLACKSCREEN_CENTER_Y = 195  # 黑屏區域中心 Y 座標
    BLACKSCREEN_CROP_MARGIN_X = 125  # 黑屏截圖裁切邊距（左右）
    BLACKSCREEN_CROP_MARGIN_Y = 75   # 黑屏截圖裁切邊距（上下）
    BLACKSCREEN_PERSIST_SECONDS = 10  # 黑屏持續秒數閾值

    # 返回遊戲提示截圖座標（基於預設視窗大小，使用與黑屏相同的座標）
    GAME_RETURN_CENTER_X = 290  # 返回遊戲提示中心 X 座標
    GAME_RETURN_CENTER_Y = 160  # 返回遊戲提示中心 Y 座標
    GAME_RETURN_CROP_MARGIN_X = 50  # 返回遊戲提示裁切邊距（左右）
    GAME_RETURN_CROP_MARGIN_Y = 10   # 返回遊戲提示裁切邊距（上下）

    # 大廳返回提示截圖座標（基於預設視窗大小）
    LOBBY_RETURN_CENTER_X = 300  # 大廳返回提示中心 X 座標
    LOBBY_RETURN_CENTER_Y = 200  # 大廳返回提示中心 Y 座標
    LOBBY_RETURN_CROP_MARGIN_X = 50  # 大廳返回提示裁切邊距（左右）
    LOBBY_RETURN_CROP_MARGIN_Y = 20  # 大廳返回提示裁切邊距（上下）

    # 截圖裁切範圍（像素）
    BETSIZE_CROP_MARGIN_X = 40  # 金額模板水平裁切邊距
    BETSIZE_CROP_MARGIN_Y = 10  # 金額模板垂直裁切邊距
    TEMPLATE_CROP_MARGIN = 20    # 通用模板裁切邊距（用於 lobby_confirm 等）
    
    # 遊戲金額配置（使用 frozenset 提升查詢效率）
    GAME_BETSIZE = frozenset((
        2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 24, 28, 32, 36, 40, 48, 56, 60, 64, 72, 80, 96, 100, 120, 140, 160, 180, 200, 240, 280, 300, 320, 360, 400, 420, 480, 500, 540, 560, 600, 640, 700, 720, 800, 840, 900, 960, 980, 1000, 1080, 1120, 1200, 1260, 1280, 1400, 1440, 1500, 1600, 1800, 2000, 2100, 2400, 2700, 3000
    ))
    
    # 遊戲金額列表（用於索引計算）
    GAME_BETSIZE_TUPLE = (
        2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 24, 28, 32, 36, 40, 48, 56, 60, 64, 72, 80, 96, 100, 120, 140, 160, 180, 200, 240, 280, 300, 320, 360, 400, 420, 480, 500, 540, 560, 600, 640, 700, 720, 800, 840, 900, 960, 980, 1000, 1080, 1120, 1200, 1260, 1280, 1400, 1440, 1500, 1600, 1800, 2000, 2100, 2400, 2700, 3000
    )


# ============================================================================
# 輔助函式
# ============================================================================

def cleanup_chromedriver_processes() -> None:
    """清除所有緩存的 chromedriver 程序。
    
    在程式啟動前執行，確保沒有殘留的 chromedriver 程序佔用資源。
    支援 Windows、macOS 和 Linux 作業系統。
    """
    logger = LoggerFactory.get_logger()
    system = platform.system().lower()
    
    logger.info("=" * 60)
    logger.info("【系統初始化】清理殘留程序")
    logger.info("=" * 60)
    
    try:
        if system == "windows":
            # Windows: 使用 taskkill 命令
            result = subprocess.run(
                ["taskkill", "/F", "/IM", "chromedriver.exe"],
                capture_output=True,
                text=True,
                timeout=Constants.CLEANUP_PROCESS_TIMEOUT
            )
            
            # 檢查結果
            if result.returncode == 0:
                logger.info("[成功] 已清除 Windows 上的 chromedriver 程序")
            elif "找不到" in result.stdout or "not found" in result.stdout.lower():
                logger.info("[成功] 沒有殘留的 chromedriver 程序")
            else:
                logger.debug(f"taskkill 執行結果: {result.stdout.strip()}")
                
        elif system in ["darwin", "linux"]:
            # macOS/Linux: 使用 killall 命令
            result = subprocess.run(
                ["killall", "-9", "chromedriver"],
                capture_output=True,
                text=True,
                timeout=Constants.CLEANUP_PROCESS_TIMEOUT
            )
            
            # killall 在沒有找到程序時會返回非 0，這是正常的
            if result.returncode == 0:
                logger.info(f"[成功] 已清除 {system.upper()} 上的 chromedriver 程序")
            else:
                logger.info("[成功] 沒有殘留的 chromedriver 程序")
        else:
            logger.warning(f"[警告] 不支援的作業系統: {system}，跳過清除 chromedriver")
            
    except subprocess.TimeoutExpired:
        logger.warning("[警告] 清除 chromedriver 程序逾時")
    except FileNotFoundError:
        logger.info("[成功] 沒有殘留的 chromedriver 程序")
    except Exception as e:
        logger.warning(f"[警告] 清除程序時發生錯誤: {e}")
    
    logger.info("")


def get_resource_path(relative_path: str = "") -> Path:
    """取得資源檔案的絕對路徑。
    
    在開發環境中，返回專案根目錄的路徑。
    在打包後的環境中，返回 exe 所在目錄的路徑（而非臨時目錄）。
    
    Args:
        relative_path: 相對於根目錄的路徑
        
    Returns:
        資源檔案的絕對路徑
    """
    if getattr(sys, 'frozen', False):
        # 打包後：使用 exe 所在目錄（不是 _MEIPASS 臨時目錄）
        # 因為 lib 和 img 應該放在 exe 旁邊，方便使用者編輯
        base_path = Path(sys.executable).resolve().parent
    else:
        # 開發環境：使用 main.py 的父目錄的父目錄
        base_path = Path(__file__).resolve().parent.parent
    
    if relative_path:
        return base_path / relative_path
    return base_path


def cv2_imread_unicode(file_path: Union[str, Path], flags: int = cv2.IMREAD_COLOR) -> Optional[np.ndarray]:
    """安全讀取圖片（支援 Unicode 路徑）。
    
    OpenCV 的 cv2.imread() 無法處理包含中文或其他非 ASCII 字元的路徑。
    此函式使用 numpy 和 PIL 作為替代方案。
    
    Args:
        file_path: 圖片檔案路徑（支援中文路徑）
        flags: OpenCV 讀取標誌（cv2.IMREAD_COLOR, cv2.IMREAD_GRAYSCALE 等）
        
    Returns:
        圖片的 numpy 陣列，失敗返回 None
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
        
    except Exception as e:
        # 返回 None 保持與 cv2.imread() 相同的行為
        return None


# ============================================================================
# 資料類別
# ============================================================================

@dataclass(frozen=True)
class UserCredential:
    """使用者憑證資料結構（不可變）。"""
    username: str
    password: str
    proxy: Optional[str] = None
    
    def __post_init__(self) -> None:
        """驗證資料完整性"""
        if not self.username or not self.password:
            raise ValueError("使用者名稱和密碼不能為空")


@dataclass(frozen=True)
class BetRule:
    """下注規則資料結構（不可變）。
    
    支援三種類型:
    - 'a' (自動旋轉): amount, spin_count
    - 's' (標準規則): amount, duration, min_seconds, max_seconds
    - 'f' (購買免費遊戲): amount, free_game_type (1=only_freegame, 2=awake_power, 3=immortal_awake)
    
    前綴說明:
    - 帶 '-' 前綴（如 -a:2:10）: 只執行一次
    - 不帶前綴（如 a:2:10）: 循環執行
    """
    rule_type: str  # 'a'、's' 或 'f'
    amount: float
    spin_count: Optional[int] = None  # 'a' 類型使用
    duration: Optional[int] = None  # 's' 類型使用（分鐘）
    min_seconds: Optional[float] = None  # 's' 類型使用
    max_seconds: Optional[float] = None  # 's' 類型使用
    free_game_type: Optional[int] = None  # 'f' 類型使用 (1=only_freegame, 2=awake_power, 3=immortal_awake)
    once_only: bool = False  # 是否只執行一次（帶 '-' 前綴的規則）
    
    def __post_init__(self) -> None:
        """驗證資料完整性"""
        if self.amount <= 0:
            raise ValueError(f"下注金額必須大於 0: {self.amount}")
        
        if self.rule_type == 'a':
            # 自動旋轉規則驗證
            if self.spin_count is None:
                raise ValueError("自動旋轉規則必須指定次數")
            if self.spin_count not in [10, 50, 100]:
                raise ValueError(f"自動旋轉次數必須是 10、50 或 100: {self.spin_count}")
        
        elif self.rule_type == 's':
            # 標準規則驗證
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
            if self.free_game_type is None:
                raise ValueError("購買免費遊戲規則必須指定類別 (1、2 或 3)")
            if self.free_game_type not in [1, 2, 3]:
                raise ValueError(f"免費遊戲類別必須是 1 (免費遊戲)、2 (覺醒之力) 或 3 (不朽覺醒): {self.free_game_type}")
        
        else:
            raise ValueError(f"無效的規則類型: {self.rule_type}，必須是 'a'、's' 或 'f'")


@dataclass(frozen=True)
class ProxyInfo:
    """Proxy 資訊資料結構（不可變）。"""
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
        """轉換為 Proxy URL 格式。
        
        Returns:
            格式化的 Proxy URL
        """
        # 使用字串拼接而非 f-string 在大量呼叫時更高效
        return f"http://{self.username}:{self.password}@{self.host}:{self.port}"
    
    def to_connection_string(self) -> str:
        """轉換為連接字串格式（快取結果）。
        
        Returns:
            格式化的連接字串 "host:port:username:password"
        """
        return f"{self.host}:{self.port}:{self.username}:{self.password}"
    
    def __str__(self) -> str:
        """字串表示（隱藏敏感資訊）"""
        return f"ProxyInfo({self.host}:{self.port}, user={self.username[:3]}***)"
    
    @staticmethod
    def from_connection_string(connection_string: str) -> 'ProxyInfo':
        """從連接字串建立 ProxyInfo 實例。
        
        Args:
            connection_string: 格式為 "host:port:username:password"
            
        Returns:
            ProxyInfo 實例
            
        Raises:
            ValueError: 格式不正確時
        """
        parts = connection_string.split(':')
        if len(parts) < 4:
            raise ValueError(f"Proxy 連接字串格式不正確: {connection_string}")
        
        return ProxyInfo(
            host=parts[0],
            port=int(parts[1]),
            username=parts[2],
            password=':'.join(parts[3:])  # 密碼可能包含冒號
        )


@dataclass
class BrowserContext:
    """瀏覽器上下文資訊。
    
    封裝瀏覽器實例及其相關資訊，提供便捷的存取介面。
    
    Attributes:
        driver: WebDriver 實例
        credential: 使用者憑證
        index: 瀏覽器索引（從 1 開始）
        proxy_port: Proxy 埠號（可選）
        created_at: 建立時間戳
    """
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
    """操作結果封裝。
    
    用於封裝操作的執行結果，包含成功狀態、資料、錯誤和訊息。
    
    Attributes:
        success: 操作是否成功
        data: 操作返回的資料
        error: 發生的例外（如果有）
        message: 額外的訊息
    """
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


# ============================================================================
# 例外類別
# ============================================================================

class AutoSlotGameError(Exception):
    """基礎例外類別"""
    pass


class ConfigurationError(AutoSlotGameError):
    """配置相關錯誤"""
    pass


class BrowserCreationError(AutoSlotGameError):
    """瀏覽器建立錯誤"""
    pass


class ProxyServerError(AutoSlotGameError):
    """Proxy 伺服器錯誤"""
    pass


class ImageDetectionError(AutoSlotGameError):
    """圖片檢測錯誤"""
    pass


# ============================================================================
# 日誌系統
# ============================================================================

class LogLevel(Enum):
    """日誌等級"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class ColoredFormatter(logging.Formatter):
    """帶顏色的日誌格式化器。
    
    使用 ANSI 顏色碼為不同等級的日誌訊息添加顏色。
    """
    
    # ANSI 顏色碼
    COLORS = {
        'RESET': "\033[0m",
        'INFO': "\033[32m",       # 綠色
        'WARNING': "\033[33m",    # 黃色
        'ERROR': "\033[31m",      # 紅色
        'CRITICAL': "\033[35m",   # 紫色
        'DEBUG': "\033[36m",      # 青色
        'TIMESTAMP': "\033[90m",  # 灰色
    }
    
    def __init__(self, fmt: Optional[str] = None, datefmt: Optional[str] = None) -> None:
        """初始化顏色格式化器。
        
        Args:
            fmt: 日誌格式字串
            datefmt: 日期格式字串
        """
        super().__init__(fmt, datefmt)
        self.formatters = {
            logging.DEBUG: self._create_formatter(self.COLORS['DEBUG'], 'DEBUG'),
            logging.INFO: self._create_formatter(self.COLORS['INFO'], 'INFO'),
            logging.WARNING: self._create_formatter(self.COLORS['WARNING'], 'WARNING'),
            logging.ERROR: self._create_formatter(self.COLORS['ERROR'], 'ERROR'),
            logging.CRITICAL: self._create_formatter(self.COLORS['CRITICAL'], 'CRITICAL'),
        }
    
    def _create_formatter(self, color: str, level_name: str) -> logging.Formatter:
        """建立指定顏色的格式化器"""
        return logging.Formatter(
            f"{self.COLORS['TIMESTAMP']}%(asctime)s{self.COLORS['RESET']} - "
            f"{color}%(levelname)-8s{self.COLORS['RESET']} - "
            f"%(message)s"
        )
    
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


class FlushingStreamHandler(logging.StreamHandler):
    """自動刷新的 StreamHandler，解決多執行緒環境下的緩衝阻塞問題。"""
    
    def emit(self, record: logging.LogRecord) -> None:
        """輸出日誌記錄並強制刷新緩衝區。
        
        Args:
            record: 日誌記錄物件
        """
        try:
            super().emit(record)
            self.flush()  # 每次輸出後立即刷新
        except Exception:
            self.handleError(record)


class LoggerFactory:
    """Logger 工廠類別 - 使用單例模式優化效能"""
    
    _loggers: Dict[str, logging.Logger] = {}
    _lock = threading.RLock()  # 使用 RLock 避免死鎖
    _formatter: Optional[ColoredFormatter] = None  # 共用 formatter 實例
    
    @classmethod
    def get_logger(
        cls, 
        name: str = "AutoSlotGame",
        level: LogLevel = LogLevel.INFO
    ) -> logging.Logger:
        """取得或建立 logger 實例（執行緒安全）。
        
        Args:
            name: Logger 名稱
            level: 日誌等級
            
        Returns:
            配置完成的 Logger 物件
        """
        # 快速路徑：無鎖檢查（大多數情況下避免加鎖）
        if name in cls._loggers:
            return cls._loggers[name]
        
        with cls._lock:
            # 雙重檢查避免重複建立
            if name in cls._loggers:
                return cls._loggers[name]
            
            logger = logging.getLogger(name)
            logger.setLevel(level.value)
            logger.propagate = False
            
            # 避免重複添加 handler
            if not logger.handlers:
                # 共用 formatter 實例以節省記憶體
                if cls._formatter is None:
                    cls._formatter = ColoredFormatter()
                
                # 使用自動刷新的 Handler 避免緩衝阻塞
                console_handler = FlushingStreamHandler(sys.stdout)
                console_handler.setLevel(level.value)
                console_handler.setFormatter(cls._formatter)
                logger.addHandler(console_handler)
            
            cls._loggers[name] = logger
            return logger


# ============================================================================
# 配置讀取器 (使用 Protocol 和依賴注入)
# ============================================================================

class ConfigReaderProtocol(Protocol):
    """配置讀取器協議"""
    
    def read_user_credentials(self, filename: str) -> List[UserCredential]:
        """讀取使用者憑證"""
        ...
    
    def read_bet_rules(self, filename: str) -> List[BetRule]:
        """讀取下注規則"""
        ...


class ConfigReader:
    """配置檔案讀取器。
    
    讀取並解析系統所需的各種配置檔案。
    採用上下文管理器和更好的錯誤處理。
    
    Attributes:
        lib_path: 配置檔案所在目錄路徑
        logger: 日誌記錄器
    """
    
    def __init__(
        self, 
        lib_path: Optional[Path] = None,
        logger: Optional[logging.Logger] = None
    ) -> None:
        """初始化配置讀取器。
        
        Args:
            lib_path: 配置檔案目錄路徑,預設為專案的 lib 目錄
            logger: 日誌記錄器
        """
        if lib_path is None:
            # 使用輔助函式取得專案根目錄
            lib_path = get_resource_path(Constants.DEFAULT_LIB_PATH)
        
        self.lib_path = Path(lib_path)
        self.logger = logger or LoggerFactory.get_logger()
        
        # 驗證目錄存在
        if not self.lib_path.exists():
            raise ConfigurationError(f"配置目錄不存在: {self.lib_path}")
    
    def _read_file_lines(self, filename: str, skip_header: bool = True) -> List[str]:
        """讀取檔案並返回有效行列表（優化版）。
        
        Args:
            filename: 檔案名稱
            skip_header: 是否跳過首行標題
            
        Returns:
            有效行列表（去除空行和註釋）
            
        Raises:
            ConfigurationError: 檔案讀取失敗
        """
        file_path = self.lib_path / filename
        
        if not file_path.exists():
            raise ConfigurationError(f"找不到配置檔案: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8', buffering=8192) as f:
                lines = f.readlines()
            
            # 跳過標題行
            start_index = 1 if skip_header and lines else 0
            
            # 使用列表推導式（更高效）
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
        第三欄為出口 IP（可選），程式會自動組合完整的 proxy 連接字串
        
        Args:
            filename: 檔案名稱
            
        Returns:
            使用者憑證列表
            
        Raises:
            ConfigurationError: 讀取或解析失敗
        """
        credentials = []
        lines = self._read_file_lines(filename, skip_header=True)
        
        for line_number, line in enumerate(lines, start=2):  # +2 因為跳過標題
            try:
                parts = [p.strip() for p in line.split(',')]
                
                if len(parts) < 2:
                    self.logger.warning(f"第 {line_number} 行格式不完整 已跳過 {line}")
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
                self.logger.warning(f"第 {line_number} 行資料無效 {e}")
                continue
        
        return credentials
    
    def read_bet_rules(
        self, 
        filename: str = Constants.DEFAULT_RULES_FILE
    ) -> List[BetRule]:
        """讀取下注規則檔案。
        
        支援三種格式:
        - a:金額:次數 (自動旋轉規則)
        - s:金額:時間(分鐘):最小(秒數):最大(秒數) (標準規則)
        - f:金額:類別 (購買免費遊戲)
        
        前綴說明:
        - 帶 '-' 前綴（如 -a:2:10）: 只執行一次
        - 不帶前綴（如 a:2:10）: 循環執行
        
        Args:
            filename: 檔案名稱
            
        Returns:
            下注規則列表
            
        Raises:
            ConfigurationError: 讀取或解析失敗
        """
        rules = []
        lines = self._read_file_lines(filename, skip_header=True)
        
        for line_number, line in enumerate(lines, start=2):
            try:
                parts = line.split(':')
                
                if len(parts) < 2:
                    self.logger.warning(f"第 {line_number} 行格式不完整 已跳過 {line}")
                    continue
                
                # 檢查是否帶有 '-' 前綴（只執行一次）
                rule_type_raw = parts[0].strip().lower()
                once_only = rule_type_raw.startswith('-')
                rule_type = rule_type_raw.lstrip('-')
                
                if rule_type == 'a':
                    # 自動旋轉規則: a:金額:次數
                    if len(parts) < 3:
                        self.logger.warning(f"第 {line_number} 行格式不完整 已跳過 {line}")
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
                    # 標準規則: s:金額:時間:最小秒數:最大秒數
                    if len(parts) < 5:
                        self.logger.warning(f"第 {line_number} 行格式不完整 已跳過 {line}")
                        continue
                    
                    amount = float(parts[1].strip())
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
                    
                elif rule_type == 'f':
                    # 購買免費遊戲規則: f:金額:類別
                    # 類別: 1=only_freegame, 2=awake_power, 3=immortal_awake
                    if len(parts) < 3:
                        self.logger.warning(f"第 {line_number} 行缺少免費遊戲類別（格式: f:金額:類別）")
                        continue
                    
                    amount = float(parts[1].strip())
                    free_game_type = int(parts[2].strip())
                    
                    if free_game_type not in [1, 2, 3]:
                        self.logger.warning(f"第 {line_number} 行無效的免費遊戲類別 '{free_game_type}'（必須是 1、2 或 3）")
                        continue
                    
                    rules.append(BetRule(
                        rule_type='f',
                        amount=amount,
                        free_game_type=free_game_type,
                        once_only=once_only
                    ))
                    
                else:
                    self.logger.warning(f"第 {line_number} 行無效的規則類型 '{rule_type}' 已跳過")
                    continue
                
            except (ValueError, IndexError) as e:
                self.logger.warning(f"第 {line_number} 行無法解析 {e}")
                continue
        
        return rules


# ============================================================================
# Proxy 伺服器 (改進資源管理和執行緒安全)
# ============================================================================

class ProxyConnectionHandler:
    """Proxy 連接處理器"""
    
    def __init__(
        self, 
        upstream_proxy: ProxyInfo,
        logger: Optional[logging.Logger] = None
    ):
        self.upstream_proxy = upstream_proxy
        self.logger = logger or LoggerFactory.get_logger()
    
    def handle_connect_request(
        self, 
        client_socket: socket.socket,
        request: bytes
    ) -> None:
        """處理 HTTPS CONNECT 請求。
        
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
        """處理普通 HTTP 請求。
        
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
        """雙向轉發數據。
        
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
    簡易 HTTP Proxy 伺服器 (使用 Python 內建模組)
    將帶認證的遠端 proxy 轉換為本地無需認證的 proxy
    採用更好的資源管理和執行緒安全
    """
    
    def __init__(
        self, 
        local_port: int, 
        upstream_proxy: ProxyInfo,
        logger: Optional[logging.Logger] = None
    ):
        """
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
        """處理客戶端連接。
        
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
        """啟動 proxy 伺服器。
        
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
                    self.server_socket.settimeout(Constants.SERVER_SOCKET_TIMEOUT)
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
    """本機 Proxy 中繼伺服器管理器。
    
    為每個瀏覽器建立獨立的本機 Proxy 埠,將請求轉發到上游 Proxy。
    採用執行緒安全和更好的資源管理。
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
        """啟動本機 Proxy 中繼伺服器。
        
        Args:
            upstream_proxy: 上游 Proxy 資訊
            
        Returns:
            本機埠號,失敗返回 None
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
                    self.logger.error(f"Proxy 伺服器執行失敗 埠 {local_port} {e}")
            
            server_thread = threading.Thread(target=run_server, daemon=True)
            server_thread.start()
            
            # 儲存實例和執行緒參考
            with self._lock:
                self._proxy_servers[local_port] = server
                self._proxy_threads[local_port] = server_thread
            
            # 等待伺服器啟動
            time.sleep(Constants.PROXY_SERVER_START_WAIT)
            
            self.logger.info(f"[成功] Proxy 中繼已啟動 (埠: {local_port})")
            return local_port
            
        except Exception as e:
            self.logger.error(f"啟動本機 Proxy 伺服器失敗 {e}")
            return None
    
    def stop_proxy_server(self, local_port: int) -> None:
        """停止指定的 proxy 伺服器（優化版）。
        
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
        """停止所有 proxy 伺服器（優化版）"""
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
        """上下文管理器退出,自動清理資源"""
        self.stop_all_servers()
        return False


# ============================================================================
# 瀏覽器管理器 (改進錯誤處理和資源管理)
# ============================================================================

class BrowserManager:
    """瀏覽器管理器。
    
    提供 WebDriver 建立和配置功能,支援自動和手動驅動程式管理。
    採用更好的錯誤處理和資源清理。
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """初始化瀏覽器管理器"""
        self.logger = logger or LoggerFactory.get_logger()
    
    @staticmethod
    def create_chrome_options(local_proxy_port: Optional[int] = None) -> Options:
        """建立 Chrome 瀏覽器選項。
        
        Args:
            local_proxy_port: 本機 proxy 中繼埠號（可選）
            
        Returns:
            Options: 配置好的 Chrome 選項
        """
        logger = LoggerFactory.get_logger()
        chrome_options = Options()
        
        # 本機 Proxy 設定
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
        # 移除: --disable-ipc-flooding-protection (可能導致通訊過載)
        
        # 網路效能優化設定
        # 移除: --dns-prefetch-disable (會降低 DNS 解析速度)
        # 移除: --disable-background-networking (會影響連線池管理)
        # 移除: --disable-features=NetworkTimeServiceQuerying (影響時間同步)
        
        # 啟用網路加速功能
        chrome_options.add_argument("--enable-features=NetworkService,NetworkServiceInProcess")
        chrome_options.add_argument("--enable-quic")  # 啟用 QUIC 協定加速
        chrome_options.add_argument("--enable-tcp-fast-open")  # TCP 快速開啟
        
        # 其他優化設定
        chrome_options.add_argument("--disable-sync")
        chrome_options.add_argument("--metrics-recording-only")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--disable-extensions")
        
        # 記憶體與渲染優化
        chrome_options.add_argument("--disk-cache-size=209715200")  # 200MB 磁碟快取
        chrome_options.add_argument("--media-cache-size=209715200")  # 200MB 媒體快取
        
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
            # 靜音設定（2 = 靜音，1 = 允許聲音）
            "profile.content_settings.exceptions.sound": {
                "*": {
                    "setting": 2
                }
            }
        })
        
        return chrome_options
    
    def create_webdriver(
        self, 
        local_proxy_port: Optional[int] = None
    ) -> WebDriver:
        """建立 WebDriver 實例（優化版）。
        
        優先使用 WebDriver Manager 自動管理驅動程式，
        若失敗則嘗試使用專案內的驅動程式檔案作為備援。
        
        Args:
            local_proxy_port: 本機 proxy 中繼埠號（可選）
            
        Returns:
            WebDriver: WebDriver 實例
            
        Raises:
            BrowserCreationError: 當所有方法都失敗時
        """
        chrome_options = self.create_chrome_options(local_proxy_port)
        driver = None
        errors = []
        
        # 方法 1: 優先使用 WebDriver Manager 自動管理
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
        except Exception as e:
            errors.append(f"WebDriver Manager: {e}")
            self.logger.warning(f"WebDriver Manager 失敗，嘗試使用本機驅動程式")
            
            # 方法 2: 使用專案內的驅動程式檔案作為備援
            try:
                driver = self._create_webdriver_with_local_driver(chrome_options)
                
            except FileNotFoundError as e2:
                errors.append(f"本機驅動程式: {e2}")
                self.logger.error(f"本機驅動程式不存在: {e2}")
            
            except Exception as e2:
                errors.append(f"本機驅動程式: {e2}")
                self.logger.error(f"本機驅動程式也失敗: {e2}")
        
        if driver is None:
            error_message = "無法建立瀏覽器實例。\n" + "\n".join(f"- {error}" for error in errors)
            raise BrowserCreationError(error_message)
        
        # 配置超時和優化
        self._configure_webdriver(driver)
        return driver
    
    def _configure_webdriver(self, driver: WebDriver) -> None:
        """配置 WebDriver 超時和優化設定。
        
        Args:
            driver: WebDriver 實例
        """
        # 設定超時
        with suppress(Exception):
            driver.set_page_load_timeout(Constants.DEFAULT_PAGE_LOAD_TIMEOUT)
            driver.set_script_timeout(Constants.DEFAULT_SCRIPT_TIMEOUT)
            driver.implicitly_wait(Constants.DEFAULT_IMPLICIT_WAIT)
        
        # 網路優化
        with suppress(Exception):
            driver.execute_cdp_cmd("Network.enable", {})
            driver.execute_cdp_cmd("Network.emulateNetworkConditions", {
                "offline": False,
                "downloadThroughput": -1,
                "uploadThroughput": -1,
                "latency": 0
            })
    
    def _create_webdriver_with_local_driver(self, chrome_options: Options) -> WebDriver:
        """使用專案內的驅動程式檔案建立 WebDriver。
        
        根據作業系統自動選擇正確的驅動程式檔案。
        
        Args:
            chrome_options: Chrome 選項
            
        Returns:
            WebDriver: WebDriver 實例
            
        Raises:
            FileNotFoundError: 驅動程式不存在
            BrowserCreationError: 無法啟動驅動程式
        """
        # 使用輔助函式取得專案根目錄
        project_root = get_resource_path()
        
        # 根據作業系統選擇驅動程式
        system = platform.system().lower()
        driver_filename = "chromedriver.exe" if system == "windows" else "chromedriver"
        
        driver_path = project_root / driver_filename
        
        if not driver_path.exists():
            raise FileNotFoundError(
                f"找不到驅動程式檔案\n"
                f"請確保 {driver_filename} 存在於專案根目錄"
            )
        
        # 確保驅動程式有執行權限 (Unix-like 系統)
        if system in ["darwin", "linux"]:
            import os
            with suppress(Exception):
                os.chmod(driver_path, 0o755)
        
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
        """建立瀏覽器上下文管理器。
        
        Args:
            credential: 使用者憑證
            index: 瀏覽器索引
            proxy_port: Proxy 埠號
            
        Yields:
            BrowserContext: 瀏覽器上下文
            
        Raises:
            BrowserCreationError: 建立失敗
        """
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


# ============================================================================
# 同步瀏覽器操作器 (改進執行緒池和錯誤處理)
# ============================================================================

class SyncBrowserOperator:
    """同步瀏覽器操作器。
    
    對多個瀏覽器實例同步執行相同的操作。
    使用執行緒池提升效能和資源管理。
    """
    
    def __init__(
        self,
        max_workers: Optional[int] = None,
        logger: Optional[logging.Logger] = None
    ):
        """初始化操作器。
        
        Args:
            max_workers: 最大工作執行緒數
            logger: 日誌記錄器
        """
        self.max_workers = max_workers or Constants.MAX_THREAD_WORKERS
        self.logger = logger or LoggerFactory.get_logger()
        self.last_canvas_rect: Optional[Dict[str, float]] = None  # Canvas 區域資訊
    
    def execute_sync(
        self,
        browser_contexts: List[BrowserContext],
        operation_func: Callable[[BrowserContext, int, int], Any],
        operation_name: str,
        timeout: Optional[float] = None
    ) -> List[OperationResult]:
        """同步執行操作到所有瀏覽器（優化版）。
        
        Args:
            browser_contexts: 瀏覽器上下文列表
            operation_func: 操作函式,接受參數 (context, index, total)
            operation_name: 操作名稱(用於日誌)
            timeout: 超時時間（秒）
            
        Returns:
            所有操作的結果列表
        """
        total = len(browser_contexts)
        results: List[OperationResult] = [OperationResult(False)] * total
        
        def is_browser_alive(driver: WebDriver) -> bool:
            """檢查瀏覽器是否仍然有效"""
            try:
                # 嘗試獲取當前 URL，如果瀏覽器已關閉會拋出異常
                _ = driver.current_url
                return True
            except Exception:
                return False
        
        def execute_operation(index: int, context: BrowserContext) -> Tuple[int, OperationResult]:
            """在執行緒中執行操作"""
            try:
                # 檢查瀏覽器是否仍然有效
                if not is_browser_alive(context.driver):
                    self.logger.warning(f"瀏覽器 {index+1}/{total} 已關閉，跳過 {operation_name}")
                    return index, OperationResult(
                        success=False,
                        message="瀏覽器已關閉"
                    )
                
                result_data = operation_func(context, index + 1, total)
                return index, OperationResult(
                    success=True,
                    data=result_data,
                    message=f"{operation_name} 成功"
                )
            except Exception as e:
                self.logger.error(f"瀏覽器 {index+1}/{total} {operation_name} 失敗: {e}")
                return index, OperationResult(
                    success=False,
                    error=e,
                    message=str(e)
                )
        
        # 使用執行緒池執行
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任務
            futures = [
                executor.submit(execute_operation, i, context)
                for i, context in enumerate(browser_contexts)
            ]
            
            # 收集結果
            try:
                for future in as_completed(futures, timeout=timeout):
                    index, result = future.result()
                    results[index] = result
            except TimeoutError:
                self.logger.error(f"{operation_name} 執行超時")
        
        success_count = sum(1 for r in results if r.success)
        if success_count < total:
            self.logger.warning(f"[警告] 部分操作未成功: {success_count}/{total}")
        
        return results
    
    def navigate_all(
        self,
        browser_contexts: List[BrowserContext],
        url: str,
        timeout: Optional[float] = None
    ) -> List[OperationResult]:
        """同步導航所有瀏覽器到指定 URL。
        
        Args:
            browser_contexts: 瀏覽器上下文列表
            url: 目標 URL
            timeout: 超時時間
            
        Returns:
            操作結果列表
        """
        def navigate_operation(context: BrowserContext, index: int, total: int) -> str:
            context.driver.get(url)
            return context.driver.current_url
        
        return self.execute_sync(
            browser_contexts,
            navigate_operation,
            f"導航到 {url}",
            timeout=timeout
        )
    
    def navigate_to_login_page(
        self,
        browser_contexts: List[BrowserContext],
        timeout: Optional[float] = None
    ) -> List[OperationResult]:
        """同步導航所有瀏覽器到登入頁面。
        
        Args:
            browser_contexts: 瀏覽器上下文列表
            timeout: 超時時間
            
        Returns:
            操作結果列表
        """
        return self.navigate_all(browser_contexts, Constants.LOGIN_PAGE, timeout)
    
    def navigate_to_game_page(
        self,
        browser_contexts: List[BrowserContext],
        timeout: Optional[float] = None
    ) -> List[OperationResult]:
        """同步導航所有瀏覽器到遊戲頁面，並點擊遊戲圖層。
        
        Args:
            browser_contexts: 瀏覽器上下文列表
            timeout: 超時時間
            
        Returns:
            操作結果列表
        """
        def game_page_operation(context: BrowserContext, index: int, total: int) -> bool:
            driver = context.driver
            
            try:
                # 1. 點擊搜尋按鈕
                search_btn = driver.find_element(By.XPATH, Constants.SEARCH_BUTTON)
                search_btn.click()
                time.sleep(1)  # 等待搜尋框出現
                
                # 2. 在搜尋框輸入「戰神」
                search_input = driver.find_element(By.XPATH, Constants.SEARCH_INPUT)
                search_input.clear()
                search_input.send_keys('戰神')
                
                # 3. 按下 Enter
                search_input.send_keys('\n')  # 發送換行鍵
                
                # 4. 等待 10 秒讓搜尋結果完全載入
                time.sleep(5)
                
                # 5. 點擊第一個遊戲圖層
                game_xpath = driver.find_element(By.XPATH, Constants.GAME_XPATH)
                game_xpath.click()
                time.sleep(5)  # 等待遊戲載入
                
                # 6. 等待 iframe 出現並切換進入
                time.sleep(2)  # 等待 iframe 載入
                iframe = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, Constants.GAME_IFRAME))
                )
                driver.switch_to.frame(iframe)
                self.logger.debug(f"瀏覽器 {index + 1} 已切換到遊戲 iframe")
                
                return True
            except Exception as e:
                self.logger.debug(f"進入遊戲流程失敗: {e}")
                return False
        
        return self.execute_sync(
            browser_contexts,
            game_page_operation,
            "進入遊戲頁面",
            timeout=timeout
        )
    
    def perform_login_all(
        self,
        browser_contexts: List[BrowserContext],
        timeout: Optional[float] = None
    ) -> List[OperationResult]:
        """同步執行所有瀏覽器的登入操作。
        
        Args:
            browser_contexts: 瀏覽器上下文列表
            timeout: 超時時間
            
        Returns:
            操作結果列表
        """
        def login_operation(context: BrowserContext, index: int, total: int) -> bool:
            driver = context.driver
            credential = context.credential
            
            # 確保登入表單已打開（最多重試3次）
            max_form_attempts = 3
            form_opened = False
            
            for attempt in range(1, max_form_attempts + 1):
                try:
                    # 1. 先檢查登入表單是否已經存在
                    # try:
                    #     popup = driver.find_element(By.CSS_SELECTOR, ".popup-wrap, .popup-account-container")
                    #     if popup.is_displayed():
                    #         self.logger.debug(f"[{credential.username}] 登入表單已存在，跳過點擊登入按鈕")
                    #         form_opened = True
                    #         break
                    #     else:
                    #         raise Exception("登入表單不可見")
                    # except Exception:
                    #     # 2. 登入表單不存在，點擊初始登入按鈕
                    #     if attempt > 1:
                    #         self.logger.warning(f"[{credential.username}] 第 {attempt} 次嘗試打開登入表單")
                    #     else:
                    #         self.logger.debug(f"[{credential.username}] 登入表單不存在，點擊初始登入按鈕")
                    
                    # 2.1 先等待 loading 遮罩層消失（避免點擊被攔截）
                    try:
                        WebDriverWait(driver, 10).until(
                            EC.invisibility_of_element_located((By.CSS_SELECTOR, ".loading-container"))
                        )
                        self.logger.debug(f"[{credential.username}] Loading 遮罩層已消失")
                    except Exception:
                        # 如果找不到 loading 元素，代表已經消失或不存在，繼續執行
                        self.logger.debug(f"[{credential.username}] 未檢測到 loading 遮罩層")
                    
                    # 2.2 等待登入按鈕可點擊
                    initial_login_btn = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, Constants.INITIAL_LOGIN_BUTTON))
                    )
                    
                    # 2.3 使用 JavaScript 點擊（更可靠，避免點擊攔截）
                    try:
                        driver.execute_script("arguments[0].click();", initial_login_btn)
                        self.logger.debug(f"[{credential.username}] 已點擊初始登入按鈕（使用 JavaScript）")
                    except Exception as js_err:
                        # JavaScript 點擊失敗，嘗試常規點擊
                        self.logger.debug(f"[{credential.username}] JavaScript 點擊失敗，嘗試常規點擊")
                        initial_login_btn.click()
                        self.logger.debug(f"[{credential.username}] 已點擊初始登入按鈕")
                    
                    time.sleep(2)  # 等待彈窗動畫
                    
                    # 3. 確認登入表單已完全載入且可見
                    popup = WebDriverWait(driver, 8).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, ".popup-wrap, .popup-account-container"))
                    )
                    self.logger.info(f"[{credential.username}] ✓ 登入表單已確認顯示")
                    form_opened = True
                    break
                    
                except Exception as e:
                    if attempt < max_form_attempts:
                        self.logger.warning(f"[{credential.username}] 第 {attempt} 次打開登入表單失敗: {e}，重試中...")
                        time.sleep(1)
                    else:
                        self.logger.error(f"[{credential.username}] 嘗試 {max_form_attempts} 次後仍無法打開登入表單")
                        return False
            
            if not form_opened:
                self.logger.error(f"[{credential.username}] 無法打開登入表單")
                return False
            
            try:
                # 4. 確認帳號輸入框可見且可互動
                username_input = WebDriverWait(driver, 15).until(
                    EC.visibility_of_element_located((By.XPATH, Constants.USERNAME_INPUT))
                )
                self.logger.debug(f"[{credential.username}] 帳號輸入框已就緒")
                time.sleep(1)  # 額外等待確保表單完全穩定
                
            except Exception as e:
                self.logger.error(f"[{credential.username}] 帳號輸入框未就緒: {e}")
                return False

            try:
                # 輸入帳號 - 等待元素可點擊
                username_input = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, Constants.USERNAME_INPUT))
                )
                username_input.clear()
                time.sleep(0.5)  # 清空後短暫等待
                username_input.send_keys(credential.username)
                self.logger.debug(f"[{credential.username}] 已輸入帳號")
                
                # 輸入密碼 - 等待元素可點擊
                password_input = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, Constants.PASSWORD_INPUT))
                )
                password_input.clear()
                time.sleep(0.5)  # 清空後短暫等待
                password_input.send_keys(credential.password)
                self.logger.debug(f"[{credential.username}] 已輸入密碼")
                
                # 點擊登入按鈕前先等待 loading 消失
                try:
                    WebDriverWait(driver, 10).until(
                        EC.invisibility_of_element_located((By.CSS_SELECTOR, ".loading-container"))
                    )
                    self.logger.debug(f"[{credential.username}] Loading 遮罩層已消失")
                except Exception:
                    self.logger.debug(f"[{credential.username}] 未檢測到 loading 遮罩層")
                
                # 點擊登入按鈕 - 使用 JavaScript 點擊避免被遮擋
                login_button = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, Constants.LOGIN_BUTTON))
                )
                try:
                    driver.execute_script("arguments[0].click();", login_button)
                    self.logger.info(f"[{credential.username}] 已點擊登入按鈕（使用 JavaScript），等待登入完成...")
                except Exception:
                    login_button.click()
                    self.logger.info(f"[{credential.username}] 已點擊登入按鈕，等待登入完成...")
                
                time.sleep(Constants.LOGIN_WAIT_TIME)  # 等待登入完成
                
                # 登入後直接強制關閉所有彈窗（公告、廣告等）
                self.logger.debug(f"[{credential.username}] 開始關閉登入後的公告彈窗...")
                time.sleep(2)  # 等待公告彈窗可能出現
                
                try:
                    # 使用 JavaScript 強制隱藏所有彈窗
                    driver.execute_script("""
                        const popups = document.querySelectorAll('.popup-container, .popup-wrap, .popup-account-container');
                        popups.forEach(popup => {
                            popup.style.display = 'none';
                            popup.style.visibility = 'hidden';
                            popup.remove();
                        });
                        
                        // 移除遮罩層
                        const overlays = document.querySelectorAll('[class*="overlay"], [class*="mask"]');
                        overlays.forEach(overlay => overlay.remove());
                    """)
                    self.logger.info(f"[{credential.username}] ✓ 已關閉所有公告彈窗")
                except Exception as e:
                    self.logger.debug(f"[{credential.username}] 關閉公告彈窗時發生錯誤（可忽略）: {e}")
                    
            except Exception as e:
                self.logger.error(f"[{credential.username}] 登入過程中發生錯誤: {e}")
                return False
            
            # 使用 JavaScript 直接隱藏所有廣告彈窗
            try:
                driver.execute_script("""
                    // 隱藏所有彈窗容器
                    const popups = document.querySelectorAll('.popup-container, .popup-wrap');
                    popups.forEach(popup => {
                        popup.style.display = 'none';
                        popup.style.visibility = 'hidden';
                    });
                    
                    // 移除遮罩層（如果有）
                    const overlays = document.querySelectorAll('[class*="overlay"], [class*="mask"]');
                    overlays.forEach(overlay => overlay.remove());
                """)
                self.logger.debug("已隱藏所有廣告彈窗")
            except Exception as e:
                self.logger.debug(f"隱藏廣告彈窗時發生錯誤: {e}")
            
            # 針對 richpanda 網站的廣告彈窗處理
            if "richpanda" in Constants.LOGIN_PAGE:
                try:
                    # 檢查廣告容器和關閉按鈕是否都存在
                    ads_container = driver.find_elements(By.CSS_SELECTOR, "div.ads-container.pc")
                    close_button = driver.find_elements(By.CSS_SELECTOR, "button.close-btn-container.btn-close")
                    
                    if ads_container and close_button:
                        # 廣告和關閉按鈕都存在，點擊關閉按鈕
                        try:
                            driver.execute_script("arguments[0].click();", close_button[0])
                            self.logger.info(f"[{credential.username}] ✓ 已關閉 richpanda 廣告彈窗")
                        except Exception:
                            close_button[0].click()
                            self.logger.info(f"[{credential.username}] ✓ 已關閉 richpanda 廣告彈窗")
                        time.sleep(0.5)  # 等待關閉動畫
                    else:
                        self.logger.debug(f"[{credential.username}] 未檢測到 richpanda 廣告彈窗")
                except Exception as e:
                    self.logger.debug(f"[{credential.username}] 處理 richpanda 廣告彈窗時發生錯誤: {e}")
            
            return True
        
        return self.execute_sync(
            browser_contexts,
            login_operation,
            "登入操作",
            timeout=timeout
        )
    
    def press_space_all(
        self,
        browser_contexts: List[BrowserContext],
        timeout: Optional[float] = None
    ) -> List[OperationResult]:
        """同步在所有瀏覽器中按下空白鍵。
        
        Args:
            browser_contexts: 瀏覽器上下文列表
            timeout: 超時時間
            
        Returns:
            操作結果列表
        """
        def press_space_operation(context: BrowserContext, index: int, total: int) -> bool:
            BrowserHelper.execute_cdp_space_key(context.driver)
            return True
        
        return self.execute_sync(
            browser_contexts,
            press_space_operation,
            "按下空白鍵",
            timeout=timeout
        )
    
    def buy_free_game_single(
        self,
        context: BrowserContext,
        canvas_rect: Dict[str, float],
        free_game_type: int = 1
    ) -> bool:
        """在單個瀏覽器中購買免費遊戲。
        
        Args:
            context: 瀏覽器上下文
            canvas_rect: Canvas 區域資訊 {"x", "y", "w", "h"}
            free_game_type: 免費遊戲類別 (1=only_freegame, 2=awake_power, 3=immortal_awake)
            
        Returns:
            是否成功
        """
        try:
            username = context.credential.username
            driver = context.driver
            
            # === 第一次點擊（免費遊戲區域） ===
            freegame_x, freegame_y = BrowserHelper.calculate_click_position(
                canvas_rect,
                Constants.BUY_FREE_GAME_BUTTON_X_RATIO,
                Constants.BUY_FREE_GAME_BUTTON_Y_RATIO
            )
            
            self.logger.info(f"[{username}] 點擊免費遊戲區域 ({freegame_x:.1f}, {freegame_y:.1f})...")
            BrowserHelper.execute_cdp_click(driver, freegame_x, freegame_y)
            time.sleep(Constants.FREE_GAME_CLICK_WAIT)
            
            # === 第二次點擊（確認按鈕） ===
            # 根據類別選擇座標
            if free_game_type == 3:
                # 不朽覺醒類別
                confirm_x_ratio = Constants.BUY_FREE_GAME_IMMORTAL_AWAKE_X_RATIO
                confirm_y_ratio = Constants.BUY_FREE_GAME_IMMORTAL_AWAKE_Y_RATIO
                type_name = "不朽覺醒"
            elif free_game_type == 2:
                # 覺醒之力類別
                confirm_x_ratio = Constants.BUY_FREE_GAME_AWAKE_POWER_X_RATIO
                confirm_y_ratio = Constants.BUY_FREE_GAME_AWAKE_POWER_Y_RATIO
                type_name = "覺醒之力"
            else:
                # 免費遊戲類別 (預設)
                confirm_x_ratio = Constants.BUY_FREE_GAME_ONLY_FREEGAME_X_RATIO
                confirm_y_ratio = Constants.BUY_FREE_GAME_ONLY_FREEGAME_Y_RATIO
                type_name = "免費遊戲"
            
            confirm_x, confirm_y = BrowserHelper.calculate_click_position(
                canvas_rect,
                confirm_x_ratio,
                confirm_y_ratio
            )
            
            self.logger.info(f"[{username}] 點擊確認按鈕 [{type_name}] ({confirm_x:.1f}, {confirm_y:.1f})...")
            BrowserHelper.execute_cdp_click(driver, confirm_x, confirm_y)
            
            # === 購買完成後等待並自動按空白鍵 ===
            self.logger.info(f"[{username}] 購買完成，等待 {Constants.BUY_FREE_GAME_WAIT_SECONDS} 秒後開始遊戲...")
            time.sleep(Constants.BUY_FREE_GAME_WAIT_SECONDS)
            
            self.logger.info(f"[{username}] 按下空白鍵開始遊戲...")
            BrowserHelper.execute_cdp_space_key(driver)
            
            self.logger.info(f"[{username}] 免費遊戲購買流程完成！")
            return True
            
        except Exception as e:
            self.logger.error(f"[{username}] 購買免費遊戲失敗：{e}")
            return False
    
    def buy_free_game_all(
        self,
        browser_contexts: List[BrowserContext],
        canvas_rect: Dict[str, float],
        free_game_type: int = 1,
        timeout: Optional[float] = None
    ) -> List[OperationResult]:
        """同步在所有瀏覽器中購買免費遊戲。
        
        Args:
            browser_contexts: 瀏覽器上下文列表
            canvas_rect: Canvas 區域資訊
            free_game_type: 免費遊戲類別 (1=only_freegame, 2=awake_power, 3=immortal_awake)
            timeout: 超時時間
            
        Returns:
            操作結果列表
        """
        def buy_operation(context: BrowserContext, index: int, total: int) -> bool:
            """購買免費遊戲操作"""
            username = context.credential.username
            driver = context.driver
            
            try:
                # === 第一次點擊（免費遊戲區域） ===
                freegame_x, freegame_y = BrowserHelper.calculate_click_position(
                    canvas_rect,
                    Constants.BUY_FREE_GAME_BUTTON_X_RATIO,
                    Constants.BUY_FREE_GAME_BUTTON_Y_RATIO
                )
                
                BrowserHelper.execute_cdp_click(driver, freegame_x, freegame_y)
                time.sleep(Constants.FREE_GAME_CLICK_WAIT)
                
                # === 第二次點擊（確認按鈕） ===
                # 根據類別選擇座標
                if free_game_type == 3:
                    # immortal_awake 類別
                    confirm_x_ratio = Constants.BUY_FREE_GAME_IMMORTAL_AWAKE_X_RATIO
                    confirm_y_ratio = Constants.BUY_FREE_GAME_IMMORTAL_AWAKE_Y_RATIO
                elif free_game_type == 2:
                    # awake_power 類別
                    confirm_x_ratio = Constants.BUY_FREE_GAME_AWAKE_POWER_X_RATIO
                    confirm_y_ratio = Constants.BUY_FREE_GAME_AWAKE_POWER_Y_RATIO
                else:
                    # only_freegame 類別 (預設)
                    confirm_x_ratio = Constants.BUY_FREE_GAME_ONLY_FREEGAME_X_RATIO
                    confirm_y_ratio = Constants.BUY_FREE_GAME_ONLY_FREEGAME_Y_RATIO
                
                confirm_x, confirm_y = BrowserHelper.calculate_click_position(
                    canvas_rect,
                    confirm_x_ratio,
                    confirm_y_ratio
                )
                
                BrowserHelper.execute_cdp_click(driver, confirm_x, confirm_y)
                
                # === 購買完成後等待並自動按空白鍵 ===
                time.sleep(Constants.BUY_FREE_GAME_WAIT_SECONDS)
                BrowserHelper.execute_cdp_space_key(driver)
                
                return True
                
            except Exception as e:
                self.logger.error(f"[{username}] 購買失敗: {e}")
                return False
        
        return self.execute_sync(
            browser_contexts,
            buy_operation,
            "購買免費遊戲",
            timeout
        )
    
    def resize_and_arrange_all(
        self,
        browser_contexts: List[BrowserContext],
        width: int = Constants.DEFAULT_WINDOW_WIDTH,
        height: int = Constants.DEFAULT_WINDOW_HEIGHT,
        columns: int = Constants.DEFAULT_WINDOW_COLUMNS,
        timeout: Optional[float] = None
    ) -> List[OperationResult]:
        """調整所有瀏覽器視窗大小並進行排列。
        
        Args:
            browser_contexts: 瀏覽器上下文列表
            width: 視窗寬度
            height: 視窗高度
            columns: 每行視窗數量（預設4列）
            timeout: 超時時間
            
        Returns:
            操作結果列表
        """
        def resize_and_position_operation(context: BrowserContext, index: int, total: int) -> bool:
            # 計算視窗位置 (4x3 排列)
            row = (index - 1) // columns
            col = (index - 1) % columns
            
            x = col * width
            y = row * height
            
            # 調整視窗大小和位置
            context.driver.set_window_size(width, height)
            context.driver.set_window_position(x, y)
            return True
        
        return self.execute_sync(
            browser_contexts,
            resize_and_position_operation,
            f"調整視窗大小為 {width}x{height} 並進行 {columns}列排列",
            timeout=timeout
        )
    
    def close_all(
        self,
        browser_contexts: List[BrowserContext],
        timeout: Optional[float] = None
    ) -> List[OperationResult]:
        """同步關閉所有瀏覽器。
        
        Args:
            browser_contexts: 瀏覽器上下文列表
            timeout: 超時時間
            
        Returns:
            操作結果列表
        """
        def close_operation(context: BrowserContext, index: int, total: int) -> bool:
            context.driver.quit()
            return True
        
        return self.execute_sync(
            browser_contexts,
            close_operation,
            "關閉瀏覽器",
            timeout=timeout
        )
    
    def adjust_betsize_all(
        self,
        browser_contexts: List[BrowserContext],
        target_amount: float,
        timeout: Optional[float] = None,
        silent: bool = False,
        stop_event: Optional[threading.Event] = None
    ) -> List[OperationResult]:
        """同步調整所有瀏覽器的下注金額（無限等待版）。
        
        所有瀏覽器會無限等待直到金額調整完成，才會一起進入下一個動作。
        
        Args:
            browser_contexts: 瀏覽器上下文列表
            target_amount: 目標金額
            timeout: 已棄用，保留參數以維持向後相容
            silent: 是否靜默模式（不輸出詳細日誌）
            stop_event: 可選的停止事件，用於控制中斷操作
            
        Returns:
            操作結果列表
        """
        def adjust_operation(context: BrowserContext, index: int, total: int) -> bool:
            return self.adjust_betsize(context.driver, target_amount, silent=silent, stop_event=stop_event)
        
        results = self.execute_sync(
            browser_contexts,
            adjust_operation,
            f"調整下注金額到 {target_amount}",
            timeout=None  # 無超時限制
        )
        
        return results
    
    def get_current_betsize(self, driver: WebDriver, retry_count: int = None, silent: bool = False) -> Optional[float]:
        """取得當前下注金額（優化版）。
        
        Args:
            driver: WebDriver 實例
            retry_count: 重試次數（預設使用常數）
            silent: 是否靜默模式（不輸出詳細日誌）
            
        Returns:
            Optional[float]: 當前金額，失敗返回None
        """
        if retry_count is None:
            retry_count = Constants.BETSIZE_READ_MAX_RETRIES
        
        for attempt in range(retry_count):
            try:
                if attempt > 0:
                    time.sleep(Constants.BETSIZE_READ_RETRY_WAIT)  # 等待畫面穩定
                
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
                                self.logger.info(f"[成功] 目前金額: {amount_value}")
                            return amount_value
                    except ValueError:
                        pass
                
            except Exception as e:
                self.logger.error(f"查詢下注金額時發生錯誤: {e}")
        
        return None
    
    def _compare_betsize_images(self, screenshot_gray: np.ndarray) -> Tuple[Optional[str], float]:
        """使用 bet_size 資料夾中的圖片比對（優化版）。
        
        Args:
            screenshot_gray: 截圖（灰階）
            
        Returns:
            Tuple[Optional[str], float]: (匹配的金額, 信心度)
        """
        try:
            # 使用輔助函式取得專案根目錄
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
    
    def _click_betsize_button(self, driver: WebDriver, x_ratio: float, y_ratio: float) -> None:
        """點擊下注金額調整按鈕。
        
        Args:
            driver: WebDriver 實例
            x_ratio: X 座標比例 (0-1)
            y_ratio: Y 座標比例 (0-1)
        """
        # 截取畫面獲取實際尺寸
        screenshot = driver.get_screenshot_as_png()
        screenshot_img = Image.open(io.BytesIO(screenshot))
        image_width, image_height = screenshot_img.size
        
        # 使用比例計算實際座標
        actual_x = int(image_width * x_ratio)
        actual_y = int(image_height * y_ratio)
        
        # 執行點擊
        BrowserHelper.execute_cdp_click(driver, actual_x, actual_y)
    
    def adjust_betsize(self, driver: WebDriver, target_amount: float, max_attempts: int = None, silent: bool = False, stop_event: Optional[threading.Event] = None) -> bool:
        """調整下注金額到目標值（無限等待版）。
        
        Args:
            driver: WebDriver 實例
            target_amount: 目標金額
            max_attempts: 已棄用，保留參數以維持向後相容
            silent: 是否靜默模式（不輸出詳細日誌）
            stop_event: 可選的停止事件，用於控制中斷操作
            
        Returns:
            bool: 調整成功返回True，被中斷返回False
        """
        try:
            # 檢查目標金額
            if target_amount not in Constants.GAME_BETSIZE:
                if not silent:
                    self.logger.error(f"目標金額 {target_amount} 不在可用金額列表中")
                return False
            
            # 無限等待直到成功取得當前金額
            attempt = 0
            current_amount = None
            while current_amount is None:
                # 檢查停止事件
                if stop_event is not None and stop_event.is_set():
                    if not silent:
                        self.logger.info("[中斷] 金額調整已被停止")
                    return False
                
                current_amount = self.get_current_betsize(driver, silent=silent)
                if current_amount is None:
                    attempt += 1
                    if attempt == 1 or attempt % 20 == 0:
                        self.logger.warning(f"[警告] 無法識別目前金額，持續等待中... (嘗試 {attempt} 次)")
                    time.sleep(Constants.BETSIZE_ADJUST_RETRY_WAIT)
            
            # 檢查是否已是目標金額
            if current_amount == target_amount:
                if not silent:
                    self.logger.info("[成功] 金額已符合目標")
                return True
            
            # 計算需要調整的方向
            current_index = Constants.GAME_BETSIZE_TUPLE.index(current_amount)
            target_index = Constants.GAME_BETSIZE_TUPLE.index(target_amount)
            diff = target_index - current_index
            
            # 設定點擊座標比例
            if diff > 0:
                # 需要增加金額
                click_x_ratio = Constants.BETSIZE_INCREASE_BUTTON_X
                click_y_ratio = Constants.BETSIZE_INCREASE_BUTTON_Y
                direction = "增加"
            else:
                # 需要減少金額
                click_x_ratio = Constants.BETSIZE_DECREASE_BUTTON_X
                click_y_ratio = Constants.BETSIZE_DECREASE_BUTTON_Y
                direction = "減少"
            
            # 無限循環調整，直到達到目標金額
            attempt = 0
            while True:
                # 檢查停止事件
                if stop_event is not None and stop_event.is_set():
                    if not silent:
                        self.logger.info("[中斷] 金額調整已被停止")
                    return False
                
                attempt += 1
                
                # 先檢查當前金額
                current_amount = self.get_current_betsize(driver, silent=silent)
                
                if current_amount is None:
                    # 記錄金額識別失敗
                    if attempt % 20 == 0:
                        self.logger.warning(f"[警告] 金額識別失敗，持續等待中... (嘗試 {attempt} 次)")
                    time.sleep(Constants.BETSIZE_ADJUST_RETRY_WAIT)
                    continue
                
                # 檢查是否已達目標
                if current_amount == target_amount:
                    if not silent:
                        self.logger.info(f"[成功] 金額調整完成: {current_amount}")
                    return True
                
                # 未達目標，點擊一次調整按鈕
                self._click_betsize_button(driver, click_x_ratio, click_y_ratio)
                
                # 等待畫面更新
                time.sleep(Constants.BETSIZE_ADJUST_STEP_WAIT)
            
        except Exception as e:
            if not silent:
                self.logger.error(f"[錯誤] 調整過程發生錯誤: {e}")
            # 檢查停止事件
            if stop_event is not None and stop_event.is_set():
                return False
            # 發生異常時等待後重試
            time.sleep(1)
            return self.adjust_betsize(driver, target_amount, silent=silent, stop_event=stop_event)
    
    def capture_betsize_template(self, driver: WebDriver, amount: float) -> bool:
        """截取下注金額模板。
        
        Args:
            driver: WebDriver 實例
            amount: 下注金額
            
        Returns:
            bool: 截取成功返回True
        """
        try:
            # 固定座標比例：金額顯示位置
            target_x_ratio = Constants.BETSIZE_DISPLAY_X
            target_y_ratio = Constants.BETSIZE_DISPLAY_Y
            
            # 截取整個瀏覽器畫面
            screenshot = driver.get_screenshot_as_png()
            screenshot_img = Image.open(io.BytesIO(screenshot))
            
            # 獲取實際截圖尺寸
            image_width, image_height = screenshot_img.size
            
            # 使用比例計算實際座標
            actual_x = int(image_width * target_x_ratio)
            actual_y = int(image_height * target_y_ratio)
            
            # 裁切範圍（使用常數定義）
            crop_left = max(0, actual_x - Constants.BETSIZE_CROP_MARGIN_X)
            crop_top = max(0, actual_y - Constants.BETSIZE_CROP_MARGIN_Y)
            crop_right = min(image_width, actual_x + Constants.BETSIZE_CROP_MARGIN_X)
            crop_bottom = min(image_height, actual_y + Constants.BETSIZE_CROP_MARGIN_Y)
            
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
            
            self.logger.info(f"[成功] 模板已儲存: {filename}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"截取金額模板失敗: {e}")
            return False

    def capture_blackscreen_template(self, driver: WebDriver) -> bool:
        """截取黑屏區域模板。
        
        使用 Constants 定義的座標和裁切範圍。
        
        Args:
            driver: WebDriver 實例
            
        Returns:
            bool: 截取成功返回True
        """
        try:
            # 使用常數定義：黑屏中心位置和裁切邊距
            center_x = Constants.BLACKSCREEN_CENTER_X
            center_y = Constants.BLACKSCREEN_CENTER_Y
            margin_x = Constants.BLACKSCREEN_CROP_MARGIN_X  # 左右邊距
            margin_y = Constants.BLACKSCREEN_CROP_MARGIN_Y  # 上下邊距
            
            # 截取整個瀏覽器畫面
            screenshot = driver.get_screenshot_as_png()
            screenshot_img = Image.open(io.BytesIO(screenshot))
            
            # 獲取實際截圖尺寸
            image_width, image_height = screenshot_img.size
            
            # 計算裁切範圍（左右使用 margin_x，上下使用 margin_y）
            crop_left = max(0, center_x - margin_x)
            crop_top = max(0, center_y - margin_y)
            crop_right = min(image_width, center_x + margin_x)
            crop_bottom = min(image_height, center_y + margin_y)
            
            # 裁切圖片
            cropped_img = screenshot_img.crop((crop_left, crop_top, crop_right, crop_bottom))
            
            # 使用輔助函式取得專案根目錄
            img_dir = get_resource_path("img")
            img_dir.mkdir(parents=True, exist_ok=True)
            
            # 固定檔名
            filename = "black_screen.png"
            output_path = img_dir / filename
            cropped_img.save(output_path)
            
            self.logger.info(f"[成功] 黑屏模板已儲存: {filename} (座標: {center_x},{center_y}, 範圍: 左右{margin_x}px 上下{margin_y}px)")
            
            return True
            
        except Exception as e:
            self.logger.error(f"截取黑屏模板失敗: {e}")
            return False

    def capture_game_return_template(self, driver: WebDriver) -> bool:
        """截取返回遊戲提示區域模板。
        
        使用 Constants 定義的座標和裁切範圍。
        
        Args:
            driver: WebDriver 實例
            
        Returns:
            bool: 截取成功返回True
        """
        try:
            # 使用常數定義：返回遊戲提示中心位置和裁切邊距
            center_x = Constants.GAME_RETURN_CENTER_X
            center_y = Constants.GAME_RETURN_CENTER_Y
            margin_x = Constants.GAME_RETURN_CROP_MARGIN_X  # 左右邊距
            margin_y = Constants.GAME_RETURN_CROP_MARGIN_Y  # 上下邊距
            
            # 截取整個瀏覽器畫面
            screenshot = driver.get_screenshot_as_png()
            screenshot_img = Image.open(io.BytesIO(screenshot))
            
            # 獲取實際截圖尺寸
            image_width, image_height = screenshot_img.size
            
            # 計算裁切範圍（左右使用 margin_x，上下使用 margin_y）
            crop_left = max(0, center_x - margin_x)
            crop_top = max(0, center_y - margin_y)
            crop_right = min(image_width, center_x + margin_x)
            crop_bottom = min(image_height, center_y + margin_y)
            
            # 裁切圖片
            cropped_img = screenshot_img.crop((crop_left, crop_top, crop_right, crop_bottom))
            
            # 使用輔助函式取得專案根目錄
            img_dir = get_resource_path("img")
            img_dir.mkdir(parents=True, exist_ok=True)
            
            # 固定檔名
            filename = "game_return.png"
            output_path = img_dir / filename
            cropped_img.save(output_path)
            
            self.logger.info(f"[成功] 返回遊戲提示模板已儲存: {filename} (座標: {center_x},{center_y}, 範圍: 左右{margin_x}px 上下{margin_y}px)")
            
            return True
            
        except Exception as e:
            self.logger.error(f"截取返回遊戲提示模板失敗: {e}")
            return False

    def capture_lobby_return_template(self, driver: WebDriver) -> bool:
        """截取大廳返回提示模板。
        
        參考 lobby_login 的方式，截取整個瀏覽器畫面（不裁切）。
        
        Args:
            driver: WebDriver 實例
            
        Returns:
            bool: 截取成功返回True
        """
        try:
            # 使用輔助函式取得專案根目錄
            img_dir = get_resource_path("img")
            img_dir.mkdir(parents=True, exist_ok=True)
            
            # 固定檔名
            filename = "lobby_return.png"
            output_path = img_dir / filename
            
            # 截取整個瀏覽器畫面（與 lobby_login 相同方式）
            screenshot = driver.get_screenshot_as_png()
            screenshot_img = Image.open(io.BytesIO(screenshot))
            
            # 直接儲存完整截圖（不裁切）
            screenshot_img.save(output_path)
            
            self.logger.info(f"[成功] 大廳返回提示模板已儲存: {filename} (完整瀏覽器截圖)")
            
            return True
            
        except Exception as e:
            self.logger.error(f"截取大廳返回提示模板失敗: {e}")
            return False


# ============================================================================
# 瀏覽器操作輔助類
# ============================================================================

class BrowserHelper:
    """瀏覽器操作輔助類別。
    
    提供常用的瀏覽器操作方法，避免程式碼重複。
    包括 CDP 點擊、座標計算、按鍵模擬等。
    """
    
    @staticmethod
    def execute_cdp_click(driver: WebDriver, x: float, y: float) -> None:
        """使用 Chrome DevTools Protocol 執行點擊操作。
        
        Args:
            driver: WebDriver 實例
            x: X 座標
            y: Y 座標
        """
        for event_type in ["mousePressed", "mouseReleased"]:
            driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
                "type": event_type,
                "x": x,
                "y": y,
                "button": "left",
                "clickCount": 1
            })
    
    @staticmethod
    def execute_cdp_space_key(driver: WebDriver) -> None:
        """使用 Chrome DevTools Protocol 按下空白鍵。
        
        Args:
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
    def calculate_click_position(
        canvas_rect: Dict[str, float],
        x_ratio: float,
        y_ratio: float
    ) -> Tuple[float, float]:
        """根據 Canvas 區域和比例計算點擊座標。
        
        Args:
            canvas_rect: Canvas 區域資訊 {"x", "y", "w", "h"}
            x_ratio: X 座標比例
            y_ratio: Y 座標比例
            
        Returns:
            (x, y) 實際座標
        """
        x = canvas_rect["x"] + canvas_rect["w"] * x_ratio
        y = canvas_rect["y"] + canvas_rect["h"] * y_ratio
        return x, y
    
    @staticmethod
    def calculate_scaled_position(
        base_x: float,
        base_y: float,
        screenshot_width: int,
        screenshot_height: int,
        base_width: int = Constants.DEFAULT_WINDOW_WIDTH,
        base_height: int = Constants.DEFAULT_WINDOW_HEIGHT
    ) -> Tuple[int, int]:
        """根據視窗大小計算縮放後的座標。
        
        Args:
            base_x: 基準 X 座標（基於預設視窗大小）
            base_y: 基準 Y 座標（基於預設視窗大小）
            screenshot_width: 實際截圖寬度
            screenshot_height: 實際截圖高度
            base_width: 基準視窗寬度
            base_height: 基準視窗高度
            
        Returns:
            (actual_x, actual_y) 實際座標
        """
        x_ratio = base_x / base_width
        y_ratio = base_y / base_height
        actual_x = int(screenshot_width * x_ratio)
        actual_y = int(screenshot_height * y_ratio)
        return actual_x, actual_y


# ============================================================================
# 圖片檢測器
# ============================================================================

class ImageDetector:
    """圖片檢測器。
    
    提供螢幕截圖、圖片比對和座標定位功能。
    使用 OpenCV 進行模板匹配，支援多種圖片格式。
    
    Attributes:
        logger: 日誌記錄器
        project_root: 專案根目錄
        image_dir: 圖片目錄
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """初始化圖片檢測器"""
        self.logger = logger or LoggerFactory.get_logger()
        
        # 使用輔助函式取得專案根目錄和圖片目錄
        self.project_root = get_resource_path()
        self.image_dir = get_resource_path(Constants.IMAGE_DIR)
        
        # 確保圖片目錄存在
        self.image_dir.mkdir(parents=True, exist_ok=True)
    
    def get_template_path(self, template_name: str) -> Path:
        """取得模板圖片路徑。
        
        Args:
            template_name: 模板圖片檔名
            
        Returns:
            模板圖片完整路徑
        """
        return self.image_dir / template_name
    
    def template_exists(self, template_name: str) -> bool:
        """檢查模板圖片是否存在。
        
        Args:
            template_name: 模板圖片檔名
            
        Returns:
            是否存在
        """
        return self.get_template_path(template_name).exists()
    
    def capture_screenshot(self, driver: WebDriver, save_path: Optional[Path] = None) -> np.ndarray:
        """截取瀏覽器畫面。
        
        Args:
            driver: WebDriver 實例
            save_path: 儲存路徑（可選）
            
        Returns:
            OpenCV 格式的圖片陣列 (BGR)
            
        Raises:
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
                # cv2.imwrite 無法處理中文路徑，改用 imencode + 檔案寫入
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
    
    def match_template(self, screenshot: np.ndarray, template_path: Path, threshold: float = Constants.MATCH_THRESHOLD) -> Optional[Tuple[int, int, float]]:
        """在截圖中尋找模板圖片。
        
        Args:
            screenshot: 截圖（OpenCV 格式）
            template_path: 模板圖片路徑
            threshold: 匹配閾值（0-1）
            
        Returns:
            如果找到: (x, y, confidence) - 中心座標和信心度
            如果未找到: None
            
        Raises:
            ImageDetectionError: 檢測失敗
        """
        try:
            if not template_path.exists():
                raise FileNotFoundError(f"模板圖片不存在: {template_path}")
            
            # 讀取模板圖片（使用支援 Unicode 路徑的函式，解決中文路徑問題）
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
    
    def detect_in_browser(self, driver: WebDriver, template_name: str, threshold: float = Constants.MATCH_THRESHOLD) -> Optional[Tuple[int, int, float]]:
        """在瀏覽器中檢測模板圖片。
        
        Args:
            driver: WebDriver 實例
            template_name: 模板圖片檔名
            threshold: 匹配閾值
            
        Returns:
            如果找到: (x, y, confidence)
            如果未找到: None
        """
        try:
            # 檢查瀏覽器是否仍然有效
            try:
                _ = driver.current_url
            except Exception:
                self.logger.warning(f"瀏覽器已關閉，無法進行圖片檢測")
                return None
            
            screenshot = self.capture_screenshot(driver)
            template_path = self.get_template_path(template_name)
            return self.match_template(screenshot, template_path, threshold)
        except Exception as e:
            self.logger.error(f"瀏覽器圖片檢測失敗 {e}")
            return None
    
    def detect_black_screen(
        self, 
        driver: WebDriver,
        threshold: float = Constants.MATCH_THRESHOLD
    ) -> bool:
        """檢測指定區域是否出現黑屏。
        
        Args:
            driver: WebDriver 實例
            threshold: 匹配閾值
            
        Returns:
            是否檢測到黑屏
        """
        try:
            # 截取全螢幕
            screenshot = self.capture_screenshot(driver)
            if screenshot is None:
                return False
            
            # 獲取截圖尺寸
            height, width = screenshot.shape[:2]
            
            # 使用常數定義的座標和邊距
            center_x = Constants.BLACKSCREEN_CENTER_X
            center_y = Constants.BLACKSCREEN_CENTER_Y
            margin_x = Constants.BLACKSCREEN_CROP_MARGIN_X
            margin_y = Constants.BLACKSCREEN_CROP_MARGIN_Y
            
            # 計算裁切範圍
            crop_left = max(0, center_x - margin_x)
            crop_top = max(0, center_y - margin_y)
            crop_right = min(width, center_x + margin_x)
            crop_bottom = min(height, center_y + margin_y)
            
            # 裁切區域
            cropped = screenshot[crop_top:crop_bottom, crop_left:crop_right]
            
            # 讀取黑屏模板
            template_path = self.get_template_path(Constants.BLACK_SCREEN)
            if not template_path.exists():
                self.logger.debug(f"黑屏模板不存在: {template_path}")
                return False
            
            template = cv2_imread_unicode(template_path)
            if template is None:
                self.logger.debug("無法讀取黑屏模板")
                return False
            
            # 轉換為灰階
            cropped_gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            
            # 模板匹配
            result = cv2.matchTemplate(cropped_gray, template_gray, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(result)
            
            return max_val >= threshold
            
        except Exception as e:
            self.logger.debug(f"黑屏檢測失敗: {e}")
            return False


# ============================================================================
# 瀏覽器恢復管理器
# ============================================================================

class BrowserRecoveryManager:
    """瀏覽器恢復管理器。
    
    負責處理瀏覽器錯誤檢測、自動重啟等恢復操作。
    提供模組化的錯誤處理流程。
    """
    
    def __init__(
        self,
        image_detector: 'ImageDetector',
        browser_operator: 'SyncBrowserOperator',
        logger: Optional[logging.Logger] = None
    ):
        """初始化恢復管理器。
        
        Args:
            image_detector: 圖片檢測器
            browser_operator: 瀏覽器操作器
            logger: 日誌記錄器
        """
        self.image_detector = image_detector
        self.browser_operator = browser_operator
        self.logger = logger or LoggerFactory.get_logger()
    
    def detect_black_screen(self, driver: WebDriver) -> bool:
        """檢測瀏覽器中是否出現黑屏。
        
        Args:
            driver: WebDriver 實例
            
        Returns:
            是否檢測到黑屏
        """
        try:
            return self.image_detector.detect_black_screen(driver)
        except Exception as e:
            self.logger.debug(f"黑屏檢測失敗: {e}")
            return False
    
    def _check_region(
        self,
        screenshot: np.ndarray,
        template: np.ndarray,
        x: int,
        y: int,
        region_name: str
    ) -> Tuple[float, bool]:
        """檢查指定區域的匹配值。
        
        Args:
            screenshot: 螢幕截圖
            template: 模板圖片
            x: X 座標
            y: Y 座標
            region_name: 區域名稱
            
        Returns:
            (匹配值, 是否匹配)
        """
        try:
            height, width = screenshot.shape[:2]
            margin = Constants.TEMPLATE_CROP_MARGIN
            threshold = Constants.MATCH_THRESHOLD
            
            # 計算裁切範圍
            crop_left = max(0, x - margin)
            crop_top = max(0, y - margin)
            crop_right = min(width, x + margin)
            crop_bottom = min(height, y + margin)
            
            # 裁切區域
            cropped = screenshot[crop_top:crop_bottom, crop_left:crop_right]
            
            # 轉換為灰階
            cropped_gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            
            # 模板匹配
            result = cv2.matchTemplate(cropped_gray, template_gray, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(result)
            
            return (max_val, max_val >= threshold)
            
        except Exception as e:
            self.logger.debug(f"{region_name}區域檢測失敗: {e}")
            return (0.0, False)
    
    def refresh_browser(self, context: BrowserContext) -> bool:
        """重新整理單個瀏覽器（導航到遊戲頁面）。
        
        Args:
            context: 瀏覽器上下文
            
        Returns:
            是否成功
        """
        try:
            context.driver.get(Constants.GAME_PAGE)
            time.sleep(Constants.DEFAULT_WAIT_SECONDS)
            return True
        except Exception as e:
            self.logger.error(f"瀏覽器 {context.index} 導航到遊戲頁面失敗: {e}")
            return False
    
    def refresh_and_login(self, context: BrowserContext) -> bool:
        """重新整理瀏覽器並完成登入流程。
        
        包含以下步驟：
        1. 導航到登入頁面
        2. 放大視窗 → 導航到遊戲頁面（搜尋並點擊遊戲）→ 縮回原始大小
        3. 切換到遊戲 iframe
        4. 等待並點擊 lobby_login
        5. 檢測並處理後續畫面：
           - 情境 A: 出現 game_return → 點擊返回按鈕
           - 情境 B: 出現 lobby_confirm → 點擊確認按鈕
        
        Args:
            context: 瀏覽器上下文
            
        Returns:
            是否成功
        """
        try:
            # 步驟 1: 導航到登入頁面
            if not self.refresh_browser(context):
                return False
            
            # 步驟 2: 導航到遊戲頁面（搜尋並點擊遊戲）
            # 為了確保 DOM 元素正確渲染，需要暫時放大瀏覽器
            driver = context.driver
            
            # 2.1 記錄原始視窗大小和位置
            original_size = driver.get_window_size()
            original_position = driver.get_window_position()
            original_width = original_size['width']
            original_height = original_size['height']
            original_x = original_position['x']
            original_y = original_position['y']
            
            self.logger.debug(f"瀏覽器 {context.index} 原始大小: {original_width}x{original_height}, 位置: ({original_x}, {original_y})")
            
            # 2.2 放大視窗到固定尺寸（避免 maximize_window 多瀏覽器衝突）
            driver.set_window_size(Constants.ENLARGED_WINDOW_WIDTH, Constants.ENLARGED_WINDOW_HEIGHT)
            time.sleep(1)  # 等待視窗調整完成
            self.logger.debug(f"瀏覽器 {context.index} 已放大至 {Constants.ENLARGED_WINDOW_WIDTH}x{Constants.ENLARGED_WINDOW_HEIGHT}")
            
            # 2.2.1 關閉可能出現的公告彈窗
            try:
                driver.execute_script("""
                    // 隱藏所有彈窗容器
                    const popups = document.querySelectorAll('.popup-container, .popup-wrap');
                    popups.forEach(popup => {
                        popup.style.display = 'none';
                        popup.style.visibility = 'hidden';
                    });
                    
                    // 移除遮罩層（如果有）
                    const overlays = document.querySelectorAll('[class*="overlay"], [class*="mask"]');
                    overlays.forEach(overlay => overlay.remove());
                """)
                self.logger.debug(f"瀏覽器 {context.index} 已隱藏公告彈窗")
                time.sleep(1)  # 等待彈窗關閉
            except Exception as e:
                self.logger.debug(f"瀏覽器 {context.index} 關閉公告彈窗時發生錯誤: {e}")
            
            # 2.3 執行導航到遊戲頁面（不切換 iframe）
            try:
                # 2.3.1 先等待 loading 遮罩層消失
                try:
                    WebDriverWait(driver, 10).until(
                        EC.invisibility_of_element_located((By.CSS_SELECTOR, ".loading-container"))
                    )
                    self.logger.debug(f"瀏覽器 {context.index} Loading 遮罩層已消失")
                except Exception:
                    self.logger.debug(f"瀏覽器 {context.index} 未檢測到 loading 遮罩層")
                
                # 2.3.2 點擊搜尋按鈕 - 使用 JavaScript 點擊避免被遮擋
                search_btn = driver.find_element(By.XPATH, Constants.SEARCH_BUTTON)
                try:
                    driver.execute_script("arguments[0].click();", search_btn)
                    self.logger.debug(f"瀏覽器 {context.index} 已點擊搜尋按鈕（使用 JavaScript）")
                except Exception:
                    search_btn.click()
                    self.logger.debug(f"瀏覽器 {context.index} 已點擊搜尋按鈕")
                time.sleep(1)
                
                # 2.3.3 在搜尋框輸入「戰神」
                search_input = driver.find_element(By.XPATH, Constants.SEARCH_INPUT)
                search_input.clear()
                search_input.send_keys('戰神')
                search_input.send_keys('\n')
                time.sleep(5)  # 等待搜尋結果載入
                
                # 點擊第一個遊戲圖層 - 使用 JavaScript 點擊避免被其他元素擋住
                game_element = driver.find_element(By.XPATH, Constants.GAME_XPATH)
                # 先滾動到元素可見位置
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", game_element)
                time.sleep(1)
                # 使用 JavaScript 點擊
                driver.execute_script("arguments[0].click();", game_element)
                self.logger.debug(f"瀏覽器 {context.index} 已點擊遊戲（使用 JS 點擊）")
                time.sleep(10)  # 等待遊戲載入
                
            except Exception as e:
                # 恢復原始大小後返回
                driver.set_window_size(original_width, original_height)
                driver.set_window_position(original_x, original_y)
                self.logger.error(f"瀏覽器 {context.index} 導航到遊戲頁面失敗: {e}")
                return False
            
            # 2.4 縮回原始大小和位置
            driver.set_window_size(original_width, original_height)
            driver.set_window_position(original_x, original_y)
            time.sleep(2)  # 等待視窗調整和頁面穩定
            self.logger.debug(f"瀏覽器 {context.index} 已恢復原始大小和位置")
            
            # 步驟 3: 等待並點擊 lobby_login（_wait_and_click_template 會自動處理 iframe 切換）
            if not self._wait_and_click_template(
                context,
                Constants.LOBBY_LOGIN,
                Constants.LOBBY_LOGIN_BUTTON_X_RATIO,
                Constants.LOBBY_LOGIN_BUTTON_Y_RATIO,
                "lobby_login"
            ):
                return False
            
            # 步驟 4: 等待畫面穩定後，檢測出現的是 game_return 還是 lobby_confirm
            time.sleep(2)
            
            # 檢測循環（最多 60 次，每次間隔 1 秒）
            # 使用 OpenCV 模板匹配檢測瀏覽器截圖中是否包含目標圖片區域
            max_attempts = Constants.MAX_DETECTION_ATTEMPTS
            for attempt in range(max_attempts):
                # 同時檢測兩種目標圖片是否存在於瀏覽器畫面的某個區域
                # has_game_return: 檢測是否在畫面中找到 game_return 圖片區域
                has_game_return = self.detect_game_return(context.driver)
                # has_lobby_confirm: 檢測是否在畫面中找到 lobby_confirm 圖片區域
                has_lobby_confirm = self.image_detector.detect_in_browser(
                    context.driver,
                    Constants.LOBBY_CONFIRM
                ) is not None
                
                # 情境 1: 檢測到 game_return
                if has_game_return:
                    self.logger.debug(f"瀏覽器 {context.index} 檢測到 game_return，正在點擊返回...")
                    if self.click_game_return(context):
                        self.logger.debug(f"瀏覽器 {context.index} 已點擊 game_return，已回到遊戲")
                        return True
                    else:
                        self.logger.debug(f"瀏覽器 {context.index} 點擊 game_return 失敗")
                        return False
                
                # 情境 2: 檢測到 lobby_confirm
                if has_lobby_confirm:
                    self.logger.info(f"瀏覽器 {context.index} 檢測到 lobby_confirm，正在點擊確認...")
                    
                    # 取得 Canvas 區域並點擊
                    try:
                        rect = context.driver.execute_script(f"""
                            const canvas = document.getElementById('{Constants.GAME_CANVAS}');
                            const r = canvas.getBoundingClientRect();
                            return {{x: r.left, y: r.top, w: r.width, h: r.height}};
                        """)
                        
                        click_x, click_y = BrowserHelper.calculate_click_position(
                            rect,
                            Constants.LOBBY_CONFIRM_BUTTON_X_RATIO,
                            Constants.LOBBY_CONFIRM_BUTTON_Y_RATIO
                        )
                        
                        time.sleep(Constants.TEMPLATE_CAPTURE_WAIT)
                        BrowserHelper.execute_cdp_click(context.driver, click_x, click_y)
                        self.logger.info(f"瀏覽器 {context.index} 已點擊 lobby_confirm，已回到遊戲")
                        time.sleep(Constants.DEFAULT_WAIT_SECONDS)
                        return True
                        
                    except Exception as e:
                        self.logger.error(f"瀏覽器 {context.index} 點擊 lobby_confirm 失敗: {e}")
                        return False
                
                # 都沒檢測到，繼續等待
                time.sleep(Constants.DETECTION_INTERVAL)
            
            # 超時未檢測到任何圖片
            self.logger.error(f"瀏覽器 {context.index} 等待 game_return 或 lobby_confirm 超時")
            return False
            
        except Exception as e:
            self.logger.error(f"瀏覽器 {context.index} 重新整理並登入失敗: {e}")
            return False
    
    def _wait_and_click_template(
        self,
        context: BrowserContext,
        template_name: str,
        x_ratio: float,
        y_ratio: float,
        display_name: str,
        max_attempts: int = Constants.MAX_DETECTION_ATTEMPTS
    ) -> bool:
        """等待模板出現並點擊。
        
        Args:
            context: 瀏覽器上下文
            template_name: 模板名稱
            x_ratio: X 座標比例
            y_ratio: Y 座標比例
            display_name: 顯示名稱
            max_attempts: 最大嘗試次數
            
        Returns:
            是否成功
        """
        try:
            # 切換到 iframe（如果是 lobby_login，需要先切換）
            if template_name == Constants.LOBBY_LOGIN:
                try:
                    iframe = WebDriverWait(context.driver, 15).until(
                        EC.presence_of_element_located((By.XPATH, Constants.GAME_IFRAME))
                    )
                    context.driver.switch_to.frame(iframe)
                    self.logger.debug(f"瀏覽器 {context.index} 已切換到遊戲 iframe")
                except Exception as e:
                    self.logger.error(f"瀏覽器 {context.index} 切換 iframe 失敗: {e}")
                    return False
            
            # 等待模板出現
            attempt = 0
            found = False
            
            while attempt < max_attempts and not found:
                attempt += 1
                time.sleep(Constants.DETECTION_INTERVAL)
                
                result = self.image_detector.detect_in_browser(
                    context.driver,
                    template_name
                )
                
                if result is not None:
                    found = True
                    self.logger.debug(f"瀏覽器 {context.index} 檢測到 {display_name}")
                    break
                
                # 特別處理：如果正在等待 lobby_login，同時檢測是否直接出現 game_return
                # 這種情況代表頁面跳過了 lobby_login，直接進入遊戲
                if template_name == Constants.LOBBY_LOGIN:
                    has_game_return = self.detect_game_return(context.driver)
                    if has_game_return:
                        self.logger.info(f"瀏覽器 {context.index} 等待 {display_name} 時檢測到 game_return，頁面已直接進入遊戲")
                        # 視為成功，因為目標是完成登入流程
                        return True
            
            if not found:
                self.logger.error(f"瀏覽器 {context.index} 等待 {display_name} 超時")
                return False
            
            # 取得 Canvas 區域
            try:
                rect = context.driver.execute_script(f"""
                    const canvas = document.getElementById('{Constants.GAME_CANVAS}');
                    const r = canvas.getBoundingClientRect();
                    return {{x: r.left, y: r.top, w: r.width, h: r.height}};
                """)
            except Exception as e:
                self.logger.error(f"瀏覽器 {context.index} 取得 Canvas 座標失敗: {e}")
                return False
            
            # 計算點擊座標
            click_x, click_y = BrowserHelper.calculate_click_position(
                rect,
                x_ratio,
                y_ratio
            )
            
            # 執行點擊
            time.sleep(Constants.TEMPLATE_CAPTURE_WAIT)
            BrowserHelper.execute_cdp_click(context.driver, click_x, click_y)
            self.logger.debug(f"瀏覽器 {context.index} 已點擊 {display_name}")
            
            # 等待動作完成
            time.sleep(Constants.DEFAULT_WAIT_SECONDS)
            
            return True
            
        except Exception as e:
            self.logger.error(f"瀏覽器 {context.index} 處理 {display_name} 失敗: {e}")
            return False
    
    def detect_game_return(self, driver: WebDriver) -> bool:
        """檢測瀏覽器中是否出現 game_return 圖片。
        
        Args:
            driver: WebDriver 實例
            
        Returns:
            是否檢測到 game_return
        """
        try:
            result = self.image_detector.detect_in_browser(driver, Constants.GAME_RETURN)
            return result is not None
        except Exception as e:
            self.logger.debug(f"game_return 檢測失敗: {e}")
            return False
    
    def detect_lobby_return(self, driver: WebDriver) -> bool:
        """檢測瀏覽器中是否出現 lobby_return 圖片。
        
        Args:
            driver: WebDriver 實例
            
        Returns:
            是否檢測到 lobby_return
        """
        try:
            result = self.image_detector.detect_in_browser(driver, Constants.LOBBY_RETURN)
            return result is not None
        except Exception as e:
            self.logger.debug(f"lobby_return 檢測失敗: {e}")
            return False
    
    def _handle_lobby_return_scenario(self, context: BrowserContext) -> bool:
        """處理 lobby_return 場景：回到 LOGIN_PAGE 並執行完整登入流程。
        
        包含以下步驟：
        1. 導航到 LOGIN_PAGE
        2. 放大視窗
        3. 搜尋「戰神」並點擊遊戲
        4. 縮回原始大小
        5. 切換到遊戲 iframe
        6. 等待並點擊 lobby_login
        7. 檢測並處理 game_return 或 lobby_confirm
        
        Args:
            context: 瀏覽器上下文
            
        Returns:
            是否成功
        """
        try:
            driver = context.driver
            
            # 步驟 1: 導航到 LOGIN_PAGE
            self.logger.info(f"瀏覽器 {context.index} 導航到 LOGIN_PAGE...")
            driver.get(Constants.LOGIN_PAGE)
            time.sleep(Constants.DEFAULT_WAIT_SECONDS)
            
            # 步驟 2: 記錄原始視窗大小和位置
            original_size = driver.get_window_size()
            original_position = driver.get_window_position()
            original_width = original_size['width']
            original_height = original_size['height']
            original_x = original_position['x']
            original_y = original_position['y']
            
            self.logger.debug(f"瀏覽器 {context.index} 原始大小: {original_width}x{original_height}, 位置: ({original_x}, {original_y})")
            
            # 步驟 3: 放大視窗到固定尺寸（避免 maximize_window 多瀏覽器衝突）
            driver.set_window_size(Constants.ENLARGED_WINDOW_WIDTH, Constants.ENLARGED_WINDOW_HEIGHT)
            time.sleep(1)  # 等待視窗調整完成
            self.logger.debug(f"瀏覽器 {context.index} 已放大至 {Constants.ENLARGED_WINDOW_WIDTH}x{Constants.ENLARGED_WINDOW_HEIGHT}")
            
            # 步驟 4: 執行導航到遊戲頁面（不切換 iframe）
            try:
                # 點擊搜尋按鈕
                search_btn = driver.find_element(By.XPATH, Constants.SEARCH_BUTTON)
                search_btn.click()
                time.sleep(1)
                
                # 2.3.3 在搜尋框輸入「戰神」
                search_input = driver.find_element(By.XPATH, Constants.SEARCH_INPUT)
                search_input.clear()
                search_input.send_keys('戰神')
                search_input.send_keys('\n')
                time.sleep(5)  # 等待搜尋結果載入
                
                # 2.3.4 點擊第一個遊戲圖層 - 使用 JavaScript 點擊避免被其他元素擋住
                game_element = driver.find_element(By.XPATH, Constants.GAME_XPATH)
                # 先滾動到元素可見位置
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", game_element)
                time.sleep(1)
                # 使用 JavaScript 點擊
                driver.execute_script("arguments[0].click();", game_element)
                self.logger.debug(f"瀏覽器 {context.index} 已點擊遊戲（使用 JS 點擊）")
                time.sleep(5)  # 等待遊戲載入
                
            except Exception as e:
                # 恢復原始大小後返回
                driver.set_window_size(original_width, original_height)
                driver.set_window_position(original_x, original_y)
                self.logger.error(f"瀏覽器 {context.index} 導航到遊戲頁面失敗: {e}")
                return False
            
            # 步驟 5: 縮回原始大小和位置
            driver.set_window_size(original_width, original_height)
            driver.set_window_position(original_x, original_y)
            time.sleep(2)  # 等待視窗調整和頁面穩定
            self.logger.debug(f"瀏覽器 {context.index} 已恢復原始大小和位置")
            
            # 步驟 6: 等待並點擊 lobby_login
            if not self._wait_and_click_template(
                context,
                Constants.LOBBY_LOGIN,
                Constants.LOBBY_LOGIN_BUTTON_X_RATIO,
                Constants.LOBBY_LOGIN_BUTTON_Y_RATIO,
                "lobby_login"
            ):
                return False
            
            # 步驟 7: 等待畫面穩定後，檢測出現的是 game_return 還是 lobby_confirm
            time.sleep(2)
            
            # 檢測循環（最多 60 次，每次間隔 1 秒）
            max_attempts = Constants.MAX_DETECTION_ATTEMPTS
            for attempt in range(max_attempts):
                # 同時檢測兩種目標圖片
                has_game_return = self.detect_game_return(context.driver)
                has_lobby_confirm = self.image_detector.detect_in_browser(
                    context.driver,
                    Constants.LOBBY_CONFIRM
                ) is not None
                
                # 情境 1: 檢測到 game_return
                if has_game_return:
                    self.logger.debug(f"瀏覽器 {context.index} 檢測到 game_return，正在點擊返回...")
                    # 注意：這裡不遞迴調用 click_game_return，只執行點擊動作
                    if self._click_game_return_button_only(context):
                        self.logger.info(f"瀏覽器 {context.index} 已點擊 game_return，已回到遊戲")
                        return True
                    else:
                        self.logger.debug(f"瀏覽器 {context.index} 點擊 game_return 失敗")
                        return False
                
                # 情境 2: 檢測到 lobby_confirm
                if has_lobby_confirm:
                    self.logger.info(f"瀏覽器 {context.index} 檢測到 lobby_confirm，正在點擊確認...")
                    
                    # 取得 Canvas 區域並點擊
                    try:
                        rect = context.driver.execute_script(f"""
                            const canvas = document.getElementById('{Constants.GAME_CANVAS}');
                            const r = canvas.getBoundingClientRect();
                            return {{x: r.left, y: r.top, w: r.width, h: r.height}};
                        """)
                        
                        click_x, click_y = BrowserHelper.calculate_click_position(
                            rect,
                            Constants.LOBBY_CONFIRM_BUTTON_X_RATIO,
                            Constants.LOBBY_CONFIRM_BUTTON_Y_RATIO
                        )
                        
                        time.sleep(Constants.TEMPLATE_CAPTURE_WAIT)
                        BrowserHelper.execute_cdp_click(context.driver, click_x, click_y)
                        self.logger.info(f"瀏覽器 {context.index} 已點擊 lobby_confirm，已回到遊戲")
                        time.sleep(Constants.DEFAULT_WAIT_SECONDS)
                        return True
                        
                    except Exception as e:
                        self.logger.error(f"瀏覽器 {context.index} 點擊 lobby_confirm 失敗: {e}")
                        return False
                
                # 都沒檢測到，繼續等待
                time.sleep(Constants.DETECTION_INTERVAL)
            
            # 超時未檢測到任何圖片
            self.logger.error(f"瀏覽器 {context.index} 等待 game_return 或 lobby_confirm 超時")
            return False
            
        except Exception as e:
            self.logger.error(f"瀏覽器 {context.index} 處理 lobby_return 場景失敗: {e}")
            return False
    
    def _click_game_return_button_only(self, context: BrowserContext) -> bool:
        """僅執行點擊 game_return 按鈕，不檢測後續的 lobby_return。
        
        用於避免在 _handle_lobby_return_scenario 中遞迴調用。
        
        Args:
            context: 瀏覽器上下文
            
        Returns:
            是否成功
        """
        try:
            rect = None
            found_method = None
            
            # 嘗試方案 1: 先嘗試外層頁面
            try:
                context.driver.switch_to.default_content()
                time.sleep(0.5)
                
                rect = context.driver.execute_script(f"""
                    const canvas = document.getElementById('{Constants.GAME_CANVAS}');
                    if (canvas) {{
                        const r = canvas.getBoundingClientRect();
                        return {{x: r.left, y: r.top, w: r.width, h: r.height}};
                    }}
                    return null;
                """)
                
                if rect:
                    found_method = "外層頁面"
            except Exception:
                pass
            
            # 嘗試方案 2: 如果外層找不到，再嘗試 iframe
            if not rect:
                try:
                    iframe = WebDriverWait(context.driver, 3).until(
                        EC.presence_of_element_located((By.XPATH, Constants.GAME_IFRAME))
                    )
                    context.driver.switch_to.frame(iframe)
                    time.sleep(0.5)
                    
                    rect = context.driver.execute_script(f"""
                        const canvas = document.getElementById('{Constants.GAME_CANVAS}');
                        if (canvas) {{
                            const r = canvas.getBoundingClientRect();
                            return {{x: r.left, y: r.top, w: r.width, h: r.height}};
                        }}
                        return null;
                    """)
                    
                    if rect:
                        found_method = "iframe"
                except Exception:
                    pass
            
            if not rect:
                self.logger.warning(f"瀏覽器 {context.index} 無法找到 Canvas 元素")
                return False
            
            # 計算點擊座標並執行點擊
            click_x, click_y = BrowserHelper.calculate_click_position(
                rect,
                Constants.GAME_CONFIRM_BUTTON_X_RATIO,
                Constants.GAME_CONFIRM_BUTTON_Y_RATIO
            )
            
            time.sleep(Constants.TEMPLATE_CAPTURE_WAIT)
            BrowserHelper.execute_cdp_click(context.driver, click_x, click_y)
            self.logger.debug(f"瀏覽器 {context.index} 已在{found_method}點擊 game_return 按鈕")
            time.sleep(Constants.DEFAULT_WAIT_SECONDS)
            
            return True
            
        except Exception as e:
            self.logger.error(f"瀏覽器 {context.index} 點擊 game_return 按鈕失敗: {e}")

            return False
    
    def click_game_return(self, context: BrowserContext) -> bool:
        """點擊 game_return 的返回按鈕（使用專屬的 game_confirm 座標）。
        
        點擊後檢測是否出現 lobby_return，如果出現則執行完整登入流程。
        
        Args:
            context: 瀏覽器上下文
            
        Returns:
            是否成功
        """
        try:
            rect = None
            found_method = None
            
            # 嘗試方案 1: 先嘗試外層頁面（通常 game_return 出現在外層）
            try:
                context.driver.switch_to.default_content()
                time.sleep(0.5)  # 等待切換完成
                
                rect = context.driver.execute_script(f"""
                    const canvas = document.getElementById('{Constants.GAME_CANVAS}');
                    if (canvas) {{
                        const r = canvas.getBoundingClientRect();
                        return {{x: r.left, y: r.top, w: r.width, h: r.height}};
                    }}
                    return null;
                """)
                
                if rect:
                    found_method = "外層頁面"
                    self.logger.debug(f"瀏覽器 {context.index} 在外層頁面找到 Canvas")
            except Exception as e:
                self.logger.debug(f"瀏覽器 {context.index} 在外層頁面查找 Canvas 失敗: {e}")
            
            # 嘗試方案 2: 如果外層找不到，再嘗試 iframe
            if not rect:
                try:
                    iframe = WebDriverWait(context.driver, 3).until(
                        EC.presence_of_element_located((By.XPATH, Constants.GAME_IFRAME))
                    )
                    context.driver.switch_to.frame(iframe)
                    time.sleep(0.5)  # 等待切換完成
                    
                    rect = context.driver.execute_script(f"""
                        const canvas = document.getElementById('{Constants.GAME_CANVAS}');
                        if (canvas) {{
                            const r = canvas.getBoundingClientRect();
                            return {{x: r.left, y: r.top, w: r.width, h: r.height}};
                        }}
                        return null;
                    """)
                    
                    if rect:
                        found_method = "iframe"
                        self.logger.debug(f"瀏覽器 {context.index} 在 iframe 中找到 Canvas")
                except Exception as e:
                    self.logger.debug(f"瀏覽器 {context.index} 在 iframe 查找 Canvas 失敗: {e}")
            
            # 如果都找不到 Canvas，記錄錯誤並返回失敗
            if not rect:
                self.logger.warning(f"瀏覽器 {context.index} 兩種方案都無法找到 Canvas 元素，點擊失敗")
                return False
            
            # 計算點擊座標（使用專屬的 game_confirm 按鈕座標）
            click_x, click_y = BrowserHelper.calculate_click_position(
                rect,
                Constants.GAME_CONFIRM_BUTTON_X_RATIO,
                Constants.GAME_CONFIRM_BUTTON_Y_RATIO
            )
            
            # 執行點擊
            time.sleep(Constants.TEMPLATE_CAPTURE_WAIT)
            BrowserHelper.execute_cdp_click(context.driver, click_x, click_y)
            self.logger.debug(f"瀏覽器 {context.index} 已在{found_method}點擊 game_return 返回按鈕 (座標: {click_x:.0f}, {click_y:.0f})")
            
            # 等待動作完成
            time.sleep(Constants.DEFAULT_WAIT_SECONDS)
            
            # === 新增：檢測是否出現 lobby_return ===
            self.logger.debug(f"瀏覽器 {context.index} 檢測是否出現 lobby_return...")
            has_lobby_return = self.detect_lobby_return(context.driver)
            
            if has_lobby_return:
                self.logger.info(f"瀏覽器 {context.index} 檢測到 lobby_return，執行完整登入流程...")
                return self._handle_lobby_return_scenario(context)
            else:
                self.logger.debug(f"瀏覽器 {context.index} 未檢測到 lobby_return，直接返回成功")
                return True
            
        except Exception as e:
            self.logger.error(f"瀏覽器 {context.index} 點擊 game_return 失敗（異常）: {e}")
            return False
    
    def wait_for_template(
        self,
        contexts: List[BrowserContext],
        template_name: str,
        max_attempts: int = Constants.MAX_DETECTION_ATTEMPTS
    ) -> bool:
        """等待所有瀏覽器顯示指定模板。
        
        Args:
            contexts: 瀏覽器上下文列表
            template_name: 模板名稱
            max_attempts: 最大嘗試次數
            
        Returns:
            是否所有瀏覽器都找到
        """
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            all_found = True
            
            for context in contexts:
                try:
                    result = self.image_detector.detect_in_browser(
                        context.driver,
                        template_name
                    )
                    if not result:
                        all_found = False
                        break
                except Exception:
                    all_found = False
                    break
            
            if all_found:
                return True
            
            # 顯示進度
            if attempt % Constants.DETECTION_PROGRESS_INTERVAL == 0:
                found_count = sum(
                    1 for context in contexts
                    if self.image_detector.detect_in_browser(
                        context.driver,
                        template_name
                    ) is not None
                )
                self.logger.info(f"檢測中... ({found_count}/{len(contexts)})")
            
            time.sleep(Constants.DETECTION_INTERVAL)
        
        return False
    
    def restart_and_recover(
        self,
        contexts: List[BrowserContext],
        canvas_rect: Dict[str, float]
    ) -> bool:
        """重啟瀏覽器並恢復到可用狀態。
        
        Args:
            contexts: 需要重啟的瀏覽器上下文列表
            canvas_rect: Canvas 區域資訊
            
        Returns:
            是否成功
        """
        if not contexts:
            return True
        
        # 1. 導航所有瀏覽器到遊戲頁面
        for context in contexts:
            self.refresh_browser(context)
        
        # 2. 等待 lobby_login 出現
        if not self.wait_for_template(contexts, Constants.LOBBY_LOGIN):
            self.logger.error("等待 lobby_login 超時")
            return False
        
        # 3. 計算並點擊開始遊戲按鈕
        start_x, start_y = BrowserHelper.calculate_click_position(
            canvas_rect,
            Constants.LOBBY_LOGIN_BUTTON_X_RATIO,
            Constants.LOBBY_LOGIN_BUTTON_Y_RATIO
        )
        
        time.sleep(Constants.TEMPLATE_CAPTURE_WAIT)
        
        # 同步點擊所有瀏覽器
        for context in contexts:
            try:
                BrowserHelper.execute_cdp_click(context.driver, start_x, start_y)
            except Exception as e:
                self.logger.error(f"瀏覽器 {context.index} 點擊失敗: {e}")
        
        # 4. 等待 lobby_login 消失
        time.sleep(Constants.DEFAULT_WAIT_SECONDS)
        
        return True


# ============================================================================
# 遊戲控制中心
# ============================================================================

class GameControlCenter:
    """遊戲控制中心。
    
    提供互動式命令行介面，用於控制多個瀏覽器的遊戲操作。
    支援啟動、暫停遊戲等基本控制功能。
    
    Attributes:
        browser_contexts: 瀏覽器上下文列表
        browser_operator: 瀏覽器操作器
        logger: 日誌記錄器
        running: 控制中心運行狀態
        game_running: 遊戲運行狀態
    """
    
    def __init__(
        self,
        browser_contexts: List[BrowserContext],
        browser_operator: SyncBrowserOperator,
        bet_rules: List[BetRule],
        logger: Optional[logging.Logger] = None
    ):
        """初始化控制中心。
        
        Args:
            browser_contexts: 瀏覽器上下文列表
            browser_operator: 瀏覽器操作器
            bet_rules: 下注規則列表
            logger: 日誌記錄器
        """
        self.browser_contexts = browser_contexts
        self.browser_operator = browser_operator
        self.bet_rules = bet_rules  # 在初始化時就設定規則
        self.logger = logger or LoggerFactory.get_logger()
        self.running = False
        self.game_running = False  # 遊戲運行狀態
        self.auto_press_running = False  # 自動按鍵運行狀態
        self.min_interval = 1.0  # 最小間隔時間
        self.max_interval = 1.0  # 最大間隔時間
        self.auto_press_threads: Dict[int, threading.Thread] = {}  # 每個瀏覽器的執行緒
        self._stop_event = threading.Event()  # 停止事件
        
        # 規則執行相關
        self.rule_running = False  # 規則執行狀態
        self.rule_thread: Optional[threading.Thread] = None  # 規則執行執行緒
        
        # 自動跳過點擊相關
        self.auto_skip_running = False  # 自動跳過點擊運行狀態
        self.auto_skip_thread: Optional[threading.Thread] = None  # 自動跳過點擊執行緒
        self._auto_skip_stop_event = threading.Event()  # 自動跳過停止事件
        
        # 黑屏檢測時間戳（key: 瀏覽器索引）
        self._blackscreen_timestamps: Dict[int, Optional[float]] = {}  # 黑屏首次檢測時間戳（key: 瀏覽器索引）
        
        # 規則執行時間控制相關
        self.rule_execution_start_time: Optional[float] = None  # 規則執行開始時間
        self.rule_execution_max_hours: Optional[float] = None  # 規則執行最大小時數
        self.time_monitor_running = False  # 時間監控運行狀態
        self.time_monitor_thread: Optional[threading.Thread] = None  # 時間監控執行緒
        self._time_monitor_stop_event = threading.Event()  # 時間監控停止事件
        
        # 自動執行相關
        self.user_has_input = False  # 記錄用戶是否有輸入過命令
        self.auto_start_timer: Optional[threading.Timer] = None  # 自動啟動計時器
        
        # 初始化恢復管理器
        self.image_detector = ImageDetector(logger=self.logger)
        self.recovery_manager = BrowserRecoveryManager(
            image_detector=self.image_detector,
            browser_operator=self.browser_operator,
            logger=self.logger
        )
    
    def show_help(self) -> None:
        """顯示幫助信息"""
        help_text = """
==========================================================
                    【遊戲控制中心 - 指令說明】
==========================================================

【自動操作】
  s <最小>,<最大>     開始自動按鍵（設定隨機間隔秒數）
                      範例: s 1,2  → 每次間隔 1~2 秒按空白鍵
                      提示: 先用 'b' 調整好金額後再啟動
                   
  r <小時數>          執行規則模式（依照 lib/用戶規則.txt）
                      格式: 金額:分鐘:最小秒:最大秒
                      範例: r 0     → 無限執行所有規則
                            r 2     → 執行 2 小時後自動停止
                            r 0.5   → 執行 30 分鐘後自動停止
                      提示: 時間到後會自動關閉所有瀏覽器並退出
                   
  p                   暫停目前運行的自動操作（按鍵或規則）

【金額與遊戲】  
  b <金額>            調整所有瀏覽器的下注金額
                      範例: b 2, b 4, b 10, b 100
                      提示: 金額必須在系統支援範圍內
  
  f <編號>            購買免費遊戲
                      f 0      → 所有瀏覽器
                      f 1      → 第 1 個瀏覽器
                      f 1,2,3  → 第 1、2、3 個瀏覽器
                      提示: 購買後需手動遊玩，結束後按 Enter
  
  a <次數>            設定自動旋轉次數
                      a 10     → 自動旋轉 10 次
                      a 50     → 自動旋轉 50 次  
                      a 100    → 自動旋轉 100 次
                      提示: 設定後會自動執行

【工具與系統】
  c                   截取金額模板（用於優化金額識別）
                      提示: 在遊戲中調整到特定金額後使用

  k                   截取黑屏模板（座標 300,195，範圍 50px）
                      提示: 選擇單一瀏覽器截取，檔名固定為 black_screen.png

  g                   截取返回遊戲提示模板（座標 300,195，範圍 50px）
                      提示: 選擇單一瀏覽器截取，檔名固定為 game_return.png

  y                   截取大廳返回提示模板（參考 lobby_login 方式，完整截圖）
                      提示: 選擇單一瀏覽器截取，檔名固定為 lobby_return.png

  h                   顯示此幫助信息

  q <編號>            關閉指定瀏覽器
                      q 0      → 關閉所有瀏覽器並退出程式
                      q 1      → 關閉第 1 個瀏覽器
                      q 1,2,3  → 關閉第 1、2、3 個瀏覽器

==========================================================
[提示] 初始視窗大小為 600x400，您可以自由調整視窗大小
==========================================================
"""
        self.logger.info(help_text)
    
    def _is_browser_alive(self, driver: WebDriver) -> bool:
        """檢查瀏覽器是否仍然有效。
        
        Args:
            driver: WebDriver 實例
            
        Returns:
            bool: True 表示瀏覽器有效，False 表示已關閉
        """
        try:
            _ = driver.current_url
            return True
        except Exception:
            return False
    
    def _auto_press_loop_single(self, context: BrowserContext, browser_index: int) -> None:
        """單個瀏覽器的自動按鍵循環（優化版）。
        
        Args:
            context: 瀏覽器上下文
            browser_index: 瀏覽器索引
        """
        import random
        
        press_count = 0
        username = context.credential.username
        driver = context.driver
        
        while not self._stop_event.is_set():
            try:
                # 檢查瀏覽器是否仍然有效
                try:
                    _ = driver.current_url
                except Exception:
                    self.logger.warning(f"瀏覽器 {browser_index} ({username}) 已關閉，停止自動按鍵")
                    break
                
                press_count += 1
                
                # 執行按空白鍵
                try:
                    BrowserHelper.execute_cdp_space_key(driver)
                except Exception as e:
                    self.logger.error(f"瀏覽器 {browser_index} ({username}) 按鍵失敗: {e}")
                
                # 每個瀏覽器使用獨立的隨機間隔
                interval = random.uniform(self.min_interval, self.max_interval)
                
                # 使用 wait 而非 sleep，這樣可以立即響應停止信號
                if self._stop_event.wait(timeout=interval):
                    break
                    
            except Exception as e:
                self.logger.error(f"瀏覽器 {browser_index} ({username}) 執行錯誤: {e}")
                self._stop_event.wait(timeout=Constants.STOP_EVENT_ERROR_WAIT)
        
        self.logger.info(f"瀏覽器 {browser_index} ({username}) 已停止，共執行 {press_count} 次")
    
    def _auto_skip_click_loop(self) -> None:
        """自動跳過點擊循環（每30秒點擊一次所有瀏覽器）。
        
        持續運行直到收到停止信號，用於自動跳過結算畫面等。
        """
        self.logger.info("[啟動] 自動跳過點擊功能已啟動（每 30 秒點擊一次）")
        
        # 檢查 Canvas 區域是否已初始化
        if not hasattr(self.browser_operator, 'last_canvas_rect') or \
           self.browser_operator.last_canvas_rect is None:
            self.logger.warning("Canvas 區域未初始化，自動跳過功能無法啟動")
            return
        
        # 計算點擊座標
        rect = self.browser_operator.last_canvas_rect
        lobby_x, lobby_y = BrowserHelper.calculate_click_position(
            rect,
            Constants.LOBBY_LOGIN_BUTTON_X_RATIO,
            Constants.LOBBY_LOGIN_BUTTON_Y_RATIO
        )
        
        click_count = 0
        
        while not self._auto_skip_stop_event.is_set():
            try:
                # 等待指定間隔時間，如果收到停止信號則立即退出
                if self._auto_skip_stop_event.wait(timeout=Constants.AUTO_SKIP_CLICK_INTERVAL):
                    break
                
                click_count += 1
                
                # 對所有瀏覽器執行點擊
                for i, context in enumerate(self.browser_contexts, 1):
                    try:
                        # 檢查瀏覽器是否仍然有效
                        try:
                            _ = context.driver.current_url
                        except Exception:
                            # 瀏覽器已關閉，跳過
                            continue
                        
                        BrowserHelper.execute_cdp_click(context.driver, lobby_x, lobby_y)
                    except Exception as e:
                        # 靜默處理錯誤，避免日誌過多
                        pass
                
                # 每隔一段時間顯示一次統計信息（例如每 10 次）
                if click_count % 10 == 0:
                    self.logger.debug(f"自動跳過已執行 {click_count} 次")
                    
            except Exception as e:
                self.logger.error(f"自動跳過點擊發生錯誤: {e}")
                self._auto_skip_stop_event.wait(timeout=Constants.STOP_EVENT_ERROR_WAIT)
        
        self.logger.info(f"[停止] 自動跳過點擊功能已停止（共執行 {click_count} 次）")

    
    def _start_auto_press(self) -> None:
        """為每個瀏覽器啟動獨立的自動按鍵執行緒。"""
        if self.auto_press_running:
            self.logger.warning("自動按鍵已在運行中")
            return
        
        # 清除停止事件
        self._stop_event.clear()
        self.auto_press_threads.clear()
        
        # 為每個瀏覽器啟動獨立執行緒
        for i, context in enumerate(self.browser_contexts, 1):
            thread = threading.Thread(
                target=self._auto_press_loop_single,
                args=(context, i),
                daemon=True,
                name=f"AutoPressThread-{i}"
            )
            self.auto_press_threads[i] = thread
            thread.start()
        
        self.auto_press_running = True
        self.game_running = True
        
        self.logger.info(f"[成功] 已啟動 {len(self.browser_contexts)} 個瀏覽器的自動按鍵")
    
    def _stop_auto_press(self) -> None:
        """停止所有自動按鍵執行緒。"""
        if not self.auto_press_running:
            self.logger.warning("自動按鍵未在運行")
            return
        
        # 設置停止事件
        self._stop_event.set()
        
        # 等待所有執行緒結束
        stopped_count = 0
        for browser_index, thread in self.auto_press_threads.items():
            if thread and thread.is_alive():
                thread.join(timeout=Constants.AUTO_PRESS_STOP_TIMEOUT)
                
                if not thread.is_alive():
                    stopped_count += 1
                else:
                    self.logger.warning(f"瀏覽器 {browser_index} 的執行緒未能正常結束")
            else:
                stopped_count += 1
        
        self.logger.info(f"[成功] 已停止 {stopped_count}/{len(self.auto_press_threads)} 個瀏覽器")
        
        self.auto_press_threads.clear()
        self.auto_press_running = False
        self.game_running = False
    
    def _start_auto_skip_click(self) -> None:
        """啟動自動跳過點擊功能。"""
        if self.auto_skip_running:
            self.logger.debug("自動跳過點擊功能已在運行中")
            return
        
        # 清除停止事件
        self._auto_skip_stop_event.clear()
        
        # 啟動自動跳過執行緒
        self.auto_skip_thread = threading.Thread(
            target=self._auto_skip_click_loop,
            daemon=True,
            name="AutoSkipClickThread"
        )
        self.auto_skip_thread.start()
        self.auto_skip_running = True
    
    def _stop_auto_skip_click(self) -> None:
        """停止自動跳過點擊功能。"""
        if not self.auto_skip_running:
            return
        
        # 設置停止事件
        self._auto_skip_stop_event.set()
        
        # 等待執行緒結束
        if self.auto_skip_thread and self.auto_skip_thread.is_alive():
            self.auto_skip_thread.join(timeout=Constants.AUTO_PRESS_THREAD_JOIN_TIMEOUT)
        
        self.auto_skip_thread = None
        self.auto_skip_running = False
    
    def _time_monitor_loop(self) -> None:
        """規則執行時間監控循環（每 10 秒檢查一次）。
        
        持續運行直到收到停止信號或達到設定的執行時間，
        時間到後自動關閉所有瀏覽器並退出程式。
        """
        if self.rule_execution_start_time is None or self.rule_execution_max_hours is None:
            self.logger.error("[錯誤] 時間監控啟動失敗：缺少必要參數")
            return
        
        self.logger.info(f"[啟動] 規則執行時間監控已啟動（將在 {self.rule_execution_max_hours} 小時後自動停止）")
        
        # 計算結束時間
        end_time = self.rule_execution_start_time + (self.rule_execution_max_hours * 3600)
        
        check_count = 0
        while not self._time_monitor_stop_event.is_set():
            try:
                # 檢查必要參數是否仍然存在（規則執行可能已停止）
                if self.rule_execution_start_time is None or self.rule_execution_max_hours is None:
                    self.logger.debug("[停止] 規則執行已結束，時間監控自動停止")
                    break
                
                # 重新計算結束時間（以防參數被更新）
                end_time = self.rule_execution_start_time + (self.rule_execution_max_hours * 3600)
                
                # 先檢查是否達到執行時間（在等待之前檢查）
                current_time = time.time()
                if current_time >= end_time:
                    elapsed_hours = (current_time - self.rule_execution_start_time) / 3600
                    self.logger.info("")
                    self.logger.info("=" * 60)
                    self.logger.info(f"【時間到】規則已執行 {elapsed_hours:.2f} 小時，準備自動停止")
                    self.logger.info("=" * 60)
                    self.logger.info("")
                    
                    # 設置停止事件，通知所有執行緒停止
                    self._stop_event.set()
                    self._auto_skip_stop_event.set()
                    
                    # 等待規則執行緒檢測到停止信號
                    time.sleep(2)
                    
                    # 強制停止規則執行狀態
                    self.rule_running = False
                    self.auto_press_running = False
                    
                    # 在關閉前，先導航到登入頁面並等待 10 秒
                    try:
                        self.logger.info("正在導航到登入頁面...")
                        self.browser_operator.navigate_to_login_page(self.browser_contexts)
                        self.logger.info("等待 10 秒後關閉...")
                        time.sleep(10)
                    except Exception as e:
                        self.logger.warning(f"導航到登入頁面失敗: {e}，將直接關閉瀏覽器")
                    
                    # 關閉所有瀏覽器
                    self.logger.info("正在關閉所有瀏覽器...")
                    try:
                        closed_count = 0
                        for i, context in enumerate(list(self.browser_contexts)):
                            try:
                                context.driver.quit()
                                closed_count += 1
                                self.logger.info(f"[成功] 已關閉瀏覽器 {i} ({context.credential.username})")
                            except Exception as e:
                                self.logger.error(f"關閉瀏覽器 {i} 失敗: {e}")
                        
                        self.logger.info(f"[成功] 已關閉 {closed_count} 個瀏覽器")
                        self.logger.info("")
                        self.logger.info("程式將在 3 秒後自動退出...")
                        time.sleep(3)
                        
                        # 使用 os._exit() 強制退出整個程序（包括所有執行緒）
                        self.logger.info("再見！")
                        import os
                        os._exit(0)
                        
                    except Exception as e:
                        self.logger.error(f"關閉瀏覽器時發生錯誤: {e}")
                        import os
                        os._exit(1)
                
                # 等待檢查間隔，如果收到停止信號則立即退出
                if self._time_monitor_stop_event.wait(timeout=Constants.RULE_EXECUTION_TIME_CHECK_INTERVAL):
                    break
                
                check_count += 1
                
                # 根據總執行時間決定顯示頻率
                current_time = time.time()
                remaining_seconds = end_time - current_time
                remaining_hours = remaining_seconds / 3600
                
                # 如果總時間 <= 0.5 小時（30分鐘），每分鐘顯示一次（6次檢查）
                # 如果總時間 > 0.5 小時，每 5 分鐘顯示一次（30次檢查）
                display_interval = 6 if (self.rule_execution_max_hours is not None and self.rule_execution_max_hours <= 0.5) else 30
                
                if check_count % display_interval == 0:
                    if remaining_hours >= 0:
                        remaining_minutes = remaining_seconds / 60
                        if remaining_hours >= 1:
                            self.logger.info(f"[時間監控] 剩餘執行時間: {remaining_hours:.2f} 小時")
                        else:
                            self.logger.info(f"[時間監控] 剩餘執行時間: {remaining_minutes:.1f} 分鐘")
                    
            except Exception as e:
                self.logger.error(f"時間監控發生錯誤: {e}")
                self._time_monitor_stop_event.wait(timeout=Constants.STOP_EVENT_ERROR_WAIT)
        
        self.logger.info("[停止] 規則執行時間監控已停止")
    
    def _start_time_monitor(self) -> None:
        """啟動規則執行時間監控功能。"""
        if self.time_monitor_running:
            self.logger.debug("規則執行時間監控功能已在運行中")
            return
        
        # 清除停止事件
        self._time_monitor_stop_event.clear()
        
        # 啟動時間監控執行緒
        self.time_monitor_thread = threading.Thread(
            target=self._time_monitor_loop,
            daemon=True,
            name="TimeMonitorThread"
        )
        self.time_monitor_thread.start()
        self.time_monitor_running = True
    
    def _stop_time_monitor(self) -> None:
        """停止規則執行時間監控功能。"""
        if not self.time_monitor_running:
            return
        
        # 設置停止事件
        self._time_monitor_stop_event.set()
        
        # 等待執行緒結束
        if self.time_monitor_thread and self.time_monitor_thread.is_alive():
            self.time_monitor_thread.join(timeout=Constants.AUTO_PRESS_THREAD_JOIN_TIMEOUT)
        
        self.time_monitor_thread = None
        self.time_monitor_running = False
    
    def _blackscreen_monitor_loop(self) -> None:
        """黑屏監控循環（每 10 秒檢測一次）。
        
        持續運行直到收到停止信號，用於自動檢測並處理黑屏和 game_return。
        使用 ThreadPoolExecutor 並行處理多個瀏覽器的恢復流程。
        """
        self.logger.info("[啟動] 黑屏監控功能已啟動（每 10 秒檢測一次）")
        
        check_count = 0
        refresh_count = 0
        
        while self.running:
            try:
                # 等待 10 秒
                time.sleep(10)
                
                check_count += 1
                
                # 收集需要處理黑屏恢復的瀏覽器
                browsers_to_recover = []
                
                # 對所有瀏覽器執行檢測
                for i, context in enumerate(self.browser_contexts, 1):
                    try:
                        # 檢查瀏覽器是否仍然有效
                        try:
                            _ = context.driver.current_url
                        except Exception:
                            # 瀏覽器已關閉，跳過並清除時間戳
                            self._blackscreen_timestamps.pop(i, None)
                            continue
                        
                        # 檢測是否有黑屏
                        has_black_screen = self.recovery_manager.detect_black_screen(context.driver)
                        current_time = time.time()
                        
                        if has_black_screen:
                            # 如果是首次檢測到黑屏，記錄時間戳
                            if i not in self._blackscreen_timestamps or self._blackscreen_timestamps[i] is None:
                                self._blackscreen_timestamps[i] = current_time
                                self.logger.debug(f"[檢測] 瀏覽器 {i} 首次檢測到黑屏")
                            else:
                                # 計算黑屏持續時間
                                elapsed = current_time - self._blackscreen_timestamps[i]
                                
                                # 如果黑屏持續超過閾值，才執行重新導航
                                if elapsed >= Constants.BLACKSCREEN_PERSIST_SECONDS:
                                    self.logger.warning(f"[檢測] 瀏覽器 {i} 黑屏已持續 {elapsed:.1f} 秒，加入恢復佇列...")
                                    browsers_to_recover.append((i, context))
                                    # 清除時間戳
                                    self._blackscreen_timestamps[i] = None
                                else:
                                    self.logger.debug(f"[檢測] 瀏覽器 {i} 黑屏持續 {elapsed:.1f} 秒（閾值: {Constants.BLACKSCREEN_PERSIST_SECONDS} 秒）")
                            
                            # 檢測到黑屏後繼續下一個瀏覽器
                            continue
                        else:
                            # 如果黑屏消失，清除時間戳
                            if i in self._blackscreen_timestamps and self._blackscreen_timestamps[i] is not None:
                                self.logger.debug(f"[檢測] 瀏覽器 {i} 黑屏已消失")
                                self._blackscreen_timestamps[i] = None
                        
                        # 檢測是否有 game_return 圖片
                        has_game_return = self.recovery_manager.detect_game_return(context.driver)
                        
                        if has_game_return:
                            self.logger.warning(f"[檢測] 瀏覽器 {i} 出現 game_return，正在點擊返回...")
                            
                            # 嘗試點擊返回按鈕（最多 2 次）
                            success = False
                            for attempt in range(2):
                                if self.recovery_manager.click_game_return(context):
                                    refresh_count += 1
                                    self.logger.info(f"[成功] 瀏覽器 {i} 已點擊返回按鈕")
                                    success = True
                                    break
                                else:
                                    if attempt == 0:
                                        self.logger.warning(f"[重試] 瀏覽器 {i} 第 {attempt + 1} 次點擊失敗，正在重試...")
                                        time.sleep(1)  # 等待 1 秒後重試
                            
                            if not success:
                                self.logger.error(f"[失敗] 瀏覽器 {i} 點擊返回失敗（已重試 2 次）")
                                
                    except Exception as e:
                        # 靜默處理錯誤，避免日誌過多
                        pass
                
                # 如果有需要恢復的瀏覽器，使用執行緒池並行處理
                if browsers_to_recover:
                    self.logger.info(f"[並行處理] 開始並行處理 {len(browsers_to_recover)} 個瀏覽器的黑屏恢復...")
                    
                    def recover_single_browser(browser_info):
                        """恢復單個瀏覽器"""
                        i, context = browser_info
                        try:
                            self.logger.info(f"[開始] 瀏覽器 {i} 正在導航到遊戲頁面並重新登入...")
                            if self.recovery_manager.refresh_and_login(context):
                                self.logger.info(f"[成功] 瀏覽器 {i} 已導航並重新登入完成")
                                return True
                            else:
                                self.logger.error(f"[失敗] 瀏覽器 {i} 導航或登入失敗")
                                return False
                        except Exception as e:
                            self.logger.error(f"[錯誤] 瀏覽器 {i} 恢復過程發生異常: {e}")
                            return False
                    
                    # 使用執行緒池並行處理所有需要恢復的瀏覽器
                    with ThreadPoolExecutor(max_workers=min(len(browsers_to_recover), Constants.MAX_THREAD_WORKERS)) as executor:
                        futures = {executor.submit(recover_single_browser, browser_info): browser_info for browser_info in browsers_to_recover}
                        
                        for future in as_completed(futures):
                            browser_info = futures[future]
                            i, context = browser_info
                            try:
                                if future.result():
                                    refresh_count += 1
                            except Exception as e:
                                self.logger.error(f"[異常] 瀏覽器 {i} 執行緒執行異常: {e}")
                    
                    self.logger.info(f"[完成] 已完成 {len(browsers_to_recover)} 個瀏覽器的黑屏恢復處理")
                
                # 每一段時間顯示一次統計信息（例如每 30 次）
                if check_count % 30 == 0:
                    self.logger.debug(f"黑屏監控已檢測 {check_count} 次，重整 {refresh_count} 次")
                    
            except Exception as e:
                self.logger.error(f"黑屏監控發生錯誤: {e}")
                time.sleep(Constants.STOP_EVENT_ERROR_WAIT)
        
        self.logger.info(f"[停止] 黑屏監控功能已停止（共檢測 {check_count} 次，重整 {refresh_count} 次）")
    
    def _rule_execution_loop(self) -> None:
        """規則執行主循環（在獨立執行緒中運行）。
        
        執行邏輯:
        1. 先執行所有帶 '-' 前綴的規則（once_only=True）
        2. 然後循環執行所有不帶 '-' 前綴的規則（once_only=False）
        
        前綴說明:
        - 帶 '-' 前綴（如 -a:2:10）: 只執行一次
        - 不帶前綴（如 a:2:10）: 循環執行
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
            self.logger.info(f"[階段 1] 執行 {len(once_rules)} 條單次規則（帶 '-' 前綴）...")
            
            for rule_index, rule in enumerate(once_rules):
                if self._stop_event.is_set():
                    self.logger.info("收到停止信號")
                    break
                
                try:
                    # 根據規則類型執行對應的操作
                    if rule.rule_type == 'a':
                        self._execute_auto_spin_rule(rule, rule_index + 1, len(once_rules))
                    elif rule.rule_type == 's':
                        self._execute_standard_rule(rule, rule_index + 1, len(once_rules))
                    elif rule.rule_type == 'f':
                        self._execute_free_game_rule(rule, rule_index + 1, len(once_rules))
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
            self.logger.warning("沒有循環規則（不帶 '-' 前綴），規則執行結束")
            self.rule_running = False
            return
        
        self.logger.info(f"[階段 2] 開始循環執行 {len(loop_rules)} 條規則...")
        
        rule_index = 0
        while not self._stop_event.is_set() and self.rule_running:
            try:
                current_rule = loop_rules[rule_index]
                
                # 根據規則類型執行對應的操作
                if current_rule.rule_type == 'a':
                    self._execute_auto_spin_rule(current_rule, rule_index + 1, len(loop_rules))
                elif current_rule.rule_type == 's':
                    self._execute_standard_rule(current_rule, rule_index + 1, len(loop_rules))
                elif current_rule.rule_type == 'f':
                    self._execute_free_game_rule(current_rule, rule_index + 1, len(loop_rules))
                
                # 檢查是否被停止
                if self._stop_event.is_set():
                    self.logger.info("收到停止信號")
                    break
                
                # 顯示完成訊息
                self.logger.info(f"[成功] 規則 {rule_index + 1} 執行完成")
                
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
                if self._stop_event.wait(timeout=Constants.STOP_EVENT_WAIT_TIMEOUT):
                    break
        
        # 最終清理
        if self.auto_press_running:
            for browser_index, thread in self.auto_press_threads.items():
                if thread and thread.is_alive():
                    thread.join(timeout=Constants.AUTO_PRESS_THREAD_JOIN_TIMEOUT)
        
        self.auto_press_threads.clear()
        self.auto_press_running = False
        
        # 停止自動跳過點擊功能
        if self.auto_skip_running:
            self._stop_auto_skip_click()
        
        self.logger.info("")
        self.logger.info("規則執行已停止")
        self.rule_running = False
        
        # 清理時間控制狀態
        self.rule_execution_start_time = None
        self.rule_execution_max_hours = None
    
    def _execute_auto_spin_rule(self, rule: BetRule, rule_num: int, total_rules: int) -> None:
        """執行自動旋轉規則 ('a' 類型)。
        
        Args:
            rule: 自動旋轉規則
            rule_num: 規則編號（顯示用）
            total_rules: 總規則數（顯示用）
        """
        self.logger.info("")
        self.logger.info("=" * 60)
        self.logger.info(
            f"【自動旋轉規則 {rule_num}/{total_rules}】"
            f"金額 {rule.amount}, 次數 {rule.spin_count}"
        )
        self.logger.info("=" * 60)
        self.logger.info("")
        
        # 步驟 1: 調整金額
        self.logger.info(f"[步驟 1/2] 調整金額到 {rule.amount}...")
        results = self.browser_operator.adjust_betsize_all(
            self.browser_contexts,
            rule.amount,
            silent=True,
            stop_event=self._stop_event
        )
        
        # 檢查是否被中斷
        if self._stop_event.is_set():
            self.logger.info("[中斷] 金額調整已被停止")
            return
        
        success_count = sum(1 for r in results if r.success)
        active_browsers = len([ctx for ctx in self.browser_contexts if self._is_browser_alive(ctx.driver)])
        
        if success_count == active_browsers:
            self.logger.info(f"[成功] 全部 {success_count} 個瀏覽器金額調整完成")
        else:
            self.logger.warning(f"[警告] {success_count}/{active_browsers} 個瀏覽器金額調整完成")
        
        # 步驟 2: 設定自動旋轉（使用內建的 'a' 命令邏輯）
        self.logger.info(f"設定自動旋轉 {rule.spin_count} 次...")
        
        # 檢查 Canvas 區域
        if not hasattr(self.browser_operator, 'last_canvas_rect') or \
           self.browser_operator.last_canvas_rect is None:
            self.logger.error("Canvas 區域未初始化，跳過此規則")
            return
        
        rect = self.browser_operator.last_canvas_rect
        
        # 計算點擊座標
        auto_x, auto_y = BrowserHelper.calculate_click_position(
            rect,
            Constants.AUTO_SPIN_BUTTON_X_RATIO,
            Constants.AUTO_SPIN_BUTTON_Y_RATIO
        )
        
        count_ratio_map = {
            10: (Constants.AUTO_SPIN_10_X_RATIO, Constants.AUTO_SPIN_10_Y_RATIO),
            50: (Constants.AUTO_SPIN_50_X_RATIO, Constants.AUTO_SPIN_50_Y_RATIO),
            100: (Constants.AUTO_SPIN_100_X_RATIO, Constants.AUTO_SPIN_100_Y_RATIO)
        }
        x_ratio, y_ratio = count_ratio_map[rule.spin_count]
        count_x, count_y = BrowserHelper.calculate_click_position(rect, x_ratio, y_ratio)
        
        # 對所有瀏覽器執行自動旋轉設定
        def auto_spin_operation(context: BrowserContext, index: int, total: int) -> bool:
            try:
                BrowserHelper.execute_cdp_click(context.driver, auto_x, auto_y)
                time.sleep(Constants.AUTO_SPIN_MENU_WAIT)
                BrowserHelper.execute_cdp_click(context.driver, count_x, count_y)
                return True
            except Exception as e:
                self.logger.error(f"[{context.credential.username}] 設定自動旋轉失敗: {e}")
                return False
        
        results = self.browser_operator.execute_sync(
            self.browser_contexts,
            auto_spin_operation,
            f"設定自動旋轉 {rule.spin_count} 次"
        )
        
        success_count = sum(1 for r in results if r.success)
        if success_count == active_browsers:
            self.logger.info(f"[成功] 自動旋轉設定完成: 全部 {success_count} 個瀏覽器成功")
        else:
            self.logger.warning(f"[警告] {success_count}/{active_browsers} 個瀏覽器設定成功")
    
    def _execute_standard_rule(self, rule: BetRule, rule_num: int, total_rules: int) -> None:
        """執行標準規則 ('s' 類型)。
        
        Args:
            rule: 標準規則
            rule_num: 規則編號（顯示用）
            total_rules: 總規則數（顯示用）
        """
        # === 步驟 1: 確保自動按鍵已完全停止 ===
        if self.auto_press_running:
            self.logger.info("停止自動按鍵...")
            
            # 設置停止事件
            self._stop_event.set()
            
            # 等待所有執行緒完全停止
            for browser_index, thread in list(self.auto_press_threads.items()):
                if thread and thread.is_alive():
                    thread.join(timeout=Constants.AUTO_PRESS_THREAD_JOIN_TIMEOUT)
                    if thread.is_alive():
                        self.logger.warning(f"瀏覽器 {browser_index} 執行緒未能及時停止")
            
            self.auto_press_threads.clear()
            self.auto_press_running = False
            
            # 等待畫面穩定
            time.sleep(Constants.RULE_SWITCH_WAIT)
            self.logger.info("[成功] 自動按鍵已停止")
            
            # 清除停止事件，讓主循環可以繼續執行
            self._stop_event.clear()
        
        # 顯示規則資訊
        self.logger.info("")
        self.logger.info("=" * 60)
        self.logger.info(
            f"【標準規則 {rule_num}/{total_rules}】"
            f"金額 {rule.amount}, 持續 {rule.duration} 分鐘, "
            f"間隔 {rule.min_seconds}~{rule.max_seconds} 秒"
        )
        self.logger.info("=" * 60)
        self.logger.info("")
        
        # 在金額調整前檢查停止標記
        if self._stop_event.is_set():
            self.logger.info("[中斷] 收到停止信號，跳過當前規則")
            return
        
        # === 步驟 2: 調整所有瀏覽器的下注金額 ===
        self.logger.info(f"[步驟 1/2] 調整金額到 {rule.amount}...")
        results = self.browser_operator.adjust_betsize_all(
            self.browser_contexts,
            rule.amount,
            silent=True,
            stop_event=self._stop_event
        )
        
        # 檢查是否被中斷
        if self._stop_event.is_set():
            self.logger.info("[中斷] 金額調整已被停止")
            return
        
        # 統計結果
        success_count = sum(1 for r in results if r.success)
        active_browsers = len([ctx for ctx in self.browser_contexts if self._is_browser_alive(ctx.driver)])
        
        if success_count == active_browsers:
            self.logger.info(f"[成功] 全部 {success_count} 個瀏覽器金額調整完成")
        else:
            self.logger.warning(
                f"[警告] {success_count}/{active_browsers} 個瀏覽器金額調整完成"
            )
            # 如果有失敗的，記錄詳情
            for i, result in enumerate(results):
                if not result.success and i < len(self.browser_contexts):
                    username = self.browser_contexts[i].credential.username
                    if result.message != "瀏覽器已關閉":
                        self.logger.error(f"  [{username}] 調整失敗")
        
        self.logger.info("")
        
        # 在啟動自動按鍵前檢查停止標記
        if self._stop_event.is_set():
            self.logger.info("[中斷] 收到停止信號，跳過自動按鍵")
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
        
        # 為每個瀏覽器啟動自動按鍵執行緒
        for i, context in enumerate(self.browser_contexts, 1):
            thread = threading.Thread(
                target=self._auto_press_loop_single,
                args=(context, i),
                daemon=True,
                name=f"RuleAutoPress-{i}"
            )
            self.auto_press_threads[i] = thread
            thread.start()
        
        self.auto_press_running = True
        
        # === 步驟 4: 等待指定時間 ===
        wait_seconds = rule.duration * 60
        elapsed_time = 0
        check_interval = 1.0  # 每秒檢查一次
        
        # 只在第一次顯示進度提示
        progress_shown = False
        
        while elapsed_time < wait_seconds and not self._stop_event.is_set():
            if self._stop_event.wait(timeout=check_interval):
                break
            elapsed_time += check_interval
            
            # 每 60 秒顯示一次剩餘時間
            if int(elapsed_time) % 60 == 0 and elapsed_time > 0:
                remaining_minutes = int((wait_seconds - elapsed_time) / 60)
                if remaining_minutes > 0:
                    if not progress_shown:
                        progress_shown = True
                    self.logger.info(f"剩餘 {remaining_minutes} 分鐘...")
    
    def _execute_free_game_rule(self, rule: BetRule, rule_num: int, total_rules: int) -> None:
        """執行購買免費遊戲規則 ('f' 類型)。
        
        Args:
            rule: 免費遊戲規則
            rule_num: 規則編號（顯示用）
            total_rules: 總規則數（顯示用）
        """
        # === 步驟 1: 確保自動按鍵已完全停止 ===
        if self.auto_press_running:
            self.logger.info("停止自動按鍵...")
            
            # 設置停止事件
            self._stop_event.set()
            
            # 等待所有執行緒完全停止
            for browser_index, thread in list(self.auto_press_threads.items()):
                if thread and thread.is_alive():
                    thread.join(timeout=Constants.AUTO_PRESS_THREAD_JOIN_TIMEOUT)
                    if thread.is_alive():
                        self.logger.warning(f"瀏覽器 {browser_index} 執行緒未能及時停止")
            
            self.auto_press_threads.clear()
            self.auto_press_running = False
            
            # 等待畫面穩定
            time.sleep(Constants.RULE_SWITCH_WAIT)
            self.logger.info("[成功] 自動按鍵已停止")
            
            # 清除停止事件，讓主循環可以繼續執行
            self._stop_event.clear()
        
        # 顯示規則資訊
        type_name = "免費遊戲" if rule.free_game_type == 1 else "覺醒之力"
        self.logger.info("")
        self.logger.info("=" * 60)
        self.logger.info(
            f"【免費遊戲規則 {rule_num}/{total_rules}】"
            f"金額 {rule.amount} | 類別: {type_name}"
        )
        self.logger.info("=" * 60)
        self.logger.info("")
        
        # 在金額調整前檢查停止標記
        if self._stop_event.is_set():
            self.logger.info("[中斷] 收到停止信號，跳過當前規則")
            return
        
        # === 步驟 2: 調整所有瀏覽器的下注金額 ===
        self.logger.info(f"[步驟 1/2] 調整金額到 {rule.amount}...")
        results = self.browser_operator.adjust_betsize_all(
            self.browser_contexts,
            rule.amount,
            silent=True,
            stop_event=self._stop_event
        )
        
        # 檢查是否被中斷
        if self._stop_event.is_set():
            self.logger.info("[中斷] 金額調整已被停止")
            return
        
        # 統計結果
        success_count = sum(1 for r in results if r.success)
        active_browsers = len([ctx for ctx in self.browser_contexts if self._is_browser_alive(ctx.driver)])
        
        if success_count == active_browsers:
            self.logger.info(f"[成功] 全部 {success_count} 個瀏覽器金額調整完成")
        else:
            self.logger.warning(
                f"[警告] {success_count}/{active_browsers} 個瀏覽器金額調整完成"
            )
        
        self.logger.info("")
        
        # 在購買免費遊戲前檢查停止標記
        if self._stop_event.is_set():
            self.logger.info("[中斷] 收到停止信號，跳過免費遊戲購買")
            return
        
        # === 步驟 3: 購買免費遊戲 ===
        self.logger.info("[步驟 2/2] 開始購買免費遊戲...")
        
        # 檢查 Canvas 區域
        if not hasattr(self.browser_operator, 'last_canvas_rect') or \
           self.browser_operator.last_canvas_rect is None:
            self.logger.error("Canvas 區域未初始化，跳過此規則")
            return
        
        # 使用 buy_free_game_all 方法購買免費遊戲
        try:
            results = self.browser_operator.buy_free_game_all(
                self.browser_contexts,
                self.browser_operator.last_canvas_rect,
                rule.free_game_type
            )
            
            success_count = sum(1 for r in results if r.success)
            if success_count == active_browsers:
                self.logger.info(f"[成功] 全部 {success_count} 個瀏覽器購買完成")
            else:
                self.logger.warning(f"[警告] {success_count}/{active_browsers} 個瀏覽器購買完成")
            
            self.logger.info("")
            self.logger.info("[提示] 免費遊戲進行中，自動跳過功能會處理結算畫面")
        
        except Exception as e:
            self.logger.error(f"購買免費遊戲時發生錯誤: {e}")
    
    def _start_rule_execution(self, max_hours: Optional[float] = None) -> None:
        """啟動規則執行。
        
        Args:
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
        self.rule_execution_start_time = time.time()
        self.rule_execution_max_hours = max_hours
        
        # 顯示規則列表
        self.logger.info("載入的規則:")
        for i, rule in enumerate(self.bet_rules, 1):
            if rule.rule_type == 'a':
                self.logger.info(
                    f"  {i}. [自動旋轉] 金額 {rule.amount}, 次數 {rule.spin_count}"
                )
            elif rule.rule_type == 's':
                self.logger.info(
                    f"  {i}. [標準規則] 金額 {rule.amount}, 持續 {rule.duration} 分鐘, "
                    f"間隔 {rule.min_seconds}~{rule.max_seconds} 秒"
                )
            elif rule.rule_type == 'f':
                self.logger.info(
                    f"  {i}. [免費遊戲] 金額 {rule.amount}"
                )
        
        # 清除停止事件
        self._stop_event.clear()
        
        # 啟動自動跳過點擊功能（每30秒點擊一次）
        self._start_auto_skip_click()
        
        # 啟動時間監控執行緒（如果設定了時間限制）
        if max_hours is not None:
            self._start_time_monitor()
            self.logger.info("")
            self.logger.info(f"[成功] 規則執行已啟動 (將在 {max_hours} 小時後自動停止，按 'p' 可暫停)")
        else:
            self.logger.info("")
            self.logger.info("[成功] 規則執行已啟動 (按 'p' 可暫停)")
        self.logger.info("")
        
        # 啟動規則執行執行緒（放在最後，確保提示訊息先輸出）
        self.rule_thread = threading.Thread(
            target=self._rule_execution_loop,
            daemon=True,
            name="RuleExecutionThread"
        )
        self.rule_thread.start()
        self.rule_running = True
        self.game_running = True
    
    def _stop_rule_execution(self) -> None:
        """停止規則執行。"""
        if not self.rule_running:
            self.logger.warning("規則執行未在運行")
            return
        
        self.logger.info("正在停止規則執行...")
        
        # 停止時間監控（如果正在運行）
        if self.time_monitor_running:
            self._stop_time_monitor()
        
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
            
            self.logger.info(f"[成功] 已停止 {stopped_count}/{len(self.auto_press_threads)} 個瀏覽器的自動按鍵")
            self.auto_press_threads.clear()
            self.auto_press_running = False
        
        # 等待規則執行緒結束
        if self.rule_thread and self.rule_thread.is_alive():
            self.rule_thread.join(timeout=Constants.AUTO_PRESS_STOP_TIMEOUT)
            
            if not self.rule_thread.is_alive():
                self.logger.info("[成功] 規則執行已停止")
            else:
                self.logger.warning("規則執行執行緒未能正常結束")
        
        self.rule_running = False
        self.game_running = False
        self.rule_thread = None
        
        # 清理時間控制狀態
        self.rule_execution_start_time = None
        self.rule_execution_max_hours = None
        
        # 停止自動跳過點擊功能
        if self.auto_skip_running:
            self._stop_auto_skip_click()
    
    def process_command(self, command: str) -> bool:
        """處理用戶指令。
        
        Args:
            command: 用戶輸入的指令
            
        Returns:
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
                if not command_arguments:
                    self.logger.error("指令格式錯誤，請使用: q <編號>")
                    self.logger.info("  q 0      - 關閉所有瀏覽器並退出")
                    self.logger.info("  q 1      - 關閉第 1 個瀏覽器")
                    self.logger.info("  q 1,2,3  - 關閉第 1、2、3 個瀏覽器")
                    return True
                
                try:
                    # 解析參數
                    target_indices = []
                    
                    # 處理逗號分隔的多個編號
                    if ',' in command_arguments:
                        try:
                            indices = [int(x.strip()) for x in command_arguments.split(',')]
                            for browser_index in indices:
                                if browser_index < 1 or browser_index > len(self.browser_contexts):
                                    self.logger.error(
                                        f"瀏覽器編號 {browser_index} 無效，請輸入 1-{len(self.browser_contexts)} 之間的數字"
                                    )
                                    return True
                            target_indices = indices
                        except ValueError:
                            self.logger.error(f"無效的編號格式: {command_arguments}，請使用數字和逗號 (例如: q 1,2,3)")
                            return True
                    else:
                        # 單一數字
                        try:
                            index = int(command_arguments)
                            if index == 0:
                                # 0 表示所有瀏覽器
                                target_indices = list(range(1, len(self.browser_contexts) + 1))
                            elif index < 1 or index > len(self.browser_contexts):
                                self.logger.error(
                                    f"瀏覽器編號無效，請輸入 0 (全部) 或 1-{len(self.browser_contexts)} 之間的數字"
                                )
                                return True
                            else:
                                target_indices = [index]
                        except ValueError:
                            self.logger.error(f"無效的編號: {command_arguments}，請輸入數字 (例如: q 1 或 q 1,2)")
                            return True
                    
                    # 顯示執行信息
                    if len(target_indices) == len(self.browser_contexts):
                        self.logger.info(f"開始關閉瀏覽器 (全部 {len(target_indices)} 個)")
                    elif len(target_indices) == 1:
                        username = self.browser_contexts[target_indices[0] - 1].credential.username
                        self.logger.info(f"開始關閉瀏覽器 (瀏覽器 {target_indices[0]}: {username})")
                    else:
                        self.logger.info(f"開始關閉瀏覽器 ({len(target_indices)} 個)")
                    
                    # 在關閉前，先導航到登入頁面並等待 10 秒
                    try:
                        target_contexts = [self.browser_contexts[i - 1] for i in target_indices]
                        self.logger.info("正在導航到登入頁面...")
                        self.browser_operator.navigate_to_login_page(target_contexts)
                        self.logger.info("等待 10 秒後關閉...")
                        time.sleep(10)
                    except Exception as e:
                        self.logger.warning(f"導航到登入頁面失敗: {e}，將直接關閉瀏覽器")
                    
                    # 關閉指定的瀏覽器
                    closed_count = 0
                    failed_browsers = []
                    
                    # 從後往前遍歷，避免索引問題
                    for browser_index in sorted(target_indices, reverse=True):
                        try:
                            context = self.browser_contexts[browser_index - 1]
                            username = context.credential.username
                            
                            # 關閉瀏覽器
                            context.driver.quit()
                            
                            # 從列表中移除
                            self.browser_contexts.pop(browser_index - 1)
                            
                            self.logger.info(f"[成功] 已關閉瀏覽器 {browser_index} ({username})")
                            closed_count += 1
                            
                        except Exception as e:
                            username = self.browser_contexts[browser_index - 1].credential.username
                            self.logger.error(f"關閉瀏覽器 {browser_index} ({username}) 失敗: {e}")
                            failed_browsers.append((browser_index, username))
                    
                    # 顯示總結
                    if closed_count == len(target_indices):
                        self.logger.info(f"[成功] 關閉完成: 全部 {closed_count} 個瀏覽器已關閉")
                    else:
                        self.logger.warning(
                            f"[警告] 部分完成: {closed_count}/{len(target_indices)} 個瀏覽器已關閉"
                        )
                        if failed_browsers:
                            for browser_index, username in failed_browsers:
                                self.logger.error(f"  瀏覽器 {browser_index} ({username}) 失敗")
                    
                    # 如果所有瀏覽器都關閉了，退出控制中心
                    if len(self.browser_contexts) == 0:
                        self.logger.info("所有瀏覽器已關閉，退出控制中心")
                        return False
                    else:
                        self.logger.info(f"剩餘 {len(self.browser_contexts)} 個瀏覽器仍在運行")
                    
                except Exception as e:
                    self.logger.error(f"關閉瀏覽器時發生錯誤: {e}")
            
            elif cmd == 'h':
                self.show_help()
            
            elif cmd == 's':
                # 解析 's' 指令參數
                if not command_arguments:
                    self.logger.error("[錯誤] 指令格式錯誤")
                    self.logger.info("   正確格式: s <最小>,<最大>")
                    self.logger.info("   範例: s 1,2  → 間隔 1~2 秒按空白鍵")
                    return True
                
                # 解析用戶輸入的間隔時間
                try:
                    interval_parts = command_arguments.split(',')
                    if len(interval_parts) != 2:
                        self.logger.error("[錯誤] 間隔格式錯誤，需要兩個數字")
                        self.logger.info("   範例: s 1,2 或 s 1.5,3")
                        return True
                    
                    min_interval = float(interval_parts[0].strip())
                    max_interval = float(interval_parts[1].strip())
                    
                    if min_interval <= 0 or max_interval <= 0:
                        self.logger.error("[錯誤] 間隔時間必須大於 0")
                        return True
                    
                    if min_interval > max_interval:
                        self.logger.error("[錯誤] 最小間隔不能大於最大間隔")
                        self.logger.info(f"   您輸入的: 最小={min_interval}, 最大={max_interval}")
                        return True
                        
                except ValueError:
                    self.logger.error("[錯誤] 間隔格式錯誤，請輸入有效的數字")
                    self.logger.info("   範例: s 1,2 或 s 1.5,3")
                    return True
                
                # 檢查是否已在運行
                if self.auto_press_running:
                    self.logger.warning("[警告] 自動按鍵已在運行中")
                    self.logger.info(f"   目前設定: {self.min_interval}~{self.max_interval} 秒")
                    self.logger.info("   提示: 請先使用 'p' 暫停，再重新啟動")
                    return True
                
                # 設置間隔時間
                self.min_interval = min_interval
                self.max_interval = max_interval
                
                self.logger.info("")
                self.logger.info("[成功] 自動按鍵已啟動")
                self.logger.info(f"  > 間隔時間: {min_interval}~{max_interval} 秒")
                self.logger.info(f"  > 瀏覽器數: {len(self.browser_contexts)} 個")
                self.logger.info("  > 暫停指令: p")
                self.logger.info("")
                
                # 啟動自動按鍵
                self._start_auto_press()
            
            elif cmd == 'p':
                # 暫停指令 - 可暫停自動按鍵或規則執行
                if self.auto_press_running:
                    self._stop_auto_press()
                    self.logger.info("")
                    self.logger.info("[成功] 已暫停自動按鍵")
                    self.logger.info("")
                    # 暫停後自動顯示幫助
                    self.show_help()
                elif self.rule_running:
                    self._stop_rule_execution()
                    self.logger.info("")
                    self.logger.info("[成功] 已暫停規則執行")
                    self.logger.info("")
                    # 暫停後自動顯示幫助
                    self.show_help()
                else:
                    self.logger.warning("[警告] 目前沒有運行中的自動操作")
                    self.logger.info("   提示: 使用 's 1,2' 啟動自動按鍵，或使用 'r' 啟動規則執行")
            
            elif cmd == 'r':
                # 開始執行規則（必須提供小時參數，0 代表無限執行）
                if self.rule_running:
                    self.logger.warning("[警告] 規則執行已在運行中，請先使用 'p' 暫停")
                    return True
                
                if self.auto_press_running:
                    self.logger.warning("自動按鍵正在運行，請先使用 'p' 暫停")
                    return True
                
                # 檢查是否提供參數
                if not command_arguments:
                    self.logger.error("指令格式錯誤，請使用: r <小時數>")
                    self.logger.info("  r 0      - 無限執行所有規則")
                    self.logger.info("  r 2      - 執行 2 小時後自動停止")
                    self.logger.info("  r 0.5    - 執行 30 分鐘後自動停止")
                    return True
                
                # 解析小時參數
                try:
                    hours = float(command_arguments)
                    if hours < 0:
                        self.logger.error(f"執行時間不能小於 0: {hours}")
                        return True
                    
                    # hours == 0 代表無限執行
                    max_hours = None if hours == 0 else hours
                    
                    if max_hours is None:
                        self.logger.info("設定規則執行模式: 無限執行")
                    else:
                        self.logger.info(f"設定規則執行時間: {max_hours} 小時")
                        
                except ValueError:
                    self.logger.error(f"無效的小時數: {command_arguments}，請輸入數字")
                    return True
                
                self._start_rule_execution(max_hours=max_hours)
            
            elif cmd == 'b':
                # 解析 b 指令參數
                if not command_arguments:
                    self.logger.error("指令格式錯誤，請使用: b amount (例如: b 0.4)")
                    return True
                
                try:
                    target_amount = float(command_arguments)
                    
                    self.logger.info(f"開始調整金額到 {target_amount}...")
                    
                    # 使用同步方法調整所有瀏覽器的金額
                    results = self.browser_operator.adjust_betsize_all(
                        self.browser_contexts,
                        target_amount
                    )
                    
                    # 統計結果（只計算活躍瀏覽器）
                    success_count = sum(1 for r in results if r.success)
                    active_browsers = len([ctx for ctx in self.browser_contexts if self._is_browser_alive(ctx.driver)])
                    
                    if success_count == active_browsers:
                        self.logger.info(f"[成功] 金額調整完成: 全部 {success_count} 個瀏覽器成功")
                    else:
                        self.logger.warning(
                            f"[警告] 部分完成: {success_count}/{active_browsers} 個瀏覽器成功"
                        )
                        # 顯示失敗的瀏覽器（排除已關閉的）
                        for i, result in enumerate(results):
                            if not result.success and i < len(self.browser_contexts):
                                if result.message != "瀏覽器已關閉":
                                    username = self.browser_contexts[i].credential.username
                                    self.logger.error(f"  瀏覽器 {i+1} ({username}) 失敗")
                    
                except ValueError:
                    self.logger.error(f"無效的金額: {command_arguments}，請輸入數字")
            
            elif cmd == 'f':
                # 購買免費遊戲指令
                if not command_arguments:
                    self.logger.error("指令格式錯誤，請使用: f <編號>")
                    self.logger.info("  f 0      - 所有瀏覽器")
                    self.logger.info("  f 1      - 第 1 個瀏覽器")
                    self.logger.info("  f 1,2,3  - 第 1、2、3 個瀏覽器")
                    return True
                
                try:
                    # 檢查 Canvas 區域資訊
                    if not hasattr(self.browser_operator, 'last_canvas_rect') or \
                       self.browser_operator.last_canvas_rect is None:
                        self.logger.error("Canvas 區域未初始化，請確保已完成登入流程")
                        return True
                    
                    # 解析參數
                    target_indices = []
                    
                    # 處理逗號分隔的多個編號
                    if ',' in command_arguments:
                        try:
                            indices = [int(x.strip()) for x in command_arguments.split(',')]
                            for browser_index in indices:
                                if browser_index < 1 or browser_index > len(self.browser_contexts):
                                    self.logger.error(
                                        f"瀏覽器編號 {browser_index} 無效，請輸入 1-{len(self.browser_contexts)} 之間的數字"
                                    )
                                    return True
                            target_indices = indices
                        except ValueError:
                            self.logger.error(f"無效的編號格式: {command_arguments}，請使用數字和逗號 (例如: f 1,2,3)")
                            return True
                    else:
                        # 單一數字
                        try:
                            index = int(command_arguments)
                            if index == 0:
                                # 0 表示所有瀏覽器
                                target_indices = list(range(1, len(self.browser_contexts) + 1))
                            elif index < 1 or index > len(self.browser_contexts):
                                self.logger.error(
                                    f"瀏覽器編號無效，請輸入 0 (全部) 或 1-{len(self.browser_contexts)} 之間的數字"
                                )
                                return True
                            else:
                                target_indices = [index]
                        except ValueError:
                            self.logger.error(f"無效的編號: {command_arguments}，請輸入數字 (例如: f 1 或 f 1,2)")
                            return True
                    
                    # 顯示執行信息
                    if len(target_indices) == len(self.browser_contexts):
                        self.logger.info(f"開始購買免費遊戲 (全部 {len(target_indices)} 個瀏覽器)")
                    elif len(target_indices) == 1:
                        # 安全檢查：確保索引有效
                        if target_indices[0] - 1 < len(self.browser_contexts):
                            username = self.browser_contexts[target_indices[0] - 1].credential.username
                            self.logger.info(f"開始購買免費遊戲 (瀏覽器 {target_indices[0]}: {username})")
                        else:
                            self.logger.error(f"瀏覽器 {target_indices[0]} 不存在或已關閉")
                            return True
                    else:
                        self.logger.info(f"開始購買免費遊戲 ({len(target_indices)} 個瀏覽器)")
                    
                    # 準備目標瀏覽器上下文列表（過濾已關閉的瀏覽器）
                    target_contexts = []
                    valid_indices = []
                    for browser_index in target_indices:
                        if browser_index - 1 < len(self.browser_contexts):
                            context = self.browser_contexts[browser_index - 1]
                            if self._is_browser_alive(context.driver):
                                target_contexts.append(context)
                                valid_indices.append(browser_index)
                            else:
                                self.logger.warning(f"瀏覽器 {browser_index} 已關閉，跳過")
                        else:
                            self.logger.warning(f"瀏覽器 {browser_index} 不存在，跳過")
                    
                    if not target_contexts:
                        self.logger.error("沒有有效的瀏覽器可執行操作")
                        return True
                    
                    # 選擇免費遊戲類別
                    self.logger.info("請選擇免費遊戲類別:")
                    self.logger.info("  1 - 免費遊戲")
                    self.logger.info("  2 - 覺醒之力")
                    self.logger.info("  3 - 不朽覺醒")
                    
                    try:
                        print("請輸入類別 (1、2 或 3) > ", end="", flush=True)
                        type_input = input().strip()
                        
                        if type_input == '1':
                            free_game_type = 1
                            type_name = "免費遊戲"
                        elif type_input == '2':
                            free_game_type = 2
                            type_name = "覺醒之力"
                        elif type_input == '3':
                            free_game_type = 3
                            type_name = "不朽覺醒"
                        else:
                            self.logger.error(f"無效的類別: {type_input}，請輸入 1、2 或 3")
                            return True
                        
                        self.logger.info(f"已選擇: {type_name}")
                        
                    except (EOFError, KeyboardInterrupt):
                        self.logger.info("已取消操作")
                        return True
                    
                    # 使用同步方式執行購買
                    results = self.browser_operator.buy_free_game_all(
                        target_contexts,
                        self.browser_operator.last_canvas_rect,
                        free_game_type
                    )
                    
                    # 統計結果
                    success_count = sum(1 for r in results if r.success)
                    failed_browsers = [
                        (valid_indices[i], target_contexts[i].credential.username)
                        for i, r in enumerate(results)
                        if not r.success
                    ]
                    
                    # 顯示總結
                    if success_count == len(target_contexts):
                        self.logger.info(f"[成功] 購買完成: 全部 {success_count} 個瀏覽器成功")
                    else:
                        self.logger.warning(
                            f"[警告] 部分完成: {success_count}/{len(target_contexts)} 個瀏覽器成功"
                        )
                        if failed_browsers:
                            for browser_index, username in failed_browsers:
                                self.logger.error(f"  瀏覽器 {browser_index} ({username}) 失敗")
                    
                    # 等待用戶確認免費遊戲流程結束
                    if success_count > 0:
                        self.logger.info("免費遊戲已啟動，請手動遊玩")
                        self.logger.info("結束後請按 Enter 繼續（系統將自動結算）")
                        
                        try:
                            print("按 Enter 繼續 > ", end="", flush=True)
                            input()
                            
                            # 對成功購買的瀏覽器執行空白鍵
                            
                            # 只對成功的瀏覽器執行
                            successful_contexts = [
                                target_contexts[i]
                                for i, r in enumerate(results)
                                if r.success
                            ]
                            
                            if successful_contexts:
                                press_results = self.browser_operator.press_space_all(successful_contexts)
                                press_success = sum(1 for r in press_results if r.success)
                                
                                self.logger.info(f"[成功] 已對 {press_success} 個瀏覽器執行結算")
                                
                                # 點擊 LOBBY_LOGIN_BUTTON 座標（連續 5 次，間隔 1 秒）- 快速跳過結算畫面
                                self.logger.info("正在跳過結算畫面...")
                                rect = self.browser_operator.last_canvas_rect
                                lobby_x, lobby_y = BrowserHelper.calculate_click_position(
                                    rect,
                                    Constants.LOBBY_LOGIN_BUTTON_X_RATIO,
                                    Constants.LOBBY_LOGIN_BUTTON_Y_RATIO
                                )
                                
                                def click_lobby_button(context: BrowserContext, index: int, total: int) -> bool:
                                    """跳過結算畫面"""
                                    driver = context.driver
                                    try:
                                        time.sleep(Constants.FREE_GAME_SETTLE_INITIAL_WAIT)  # 等待後開始點擊
                                        for click_num in range(1, Constants.FREE_GAME_SETTLE_CLICK_COUNT + 1):  # 連續點擊跳過結算
                                            BrowserHelper.execute_cdp_click(driver, lobby_x, lobby_y)
                                            if click_num < Constants.FREE_GAME_SETTLE_CLICK_COUNT:  # 最後一次不需要等待
                                                time.sleep(Constants.FREE_GAME_SETTLE_CLICK_INTERVAL)  # 點擊間隔
                                        return True
                                    except Exception as e:
                                        self.logger.error(f"瀏覽器 {index} 點擊失敗: {e}")
                                        return False
                                
                                click_results = self.browser_operator.execute_sync(
                                    successful_contexts,
                                    click_lobby_button,
                                    "跳過結算畫面"
                                )
                                click_success = sum(1 for r in click_results if r.success)
                                
                                self.logger.info(f"[成功] 已對 {click_success} 個瀏覽器跳過結算畫面")
                                self.logger.info("免費遊戲流程完成")
                            
                        except (EOFError, KeyboardInterrupt):
                            self.logger.info("\n已取消等待")
                        except Exception as e:
                            self.logger.error(f"執行空白鍵時發生錯誤: {e}")
                    
                    self.logger.info("")
                    
                except Exception as e:
                    self.logger.error(f"購買過程發生錯誤: {e}")
            
            elif cmd == 'a':
                # 自動旋轉指令
                if not command_arguments:
                    self.logger.error("指令格式錯誤，請使用: a <次數>")
                    self.logger.info("  a 10   - 自動旋轉 10 次")
                    self.logger.info("  a 50   - 自動旋轉 50 次")
                    self.logger.info("  a 100  - 自動旋轉 100 次")
                    return True
                
                try:
                    # 檢查 Canvas 區域資訊
                    if not hasattr(self.browser_operator, 'last_canvas_rect') or \
                       self.browser_operator.last_canvas_rect is None:
                        self.logger.error("Canvas 區域未初始化，請確保已完成登入流程")
                        return True
                    
                    # 解析次數參數
                    spin_count = int(command_arguments.strip())
                    
                    # 驗證次數是否有效
                    if spin_count not in [10, 50, 100]:
                        self.logger.error(f"無效的次數: {spin_count}，請輸入 10、50 或 100")
                        return True
                    
                    self.logger.info(f"開始設定自動旋轉 {spin_count} 次...")
                    
                    # 取得 Canvas 區域
                    rect = self.browser_operator.last_canvas_rect
                    
                    # 計算第一次點擊座標（自動轉按鈕）
                    auto_x, auto_y = BrowserHelper.calculate_click_position(
                        rect,
                        Constants.AUTO_SPIN_BUTTON_X_RATIO,
                        Constants.AUTO_SPIN_BUTTON_Y_RATIO
                    )
                    
                    # 根據次數選擇第二次點擊座標
                    count_ratio_map = {
                        10: (Constants.AUTO_SPIN_10_X_RATIO, Constants.AUTO_SPIN_10_Y_RATIO),
                        50: (Constants.AUTO_SPIN_50_X_RATIO, Constants.AUTO_SPIN_50_Y_RATIO),
                        100: (Constants.AUTO_SPIN_100_X_RATIO, Constants.AUTO_SPIN_100_Y_RATIO)
                    }
                    x_ratio, y_ratio = count_ratio_map[spin_count]
                    count_x, count_y = BrowserHelper.calculate_click_position(rect, x_ratio, y_ratio)
                    
                    # 使用同步方式對所有瀏覽器執行點擊
                    def auto_spin_operation(context: BrowserContext, index: int, total: int) -> bool:
                        """執行自動旋轉設定"""
                        username = context.credential.username
                        driver = context.driver
                        
                        try:
                            # 第一次點擊（自動轉按鈕）
                            BrowserHelper.execute_cdp_click(driver, auto_x, auto_y)
                            time.sleep(Constants.AUTO_SPIN_MENU_WAIT)  # 等待選單出現
                            
                            # 第二次點擊（選擇次數）
                            BrowserHelper.execute_cdp_click(driver, count_x, count_y)
                            
                            return True
                            
                        except Exception as e:
                            self.logger.error(f"[{username}] 設定自動旋轉失敗: {e}")
                            return False
                    
                    results = self.browser_operator.execute_sync(
                        self.browser_contexts,
                        auto_spin_operation,
                        f"設定自動旋轉 {spin_count} 次"
                    )
                    
                    # 統計結果
                    success_count = sum(1 for r in results if r.success)
                    active_browsers = len([ctx for ctx in self.browser_contexts if self._is_browser_alive(ctx.driver)])
                    
                    if success_count == active_browsers:
                        self.logger.info(f"[成功] 自動旋轉設定完成: 全部 {success_count} 個瀏覽器成功")
                    else:
                        self.logger.warning(
                            f"[警告] 部分完成: {success_count}/{active_browsers} 個瀏覽器成功"
                        )
                        # 顯示失敗的瀏覽器（排除已關閉的）
                        for i, result in enumerate(results):
                            if not result.success and i < len(self.browser_contexts):
                                if result.message != "瀏覽器已關閉":
                                    username = self.browser_contexts[i].credential.username
                                    self.logger.error(f"  瀏覽器 {i+1} ({username}) 失敗")
                    
                except ValueError:
                    self.logger.error(f"無效的次數: {command_arguments}，請輸入 10、50 或 100")
                except Exception as e:
                    self.logger.error(f"設定自動旋轉時發生錯誤: {e}")
            
            elif cmd == 'c':
                self.logger.info("")
                self.logger.info("=== 截取金額模板工具 ===")
                self.logger.info("請輸入目前遊戲顯示的金額（例: 0.4, 2.4, 10）")
                self.logger.info("按 Enter 鍵退出")
                
                while True:
                    try:
                        print("\n金額: ", end="", flush=True)
                        amount_input = input().strip()
                        
                        # 空白輸入則退出
                        if not amount_input:
                            self.logger.info("退出金額模板工具")
                            break
                        
                        amount = float(amount_input)
                        
                        # 使用 Constants.GAME_BETSIZE 驗證金額
                        if amount not in Constants.GAME_BETSIZE:
                            self.logger.warning(f"[警告] 金額 {amount} 不在標準列表中，但仍會建立模板")
                        
                        # 使用第一個有效的瀏覽器截取
                        valid_browser_found = False
                        for context in self.browser_contexts:
                            if self._is_browser_alive(context.driver):
                                if self.browser_operator.capture_betsize_template(context.driver, amount):
                                    self.logger.info("[成功] 模板截取成功")
                                    valid_browser_found = True
                                    break
                                else:
                                    self.logger.error("✗ 模板截取失敗")
                                    break
                        
                        if not valid_browser_found:
                            self.logger.error("沒有可用的瀏覽器")
                            break
                            
                    except ValueError:
                        self.logger.error("金額格式錯誤，請輸入有效數字（例如: 0.4）")
                    except EOFError:
                        self.logger.info("退出金額模板工具")
                        break
                    except KeyboardInterrupt:
                        self.logger.info("\n退出金額模板工具")
                        break
                    except Exception as e:
                        self.logger.error(f"截取失敗: {e}")
            
            elif cmd == 'k':
                self.logger.info("")
                self.logger.info("=== 截取黑屏模板工具 ===")
                self.logger.info("請選擇要截取的瀏覽器:")
                for i, context in enumerate(self.browser_contexts, 1):
                    if self._is_browser_alive(context.driver):
                        username = context.credential.username
                        self.logger.info(f"  {i}      - 瀏覽器 {i} ({username})")
                self.logger.info("  q      - 退出")
                self.logger.info("")
                
                try:
                    print("請輸入編號: ", end="", flush=True)
                    user_input = input().strip().lower()
                    
                    # 檢查是否要退出
                    if user_input == 'q':
                        self.logger.info("退出黑屏模板工具")
                    else:
                        # 截取指定瀏覽器
                        try:
                            browser_index = int(user_input)
                            if 1 <= browser_index <= len(self.browser_contexts):
                                context = self.browser_contexts[browser_index - 1]
                                if self._is_browser_alive(context.driver):
                                    if self.browser_operator.capture_blackscreen_template(context.driver):
                                        self.logger.info("[成功] 黑屏模板截取成功")
                                    else:
                                        self.logger.error("模板截取失敗")
                                else:
                                    self.logger.error(f"瀏覽器 {browser_index} 已關閉")
                            else:
                                self.logger.error(f"無效的瀏覽器編號: {browser_index}")
                        except ValueError:
                            self.logger.error(f"無效的輸入: {user_input}")
                            
                except EOFError:
                    self.logger.info("退出黑屏模板工具")
                except KeyboardInterrupt:
                    self.logger.info("\n退出黑屏模板工具")
                except Exception as e:
                    self.logger.error(f"截取失敗: {e}")
            
            elif cmd == 'g':
                self.logger.info("")
                self.logger.info("=== 截取返回遊戲提示模板工具 ===")
                self.logger.info("請選擇要截取的瀏覽器:")
                for i, context in enumerate(self.browser_contexts, 1):
                    if self._is_browser_alive(context.driver):
                        username = context.credential.username
                        self.logger.info(f"  {i}      - 瀏覽器 {i} ({username})")
                self.logger.info("  q      - 退出")
                self.logger.info("")
                
                try:
                    print("請輸入編號: ", end="", flush=True)
                    user_input = input().strip().lower()
                    
                    # 檢查是否要退出
                    if user_input == 'q':
                        self.logger.info("退出返回遊戲提示模板工具")
                    else:
                        # 截取指定瀏覽器
                        try:
                            browser_index = int(user_input)
                            if 1 <= browser_index <= len(self.browser_contexts):
                                context = self.browser_contexts[browser_index - 1]
                                if self._is_browser_alive(context.driver):
                                    if self.browser_operator.capture_game_return_template(context.driver):
                                        self.logger.info("[成功] 返回遊戲提示模板截取成功")
                                    else:
                                        self.logger.error("模板截取失敗")
                                else:
                                    self.logger.error(f"瀏覽器 {browser_index} 已關閉")
                            else:
                                self.logger.error(f"無效的瀏覽器編號: {browser_index}")
                        except ValueError:
                            self.logger.error(f"無效的輸入: {user_input}")
                            
                except EOFError:
                    self.logger.info("退出返回遊戲提示模板工具")
                except KeyboardInterrupt:
                    self.logger.info("\n退出返回遊戲提示模板工具")
                except Exception as e:
                    self.logger.error(f"截取失敗: {e}")
            
            elif cmd == 'y':
                self.logger.info("")
                self.logger.info("=== 截取大廳返回提示模板工具 ===")
                self.logger.info("請選擇要截取的瀏覽器:")
                for i, context in enumerate(self.browser_contexts, 1):
                    if self._is_browser_alive(context.driver):
                        username = context.credential.username
                        self.logger.info(f"  {i}      - 瀏覽器 {i} ({username})")
                self.logger.info("  q      - 退出")
                self.logger.info("")
                
                try:
                    print("請輸入編號: ", end="", flush=True)
                    user_input = input().strip().lower()
                    
                    # 檢查是否要退出
                    if user_input == 'q':
                        self.logger.info("退出大廳返回提示模板工具")
                    else:
                        # 截取指定瀏覽器
                        try:
                            browser_index = int(user_input)
                            if 1 <= browser_index <= len(self.browser_contexts):
                                context = self.browser_contexts[browser_index - 1]
                                if self._is_browser_alive(context.driver):
                                    if self.browser_operator.capture_lobby_return_template(context.driver):
                                        self.logger.info("[成功] 大廳返回提示模板截取成功")
                                    else:
                                        self.logger.error("模板截取失敗")
                                else:
                                    self.logger.error(f"瀏覽器 {browser_index} 已關閉")
                            else:
                                self.logger.error(f"無效的瀏覽器編號: {browser_index}")
                        except ValueError:
                            self.logger.error(f"無效的輸入: {user_input}")
                            
                except EOFError:
                    self.logger.info("退出大廳返回提示模板工具")
                except KeyboardInterrupt:
                    self.logger.info("\n退出大廳返回提示模板工具")
                except Exception as e:
                    self.logger.error(f"截取失敗: {e}")
            
            else:
                self.logger.warning(f"未知指令 {command}")
                self.logger.info("輸入 'h' 查看可用指令")
        
        except Exception as e:
            self.logger.error(f"執行指令時發生錯誤 {e}")
        
        return True
    
    def start(self) -> None:
        """啟動控制中心"""
        self.running = True
        self.logger.info("")
        self.logger.info("=" * 60)
        self.logger.info("           【遊戲控制中心】已啟動")
        self.logger.info("=" * 60)
        self.logger.info("")
        self.logger.info(f"[成功] 已連接 {len(self.browser_contexts)} 個瀏覽器")
        self.logger.info("")
        
        # 啟動黑屏監控功能
        threading.Thread(target=self._blackscreen_monitor_loop, daemon=True, name="BlackscreenMonitorThread").start()
        
        # 自動顯示幫助訊息
        self.show_help()
        
        # 啟動60秒自動執行計時器
        self.logger.info("")
        self.logger.info("⏰ 將在 60 秒後自動執行 'r 4' 命令（4小時規則執行）")
        self.logger.info("   如需取消，請輸入任意命令")
        self.logger.info("")
        
        def auto_execute_r4():
            """60秒後自動執行 r 4 命令"""
            if not self.user_has_input and self.running:
                self.logger.info("")
                self.logger.info("⏰ 60秒已到，自動執行 'r 4' 命令...")
                self.logger.info("")
                self.process_command("r 4")
        
        self.auto_start_timer = threading.Timer(60.0, auto_execute_r4)
        self.auto_start_timer.daemon = True
        self.auto_start_timer.start()
        
        try:
            while self.running:
                try:
                    print(">>> ", end="", flush=True)
                    command = input().strip()
                    
                    # 記錄用戶已經輸入過命令，取消自動執行
                    if not self.user_has_input:
                        self.user_has_input = True
                        if self.auto_start_timer and self.auto_start_timer.is_alive():
                            self.auto_start_timer.cancel()
                            self.logger.info("[提示] 已取消自動執行 'r 4' 命令")
                    
                    if command:
                        if not self.process_command(command):
                            break
                    else:
                        self.logger.warning("[警告] 請輸入指令（輸入 'h' 查看幫助）")
                        
                except EOFError:
                    self.logger.info("\n[警告] 檢測到 EOF，退出控制中心")
                    break
                except KeyboardInterrupt:
                    self.logger.info("\n[警告] 使用者中斷，退出控制中心")
                    break
        finally:
            # 取消自動執行計時器
            if self.auto_start_timer and self.auto_start_timer.is_alive():
                self.auto_start_timer.cancel()
            
            # 確保停止自動跳過點擊功能
            if self.auto_skip_running:
                self._stop_auto_skip_click()
            
            # 確保停止所有自動操作
            if self.auto_press_running:
                self._stop_auto_press()
            if self.rule_running:
                self._stop_rule_execution()
            
            self.running = False
            self.logger.info("[成功] 控制中心已關閉")
    
    def stop(self) -> None:
        """停止控制中心"""
        self.running = False
        
        # 確保停止自動跳過點擊功能
        if self.auto_skip_running:
            self._stop_auto_skip_click()
        
        # 確保停止自動按鍵
        if self.auto_press_running:
            self._stop_auto_press()


# ============================================================================
# 應用程式類別
# ============================================================================

class AutoSlotGameApp:
    """賽特遊戲自動化應用程式主類別。
    
    整合所有元件,提供統一的介面。
    """
    
    def __init__(
        self,
        config_reader: Optional[ConfigReader] = None,
        browser_manager: Optional[BrowserManager] = None,
        proxy_manager: Optional[LocalProxyServerManager] = None,
        browser_operator: Optional[SyncBrowserOperator] = None,
        logger: Optional[logging.Logger] = None
    ):
        """初始化應用程式。
        
        Args:
            config_reader: 配置讀取器
            browser_manager: 瀏覽器管理器
            proxy_manager: Proxy 管理器
            browser_operator: 瀏覽器操作器
            logger: 日誌記錄器
        """
        self.logger = logger or LoggerFactory.get_logger()
        self.config_reader = config_reader or ConfigReader(logger=self.logger)
        self.browser_manager = browser_manager or BrowserManager(logger=self.logger)
        self.proxy_manager = proxy_manager or LocalProxyServerManager(logger=self.logger)
        self.browser_operator = browser_operator or SyncBrowserOperator(logger=self.logger)
        
        self.credentials: List[UserCredential] = []
        self.rules: List[BetRule] = []
        self.browser_contexts: List[BrowserContext] = []
        self.image_detector = ImageDetector(logger=self.logger)
        self.recovery_manager: Optional[BrowserRecoveryManager] = None  # 延遲初始化
        self.last_canvas_rect = None  # 儲存 Canvas 區域資訊
    
    def _ensure_recovery_manager(self) -> None:
        """確保 recovery_manager 已初始化。"""
        if self.recovery_manager is None:
            self.recovery_manager = BrowserRecoveryManager(
                self.image_detector,
                self.browser_operator,
                self.logger
            )
    
    def _print_step(self, step: Union[int, str], title: str) -> None:
        """輸出步驟標題。
        
        Args:
            step: 步驟編號（整數或字串）
            title: 步驟標題
        """
        self.logger.info("")
        self.logger.info(f"步驟 {step} {title}")
        self.logger.info("")
    
    def load_configurations(self) -> None:
        """載入所有配置檔案。
        
        Raises:
            ConfigurationError: 配置載入失敗
        """
        self.logger.info("")
        self.logger.info("=" * 60)
        self.logger.info(f"【{Constants.SYSTEM_NAME}】v{Constants.VERSION}")
        self.logger.info("=" * 60)
        self.logger.info("")
        
        self.logger.info("【步驟 1/8】載入配置檔案...")
        self.logger.info("")
        
        # 讀取使用者憑證（包含 proxy 資訊）
        self.credentials = self.config_reader.read_user_credentials()
        self.logger.info(f"  > 已載入 {len(self.credentials)} 個使用者帳號")
        
        # 讀取下注規則
        self.rules = self.config_reader.read_bet_rules()
        self.logger.info(f"  > 已載入 {len(self.rules)} 條下注規則")
        
        self.logger.info("")
        self.logger.info(f"[成功] 配置載入完成")
        self.logger.info("")
    
    def auto_determine_browser_count(self) -> int:
        """自動決定要開啟的瀏覽器數量（根據用戶資料檔案）。
        
        Returns:
            瀏覽器數量
        """
        max_browsers = len(self.credentials)
        
        if max_browsers == 0:
            raise ConfigurationError("[錯誤] 沒有可用的使用者憑證，請檢查 lib/用戶資料.txt")
        
        self.logger.info("【步驟 2/8】確定瀏覽器數量")
        self.logger.info("")
        
        # 如果帳號數量超過 12，提示用戶並限制為 12
        if max_browsers > 12:
            self.logger.warning(f"[警告] 偵測到 {max_browsers} 個帳號，但系統最多支援 12 個瀏覽器")
            self.logger.warning(f"[警告] 將自動使用前 12 組帳號進行運行")
            self.logger.info("")
            browser_count = 12
        else:
            browser_count = max_browsers
        
        self.logger.info(f"[成功] 已確定開啟 {browser_count} 個瀏覽器")
        self.logger.info("")
        return browser_count
    
    def setup_proxy_servers(self, browser_count: int) -> List[Optional[int]]:
        """設定 Proxy 中繼伺服器（同步啟動）。
        
        Args:
            browser_count: 瀏覽器數量
            
        Returns:
            Proxy 埠號列表
        """
        self.logger.info("【步驟 3/8】啟動 Proxy 中繼伺服器")
        self.logger.info("")
        
        proxy_ports: List[Optional[int]] = [None] * browser_count
        
        def start_single_proxy_server(
            index: int,
            credential: UserCredential
        ) -> Tuple[int, Optional[int]]:
            """在執行緒中啟動單個 Proxy 伺服器"""
            local_proxy_port = None
            
            if credential.proxy:
                try:
                    # 解析 proxy 字串
                    parts = credential.proxy.split(':')
                    if len(parts) >= 4:
                        proxy_info = ProxyInfo(
                            host=parts[0],
                            port=int(parts[1]),
                            username=parts[2],
                            password=':'.join(parts[3:])
                        )
                        
                        local_proxy_port = self.proxy_manager.start_proxy_server(proxy_info)
                        
                        if not local_proxy_port:
                            self.logger.warning(
                                f"[警告] 瀏覽器 {index+1}: Proxy 啟動失敗，將使用直連"
                            )
                    else:
                        self.logger.warning(f"[警告] 瀏覽器 {index+1}: Proxy 格式錯誤，將使用直連")
                        
                except Exception as e:
                    self.logger.error(f"[錯誤] 瀏覽器 {index+1}: Proxy 設定失敗 - {e}")
            
            return index, local_proxy_port
        
        # 使用執行緒池同步啟動所有 Proxy 伺服器
        with ThreadPoolExecutor(max_workers=Constants.MAX_THREAD_WORKERS) as executor:
            futures = []
            for i in range(browser_count):
                future = executor.submit(
                    start_single_proxy_server,
                    i,
                    self.credentials[i]
                )
                futures.append(future)
            
            # 收集結果
            for future in as_completed(futures):
                index, local_proxy_port = future.result()
                proxy_ports[index] = local_proxy_port
        
        active_count = sum(1 for p in proxy_ports if p is not None)
        direct_count = len(proxy_ports) - active_count
        
        self.logger.info(f"[成功] Proxy 設定完成")
        self.logger.info(f"  > {active_count} 個使用 Proxy 中繼")
        self.logger.info(f"  > {direct_count} 個使用直連")
        self.logger.info("")
        
        return proxy_ports
    
    def create_browser_instances(
        self,
        browser_count: int,
        proxy_ports: List[Optional[int]]
    ) -> List[BrowserContext]:
        """建立瀏覽器實例（優化版）。
        
        Args:
            browser_count: 瀏覽器數量
            proxy_ports: Proxy 埠號列表
            
        Returns:
            瀏覽器上下文列表
        """
        self.logger.info("【步驟 4/8】建立瀏覽器實例")
        self.logger.info("")
        
        browser_results: List[Optional[BrowserContext]] = [None] * browser_count
        
        def create_browser_instance(
            index: int,
            credential: UserCredential,
            proxy_port: Optional[int]
        ) -> Tuple[int, Optional[BrowserContext]]:
            """在執行緒中建立瀏覽器實例"""
            try:
                driver = self.browser_manager.create_webdriver(local_proxy_port=proxy_port)
                
                context = BrowserContext(
                    driver=driver,
                    credential=credential,
                    index=index + 1,
                    proxy_port=proxy_port
                )
                
                return index, context
                
            except Exception as e:
                self.logger.error(f"[錯誤] 瀏覽器 {index+1}/{browser_count} 建立失敗: {e}")
                return index, None
        
        # 使用執行緒池建立瀏覽器
        with ThreadPoolExecutor(max_workers=Constants.MAX_THREAD_WORKERS) as executor:
            futures = [
                executor.submit(create_browser_instance, i, self.credentials[i], proxy_ports[i])
                for i in range(browser_count)
            ]
            
            # 收集結果
            for future in as_completed(futures):
                index, context = future.result()
                browser_results[index] = context
        
        # 過濾成功建立的瀏覽器
        contexts = [context for context in browser_results if context is not None]
        
        if len(contexts) == browser_count:
            self.logger.info(f"[成功] 瀏覽器建立完成: 成功建立 {len(contexts)} 個")
        else:
            self.logger.warning(f"[警告] 部分瀏覽器建立失敗")
            self.logger.warning(f"  > 成功: {len(contexts)} 個")
            self.logger.warning(f"  > 失敗: {browser_count - len(contexts)} 個")
        
        self.logger.info("")
        return contexts
    
    def run(self) -> None:
        """執行主程式流程。
        
        Raises:
            Exception: 執行過程中的錯誤
        """
        try:
            # 載入配置
            self.load_configurations()
            
            # 自動決定瀏覽器數量
            browser_count = self.auto_determine_browser_count()
            
            # 設定 Proxy 伺服器
            proxy_ports = self.setup_proxy_servers(browser_count)
            
            # 建立瀏覽器實例
            self.browser_contexts = self.create_browser_instances(browser_count, proxy_ports)
            
            if not self.browser_contexts:
                raise BrowserCreationError("[錯誤] 沒有成功建立任何瀏覽器實例")
            
            # 步驟 5: 導航到登入頁面
            self.logger.info("【步驟 5/8】導航到登入頁面")
            self.logger.info("")
            login_results = self.browser_operator.navigate_to_login_page(
                self.browser_contexts
            )
            self.logger.info("[成功] 登入頁面載入完成")
            self.logger.info("")
            time.sleep(Constants.DEFAULT_WAIT_SECONDS)
            
            # 步驟 6: 執行登入操作（同步）
            self.logger.info("【步驟 6/8】執行登入操作")
            self.logger.info("")
            login_results = self.browser_operator.perform_login_all(
                self.browser_contexts
            )
            self.logger.info("[成功] 登入操作完成")
            self.logger.info("")
            time.sleep(Constants.DEFAULT_WAIT_SECONDS)
            
            # 步驟 7: 導航到遊戲頁面
            self.logger.info("【步驟 7/8】導航到遊戲頁面")
            self.logger.info("")
            game_results = self.browser_operator.navigate_to_game_page(
                self.browser_contexts
            )
            self.logger.info("[成功] 遊戲頁面載入完成")
            self.logger.info("")
            time.sleep(Constants.DEFAULT_WAIT_SECONDS)
            
            # 步驟 8: 調整視窗排列
            self.logger.info(f"【步驟 8/8】調整視窗排列 ({Constants.DEFAULT_WINDOW_WIDTH}x{Constants.DEFAULT_WINDOW_HEIGHT})")
            self.logger.info("")
            resize_results = self.browser_operator.resize_and_arrange_all(
                self.browser_contexts,
                width=Constants.DEFAULT_WINDOW_WIDTH,
                height=Constants.DEFAULT_WINDOW_HEIGHT,
                columns=Constants.DEFAULT_WINDOW_COLUMNS
            )
            self.logger.info("[成功] 視窗排列完成")
            self.logger.info("")
            time.sleep(Constants.DEFAULT_WAIT_SECONDS)
            
            # 圖片檢測與遊戲流程
            self.logger.info("=" * 60)
            self.logger.info("【圖片檢測與遊戲初始化】")
            self.logger.info("=" * 60)
            self.logger.info("")
            self._execute_image_detection_flow()
            
            # 啟動遊戲控制中心
            self.logger.info("")
            self.logger.info("=" * 60)
            self.logger.info("【遊戲控制中心】")
            self.logger.info("=" * 60)
            self.logger.info("")
            control_center = GameControlCenter(
                browser_contexts=self.browser_contexts,
                browser_operator=self.browser_operator,
                bet_rules=self.rules,
                logger=self.logger
            )
            control_center.start()
            
        except KeyboardInterrupt:
            self.logger.warning("\n[警告] 使用者中斷程式執行")
        except Exception as e:
            self.logger.error(f"[錯誤] 系統發生錯誤: {e}", exc_info=True)
            raise
        finally:
            self.cleanup()
    
    def _execute_image_detection_flow(self) -> None:
        """執行圖片檢測流程。
        
        包含 lobby_login 和 lobby_confirm 的檢測與處理。
        """
        if not self.browser_contexts:
            self.logger.error("[錯誤] 沒有可用的瀏覽器實例")
            return
        
        # 使用第一個瀏覽器作為參考
        reference_browser = self.browser_contexts[0]
        
        # 階段 1: 處理 lobby_login
        self.logger.info("【階段 1】檢測 lobby_login 畫面")
        self.logger.info("")
        self._handle_lobby_login(reference_browser)
        
        # 階段 2: 處理 lobby_confirm
        self.logger.info("")
        self.logger.info("【階段 2】檢測 lobby_confirm 畫面")
        self.logger.info("")
        self._handle_lobby_confirm(reference_browser)
        
        self.logger.info("")
        self.logger.info("[成功] 圖片檢測與初始化完成")
        self.logger.info("")
    
    def _handle_lobby_image(
        self, 
        reference_browser: BrowserContext, 
        template_name: str, 
        display_name: str
    ) -> None:
        """處理 lobby 圖片的檢測與點擊（通用方法）。
        
        Args:
            reference_browser: 參考瀏覽器
            template_name: 模板檔名
            display_name: 顯示名稱
        """
        # 1. 檢查模板是否存在
        if not self.image_detector.template_exists(template_name):
            self.logger.warning(f"模板圖片 {template_name} 不存在")
            self._prompt_capture_template(reference_browser, template_name, display_name)
        else:
            self.logger.info(f"找到模板圖片 {template_name}")
        
        # 2. 持續檢測直到找到圖片
        self.logger.info(f"正在檢測 {display_name}")
        detection_results = self._continuous_detect_until_found(template_name, display_name)
        
        # 3. 自動執行點擊
        self._auto_click(display_name, detection_results)
        
        # 4. 等待圖片消失
        self._wait_for_image_disappear(template_name)
        self.logger.info(f"{display_name} 已消失")
    
    def _handle_lobby_login(self, reference_browser: BrowserContext) -> None:
        """處理 lobby_login 的檢測與點擊。
        
        Args:
            reference_browser: 參考瀏覽器
        """
        # 1. 檢查模板是否存在
        template_name = Constants.LOBBY_LOGIN
        display_name = "lobby_login"
        
        if not self.image_detector.template_exists(template_name):
            self.logger.warning(f"模板圖片 {template_name} 不存在")
            self._prompt_capture_template(reference_browser, template_name, display_name)
        
        # 2. 持續檢測直到所有瀏覽器都找到圖片
        detection_results = self._continuous_detect_until_found(template_name, display_name)
        
        # 3. 使用 Canvas 比例計算座標並點擊
        time.sleep(Constants.TEMPLATE_CAPTURE_WAIT)
        
        def click_with_canvas_ratio_operation(context: BrowserContext, index: int, total: int) -> bool:
            """使用 Canvas 比例計算座標並點擊"""
            try:
                # 取得 Canvas 區域
                try:
                    rect = context.driver.execute_script(f"""
                        const canvas = document.getElementById('{Constants.GAME_CANVAS}');
                        const r = canvas.getBoundingClientRect();
                        return {{x: r.left, y: r.top, w: r.width, h: r.height}};
                    """)
                except Exception as e:
                    self.logger.error(f"瀏覽器 {index + 1} 取得 Canvas 座標失敗: {e}")
                    return False
                
                # 使用比例計算點擊座標
                click_x = rect["x"] + rect["w"] * Constants.LOBBY_LOGIN_BUTTON_X_RATIO
                click_y = rect["y"] + rect["h"] * Constants.LOBBY_LOGIN_BUTTON_Y_RATIO
                
                # 執行點擊
                self._click_coordinate(context.driver, click_x, click_y)
                self.logger.info(f"瀏覽器 {index + 1} 已點擊 {display_name} (座標: {click_x:.0f}, {click_y:.0f})")
                return True
            except Exception as e:
                self.logger.error(f"瀏覽器 {index + 1} 點擊失敗: {e}")
                return False
        
        click_results = self.browser_operator.execute_sync(
            self.browser_contexts,
            click_with_canvas_ratio_operation,
            f"點擊 {display_name}"
        )
        
        # 4. 等待所有瀏覽器中的圖片消失
        self._wait_for_image_disappear(template_name)
    
    def _handle_lobby_confirm(self, reference_browser: BrowserContext) -> None:
        """處理 lobby_confirm 的檢測與點擊。
        
        Args:
            reference_browser: 參考瀏覽器
        """
        # 1. 檢查模板是否存在
        template_name = Constants.LOBBY_CONFIRM
        display_name = "lobby_confirm"
        
        if not self.image_detector.template_exists(template_name):
            self.logger.warning(f"模板圖片 {template_name} 不存在")
            self._prompt_capture_template(reference_browser, template_name, display_name)
        
        # 2. 持續檢測直到所有瀏覽器都找到圖片
        detection_results = self._continuous_detect_until_found(template_name, display_name)
        
        # 3. 使用 Canvas 比例計算座標並點擊
        time.sleep(Constants.TEMPLATE_CAPTURE_WAIT)
        
        # 保存 Canvas rect 供後續使用（只需取得一次，所有瀏覽器的 Canvas rect 應該相同）
        canvas_rect_saved = False
        
        def click_with_canvas_ratio_operation(context: BrowserContext, index: int, total: int) -> bool:
            """使用 Canvas 比例計算座標並點擊"""
            nonlocal canvas_rect_saved
            try:
                # 取得 Canvas 區域
                try:
                    rect = context.driver.execute_script(f"""
                        const canvas = document.getElementById('{Constants.GAME_CANVAS}');
                        const r = canvas.getBoundingClientRect();
                        return {{x: r.left, y: r.top, w: r.width, h: r.height}};
                    """)
                    
                    # 保存 Canvas rect 到 GameAutomat 和 SyncBrowserOperator（只保存一次）
                    if not canvas_rect_saved:
                        self.last_canvas_rect = rect
                        self.browser_operator.last_canvas_rect = rect
                        canvas_rect_saved = True
                        self.logger.debug(f"已保存 Canvas 區域資訊: {rect}")
                        
                except Exception as e:
                    self.logger.error(f"瀏覽器 {index + 1} 取得 Canvas 座標失敗: {e}")
                    return False
                
                # 使用比例計算點擊座標
                click_x = rect["x"] + rect["w"] * Constants.LOBBY_CONFIRM_BUTTON_X_RATIO
                click_y = rect["y"] + rect["h"] * Constants.LOBBY_CONFIRM_BUTTON_Y_RATIO
                
                # 執行點擊
                self._click_coordinate(context.driver, click_x, click_y)
                self.logger.info(f"瀏覽器 {index + 1} 已點擊 {display_name} (座標: {click_x:.0f}, {click_y:.0f})")
                return True
            except Exception as e:
                self.logger.error(f"瀏覽器 {index + 1} 點擊失敗: {e}")
                return False
        
        click_results = self.browser_operator.execute_sync(
            self.browser_contexts,
            click_with_canvas_ratio_operation,
            f"點擊 {display_name}"
        )
        
        # 4. 等待所有瀏覽器中的圖片消失
        self._wait_for_image_disappear(template_name)
        
        # 5. 所有瀏覽器都成功進入遊戲
        self.logger.info("[成功] 所有瀏覽器已準備就緒")
        time.sleep(Constants.DETECTION_COMPLETE_WAIT)
    
    def _wait_for_lobby_confirm_with_error_handling(self) -> None:
        """等待 lobby_confirm 出現，包含錯誤訊息檢測和自動重啟邏輯（同步版本）。
        
        流程：
        1. 同步檢測所有瀏覽器的 lobby_confirm（前 3 次）
        2. 如果未找到，同步檢測錯誤訊息
        3. 如果檢測到錯誤且持續超過設定秒數，同步重啟所有錯誤的瀏覽器
        4. 重複直到所有瀏覽器都顯示 lobby_confirm
        """
        self._ensure_recovery_manager()  # 確保 recovery_manager 已初始化
        
        template_name = Constants.LOBBY_CONFIRM
        total_browsers = len(self.browser_contexts)
        browser_states = {}  # 記錄每個瀏覽器的狀態
        
        # 初始化瀏覽器狀態
        for i in range(1, total_browsers + 1):
            browser_states[i] = {
                'found_confirm': False,
                'error_start_time': None,
                'lobby_confirm_attempts': 0
            }
        
        self.logger.info("開始檢測 lobby_confirm（包含錯誤訊息監控）")
        last_progress = -1
        
        while True:
            # 同步檢測所有待處理的瀏覽器
            pending_browsers = [
                i for i in range(1, total_browsers + 1)
                if not browser_states[i]['found_confirm']
            ]
            
            if not pending_browsers:
                self.logger.info("[成功] 所有瀏覽器都已檢測到 lobby_confirm")
                break
            
            # 檢測 lobby_confirm 和錯誤訊息
            current_time = time.time()
            errors_to_restart = []
            new_errors = []
            
            for i in pending_browsers:
                context = self.browser_contexts[i - 1]
                browser_states[i]['lobby_confirm_attempts'] += 1
                
                try:
                    # 檢測 lobby_confirm
                    result = self.image_detector.detect_in_browser(
                        context.driver,
                        template_name
                    )
                    
                    if result:
                        # 找到 lobby_confirm
                        browser_states[i]['found_confirm'] = True
                        browser_states[i]['error_start_time'] = None
                        continue
                    
                except Exception as e:
                    self.logger.error(f"瀏覽器 {i} 檢測過程發生錯誤: {e}")
            
            # 檢查是否有需要重整的瀏覽器（移除錯誤檢測相關邏輯後，此處可能沒有輸出）
            # 輸出新檢測到的錯誤（已移除）
            if new_errors:
                self.logger.warning(f"檢測到錯誤訊息: 瀏覽器 {', '.join(map(str, new_errors))}")
            
            # 同步重啟所有需要重啟的瀏覽器
            if errors_to_restart:
                self.logger.error(f"執行重啟: 瀏覽器 {', '.join(map(str, errors_to_restart))}")
                self._restart_browsers_simple(errors_to_restart, browser_states)
            
            # 顯示進度（只在變化時輸出）
            found_count = sum(1 for state in browser_states.values() if state['found_confirm'])
            if found_count != last_progress:
                if found_count > 0:
                    self.logger.info(f"進度: {found_count}/{total_browsers} 個瀏覽器已就緒")
                last_progress = found_count
            
            time.sleep(Constants.DETECTION_INTERVAL)
    
    def _restart_browsers_simple(
        self,
        browser_indices: List[int],
        browser_states: dict
    ) -> None:
        """簡化的瀏覽器重啟流程。
        
        Args:
            browser_indices: 需要重啟的瀏覽器索引列表
            browser_states: 瀏覽器狀態字典
        """
        if not browser_indices or not self.last_canvas_rect:
            return
        
        self._ensure_recovery_manager()
        
        # 準備需要重啟的瀏覽器上下文
        contexts_to_restart = [
            self.browser_contexts[i - 1]
            for i in browser_indices
        ]
        
        # 使用 recovery_manager 執行重啟和恢復
        success = self.recovery_manager.restart_and_recover(
            contexts_to_restart,
            self.last_canvas_rect
        )
        
        if success:
            # 重置狀態
            for i in browser_indices:
                browser_states[i]['error_start_time'] = None
                browser_states[i]['lobby_confirm_attempts'] = 0
            
            browser_list = ', '.join(map(str, browser_indices))
            self.logger.info(f"[成功] 瀏覽器 {browser_list} 已重啟並等待 lobby_confirm")
        else:
            self.logger.error("瀏覽器重啟失敗")
    
    def _click_coordinate(self, driver: WebDriver, x: float, y: float) -> None:
        """點擊指定座標。
        
        Args:
            driver: WebDriver 實例
            x: X座標
            y: Y座標
        """
        BrowserHelper.execute_cdp_click(driver, x, y)
    
    def _auto_capture_lobby_confirm(self, reference_browser: BrowserContext) -> None:
        """自動截取 lobby_confirm 模板圖片。
        
        使用已知的確認按鈕座標自動截取模板。
        
        Args:
            reference_browser: 參考瀏覽器
        """
        try:
            # 取得確認按鈕座標
            rect = self.last_canvas_rect
            confirm_x = rect["x"] + rect["w"] * Constants.LOBBY_CONFIRM_BUTTON_X_RATIO
            confirm_y = rect["y"] + rect["h"] * Constants.LOBBY_CONFIRM_BUTTON_Y_RATIO
            
            # 截取畫面
            screenshot = reference_browser.driver.get_screenshot_as_png()
            screenshot_img = Image.open(io.BytesIO(screenshot))
            
            # 獲取實際截圖尺寸
            image_width, image_height = screenshot_img.size
            
            center_x = int(confirm_x)
            center_y = int(confirm_y)
            
            # 固定像素偏移（使用常數定義）
            crop_left = max(0, center_x - Constants.TEMPLATE_CROP_MARGIN)
            crop_top = max(0, center_y - Constants.TEMPLATE_CROP_MARGIN)
            crop_right = min(image_width, center_x + Constants.TEMPLATE_CROP_MARGIN)
            crop_bottom = min(image_height, center_y + Constants.TEMPLATE_CROP_MARGIN)
            
            cropped_img = screenshot_img.crop((crop_left, crop_top, crop_right, crop_bottom))
            
            # 儲存圖片
            template_path = self.image_detector.get_template_path(Constants.LOBBY_CONFIRM)
            template_path.parent.mkdir(parents=True, exist_ok=True)
            cropped_img.save(template_path)
            
            self.logger.info("[成功] 模板建立成功")
            
        except Exception as e:
            self.logger.error(f"自動建立 lobby_confirm.png 失敗: {e}")
            raise
    
    def _prompt_capture_template(self, reference_browser: BrowserContext, template_name: str, display_name: str) -> None:
        """提示用戶截取模板圖片。
        
        Args:
            reference_browser: 參考瀏覽器
            template_name: 模板檔名
            display_name: 顯示名稱
        """
        self.logger.info(f"[警告] 模板圖片不存在: {template_name}")
        self.logger.info("")
        self.logger.info(f"[提示] 需要截取 {display_name} 的參考圖片")
        self.logger.info("   請確保遊戲畫面已顯示目標內容")
        print(f"\n按 Enter 鍵開始截取第一個瀏覽器的畫面...", end="", flush=True)
        
        try:
            input()
            
            # 截取並儲存模板
            template_path = self.image_detector.get_template_path(template_name)
            self.image_detector.capture_screenshot(reference_browser.driver, template_path)
            self.logger.info(f"[成功] 模板圖片已建立: {template_path}")
            self.logger.info("")
            
        except (EOFError, KeyboardInterrupt):
            self.logger.warning("\n[警告] 使用者取消截圖")
            raise
    
    def _handle_image_not_found(self, reference_browser: BrowserContext, template_name: str, display_name: str) -> None:
        """處理圖片未檢測到的情況，提供選項讓用戶重新截圖或跳過。
        
        Args:
            reference_browser: 參考瀏覽器
            template_name: 模板檔名
            display_name: 顯示名稱
        """
        self.logger.info("當前模板圖片可能與實際畫面不符")
        self.logger.info("選項")
        self.logger.info(f"  1 重新截取 {display_name} 模板圖片")
        self.logger.info("  2 等待並重新檢測")
        self.logger.info("  3 跳過此階段")
        
        while True:
            try:
                print(f"\n請選擇 (1/2/3): ", end="", flush=True)
                choice = input().strip()
                
                if choice == "1":
                    # 重新截取模板
                    self.logger.info(f"準備重新截取 {display_name} 模板")
                    self._prompt_capture_template(reference_browser, template_name, display_name)
                    
                    # 重新檢測
                    self.logger.info("使用新模板重新檢測")
                    detection_results = self._detect_in_all_browsers(template_name)
                    found_count = sum(1 for result in detection_results if result is not None)
                    
                    if found_count > 0:
                        self.logger.info(f"檢測到 {found_count}/{len(self.browser_contexts)} 個瀏覽器中有 {display_name}")
                        self._prompt_user_click(display_name, detection_results)
                        self.logger.info(f"等待 {display_name} 消失")
                        self._wait_for_image_disappear(template_name)
                        self.logger.info(f"{display_name} 已消失")
                        return
                    else:
                        self.logger.warning(f"仍未檢測到 {display_name} 請重新選擇")
                        continue
                
                elif choice == "2":
                    # 等待並重新檢測
                    self.logger.info(f"等待 {display_name} 出現")
                    self.logger.info("持續檢測中 每3秒檢測一次 按 Ctrl+C 可中斷")
                    
                    try:
                        for attempt in range(Constants.DETECTION_WAIT_MAX_ATTEMPTS):
                            time.sleep(Constants.DEFAULT_WAIT_SECONDS)
                            detection_results = self._detect_in_all_browsers(template_name)
                            found_count = sum(1 for result in detection_results if result is not None)
                            
                            if found_count > 0:
                                self.logger.info(f"檢測到 {found_count}/{len(self.browser_contexts)} 個瀏覽器中有 {display_name}")
                                self._prompt_user_click(display_name, detection_results)
                                self.logger.info(f"等待 {display_name} 消失")
                                self._wait_for_image_disappear(template_name)
                                self.logger.info(f"{display_name} 已消失")
                                return
                            
                            if (attempt + 1) % 5 == 0:
                                self.logger.info(f"檢測進度 {attempt + 1}/{Constants.DETECTION_WAIT_MAX_ATTEMPTS} 次 仍未找到")
                        
                        self.logger.warning(f"等待超時 未檢測到 {display_name}")
                        continue
                        
                    except KeyboardInterrupt:
                        self.logger.info("用戶中斷等待")
                        continue
                
                elif choice == "3":
                    # 跳過此階段
                    self.logger.info("已跳過該階段")
                    return
                
                else:
                    self.logger.warning("無效的選擇 請輸入 1 2 或 3")
                    continue
                    
            except (EOFError, KeyboardInterrupt):
                self.logger.warning("用戶中斷操作")
                raise
    
    def _continuous_detect_until_found(self, template_name: str, display_name: str) -> List[Optional[Tuple[int, int, float]]]:
        """持續檢測直到在所有瀏覽器中找到圖片。
        
        Args:
            template_name: 模板圖片檔名
            display_name: 顯示名稱
            
        Returns:
            檢測結果列表 (每個元素為 None 或 (x, y, confidence))
        """
        attempt = 0
        total_browsers = len(self.browser_contexts)
        
        self.logger.info(f"[檢測] 開始檢測 {display_name}...")
        
        while True:
            attempt += 1
            detection_results = self._detect_in_all_browsers(template_name, silent=True)
            found_count = sum(1 for result in detection_results if result is not None)
            
            # 只有當所有瀏覽器都找到圖片時才返回
            if found_count == total_browsers:
                # 顯示最終找到的座標
                self.logger.info(f"[成功] 所有瀏覽器都已檢測到 {display_name}")
                return detection_results
            
            # 每 N 次檢測顯示一次進度
            if attempt % Constants.DETECTION_PROGRESS_INTERVAL == 0:
                self.logger.info(f"   檢測進度: {found_count}/{total_browsers} 個瀏覽器已就緒")
            
            time.sleep(Constants.DETECTION_INTERVAL)
    
    def _detect_in_all_browsers(self, template_name: str, silent: bool = False) -> List[Optional[Tuple[int, int, float]]]:
        """在所有瀏覽器中檢測模板圖片。
        
        Args:
            template_name: 模板圖片檔名
            silent: 是否靜默模式(不輸出log)
            
        Returns:
            檢測結果列表 (每個元素為 None 或 (x, y, confidence))
        """
        results: List[Optional[Tuple[int, int, float]]] = []
        
        for i, context in enumerate(self.browser_contexts, 1):
            try:
                result = self.image_detector.detect_in_browser(
                    context.driver,
                    template_name
                )
                
                if result and not silent:
                    x, y, confidence = result
                    self.logger.info(f"瀏覽器 {i}/{len(self.browser_contexts)} 找到圖片 座標 {x} {y} 信心度 {confidence:.2f}")
                
                results.append(result)
                
            except ImageDetectionError as e:
                if not silent:
                    self.logger.error(f"瀏覽器 {i}/{len(self.browser_contexts)} 圖片檢測錯誤: {e}")
                results.append(None)
            except Exception as e:
                if not silent:
                    self.logger.error(f"瀏覽器 {i}/{len(self.browser_contexts)} 未預期錯誤: {e}")
                results.append(None)
        
        return results
    
    def _auto_click(self, display_name: str, detection_results: List[Optional[Tuple[int, int, float]]]) -> None:
        """自動執行點擊操作。
        
        Args:
            display_name: 顯示名稱
            detection_results: 檢測結果列表
        """
        self.logger.info(f"找到 {display_name}，自動執行點擊操作")
        
        def click_operation(context: BrowserContext, index: int, total: int) -> bool:
            """在單個瀏覽器中執行點擊操作"""
            result = detection_results[index - 1]
            if result is None:
                return False
            
            x, y, confidence = result
            
            try:
                BrowserHelper.execute_cdp_click(context.driver, x, y)
                self.logger.debug(f"瀏覽器 {index} 在座標 ({x}, {y}) 執行點擊成功")
                return True
            except Exception as e:
                self.logger.error(f"瀏覽器 {index} 點擊失敗: {e}")
                return False
        
        # 同步執行所有點擊
        self.browser_operator.execute_sync(
            self.browser_contexts,
            click_operation,
            f"點擊 {display_name}"
        )
    
    def _wait_for_image_disappear(self, template_name: str) -> None:
        """持續等待圖片在所有瀏覽器中消失。
        
        Args:
            template_name: 模板圖片檔名
        """
        attempt = 0
        total_browsers = len(self.browser_contexts)
        
        while True:
            attempt += 1
            
            # 檢測所有瀏覽器
            still_present = []
            for i, context in enumerate(self.browser_contexts, 1):
                try:
                    result = self.image_detector.detect_in_browser(
                        context.driver,
                        template_name
                    )
                    if result:
                        still_present.append(i)
                except Exception as e:
                    self.logger.debug(f"瀏覽器 {i} 檢測失敗 {e}")
            
            disappeared_count = total_browsers - len(still_present)
            
            # 如果所有瀏覽器都沒有找到圖片，則返回
            if not still_present:
                self.logger.info(f"[成功] 圖片已消失")
                return
            
            # 每 10 次檢測顯示一次進度
            if attempt % 10 == 0:
                self.logger.info(f"等待中... ({disappeared_count}/{total_browsers} 已消失)")
            
            # 等待後再次檢測
            time.sleep(Constants.DETECTION_INTERVAL)
    
    def cleanup(self) -> None:
        """清理所有資源（優化版）"""
        self.logger.info("正在清理資源...")
        
        # 1. 關閉所有瀏覽器
        if self.browser_contexts:
            try:
                self.browser_operator.close_all(self.browser_contexts)
            except Exception as e:
                self.logger.error(f"關閉瀏覽器時發生錯誤: {e}")
            finally:
                self.browser_contexts.clear()
        
        # 2. 停止所有 Proxy 伺服器
        try:
            self.proxy_manager.stop_all_servers()
        except Exception as e:
            self.logger.error(f"停止 Proxy 伺服器時發生錯誤: {e}")
        
        self.logger.info("[成功] 清理完成")


# ============================================================================
# 主程式入口
# ============================================================================

def main() -> None:
    """主程式入口函式。
    
    初始化並執行應用程式。
    """
    logger = LoggerFactory.get_logger()
    
    # 在程式啟動前清除所有緩存的 chromedriver 程序
    cleanup_chromedriver_processes()
    
    try:
        app = AutoSlotGameApp()
        app.run()
    except KeyboardInterrupt:
        logger.warning("使用者中斷程式執行")
        sys.exit(0)
    except ConfigurationError as e:
        logger.critical(f"配置錯誤: {e}")
        sys.exit(1)
    except BrowserCreationError as e:
        logger.critical(f"瀏覽器建立失敗: {e}")
        sys.exit(1)
    except ProxyServerError as e:
        logger.critical(f"Proxy 伺服器錯誤: {e}")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"應用程式執行失敗: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
