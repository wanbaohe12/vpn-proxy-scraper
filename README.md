# VPN代理抓取工具 v2.0

一个功能强大的VPN/代理服务器抓取工具，带有图形界面，支持多种输出格式，可打包为单个exe文件。

## ✨ 功能特性

- ✅ **图形界面** - 直观易用的Tkinter GUI界面
- ✅ **多代理源** - 支持快代理、89IP、IP3366、站大爷等国内代理源
- ✅ **智能测试** - 多线程并发测试代理速度、可用性、匿名度
- ✅ **多种输出格式** - 支持Clash、Shadowsocks、V2Ray、HTTP/SOCKS5等格式
- ✅ **一键打包** - 支持打包为单个exe文件，无需安装Python
- ✅ **中文界面** - 完全中文化，解决编码问题

## 📦 支持的输出格式

| 格式 | 文件扩展名 | 适用软件 |
|------|------------|----------|
| HTTP/HTTPS代理 | `.txt` | 浏览器、Proxifier、BurpSuite |
| SOCKS5代理 | `.txt` | 支持SOCKS5的客户端 |
| Shadowsocks订阅 | `.txt` | Shadowsocks客户端 |
| Clash配置文件 | `.yaml` | Clash for Windows/Android |
| V2Ray订阅 | `.txt` | V2RayN、Qv2ray |
| Proxifier格式 | `.txt` | Proxifier |
| BurpSuite格式 | `.txt` | BurpSuite |
| FoxyProxy格式 | `.json` | FoxyProxy浏览器扩展 |

## 🚀 快速开始

### 方法1：直接运行Python脚本（需要Python环境）

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 运行程序
python main.py
```

### 方法2：打包为exe文件（推荐，无需Python）

```bash
# 1. 安装依赖和打包工具
pip install -r requirements.txt

# 2. 打包为exe
python build.py

# 3. 运行生成的exe文件
#    双击 "VPN代理抓取工具.exe"
```

## 🖥️ 图形界面使用指南

### 主界面说明

1. **控制面板** - 设置超时时间、线程数、选择代理源
2. **按钮面板** - 开始抓取、测试代理、导出结果、清空列表
3. **进度状态** - 显示当前进度和统计信息
4. **代理列表** - 显示抓取到的代理详情（可用代理绿色高亮）
5. **日志输出** - 显示详细的操作日志

### 使用流程

1. **第一步：抓取代理**
   - 设置合适的超时时间（建议10-15秒）
   - 选择要抓取的代理源（默认使用国内源）
   - 点击"开始抓取"按钮

2. **第二步：测试代理**
   - 抓取完成后，点击"测试代理"按钮
   - 程序会自动测试所有代理的可用性和速度
   - 可用代理会显示为绿色，不可用代理为红色

3. **第三步：导出结果**
   - 测试完成后，点击"导出代理"按钮
   - 选择输出格式（支持多种代理软件格式）
   - 选择输出目录，点击导出
   - 程序会自动生成对应格式的配置文件

## 🔧 项目结构

```
E:\ai\text\
├── main.py                 # 主程序入口
├── build.py                # 打包脚本
├── requirements.txt        # Python依赖
├── README.md               # 说明文档
├── src/                    # 源代码目录
│   ├── __init__.py
│   ├── proxy_scraper.py   # 代理抓取核心
│   ├── output_formatter.py # 输出格式化
│   └── gui.py             # 图形界面
├── config/                 # 配置文件目录
├── data/                   # 数据文件目录
├── output/                 # 输出文件目录（自动创建）
├── resources/              # 资源文件目录（图标等）
└── .vscode/               # VSCode配置（开发用）
```

## 📊 代理源说明

### 国内代理源（无需翻墙）

| 源名称 | 网址 | 类型 | 匿名度 | 稳定性 |
|--------|------|------|--------|--------|
| 快代理 | kuaidaili.com | HTTP/HTTPS/SOCKS5 | 高匿 | ⭐⭐⭐⭐ |
| 89IP | 89ip.cn | HTTP | 透明 | ⭐⭐⭐ |
| IP3366 | ip3366.net | HTTP/HTTPS | 高匿 | ⭐⭐⭐⭐ |
| 站大爷 | zdaye.com | HTTP | 高匿 | ⭐⭐⭐ |

### 国外代理源（需要科学上网）

> 注：国外代理源在代码中默认注释，如需使用请取消注释

| 源名称 | 网址 | 类型 | 匿名度 | 稳定性 |
|--------|------|------|--------|--------|
| Free Proxy List | free-proxy-list.net | HTTP/HTTPS | 多种 | ⭐⭐⭐ |
| SSL Proxies | sslproxies.org | HTTPS | 匿名 | ⭐⭐⭐⭐ |
| US Proxy | us-proxy.org | HTTP/HTTPS | 匿名 | ⭐⭐⭐⭐ |
| SOCKS Proxy | socks-proxy.net | SOCKS4/5 | 匿名 | ⭐⭐⭐ |

## 🛠️ 开发说明

### 环境要求

- Python 3.7 或更高版本
- Windows 7/10/11（Linux/Mac可能需要调整）

### 安装开发环境

```bash
# 克隆项目（如果有）
git clone <repository-url>

# 进入项目目录
cd vpn-proxy-scraper

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 添加新的代理源

1. 在 `src/proxy_scraper.py` 中添加新的解析方法
2. 方法名格式：`parse_<source_name>`
3. 返回代理字典列表，包含必要字段
4. 在 `scrape_all_proxies` 方法中添加新源到sources列表

### 添加新的输出格式

1. 在 `src/output_formatter.py` 中添加新的格式化方法
2. 方法名格式：`format_<format_name>`
3. 在 `format_all` 方法中添加新的格式支持

## ⚠️ 注意事项

1. **合法性** - 仅用于学习和研究目的，请遵守当地法律法规
2. **稳定性** - 免费代理质量参差不齐，可用率通常不高
3. **安全性** - 免费代理可能记录流量，请勿用于敏感操作
4. **更新频率** - 代理源网站可能更新页面结构，需要定期维护
5. **网络环境** - 某些代理源可能需要科学上网才能访问

## 🔄 更新日志

### v2.0 (2026-03-01)
- ✅ 全新图形界面（Tkinter）
- ✅ 支持多种代理软件输出格式
- ✅ 一键打包为exe功能
- ✅ 多线程并发测试
- ✅ 智能评分系统
- ✅ 中文界面，解决编码问题

### v1.0 (早期版本)
- 命令行界面
- 基础代理抓取功能
- 简单的HTTP输出格式

## 📝 常见问题

### Q1: 代理测试全部失败？
- 检查网络连接是否正常
- 增加超时时间（建议15-20秒）
- 尝试更换代理源

### Q2: 打包后的exe文件很大？
- PyInstaller打包会包含Python解释器和所有依赖
- 使用UPX压缩可以减小体积（需单独安装UPX）
- 排除不必要的模块可以减小体积

### Q3: 界面显示乱码？
- 程序已内置UTF-8编码支持
- 确保系统区域设置为中文
- 在VSCode中运行可避免乱码问题

### Q4: 某些代理源无法访问？
- 国内代理源应该可以直接访问
- 国外代理源可能需要科学上网
- 可以修改代码使用其他代理源

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开Pull Request

## 📄 许可证

本项目仅供学习和研究使用。使用本工具产生的任何后果由使用者自行承担。

---

**温馨提示**: 代理工具的使用应符合法律法规，尊重网络秩序，保护个人隐私安全。