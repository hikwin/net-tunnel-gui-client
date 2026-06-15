import tkinter as tk
from tkinter import ttk, messagebox
import threading
import subprocess
import os
import re
import sys
import webbrowser
import json
from datetime import datetime

# Import local modules
import ip_service
from ipget_gui import IPGetApp

class TunnelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("内网穿透 GUI 客户端")
        self.root.geometry("860x700")
        self.root.minsize(800, 600)
        self.root.configure(bg="#1e1e2e")

        # Color Palette
        self.colors = {
            "bg": "#1e1e2e",
            "card": "#252538",
            "border": "#313244",
            "text": "#cdd6f4",
            "text_muted": "#a6adc8",
            "accent": "#f9e2af",       # Yellow/Gold
            "accent_hover": "#f5e0dc",
            "success": "#a6e3a1",      # Green
            "warning": "#f9e2af",      # Yellow
            "danger": "#f38ba8",       # Red
            "input_bg": "#181825",
            "btn_start": "#89b4fa",    # Blue
            "btn_start_hover": "#b4befe"
        }

        # App state
        self.active_proc = None
        self.tunnel_thread = None
        self.public_url = None
        self.is_running = False
        
        # Local machine IP state
        self.local_public_ipv4 = None
        self.local_public_ipv6 = None
        
        # Language state
        self.current_lang = "zh"
        
        # Localization data
        self.lang_data = {
            "zh": {
                "window_title": "内网穿透 GUI 客户端",
                "title_label": "内网穿透 GUI 客户端",
                "author": " 作者：",
                "help_btn": "❓ 帮助说明",
                "pub_ipv4": "本机公网 IPv4:",
                "pub_ipv6": "本机公网 IPv6:",
                "btn_refresh": "刷新",
                "btn_refresh_loading": "刷新中...",
                "btn_detail": "详细信息",
                "lbl_port": "本地目标端口:",
                "lbl_provider": "选择穿透服务商:",
                "config_frame": "服务商配置选项",
                "lbl_subdomain": "子域名 (可选 - 英文/数字):",
                "lbl_host": "隧道服务器 Host (默认 localtunnel.me):",
                "ssh_info": "SSH 隧道无需额外本地配置。\n它直接利用系统内置 SSH 发起转发请求。",
                "btn_start_tunnel": "开启隧道服务",
                "btn_stop_tunnel": "停止隧道服务",
                "status_title": "隧道连接状态:",
                "status_closed": "已关闭",
                "status_connecting": "连接中...",
                "status_running": "已启动",
                "port_status_title": "本地端口检测:",
                "port_status_inactive": "未启动",
                "port_status_listening": "正常监听中 ({port})",
                "port_status_not_listening": "未检测到服务 (请开启本地 {port} 端口)",
                "url_title": "生成的公共访问链接:",
                "url_val_waiting": "等待隧道启动...",
                "url_val_generating": "正在生成链接...",
                "btn_copy": "复制链接",
                "btn_browser": "浏览器打开",
                "tip_card": "使用说明及提示",
                "console_lbl": "隧道控制台标准输出 (实时)",
                "help_title": "帮助与说明",
                "help_header": "❓ 软件说明与隐私申明",
                "help_close": "我知道了",
                "help_text": (
                    "【软件作用】\n"
                    "本软件是一款极简的内网穿透与网络诊断 GUI 客户端。集成 Localtunnel、Serveo 和 Pinggy.io 穿透服务，帮助开发者一键将本地端口（如 Web 服务、API 服务）映射至公网进行临时调试。同时，内置的双栈 IP 检测与地理位置比对工具支持 IPv4/IPv6，可用于排查网络联通性及本地服务健康状态。\n\n"
                    "【隐私申明】\n"
                    "1. 纯本地运行：本软件为完全开源、本地运行 of 客户端工具。我们不会收集、储存或上传您的任何个人隐私数据（包括您的真实 IP 地址、穿透流量、本地服务端口等）。\n"
                    "2. 第三方查询：本机公网 IP 查询及归属地检索使用公开的第三方 API 镜像接口，相关查询请求由您的计算机直接向服务商发起，我们不设 any 中转服务器，数据仅在本地前端临时渲染展示。\n"
                    "3. 隧道传输安全：内网穿透服务直接连接到各服务商的公网代理服务器，您的流量完全在您与穿透服务商之间传输，建议不要在公开的隧道中传输敏感/未加密的生产环境数据。\n\n"
                    "【免责申明】\n"
                    "请确保使用本软件进行合法的开发与测试工作。严禁将本软件用于任何形式的非法目的。因使用本工具（及第三方隧道）所产生的一切法律纠纷与安全责任，均由使用者本人独立承担，本软件作者不承担任何连带赔偿与法律责任。\n\n"
                    "作者主页：https://hik.win"
                ),
                "toast_copied": "复制成功!",
                "err_invalid_port": "请输入有效的数字端口。",
                "err_title": "输入错误",
                "success_title": "成功",
                "success_copy_url": "已成功复制公网访问链接到剪贴板！",
                "getting_ip": "获取中...",
                "get_ip_failed_offline": "获取失败 (离线)",
                "get_ip_not_assigned": "未分配 / 禁用",
                "log_detect_ip": "正在检测本机公网 IP 地址...",
                "log_found_ipv4": "检测到本机公网 IPv4: {ip}",
                "log_failed_ipv4": "本机公网 IPv4 获取失败",
                "log_found_ipv6": "检测到本机公网 IPv6: {ip}",
                "log_failed_ipv6": "未检测到本机公网 IPv6 地址",
                "log_checking_deps": "正在加载并检查环境依赖项...",
                "log_dep_results": "系统环境检测: NPX (Localtunnel)={npx_ok}, OpenSSH (SSH)={ssh_ok}",
                "log_ssh_key_gen": "检测到系统不存在 SSH 密钥，正在自动为您生成 Ed25519 密钥对以用于免密通道连接...",
                "log_ssh_key_ed25519_ok": "SSH 密钥对 (Ed25519) 生成成功！",
                "log_ssh_key_ed25519_err": "Ed25519 密钥生成失败: {stderr}，尝试生成 RSA 密钥对...",
                "log_ssh_key_rsa_ok": "RSA 密钥对生成成功！",
                "log_ssh_key_rsa_err": "RSA 密钥生成失败: {stderr}",
                "log_ssh_key_err": "生成 SSH 密钥时发生异常: {e}",
                "log_starting_tunnel": "正在启动穿透服务 [{provider}] 映射本地端口: {port}...",
                "log_exec_cmd": "执行命令: {cmd}",
                "log_tunnel_ok": "隧道连接成功！公网 URL: {url}",
                "log_tunnel_exit": "隧道进程退出，退出码: {code}",
                "log_stopping_tunnel": "正在停止隧道服务...",
                "log_stop_err": "终止进程发生错误: {e}",
                "log_stopped_ok": "隧道服务已安全停止。",
                "log_copied": "链接已复制到剪贴板。",
                "log_browser_opened": "已请求系统浏览器打开链接: {url}",
                "log_copy_fail": "复制失败: {e}",
                "log_config_saved": "配置已保存到: {path}",
                "log_config_save_fail": "保存配置失败: {e}",
                "log_config_load_fail": "加载配置文件失败: {e}",
                "tip_lt": "• Localtunnel 是一个基于 Node.js 的免费反向代理穿透客户端。\n• 子域名为选填项，如果不填，系统会默认生成一个随机域名。\n• Host 参数通常使用官网默认的 'https://localtunnel.me'。\n• 优点：不需要任何账户即可启动，速度和稳定性极佳。",
                "tip_serveo": "• serveo.net 是一项极简的 SSH 远程端口映射服务。\n• 优点：使用纯 SSH 转发，不需要本地安装任何辅助二进制文件，直接复用操作系统的 OpenSSH 客户端。\n• 它的公共链接以 `.serveo.net` 或 `.serveousercontent.com` 结尾，对 HTTP/HTTPS 的代理非常适合测试 API 与前端网页。",
                "tip_pinggy": "• Pinggy.io 是一项高性能且防火墙友好的 SSH 穿透服务。\n• 优点：同样使用纯 SSH 转发，直连远程服务器的 443 端口，对大多数严格的企业内网也有极强的穿透力。\n• 它的免费公网链接以 `.pinggy.link` 结尾，不需要任何客户端安装，适合开发测试与 webhook 回调。"
            },
            "en": {
                "window_title": "Intranet Penetration GUI Client",
                "title_label": "Intranet Penetration GUI Client",
                "author": " Author: ",
                "help_btn": "❓ Help & Info",
                "pub_ipv4": "Local Public IPv4:",
                "pub_ipv6": "Local Public IPv6:",
                "btn_refresh": "Refresh",
                "btn_refresh_loading": "Refreshing...",
                "btn_detail": "Details",
                "lbl_port": "Local Target Port:",
                "lbl_provider": "Select Provider:",
                "config_frame": "Provider Options",
                "lbl_subdomain": "Subdomain (Optional - alphanumeric):",
                "lbl_host": "Tunnel Server Host (Default localtunnel.me):",
                "ssh_info": "SSH tunnel requires no local configuration.\nIt directly uses system OpenSSH client for port forwarding.",
                "btn_start_tunnel": "Start Tunnel Service",
                "btn_stop_tunnel": "Stop Tunnel Service",
                "status_title": "Tunnel Status:",
                "status_closed": "Closed",
                "status_connecting": "Connecting...",
                "status_running": "Running",
                "port_status_title": "Local Port Check:",
                "port_status_inactive": "Inactive",
                "port_status_listening": "Listening ({port})",
                "port_status_not_listening": "No service detected (Please start service on port {port})",
                "url_title": "Public Access URL:",
                "url_val_waiting": "Waiting for tunnel to start...",
                "url_val_generating": "Generating URL...",
                "btn_copy": "Copy URL",
                "btn_browser": "Open in Browser",
                "tip_card": "Usage & Tips",
                "console_lbl": "Tunnel Console Stdout (Real-time)",
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
                "err_invalid_port": "Please enter a valid numeric port.",
                "err_title": "Input Error",
                "success_title": "Success",
                "success_copy_url": "Successfully copied public access link to clipboard!",
                "getting_ip": "Retrieving...",
                "get_ip_failed_offline": "Failed (Offline)",
                "get_ip_not_assigned": "Not Assigned / Disabled",
                "log_detect_ip": "Detecting public IP address...",
                "log_found_ipv4": "Detected public IPv4: {ip}",
                "log_failed_ipv4": "Failed to get public IPv4",
                "log_found_ipv6": "Detected public IPv6: {ip}",
                "log_failed_ipv6": "No public IPv6 address detected",
                "log_checking_deps": "Checking environment dependencies...",
                "log_dep_results": "Environment check: NPX (Localtunnel)={npx_ok}, OpenSSH (SSH)={ssh_ok}",
                "log_ssh_key_gen": "No SSH keys found. Generating Ed25519 key pair for passwordless connection...",
                "log_ssh_key_ed25519_ok": "SSH key pair (Ed25519) generated successfully!",
                "log_ssh_key_ed25519_err": "Ed25519 key generation failed: {stderr}. Trying RSA...",
                "log_ssh_key_rsa_ok": "RSA key pair generated successfully!",
                "log_ssh_key_rsa_err": "RSA key generation failed: {stderr}",
                "log_ssh_key_err": "Exception generating SSH key: {e}",
                "log_starting_tunnel": "Starting tunnel service [{provider}] on port {port}...",
                "log_exec_cmd": "Executing command: {cmd}",
                "log_tunnel_ok": "Tunnel connection established! Public URL: {url}",
                "log_tunnel_exit": "Tunnel process exited with code: {code}",
                "log_stopping_tunnel": "Stopping tunnel service...",
                "log_stop_err": "Error terminating process: {e}",
                "log_stopped_ok": "Tunnel service safely stopped.",
                "log_copied": "URL copied to clipboard.",
                "log_browser_opened": "Opening URL in system browser: {url}",
                "log_copy_fail": "Copy failed: {e}",
                "log_config_saved": "Config saved to: {path}",
                "log_config_save_fail": "Failed to save config: {e}",
                "log_config_load_fail": "Failed to load config: {e}",
                "tip_lt": "• Localtunnel is a free, Node.js-based reverse proxy client.\n• Subdomain is optional. If left blank, a random domain will be generated.\n• Host defaults to 'https://localtunnel.me'.\n• Advantage: No account needed, speed and stability are excellent.",
                "tip_serveo": "• serveo.net is an ultra-simple SSH port forwarding service.\n• Advantage: Uses pure SSH. No local agent binary is needed as it uses openSSH.\n• Public URLs end with `.serveo.net` or `.serveousercontent.com`, perfect for APIs and web page testing.",
                "tip_pinggy": "• Pinggy.io is a high-performance, firewall-friendly SSH tunnel service.\n• Advantage: Uses pure SSH to port 443, making it highly effective even behind strict corporate firewalls.\n• Free URLs end with `.pinggy.link`. No installation is required, ideal for webhooks."
            }
        }
        
        # Initialize styles
        self.setup_styles()
        
        # Build UI layout
        self.build_ui()
        
        # Load configuration (sets current_lang, port, provider, sub, host)
        self.load_config()
        
        # Update text for all elements based on current language
        self.update_ui_text()
        
        # Check dependencies in background
        self.check_dependencies_async()
        
        # Initial IP fetch
        self.refresh_local_ips()

    def get_text(self, key, **kwargs):
        """Retrieve translated string with optional interpolation."""
        text = self.lang_data[self.current_lang].get(key, "")
        if kwargs:
            return text.format(**kwargs)
        return text

    def get_config_path(self):
        """Locate configuration file next to executable or source file."""
        if getattr(sys, 'frozen', False):
            exe_dir = os.path.dirname(sys.executable)
        else:
            exe_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(exe_dir, "config.json")

    def load_config(self):
        """Load settings from config.json."""
        config_path = self.get_config_path()
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                    self.current_lang = config.get("lang", "zh")
                    if self.current_lang not in ["zh", "en"]:
                        self.current_lang = "zh"
                    
                    self.lang_var.set("English" if self.current_lang == "en" else "中文")
                    
                    port = config.get("port", "8000")
                    self.port_input.delete(0, tk.END)
                    self.port_input.insert(0, port)
                    
                    provider = config.get("provider", "Localtunnel (lt)")
                    if provider in ["Localtunnel (lt)", "serveo.net (SSH)", "Pinggy.io (SSH)"]:
                        self.provider_select.set(provider)
                        
                    subdomain = config.get("subdomain", "")
                    self.lt_subdomain.delete(0, tk.END)
                    self.lt_subdomain.insert(0, subdomain)
                    
                    host = config.get("host", "https://localtunnel.me")
                    self.lt_host.delete(0, tk.END)
                    self.lt_host.insert(0, host)
                    
                    return
            except Exception as e:
                # Log using the default language since update_ui_text hasn't run yet
                self.log(self.get_text("log_config_load_fail", e=e))
                
        # Default state
        self.current_lang = "zh"
        self.lang_var.set("中文")

    def save_config(self):
        """Save current UI values and language choice to config.json."""
        config_path = self.get_config_path()
        try:
            config = {
                "lang": self.current_lang,
                "port": self.port_input.get().strip(),
                "provider": self.provider_var.get(),
                "subdomain": self.lt_subdomain.get().strip(),
                "host": self.lt_host.get().strip()
            }
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            self.log(self.get_text("log_config_saved", path=config_path))
        except Exception as e:
            self.log(self.get_text("log_config_save_fail", e=e))

    def on_language_change(self):
        """Triggered when user selects a different language from the dropdown."""
        selected = self.lang_var.get()
        if selected == "English":
            self.current_lang = "en"
        else:
            self.current_lang = "zh"
        self.update_ui_text()
        self.save_config()

    def update_ui_text(self):
        """Update all text widgets with selected language."""
        self.root.title(self.get_text("window_title"))
        self.title_label.config(text=self.get_text("title_label"))
        self.author_lbl.config(text=self.get_text("author"))
        self.btn_help.config(text=self.get_text("help_btn"))
        
        self.lbl_pub_ipv4.config(text=self.get_text("pub_ipv4"))
        self.lbl_pub_ipv6.config(text=self.get_text("pub_ipv6"))
        
        # Manage refresh button text state
        ref_text = self.btn_ip_refresh.cget("text")
        if ref_text in ["刷新中...", "Refreshing..."]:
            self.btn_ip_refresh.config(text=self.get_text("btn_refresh_loading"))
        else:
            self.btn_ip_refresh.config(text=self.get_text("btn_refresh"))
            
        self.btn_ip_detail.config(text=self.get_text("btn_detail"))
        self.lbl_port.config(text=self.get_text("lbl_port"))
        self.lbl_provider.config(text=self.get_text("lbl_provider"))
        self.config_frame.config(text=self.get_text("config_frame"))
        self.lbl_subdomain.config(text=self.get_text("lbl_subdomain"))
        self.lbl_host.config(text=self.get_text("lbl_host"))
        self.info_label.config(text=self.get_text("ssh_info"))
        
        if self.is_running:
            self.btn_action.config(text=self.get_text("btn_stop_tunnel"))
        else:
            self.btn_action.config(text=self.get_text("btn_start_tunnel"))
            
        self.lbl_status_title.config(text=self.get_text("status_title"))
        
        # Connection status label
        status_text = self.lbl_status.cget("text")
        if status_text in ["已关闭", "Closed", "已停止", "Stopped"]:
            self.lbl_status.config(text=self.get_text("status_closed"))
        elif status_text in ["连接中...", "Connecting..."]:
            self.lbl_status.config(text=self.get_text("status_connecting"))
        elif status_text in ["已启动", "Running"]:
            self.lbl_status.config(text=self.get_text("status_running"))
            
        self.lbl_port_status_title.config(text=self.get_text("port_status_title"))
        
        # Local Port check label
        port_status_text = self.lbl_port_status.cget("text")
        port = self.port_input.get().strip()
        if port_status_text in ["未启动", "Inactive"]:
            self.lbl_port_status.config(text=self.get_text("port_status_inactive"))
        elif "监听" in port_status_text or "Listening" in port_status_text:
            self.lbl_port_status.config(text=self.get_text("port_status_listening", port=port))
        elif "未检测到" in port_status_text or "No service" in port_status_text:
            self.lbl_port_status.config(text=self.get_text("port_status_not_listening", port=port))
            
        self.lbl_url_title.config(text=self.get_text("url_title"))
        
        # URL label
        url_text = self.lbl_url_val.cget("text")
        if url_text in ["等待隧道启动...", "Waiting for tunnel to start..."]:
            self.lbl_url_val.config(text=self.get_text("url_val_waiting"))
        elif url_text in ["正在生成链接...", "Generating URL..."]:
            self.lbl_url_val.config(text=self.get_text("url_val_generating"))
            
        self.btn_copy.config(text=self.get_text("btn_copy"))
        self.btn_browser.config(text=self.get_text("btn_browser"))
        self.tip_card.config(text=self.get_text("tip_card"))
        self.console_lbl.config(text=self.get_text("console_lbl"))
        
        # Update tip descriptions
        self.on_provider_change()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('default')
        style.configure(".", background=self.colors["bg"], foreground=self.colors["text"])
        
        # Combobox styling override
        style.map('TCombobox', fieldbackground=[('readonly', self.colors["input_bg"])])
        style.configure('TCombobox', 
                        background=self.colors["border"], 
                        foreground=self.colors["text"],
                        arrowcolor=self.colors["text"])

    def log(self, message):
        """Thread-safe append logs to console."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] {message}\n"
        
        def append():
            try:
                if self.root and self.root.winfo_exists():
                    self.console.config(state="normal")
                    self.console.insert(tk.END, formatted)
                    self.console.see(tk.END)
                    self.console.config(state="disabled")
            except Exception:
                pass
            
        self.root.after(0, append)

    def check_dependencies_async(self):
        """Asynchronously check local executables/packages."""
        self.log(self.get_text("log_checking_deps"))
        
        def worker():
            # Check npx
            try:
                res = subprocess.run("npx -v", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                npx_ok = res.returncode == 0
            except Exception:
                npx_ok = False
                
            # Check SSH
            try:
                res = subprocess.run("ssh -V", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                ssh_ok = res.returncode == 0
            except Exception:
                ssh_ok = False

            self.log(self.get_text("log_dep_results", npx_ok=npx_ok, ssh_ok=ssh_ok))
            
        threading.Thread(target=worker, daemon=True).start()

    def build_ui(self):
        main_frame = tk.Frame(self.root, bg=self.colors["bg"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 20))

        # ---------------- HEADER ----------------
        header_frame = tk.Frame(main_frame, bg=self.colors["bg"])
        header_frame.pack(fill=tk.X, pady=(0, 8))
        
        self.title_label = tk.Label(header_frame, text="内网穿透 GUI 客户端", 
                               font=("Segoe UI", 13, "bold"), 
                               bg=self.colors["bg"], fg=self.colors["text"])
        self.title_label.pack(side=tk.LEFT)
        
        self.subtitle_label = tk.Label(header_frame, text="Localtunnel / SSH Tunnels", 
                                  font=("Segoe UI", 9), 
                                  bg=self.colors["bg"], fg=self.colors["text_muted"])
        self.subtitle_label.pack(side=tk.LEFT, padx=10, pady=(4, 0))
        
        # Author Label
        self.author_lbl = tk.Label(header_frame, text=" 作者：", font=("Segoe UI", 9),
                              bg=self.colors["bg"], fg=self.colors["text_muted"])
        self.author_lbl.pack(side=tk.LEFT, pady=(4, 0))
        
        author_link = tk.Label(header_frame, text="hik", font=("Segoe UI", 9, "underline"),
                               bg=self.colors["bg"], fg=self.colors["btn_start"], cursor="hand2")
        author_link.pack(side=tk.LEFT, pady=(4, 0))
        author_link.bind("<Button-1>", lambda e: webbrowser.open("https://hik.win"))

        # Help Icon
        self.btn_help = tk.Label(header_frame, text="❓ 帮助说明", font=("Segoe UI", 9, "bold"),
                                 bg=self.colors["bg"], fg=self.colors["accent"], cursor="hand2")
        self.btn_help.pack(side=tk.RIGHT, pady=(4, 0), padx=5)
        self.btn_help.bind("<Button-1>", lambda e: self.show_help_dialog())
        
        # Language Selector Combobox
        self.lang_var = tk.StringVar(value="中文")
        self.lang_select = ttk.Combobox(header_frame, textvariable=self.lang_var, 
                                        values=["中文", "English"],
                                        state="readonly", font=("Segoe UI", 9), width=8)
        self.lang_select.pack(side=tk.RIGHT, pady=(4, 0), padx=(5, 15))
        self.lang_select.bind("<<ComboboxSelected>>", lambda e: self.on_language_change())

        # ---------------- IP INFO CARD (Integrated from IPGet) ----------------
        self.ip_card = tk.Frame(main_frame, bg=self.colors["card"],
                                highlightbackground=self.colors["border"], highlightthickness=1)
        self.ip_card.pack(fill=tk.X, pady=(0, 15))
        
        ip_card_inner = tk.Frame(self.ip_card, bg=self.colors["card"], padx=15, pady=10)
        ip_card_inner.pack(fill=tk.X)
        
        # Public IPv4
        self.lbl_pub_ipv4 = tk.Label(ip_card_inner, text="本机公网 IPv4:", font=("Segoe UI", 10), 
                                bg=self.colors["card"], fg=self.colors["text_muted"])
        self.lbl_pub_ipv4.grid(row=0, column=0, sticky=tk.W, pady=3)
        self.val_pub_ipv4 = tk.Entry(ip_card_inner, font=("Consolas", 10, "bold"), fg=self.colors["text"], width=15)
        self.val_pub_ipv4.insert(0, "正在获取...")
        self.val_pub_ipv4.config(state="readonly")
        self.val_pub_ipv4.grid(row=0, column=1, sticky=tk.W, padx=(5, 15), pady=3)
        self.setup_ip_entry(self.val_pub_ipv4, "公网 IPv4 地址")
        
        # Public IPv6
        self.lbl_pub_ipv6 = tk.Label(ip_card_inner, text="本机公网 IPv6:", font=("Segoe UI", 10), 
                                bg=self.colors["card"], fg=self.colors["text_muted"])
        self.lbl_pub_ipv6.grid(row=0, column=2, sticky=tk.W, pady=3)
        self.val_pub_ipv6 = tk.Entry(ip_card_inner, font=("Consolas", 10, "bold"), fg=self.colors["text"], width=28)
        self.val_pub_ipv6.insert(0, "正在获取...")
        self.val_pub_ipv6.config(state="readonly")
        self.val_pub_ipv6.grid(row=0, column=3, sticky=tk.W, padx=(5, 15), pady=3)
        self.setup_ip_entry(self.val_pub_ipv6, "公网 IPv6 地址")
        
        # Detail / Refresh Buttons on the right
        btn_frame = tk.Frame(ip_card_inner, bg=self.colors["card"])
        btn_frame.grid(row=0, column=4, sticky=tk.E, pady=3)
        
        self.btn_ip_refresh = tk.Button(btn_frame, text="刷新", 
                                        bg=self.colors["border"], fg=self.colors["text"],
                                        activebackground=self.colors["accent"], activeforeground="#11111b",
                                        bd=0, relief="flat", padx=10, pady=2, 
                                        font=("Segoe UI", 9, "bold"), cursor="hand2",
                                        command=self.refresh_local_ips)
        self.btn_ip_refresh.pack(side=tk.LEFT, padx=5)
        
        self.btn_ip_detail = tk.Button(btn_frame, text="详细信息", 
                                      bg=self.colors["btn_start"], fg="#11111b",
                                      activebackground=self.colors["btn_start_hover"], activeforeground="#11111b",
                                      bd=0, relief="flat", padx=10, pady=2, 
                                      font=("Segoe UI", 9, "bold"), cursor="hand2",
                                      command=self.show_ip_details)
        self.btn_ip_detail.pack(side=tk.LEFT, padx=5)
        
        ip_card_inner.grid_columnconfigure(4, weight=1)

        # ---------------- MIDDLE CONTAINER ----------------
        middle_container = tk.Frame(main_frame, bg=self.colors["bg"])
        middle_container.pack(fill=tk.BOTH, expand=True)

        # Left Column: Config Panel
        self.left_panel = tk.Frame(middle_container, bg=self.colors["card"],
                                   highlightbackground=self.colors["border"], highlightthickness=1)
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        left_inner = tk.Frame(self.left_panel, bg=self.colors["card"], padx=15, pady=15)
        left_inner.pack(fill=tk.BOTH, expand=True)
        
        # Target Port
        self.lbl_port = tk.Label(left_inner, text="本地目标端口:", font=("Segoe UI", 10, "bold"), 
                            bg=self.colors["card"], fg=self.colors["text"])
        self.lbl_port.pack(anchor=tk.W, pady=(0, 5))
        
        self.port_input = tk.Entry(left_inner, bg=self.colors["input_bg"], fg=self.colors["text"],
                                   insertbackground=self.colors["text"], bd=0, 
                                   highlightthickness=1, highlightbackground=self.colors["border"], 
                                   highlightcolor=self.colors["btn_start"], font=("Consolas", 11), width=15)
        self.port_input.pack(anchor=tk.W, fill=tk.X, pady=(0, 15), ipady=3)
        self.port_input.insert(0, "8000")
        
        # Service Provider Selection
        self.provider_var = tk.StringVar()
        self.lbl_provider = tk.Label(left_inner, text="选择穿透服务商:", font=("Segoe UI", 10, "bold"), 
                                bg=self.colors["card"], fg=self.colors["text"])
        self.lbl_provider.pack(anchor=tk.W, pady=(0, 5))
        
        self.provider_select = ttk.Combobox(left_inner, textvariable=self.provider_var, 
                                            values=["Localtunnel (lt)", "serveo.net (SSH)", "Pinggy.io (SSH)"],
                                            state="readonly", font=("Segoe UI", 10))
        self.provider_select.pack(anchor=tk.W, fill=tk.X, pady=(0, 15))
        self.provider_select.current(0)
        self.provider_select.bind("<<ComboboxSelected>>", lambda e: self.on_provider_change())

        # Dynamic Configurations Container
        self.config_frame = tk.LabelFrame(left_inner, text="服务商配置选项", font=("Segoe UI", 10, "bold"),
                                           bg=self.colors["card"], fg=self.colors["accent"],
                                           highlightbackground=self.colors["border"], highlightthickness=1, 
                                           padx=10, pady=10)
        self.config_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Localtunnel Form Widgets
        self.lt_form = tk.Frame(self.config_frame, bg=self.colors["card"])
        self.lbl_subdomain = tk.Label(self.lt_form, text="子域名 (可选 - 英文/数字):", font=("Segoe UI", 10), 
                                 bg=self.colors["card"], fg=self.colors["text_muted"])
        self.lbl_subdomain.pack(anchor=tk.W, pady=(0, 2))
        self.lt_subdomain = tk.Entry(self.lt_form, bg=self.colors["input_bg"], fg=self.colors["text"],
                                     insertbackground=self.colors["text"], bd=0,
                                     highlightthickness=1, highlightbackground=self.colors["border"],
                                     highlightcolor=self.colors["accent"], font=("Consolas", 10))
        self.lt_subdomain.pack(anchor=tk.W, fill=tk.X, pady=(0, 10), ipady=2)
        
        self.lbl_host = tk.Label(self.lt_form, text="隧道服务器 Host (默认 localtunnel.me):", font=("Segoe UI", 10), 
                            bg=self.colors["card"], fg=self.colors["text_muted"])
        self.lbl_host.pack(anchor=tk.W, pady=(0, 2))
        self.lt_host = tk.Entry(self.lt_form, bg=self.colors["input_bg"], fg=self.colors["text"],
                                insertbackground=self.colors["text"], bd=0,
                                highlightthickness=1, highlightbackground=self.colors["border"],
                                highlightcolor=self.colors["accent"], font=("Consolas", 10))
        self.lt_host.pack(anchor=tk.W, fill=tk.X, pady=(0, 5), ipady=2)
        self.lt_host.insert(0, "https://localtunnel.me")

        # SSH / No Config Informational Form
        self.info_form = tk.Frame(self.config_frame, bg=self.colors["card"])
        self.info_label = tk.Label(self.info_form, text="SSH 隧道无需额外本地配置。\n它直接利用系统内置 SSH 发起转发请求。",
                                   font=("Segoe UI", 10), bg=self.colors["card"], fg=self.colors["text_muted"], justify=tk.LEFT)
        self.info_label.pack(anchor=tk.W, pady=20)

        # Action Button
        self.btn_action = tk.Button(left_inner, text="开启隧道服务", 
                                     bg=self.colors["btn_start"], fg="#11111b",
                                     activebackground=self.colors["btn_start_hover"], activeforeground="#11111b",
                                     bd=0, relief="flat", padx=15, pady=8, 
                                     font=("Segoe UI", 11, "bold"), cursor="hand2",
                                     command=self.toggle_tunnel)
        self.btn_action.pack(fill=tk.X)
        self.btn_action.bind("<Enter>", lambda e: e.widget.config(bg=self.colors["btn_start_hover"] if not self.is_running else self.colors["danger"]))
        self.btn_action.bind("<Leave>", lambda e: e.widget.config(bg=self.colors["btn_start"] if not self.is_running else "#e06c75"))

        # Right Column: Tunnel Status and URL Display
        self.right_panel = tk.Frame(middle_container, bg=self.colors["card"],
                                    highlightbackground=self.colors["border"], highlightthickness=1)
        self.right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        right_inner = tk.Frame(self.right_panel, bg=self.colors["card"], padx=15, pady=15)
        right_inner.pack(fill=tk.BOTH, expand=True)

        # Status Label Frame
        status_frame = tk.Frame(right_inner, bg=self.colors["card"])
        status_frame.pack(fill=tk.X, pady=(0, 12))
        
        self.lbl_status_title = tk.Label(status_frame, text="隧道连接状态:", font=("Segoe UI", 10, "bold"), 
                                    bg=self.colors["card"], fg=self.colors["text"])
        self.lbl_status_title.pack(side=tk.LEFT)
        
        self.lbl_status = tk.Label(status_frame, text="已关闭", font=("Segoe UI", 10, "bold"), 
                                   bg=self.colors["border"], fg=self.colors["text_muted"], padx=8, pady=3)
        self.lbl_status.pack(side=tk.LEFT, padx=10)

        # Local Port Status Label Frame
        port_status_frame = tk.Frame(right_inner, bg=self.colors["card"])
        port_status_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.lbl_port_status_title = tk.Label(port_status_frame, text="本地端口检测:", font=("Segoe UI", 10, "bold"), 
                                         bg=self.colors["card"], fg=self.colors["text"])
        self.lbl_port_status_title.pack(side=tk.LEFT)
        
        self.lbl_port_status = tk.Label(port_status_frame, text="未启动", font=("Segoe UI", 10, "bold"), 
                                        bg=self.colors["border"], fg=self.colors["text_muted"], padx=8, pady=3)
        self.lbl_port_status.pack(side=tk.LEFT, padx=10)

        # URL Output Card
        url_card = tk.Frame(right_inner, bg=self.colors["input_bg"], 
                            highlightbackground=self.colors["border"], highlightthickness=1)
        url_card.pack(fill=tk.X, pady=(0, 20))
        
        url_card_inner = tk.Frame(url_card, bg=self.colors["input_bg"], padx=15, pady=15)
        url_card_inner.pack(fill=tk.X)
        
        self.lbl_url_title = tk.Label(url_card_inner, text="生成的公共访问链接:", font=("Segoe UI", 10), 
                                 bg=self.colors["input_bg"], fg=self.colors["text_muted"])
        self.lbl_url_title.pack(anchor=tk.W, pady=(0, 5))
        
        self.lbl_url_val = tk.Label(url_card_inner, text="等待隧道启动...", font=("Consolas", 12, "underline"), 
                                    bg=self.colors["input_bg"], fg=self.colors["text_muted"], cursor="hand2")
        self.lbl_url_val.pack(anchor=tk.W, fill=tk.X, pady=5)
        self.lbl_url_val.bind("<Button-1>", lambda e: self.open_in_browser())
        
        # URL interactive buttons
        url_btn_frame = tk.Frame(right_inner, bg=self.colors["card"])
        url_btn_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.btn_copy = tk.Button(url_btn_frame, text="复制链接", 
                                   bg=self.colors["border"], fg=self.colors["text"],
                                   activebackground=self.colors["btn_start"], activeforeground="#11111b",
                                   bd=0, relief="flat", padx=12, pady=5, 
                                   font=("Segoe UI", 9, "bold"), cursor="hand2",
                                   command=self.copy_url)
        self.btn_copy.pack(side=tk.LEFT, padx=(0, 10))
        
        self.btn_browser = tk.Button(url_btn_frame, text="浏览器打开", 
                                      bg=self.colors["border"], fg=self.colors["text"],
                                      activebackground=self.colors["btn_start"], activeforeground="#11111b",
                                      bd=0, relief="flat", padx=12, pady=5, 
                                      font=("Segoe UI", 9, "bold"), cursor="hand2",
                                      command=self.open_in_browser)
        self.btn_browser.pack(side=tk.LEFT)
        
        # Disabled buttons until URL found
        self.btn_copy.config(state="disabled")
        self.btn_browser.config(state="disabled")

        # Provider instructions tip box
        self.tip_card = tk.LabelFrame(right_inner, text="使用说明及提示", font=("Segoe UI", 10, "bold"),
                                      bg=self.colors["card"], fg=self.colors["accent"],
                                      highlightbackground=self.colors["border"], highlightthickness=1, 
                                      padx=10, pady=10)
        self.tip_card.pack(fill=tk.BOTH, expand=True)
        
        self.lbl_tip_desc = tk.Label(self.tip_card, text="提示信息加载中...", font=("Segoe UI", 10),
                                     bg=self.colors["card"], fg=self.colors["text_muted"], justify=tk.LEFT, wraplength=320)
        self.lbl_tip_desc.pack(anchor=tk.W, fill=tk.BOTH, expand=True)

        # ---------------- SECTION 3: CONSOLE LOG PANEL ----------------
        console_frame = tk.Frame(main_frame, bg=self.colors["bg"])
        console_frame.pack(fill=tk.X, pady=(15, 0))
        
        console_lbl_frame = tk.Frame(console_frame, bg=self.colors["bg"])
        console_lbl_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.console_lbl = tk.Label(console_lbl_frame, text="隧道控制台标准输出 (实时)", font=("Segoe UI", 10, "bold"), 
                               bg=self.colors["bg"], fg=self.colors["text_muted"])
        self.console_lbl.pack(side=tk.LEFT)
        
        self.console = tk.Text(console_frame, height=6, bg=self.colors["input_bg"], fg="#a6e3a1",
                               bd=0, highlightthickness=1, highlightbackground=self.colors["border"],
                               font=("Consolas", 9), wrap=tk.WORD, state="disabled")
        self.console.pack(fill=tk.X)

    def on_provider_change(self):
        """Hide/Show configuration fields based on service provider selected."""
        provider = self.provider_var.get()
        
        # Clear forms
        self.lt_form.pack_forget()
        self.info_form.pack_forget()
        
        if "Localtunnel" in provider:
            self.lt_form.pack(fill=tk.X)
            self.lbl_tip_desc.config(text=self.get_text("tip_lt"))
        else: # SSH tunnels (serveo.net, Pinggy.io)
            self.info_form.pack(fill=tk.X)
            if "serveo.net" in provider:
                self.lbl_tip_desc.config(text=self.get_text("tip_serveo"))
            else: # Pinggy.io
                self.lbl_tip_desc.config(text=self.get_text("tip_pinggy"))

    def toggle_tunnel(self):
        """Start or Stop the tunnel process."""
        if self.is_running:
            self.stop_tunnel()
        else:
            self.start_tunnel()

    def ensure_ssh_key(self):
        """Check if at least one SSH key exists, if not generate a default one."""
        ssh_dir = os.path.expanduser("~/.ssh")
        if not os.path.exists(ssh_dir):
            try:
                os.makedirs(ssh_dir, exist_ok=True)
            except Exception as e:
                self.log(f"Create .ssh dir failed: {e}" if self.current_lang == 'en' else f"创建 .ssh 目录失败: {e}")
                return False

        # Common SSH key files
        key_files = ["id_rsa", "id_ed25519", "id_ecdsa", "id_dsa"]
        has_key = False
        for kf in key_files:
            if os.path.exists(os.path.join(ssh_dir, kf)):
                has_key = True
                break

        if not has_key:
            self.log(self.get_text("log_ssh_key_gen"))
            key_path = os.path.join(ssh_dir, "id_ed25519")
            try:
                # Use subprocess to run ssh-keygen without window to prevent flash
                res = subprocess.run(
                    ["ssh-keygen", "-t", "ed25519", "-f", key_path, "-N", ""],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                )
                if res.returncode == 0:
                    self.log(self.get_text("log_ssh_key_ed25519_ok"))
                    return True
                else:
                    self.log(self.get_text("log_ssh_key_ed25519_err", stderr=res.stderr.strip()))
                    key_path_rsa = os.path.join(ssh_dir, "id_rsa")
                    res_rsa = subprocess.run(
                        ["ssh-keygen", "-t", "rsa", "-b", "2048", "-f", key_path_rsa, "-N", ""],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                    )
                    if res_rsa.returncode == 0:
                        self.log(self.get_text("log_ssh_key_rsa_ok"))
                        return True
                    else:
                        self.log(self.get_text("log_ssh_key_rsa_err", stderr=res_rsa.stderr.strip()))
            except Exception as e:
                self.log(self.get_text("log_ssh_key_err", e=e))
                return False
        return True

    def start_tunnel(self):
        port = self.port_input.get().strip()
        if not port or not port.isdigit():
            messagebox.showerror(self.get_text("err_title"), self.get_text("err_invalid_port"))
            return
            
        provider = self.provider_var.get()
        cmd = ""
        url_regex = ""

        if "Localtunnel" in provider:
            sub = self.lt_subdomain.get().strip()
            host = self.lt_host.get().strip()
            cmd = f"npx localtunnel --port {port}"
            if sub:
                cmd += f" --subdomain {sub}"
            if host:
                cmd += f" --host {host}"
            url_regex = r"your url is:\s+(https?://[^\s]+)"
            
        elif "serveo.net" in provider:
            cmd = f"ssh -o StrictHostKeyChecking=no -R 80:127.0.0.1:{port} serveo.net"
            url_regex = r"from\s+(https?://[^\s]+)"
            
        elif "Pinggy.io" in provider:
            cmd = f"ssh -p 443 -o StrictHostKeyChecking=no -R0:localhost:{port} free.pinggy.io"
            url_regex = r"(https://[a-zA-Z0-9\-\.]+\.pinggy(?:-free)?\.(?:link|net))"

        self.log(self.get_text("log_starting_tunnel", provider=provider, port=port))
        self.log(self.get_text("log_exec_cmd", cmd=cmd))

        self.is_running = True
        self.btn_action.config(text=self.get_text("btn_stop_tunnel"), bg="#e06c75")
        self.lbl_status.config(text=self.get_text("status_connecting"), bg=self.colors["warning"], fg="#11111b")
        self.lbl_url_val.config(text=self.get_text("url_val_generating"), fg=self.colors["text_muted"])
        
        # Save config when starting the tunnel
        self.save_config()

        # Disable configs while running
        self.port_input.config(state="disabled")
        self.provider_select.config(state="disabled")
        self.lt_subdomain.config(state="disabled")
        self.lt_host.config(state="disabled")

        def on_url_found(url):
            self.public_url = url
            self.log(self.get_text("log_tunnel_ok", url=url))
            
            def update():
                self.lbl_url_val.config(text=url, fg=self.colors["success"])
                self.lbl_status.config(text=self.get_text("status_running"), bg=self.colors["success"], fg="#11111b")
                self.btn_copy.config(state="normal")
                self.btn_browser.config(state="normal")
                
            self.root.after(0, update)

        def on_output(line):
            def write():
                self.console.config(state="normal")
                self.console.insert(tk.END, line)
                self.console.see(tk.END)
                self.console.config(state="disabled")
            self.root.after(0, write)

        def on_exit(code):
            self.log(self.get_text("log_tunnel_exit", code=code))
            self.root.after(0, self.reset_ui_stopped)

        def worker():
            try:
                if "SSH" in provider:
                    self.ensure_ssh_key()
                # Spawn subprocess locally
                proc = subprocess.Popen(
                    cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    stdin=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                )
                self.active_proc = proc
                
                url_found = False
                for line in proc.stdout:
                    if not self.is_running:
                        break
                    on_output(line)
                    if not url_found:
                        match = re.search(url_regex, line)
                        if match:
                            url = match.group(1).strip()
                            on_url_found(url)
                            url_found = True
                            
                proc.wait()
                if self.is_running:
                    on_exit(proc.returncode)
            except Exception as e:
                # Only log and raise exit code if the tunnel wasn't stopped intentionally
                if self.is_running:
                    on_output(f"Exception starting tunnel: {e}\n" if self.current_lang == 'en' else f"启动隧道发生异常: {e}\n")
                    on_exit(-1)

        self.tunnel_thread = threading.Thread(target=worker, daemon=True)
        self.tunnel_thread.start()
        
        # Start checking local target port status dynamically
        self.root.after(100, self.poll_port_status)

    def stop_tunnel(self):
        if not self.is_running:
            return
            
        self.log(self.get_text("log_stopping_tunnel"))
        self.is_running = False
        
        # Kill the subprocess tree cleanly on Windows to prevent orphan node/ssh processes
        if self.active_proc:
            try:
                if os.name == 'nt':
                    # Windows process tree kill
                    subprocess.run(f"taskkill /F /T /PID {self.active_proc.pid}", 
                                   shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    self.active_proc.terminate()
            except Exception as e:
                self.log(self.get_text("log_stop_err", e=e))
            self.active_proc = None

        self.reset_ui_stopped()
        self.log(self.get_text("log_stopped_ok"))

    def reset_ui_stopped(self):
        """Reset elements back to stopped state."""
        self.is_running = False
        self.public_url = None
        self.active_proc = None
        
        self.lbl_status.config(text=self.get_text("status_closed"), bg=self.colors["border"], fg=self.colors["text_muted"])
        self.lbl_port_status.config(text=self.get_text("port_status_inactive"), bg=self.colors["border"], fg=self.colors["text_muted"])
        self.lbl_url_val.config(text=self.get_text("url_val_waiting"), fg=self.colors["text_muted"])
        self.btn_action.config(text=self.get_text("btn_start_tunnel"), bg=self.colors["btn_start"])
        
        self.btn_copy.config(state="disabled")
        self.btn_browser.config(state="disabled")
        
        # Re-enable inputs
        self.port_input.config(state="normal")
        self.provider_select.config(state="normal")
        self.lt_subdomain.config(state="normal")
        self.lt_host.config(state="normal")

    def copy_url(self):
        if self.public_url:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.public_url)
            self.log(self.get_text("log_copied"))
            messagebox.showinfo(self.get_text("success_title"), self.get_text("success_copy_url"))

    def open_in_browser(self):
        if self.public_url:
            webbrowser.open(self.public_url)
            self.log(self.get_text("log_browser_opened", url=self.public_url))

    def refresh_local_ips(self):
        """Asynchronously refresh the public IPv4 and IPv6 of the local machine."""
        try:
            if self.root and self.root.winfo_exists():
                self.btn_ip_refresh.config(state="disabled", text=self.get_text("btn_refresh_loading"))
                self.set_entry_text(self.val_pub_ipv4, self.get_text("getting_ip"), self.colors["text_muted"])
                self.set_entry_text(self.val_pub_ipv6, self.get_text("getting_ip"), self.colors["text_muted"])
        except Exception:
            pass
        self.log(self.get_text("log_detect_ip"))
        
        def worker():
            ipv4 = ip_service.fetch_public_ip()
            self.local_public_ipv4 = ipv4
            ipv4_show = ipv4 if ipv4 else self.get_text("get_ip_failed_offline")
            ipv4_color = self.colors["accent"] if ipv4 else self.colors["danger"]
            self.root.after(0, lambda: self.set_entry_text(self.val_pub_ipv4, ipv4_show, ipv4_color))
            if ipv4:
                self.log(self.get_text("log_found_ipv4", ip=ipv4))
            else:
                self.log(self.get_text("log_failed_ipv4"))
                
            ipv6 = ip_service.fetch_public_ipv6()
            self.local_public_ipv6 = ipv6
            ipv6_show = ipv6 if ipv6 else self.get_text("get_ip_not_assigned")
            ipv6_color = self.colors["accent"] if ipv6 else self.colors["text_muted"]
            self.root.after(0, lambda: self.set_entry_text(self.val_pub_ipv6, ipv6_show, ipv6_color))
            if ipv6:
                self.log(self.get_text("log_found_ipv6", ip=ipv6))
            else:
                self.log(self.get_text("log_failed_ipv6"))
                
            def finish():
                try:
                    if self.root and self.root.winfo_exists():
                        self.btn_ip_refresh.config(state="normal", text=self.get_text("btn_refresh"))
                except Exception:
                    pass
            self.root.after(0, finish)
            
        threading.Thread(target=worker, daemon=True).start()

    def show_ip_details(self):
        """Pop up a new Toplevel window to show the full IPGetApp UI."""
        popup = tk.Toplevel(self.root)
        IPGetApp(popup, lang=self.current_lang)

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
                    self.log(self.get_text("log_copied"))
                    flash_feedback()
                    show_toast(self.get_text("toast_copied"))
            except Exception as e:
                self.log(self.get_text("log_copy_fail", e=e))

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
        
        # Center the dialog relative to root
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
                              bg=self.colors["btn_start"], fg="#11111b",
                              activebackground=self.colors["btn_start_hover"], activeforeground="#11111b",
                              bd=0, relief="flat", padx=20, pady=6, 
                              font=("Segoe UI", 9, "bold"), cursor="hand2",
                              command=dialog.destroy)
        btn_close.pack(anchor=tk.CENTER)

    def poll_port_status(self):
        """Periodically check the status of the local target port while the tunnel is running."""
        if not self.is_running:
            return
            
        port = self.port_input.get().strip()
        if port and port.isdigit():
            def worker():
                is_open = ip_service.check_port_listening(port)
                
                def update():
                    if not self.is_running:
                        return
                    if is_open:
                        self.lbl_port_status.config(
                            text=self.get_text("port_status_listening", port=port), 
                            bg=self.colors["success"], fg="#11111b"
                        )
                    else:
                        self.lbl_port_status.config(
                            text=self.get_text("port_status_not_listening", port=port), 
                            bg=self.colors["danger"], fg="#11111b"
                        )
                
                self.root.after(0, update)
                
            threading.Thread(target=worker, daemon=True).start()
            
        # Re-schedule check in 3 seconds
        self.root.after(3000, self.poll_port_status)

if __name__ == "__main__":
    root = tk.Tk()
    app = TunnelApp(root)
    # Ensure subprocesses are cleaned up on window close
    def on_closing():
        if app.is_running:
            app.stop_tunnel()
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
