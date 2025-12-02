#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
管理器模組

提供瀏覽器、Proxy 等資源管理功能。
"""

from .browser_helper import BrowserHelper
from .browser_manager import BrowserManager
from .proxy_manager import (
    LocalProxyServerManager,
    ProxyConnectionHandler,
    SimpleProxyServer,
)

__all__ = [
    # 瀏覽器管理
    'BrowserHelper',
    'BrowserManager',
    
    # Proxy 管理
    'LocalProxyServerManager',
    'ProxyConnectionHandler',
    'SimpleProxyServer',
]
