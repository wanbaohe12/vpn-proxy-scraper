@echo off
echo ========================================
echo 代理抓取工具 - 安装脚本
echo ========================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [!] Python未安装
    echo 请从 https://www.python.org/downloads/ 下载并安装Python 3.7+
    echo 安装时请勾选"Add Python to PATH"
    pause
    exit /b 1
)

echo [✓] Python已安装

REM 升级pip
echo.
echo [*] 升级pip...
python -m pip install --upgrade pip

REM 安装依赖
echo.
echo [*] 安装依赖...
echo 这可能需要几分钟，请稍候...

python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

if errorlevel 1 (
    echo [!] 依赖安装失败，尝试使用备用源...
    python -m pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
)

if errorlevel 1 (
    echo [!] 依赖安装失败，请检查网络连接
    pause
    exit /b 1
)

echo.
echo [✓] 安装完成！
echo.
echo 使用方法：
echo 1. 运行GUI版本: python main.py
echo 2. 命令行版本: python -m src.proxy_manager
echo.
echo 打包为exe: 运行 build_exe.bat
echo.
pause