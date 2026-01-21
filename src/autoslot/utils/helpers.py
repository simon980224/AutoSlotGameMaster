"""
輔助函式

提供系統範圍內的通用輔助函式。
"""

import sys
import platform
import subprocess
from pathlib import Path
from typing import Optional, Union

import cv2
import numpy as np
from PIL import Image

from ..core.constants import Constants
from .logger import LoggerFactory


def cleanup_chromedriver_processes() -> None:
    """清除所有緩存的 chromedriver 程序
    
    在程式啟動前執行，確保沒有殘留的 chromedriver 程序佔用資源。
    支援 Windows、macOS 和 Linux 作業系統。
    """
    logger = LoggerFactory.get_logger()
    system = platform.system().lower()
    
    logger.info("=" * 60)
    logger.info("【系統初始化】清理殘留程序")
    logger.info("=" * 60)
    
    try:
        if system == "windows":
            result = subprocess.run(
                ["taskkill", "/F", "/IM", "chromedriver.exe"],
                capture_output=True,
                text=True,
                timeout=Constants.CLEANUP_PROCESS_TIMEOUT
            )
            
            if result.returncode == 0:
                logger.info("[成功] 已清除 Windows 上的 chromedriver 程序")
            elif "找不到" in result.stdout or "not found" in result.stdout.lower():
                logger.info("[成功] 沒有殘留的 chromedriver 程序")
            else:
                logger.debug(f"taskkill 執行結果: {result.stdout.strip()}")
                
        elif system in ["darwin", "linux"]:
            result = subprocess.run(
                ["killall", "-9", "chromedriver"],
                capture_output=True,
                text=True,
                timeout=Constants.CLEANUP_PROCESS_TIMEOUT
            )
            
            if result.returncode == 0:
                logger.info(f"[成功] 已清除 {system.upper()} 上的 chromedriver 程序")
            else:
                logger.info("[成功] 沒有殘留的 chromedriver 程序")
        else:
            logger.warning(f"[警告] 不支援的作業系統: {system}，跳過清除 chromedriver")
            
    except subprocess.TimeoutExpired:
        logger.warning("[警告] 清除 chromedriver 程序逾時")
    except FileNotFoundError:
        logger.info("[成功] 沒有殘留的 chromedriver 程序")
    except Exception as e:
        logger.warning(f"[警告] 清除程序時發生錯誤: {e}")
    
    logger.info("")


def get_resource_path(relative_path: str = "") -> Path:
    """取得資源檔案的絕對路徑
    
    在開發環境中，返回專案根目錄的路徑。
    在打包後的環境中，返回 exe 所在目錄的路徑。
    
    Args:
        relative_path: 相對於根目錄的路徑
        
    Returns:
        資源檔案的絕對路徑
    """
    if getattr(sys, 'frozen', False):
        # 打包後：使用 exe 所在目錄
        base_path = Path(sys.executable).resolve().parent
    else:
        # 開發環境：使用專案根目錄
        base_path = Path(__file__).resolve().parent.parent.parent.parent
    
    if relative_path:
        return base_path / relative_path
    return base_path


def cv2_imread_unicode(file_path: Union[str, Path], flags: int = cv2.IMREAD_COLOR) -> Optional[np.ndarray]:
    """安全讀取圖片（支援 Unicode 路徑）
    
    OpenCV 的 cv2.imread() 無法處理包含中文或其他非 ASCII 字元的路徑。
    此函式使用 numpy 和 PIL 作為替代方案。
    
    Args:
        file_path: 圖片檔案路徑（支援中文路徑）
        flags: OpenCV 讀取標誌
        
    Returns:
        圖片的 numpy 陣列，失敗返回 None
    """
    try:
        path = Path(file_path)
        pil_image = Image.open(path)
        img_array = np.array(pil_image)
        
        if flags == cv2.IMREAD_GRAYSCALE:
            if len(img_array.shape) == 3:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        elif flags == cv2.IMREAD_COLOR:
            if len(img_array.shape) == 2:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2RGB)
            elif img_array.shape[2] == 4:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
            if len(img_array.shape) == 3 and img_array.shape[2] == 3:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        return img_array
        
    except Exception:
        return None
