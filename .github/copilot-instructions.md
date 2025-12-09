# AutoSlotGameMaster - AI 程式碼代理指南

## 專案概述

金富翁遊戲自動化系統 - 使用 Selenium WebDriver 控制多個瀏覽器實例，透過圖片識別和 Chrome DevTools Protocol 實現遊戲自動化。

**核心技術**: Python 3.8+, Selenium 4.25+, OpenCV, 本地 Proxy 中繼伺服器, 執行緒池並行處理

## 版本資訊

**目前版本**: v1.12.0

**更新內容**:

- v1.12.0: 移除視窗大小鎖定功能，允許用戶自由調整視窗大小（初始仍為 600x400）；改為自動決定瀏覽器數量（最多 12 個）
- v1.11.0: 新增自動跳過點擊功能，每 30 秒自動點擊跳過區域（背景執行，持續運行直到程式關閉）
- v1.10.0: 新增視窗大小鎖定功能，自動監控並恢復視窗大小（位置可自由移動）
- v1.9.0: 優化系統啟動流程（自動顯示完整指令列表，移除 emoji 符號，統一日誌格式）
- v1.8.0: 優化關閉瀏覽器功能（'q' 指令），支援選擇性關閉指定瀏覽器
- v1.7.1: 修正金額識別問題（統一使用 Constants 定義，移除重複定義和硬編碼數值）
- v1.7.0: 新增規則執行功能（'r' 指令），支援自動切換金額並按空白鍵，規則循環執行
- v1.6.2: 調整遊戲金額配置（GAME_BETSIZE 和 GAME_BETSIZE_TUPLE），從 73 種金額優化為 64 種金額
- v1.6.1: 調整金額顯示和裁切參數（BETSIZE_DISPLAY_Y: 380→370, CROP_MARGIN_X: 50→40, CROP_MARGIN_Y: 20→10）
- v1.6.0: 新增 lobby_confirm 錯誤訊息檢測與自動重啟機制（雙區域檢測、1 秒閾值觸發）
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
- **獨立執行緒**: `GameControlCenter._auto_press_loop_single()` 為每個瀏覽器啟動獨立執行緒，使用 `threading.Event` 控制停止
- **背景自動化**（v1.11.0 新增）: `GameControlCenter._auto_skip_click_loop()` 在背景持續運行，每 30 秒自動點擊所有瀏覽器的跳過區域
- **最大工作數**: `Constants.MAX_THREAD_WORKERS = 10`

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

- **模板位置**: `img/lobby_login.png`, `img/lobby_confirm.png`, `img/error_message.png`（v1.6.0 新增）, `img/bet_size/*.png`
- **檢測方法**: OpenCV `cv2.matchTemplate()` with `TM_CCOEFF_NORMED`
- **閾值**: `Constants.MATCH_THRESHOLD = 0.8`
- **座標計算**: 使用 Canvas 區域比例計算點擊座標
  - `LOBBY_LOGIN_BUTTON_X_RATIO = 0.55`, `LOBBY_LOGIN_BUTTON_Y_RATIO = 1.2`
  - `LOBBY_CONFIRM_BUTTON_X_RATIO = 0.78`, `LOBBY_CONFIRM_BUTTON_Y_RATIO = 1.15`
- **錯誤檢測**（v1.6.0 新增）:
  - 雙區域檢測：左側 `(240, 190)` 和右側 `(360, 190)`
  - 時間閾值：錯誤訊息持續 1 秒即觸發自動重啟
  - 自動重啟流程：重新整理 → 檢測 lobby_login → 點擊 → 等待 lobby_confirm

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

## 測試注意事項

- **避免硬編碼座標**: 使用 Canvas 區域比例計算
- **Proxy 格式驗證**: 確保 `用戶資料.txt` 第三欄格式正確（`host:port:user:pass`）
- **金額模板建立**: 使用 `c` 命令在控制中心截取模板
- **Chrome 版本相容性**: 確保 `chromedriver` 版本與 Chrome 版本匹配

## 效能優化建議

1. **減少日誌輸出**: 在生產環境使用 `INFO` 等級，開發時使用 `DEBUG`
2. **並行度調整**: 根據系統資源調整 `MAX_THREAD_WORKERS`
3. **檢測間隔**: 調整 `DETECTION_INTERVAL` 平衡響應速度與 CPU 使用
4. **Proxy 緩衝區**: 調整 `PROXY_BUFFER_SIZE` 適應網路環境

---

**專案維護者**: simon980224  
**程式碼風格**: PEP 8 + 繁體中文註釋  
**Python 版本**: 3.8+
