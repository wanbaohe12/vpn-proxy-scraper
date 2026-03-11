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
        'beautifulsoup4': 'bs4',
        'lxml': 'lxml',
        'PyYAML': 'yaml',
        'PyQt5': 'PyQt5.QtWidgets',
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
        "PyQt5>=5.15.0",
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

def setup_directories():
    """创建必要的目录"""
    dirs = ['output', 'data', 'config', 'logs']
    for d in dirs:
        os.makedirs(d, exist_ok=True)

def run_gui():
    """运行GUI主程序"""
    try:
        # 导入GUI模块
        from ui.main_window import ProxyScraperGUI
        from PyQt5.QtWidgets import QApplication
        from config_manager import get_config
        
        print("启动图形界面...")
        print("提示：")
        print("1. 点击'开始抓取'从多个源获取代理")
        print("2. 点击'测试代理'验证代理可用性")
        print("3. 点击'导出代理'生成各种格式配置文件")
        print("=" * 60)
        
        # 创建必要的目录
        setup_directories()
        
        # 加载配置
        config = get_config()
        print(f"配置加载完成: {config.config_file}")
        
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

def run_cli():
    """运行命令行版本"""
    from proxy_manager import ProxyManager
    from config_manager import get_config
    import json
    
    print("=" * 60)
    print("VPN代理抓取工具 - 命令行模式")
    print("=" * 60)
    
    # 加载配置
    config = get_config()
    
    # 创建管理器
    timeout = config.get_timeout()
    max_workers = config.get_max_workers()
    
    print(f"超时时间: {timeout}s")
    print(f"最大线程数: {max_workers}")
    print("-" * 60)
    
    manager = ProxyManager(timeout=timeout, max_workers=max_workers)
    
    # 运行完整流程
    def progress_callback(current, total, success, failed, msg):
        if total > 0:
            percent = int(current / total * 100)
            print(f"\r[{percent:3d}%] {msg[:50]}", end='', flush=True)
    
    result = manager.run_full_process(test_proxies=True, progress_callback=progress_callback)
    print()  # 换行
    
    print("-" * 60)
    print(f"抓取完成!")
    print(f"  总代理数: {result['total_scraped']}")
    print(f"  可用代理: {result['total_working']}")
    print(f"  失败代理: {result['total_failed']}")
    
    if result['working_proxies']:
        # 导出结果
        saved_files = manager.export_proxies(result['working_proxies'])
        print("-" * 60)
        print("生成的文件:")
        for filename, filepath in saved_files.items():
            print(f"  • {filename}")
    
    print("=" * 60)

def main():
    """主函数"""
    print("=" * 60)
    print("VPN代理抓取工具 v2.1")
    print("=" * 60)
    
    # 检查命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == '--cli':
        # 命令行模式
        missing = check_dependencies()
        if missing:
            print(f"缺少依赖: {', '.join(missing)}")
            print("请运行: pip install -r requirements.txt")
            return
        
        setup_directories()
        run_cli()
    else:
        # GUI模式
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
        
        run_gui()

if __name__ == '__main__':
    main()
