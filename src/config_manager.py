#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
支持用户自定义配置持久化
"""

import json
import os
from typing import Dict, Any, Optional
from datetime import datetime


class ConfigManager:
    """配置管理器"""
    
    DEFAULT_CONFIG = {
        # 代理测试设置
        'timeout': 10,
        'max_workers': 50,
        'test_urls': [
            'http://httpbin.org/ip',
            'http://www.baidu.com',
            'http://www.qq.com',
            'http://www.sohu.com',
            'http://www.163.com',
        ],
        
        # 代理源设置
        'sources': {
            'kuaidaili': {'enabled': True, 'pages': 5},
            'ip89': {'enabled': True, 'pages': 10},
            'ip3366': {'enabled': True, 'pages': 5},
            'proxy_list_download': {'enabled': True},
            'geonode': {'enabled': True},
        },
        
        # Shadowsocks/V2Ray 设置
        'shadowsocks': {
            'method': 'aes-256-gcm',
            'password': None,  # None表示自动生成随机密码
        },
        'v2ray': {
            'uuid': None,  # None表示自动生成随机UUID
        },
        
        # 输出设置
        'output': {
            'default_dir': 'output',
            'formats': ['http', 'https', 'socks5', 'clash', 'shadowsocks', 'json'],
        },
        
        # UI设置
        'ui': {
            'window_width': 1200,
            'window_height': 800,
            'theme': 'default',
        }
    }
    
    def __init__(self, config_file: str = 'config/settings.json'):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                # 合并用户配置和默认配置
                return self._merge_config(self.DEFAULT_CONFIG.copy(), user_config)
            except Exception as e:
                print(f"加载配置文件失败: {e}，使用默认配置")
                return self.DEFAULT_CONFIG.copy()
        else:
            # 配置文件不存在，创建默认配置
            self.save_config(self.DEFAULT_CONFIG.copy())
            return self.DEFAULT_CONFIG.copy()
    
    def save_config(self, config: Dict[str, Any] = None):
        """保存配置到文件"""
        if config is None:
            config = self.config
        
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            self.config = config
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False
    
    def _merge_config(self, default: Dict, user: Dict) -> Dict:
        """递归合并配置"""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any):
        """设置配置项"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save_config()
    
    def get_timeout(self) -> int:
        """获取超时时间"""
        return self.get('timeout', 10)
    
    def get_max_workers(self) -> int:
        """获取最大线程数"""
        return self.get('max_workers', 50)
    
    def get_test_urls(self) -> list:
        """获取测试URL列表"""
        return self.get('test_urls', self.DEFAULT_CONFIG['test_urls'])
    
    def get_enabled_sources(self) -> Dict[str, Dict]:
        """获取启用的代理源"""
        sources = self.get('sources', {})
        return {name: config for name, config in sources.items() if config.get('enabled', True)}
    
    def get_shadowsocks_config(self) -> Dict[str, str]:
        """获取Shadowsocks配置"""
        return {
            'method': self.get('shadowsocks.method', 'aes-256-gcm'),
            'password': self.get('shadowsocks.password')
        }
    
    def get_v2ray_config(self) -> Dict[str, str]:
        """获取V2Ray配置"""
        return {
            'uuid': self.get('v2ray.uuid')
        }
    
    def reset_to_default(self):
        """重置为默认配置"""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save_config()
        return self.config
    
    def export_config(self, filepath: str) -> bool:
        """导出配置到指定路径"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"导出配置失败: {e}")
            return False
    
    def import_config(self, filepath: str) -> bool:
        """从指定路径导入配置"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
            self.config = self._merge_config(self.DEFAULT_CONFIG.copy(), user_config)
            self.save_config()
            return True
        except Exception as e:
            print(f"导入配置失败: {e}")
            return False


# 全局配置实例
_config_instance = None

def get_config(config_file: str = 'config/settings.json') -> ConfigManager:
    """获取全局配置实例"""
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigManager(config_file)
    return _config_instance
