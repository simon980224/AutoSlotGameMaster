"""
系統常數定義

包含所有系統範圍內使用的常數，避免硬編碼。
"""


class Constants:
    """系統常量"""
    # 版本資訊
    VERSION = "2.0.0"
    SYSTEM_NAME = "賽特遊戲自動化系統"
    
    DEFAULT_LIB_PATH = "lib"
    DEFAULT_CREDENTIALS_FILE = "用戶資料.txt"
    DEFAULT_RULES_FILE = "用戶規則.txt"
    
    # Proxy 配置（Brightdata）
    PROXY_HOST = "brd.superproxy.io"
    PROXY_PORT = 33335
    PROXY_USERNAME_BASE = "brd-customer-hl_aa7b7b79-zone-isp_proxy2"
    PROXY_PASSWORD = "a2d0f4cabz6r"
    
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
    LOGIN_PAGE = "https://www.fin88.app/"
    GAME_PAGE = "https://www.fin88.app/"

    # 頁面元素選擇器
    INITIAL_LOGIN_BUTTON = "//button[contains(@class, 'btn') and contains(@class, 'login') and contains(@class, 'pc') and text()='登入']"
    USERNAME_INPUT = "//input[@placeholder='請輸入帳號/手機號']"
    PASSWORD_INPUT = "//input[@placeholder='請輸入您的登入密碼']"
    LOGIN_BUTTON = "//button[contains(@class, 'custom-button') and @type='submit' and text()='登入遊戲']"
    POPUP_CLOSE_BUTTON = "//button[contains(@class, 'btn-close')]"
    SEARCH_BUTTON = "//button[contains(@class, 'search-btn')]"
    SEARCH_INPUT = "//input[@placeholder='按換行鍵搜索']"
    GAME_XPATH = "//div[contains(@class, 'game-card-container') and .//div[contains(@style, 'ATG-egyptian-mythology.png')]]"
    GAME_IFRAME = "//iframe[contains(@class, 'iframe-item')]"
    GAME_CANVAS = "GameCanvas"
    
    # 圖片檢測配置
    IMAGE_DIR = "img"
    LOBBY_LOGIN = "lobby_login.png"
    LOBBY_CONFIRM = "lobby_confirm.png"
    LOBBY_RETURN = "lobby_return.png"
    GAME_RETURN = "game_return.png"
    BLACK_SCREEN = "black_screen.png"
    MATCH_THRESHOLD = 0.8
    BETSIZE_MATCH_THRESHOLD = 0.85
    DETECTION_INTERVAL = 1.0
    MAX_DETECTION_ATTEMPTS = 60
    
    # Canvas 動態計算比例（用於點擊座標）
    LOBBY_LOGIN_BUTTON_X_RATIO = 0.5
    LOBBY_LOGIN_BUTTON_Y_RATIO = 0.9
    
    LOBBY_CONFIRM_BUTTON_X_RATIO = 0.74
    LOBBY_CONFIRM_BUTTON_Y_RATIO = 0.85
    
    BUY_FREE_GAME_BUTTON_X_RATIO = 0.15
    BUY_FREE_GAME_BUTTON_Y_RATIO = 0.75
    BUY_FREE_GAME_CONFIRM_X_RATIO = 0.65
    BUY_FREE_GAME_CONFIRM_Y_RATIO = 0.9
    BUY_FREE_GAME_WAIT_SECONDS = 10
    
    GAME_CONFIRM_BUTTON_X_RATIO = 0.5
    GAME_CONFIRM_BUTTON_Y_RATIO = 0.55
    
    AUTO_SPIN_BUTTON_X_RATIO = 0.8
    AUTO_SPIN_BUTTON_Y_RATIO = 0.77
    AUTO_SPIN_10_X_RATIO = 0.4
    AUTO_SPIN_10_Y_RATIO = 0.5
    AUTO_SPIN_50_X_RATIO = 0.5
    AUTO_SPIN_50_Y_RATIO = 0.5
    AUTO_SPIN_100_X_RATIO = 0.57
    AUTO_SPIN_100_Y_RATIO = 0.5
    
    # 操作相關常量
    DEFAULT_WAIT_SECONDS = 3
    DETECTION_PROGRESS_INTERVAL = 20
    
    # 操作等待時間（秒）
    LOGIN_WAIT_TIME = 5
    BETSIZE_ADJUST_STEP_WAIT = 3.0
    BETSIZE_ADJUST_VERIFY_WAIT = 2.0
    BETSIZE_ADJUST_RETRY_WAIT = 1.0
    BETSIZE_READ_RETRY_WAIT = 0.5
    FREE_GAME_CLICK_WAIT = 2
    FREE_GAME_SETTLE_INITIAL_WAIT = 3
    FREE_GAME_SETTLE_CLICK_INTERVAL = 3
    AUTO_SPIN_MENU_WAIT = 0.5
    PROXY_SERVER_START_WAIT = 1
    TEMPLATE_CAPTURE_WAIT = 1
    DETECTION_COMPLETE_WAIT = 2
    RULE_SWITCH_WAIT = 1.0
    AUTO_PRESS_THREAD_JOIN_TIMEOUT = 2.0
    AUTO_PRESS_STOP_TIMEOUT = 5.0
    STOP_EVENT_WAIT_TIMEOUT = 5.0
    STOP_EVENT_ERROR_WAIT = 1.0
    SERVER_SOCKET_TIMEOUT = 1.0
    CLEANUP_PROCESS_TIMEOUT = 10
    AUTO_SKIP_CLICK_INTERVAL = 60
    RULE_EXECUTION_TIME_CHECK_INTERVAL = 10
    
    # 重試與循環配置
    BETSIZE_ADJUST_MAX_ATTEMPTS = 400
    BETSIZE_READ_MAX_RETRIES = 2
    FREE_GAME_SETTLE_CLICK_COUNT = 5
    DETECTION_WAIT_MAX_ATTEMPTS = 20
    LOBBY_CONFIRM_CHECK_ATTEMPTS = 3
    
    # 視窗排列配置
    DEFAULT_WINDOW_WIDTH = 600
    DEFAULT_WINDOW_HEIGHT = 400
    DEFAULT_WINDOW_COLUMNS = 4
    
    # 下注金額調整按鈕座標
    BETSIZE_INCREASE_BUTTON_X = 0.8
    BETSIZE_INCREASE_BUTTON_Y = 0.89
    BETSIZE_DECREASE_BUTTON_X = 0.63
    BETSIZE_DECREASE_BUTTON_Y = 0.89
    BETSIZE_DISPLAY_X = 0.72
    BETSIZE_DISPLAY_Y = 0.89

    # 黑屏截圖座標（基於預設視窗大小）
    BLACKSCREEN_CENTER_X = 300
    BLACKSCREEN_CENTER_Y = 195
    BLACKSCREEN_CROP_MARGIN_X = 125
    BLACKSCREEN_CROP_MARGIN_Y = 75
    BLACKSCREEN_PERSIST_SECONDS = 10

    # 返回遊戲提示截圖座標
    GAME_RETURN_CENTER_X = 290
    GAME_RETURN_CENTER_Y = 160
    GAME_RETURN_CROP_MARGIN_X = 50
    GAME_RETURN_CROP_MARGIN_Y = 10

    # 大廳返回提示截圖座標
    LOBBY_RETURN_CENTER_X = 300
    LOBBY_RETURN_CENTER_Y = 200
    LOBBY_RETURN_CROP_MARGIN_X = 50
    LOBBY_RETURN_CROP_MARGIN_Y = 20

    # 截圖裁切範圍（像素）
    BETSIZE_CROP_MARGIN_X = 40
    BETSIZE_CROP_MARGIN_Y = 10
    TEMPLATE_CROP_MARGIN = 20
    
    # 遊戲金額配置
    GAME_BETSIZE = frozenset((
        2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 24, 28, 32, 36, 40, 48, 56, 60, 64, 72, 
        80, 96, 100, 120, 140, 160, 180, 200, 240, 280, 300, 320, 360, 400, 420, 480, 
        500, 540, 560, 600, 640, 700, 720, 800, 840, 900, 960, 980, 1000, 1080, 1120, 
        1200, 1260, 1280, 1400, 1440, 1500, 1600, 1800, 2000, 2100, 2400, 2700, 3000
    ))
    
    # 遊戲金額列表（用於索引計算）
    GAME_BETSIZE_TUPLE = (
        2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 24, 28, 32, 36, 40, 48, 56, 60, 64, 72, 
        80, 96, 100, 120, 140, 160, 180, 200, 240, 280, 300, 320, 360, 400, 420, 480, 
        500, 540, 560, 600, 640, 700, 720, 800, 840, 900, 960, 980, 1000, 1080, 1120, 
        1200, 1260, 1280, 1400, 1440, 1500, 1600, 1800, 2000, 2100, 2400, 2700, 3000
    )
