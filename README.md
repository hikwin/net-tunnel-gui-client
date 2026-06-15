# IPGet & Intranet Tunnel GUI Client (内网穿透与双栈网络诊断工具)

本软件是一款专为开发者设计的极简、轻量级**内网穿透管理**与**双栈网络诊断** GUI 客户端。不仅支持一键将本地开发端口暴露到公网（调试 API, Web 网页, Webhook），同时提供高精度的 IPv4/IPv6 公网 IP 查询、纯真局域网归属地比对和实时本地服务端口健康监控。

---

## 🌟 核心功能

### 1. 多通道内网穿透
- **Localtunnel (npx)**: 一键调用 Node 环境穿透，支持自定义子域名及穿透 Host 服务端。
- **Serveo (SSH)**: 基于系统内置 OpenSSH 客户端的免安装穿透，自动解析生成的代理链接。
- **Pinggy.io (SSH)**: 高性能且防火墙友好的纯 SSH 穿透通道，自动生成安全加密的 `.pinggy.link` 地址。
- **SSH 密钥自动建构**: 免去密码输入，自动在 `~/.ssh/` 下生成 Ed25519 或 RSA 安全密钥对以供免密握手。

### 2. 实时本地服务状态监控
- 隧道启动后，后台线程每 **3秒** 轮询检测一次本地目标端口（通过轻量级 TCP 通讯连通性测试）。
- **正常监听中** (绿色指示灯): 您的本地服务已经正常启动并响应。
- **未检测到服务** (红色预警灯): 提醒您及时在本地启动对应端口的服务，以免穿透页面显示 502/504 错误。

### 3. IPv4 / IPv6 双栈 IP 检测
- 启动及刷新时，异步并发获取主机的**局域网 IPv4/IPv6** 以及 **公网 IPv4/IPv6**。
- 支持无 IPv6 环境下的智能平滑降级（显示为`未分配 / 禁用`），避免线程卡死与 UI 阻塞。

### 4. 归属地双重核验比对
- 集成纯真 IP 数据库解析模块（`qqwry_parser.py`），直接在本地对 IPv4 进行检索。
- 联动网络 API 地理位置接口对查询结果进行双重核验：
  - **结果一致**: 本地数据库解析与网络接口高度吻合（绿色亮边提示）。
  - **存在差异**: 本地数据可能过期或网络解析出现分歧（红色边框预警）。
  - **Chunzhen 数据库一键更新**: 自带数据库版本号，支持直接从官方镜像站异步多线程断点下载最新的 `qqwry.dat` 文件。

### 5. 精细化 UI 体验
- **深色美学设计**: 沉浸式暗色猫头鹰配色体系，主次分明。
- **智能选择与自动复制**: 
  - IP 地址文本框为平直且背景融合的 `tk.Entry` 控件，支持鼠标拖拽选择局部文本。
  - 单击或 Tab 键切入输入框时，**自动全选**整个 IP 地址。
  - 双击 IP 地址或右键点击“复制全部”时，复制数据并触发 **2秒 自动消失的 "复制成功!" toast 气泡通知**，伴随输入框短暂绿光闪烁，告别粗鲁的弹框打扰。
- **帮助与隐私窗口**: 点击右上角的 `❓ 帮助说明` 即可展示软件作用、100% 纯本地运行的隐私声明和免责声明。
- **作者链接**: 标题后方附带作者 `hik` 链接，点击直达主页：[https://hik.win](https://hik.win)。

---

## 🛠️ 环境依赖

1. **Python 环境**: Python 3.10+
2. **SSH 客户端**: 系统已配置并开启内置的 `ssh` 工具（Serveo & Pinggy.io 依赖）。
3. **Node.js**: 系统支持并已安装 `npx` 工具（Localtunnel 依赖）。

---

## 🚀 运行说明

### 方法 A：直接运行 Python 源码
```bash
# 克隆/下载项目后，切换到对应目录
python tunnel_gui.py
```

### 方法 B：运行打包好的绿色单文件程序
直接双击运行编译完成的 `dist/tunnel_gui.exe` 即可（无需本地配置 Python 环境）。

---

## 📦 打包编译配置

本项目完全兼容 **PyInstaller** 进行打包。为了防止数据文件丢失及下载目录错乱，程序采用了智能的**双路径解析策略**：
1. **打包内置**: 默认内置的 `qqwry.dat` 将会随打包嵌入 `.exe`，解压至临时运行时路径 `sys._MEIPASS`。
2. **持久化下载**: 当用户点击“更新数据库”下载最新的数据库时，程序会自动将其写入到**与运行的 `.exe` 同级的永久文件夹**下。此后启动将优先加载该永久数据库，防止更新丢失。

**PyInstaller 打包命令**:
```bash
python -m PyInstaller --onefile --noconsole --add-data "qqwry.dat;." tunnel_gui.py
```
- `--onefile`: 编译为单个独立的可执行文件。
- `--noconsole`: 运行时不显示后台 CMD 控制台窗口。
- `--add-data "qqwry.dat;."`: 将当前目录的纯真 IP 数据库打包进可执行文件的根目录。

---

## 📄 隐私与安全声明

* **100% 隐私透明**: 本软件为纯本地客户端工具。我们承诺不收集、不中转、不上传您的任何网络访问历史、IP 地址或隧道流量。
* **直接通信**: 所有的 IP 归属地与网络接口查询均由您的本地设备直连第三方公开 API 镜像，保证数据传输链纯净安全。

---

# IPGet & Intranet Tunnel GUI Client

This software is a minimalist, lightweight **intranet penetration management** and **dual-stack network diagnostics** GUI client designed for developers. It supports exposing local development ports to the public internet (for debugging APIs, web pages, and webhooks) with one click, while providing high-precision IPv4/IPv6 public IP queries, local Chunzhen IP database IP lookup comparisons, and real-time local port health monitoring.

---

## 🌟 Core Features

### 1. Multi-Channel Intranet Penetration
- **Localtunnel (npx)**: One-click tunnel initialization using Node.js environment, supporting custom subdomains and custom host servers.
- **Serveo (SSH)**: No-installation tunnel using the built-in system OpenSSH client, automatically parsing generated proxy URLs.
- **Pinggy.io (SSH)**: High-performance and firewall-friendly pure SSH tunnel, generating secure encrypted `.pinggy.link` URLs.
- **Automatic SSH Key Construction**: Generates Ed25519 or RSA key pairs in `~/.ssh/` automatically for passwordless handshakes.

### 2. Real-Time Local Port Monitoring
- Once the tunnel starts, a background thread checks the target local port status every **3 seconds** (using a lightweight TCP connectivity check).
- **Listening** (Green badge): Your local service is running and responding.
- **No Service Detected** (Red badge): Reminds you to start the local service on that port to prevent 502/504 errors.

### 3. IPv4 / IPv6 Dual-Stack IP Detection
- Asynchronously queries **Local IPv4/IPv6** and **Public IPv4/IPv6** on startup and refresh.
- Supports smooth fallback when IPv6 is unavailable (displays `Not Assigned / Disabled`) to prevent thread blocks and UI freezes.

### 4. Dual-Verification IP Geolocation
- Integrates Chunzhen IP database reader (`qqwry_parser.py`) for offline IPv4 lookup.
- Cross-references offline lookups against online API geolocation queries:
  - **Consistent**: Local database matches online API (highlighted with a green border).
  - **Discrepancy**: Warns if local data is outdated or doesn't match the API (highlighted with a red border).
  - **One-Click DB Update**: Supports downloading/updating the latest `qqwry.dat` from official mirrors with a multi-threaded progress bar.

### 5. Premium UI Experience
- **Dark Owl Theme**: Aesthetic dark theme with visual hierarchy.
- **Selectable & Copiable text**: IP addresses are in flat `tk.Entry` fields allowing text selection, auto-selecting on click/focus.
- **Double-click copy**: Automatically copies text and shows a **2-second "Copied!" toast notification** and a green flash effect, replacing intrusive alerts.
- **Help & Privacy Modal**: Accessible from the top right `❓ Help & Info` displaying details and a 100% local-running privacy statement.
- **Author info**: Title header includes a link to author `hik`'s homepage: [https://hik.win](https://hik.win).
- **Language Switcher**: Built-in dynamic language switching (中文 / English) that updates the entire UI instantly.
- **Settings Persistence**: Saves current language, target port, service provider, localtunnel subdomain, and host to `config.json` inside the application directory, auto-loading them on start.

---

## 🛠️ Requirements

1. **Python Environment**: Python 3.10+
2. **SSH Client**: Built-in system `ssh` command enabled (required by Serveo & Pinggy.io).
3. **Node.js**: `npx` command enabled (required by Localtunnel).

---

## 🚀 Running the App

### Method A: Run source code directly
```bash
# Clone/download project, navigate to the folder
python tunnel_gui.py
```

### Method B: Run packaged standalone executable
Double-click `dist/tunnel_gui.exe` (no Python installation required).

---

## 📦 Packaging & Compilation

This project is fully compatible with **PyInstaller**. It uses a **dual-path lookup strategy** to manage the IP database:
1. **Bundled DB**: The default `qqwry.dat` is embedded inside the `.exe` and extracted to the temporary folder `sys._MEIPASS` at runtime.
2. **Persistent DB**: When the database is updated/downloaded, it is saved directly to the permanent directory alongside the `.exe`. Subsequent launches will load this updated database.

**PyInstaller packaging command**:
```bash
python -m PyInstaller --onefile --noconsole --add-data "qqwry.dat;." tunnel_gui.py
```
- `--onefile`: Generates a single standalone executable.
- `--noconsole`: Hides the command line window.
- `--add-data "qqwry.dat;."`: Bundles the local IP database into the executable root.

---

## 📄 Privacy & Security Policy

* **100% Privacy**: This tool runs entirely on your local machine. We do not collect, proxy, or upload your IP addresses, network traffic, or port configurations.
* **Direct Connection**: Geolocation lookups and tunnel connections are established directly between your computer and the providers/APIs, ensuring pure and secure data transmission.

