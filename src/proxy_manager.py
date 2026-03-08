#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代理管理器 - 核心功能模块
负责代理抓取、测试、管理和输出
"""

import requests
import concurrent.futures
import time
import json
import re
import socket
import threading
import queue
import random
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Set
from bs4 import BeautifulSoup
import urllib3
import logging

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ProxyManager:
    """代理管理器"""
    
    def __init__(self, timeout: int = 10, max_workers: int = 50):
        self.timeout = timeout
        self.max_workers = max_workers
        self.session = requests.Session()
        self.all_proxies = []
        self.working_proxies = []
        self.failed_proxies = []
        
        # 用户代理池
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/119.0.0.0 Safari/537.36',
        ]
    
    def get_random_headers(self) -> Dict[str, str]:
        """获取随机请求头"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        }
    
    def fetch_with_retry(self, url: str, max_retries: int = 3) -> Optional[str]:
        """带重试机制的网页获取"""
        for attempt in range(max_retries):
            try:
                headers = self.get_random_headers()
                response = self.session.get(
                    url,
                    headers=headers,
                    timeout=self.timeout,
                    verify=False,
                    allow_redirects=True
                )
                response.raise_for_status()
                return response.text
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.debug(f"获取 {url} 失败 ({attempt+1}/{max_retries}): {e}")
                else:
                    time.sleep(1)
        return None
    
    # ==================== 代理源解析 ====================
    
    def parse_kuaidaili(self) -> List[Dict]:
        """快代理 - 国内高匿代理"""
        proxies = []
        try:
            # 抓取多个页面
            base_urls = [
                "https://www.kuaidaili.com/free/inha/{}/",  # 高匿
                "https://www.kuaidaili.com/free/intr/{}/",  # 普通
            ]
            
            for base_url in base_urls:
                for page in range(1, 6):  # 前5页
                    url = base_url.format(page)
                    html = self.fetch_with_retry(url)
                    if not html:
                        continue
                    
                    soup = BeautifulSoup(html, 'html.parser')
                    table = soup.find('table')
                    
                    if table:
                        rows = table.find_all('tr')[1:]
                        for row in rows:
                            cols = row.find_all('td')
                            if len(cols) >= 8:
                                ip = cols[0].text.strip()
                                port = cols[1].text.strip()
                                proxy_type = cols[3].text.strip().lower()
                                location = cols[4].text.strip()
                                
                                protocol = 'http'
                                if 'https' in proxy_type:
                                    protocol = 'https'
                                elif 'socks' in proxy_type:
                                    protocol = 'socks5'
                                
                                proxy = {
                                    'ip': ip,
                                    'port': port,
                                    'country': '中国',
                                    'region': location,
                                    'anonymity': '高匿',
                                    'protocol': protocol,
                                    'type': 'http' if protocol != 'socks5' else 'socks5',
                                    'source': 'kuaidaili.com',
                                    'added_at': datetime.now().isoformat(),
                                }
                                proxies.append(proxy)
                    
                    time.sleep(0.3)  # 礼貌延迟
                
        except Exception as e:
            logger.error(f"解析快代理失败: {e}")
        
        logger.info(f"快代理抓取到 {len(proxies)} 个代理")
        return proxies
    
    def parse_89ip(self) -> List[Dict]:
        """89ip代理 - 国内透明代理"""
        proxies = []
        try:
            for page in range(1, 11):  # 前10页
                url = f"https://www.89ip.cn/index_{page}.html"
                html = self.fetch_with_retry(url)
                if not html:
                    continue
                
                soup = BeautifulSoup(html, 'html.parser')
                table = soup.find('table')
                
                if table:
                    rows = table.find_all('tr')[1:]
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) >= 2:
                            ip_port = cols[0].text.strip()
                            location = cols[1].text.strip() if len(cols) > 1 else "未知"
                            
                            # 解析IP和端口
                            match = re.match(r'(\d+\.\d+\.\d+\.\d+)[:\s]+(\d+)', ip_port)
                            if match:
                                ip = match.group(1)
                                port = match.group(2)
                                
                                proxy = {
                                    'ip': ip,
                                    'port': port,
                                    'country': '中国',
                                    'region': location,
                                    'anonymity': '透明',
                                    'protocol': 'http',
                                    'type': 'http',
                                    'source': '89ip.cn',
                                    'added_at': datetime.now().isoformat(),
                                }
                                proxies.append(proxy)
                
                time.sleep(0.3)
                
        except Exception as e:
            logger.error(f"解析89ip失败: {e}")
        
        logger.info(f"89ip抓取到 {len(proxies)} 个代理")
        return proxies
    
    def parse_ip3366(self) -> List[Dict]:
        """ip3366代理"""
        proxies = []
        try:
            for page in range(1, 6):
                url = f"http://www.ip3366.net/free/?stype=1&page={page}"
                html = self.fetch_with_retry(url)
                if not html:
                    continue
                
                soup = BeautifulSoup(html, 'html.parser')
                table = soup.find('table', {'class': 'table table-bordered table-striped'})
                
                if table:
                    rows = table.find_all('tr')[1:]
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) >= 8:
                            ip = cols[0].text.strip()
                            port = cols[1].text.strip()
                            proxy_type = cols[3].text.strip().lower()
                            location = cols[5].text.strip()
                            
                            protocol = 'http'
                            if 'https' in proxy_type:
                                protocol = 'https'
                            elif 'socks' in proxy_type:
                                protocol = 'socks5'
                            
                            proxy = {
                                'ip': ip,
                                'port': port,
                                'country': '中国',
                                'region': location,
                                'anonymity': '高匿',
                                'protocol': protocol,
                                'type': 'http' if protocol != 'socks5' else 'socks5',
                                'source': 'ip3366.net',
                                'added_at': datetime.now().isoformat(),
                            }
                            proxies.append(proxy)
                
                time.sleep(0.3)
                
        except Exception as e:
            logger.error(f"解析ip3366失败: {e}")
        
        logger.info(f"ip3366抓取到 {len(proxies)} 个代理")
        return proxies
    
    def parse_proxy_list_download(self) -> List[Dict]:
        """proxy-list.download - 国外代理"""
        proxies = []
        try:
            urls = [
                "https://www.proxy-list.download/api/v1/get?type=http",
                "https://www.proxy-list.download/api/v1/get?type=https",
                "https://www.proxy-list.download/api/v1/get?type=socks4",
                "https://www.proxy-list.download/api/v1/get?type=socks5",
            ]
            
            for url in urls:
                response = self.session.get(url, timeout=self.timeout)
                if response.status_code == 200:
                    lines = response.text.strip().split('\n')
                    for line in lines:
                        if ':' in line:
                            ip, port = line.strip().split(':')
                            
                            # 确定协议
                            if 'socks4' in url:
                                protocol = 'socks4'
                            elif 'socks5' in url:
                                protocol = 'socks5'
                            elif 'https' in url:
                                protocol = 'https'
                            else:
                                protocol = 'http'
                            
                            proxy = {
                                'ip': ip,
                                'port': port,
                                'country': '未知',
                                'region': '未知',
                                'anonymity': '未知',
                                'protocol': protocol,
                                'type': 'http' if protocol not in ['socks4', 'socks5'] else protocol,
                                'source': 'proxy-list.download',
                                'added_at': datetime.now().isoformat(),
                            }
                            proxies.append(proxy)
                
                time.sleep(0.5)
                
        except Exception as e:
            logger.error(f"解析proxy-list.download失败: {e}")
        
        logger.info(f"proxy-list.download抓取到 {len(proxies)} 个代理")
        return proxies
    
    def parse_geonode(self) -> List[Dict]:
        """Geonode - 免费代理API"""
        proxies = []
        try:
            url = "https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc"
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                for item in data.get('data', []):
                    proxy = {
                        'ip': item.get('ip'),
                        'port': str(item.get('port')),
                        'country': item.get('country', '未知'),
                        'region': item.get('city', '未知'),
                        'anonymity': item.get('anonymityLevel', '未知'),
                        'protocol': item.get('protocols', ['http'])[0].lower(),
                        'type': item.get('protocols', ['http'])[0].lower(),
                        'source': 'geonode.com',
                        'added_at': datetime.now().isoformat(),
                        'speed': item.get('speed', 0),
                        'uptime': item.get('uptime', '0%'),
                    }
                    proxies.append(proxy)
        except Exception as e:
            logger.error(f"解析Geonode失败: {e}")
        
        logger.info(f"Geonode抓取到 {len(proxies)} 个代理")
        return proxies
    
    # ==================== 代理测试 ====================
    
    def test_proxy(self, proxy: Dict) -> Optional[Dict]:
        """测试单个代理"""
        try:
            proxy_url = f"{proxy['protocol']}://{proxy['ip']}:{proxy['port']}"
            proxies_config = {
                'http': proxy_url,
                'https': proxy_url
            }
            
            # 测试1: 连接速度
            test_urls = [
                'http://www.baidu.com',
                'http://www.qq.com',
                'http://www.sohu.com',
            ]
            
            for test_url in test_urls:
                try:
                    start_time = time.time()
                    response = requests.get(
                        test_url,
                        proxies=proxies_config,
                        timeout=self.timeout,
                        verify=False,
                        headers=self.get_random_headers()
                    )
                    elapsed = time.time() - start_time
                    
                    if response.status_code == 200 and len(response.text) > 1000:
                        # 测试通过
                        proxy['working'] = True
                        proxy['response_time'] = round(elapsed * 1000, 2)  # 毫秒
                        proxy['last_checked'] = datetime.now().isoformat()
                        
                        # 计算评分
                        score = 0
                        if proxy['response_time'] < 1000:
                            score += 40
                        elif proxy['response_time'] < 3000:
                            score += 20
                        else:
                            score += 10
                        
                        if proxy['anonymity'] == '高匿':
                            score += 30
                        elif proxy['anonymity'] == '匿名':
                            score += 20
                        elif proxy['anonymity'] == '透明':
                            score += 10
                        
                        if proxy['protocol'] == 'https':
                            score += 20
                        
                        proxy['score'] = score
                        return proxy
                        
                except Exception:
                    continue
            
            # 所有测试都失败
            proxy['working'] = False
            proxy['last_checked'] = datetime.now().isoformat()
            return proxy
            
        except Exception as e:
            proxy['working'] = False
            proxy['error'] = str(e)
            proxy['last_checked'] = datetime.now().isoformat()
            return proxy
    
    def test_proxies_batch(self, proxies: List[Dict], progress_callback=None) -> Tuple[List[Dict], List[Dict]]:
        """批量测试代理"""
        working = []
        failed = []
        
        logger.info(f"开始测试 {len(proxies)} 个代理")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.test_proxy, proxy): proxy for proxy in proxies}
            
            for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
                proxy = futures[future]
                try:
                    result = future.result()
                    if result and result.get('working'):
                        working.append(result)
                        msg = f"✓ {proxy['ip']}:{proxy['port']} - {result['response_time']}ms"
                    else:
                        failed.append(result if result else proxy)
                        msg = f"✗ {proxy['ip']}:{proxy['port']}"
                    
                    if progress_callback:
                        progress_callback(i, len(proxies), len(working), len(failed), msg)
                    else:
                        if i % 10 == 0 or i == len(proxies):
                            logger.info(f"进度: {i}/{len(proxies)} | 可用: {len(working)} | 不可用: {len(failed)}")
                            
                except Exception as e:
                    failed.append(proxy)
                    msg = f"✗ {proxy['ip']}:{proxy['port']} - 错误: {str(e)[:50]}"
                    if progress_callback:
                        progress_callback(i, len(proxies), len(working), len(failed), msg)
        
        logger.info(f"测试完成: 可用 {len(working)} 个, 不可用 {len(failed)} 个")
        return working, failed
    
    # ==================== 主流程 ====================
    
    def scrape_proxies(self, progress_callback=None) -> List[Dict]:
        """抓取所有代理源"""
        all_proxies = []
        
        sources = [
            self.parse_kuaidaili,
            self.parse_89ip,
            self.parse_ip3366,
            self.parse_proxy_list_download,
            self.parse_geonode,
        ]
        
        logger.info("开始从多个源抓取代理...")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(sources)) as executor:
            futures = {executor.submit(source): source.__name__ for source in sources}
            
            for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
                source_name = futures[future]
                try:
                    proxies = future.result()
                    all_proxies.extend(proxies)
                    
                    msg = f"{source_name}: 抓取到 {len(proxies)} 个代理"
                    if progress_callback:
                        progress_callback(i, len(sources), len(all_proxies), 0, msg)
                    else:
                        logger.info(msg)
                        
                except Exception as e:
                    msg = f"{source_name}: 抓取失败 - {str(e)[:50]}"
                    if progress_callback:
                        progress_callback(i, len(sources), len(all_proxies), 0, msg)
                    else:
                        logger.error(msg)
        
        # 去重
        unique_proxies = []
        seen = set()
        for proxy in all_proxies:
            key = f"{proxy['ip']}:{proxy['port']}:{proxy['protocol']}"
            if key not in seen:
                seen.add(key)
                unique_proxies.append(proxy)
        
        self.all_proxies = unique_proxies
        logger.info(f"总共抓取到 {len(unique_proxies)} 个唯一代理")
        return unique_proxies
    
    def run_full_process(self, test_proxies: bool = True, progress_callback=None) -> Dict:
        """运行完整流程"""
        result = {
            'total_scraped': 0,
            'total_working': 0,
            'total_failed': 0,
            'working_proxies': [],
            'failed_proxies': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # 1. 抓取代理
        if progress_callback:
            progress_callback(0, 100, 0, 0, "开始抓取代理...")
        
        proxies = self.scrape_proxies(progress_callback)
        result['total_scraped'] = len(proxies)
        
        # 2. 测试代理
        if test_proxies and proxies:
            if progress_callback:
                progress_callback(50, 100, 0, 0, "开始测试代理...")
            
            working, failed = self.test_proxies_batch(proxies, progress_callback)
            result['working_proxies'] = working
            result['failed_proxies'] = failed
            result['total_working'] = len(working)
            result['total_failed'] = len(failed)
            
            # 按评分排序
            working.sort(key=lambda x: x.get('score', 0), reverse=True)
            result['working_proxies'] = working
            
            if progress_callback:
                progress_callback(100, 100, len(working), len(failed), 
                                f"完成! 可用: {len(working)} 个")
        
        return result
    
    # ==================== 输出格式 ====================
    
    @staticmethod
    def format_for_clash(proxies: List[Dict]) -> str:
        """Clash配置文件格式"""
        import yaml
        
        clash_config = {
            'proxies': [],
            'proxy-groups': [
                {
                    'name': '自动选择',
                    'type': 'url-test',
                    'proxies': [],
                    'url': 'http://www.gstatic.com/generate_204',
                    'interval': 300
                },
                {
                    'name': '手动选择',
                    'type': 'select',
                    'proxies': []
                }
            ],
            'rules': [
                'DOMAIN-SUFFIX,google.com,自动选择',
                'DOMAIN-SUFFIX,youtube.com,自动选择',
                'DOMAIN-SUFFIX,twitter.com,自动选择',
                'DOMAIN-SUFFIX,facebook.com,自动选择',
                'GEOIP,CN,DIRECT',
                'MATCH,自动选择'
            ]
        }
        
        for i, proxy in enumerate(proxies):
            if proxy.get('working'):
                proxy_name = f"proxy_{i+1}"
                
                if proxy['protocol'] in ['socks4', 'socks5']:
                    proxy_config = {
                        'name': proxy_name,
                        'type': 'socks5',
                        'server': proxy['ip'],
                        'port': int(proxy['port']),
                        'udp': True
                    }
                else:
                    proxy_config = {
                        'name': proxy_name,
                        'type': 'http' if proxy['protocol'] == 'http' else 'https',
                        'server': proxy['ip'],
                        'port': int(proxy['port']),
                        'tls': proxy['protocol'] == 'https',
                        'skip-cert-verify': True
                    }
                
                clash_config['proxies'].append(proxy_config)
                clash_config['proxy-groups'][0]['proxies'].append(proxy_name)
                clash_config['proxy-groups'][1]['proxies'].append(proxy_name)
        
        return yaml.dump(clash_config, allow_unicode=True, sort_keys=False)
    
    @staticmethod
    def format_for_shadowsocks(proxies: List[Dict]) -> str:
        """Shadowsocks订阅链接格式"""
        import base64
        
        ss_links = []
        for proxy in proxies:
            if proxy.get('working'):
                # 简化配置
                config = {
                    'server': proxy['ip'],
                    'server_port': int(proxy['port']),
                    'password': 'password123',  # 默认密码
                    'method': 'aes-256-gcm',
                    'remarks': f"{proxy['ip']}:{proxy['port']}"
                }
                
                # 创建ss://链接
                uri = f"{config['method']}:{config['password']}@{config['server']}:{config['server_port']}#{config['remarks']}"
                encoded = base64.b64encode(uri.encode()).decode()
                ss_links.append(f"ss://{encoded}")
        
        # 订阅链接格式
        return "\n".join(ss_links)
    
    @staticmethod
    def format_simple_list(proxies: List[Dict], protocol_filter: str = None) -> str:
        """简单代理列表格式"""
        lines = []
        for proxy in proxies:
            if proxy.get('working'):
                if protocol_filter and proxy['protocol'] != protocol_filter:
                    continue
                lines.append(f"{proxy['protocol']}://{proxy['ip']}:{proxy['port']}")
        return "\n".join(lines)
    
    @staticmethod
    def format_json(proxies: List[Dict]) -> str:
        """JSON格式输出"""
        return json.dumps(proxies, ensure_ascii=False, indent=2)
    
    # ==================== 订阅链接功能 ====================
    
    @staticmethod
    def generate_ss_subscription_links(proxies: List[Dict]) -> Dict[str, str]:
        """生成Shadowsocks订阅链接"""
        import base64
        
        subscription_links = {
            "raw_links": [],      # 原始SS链接列表
            "base64_encoded": "", # base64编码的订阅内容
            "data_url": "",       # data: URL格式
            "subscription_url": "" # 完整订阅链接（如果启动服务器）
        }
        
        # 生成原始SS链接
        ss_links = []
        for proxy in proxies:
            if proxy.get('working') and proxy['protocol'] in ['http', 'https', 'socks4', 'socks5']:
                # 转换为SS格式需要密码和加密方法
                # 使用默认配置
                password = "openclaw123"
                method = "aes-256-gcm"
                
                # SS URI格式: ss://method:password@host:port#remark
                ss_uri = f"{method}:{password}@{proxy['ip']}:{proxy['port']}#{proxy['ip']}:{proxy['port']}"
                encoded_uri = base64.b64encode(ss_uri.encode()).decode()
                ss_link = f"ss://{encoded_uri}"
                ss_links.append(ss_link)
        
        subscription_links["raw_links"] = ss_links
        
        # 生成base64编码的订阅内容（多个链接每行一个）
        if ss_links:
            subscription_content = "\n".join(ss_links)
            subscription_links["base64_encoded"] = base64.b64encode(
                subscription_content.encode()
            ).decode()
            
            # 生成data: URL
            subscription_links["data_url"] = (
                f"data:text/plain;base64,{subscription_links['base64_encoded']}"
            )
        
        return subscription_links
    
    @staticmethod
    def generate_clash_subscription(proxies: List[Dict]) -> Dict[str, str]:
        """生成Clash订阅内容"""
        # 直接调用静态方法
        clash_yaml = ProxyManager.format_for_clash(proxies)
        
        import base64
        encoded_content = base64.b64encode(clash_yaml.encode()).decode()
        
        return {
            "yaml_content": clash_yaml,
            "base64_encoded": encoded_content,
            "data_url": f"data:text/yaml;base64,{encoded_content}"
        }
    
    @staticmethod  
    def generate_subscription_links(proxies: List[Dict]) -> Dict[str, Dict]:
        """生成所有订阅链接格式"""
        return {
            "shadowsocks": ProxyManager.generate_ss_subscription_links(proxies),
            "clash": ProxyManager.generate_clash_subscription(proxies),
            "simple_list": {
                "http_list": ProxyManager.format_simple_list(proxies, 'http'),
                "socks5_list": ProxyManager.format_simple_list(proxies, 'socks5'),
                "all_list": ProxyManager.format_simple_list(proxies)
            }
        }
    
    def start_subscription_server(self, proxies: List[Dict], port: int = 8080) -> Dict[str, str]:
        """启动本地订阅服务器（简单实现）"""
        import threading
        from http.server import HTTPServer, BaseHTTPRequestHandler
        import urllib.parse
        import base64
        
        class SubscriptionHandler(BaseHTTPRequestHandler):
            proxies = proxies
            manager = self
            
            def do_GET(self):
                parsed = urllib.parse.urlparse(self.path)
                path = parsed.path
                
                if path == '/subscription/ss':
                    # Shadowsocks订阅
                    links = self.manager.generate_ss_subscription_links(self.proxies)
                    content = "\n".join(links["raw_links"])
                    encoded = base64.b64encode(content.encode()).decode()
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/plain')
                    self.end_headers()
                    self.wfile.write(encoded.encode())
                    
                elif path == '/subscription/clash':
                    # Clash订阅
                    subscription = self.manager.generate_clash_subscription(self.proxies)
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/yaml')
                    self.end_headers()
                    self.wfile.write(subscription["yaml_content"].encode())
                    
                elif path == '/subscription/raw':
                    # 原始链接列表
                    content = self.manager.format_simple_list(self.proxies)
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/plain')
                    self.end_headers()
                    self.wfile.write(content.encode())
                    
                else:
                    # 默认页面
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html')
                    self.end_headers()
                    
                    html = f"""
                    <html>
                    <head><title>代理订阅服务器</title></head>
                    <body>
                        <h1>代理订阅服务器</h1>
                        <p>可用订阅链接：</p>
                        <ul>
                            <li><a href="/subscription/ss">Shadowsocks订阅</a></li>
                            <li><a href="/subscription/clash">Clash配置</a></li>
                            <li><a href="/subscription/raw">原始代理列表</a></li>
                        </ul>
                        <p>将上述链接复制到代理客户端即可导入。</p>
                    </body>
                    </html>
                    """
                    self.wfile.write(html.encode())
        
        server = HTTPServer(('localhost', port), SubscriptionHandler)
        server_thread = threading.Thread(target=server.serve_forever, daemon=True)
        server_thread.start()
        
        return {
            "server": server,
            "thread": server_thread,
            "urls": {
                "shadowsocks": f"http://localhost:{port}/subscription/ss",
                "clash": f"http://localhost:{port}/subscription/clash",
                "raw": f"http://localhost:{port}/subscription/raw",
                "web": f"http://localhost:{port}/"
            }
        }
    
    # ==================== 导出功能 ====================
    
    def export_proxies(self, proxies: List[Dict], output_dir: str = "output") -> Dict[str, str]:
        """导出所有格式"""
        import os
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        formats = {
            'http.txt': self.format_simple_list(proxies, 'http'),
            'https.txt': self.format_simple_list(proxies, 'https'),
            'socks5.txt': self.format_simple_list(proxies, 'socks5'),
            'all_proxies.txt': self.format_simple_list(proxies),
            'clash.yaml': self.format_for_clash(proxies),
            'shadowsocks.txt': self.format_for_shadowsocks(proxies),
            'proxies.json': self.format_json(proxies),
        }
        
        # 生成订阅链接内容
        subscription_links = self.generate_subscription_links(proxies)
        
        # 添加订阅链接文件
        subscription_formats = {
            'ss_subscription.txt': '\n'.join(subscription_links['shadowsocks']['raw_links']),
            'subscription_base64.txt': subscription_links['shadowsocks']['base64_encoded'],
            'subscription_data_url.txt': subscription_links['shadowsocks']['data_url'],
            'clash_subscription.yaml': subscription_links['clash']['yaml_content'],
            'clash_base64.txt': subscription_links['clash']['base64_encoded'],
            'clash_data_url.txt': subscription_links['clash']['data_url'],
        }
        
        # 合并格式
        formats.update(subscription_formats)
        
        saved_files = {}
        for filename, content in formats.items():
            if content and content.strip():
                filepath = os.path.join(output_dir, f"{timestamp}_{filename}")
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                saved_files[filename] = filepath
        
        # 生成报告
        report = self._generate_report(proxies, timestamp, saved_files)
        report_path = os.path.join(output_dir, f"{timestamp}_report.txt")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        saved_files['report.txt'] = report_path
        
        return saved_files
    
    def _generate_report(self, proxies: List[Dict], timestamp: str, saved_files: Dict) -> str:
        """生成报告"""
        working = [p for p in proxies if p.get('working')]
        
        report = [
            "=" * 60,
            f"代理抓取报告 - {timestamp}",
            "=" * 60,
            f"抓取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"总代理数: {len(proxies)}",
            f"可用代理: {len(working)}",
            f"可用率: {len(working)/len(proxies)*100:.1f}%" if proxies else "0%",
            "",
            "代理类型统计:",
        ]
        
        # 统计
        protocols = {}
        for proxy in working:
            protocol = proxy['protocol']
            protocols[protocol] = protocols.get(protocol, 0) + 1
        
        for protocol, count in sorted(protocols.items()):
            report.append(f"  {protocol.upper():10s}: {count:4d} 个")
        
        if working:
            report.extend([
                "",
                "最快10个代理:",
            ])
            
            fastest = sorted(working, key=lambda x: x.get('response_time', 9999))[:10]
            for i, proxy in enumerate(fastest, 1):
                report.append(
                    f"{i:2d}. {proxy['protocol']}://{proxy['ip']}:{proxy['port']} "
                    f"- {proxy.get('response_time', 0):.0f}ms "
                    f"- {proxy.get('country', '未知')}"
                )
        
        report.extend([
            "",
            "生成的文件:",
        ])
        
        for filename, filepath in saved_files.items():
            if os.path.exists(filepath):
                size = os.path.getsize(filepath)
                report.append(f"  {filename:20s} - {size:,d} bytes")
        
        report.extend([
            "",
            "使用说明:",
            "  1. HTTP/HTTPS代理: 直接复制到代理软件",
            "  2. Clash配置: 导入到Clash客户端",
            "  3. Shadowsocks: 添加到订阅或手动添加",
            "  4. SOCKS5: 支持SOCKS5的软件可直接使用",
            "",
            "订阅链接使用:",
            "  5. SS订阅链接: 复制 ss_subscription.txt 内容到支持SS的客户端",
            "  6. Base64订阅: 复制 subscription_base64.txt 内容作为订阅链接",
            "  7. Data URL: 复制 subscription_data_url.txt 的data: URL",
            "  8. Clash订阅: 直接导入 clash_subscription.yaml",
            "",
            "提示: 使用 start_subscription_server() 启动本地HTTP服务器",
            "      生成可访问的订阅链接URL",
            "=" * 60
        ])
        
        return "\n".join(report)