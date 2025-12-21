# AutoSlotGameMaster - AI 程式碼代理指南

## 專案概述

金富翁遊戲自動化系統 - 使用 Selenium WebDriver 控制多個瀏覽器實例，透過圖片識別和 Chrome DevTools Protocol 實現遊戲自動化。

**核心技術**: Python 3.8+, Selenium 4.25+, OpenCV, 本地 Proxy 中繼伺服器, 執行緒池並行處理

## 版本資訊

**目前版本**: v1.18.0

**更新內容**:

- v1.18.0: 新增 game_return 圖片檢測功能（自動檢測並點擊返回遊戲提示，使用專屬座標 0.54,0.84；優化錯誤恢復流程為完整登入流程，包含導航、lobby_login、lobby_confirm；'g' 命令支援截取 game_return 模板）
- v1.17.1: 修正自動跳過點擊功能的時間戳錯誤（將 AUTO_SKIP_CLICK_INTERVAL 從極大值改為 86400 秒，避免 'r' 命令執行時出現 timestamp too large to convert to C \_PyTime_t 錯誤）
- v1.17.0: 優化調整金額功能（每次調整間隔改為 3 秒，超過最大嘗試次數自動關閉該瀏覽器；adjust_betsize 失敗時拋出異常，adjust_betsize_all 自動關閉失敗的瀏覽器並從列表移除）
- v1.16.1: 修正規則執行時間控制功能（修正時間到達後無法正常退出的問題，使用 os.\_exit() 強制終止；優化時間檢查邏輯，先檢查再等待；短時間執行時每分鐘顯示剩餘時間；'r' 命令現在必須提供參數，r 0 代表無限執行）
- v1.16.0: 新增規則執行時間控制功能（'r' 命令支援可選的小時參數，時間到後自動關閉所有瀏覽器並退出）
- v1.15.0: 新增錯誤訊息自動監控與重整功能（每 10 秒檢測，雙區域模板匹配，'e' 命令截取左右兩張模板）
- v1.14.3: 修正按下 'p' 後規則仍繼續執行的問題（在規則執行的關鍵步驟之間加入停止檢查，包括金額調整前、自動按鍵啟動前、免費遊戲購買前）
- v1.14.2: 修正規則執行循環問題（'f' 規則執行後正確清除停止事件，確保循環繼續；優化日誌輸出順序，避免執行緒日誌交錯）
- v1.14.1: 修正規則執行中 'f' 規則 AttributeError 問題（改用 browser_operator.last_canvas_rect），並優化金額識別失敗日誌（即使在靜默模式下也記錄關鍵錯誤，每 20 次重試輸出一次警告）
- v1.14.0: 擴展規則執行功能，支援 'f' 類型規則（購買免費遊戲），規則格式: f:金額
- v1.5.0: 統一管理所有魔法數字（視窗尺寸、座標、等待時間、重試次數等），提升程式碼可維護性
- v1.4.3: 優化瀏覽器網路設定（啟用 QUIC、TCP Fast Open、NetworkService）
- v1.4.2: 修正 Windows 中文路徑截圖儲存失敗問題
- v1.4.1: 新增瀏覽器靜音功能，自動將所有瀏覽器設為靜音
- v1.4.0: 優化免費遊戲結算流程（3 秒後開始點擊，間隔 3 秒，共 5 次）
- v1.3.0: 新增自動旋轉功能（支援 10、50、100 次）
- v1.2.0: 新增專案啟動前自動清除 chromedriver 快取功能
- v1.1.0: 修正 OpenCV 無法讀取中文路徑圖片的問題
- v1.0.0: 初始版本發布

## 架構特點

### 0. 模組化架構 (v2.0.0 新增)

專案採用模組化架構，功能拆分為獨立模組：

```
src/autoslot/
├── core/           # 核心模組（常數、例外、資料模型）
├── utils/          # 工具模組（日誌、輔助函式）
├── config/         # 配置模組（配置讀取）
├── managers/       # 管理器模組（瀏覽器、Proxy、輔助工具）
├── operators/      # 操作器模組（待遷移）
├── detectors/      # 檢測器模組（待遷移）
└── app/            # 應用程式模組（待遷移）
```

**使用方式**:

```python
from autoslot import (
    Constants,              # 核心常數
    LoggerFactory,         # 日誌工廠
    ConfigReader,          # 配置讀取
    BrowserManager,        # 瀏覽器管理
    LocalProxyServerManager,  # Proxy 管理
    BrowserHelper,         # 瀏覽器輔助工具
)
```

### 1. 依賴注入與工廠模式

- 所有主要類別支援依賴注入（透過建構函式參數）
- `LoggerFactory.get_logger()` - 單例模式的 Logger 工廠
- `BrowserManager.create_webdriver()` - 優先使用專案根目錄的 `chromedriver`，失敗時自動降級到 WebDriver Manager
- 使用 `Protocol` 定義介面（如 `ConfigReaderProtocol`）

### 2. 上下文管理器與資源清理

- `LocalProxyServerManager` 支援 `with` 語句自動清理資源
- `BrowserManager.create_browser_context()` 使用 `@contextmanager` 確保 WebDriver 正確關閉
- 所有 socket 操作使用 `with suppress(Exception)` 避免清理時異常

### 3. 並行處理架構

- **同步操作**: `SyncBrowserOperator.execute_sync()` 使用 `ThreadPoolExecutor` 對所有瀏覽器執行相同操作
- **瀏覽器狀態檢測**（v1.12.1 新增）: 所有操作前自動檢查瀏覽器有效性，關閉的瀏覽器自動跳過，避免程序停頓
- **獨立執行緒**: `GameControlCenter._auto_press_loop_single()` 為每個瀏覽器啟動獨立執行緒，使用 `threading.Event` 控制停止
- **執行緒保護**（v1.12.1 新增）: 自動按鍵循環中檢測瀏覽器狀態，關閉時立即停止執行緒，避免無效操作
- **背景自動化**（v1.11.0 新增）: `GameControlCenter._auto_skip_click_loop()` 在背景持續運行，每 30 秒自動點擊所有瀏覽器的跳過區域
- **錯誤監控**（v1.15.0 新增）: `GameControlCenter._error_monitor_loop()` 在背景持續運行，每 10 秒檢測所有瀏覽器的錯誤訊息，檢測到異常時自動重新整理
- **最大工作數**: `Constants.MAX_THREAD_WORKERS = 10`
- **狀態檢測方法**: `_is_browser_alive()` 透過嘗試讀取 `driver.current_url` 判斷瀏覽器是否仍然有效

### 4. Proxy 中繼架構

```python
遠端 Proxy (需認證)
  ↓
SimpleProxyServer (本地埠 9000+, 無需認證)
  ↓
Chrome (使用本地 Proxy)
```

- `ProxyConnectionHandler` 處理 CONNECT 和 HTTP 請求
- 使用 `select.select()` 實現雙向數據轉發
- 每個瀏覽器使用獨立的本地埠（9000, 9001, 9002...）

### 5. 圖片識別流程

- **模板位置**: `img/lobby_login.png`, `img/lobby_confirm.png`, `img/error_message_left.png`（v1.15.0 更新）, `img/error_message_right.png`（v1.15.0 更新）, `img/bet_size/*.png`
- **檢測方法**: OpenCV `cv2.matchTemplate()` with `TM_CCOEFF_NORMED`
- **閾值**: `Constants.MATCH_THRESHOLD = 0.8`
- **座標計算**: 使用 Canvas 區域比例計算點擊座標
  - `LOBBY_LOGIN_BUTTON_X_RATIO = 0.55`, `LOBBY_LOGIN_BUTTON_Y_RATIO = 1.2`
  - `LOBBY_CONFIRM_BUTTON_X_RATIO = 0.78`, `LOBBY_CONFIRM_BUTTON_Y_RATIO = 1.15`
- **錯誤檢測**（v1.15.0 更新）:
  - 雙區域雙模板檢測：左側使用 `error_message_left.png`，右側使用 `error_message_right.png`
  - 檢測座標：左側 `(240, 190)`，右側 `(360, 190)`
  - 裁切邊距：`TEMPLATE_CROP_MARGIN = 20`
  - 匹配閾值：`MATCH_THRESHOLD = 0.8`
  - 監控頻率：每 10 秒檢測一次（在背景執行緒中持續運行）
  - 觸發條件：左右兩側都檢測到錯誤訊息時立即觸發
  - 自動處理：檢測到錯誤時自動重新整理瀏覽器

### 6. 資料結構（不可變）

所有資料類別使用 `@dataclass(frozen=True)` 確保不可變性：

- `UserCredential(username, password, proxy)` - Proxy 格式: `host:port:username:password`
- `BetRule(amount, duration, min_seconds, max_seconds)` - 下注規則：金額、持續時間（分鐘）、最小間隔秒數、最大間隔秒數
- `ProxyInfo.from_connection_string()` - 從連接字串建立實例

### 7. 常數管理 (v1.5.0 新增)

所有魔法數字統一在 `Constants` 類別中管理，避免硬編碼：

#### 視窗與座標常數

- `DEFAULT_WINDOW_WIDTH = 600` - 預設視窗寬度
- `DEFAULT_WINDOW_HEIGHT = 400` - 預設視窗高度
- `BETSIZE_INCREASE_BUTTON_X/Y` - 增加金額按鈕座標
- `BETSIZE_DECREASE_BUTTON_X/Y` - 減少金額按鈕座標
- `BETSIZE_DISPLAY_X/Y` - 金額顯示位置座標

#### 等待時間常數

- `LOGIN_WAIT_TIME = 5` - 登入後等待時間
- `BETSIZE_ADJUST_STEP_WAIT = 0.3` - 調整金額每步等待
- `FREE_GAME_CLICK_WAIT = 2` - 免費遊戲點擊間隔
- `FREE_GAME_SETTLE_INITIAL_WAIT = 3` - 免費遊戲結算初始等待
- `PROXY_SERVER_START_WAIT = 1` - Proxy 伺服器啟動等待
- `ERROR_MESSAGE_PERSIST_SECONDS = 1` - 錯誤訊息持續秒數閾值（v1.6.0 新增）
- `AUTO_SKIP_CLICK_INTERVAL = 30` - 自動跳過點擊間隔時間（v1.11.0 新增）

#### 重試與循環配置

- `BETSIZE_ADJUST_MAX_ATTEMPTS = 200` - 調整金額最大嘗試次數
- `BETSIZE_READ_MAX_RETRIES = 2` - 讀取金額最大重試次數
- `FREE_GAME_SETTLE_CLICK_COUNT = 5` - 免費遊戲結算點擊次數
- `DETECTION_WAIT_MAX_ATTEMPTS = 20` - 檢測等待最大嘗試次數

#### 截圖裁切常數

- `BETSIZE_CROP_MARGIN_X = 50` - 金額模板水平裁切邊距
- `BETSIZE_CROP_MARGIN_Y = 20` - 金額模板垂直裁切邊距
- `TEMPLATE_CROP_MARGIN = 20` - 通用模板裁切邊距

**重要原則**: 任何需要調整的數值都應定義為常數，避免在程式碼中出現魔法數字

## 關鍵檔案與目錄

### 配置檔案

- `lib/用戶資料.txt` - 格式: `帳號,密碼,IP:port:user:password`（第三欄為 Proxy，可為空）
- `lib/用戶規則.txt` - 格式: `金額:時間(分鐘):最小(秒數):最大(秒數)`
- 使用 `ConfigReader._read_file_lines()` 讀取，自動跳過標題行和註釋

### 圖片資源

- `img/lobby_login.png` - 遊戲登入畫面
- `img/lobby_confirm.png` - 確認按鈕（可自動生成）
- `img/bet_size/*.png` - 金額識別模板（檔名即為金額，如 `0.4.png`, `10.png`）

### 驅動程式

- **macOS/Linux**: `chromedriver`（需執行權限 `chmod +x`）
- **Windows**: `chromedriver.exe`
- 位置: 專案根目錄（與 `src/` 同級）

## 開發工作流程

### 本機執行

```bash
# 配置 Python 環境（虛擬環境或 Conda）
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows

# 安裝依賴
pip install -r requirements.txt

# 執行主程式
python src/main.py
```

**v1.12.0 變更**：程式會自動根據 `lib/用戶資料.txt` 中的帳號數量決定要開啟的瀏覽器數量（最多 12 個），無需手動輸入。

### 打包為可執行檔

```bash
# 使用 build.py 腳本（會清理舊檔案、檢查依賴、打包、複製資源）
python build.py

# 輸出位置: dist/AutoSlotGameMaster.exe
# 包含目錄: dist/img/, dist/lib/
```

### 除錯技巧

1. **調整日誌等級**: `LoggerFactory.get_logger(level=LogLevel.DEBUG)`
2. **單一瀏覽器測試**: 修改 `auto_determine_browser_count()` 返回 1（v1.12.0 後已改為自動決定）
3. **跳過圖片檢測**: 在 `_execute_image_detection_flow()` 中註釋相關步驟
4. **查看 Proxy 流量**: 使用 `self.logger.debug()` 輸出 Proxy 請求

## 命名與編碼規範

### 類別命名

- 管理器: `*Manager` (如 `BrowserManager`, `LocalProxyServerManager`)
- 操作器: `*Operator` (如 `SyncBrowserOperator`)
- 處理器: `*Handler` (如 `ProxyConnectionHandler`)
- 中心: `*Center` (如 `GameControlCenter`)

### 方法命名

- 私有方法: `_method_name()` (如 `_auto_press_loop_single()`)
- 建立資源: `create_*()` (如 `create_webdriver()`)
- 清理資源: `cleanup()` 或 `stop_*()`
- 同步操作: `*_all()` (如 `navigate_all()`, `adjust_betsize_all()`)

### 編碼慣例

- 使用 **繁體中文** 進行日誌輸出和使用者訊息
- 程式碼註釋和文件字串使用繁體中文
- 變數和函式名稱使用英文（snake_case）
- 常量使用大寫字母（UPPER_CASE）

### 錯誤處理

- 自訂例外繼承自 `AutoSlotGameError`
- 使用 `with suppress(Exception)` 處理清理時的非關鍵錯誤
- 在執行緒池中捕獲並記錄個別任務的例外

## 常見開發任務

### 新增命令到控制中心

在 `GameControlCenter.process_command()` 中添加新的 `elif cmd == 'x':` 分支，參考現有命令（如 `'b'` 調整金額、`'f'` 購買免費遊戲）。

### 新增圖片檢測模板

1. 在 `Constants` 中定義模板檔名和座標比例常量
2. 在 `img/` 目錄中放置模板圖片
3. 使用 `ImageDetector.detect_in_browser()` 進行檢測
4. 使用 `_continuous_detect_until_found()` 等待圖片出現

### 調整下注金額邏輯

- **可用金額**: 定義在 `Constants.GAME_BETSIZE_TUPLE`（必須按順序排列，共 64 種金額）
- **識別方法**: `SyncBrowserOperator.get_current_betsize()` 使用圖片比對
- **調整方法**: `adjust_betsize()` 計算索引差異，點擊增加/減少按鈕
- **按鈕座標**: 增加 `(440, 370)`，減少 `(360, 370)`（基於 600x400 視窗）

### 修改瀏覽器配置

在 `BrowserManager.create_chrome_options()` 中添加 Chrome 參數。注意：

- 使用 `--disable-*` 參數優化效能
- Chrome 131+ 特定優化已包含
- Proxy 設定透過 `--proxy-server=http://127.0.0.1:9000` 傳遞

### 處理多瀏覽器同步操作

使用 `SyncBrowserOperator.execute_sync()` 模式：

```python
def operation_func(context: BrowserContext, index: int, total: int) -> Any:
    # 在單一瀏覽器中執行操作
    return result

results = self.browser_operator.execute_sync(
    self.browser_contexts,
    operation_func,
    "操作名稱"
)
```

**v1.12.1 更新**: `execute_sync()` 現在會自動檢查瀏覽器狀態，已關閉的瀏覽器會被跳過並返回失敗結果（message: "瀏覽器已關閉"）。

### 檢查瀏覽器狀態（v1.12.1 新增）

在需要確認瀏覽器是否仍然有效時，使用 `_is_browser_alive()` 方法：

```python
def _is_browser_alive(self, driver: WebDriver) -> bool:
    """檢查瀏覽器是否仍然有效"""
    try:
        _ = driver.current_url
        return True
    except Exception:
        return False
```

**使用場景**：

- 規則執行中統計成功率時，只計算活躍瀏覽器
- 自動按鍵循環開始前，檢查瀏覽器是否有效
- 批次操作前，過濾掉已關閉的瀏覽器
- 背景執行緒中，避免對無效瀏覽器執行操作

## 測試注意事項

- **避免硬編碼座標**: 使用 Canvas 區域比例計算
- **Proxy 格式驗證**: 確保 `用戶資料.txt` 第三欄格式正確（`host:port:user:pass`）
- **金額模板建立**: 使用 `c` 命令在控制中心截取模板
- **Chrome 版本相容性**: 確保 `chromedriver` 版本與 Chrome 版本匹配
- **瀏覽器狀態測試**（v1.12.1 新增）: 測試規則執行或自動按鍵時關閉部分瀏覽器，確認系統能正確跳過並繼續運行

## 效能優化建議

1. **減少日誌輸出**: 在生產環境使用 `INFO` 等級，開發時使用 `DEBUG`
2. **並行度調整**: 根據系統資源調整 `MAX_THREAD_WORKERS`
3. **檢測間隔**: 調整 `DETECTION_INTERVAL` 平衡響應速度與 CPU 使用
4. **Proxy 緩衝區**: 調整 `PROXY_BUFFER_SIZE` 適應網路環境

---

**專案維護者**: simon980224  
**程式碼風格**: PEP 8 + 繁體中文註釋  
**Python 版本**: 3.8+
