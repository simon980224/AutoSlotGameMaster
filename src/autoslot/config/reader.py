"""
配置讀取器模組

負責讀取和解析系統配置檔案。
"""

import logging
from pathlib import Path
from typing import List, Optional

from ..core import Constants, UserCredential, BetRule, ConfigurationError
from ..utils import LoggerFactory, get_resource_path


class ConfigReader:
    """配置檔案讀取器。
    
    讀取並解析系統所需的各種配置檔案。
    採用上下文管理器和更好的錯誤處理。
    
    Attributes:
        lib_path: 配置檔案所在目錄路徑
        logger: 日誌記錄器
    """
    
    def __init__(
        self, 
        lib_path: Optional[Path] = None,
        logger: Optional[logging.Logger] = None
    ) -> None:
        """初始化配置讀取器。
        
        Args:
            lib_path: 配置檔案目錄路徑,預設為專案的 lib 目錄
            logger: 日誌記錄器
        """
        if lib_path is None:
            lib_path = get_resource_path(Constants.DEFAULT_LIB_PATH)
        
        self.lib_path = Path(lib_path)
        self.logger = logger or LoggerFactory.get_logger()
        
        # 驗證目錄存在
        if not self.lib_path.exists():
            raise ConfigurationError(f"配置目錄不存在: {self.lib_path}")
    
    def _read_file_lines(self, filename: str, skip_header: bool = True) -> List[str]:
        """讀取檔案並返回有效行列表（優化版）。
        
        Args:
            filename: 檔案名稱
            skip_header: 是否跳過首行標題
            
        Returns:
            有效行列表（去除空行和註釋）
            
        Raises:
            ConfigurationError: 檔案讀取失敗
        """
        file_path = self.lib_path / filename
        
        if not file_path.exists():
            raise ConfigurationError(f"找不到配置檔案: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8', buffering=8192) as f:
                lines = f.readlines()
            
            # 跳過標題行
            start_index = 1 if skip_header and lines else 0
            
            # 使用列表推導式（更高效）
            valid_lines = [
                line.strip() 
                for line in lines[start_index:] 
                if (stripped := line.strip()) and not stripped.startswith('#')
            ]
            
            return valid_lines
            
        except (IOError, OSError) as e:
            raise ConfigurationError(f"讀取檔案失敗 {filename}: {e}") from e
        except Exception as e:
            raise ConfigurationError(f"解析檔案失敗 {filename}: {e}") from e
    
    def read_user_credentials(
        self, 
        filename: str = Constants.DEFAULT_CREDENTIALS_FILE
    ) -> List[UserCredential]:
        """讀取使用者憑證檔案。
        
        檔案格式: 帳號,密碼,IP:port:user:password (首行為標題)
        第三欄為 proxy 資訊，格式為 host:port:username:password
        
        Args:
            filename: 檔案名稱
            
        Returns:
            使用者憑證列表
            
        Raises:
            ConfigurationError: 讀取或解析失敗
        """
        credentials = []
        lines = self._read_file_lines(filename, skip_header=True)
        
        for line_number, line in enumerate(lines, start=2):  # +2 因為跳過標題
            try:
                parts = [p.strip() for p in line.split(',')]
                
                if len(parts) < 2:
                    self.logger.warning(f"第 {line_number} 行格式不完整 已跳過 {line}")
                    continue
                
                username = parts[0]
                password = parts[1]
                # 第三欄是 proxy 資訊，格式為 host:port:username:password
                # 如果第三欄不存在或為空字串，則 proxy 為 None（不使用 proxy）
                proxy = parts[2] if len(parts) >= 3 and parts[2].strip() else None
                
                credentials.append(UserCredential(
                    username=username,
                    password=password,
                    proxy=proxy
                ))  
                
            except ValueError as e:
                self.logger.warning(f"第 {line_number} 行資料無效 {e}")
                continue
        
        return credentials
    
    def read_bet_rules(
        self, 
        filename: str = Constants.DEFAULT_RULES_FILE
    ) -> List[BetRule]:
        """讀取下注規則檔案。
        
        檔案格式: 金額:時間(分鐘) (首行為標題)
        
        Args:
            filename: 檔案名稱
            
        Returns:
            下注規則列表
            
        Raises:
            ConfigurationError: 讀取或解析失敗
        """
        rules = []
        lines = self._read_file_lines(filename, skip_header=True)
        
        for line_number, line in enumerate(lines, start=2):
            try:
                parts = line.split(':')
                
                if len(parts) < 2:
                    self.logger.warning(f"第 {line_number} 行格式不完整 已跳過 {line}")
                    continue
                
                amount = float(parts[0].strip())
                duration = int(parts[1].strip())
                
                rules.append(BetRule(amount=amount, duration=duration))
                
            except (ValueError, IndexError) as e:
                self.logger.warning(f"第 {line_number} 行無法解析 {e}")
                continue
        
        return rules
