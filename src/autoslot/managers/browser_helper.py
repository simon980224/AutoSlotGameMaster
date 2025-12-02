"""
瀏覽器輔助工具

提供瀏覽器操作的輔助方法。
"""

from typing import Dict, Tuple

from selenium.webdriver.chrome.webdriver import WebDriver

from ..core import Constants


class BrowserHelper:
    """瀏覽器操作輔助類別。
    
    提供常用的瀏覽器操作方法，避免程式碼重複。
    包括 CDP 點擊、座標計算、按鍵模擬等。
    """
    
    @staticmethod
    def execute_cdp_click(driver: WebDriver, x: float, y: float) -> None:
        """使用 Chrome DevTools Protocol 執行點擊操作。
        
        Args:
            driver: WebDriver 實例
            x: X 座標
            y: Y 座標
        """
        for event_type in ["mousePressed", "mouseReleased"]:
            driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
                "type": event_type,
                "x": x,
                "y": y,
                "button": "left",
                "clickCount": 1
            })
    
    @staticmethod
    def execute_cdp_space_key(driver: WebDriver) -> None:
        """使用 Chrome DevTools Protocol 按下空白鍵。
        
        Args:
            driver: WebDriver 實例
        """
        # 按下空白鍵
        driver.execute_cdp_cmd("Input.dispatchKeyEvent", {
            "type": "keyDown",
            "key": " ",
            "code": "Space",
            "windowsVirtualKeyCode": 32,
            "nativeVirtualKeyCode": 32
        })
        # 釋放空白鍵
        driver.execute_cdp_cmd("Input.dispatchKeyEvent", {
            "type": "keyUp",
            "key": " ",
            "code": "Space",
            "windowsVirtualKeyCode": 32,
            "nativeVirtualKeyCode": 32
        })
    
    @staticmethod
    def calculate_click_position(
        canvas_rect: Dict[str, float],
        x_ratio: float,
        y_ratio: float
    ) -> Tuple[float, float]:
        """根據 Canvas 區域和比例計算點擊座標。
        
        Args:
            canvas_rect: Canvas 區域資訊 {"x", "y", "w", "h"}
            x_ratio: X 座標比例
            y_ratio: Y 座標比例
            
        Returns:
            (x, y) 實際座標
        """
        x = canvas_rect["x"] + canvas_rect["w"] * x_ratio
        y = canvas_rect["y"] + canvas_rect["h"] * y_ratio
        return x, y
    
    @staticmethod
    def calculate_scaled_position(
        base_x: float,
        base_y: float,
        screenshot_width: int,
        screenshot_height: int,
        base_width: int = Constants.DEFAULT_WINDOW_WIDTH,
        base_height: int = Constants.DEFAULT_WINDOW_HEIGHT
    ) -> Tuple[int, int]:
        """根據視窗大小計算縮放後的座標。
        
        Args:
            base_x: 基準 X 座標（基於預設視窗大小）
            base_y: 基準 Y 座標（基於預設視窗大小）
            screenshot_width: 實際截圖寬度
            screenshot_height: 實際截圖高度
            base_width: 基準視窗寬度
            base_height: 基準視窗高度
            
        Returns:
            (actual_x, actual_y) 實際座標
        """
        x_ratio = base_x / base_width
        y_ratio = base_y / base_height
        actual_x = int(screenshot_width * x_ratio)
        actual_y = int(screenshot_height * y_ratio)
        return actual_x, actual_y
