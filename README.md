# AutoSlotGameMaster

<p align="center">
  <strong>🎰 遊戲自動化系統 - 多瀏覽器並行控制 | 圖片識別 | Proxy 中繼</strong>
</p>

<p align="center">
  <a href="#"><img src="https://img.shields.io/badge/version-2.0.3-brightgreen.svg" alt="Version"></a>
  <a href="#"><img src="https://img.shields.io/badge/python-3.8%2B-blue.svg" alt="Python"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License"></a>
  <a href="#"><img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg" alt="Platform"></a>
</p>

---

## 📖 簡介

AutoSlotGameMaster 是一個使用 **Selenium WebDriver**、**OpenCV 圖片識別** 和 **Chrome DevTools Protocol** 實現的遊戲自動化系統。

### ✨ 核心功能

- 🖥️ **多瀏覽器並行控制** - 同時操控多個遊戲視窗，自動排列佈局
- 🔍 **智慧圖片識別** - 基於 OpenCV 模板匹配的畫面自動辨識
- 🌐 **本地 Proxy 中繼** - 支援獨立網路出口配置
- ⚡ **自動下注系統** - 定時旋轉、自動旋轉、免費遊戲購買
- 🔄 **異常自動恢復** - 黑屏檢測、掉線重連、錯誤自動處理
- 🎮 **互動式控制面板** - 便捷的命令列操作介面

---

## 🚀 快速開始

### 系統需求

- Python 3.8+
- Google Chrome 瀏覽器
- 作業系統：Windows / macOS / Linux

### 安裝

```bash
# 1. 複製專案
git clone https://github.com/your-repo/AutoSlotGameMaster.git
cd AutoSlotGameMaster

# 2. 安裝依賴
pip install -r requirements.txt

# 3. 設定用戶資料
# 編輯 lib/用戶資料.txt 和 lib/用戶規則.txt
```

### 執行

```bash
# 戰神賽特版本
python src/main.py

# 金富翁版本
python src/main_jfw.py
```

---

## 📁 專案結構

```
AutoSlotGameMaster/
├── src/
│   ├── main.py          # 戰神賽特自動化（主要入口）
│   └── main_jfw.py      # 金富翁自動化
├── lib/
│   ├── 用戶資料.txt      # 帳號密碼與 Proxy 設定
│   └── 用戶規則.txt      # 下注規則配置
├── img/
│   └── bet_size/        # 金額識別模板
├── build.py             # PyInstaller 打包腳本
├── requirements.txt     # Python 依賴
└── README.md
```

---

## ⚙️ 配置說明

### 用戶資料 (`lib/用戶資料.txt`)

每行一組帳號，格式：`帳號,密碼,IP:port:user:password`

```
帳號,密碼,代理IP:代理埠:代理帳號:代理密碼
user001,pass123,192.168.1.1:8080:proxyuser:proxypass
```

### 用戶規則 (`lib/用戶規則.txt`)

| 前綴 | 說明         |
| ---- | ------------ |
| (無) | 循環執行     |
| `-`  | 執行一次     |
| `#`  | 註釋（跳過） |

| 規則類型     | 格式                                    | 範例        |
| ------------ | --------------------------------------- | ----------- |
| `s` 定時旋轉 | `s:金額:最小間隔,最大間隔:持續時間(分)` | `s:4:1,3:5` |
| `a` 自動旋轉 | `a:金額:次數`                           | `a:8:100`   |
| `f` 免費遊戲 | `f:金額[:類別]`                         | `f:20:1`    |

---

## 🎮 控制面板指令

啟動後可使用以下指令：

| 指令              | 說明                         |
| ----------------- | ---------------------------- |
| `r [小時]`        | 執行規則（可選指定執行時間） |
| `p`               | 暫停執行                     |
| `a [次數]`        | 自動旋轉（10/50/100 次）     |
| `f [金額] [類別]` | 購買免費遊戲                 |
| `b [金額]`        | 調整下注金額                 |
| `q [編號]`        | 關閉瀏覽器（可選指定編號）   |
| `h`               | 顯示幫助                     |

---

## 🏗️ 架構設計

### 核心類別

```
Constants           → 系統常量集中管理
UserCredential      → 用戶帳密資料結構 (frozen dataclass)
BetRule             → 下注規則資料結構
ConfigReader        → 配置檔案讀取器
LocalProxyServer    → 本地 Proxy 中繼伺服器
BrowserManager      → Chrome WebDriver 管理器
ImageDetector       → OpenCV 圖片識別引擎
SyncBrowserOperator → 多瀏覽器同步操作器
GameControlCenter   → 互動式控制面板
```

### 設計特點

- **座標比例系統** - 所有 Canvas 點擊座標使用相對比例，適應不同解析度
- **自訂例外層級** - `AutoSlotGameError` 基類，便於統一錯誤處理
- **執行緒池並行** - 使用 `ThreadPoolExecutor` 實現多瀏覽器同步操作
- **上下文管理器** - 資源自動清理，避免記憶體洩漏

---

## 📦 打包發布

```bash
# 使用 PyInstaller 打包成執行檔
python build.py
```

打包需要：

- `sett.ico` 圖示檔案於專案根目錄
- PyInstaller 6.0+

---

## 🔧 開發指南

### 新增常量

所有魔法數字必須加入 `Constants` 類別：

```python
class Constants:
    # =========================================================================
    # 視窗配置
    # =========================================================================
    DEFAULT_WINDOW_WIDTH: int = 600
    DEFAULT_WINDOW_HEIGHT: int = 400
```

### 新增下注金額

1. 更新 `Constants.GAME_BETSIZE` tuple
2. 在 `img/bet_size/` 目錄加入對應金額的模板圖片

### 調整點擊座標

修改 `Constants` 中對應的 `*_X_RATIO` / `*_Y_RATIO` 值：

```python
GAME_LOGIN_BUTTON_X_RATIO: float = 0.5   # 相對於 canvas 寬度
GAME_LOGIN_BUTTON_Y_RATIO: float = 0.9   # 相對於 canvas 高度
```

---

## 📋 依賴套件

| 套件              | 版本    | 用途              |
| ----------------- | ------- | ----------------- |
| selenium          | ≥4.25.0 | 瀏覽器自動化      |
| webdriver-manager | ≥4.0.0  | ChromeDriver 管理 |
| opencv-python     | ≥4.8.0  | 圖片識別          |
| pillow            | ≥10.0.0 | 截圖處理          |
| numpy             | ≥1.24.0 | 數值計算          |
| pyinstaller       | ≥6.0.0  | 打包工具          |

---

## 📜 版本歷程

### 2.0.3 (2026-02-15)

- 修正: r 功能金額調整期間會自動下注的問題
- 改進: 金額調整必須全部瀏覽器成功才執行下一步
- 改進: 自動跳過功能從點擊改為按空白鍵

### 2.0.2 (2026-02-12)

- 新增: 根據 LOGIN_PAGE 自動切換 sett2 遊戲識別碼（fin88,richpanda 使用專用識別碼）

### 2.0.1 (2026-02-12)

- 修復: 暫停規則執行(p)後，手動指令(如 b、a)失效的問題
- 原因: `_stop_rule_execution` 未重置 `_stop_event`，導致後續操作被誤判為已停止

### 2.0.0 (2026-02-01)

- 重構: 全面模組化架構設計
- 新增: 多視窗同步操作功能
- 新增: 智慧圖片識別系統
- 新增: 互動式控制面板
- 新增: 錯誤監控與自動恢復機制

---

## ⚠️ 免責聲明

本軟體僅供學習與研究使用。使用者應自行承擔使用本軟體的所有風險與責任。作者不對任何因使用本軟體而產生的直接或間接損失負責。

---

## 📄 授權條款

本專案採用 [MIT License](LICENSE) 授權。

---

## 👥 作者

**凡臻科技** - _Initial work_

---

<p align="center">
  <sub>Made with ❤️ by 凡臻科技</sub>
</p>
