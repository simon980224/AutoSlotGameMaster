# AutoSlotGameMaster - 金富翁遊戲自動化系統

> 專業的多帳號遊戲自動化解決方案

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/Code%20Style-PEP%208-orange.svg)](https://www.python.org/dev/peps/pep-0008/)

## ✨ 特色功能

- 🚀 **並行啟動** - 同時啟動多個瀏覽器，節省時間
- 🎮 **自動操作** - 智慧遊戲控制，解放雙手
- 🖥️ **視窗管理** - 自動排列視窗，整齊有序
- 🔒 **執行緒安全** - 穩定可靠的狀態管理
- 📝 **完整日誌** - 詳細的操作記錄
- 🛠️ **易於配置** - 靈活的參數設定

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

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 設定帳號

編輯 `user_credentials.txt`：
```
username:password
user001:pass123
user002:pass456
```

### 3. 執行程式

```bash
python3 src/test.py
```

### 4. 控制遊戲

- 輸入 `c` 開始遊戲
- 輸入 `p` 暫停遊戲
- 輸入 `q` 退出程式

## 💻 系統需求

### 必要條件
- Python 3.8 或更高版本
- Chrome 瀏覽器
- ChromeDriver（已包含在專案中）

### 硬體建議
- **CPU**: 多核心處理器
- **記憶體**: 4GB+ (每個瀏覽器約 200-300MB)
- **螢幕**: 1920x1080 或更高解析度

### 支援的作業系統
- ✅ macOS
- ✅ Windows
- ✅ Linux

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

### 基本使用

```bash
python3 src/test.py
```

### 流程說明

1. **輸入數量** - 選擇要啟動的瀏覽器數量（1-20）
2. **自動登入** - 程式自動登入所有帳號
3. **視窗排列** - 自動排列成網格佈局
4. **開始控制** - 使用指令控制所有瀏覽器

### 可用指令

| 指令 | 功能 | 說明 |
|-----|------|-----|
| `c` | 繼續 | 開始自動操作遊戲 |
| `p` | 暫停 | 暫停所有自動操作 |
| `q` | 退出 | 關閉所有瀏覽器並退出 |

## ⚙️ 配置說明

### 視窗配置

在 `src/test.py` 中修改 `WindowConfig`：

```python
@dataclass
class WindowConfig:
    width: int = 600      # 視窗寬度
    height: int = 400     # 視窗高度
    columns: int = 5      # 每行視窗數
    rows: int = 4         # 每列視窗數
```

### 遊戲配置

在 `src/test.py` 中修改 `GameConfig`：

```python
@dataclass
class GameConfig:
    max_accounts: int = 20         # 最大帳號數
    key_interval: int = 15         # 按鍵間隔（秒）
    page_load_timeout: int = 300   # 頁面載入超時
    implicit_wait: int = 30        # 隱式等待時間
    explicit_wait: int = 5         # 顯式等待時間
```

## 📚 文檔

本專案提供完整的文檔：

- **[使用指南](USAGE_GUIDE.md)** - 詳細的使用說明和範例
- **[程式碼指南](CODE_GUIDE.md)** - 程式碼結構和開發指南
- **[重構總結](REFACTORING_SUMMARY.md)** - 重構改進說明
- **[重構報告](REFACTORING_REPORT.md)** - 詳細的統計和分析

## 🏗️ 專案結構

```
AutoSlotGameMaster/
├── src/
│   ├── test.py              # 主程式
│   ├── main.py              # （原始程式）
│   └── test copy.py         # （備份）
├── chromedriver             # Chrome 驅動程式（macOS/Linux）
├── chromedriver.exe         # Chrome 驅動程式（Windows）
├── requirements.txt         # Python 依賴套件
├── user_credentials.txt     # 使用者帳號設定
├── user_functions.txt       # 功能說明
├── README.md               # 本檔案
├── USAGE_GUIDE.md          # 使用指南
├── CODE_GUIDE.md           # 程式碼指南
├── REFACTORING_SUMMARY.md  # 重構總結
├── REFACTORING_REPORT.md   # 重構報告
└── LICENSE                 # 授權資訊
```

## ❓ 常見問題

### Q: 找不到 ChromeDriver？
**A**: 確保 `chromedriver` 檔案在專案根目錄，並且有執行權限。

### Q: 登入失敗？
**A**: 檢查 `user_credentials.txt` 格式和帳號密碼是否正確。

### Q: 視窗排列不正確？
**A**: 調整 `WindowConfig` 的參數以適應您的螢幕大小。

### Q: 如何修改按鍵間隔？
**A**: 修改 `GameConfig.key_interval` 的值（單位：秒）。

### Q: 可以同時操作多少個瀏覽器？
**A**: 預設最多 20 個，可以修改 `GameConfig.max_accounts` 調整。

更多問題請參考 [使用指南](USAGE_GUIDE.md)。

## 🔄 更新日誌

### v2.0.0 (2025-11-11) - 重大重構

#### ✨ 新增
- 完整的型別提示系統
- 結構化的日誌系統
- 執行緒安全的狀態管理器
- 詳細的文檔字串

#### 🔧 改進
- 統一命名規範（snake_case）
- 模組化程式碼結構
- 改進錯誤處理機制
- 優化函式職責分離

#### 📝 文檔
- 新增使用指南
- 新增程式碼指南
- 新增重構報告
- 新增重構總結

### v1.0.0 (初始版本)
- 基本的多帳號登入功能
- 視窗排列功能
- 遊戲自動控制

## 🛡️ 安全提示

⚠️ **重要提醒**：

1. ❌ 不要分享 `user_credentials.txt` 檔案
2. 🔑 定期更改密碼
3. 🚫 不要在公共電腦上使用
4. 📋 注意遵守遊戲的使用條款
5. 💾 定期備份重要資料

## 🤝 貢獻

歡迎貢獻！請遵循以下步驟：

1. Fork 本專案
2. 建立特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

### 程式碼風格

本專案遵循：
- PEP 8 - Python 程式碼風格指南
- PEP 484 - 型別提示
- PEP 257 - 文檔字串慣例

## 📄 授權資訊

本專案採用 MIT 授權 - 詳見 [LICENSE](LICENSE) 檔案

## 👥 作者

- **simon980224** - [GitHub](https://github.com/simon980224)

## 🙏 致謝

- Selenium 團隊提供強大的自動化工具
- Python 社群的持續支持

## 📞 聯絡方式

如有問題或建議，請：
- 開啟 [Issue](https://github.com/simon980224/AutoSlotGameMaster/issues)
- 發送 Pull Request

## 🌟 Star History

如果這個專案對您有幫助，請給我們一個 ⭐️！

---

**免責聲明**：本工具僅供學習和研究使用。使用者應自行承擔使用本工具的風險，並遵守相關遊戲的使用條款和當地法律法規。

Made with ❤️ by simon980224
