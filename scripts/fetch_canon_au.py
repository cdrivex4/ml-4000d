import urllib.request
import re

url = "https://www.canon.com.au/cameras/eos-3000d/support"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        print(f"Fetched {len(html)} bytes from {url}")
        
        matches = set(re.findall(r'href=[\'"]([^\'"]*(?:firmware|download|c-wss|v110|CCF|\.zip)[^\'"]*)[\'"]', html, re.I))
        for m in sorted(matches):
            print("  ", m)
except Exception as e:
    print("Error:", e)
