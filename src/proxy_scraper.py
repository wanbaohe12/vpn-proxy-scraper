#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代理抓取核心模块
支持多个代理源，严格测试
"""

import requests
import re
import time
import json
import concurrent.futures
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import random
from bs4 import BeautifulSoup
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ProxyScraper:
    """高级代理抓取器"""
    
    def __init__(self, timeout: int = 10, max_workers: int = 30):
        self.timeout = timeout
        self.max_workers = max_workers
        self.session = requests.Session()
        
        # 用户代理
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
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
        }
    
    def fetch_url(self, url: str) -> Optional[str]:
        """获取网页内容"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                headers = self.get_random_headers()
                response = self.session.get(
                    url, 
                    headers=headers, 
                    timeout=self.timeout,
                    verify=False
                )
                response.raise_for_status()
                return response.text
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"获取 {url} 失败: {e}")
                else:
                    time.sleep(1)
        return None
    
    # ==================== 代理源解析方法 ====================
    
    def parse_kuaidaili(self) -> List[Dict]:
        """快代理"""
        proxies = []
        try:
            for page in range(1, 4):
                url = f"https://www.kuaidaili.com/free/inha/{page}/"
                html = self.fetch_url(url)
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
                                'anonymity': 'high',
                                'protocol': protocol,
                                'type': 'http' if protocol != 'socks5' else 'socks5',
                                'source': 'kuaidaili.com',
                                'speed': '未知',
                                'score': 0,
                                'working': None,
                            }
                            proxies.append(proxy)
                time.sleep(0.5)
        except Exception as e:
            print(f"解析快代理失败: {e}")
        
        return proxies
    
    def parse_89ip(self) -> List[Dict]:
        """89IP代理"""
        proxies = []
        try:
            for page in range(1, 4):
                url = f"https://www.89ip.cn/index_{page}.html"
                html = self.fetch_url(url)
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
                            
                            match = re.match(r'(\d+\.\d+\.\d+\.\d+)[:\s]+(\d+)', ip_port)
                            if match:
                                ip = match.group(1)
                                port = match.group(2)
                                
                                proxy = {
                                    'ip': ip,
                                    'port': port,
                                    'country': '中国',
                                    'region': location,
                                    'anonymity': 'transparent',
                                    'protocol': 'http',
                                    'type': 'http',
                                    'source': '89ip.cn',
                                    'speed': '未知',
                                    'score': 0,
                                    'working': None,
                                }
                                proxies.append(proxy)
                time.sleep(0.5)
        except Exception as e:
            print(f"解析89ip失败: {e}")
        
        return proxies
    
    def parse_ip3366(self) -> List[Dict]:
        """IP3366代理"""
        proxies = []
        try:
            for page in range(1, 4):
                url = f"http://www.ip3366.net/?stype=1&page={page}"
                html = self.fetch_url(url)
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
                            location = cols[5].text.strip()
                            proxy_type = cols[3].text.strip().lower()
                            
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
                                'anonymity': 'high',
                                'protocol': protocol,
                                'type': 'http' if protocol != 'socks5' else 'socks5',
                                'source': 'ip3366.net',
                                'speed': '未知',
                                'score': 0,
                                'working': None,
                            }
                            proxies.append(proxy)
                time.sleep(0.5)
        except Exception as e:
            print(f"解析ip3366失败: {e}")
        
        return proxies
    
    def parse_zdaye(self) -> List[Dict]:
        """站大爷代理"""
        proxies = []
        try:
            url = "https://www.zdaye.com/"
            html = self.fetch_url(url)
            if not html:
                return proxies
                
            # 使用正则提取IP和端口
            pattern = r'(\d+\.\d+\.\d+\.\d+)[:\s]+(\d+)'
            matches = re.finditer(pattern, html)
            
            for match in matches:
                ip = match.group(1)
                port = match.group(2)
                
                proxy = {
                    'ip': ip,
                    'port': port,
                    'country': '中国',
                    'region': '未知',
                    'anonymity': 'high',
                    'protocol': 'http',
                    'type': 'http',
                    'source': 'zdaye.com',
                    'speed': '未知',
                    'score': 0,
                    'working': None,
                }
                proxies.append(proxy)
        except Exception as e:
            print(f"解析站大爷失败: {e}")
        
        return proxies
    
    # ==================== 代理测试方法 ====================
    
    def test_proxy_speed(self, proxy: Dict) -> Tuple[bool, float]:
        """测试代理速度和可用性"""
        test_urls = [
            'http://www.baidu.com',
            'http://www.qq.com',
            'http://www.taobao.com',
        ]
        
        proxy_url = f"{proxy['protocol']}://{proxy['ip']}:{proxy['port']}"
        
        for test_url in test_urls:
            try:
                start_time = time.time()
                response = requests.get(
                    test_url,
                    proxies={'http': proxy_url, 'https': proxy_url},
                    timeout=self.timeout,
                    verify=False
                )
                elapsed = time.time() - start_time
                
                if response.status_code == 200 and len(response.text) > 1000:
                    return True, round(elapsed * 1000, 2)  # 毫秒
            except:
                continue
        
        return False, 0
    
    def test_proxy_comprehensive(self, proxy: Dict) -> Optional[Dict]:
        """全面测试代理"""
        try:
            # 测试速度和可用性
            working, speed = self.test_proxy_speed(proxy)
            if not working:
                proxy['working'] = False
                proxy['error'] = '连接失败'
                return proxy
            
            # 计算评分
            score = 0
            if speed < 1000: score += 30
            elif speed < 3000: score += 20
            elif speed < 5000: score += 10
            
            if proxy['anonymity'] == 'high': score += 20
            elif proxy['anonymity'] == 'anonymous': score += 15
            elif proxy['anonymity'] == 'elite': score += 25
            
            if proxy['protocol'] == 'https': score += 10
            if 'socks' in proxy['protocol']: score += 5
            
            # 更新代理信息
            proxy.update({
                'working': True,
                'speed_ms': speed,
                'score': score,
                'last_checked': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
            return proxy
            
        except Exception as e:
            proxy['working'] = False
            proxy['error'] = str(e)
            return proxy
    
    def test_proxies_batch(self, proxies: List[Dict], progress_callback=None) -> Tuple[List[Dict], List[Dict]]:
        """批量测试代理"""
        working = []
        failed = []
        
        print(f"开始测试 {len(proxies)} 个代理...")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.test_proxy_comprehensive, proxy): proxy for proxy in proxies}
            
            for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
                proxy = futures[future]
                try:
                    result = future.result()
                    if result and result.get('working'):
                        working.append(result)
                        msg = f"{proxy['ip']}:{proxy['port']} - 可用 ({result['speed_ms']}ms)"
                    else:
                        failed.append(result if result else proxy)
                        msg = f"{proxy['ip']}:{proxy['port']} - 不可用"
                        
                    if progress_callback:
                        progress_callback(i, len(proxies), len(working), len(failed), msg)
                    else:
                        status = "✓" if result and result.get('working') else "✗"
                        print(f"[{status}] {i}/{len(proxies)} {msg}")
                        
                except Exception as e:
                    failed.append(proxy)
                    msg = f"{proxy['ip']}:{proxy['port']} - 测试异常"
                    if progress_callback:
                        progress_callback(i, len(proxies), len(working), len(failed), msg)
                    else:
                        print(f"[✗] {i}/{len(proxies)} {msg}: {e}")
                
                # 进度显示
                if i % 10 == 0 or i == len(proxies):
                    if not progress_callback:
                        print(f"进度: {i}/{len(proxies)} | 可用: {len(working)} | 不可用: {len(failed)}")
        
        return working, failed
    
    # ==================== 代理抓取主流程 ====================
    
    def scrape_all_proxies(self) -> List[Dict]:
        """从所有源抓取代理"""
        all_proxies = []
        
        print("开始从多个源抓取代理...")
        
        # 国内源
        sources = [
            self.parse_kuaidaili,
            self.parse_89ip,
            self.parse_ip3366,
            self.parse_zdaye,
        ]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(sources)) as executor:
            futures = [executor.submit(source) for source in sources]
            for future in concurrent.futures.as_completed(futures):
                try:
                    proxies = future.result()
                    all_proxies.extend(proxies)
                    print(f"抓取到 {len(proxies)} 个代理")
                except Exception as e:
                    print(f"抓取失败: {e}")
        
        # 去重
        unique_proxies = []
        seen = set()
        for proxy in all_proxies:
            key = f"{proxy['ip']}:{proxy['port']}:{proxy['protocol']}"
            if key not in seen:
                seen.add(key)
                unique_proxies.append(proxy)
        
        print(f"总共抓取到 {len(unique_proxies)} 个唯一代理")
        return unique_proxies