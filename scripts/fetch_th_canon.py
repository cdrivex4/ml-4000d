import urllib.request
import re

url = "https://th.canon/en/support/0400852502"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}
try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as r:
        html = r.read().decode('utf-8', errors='ignore')
        print("Success! Fetched length:", len(html))
        
        # Search for download links
        links = re.findall(r'href=[\'"]([^\'"]*(?:gdlp|c-wss|download|zip|\.FIR)[^\'"]*)[\'"]', html, re.I)
        print("Links found:")
        for l in set(links):
            print("  ", l)
            
        # Also check for form action or javascript variables
        for m in re.finditer(r'(https?://[^\s"\'<>]+(?:zip|FIR|c-wss)[^\s"\'<>]*)', html, re.I):
            print("Direct match:", m.group(1))
except Exception as e:
    print("Error:", e)
