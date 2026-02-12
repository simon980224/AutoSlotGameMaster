# AutoSlotGameMaster - AI Coding Agent Instructions

## 專案概述

這是一個基於 Selenium WebDriver + OpenCV 的遊戲自動化系統，支援多瀏覽器並行控制、本地 Proxy 中繼、圖片識別與自動下注功能。

## 架構與核心模組

### 雙版本入口

- [src/main.py](src/main.py) - 戰神賽特自動化（主要開發）
- [src/main_jfw.py](src/main_jfw.py) - 金富翁自動化（類似架構但目標網站不同）

### 核心類別架構

```
Constants          → 所有常量集中管理（版本、URL、XPath、座標比例、超時）
UserCredential     → 用戶帳密 + Proxy 資料結構 (dataclass, frozen=True)
BetRule            → 下注規則：a(自動旋轉)、s(定時旋轉)、f(免費遊戲)
ConfigReader       → 讀取 lib/用戶資料.txt 和 lib/用戶規則.txt
LocalProxyServer   → 本地 Proxy 中繼伺服器（socket 實作）
BrowserManager     → Chrome WebDriver 管理與多視窗排列
ImageDetector      → OpenCV 模板匹配（cv2.matchTemplate）
SyncBrowserOperator → 同步操作所有瀏覽器（ThreadPoolExecutor）
GameControlCenter  → 互動式命令列控制面板
```

## 關鍵設計模式

### 座標計算使用比例而非絕對值

所有 Canvas 點擊座標都用比例定義，例如：

```python
GAME_LOGIN_BUTTON_X_RATIO = 0.5   # 相對於 canvas 寬度
GAME_LOGIN_BUTTON_Y_RATIO = 0.9   # 相對於 canvas 高度
```

### 配置檔案格式

- **用戶資料** (`lib/用戶資料.txt`): `帳號,密碼,IP:port:user:password` 每行一組
- **用戶規則** (`lib/用戶規則.txt`): 前綴 + 規則類型 + 參數
  - 前綴: 無=循環執行, `-`=執行一次, `#`=註釋
  - 類型: `s:金額:間隔:時間`, `a:金額:次數`, `f:金額[:類別]`

### 圖片模板放置

- 模板圖片放在 `img/` 目錄
- 金額識別模板在 `img/bet_size/` 子目錄
- 使用 OpenCV `cv2.matchTemplate` 搭配 `MATCH_THRESHOLD` (預設 0.8-0.9)

## 開發規範

### 新增常量

所有魔法數字必須加入 `Constants` 類別，按功能分組並加註解：

```python
# =========================================================================
# 視窗配置
# =========================================================================
DEFAULT_WINDOW_WIDTH: int = 600
```

### 錯誤處理

使用自訂例外類別層級：

```
AutoSlotGameError (基類)
├── ConfigurationError
├── BrowserCreationError
├── ProxyServerError
└── ImageDetectionError
```

### 日誌輸出

- 使用 `logging` 模組，避免直接 print
- 多執行緒環境下已設置 `PYTHONUNBUFFERED=1` 和行緩衝
- 分隔線使用 `Constants.LOG_SEPARATOR`

## 構建與執行

### 開發環境

```bash
pip install -r requirements.txt  # selenium, opencv-python, pillow, webdriver-manager
python src/main.py               # 執行戰神賽特版本
```

### 打包成執行檔

```bash
python build.py                  # 使用 PyInstaller 打包
```

需要 `sett.ico` 圖示檔案於專案根目錄。

## 常見修改場景

### 調整遊戲網站 URL

修改 `Constants.LOGIN_PAGE` 和相關 XPath 選擇器。

### 新增下注金額

更新 `Constants.GAME_BETSIZE` tuple，並在 `img/bet_size/` 加入對應模板。

### 調整點擊座標

修改 `Constants` 中對應的 `*_X_RATIO` / `*_Y_RATIO` 值。

### 切換遊戲版本

修改 `Constants.IS_SETTE_1` (True=賽特一, False=賽特二)。
