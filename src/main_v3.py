"""
金富翁遊戲自動化系統 - 多瀏覽器同步版本

重點改進：
1. 所有瀏覽器完全同步操作
2. 啟動時詢問瀏覽器數量並讀取配置
3. 支援最多 12 組帳號 (user_credentials.txt)
4. 支援無限組規則 (user_rules.txt) - 格式: 金額:時間(分鐘)
5. 視窗自動排列 4x3 網格 (600x400)
6. 統一控制模式介面

作者: simon980224
版本: 3.0.0 (同步重構版)
Python: 3.8+
"""

from __future__ import annotations
import time
import threading
import logging
import cv2
import numpy as np
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager


# ==================== 全域配置 ====================

# URL 配置
LOGIN_PAGE = "https://gf777.co/"
GAME_PAGE = "https://lobby-tw1.gf777.co/desktop/index.html?language=zh-tw&action=real"

# 視窗配置
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 400
GRID_COLS = 4
GRID_ROWS = 3
MAX_BROWSERS = 12

# 遊戲配置
GAME_BETSIZE = (
    0.4, 0.8, 1, 1.2, 1.6, 2, 2.4, 2.8, 3, 3.2, 3.6, 4, 5, 6, 7, 8, 9, 10,
    12, 14, 16, 18, 20, 24, 28, 32, 36, 40, 48, 56, 60, 64, 72, 80, 100,
    120, 140, 160, 180, 200, 240, 280, 300, 320, 360, 400, 420, 480, 500,
    540, 560, 600, 640, 700, 720, 800, 840, 900, 960, 980, 1000, 1080,
    1120, 1200, 1260, 1280, 1400, 1440, 1600, 1800, 2000
)

# 路徑配置
PROJECT_ROOT = Path(__file__).resolve().parent.parent
IMG_DIR = PROJECT_ROOT / "img"
BETSIZE_DIR = IMG_DIR / "bet_size"
LIB_DIR = PROJECT_ROOT / "lib"
CREDENTIALS_FILE = LIB_DIR / "user_credentials.txt"
RULES_FILE = LIB_DIR / "user_rules.txt"

# 圖片模板路徑
TEMPLATE_LOBBY_LOGIN = IMG_DIR / "lobby_login.png"
TEMPLATE_LOBBY_CONFIRM = IMG_DIR / "lobby_confirm.png"

# 控制指令
CONTROL_COMMANDS = {
    '1': '一般模式 (0~5秒轉一次)',
    '2': '開始/繼續規則執行',
    '3': '暫停目前運行',
    '4': '調整下注金額',
    '5': '購買免費遊戲',
    '6': '截取金額模板',
    'h': '顯示說明',
    'q': '退出程式'
}


# ==================== 日誌配置 ====================

class ColorFormatter(logging.Formatter):
    """彩色日誌格式化器"""
    
    COLORS = {
        'DEBUG': '\033[36m',
        'INFO': '\033[32m',
        'WARNING': '\033[33m',
        'ERROR': '\033[31m',
        'CRITICAL': '\033[35m',
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logger() -> logging.Logger:
    """設定日誌記錄器"""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    
    if logger.handlers:
        return logger
    
    handler = logging.StreamHandler()
    formatter = ColorFormatter('[%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger


logger = setup_logger()


# ==================== 資料模型 ====================

@dataclass
class UserCredential:
    """用戶憑證"""
    username: str
    password: str
    proxy: Optional[str] = None


@dataclass
class GameRule:
    """遊戲規則"""
    amount: float
    duration_minutes: int


@dataclass
class BrowserInstance:
    """瀏覽器實例"""
    driver: WebDriver
    credential: UserCredential
    index: int


# ==================== Proxy 管理器 ====================

class ProxyExtensionManager:
    """Proxy Chrome Extension 管理器"""
    
    @staticmethod
    def create_proxy_extension(proxy_config: str) -> Path:
        """
        建立 Proxy 擴充套件
        
        Args:
            proxy_config: proxy 配置字串 (格式: host:port:user:pass)
            
        Returns:
            Path: 擴充套件目錄路徑
        """
        parts = proxy_config.split(':')
        if len(parts) != 4:
            raise ValueError(f"無效的 proxy 格式: {proxy_config}")
        
        host, port, user, password = parts
        
        manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 3,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "storage",
        "webRequest"
    ],
    "host_permissions": [
        "<all_urls>"
    ],
    "background": {
        "service_worker": "background.js"
    },
    "minimum_chrome_version": "22.0.0"
}
"""
        
        background_js = f"""
var config = {{
    mode: "fixed_servers",
    rules: {{
        singleProxy: {{
            scheme: "http",
            host: "{host}",
            port: parseInt({port})
        }},
        bypassList: ["localhost"]
    }}
}};

chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});

function callbackFn(details) {{
    return {{
        authCredentials: {{
            username: "{user}",
            password: "{password}"
        }}
    }};
}}

chrome.webRequest.onAuthRequired.addListener(
    callbackFn,
    {{urls: ["<all_urls>"]}},
    ['blocking']
);
"""
        
        # 建立臨時目錄
        plugin_dir = PROJECT_ROOT / f"proxy_extension_{int(time.time()*1000)}"
        plugin_dir.mkdir(exist_ok=True)
        
        # 寫入檔案
        (plugin_dir / "manifest.json").write_text(manifest_json)
        (plugin_dir / "background.js").write_text(background_js)
        
        return plugin_dir


# ==================== 配置載入器 ====================

class ConfigLoader:
    """配置檔案載入器"""
    
    @staticmethod
    def load_credentials(max_count: int = MAX_BROWSERS) -> List[UserCredential]:
        """
        載入用戶憑證 (最多 12 組)
        
        格式: 帳號,密碼,proxy
        """
        if not CREDENTIALS_FILE.exists():
            logger.error(f"找不到憑證檔案: {CREDENTIALS_FILE}")
            return []
        
        credentials = []
        with open(CREDENTIALS_FILE, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i >= max_count:
                    logger.warning(f"憑證超過 {max_count} 組，只讀取前 {max_count} 組")
                    break
                
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split(',')
                if len(parts) < 2:
                    logger.warning(f"跳過無效憑證: {line}")
                    continue
                
                username = parts[0].strip()
                password = parts[1].strip()
                proxy = parts[2].strip() if len(parts) > 2 else None
                
                credentials.append(UserCredential(username, password, proxy))
        
        logger.info(f"成功載入 {len(credentials)} 組憑證")
        return credentials
    
    @staticmethod
    def load_rules() -> List[GameRule]:
        """
        載入遊戲規則 (無限組)
        
        格式: 金額:時間(分鐘)
        範例: 0.4:10
        """
        if not RULES_FILE.exists():
            logger.error(f"找不到規則檔案: {RULES_FILE}")
            return []
        
        rules = []
        with open(RULES_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or line.startswith('金額'):
                    continue
                
                parts = line.split(':')
                if len(parts) != 2:
                    logger.warning(f"跳過無效規則: {line}")
                    continue
                
                try:
                    amount = float(parts[0].strip())
                    duration = int(parts[1].strip())
                    rules.append(GameRule(amount, duration))
                except ValueError:
                    logger.warning(f"跳過無效規則: {line}")
                    continue
        
        logger.info(f"成功載入 {len(rules)} 組規則")
        return rules


# ==================== 圖片處理工具 ====================

class ImageProcessor:
    """圖片處理工具類"""
    
    @staticmethod
    def capture_screenshot(driver: WebDriver) -> np.ndarray:
        """截取瀏覽器畫面"""
        try:
            screenshot = driver.get_screenshot_as_png()
            img_array = np.frombuffer(screenshot, np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            return img
        except Exception as e:
            logger.error(f"截圖失敗: {e}")
            return None
    
    @staticmethod
    def find_template(screenshot: np.ndarray, template_path: Path, threshold: float = 0.8) -> bool:
        """
        在截圖中尋找模板
        
        Returns:
            bool: True 表示找到，False 表示未找到
        """
        if not template_path.exists():
            return False
        
        template = cv2.imread(str(template_path), cv2.IMREAD_COLOR)
        if template is None:
            return False
        
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(result)
        
        return max_val >= threshold
    
    @staticmethod
    def save_template(driver: WebDriver, output_path: Path) -> bool:
        """儲存模板圖片"""
        screenshot = ImageProcessor.capture_screenshot(driver)
        if screenshot is None:
            return False
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(output_path), screenshot)
        logger.info(f"已儲存模板: {output_path}")
        return True


# ==================== 瀏覽器管理器 ====================

class BrowserManager:
    """瀏覽器管理器 - 負責初始化和管理所有瀏覽器"""
    
    @staticmethod
    def create_browser(credential: UserCredential, index: int) -> Optional[WebDriver]:
        """建立單個瀏覽器實例"""
        try:
            options = Options()
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_experimental_option('excludeSwitches', ['enable-automation'])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Proxy 設定
            if credential.proxy:
                try:
                    plugin_dir = ProxyExtensionManager.create_proxy_extension(credential.proxy)
                    options.add_argument(f'--load-extension={plugin_dir}')
                    logger.info(f"瀏覽器 {index+1}: 已設定 Proxy")
                except Exception as e:
                    logger.warning(f"瀏覽器 {index+1}: Proxy 設定失敗 - {e}")
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            
            logger.info(f"瀏覽器 {index+1}: 建立成功")
            return driver
            
        except Exception as e:
            logger.error(f"瀏覽器 {index+1}: 建立失敗 - {e}")
            return None
    
    @staticmethod
    def arrange_windows(browsers: List[BrowserInstance]) -> None:
        """
        排列視窗為 4x3 網格
        
        視窗大小: 600x400
        排列方式: 由左至右、由上而下
        """
        logger.info("開始排列視窗...")
        
        for i, browser in enumerate(browsers):
            row = i // GRID_COLS
            col = i % GRID_COLS
            
            x = col * WINDOW_WIDTH
            y = row * WINDOW_HEIGHT
            
            try:
                browser.driver.set_window_position(x, y)
                browser.driver.set_window_size(WINDOW_WIDTH, WINDOW_HEIGHT)
                logger.info(f"瀏覽器 {i+1}: 視窗位置 ({x}, {y})")
            except Exception as e:
                logger.error(f"瀏覽器 {i+1}: 視窗設定失敗 - {e}")
        
        logger.info(f"視窗排列完成 ({len(browsers)} 個瀏覽器)")


# ==================== 登入管理器 ====================

class LoginManager:
    """登入流程管理器 - 處理所有瀏覽器的同步登入"""
    
    @staticmethod
    def login_all(browsers: List[BrowserInstance]) -> bool:
        """
        所有瀏覽器同步登入
        
        流程:
        1. 導向 LOGIN_PAGE
        2. 輸入帳號密碼
        3. 等待 10 秒
        4. 導向 GAME_PAGE
        5. 調整視窗大小並排列
        """
        logger.info("=" * 60)
        logger.info("開始同步登入流程")
        logger.info("=" * 60)
        
        # 步驟 1: 導向登入頁面
        logger.info("步驟 1/5: 導向登入頁面...")
        for browser in browsers:
            try:
                browser.driver.get(LOGIN_PAGE)
                logger.info(f"瀏覽器 {browser.index+1}: 已導向登入頁面")
            except Exception as e:
                logger.error(f"瀏覽器 {browser.index+1}: 導向失敗 - {e}")
        
        time.sleep(3)
        
        # 步驟 2: 輸入帳號密碼
        logger.info("步驟 2/5: 輸入帳號密碼...")
        for browser in browsers:
            try:
                # 找到帳號輸入框
                username_input = browser.driver.find_element(By.ID, "LoginName")
                username_input.clear()
                username_input.send_keys(browser.credential.username)
                
                # 找到密碼輸入框
                password_input = browser.driver.find_element(By.ID, "Password")
                password_input.clear()
                password_input.send_keys(browser.credential.password)
                
                # 提交表單
                password_input.send_keys(Keys.RETURN)
                
                logger.info(f"瀏覽器 {browser.index+1}: 已提交登入")
            except Exception as e:
                logger.error(f"瀏覽器 {browser.index+1}: 登入失敗 - {e}")
        
        # 步驟 3: 等待 10 秒
        logger.info("步驟 3/5: 等待登入處理...")
        for i in range(10, 0, -1):
            print(f"\r等待 {i} 秒...", end='', flush=True)
            time.sleep(1)
        print()
        
        # 步驟 4: 導向遊戲頁面
        logger.info("步驟 4/5: 導向遊戲頁面...")
        for browser in browsers:
            try:
                browser.driver.get(GAME_PAGE)
                logger.info(f"瀏覽器 {browser.index+1}: 已導向遊戲頁面")
            except Exception as e:
                logger.error(f"瀏覽器 {browser.index+1}: 導向失敗 - {e}")
        
        time.sleep(3)
        
        # 步驟 5: 排列視窗
        logger.info("步驟 5/5: 排列視窗...")
        BrowserManager.arrange_windows(browsers)
        
        logger.info("=" * 60)
        logger.info("登入流程完成")
        logger.info("=" * 60)
        
        return True


# ==================== 圖片偵測管理器 ====================

class ImageDetectionManager:
    """圖片偵測管理器 - 處理 lobby_login 和 lobby_confirm 的偵測"""
    
    @staticmethod
    def wait_for_lobby_login_disappear(browsers: List[BrowserInstance], timeout: int = 300) -> bool:
        """
        等待 lobby_login 圖片消失
        
        如果模板不存在，提示用戶按 's' 截取
        """
        logger.info("=" * 60)
        logger.info("等待 lobby_login 圖片消失...")
        logger.info("=" * 60)
        
        # 檢查模板是否存在
        if not TEMPLATE_LOBBY_LOGIN.exists():
            logger.warning("找不到 lobby_login.png 模板")
            logger.info("請按 's' 鍵截取第一個瀏覽器的畫面作為模板")
            
            while True:
                cmd = input("請輸入指令 (s=截取模板): ").strip().lower()
                if cmd == 's':
                    if ImageProcessor.save_template(browsers[0].driver, TEMPLATE_LOBBY_LOGIN):
                        logger.info("模板截取成功，開始偵測...")
                        break
                    else:
                        logger.error("模板截取失敗，請重試")
        
        # 開始偵測
        start_time = time.time()
        while time.time() - start_time < timeout:
            # 只檢查第一個瀏覽器
            screenshot = ImageProcessor.capture_screenshot(browsers[0].driver)
            if screenshot is not None:
                found = ImageProcessor.find_template(screenshot, TEMPLATE_LOBBY_LOGIN)
                if not found:
                    logger.info("✓ lobby_login 已消失")
                    return True
            
            time.sleep(2)
        
        logger.error(f"超時 ({timeout} 秒)：lobby_login 未消失")
        return False
    
    @staticmethod
    def wait_for_lobby_confirm_disappear(browsers: List[BrowserInstance], timeout: int = 300) -> bool:
        """
        等待 lobby_confirm 圖片消失
        
        如果模板不存在，提示用戶按 's' 截取
        """
        logger.info("=" * 60)
        logger.info("等待 lobby_confirm 圖片消失...")
        logger.info("=" * 60)
        
        # 檢查模板是否存在
        if not TEMPLATE_LOBBY_CONFIRM.exists():
            logger.warning("找不到 lobby_confirm.png 模板")
            logger.info("請按 's' 鍵截取第一個瀏覽器的畫面作為模板")
            
            while True:
                cmd = input("請輸入指令 (s=截取模板): ").strip().lower()
                if cmd == 's':
                    if ImageProcessor.save_template(browsers[0].driver, TEMPLATE_LOBBY_CONFIRM):
                        logger.info("模板截取成功，開始偵測...")
                        break
                    else:
                        logger.error("模板截取失敗，請重試")
        
        # 開始偵測
        start_time = time.time()
        while time.time() - start_time < timeout:
            # 只檢查第一個瀏覽器
            screenshot = ImageProcessor.capture_screenshot(browsers[0].driver)
            if screenshot is not None:
                found = ImageProcessor.find_template(screenshot, TEMPLATE_LOBBY_CONFIRM)
                if not found:
                    logger.info("✓ lobby_confirm 已消失")
                    return True
            
            time.sleep(2)
        
        logger.error(f"超時 ({timeout} 秒)：lobby_confirm 未消失")
        return False


# ==================== 遊戲控制器 ====================

class GameController:
    """遊戲控制器 - 處理遊戲操作"""
    
    def __init__(self, browsers: List[BrowserInstance], rules: List[GameRule]):
        self.browsers = browsers
        self.rules = rules
        self.running = False
        self.current_mode = None
        self.rule_thread = None
    
    def send_space_all(self) -> None:
        """所有瀏覽器發送空白鍵"""
        for browser in self.browsers:
            try:
                # 切換到遊戲 iframe
                browser.driver.switch_to.frame("gameiframe")
                
                # 發送空白鍵
                actions = ActionChains(browser.driver)
                actions.send_keys(Keys.SPACE)
                actions.perform()
                
                # 切回主頁面
                browser.driver.switch_to.default_content()
            except Exception as e:
                logger.error(f"瀏覽器 {browser.index+1}: 發送空白鍵失敗 - {e}")
    
    def normal_mode(self) -> None:
        """一般模式：0~5秒轉一次"""
        logger.info("啟動一般模式 (0~5秒轉一次)")
        self.running = True
        self.current_mode = 'normal'
        
        try:
            while self.running and self.current_mode == 'normal':
                self.send_space_all()
                interval = np.random.uniform(0, 5)
                time.sleep(interval)
        except Exception as e:
            logger.error(f"一般模式錯誤: {e}")
        finally:
            self.running = False
            logger.info("一般模式已停止")
    
    def rule_mode(self) -> None:
        """規則模式：按照 user_rules.txt 執行"""
        if not self.rules:
            logger.error("沒有可用的規則")
            return
        
        logger.info("啟動規則模式")
        logger.info(f"共有 {len(self.rules)} 組規則")
        
        self.running = True
        self.current_mode = 'rule'
        
        try:
            for i, rule in enumerate(self.rules):
                if not self.running or self.current_mode != 'rule':
                    break
                
                logger.info(f"執行規則 {i+1}/{len(self.rules)}: 金額={rule.amount}, 持續時間={rule.duration_minutes}分鐘")
                
                # 調整金額
                self.adjust_betsize_all(rule.amount)
                
                # 執行指定時間
                end_time = time.time() + (rule.duration_minutes * 60)
                while time.time() < end_time:
                    if not self.running or self.current_mode != 'rule':
                        break
                    
                    self.send_space_all()
                    interval = np.random.uniform(10, 15)
                    time.sleep(interval)
                
                logger.info(f"規則 {i+1}/{len(self.rules)} 執行完成")
            
            logger.info("所有規則執行完成")
        except Exception as e:
            logger.error(f"規則模式錯誤: {e}")
        finally:
            self.running = False
            self.current_mode = None
            logger.info("規則模式已停止")
    
    def adjust_betsize_all(self, target_amount: float) -> None:
        """所有瀏覽器調整下注金額"""
        logger.info(f"調整所有瀏覽器金額至 {target_amount}")
        
        for browser in self.browsers:
            try:
                self._adjust_single_betsize(browser, target_amount)
            except Exception as e:
                logger.error(f"瀏覽器 {browser.index+1}: 調整金額失敗 - {e}")
    
    def _adjust_single_betsize(self, browser: BrowserInstance, target_amount: float, max_attempts: int = 100) -> bool:
        """
        調整單個瀏覽器的下注金額
        
        流程:
        1. 截取當前畫面
        2. 比對 bet_size 資料夾中的圖片找出當前金額
        3. 計算需要調整的方向和次數
        4. 點擊增加/減少按鈕
        5. 驗證結果
        """
        try:
            # 檢查目標金額是否有效
            if target_amount not in GAME_BETSIZE:
                logger.error(f"瀏覽器 {browser.index+1}: 目標金額 {target_amount} 不在可用列表中")
                return False
            
            # 取得當前金額
            current_amount = self._get_current_betsize(browser)
            if current_amount is None:
                logger.error(f"瀏覽器 {browser.index+1}: 無法識別當前金額")
                return False
            
            logger.info(f"瀏覽器 {browser.index+1}: 當前金額={current_amount}, 目標金額={target_amount}")
            
            # 如果已是目標金額
            if current_amount == target_amount:
                logger.info(f"瀏覽器 {browser.index+1}: 已是目標金額")
                return True
            
            # 計算調整方向
            current_index = GAME_BETSIZE.index(current_amount)
            target_index = GAME_BETSIZE.index(target_amount)
            diff = target_index - current_index
            
            # 設定點擊座標 (基於 600x400 視窗)
            if diff > 0:
                # 增加金額
                click_x = 440
                click_y = 370
                direction = "增加"
                steps = diff
            else:
                # 減少金額
                click_x = 360
                click_y = 370
                direction = "減少"
                steps = abs(diff)
            
            logger.info(f"瀏覽器 {browser.index+1}: 預計{direction}按鈕點擊 {steps} 次")
            
            # 執行點擊
            for i in range(steps):
                self._click_coordinate(browser, click_x, click_y)
                time.sleep(0.3)
            
            time.sleep(1)
            
            # 驗證並微調
            for attempt in range(max_attempts):
                current_amount = self._get_current_betsize(browser)
                
                if current_amount is None:
                    logger.warning(f"瀏覽器 {browser.index+1}: 驗證失敗 ({attempt+1}/{max_attempts})")
                    time.sleep(0.5)
                    continue
                
                if current_amount == target_amount:
                    logger.info(f"瀏覽器 {browser.index+1}: ✓ 調整成功")
                    return True
                
                # 繼續微調
                if current_amount < target_amount:
                    self._click_coordinate(browser, 440, 370)
                else:
                    self._click_coordinate(browser, 360, 370)
                
                time.sleep(0.5)
            
            logger.error(f"瀏覽器 {browser.index+1}: 調整失敗 (超過最大嘗試次數)")
            return False
            
        except Exception as e:
            logger.error(f"瀏覽器 {browser.index+1}: 調整金額錯誤 - {e}")
            return False
    
    def _get_current_betsize(self, browser: BrowserInstance) -> Optional[float]:
        """
        取得當前下注金額
        
        透過截圖與 bet_size 資料夾中的圖片比對
        """
        try:
            # 截取畫面
            screenshot = ImageProcessor.capture_screenshot(browser.driver)
            if screenshot is None:
                return None
            
            # 轉換為灰階
            screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            
            # 比對所有 bet_size 圖片
            best_match = None
            best_score = 0.0
            
            if not BETSIZE_DIR.exists():
                logger.warning(f"bet_size 資料夾不存在: {BETSIZE_DIR}")
                return None
            
            for img_file in sorted(BETSIZE_DIR.glob("*.png")):
                template = cv2.imread(str(img_file), cv2.IMREAD_GRAYSCALE)
                if template is None:
                    continue
                
                # 使用模板匹配
                result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, _ = cv2.minMaxLoc(result)
                
                if max_val > best_score:
                    best_score = max_val
                    best_match = img_file.stem
            
            # 檢查相似度閾值
            if best_score >= 0.8 and best_match:
                try:
                    amount = float(best_match)
                    return amount
                except ValueError:
                    logger.warning(f"無法轉換金額: {best_match}")
            
            return None
            
        except Exception as e:
            logger.error(f"取得當前金額錯誤: {e}")
            return None
    
    def _click_coordinate(self, browser: BrowserInstance, x: float, y: float) -> None:
        """
        點擊指定座標
        
        使用 CDP 協議直接點擊
        """
        try:
            # 取得視窗位置
            window_rect = browser.driver.get_window_rect()
            
            # 計算實際點擊位置
            actual_x = x
            actual_y = y
            
            # 使用 CDP 點擊
            browser.driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
                "type": "mousePressed",
                "x": actual_x,
                "y": actual_y,
                "button": "left",
                "clickCount": 1
            })
            
            browser.driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
                "type": "mouseReleased",
                "x": actual_x,
                "y": actual_y,
                "button": "left",
                "clickCount": 1
            })
            
        except Exception as e:
            logger.error(f"點擊座標失敗: {e}")
    
    def pause(self) -> None:
        """暫停當前運行"""
        self.running = False
        self.current_mode = None
        logger.info("已暫停")
    
    def start_normal_mode(self) -> None:
        """啟動一般模式 (背景執行緒)"""
        if self.running:
            logger.warning("已有模式在運行中")
            return
        
        self.rule_thread = threading.Thread(target=self.normal_mode, daemon=True)
        self.rule_thread.start()
    
    def start_rule_mode(self) -> None:
        """啟動規則模式 (背景執行緒)"""
        if self.running:
            logger.warning("已有模式在運行中")
            return
        
        self.rule_thread = threading.Thread(target=self.rule_mode, daemon=True)
        self.rule_thread.start()
    
    def buy_free_game_all(self) -> None:
        """所有瀏覽器購買免費遊戲"""
        logger.info("購買免費遊戲功能尚未實作")
        # TODO: 實作購買免費遊戲邏輯
    
    def capture_amount_template(self) -> None:
        """截取金額模板"""
        logger.info("截取金額模板功能尚未實作")
        # TODO: 實作截取金額模板邏輯


# ==================== 控制介面 ====================

class ControlInterface:
    """控制介面 - 提供統一的控制面板"""
    
    def __init__(self, controller: GameController):
        self.controller = controller
    
    def show_menu(self) -> None:
        """顯示控制選單"""
        print()
        print("=" * 60)
        print("控制模式")
        print("=" * 60)
        for key, desc in CONTROL_COMMANDS.items():
            print(f"  [{key}] {desc}")
        print("=" * 60)
    
    def run(self) -> None:
        """執行控制迴圈"""
        self.show_menu()
        
        while True:
            try:
                cmd = input("\n請輸入指令: ").strip().lower()
                
                if cmd == '1':
                    self.controller.start_normal_mode()
                elif cmd == '2':
                    self.controller.start_rule_mode()
                elif cmd == '3':
                    self.controller.pause()
                elif cmd == '4':
                    amount = float(input("請輸入目標金額: ").strip())
                    self.controller.adjust_betsize_all(amount)
                elif cmd == '5':
                    self.controller.buy_free_game_all()
                elif cmd == '6':
                    self.controller.capture_amount_template()
                elif cmd == 'h':
                    self.show_menu()
                elif cmd == 'q':
                    logger.info("退出程式...")
                    self.controller.pause()
                    break
                else:
                    logger.warning(f"未知指令: {cmd}")
            
            except KeyboardInterrupt:
                logger.info("\n收到中斷信號，退出程式...")
                self.controller.pause()
                break
            except Exception as e:
                logger.error(f"執行錯誤: {e}")


# ==================== 主程式 ====================

class Application:
    """主應用程式"""
    
    def __init__(self):
        self.browsers: List[BrowserInstance] = []
        self.credentials: List[UserCredential] = []
        self.rules: List[GameRule] = []
    
    def run(self) -> None:
        """執行主流程"""
        try:
            logger.info("=" * 60)
            logger.info("金富翁遊戲自動化系統 v3.0.0")
            logger.info("=" * 60)
            
            # 步驟 1: 載入配置
            self._load_config()
            
            # 步驟 2: 詢問瀏覽器數量
            browser_count = self._ask_browser_count()
            
            # 步驟 3: 初始化瀏覽器
            self._initialize_browsers(browser_count)
            
            # 步驟 4: 登入所有瀏覽器
            LoginManager.login_all(self.browsers)
            
            # 步驟 5: 等待圖片偵測
            self._wait_for_game_ready()
            
            # 步驟 6: 啟動控制介面
            self._start_control_interface()
            
        except KeyboardInterrupt:
            logger.info("\n收到中斷信號，正在清理...")
        except Exception as e:
            logger.error(f"程式錯誤: {e}", exc_info=True)
        finally:
            self._cleanup()
    
    def _load_config(self) -> None:
        """載入配置檔案"""
        logger.info("載入配置檔案...")
        
        self.credentials = ConfigLoader.load_credentials()
        if not self.credentials:
            raise Exception("無法載入憑證檔案")
        
        self.rules = ConfigLoader.load_rules()
        if not self.rules:
            logger.warning("無法載入規則檔案，某些功能將無法使用")
    
    def _ask_browser_count(self) -> int:
        """詢問用戶要啟動幾個瀏覽器"""
        max_count = min(len(self.credentials), MAX_BROWSERS)
        
        while True:
            try:
                count = input(f"請輸入要啟動的瀏覽器數量 (1-{max_count}): ").strip()
                count = int(count)
                
                if 1 <= count <= max_count:
                    return count
                else:
                    logger.warning(f"請輸入 1 到 {max_count} 之間的數字")
            except ValueError:
                logger.warning("請輸入有效的數字")
    
    def _initialize_browsers(self, count: int) -> None:
        """初始化瀏覽器"""
        logger.info(f"初始化 {count} 個瀏覽器...")
        
        for i in range(count):
            credential = self.credentials[i]
            driver = BrowserManager.create_browser(credential, i)
            
            if driver:
                browser = BrowserInstance(driver, credential, i)
                self.browsers.append(browser)
            else:
                logger.error(f"瀏覽器 {i+1} 初始化失敗")
        
        if not self.browsers:
            raise Exception("沒有成功初始化的瀏覽器")
        
        logger.info(f"成功初始化 {len(self.browsers)} 個瀏覽器")
    
    def _wait_for_game_ready(self) -> None:
        """等待遊戲準備完成"""
        # 等待 lobby_login 消失
        if not ImageDetectionManager.wait_for_lobby_login_disappear(self.browsers):
            raise Exception("lobby_login 偵測超時")
        
        # 等待 lobby_confirm 消失
        if not ImageDetectionManager.wait_for_lobby_confirm_disappear(self.browsers):
            raise Exception("lobby_confirm 偵測超時")
        
        logger.info("遊戲準備完成，進入控制模式")
    
    def _start_control_interface(self) -> None:
        """啟動控制介面"""
        controller = GameController(self.browsers, self.rules)
        interface = ControlInterface(controller)
        interface.run()
    
    def _cleanup(self) -> None:
        """清理資源"""
        logger.info("正在關閉瀏覽器...")
        
        for browser in self.browsers:
            try:
                browser.driver.quit()
                logger.info(f"瀏覽器 {browser.index+1} 已關閉")
            except Exception as e:
                logger.error(f"關閉瀏覽器 {browser.index+1} 失敗: {e}")
        
        logger.info("程式結束")


# ==================== 程式入口 ====================

def main() -> None:
    """程式入口"""
    app = Application()
    app.run()


if __name__ == "__main__":
    main()
