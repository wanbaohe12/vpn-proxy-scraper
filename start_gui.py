#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动代理抓取工具GUI - 修复版本
"""

import sys
import os
import traceback

# 设置编码
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def check_deps():
    """检查依赖"""
    deps = ['PyQt5', 'requests', 'bs4', 'yaml', 'lxml']
    missing = []
    
    for dep in deps:
        try:
            if dep == 'bs4':
                __import__('bs4')
            elif dep == 'yaml':
                __import__('yaml')
            else:
                __import__(dep)
        except ImportError:
            missing.append(dep)
    
    return missing

def main():
    """主函数"""
    print("=" * 60)
    print("代理抓取工具 v1.0")
    print("=" * 60)
    
    # 检查依赖
    missing = check_deps()
    if missing:
        print(f"缺少依赖: {', '.join(missing)}")
        print("\n请运行以下命令安装依赖:")
        print("pip install -r requirements.txt")
        print("\n或逐个安装:")
        for dep in missing:
            print(f"pip install {dep}")
        input("\n按回车键退出...")
        return
    
    try:
        # 导入GUI
        from ui.main_window import ProxyScraperGUI
        
        print("正在启动图形界面...")
        print("请稍候...")
        
        # 创建目录
        os.makedirs('output', exist_ok=True)
        os.makedirs('data', exist_ok=True)
        
        # 运行GUI
        app = ProxyScraperGUI()
        app.run()
        
    except Exception as e:
        print(f"启动失败: {e}")
        traceback.print_exc()
        input("按回车键退出...")

if __name__ == "__main__":
    main()