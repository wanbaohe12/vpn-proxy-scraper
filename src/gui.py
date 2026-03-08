#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI界面模块 - 代理抓取工具图形界面
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import queue
import time
from datetime import datetime
import os
import sys

# 导入我们的模块
from .proxy_scraper import ProxyScraper
from .output_formatter import OutputFormatter


class ProxyScraperGUI:
    """代理抓取工具GUI"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("VPN代理抓取工具 v2.0")
        self.root.geometry("1000x700")
        
        # 设置图标（如果有）
        try:
            self.root.iconbitmap(default='resources/icon.ico')
        except:
            pass
        
        # 初始化变量
        self.scraper = None
        self.proxies = []
        self.working_proxies = []
        self.is_running = False
        self.progress_queue = queue.Queue()
        
        # 创建界面
        self.setup_ui()
        
        # 启动队列处理器
        self.root.after(100, self.process_queue)
    
    def setup_ui(self):
        """设置用户界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # 1. 控制面板
        control_frame = ttk.LabelFrame(main_frame, text="控制面板", padding="10")
        control_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 抓取设置
        ttk.Label(control_frame, text="超时时间(秒):").grid(row=0, column=0, padx=(0, 5))
        self.timeout_var = tk.StringVar(value="10")
        ttk.Entry(control_frame, textvariable=self.timeout_var, width=10).grid(row=0, column=1, padx=(0, 10))
        
        ttk.Label(control_frame, text="线程数:").grid(row=0, column=2, padx=(0, 5))
        self.workers_var = tk.StringVar(value="30")
        ttk.Entry(control_frame, textvariable=self.workers_var, width=10).grid(row=0, column=3, padx=(0, 10))
        
        ttk.Label(control_frame, text="抓取页数:").grid(row=0, column=4, padx=(0, 5))
        self.pages_var = tk.StringVar(value="3")
        ttk.Entry(control_frame, textvariable=self.pages_var, width=10).grid(row=0, column=5, padx=(0, 10))
        
        # 代理源选择
        ttk.Label(control_frame, text="代理源:").grid(row=1, column=0, pady=(10, 0), padx=(0, 5))
        
        self.source_vars = {}
        sources = [
            ("快代理", "kuaidaili", True),
            ("89IP", "89ip", True),
            ("IP3366", "ip3366", True),
            ("站大爷", "zdaye", True),
            ("国外代理", "foreign", False),
        ]
        
        for i, (name, key, default) in enumerate(sources):
            var = tk.BooleanVar(value=default)
            self.source_vars[key] = var
            ttk.Checkbutton(control_frame, text=name, variable=var).grid(
                row=1, column=1+i, pady=(10, 0), padx=(5, 5)
            )
        
        # 2. 按钮面板
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E))
        
        # 控制按钮
        self.start_btn = ttk.Button(button_frame, text="开始抓取", command=self.start_scraping, width=15)
        self.start_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_btn = ttk.Button(button_frame, text="停止", command=self.stop_scraping, width=15, state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=1, padx=(0, 10))
        
        self.test_btn = ttk.Button(button_frame, text="测试代理", command=self.test_proxies, width=15)
        self.test_btn.grid(row=0, column=2, padx=(0, 10))
        
        self.export_btn = ttk.Button(button_frame, text="导出代理", command=self.export_proxies, width=15)
        self.export_btn.grid(row=0, column=3, padx=(0, 10))
        
        self.clear_btn = ttk.Button(button_frame, text="清空列表", command=self.clear_list, width=15)
        self.clear_btn.grid(row=0, column=4)
        
        # 3. 进度和状态
        status_frame = ttk.LabelFrame(main_frame, text="进度状态", padding="10")
        status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 状态标签
        self.status_label = ttk.Label(status_frame, text="就绪")
        self.status_label.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E))
        
        # 统计信息
        stats_frame = ttk.Frame(status_frame)
        stats_frame.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Label(stats_frame, text="抓取总数:").grid(row=0, column=0, padx=(0, 5))
        self.total_label = ttk.Label(stats_frame, text="0", foreground="blue")
        self.total_label.grid(row=0, column=1, padx=(0, 20))
        
        ttk.Label(stats_frame, text="可用代理:").grid(row=0, column=2, padx=(0, 5))
        self.working_label = ttk.Label(stats_frame, text="0", foreground="green")
        self.working_label.grid(row=0, column=3, padx=(0, 20))
        
        ttk.Label(stats_frame, text="不可用:").grid(row=0, column=4, padx=(0, 5))
        self.failed_label = ttk.Label(stats_frame, text="0", foreground="red")
        self.failed_label.grid(row=0, column=5)
        
        # 4. 代理列表
        list_frame = ttk.LabelFrame(main_frame, text="代理列表", padding="10")
        list_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # 创建树状视图
        columns = ('#1', '#2', '#3', '#4', '#5', '#6', '#7', '#8', '#9')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # 定义列
        self.tree.heading('#1', text='IP地址')
        self.tree.heading('#2', text='端口')
        self.tree.heading('#3', text='协议')
        self.tree.heading('#4', text='类型')
        self.tree.heading('#5', text='国家')
        self.tree.heading('#6', text='速度(ms)')
        self.tree.heading('#7', text='匿名度')
        self.tree.heading('#8', text='评分')
        self.tree.heading('#9', text='来源')
        
        # 设置列宽
        self.tree.column('#1', width=120)
        self.tree.column('#2', width=60)
        self.tree.column('#3', width=70)
        self.tree.column('#4', width=80)
        self.tree.column('#5', width=80)
        self.tree.column('#6', width=80)
        self.tree.column('#7', width=80)
        self.tree.column('#8', width=60)
        self.tree.column('#9', width=100)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 网格布局
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 5. 日志输出
        log_frame = ttk.LabelFrame(main_frame, text="日志", padding="10")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 设置标签颜色
        self.tree.tag_configure('working', background='#e6ffe6')
        self.tree.tag_configure('failed', background='#ffe6e6')
    
    def log(self, message: str, level: str = "INFO"):
        """添加日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] [{level}] {message}\n"
        
        self.progress_queue.put(('log', formatted))
    
    def update_status(self, status: str):
        """更新状态"""
        self.progress_queue.put(('status', status))
    
    def update_stats(self, total: int, working: int, failed: int):
        """更新统计信息"""
        self.progress_queue.put(('stats', (total, working, failed)))
    
    def update_progress(self, current: int, total: int, working: int, failed: int, message: str = ""):
        """更新进度"""
        self.progress_queue.put(('progress', (current, total, working, failed, message)))
    
    def add_proxy_to_tree(self, proxy: Dict, is_working: bool = True):
        """添加代理到树状视图"""
        self.progress_queue.put(('add_proxy', (proxy, is_working)))
    
    def process_queue(self):
        """处理队列中的UI更新"""
        try:
            while True:
                item = self.progress_queue.get_nowait()
                item_type, data = item
                
                if item_type == 'log':
                    self.log_text.insert(tk.END, data)
                    self.log_text.see(tk.END)
                    
                elif item_type == 'status':
                    self.status_label.config(text=data)
                    
                elif item_type == 'stats':
                    total, working, failed = data
                    self.total_label.config(text=str(total))
                    self.working_label.config(text=str(working))
                    self.failed_label.config(text=str(failed))
                    
                elif item_type == 'progress':
                    current, total, working, failed, message = data
                    if total > 0:
                        progress = (current / total) * 100
                        self.progress_var.set(progress)
                    
                    # 更新统计
                    self.update_stats(total, working, failed)
                    
                    # 添加日志
                    if message:
                        self.log(message)
                        
                elif item_type == 'add_proxy':
                    proxy, is_working = data
                    
                    # 准备显示数据
                    values = (
                        proxy.get('ip', ''),
                        proxy.get('port', ''),
                        proxy.get('protocol', ''),
                        proxy.get('type', ''),
                        proxy.get('country', ''),
                        str(proxy.get('speed_ms', '')) if proxy.get('speed_ms') else '',
                        proxy.get('anonymity_checked', proxy.get('anonymity', '')),
                        str(proxy.get('score', 0)),
                        proxy.get('source', ''),
                    )
                    
                    # 插入到树中
                    tags = ('working',) if is_working else ('failed',)
                    self.tree.insert('', tk.END, values=values, tags=tags)
                    
        except queue.Empty:
            pass
        
        # 每100ms检查一次
        self.root.after(100, self.process_queue)
    
    def start_scraping(self):
        """开始抓取代理"""
        if self.is_running:
            return
        
        # 清空列表
        self.tree.delete(*self.tree.get_children())
        self.log_text.delete(1.0, tk.END)
        self.update_stats(0, 0, 0)
        
        # 获取设置
        try:
            timeout = int(self.timeout_var.get())
            max_workers = int(self.workers_var.get())
            pages = int(self.pages_var.get())
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
            return
        
        # 创建抓取器
        self.scraper = ProxyScraper(timeout=timeout, max_workers=max_workers)
        self.is_running = True
        
        # 更新按钮状态
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.test_btn.config(state=tk.DISABLED)
        self.export_btn.config(state=tk.DISABLED)
        
        # 在后台线程中运行
        thread = threading.Thread(target=self._scrape_thread)
        thread.daemon = True
        thread.start()
    
    def _scrape_thread(self):
        """抓取线程"""
        try:
            self.update_status("正在抓取代理...")
            self.log("开始从多个源抓取代理")
            
            # 抓取代理
            self.proxies = self.scraper.scrape_all_proxies()
            
            # 添加到树中
            for proxy in self.proxies:
                self.add_proxy_to_tree(proxy, is_working=False)
            
            self.update_stats(len(self.proxies), 0, 0)
            self.update_status(f"抓取完成，共 {len(self.proxies)} 个代理")
            self.log(f"抓取完成，共 {len(self.proxies)} 个代理")
            
        except Exception as e:
            self.log(f"抓取失败: {str(e)}", "ERROR")
            self.update_status("抓取失败")
        
        finally:
            self.is_running = False
            self.root.after(0, self._scraping_finished)
    
    def test_proxies(self):
        """测试代理"""
        if not self.proxies or self.is_running:
            return
        
        # 清空工作代理列表
        self.working_proxies = []
        
        # 更新按钮状态
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.test_btn.config(state=tk.DISABLED)
        self.export_btn.config(state=tk.DISABLED)
        
        # 在后台线程中运行
        thread = threading.Thread(target=self._test_thread)
        thread.daemon = True
        thread.start()
    
    def _test_thread(self):
        """测试线程"""
        try:
            self.update_status("正在测试代理...")
            self.log(f"开始测试 {len(self.proxies)} 个代理")
            
            # 定义进度回调
            def progress_callback(current, total, working, failed, message):
                self.update_progress(current, total, working, failed, message)
            
            # 测试代理
            working, failed = self.scraper.test_proxies_batch(
                self.proxies, 
                progress_callback=progress_callback
            )
            
            # 保存工作代理
            self.working_proxies = working
            
            # 清空并重新添加
            self.tree.delete(*self.tree.get_children())
            
            # 先添加可用的
            for proxy in working:
                self.add_proxy_to_tree(proxy, is_working=True)
            
            # 再添加不可用的
            for proxy in failed:
                self.add_proxy_to_tree(proxy, is_working=False)
            
            self.update_stats(len(self.proxies), len(working), len(failed))
            self.update_status(f"测试完成，可用 {len(working)} 个代理")
            self.log(f"测试完成，可用 {len(working)} 个代理，不可用 {len(failed)} 个")
            
        except Exception as e:
            self.log(f"测试失败: {str(e)}", "ERROR")
            self.update_status("测试失败")
        
        finally:
            self.is_running = False
            self.root.after(0, self._testing_finished)
    
    def _scraping_finished(self):
        """抓取完成"""
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.test_btn.config(state=tk.NORMAL)
        self.export_btn.config(state=tk.NORMAL if self.proxies else tk.DISABLED)
        
        if self.proxies:
            self.log("抓取完成，可以开始测试代理")
    
    def _testing_finished(self):
        """测试完成"""
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.test_btn.config(state=tk.NORMAL)
        self.export_btn.config(state=tk.NORMAL if self.working_proxies else tk.DISABLED)
        
        if self.working_proxies:
            self.log("测试完成，可以导出代理")
    
    def stop_scraping(self):
        """停止当前操作"""
        self.is_running = False
        self.update_status("已停止")
        self.log("操作已停止")
        
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.test_btn.config(state=tk.NORMAL if self.proxies else tk.DISABLED)
        self.export_btn.config(state=tk.NORMAL if self.working_proxies else tk.DISABLED)
    
    def export_proxies(self):
        """导出代理"""
        if not self.working_proxies:
            messagebox.showwarning("警告", "没有可用的代理可以导出")
            return
        
        # 创建导出对话框
        export_window = tk.Toplevel(self.root)
        export_window.title("导出代理")
        export_window.geometry("400x400")
        export_window.transient(self.root)
        export_window.grab_set()
        
        # 导出格式选择
        ttk.Label(export_window, text="选择导出格式:", font=('Arial', 10, 'bold')).pack(pady=(10, 5))
        
        format_var = tk.StringVar(value='all')
        formats = [
            ("所有格式", 'all'),
            ("HTTP/HTTPS代理", 'http'),
            ("SOCKS5代理", 'socks5'),
            ("Shadowsocks订阅", 'shadowsocks'),
            ("Clash配置文件", 'clash'),
            ("V2Ray订阅", 'v2ray'),
            ("Proxifier格式", 'proxifier'),
            ("BurpSuite格式", 'burpsuite'),
            ("FoxyProxy格式", 'foxyproxy'),
        ]
        
        for text, value in formats:
            ttk.Radiobutton(export_window, text=text, variable=format_var, value=value).pack(anchor=tk.W, padx=20)
        
        # 输出目录选择
        ttk.Label(export_window, text="输出目录:", font=('Arial', 10, 'bold')).pack(pady=(20, 5))
        
        dir_frame = ttk.Frame(export_window)
        dir_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        self.export_dir_var = tk.StringVar(value=os.path.join(os.getcwd(), 'output'))
        ttk.Entry(dir_frame, textvariable=self.export_dir_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        def browse_dir():
            directory = filedialog.askdirectory(initialdir=self.export_dir_var.get())
            if directory:
                self.export_dir_var.set(directory)
        
        ttk.Button(dir_frame, text="浏览", command=browse_dir, width=10).pack(side=tk.RIGHT, padx=(5, 0))
        
        # 导出按钮
        def do_export():
            format_type = format_var.get()
            output_dir = self.export_dir_var.get()
            
            if not output_dir:
                messagebox.showerror("错误", "请选择输出目录")
                return
            
            try:
                # 导出文件
                saved_files = OutputFormatter.save_files(
                    self.working_proxies, 
                    output_dir, 
                    format_type
                )
                
                # 显示导出结果
                result = f"导出完成！已保存 {len(saved_files)} 个文件:\n\n"
                for file_info in saved_files:
                    result += f"  • {file_info['filename']} ({file_info['size']} bytes)\n"
                
                messagebox.showinfo("导出成功", result)
                export_window.destroy()
                
                # 打开输出目录
                if messagebox.askyesno("打开目录", "是否打开输出目录？"):
                    os.startfile(output_dir)
                
            except Exception as e:
                messagebox.showerror("导出失败", f"导出时出错: {str(e)}")
        
        ttk.Button(export_window, text="导出", command=do_export, width=20).pack(pady=20)
        
        # 取消按钮
        ttk.Button(export_window, text="取消", command=export_window.destroy, width=20).pack(pady=(0, 20))
    
    def clear_list(self):
        """清空代理列表"""
        if messagebox.askyesno("确认", "确定要清空代理列表吗？"):
            self.tree.delete(*self.tree.get_children())
            self.proxies = []
            self.working_proxies = []
            self.update_stats(0, 0, 0)
            self.log("已清空代理列表")
    
    def run(self):
        """运行GUI"""
        self.root.mainloop()


def main():
    """主函数"""
    # 创建必要的目录
    os.makedirs('output', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    # 运行GUI
    app = ProxyScraperGUI()
    app.run()


if __name__ == '__main__':
    main()