#!/usr/bin/env python3
"""
AutoSlotGameMaster 打包腳本
使用 PyInstaller 將 mainRefactor.py 打包成 Windows 可執行檔

執行方式：
    python build.py

需要安裝：
    pip install pyinstaller

作者: simon980224
版本: 2.0.0
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def print_step(step: int, message: str) -> None:
    """印出步驟資訊"""
    print(f"\n{'='*60}")
    print(f"步驟 {step}: {message}")
    print('='*60)


def check_pyinstaller() -> bool:
    """檢查 PyInstaller 是否已安裝"""
    try:
        import PyInstaller
        print(f"✓ PyInstaller 已安裝 (版本: {PyInstaller.__version__})")
        return True
    except ImportError:
        print("✗ PyInstaller 未安裝")
        return False


def install_pyinstaller() -> bool:
    """安裝 PyInstaller"""
    print("正在安裝 PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller 安裝成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ PyInstaller 安裝失敗: {e}")
        return False


def clean_build_files() -> None:
    """清理之前的建構檔案"""
    print("清理舊的建構檔案...")
    
    dirs_to_remove = ['build', 'dist', '__pycache__']
    files_to_remove = ['*.spec']
    
    # 移除目錄
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  - 已移除目錄: {dir_name}")
    
    # 移除 spec 檔案
    for spec_file in Path('.').glob('*.spec'):
        spec_file.unlink()
        print(f"  - 已移除檔案: {spec_file}")
    
    # 移除 src/__pycache__
    src_pycache = Path('src/__pycache__')
    if src_pycache.exists():
        shutil.rmtree(src_pycache)
        print(f"  - 已移除目錄: {src_pycache}")
    
    print("✓ 清理完成")


def build_executable() -> bool:
    """建立可執行檔"""
    print("開始打包...")
    
    # 確認檔案存在
    main_file = Path('src/mainRefactor.py')
    icon_file = Path('sett.png')
    
    if not main_file.exists():
        print(f"✗ 找不到主程式檔案: {main_file}")
        return False
    
    if not icon_file.exists():
        print(f"⚠ 找不到圖示檔案: {icon_file}，將使用預設圖示")
        icon_file = None
    
    # 建立 PyInstaller 指令
    cmd = [
        'pyinstaller',
        '--onefile',  # 打包成單一執行檔
        '--windowed',  # Windows 模式（無控制台視窗）- 如果需要看 log 可以改為 --console
        '--name=AutoSlotGameMaster',  # 執行檔名稱
        '--clean',  # 清理暫存檔
    ]
    
    # 如果有圖示檔案，加入參數
    if icon_file:
        cmd.extend(['--icon', str(icon_file)])
    
    # 加入主程式
    cmd.append(str(main_file))
    
    try:
        subprocess.check_call(cmd)
        print("✓ 打包完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 打包失敗: {e}")
        return False


def copy_resources() -> bool:
    """複製資源檔案到 dist 目錄"""
    print("複製資源檔案...")
    
    dist_dir = Path('dist')
    if not dist_dir.exists():
        print("✗ dist 目錄不存在")
        return False
    
    # 複製 img 目錄
    img_src = Path('img')
    img_dst = dist_dir / 'img'
    if img_src.exists():
        if img_dst.exists():
            shutil.rmtree(img_dst)
        shutil.copytree(img_src, img_dst)
        print(f"  ✓ 已複製 img 目錄")
    else:
        print(f"  ⚠ 找不到 img 目錄")
    
    # 複製 lib 目錄
    lib_src = Path('lib')
    lib_dst = dist_dir / 'lib'
    if lib_src.exists():
        if lib_dst.exists():
            shutil.rmtree(lib_dst)
        shutil.copytree(lib_src, lib_dst)
        print(f"  ✓ 已複製 lib 目錄")
    else:
        print(f"  ⚠ 找不到 lib 目錄")
    
    print("✓ 資源檔案複製完成")
    return True


def clean_cache_files() -> None:
    """清理所有產生的緩存檔案"""
    print("清理緩存檔案...")
    
    # 移除 build 目錄
    if os.path.exists('build'):
        shutil.rmtree('build')
        print("  - 已移除 build 目錄")
    
    # 移除 spec 檔案
    for spec_file in Path('.').glob('*.spec'):
        spec_file.unlink()
        print(f"  - 已移除 {spec_file}")
    
    # 移除 __pycache__
    for pycache in Path('.').rglob('__pycache__'):
        shutil.rmtree(pycache)
        print(f"  - 已移除 {pycache}")
    
    # 移除 .pyc 檔案
    for pyc_file in Path('.').rglob('*.pyc'):
        pyc_file.unlink()
        print(f"  - 已移除 {pyc_file}")
    
    print("✓ 緩存檔案清理完成")


def show_result() -> None:
    """顯示打包結果"""
    print("\n" + "="*60)
    print("打包完成！")
    print("="*60)
    
    dist_dir = Path('dist')
    if dist_dir.exists():
        print(f"\n輸出目錄: {dist_dir.absolute()}")
        print("\n目錄結構:")
        print("dist/")
        
        # 列出所有檔案和目錄
        for item in sorted(dist_dir.iterdir()):
            if item.is_dir():
                print(f"  ├── {item.name}/")
                # 顯示子目錄的檔案數量
                file_count = len(list(item.rglob('*')))
                print(f"  │   └── ({file_count} 個檔案)")
            else:
                size_mb = item.stat().st_size / (1024 * 1024)
                print(f"  ├── {item.name} ({size_mb:.2f} MB)")
        
        print("\n可以將 dist 目錄複製到 Windows 電腦上運行")
        print("執行檔: dist/AutoSlotGameMaster.exe")
    else:
        print("\n✗ 找不到 dist 目錄")


def main():
    """主函式"""
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "AutoSlotGameMaster 打包工具" + " "*15 + "║")
    print("╚" + "="*58 + "╝")
    
    try:
        # 步驟 1: 檢查 PyInstaller
        print_step(1, "檢查 PyInstaller")
        if not check_pyinstaller():
            if not install_pyinstaller():
                print("\n✗ 無法安裝 PyInstaller，請手動安裝: pip install pyinstaller")
                return 1
        
        # 步驟 2: 清理舊檔案
        print_step(2, "清理舊的建構檔案")
        clean_build_files()
        
        # 步驟 3: 打包執行檔
        print_step(3, "打包執行檔")
        if not build_executable():
            print("\n✗ 打包失敗")
            return 1
        
        # 步驟 4: 複製資源檔案
        print_step(4, "複製資源檔案")
        if not copy_resources():
            print("\n⚠ 資源檔案複製失敗，但執行檔已建立")
        
        # 步驟 5: 清理緩存檔案
        print_step(5, "清理緩存檔案")
        clean_cache_files()
        
        # 顯示結果
        show_result()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n✗ 使用者中斷")
        return 1
    except Exception as e:
        print(f"\n✗ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
