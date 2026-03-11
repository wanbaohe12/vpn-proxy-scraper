@echo off
chcp 65001 >nul
title VPN代理抓取工具 - 打包脚本
echo ==========================================
echo   VPN代理抓取工具 - 一键打包为exe
echo ==========================================
echo.

:: 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

echo [1/3] 检查Python环境... OK
echo.

:: 检查依赖
echo [2/3] 检查并安装依赖...
python -m pip install -r requirements.txt -q
if errorlevel 1 (
    echo [警告] 依赖安装可能有问题，继续尝试打包...
) else (
    echo         依赖检查完成
echo.
)

:: 运行打包脚本
echo [3/3] 开始打包...
echo         这可能需要几分钟，请耐心等待...
echo.

python build.py

echo.
echo ==========================================
echo   打包流程结束
echo ==========================================
pause
