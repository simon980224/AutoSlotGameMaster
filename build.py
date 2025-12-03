#!/usr/bin/env python3
"""
AutoSlotGameMaster 打包腳本
使用 PyInstaller 將 main.py 打包成 Windows 可執行檔

執行方式：
    python build.py

需要安裝：
    pip install pyinstaller

作者: simon980224
版本: 1.6.0
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def print_step(step: str, description: str) -> None:
    """列印步驟資訊"""
    print(f"\n{'='*70}")
    print(f"[{step}] {description}")
    print(f"{'='*70}\n")


def clean_build_artifacts() -> None:
    """清理構建產生的緩存檔案"""
    print_step("清理", "移除舊的構建檔案...")
    
    # 需要清理的目錄和檔案
    artifacts = [
        'build',
        'dist', 
        '__pycache__',
        'src/__pycache__',
        '*.spec',
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '.pytest_cache',
        '.coverage'
    ]
    
    for artifact in artifacts:
        # 處理萬用字元
        if '*' in artifact:
            import glob
            for item in glob.glob(artifact):
                try:
                    if os.path.isfile(item):
                        os.remove(item)
                        print(f"  ✓ 已刪除檔案: {item}")
                    elif os.path.isdir(item):
                        shutil.rmtree(item)
                        print(f"  ✓ 已刪除目錄: {item}")
                except Exception as e:
                    print(f"  ✗ 無法刪除 {item}: {e}")
        else:
            # 處理普通路徑
            if os.path.exists(artifact):
                try:
                    if os.path.isdir(artifact):
                        shutil.rmtree(artifact)
                        print(f"  ✓ 已刪除目錄: {artifact}")
                    else:
                        os.remove(artifact)
                        print(f"  ✓ 已刪除檔案: {artifact}")
                except Exception as e:
                    print(f"  ✗ 無法刪除 {artifact}: {e}")


def check_requirements() -> bool:
    """檢查必要的檔案是否存在"""
    print_step("檢查", "驗證必要檔案...")
    
    required_files = [
        'src/main.py',
        'sett.ico',  # 使用 .ico 格式圖示
        'requirements.txt'
    ]
    
    required_dirs = [
        'img',
        'lib'
    ]
    
    all_exists = True
    
    # 檢查檔案
    for file in required_files:
        if os.path.isfile(file):
            print(f"  ✓ 找到檔案: {file}")
        else:
            print(f"  ✗ 缺少檔案: {file}")
            all_exists = False
    
    # 檢查目錄
    for directory in required_dirs:
        if os.path.isdir(directory):
            print(f"  ✓ 找到目錄: {directory}")
        else:
            print(f"  ✗ 缺少目錄: {directory}")
            all_exists = False
    
    return all_exists


def check_pyinstaller() -> bool:
    """檢查 PyInstaller 是否已安裝"""
    print_step("依賴", "檢查 PyInstaller...")
    
    try:
        result = subprocess.run(
            ['pyinstaller', '--version'],
            capture_output=True,
            text=True,
            check=True
        )
        version = result.stdout.strip()
        print(f"  ✓ PyInstaller 已安裝 (版本: {version})")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("  ✗ PyInstaller 未安裝")
        print("\n請執行以下命令安裝 PyInstaller:")
        print("    pip install pyinstaller")
        return False


def build_executable() -> bool:
    """使用 PyInstaller 構建可執行檔"""
    print_step("構建", "開始打包可執行檔...")
    
    # PyInstaller 命令參數
    cmd = [
        'pyinstaller',
        '--name=AutoSlotGameMaster',          # 可執行檔名稱
        '--onefile',                          # 打包成單一檔案
        '--console',                          # 保留控制台視窗
        '--icon=sett.ico',                    # 設定圖示（.ico 格式，包含多種尺寸）
        '--clean',                            # 清理臨時檔案
        '--noconfirm',                        # 覆蓋輸出目錄不提示
        # 注意：移除 --add-data 選項，讓 img 和 lib 目錄放在 exe 旁邊
        # 這樣使用者可以方便地編輯配置檔案和圖片模板
        'src/main.py'                         # 主程式入口
    ]
    
    try:
        print(f"執行命令: {' '.join(cmd)}\n")
        result = subprocess.run(cmd, check=True)
        
        if result.returncode == 0:
            print("\n  ✓ 構建成功!")
            return True
        else:
            print("\n  ✗ 構建失敗!")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"\n  ✗ 構建過程中發生錯誤: {e}")
        return False


def copy_resources() -> None:
    """複製 img 和 lib 目錄到 dist"""
    print_step("複製", "將資源檔案複製到輸出目錄...")
    
    dist_path = Path('dist')
    
    if not dist_path.exists():
        print("  ✗ dist 目錄不存在，構建可能失敗")
        return
    
    # 複製 img 目錄
    img_src = Path('img')
    img_dst = dist_path / 'img'
    if img_src.exists():
        if img_dst.exists():
            shutil.rmtree(img_dst)
        shutil.copytree(img_src, img_dst)
        print(f"  ✓ 已複製: img/ -> dist/img/")
    else:
        print(f"  ✗ 找不到 img 目錄")
    
    # 複製 lib 目錄
    lib_src = Path('lib')
    lib_dst = dist_path / 'lib'
    if lib_src.exists():
        if lib_dst.exists():
            shutil.rmtree(lib_dst)
        shutil.copytree(lib_src, lib_dst)
        print(f"  ✓ 已複製: lib/ -> dist/lib/")
    else:
        print(f"  ✗ 找不到 lib 目錄")


def clean_post_build() -> None:
    """清理構建後的臨時檔案"""
    print_step("清理", "移除構建產生的臨時檔案...")
    
    # 構建後要清理的項目
    artifacts = [
        'build',
        '*.spec',
        '__pycache__',
        'src/__pycache__'
    ]
    
    for artifact in artifacts:
        # 處理萬用字元
        if '*' in artifact:
            import glob
            for item in glob.glob(artifact):
                try:
                    if os.path.isfile(item):
                        os.remove(item)
                        print(f"  ✓ 已刪除檔案: {item}")
                    elif os.path.isdir(item):
                        shutil.rmtree(item)
                        print(f"  ✓ 已刪除目錄: {item}")
                except Exception as e:
                    print(f"  ✗ 無法刪除 {item}: {e}")
        else:
            # 處理普通路徑
            if os.path.exists(artifact):
                try:
                    if os.path.isdir(artifact):
                        shutil.rmtree(artifact)
                        print(f"  ✓ 已刪除目錄: {artifact}")
                    else:
                        os.remove(artifact)
                        print(f"  ✓ 已刪除檔案: {artifact}")
                except Exception as e:
                    print(f"  ✗ 無法刪除 {artifact}: {e}")


def show_result() -> None:
    """顯示構建結果"""
    print_step("完成", "構建結果")
    
    dist_path = Path('dist')
    exe_file = dist_path / 'AutoSlotGameMaster.exe'
    
    if exe_file.exists():
        file_size = exe_file.stat().st_size / (1024 * 1024)  # 轉換為 MB
        
        print(f"  ✓ 可執行檔: dist/AutoSlotGameMaster.exe")
        print(f"  ✓ 檔案大小: {file_size:.2f} MB")
        
        # 檢查目錄結構
        img_dir = dist_path / 'img'
        lib_dir = dist_path / 'lib'
        
        if img_dir.exists():
            print(f"  ✓ 資源目錄: dist/img/")
        if lib_dir.exists():
            print(f"  ✓ 資源目錄: dist/lib/")
        
        print("\n目錄結構:")
        print("  dist/")
        print("  ├── AutoSlotGameMaster.exe")
        print("  ├── img/")
        print("  └── lib/")
        
        print("\n您可以將 dist 目錄中的所有內容複製到 Windows 電腦執行。")
    else:
        print("  ✗ 找不到可執行檔，構建可能失敗")


def main():
    """主函式"""
    print("\n" + "="*70)
    print(" AutoSlotGameMaster v1.1.0 打包工具")
    print("="*70)
    
    # 1. 清理舊的構建檔案
    clean_build_artifacts()
    
    # 2. 檢查必要檔案
    if not check_requirements():
        print("\n❌ 缺少必要的檔案，無法繼續構建")
        sys.exit(1)
    
    # 3. 檢查 PyInstaller
    if not check_pyinstaller():
        print("\n❌ PyInstaller 未安裝，無法繼續構建")
        sys.exit(1)
    
    # 4. 構建可執行檔
    if not build_executable():
        print("\n❌ 構建失敗")
        sys.exit(1)
    
    # 5. 複製資源檔案
    copy_resources()
    
    # 6. 清理臨時檔案
    clean_post_build()
    
    # 7. 顯示結果
    show_result()
    
    print("\n✅ 打包完成!\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  使用者中斷操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 發生未預期的錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
