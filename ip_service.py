import urllib.request
import json
import socket
import os
import re

def http_get(url, timeout=5):
    """
    Perform a HTTP GET request using urllib.request.
    Automatically handles GBK / UTF-8 encoding decoding based on headers.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    if 'pconline.com.cn' in url:
        headers['Referer'] = 'http://whois.pconline.com.cn/'
        
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as response:
        content_type = response.headers.get('Content-Type', '')
        # Determine encoding from Content-Type or default to utf-8
        encoding = 'utf-8'
        if 'gbk' in content_type.lower() or 'gb2312' in content_type.lower():
            encoding = 'gbk'
        elif 'utf-8' in content_type.lower():
            encoding = 'utf-8'
        
        data = response.read()
        try:
            return data.decode(encoding, errors='replace')
        except Exception:
            # Fallback if detection failed
            try:
                return data.decode('utf-8')
            except Exception:
                return data.decode('gbk', errors='replace')

def get_local_ip():
    """Get the local private IP address of this machine."""
    try:
        # Connect to a public DNS server to determine default gateway interface
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "127.0.0.1"

def fetch_public_ip():
    """
    Fetch the public IP address of this machine from multiple providers.
    """
    providers = [
        ("https://api.ipify.org?format=json", "ip"),
        ("https://httpbin.org/ip", "origin"),
        ("http://ip-api.com/json/", "query"),
        ("http://whois.pconline.com.cn/ipJson.jsp?json=true", "ip")
    ]
    for url, key in providers:
        try:
            res_text = http_get(url, timeout=4)
            data = json.loads(res_text)
            ip = data.get(key)
            if ip:
                # If httpbin returns multiple IPs, grab the first one
                if "," in ip:
                    ip = ip.split(",")[0].strip()
                return ip.strip()
        except Exception as e:
            print(f"Failed to fetch public IP from {url}: {e}")
    return None

def query_network_location(ip):
    """
    Query the geolocation of an IP address using free public APIs.
    Combines/falls back to multiple APIs for the best result.
    """
    results = {}

    # 1. Try ip-api.com (excellent for global and detailed region/ISP mapping)
    try:
        url = f"http://ip-api.com/json/{ip}?lang=zh-CN"
        res_text = http_get(url, timeout=4)
        data = json.loads(res_text)
        if data.get("status") == "success":
            country = data.get("country", "")
            region = data.get("regionName", "")
            city = data.get("city", "")
            isp = data.get("isp", "")
            
            # Format nicely
            parts = [country, region, city]
            # De-duplicate adjacent equal items (e.g. 北京 北京)
            clean_parts = []
            for p in parts:
                if p and (not clean_parts or clean_parts[-1] != p):
                    clean_parts.append(p)
            
            loc_str = " ".join(clean_parts)
            if isp:
                loc_str += f" ({isp})"
            results["ip-api"] = loc_str
    except Exception as e:
        print(f"ip-api.com query failed for {ip}: {e}")

    # 2. Try whois.pconline.com.cn (excellent for Chinese domestic IP detail)
    try:
        url = f"http://whois.pconline.com.cn/ipJson.jsp?ip={ip}&json=true"
        res_text = http_get(url, timeout=4)
        data = json.loads(res_text)
        addr = data.get("addr")
        if addr:
            results["pconline"] = addr.strip()
    except Exception as e:
        print(f"whois.pconline.com.cn query failed for {ip}: {e}")

    # Decision logic:
    # If domestic Chinese IP, pconline is generally more precise down to district/operator.
    # If international, pconline can be inaccurate (often saying e.g. "美国 广东省广州市"),
    # so we prioritize ip-api for international IPs.
    ip_api_res = results.get("ip-api", "")
    pconline_res = results.get("pconline", "")
    
    if ip_api_res:
        # Check if the country is outside China
        is_china = ip_api_res.startswith("中国")
        if is_china and pconline_res:
            return pconline_res
        return ip_api_res
    elif pconline_res:
        return pconline_res
        
    return "未知网络归属地"

def check_consistency(local_loc, net_loc):
    """
    Check if the local and network locations are consistent.
    Performs smart keyword overlap matching to avoid false differences
    caused by spacing, language (English/Chinese), or administrative suffix (省/市).
    """
    if not local_loc or not net_loc:
        return True
        
    # Strip spaces, punctuation, casing
    def clean(s):
        s = s.lower()
        # Remove brackets and symbols
        s = re.sub(r'[\(\)\[\]\-\,\s]', '', s)
        # Remove common Chinese administrative suffixes
        for suffix in ["省", "市", "区", "县"]:
            s = s.replace(suffix, "")
        # Remove common ISP operators
        for operator in ["联通", "电信", "移动", "铁通", "教育网", "广电", "长城宽带", "unicom", "telecom", "mobile"]:
            s = s.replace(operator, "")
        # Remove database signatures
        s = s.replace("cz88.net", "").replace("纯真网络", "")
        return s

    c_local = clean(local_loc)
    c_net = clean(net_loc)
    
    if not c_local or not c_net:
        return True
        
    # If they are identical or one contains the other, they are consistent
    if c_local in c_net or c_net in c_local:
        return True
        
    # Check keyword overlap (e.g. country, province, or city keywords)
    # Extract consecutive Chinese/alphabetic segments of length >= 2
    words_local = set(re.findall(r'[\u4e00-\u9fa5]{2,}|[a-zA-Z]{3,}', c_local))
    words_net = set(re.findall(r'[\u4e00-\u9fa5]{2,}|[a-zA-Z]{3,}', c_net))
    
    # If there is at least one major geographical overlap (like "广州", "美国", etc.), count as consistent
    if words_local & words_net:
        return True
        
    return False

def download_db(target_path, progress_callback=None, cancel_event=None):
    """
    Download the qqwry.dat database file from community mirrors.
    Includes thread cancellation check and progress callback.
    """
    urls = [
        "https://github.com/metowolf/qqwry.dat/releases/latest/download/qqwry.dat",
        "https://cdn.jsdelivr.net/gh/metowolf/qqwry.dat@master/qqwry.dat",
        "https://raw.githubusercontent.com/metowolf/qqwry.dat/master/qqwry.dat"
    ]
    
    last_error = None
    for url in urls:
        if cancel_event and cancel_event.is_set():
            return False
            
        try:
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req, timeout=12) as response:
                total_size = int(response.headers.get('content-length', 0))
                
                temp_path = target_path + ".tmp"
                downloaded = 0
                block_size = 1024 * 64 # 64KB chunks
                
                with open(temp_path, 'wb') as f:
                    while True:
                        if cancel_event and cancel_event.is_set():
                            f.close()
                            if os.path.exists(temp_path):
                                os.remove(temp_path)
                            return False
                            
                        chunk = response.read(block_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback and total_size > 0:
                            percent = (downloaded / total_size) * 100
                            progress_callback(percent, downloaded, total_size)
                            
                # Success! Replace final file
                if os.path.exists(target_path):
                    os.remove(target_path)
                os.rename(temp_path, target_path)
                return True
        except Exception as e:
            print(f"Failed to download from {url}: {e}")
            last_error = e
            
    if last_error:
        raise last_error
    return False

def get_local_ipv6():
    """Get the local private/public IPv6 address of this machine."""
    try:
        s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        # Connect to a public DNS IPv6 address
        s.connect(("2001:4860:4860::8888", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        try:
            for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET6):
                ip = info[4][0]
                if not ip.startswith("fe80:") and ip != "::1":
                    return ip
            return None
        except Exception:
            return None

def fetch_public_ipv6():
    """Fetch the public IPv6 address of this machine from multiple providers."""
    providers = [
        ("https://api6.ipify.org?format=json", "ip"),
        ("https://v6.ident.me", None)
    ]
    for url, key in providers:
        try:
            res_text = http_get(url, timeout=4)
            if key:
                data = json.loads(res_text)
                ip = data.get(key)
            else:
                ip = res_text.strip()
            if ip:
                return ip.strip()
        except Exception as e:
            print(f"Failed to fetch public IPv6 from {url}: {e}")
    return None

def check_port_listening(port):
    """Check if a local port is currently listening on localhost."""
    try:
        # Connect to 127.0.0.1 on the specified port
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        # connect_ex returns 0 if successful, which means the port is open and listening
        result = s.connect_ex(('127.0.0.1', int(port)))
        s.close()
        return result == 0
    except Exception:
        return False


