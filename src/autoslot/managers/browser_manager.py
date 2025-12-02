#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
瀏覽器管理器模組

提供 WebDriver 建立和配置功能，支援自動和手動驅動程式管理。
採用優先級降級策略：優先使用專案內驅動程式，失敗時自動降級到 WebDriver Manager。
"""

import logging
import platform
from contextlib import contextmanager, suppress
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager

from ..core.constants import Constants
from ..core.exceptions import BrowserCreationError
from ..core.models import BrowserContext, UserCredential
from ..utils.helpers import get_resource_path
from ..utils.logger import LoggerFactory


class BrowserManager:
    """
    瀏覽器管理器
    
    提供 WebDriver 建立和配置功能。
    支援本機 Proxy 中繼、自動化檢測繞過、網路優化等功能。
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化瀏覽器管理器
        
        Args:
            logger: 日誌記錄器
        """
        self.logger = logger or LoggerFactory.get_logger()
    
    @staticmethod
    def create_chrome_options(local_proxy_port: Optional[int] = None) -> Options:
        """
        建立 Chrome 瀏覽器選項
        
        配置瀏覽器啟動參數，包括：
        - Proxy 設定
        - 自動化檢測繞過
        - 網路加速優化
        - 靜音設定
        
        Args:
            local_proxy_port: 本機 proxy 中繼埠號（可選）
            
        Returns:
            Options: 配置好的 Chrome 選項
        """
        logger = LoggerFactory.get_logger()
        chrome_options = Options()
        
        # 本機 Proxy 設定
        if local_proxy_port:
            proxy_address = f"http://{Constants.PROXY_SERVER_BIND_HOST}:{local_proxy_port}"
            chrome_options.add_argument(f"--proxy-server={proxy_address}")
        
        # 基本設定
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        
        # 背景執行優化設定
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_argument("--disable-background-timer-throttling")
        
        # 啟用網路加速功能
        chrome_options.add_argument("--enable-features=NetworkService,NetworkServiceInProcess")
        chrome_options.add_argument("--enable-quic")  # 啟用 QUIC 協定加速
        chrome_options.add_argument("--enable-tcp-fast-open")  # TCP 快速開啟
        
        # 其他優化設定
        chrome_options.add_argument("--disable-sync")
        chrome_options.add_argument("--metrics-recording-only")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--disable-extensions")
        
        # 記憶體與渲染優化
        chrome_options.add_argument("--disk-cache-size=209715200")  # 200MB 磁碟快取
        chrome_options.add_argument("--media-cache-size=209715200")  # 200MB 媒體快取
        
        # 移除自動化痕跡
        chrome_options.add_experimental_option(
            "excludeSwitches", 
            ["enable-automation", "enable-logging"]
        )
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 偏好設定
        chrome_options.add_experimental_option("prefs", {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_settings.popups": 0,
            # 靜音設定（2 = 靜音，1 = 允許聲音）
            "profile.content_settings.exceptions.sound": {
                "*": {
                    "setting": 2
                }
            }
        })
        
        return chrome_options
    
    def create_webdriver(
        self, 
        local_proxy_port: Optional[int] = None
    ) -> WebDriver:
        """
        建立 WebDriver 實例（優化版）
        
        優先使用專案內的驅動程式檔案，
        若失敗則嘗試使用 WebDriver Manager 自動管理作為備援。
        
        Args:
            local_proxy_port: 本機 proxy 中繼埠號（可選）
            
        Returns:
            WebDriver: WebDriver 實例
            
        Raises:
            BrowserCreationError: 當所有方法都失敗時
        """
        chrome_options = self.create_chrome_options(local_proxy_port)
        driver = None
        errors = []
        
        # 方法 1: 優先使用專案內的驅動程式檔案
        try:
            driver = self._create_webdriver_with_local_driver(chrome_options)
            
        except FileNotFoundError as e:
            errors.append(f"本機驅動程式: {e}")
            self.logger.warning(f"本機驅動程式不存在，嘗試使用 WebDriver Manager")
            
            # 方法 2: 使用 WebDriver Manager 自動管理
            try:
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
                
            except Exception as e2:
                errors.append(f"WebDriver Manager: {e2}")
                self.logger.error(f"WebDriver Manager 也失敗: {e2}")
        
        except Exception as e:
            errors.append(f"本機驅動程式: {e}")
            self.logger.warning(f"本機驅動程式失敗，嘗試備援方案: {e}")
        
        if driver is None:
            error_message = "無法建立瀏覽器實例。\n" + "\n".join(f"- {error}" for error in errors)
            raise BrowserCreationError(error_message)
        
        # 配置超時和優化
        self._configure_webdriver(driver)
        return driver
    
    def _configure_webdriver(self, driver: WebDriver) -> None:
        """
        配置 WebDriver 超時和優化設定
        
        Args:
            driver: WebDriver 實例
        """
        # 設定超時
        with suppress(Exception):
            driver.set_page_load_timeout(Constants.DEFAULT_PAGE_LOAD_TIMEOUT)
            driver.set_script_timeout(Constants.DEFAULT_SCRIPT_TIMEOUT)
            driver.implicitly_wait(Constants.DEFAULT_IMPLICIT_WAIT)
        
        # 網路優化
        with suppress(Exception):
            driver.execute_cdp_cmd("Network.enable", {})
            driver.execute_cdp_cmd("Network.emulateNetworkConditions", {
                "offline": False,
                "downloadThroughput": -1,
                "uploadThroughput": -1,
                "latency": 0
            })
    
    def _create_webdriver_with_local_driver(self, chrome_options: Options) -> WebDriver:
        """
        使用專案內的驅動程式檔案建立 WebDriver
        
        根據作業系統自動選擇正確的驅動程式檔案。
        
        Args:
            chrome_options: Chrome 選項
            
        Returns:
            WebDriver: WebDriver 實例
            
        Raises:
            FileNotFoundError: 驅動程式不存在
            BrowserCreationError: 無法啟動驅動程式
        """
        # 使用輔助函式取得專案根目錄
        project_root = get_resource_path()
        
        # 根據作業系統選擇驅動程式
        system = platform.system().lower()
        driver_filename = "chromedriver.exe" if system == "windows" else "chromedriver"
        
        driver_path = project_root / driver_filename
        
        if not driver_path.exists():
            raise FileNotFoundError(
                f"找不到驅動程式檔案\n"
                f"請確保 {driver_filename} 存在於專案根目錄"
            )
        
        # 確保驅動程式有執行權限 (Unix-like 系統)
        if system in ["darwin", "linux"]:
            import os
            with suppress(Exception):
                os.chmod(driver_path, 0o755)
        
        try:
            service = Service(str(driver_path))
            driver = webdriver.Chrome(service=service, options=chrome_options)
            return driver
        except Exception as e:
            raise BrowserCreationError(f"啟動本機驅動程式失敗: {e}") from e
    
    @contextmanager
    def create_browser_context(
        self,
        credential: UserCredential,
        index: int,
        proxy_port: Optional[int] = None
    ):
        """
        建立瀏覽器上下文管理器
        
        使用 with 語句自動管理瀏覽器生命週期：
        ```python
        with browser_manager.create_browser_context(credential, 0) as context:
            # 使用 context.driver 進行操作
            pass
        # 離開 with 區塊後自動關閉瀏覽器
        ```
        
        Args:
            credential: 使用者憑證
            index: 瀏覽器索引
            proxy_port: Proxy 埠號
            
        Yields:
            BrowserContext: 瀏覽器上下文
            
        Raises:
            BrowserCreationError: 建立失敗
        """
        driver = None
        try:
            driver = self.create_webdriver(local_proxy_port=proxy_port)
            context = BrowserContext(
                driver=driver,
                credential=credential,
                index=index,
                proxy_port=proxy_port
            )
            yield context
        finally:
            if driver:
                with suppress(Exception):
                    driver.quit()
                self.logger.debug(f"瀏覽器 #{index} 已關閉")
