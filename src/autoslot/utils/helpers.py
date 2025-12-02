"""
輔助函式模組

提供系統級的輔助函式。
"""

import sys
import platform
import subprocess
from pathlib import Path
from typing import Union, Optional

import cv2
import numpy as np
from PIL import Image

from ..utils.logger import LoggerFactory


def cleanup_chromedriver_processes() -> None:
    """清除所有緩存的 chromedriver 程序。
    
    在程式啟動前執行，確保沒有殘留的 chromedriver 程序佔用資源。
    支援 Windows、macOS 和 Linux 作業系統。
    """
    logger = LoggerFactory.get_logger()
    system = platform.system().lower()
    
    try:
        if system == "windows":
            # Windows: 使用 taskkill 命令
            result = subprocess.run(
                ["taskkill", "/F", "/IM", "chromedriver.exe"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # 檢查結果
            if result.returncode == 0:
                logger.info("✓ 已清除 Windows 上的 chromedriver 程序")
            elif "找不到" in result.stdout or "not found" in result.stdout.lower():
                logger.debug("沒有執行中的 chromedriver 程序")
            else:
                logger.debug(f"taskkill 執行結果: {result.stdout.strip()}")
                
        elif system in ["darwin", "linux"]:
            # macOS/Linux: 使用 killall 命令
            result = subprocess.run(
                ["killall", "-9", "chromedriver"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # killall 在沒有找到程序時會返回非 0，這是正常的
            if result.returncode == 0:
                logger.info(f"✓ 已清除 {system.upper()} 上的 chromedriver 程序")
            else:
                logger.debug("沒有執行中的 chromedriver 程序")
        else:
            logger.warning(f"不支援的作業系統: {system}，跳過清除 chromedriver")
            
    except subprocess.TimeoutExpired:
        logger.warning("清除 chromedriver 程序逾時")
    except FileNotFoundError:
        logger.debug(f"系統找不到清除命令（{system}），可能沒有執行中的 chromedriver")
    except Exception as e:
        logger.warning(f"清除 chromedriver 程序時發生錯誤: {e}")


def get_resource_path(relative_path: str = "") -> Path:
    """取得資源檔案的絕對路徑。
    
    在開發環境中，返回專案根目錄的路徑。
    在打包後的環境中，返回 exe 所在目錄的路徑（而非臨時目錄）。
    
    Args:
        relative_path: 相對於根目錄的路徑
        
    Returns:
        資源檔案的絕對路徑
    """
    if getattr(sys, 'frozen', False):
        # 打包後：使用 exe 所在目錄（不是 _MEIPASS 臨時目錄）
        # 因為 lib 和 img 應該放在 exe 旁邊，方便使用者編輯
        base_path = Path(sys.executable).resolve().parent
    else:
        # 開發環境：使用 main.py 的父目錄的父目錄
        base_path = Path(__file__).resolve().parent.parent.parent
    
    if relative_path:
        return base_path / relative_path
    return base_path


def cv2_imread_unicode(file_path: Union[str, Path], flags: int = cv2.IMREAD_COLOR) -> Optional[np.ndarray]:
    """安全讀取圖片（支援 Unicode 路徑）。
    
    OpenCV 的 cv2.imread() 無法處理包含中文或其他非 ASCII 字元的路徑。
    此函式使用 numpy 和 PIL 作為替代方案。
    
    Args:
        file_path: 圖片檔案路徑（支援中文路徑）
        flags: OpenCV 讀取標誌（cv2.IMREAD_COLOR, cv2.IMREAD_GRAYSCALE 等）
        
    Returns:
        圖片的 numpy 陣列，失敗返回 None
    """
    try:
        # 轉換為 Path 物件
        path = Path(file_path)
        
        # 使用 PIL 讀取圖片（PIL 支援 Unicode 路徑）
        pil_image = Image.open(path)
        
        # 轉換為 numpy 陣列
        img_array = np.array(pil_image)
        
        # 根據讀取標誌處理圖片
        if flags == cv2.IMREAD_GRAYSCALE:
            # 轉換為灰階
            if len(img_array.shape) == 3:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        elif flags == cv2.IMREAD_COLOR:
            # 確保是彩色圖片
            if len(img_array.shape) == 2:
                # 灰階轉彩色
                img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2RGB)
            elif img_array.shape[2] == 4:
                # RGBA 轉 RGB
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
            # PIL 使用 RGB，OpenCV 使用 BGR，需要轉換
            if len(img_array.shape) == 3 and img_array.shape[2] == 3:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        return img_array
        
    except Exception as e:
        # 返回 None 保持與 cv2.imread() 相同的行為
        return None
