import tkinter as tk
from tkinter import ttk, messagebox
import threading
import os
import time
import socket
import json
import webbrowser
from datetime import datetime
import re

# Import local modules
from qqwry_parser import QQWry
import ip_service

class IPGetApp:
    def __init__(self, root, lang=None):
        self.root = root
        
        # Language state
        self.current_lang = "zh"
        if lang:
            self.current_lang = lang
        else:
            self.load_config()

        # Localization data
        self.lang_data = {
            "zh": {
                "window_title": "IP 归属地查询工具",
                "title_label": "IP 归属地查询工具",
                "subtitle_label": "本地 & 免费 API 实时对比",
                "author": " 作者：",
                "help_btn": "❓ 帮助说明",
                "lbl_local_ip": "局域网 IPv4:",
                "lbl_public_ip": "公网 IPv4:",
                "lbl_local_ipv6": "局域网 IPv6:",
                "lbl_public_ipv6": "公网 IPv6:",
                "btn_refresh": "刷新本机 IP",
                "btn_refresh_loading": "获取中...",
                "lbl_query_ip": "查询 IP 地址:",
                "btn_query": "查询归属地",
                "btn_query_loading": "查询中...",
                "lbl_local_title": "本地数据库查询结果 (qqwry.dat)",
                "lbl_net_title": "网络 API 查询结果 (免费 API)",
                "no_data": "暂无数据",
                "compare_matching": "比对中...",
                "compare_matching_desc": "正在从本地数据库与网络 API 检索数据...",
                "compare_missing_db": "缺数据库",
                "compare_missing_db_desc": "本地数据库未加载，无法与网络位置比对。",
                "compare_insufficient": "信息不足",
                "compare_insufficient_desc": "数据缺失或网络查询异常，无法精确比对结果。",
                "compare_consistent": "结果一致",
                "compare_consistent_desc": "本地解析与网络 API 归属地高度吻合！",
                "compare_discrepancy": "存在差异",
                "compare_discrepancy_desc": "检测到本地数据库与网络 API 归属地不一致！",
                "lbl_db": "本地数据库状态:",
                "db_loading": "正在检测...",
                "db_loaded": "已加载 ({version})",
                "db_corrupted": "数据库已损坏",
                "db_not_installed": "数据库未安装",
                "db_downloading": "正在下载...",
                "db_download_speed": "下载中: {dl_mb:.1f}/{total_mb:.1f} MB",
                "db_loaded_old": "已装载旧版",
                "db_install_failed": "安装失败",
                "btn_db_action": "下载/更新数据库",
                "btn_db_cancel": "取消下载",
                "console_lbl": "系统日志控制台",
                "help_title": "帮助与说明",
                "help_header": "❓ 软件说明与隐私申明",
                "help_close": "我知道了",
                "help_text": (
                    "【软件作用】\n"
                    "本软件是一款极简的内网穿透与网络诊断 GUI 客户端。集成 Localtunnel、Serveo 和 Pinggy.io 穿透服务，帮助开发者一键将本地端口（如 Web 服务、API 服务）映射至公网进行临时调试。同时，内置的双栈 IP 检测与地理位置比对工具支持 IPv4/IPv6，可用于排查网络联通性及本地服务健康状态。\n\n"
                    "【隐私申明】\n"
                    "1. 纯本地运行：本软件为完全开源、本地运行的客户端工具。我们不会收集、储存或上传您的任何个人隐私数据（包括您的真实 IP 地址、穿透流量、本地服务端口等）。\n"
                    "2. 第三方查询：本机公网 IP 查询及归属地检索使用公开的第三方 API 镜像接口，相关查询请求由您的计算机直接向服务商发起，我们不设 any 中转服务器，数据仅在本地前端临时渲染展示。\n"
                    "3. 隧道传输安全：内网穿透服务直接连接到各服务商的公网代理服务器，您的流量完全在您与穿透服务商之间传输，建议不要在公开的隧道中传输敏感/未加密的生产环境数据。\n\n"
                    "【免责申明】\n"
                    "请确保使用本软件进行合法的开发与测试工作。严禁将本软件用于任何形式的非法目的。因使用本工具（及第三方隧道）所产生的一切法律纠纷与安全责任，均由使用者本人独立承担，本软件作者不承担任何连带赔偿与法律责任。\n\n"
                    "作者主页：https://hik.win"
                ),
                "toast_copied": "复制成功!",
                "log_sys_start": "系统启动中...",
                "log_reading_db": "正在读取本地 IP 数据库: {path} ...",
                "log_db_ok": "IP 数据库加载成功! 版本: {version}",
                "log_db_err": "解析本地数据库失败: {e}",
                "log_db_missing": "本地 IP 数据库 (qqwry.dat) 不存在，请下载。",
                "log_detect_ip": "正在检测本机网络接口...",
                "log_local_ipv4_ok": "获取局域网 IPv4 成功: {ip}",
                "log_pub_ipv4_ok": "获取公网 IPv4 成功: {ip}",
                "log_pub_ipv4_err": "获取公网 IPv4 失败，请检查网络连接",
                "log_local_ipv6_ok": "获取局域网 IPv6 成功: {ip}",
                "log_local_ipv6_err": "未检测到局域网 IPv6 地址",
                "log_pub_ipv6_ok": "获取公网 IPv6 成功: {ip}",
                "log_pub_ipv6_err": "未检测到公网 IPv6 地址",
                "log_query_ip": "开始查询 IP 归属地: {ip}",
                "local_ipv6_not_supported": "本地数据库只支持 IPv4 查询",
                "local_not_found": "本地数据库未收录该 IP",
                "local_query_err": "本地查询异常: {e}",
                "net_query_err": "网络查询异常: {e}",
                "local_query_res": "本地查询结果: {res}",
                "net_query_res": "网络查询结果: {res}",
                "db_unloaded": "本地数据库未加载",
                "log_db_download_start": "开始下载/更新本地归属地数据库...",
                "log_db_download_ok": "本地数据库下载完毕！重新加载数据...",
                "log_db_download_cancel": "下载被取消或失败。",
                "log_db_download_err": "下载 IP 数据库异常: {e}",
                "msg_notice": "提示",
                "msg_input_ip": "请输入要查询的 IP 地址。",
                "msg_error": "错误",
                "msg_invalid_ip": "请输入有效的 IPv4 或 IPv6 地址格式。",
                "msg_download_fail": "下载失败",
                "msg_download_fail_desc": "数据库下载失败:\n{e}",
                "unknown_location": "未知网络归属地",
                "copied_label": "已复制{label_name}到剪贴板: {val}",
                "copy_failed": "复制失败: {e}"
            },
            "en": {
                "window_title": "IP Geolocation Query Tool",
                "title_label": "IP Geolocation Query Tool",
                "subtitle_label": "Local & Free API Comparison",
                "author": " Author: ",
                "help_btn": "❓ Help & Info",
                "lbl_local_ip": "Local IPv4:",
                "lbl_public_ip": "Public IPv4:",
                "lbl_local_ipv6": "Local IPv6:",
                "lbl_public_ipv6": "Public IPv6:",
                "btn_refresh": "Refresh IPs",
                "btn_refresh_loading": "Retrieving...",
                "lbl_query_ip": "Query IP Address:",
                "btn_query": "Query Geolocation",
                "btn_query_loading": "Querying...",
                "lbl_local_title": "Local Database Results (qqwry.dat)",
                "lbl_net_title": "Network API Results (Free API)",
                "no_data": "No Data",
                "compare_matching": "Comparing...",
                "compare_matching_desc": "Retrieving data from database and API...",
                "compare_missing_db": "Missing DB",
                "compare_missing_db_desc": "Local database is not loaded. Cannot compare.",
                "compare_insufficient": "Insufficient Info",
                "compare_insufficient_desc": "Missing data or query exception. Cannot compare.",
                "compare_consistent": "Consistent",
                "compare_consistent_desc": "Local resolution matches Network API!",
                "compare_discrepancy": "Discrepancy",
                "compare_discrepancy_desc": "Database and Network API geolocations do not match!",
                "lbl_db": "Local DB Status:",
                "db_loading": "Detecting...",
                "db_loaded": "Loaded ({version})",
                "db_corrupted": "DB Corrupted",
                "db_not_installed": "DB Not Installed",
                "db_downloading": "Downloading...",
                "db_download_speed": "Downloading: {dl_mb:.1f}/{total_mb:.1f} MB",
                "db_loaded_old": "Loaded Old Version",
                "db_install_failed": "Install Failed",
                "btn_db_action": "Download/Update DB",
                "btn_db_cancel": "Cancel Download",
                "console_lbl": "System Log Console",
                "help_title": "Help & Instructions",
                "help_header": "❓ Instructions & Privacy Policy",
                "help_close": "Close",
                "help_text": (
                    "【Software Purpose】\n"
                    "This software is an ultra-simple intranet penetration and network diagnostics GUI client. It integrates Localtunnel, Serveo, and Pinggy.io to map local ports (web services, APIs) to public URLs. It also includes dual-stack IPv4/IPv6 detection and geolocation comparisons to help troubleshoot network connectivity.\n\n"
                    "【Privacy Policy】\n"
                    "1. Run Locally: This software is open-source and runs entirely on your local machine. We do not collect, store, or upload any personal data (including IP addresses, tunnel traffic, or local ports).\n"
                    "2. Geolocation Query: Public IP and geolocation lookups use public mirror APIs. These requests are sent directly from your computer to the API provider. We do not use any intermediary servers.\n"
                    "3. Tunnel Security: Traffic is sent directly between your machine and the penetration service provider's servers. Avoid transmitting sensitive/unencrypted production data over public tunnels.\n\n"
                    "【Disclaimer】\n"
                    "Please ensure legal usage of this tool for development/testing only. Illegal uses are strictly prohibited. The user assumes full liability for any legal or security issues arising from using this tool. The author assumes no joint liability.\n\n"
                    "Author Homepage: https://hik.win"
                ),
                "toast_copied": "Copied!",
                "log_sys_start": "System starting...",
                "log_reading_db": "Reading local IP database: {path} ...",
                "log_db_ok": "IP database loaded successfully! Version: {version}",
                "log_db_err": "Failed to parse local database: {e}",
                "log_db_missing": "Local IP database (qqwry.dat) does not exist. Please download.",
                "log_detect_ip": "Detecting local network interfaces...",
                "log_local_ipv4_ok": "Successfully obtained local IPv4: {ip}",
                "log_pub_ipv4_ok": "Successfully obtained public IPv4: {ip}",
                "log_pub_ipv4_err": "Failed to obtain public IPv4. Please check network.",
                "log_local_ipv6_ok": "Successfully obtained local IPv6: {ip}",
                "log_local_ipv6_err": "Local IPv6 address not detected.",
                "log_pub_ipv6_ok": "Successfully obtained public IPv6: {ip}",
                "log_pub_ipv6_err": "Public IPv6 address not detected.",
                "log_query_ip": "Querying IP geolocation: {ip}",
                "local_ipv6_not_supported": "Local DB only supports IPv4 query",
                "local_not_found": "IP not found in local DB",
                "local_query_err": "Local query exception: {e}",
                "net_query_err": "Network query exception: {e}",
                "local_query_res": "Local query result: {res}",
                "net_query_res": "Network query result: {res}",
                "db_unloaded": "Local database not loaded",
                "log_db_download_start": "Starting to download/update local database...",
                "log_db_download_ok": "Local database downloaded successfully! Reloading...",
                "log_db_download_cancel": "Download cancelled or failed.",
                "log_db_download_err": "Exception downloading IP database: {e}",
                "msg_notice": "Notice",
                "msg_input_ip": "Please enter an IP address to query.",
                "msg_error": "Error",
                "msg_invalid_ip": "Please enter a valid IPv4 or IPv6 address format.",
                "msg_download_fail": "Download Failed",
                "msg_download_fail_desc": "Database download failed:\n{e}",
                "unknown_location": "Unknown Location",
                "copied_label": "Copied {label_name} to clipboard: {val}",
                "copy_failed": "Copy failed: {e}"
            }
        }

        # App state
        import sys
        self.exe_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
        self.persistent_db_path = os.path.join(self.exe_dir, "qqwry.dat")
        self.db_path = self.persistent_db_path
        if getattr(sys, 'frozen', False):
            bundled_path = os.path.join(sys._MEIPASS, "qqwry.dat")
            if not os.path.exists(self.persistent_db_path) and os.path.exists(bundled_path):
                self.db_path = bundled_path
        self.parser = None
        self.public_ip = None
        self.local_ip = None
        self.public_ipv6 = None
        self.local_ipv6 = None
        self.download_cancelled = threading.Event()
        self.active_threads = []

        # Color system
        self.colors = {
            "bg": "#1e1e2e",
            "card": "#252538",
            "border": "#313244",
            "text": "#cdd6f4",
            "text_muted": "#a6adc8",
            "accent": "#89b4fa",       # Blue
            "accent_hover": "#b4befe", # Light Blue
            "success": "#a6e3a1",      # Green
            "warning": "#f9e2af",      # Yellow
            "danger": "#f38ba8",       # Red
            "input_bg": "#181825"
        }

        # Initialize UI Styles
        self.setup_styles()
        
        # Build UI layout
        self.build_ui()
        
        # Set values in language combobox
        self.lang_var.set("English" if self.current_lang == "en" else "中文")
        
        # Apply texts based on current language
        self.update_ui_text()
        
        # Try loading database
        self.load_database()
        
        # Initial IP fetch
        self.log(self.get_text("log_sys_start"))
        self.refresh_ips()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def get_text(self, key, **kwargs):
        """Retrieve localized string."""
        text = self.lang_data[self.current_lang].get(key, "")
        if kwargs:
            return text.format(**kwargs)
        return text

    def get_config_path(self):
        import sys
        if getattr(sys, 'frozen', False):
            exe_dir = os.path.dirname(sys.executable)
        else:
            exe_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(exe_dir, "config.json")

    def load_config(self):
        """Load configuration settings."""
        config_path = self.get_config_path()
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.current_lang = config.get("lang", "zh")
                    if self.current_lang not in ["zh", "en"]:
                        self.current_lang = "zh"
                    return
            except Exception:
                pass
        self.current_lang = "zh"

    def save_config(self):
        """Save settings to config.json, preserving other keys."""
        config_path = self.get_config_path()
        config = {}
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except Exception:
                pass
        try:
            config["lang"] = self.current_lang
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except Exception:
            pass

    def on_language_change(self):
        """Handle manual language selection in the lookup GUI."""
        selected = self.lang_var.get()
        if selected == "English":
            self.current_lang = "en"
        else:
            self.current_lang = "zh"
        self.update_ui_text()
        self.save_config()

    def update_ui_text(self):
        """Update all text values in UI to match current language."""
        self.root.title(self.get_text("window_title"))
        self.title_label.config(text=self.get_text("title_label"))
        self.subtitle_label.config(text=self.get_text("subtitle_label"))
        self.author_lbl.config(text=self.get_text("author"))
        self.btn_help.config(text=self.get_text("help_btn"))
        
        self.lbl_local_ip.config(text=self.get_text("lbl_local_ip"))
        self.lbl_public_ip.config(text=self.get_text("lbl_public_ip"))
        self.lbl_local_ipv6.config(text=self.get_text("lbl_local_ipv6"))
        self.lbl_public_ipv6.config(text=self.get_text("lbl_public_ipv6"))
        
        # Refresh button text
        ref_text = self.btn_refresh.cget("text")
        if ref_text in ["获取中...", "Retrieving..."]:
            self.btn_refresh.config(text=self.get_text("btn_refresh_loading"))
        else:
            self.btn_refresh.config(text=self.get_text("btn_refresh"))
            
        self.search_lbl.config(text=self.get_text("lbl_query_ip"))
        self.btn_query.config(text=self.get_text("btn_query"))
        self.lbl_local_title.config(text=self.get_text("lbl_local_title"))
        self.lbl_net_title.config(text=self.get_text("lbl_net_title"))
        
        # Detail Boxes
        loc_val = self.val_local_loc.cget("text")
        if loc_val in ["暂无数据", "No Data"]:
            self.val_local_loc.config(text=self.get_text("no_data"))
        elif loc_val in ["查询中...", "Querying..."]:
            self.val_local_loc.config(text=self.get_text("btn_query_loading"))
            
        net_val = self.val_net_loc.cget("text")
        if net_val in ["暂无数据", "No Data"]:
            self.val_net_loc.config(text=self.get_text("no_data"))
        elif net_val in ["查询中...", "Querying..."]:
            self.val_net_loc.config(text=self.get_text("btn_query_loading"))
            
        # Comparison banner
        badge_text = self.compare_badge.cget("text")
        if badge_text in ["待检测", "Pending"]:
            self.compare_badge.config(text="Pending" if self.current_lang == 'en' else "待检测")
            self.compare_desc.config(text=self.get_text("msg_input_ip"))
        elif badge_text in ["比对中...", "Comparing..."]:
            self.compare_badge.config(text=self.get_text("compare_matching"))
            self.compare_desc.config(text=self.get_text("compare_matching_desc"))
        elif badge_text in ["缺数据库", "Missing DB"]:
            self.compare_badge.config(text=self.get_text("compare_missing_db"))
            self.compare_desc.config(text=self.get_text("compare_missing_db_desc"))
        elif badge_text in ["信息不足", "Insufficient Info"]:
            self.compare_badge.config(text=self.get_text("compare_insufficient"))
            self.compare_desc.config(text=self.get_text("compare_insufficient_desc"))
        elif badge_text in ["结果一致", "Consistent"]:
            self.compare_badge.config(text=self.get_text("compare_consistent"))
            self.compare_desc.config(text=self.get_text("compare_consistent_desc"))
        elif badge_text in ["存在差异", "Discrepancy"]:
            self.compare_badge.config(text=self.get_text("compare_discrepancy"))
            self.compare_desc.config(text=self.get_text("compare_discrepancy_desc"))
            
        self.lbl_db.config(text=self.get_text("lbl_db"))
        
        # DB status value text
        db_text = self.db_status_val.cget("text")
        if db_text in ["正在检测...", "Detecting..."]:
            self.db_status_val.config(text=self.get_text("db_loading"))
        elif "已加载" in db_text or "Loaded" in db_text:
            if self.parser:
                v = self.parser.get_version()
                self.db_status_val.config(text=self.get_text("db_loaded", version=v))
        elif db_text in ["数据库已损坏", "DB Corrupted"]:
            self.db_status_val.config(text=self.get_text("db_corrupted"))
        elif db_text in ["数据库未安装", "DB Not Installed"]:
            self.db_status_val.config(text=self.get_text("db_not_installed"))
        elif db_text in ["已装载旧版", "Loaded Old Version"]:
            self.db_status_val.config(text=self.get_text("db_loaded_old"))
        elif db_text in ["安装失败", "Install Failed"]:
            self.db_status_val.config(text=self.get_text("db_install_failed"))
            
        # DB download action button text
        db_act_text = self.btn_db_action.cget("text")
        if db_act_text in ["下载/更新数据库", "Download/Update DB"]:
            self.btn_db_action.config(text=self.get_text("btn_db_action"))
        elif db_act_text in ["取消下载", "Cancel Download"]:
            self.btn_db_action.config(text=self.get_text("btn_db_cancel"))
            
        self.console_lbl.config(text=self.get_text("console_lbl"))

    def on_closing(self):
        """Clean up resources and destroy the window."""
        self.download_cancelled.set()
        self.root.destroy()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('default')
        style.configure(".", background=self.colors["bg"], foreground=self.colors["text"])
        
        # Progress bar styling
        style.configure("Custom.Horizontal.TProgressbar",
                        troughcolor=self.colors["input_bg"],
                        background=self.colors["accent"],
                        thickness=15,
                        borderwidth=0)

    def log(self, message):
        """Append log message to the UI console."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] {message}\n"
        
        def do_log():
            try:
                if self.root and self.root.winfo_exists():
                    self.console.config(state="normal")
                    self.console.insert(tk.END, formatted)
                    self.console.see(tk.END)
                    self.console.config(state="disabled")
            except Exception:
                pass
            
        self.root.after(0, do_log)

    def set_entry_text(self, entry_widget, text, color=None):
        """Update a readonly entry widget's text and optional foreground color."""
        try:
            if self.root and self.root.winfo_exists():
                entry_widget.config(state="normal")
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, text)
                entry_widget.config(state="readonly")
                if color:
                    entry_widget.config(fg=color)
        except Exception:
            pass

    def setup_ip_entry(self, widget, label_name="IP"):
        """Configure an IP entry widget to be selectable, have a right-click copy menu, and support double-click copy."""
        try:
            fg_color = widget.cget("fg")
        except Exception:
            fg_color = self.colors["text"]

        widget.config(
            bg=self.colors["input_bg"],
            fg=fg_color,
            readonlybackground=self.colors["input_bg"],
            bd=0,
            relief="flat",
            highlightthickness=1,
            highlightbackground=self.colors["border"],
            highlightcolor=self.colors["border"]
        )

        def on_focus(event):
            widget.select_range(0, tk.END)
            widget.icursor(tk.END)
        widget.bind("<FocusIn>", on_focus)

        def flash_feedback():
            orig_bg = self.colors["input_bg"]
            orig_border = self.colors["border"]
            widget.config(
                readonlybackground=self.colors["success"],
                highlightbackground=self.colors["success"]
            )
            def revert():
                try:
                    if widget.winfo_exists():
                        widget.config(
                            readonlybackground=orig_bg,
                            highlightbackground=orig_border
                        )
                except Exception:
                    pass
            widget.after(400, revert)

        def show_toast(text="Copied!"):
            # Destroy active toast if exists
            if hasattr(widget, "active_toast") and widget.active_toast:
                try:
                    widget.active_toast.destroy()
                except Exception:
                    pass

            toast = tk.Label(
                widget.master,
                text=text,
                font=("Segoe UI", 8, "bold"),
                bg=self.colors["success"],
                fg="#11111b",
                padx=6,
                pady=1,
                bd=0,
                relief="flat"
            )
            # Position: 8 pixels to the right of the Entry widget
            toast.place(in_=widget, relx=1.0, rely=0.5, anchor=tk.W, x=8)
            widget.active_toast = toast

            def destroy_toast():
                try:
                    if toast.winfo_exists():
                        toast.destroy()
                    if hasattr(widget, "active_toast") and widget.active_toast == toast:
                        widget.active_toast = None
                except Exception:
                    pass

            widget.after(2000, destroy_toast)

        def do_copy():
            try:
                val = widget.get().strip()
                if val and val not in ["正在获取...", "获取中...", "未分配 / 禁用", "获取失败 (离线)", 
                                       "Retrieving...", "Failed (Offline)", "Not Assigned / Disabled"]:
                    self.root.clipboard_clear()
                    self.root.clipboard_append(val)
                    self.log(self.get_text("copied_label", label_name=label_name, val=val))
                    flash_feedback()
                    show_toast(self.get_text("toast_copied"))
            except Exception as e:
                self.log(self.get_text("copy_failed", e=e))

        def on_double_click(event):
            widget.select_range(0, tk.END)
            do_copy()
            return "break"
        widget.bind("<Double-Button-1>", on_double_click)

        def show_context_menu(event):
            menu = tk.Menu(widget, tearoff=0, bg=self.colors["card"], fg=self.colors["text"],
                           activebackground=self.colors["accent"], activeforeground="#11111b", bd=1, relief="solid")
            
            has_selection = False
            try:
                has_selection = widget.selection_present()
            except Exception:
                pass
                
            if has_selection:
                menu.add_command(label="复制选中 (Copy Selected)", command=lambda: widget.event_generate("<<Copy>>"))
            
            menu.add_command(label="复制全部 (Copy All)", command=do_copy)
            menu.add_command(label="全选 (Select All)", command=lambda: widget.select_range(0, tk.END))
            
            menu.post(event.x_root, event.y_root)
            return "break"

        widget.bind("<Button-3>", show_context_menu)

    def show_help_dialog(self):
        """Show a customized modal help and privacy dialog."""
        dialog = tk.Toplevel(self.root)
        dialog.title(self.get_text("help_title"))
        dialog.geometry("520x460")
        dialog.resizable(False, False)
        dialog.configure(bg=self.colors["bg"])
        
        dialog.transient(self.root)
        dialog.grab_set()
        
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_w = self.root.winfo_width()
        root_h = self.root.winfo_height()
        x = root_x + (root_w - 520) // 2
        y = root_y + (root_h - 460) // 2
        dialog.geometry(f"+{x}+{y}")

        main_frame = tk.Frame(dialog, bg=self.colors["bg"], padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        lbl_title = tk.Label(main_frame, text=self.get_text("help_header"), font=("Segoe UI", 12, "bold"),
                             bg=self.colors["bg"], fg=self.colors["accent"])
        lbl_title.pack(anchor=tk.W, pady=(0, 15))
        
        # Scrollable or fixed content box
        content_box = tk.Text(main_frame, bg=self.colors["input_bg"], fg=self.colors["text"],
                              bd=0, highlightthickness=1, highlightbackground=self.colors["border"],
                              font=("Segoe UI", 9), wrap=tk.WORD, padx=10, pady=10)
        content_box.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        content_box.insert(tk.END, self.get_text("help_text"))
        content_box.config(state="disabled")
        
        # Close Button
        btn_close = tk.Button(main_frame, text=self.get_text("help_close"), 
                              bg=self.colors["accent"], fg="#11111b",
                              activebackground=self.colors["accent_hover"], activeforeground="#11111b",
                              bd=0, relief="flat", padx=20, pady=6, 
                              font=("Segoe UI", 9, "bold"), cursor="hand2",
                              command=dialog.destroy)
        btn_close.pack(anchor=tk.CENTER)

    def load_database(self):
        """Load the QQWry parser in a background thread."""
        def worker():
            if os.path.exists(self.db_path):
                try:
                    self.log(self.get_text("log_reading_db", path=self.db_path))
                    self.parser = QQWry(self.db_path)
                    version = self.parser.get_version()
                    self.log(self.get_text("log_db_ok", version=version))
                    
                    self.root.after(0, lambda: self.db_status_val.config(
                        text=self.get_text("db_loaded", version=version), fg=self.colors["success"]
                    ))
                except Exception as e:
                    self.log(self.get_text("log_db_err", e=e))
                    self.root.after(0, lambda: self.db_status_val.config(
                        text=self.get_text("db_corrupted"), fg=self.colors["danger"]
                    ))
            else:
                self.log(self.get_text("log_db_missing"))
                self.root.after(0, lambda: self.db_status_val.config(
                    text=self.get_text("db_not_installed"), fg=self.colors["warning"]
                ))
                
        threading.Thread(target=worker, daemon=True).start()

    def build_ui(self):
        main_frame = tk.Frame(self.root, bg=self.colors["bg"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 20))

        # ---------------- HEADER ----------------
        header_frame = tk.Frame(main_frame, bg=self.colors["bg"])
        header_frame.pack(fill=tk.X, pady=(0, 8))
        
        self.title_label = tk.Label(header_frame, text="IP 归属地查询工具", 
                               font=("Segoe UI", 13, "bold"), 
                               bg=self.colors["bg"], fg=self.colors["text"])
        self.title_label.pack(side=tk.LEFT)
        
        self.subtitle_label = tk.Label(header_frame, text="本地 & 免费 API 实时对比", 
                                  font=("Segoe UI", 9), 
                                  bg=self.colors["bg"], fg=self.colors["text_muted"])
        self.subtitle_label.pack(side=tk.LEFT, padx=10, pady=(4, 0))
        
        # Author Label
        self.author_lbl = tk.Label(header_frame, text=" 作者：", font=("Segoe UI", 9),
                              bg=self.colors["bg"], fg=self.colors["text_muted"])
        self.author_lbl.pack(side=tk.LEFT, pady=(4, 0))
        
        author_link = tk.Label(header_frame, text="hik", font=("Segoe UI", 9, "underline"),
                               bg=self.colors["bg"], fg=self.colors["accent"], cursor="hand2")
        author_link.pack(side=tk.LEFT, pady=(4, 0))
        author_link.bind("<Button-1>", lambda e: webbrowser.open("https://hik.win"))

        # Help Icon
        self.btn_help = tk.Label(header_frame, text="❓ 帮助说明", font=("Segoe UI", 9, "bold"),
                                 bg=self.colors["bg"], fg=self.colors["accent"], cursor="hand2")
        self.btn_help.pack(side=tk.RIGHT, pady=(4, 0), padx=5)
        self.btn_help.bind("<Button-1>", lambda e: self.show_help_dialog())
        
        # Language Selector
        self.lang_var = tk.StringVar(value="中文")
        self.lang_select = ttk.Combobox(header_frame, textvariable=self.lang_var, 
                                        values=["中文", "English"],
                                        state="readonly", font=("Segoe UI", 9), width=8)
        self.lang_select.pack(side=tk.RIGHT, pady=(4, 0), padx=(5, 15))
        self.lang_select.bind("<<ComboboxSelected>>", lambda e: self.on_language_change())

        # ---------------- SECTION 1: IP INFO CARD ----------------
        ip_card = tk.Frame(main_frame, bg=self.colors["card"], 
                           highlightbackground=self.colors["border"], highlightthickness=1)
        ip_card.pack(fill=tk.X, pady=5)
        
        ip_card_inner = tk.Frame(ip_card, bg=self.colors["card"], padx=15, pady=12)
        ip_card_inner.pack(fill=tk.X)
        
        # Row 0: IPv4
        # Local IPv4
        self.lbl_local_ip = tk.Label(ip_card_inner, text="局域网 IPv4:", font=("Segoe UI", 10), 
                                bg=self.colors["card"], fg=self.colors["text_muted"])
        self.lbl_local_ip.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.val_local_ip = tk.Entry(ip_card_inner, font=("Consolas", 11, "bold"), fg=self.colors["text"], width=38)
        self.val_local_ip.insert(0, "正在获取...")
        self.val_local_ip.config(state="readonly")
        self.val_local_ip.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        self.setup_ip_entry(self.val_local_ip, "局域网 IPv4 地址")
        
        # Public IPv4
        self.lbl_public_ip = tk.Label(ip_card_inner, text="公网 IPv4:", font=("Segoe UI", 10), 
                                 bg=self.colors["card"], fg=self.colors["text_muted"])
        self.lbl_public_ip.grid(row=0, column=2, sticky=tk.W, padx=(40, 0), pady=5)
        
        self.val_public_ip = tk.Entry(ip_card_inner, font=("Consolas", 11, "bold"), fg=self.colors["accent"], width=38)
        self.val_public_ip.insert(0, "正在获取...")
        self.val_public_ip.config(state="readonly")
        self.val_public_ip.grid(row=0, column=3, sticky=tk.W, padx=10, pady=5)
        self.setup_ip_entry(self.val_public_ip, "公网 IPv4 地址")
        
        # Row 1: IPv6
        # Local IPv6
        self.lbl_local_ipv6 = tk.Label(ip_card_inner, text="局域网 IPv6:", font=("Segoe UI", 10), 
                                bg=self.colors["card"], fg=self.colors["text_muted"])
        self.lbl_local_ipv6.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.val_local_ipv6 = tk.Entry(ip_card_inner, font=("Consolas", 11, "bold"), fg=self.colors["text"], width=38)
        self.val_local_ipv6.insert(0, "正在获取...")
        self.val_local_ipv6.config(state="readonly")
        self.val_local_ipv6.grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)
        self.setup_ip_entry(self.val_local_ipv6, "局域网 IPv6 地址")
        
        # Public IPv6
        self.lbl_public_ipv6 = tk.Label(ip_card_inner, text="公网 IPv6:", font=("Segoe UI", 10), 
                                 bg=self.colors["card"], fg=self.colors["text_muted"])
        self.lbl_public_ipv6.grid(row=1, column=2, sticky=tk.W, padx=(40, 0), pady=5)
        
        self.val_public_ipv6 = tk.Entry(ip_card_inner, font=("Consolas", 11, "bold"), fg=self.colors["accent"], width=38)
        self.val_public_ipv6.insert(0, "正在获取...")
        self.val_public_ipv6.config(state="readonly")
        self.val_public_ipv6.grid(row=1, column=3, sticky=tk.W, padx=10, pady=5)
        self.setup_ip_entry(self.val_public_ipv6, "公网 IPv6 地址")
        
        # Refresh Button
        self.btn_refresh = tk.Button(ip_card_inner, text="刷新本机 IP", 
                                     bg=self.colors["accent"], fg="#11111b",
                                     activebackground=self.colors["accent_hover"], activeforeground="#11111b",
                                     bd=0, relief="flat", padx=12, pady=6, 
                                     font=("Segoe UI", 9, "bold"), cursor="hand2",
                                     command=self.refresh_ips)
        self.btn_refresh.grid(row=0, column=4, rowspan=2, sticky=tk.E, padx=(50, 0), pady=5)
        self.btn_refresh.bind("<Enter>", lambda e: e.widget.config(bg=self.colors["accent_hover"]))
        self.btn_refresh.bind("<Leave>", lambda e: e.widget.config(bg=self.colors["accent"]))
        
        # Grid weight adjustments
        ip_card_inner.grid_columnconfigure(4, weight=1)

        # ---------------- SECTION 2: LOOKUP COMPARISON CARD ----------------
        query_card = tk.Frame(main_frame, bg=self.colors["card"], 
                             highlightbackground=self.colors["border"], highlightthickness=1)
        query_card.pack(fill=tk.BOTH, expand=True, pady=10)
        
        query_card_inner = tk.Frame(query_card, bg=self.colors["card"], padx=15, pady=15)
        query_card_inner.pack(fill=tk.BOTH, expand=True)
        
        # Search Box Header
        search_frame = tk.Frame(query_card_inner, bg=self.colors["card"])
        search_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.search_lbl = tk.Label(search_frame, text="查询 IP 地址:", font=("Segoe UI", 10, "bold"), 
                              bg=self.colors["card"], fg=self.colors["text"])
        self.search_lbl.pack(side=tk.LEFT, pady=5)
        
        # Text input field
        self.ip_input = tk.Entry(search_frame, bg=self.colors["input_bg"], fg=self.colors["text"],
                                 insertbackground=self.colors["text"], bd=0, 
                                 highlightthickness=1, highlightbackground=self.colors["border"], 
                                 highlightcolor=self.colors["accent"], font=("Consolas", 12), width=25)
        self.ip_input.pack(side=tk.LEFT, padx=10, ipady=4, pady=5)
        self.ip_input.bind("<Return>", lambda e: self.perform_lookup())
        
        # Query button
        self.btn_query = tk.Button(search_frame, text="查询归属地", 
                                   bg=self.colors["accent"], fg="#11111b",
                                   activebackground=self.colors["accent_hover"], activeforeground="#11111b",
                                   bd=0, relief="flat", padx=15, pady=4, 
                                   font=("Segoe UI", 9, "bold"), cursor="hand2",
                                   command=self.perform_lookup)
        self.btn_query.pack(side=tk.LEFT, padx=5, pady=5)
        self.btn_query.bind("<Enter>", lambda e: e.widget.config(bg=self.colors["accent_hover"]))
        self.btn_query.bind("<Leave>", lambda e: e.widget.config(bg=self.colors["accent"]))
        
        # Result Details Layout
        results_container = tk.Frame(query_card_inner, bg=self.colors["card"])
        results_container.pack(fill=tk.BOTH, expand=True)
        
        # Local Database Box (Left Side)
        self.local_box = tk.Frame(results_container, bg=self.colors["input_bg"], 
                                  highlightbackground=self.colors["border"], highlightthickness=1, bd=0)
        self.local_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        
        self.lbl_local_title = tk.Label(self.local_box, text="本地数据库查询结果 (qqwry.dat)", font=("Segoe UI", 10, "bold"),
                                   bg=self.colors["input_bg"], fg=self.colors["accent"])
        self.lbl_local_title.pack(anchor=tk.W, padx=12, pady=(10, 5))
        
        self.val_local_loc = tk.Label(self.local_box, text="暂无数据", font=("Segoe UI", 11, "bold"),
                                      bg=self.colors["input_bg"], fg=self.colors["text"], wraplength=320, justify=tk.LEFT)
        self.val_local_loc.pack(anchor=tk.W, fill=tk.BOTH, expand=True, padx=12, pady=10)
        
        # Network API Box (Right Side)
        self.net_box = tk.Frame(results_container, bg=self.colors["input_bg"], 
                                highlightbackground=self.colors["border"], highlightthickness=1, bd=0)
        self.net_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0))
        
        self.lbl_net_title = tk.Label(self.net_box, text="网络 API 查询结果 (免费 API)", font=("Segoe UI", 10, "bold"),
                                 bg=self.colors["input_bg"], fg=self.colors["accent"])
        self.lbl_net_title.pack(anchor=tk.W, padx=12, pady=(10, 5))
        
        self.val_net_loc = tk.Label(self.net_box, text="暂无数据", font=("Segoe UI", 11, "bold"),
                                    bg=self.colors["input_bg"], fg=self.colors["text"], wraplength=320, justify=tk.LEFT)
        self.val_net_loc.pack(anchor=tk.W, fill=tk.BOTH, expand=True, padx=12, pady=10)

        # Comparison Alert Banner (Bottom of Section 2)
        self.compare_frame = tk.Frame(query_card_inner, bg=self.colors["card"], pady=10)
        self.compare_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.compare_badge = tk.Label(self.compare_frame, text="待检测", font=("Segoe UI", 10, "bold"),
                                      bg=self.colors["border"], fg=self.colors["text_muted"], padx=10, pady=3)
        self.compare_badge.pack(side=tk.LEFT)
        
        self.compare_desc = tk.Label(self.compare_frame, text="请输入 IP 地址进行查询对比", font=("Segoe UI", 10),
                                     bg=self.colors["card"], fg=self.colors["text_muted"])
        self.compare_desc.pack(side=tk.LEFT, padx=10)

        # ---------------- SECTION 3: DATABASE STATUS PANEL ----------------
        db_card = tk.Frame(main_frame, bg=self.colors["card"], 
                           highlightbackground=self.colors["border"], highlightthickness=1)
        db_card.pack(fill=tk.X, pady=5)
        
        db_card_inner = tk.Frame(db_card, bg=self.colors["card"], padx=15, pady=12)
        db_card_inner.pack(fill=tk.X)
        
        self.lbl_db = tk.Label(db_card_inner, text="本地数据库状态:", font=("Segoe UI", 10), 
                          bg=self.colors["card"], fg=self.colors["text_muted"])
        self.lbl_db.pack(side=tk.LEFT, pady=5)
        
        self.db_status_val = tk.Label(db_card_inner, text="正在检测...", font=("Segoe UI", 10, "bold"), 
                                      bg=self.colors["card"], fg=self.colors["warning"])
        self.db_status_val.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Download Progress frame (hidden by default)
        self.progress_frame = tk.Frame(db_card_inner, bg=self.colors["card"])
        self.progress_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=20)
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, style="Custom.Horizontal.TProgressbar", 
                                            orient="horizontal", mode="determinate")
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=5)
        
        self.progress_lbl = tk.Label(self.progress_frame, text="0%", font=("Segoe UI", 9, "bold"), 
                                     bg=self.colors["card"], fg=self.colors["text_muted"], width=6)
        self.progress_lbl.pack(side=tk.LEFT, padx=5)
        
        self.progress_frame.pack_forget() # Hide originally
        
        # Download/Update Button
        self.btn_db_action = tk.Button(db_card_inner, text="下载/更新数据库", 
                                       bg=self.colors["border"], fg=self.colors["text"],
                                       activebackground=self.colors["accent"], activeforeground="#11111b",
                                       bd=0, relief="flat", padx=12, pady=4, 
                                       font=("Segoe UI", 9, "bold"), cursor="hand2",
                                       command=self.toggle_db_download)
        self.btn_db_action.pack(side=tk.RIGHT, pady=5)
        self.btn_db_action.bind("<Enter>", lambda e: e.widget.config(bg=self.colors["accent"]))
        self.btn_db_action.bind("<Leave>", lambda e: e.widget.config(bg=self.colors["border"]))

        # ---------------- SECTION 4: CONSOLE LOG PANEL ----------------
        console_frame = tk.Frame(main_frame, bg=self.colors["bg"])
        console_frame.pack(fill=tk.X, pady=(10, 0))
        
        console_lbl_frame = tk.Frame(console_frame, bg=self.colors["bg"])
        console_lbl_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.console_lbl = tk.Label(console_lbl_frame, text="系统日志控制台", font=("Segoe UI", 10, "bold"), 
                               bg=self.colors["bg"], fg=self.colors["text_muted"])
        self.console_lbl.pack(side=tk.LEFT)
        
        self.console = tk.Text(console_frame, height=5, bg=self.colors["input_bg"], fg="#a6e3a1",
                               bd=0, highlightthickness=1, highlightbackground=self.colors["border"],
                               font=("Consolas", 9), wrap=tk.WORD, state="disabled")
        self.console.pack(fill=tk.X)

    def refresh_ips(self):
        """Asynchronously retrieve the machine's local and public IP addresses."""
        try:
            if self.root and self.root.winfo_exists():
                self.btn_refresh.config(state="disabled", text=self.get_text("btn_refresh_loading"))
                self.set_entry_text(self.val_local_ip, self.get_text("btn_refresh_loading"), self.colors["text_muted"])
                self.set_entry_text(self.val_public_ip, self.get_text("btn_refresh_loading"), self.colors["text_muted"])
                self.set_entry_text(self.val_local_ipv6, self.get_text("btn_refresh_loading"), self.colors["text_muted"])
                self.set_entry_text(self.val_public_ipv6, self.get_text("btn_refresh_loading"), self.colors["text_muted"])
        except Exception:
            pass
        self.log(self.get_text("log_detect_ip"))

        def worker():
            # IPv4
            local_ip = ip_service.get_local_ip()
            self.local_ip = local_ip
            self.root.after(0, lambda: self.set_entry_text(self.val_local_ip, local_ip, self.colors["text"]))
            self.log(self.get_text("log_local_ipv4_ok", ip=local_ip))
            
            public_ip = ip_service.fetch_public_ip()
            self.public_ip = public_ip
            if public_ip:
                self.root.after(0, lambda: self.set_entry_text(self.val_public_ip, public_ip, self.colors["accent"]))
                
                def set_default_and_lookup():
                    try:
                        if self.root and self.root.winfo_exists():
                            self.set_input_default_ip(public_ip)
                            self.perform_lookup(public_ip)
                    except Exception:
                        pass
                self.root.after(100, set_default_and_lookup)
                self.log(self.get_text("log_pub_ipv4_ok", ip=public_ip))
            else:
                self.root.after(0, lambda: self.set_entry_text(self.val_public_ip, "Failed (Offline)" if self.current_lang == 'en' else "获取失败 (离线)", self.colors["danger"]))
                self.log(self.get_text("log_pub_ipv4_err"))

            # IPv6
            local_ipv6 = ip_service.get_local_ipv6()
            self.local_ipv6 = local_ipv6
            local_ipv6_show = local_ipv6 if local_ipv6 else ("Not Assigned / Disabled" if self.current_lang == 'en' else "未分配 / 禁用")
            self.root.after(0, lambda: self.set_entry_text(self.val_local_ipv6, local_ipv6_show, self.colors["text"]))
            if local_ipv6:
                self.log(self.get_text("log_local_ipv6_ok", ip=local_ipv6))
            else:
                self.log(self.get_text("log_local_ipv6_err"))
            
            public_ipv6 = ip_service.fetch_public_ipv6()
            self.public_ipv6 = public_ipv6
            public_ipv6_show = public_ipv6 if public_ipv6 else ("Not Assigned / Disabled" if self.current_lang == 'en' else "未分配 / 禁用")
            ipv6_color = self.colors["accent"] if public_ipv6 else self.colors["text_muted"]
            self.root.after(0, lambda: self.set_entry_text(self.val_public_ipv6, public_ipv6_show, ipv6_color))
            if public_ipv6:
                self.log(self.get_text("log_pub_ipv6_ok", ip=public_ipv6))
            else:
                self.log(self.get_text("log_pub_ipv6_err"))
                
            def finish():
                try:
                    if self.root and self.root.winfo_exists():
                        self.btn_refresh.config(state="normal", text=self.get_text("btn_refresh"))
                except Exception:
                    pass
            self.root.after(0, finish)
            
        threading.Thread(target=worker, daemon=True).start()

    def set_input_default_ip(self, ip):
        """Pre-populate the lookup search field with the public IP."""
        if not self.ip_input.get():
            self.ip_input.insert(0, ip)

    def perform_lookup(self, target_ip=None):
        """Lookup IP location locally and online, then compare."""
        if target_ip is None:
            target_ip = self.ip_input.get().strip()
            
        if not target_ip:
            messagebox.showwarning(self.get_text("msg_notice"), self.get_text("msg_input_ip"))
            return
            
        # Basic IPv4 and IPv6 validation
        is_ipv4 = False
        is_ipv6 = False
        try:
            socket.inet_pton(socket.AF_INET, target_ip)
            is_ipv4 = True
        except socket.error:
            try:
                socket.inet_pton(socket.AF_INET6, target_ip)
                is_ipv6 = True
            except socket.error:
                pass

        if not is_ipv4 and not is_ipv6:
            messagebox.showerror(self.get_text("msg_error"), self.get_text("msg_invalid_ip"))
            return

        self.btn_query.config(state="disabled")
        self.val_local_loc.config(text=self.get_text("btn_query_loading"), fg=self.colors["text_muted"])
        self.val_net_loc.config(text=self.get_text("btn_query_loading"), fg=self.colors["text_muted"])
        self.compare_badge.config(text=self.get_text("compare_matching"), bg=self.colors["border"], fg=self.colors["text_muted"])
        self.compare_desc.config(text=self.get_text("compare_matching_desc"), fg=self.colors["text_muted"])
        
        # Reset card borders
        self.local_box.config(highlightbackground=self.colors["border"])
        self.net_box.config(highlightbackground=self.colors["border"])
        
        self.log(self.get_text("log_query_ip", ip=target_ip))

        def worker():
            # 1. Local Database Lookup
            local_res = self.get_text("db_unloaded")
            if is_ipv6:
                local_res = self.get_text("local_ipv6_not_supported")
            elif self.parser:
                try:
                    res = self.parser.lookup(target_ip)
                    if res:
                        country, area = res
                        local_res = f"{country} {area}".strip()
                    else:
                        local_res = self.get_text("local_not_found")
                except Exception as e:
                    local_res = self.get_text("local_query_err", e=e)
                    self.log(self.get_text("local_query_err", e=e))
            else:
                self.log("Local database not loaded, skipping local resolution.")

            # 2. Network Geolocation Lookup
            try:
                net_res = ip_service.query_network_location(target_ip)
                if net_res == "未知网络归属地" and self.current_lang == 'en':
                    net_res = self.get_text("unknown_location")
            except Exception as e:
                net_res = self.get_text("net_query_err", e=e)
                self.log(self.get_text("net_query_err", e=e))

            self.log(self.get_text("local_query_res", res=local_res))
            self.log(self.get_text("net_query_res", res=net_res))

            # 3. Compare Results
            consistent = ip_service.check_consistency(local_res, net_res)
            
            # Special case exclusions for compare banner
            db_unloaded = (local_res in [self.get_text("db_unloaded"), self.get_text("local_ipv6_not_supported")])
            not_found = ("未收录" in local_res or "not found" in local_res.lower() or "unknown" in net_res.lower() or "未知" in net_res or "exception" in local_res.lower() or "exception" in net_res.lower() or "异常" in local_res or "异常" in net_res)
            
            # Update GUI safely
            self.root.after(0, lambda: self.update_lookup_results(local_res, net_res, consistent, db_unloaded, not_found))

        threading.Thread(target=worker, daemon=True).start()

    def update_lookup_results(self, local_res, net_res, consistent, db_unloaded, not_found):
        """Update lookup elements and show mismatch warning if required."""
        self.val_local_loc.config(text=local_res, fg=self.colors["text"])
        self.val_net_loc.config(text=net_res, fg=self.colors["text"])
        self.btn_query.config(state="normal")

        if db_unloaded:
            self.compare_badge.config(text=self.get_text("compare_missing_db"), bg=self.colors["warning"], fg="#11111b")
            self.compare_desc.config(text=self.get_text("compare_missing_db_desc"), fg=self.colors["warning"])
        elif not_found:
            self.compare_badge.config(text=self.get_text("compare_insufficient"), bg=self.colors["border"], fg=self.colors["text_muted"])
            self.compare_desc.config(text=self.get_text("compare_insufficient_desc"), fg=self.colors["text_muted"])
        elif consistent:
            self.compare_badge.config(text=self.get_text("compare_consistent"), bg=self.colors["success"], fg="#11111b")
            self.compare_desc.config(text=self.get_text("compare_consistent_desc"), fg=self.colors["success"])
            self.local_box.config(highlightbackground=self.colors["success"])
            self.net_box.config(highlightbackground=self.colors["success"])
        else:
            self.compare_badge.config(text=self.get_text("compare_discrepancy"), bg=self.colors["danger"], fg="#11111b")
            self.compare_desc.config(text=self.get_text("compare_discrepancy_desc"), fg=self.colors["danger"])
            
            # Highlight discrepancy cards in red border
            self.local_box.config(highlightbackground=self.colors["danger"])
            self.net_box.config(highlightbackground=self.colors["danger"])
            self.log("Warning: Database and Network API lookups do not match!" if self.current_lang == 'en' else "警告: 本地数据库与网络归属地结果不一致！")

    def toggle_db_download(self):
        """Start or Cancel downloading of the local database file."""
        if self.btn_db_action.cget("text") in ["取消下载", "Cancel Download"]:
            self.download_cancelled.set()
            self.log("Cancelling download..." if self.current_lang == 'en' else "正在取消下载...")
            return

        self.download_cancelled.clear()
        self.btn_db_action.config(text=self.get_text("btn_db_cancel"), bg=self.colors["danger"], fg="#11111b")
        self.progress_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=20)
        self.progress_bar.config(value=0)
        self.progress_lbl.config(text="0%")
        self.db_status_val.config(text=self.get_text("db_downloading"), fg=self.colors["warning"])
        self.log(self.get_text("log_db_download_start"))

        def progress_handler(percent, downloaded, total_size):
            dl_mb = downloaded / (1024 * 1024)
            total_mb = total_size / (1024 * 1024)
            
            def update():
                self.progress_bar.config(value=percent)
                self.progress_lbl.config(text=f"{percent:.1f}%")
                self.db_status_val.config(text=self.get_text("db_download_speed", dl_mb=dl_mb, total_mb=total_mb))
                
            self.root.after(0, update)

        def worker():
            try:
                success = ip_service.download_db(self.persistent_db_path, progress_handler, self.download_cancelled)
                if success:
                    self.log(self.get_text("log_db_download_ok"))
                    self.db_path = self.persistent_db_path
                    # Reload database
                    self.load_database()
                else:
                    self.log(self.get_text("log_db_download_cancel"))
                    self.root.after(0, self.reset_db_status_ui)
            except Exception as e:
                self.log(self.get_text("log_db_download_err", e=e))
                self.root.after(0, lambda: messagebox.showerror(self.get_text("msg_download_fail"), self.get_text("msg_download_fail_desc", e=e)))
                self.root.after(0, self.reset_db_status_ui)
            finally:
                self.root.after(0, lambda: self.btn_db_action.config(text=self.get_text("btn_db_action"), bg=self.colors["border"], fg=self.colors["text"]))
                self.root.after(0, lambda: self.progress_frame.pack_forget())

        threading.Thread(target=worker, daemon=True).start()

    def reset_db_status_ui(self):
        """Reset the status text of the database UI if download fails."""
        if os.path.exists(self.db_path):
            self.db_status_val.config(text=self.get_text("db_loaded_old"), fg=self.colors["warning"])
        else:
            self.db_status_val.config(text=self.get_text("db_install_failed"), fg=self.colors["danger"])

if __name__ == "__main__":
    # Create the root Tkinter window
    root = tk.Tk()
    app = IPGetApp(root)
    root.mainloop()
