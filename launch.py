#!/usr/bin/env python3
"""
极简启动脚本
"""

import sys
import os

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 强制导入并运行
if __name__ == "__main__":
    try:
        from PyQt5.QtWidgets import QApplication
        print("PyQt5 OK")
        
        from ui.main_window import ProxyScraperGUI
        print("GUI imported")
        
        # 创建目录
        os.makedirs('output', exist_ok=True)
        os.makedirs('data', exist_ok=True)
        
        # 创建应用
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        
        # 创建窗口
        window = ProxyScraperGUI()
        window.show()
        
        print("Starting event loop...")
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")