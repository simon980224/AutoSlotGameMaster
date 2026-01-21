"""
配置讀取器

讀取並解析系統所需的各種配置檔案。
"""

import logging
from pathlib import Path
from typing import Optional, List, Protocol

from ..core.constants import Constants
from ..core.models import UserCredential, BetRule
from ..core.exceptions import ConfigurationError
from ..utils.logger import LoggerFactory
from ..utils.helpers import get_resource_path


class ConfigReaderProtocol(Protocol):
    """配置讀取器協議"""
    
    def read_user_credentials(self, filename: str) -> List[UserCredential]:
        """讀取使用者憑證"""
        ...
    
    def read_bet_rules(self, filename: str) -> List[BetRule]:
        """讀取下注規則"""
        ...


class ConfigReader:
    """配置檔案讀取器"""
    
    def __init__(
        self, 
        lib_path: Optional[Path] = None,
        logger: Optional[logging.Logger] = None
    ) -> None:
        """初始化配置讀取器"""
        if lib_path is None:
            lib_path = get_resource_path(Constants.DEFAULT_LIB_PATH)
        
        self.lib_path = Path(lib_path)
        self.logger = logger or LoggerFactory.get_logger()
        
        if not self.lib_path.exists():
            raise ConfigurationError(f"配置目錄不存在: {self.lib_path}")
    
    def _read_file_lines(self, filename: str, skip_header: bool = True) -> List[str]:
        """讀取檔案並返回有效行列表"""
        file_path = self.lib_path / filename
        
        if not file_path.exists():
            raise ConfigurationError(f"找不到配置檔案: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8', buffering=8192) as f:
                lines = f.readlines()
            
            start_index = 1 if skip_header and lines else 0
            
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
        """讀取使用者憑證檔案
        
        檔案格式: 帳號,密碼,出口IP (首行為標題)
        """
        credentials = []
        lines = self._read_file_lines(filename, skip_header=True)
        
        for line_number, line in enumerate(lines, start=2):
            try:
                parts = [p.strip() for p in line.split(',')]
                
                if len(parts) < 2:
                    self.logger.warning(f"第 {line_number} 行格式不完整 已跳過 {line}")
                    continue
                
                username = parts[0]
                password = parts[1]
                
                proxy = None
                if len(parts) >= 3 and parts[2].strip():
                    exit_ip = parts[2].strip()
                    proxy = (
                        f"{Constants.PROXY_HOST}:{Constants.PROXY_PORT}:"
                        f"{Constants.PROXY_USERNAME_BASE}-ip-{exit_ip}:"
                        f"{Constants.PROXY_PASSWORD}"
                    )
                
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
        """讀取下注規則檔案
        
        支援三種格式:
        - a:金額:次數 (自動旋轉規則)
        - s:金額:時間(分鐘):最小(秒數):最大(秒數) (標準規則)
        - f:金額 (購買免費遊戲)
        """
        rules = []
        lines = self._read_file_lines(filename, skip_header=True)
        
        for line_number, line in enumerate(lines, start=2):
            try:
                parts = line.split(':')
                
                if len(parts) < 2:
                    self.logger.warning(f"第 {line_number} 行格式不完整 已跳過 {line}")
                    continue
                
                rule_type = parts[0].strip().lower()
                
                if rule_type == 'a':
                    if len(parts) < 3:
                        self.logger.warning(f"第 {line_number} 行格式不完整 已跳過 {line}")
                        continue
                    
                    amount = float(parts[1].strip())
                    spin_count = int(parts[2].strip())
                    
                    rules.append(BetRule(
                        rule_type='a',
                        amount=amount,
                        spin_count=spin_count
                    ))
                    
                elif rule_type == 's':
                    if len(parts) < 5:
                        self.logger.warning(f"第 {line_number} 行格式不完整 已跳過 {line}")
                        continue
                    
                    amount = float(parts[1].strip())
                    duration = int(parts[2].strip())
                    min_seconds = float(parts[3].strip())
                    max_seconds = float(parts[4].strip())
                    
                    rules.append(BetRule(
                        rule_type='s',
                        amount=amount,
                        duration=duration,
                        min_seconds=min_seconds,
                        max_seconds=max_seconds
                    ))
                    
                elif rule_type == 'f':
                    amount = float(parts[1].strip())
                    
                    rules.append(BetRule(
                        rule_type='f',
                        amount=amount
                    ))
                    
                else:
                    self.logger.warning(f"第 {line_number} 行無效的規則類型 '{rule_type}' 已跳過")
                    continue
                
            except (ValueError, IndexError) as e:
                self.logger.warning(f"第 {line_number} 行無法解析 {e}")
                continue
        
        return rules
