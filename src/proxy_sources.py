#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代理源模块
支持多个代理源的抓取，包含错误处理和重试机制
"""

import requests
import re
import time
import json
import random
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ProxySourceBase:
    """代理源基类"""
    
    def __init__(self, timeout: int = 10, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
        ]
    
    def get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def fetch(self, url: str) -> Optional[str]:
        """带重试的网页获取"""
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(
                    url,
                    headers=self.get_headers(),
                    timeout=self.timeout,
                    verify=False
                )
                response.raise_for_status()
                return response.text
            except Exception as e:
                logger.debug(f"获取 {url} 失败 ({attempt+1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(random.uniform(1, 3))
        return None
    
    def parse(self) -> List[Dict]:
        """解析代理，子类必须实现"""
        raise NotImplementedError


class KuaiDaiLiSource(ProxySourceBase):
    """快代理源"""
    
    name = '快代理'
    source = 'kuaidaili.com'
    
    def __init__(self, timeout: int = 10, pages: int = 5):
        super().__init__(timeout)
        self.pages = pages
    
    def parse(self) -> List[Dict]:
        proxies = []
        base_urls = [
            "https://www.kuaidaili.com/free/inha/{}/",  # 高匿
            "https://www.kuaidaili.com/free/intr/{}/",  # 普通
        ]
        
        for base_url in base_urls:
            for page in range(1, self.pages + 1):
                url = base_url.format(page)
                html = self.fetch(url)
                
                if not html:
                    continue
                
                try:
                    soup = BeautifulSoup(html, 'html.parser')
                    table = soup.find('table', {'class': 'table'})
                    
                    if table:
                        rows = table.find_all('tr')[1:]
                        for row in rows:
                            cols = row.find_all('td')
                            if len(cols) >= 7:
                                ip = cols[0].text.strip()
                                port = cols[1].text.strip()
                                proxy_type = cols[3].text.strip().lower()
                                location = cols[4].text.strip() if len(cols) > 4 else "未知"
                                
                                # 确定协议
                                if 'https' in proxy_type:
                                    protocol = 'https'
                                elif 'socks5' in proxy_type:
                                    protocol = 'socks5'
                                else:
                                    protocol = 'http'
                                
                                proxies.append({
                                    'ip': ip,
                                    'port': port,
                                    'protocol': protocol,
                                    'country': '中国',
                                    'region': location,
                                    'anonymity': '高匿' if 'inha' in base_url else '普通',
                                    'source': self.source,
                                    'added_at': datetime.now().isoformat(),
                                })
                except Exception as e:
                    logger.error(f"解析快代理页面失败: {e}")
                
                time.sleep(random.uniform(1, 2))
        
        logger.info(f"{self.name} 抓取到 {len(proxies)} 个代理")
        return proxies


class IP89Source(ProxySourceBase):
    """89IP代理源"""
    
    name = '89IP'
    source = '89ip.cn'
    
    def __init__(self, timeout: int = 10, pages: int = 10):
        super().__init__(timeout)
        self.pages = pages
    
    def parse(self) -> List[Dict]:
        proxies = []
        
        for page in range(1, self.pages + 1):
            url = f"https://www.89ip.cn/index_{page}.html"
            html = self.fetch(url)
            
            if not html:
                continue
            
            try:
                soup = BeautifulSoup(html, 'html.parser')
                table = soup.find('table', {'class': 'layui-table'})
                
                if table:
                    rows = table.find_all('tr')[1:]
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) >= 2:
                            ip = cols[0].text.strip()
                            port = cols[1].text.strip()
                            location = cols[2].text.strip() if len(cols) > 2 else "未知"
                            
                            proxies.append({
                                'ip': ip,
                                'port': port,
                                'protocol': 'http',
                                'country': '中国',
                                'region': location,
                                'anonymity': '透明',
                                'source': self.source,
                                'added_at': datetime.now().isoformat(),
                            })
            except Exception as e:
                logger.error(f"解析89IP页面失败: {e}")
            
            time.sleep(random.uniform(0.5, 1.5))
        
        logger.info(f"{self.name} 抓取到 {len(proxies)} 个代理")
        return proxies


class IP3366Source(ProxySourceBase):
    """IP3366代理源"""
    
    name = 'IP3366'
    source = 'ip3366.net'
    
    def __init__(self, timeout: int = 10, pages: int = 5):
        super().__init__(timeout)
        self.pages = pages
    
    def parse(self) -> List[Dict]:
        proxies = []
        
        for page in range(1, self.pages + 1):
            url = f"http://www.ip3366.net/free/?stype=1&page={page}"
            html = self.fetch(url)
            
            if not html:
                continue
            
            try:
                soup = BeautifulSoup(html, 'html.parser')
                table = soup.find('table', {'class': 'table'})
                
                if table:
                    rows = table.find_all('tr')[1:]
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) >= 7:
                            ip = cols[0].text.strip()
                            port = cols[1].text.strip()
                            proxy_type = cols[3].text.strip().lower()
                            location = cols[4].text.strip() if len(cols) > 4 else "未知"
                            
                            # 确定协议
                            if 'https' in proxy_type:
                                protocol = 'https'
                            elif 'socks5' in proxy_type:
                                protocol = 'socks5'
                            else:
                                protocol = 'http'
                            
                            proxies.append({
                                'ip': ip,
                                'port': port,
                                'protocol': protocol,
                                'country': '中国',
                                'region': location,
                                'anonymity': '高匿',
                                'source': self.source,
                                'added_at': datetime.now().isoformat(),
                            })
            except Exception as e:
                logger.error(f"解析IP3366页面失败: {e}")
            
            time.sleep(random.uniform(0.5, 1.5))
        
        logger.info(f"{self.name} 抓取到 {len(proxies)} 个代理")
        return proxies


class ProxyListDownloadSource(ProxySourceBase):
    """Proxy-List.Download API源"""
    
    name = 'ProxyListDownload'
    source = 'proxy-list.download'
    
    def parse(self) -> List[Dict]:
        proxies = []
        urls = [
            ("https://www.proxy-list.download/api/v1/get?type=http", "http"),
            ("https://www.proxy-list.download/api/v1/get?type=https", "https"),
            ("https://www.proxy-list.download/api/v1/get?type=socks4", "socks4"),
            ("https://www.proxy-list.download/api/v1/get?type=socks5", "socks5"),
        ]
        
        for url, protocol in urls:
            try:
                response = self.session.get(url, headers=self.get_headers(), timeout=self.timeout)
                if response.status_code == 200:
                    lines = response.text.strip().split('\n')
                    for line in lines:
                        if ':' in line:
                            parts = line.strip().split(':')
                            if len(parts) >= 2:
                                ip = parts[0]
                                port = parts[1]
                                
                                proxies.append({
                                    'ip': ip,
                                    'port': port,
                                    'protocol': protocol,
                                    'country': '未知',
                                    'region': '未知',
                                    'anonymity': '未知',
                                    'source': self.source,
                                    'added_at': datetime.now().isoformat(),
                                })
            except Exception as e:
                logger.error(f"获取ProxyListDownload失败: {e}")
            
            time.sleep(random.uniform(0.5, 1))
        
        logger.info(f"{self.name} 抓取到 {len(proxies)} 个代理")
        return proxies


class GeoNodeSource(ProxySourceBase):
    """GeoNode API源"""
    
    name = 'GeoNode'
    source = 'geonode.com'
    
    def parse(self) -> List[Dict]:
        proxies = []
        
        try:
            url = "https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc"
            response = self.session.get(url, headers=self.get_headers(), timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                for item in data.get('data', []):
                    protocols = item.get('protocols', ['http'])
                    protocol = protocols[0].lower() if protocols else 'http'
                    
                    proxies.append({
                        'ip': item.get('ip'),
                        'port': str(item.get('port')),
                        'protocol': protocol,
                        'country': item.get('country', '未知'),
                        'region': item.get('city', '未知'),
                        'anonymity': item.get('anonymityLevel', '未知'),
                        'source': self.source,
                        'added_at': datetime.now().isoformat(),
                    })
        except Exception as e:
            logger.error(f"获取GeoNode失败: {e}")
        
        logger.info(f"{self.name} 抓取到 {len(proxies)} 个代理")
        return proxies


# 代理源注册表
PROXY_SOURCES = {
    'kuaidaili': KuaiDaiLiSource,
    'ip89': IP89Source,
    'ip3366': IP3366Source,
    'proxy_list_download': ProxyListDownloadSource,
    'geonode': GeoNodeSource,
}


def get_proxy_source(name: str, **kwargs) -> Optional[ProxySourceBase]:
    """获取代理源实例"""
    if name in PROXY_SOURCES:
        return PROXY_SOURCES[name](**kwargs)
    return None


def get_all_sources(timeout: int = 10) -> List[ProxySourceBase]:
    """获取所有代理源实例"""
    return [source_class(timeout=timeout) for source_class in PROXY_SOURCES.values()]
