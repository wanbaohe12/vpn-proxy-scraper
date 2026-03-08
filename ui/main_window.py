#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口 - PyQt5 GUI界面
"""

import sys
import os
import time
import threading
import queue
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QProgressBar, QTabWidget,
    QGroupBox, QCheckBox, QComboBox, QSpinBox, QFileDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QSplitter, QFrame, QScrollArea, QGridLayout, QDialog,
    QDialogButtonBox, QTextBrowser, QPlainTextEdit
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QObject
from PyQt5.QtGui import QFont, QColor, QIcon, QTextCursor

# 导入核心模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from proxy_manager import ProxyManager


class WorkerSignals(QObject):
    """工作线程信号"""
    progress = pyqtSignal(int, int, int, int, str)  # 当前, 总数, 成功, 失败, 消息
    finished = pyqtSignal(dict)  # 完成信号
    error = pyqtSignal(str)  # 错误信号


class WorkerThread(QThread):
    """工作线程"""
    
    def __init__(self, manager, test_proxies=True):
        super().__init__()
        self.manager = manager
        self.test_proxies = test_proxies
        self.signals = WorkerSignals()
    
    def run(self):
        try:
            result = self.manager.run_full_process(
                test_proxies=self.test_proxies,
                progress_callback=self._progress_callback
            )
            self.signals.finished.emit(result)
        except Exception as e:
            self.signals.error.emit(str(e))
    
    def _progress_callback(self, current, total, success, failed, msg):
        self.signals.progress.emit(current, total, success, failed, msg)


class ProxyScraperGUI(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.manager = ProxyManager()
        self.worker_thread = None
        self.current_result = None
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle('代理抓取工具 v1.0')
        self.setGeometry(100, 100, 1200, 800)
        
        # 设置图标
        self.setWindowIcon(QIcon(self.get_icon_path()))
        
        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 顶部控制面板
        top_panel = self.create_top_panel()
        main_layout.addWidget(top_panel)
        
        # 分割器
        splitter = QSplitter(Qt.Vertical)
        
        # 状态面板
        status_panel = self.create_status_panel()
        splitter.addWidget(status_panel)
        
        # 结果面板
        result_panel = self.create_result_panel()
        splitter.addWidget(result_panel)
        
        # 日志面板
        log_panel = self.create_log_panel()
        splitter.addWidget(log_panel)
        
        splitter.setSizes([200, 400, 200])
        main_layout.addWidget(splitter)
        
        # 底部状态栏
        self.statusBar().showMessage('就绪')
    
    def create_top_panel(self):
        """创建顶部控制面板"""
        panel = QWidget()
        layout = QHBoxLayout(panel)
        
        # 标题
        title = QLabel('🧬 代理抓取工具')
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        layout.addStretch()
        
        # 设置按钮
        self.settings_btn = QPushButton('⚙️ 设置')
        self.settings_btn.clicked.connect(self.show_settings)
        layout.addWidget(self.settings_btn)
        
        return panel
    
    def create_status_panel(self):
        """创建状态面板"""
        panel = QGroupBox('📊 状态信息')
        layout = QVBoxLayout()
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)
        
        # 状态标签
        status_grid = QGridLayout()
        
        # 代理统计
        self.total_label = QLabel('总代理: 0')
        self.working_label = QLabel('可用代理: 0')
        self.failed_label = QLabel('失败代理: 0')
        
        status_grid.addWidget(QLabel('📦'), 0, 0)
        status_grid.addWidget(self.total_label, 0, 1)
        status_grid.addWidget(QLabel('✅'), 1, 0)
        status_grid.addWidget(self.working_label, 1, 1)
        status_grid.addWidget(QLabel('❌'), 2, 0)
        status_grid.addWidget(self.failed_label, 2, 1)
        
        # 速度信息
        self.speed_label = QLabel('速度: -')
        self.avg_speed_label = QLabel('平均速度: -')
        
        status_grid.addWidget(QLabel('⚡'), 3, 0)
        status_grid.addWidget(self.speed_label, 3, 1)
        status_grid.addWidget(QLabel('📈'), 4, 0)
        status_grid.addWidget(self.avg_speed_label, 4, 1)
        
        layout.addLayout(status_grid)
        
        # 控制按钮
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton('🚀 开始抓取')
        self.start_btn.clicked.connect(self.start_scraping)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        button_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton('⏹️ 停止')
        self.stop_btn.clicked.connect(self.stop_scraping)
        self.stop_btn.setEnabled(False)
        button_layout.addWidget(self.stop_btn)
        
        self.export_btn = QPushButton('💾 导出结果')
        self.export_btn.clicked.connect(self.export_results)
        self.export_btn.setEnabled(False)
        button_layout.addWidget(self.export_btn)
        
        self.subscription_btn = QPushButton('🔗 订阅链接')
        self.subscription_btn.clicked.connect(self.show_subscription_links)
        self.subscription_btn.setEnabled(False)
        self.subscription_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        button_layout.addWidget(self.subscription_btn)
        
        layout.addLayout(button_layout)
        
        panel.setLayout(layout)
        return panel
    
    def create_result_panel(self):
        """创建结果面板"""
        panel = QTabWidget()
        
        # 代理列表标签页
        proxy_tab = QWidget()
        proxy_layout = QVBoxLayout(proxy_tab)
        
        # 代理表格
        self.proxy_table = QTableWidget()
        self.proxy_table.setColumnCount(8)
        self.proxy_table.setHorizontalHeaderLabels([
            'IP地址', '端口', '协议', '国家', '速度(ms)', '匿名度', '来源', '评分'
        ])
        self.proxy_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.proxy_table.setAlternatingRowColors(True)
        proxy_layout.addWidget(self.proxy_table)
        
        panel.addTab(proxy_tab, '📋 代理列表')
        
        # 快速代理标签页
        quick_tab = QWidget()
        quick_layout = QVBoxLayout(quick_tab)
        
        self.quick_text = QTextEdit()
        self.quick_text.setReadOnly(True)
        self.quick_text.setFont(QFont('Consolas', 10))
        quick_layout.addWidget(self.quick_text)
        
        panel.addTab(quick_tab, '🚀 快速代理')
        
        # 格式预览标签页
        format_tab = QWidget()
        format_layout = QVBoxLayout(format_tab)
        
        format_selector = QHBoxLayout()
        format_selector.addWidget(QLabel('输出格式:'))
        
        self.format_combo = QComboBox()
        self.format_combo.addItems([
            'HTTP/HTTPS列表',
            'SOCKS5列表', 
            'Clash配置',
            'Shadowsocks订阅',
            'JSON格式'
        ])
        self.format_combo.currentTextChanged.connect(self.update_format_preview)
        format_selector.addWidget(self.format_combo)
        format_selector.addStretch()
        
        format_layout.addLayout(format_selector)
        
        self.format_preview = QTextEdit()
        self.format_preview.setReadOnly(True)
        self.format_preview.setFont(QFont('Consolas', 9))
        format_layout.addWidget(self.format_preview)
        
        panel.addTab(format_tab, '📄 格式预览')
        
        return panel
    
    def create_log_panel(self):
        """创建日志面板"""
        panel = QGroupBox('📝 运行日志')
        layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont('Consolas', 9))
        self.log_text.setMaximumHeight(200)
        
        layout.addWidget(self.log_text)
        panel.setLayout(layout)
        return panel
    
    def get_icon_path(self):
        """获取图标路径"""
        # 暂时返回空，可以在resources中放置图标
        return ""
    
    # ==================== 事件处理 ====================
    
    def start_scraping(self):
        """开始抓取"""
        if self.worker_thread and self.worker_thread.isRunning():
            return
        
        # 重置界面
        self.reset_ui()
        
        # 创建工作线程
        self.worker_thread = WorkerThread(self.manager, test_proxies=True)
        self.worker_thread.signals.progress.connect(self.update_progress)
        self.worker_thread.signals.finished.connect(self.on_finished)
        self.worker_thread.signals.error.connect(self.on_error)
        
        # 更新按钮状态
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.export_btn.setEnabled(False)
        self.subscription_btn.setEnabled(False)
        
        # 开始
        self.log_message("开始抓取代理...")
        self.worker_thread.start()
    
    def stop_scraping(self):
        """停止抓取"""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.terminate()
            self.worker_thread.wait()
            self.log_message("已停止")
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
    
    def on_finished(self, result):
        """任务完成"""
        self.current_result = result
        self.update_results(result)
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.export_btn.setEnabled(True)
        self.subscription_btn.setEnabled(True)
        
        self.log_message(f"完成! 抓取到 {result['total_scraped']} 个代理，其中 {result['total_working']} 个可用")
        self.statusBar().showMessage(f"完成 - 可用代理: {result['total_working']} 个")
    
    def on_error(self, error_msg):
        """发生错误"""
        QMessageBox.critical(self, "错误", f"发生错误:\n{error_msg}")
        self.log_message(f"错误: {error_msg}")
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
    
    def update_progress(self, current, total, success, failed, msg):
        """更新进度"""
        if total > 0:
            progress = int(current / total * 100)
            self.progress_bar.setValue(progress)
        
        self.working_label.setText(f"可用代理: {success}")
        self.failed_label.setText(f"失败代理: {failed}")
        
        if msg:
            self.log_message(msg)
    
    def update_results(self, result):
        """更新结果"""
        # 更新统计
        self.total_label.setText(f"总代理: {result['total_scraped']}")
        self.working_label.setText(f"可用代理: {result['total_working']}")
        self.failed_label.setText(f"失败代理: {result['total_failed']}")
        
        # 更新表格
        self.update_proxy_table(result['working_proxies'])
        
        # 更新快速代理
        self.update_quick_proxies(result['working_proxies'])
        
        # 更新格式预览
        self.update_format_preview()
    
    def update_proxy_table(self, proxies):
        """更新代理表格"""
        self.proxy_table.setRowCount(len(proxies))
        
        for i, proxy in enumerate(proxies):
            # IP地址
            ip_item = QTableWidgetItem(proxy['ip'])
            ip_item.setFlags(ip_item.flags() & ~Qt.ItemIsEditable)
            
            # 端口
            port_item = QTableWidgetItem(str(proxy['port']))
            port_item.setFlags(port_item.flags() & ~Qt.ItemIsEditable)
            
            # 协议
            protocol_item = QTableWidgetItem(proxy['protocol'].upper())
            protocol_item.setFlags(protocol_item.flags() & ~Qt.ItemIsEditable)
            
            # 国家
            country_item = QTableWidgetItem(proxy.get('country', '未知'))
            country_item.setFlags(country_item.flags() & ~Qt.ItemIsEditable)
            
            # 速度
            speed = proxy.get('response_time', 0)
            speed_item = QTableWidgetItem(f"{speed:.0f}" if speed else "未知")
            speed_item.setFlags(speed_item.flags() & ~Qt.ItemIsEditable)
            
            # 根据速度设置颜色
            if speed < 1000:
                speed_item.setForeground(QColor(0, 150, 0))  # 绿色
            elif speed < 3000:
                speed_item.setForeground(QColor(200, 150, 0))  # 橙色
            else:
                speed_item.setForeground(QColor(200, 0, 0))  # 红色
            
            # 匿名度
            anonymity_item = QTableWidgetItem(proxy.get('anonymity', '未知'))
            anonymity_item.setFlags(anonymity_item.flags() & ~Qt.ItemIsEditable)
            
            # 来源
            source_item = QTableWidgetItem(proxy.get('source', '未知'))
            source_item.setFlags(source_item.flags() & ~Qt.ItemIsEditable)
            
            # 评分
            score = proxy.get('score', 0)
            score_item = QTableWidgetItem(str(score))
            score_item.setFlags(score_item.flags() & ~Qt.ItemIsEditable)
            
            # 设置行
            self.proxy_table.setItem(i, 0, ip_item)
            self.proxy_table.setItem(i, 1, port_item)
            self.proxy_table.setItem(i, 2, protocol_item)
            self.proxy_table.setItem(i, 3, country_item)
            self.proxy_table.setItem(i, 4, speed_item)
            self.proxy_table.setItem(i, 5, anonymity_item)
            self.proxy_table.setItem(i, 6, source_item)
            self.proxy_table.setItem(i, 7, score_item)
        
        self.proxy_table.resizeColumnsToContents()
    
    def update_quick_proxies(self, proxies):
        """更新快速代理"""
        text = []
        
        # 最快的10个HTTP代理
        http_proxies = [p for p in proxies if p['protocol'] in ['http', 'https']]
        http_proxies.sort(key=lambda x: x.get('response_time', 9999))
        
        if http_proxies:
            text.append("最快的HTTP/HTTPS代理:")
            for i, proxy in enumerate(http_proxies[:10], 1):
                text.append(f"{i:2d}. {proxy['protocol']}://{proxy['ip']}:{proxy['port']}")
            text.append("")
        
        # 最快的10个SOCKS5代理
        socks_proxies = [p for p in proxies if p['protocol'] in ['socks5', 'socks4']]
        socks_proxies.sort(key=lambda x: x.get('response_time', 9999))
        
        if socks_proxies:
            text.append("最快的SOCKS5代理:")
            for i, proxy in enumerate(socks_proxies[:10], 1):
                text.append(f"{i:2d}. {proxy['protocol']}://{proxy['ip']}:{proxy['port']}")
            text.append("")
        
        # 使用说明
        text.append("使用说明:")
        text.append("1. 复制上面的链接到代理软件")
        text.append("2. HTTP/HTTPS代理支持大多数浏览器")
        text.append("3. SOCKS5代理支持更多应用程序")
        text.append("4. 推荐使用Clash等代理客户端管理")
        
        self.quick_text.setText("\n".join(text))
    
    def update_format_preview(self):
        """更新格式预览"""
        if not self.current_result or not self.current_result['working_proxies']:
            self.format_preview.setText("暂无数据")
            return
        
        proxies = self.current_result['working_proxies']
        format_type = self.format_combo.currentText()
        
        if format_type == 'HTTP/HTTPS列表':
            text = self.manager.format_simple_list(proxies)
        elif format_type == 'SOCKS5列表':
            text = self.manager.format_simple_list([p for p in proxies if p['protocol'] in ['socks5', 'socks4']])
        elif format_type == 'Clash配置':
            text = self.manager.format_for_clash(proxies)
        elif format_type == 'Shadowsocks订阅':
            text = self.manager.format_for_shadowsocks(proxies)
        elif format_type == 'JSON格式':
            text = self.manager.format_json(proxies)
        else:
            text = ""
        
        self.format_preview.setText(text)
    
    def export_results(self):
        """导出结果"""
        if not self.current_result or not self.current_result['working_proxies']:
            QMessageBox.warning(self, "警告", "没有可导出的数据")
            return
        
        # 选择目录
        dir_path = QFileDialog.getExistingDirectory(self, "选择导出目录", "output")
        if not dir_path:
            return
        
        try:
            saved_files = self.manager.export_proxies(
                self.current_result['working_proxies'],
                dir_path
            )
            
            # 显示结果
            msg = f"导出完成！生成的文件:\n\n"
            for filename, filepath in saved_files.items():
                msg += f"• {filename}\n"
            
            QMessageBox.information(self, "导出成功", msg)
            self.log_message(f"结果已导出到: {dir_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"导出时发生错误:\n{str(e)}")
            self.log_message(f"导出失败: {e}")
    
    def show_settings(self):
        """显示设置对话框"""
        # 简化的设置对话框
        from PyQt5.QtWidgets import QDialog, QFormLayout
        
        dialog = QDialog(self)
        dialog.setWindowTitle("设置")
        dialog.resize(400, 300)
        
        layout = QFormLayout()
        
        # 超时时间
        timeout_spin = QSpinBox()
        timeout_spin.setRange(5, 60)
        timeout_spin.setValue(self.manager.timeout)
        timeout_spin.valueChanged.connect(lambda v: setattr(self.manager, 'timeout', v))
        layout.addRow("超时时间(秒):", timeout_spin)
        
        # 最大线程数
        workers_spin = QSpinBox()
        workers_spin.setRange(10, 100)
        workers_spin.setValue(self.manager.max_workers)
        workers_spin.valueChanged.connect(lambda v: setattr(self.manager, 'max_workers', v))
        layout.addRow("最大线程数:", workers_spin)
        
        # 代理源选择
        sources_group = QGroupBox("代理源")
        sources_layout = QVBoxLayout()
        
        self.kuaidaili_cb = QCheckBox("快代理 (kuaidaili.com)")
        self.kuaidaili_cb.setChecked(True)
        sources_layout.addWidget(self.kuaidaili_cb)
        
        self.ip89_cb = QCheckBox("89IP (89ip.cn)")
        self.ip89_cb.setChecked(True)
        sources_layout.addWidget(self.ip89_cb)
        
        self.ip3366_cb = QCheckBox("IP3366 (ip3366.net)")
        self.ip3366_cb.setChecked(True)
        sources_layout.addWidget(self.ip3366_cb)
        
        self.proxylist_cb = QCheckBox("Proxy-List (proxy-list.download)")
        self.proxylist_cb.setChecked(True)
        sources_layout.addWidget(self.proxylist_cb)
        
        self.geonode_cb = QCheckBox("Geonode (geonode.com)")
        self.geonode_cb.setChecked(True)
        sources_layout.addWidget(self.geonode_cb)
        
        sources_group.setLayout(sources_layout)
        layout.addRow(sources_group)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def reset_ui(self):
        """重置界面"""
        self.progress_bar.setValue(0)
        self.total_label.setText("总代理: 0")
        self.working_label.setText("可用代理: 0")
        self.failed_label.setText("失败代理: 0")
        self.speed_label.setText("速度: -")
        self.avg_speed_label.setText("平均速度: -")
        
        self.proxy_table.setRowCount(0)
        self.quick_text.clear()
        self.format_preview.clear()
        self.log_text.clear()
        
        self.current_result = None
    
    def show_subscription_links(self):
        """显示订阅链接对话框"""
        if not self.current_result or 'working_proxies' not in self.current_result:
            QMessageBox.warning(self, "警告", "没有可用的代理数据，请先抓取代理。")
            return
        
        proxies = self.current_result['working_proxies']
        
        if not proxies:
            QMessageBox.warning(self, "警告", "没有可用的代理，无法生成订阅链接。")
            return
        
        # 生成订阅链接
        subscription_links = self.manager.generate_subscription_links(proxies)
        
        # 创建对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("订阅链接")
        dialog.setMinimumSize(800, 600)
        
        layout = QVBoxLayout()
        
        # 创建选项卡
        tabs = QTabWidget()
        
        # Shadowsocks选项卡
        ss_tab = QWidget()
        ss_layout = QVBoxLayout()
        
        ss_info = QLabel("Shadowsocks订阅链接（可直接复制到支持SS的客户端）：")
        ss_layout.addWidget(ss_info)
        
        ss_links = subscription_links['shadowsocks']
        
        # 原始SS链接
        ss_raw_label = QLabel("原始SS链接（每行一个）：")
        ss_layout.addWidget(ss_raw_label)
        
        ss_raw_text = QPlainTextEdit()
        ss_raw_text.setPlainText("\n".join(ss_links['raw_links']))
        ss_raw_text.setReadOnly(True)
        ss_layout.addWidget(ss_raw_text)
        
        # Base64编码
        ss_base64_label = QLabel("Base64编码（作为订阅链接使用）：")
        ss_layout.addWidget(ss_base64_label)
        
        ss_base64_text = QPlainTextEdit()
        ss_base64_text.setPlainText(ss_links['base64_encoded'])
        ss_base64_text.setReadOnly(True)
        ss_layout.addWidget(ss_base64_text)
        
        # Data URL
        ss_data_label = QLabel("Data URL（可直接粘贴到浏览器或客户端）：")
        ss_layout.addWidget(ss_data_label)
        
        ss_data_text = QPlainTextEdit()
        ss_data_text.setPlainText(ss_links['data_url'])
        ss_data_text.setReadOnly(True)
        ss_layout.addWidget(ss_data_text)
        
        ss_tab.setLayout(ss_layout)
        tabs.addTab(ss_tab, "Shadowsocks")
        
        # Clash选项卡
        clash_tab = QWidget()
        clash_layout = QVBoxLayout()
        
        clash_info = QLabel("Clash配置文件（可直接导入Clash客户端）：")
        clash_layout.addWidget(clash_info)
        
        clash_links = subscription_links['clash']
        
        # YAML内容
        clash_yaml_label = QLabel("YAML配置：")
        clash_layout.addWidget(clash_yaml_label)
        
        clash_yaml_text = QPlainTextEdit()
        clash_yaml_text.setPlainText(clash_links['yaml_content'])
        clash_yaml_text.setReadOnly(True)
        clash_layout.addWidget(clash_yaml_text)
        
        # Base64编码
        clash_base64_label = QLabel("Base64编码（作为订阅链接使用）：")
        clash_layout.addWidget(clash_base64_label)
        
        clash_base64_text = QPlainTextEdit()
        clash_base64_text.setPlainText(clash_links['base64_encoded'])
        clash_base64_text.setReadOnly(True)
        clash_layout.addWidget(clash_base64_text)
        
        clash_tab.setLayout(clash_layout)
        tabs.addTab(clash_tab, "Clash")
        
        # 简单列表选项卡
        simple_tab = QWidget()
        simple_layout = QVBoxLayout()
        
        simple_info = QLabel("简单代理列表（可直接复制使用）：")
        simple_layout.addWidget(simple_info)
        
        simple_links = subscription_links['simple_list']
        
        # HTTP列表
        http_label = QLabel("HTTP/HTTPS代理：")
        simple_layout.addWidget(http_label)
        
        http_text = QPlainTextEdit()
        http_text.setPlainText(simple_links['http_list'])
        http_text.setReadOnly(True)
        simple_layout.addWidget(http_text)
        
        # SOCKS5列表
        socks5_label = QLabel("SOCKS5代理：")
        simple_layout.addWidget(socks5_label)
        
        socks5_text = QPlainTextEdit()
        socks5_text.setPlainText(simple_links['socks5_list'])
        socks5_text.setReadOnly(True)
        simple_layout.addWidget(socks5_text)
        
        # 所有代理列表
        all_label = QLabel("所有代理：")
        simple_layout.addWidget(all_label)
        
        all_text = QPlainTextEdit()
        all_text.setPlainText(simple_links['all_list'])
        all_text.setReadOnly(True)
        simple_layout.addWidget(all_text)
        
        simple_tab.setLayout(simple_layout)
        tabs.addTab(simple_tab, "简单列表")
        
        layout.addWidget(tabs)
        
        # 按钮
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(dialog.accept)
        layout.addWidget(buttons)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def log_message(self, message):
        """添加日志消息"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        
        # 自动滚动到底部
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_text.setTextCursor(cursor)
    
    def run(self):
        """运行应用"""
        try:
            print("正在启动GUI...")
            
            # 创建QApplication
            app = QApplication.instance()
            if not app:
                app = QApplication(sys.argv)
                print("创建新的QApplication实例")
            else:
                print("使用现有的QApplication实例")
            
            # 显示窗口
            self.show()
            print(f"窗口已显示，标题: {self.windowTitle()}")
            print(f"窗口尺寸: {self.width()}x{self.height()}")
            
            # 启动事件循环
            print("启动事件循环...")
            sys.exit(app.exec_())
            
        except Exception as e:
            print(f"GUI启动失败: {e}")
            import traceback
            traceback.print_exc()
            input("按回车键退出...")


if __name__ == "__main__":
    # 直接运行测试
    gui = ProxyScraperGUI()
    gui.run()