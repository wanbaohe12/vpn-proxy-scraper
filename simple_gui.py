#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最简单的GUI启动脚本
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

try:
    # 导入必要的模块
    from PyQt5.QtWidgets import QApplication
    from ui.main_window import ProxyScraperGUI
    
    print("正在启动代理抓取工具...")
    
    # 创建目录
    os.makedirs('output', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    # 运行GUI
    app = ProxyScraperGUI()
    app.run()
    
except ImportError as e:
    print(f"导入错误: {e}")
    print("\n请确保已安装所有依赖:")
    print("pip install -r requirements.txt")
    input("按回车键退出...")
except Exception as e:
    print(f"启动失败: {e}")
    traceback.print_exc()
    input("按回车键退出...")