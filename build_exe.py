"""
AutoSlotGameMaster - Windows EXE 建置腳本

此腳本使用 PyInstaller 將 main.py 打包成 Windows 可執行檔案

使用方式：
    python build_exe.py

執行前請確保已安裝所有相依套件：
    pip install -r requirements.txt
    pip install pyinstaller

作者: simon980224
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def check_dependencies():
    """檢查必要的相依套件"""
    print("=" * 60)
    print("檢查相依套件...")
    print("=" * 60)
    
    required_packages = [
        ('selenium', 'selenium'),
        ('webdriver_manager', 'webdriver_manager'),
        ('PIL', 'pillow'),
        ('cv2', 'opencv-python'),
        ('numpy', 'numpy'),
        ('PyInstaller', 'pyinstaller')
    ]
    
    missing_packages = []
    
    for import_name, package_name in required_packages:
        try:
            __import__(import_name)
            print(f"✓ {package_name} 已安裝")
        except ImportError:
            missing_packages.append(package_name)
            print(f"✗ {package_name} 未安裝")
    
    if missing_packages:
        print("\n" + "=" * 60)
        print("警告：缺少以下套件")
        print("=" * 60)
        for pkg in missing_packages:
            print(f"  - {pkg}")
        
        print("\n請執行以下指令安裝：")
        print("  pip install " + " ".join(missing_packages))
        return False
    
    print("\n✓ 所有相依套件已安裝")
    return True


def get_project_paths():
    """取得專案路徑"""
    script_dir = Path(__file__).resolve().parent
    src_dir = script_dir / "src"
    main_py = src_dir / "main.py"
    lib_dir = script_dir / "lib"
    img_dir = script_dir / "img"
    
    return {
        'project_root': script_dir,
        'src_dir': src_dir,
        'main_py': main_py,
        'lib_dir': lib_dir,
        'img_dir': img_dir
    }


def check_project_structure():
    """檢查專案結構"""
    print("\n" + "=" * 60)
    print("檢查專案結構...")
    print("=" * 60)
    
    paths = get_project_paths()
    
    if not paths['main_py'].exists():
        print(f"✗ 找不到 main.py: {paths['main_py']}")
        return False
    print(f"✓ 找到 main.py: {paths['main_py']}")
    
    if not paths['lib_dir'].exists():
        print(f"✗ 找不到 lib 目錄: {paths['lib_dir']}")
        return False
    print(f"✓ 找到 lib 目錄: {paths['lib_dir']}")
    
    if not paths['img_dir'].exists():
        print(f"⚠ 找不到 img 目錄: {paths['img_dir']}")
        print("  (img 目錄會在首次執行時自動建立)")
    else:
        print(f"✓ 找到 img 目錄: {paths['img_dir']}")
    
    return True


def build_exe():
    """建置 EXE 檔案"""
    print("\n" + "=" * 60)
    print("開始建置 Windows 可執行檔案...")
    print("=" * 60)
    
    paths = get_project_paths()
    project_root = paths['project_root']
    main_py = paths['main_py']
    
    # PyInstaller 指令參數
    pyinstaller_args = [
        'pyinstaller',
        '--onefile',                    # 打包成單一執行檔
        '--windowed',                   # 不顯示控制台視窗（如果需要看日誌，移除此選項）
        '--name=AutoSlotGameMaster',    # 執行檔名稱
        '--clean',                      # 清理暫存檔案
        '--noconfirm',                  # 不詢問覆蓋
        
        # 加入資料檔案
        f'--add-data={paths["lib_dir"]}{os.pathsep}lib',
        
        # 隱藏的 imports（PyInstaller 可能無法自動偵測）
        '--hidden-import=selenium',
        '--hidden-import=selenium.webdriver',
        '--hidden-import=selenium.webdriver.chrome',
        '--hidden-import=selenium.webdriver.chrome.service',
        '--hidden-import=selenium.webdriver.common.by',
        '--hidden-import=selenium.webdriver.support.ui',
        '--hidden-import=selenium.webdriver.support.expected_conditions',
        '--hidden-import=selenium.common.exceptions',
        '--hidden-import=webdriver_manager',
        '--hidden-import=webdriver_manager.chrome',
        '--hidden-import=PIL',
        '--hidden-import=PIL.Image',
        '--hidden-import=cv2',
        '--hidden-import=numpy',
        
        # 工作目錄
        f'--workpath={project_root / "build"}',
        f'--distpath={project_root / "dist"}',
        f'--specpath={project_root}',
        
        # 主程式
        str(main_py)
    ]
    
    # 如果 img 目錄存在，加入
    if paths['img_dir'].exists():
        pyinstaller_args.insert(-1, f'--add-data={paths["img_dir"]}{os.pathsep}img')
    
    print("\n執行 PyInstaller 指令：")
    print(" ".join(pyinstaller_args))
    print("\n請稍候，這可能需要幾分鐘...")
    print("=" * 60)
    
    try:
        # 執行 PyInstaller
        result = subprocess.run(
            pyinstaller_args,
            cwd=project_root,
            check=True,
            capture_output=False
        )
        
        print("\n" + "=" * 60)
        print("✓ 建置完成！")
        print("=" * 60)
        
        exe_path = project_root / "dist" / "AutoSlotGameMaster.exe"
        if exe_path.exists():
            print(f"\n可執行檔案位置：")
            print(f"  {exe_path}")
            print(f"\n檔案大小：{exe_path.stat().st_size / (1024*1024):.2f} MB")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 60)
        print("✗ 建置失敗")
        print("=" * 60)
        print(f"錯誤代碼：{e.returncode}")
        return False
    except Exception as e:
        print("\n" + "=" * 60)
        print("✗ 建置失敗")
        print("=" * 60)
        print(f"錯誤：{e}")
        return False


def create_readme():
    """建立使用說明檔案"""
    paths = get_project_paths()
    readme_path = paths['project_root'] / "dist" / "README.txt"
    
    readme_content = """
AutoSlotGameMaster - Windows 可執行檔案
========================================

使用前準備：
-----------
1. 確保 lib 目錄中包含以下檔案：
   - user_credentials.txt (帳號密碼檔案)
   - user_rules.txt (遊戲規則檔案)

2. 確保 img 目錄存在（首次執行時會自動建立必要的圖片）

3. 確保已安裝 Chrome 瀏覽器（程式會自動下載對應的 ChromeDriver）


執行方式：
---------
直接雙擊 AutoSlotGameMaster.exe 執行


注意事項：
---------
1. 首次執行時需要連接網路，以下載 ChromeDriver
2. 如果需要看執行日誌，可以從命令提示字元（cmd）執行
3. 程式執行時會自動開啟 Chrome 瀏覽器
4. 請勿關閉瀏覽器視窗，否則程式會中斷


檔案結構：
---------
AutoSlotGameMaster.exe  - 主程式
lib/                    - 設定檔目錄
  ├─ user_credentials.txt
  ├─ user_rules.txt
  └─ user_proxyList.txt (選用)
img/                    - 圖片模板目錄
  └─ bet_size/         - 下注金額圖片


問題排除：
---------
1. 如果程式無法啟動，請確認：
   - 是否已安裝 Chrome 瀏覽器
   - 是否有網路連線
   - lib 目錄是否存在且包含必要檔案

2. 如果程式閃退，請從 cmd 執行以查看錯誤訊息

3. 如果 ChromeDriver 下載失敗，請檢查：
   - 網路連線
   - 防火牆設定
   - Chrome 瀏覽器版本


技術支援：
---------
作者：simon980224
版本：2.0.0

"""
    
    try:
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print(f"\n✓ 已建立使用說明：{readme_path}")
    except Exception as e:
        print(f"\n⚠ 建立使用說明失敗：{e}")


def cleanup_build_files():
    """清理建置暫存檔案"""
    print("\n" + "=" * 60)
    print("清理暫存檔案...")
    print("=" * 60)
    
    paths = get_project_paths()
    project_root = paths['project_root']
    
    cleanup_items = [
        project_root / "build",
        project_root / "AutoSlotGameMaster.spec"
    ]
    
    for item in cleanup_items:
        if item.exists():
            try:
                if item.is_dir():
                    shutil.rmtree(item)
                    print(f"✓ 已刪除：{item}")
                else:
                    item.unlink()
                    print(f"✓ 已刪除：{item}")
            except Exception as e:
                print(f"⚠ 無法刪除 {item}: {e}")


def main():
    """主程式"""
    print("\n")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║   AutoSlotGameMaster - Windows EXE 建置工具              ║")
    print("║   Version: 2.0.0                                          ║")
    print("║   Author: simon980224                                     ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    
    # 檢查相依套件
    if not check_dependencies():
        print("\n按 Enter 鍵退出...")
        input()
        return 1
    
    # 檢查專案結構
    if not check_project_structure():
        print("\n按 Enter 鍵退出...")
        input()
        return 1
    
    # 確認建置
    print("\n" + "=" * 60)
    print("準備開始建置")
    print("=" * 60)
    user_input = input("\n是否開始建置? (y/n): ").strip().lower()
    
    if user_input != 'y':
        print("已取消建置")
        return 0
    
    # 建置 EXE
    if not build_exe():
        print("\n按 Enter 鍵退出...")
        input()
        return 1
    
    # 建立使用說明
    create_readme()
    
    # 清理暫存檔案
    cleanup_prompt = input("\n是否清理建置暫存檔案? (y/n): ").strip().lower()
    if cleanup_prompt == 'y':
        cleanup_build_files()
    
    print("\n" + "=" * 60)
    print("所有步驟完成！")
    print("=" * 60)
    print("\n執行檔案位置：")
    paths = get_project_paths()
    print(f"  {paths['project_root'] / 'dist' / 'AutoSlotGameMaster.exe'}")
    print("\n請將整個 dist 資料夾複製到 Windows 電腦上執行")
    print("\n按 Enter 鍵退出...")
    input()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
