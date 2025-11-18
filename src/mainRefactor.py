"""
金富翁遊戲自動化系統



作者: 凡臻科技
版本: 3.0.0
Python: 3.8+
"""

import logging
import sys
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """帶顏色的日誌格式化器。
    
    使用 ANSI 顏色碼為不同等級的日誌訊息添加顏色。
    """
    
    # ANSI 顏色碼
    RESET = "\033[0m"
    INFO = "\033[32m"       # 綠色
    WARNING = "\033[33m"    # 黃色
    ERROR = "\033[31m"      # 紅色
    TIMESTAMP = "\033[90m"  # 灰色
    
    def __init__(self, fmt: Optional[str] = None, datefmt: Optional[str] = None) -> None:
        """初始化顏色格式化器。
        
        Args:
            fmt: 日誌格式字串
            datefmt: 日期格式字串
        """
        super().__init__(fmt, datefmt)
        self.formatters = {
            logging.INFO: logging.Formatter(
                f"{self.TIMESTAMP}%(asctime)s{self.RESET} - "
                f"{self.INFO}%(levelname)-8s{self.RESET} - "
                f"%(message)s"
            ),
            logging.WARNING: logging.Formatter(
                f"{self.TIMESTAMP}%(asctime)s{self.RESET} - "
                f"{self.WARNING}%(levelname)-8s{self.RESET} - "
                f"%(message)s"
            ),
            logging.ERROR: logging.Formatter(
                f"{self.TIMESTAMP}%(asctime)s{self.RESET} - "
                f"{self.ERROR}%(levelname)-8s{self.RESET} - "
                f"%(message)s"
            ),
        }
    
    def format(self, record: logging.LogRecord) -> str:
        """格式化日誌記錄。
        
        Args:
            record: 日誌記錄物件
            
        Returns:
            格式化後的日誌字串
        """
        formatter = self.formatters.get(record.levelno)
        if formatter:
            return formatter.format(record)
        return super().format(record)


def setup_logger() -> logging.Logger:
    """設定並返回配置好的 logger。
    
    建立控制台輸出的日誌系統,輸出帶顏色。
    
    Returns:
        配置完成的 Logger 物件
    """
    logger = logging.getLogger("AutoSlotGame")
    logger.setLevel(logging.INFO)
    
    # 避免重複添加 handler
    if logger.handlers:
        return logger
    
    # 控制台 handler (帶顏色)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(ColoredFormatter())
    
    logger.addHandler(console_handler)
    
    return logger


def main() -> None:
    """主程式入口。
    
    初始化系統並執行主要邏輯,包含錯誤處理和資源清理。
    """
    logger = setup_logger()
    
    logger.info("=== 金富翁遊戲自動化系統啟動 ===")
    
    try:
        # TODO: 主程式邏輯將在這裡實作
        pass
    except KeyboardInterrupt:
        logger.warning("使用者中斷程式執行")
    except Exception as e:
        logger.error(f"系統發生錯誤: {e}", exc_info=True)
        raise
    finally:
        logger.info("=== 系統結束 ===")


if __name__ == "__main__":
    main()
