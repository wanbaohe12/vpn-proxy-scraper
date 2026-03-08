@echo off
echo ========================================
echo 代理抓取工具 - EXE打包脚本
echo ========================================
echo.

REM 检查是否安装了PyInstaller
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [!] PyInstaller未安装
    echo [*] 正在安装PyInstaller...
    pip install pyinstaller
)

echo.
echo [*] 开始打包为EXE...
echo 这可能需要几分钟，请稍候...

REM 创建打包目录
if not exist "dist" mkdir dist
if not exist "build" mkdir build

REM 打包命令
pyinstaller --onefile ^
  --windowed ^
  --name "ProxyScraper" ^
  --icon "resources/icon.ico" ^
  --add-data "config;config" ^
  --add-data "resources;resources" ^
  --hidden-import PyQt5 ^
  --hidden-import PyQt5.QtCore ^
  --hidden-import PyQt5.QtGui ^
  --hidden-import PyQt5.QtWidgets ^
  --hidden-import bs4 ^
  --hidden-import lxml ^
  --hidden-import requests ^
  --clean ^
  main.py

if errorlevel 1 (
    echo [!] 打包失败
    pause
    exit /b 1
)

echo.
echo [✓] 打包完成！
echo.
echo EXE文件位置: dist\ProxyScraper.exe
echo.
echo 使用说明：
echo 1. 双击 dist\ProxyScraper.exe 运行
echo 2. 第一次运行可能会被安全软件警告，请选择允许
echo 3. 程序会在同级目录创建 output 文件夹存放结果
echo.
pause