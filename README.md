# AutoSlotGameMaster

<p align="center">
  <strong>🎰 遊戲自動化系統 - 多瀏覽器並行控制 | 圖片識別 | Proxy 中繼</strong>
</p>

<p align="center">
  <a href="#"><img src="https://img.shields.io/badge/version-2.5.1-brightgreen.svg" alt="Version"></a>
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
│   ├── 用戶規則.txt      # 下注規則配置
│   └── 用戶設定.txt      # 用戶自定義參數設定
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

### 用戶設定 (`lib/用戶設定.txt`)

用於自定義系統參數，格式：`參數名稱=值`，以 `#` 開頭為註釋。

| 參數                  | 預設值 | 說明                         |
| --------------------- | ------ | ---------------------------- |
| `AUTO_CLICK_INTERVAL` | 30     | 自動跳過點擊間隔（秒）       |

> 未設定的參數使用系統預設值，檔案不存在時也不會報錯。

### 用戶規則格式

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

### 2.5.1 (2026-03-13)

- 新增: `lib/用戶設定.txt` 用戶自定義參數配置檔，支援 `參數名稱=值` 格式
- 新增: `AUTO_CLICK_INTERVAL` 參數開放用戶自定義（自動跳過點擊間隔秒數，預設 30）
- 新增: `Constants.CONFIGURABLE_SETTINGS` 映射表與 `apply_user_settings()` 類別方法，支援動態覆蓋常量
- 新增: `ConfigReader.read_user_settings()` 方法，解析用戶設定檔（檔案不存在時不報錯、使用預設值）
- 改進: `_step_load_config()` 初始化流程新增用戶設定讀取與套用步驟，啟動時自動載入

### 2.5.0 (2026-02-28)

- 修復: 下注金額模板擷取因 Canvas 外座標（比例 >1.0）導致 `Coordinate 'lower' is less than 'upper'` 崩潰，改用 Canvas rect + DPR 計算實際截圖像素座標
- 修復: 下注金額辨識因模板裁切區域變更導致全螢幕匹配誤判，改為先裁切下注區域（2 倍邊距）再進行模板匹配
- 修復: 錯誤訊息處理後回到大廳未導航至登入頁，導致找不到遊戲卡片無法重新進入遊戲
- 修復: 返回大廳偵測恢復流程未導航至登入頁，導致恢復失敗
- 修復: 恢復流程視窗過小（600×400）無法找到遊戲卡片，改為恢復前最大化視窗、進入遊戲後還原尺寸與位置
- 新增: `_get_betsize_crop_region` 共用方法 - 計算下注金額顯示區域的裁切座標
- 新增: `_recovery_navigate_to_login` 步驟加入 `_handle_error_return_to_game` 與 `_handle_lobby_return_recovery` 流程
- 改進: `click_betsize_button` 改用 `BrowserHelper.click_canvas_position` 統一座標計算
- 改進: 恢復流程新增視窗最大化/還原邏輯，確保遊戲卡片可見

### 2.4.0 (2026-02-27)

- 新增: 規則執行時間監控倒數提示，定期顯示剩餘執行時間（≤ 0.5 小時每分鐘、> 0.5 小時每 5 分鐘）
- 新增: `MAX_RECOVERY_ATTEMPTS` 常量（預設 5）—— 單一瀏覽器累計恢復次數上限，超過後自動關閉該瀏覽器（複用 q 命令邏輯）
- 新增: 返回大廳畫面偵測與自動恢復流程（點擊返回大廳 → 重新進入遊戲 → 圖片檢測流程）
- 新增: `LOBBY_RETURN_BUTTON_X_RATIO` / `LOBBY_RETURN_BUTTON_Y_RATIO` 常量
- 新增: `RULE_EXECUTION_TIME_CHECK_INTERVAL` 常量（規則執行時間檢查間隔 10 秒）
- 新增: `_handle_lobby_return_recovery` / `_recovery_click_lobby_return` 方法
- 新增: `_close_browser_for_recovery` 方法，恢復超過上限時自動關閉瀏覽器
- 改進: 錯誤監控循環擴展為同時偵測黑屏、錯誤訊息與返回大廳三種狀態
- 改進: 恢復成功後自動重置恢復計數器

### 2.3.1 (2026-02-25)

- 修復: 多瀏覽器並行啟動時登入表單輸入帳密偶發 WebDriverException 崩潰（`Symbols not available`），改用 JavaScript 填入帳密取代 `send_keys()`
- 修復: ChromeDriver 瞬態錯誤（空 Message）未被識別為可重試錯誤，導致本可重試成功的登入直接失敗
- 改進: `is_retryable_error()` 取代原 `is_network_error()`，同時支援例外類型判斷與關鍵字匹配
- 改進: 登入表單彈窗出現後增加動畫穩定等待，避免元素交互時 DOM 仍在渲染
- 改進: 登入重試前自動刷新頁面，確保 DOM 狀態乾淨
- 新增: `RETRYABLE_EXCEPTIONS` 常量 - 可重試的 Selenium 例外類型集合

### 2.3.0 (2026-02-25)

- 重構: 自動跳過點擊從錯誤監控循環中抽出為獨立執行緒 `AutoSkipClickThread`，使用 `Event.wait` 精準計時，不受監控邏輯影響
- 重構: 所有瀏覽器操作改為直接存取 driver，移除全部 `execute_task` 任務佇列呼叫，消除排隊等待和超時跳過問題
- 改進: 自動跳過點擊不再排除恢復中的瀏覽器，確保所有視窗都會被點擊
- 改進: 自動按鍵（按空白鍵）改為直接操作 driver，不再排隊
- 改進: 錯誤監控檢測（黑屏/錯誤訊息）改為直接操作 driver，提升檢測即時性
- 改進: 恢復流程（導航、進入遊戲、圖片檢測、點擊按鈕）全部改為直接操作 driver
- 改進: 免費遊戲購買/結算、關閉瀏覽器導航均改為直接操作 driver

### 2.2.1 (2026-02-24)

- 修復: `_execute_auto_spin_rule` 缺少 `_ensure_auto_press_stopped()`，規則從 s 型切換到 a 型時可能以錯誤金額下注
- 修復: 恢復流程點擊 game_confirm 後未等待圖片消失，導致卡在遊戲開始畫面
- 新增: `_recovery_wait_for_image_disappear` 方法 - 單一瀏覽器等待圖片消失（含自動重新點擊機制）
- 改進: 恢復流程的圖片檢測流程現在與初始登入流程一致

### 2.2.0 (2026-02-20)

- 新增: 錯誤訊息處理後自動檢查 Canvas 是否存在
- 新增: 若點擊錯誤確認後回到大廳，自動執行重新進入遊戲流程
- 新增: `_check_canvas_exists` 方法 - 檢查 iframe 和 Canvas 元素存在性
- 新增: `_handle_error_return_to_game` 方法 - 錯誤後回到大廳的恢復流程
- 改進: `_handle_error_click_confirm` 現在會判斷是否需要重新進入遊戲

### 2.1.0 (2026-02-20)

- 新增: 規則執行時間到達後，自動倒數 60 秒關閉所有瀏覽器
- 新增: AUTO_CLOSE_COUNTDOWN_SECONDS 常量（預設 60 秒）
- 改進: 倒數期間用戶輸入任何命令可取消自動關閉

### 2.0.6 (2026-02-18)

- 修正: AUTO_CLICK_INTERVAL 在金額調整期間會被暫停的問題
- 改進: 自動點擊功能現在從程式開始到結束永遠保持運行

### 2.0.5 (2026-02-18)

- 新增: AUTO_CLOSE_CLICK 座標 (0.5, 0.25)，每 30 秒自動跳過時同時點擊兩個位置

### 2.0.4 (2026-02-18)

- 改進: 自動跳過功能從按空白鍵改為點擊關閉按鈕座標
- 新增: AUTO_SKIP_CLICK_X_RATIO 和 AUTO_SKIP_CLICK_Y_RATIO 常量

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
