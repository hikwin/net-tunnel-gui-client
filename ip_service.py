import urllib.request
import json
import socket
import os
import re
import concurrent.futures

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

def fetch_single_ip(url, key, timeout=4):
    """Fetch IP from a single provider."""
    try:
        res_text = http_get(url, timeout=timeout)
        if not res_text:
            return None
        res_text = res_text.strip()
        if key:
            data = json.loads(res_text)
            ip = data.get(key)
        else:
            ip = res_text
        if ip:
            if "," in ip:
                ip = ip.split(",")[0].strip()
            ip = ip.strip()
            if "." in ip or ":" in ip:
                return ip
    except Exception:
        pass
    return None

def fetch_public_ip():
    """
    Fetch the public IP address of this machine from multiple providers in parallel.
    """
    providers = [
        ("https://api.ipify.org?format=json", "ip"),
        ("https://httpbin.org/ip", "origin"),
        ("http://ip-api.com/json/", "query"),
        ("http://ipinfo.io/ip", None)
    ]
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(providers)) as executor:
        futures = {
            executor.submit(fetch_single_ip, url, key, 4): url
            for url, key in providers
        }
        for future in concurrent.futures.as_completed(futures):
            try:
                ip = future.result()
                if ip:
                    return ip
            except Exception:
                pass
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
    except Exception:
        pass

    # 2. Try Baidu OpenData IP API (excellent for Chinese domestic IP detail, replacement for whois.pconline.com.cn)
    try:
        url = f"http://opendata.baidu.com/api.php?query={ip}&co=&resource_id=6006&oe=utf-8"
        res_text = http_get(url, timeout=4)
        data = json.loads(res_text)
        if data.get("status") == "0" and data.get("data"):
            location = data["data"][0].get("location")
            if location:
                results["pconline"] = location.strip()
    except Exception:
        pass

    # Decision logic:
    # If domestic Chinese IP, pconline (now Baidu) is generally more precise down to district/operator.
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
        "https://gh-proxy.com/https://github.com/metowolf/qqwry.dat/releases/latest/download/qqwry.dat",
        "https://ghproxy.net/https://github.com/metowolf/qqwry.dat/releases/latest/download/qqwry.dat",
        "https://mirror.ghproxy.com/https://github.com/metowolf/qqwry.dat/releases/latest/download/qqwry.dat",
        "https://github.com/metowolf/qqwry.dat/releases/latest/download/qqwry.dat",
        "https://cdn.jsdelivr.net/gh/metowolf/qqwry.dat@master/qqwry.dat",
        "https://raw.githubusercontent.com/metowolf/qqwry.dat/master/qqwry.dat"
    ]
    
    last_error = None
    for url in urls:
        if cancel_event and cancel_event.is_set():
            return False
            
        try:
            print(f"Trying to download database from {url}...")
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            import ssl
            ssl_context = ssl._create_unverified_context()
            
            with urllib.request.urlopen(req, timeout=30, context=ssl_context) as response:
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
        print("All direct and mirror download attempts failed. Trying to use system curl as fallback...")
        for url in urls:
            if cancel_event and cancel_event.is_set():
                return False
            try:
                print(f"Trying to download database via curl from {url}...")
                temp_path = target_path + ".tmp"
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                
                curl_bin = "curl.exe" if os.name == 'nt' else "curl"
                cmd = f'{curl_bin} --ssl-no-revoke -L --fail --connect-timeout 20 -o "{temp_path}" "{url}"'
                
                import subprocess
                res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                     creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                if res.returncode == 0 and os.path.exists(temp_path) and os.path.getsize(temp_path) > 5000000:
                    if os.path.exists(target_path):
                        os.remove(target_path)
                    os.rename(temp_path, target_path)
                    return True
            except Exception as curl_e:
                print(f"Failed to download via curl from {url}: {curl_e}")
                last_error = curl_e
                continue
                
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
    """Fetch the public IPv6 address of this machine from multiple providers in parallel."""
    providers = [
        ("https://speed.neu6.edu.cn/getIP.php", None),
        ("https://ipv6.lookup.test-ipv6.com/ip/", "ip"),
        ("https://v6.ident.me", None),
        ("https://api6.ipify.org?format=json", "ip")
    ]
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(providers)) as executor:
        futures = {
            executor.submit(fetch_single_ip, url, key, 4): url
            for url, key in providers
        }
        for future in concurrent.futures.as_completed(futures):
            try:
                ip = future.result()
                if ip:
                    return ip
            except Exception:
                pass
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


