#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
输出格式化模块
支持多种代理软件格式输出
"""

import json
import yaml
import base64
from typing import List, Dict
import datetime


class OutputFormatter:
    """输出格式化器"""
    
    @staticmethod
    def format_socks5(proxies: List[Dict]) -> str:
        """Socks5格式输出"""
        lines = []
        for proxy in proxies:
            if proxy.get('working') and proxy.get('protocol') in ['socks', 'socks5']:
                lines.append(f"socks5://{proxy['ip']}:{proxy['port']}")
        return "\n".join(lines)
    
    @staticmethod
    def format_http(proxies: List[Dict]) -> str:
        """HTTP/HTTPS格式输出"""
        lines = []
        for proxy in proxies:
            if proxy.get('working') and proxy.get('protocol') in ['http', 'https']:
                lines.append(f"{proxy['protocol']}://{proxy['ip']}:{proxy['port']}")
        return "\n".join(lines)
    
    @staticmethod
    def format_shadowsocks(proxies: List[Dict]) -> str:
        """Shadowsocks格式输出 (base64编码)"""
        configs = []
        for proxy in proxies:
            if proxy.get('working'):
                # Shadowsocks需要密码，这里使用默认值
                config = {
                    "server": proxy['ip'],
                    "server_port": int(proxy['port']),
                    "password": "password123",  # 默认密码
                    "method": "aes-256-gcm",
                    "remarks": f"{proxy['ip']}:{proxy['port']} - {proxy.get('score', 0)}分"
                }
                configs.append(config)
        
        # 转为ss://格式
        ss_links = []
        for config in configs:
            # 格式: method:password@server:port
            method = config['method']
            password = config['password']
            server = config['server']
            port = config['server_port']
            remark = config['remarks']
            
            # 创建ss://链接
            ss_uri = f"{method}:{password}@{server}:{port}#{remark}"
            encoded = base64.b64encode(ss_uri.encode()).decode()
            ss_links.append(f"ss://{encoded}")
        
        return "\n".join(ss_links)
    
    @staticmethod
    def format_clash(proxies: List[Dict]) -> str:
        """Clash配置格式输出"""
        clash_config = {
            "proxies": [],
            "proxy-groups": [
                {
                    "name": "自动选择",
                    "type": "url-test",
                    "proxies": [],
                    "url": "http://www.gstatic.com/generate_204",
                    "interval": 300
                },
                {
                    "name": "香港节点",
                    "type": "select",
                    "proxies": []
                },
                {
                    "name": "美国节点",
                    "type": "select",
                    "proxies": []
                },
                {
                    "name": "日本节点",
                    "type": "select",
                    "proxies": []
                }
            ],
            "rules": [
                "DOMAIN-SUFFIX,google.com,自动选择",
                "DOMAIN-SUFFIX,youtube.com,自动选择",
                "DOMAIN-SUFFIX,twitter.com,自动选择",
                "DOMAIN-SUFFIX,facebook.com,自动选择",
                "GEOIP,CN,DIRECT",
                "MATCH,自动选择"
            ]
        }
        
        for i, proxy in enumerate(proxies):
            if proxy.get('working'):
                proxy_name = f"proxy_{i+1}"
                
                # 根据代理类型创建配置
                if proxy.get('protocol') in ['socks', 'socks5']:
                    proxy_config = {
                        "name": proxy_name,
                        "type": "socks5",
                        "server": proxy['ip'],
                        "port": int(proxy['port']),
                        "udp": True
                    }
                else:  # HTTP/HTTPS
                    proxy_config = {
                        "name": proxy_name,
                        "type": "http",
                        "server": proxy['ip'],
                        "port": int(proxy['port']),
                        "tls": proxy.get('protocol') == 'https',
                        "skip-cert-verify": True
                    }
                
                # 添加地区信息
                if 'country' in proxy:
                    proxy_config['country'] = proxy['country']
                
                clash_config["proxies"].append(proxy_config)
                clash_config["proxy-groups"][0]["proxies"].append(proxy_name)
                
                # 按地区分组
                country = proxy.get('country', '').lower()
                if '香港' in country or 'hongkong' in country:
                    clash_config["proxy-groups"][1]["proxies"].append(proxy_name)
                elif '美国' in country or 'usa' in country or 'united states' in country:
                    clash_config["proxy-groups"][2]["proxies"].append(proxy_name)
                elif '日本' in country or 'japan' in country:
                    clash_config["proxy-groups"][3]["proxies"].append(proxy_name)
        
        return yaml.dump(clash_config, allow_unicode=True, sort_keys=False)
    
    @staticmethod
    def format_v2ray(proxies: List[Dict]) -> str:
        """V2Ray格式输出"""
        v2ray_configs = []
        
        for proxy in proxies:
            if proxy.get('working'):
                # 简化V2Ray配置
                config = {
                    "v": "2",
                    "ps": f"{proxy['ip']}:{proxy['port']} - {proxy.get('score', 0)}分",
                    "add": proxy['ip'],
                    "port": proxy['port'],
                    "id": "b831381d-6324-4d53-ad4f-8cda48b30811",  # 默认UUID
                    "aid": "0",
                    "net": "tcp",
                    "type": "none",
                    "host": "",
                    "path": "",
                    "tls": ""
                }
                
                # 转为vmess://链接
                import json
                json_str = json.dumps(config)
                encoded = base64.b64encode(json_str.encode()).decode()
                v2ray_configs.append(f"vmess://{encoded}")
        
        return "\n".join(v2ray_configs)
    
    @staticmethod
    def format_proxifier(proxies: List[Dict]) -> str:
        """Proxifier格式输出"""
        lines = []
        for proxy in proxies:
            if proxy.get('working'):
                protocol = proxy['protocol'].upper()
                lines.append(f"{proxy['ip']}:{proxy['port']} {protocol}")
        return "\n".join(lines)
    
    @staticmethod
    def format_burpsuite(proxies: List[Dict]) -> str:
        """BurpSuite格式输出"""
        lines = []
        for proxy in proxies:
            if proxy.get('working'):
                lines.append(f"{proxy['ip']}:{proxy['port']}")
        return "\n".join(lines)
    
    @staticmethod
    def format_foxyproxy(proxies: List[Dict]) -> str:
        """FoxyProxy格式输出"""
        config = {
            "whitePatterns": [],
            "blackPatterns": [],
            "proxySettings": []
        }
        
        for proxy in proxies:
            if proxy.get('working'):
                proxy_setting = {
                    "type": proxy['protocol'],
                    "host": proxy['ip'],
                    "port": int(proxy['port']),
                    "username": "",
                    "password": "",
                    "proxyDNS": True
                }
                config["proxySettings"].append(proxy_setting)
        
        return json.dumps(config, indent=2)
    
    @staticmethod
    def format_all(proxies: List[Dict], format_type: str = 'all') -> Dict[str, str]:
        """生成所有格式的输出"""
        results = {}
        
        # 按评分排序
        sorted_proxies = sorted(
            [p for p in proxies if p.get('working')], 
            key=lambda x: x.get('score', 0), 
            reverse=True
        )
        
        if format_type == 'all' or format_type == 'http':
            results['http.txt'] = OutputFormatter.format_http(sorted_proxies)
        
        if format_type == 'all' or format_type == 'socks5':
            results['socks5.txt'] = OutputFormatter.format_socks5(sorted_proxies)
        
        if format_type == 'all' or format_type == 'shadowsocks':
            results['shadowsocks.txt'] = OutputFormatter.format_shadowsocks(sorted_proxies)
        
        if format_type == 'all' or format_type == 'clash':
            results['clash.yaml'] = OutputFormatter.format_clash(sorted_proxies)
        
        if format_type == 'all' or format_type == 'v2ray':
            results['v2ray.txt'] = OutputFormatter.format_v2ray(sorted_proxies)
        
        if format_type == 'all' or format_type == 'proxifier':
            results['proxifier.txt'] = OutputFormatter.format_proxifier(sorted_proxies)
        
        if format_type == 'all' or format_type == 'burpsuite':
            results['burpsuite.txt'] = OutputFormatter.format_burpsuite(sorted_proxies)
        
        if format_type == 'all' or format_type == 'foxyproxy':
            results['foxyproxy.json'] = OutputFormatter.format_foxyproxy(sorted_proxies)
        
        # 生成汇总报告
        if sorted_proxies:
            report = [
                "=" * 60,
                f"代理抓取报告 - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "=" * 60,
                f"可用代理总数: {len(sorted_proxies)}",
                "",
                "最快10个代理:"
            ]
            
            for i, proxy in enumerate(sorted_proxies[:10], 1):
                report.append(
                    f"{i:2d}. {proxy['protocol']}://{proxy['ip']}:{proxy['port']} "
                    f"- {proxy.get('country', '未知')} "
                    f"- {proxy.get('speed_ms', 0)}ms "
                    f"- {proxy.get('score', 0)}分"
                )
            
            report.extend([
                "",
                "代理类型统计:",
                f"  HTTP/HTTPS: {len([p for p in sorted_proxies if p['protocol'] in ['http', 'https']])}",
                f"  SOCKS5: {len([p for p in sorted_proxies if p['protocol'] in ['socks', 'socks5']])}",
                "",
                "输出文件说明:",
                "  http.txt - HTTP/HTTPS代理列表",
                "  socks5.txt - SOCKS5代理列表",
                "  shadowsocks.txt - Shadowsocks订阅链接",
                "  clash.yaml - Clash配置文件",
                "  v2ray.txt - V2Ray订阅链接",
                "  proxifier.txt - Proxifier格式",
                "  burpsuite.txt - BurpSuite格式",
                "  foxyproxy.json - FoxyProxy格式",
                "=" * 60
            ])
            
            results['report.txt'] = "\n".join(report)
        
        return results
    
    @staticmethod
    def save_files(proxies: List[Dict], output_dir: str, format_type: str = 'all'):
        """保存所有格式的文件"""
        import os
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 生成当前时间戳
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 生成所有格式
        files = OutputFormatter.format_all(proxies, format_type)
        
        # 保存文件
        saved_files = []
        for filename, content in files.items():
            # 添加时间戳到文件名
            name, ext = os.path.splitext(filename)
            final_filename = f"{name}_{timestamp}{ext}"
            filepath = os.path.join(output_dir, final_filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            saved_files.append({
                'filename': final_filename,
                'path': filepath,
                'size': len(content)
            })
        
        return saved_files