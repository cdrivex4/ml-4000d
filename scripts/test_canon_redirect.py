import urllib.request
import os

url = "https://pdisp01.c-wss.com/gdl/WWUFORedirectTarget.do?id=MDQwMDAwODUyNTAx&cmp=ACB&lang=EN"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://th.canon/en/support/0400852502'
}

req = urllib.request.Request(url, headers=headers)
print("Querying redirect URL...")
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        print("Final URL:", resp.geturl())
        print("Status:", resp.status)
        print("Headers:", resp.headers)
except Exception as e:
    print("Error:", e)
