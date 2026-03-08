#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接运行GUI界面
"""

import sys
import os

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """运行GUI"""
    try:
        # 检查PyQt5
        try:
            from PyQt5.QtWidgets import QApplication
        except ImportError:
            print("错误: 未安装PyQt5")
            print("请运行: pip install pyqt5")
            input("按回车键退出...")
            return
        
        # 导入GUI
        from ui.main_window import ProxyScraperGUI
        
        print("启动代理抓取工具 GUI...")
        print("请稍候...")
        
        # 创建必要目录
        os.makedirs('output', exist_ok=True)
        os.makedirs('data', exist_ok=True)
        
        # 运行GUI
        app = ProxyScraperGUI()
        app.run()
        
    except Exception as e:
        print(f"启动失败: {e}")
        import traceback
        traceback.print_exc()
        input("按回车键退出...")

if __name__ == "__main__":
    main()