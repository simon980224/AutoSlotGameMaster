# AutoSlotGameMaster

> 金富翁遊戲自動化系統 - 多瀏覽器並行控制、圖片識別、Proxy 中繼

[![Version](https://img.shields.io/badge/version-1.14.3-brightgreen.svg)](https://github.com/simon980224/AutoSlotGameMaster)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://github.com/simon980224/AutoSlotGameMaster)

一個使用 Selenium WebDriver、OpenCV 圖片識別和 Chrome DevTools Protocol 實現的遊戲自動化系統。支援多瀏覽器並行控制、本地 Proxy 中繼、自動下注和免費遊戲購買等功能。

## ✨ 核心特性

- 🚀 **多瀏覽器並行控制** - 使用執行緒池同步管理多個瀏覽器實例
- 🔍 **圖片識別** - OpenCV 模板匹配，自動檢測遊戲畫面並執行操作
- 🌐 **Proxy 中繼** - 本地無認證 Proxy 伺服器，自動轉發到遠端認證 Proxy
- 💰 **自動下注** - 智慧識別和調整下注金額（支援 64 種金額）
- 🎮 **遊戲控制中心** - 互動式命令介面，即時控制所有瀏覽器
- 🔄 **自動化流程** - 自動登入、導航、圖片檢測、點擊操作
- 📦 **一鍵打包** - 使用 PyInstaller 打包成 Windows 可執行檔

## 🏗️ 系統架構

### 核心元件

```
┌─────────────────────────────────────────────────────────┐
│                   AutoSlotGameApp                       │
│  (應用程式主類別 - 整合所有元件)                         │
└─────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
┌───────▼──────┐  ┌────────▼────────┐  ┌─────▼────────┐
│ ConfigReader │  │ BrowserManager  │  │   Proxy      │
│ 配置讀取器    │  │ 瀏覽器管理器     │  │   Manager    │
└──────────────┘  └─────────────────┘  └──────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
┌───────▼──────────┐  ┌────▼─────────┐  ┌───▼──────────┐
│ SyncBrowser      │  │ ImageDetector│  │ GameControl  │
│ Operator         │  │ 圖片檢測器    │  │ Center       │
│ 同步操作器        │  └──────────────┘  │ 控制中心      │
└──────────────────┘                    └──────────────┘
```

### Proxy 中繼架構

```
遠端 Proxy (需認證)
  ↓ host:port:user:pass
SimpleProxyServer (本地埠 9000+, 無需認證)
  ↓ 127.0.0.1:9000
Chrome (透過本地 Proxy 連接)
```

## 📋 目錄結構

```
AutoSlotGameMaster/
├── src/
│   ├── main.py              # 主程式（3500+ 行，包含所有類別）
│   ├── main_backup.py       # 備份檔案
│   └── test.py              # 測試腳本
├── lib/
│   ├── 用戶資料.txt          # 使用者憑證配置
│   └── 用戶規則.txt          # 下注規則配置
├── img/
│   ├── lobby_login.png      # 登入畫面模板
│   ├── lobby_confirm.png    # 確認按鈕模板
│   ├── error_message.png    # 錯誤訊息模板（v1.6.0 新增）
│   └── bet_size/            # 金額識別模板（64 張圖片）
│       ├── 2.png
│       ├── 4.png
│       ├── 6.png
│       └── ... (共 64 種金額)
├── .github/
│   └── copilot-instructions.md  # AI 代理指南
├── chromedriver             # Chrome 驅動程式 (macOS/Linux)
├── chromedriver.exe         # Chrome 驅動程式 (Windows)
├── build.py                 # 打包腳本
├── requirements.txt         # Python 依賴
├── sett.png                 # 應用程式圖示
├── LICENSE                  # MIT 授權
└── README.md                # 本檔案
```

## 🚀 快速開始

### 環境需求

- **Python**: 3.8 或以上版本
- **Chrome**: 已安裝 Google Chrome 瀏覽器
- **ChromeDriver**: 與 Chrome 版本相符的驅動程式（已包含）
- **作業系統**: Windows 10/11, macOS 10.14+, Linux

### 安裝步驟

#### 1. 複製專案

```bash
git clone https://github.com/simon980224/AutoSlotGameMaster.git
cd AutoSlotGameMaster
```

#### 2. 建立虛擬環境（建議）

```bash
# 使用 venv
python -m venv venv

# 啟動虛擬環境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

#### 3. 安裝依賴

```bash
pip install -r requirements.txt
```

依賴套件：

- `selenium>=4.25.0` - 瀏覽器自動化
- `webdriver-manager>=4.0.0` - 驅動程式管理
- `pillow>=10.0.0` - 圖片處理
- `opencv-python>=4.8.0` - 圖片識別
- `numpy>=1.24.0` - 數值計算

#### 4. 配置檔案

編輯 `lib/用戶資料.txt`（帳號資訊）：

```
帳號:密碼:IP:port:user:password
user001,password123,82.22.69.70:7277:proxyuser:proxypass
user002,password456,  # 第三欄空白表示不使用 Proxy
```

編輯 `lib/用戶規則.txt`（下注規則）：

```
金額:時間(分鐘):最小(秒數):最大(秒數)
4:10:1:1
8:20:1:10
```

**說明**：每條規則格式為 `金額:持續時間:最小間隔:最大間隔`

- 第一條：金額 4，持續 10 分鐘，每次按空白鍵間隔 1~1 秒
- 第二條：金額 8，持續 20 分鐘，每次按空白鍵間隔 1~10 秒（每個瀏覽器獨立隨機）

#### 5. 確保驅動程式可執行

```bash
# macOS/Linux
chmod +x chromedriver

# Windows 無需此步驟
```

### 執行程式

```bash
python src/main.py
```

## 🎮 使用指南

### 程式執行流程

1. **載入配置** - 讀取使用者憑證和下注規則
2. **選擇數量** - 輸入要開啟的瀏覽器數量（1-N）
3. **啟動 Proxy** - 為需要的瀏覽器啟動本地 Proxy 中繼
4. **建立瀏覽器** - 並行建立所有瀏覽器實例
5. **自動登入** - 同步執行登入操作
6. **導航遊戲** - 進入遊戲頁面並調整視窗排列
7. **圖片檢測** - 檢測並點擊 `lobby_login` 和 `lobby_confirm`
8. **控制中心** - 進入互動式控制介面

### 控制中心命令

程式進入控制中心後，可使用以下命令：

#### 遊戲控制

```bash
# 開始自動按鍵（隨機間隔）
s 1,2          # 間隔 1~2 秒
s 0.5,1.5      # 間隔 0.5~1.5 秒

# 開始執行規則（自動切換金額）
r              # 依照 lib/用戶規則.txt 自動切換金額並按空白鍵
               # 規則格式: 金額:時間(分鐘):最小(秒數):最大(秒數)
               # 規則循環執行，時間到達自動切換下一條

# 暫停自動按鍵或規則執行
p

# 調整下注金額
b 0.4          # 調整所有瀏覽器到 0.4
b 10           # 調整所有瀏覽器到 10
b 2000         # 調整所有瀏覽器到 2000

# 購買免費遊戲
f 0            # 所有瀏覽器都購買
f 1            # 第 1 個瀏覽器購買
f 1,2,3        # 第 1、2、3 個瀏覽器購買

# 設定自動旋轉
a 10           # 自動旋轉 10 次
a 50           # 自動旋轉 50 次
a 100          # 自動旋轉 100 次

# 截取金額模板（用於金額識別）
c
```

#### 系統控制

```bash
# 顯示幫助
h

# 退出控制中心
q
```

### 金額識別模板建立

如果 `img/bet_size/` 中缺少某些金額模板：

1. 手動調整遊戲內的金額到目標值
2. 在控制中心輸入 `c` 進入截圖模式
3. 輸入當前金額（例如：`0.4`）
4. 系統自動截取並儲存模板為 `img/bet_size/0.4.png`

## 📦 打包為可執行檔

使用內建的打包腳本：

```bash
python build.py
```

打包腳本會自動：

1. ✅ 清理舊的構建檔案
2. ✅ 檢查必要檔案和依賴
3. ✅ 使用 PyInstaller 打包
4. ✅ 複製資源檔案（img/, lib/）
5. ✅ 清理臨時檔案

輸出位置：`dist/AutoSlotGameMaster.exe`

打包後的目錄結構：

```
dist/
├── AutoSlotGameMaster.exe
├── img/
│   ├── lobby_login.png
│   ├── lobby_confirm.png
│   ├── error_message.png
│   └── bet_size/
└── lib/
    ├── 用戶資料.txt
    └── 用戶規則.txt
```

## 🔧 進階配置

### 常量調整

編輯 `src/main.py` 中的 `Constants` 類別：

```python
class Constants:
    # 執行緒池配置
    MAX_THREAD_WORKERS = 10  # 最大並行工作數

    # 超時設定
    DEFAULT_TIMEOUT_SECONDS = 30
    DEFAULT_PAGE_LOAD_TIMEOUT = 600

    # 圖片檢測
    MATCH_THRESHOLD = 0.8  # 匹配閾值（0-1）
    DETECTION_INTERVAL = 1.0  # 檢測間隔（秒）

    # 錯誤檢測（v1.6.0 新增）
    ERROR_MESSAGE_LEFT_X = 240  # 左側錯誤訊息區域 X 座標
    ERROR_MESSAGE_LEFT_Y = 190  # 左側錯誤訊息區域 Y 座標
    ERROR_MESSAGE_RIGHT_X = 360  # 右側錯誤訊息區域 X 座標
    ERROR_MESSAGE_RIGHT_Y = 190  # 右側錯誤訊息區域 Y 座標
    ERROR_MESSAGE_PERSIST_SECONDS = 1  # 錯誤訊息持續秒數閾值

    # 視窗配置
    DEFAULT_WINDOW_WIDTH = 600
    DEFAULT_WINDOW_HEIGHT = 400
    DEFAULT_WINDOW_COLUMNS = 4  # 每行視窗數

    # Proxy 配置
    DEFAULT_PROXY_START_PORT = 9000
    PROXY_BUFFER_SIZE = 4096
```

### Chrome 選項調整

在 `BrowserManager.create_chrome_options()` 中添加參數：

```python
chrome_options.add_argument("--headless")  # 無頭模式
chrome_options.add_argument("--window-size=1920,1080")  # 自訂視窗大小
```

### 日誌等級

```python
# 在 main() 函式中調整
logger = LoggerFactory.get_logger(level=LogLevel.DEBUG)  # 詳細除錯
logger = LoggerFactory.get_logger(level=LogLevel.INFO)   # 一般資訊
```

## 🏛️ 架構設計

### 設計模式

1. **工廠模式** - `LoggerFactory`, `BrowserManager`
2. **單例模式** - Logger 實例快取
3. **依賴注入** - 所有主要類別支援建構函式注入
4. **上下文管理器** - 自動資源清理（`with` 語句）
5. **執行緒池模式** - `ThreadPoolExecutor` 並行處理
6. **策略模式** - `SyncBrowserOperator.execute_sync()`

### 資料結構

所有資料類別使用 `@dataclass(frozen=True)` 確保不可變性：

```python
@dataclass(frozen=True)
class UserCredential:
    username: str
    password: str
    proxy: Optional[str] = None

@dataclass(frozen=True)
class BetRule:
    amount: float
    duration: int

@dataclass(frozen=True)
class ProxyInfo:
    host: str
    port: int
    username: str
    password: str
```

### 錯誤處理

自訂例外層次結構：

```
AutoSlotGameError (基礎例外)
├── ConfigurationError (配置錯誤)
├── BrowserCreationError (瀏覽器建立錯誤)
├── ProxyServerError (Proxy 伺服器錯誤)
└── ImageDetectionError (圖片檢測錯誤)
```

## 🐛 除錯技巧

### 1. 單一瀏覽器測試

修改 `prompt_browser_count()` 強制返回 1：

```python
def prompt_browser_count(self) -> int:
    return 1  # 強制單一瀏覽器
```

### 2. 查看詳細日誌

```python
logger = LoggerFactory.get_logger(level=LogLevel.DEBUG)
```

### 3. 跳過圖片檢測

在 `_execute_image_detection_flow()` 中註釋相關步驟：

```python
def _execute_image_detection_flow(self) -> None:
    # self._handle_lobby_login(reference_browser)  # 註釋此行
    # self._handle_lobby_confirm(reference_browser)  # 註釋此行
    pass
```

### 4. Proxy 連線問題

檢查 Proxy 格式：`host:port:username:password`

```bash
# 測試 Proxy 連線
curl -x http://username:password@host:port https://www.google.com
```

### 5. ChromeDriver 版本不符

```bash
# 檢查 Chrome 版本
google-chrome --version  # Linux
# 或在瀏覽器中訪問 chrome://version/

# 下載對應版本的 ChromeDriver
# https://chromedriver.chromium.org/downloads
```

## 📊 效能優化

1. **並行度** - 根據 CPU 核心數調整 `MAX_THREAD_WORKERS`
2. **檢測間隔** - 平衡 `DETECTION_INTERVAL` 與 CPU 使用率
3. **Proxy 緩衝** - 調整 `PROXY_BUFFER_SIZE` 適應網路狀況
4. **日誌等級** - 生產環境使用 `INFO`，開發使用 `DEBUG`

## 🤝 貢獻指南

歡迎提交 Issue 和 Pull Request！

### 開發流程

1. Fork 本專案
2. 建立功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

### 程式碼風格

- 遵循 **PEP 8** 規範
- 使用**繁體中文**撰寫註釋和日誌訊息
- 變數和函式使用 `snake_case`
- 類別使用 `PascalCase`
- 常量使用 `UPPER_CASE`

## 📝 版本歷史

### v1.14.3 (2025-12-11)

- 🐛 **修正按下 'p' 後規則仍繼續執行的問題**：在規則執行的關鍵步驟之間加入停止檢查
- ⚡ **停止響應優化**：按下 'p' 後系統可立即中斷當前規則，無需等待完整執行
- 🔍 **多重檢查點**：在金額調整前、自動按鍵啟動前、免費遊戲購買前都檢查停止標記
- 🎯 **精準控制**：停止信號觸發後，當前規則立即跳過，進入停止流程
- 💡 **使用體驗提升**：避免因長時間金額調整（可能超過 1 分鐘）導致停止延遲
- 🚀 **適用範圍**：標準規則（'s'）和免費遊戲規則（'f'）都已加入停止檢查

**修正細節**：

- `_execute_standard_rule()`：在金額調整前和自動按鍵啟動前檢查 `self._stop_event.is_set()`
- `_execute_free_game_rule()`：在金額調整前和免費遊戲購買前檢查 `self._stop_event.is_set()`
- 檢查點位置：規則資訊顯示後、操作執行前，確保無效操作不會啟動

### v1.14.2 (2025-12-11)

- 🐛 **修正規則執行循環問題**：'f' 規則執行後正確清除停止事件，確保循環繼續
- 🔄 **停止事件管理優化**：標準規則（'s'）和免費遊戲規則（'f'）在停止自動按鍵後立即清除停止事件
- 🎯 **循環執行改善**：規則執行主循環不再因停止事件殘留而意外退出
- 📊 **日誌輸出優化**：調整執行緒啟動順序，避免主執行緒和規則執行執行緒的日誌交錯
- 💡 **使用體驗提升**：規則循環（s → f → s → ...）現在可以正常運行，無需手動干預
- 🚀 **背景自動化整合**：30 秒自動跳過功能與免費遊戲規則完美配合，自動處理結算畫面

**修正細節**：

- `_execute_standard_rule()`：停止自動按鍵後添加 `self._stop_event.clear()` 清除停止事件
- `_execute_free_game_rule()`：停止自動按鍵後添加 `self._stop_event.clear()` 清除停止事件
- `_start_rule_execution()`：調整執行緒啟動順序，先輸出提示訊息再啟動規則執行執行緒

### v1.14.1 (2025-12-11)

- 🐛 **修正規則執行中 'f' 規則 AttributeError 問題**：改用 `browser_operator.last_canvas_rect` 替代 `self.last_canvas_rect`
- 📊 **優化金額識別失敗日誌**：即使在靜默模式（silent=True）下也記錄關鍵錯誤，避免調試困難
- 🔍 **週期性警告輸出**：金額識別失敗時每 20 次重試輸出一次警告，避免日誌過載但保留診斷資訊
- 🎯 **準確定位問題根源**：當金額調整時間過長（例如 2 分 29 秒）時，警告日誌可清楚指出是金額識別失敗導致
- 💡 **改善除錯體驗**：提示用戶檢查 `img/bet_size/` 資料夾中的金額模板圖片

**修正細節**：

- `_execute_free_game_rule()`：使用 `self.browser_operator.last_canvas_rect` 替代 `self.last_canvas_rect`
- `adjust_betsize()`：初始金額識別失敗時強制輸出錯誤日誌（即使 silent=True）
- `adjust_betsize()`：重試循環中每 20 次輸出一次警告日誌，包含嘗試次數資訊

### v1.14.0 (2025-12-10)

- ✨ **擴展規則執行功能**：支援 'f' 類型規則（購買免費遊戲）
- 🎮 **新規則格式**：`f:金額` - 購買指定金額的免費遊戲
- 🔄 **完整規則循環**：支援 a（自動旋轉）、s（標準規則）、f（免費遊戲）三種規則類型混合執行
- 🚀 **自動化流程**：免費遊戲購買完成後，背景自動跳過功能會自動處理結算畫面
- 📝 **規則執行邏輯**：階段 1 執行所有 'a' 規則（一次性），階段 2 循環執行 's' 和 'f' 規則

**規則設定範例**：

```
a:2:10          # 自動旋轉 10 次，金額 2
s:4:1:1:1       # 標準規則，金額 4，持續 1 分鐘，間隔 1~1 秒
f:8             # 購買免費遊戲，金額 8
s:10:2:1:10     # 標準規則，金額 10，持續 2 分鐘，間隔 1~10 秒
```

### v1.13.0 (2025-12-10)

- ✨ **擴展規則執行功能**：支援 'a' 類型規則（自動旋轉）和 's' 類型規則（標準規則）
- 🎯 **多種規則格式**：
  - `a:金額:次數` - 自動旋轉規則
  - `s:金額:時間(分鐘):最小(秒數):最大(秒數)` - 標準規則
- 🔄 **規則執行邏輯**：'a' 規則只執行一次，'s' 規則循環執行
- 📊 **日誌輸出優化**：新增 silent 參數，規則執行時減少冗餘日誌
- 🚀 **自動化流程改善**：規則執行更智慧，自動區分一次性規則和循環規則

### v1.12.1 (2025-12-09)

- 🐛 **修正規則執行中關閉瀏覽器導致程序停頓的問題**：添加瀏覽器狀態檢測機制
- 🔍 **智慧瀏覽器狀態檢測**：所有操作前自動檢查瀏覽器是否仍然有效
- 🛡️ **防止操作停頓**：關閉的瀏覽器自動跳過，不再嘗試執行操作
- 🔄 **規則執行優化**：規則執行中關閉部分瀏覽器時，系統自動調整計數並繼續運行
- 📊 **準確的成功率統計**：只計算活躍瀏覽器的操作結果，排除已關閉的瀏覽器
- ✨ **自動按鍵執行緒保護**：自動按鍵循環中檢測瀏覽器狀態，關閉時立即停止執行緒
- 🎯 **自動跳過點擊優化**：跳過區域點擊時檢測瀏覽器狀態，關閉的瀏覽器自動跳過
- 💡 **適用範圍**：修正涉及 `execute_sync()`、`_rule_execution_loop()`、`_auto_press_loop_single()` 等多個關鍵函式
- 🚀 **提升穩定性**：避免對已關閉瀏覽器執行操作導致的異常和延遲

**修正細節**：

- `SyncBrowserOperator.execute_sync()`：操作前檢查瀏覽器有效性，無效時返回失敗結果並附帶 "瀏覽器已關閉" 訊息
- `GameControlCenter._is_browser_alive()`：新增專用方法檢測瀏覽器狀態
- `GameControlCenter._auto_press_loop_single()`：循環開始前檢查瀏覽器狀態，關閉時立即退出執行緒
- `GameControlCenter._auto_skip_click_loop()`：點擊前檢查瀏覽器狀態，關閉的自動跳過
- `GameControlCenter._rule_execution_loop()`：統計時只計算活躍瀏覽器，避免誤報錯誤
- 所有命令處理：調整結果統計邏輯，排除 "瀏覽器已關閉" 的失敗記錄

### v1.12.0 (2025-12-09)

- 🔧 **移除視窗大小鎖定功能**：允許用戶自由調整視窗大小，不再強制恢復
- 📏 **保留初始視窗尺寸**：啟動時仍設定為 600x400
- 💨 **簡化系統資源**：減少背景執行緒數量，降低 CPU 使用率
- 🎯 **優化啟動流程**：瀏覽器數量改為自動決定（根據用戶資料檔案），最多支援 12 個
- ⚡ **提升使用體驗**：移除手動輸入步驟，程式啟動更流暢

### v1.11.0 (2025-12-06)

- ✨ **新增自動跳過點擊功能**：每 30 秒自動點擊跳過區域（背景執行，持續運行）
- 🔄 **背景執行緒運行**：獨立執行緒持續監控，自動點擊所有瀏覽器的跳過按鈕
- 🎯 **智慧座標定位**：使用 LOBBY_LOGIN_BUTTON 座標（X: 0.55, Y: 1.2）作為跳過區域
- 🚀 **自動啟動**：控制中心啟動時自動開始運行，無需手動操作
- 🛡️ **錯誤容忍**：個別瀏覽器點擊失敗不影響其他瀏覽器，靜默處理異常
- 🔌 **優雅停止**：程式關閉時自動停止背景執行緒，確保資源正確清理
- 📊 **靜默運行**：使用 debug 級別日誌，不干擾用戶操作
- 💡 **持續運行**：從啟動到關閉全程運行，自動處理遊戲結算畫面和彈窗

### v1.10.0 (2025-12-06)

- ✨ **新增視窗大小鎖定功能**：自動監控並恢復視窗大小，防止意外調整
- 🖼️ **固定視窗尺寸**：自動鎖定為 600x400，每 1 秒檢查一次並恢復
- 📍 **位置自由移動**：只鎖定大小，不限制視窗位置，可隨意拖曳
- 🔄 **獨立執行緒監控**：每個瀏覽器使用獨立執行緒，互不影響
- 🚀 **自動啟動**：控制中心啟動時自動開始監控，無需手動配置
- 🛡️ **錯誤容忍**：調整失敗時自動重試，確保視窗大小穩定
- 🔌 **優雅停止**：程式關閉時自動停止所有監控執行緒

### v1.9.0 (2025-12-06)

- ✨ **優化系統啟動流程**：控制中心啟動後自動顯示完整指令列表
- 🎨 **統一日誌格式**：移除所有 emoji 符號，使用文字標記（[成功]、[錯誤]、[警告]、[提示]、[檢測]）
- 🔇 **減少冗餘日誌**：金額調整操作支援靜默模式，規則執行時不再輸出大量「目前金額」訊息
- 💡 **改善用戶體驗**：暫停操作（'p' 指令）後自動顯示幫助訊息
- 📋 **自動顯示幫助**：啟動時自動執行 'h' 指令，無需手動輸入即可查看所有可用指令
- 🔧 **提升可讀性**：統一使用 `>` 代替 `•`，`=` 代替 `━`，提升終端機相容性

### v1.8.0 (2025-12-03)

- ✨ **優化關閉瀏覽器功能**：重構 `q` 指令，支援選擇性關閉指定瀏覽器
- 🎯 **靈活的關閉選項**：
  - `q 0` - 關閉所有瀏覽器並退出控制中心
  - `q 1` - 只關閉第 1 個瀏覽器
  - `q 1,2,3` - 關閉第 1、2、3 個瀏覽器（支援多選）
- 🔄 **智慧退出機制**：關閉所有瀏覽器時自動退出控制中心
- 🛡️ **從後往前刪除**：避免索引錯位問題，確保正確關閉指定瀏覽器
- 📊 **詳細狀態反饋**：顯示成功/失敗數量、剩餘瀏覽器數量
- 💡 **參考 'f' 指令設計**：保持命令風格一致性，提升使用體驗
- 📝 **更新幫助資訊**：清楚列出所有 `q` 命令用法

### v1.7.1 (2025-12-03)

- 🔧 **修正金額識別問題**：統一使用 Constants 定義，提升系統穩定性
- 🎯 **移除重複定義**：消除程式碼中的重複金額列表定義（GAME_BETSIZE_SET）
- 📊 **統一常數管理**：所有硬編碼數值改為參照 Constants 類別
- 🔢 **新增常數**：BETSIZE_MATCH_THRESHOLD、RULE_SWITCH_WAIT、AUTO_PRESS_THREAD_JOIN_TIMEOUT 等
- ✨ **改善可維護性**：所有超時、等待時間、閾值統一在 Constants 中定義
- 🐛 **修正 'c' 指令**：移除重複的 GAME_BETSIZE 定義，直接使用 Constants.GAME_BETSIZE
- 📝 **程式碼品質提升**：消除所有魔法數字，提高程式碼可讀性和一致性

### v1.7.0 (2025-12-03)

- ✨ **新增規則執行功能** - 全新的 `r` 指令，實現自動化金額切換策略
- 🎯 **智慧規則循環**：依照 `用戶規則.txt` 自動切換下注金額，時間到達後切換下一條規則
- 🔄 **無限循環執行**：所有規則執行完畢後自動回到第一條規則，持續運行
- 🎮 **整合自動按鍵**：每條規則執行時自動按空白鍵，時間到達前完全停止再調整金額
- 🛡️ **安全切換機制**：換規則前確保所有自動按鍵執行緒完全停止，等待畫面穩定後才調整金額
- ⏱️ **精準時間控制**：按分鐘設定每條規則持續時間，自動計時和切換
- 📊 **即時進度顯示**：每 60 秒顯示剩餘時間，清楚掌握執行進度
- 🚀 **程式啟動時載入**：規則在程式啟動時就讀取，避免執行時 I/O 延遲
- 📝 **統一輸出風格**：與其他功能保持一致的日誌格式和進度顯示
- 💡 **使用範例**：`r` 啟動規則執行，`p` 暫停，支援與自動按鍵功能互斥運行

**規則設定範例** (`lib/用戶規則.txt`)：

```
金額:時間(分鐘):最小(秒數):最大(秒數)
4:10:1:1
8:20:1:10
16:5:0.5:2
```

**執行效果**：

- 第 1 條規則：金額 4，持續 10 分鐘，每個瀏覽器間隔 1~1 秒按空白鍵
- 第 2 條規則：金額 8，持續 20 分鐘，每個瀏覽器隨機間隔 1~10 秒按空白鍵
- 第 3 條規則：金額 16，持續 5 分鐘，每個瀏覽器隨機間隔 0.5~2 秒按空白鍵
- 執行完後回到第一條規則，無限循環

### v1.6.2 (2025-12-03)

- 🎯 **金額配置優化**：調整遊戲金額配置以符合實際遊戲設定
- 🔢 更新 `GAME_BETSIZE` 和 `GAME_BETSIZE_TUPLE`：從 73 種金額優化為 64 種金額
- 📊 移除不常用的金額選項（如 0.4, 0.8, 1.0 等小額），保留 2-2000 範圍
- ✨ 提升金額識別準確度和調整效率

### v1.6.1 (2025-12-03)

- 🔧 **參數優化**：調整金額識別相關參數以提高準確度
- 📐 `BETSIZE_DISPLAY_Y`: 380 → 370（金額顯示位置 Y 座標）
- ✂️ `BETSIZE_CROP_MARGIN_X`: 50 → 40（金額模板水平裁切邊距）
- ✂️ `BETSIZE_CROP_MARGIN_Y`: 20 → 10（金額模板垂直裁切邊距）
- 📈 提升金額讀取和模板匹配的精確度

### v1.6.0 (2025-12-01)

- ✨ **新增錯誤訊息檢測與自動重啟機制**
- 🔍 雙區域檢測：同時檢測左側 `(240, 190)` 和右側 `(360, 190)` 的錯誤訊息
- ⚡ 快速響應：錯誤訊息持續 1 秒即觸發自動重啟（可避免長時間卡住）
- 🔄 智慧重啟流程：自動重新整理 → 檢測 lobby_login → 點擊 → 等待 lobby_confirm
- 📊 批次處理：同步收集所有瀏覽器錯誤狀態，批次執行重啟操作
- 🎯 精準檢測：只檢測需要重啟的瀏覽器，不影響正常運行的瀏覽器
- 📝 優化日誌：合併顯示相同狀態，減少冗餘輸出，提升可讀性

### v1.5.0 (2025-01-29)

- 🎯 **重大重構**：統一管理所有魔法數字至 Constants 類別
- 📐 新增視窗尺寸相關常數（DEFAULT_WINDOW_WIDTH/HEIGHT）
- 📍 新增按鈕座標常數（BETSIZE_INCREASE/DECREASE_BUTTON_X/Y 等）
- ⏱️ 新增操作等待時間常數（LOGIN_WAIT_TIME、FREE_GAME_CLICK_WAIT 等）
- 🔄 新增重試與循環配置常數（BETSIZE_ADJUST_MAX_ATTEMPTS、FREE_GAME_SETTLE_CLICK_COUNT 等）
- 🖼️ 新增截圖裁切範圍常數（BETSIZE_CROP_MARGIN_X/Y、TEMPLATE_CROP_MARGIN）
- ✨ 提升程式碼可維護性、可讀性和一致性
- 📚 移除所有硬編碼數值，集中管理配置參數

### v1.4.3 (2025-01-27)

- ⚡ 優化瀏覽器網路設定，提升連線效能
- 🚀 啟用 QUIC 協定、TCP Fast Open 和 NetworkService
- 🔧 移除可能降低效能的網路設定（dns-prefetch-disable 等）
- 💾 調整磁碟快取和媒體快取為 200MB，改善載入速度

### v1.4.2 (2025-01-27)

- 🐛 修正 Windows 中文路徑截圖儲存失敗問題
- 🔧 改用 `cv2.imencode()` + 標準檔案操作，完全支援 Unicode 路徑
- ✅ 解決「截圖已儲存」但檔案實際未建立的問題
- 📚 更新版本資訊和相關文件

### v1.4.1 (2025-01-26)

- ✨ 新增瀏覽器靜音功能
- 🔇 自動將所有瀏覽器實例設為靜音，避免遊戲聲音干擾
- 🔧 在 Chrome 選項中加入 `profile.content_settings.exceptions.sound` 設定
- 📚 更新相關程式碼註釋

### v1.4.0 (2025-01-25)

- ✨ 優化免費遊戲結算流程，調整點擊時機和間隔
- 🎮 改進結算畫面跳過功能：3 秒後開始點擊，每次間隔 3 秒，共點擊 5 次
- 🐛 修正點擊過快導致結算畫面未出現的問題
- 📚 更新相關日誌訊息，更清楚說明功能用途

### v1.3.0 (2025-01-25)

- ✨ 新增自動旋轉功能，支援設定 10、50、100 次自動旋轉
- 🎮 改進遊戲控制介面，添加 `a` 指令控制自動旋轉
- 📚 更新使用指南和命令說明文件

### v1.2.0 (2025-01-23)

- ✨ 新增專案啟動前自動清除 chromedriver 快取功能
- 🔧 改善程式啟動穩定性，避免殘留程序佔用資源
- 📚 更新相關文件說明

### v1.1.0 (2025-01-22)

- 🐛 修正 OpenCV 無法讀取中文路徑圖片的問題
- 🔧 程式碼優化與重構
- 📚 完善文件與註釋
- ⚡ 效能改進

### v1.0.0 (2025-01-22)

- ✨ 初始版本發布
- 🚀 多瀏覽器並行控制
- 🔍 圖片識別與自動化
- 🌐 Proxy 中繼功能
- 🎮 互動式控制中心

## ⚠️ 免責聲明

本專案僅供學習和研究用途。使用者需自行承擔使用本軟體的所有風險和責任。請遵守當地法律法規和遊戲服務條款。

## 📄 授權

本專案採用 [MIT License](LICENSE) 授權。

## 👨‍💻 作者

**simon980224** - [GitHub](https://github.com/simon980224)

## 🙏 致謝

- [Selenium](https://www.selenium.dev/) - 瀏覽器自動化框架
- [OpenCV](https://opencv.org/) - 電腦視覺函式庫
- [PyInstaller](https://www.pyinstaller.org/) - Python 打包工具

---

**⭐ 如果這個專案對您有幫助，請給個星星支持！**
