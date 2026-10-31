import urllib.request
import re
import json

def get_page(url):
    print("Fetching:", url)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
            print("Length:", len(content))
            return content
    except Exception as e:
        print("Error fetching:", e)
        return ""

def search_patterns(html):
    # Search for any .zip or .FIR or gdlp
    matches = set()
    for m in re.finditer(r'(https?://[^\s"\'<>]*(?:zip|FIR|c-wss)[^\s"\'<>]*)', html, re.I):
        matches.add(m.group(1))
    for m in re.finditer(r'[\'"](/[^"\'<>]*(?:download|firmware|0200)[^"\'<>]*)[\'"]', html, re.I):
        matches.add(m.group(1))
    return list(matches)

# Let's search Asia Canon support page for EOS 4000D firmware
html = get_page("https://asia.canon/en/support/0200676402")
results = search_patterns(html)
print("Matches found on page 0200676402:")
for r in sorted(results):
    print("  ", r)
