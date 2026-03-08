#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VPN代理抓取工具 - 主程序入口
图形界面版本，支持多种输出格式
"""

import sys
import os
import traceback

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def check_dependencies():
    """检查依赖是否安装"""
    # 包名到导入名的映射
    package_map = {
        'requests': 'requests',
        'beautifulsoup4': 'bs4',  # beautifulsoup4的导入名是bs4
        'lxml': 'lxml',
        'PyYAML': 'yaml',  # PyYAML的导入名是yaml
    }
    
    missing = []
    
    for package, import_name in package_map.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(package)
    
    return missing

def install_dependencies():
    """安装依赖"""
    import subprocess
    import sys
    
    print("正在安装依赖...")
    
    # 使用国内镜像源加速
    mirror = "https://pypi.tuna.tsinghua.edu.cn/simple"
    
    requirements = [
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0", 
        "lxml>=4.9.0",
        "PyYAML>=6.0",
        "tkinter"  # tkinter通常是Python内置的
    ]
    
    for req in requirements:
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                req, "-i", mirror, "--trusted-host", "pypi.tuna.tsinghua.edu.cn"
            ])
            print(f"✓ 已安装: {req}")
        except subprocess.CalledProcessError:
            print(f"✗ 安装失败: {req}")
    
    print("依赖安装完成！")

def run_gui():
    """运行GUI主程序"""
    try:
        # 导入GUI模块 - 修正导入路径
        from ui.main_window import ProxyScraperGUI
        from PyQt5.QtWidgets import QApplication
        
        print("启动图形界面...")
        print("提示：")
        print("1. 点击'开始抓取'从多个源获取代理")
        print("2. 点击'测试代理'验证代理可用性")
        print("3. 点击'导出代理'生成各种格式配置文件")
        print("=" * 60)
        
        # 创建必要的目录
        os.makedirs('output', exist_ok=True)
        os.makedirs('data', exist_ok=True)
        
        # 创建QApplication实例
        app = QApplication(sys.argv)
        
        # 创建并显示GUI
        gui = ProxyScraperGUI()
        gui.show()
        
        # 启动事件循环
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"启动失败: {e}")
        traceback.print_exc()
        input("按回车键退出...")

def main():
    """主函数"""
    print("=" * 60)
    print("VPN代理抓取工具 v2.0")
    print("=" * 60)
    
    # 检查依赖
    missing = check_dependencies()
    if missing:
        print(f"缺少依赖: {', '.join(missing)}")
        print("正在自动安装依赖...")
        install_dependencies()
        
        # 重新检查
        missing = check_dependencies()
        if missing:
            print(f"安装后仍缺少依赖: {', '.join(missing)}")
            print("请手动安装: pip install -r requirements.txt")
            print("程序将在5秒后退出...")
            import time
            time.sleep(5)
            return
        
        print("依赖安装完成，重新启动程序...")
        # 重新导入模块并运行
        return run_gui()
    
    run_gui()

if __name__ == '__main__':
    main()