#!/usr/bin/env python3
"""
AutoSlotGameMaster 打包腳本
使用 PyInstaller 將 main.py 打包成 Windows 可執行檔

執行方式：
    python build.py

需要安裝：
    pip install pyinstaller

作者: simon980224
版本: 1.0.0
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


class BuildConfig:
    """建構配置"""
    
    # 專案資訊
    APP_NAME = "AutoSlotGameMaster"
    APP_VERSION = "2.0.0"
    AUTHOR = "simon980224"
    
    # 主程式檔案
    MAIN_SCRIPT = "src/main.py"
    
    # 輸出目錄
    OUTPUT_DIR = "dist"
    BUILD_DIR = "build"
    
    # 圖示檔案（如果有的話）
    # ICON_FILE = "img/icon.ico"  # 取消註解如果有圖示
    
    # 需要包含的資料檔案（打包進 exe）
    DATA_FILES = [
        ("lib/*", "lib"),            # 配置檔案目錄下所有檔案
        ("img/*", "img"),            # 圖片資源目錄下所有檔案
        ("img/bet_size/*", "img/bet_size"),  # bet_size 子目錄
        ("chromedriver", "."),       # ChromeDriver (macOS/Linux)
    ]
    
    # 需要包含的隱藏導入
    HIDDEN_IMPORTS = [
        "selenium",
        "selenium.webdriver",
        "selenium.webdriver.chrome",
        "selenium.webdriver.chrome.service",
        "selenium.webdriver.support",
        "selenium.webdriver.support.ui",
        "selenium.webdriver.support.expected_conditions",
        "selenium.webdriver.common.by",
        "selenium.common.exceptions",
        "webdriver_manager",
        "webdriver_manager.chrome",
        "PIL",
        "PIL.Image",
        "cv2",
        "numpy",
    ]
    
    # 排除的模組（減小檔案大小）
    EXCLUDES = [
        "tkinter",
        "matplotlib",
        "pandas",
        "scipy",
        "pytest",
        "IPython",
    ]


class Builder:
    """建構管理器"""
    
    def __init__(self, config: BuildConfig):
        """初始化建構器"""
        self.config = config
        self.project_root = Path(__file__).parent.absolute()
        
    def check_environment(self) -> bool:
        """檢查建構環境"""
        print("🔍 檢查建構環境...")
        
        # 檢查 Python 版本
        python_version = sys.version_info
        print(f"   Python 版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        if python_version < (3, 8):
            print("❌ 錯誤：需要 Python 3.8 或更高版本")
            return False
        
        # 檢查 PyInstaller 是否安裝
        try:
            import PyInstaller
            print(f"   PyInstaller 版本: {PyInstaller.__version__}")
        except ImportError:
            print("❌ 錯誤：未安裝 PyInstaller")
            print("   請執行: pip install pyinstaller")
            return False
        
        # 檢查主程式檔案
        main_script = self.project_root / self.config.MAIN_SCRIPT
        if not main_script.exists():
            print(f"❌ 錯誤：找不到主程式檔案 {self.config.MAIN_SCRIPT}")
            return False
        print(f"   主程式: {self.config.MAIN_SCRIPT}")
        
        # 檢查必要目錄
        for src, _ in self.config.DATA_FILES:
            src_path = self.project_root / src
            if not src_path.exists():
                print(f"⚠️  警告：找不到資源目錄 {src}")
        
        print("✅ 環境檢查完成\n")
        return True
    
    def clean_build_dirs(self) -> None:
        """清理舊的建構目錄"""
        print("🧹 清理舊的建構檔案...")
        
        dirs_to_clean = [
            self.project_root / self.config.BUILD_DIR,
            self.project_root / self.config.OUTPUT_DIR,
            self.project_root / f"{self.config.APP_NAME}.spec",
            self.project_root / "__pycache__",
            self.project_root / "src" / "__pycache__",
        ]
        
        for path in dirs_to_clean:
            if path.exists():
                if path.is_file():
                    path.unlink()
                    print(f"   已刪除: {path.name}")
                else:
                    shutil.rmtree(path)
                    print(f"   已刪除: {path.name}/")
        
        # 清理所有 .pyc 檔案
        for pyc_file in self.project_root.rglob("*.pyc"):
            pyc_file.unlink()
            print(f"   已刪除: {pyc_file.relative_to(self.project_root)}")
        
        print("✅ 清理完成\n")
    
    def build_pyinstaller_command(self) -> list:
        """建立 PyInstaller 指令"""
        cmd = [
            "pyinstaller",
            "--name", self.config.APP_NAME,
            "--onefile",  # 打包成單一執行檔
            "--console",  # 顯示 console 視窗（改為 --windowed 隱藏）
            "--clean",
            "--noconfirm",
        ]
        
        # 添加圖示（如果有）
        if hasattr(self.config, 'ICON_FILE'):
            icon_path = self.project_root / self.config.ICON_FILE
            if icon_path.exists():
                cmd.extend(["--icon", str(icon_path)])
        
        # 添加資料檔案（遞迴添加整個目錄）
        self._add_data_files(cmd)
        
        # 添加隱藏導入
        for module in self.config.HIDDEN_IMPORTS:
            cmd.extend(["--hidden-import", module])
        
        # 排除模組
        for module in self.config.EXCLUDES:
            cmd.extend(["--exclude-module", module])
        
        # 添加主程式
        cmd.append(str(self.project_root / self.config.MAIN_SCRIPT))
        
        return cmd
    
    def _add_data_files(self, cmd: list) -> None:
        """遞迴添加資料檔案到指令中"""
        print("\n📦 正在添加資源檔案...")
        
        # 添加 lib 目錄下所有檔案
        lib_dir = self.project_root / "lib"
        if lib_dir.exists():
            file_count = 0
            for file in lib_dir.rglob("*"):
                if file.is_file():
                    rel_path = file.relative_to(lib_dir)
                    dst_dir = f"lib/{rel_path.parent}" if rel_path.parent != Path(".") else "lib"
                    cmd.extend(["--add-data", f"{file}{os.pathsep}{dst_dir}"])
                    file_count += 1
            print(f"   ✓ lib/ - {file_count} 個檔案")
        
        # 添加 img 目錄下所有檔案
        img_dir = self.project_root / "img"
        if img_dir.exists():
            file_count = 0
            for file in img_dir.rglob("*"):
                if file.is_file():
                    rel_path = file.relative_to(img_dir)
                    dst_dir = f"img/{rel_path.parent}" if rel_path.parent != Path(".") else "img"
                    cmd.extend(["--add-data", f"{file}{os.pathsep}{dst_dir}"])
                    file_count += 1
            print(f"   ✓ img/ - {file_count} 個檔案")
        
        # 添加 chromedriver (支援 Windows 和 macOS/Linux)
        chromedriver_win = self.project_root / "chromedriver.exe"
        chromedriver_unix = self.project_root / "chromedriver"
        
        if chromedriver_win.exists():
            cmd.extend(["--add-binary", f"{chromedriver_win}{os.pathsep}."])
            size_mb = chromedriver_win.stat().st_size / (1024 * 1024)
            print(f"   ✓ chromedriver.exe ({size_mb:.1f} MB)")
        
        if chromedriver_unix.exists():
            cmd.extend(["--add-binary", f"{chromedriver_unix}{os.pathsep}."])
            size_mb = chromedriver_unix.stat().st_size / (1024 * 1024)
            print(f"   ✓ chromedriver ({size_mb:.1f} MB)")
        
        print()
    
    def build(self) -> bool:
        """執行建構"""
        print("🔨 開始建構 EXE 檔案...")
        print(f"   應用程式: {self.config.APP_NAME}")
        print(f"   版本: {self.config.APP_VERSION}")
        print(f"   作者: {self.config.AUTHOR}\n")
        
        # 建立指令
        cmd = self.build_pyinstaller_command()
        
        # 顯示指令（除錯用）
        print("📋 PyInstaller 指令:")
        print("   " + " ".join(cmd) + "\n")
        
        # 執行建構
        try:
            result = subprocess.run(cmd, check=True, cwd=self.project_root)
            
            if result.returncode == 0:
                print("\n✅ 建構成功！")
                return True
            else:
                print("\n❌ 建構失敗")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"\n❌ 建構過程發生錯誤: {e}")
            return False
        except Exception as e:
            print(f"\n❌ 未預期的錯誤: {e}")
            return False
    
    def create_readme(self) -> None:
        """建立 README 檔案到輸出目錄"""
        print("\n📝 建立使用說明...")
        
        output_dir = self.project_root / self.config.OUTPUT_DIR
        
        readme_content = f"""
╔═══════════════════════════════════════════════════════════════╗
║                {self.config.APP_NAME} v{self.config.APP_VERSION}                ║
║                     by {self.config.AUTHOR}                      ║
╚═══════════════════════════════════════════════════════════════╝

📋 使用說明
═══════════════════════════════════════════════════════════════

1. 首次使用設定
   ─────────────────────────────────────────────────────────
   □ 編輯 lib/user_credentials.txt 設定帳號密碼
     格式：帳號,密碼,proxy（可選）
     範例：user001,pass123,ip:port:username:password
   
   □ 編輯 lib/user_rules.txt 設定遊戲規則（可選）
     格式：金額:時間(分鐘)
     範例：0.4:10

2. 執行程式
   ─────────────────────────────────────────────────────────
   □ 將 {self.config.APP_NAME}.exe 放在任意位置
   □ 雙擊 {self.config.APP_NAME}.exe 啟動程式
   □ 輸入要啟動的瀏覽器數量（1-12）
   □ 等待自動登入與視窗排列完成
   
   ※ 所有配置檔案和圖片已內建於 exe，無需額外檔案

3. 控制指令
   ─────────────────────────────────────────────────────────
   c          - 開始自動遊戲
   p          - 暫停遊戲
   b <金額>   - 調整下注金額（例如：b 2.4）
   f          - 購買免費遊戲
   s          - 截取螢幕
   q          - 退出程式
   h          - 顯示幫助

4. 注意事項
   ─────────────────────────────────────────────────────────
   ⚠️ 確保 Chrome 瀏覽器已安裝最新版本
   ⚠️ 確保網路連線穩定
   ⚠️ 首次執行可能需要下載 ChromeDriver
   ⚠️ 單一執行檔啟動速度較慢（正常現象）
   ⚠️ 所有資源已打包進 exe，無需額外檔案

5. 常見問題
   ─────────────────────────────────────────────────────────
   Q: 程式無法啟動？
   A: 確認防毒軟體沒有阻擋程式執行

   Q: 登入失敗？
   A: 檢查 lib/user_credentials.txt 格式與內容

   Q: 視窗排列不正確？
   A: 調整螢幕解析度至 1920x1080 或更高

   Q: 圖像識別失敗？
   A: 所有圖片已內建，如果仍失敗請檢查網路連線
   
   Q: 啟動很慢？
   A: 這是正常的，單一執行檔需要先解壓縮到臨時目錄
   
   Q: 如何修改配置？
   A: 配置已內建，需要修改請重新編譯或使用原始碼版本

6. 技術支援
   ─────────────────────────────────────────────────────────
   GitHub: https://github.com/{self.config.AUTHOR}/{self.config.APP_NAME}
   Issues: https://github.com/{self.config.AUTHOR}/{self.config.APP_NAME}/issues

═══════════════════════════════════════════════════════════════

⚖️ 免責聲明
本工具僅供學習和研究使用，使用者應自行承擔使用風險。
請遵守相關遊戲的使用條款和當地法律法規。

© 2024-2025 {self.config.AUTHOR}. All rights reserved.
Licensed under MIT License.

═══════════════════════════════════════════════════════════════
"""
        
        readme_file = output_dir / "使用說明.txt"
        try:
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(readme_content.strip())
            print(f"   已建立: {readme_file.name}")
        except Exception as e:
            print(f"   ⚠️ 無法建立 README: {e}")
    
    def show_summary(self) -> None:
        """顯示建構摘要"""
        output_dir = self.project_root / self.config.OUTPUT_DIR
        exe_file = output_dir / f"{self.config.APP_NAME}.exe"
        
        print("\n" + "═" * 70)
        print("🎉 建構完成！")
        print("═" * 70)
        print(f"\n📦 輸出位置: {output_dir}")
        print(f"📄 執行檔: {exe_file.name}")
        print(f"📊 檔案大小: ", end="")
        
        # 計算檔案大小
        try:
            if exe_file.exists():
                file_size = exe_file.stat().st_size
                file_size_mb = file_size / (1024 * 1024)
                print(f"{file_size_mb:.2f} MB")
            else:
                print("無法計算")
        except Exception:
            print("無法計算")
        
        print("\n📁 檔案結構:")
        print(f"   dist/")
        print(f"   └── {self.config.APP_NAME}.exe    # 單一執行檔（包含所有依賴和資源）")
        
        print("\n🚀 如何使用:")
        print(f"   1. 複製 {exe_file.name} 到任意位置")
        print(f"   2. 雙擊執行 {self.config.APP_NAME}.exe")
        print(f"   3. 無需其他檔案，所有資源已打包進 exe")
        
        print("\n⚠️  注意事項:")
        print("   • 單一執行檔啟動速度較慢（需解壓縮到臨時目錄）")
        print("   • 首次執行時 Windows 可能會顯示安全警告")
        print("   • 需要安裝 Chrome 瀏覽器")
        print("   • 建議使用 Windows 10/11 系統")
        print("   • 所有配置檔案和圖片已內建於 exe 中")
        
        print("\n" + "═" * 70 + "\n")
    
    def run(self) -> bool:
        """執行完整的建構流程"""
        print("\n" + "═" * 70)
        print(f"  🚀 {self.config.APP_NAME} 建構工具")
        print("═" * 70 + "\n")
        
        # 1. 檢查環境
        if not self.check_environment():
            return False
        
        # 2. 清理舊檔案
        self.clean_build_dirs()
        
        # 3. 執行建構
        if not self.build():
            return False
        
        # 4. 建立說明文件
        self.create_readme()
        
        # 5. 顯示摘要
        self.show_summary()
        
        return True


def main():
    """主程式入口"""
    config = BuildConfig()
    builder = Builder(config)
    
    try:
        success = builder.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ 使用者中斷建構")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 發生未預期的錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
