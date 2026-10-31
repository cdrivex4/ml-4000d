import urllib.request
import re

url = "https://asia.canon/en/support/EOS_3000D/model"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as r:
        html = r.read().decode('utf-8', errors='ignore')
        print("Success! Fetched len:", len(html))
        # Look for firmware or download URLs
        matches = set(re.findall(r'href=[\'"]([^\'"]*(?:firmware|support/[0-9a-zA-Z_]+|0200|v110|CCF)[^\'"]*)[\'"]', html, re.I))
        for m in sorted(matches):
            print(" ", m)
except Exception as e:
    print("Error:", e)
