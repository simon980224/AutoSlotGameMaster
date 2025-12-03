"""
系統常量定義

所有系統使用的常數都集中在此模組管理。
"""


class Constants:
    """系統常量"""
    
    # 版本資訊
    VERSION = "2.0.1"
    
    # 配置檔案相關
    DEFAULT_LIB_PATH = "lib"
    DEFAULT_CREDENTIALS_FILE = "用戶資料.txt"
    DEFAULT_RULES_FILE = "用戶規則.txt"
    
    # 網路與超時設定
    DEFAULT_PROXY_START_PORT = 9000
    DEFAULT_TIMEOUT_SECONDS = 30
    DEFAULT_PAGE_LOAD_TIMEOUT = 600
    DEFAULT_SCRIPT_TIMEOUT = 600
    DEFAULT_IMPLICIT_WAIT = 60
    
    # 執行緒與連線設定
    MAX_THREAD_WORKERS = 10
    PROXY_SERVER_BIND_HOST = "127.0.0.1"
    PROXY_BUFFER_SIZE = 4096
    PROXY_SELECT_TIMEOUT = 1.0
    
    # URL 配置
    LOGIN_PAGE = "https://m.jfw-win.com/#/login?redirect=%2Fhome%2Fpage"
    GAME_PAGE = "https://m.jfw-win.com/#/home/loding?game_code=egyptian-mythology&factory_code=ATG&state=true&name=%E6%88%B0%E7%A5%9E%E8%B3%BD%E7%89%B9"
    
    # 頁面元素選擇器
    USERNAME_INPUT = "//input[@placeholder='請輸入帳號']"
    PASSWORD_INPUT = "//input[@placeholder='請輸入密碼']"
    LOGIN_BUTTON = "//div[contains(@class, 'login-btn')]//span[text()='立即登入']/.."
    GAME_IFRAME = "gameFrame-0"
    GAME_CANVAS = "GameCanvas"
    
    # 圖片檢測配置
    IMAGE_DIR = "img"
    LOBBY_LOGIN = "lobby_login.png"
    LOBBY_CONFIRM = "lobby_confirm.png"
    ERROR_MESSAGE = "error_message.png"
    MATCH_THRESHOLD = 0.8  # 圖片匹配閾值
    DETECTION_INTERVAL = 1.0  # 檢測間隔（秒）
    MAX_DETECTION_ATTEMPTS = 60  # 最大檢測次數
    
    # Canvas 動態計算比例（用於點擊座標）
    LOBBY_LOGIN_BUTTON_X_RATIO = 0.55
    LOBBY_LOGIN_BUTTON_Y_RATIO = 1.2
    LOBBY_CONFIRM_BUTTON_X_RATIO = 0.78
    LOBBY_CONFIRM_BUTTON_Y_RATIO = 1.15
    BUY_FREE_GAME_BUTTON_X_RATIO = 0.23
    BUY_FREE_GAME_BUTTON_Y_RATIO = 1.05
    BUY_FREE_GAME_CONFIRM_X_RATIO = 0.65
    BUY_FREE_GAME_CONFIRM_Y_RATIO = 1.2
    BUY_FREE_GAME_WAIT_SECONDS = 10
    
    # 自動旋轉按鈕座標比例
    AUTO_SPIN_BUTTON_X_RATIO = 0.8
    AUTO_SPIN_BUTTON_Y_RATIO = 1.05
    AUTO_SPIN_10_X_RATIO = 0.5
    AUTO_SPIN_10_Y_RATIO = 0.83
    AUTO_SPIN_50_X_RATIO = 0.56
    AUTO_SPIN_50_Y_RATIO = 0.83
    AUTO_SPIN_100_X_RATIO = 0.62
    AUTO_SPIN_100_Y_RATIO = 0.83
    
    # 操作相關常量
    DEFAULT_WAIT_SECONDS = 3
    DETECTION_PROGRESS_INTERVAL = 20
    
    # 操作等待時間（秒）
    LOGIN_WAIT_TIME = 5
    BETSIZE_ADJUST_STEP_WAIT = 0.3
    BETSIZE_ADJUST_VERIFY_WAIT = 1.0
    BETSIZE_ADJUST_RETRY_WAIT = 0.5
    BETSIZE_READ_RETRY_WAIT = 0.5
    FREE_GAME_CLICK_WAIT = 2
    FREE_GAME_SETTLE_INITIAL_WAIT = 3
    FREE_GAME_SETTLE_CLICK_INTERVAL = 3
    AUTO_SPIN_MENU_WAIT = 0.5
    PROXY_SERVER_START_WAIT = 1
    TEMPLATE_CAPTURE_WAIT = 1
    DETECTION_COMPLETE_WAIT = 2
    
    # 重試與循環配置
    BETSIZE_ADJUST_MAX_ATTEMPTS = 200
    BETSIZE_READ_MAX_RETRIES = 2
    FREE_GAME_SETTLE_CLICK_COUNT = 5
    DETECTION_WAIT_MAX_ATTEMPTS = 20
    LOBBY_CONFIRM_CHECK_ATTEMPTS = 3
    
    # 視窗排列配置
    DEFAULT_WINDOW_WIDTH = 600
    DEFAULT_WINDOW_HEIGHT = 400
    DEFAULT_WINDOW_COLUMNS = 4
    
    # 下注金額調整按鈕座標（基於預設視窗大小）
    BETSIZE_INCREASE_BUTTON_X = 440
    BETSIZE_INCREASE_BUTTON_Y = 370
    BETSIZE_DECREASE_BUTTON_X = 360
    BETSIZE_DECREASE_BUTTON_Y = 370
    BETSIZE_DISPLAY_X = 400
    BETSIZE_DISPLAY_Y = 370
    
    # 錯誤訊息圖片識別座標（基於預設視窗大小）
    ERROR_MESSAGE_LEFT_X = 240
    ERROR_MESSAGE_LEFT_Y = 190
    ERROR_MESSAGE_RIGHT_X = 360
    ERROR_MESSAGE_RIGHT_Y = 190
    ERROR_MESSAGE_PERSIST_SECONDS = 1
    
    # 截圖裁切範圍（像素）
    BETSIZE_CROP_MARGIN_X = 40
    BETSIZE_CROP_MARGIN_Y = 10
    TEMPLATE_CROP_MARGIN = 20
    
    # 遊戲金額配置（使用 frozenset 提升查詢效率）
    GAME_BETSIZE = frozenset((
        0.4, 0.8, 1, 1.2, 1.6, 2, 2.4, 2.8, 3, 3.2, 3.6, 4, 5, 6, 7, 8, 9, 10,
        12, 14, 16, 18, 20, 24, 28, 32, 36, 40, 48, 56, 60, 64, 72, 80, 100,
        120, 140, 160, 180, 200, 240, 280, 300, 320, 360, 400, 420, 480, 500,
        540, 560, 600, 640, 700, 720, 800, 840, 900, 960, 980, 1000, 1080,
        1120, 1200, 1260, 1280, 1400, 1440, 1600, 1800, 2000
    ))
    
    # 遊戲金額列表（用於索引計算）
    GAME_BETSIZE_TUPLE = (
        0.4, 0.8, 1, 1.2, 1.6, 2, 2.4, 2.8, 3, 3.2, 3.6, 4, 5, 6, 7, 8, 9, 10,
        12, 14, 16, 18, 20, 24, 28, 32, 36, 40, 48, 56, 60, 64, 72, 80, 100,
        120, 140, 160, 180, 200, 240, 280, 300, 320, 360, 400, 420, 480, 500,
        540, 560, 600, 640, 700, 720, 800, 840, 900, 960, 980, 1000, 1080,
        1120, 1200, 1260, 1280, 1400, 1440, 1600, 1800, 2000
    )
