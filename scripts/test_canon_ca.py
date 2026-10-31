import urllib.request
import json
import re

# Search Canon Canada API or page for EOS Rebel T100
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': '*/*'
}

def search_canon_ca():
    url = "https://www.canon.ca/en/support/Support-Detail?m=2680C003"
    print("Trying canon.ca...")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
            print("Canon.ca response len:", len(content))
            for m in re.finditer(r'(https?://[^\s"\'<>]*(?:zip|c-wss)[^\s"\'<>]*)', content):
                print("Found link:", m.group(1))
    except Exception as e:
        print("Canon.ca error:", e)

search_canon_ca()
