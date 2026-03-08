#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包脚本 - 将VPN代理抓取工具打包为exe
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

def check_pyinstaller():
    """检查PyInstaller是否安装"""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False

def install_pyinstaller():
    """安装PyInstaller"""
    print("正在安装PyInstaller...")
    
    # 使用国内镜像
    mirror = "https://pypi.tuna.tsinghua.edu.cn/simple"
    
    cmd = [
        sys.executable, "-m", "pip", "install",
        "pyinstaller>=6.0.0",
        "-i", mirror, "--trusted-host", "pypi.tuna.tsinghua.edu.cn"
    ]
    
    try:
        subprocess.check_call(cmd)
        print("✓ PyInstaller安装成功")
        return True
    except subprocess.CalledProcessError:
        print("✗ PyInstaller安装失败")
        return False

def clean_build():
    """清理构建目录"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['main.spec']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"清理目录: {dir_name}")
            shutil.rmtree(dir_name)
    
    for file_name in files_to_clean:
        if os.path.exists(file_name):
            print(f"清理文件: {file_name}")
            os.remove(file_name)
    
    # 清理src目录中的__pycache__
    src_pycache = Path("src") / "__pycache__"
    if src_pycache.exists():
        print(f"清理目录: {src_pycache}")
        shutil.rmtree(src_pycache)

def build_exe():
    """构建exe文件"""
    print("开始构建exe文件...")
    
    # PyInstaller参数
    args = [
        'pyinstaller',
        '--name=VPN代理抓取工具',
        '--windowed',  # 不显示控制台窗口
        '--onefile',   # 打包成单个exe
        # '--icon=resources/icon.ico',  # 图标（如果有）
        '--add-data=src;src',  # 添加src目录
        '--add-data=README.md;.',  # 添加README
        '--add-data=requirements.txt;.',  # 添加requirements
        '--clean',  # 清理临时文件
        '--noconfirm',  # 替换输出目录时不需要确认
    ]
    
    # 添加隐藏导入（如果需要）
    hidden_imports = [
        'requests',
        'bs4',
        'lxml',
        'yaml',
        'queue',
        'concurrent.futures',
        'urllib3',
        'tkinter',
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtWidgets',
        'PyQt5.QtGui',
    ]
    
    for imp in hidden_imports:
        args.append(f'--hidden-import={imp}')
    
    # 添加排除模块（减少体积）
    excludes = [
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        # 'PyQt5',  # 保留，不排除
        'PySide2',
        'test',
        'unittest',
    ]
    
    for exc in excludes:
        args.append(f'--exclude-module={exc}')
    
    # 添加主文件
    args.append('main.py')
    
    # 执行构建
    print(f"执行命令: {' '.join(args)}")
    try:
        result = subprocess.run(args, check=True, capture_output=True, text=True)
        print("构建输出:")
        print(result.stdout)
        if result.stderr:
            print("构建错误:")
            print(result.stderr)
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"构建失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def create_resource_dirs():
    """创建资源目录"""
    os.makedirs('resources', exist_ok=True)
    os.makedirs('output', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    # 创建默认配置文件
    config_content = """# VPN代理抓取工具配置
timeout: 10
max_workers: 30
pages_per_source: 3

# 代理源配置
sources:
  kuaidaili: true
  89ip: true
  ip3366: true
  zdaye: true
  foreign: false

# 输出格式
output_formats:
  http: true
  socks5: true
  shadowsocks: true
  clash: true
  v2ray: true
  proxifier: true
  burpsuite: true
  foxyproxy: true
"""
    
    config_path = Path('config') / 'config.yaml'
    config_path.parent.mkdir(exist_ok=True)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    # 创建默认图标（如果没有）
    icon_path = Path('resources') / 'icon.ico'
    if not icon_path.exists():
        print(f"注意: 图标文件 {icon_path} 不存在")
        print("请将icon.ico文件放入resources目录以获得更好的视觉效果")

def check_dependencies():
    """检查所有依赖"""
    required = ['requests', 'bs4', 'lxml', 'yaml']
    missing = []
    
    for package in required:
        try:
            if package == 'bs4':
                __import__('bs4')
            elif package == 'yaml':
                __import__('yaml')
            else:
                __import__(package)
        except ImportError:
            missing.append(package)
    
    return missing

def install_dependencies():
    """安装所有依赖"""
    print("安装项目依赖...")
    
    mirror = "https://pypi.tuna.tsinghua.edu.cn/simple"
    
    cmd = [
        sys.executable, "-m", "pip", "install",
        "-r", "requirements.txt",
        "-i", mirror, "--trusted-host", "pypi.tuna.tsinghua.edu.cn"
    ]
    
    try:
        subprocess.check_call(cmd)
        print("✓ 依赖安装成功")
        return True
    except subprocess.CalledProcessError:
        print("✗ 依赖安装失败")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("VPN代理抓取工具 - 打包脚本")
    print("=" * 60)
    
    # 检查平台
    current_platform = platform.system()
    if current_platform != 'Windows':
        print(f"警告: 当前平台为 {current_platform}，建议在Windows上打包")
        print("继续打包可能会出现问题")
        choice = input("是否继续？(y/n): ")
        if choice.lower() != 'y':
            return
    
    # 1. 检查依赖
    missing = check_dependencies()
    if missing:
        print(f"缺少依赖: {', '.join(missing)}")
        choice = input("是否自动安装？(y/n): ")
        if choice.lower() == 'y':
            if not install_dependencies():
                print("依赖安装失败，无法继续打包")
                return
        else:
            print("请手动安装依赖: pip install -r requirements.txt")
            return
    
    # 2. 检查PyInstaller
    if not check_pyinstaller():
        print("PyInstaller未安装")
        choice = input("是否自动安装？(y/n): ")
        if choice.lower() == 'y':
            if not install_pyinstaller():
                print("PyInstaller安装失败，无法打包")
                return
        else:
            print("请手动安装: pip install pyinstaller")
            return
    
    # 3. 创建资源目录
    create_resource_dirs()
    
    # 4. 清理旧构建
    print("\n清理旧构建文件...")
    clean_build()
    
    # 5. 构建exe
    print("\n开始构建...")
    if build_exe():
        print("\n" + "=" * 60)
        print("构建成功！")
        print("=" * 60)
        
        # 显示构建结果
        dist_dir = Path("dist")
        if dist_dir.exists():
            exe_files = list(dist_dir.glob("*.exe"))
            if exe_files:
                exe_path = exe_files[0]
                print(f"生成的可执行文件: {exe_path}")
                print(f"文件大小: {exe_path.stat().st_size / (1024*1024):.2f} MB")
                
                # 复制到根目录
                target_path = Path("VPN代理抓取工具.exe")
                shutil.copy(exe_path, target_path)
                print(f"已复制到: {target_path}")
                
                print("\n使用说明:")
                print("1. 双击 'VPN代理抓取工具.exe' 运行程序")
                print("2. 程序会自动创建 output 目录保存结果")
                print("3. 界面操作: 抓取 -> 测试 -> 导出")
                
                # 打开目录
                choice = input("\n是否打开输出目录？(y/n): ")
                if choice.lower() == 'y':
                    os.startfile(dist_dir)
            else:
                print("未找到生成的exe文件")
        else:
            print("dist目录不存在，构建可能失败")
    else:
        print("\n构建失败！")
        print("请检查错误信息并重试")
    
    input("\n按回车键退出...")

if __name__ == '__main__':
    main()