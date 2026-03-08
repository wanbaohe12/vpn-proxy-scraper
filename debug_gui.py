#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试GUI导入
"""

import sys
import os
import traceback

def check_imports():
    """检查所有导入"""
    print("=" * 60)
    print("检查导入...")
    print("=" * 60)
    
    modules = ['PyQt5', 'requests', 'bs4', 'yaml', 'lxml']
    
    for module in modules:
        try:
            if module == 'bs4':
                __import__('bs4')
            elif module == 'yaml':
                __import__('yaml')
            else:
                __import__(module)
            print(f"[OK] {module}")
        except ImportError as e:
            print(f"[FAIL] {module}: {e}")
            return False
    
    print("\n" + "=" * 60)
    print("检查核心模块...")
    print("=" * 60)
    
    # 检查proxy_manager
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        from proxy_manager import ProxyManager
        print("✓ proxy_manager")
    except Exception as e:
        print(f"✗ proxy_manager: {e}")
        traceback.print_exc()
        return False
    
    # 检查main_window
    try:
        from ui.main_window import ProxyScraperGUI
        print("✓ main_window")
    except Exception as e:
        print(f"✗ main_window: {e}")
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("所有导入检查通过！")
    print("=" * 60)
    return True

if __name__ == "__main__":
    if check_imports():
        print("\n尝试启动GUI...")
        try:
            from ui.main_window import ProxyScraperGUI
            app = ProxyScraperGUI()
            print("GUI创建成功，开始运行...")
            app.run()
        except Exception as e:
            print(f"启动失败: {e}")
            traceback.print_exc()
            input("按回车键退出...")
    else:
        input("按回车键退出...")