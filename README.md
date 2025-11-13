# AutoSlotGameMaster - 戰神賽特遊戲自動化系統

> 專業的多帳號老虎機遊戲自動化解決方案，支援 Proxy 與規則化執行

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/Code%20Style-PEP%208-orange.svg)](https://www.python.org/dev/peps/pep-0008/)
[![Selenium](https://img.shields.io/badge/Selenium-4.25+-green.svg)](https://www.selenium.dev/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-blue.svg)](https://opencv.org/)

## ✨ 特色功能

### 核心功能
- 🚀 **並行啟動** - 同時啟動多個瀏覽器實例，大幅節省時間
- 🎮 **自動操作** - 智慧遊戲控制，定時按鍵，解放雙手
- 🖥️ **視窗管理** - 自動排列成網格佈局，整齊有序
- 🔒 **執行緒安全** - 穩定可靠的多執行緒狀態管理
- 📝 **完整日誌** - 詳細的操作記錄與錯誤追蹤

### 進階功能
- 🌐 **Proxy 支援** - 支援每個帳號使用獨立 Proxy（含帳密驗證）
- 💰 **金額調整** - 透過圖像識別精準調整下注金額
- 📋 **規則執行** - 支援多階段金額與時間規則設定
- 🎯 **圖像識別** - 使用 OpenCV 進行畫面檢測與匹配
- 🎰 **免費遊戲** - 支援自動購買免費遊戲功能
- ⌨️ **CDP 控制** - 使用 Chrome DevTools Protocol 精準控制

## 📋 目錄

- [快速開始](#快速開始)
- [系統需求](#系統需求)
- [安裝說明](#安裝說明)
- [使用方法](#使用方法)
- [配置說明](#配置說明)
- [文檔](#文檔)
- [常見問題](#常見問題)
- [更新日誌](#更新日誌)
- [授權資訊](#授權資訊)

## 🚀 快速開始

### 1. 安裝相依套件

```bash
pip install -r requirements.txt
```

### 2. 設定帳號資訊

編輯 `lib/user_credentials.txt`，格式如下：
```
帳號,密碼,proxy
user001,pass123,ip:port:username:password
user002,pass456,
user003,pass789,142.111.48.253:7030:proxyuser:proxypass
```

**說明**：
- 第一行為標題，會自動跳過
- Proxy 欄位可選，留空表示不使用 Proxy
- Proxy 格式：`IP:埠號:使用者名稱:密碼`

### 3. 設定遊戲規則（選擇性）

編輯 `lib/user_rules.txt`，設定不同金額的執行時間：
```
金額:時間(分鐘)
0.4:10
1:15
2:20
```

**說明**：
- 第一行為標題，會自動跳過
- 金額必須在系統支援的範圍內
- 系統會依序執行各規則，全部完成後自動停止

### 4. 執行程式

**使用主程式（支援規則與 Proxy）**：
```bash
python3 src/main.py
```

**使用測試版本**：
```bash
python3 src/test.py
```

### 5. 控制遊戲

執行後可使用以下指令：

| 指令 | 功能 | 說明 |
|-----|------|-----|
| `c` | 繼續 | 開始自動操作遊戲 |
| `p` | 暫停 | 暫停所有自動操作 |
| `b <金額>` | 調整金額 | 調整下注金額，例如 `b 2.4` |
| `f` | 免費遊戲 | 購買並執行免費遊戲 |
| `q` | 退出 | 關閉所有瀏覽器並退出 |

## 💻 系統需求

### 必要條件
- **Python**: 3.8 或更高版本
- **Chrome**: 最新版本瀏覽器
- **ChromeDriver**: 已包含在專案中（需與 Chrome 版本相容）
- **作業系統**: macOS / Windows / Linux

### Python 相依套件
```
selenium>=4.25.0          # 瀏覽器自動化核心
opencv-python>=4.8.0      # 圖像識別與處理
numpy>=1.24.0             # 數值運算
pillow>=10.0.0            # 圖片處理
pyautogui>=0.9.54         # GUI 自動化
webdriver-manager>=4.0.0  # WebDriver 管理
```

### 硬體建議
- **CPU**: 多核心處理器（建議 4 核心以上）
- **記憶體**: 8GB+ RAM（每個瀏覽器約 200-300MB）
- **螢幕**: 1920x1080 或更高解析度（網格佈局需要）
- **網路**: 穩定的網路連線（支援 Proxy）

## 📦 安裝說明

### 方法 1：使用 pip

```bash
# 複製專案
git clone https://github.com/simon980224/AutoSlotGameMaster.git
cd AutoSlotGameMaster

# 安裝依賴
pip install -r requirements.txt
```

### 方法 2：使用虛擬環境（推薦）

```bash
# 建立虛擬環境
python3 -m venv venv

# 啟動虛擬環境
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安裝依賴
pip install -r requirements.txt
```

## 📖 使用方法

### 基本使用流程

```bash
# 1. 執行主程式
python3 src/main.py

# 2. 輸入要啟動的瀏覽器數量（1-12）
請輸入要啟動的瀏覽器數量 (1~12)：3

# 3. 等待自動登入與視窗排列
# 系統會自動：
# - 建立瀏覽器實例
# - 登入各個帳號
# - 排列視窗成網格
# - 進入遊戲頁面

# 4. 使用指令控制
請輸入指令：c        # 開始自動遊戲
請輸入指令：b 2.4    # 調整金額為 2.4
請輸入指令：f        # 購買免費遊戲
請輸入指令：p        # 暫停
請輸入指令：q        # 退出
```

### 進階功能說明

#### 1. 金額調整功能
使用圖像識別技術自動調整下注金額：
```bash
請輸入指令：b 2.4
# 系統會：
# 1. 截取當前金額顯示區域
# 2. 與預存圖片比對識別當前金額
# 3. 計算需要調整的次數
# 4. 自動按鍵調整到目標金額
# 5. 驗證調整結果
```

#### 2. 規則化執行
設定 `lib/user_rules.txt` 後，系統會自動：
1. 依序執行各規則
2. 每條規則開始前自動調整金額
3. 在指定時間內持續遊戲
4. 時間到後切換下一條規則
5. 全部完成後自動停止

#### 3. Proxy 使用
在 `lib/user_credentials.txt` 中設定：
```
帳號,密碼,proxy
user1,pass1,142.111.48.253:7030:proxyuser:proxypass
```
系統會自動建立 Chrome Extension 處理 Proxy 認證。

#### 4. 免費遊戲購買
```bash
請輸入指令：f
# 系統會：
# 1. 點擊免費遊戲按鈕
# 2. 點擊確認按鈕
# 3. 開始自動按空白鍵（每15秒）
# 4. 輸入 'over' 結束自動按鍵
```

## ⚙️ 配置說明

### 視窗配置

在 `src/main.py` 或 `src/test.py` 中修改 `WindowConfig`：

```python
@dataclass
class WindowConfig:
    width: int = 600      # 視窗寬度（像素）
    height: int = 400     # 視窗高度（像素）
    columns: int = 4      # 每行視窗數
    rows: int = 3         # 每列視窗數
```

### 遊戲配置

在 `src/main.py` 或 `src/test.py` 中修改 `GameConfig`：

```python
@dataclass
class GameConfig:
    max_accounts: int = 12              # 最大帳號數量
    key_interval: int = 15              # 按鍵間隔（秒）
    page_load_timeout: int = 600        # 頁面載入超時（秒）
    script_timeout: int = 600           # 腳本執行超時（秒）
    implicit_wait: int = 60             # 隱式等待時間（秒）
    explicit_wait: int = 10             # 顯式等待時間（秒）
    image_detect_timeout: int = 180     # 圖片檢測超時（秒）
    image_detect_interval: float = 0.5  # 圖片檢測間隔（秒）
    image_match_threshold: float = 0.8  # 圖片匹配閾值（0-1）
```

### 帳號設定格式

`lib/user_credentials.txt`:
```
帳號,密碼,proxy
account1,password1,142.111.48.253:7030:user:pass
account2,password2,                              # 不使用 proxy
account3,password3,31.59.20.176:6754:user:pass
```

### 規則設定格式

`lib/user_rules.txt`:
```
金額:時間(分鐘)
0.4:10          # 0.4 倍率執行 10 分鐘
1.2:15          # 1.2 倍率執行 15 分鐘
2.4:20          # 2.4 倍率執行 20 分鐘
```

**可用金額列表**：
```
0.4, 0.8, 1, 1.2, 1.6, 2, 2.4, 2.8, 3, 3.2, 3.6, 4, 5, 6, 7, 8, 9, 10,
12, 14, 16, 18, 20, 24, 28, 32, 36, 40, 48, 56, 60, 64, 72, 80, 100,
120, 140, 160, 180, 200, 240, 280, 300, 320, 360, 400, 420, 480, 500,
540, 560, 600, 640, 700, 720, 800, 840, 900, 960, 980, 1000, 1080,
1120, 1200, 1260, 1280, 1400, 1440, 1600, 1800, 2000
```

## 📚 文檔

目前專案包含以下文檔：

- **[README.md](README.md)** - 本檔案，專案總覽與使用說明
- **[報價單.md](報價單.md)** - 專案報價資訊
- **[你直接看這個.txt](你直接看這個.txt)** - 開發筆記與除錯資訊

### 更多資源
- **程式碼註解** - 所有函式都有完整的 docstring 說明
- **型別提示** - 使用 Python 型別提示提升程式碼可讀性
- **錯誤處理** - 完善的例外處理與日誌記錄

## 🏗️ 專案結構

```
AutoSlotGameMaster/
├── src/                        # 原始程式碼目錄
│   ├── main.py                 # 主程式（支援規則與 Proxy）
│   ├── test.py                 # 測試版本（簡化版）
│   └── test copy.py            # 備份檔案
├── lib/                        # 配置檔案目錄
│   ├── user_credentials.txt    # 帳號密碼設定（支援 Proxy）
│   ├── user_rules.txt          # 遊戲規則設定
│   └── user_proxyList.txt      # Proxy 列表
├── img/                        # 圖片資源目錄
│   ├── bet_size/               # 金額識別圖片
│   ├── lobby_login.png         # 大廳登入圖片
│   └── lobby_confirm.png       # 大廳確認圖片
├── docs/                       # 文檔目錄（空）
├── chromedriver                # ChromeDriver (macOS/Linux)
├── chromedriver.exe            # ChromeDriver (Windows)
├── requirements.txt            # Python 相依套件列表
├── README.md                   # 本檔案
├── 報價單.md                   # 報價資訊
├── 你直接看這個.txt            # 開發筆記
└── LICENSE                     # MIT 授權條款
```

### 核心模組說明

#### main.py（主程式）
- ✅ 支援 Proxy 連線（含帳密認證）
- ✅ 支援遊戲規則設定
- ✅ 圖像識別金額調整
- ✅ 免費遊戲購買功能
- ✅ CDP 精準控制

#### test.py（測試版）
- ✅ 簡化版本
- ✅ 基本登入與控制
- ✅ 適合測試使用

## ❓ 常見問題

### Q1: 找不到 ChromeDriver？
**A**: 
1. 確保 `chromedriver` 檔案在專案根目錄
2. macOS/Linux 需要執行權限：`chmod +x chromedriver`
3. 確認 ChromeDriver 版本與 Chrome 瀏覽器版本相容

### Q2: 登入失敗？
**A**: 
1. 檢查 `lib/user_credentials.txt` 格式是否正確
2. 確認帳號密碼正確無誤
3. 檢查網路連線狀態
4. 如果使用 Proxy，確認 Proxy 設定正確

### Q3: 視窗排列不正確？
**A**: 
1. 調整 `WindowConfig` 的 `width` 和 `height`
2. 調整 `columns` 和 `rows` 以適應螢幕大小
3. 建議螢幕解析度至少 1920x1080

### Q4: 圖像識別失敗？
**A**: 
1. 確認 `img/bet_size/` 資料夾有對應的金額圖片
2. 檢查 `image_match_threshold` 設定（預設 0.8）
3. 確保遊戲畫面清晰，視窗大小正確

### Q5: Proxy 連線失敗？
**A**: 
1. 確認 Proxy 格式：`ip:port:username:password`
2. 測試 Proxy 是否可用
3. 檢查 Proxy 帳號密碼是否正確
4. 確認防火牆設定

### Q6: 如何修改按鍵間隔？
**A**: 修改 `GameConfig.key_interval` 的值（單位：秒）。
```python
key_interval: int = 15  # 改為想要的秒數
```

### Q7: 可以同時操作多少個瀏覽器？
**A**: 
- 預設最多 12 個
- 可修改 `GameConfig.max_accounts` 調整
- 實際上限取決於電腦效能

### Q8: 規則設定無效？
**A**: 
1. 確認 `lib/user_rules.txt` 格式正確
2. 檢查金額是否在 `GAME_BETSIZE` 列表中
3. 查看日誌訊息確認規則是否載入成功

### Q9: 程式突然中斷？
**A**: 
1. 查看終端機的錯誤訊息
2. 檢查網路連線狀態
3. 確認 Chrome 沒有崩潰
4. 檢查記憶體使用情況

### Q10: 如何更新 ChromeDriver？
**A**: 
1. 前往 [ChromeDriver 下載頁面](https://chromedriver.chromium.org/downloads)
2. 下載與 Chrome 版本相符的 ChromeDriver
3. 替換專案根目錄的 `chromedriver` 檔案

## 🔄 版本歷史

### v2.0.0 (2025-01-13) - 主要更新

#### ✨ 新增功能
- ✅ **Proxy 支援**：每個帳號可設定獨立 Proxy（含帳密認證）
- ✅ **遊戲規則**：支援多階段金額與時間規則設定
- ✅ **圖像識別**：使用 OpenCV 自動識別並調整下注金額
- ✅ **免費遊戲**：自動購買免費遊戲功能
- ✅ **CDP 控制**：使用 Chrome DevTools Protocol 精準控制鍵盤與滑鼠
- ✅ **Canvas 操作**：動態計算 Canvas 座標進行精準點擊

#### 🔧 改進
- 🔧 完整的型別提示（Type Hints）
- 🔧 結構化的日誌系統
- 🔧 執行緒安全的狀態管理器
- 🔧 詳細的函式文檔字串（Docstrings）
- 🔧 統一的命名規範（snake_case）
- 🔧 模組化程式碼結構
- 🔧 改進的錯誤處理機制
- 🔧 網路連線優化設定
- 🔧 延長超時時間以適應不穩定網路

#### 🐛 修復
- 🐛 修復視窗排列問題
- 🐛 修復登入流程穩定性
- 🐛 修復多執行緒競爭條件
- 🐛 改善圖片檢測可靠性

#### 📝 已知問題
- ⚠️ 網路不穩定時第二個瀏覽器可能連線超時
- ⚠️ 某些情況下會出現 input 提示導致意外登出
- ⚠️ 免費遊戲結束後需要手動輸入 'over' 停止

### v1.0.0 (2024) - 初始版本
- ✅ 基本的多帳號登入功能
- ✅ 視窗排列功能
- ✅ 簡單的遊戲自動控制

## 🛡️ 安全與隱私

### ⚠️ 重要提醒

1. **❌ 不要分享**：
   - `lib/user_credentials.txt` - 包含帳號密碼
   - `lib/user_proxyList.txt` - 包含 Proxy 資訊
   - 任何含有個人資訊的檔案

2. **🔑 密碼安全**：
   - 定期更改密碼
   - 使用強密碼
   - 不要使用相同密碼

3. **🚫 使用限制**：
   - 不要在公共電腦上使用
   - 注意遵守遊戲的使用條款
   - 了解當地法律法規

4. **💾 資料備份**：
   - 定期備份重要設定檔
   - 保護好 Proxy 帳號資訊

5. **🌐 網路安全**：
   - 使用可信任的 Proxy
   - 注意網路連線安全
   - 定期檢查 Proxy 狀態

## 🤝 貢獻

歡迎貢獻！請遵循以下步驟：

1. Fork 本專案
2. 建立特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

### 程式碼風格指南

本專案遵循以下規範：
- **PEP 8** - Python 程式碼風格指南
- **PEP 484** - 型別提示（Type Hints）
- **PEP 257** - 文檔字串慣例（Docstrings）
- **snake_case** - 函式與變數命名
- **PascalCase** - 類別命名

### 提交前檢查清單

- [ ] 程式碼遵循 PEP 8 風格
- [ ] 新增適當的型別提示
- [ ] 撰寫完整的 docstring
- [ ] 測試程式碼可正常執行
- [ ] 更新相關文檔

## 📄 授權資訊

本專案採用 **MIT 授權** - 詳見 [LICENSE](LICENSE) 檔案

### MIT License 重點

- ✅ 商業使用
- ✅ 修改
- ✅ 分發
- ✅ 私人使用
- ⚠️ 無保證責任
- ⚠️ 需保留版權聲明

## 👥 作者與貢獻者

- **simon980224** - 初始開發 - [GitHub](https://github.com/simon980224)

## 🙏 致謝

感謝以下開源專案：

- **[Selenium](https://www.selenium.dev/)** - 強大的瀏覽器自動化框架
- **[OpenCV](https://opencv.org/)** - 電腦視覺與圖像處理函式庫
- **[NumPy](https://numpy.org/)** - 科學計算基礎套件
- **[Python](https://www.python.org/)** - 優秀的程式語言

特別感謝：
- Python 社群的持續支持
- 所有測試與反饋的使用者

## 📞 聯絡方式

如有問題或建議，請：
- 📝 開啟 [Issue](https://github.com/simon980224/AutoSlotGameMaster/issues)
- 🔧 發送 Pull Request
- 📧 聯絡作者

## 🌟 支持專案

如果這個專案對您有幫助，請給我們一個 ⭐️！

[![GitHub stars](https://img.shields.io/github/stars/simon980224/AutoSlotGameMaster?style=social)](https://github.com/simon980224/AutoSlotGameMaster/stargazers)

---

## ⚖️ 免責聲明

**重要聲明**：

1. **教育目的**：本工具僅供學習和研究使用
2. **使用風險**：使用者應自行承擔使用本工具的風險
3. **法律責任**：請遵守相關遊戲的使用條款和當地法律法規
4. **無保證**：本軟體按「現況」提供，不提供任何明示或暗示的保證
5. **不負責任**：作者不對因使用本軟體造成的任何損失負責

**使用本工具即表示您已閱讀並同意上述聲明。**

---

<div align="center">

**Made with ❤️ by simon980224**

*AutoSlotGameMaster © 2024-2025*

</div>
