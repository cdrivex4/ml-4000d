import urllib.request
import re

url = "https://in.canon/en/support/eos-3000d/model"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        print(f"Fetched {len(html)} bytes from {url}")
        
        # Look for firmware links or support detail IDs
        matches = re.findall(r'href=[\'"]([^\'"]*(?:firmware|support/[0-9]+|0200|v110|CCF)[^\'"]*)[\'"]', html, re.I)
        print("Matches:")
        for m in set(matches):
            print("  ", m)
except Exception as e:
    print("Error:", e)
